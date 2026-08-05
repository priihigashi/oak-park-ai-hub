"""Regression test for the corrupt-image class that stopped the content pipeline.

Failure being pinned (run 28161948295, 2026-06-25): Drive's anonymous
`/uc?export=download` endpoint answers 200 OK with an HTML error page when the
file is private or missing. The old guard in `_download_drive_photo` only asked
"is this bigger than 2000 bytes?", which an HTML error page comfortably is — so
ten error pages were written out as `.jpg`, the strict carousel reviewer flagged
all ten as "corrupt or unreadable", and the workflow went red.

The point of this file is that `test_html_error_page_is_rejected` MUST fail if
the size-only guard is ever restored. It is written against the exact payload
shape Google actually returns, not a synthetic blob.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "content_creator"))

from carousel_builder import _accept_downloaded_photo, _looks_like_image_bytes  # noqa: E402


# A trimmed but structurally faithful copy of what drive.google.com/uc returns
# for a file that is not publicly shared. Note it is >2000 bytes — that is the
# whole reason the old size-only check let it through.
DRIVE_ERROR_PAGE = (
    b"<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
    b"<title>Google Drive - Access Denied</title></head><body>"
    b"<p>Sorry, you can&#39;t access this file because you are not authorized.</p>"
    + b"<!-- padding to exceed the legacy 2000-byte floor -->" * 60
    + b"</body></html>"
)

PNG_1PX = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _write(tmpdir, name, payload):
    p = os.path.join(tmpdir, name)
    with open(p, "wb") as fh:
        fh.write(payload)
    return p


class TestLooksLikeImageBytes(unittest.TestCase):
    def test_html_error_page_is_not_an_image(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(_looks_like_image_bytes(_write(d, "a.jpg", DRIVE_ERROR_PAGE)))

    def test_json_error_body_is_not_an_image(self):
        with tempfile.TemporaryDirectory() as d:
            payload = b'{"error":{"code":404,"message":"File not found"}}' + b" " * 3000
            self.assertFalse(_looks_like_image_bytes(_write(d, "a.jpg", payload)))

    def test_real_signatures_are_accepted(self):
        cases = {
            "a.png": PNG_1PX,
            "a.jpg": b"\xff\xd8\xff\xe0" + b"\x00" * 40,
            "a.gif": b"GIF89a" + b"\x00" * 40,
            "a.webp": b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 40,
            "a.heic": b"\x00\x00\x00\x18ftypheic" + b"\x00" * 40,
            "a.tif": b"II*\x00" + b"\x00" * 40,
        }
        with tempfile.TemporaryDirectory() as d:
            for name, payload in cases.items():
                self.assertTrue(_looks_like_image_bytes(_write(d, name, payload)), name)

    def test_missing_and_empty_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(_looks_like_image_bytes(os.path.join(d, "nope.jpg")))
            self.assertFalse(_looks_like_image_bytes(_write(d, "empty.jpg", b"")))


class TestAcceptDownloadedPhoto(unittest.TestCase):
    def test_html_error_page_is_rejected_and_deleted(self):
        """THE regression case. If this passes with a size-only guard, the guard is wrong."""
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "slide2.jpg", DRIVE_ERROR_PAGE)
            self.assertGreater(os.path.getsize(p), 2000,
                               "fixture must be big enough to defeat the legacy size floor")
            self.assertFalse(_accept_downloaded_photo(p))
            self.assertFalse(os.path.exists(p), "rejected payload must not be left on disk")

    def test_tiny_file_still_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "tiny.jpg", b"\xff\xd8\xff" + b"\x00" * 10)
            self.assertFalse(_accept_downloaded_photo(p))

    def test_valid_png_is_accepted_and_kept(self):
        with tempfile.TemporaryDirectory() as d:
            # Pad past the 2000-byte floor without breaking the PNG signature;
            # Pillow tolerates trailing bytes after IEND.
            p = _write(d, "ok.png", PNG_1PX + b"\x00" * 4000)
            self.assertTrue(_accept_downloaded_photo(p))
            self.assertTrue(os.path.exists(p))

    def test_jpeg_signature_but_undecodable_is_rejected_when_pillow_present(self):
        """Magic bytes alone are not proof; the Pillow gate must still catch garbage."""
        try:
            import PIL  # noqa: F401
        except Exception:
            self.skipTest("Pillow not installed — the second gate is inactive by design")
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "fake.jpg", b"\xff\xd8\xff" + os.urandom(4000))
            self.assertFalse(_accept_downloaded_photo(p))


if __name__ == "__main__":
    unittest.main()
