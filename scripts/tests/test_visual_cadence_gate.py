"""Tests for SH-148 visual cadence gate contract."""

import json
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

from visual_cadence_gate import (  # noqa: E402
    CadenceViolation,
    VisualCadenceGateError,
    attach_cadence_report,
    cadence_gate_enabled,
    check_visual_cadence,
)


def _slide(slide_num, **fields):
    base = {"slide": slide_num}
    base.update(fields)
    return base


class VisualCadenceGateTest(unittest.TestCase):
    # --- happy paths --------------------------------------------------------

    def test_alternating_pattern_passes(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="product-photo"),
                _slide(3, visual_hint="none"),
                _slide(4, visual_hint="context-image"),
                _slide(5, slide_purpose="sources"),
            ]
        }
        self.assertEqual(check_visual_cadence(content, route="opc"), [])

    def test_all_visuals_passes(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="bio-card"),
                _slide(3, visual_hint="product-photo"),
                _slide(4, visual_hint="context-image"),
                _slide(5, slide_purpose="sources"),
            ]
        }
        self.assertEqual(check_visual_cadence(content, route="brazil"), [])

    def test_single_text_only_middle_slide_passes(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="context-image"),
                _slide(3, visual_hint="none"),
                _slide(4, visual_hint="product-photo"),
                _slide(5, slide_purpose="sources"),
            ]
        }
        self.assertEqual(check_visual_cadence(content, route="opc"), [])

    # --- violation paths ----------------------------------------------------

    def test_two_consecutive_text_only_triggers_violation(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="none"),
                _slide(3, visual_hint="none"),
                _slide(4, visual_hint="product-photo"),
                _slide(5, slide_purpose="sources"),
            ]
        }
        violations = check_visual_cadence(content, route="opc")
        self.assertEqual(len(violations), 1)
        v = violations[0]
        self.assertEqual(v.consecutive_count, 2)
        self.assertEqual(v.start_slide_index, 2)
        self.assertEqual(v.end_slide_index, 3)

    def test_three_consecutive_text_only_triggers_one_violation(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="none"),
                _slide(3, visual_hint="none"),
                _slide(4, visual_hint="none"),
                _slide(5, slide_purpose="sources"),
            ]
        }
        violations = check_visual_cadence(content, route="brazil")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].consecutive_count, 3)

    def test_two_separate_runs_each_violate(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="none"),
                _slide(3, visual_hint="none"),
                _slide(4, visual_hint="product-photo"),
                _slide(5, visual_hint="none"),
                _slide(6, visual_hint="none"),
                _slide(7, slide_purpose="sources"),
            ]
        }
        violations = check_visual_cadence(content, route="opc")
        self.assertEqual(len(violations), 2)
        self.assertEqual(violations[0].start_slide_index, 2)
        self.assertEqual(violations[1].start_slide_index, 5)

    def test_missing_visual_hint_treated_as_text_only(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2),  # no visual_hint at all
                _slide(3),  # no visual_hint
                _slide(4, slide_purpose="sources"),
            ]
        }
        violations = check_visual_cadence(content, route="opc")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].consecutive_count, 2)

    def test_empty_string_visual_hint_treated_as_text_only(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint=""),
                _slide(3, visual_hint=""),
                _slide(4, slide_purpose="sources"),
            ]
        }
        violations = check_visual_cadence(content, route="brazil")
        self.assertEqual(len(violations), 1)

    # --- cover/sources exemption -------------------------------------------

    def test_cover_with_no_visual_hint_does_not_count(self):
        content = {
            "slides": [
                _slide(1),  # cover by position 1, no visual_hint -> exempt
                _slide(2, visual_hint="product-photo"),
                _slide(3, visual_hint="none"),
                _slide(4, slide_purpose="sources"),
            ]
        }
        self.assertEqual(check_visual_cadence(content, route="opc"), [])

    def test_sources_with_no_visual_hint_does_not_extend_run(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="none"),  # single text-only middle slide
                _slide(3, slide_purpose="sources"),  # exempt, ends run
            ]
        }
        self.assertEqual(check_visual_cadence(content, route="brazil"), [])

    # --- defensive anchor detection ----------------------------------------

    def test_sticker_without_visual_hint_counts_as_anchor(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, sticker_slot="someone.png"),  # no visual_hint set
                _slide(3, visual_hint="none"),
                _slide(4, slide_purpose="sources"),
            ]
        }
        self.assertEqual(check_visual_cadence(content, route="brazil"), [])

    def test_bio_card_without_visual_hint_counts_as_anchor(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, bio_cards=[{"name": "X", "photo": "x.png"}]),
                _slide(3, visual_hint="none"),
                _slide(4, slide_purpose="sources"),
            ]
        }
        self.assertEqual(check_visual_cadence(content, route="brazil"), [])

    # --- route handling ----------------------------------------------------

    def test_unrouted_raises(self):
        with self.assertRaises(VisualCadenceGateError):
            check_visual_cadence({"slides": []}, route="unrouted")

    def test_unknown_route_raises(self):
        with self.assertRaises(VisualCadenceGateError):
            check_visual_cadence({"slides": []}, route="stocks")

    def test_route_aliases_resolve(self):
        for route in ("opc", "OPC", "oak-park", "news", "brazil", "usa", "br", "us"):
            check_visual_cadence({"slides": []}, route=route)

    # --- attach_cadence_report (flag-gated) --------------------------------

    def test_flag_off_returns_same_object_and_byte_identical(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="none"),
                _slide(3, visual_hint="none"),
                _slide(4, slide_purpose="sources"),
            ]
        }
        before = json.dumps(content, sort_keys=True)
        result = attach_cadence_report(
            content, route="opc", env={"STORY_PIPELINE_V2_ENABLED": "0"}
        )
        self.assertIs(result, content)
        self.assertEqual(json.dumps(result, sort_keys=True), before)
        self.assertNotIn("visual_cadence", content)

    def test_flag_off_default_env_returns_same_object(self):
        content = {"slides": [_slide(1, type="cover")]}
        env_without_flag = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_ENABLED"}
        result = attach_cadence_report(content, route="opc", env=env_without_flag)
        self.assertIs(result, content)

    def test_flag_on_attaches_report_without_mutating_input(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="none"),
                _slide(3, visual_hint="none"),
                _slide(4, slide_purpose="sources"),
            ]
        }
        result = attach_cadence_report(
            content, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertIsNot(result, content)
        self.assertNotIn("visual_cadence", content)
        self.assertEqual(result["visual_cadence"]["sh_id"], "SH-148")
        self.assertEqual(result["visual_cadence"]["route"], "news")
        self.assertEqual(result["visual_cadence"]["max_consecutive_text_only"], 1)
        self.assertFalse(result["visual_cadence"]["pass"])
        self.assertEqual(len(result["visual_cadence"]["violations"]), 1)

    def test_flag_on_pass_when_cadence_clean(self):
        content = {
            "slides": [
                _slide(1, type="cover"),
                _slide(2, visual_hint="product-photo"),
                _slide(3, visual_hint="none"),
                _slide(4, visual_hint="context-image"),
                _slide(5, slide_purpose="sources"),
            ]
        }
        result = attach_cadence_report(
            content, route="opc", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertTrue(result["visual_cadence"]["pass"])
        self.assertEqual(result["visual_cadence"]["violations"], [])

    def test_flag_on_none_content_returns_none(self):
        result = attach_cadence_report(
            None, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertIsNone(result)

    def test_flag_truthy_values(self):
        self.assertFalse(cadence_gate_enabled({}))
        self.assertFalse(cadence_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "0"}))
        self.assertTrue(cadence_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "1"}))
        self.assertTrue(cadence_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "true"}))


if __name__ == "__main__":
    unittest.main()
