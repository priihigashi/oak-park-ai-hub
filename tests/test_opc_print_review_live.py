"""Static contract for the OPC live-review UX. No browser or paid API."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/factcheck_print"))
import opc_render as r

class LiveReview(unittest.TestCase):
    def test_dom_is_source_of_truth(self):
        self.assertIn("function collectReview()", r.REVIEW_JS)
        self.assertIn("document.querySelectorAll('.card[data-review-id]')", r.REVIEW_JS)
        self.assertIn("document.addEventListener('input'", r.REVIEW_JS)
        self.assertIn("window.refreshOPCReview=renderReview", r.REVIEW_JS)

    def test_note_only_feedback_is_kept(self):
        self.assertIn("if(!clean(comment)&&!choice)return", r.REVIEW_JS)
        self.assertIn("NOTE ONLY", r.REVIEW_JS)

    def test_copy_has_safe_fallback(self):
        self.assertIn("navigator.clipboard.writeText", r.REVIEW_JS)
        self.assertIn("range.selectNodeContents(out)", r.REVIEW_JS)

if __name__ == "__main__":
    unittest.main()
