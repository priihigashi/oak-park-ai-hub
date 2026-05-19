"""Tests for SH-147 named-person face gate contract."""

import json
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

from named_person_face_gate import (  # noqa: E402
    FaceViolation,
    NamedPersonFaceGateError,
    attach_face_gate_report,
    check_named_person_face_coverage,
    face_gate_enabled,
)


class NamedPersonFaceGateTest(unittest.TestCase):
    def _slide_named_no_face(self):
        return {
            "slide": 2,
            "body_pt": "Segundo o senador <strong>Marcelo Castro</strong>, a CPI foi suspensa.",
        }

    def _slide_named_with_sticker(self):
        return {
            "slide": 2,
            "body_pt": "<strong>Marcelo Castro</strong> declarou hoje.",
            "sticker_slot": "marcelo_castro.png",
        }

    def _slide_named_with_bio_card_photo(self):
        return {
            "slide": 3,
            "body": "<strong>Mike McFolling</strong> says new construction permits stalled.",
            "bio_cards": [{"name": "Mike McFolling", "photo": "mike.png"}],
        }

    def _slide_named_with_bio_card_initials(self):
        return {
            "slide": 3,
            "body": "Senator <strong>Jane Doe</strong> blocked the vote.",
            "bio_cards": [{"name": "Jane Doe", "initials": "JD"}],
        }

    def _slide_named_with_html_sticker(self):
        return {
            "slide": 4,
            "body": "Representative <strong>Carlos Silva</strong> abstained.",
            "rendered_html": "<div class='sticker-slot'><img src='carlos.png'/></div>",
        }

    def _slide_no_named_person(self):
        return {
            "slide": 2,
            "body": "The concrete patio needs proper drainage and a 1/4 inch per foot slope.",
        }

    def _slide_named_in_multiple_languages(self):
        return {
            "slide": 5,
            "body_pt": "<strong>Lula da Silva</strong> recebeu o relatório.",
            "body_en": "<strong>Lula da Silva</strong> received the report.",
        }

    # --- core detection -----------------------------------------------------

    def test_named_person_without_face_triggers_violation(self):
        content = {"slides": [self._slide_named_no_face()]}
        violations = check_named_person_face_coverage(content, route="brazil")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].person_name, "Marcelo Castro")
        self.assertEqual(violations[0].slide_index, 2)
        self.assertIn("no face treatment", violations[0].reason)

    def test_named_person_with_sticker_passes(self):
        content = {"slides": [self._slide_named_with_sticker()]}
        self.assertEqual(check_named_person_face_coverage(content, route="brazil"), [])

    def test_named_person_with_bio_card_photo_passes(self):
        content = {"slides": [self._slide_named_with_bio_card_photo()]}
        self.assertEqual(check_named_person_face_coverage(content, route="opc"), [])

    def test_named_person_with_bio_card_initials_passes(self):
        content = {"slides": [self._slide_named_with_bio_card_initials()]}
        self.assertEqual(check_named_person_face_coverage(content, route="opc"), [])

    def test_named_person_with_html_sticker_class_passes(self):
        content = {"slides": [self._slide_named_with_html_sticker()]}
        self.assertEqual(check_named_person_face_coverage(content, route="brazil"), [])

    def test_no_named_person_no_violation(self):
        content = {"slides": [self._slide_no_named_person()]}
        self.assertEqual(check_named_person_face_coverage(content, route="opc"), [])

    def test_duplicate_name_across_languages_counted_once_per_slide(self):
        content = {"slides": [self._slide_named_in_multiple_languages()]}
        violations = check_named_person_face_coverage(content, route="brazil")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].person_name, "Lula da Silva")

    def test_mixed_slides_only_flag_offenders(self):
        content = {
            "slides": [
                self._slide_named_with_sticker(),       # pass
                self._slide_no_named_person(),          # pass (no name)
                self._slide_named_no_face(),            # FAIL
                self._slide_named_with_bio_card_photo(),# pass
            ]
        }
        violations = check_named_person_face_coverage(content, route="brazil")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].person_name, "Marcelo Castro")

    # --- route handling -----------------------------------------------------

    def test_unrouted_raises(self):
        with self.assertRaises(NamedPersonFaceGateError):
            check_named_person_face_coverage({"slides": []}, route="unrouted")

    def test_unknown_route_raises(self):
        with self.assertRaises(NamedPersonFaceGateError):
            check_named_person_face_coverage({"slides": []}, route="stocks")

    def test_route_aliases_resolve(self):
        # all of these must not raise
        for route in ("opc", "OPC", "oak-park", "news", "brazil", "usa", "br", "us"):
            check_named_person_face_coverage({"slides": []}, route=route)

    # --- attach_face_gate_report (flag-gated) -------------------------------

    def test_flag_off_returns_same_object_and_byte_identical(self):
        content = {"slides": [self._slide_named_no_face()]}
        before = json.dumps(content, sort_keys=True)
        result = attach_face_gate_report(
            content, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "0"}
        )
        self.assertIs(result, content)
        self.assertEqual(json.dumps(result, sort_keys=True), before)
        self.assertNotIn("face_gate", content)

    def test_flag_off_default_env_returns_same_object(self):
        content = {"slides": [self._slide_named_no_face()]}
        # No STORY_PIPELINE_V2_ENABLED in env => default off
        env_without_flag = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_ENABLED"}
        result = attach_face_gate_report(content, route="brazil", env=env_without_flag)
        self.assertIs(result, content)

    def test_flag_on_attaches_report_without_mutating_input(self):
        content = {"slides": [self._slide_named_no_face()]}
        result = attach_face_gate_report(
            content, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertIsNot(result, content)
        self.assertNotIn("face_gate", content)
        self.assertEqual(result["face_gate"]["sh_id"], "SH-147")
        self.assertEqual(result["face_gate"]["route"], "news")
        self.assertFalse(result["face_gate"]["pass"])
        self.assertEqual(len(result["face_gate"]["violations"]), 1)
        self.assertEqual(result["face_gate"]["violations"][0]["person_name"], "Marcelo Castro")

    def test_flag_on_pass_when_face_present(self):
        content = {"slides": [self._slide_named_with_sticker()]}
        result = attach_face_gate_report(
            content, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertTrue(result["face_gate"]["pass"])
        self.assertEqual(result["face_gate"]["violations"], [])

    def test_flag_on_none_content_returns_none(self):
        result = attach_face_gate_report(
            None, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertIsNone(result)

    def test_flag_truthy_values(self):
        self.assertFalse(face_gate_enabled({}))
        self.assertFalse(face_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "0"}))
        self.assertTrue(face_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "1"}))
        self.assertTrue(face_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "true"}))
        self.assertTrue(face_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "TRUE"}))
        self.assertTrue(face_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "yes"}))


if __name__ == "__main__":
    unittest.main()
