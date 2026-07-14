"""Tests for FORMAT-021 voice gate integration into carousel_reviewer."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

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


@unittest.skipIf(_reviewer is None, _SKIP_REASON)
class VoiceGateReviewerIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.reviewer = _reviewer

    def test_flag_off_returns_empty(self):
        content = {"cover_en": "Did you know this changed?"}
        with patch.dict(os.environ, {"VOICE_GATE_ENABLED": "0"}, clear=False):
            issues = self.reviewer._run_voice_gate_check(content, "usa", {})
        self.assertEqual(issues, [])

    def test_flag_on_appends_banned_hook(self):
        content = {"cover_en": "Did you know this changed?"}
        with patch.dict(os.environ, {"VOICE_GATE_ENABLED": "1", "SHEETS_TOKEN": ""}, clear=False):
            with patch.object(self.reviewer, "VOICE_GATE_ENABLED", True):
                issues = self.reviewer._run_voice_gate_check(content, "usa", {})
        self.assertEqual(len(issues), 1)
        self.assertTrue(issues[0].startswith("[voice-gate] banned_hook:"))

    def test_unknown_niche_skips(self):
        with patch.dict(os.environ, {"VOICE_GATE_ENABLED": "1"}, clear=False):
            with patch.object(self.reviewer, "VOICE_GATE_ENABLED", True):
                issues = self.reviewer._run_voice_gate_check({"cover_en": "Did you know?"}, "stocks", {})
        self.assertEqual(issues, [])

    def test_check_built_post_flag_on_appends_voice_gate_string(self):
        result = {
            "post_id": "voice-gate-post",
            "topic": "Test topic",
            "niche": "usa",
            "content": {"cover_en": "Did you know this changed?"},
            "caption": "Here is the breakdown.",
            "in_post_hashtags": "#policy #history #context",
        }
        with patch.dict(os.environ, {"VOICE_GATE_ENABLED": "1", "WORK_DIR": "/nonexistent", "SHEETS_TOKEN": ""}, clear=False):
            with patch.object(self.reviewer, "VOICE_GATE_ENABLED", True):
                out = self.reviewer.check_built_post(result)
        voice_issues = [i for i in out["issues"] if "[voice-gate]" in i]
        self.assertEqual(len(voice_issues), 1)
        self.assertIn("banned_hook", voice_issues[0])

    def test_gate_module_unavailable_returns_empty(self):
        with patch.object(self.reviewer, "check_voice_personality", None):
            with patch.object(self.reviewer, "VOICE_GATE_ENABLED", True):
                issues = self.reviewer._run_voice_gate_check({"cover_en": "Did you know?"}, "usa", {})
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
