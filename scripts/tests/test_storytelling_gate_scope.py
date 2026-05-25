"""Tests for the STORY_PIPELINE_V2_NICHES bake-control scope helper.

Verifies ``carousel_reviewer._storytelling_gate_in_scope`` and that the
scope check is honored by all 4 storytelling gate hooks (face, cadence,
news source dual-gate, motion/static).
"""

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
class StorytellingGateScopeTest(unittest.TestCase):
    """Direct tests of _storytelling_gate_in_scope()."""

    def test_flag_off_returns_false_regardless_of_scope(self):
        for scope in ("", "brazil", "brazil,usa", "all"):
            with patch.dict(os.environ, {
                "STORY_PIPELINE_V2_ENABLED": "0",
                "STORY_PIPELINE_V2_NICHES": scope,
            }, clear=False):
                self.assertFalse(_reviewer._storytelling_gate_in_scope("brazil"))

    def test_flag_default_env_returns_false(self):
        env = {k: v for k, v in os.environ.items()
               if k not in ("STORY_PIPELINE_V2_ENABLED", "STORY_PIPELINE_V2_NICHES")}
        with patch.dict(os.environ, env, clear=True):
            self.assertFalse(_reviewer._storytelling_gate_in_scope("brazil"))

    def test_flag_on_no_scope_means_all_niches_in_scope(self):
        env = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_NICHES"}
        env["STORY_PIPELINE_V2_ENABLED"] = "1"
        with patch.dict(os.environ, env, clear=True):
            for niche in ("brazil", "usa", "opc", "news", "anything"):
                self.assertTrue(_reviewer._storytelling_gate_in_scope(niche), f"niche={niche!r}")

    def test_flag_on_empty_scope_means_all_niches(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "",
        }, clear=False):
            for niche in ("brazil", "usa", "opc", "news"):
                self.assertTrue(_reviewer._storytelling_gate_in_scope(niche))

    def test_scope_brazil_only_includes_brazil(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil",
        }, clear=False):
            self.assertTrue(_reviewer._storytelling_gate_in_scope("brazil"))

    def test_scope_brazil_only_excludes_opc_and_usa(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil",
        }, clear=False):
            self.assertFalse(_reviewer._storytelling_gate_in_scope("opc"))
            self.assertFalse(_reviewer._storytelling_gate_in_scope("usa"))
            self.assertFalse(_reviewer._storytelling_gate_in_scope("news"))

    def test_scope_multi_niche_csv(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil,usa",
        }, clear=False):
            self.assertTrue(_reviewer._storytelling_gate_in_scope("brazil"))
            self.assertTrue(_reviewer._storytelling_gate_in_scope("usa"))
            self.assertFalse(_reviewer._storytelling_gate_in_scope("opc"))

    def test_scope_case_insensitive(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "BRAZIL, USA",
        }, clear=False):
            self.assertTrue(_reviewer._storytelling_gate_in_scope("brazil"))
            self.assertTrue(_reviewer._storytelling_gate_in_scope("Brazil"))
            self.assertTrue(_reviewer._storytelling_gate_in_scope("usa"))

    def test_scope_with_whitespace_and_empty_entries(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": " brazil , , usa ,",
        }, clear=False):
            self.assertTrue(_reviewer._storytelling_gate_in_scope("brazil"))
            self.assertTrue(_reviewer._storytelling_gate_in_scope("usa"))
            self.assertFalse(_reviewer._storytelling_gate_in_scope("opc"))

    def test_empty_niche_with_scope_returns_false(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil",
        }, clear=False):
            self.assertFalse(_reviewer._storytelling_gate_in_scope(""))
            self.assertFalse(_reviewer._storytelling_gate_in_scope(None))


@unittest.skipIf(_reviewer is None, _SKIP_REASON)
class GateHooksHonorScopeTest(unittest.TestCase):
    """Verifies all 4 gate hooks return [] when niche is out of scope,
    even though the master flag is ON and the niche is in the gate's
    supported list."""

    def _named_no_face(self):
        return {
            "slides": [{
                "slide": 2,
                "body_pt": "Segundo <strong>Marcelo Castro</strong>, ...",
            }]
        }

    def _bad_cadence(self):
        return {
            "slides": [
                {"slide": 1, "type": "cover"},
                {"slide": 2, "visual_hint": "none"},
                {"slide": 3, "visual_hint": "none"},
                {"slide": 4, "slide_purpose": "sources"},
            ]
        }

    def _single_source_confirmed(self):
        return {"claims": [{"text": "x", "status": "confirmed", "sources": ["G1"]}]}

    def test_face_gate_skips_when_opc_out_of_scope(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil",
        }, clear=False):
            issues = _reviewer._run_face_gate_check(self._named_no_face(), "opc")
        self.assertEqual(issues, [])

    def test_face_gate_fires_when_brazil_in_scope(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil",
        }, clear=False):
            issues = _reviewer._run_face_gate_check(self._named_no_face(), "brazil")
        self.assertEqual(len(issues), 1)
        self.assertIn("Marcelo Castro", issues[0])

    def test_cadence_gate_skips_when_opc_out_of_scope(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil",
        }, clear=False):
            issues = _reviewer._run_cadence_gate_check(self._bad_cadence(), "opc")
        self.assertEqual(issues, [])

    def test_news_source_advisory_skips_when_opc_out_of_scope(self):
        # opc is already not in the news-source niche list — but this still
        # verifies the scope check fires before the niche-list check
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil",
        }, clear=False):
            issues = _reviewer._run_news_source_dual_gate_advisory(
                self._single_source_confirmed(), "usa"
            )
        # usa is in gate's niche list but NOT in scope -> empty
        self.assertEqual(issues, [])

    def test_news_source_advisory_fires_when_brazil_in_scope(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil",
        }, clear=False):
            issues = _reviewer._run_news_source_dual_gate_advisory(
                self._single_source_confirmed(), "brazil"
            )
        self.assertGreaterEqual(len(issues), 1)

    def test_motion_static_gate_skips_when_opc_out_of_scope(self):
        with patch.dict(os.environ, {
            "STORY_PIPELINE_V2_ENABLED": "1",
            "STORY_PIPELINE_V2_NICHES": "brazil",
        }, clear=False):
            issues = _reviewer._run_motion_static_gate_check(
                {}, "opc", "some-post", "/nonexistent"
            )
        self.assertEqual(issues, [])

    def test_legacy_unset_scope_keeps_all_niches_enabled(self):
        """Sanity: existing prod-style flag with no NICHES var = all niches gated."""
        env = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_NICHES"}
        env["STORY_PIPELINE_V2_ENABLED"] = "1"
        with patch.dict(os.environ, env, clear=True):
            for niche in ("opc", "brazil", "usa"):
                issues = _reviewer._run_face_gate_check(self._named_no_face(), niche)
                self.assertEqual(len(issues), 1, f"niche={niche!r}: expected face gate to fire")


if __name__ == "__main__":
    unittest.main()
