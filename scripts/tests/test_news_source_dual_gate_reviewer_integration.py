"""Tests for SH-151 PR B — News source dual-gate reviewer integration.

Verifies the additive advisory hook in ``carousel_reviewer.check_built_post`` /
``_run_news_source_dual_gate_advisory``:
- ``STORY_PIPELINE_V2_ENABLED=0`` (default) -> no advisories appended
- ``STORY_PIPELINE_V2_ENABLED=1`` -> News source violations appear as
  ``[news-source-gate][advisory]`` strings
- advisories do not make ``passed`` false
- unrouted/unknown niche -> silent skip, never raises
- missing/unavailable gate module -> empty list (no crash)
"""

import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))


def _install_google_stubs():
    """Provide tiny import-time stubs for optional Google deps in local tests."""
    google = types.ModuleType("google")
    oauth2 = types.ModuleType("google.oauth2")
    credentials_mod = types.ModuleType("google.oauth2.credentials")
    googleapiclient = types.ModuleType("googleapiclient")
    discovery_mod = types.ModuleType("googleapiclient.discovery")
    http_mod = types.ModuleType("googleapiclient.http")

    class Credentials:
        @classmethod
        def from_authorized_user_info(cls, *_args, **_kwargs):
            return cls()

    class MediaIoBaseDownload:
        pass

    class MediaFileUpload:
        def __init__(self, *_args, **_kwargs):
            pass

    def build(*_args, **_kwargs):
        return None

    credentials_mod.Credentials = Credentials
    discovery_mod.build = build
    http_mod.MediaIoBaseDownload = MediaIoBaseDownload
    http_mod.MediaFileUpload = MediaFileUpload
    oauth2.credentials = credentials_mod
    google.oauth2 = oauth2
    googleapiclient.discovery = discovery_mod
    googleapiclient.http = http_mod

    sys.modules.setdefault("google", google)
    sys.modules.setdefault("google.oauth2", oauth2)
    sys.modules.setdefault("google.oauth2.credentials", credentials_mod)
    sys.modules.setdefault("googleapiclient", googleapiclient)
    sys.modules.setdefault("googleapiclient.discovery", discovery_mod)
    sys.modules.setdefault("googleapiclient.http", http_mod)


_install_google_stubs()

# carousel_reviewer.py imports production deps that are not required to
# validate this small integration hook. CI has them installed; local runs skip
# cleanly if any are missing.
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


def _confirmed_single_source_content():
    return {
        "claims": [
            {
                "text": "Banco Master sale was confirmed",
                "status": "confirmed",
                "sources": ["G1"],
            }
        ]
    }


def _confirmed_two_source_content():
    return {
        "claims": [
            {
                "text": "Banco Master sale was confirmed",
                "status": "confirmed",
                "sources": ["G1", "Folha"],
            }
        ]
    }


def _allegation_single_source_content():
    return {
        "claims": [
            {
                "text": "The report alleges a private negotiation",
                "status": "allegation",
                "sources": ["G1"],
            }
        ]
    }


def _banned_source_content():
    return {
        "claims": [
            {
                "text": "Context copied from an inspiration account",
                "status": "allegation",
                "sources": ["Inspired by @marceloem23"],
            }
        ]
    }


@unittest.skipIf(_reviewer is None, _SKIP_REASON)
class NewsSourceDualGateReviewerIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.reviewer = _reviewer

    # --- flag OFF (default) -------------------------------------------------

    def test_flag_off_returns_empty(self):
        content = _confirmed_single_source_content()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "0"}, clear=False):
            advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "brazil")
        self.assertEqual(advisories, [])

    def test_flag_default_env_returns_empty(self):
        content = _confirmed_single_source_content()
        env = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_ENABLED"}
        with patch.dict(os.environ, env, clear=True):
            advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "brazil")
        self.assertEqual(advisories, [])

    # --- flag ON ------------------------------------------------------------

    def test_flag_on_single_source_confirmed_claim_adds_advisory(self):
        content = _confirmed_single_source_content()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "brazil")
        self.assertEqual(len(advisories), 1)
        self.assertTrue(advisories[0].startswith("[news-source-gate][advisory] claim 1"))
        self.assertIn("insufficient_independent_sources", advisories[0])

    def test_flag_on_clean_confirmed_claim_returns_empty(self):
        content = _confirmed_two_source_content()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "brazil")
        self.assertEqual(advisories, [])

    def test_flag_on_allegation_single_source_returns_empty(self):
        content = _allegation_single_source_content()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "brazil")
        self.assertEqual(advisories, [])

    def test_flag_on_banned_source_adds_advisory(self):
        content = _banned_source_content()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "usa")
        self.assertEqual(len(advisories), 1)
        self.assertIn("banned_source_used", advisories[0])
        self.assertIn("@marceloem23", advisories[0])

    def test_flag_on_truthy_values_all_enable(self):
        content = _confirmed_single_source_content()
        for val in ("1", "true", "TRUE", "yes", "on"):
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": val}, clear=False):
                advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "brazil")
            self.assertEqual(len(advisories), 1, f"value {val!r} should enable gate")

    # --- route filtering / safety -------------------------------------------

    def test_opc_route_silently_skipped(self):
        content = _confirmed_single_source_content()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "opc")
        self.assertEqual(advisories, [])

    def test_unknown_niche_silently_skipped(self):
        content = _confirmed_single_source_content()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "stocks")
        self.assertEqual(advisories, [])

    def test_none_content_does_not_crash(self):
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            advisories = self.reviewer._run_news_source_dual_gate_advisory(None, "brazil")
        self.assertIsInstance(advisories, list)

    def test_gate_module_unavailable_returns_empty(self):
        with patch.object(self.reviewer, "check_news_source_dual_gate", None):
            content = _confirmed_single_source_content()
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
                advisories = self.reviewer._run_news_source_dual_gate_advisory(content, "brazil")
            self.assertEqual(advisories, [])

    # --- integration via check_built_post ----------------------------------

    def test_check_built_post_flag_off_no_news_source_advisory(self):
        result = {
            "post_id": "test-post-1",
            "topic": "Banco Master",
            "niche": "brazil",
            "content": _confirmed_single_source_content(),
        }
        with tempfile.TemporaryDirectory() as tmp:
            post_dir = Path(tmp) / "test-post-1"
            post_dir.mkdir()
            (post_dir / "caption.txt").write_text("caption", encoding="utf-8")
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "0", "WORK_DIR": tmp}, clear=False):
                out = self.reviewer.check_built_post(result)
        self.assertNotIn("advisories", out)
        self.assertEqual([i for i in out["issues"] if "[news-source-gate]" in i], [])

    def test_check_built_post_flag_on_adds_advisory_without_blocking(self):
        result = {
            "post_id": "test-post-2",
            "topic": "Banco Master",
            "niche": "brazil",
            "content": _confirmed_single_source_content(),
        }
        with tempfile.TemporaryDirectory() as tmp:
            post_dir = Path(tmp) / "test-post-2"
            post_dir.mkdir()
            (post_dir / "caption.txt").write_text("caption", encoding="utf-8")
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1", "WORK_DIR": tmp}, clear=False):
                out = self.reviewer.check_built_post(result)
        self.assertEqual([i for i in out["issues"] if "[news-source-gate]" in i], [])
        self.assertEqual(len(out.get("advisories", [])), 1)
        self.assertIn("[news-source-gate][advisory]", out["advisories"][0])
        self.assertTrue(out["passed"])


if __name__ == "__main__":
    unittest.main()
