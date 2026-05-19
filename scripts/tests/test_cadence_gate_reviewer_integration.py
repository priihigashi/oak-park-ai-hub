"""Tests for SH-148 PR B — cadence gate integration into carousel_reviewer.

Verifies the additive hook in ``carousel_reviewer.check_built_post`` /
``_run_cadence_gate_check``:
- ``STORY_PIPELINE_V2_ENABLED=0`` (default) -> no cadence-gate issues appended
- ``STORY_PIPELINE_V2_ENABLED=1`` -> cadence violations appended as
  ``[cadence-gate] slides A-B: reason`` strings
- unrouted/unknown niche -> silent skip, never raises
- missing/unavailable gate module -> empty list (no crash)
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

# Same skip-on-import-fail pattern as SH-147 PR B test. CI (Python 3.11)
# imports cleanly; local Python 3.9 with no google deps will skip.
try:
    import carousel_reviewer as _reviewer  # noqa: E402
    _REVIEWER_IMPORT_ERROR = None
except Exception as _e:
    _reviewer = None
    _REVIEWER_IMPORT_ERROR = _e


_SKIP_REASON = (
    f"carousel_reviewer unavailable in this env: {_REVIEWER_IMPORT_ERROR!r}. "
    "Tests will run in CI where production deps are installed."
)


def _slide(slide_num, **fields):
    base = {"slide": slide_num}
    base.update(fields)
    return base


def _content_with_two_consecutive_text_only():
    return {
        "slides": [
            _slide(1, type="cover"),
            _slide(2, visual_hint="none"),
            _slide(3, visual_hint="none"),
            _slide(4, visual_hint="product-photo"),
            _slide(5, slide_purpose="sources"),
        ]
    }


def _content_with_three_consecutive_text_only():
    return {
        "slides": [
            _slide(1, type="cover"),
            _slide(2, visual_hint="none"),
            _slide(3, visual_hint="none"),
            _slide(4, visual_hint="none"),
            _slide(5, slide_purpose="sources"),
        ]
    }


def _content_clean_cadence():
    return {
        "slides": [
            _slide(1, type="cover"),
            _slide(2, visual_hint="product-photo"),
            _slide(3, visual_hint="none"),
            _slide(4, visual_hint="context-image"),
            _slide(5, slide_purpose="sources"),
        ]
    }


@unittest.skipIf(_reviewer is None, _SKIP_REASON)
class CadenceGateReviewerIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.reviewer = _reviewer

    # --- flag OFF (default) -------------------------------------------------

    def test_flag_off_returns_empty(self):
        content = _content_with_two_consecutive_text_only()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "0"}, clear=False):
            issues = self.reviewer._run_cadence_gate_check(content, "opc")
        self.assertEqual(issues, [])

    def test_flag_default_env_returns_empty(self):
        content = _content_with_two_consecutive_text_only()
        env = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_ENABLED"}
        with patch.dict(os.environ, env, clear=True):
            issues = self.reviewer._run_cadence_gate_check(content, "opc")
        self.assertEqual(issues, [])

    # --- flag ON ------------------------------------------------------------

    def test_flag_on_two_consecutive_emits_violation(self):
        content = _content_with_two_consecutive_text_only()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_cadence_gate_check(content, "opc")
        self.assertEqual(len(issues), 1)
        self.assertTrue(issues[0].startswith("[cadence-gate] slides 2-3:"))

    def test_flag_on_three_consecutive_emits_violation(self):
        content = _content_with_three_consecutive_text_only()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_cadence_gate_check(content, "brazil")
        self.assertEqual(len(issues), 1)
        self.assertTrue(issues[0].startswith("[cadence-gate] slides 2-4:"))

    def test_flag_on_clean_cadence_no_issues(self):
        content = _content_clean_cadence()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_cadence_gate_check(content, "opc")
        self.assertEqual(issues, [])

    def test_flag_on_truthy_values_all_enable(self):
        content = _content_with_two_consecutive_text_only()
        for val in ("1", "true", "TRUE", "yes", "on"):
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": val}, clear=False):
                issues = self.reviewer._run_cadence_gate_check(content, "opc")
            self.assertEqual(len(issues), 1, f"value {val!r} should enable gate")

    # --- niche filtering / safety -------------------------------------------

    def test_unknown_niche_silently_skipped(self):
        content = _content_with_two_consecutive_text_only()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_cadence_gate_check(content, "stocks")
        self.assertEqual(issues, [])

    def test_empty_niche_silently_skipped(self):
        content = _content_with_two_consecutive_text_only()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_cadence_gate_check(content, "")
        self.assertEqual(issues, [])

    def test_none_content_does_not_crash(self):
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_cadence_gate_check(None, "opc")
        self.assertIsInstance(issues, list)

    def test_gate_module_unavailable_returns_empty(self):
        with patch.object(self.reviewer, "check_visual_cadence", None):
            content = _content_with_two_consecutive_text_only()
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
                issues = self.reviewer._run_cadence_gate_check(content, "opc")
            self.assertEqual(issues, [])

    # --- integration via check_built_post ----------------------------------

    def test_check_built_post_flag_off_no_cadence_gate_string(self):
        result = {
            "post_id": "test-cadence-1",
            "topic": "Test topic",
            "niche": "opc",
            "content": _content_with_two_consecutive_text_only(),
        }
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "0", "WORK_DIR": "/nonexistent"}, clear=False):
            out = self.reviewer.check_built_post(result)
        cadence_issues = [i for i in out["issues"] if "[cadence-gate]" in i]
        self.assertEqual(cadence_issues, [])

    def test_check_built_post_flag_on_appends_cadence_gate_string(self):
        result = {
            "post_id": "test-cadence-2",
            "topic": "Test topic",
            "niche": "brazil",
            "content": _content_with_three_consecutive_text_only(),
        }
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1", "WORK_DIR": "/nonexistent"}, clear=False):
            out = self.reviewer.check_built_post(result)
        cadence_issues = [i for i in out["issues"] if "[cadence-gate]" in i]
        self.assertEqual(len(cadence_issues), 1)
        self.assertIn("slides 2-4", cadence_issues[0])


if __name__ == "__main__":
    unittest.main()
