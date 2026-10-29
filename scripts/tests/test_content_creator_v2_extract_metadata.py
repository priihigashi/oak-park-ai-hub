"""Sprint 2-C: tests for ffprobe.extract() — the engine behind extract_metadata CLI.

Mocks subprocess.run so ffprobe binary is not required in CI.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.content_creator_v2.ffprobe import extract


_MOCK_PROBE = {
    "format": {
        "duration": "12.5",
        "tags": {"creation_time": "2026-01-01T10:00:00.000000Z"},
    },
    "streams": [{"codec_type": "video", "width": 1080, "height": 1920}],
}


def _dummy_run(returncode: int = 0, stdout: str = "", stderr: str = "") -> MagicMock:
    return MagicMock(returncode=returncode, stdout=stdout, stderr=stderr)


def _file(tmp_path: Path, name: str = "clip.mp4", content: bytes = b"\x00" * 1024) -> Path:
    p = tmp_path / name
    p.write_bytes(content)
    return p


class TestExtractMetadataShape:
    def test_returns_media_asset(self, tmp_path):
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(_MOCK_PROBE))):
            asset = extract(p)
        assert asset.path == str(p.resolve())
        assert asset.duration == pytest.approx(12.5)
        assert asset.width == 1080
        assert asset.height == 1920
        assert asset.checksum  # non-empty SHA-256

    def test_portrait_orientation(self, tmp_path):
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(_MOCK_PROBE))):
            asset = extract(p)
        assert asset.orientation == "portrait"

    def test_landscape_orientation(self, tmp_path):
        landscape = {"format": {"duration": "5.0", "tags": {}},
                     "streams": [{"codec_type": "video", "width": 1920, "height": 1080}]}
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(landscape))):
            asset = extract(p)
        assert asset.orientation == "landscape"

    def test_square_orientation(self, tmp_path):
        square = {"format": {"duration": "3.0", "tags": {}},
                  "streams": [{"codec_type": "video", "width": 1080, "height": 1080}]}
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(square))):
            asset = extract(p)
        assert asset.orientation == "square"

    def test_captured_at_from_tags(self, tmp_path):
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(_MOCK_PROBE))):
            asset = extract(p)
        assert asset.captured_at == "2026-01-01T10:00:00.000000Z"

    def test_captured_at_none_when_no_tag(self, tmp_path):
        no_tag = {"format": {"duration": "3.0", "tags": {}},
                  "streams": [{"codec_type": "video", "width": 720, "height": 1280}]}
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(no_tag))):
            asset = extract(p)
        assert asset.captured_at is None


class TestExtractMetadataDefaults:
    def test_default_owner_is_priscila(self, tmp_path):
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(_MOCK_PROBE))):
            asset = extract(p)
        assert asset.owner == "priscila"

    def test_default_source_is_personal(self, tmp_path):
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(_MOCK_PROBE))):
            asset = extract(p)
        assert asset.source == "personal"

    def test_custom_owner_and_source(self, tmp_path):
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(_MOCK_PROBE))):
            asset = extract(p, owner="mike", source="licensed")
        assert asset.owner == "mike"
        assert asset.source == "licensed"


class TestExtractMetadataErrors:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        ghost = tmp_path / "ghost.mp4"
        with pytest.raises(FileNotFoundError):
            extract(ghost)

    def test_ffprobe_failure_raises_runtime_error(self, tmp_path):
        p = _file(tmp_path)
        with patch("subprocess.run", return_value=_dummy_run(returncode=1, stderr="No such file")):
            with pytest.raises(RuntimeError, match="ffprobe failed"):
                extract(p)

    def test_stable_checksum_across_calls(self, tmp_path):
        p = _file(tmp_path, content=b"deterministic")
        with patch("subprocess.run", return_value=_dummy_run(stdout=json.dumps(_MOCK_PROBE))):
            a1 = extract(p)
            a2 = extract(p)
        assert a1.checksum == a2.checksum
