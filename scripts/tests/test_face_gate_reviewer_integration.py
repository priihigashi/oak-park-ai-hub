"""Tests for SH-147 PR B — face gate integration into carousel_reviewer.

Verifies the additive hook in ``carousel_reviewer.check_built_post`` /
``_run_face_gate_check``:
- ``STORY_PIPELINE_V2_ENABLED=0`` (default) -> no face-gate issues appended
- ``STORY_PIPELINE_V2_ENABLED=1`` -> face-gate violations appended as
  ``[face-gate] slide N: Name — reason`` strings
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

# carousel_reviewer.py imports production deps (google-auth, google-api-python-client,
# PIL, anthropic, openai, etc.) that aren't required to validate the face-gate
# integration logic itself. CI runs with these installed (Python 3.11). Locally
# we skip cleanly if any are missing so contributors can still iterate.
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


def _content_with_named_person_no_face():
    return {
        "slides": [
            {
                "slide": 2,
                "body_pt": "Segundo o senador <strong>Marcelo Castro</strong>, a CPI foi suspensa.",
            }
        ]
    }


def _content_with_named_person_and_sticker():
    return {
        "slides": [
            {
                "slide": 2,
                "body_pt": "<strong>Marcelo Castro</strong> declarou hoje.",
                "sticker_slot": "marcelo.png",
            }
        ]
    }


def _content_with_no_named_person():
    return {
        "slides": [
            {"slide": 2, "body": "The concrete patio needs proper drainage."}
        ]
    }


@unittest.skipIf(_reviewer is None, _SKIP_REASON)
class FaceGateReviewerIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.reviewer = _reviewer

    # --- flag OFF (default) -------------------------------------------------

    def test_flag_off_returns_empty(self):
        content = _content_with_named_person_no_face()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "0"}, clear=False):
            issues = self.reviewer._run_face_gate_check(content, "brazil")
        self.assertEqual(issues, [])

    def test_flag_default_env_returns_empty(self):
        content = _content_with_named_person_no_face()
        env = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_ENABLED"}
        with patch.dict(os.environ, env, clear=True):
            issues = self.reviewer._run_face_gate_check(content, "brazil")
        self.assertEqual(issues, [])

    def test_flag_off_truthy_string_zero(self):
        content = _content_with_named_person_no_face()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "false"}, clear=False):
            issues = self.reviewer._run_face_gate_check(content, "brazil")
        self.assertEqual(issues, [])

    # --- flag ON ------------------------------------------------------------

    def test_flag_on_appends_violation_string(self):
        content = _content_with_named_person_no_face()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_face_gate_check(content, "brazil")
        self.assertEqual(len(issues), 1)
        self.assertTrue(issues[0].startswith("[face-gate] slide 2: Marcelo Castro"))

    def test_flag_on_pass_when_face_present(self):
        content = _content_with_named_person_and_sticker()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_face_gate_check(content, "brazil")
        self.assertEqual(issues, [])

    def test_flag_on_no_named_person_no_issues(self):
        content = _content_with_no_named_person()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_face_gate_check(content, "opc")
        self.assertEqual(issues, [])

    def test_flag_on_truthy_values_all_enable(self):
        content = _content_with_named_person_no_face()
        for val in ("1", "true", "TRUE", "yes", "on"):
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": val}, clear=False):
                issues = self.reviewer._run_face_gate_check(content, "brazil")
            self.assertEqual(len(issues), 1, f"value {val!r} should enable gate")

    # --- niche filtering / safety -------------------------------------------

    def test_unknown_niche_silently_skipped(self):
        content = _content_with_named_person_no_face()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_face_gate_check(content, "stocks")
        self.assertEqual(issues, [])

    def test_empty_niche_silently_skipped(self):
        content = _content_with_named_person_no_face()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_face_gate_check(content, "")
        self.assertEqual(issues, [])

    def test_none_content_does_not_crash(self):
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_face_gate_check(None, "opc")
        # Either empty or a gate-failed marker, but must not raise.
        self.assertIsInstance(issues, list)

    def test_gate_module_unavailable_returns_empty(self):
        # Simulate the gate module failing to import.
        with patch.object(self.reviewer, "check_named_person_face_coverage", None):
            content = _content_with_named_person_no_face()
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
                issues = self.reviewer._run_face_gate_check(content, "brazil")
            self.assertEqual(issues, [])

    # --- integration via check_built_post ----------------------------------

    def test_check_built_post_flag_off_no_face_gate_string(self):
        """End-to-end: a built post result with a named-person-no-face content
        should NOT produce [face-gate] issues when the flag is off."""
        result = {
            "post_id": "test-post-1",
            "topic": "Test topic",
            "niche": "brazil",
            "content": _content_with_named_person_no_face(),
        }
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "0", "WORK_DIR": "/nonexistent"}, clear=False):
            out = self.reviewer.check_built_post(result)
        face_gate_issues = [i for i in out["issues"] if "[face-gate]" in i]
        self.assertEqual(face_gate_issues, [])

    def test_check_built_post_flag_on_appends_face_gate_string(self):
        result = {
            "post_id": "test-post-2",
            "topic": "Test topic",
            "niche": "brazil",
            "content": _content_with_named_person_no_face(),
        }
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1", "WORK_DIR": "/nonexistent"}, clear=False):
            out = self.reviewer.check_built_post(result)
        face_gate_issues = [i for i in out["issues"] if "[face-gate]" in i]
        self.assertEqual(len(face_gate_issues), 1)
        self.assertIn("Marcelo Castro", face_gate_issues[0])


if __name__ == "__main__":
    unittest.main()
