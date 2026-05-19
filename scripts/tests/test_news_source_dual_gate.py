"""Tests for SH-151 news source dual-gate contract."""

import json
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

from news_source_dual_gate import (  # noqa: E402
    NewsSourceDualGateError,
    SourceViolation,
    attach_news_source_dual_gate_report,
    check_news_source_dual_gate,
    news_source_dual_gate_enabled,
)


def _claim(text, status, sources):
    return {"text": text, "status": status, "sources": list(sources)}


class NewsSourceDualGateTest(unittest.TestCase):
    # --- happy paths ------------------------------------------------------

    def test_confirmed_claim_with_two_outlets_passes(self):
        content = {"claims": [_claim("X happened", "confirmed", ["Folha", "G1"])]}
        self.assertEqual(check_news_source_dual_gate(content, route="brazil"), [])

    def test_allegation_with_single_source_passes(self):
        content = {"claims": [_claim("Y allegedly", "allegation", ["Folha"])]}
        self.assertEqual(check_news_source_dual_gate(content, route="brazil"), [])

    def test_interpretation_with_no_sources_passes(self):
        content = {"claims": [_claim("Z analysis", "interpretation", [])]}
        self.assertEqual(check_news_source_dual_gate(content, route="brazil"), [])

    def test_opc_route_is_no_op_even_with_violations(self):
        content = {
            "claims": [
                _claim("Confirmed but single-sourced", "confirmed", ["G1"]),
                {"text": "uses banned source", "sources": ["@marceloem23"]},
            ]
        }
        self.assertEqual(check_news_source_dual_gate(content, route="opc"), [])

    # --- insufficient_independent_sources --------------------------------

    def test_confirmed_with_zero_sources_violates(self):
        content = {"claims": [_claim("X confirmed", "confirmed", [])]}
        violations = check_news_source_dual_gate(content, route="brazil")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].kind, "insufficient_independent_sources")
        self.assertIn("0 independent", violations[0].detail)

    def test_confirmed_with_single_source_violates(self):
        content = {"claims": [_claim("X confirmed", "confirmed", ["G1"])]}
        violations = check_news_source_dual_gate(content, route="brazil")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].kind, "insufficient_independent_sources")

    def test_confirmed_with_duplicate_outlet_normalized_violates(self):
        # G1 and "G1 Globo" should normalize to the same outlet
        content = {"claims": [_claim("X confirmed", "confirmed", ["G1", "G1 Globo"])]}
        violations = check_news_source_dual_gate(content, route="brazil")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].kind, "insufficient_independent_sources")

    def test_confirmed_with_two_different_outlets_passes_even_with_suffix(self):
        content = {"claims": [_claim("X confirmed", "confirmed", ["G1 Globo", "Folha"])]}
        self.assertEqual(check_news_source_dual_gate(content, route="brazil"), [])

    # --- banned_source_used ----------------------------------------------

    def test_banned_source_always_flagged(self):
        content = {"claims": [_claim("any claim", "allegation", ["@marceloem23"])]}
        violations = check_news_source_dual_gate(content, route="brazil")
        kinds = [v.kind for v in violations]
        self.assertIn("banned_source_used", kinds)

    def test_banned_source_inside_wrapping_text_flagged(self):
        content = {"claims": [_claim("any claim", "allegation", ["Inspired by @marceloem23"])]}
        violations = check_news_source_dual_gate(content, route="brazil")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].kind, "banned_source_used")

    def test_banned_source_does_not_count_toward_dual_source_for_confirmed(self):
        # Banned source + 1 real outlet = still insufficient
        content = {
            "claims": [
                _claim("X confirmed", "confirmed", ["@marceloem23", "G1"]),
            ]
        }
        kinds = sorted(v.kind for v in check_news_source_dual_gate(content, route="brazil"))
        self.assertEqual(kinds, ["banned_source_used", "insufficient_independent_sources"])

    def test_banned_source_plus_two_outlets_only_banned_violation(self):
        content = {
            "claims": [
                _claim("X confirmed", "confirmed", ["@marceloem23", "G1", "Folha"]),
            ]
        }
        kinds = [v.kind for v in check_news_source_dual_gate(content, route="brazil")]
        # banned still flagged, but independent source count satisfied (G1 + Folha)
        self.assertEqual(kinds, ["banned_source_used"])

    def test_custom_banned_list_overrides_default(self):
        # Default banned list flags @marceloem23. A custom list that does NOT
        # include @marceloem23 must NOT flag it. Two real outlets satisfy
        # the dual-source rule, so the whole claim passes.
        content = {"claims": [_claim("any claim", "confirmed", ["@marceloem23", "G1"])]}
        violations = check_news_source_dual_gate(
            content,
            route="brazil",
            banned_sources=frozenset({"@evilaccount"}),
        )
        # No banned violation (custom list respected) and no insufficient
        # violation (two distinct outlets).
        self.assertEqual(violations, [])

    def test_custom_banned_list_still_flags_listed_handle(self):
        content = {"claims": [_claim("any claim", "confirmed", ["@evilaccount", "G1", "Folha"])]}
        kinds = [
            v.kind
            for v in check_news_source_dual_gate(
                content, route="brazil", banned_sources=frozenset({"@evilaccount"})
            )
        ]
        self.assertEqual(kinds, ["banned_source_used"])

    # --- status detection -------------------------------------------------

    def test_confirmed_status_variants_all_trigger_rule(self):
        for status in ("confirmed", "CONFIRMED", "verified", "true", "fact", "confirmado", "verdadeiro"):
            content = {"claims": [_claim("x", status, ["G1"])]}
            violations = check_news_source_dual_gate(content, route="brazil")
            self.assertEqual(len(violations), 1, f"status {status!r} should trigger rule")
            self.assertEqual(violations[0].kind, "insufficient_independent_sources")

    def test_non_confirmed_status_skips_dual_source_check(self):
        for status in ("allegation", "interpretation", "rumor", "unverified", "", "unknown"):
            content = {"claims": [_claim("x", status, ["G1"])]}
            self.assertEqual(check_news_source_dual_gate(content, route="brazil"), [])

    def test_missing_status_skips_dual_source_check(self):
        content = {"claims": [{"text": "no status field", "sources": ["G1"]}]}
        self.assertEqual(check_news_source_dual_gate(content, route="brazil"), [])

    # --- multiple claims --------------------------------------------------

    def test_mixed_claim_set(self):
        content = {
            "claims": [
                _claim("pass1", "confirmed", ["Folha", "G1"]),       # pass
                _claim("fail1", "confirmed", ["UOL"]),                # insufficient
                _claim("pass2", "allegation", ["G1"]),                # pass (allegation)
                _claim("fail2", "confirmed", ["@marceloem23", "G1"]), # banned + insufficient
            ]
        }
        violations = check_news_source_dual_gate(content, route="brazil")
        # Expect: 1 insufficient (claim 1), 1 banned + 1 insufficient (claim 3)
        self.assertEqual(len(violations), 3)
        kinds_by_idx = sorted((v.claim_index, v.kind) for v in violations)
        self.assertEqual(kinds_by_idx, [
            (1, "insufficient_independent_sources"),
            (3, "banned_source_used"),
            (3, "insufficient_independent_sources"),
        ])

    # --- route handling ---------------------------------------------------

    def test_unrouted_raises(self):
        with self.assertRaises(NewsSourceDualGateError):
            check_news_source_dual_gate({}, route="unrouted")

    def test_unknown_route_raises(self):
        with self.assertRaises(NewsSourceDualGateError):
            check_news_source_dual_gate({}, route="stocks")

    def test_route_aliases_resolve(self):
        # News aliases enforce the rule; OPC aliases pass through as no-op
        for route in ("brazil", "usa", "br", "us", "news"):
            check_news_source_dual_gate({"claims": []}, route=route)
        for route in ("opc", "oak-park", "OPC"):
            self.assertEqual(check_news_source_dual_gate({"claims": []}, route=route), [])

    # --- malformed input --------------------------------------------------

    def test_missing_claims_field_returns_empty(self):
        self.assertEqual(check_news_source_dual_gate({}, route="brazil"), [])

    def test_non_list_claims_returns_empty(self):
        self.assertEqual(check_news_source_dual_gate({"claims": "not a list"}, route="brazil"), [])

    def test_non_dict_claim_skipped(self):
        content = {"claims": ["bad", _claim("good", "confirmed", ["G1", "Folha"])]}
        self.assertEqual(check_news_source_dual_gate(content, route="brazil"), [])

    def test_non_list_sources_treated_as_empty(self):
        content = {"claims": [{"text": "x", "status": "confirmed", "sources": "Folha"}]}
        violations = check_news_source_dual_gate(content, route="brazil")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].kind, "insufficient_independent_sources")

    def test_non_dict_content_raises(self):
        with self.assertRaises(NewsSourceDualGateError):
            check_news_source_dual_gate("not a dict", route="brazil")

    # --- attach_news_source_dual_gate_report (flag-gated) ---------------

    def test_flag_off_returns_same_object_and_byte_identical(self):
        content = {"claims": [_claim("x", "confirmed", ["G1"])]}
        before = json.dumps(content, sort_keys=True)
        result = attach_news_source_dual_gate_report(
            content, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "0"}
        )
        self.assertIs(result, content)
        self.assertEqual(json.dumps(result, sort_keys=True), before)
        self.assertNotIn("news_source_dual_gate", content)

    def test_flag_off_default_env_returns_same_object(self):
        content = {"claims": []}
        env_without_flag = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_ENABLED"}
        result = attach_news_source_dual_gate_report(content, route="brazil", env=env_without_flag)
        self.assertIs(result, content)

    def test_flag_on_attaches_report_for_news(self):
        content = {"claims": [_claim("x", "confirmed", ["G1"])]}
        result = attach_news_source_dual_gate_report(
            content, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertIsNot(result, content)
        self.assertNotIn("news_source_dual_gate", content)
        self.assertEqual(result["news_source_dual_gate"]["sh_id"], "SH-151")
        self.assertEqual(result["news_source_dual_gate"]["route"], "news")
        self.assertTrue(result["news_source_dual_gate"]["applies"])
        self.assertFalse(result["news_source_dual_gate"]["pass"])
        self.assertEqual(len(result["news_source_dual_gate"]["violations"]), 1)

    def test_flag_on_opc_report_marks_does_not_apply(self):
        content = {"claims": [_claim("x", "confirmed", ["G1"])]}  # would violate in news
        result = attach_news_source_dual_gate_report(
            content, route="opc", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertEqual(result["news_source_dual_gate"]["route"], "opc")
        self.assertFalse(result["news_source_dual_gate"]["applies"])
        self.assertTrue(result["news_source_dual_gate"]["pass"])
        self.assertEqual(result["news_source_dual_gate"]["violations"], [])

    def test_flag_on_pass_when_clean(self):
        content = {"claims": [_claim("x", "confirmed", ["G1", "Folha"])]}
        result = attach_news_source_dual_gate_report(
            content, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertTrue(result["news_source_dual_gate"]["pass"])
        self.assertEqual(result["news_source_dual_gate"]["violations"], [])

    def test_flag_on_none_content_returns_none(self):
        result = attach_news_source_dual_gate_report(
            None, route="brazil", env={"STORY_PIPELINE_V2_ENABLED": "1"}
        )
        self.assertIsNone(result)

    def test_flag_truthy_values(self):
        self.assertFalse(news_source_dual_gate_enabled({}))
        self.assertFalse(news_source_dual_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "0"}))
        self.assertTrue(news_source_dual_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "1"}))
        self.assertTrue(news_source_dual_gate_enabled({"STORY_PIPELINE_V2_ENABLED": "true"}))


if __name__ == "__main__":
    unittest.main()
