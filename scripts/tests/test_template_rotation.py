"""Tests for content_creator template rotation scoring."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

import main as content_main  # noqa: E402


class TemplateRotationTest(unittest.TestCase):
    def test_educational_topic_picks_explainer(self):
        picked = content_main._pick_template_by_topic(
            "What is socialism and why does the definition matter?",
            "usa",
            recent_templates=[],
        )
        self.assertEqual(picked, "educational-explainer")

    def test_brazil_definition_topic_picks_explainer(self):
        picked = content_main._pick_template_by_topic(
            "What is a court injunction and why does it matter?",
            "brazil",
            recent_templates=[],
        )
        self.assertEqual(picked, "educational-explainer")

    def test_opc_progress_topic_picks_progress(self):
        picked = content_main._pick_template_by_topic(
            "Before and after progress from a kitchen demolition jobsite",
            "opc",
            recent_templates=[],
        )
        self.assertEqual(picked, "progress")

    def test_recent_penalty_can_move_opc_back_to_tip(self):
        picked = content_main._pick_template_by_topic(
            "Project progress after framing inspection",
            "opc",
            recent_templates=["progress", "progress", "progress"],
        )
        self.assertEqual(picked, "tip")

    def test_explicit_news_template_still_wins(self):
        entry = {"template_key": "educational-explainer"}
        picked = content_main._resolve_news_template(
            entry,
            "usa",
            topic="breaking vote",
            recent_templates=["educational-explainer"],
        )
        self.assertEqual(picked, "educational-explainer")

    def test_explicit_native_returns_none_for_existing_renderer_contract(self):
        entry = {"template_key": "native"}
        picked = content_main._resolve_news_template(
            entry,
            "brazil",
            topic="what is a court rule",
            recent_templates=[],
        )
        self.assertIsNone(picked)


if __name__ == "__main__":
    unittest.main()
