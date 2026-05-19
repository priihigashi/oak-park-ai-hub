"""Tests for SH-145 Story Outline Contract.

These tests intentionally exercise the pure helper module only. Pipeline wiring is
kept out of this PR because the large renderer is high-risk; integration should be
one additive hook after this contract is reviewed.
"""

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

from story_outline import (  # noqa: E402
    build_story_outline,
    attach_story_outline,
    default_spine,
    story_pipeline_enabled,
)


class StoryOutlineContractTest(unittest.TestCase):
    def sample_opc_content(self):
        return {
            "headline": "3 COSTLY MISTAKES",
            "subhead": "$20K mistake before you sign",
            "hook_frame": "costly_mistake",
            "viewer_question": "Am I making this mistake right now?",
            "payoff": "Ask for slope calculation before quote approval.",
            "why_this_matters_now": "Rainy season exposes patio drainage problems.",
            "proof_needed": "FBC drainage rule + contractor estimate context",
            "cta": "SAVE BEFORE YOUR NEXT BID.",
            "sources": ["Florida Building Code", "UF IFAS"],
            "slides": [
                {"slide": 2, "visual_hint": "context-image", "context_image_query": "concrete patio drainage residential"},
                {"slide": 3, "visual_hint": "context-image", "context_image_query": "channel drain installation patio"},
                {"slide": 4, "visual_hint": "context-image", "context_image_query": "contractor level patio slope"},
            ],
        }

    def test_flag_off_returns_same_object_unchanged(self):
        content = self.sample_opc_content()
        result = attach_story_outline(content, topic="Patio drainage", niche="opc", env={"STORY_PIPELINE_V2_ENABLED": "0"})
        self.assertIs(result, content)
        self.assertNotIn("story_outline", content)

    def test_flag_on_attaches_additive_opc_outline_without_mutating_input(self):
        content = self.sample_opc_content()
        result = attach_story_outline(content, topic="Patio drainage", niche="opc", env={"STORY_PIPELINE_V2_ENABLED": "1"})
        self.assertIsNot(result, content)
        self.assertNotIn("story_outline", content)
        outline = result["story_outline"]
        self.assertEqual(outline["schema_version"], "story_outline.v0.1")
        self.assertEqual(outline["sh_id"], "SH-145")
        self.assertEqual(outline["route"], "opc")
        self.assertEqual(outline["spine"], ["hook", "cost", "teach", "apply", "sources"])
        self.assertEqual(len(outline["slides"]), 5)
        self.assertEqual(outline["slides"][0]["purpose"], "hook")
        self.assertIn("viewer_question", outline["route_extension"])

    def test_news_default_spines_match_five_and_six_slide_contracts(self):
        self.assertEqual(
            default_spine("brazil", 5),
            ["claim", "number", "evidence", "opposition+implication", "sources"],
        )
        self.assertEqual(
            default_spine("usa", 6),
            ["claim", "number", "evidence", "opposition", "implication", "sources"],
        )

    def test_content_slide_purposes_override_defaults_by_slide_number(self):
        content = self.sample_opc_content()
        content["slide_purposes"] = [
            {"slide": 1, "purpose": "hook"},
            {"slide": 2, "purpose": "cost"},
            {"slide": 3, "purpose": "teach"},
            {"slide": 4, "purpose": "apply"},
            {"slide": 5, "purpose": "sources"},
        ]
        outline = build_story_outline(content, topic="Patio drainage", niche="opc", slide_count=5)
        self.assertEqual(outline["spine"], ["hook", "cost", "teach", "apply", "sources"])

    def test_story_pipeline_enabled_accepts_only_explicit_truthy_values(self):
        self.assertFalse(story_pipeline_enabled({}))
        self.assertFalse(story_pipeline_enabled({"STORY_PIPELINE_V2_ENABLED": "0"}))
        self.assertTrue(story_pipeline_enabled({"STORY_PIPELINE_V2_ENABLED": "1"}))
        self.assertTrue(story_pipeline_enabled({"STORY_PIPELINE_V2_ENABLED": "true"}))


if __name__ == "__main__":
    unittest.main()
