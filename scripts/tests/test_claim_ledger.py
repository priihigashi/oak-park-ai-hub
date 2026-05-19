"""Tests for SH-146 route-specific claim ledger contract."""

import json
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

from claim_ledger import (  # noqa: E402
    ClaimLedgerError,
    attach_claim_ledger,
    build_claim_ledger,
    build_news_claim_ledger,
    build_opc_claim_ledger,
    claim_ledger_enabled,
)


class ClaimLedgerContractTest(unittest.TestCase):
    def sample_opc_content(self):
        return {
            "headline": "3 COSTLY MISTAKES",
            "subhead": "$20K mistake before you sign",
            "hook_answer": "The mistake: skipping the slope calculation before pouring.",
            "slide2_headline": "REAL COST",
            "slide2_stat": "UP TO $20K",
            "slide2_label": "Drainage repairs depend on scope (FBC + contractor estimate).",
            "slide3_items": [{"title": "Slope", "sub": "Water follows gravity toward the slab."}],
            "slide4_headline": "CHECK SLOPE FIRST",
            "slide4_body": "Ask for the slope calculation before signing.",
            "payoff": "Ask for slope calculation before quote approval.",
            "sources": ["Florida Building Code", "UF IFAS"],
        }

    def sample_news_content(self):
        return {
            "cover_pt": "O NÚMERO REAL",
            "cover_en": "The real number",
            "cover_claim": "O Brasil gasta 3x mais.",
            "claim_status": "PARCIALMENTE CORRETO",
            "cover_credibility_badge": "MÉDIA CREDIBILIDADE",
            "slides": [{"type": "data", "heading_pt": "O que os dados dizem"}],
            "sources": ["CNJ", "G1"],
        }

    def test_opc_ledger_shape_is_homeowner_specific(self):
        ledger = build_opc_claim_ledger(self.sample_opc_content())
        self.assertEqual(ledger["schema_version"], "claim_ledger.v0.1")
        self.assertEqual(ledger["sh_id"], "SH-146")
        self.assertEqual(ledger["route"], "opc")
        self.assertEqual(ledger["claim_model"], "homeowner_decision")
        self.assertIn("risk_or_cost", ledger["claims"])
        self.assertIn("recommended_action", ledger["claims"])
        self.assertNotIn("core_claim", ledger["claims"])

    def test_news_ledger_shape_is_evidence_status_specific(self):
        ledger = build_news_claim_ledger(self.sample_news_content())
        self.assertEqual(ledger["route"], "news")
        self.assertEqual(ledger["claim_model"], "fact_status")
        self.assertIn("core_claim", ledger["claims"])
        self.assertIn("reported_evidence", ledger["claims"])
        self.assertNotIn("recommended_action", ledger["claims"])

    def test_dispatch_maps_brazil_and_usa_to_news(self):
        self.assertEqual(build_claim_ledger(self.sample_news_content(), route="brazil")["route"], "news")
        self.assertEqual(build_claim_ledger(self.sample_news_content(), route="usa")["route"], "news")

    def test_unrouted_and_unknown_routes_raise(self):
        with self.assertRaises(ClaimLedgerError):
            build_claim_ledger(self.sample_opc_content(), route="unrouted")
        with self.assertRaises(ClaimLedgerError):
            build_claim_ledger(self.sample_opc_content(), route="stocks")

    def test_flag_off_returns_same_object_and_snapshot(self):
        content = self.sample_opc_content()
        before = json.dumps(content, sort_keys=True)
        result = attach_claim_ledger(content, route="opc", env={"STORY_PIPELINE_V2_ENABLED": "0"})
        self.assertIs(result, content)
        self.assertEqual(json.dumps(result, sort_keys=True), before)
        self.assertNotIn("claim_ledger", content)

    def test_flag_on_attaches_ledger_without_mutating_input(self):
        content = self.sample_opc_content()
        result = attach_claim_ledger(content, route="opc", env={"STORY_PIPELINE_V2_ENABLED": "1"})
        self.assertIsNot(result, content)
        self.assertNotIn("claim_ledger", content)
        self.assertEqual(result["claim_ledger"]["route"], "opc")

    def test_flag_truthy_values_match_story_pipeline_flag(self):
        self.assertFalse(claim_ledger_enabled({}))
        self.assertFalse(claim_ledger_enabled({"STORY_PIPELINE_V2_ENABLED": "0"}))
        self.assertTrue(claim_ledger_enabled({"STORY_PIPELINE_V2_ENABLED": "1"}))
        self.assertTrue(claim_ledger_enabled({"STORY_PIPELINE_V2_ENABLED": "true"}))


if __name__ == "__main__":
    unittest.main()
