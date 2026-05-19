"""Tests for SH-149 motion/static sibling folder gate contract."""

import json
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

from motion_static_sibling_gate import (  # noqa: E402
    MotionStaticSiblingGateError,
    MotionStaticViolation,
    attach_motion_static_report,
    check_motion_static_siblings,
    motion_static_gate_enabled,
)


def _build(static_files=None, motion_files=None, static_only=False):
    return {
        "static_only": static_only,
        "build_artifacts": {
            "static_files": list(static_files or []),
            "motion_files": list(motion_files or []),
        },
    }


class MotionStaticSiblingGateTest(unittest.TestCase):
    # --- happy paths -------------------------------------------------------

    def test_full_motion_build_passes(self):
        content = _build(
            static_files=["slide1.png", "slide2.png", "slide3.png"],
            motion_files=[
                "carousel.mp4",
                "carousel.gif",
                "cover_preview.png",
                "slide2_motion.png",
                "slide3_motion.png",
            ],
        )
        self.assertEqual(check_motion_static_siblings(content, route="opc"), [])

    def test_static_only_override_skips_motion_checks(self):
        content = _build(
            static_files=["slide1.png", "slide2.png"],
            motion_files=[],
            static_only=True,
        )
        self.assertEqual(check_motion_static_siblings(content, route="brazil"), [])

    # --- single-violation paths -------------------------------------------

    def test_missing_static_files_violation(self):
        content = _build(
            static_files=[],
            motion_files=["carousel.mp4", "carousel.gif", "cover_preview.png"],
        )
        violations = check_motion_static_siblings(content, route="opc")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].kind, "missing_static")

    def test_empty_motion_violation(self):
        content = _build(static_files=["slide1.png"], motion_files=[])
        violations = check_motion_static_siblings(content, route="opc")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].kind, "empty_motion")

    def test_missing_mp4_only(self):
        content = _build(
            static_files=["slide1.png"],
            motion_files=["carousel.gif", "cover_preview.png"],
        )
        kinds = [v.kind for v in check_motion_static_siblings(content, route="opc")]
        self.assertIn("missing_mp4", kinds)
        self.assertNotIn("missing_gif", kinds)
        self.assertNotIn("missing_preview", kinds)

    def test_missing_gif_only(self):
        content = _build(
            static_files=["slide1.png"],
            motion_files=["carousel.mp4", "cover_preview.png"],
        )
        kinds = [v.kind for v in check_motion_static_siblings(content, route="opc")]
        self.assertIn("missing_gif", kinds)
        self.assertNotIn("missing_mp4", kinds)
        self.assertNotIn("missing_preview", kinds)

    def test_missing_preview_only(self):
        content = _build(
            static_files=["slide1.png"],
            motion_files=["carousel.mp4", "carousel.gif", "slide2_motion.png"],
        )
        kinds = [v.kind for v in check_motion_static_siblings(content, route="opc")]
        self.assertIn("missing_preview", kinds)
        self.assertNotIn("missing_mp4", kinds)
        self.assertNotIn("missing_gif", kinds)

    def test_multiple_violations_emitted_together(self):
        content = _build(
            static_files=[],
            motion_files=["carousel.mp4"],  # missing gif + preview, plus missing static
        )
        kinds = sorted(v.kind for v in check_motion_static_siblings(content, route="opc"))
        self.assertEqual(kinds, ["missing_gif", "missing_preview", "missing_static"])

    # --- preview frame detection ------------------------------------------

    def test_preview_filenames_accepted(self):
        for name in (
            "preview.png",
            "cover_preview.png",
            "carousel_thumb.png",
            "first_frame.png",
            "first-frame.png",
            "cover.png",
            "v1_topic_cover.png",
            "video_thumbnail.png",
        ):
            content = _build(
                static_files=["slide1.png"],
                motion_files=["c.mp4", "c.gif", name],
            )
            kinds = [v.kind for v in check_motion_static_siblings(content, route="opc")]
            self.assertNotIn("missing_preview", kinds, f"preview name {name!r} not accepted")

    def test_non_preview_png_does_not_satisfy_preview_requirement(self):
        content = _build(
            static_files=["slide1.png"],
            motion_files=["c.mp4", "c.gif", "slide2_motion.png"],
        )
        kinds = [v.kind for v in check_motion_static_siblings(content, route="opc")]
        self.assertIn("missing_preview", kinds)

    # --- file extension robustness ----------------------------------------

    def test_mp4_extension_case_insensitive(self):
        content = _build(
            static_files=["s.png"],
            motion_files=["CAROUSEL.MP4", "c.gif", "preview.png"],
        )
        self.assertEqual(check_motion_static_siblings(content, route="opc"), [])

    def test_m4v_counts_as_mp4(self):
        content = _build(
            static_files=["s.png"],
            motion_files=["carousel.m4v", "c.gif", "preview.png"],
        )
        self.assertEqual(check_motion_static_siblings(content, route="opc"), [])

    def test_files_with_paths_are_handled(self):
        content = _build(
            static_files=["png/slide1.png"],
            motion_files=["motion/carousel.mp4", "motion/carousel.gif", "motion/preview.png"],
        )
        self.assertEqual(check_motion_static_siblings(content, route="brazil"), [])

    # --- route handling ----------------------------------------------------

    def test_unrouted_raises(self):
        with self.assertRaises(MotionStaticSiblingGateError):
            check_motion_static_siblings(_build(), route="unrouted")

    def test_unknown_route_raises(self):
        with self.assertRaises(MotionStaticSiblingGateError):
            check_motion_static_siblings(_build(), route="stocks")

    def test_route_aliases_resolve(self):
        for route in ("opc", "OPC", "oak-park", "news", "brazil", "usa", "br", "us"):
            check_motion_static_siblings(_build(static_files=["s.png"], static_only=True), route=route)

    # --- malformed input handling -----------------------------------------

    def test_missing_build_artifacts_dict_returns_violations(self):
        content = {}
        violations = check_motion_static_siblings(content, route="opc")
        kinds = sorted(v.kind for v in violations)
        self.assertEqual(kinds, ["empty_motion", "missing_static"])

    def test_non_list_static_files_treated_as_empty(self):
        content = {"build_artifacts": {"static_files": "slide1.png", "motion_files": ["c.mp4", "c.gif", "preview.png"]}}
        kinds = [v.kind for v in check_motion_static_siblings(content, route="opc")]
        self.assertIn("missing_static", kinds)

    def test_non_dict_content_raises(self):
        with self.assertRaises(MotionStaticSiblingGateError):
            check_motion_static_siblings("not a dict", route="opc")

    # --- attach_motion_static_report (flag-gated) -------------------------

    def test_flag_off_returns_same_object_and_byte_identical(self):
        content = _build(static_files=[], motion_files=[])
        before = json.dumps(content, sort_keys=True)
        result = attach_motion_static_report(
            content, route="opc", env={"STORY_PIPELINE_V2_ENABLED": "0"}
        )
        self.assertIs(result, content)
        self.assertEqual(json.dumps(result, sort_keys=True), before)
        self.assertNotIn("motion_static_sibling", content)

    def test_flag_off_default_env_returns_same_object(self):
        content = _build(static_files=["s.png"])
        env_without_flag = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_ENABLED"}
        result = attach_motion_static_report(content, route="opc", env=env_without_flag)
        self.assertIs(result, content)

    def test_flag_on_attaches_report_without_mutating_input(self):
        content = _build(static_files=[], motion_files=[])
        result = attach_motion_static_report(
            content, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertIsNot(result, content)
        self.assertNotIn("motion_static_sibling", content)
        self.assertEqual(result["motion_static_sibling"]["sh_id"], "SH-149")
        self.assertEqual(result["motion_static_sibling"]["route"], "news")
        self.assertFalse(result["motion_static_sibling"]["pass"])
        self.assertEqual(result["motion_static_sibling"]["static_only_override"], False)
        kinds = [v["kind"] for v in result["motion_static_sibling"]["violations"]]
        self.assertIn("missing_static", kinds)
        self.assertIn("empty_motion", kinds)

    def test_flag_on_pass_when_complete(self):
        content = _build(
            static_files=["s.png"],
            motion_files=["c.mp4", "c.gif", "preview.png"],
        )
        result = attach_motion_static_report(
            content, route="opc", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertTrue(result["motion_static_sibling"]["pass"])
        self.assertEqual(result["motion_static_sibling"]["violations"], [])

    def test_flag_on_static_only_reflected_in_report(self):
        content = _build(static_files=["s.png"], motion_files=[], static_only=True)
        result = attach_motion_static_report(
            content, route="opc", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertTrue(result["motion_static_sibling"]["static_only_override"])
        self.assertTrue(result["motion_static_sibling"]["pass"])

    def test_flag_on_none_content_returns_none(self):
        result = attach_motion_static_report(
            None, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertIsNone(result)

    def test_flag_truthy_values(self):
        self.assertFalse(motion_static_gate_enabled({}))
        self.assertFalse(motion_static_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "0"}))
        self.assertTrue(motion_static_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "1"}))
        self.assertTrue(motion_static_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "true"}))


if __name__ == "__main__":
    unittest.main()
