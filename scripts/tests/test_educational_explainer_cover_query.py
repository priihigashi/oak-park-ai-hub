"""Regression tests for FORMAT-021 educational explainer cover queries."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

from carousel_builder import _detect_bad_cover_query_in_explainer  # noqa: E402


class EducationalExplainerCoverQueryTest(unittest.TestCase):
    def test_rejects_literal_schema_placeholder(self):
        content = {
            "cover_visual": {
                "option_a": {
                    "search_query": "Wikimedia/Wikipedia search term",
                }
            }
        }
        self.assertEqual(
            _detect_bad_cover_query_in_explainer(content),
            "Wikimedia/Wikipedia search term",
        )

    def test_rejects_generic_search_term(self):
        content = {
            "cover_visual": {
                "option_a": {
                    "search_query": "search term",
                }
            }
        }
        self.assertEqual(_detect_bad_cover_query_in_explainer(content), "search term")

    def test_accepts_named_person(self):
        content = {
            "cover_visual": {
                "option_a": {
                    "search_query": "Earl Warren",
                }
            }
        }
        self.assertEqual(_detect_bad_cover_query_in_explainer(content), "")

    def test_missing_query_is_not_flagged_here(self):
        self.assertEqual(_detect_bad_cover_query_in_explainer({"cover_visual": {}}), "")


if __name__ == "__main__":
    unittest.main()
