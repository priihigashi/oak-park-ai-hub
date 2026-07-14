"""Tests for FORMAT-021 voice/personality gate."""

import json
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

from voice_personality_gate import (  # noqa: E402
    attach_voice_personality_report,
    check_voice_personality,
    normalize_hashtag_set,
    voice_gate_enabled,
)


class VoicePersonalityGateTest(unittest.TestCase):
    def test_flag_default_off(self):
        env = {k: v for k, v in os.environ.items() if k != "VOICE_GATE_ENABLED"}
        self.assertFalse(voice_gate_enabled(env))

    def test_banned_hook_detected_on_cover_and_first_slide(self):
        content = {
            "cover_en": "Did you know the law changed?",
            "slides": [{"hook": "Most people don't know this part."}],
        }
        kinds = [v.kind for v in check_voice_personality(content, route="usa")]
        self.assertEqual(kinds.count("banned_hook"), 2)

    def test_personality_example_not_flagged(self):
        content = {
            "cover_en": "Most people use these 3 words interchangeably. They mean completely different things.",
            "slides": [{"hook": "Here is the difference."}],
        }
        self.assertEqual(check_voice_personality(content, route="usa"), [])

    def test_bibliography_only_sources_flagged(self):
        content = {
            "sources": [
                "Reuters — June 8, 2026",
                "AP News — 2026-06-08",
                "BBC — 2025",
            ]
        }
        violations = check_voice_personality(content, route="usa")
        self.assertEqual([v.kind for v in violations], ["bibliography_sources"])

    def test_sources_with_context_pass(self):
        content = {
            "sources": [
                "Reuters — June 8, 2026 — explains the vote timeline.",
                "AP News — 2026-06-08 — reported the court filing.",
            ]
        }
        self.assertEqual(check_voice_personality(content, route="usa"), [])

    def test_parallel_bland_grid_flagged(self):
        content = {
            "comparison_grid": {
                "columns": [
                    {"label": "Before", "items": ["A", "B"]},
                    {"label": "After", "items": ["C"]},
                ]
            }
        }
        kinds = [v.kind for v in check_voice_personality(content, route="usa")]
        self.assertIn("parallel_bland_grid", kinds)

    def test_comparison_grid_with_three_items_passes(self):
        content = {
            "comparison_grid": {
                "columns": [
                    {
                        "label": "Capitalismo",
                        "items": [
                            "Markets set most prices.",
                            "Private ownership drives investment.",
                            "Profit decides what expands.",
                        ],
                    },
                    {
                        "label": "Socialismo",
                        "items": [
                            "Public planning shapes priorities.",
                            "Collective ownership is the goal.",
                            "Distribution is part of the debate.",
                        ],
                    },
                ]
            }
        }
        self.assertEqual(check_voice_personality(content, route="usa"), [])

    def test_recycled_hashtag_block_flagged(self):
        tags = "#policy #history #context #news"
        content = {"in_post_hashtags": tags}
        recent = [normalize_hashtag_set("#other #tags"), normalize_hashtag_set(tags)]
        kinds = [v.kind for v in check_voice_personality(content, route="usa", recent_hashtag_sets=recent)]
        self.assertIn("recycled_hashtag_block", kinds)

    def test_attach_report_flag_off_same_object(self):
        content = {"cover_en": "Did you know this?"}
        before = json.dumps(content, sort_keys=True)
        out = attach_voice_personality_report(content, route="usa", env={"VOICE_GATE_ENABLED": "0"})
        self.assertIs(out, content)
        self.assertEqual(json.dumps(out, sort_keys=True), before)

    def test_attach_report_flag_on_deep_copy(self):
        content = {"cover_en": "Did you know this?"}
        out = attach_voice_personality_report(content, route="usa", env={"VOICE_GATE_ENABLED": "1"})
        self.assertIsNot(out, content)
        self.assertNotIn("voice_personality_gate", content)
        self.assertFalse(out["voice_personality_gate"]["pass"])


if __name__ == "__main__":
    unittest.main()
