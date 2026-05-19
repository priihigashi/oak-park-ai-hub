"""Integration tests for SH-145/STORY-001 metadata attachment."""

import os
import json
import unittest
from pathlib import Path
import sys
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

import carousel_builder  # noqa: E402


class StoryPipelineIntegrationTest(unittest.TestCase):
    def sample_content(self):
        return {
            "headline": "3 COSTLY MISTAKES",
            "subhead": "$20K mistake before you sign",
            "hook_frame": "costly_mistake",
            "viewer_question": "Am I making this mistake right now?",
            "cta": "SAVE BEFORE YOUR NEXT BID.",
            "sources": ["Florida Building Code", "UF IFAS"],
            "slides": [
                {"slide": 2, "visual_hint": "context-image", "context_image_query": "concrete patio drainage residential"},
                {"slide": 3, "visual_hint": "context-image", "context_image_query": "channel drain installation patio"},
                {"slide": 4, "visual_hint": "context-image", "context_image_query": "contractor level patio slope"},
            ],
        }

    def test_flag_off_returns_generator_content_object_unchanged(self):
        content = self.sample_content()
        before = json.dumps(content, sort_keys=True)
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "0"}, clear=False):
            with patch.object(carousel_builder, "generate_progress_content", return_value=content):
                result = carousel_builder.generate_carousel_content("Patio drainage", "opc", template_key="progress")

        self.assertIs(result, content)
        self.assertEqual(json.dumps(result, sort_keys=True), before)
        self.assertNotIn("story_outline", result)
        self.assertNotIn("editorial_contract", result)

    def test_flag_on_attaches_story_outline_and_opc_contract(self):
        content = self.sample_content()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            with patch.object(carousel_builder, "generate_progress_content", return_value=content):
                result = carousel_builder.generate_carousel_content("Patio drainage", "opc", template_key="progress")

        self.assertIsNot(result, content)
        self.assertNotIn("story_outline", content)
        self.assertEqual(result["story_outline"]["route"], "opc")
        self.assertEqual(result["editorial_contract"], {"route": "opc", "version": "0.1.0-stub", "loaded": False})

    def test_flag_on_maps_brazil_route_to_news_contract(self):
        content = self.sample_content()
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            with patch.object(carousel_builder, "generate_brazil_content", return_value=content):
                result = carousel_builder.generate_carousel_content("Brazil topic", "brazil")

        self.assertEqual(result["story_outline"]["route"], "brazil")
        self.assertEqual(result["editorial_contract"], {"route": "news", "version": "0.1.0-stub", "loaded": False})


if __name__ == "__main__":
    unittest.main()
