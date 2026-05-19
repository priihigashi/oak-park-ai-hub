"""SH-146 route-specific claim ledger contract.

Pure, additive helper for future storytelling pipeline stages. This module does
not call LLMs and is not imported by production code yet.
"""

from __future__ import annotations

import os
from copy import deepcopy
from typing import Any


_FLAG = "STORY_PIPELINE_V2_ENABLED"

_NEWS_ALIASES = {"news", "brazil", "usa", "br", "us", "brazil_news", "usa_news", "news_brazil", "news_usa"}
_OPC_ALIASES = {"opc", "content", "oak_park", "oak-park"}


class ClaimLedgerError(ValueError):
    """Raised when a claim ledger cannot be built for the requested route."""


def claim_ledger_enabled(env: dict[str, str] | None = None) -> bool:
    """Return True only when the storytelling pipeline flag is explicitly enabled."""
    source = os.environ if env is None else env
    return str(source.get(_FLAG, "0")).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_claim_route(route: str) -> str:
    value = (route or "").strip().lower()
    if value in _OPC_ALIASES:
        return "opc"
    if value in _NEWS_ALIASES:
        return "news"
    if value == "unrouted":
        raise ClaimLedgerError("Cannot build claim ledger for unrouted content")
    raise ClaimLedgerError(f"Unknown claim ledger route: {route!r}")


def _present_fields(content: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: content.get(field) for field in fields if content.get(field) not in (None, "", [], {})}


def build_opc_claim_ledger(content: dict[str, Any]) -> dict[str, Any]:
    """Build the OPC/homeowner claim ledger shape."""
    if not isinstance(content, dict):
        raise ClaimLedgerError("content must be a dict")

    return {
        "schema_version": "claim_ledger.v0.1",
        "sh_id": "SH-146",
        "route": "opc",
        "claim_model": "homeowner_decision",
        "claims": {
            "hook": _present_fields(content, ["headline", "subhead", "hook_answer"]),
            "risk_or_cost": _present_fields(content, ["slide2_headline", "slide2_stat", "slide2_label"]),
            "teaching_points": content.get("slide3_items") if isinstance(content.get("slide3_items"), list) else [],
            "recommended_action": _present_fields(content, ["slide4_headline", "slide4_body", "payoff"]),
            "sources": content.get("sources") if isinstance(content.get("sources"), list) else [],
        },
        "source_requirements": {
            "numeric_claims_need_named_source": True,
            "consumer_quote_guides_are_primary_sources": False,
            "allowed_uncited_claim_type": "scope-dependent contractor estimate",
        },
    }


def build_news_claim_ledger(content: dict[str, Any]) -> dict[str, Any]:
    """Build the News/evidence-status claim ledger shape."""
    if not isinstance(content, dict):
        raise ClaimLedgerError("content must be a dict")

    return {
        "schema_version": "claim_ledger.v0.1",
        "sh_id": "SH-146",
        "route": "news",
        "claim_model": "fact_status",
        "claims": {
            "core_claim": _present_fields(content, ["cover_claim", "cover_pt", "cover_en"]),
            "fact_claims": _present_fields(content, ["claim_status", "cover_credibility_badge"]),
            "reported_evidence": content.get("slides") if isinstance(content.get("slides"), list) else [],
            "sources": content.get("sources") if isinstance(content.get("sources"), list) else [],
        },
        "source_requirements": {
            "separate_fact_allegation_interpretation": True,
            "confirmed_claims_prefer_two_independent_sources": True,
            "preserve_attribution_language": True,
        },
    }


def build_claim_ledger(content: dict[str, Any], *, route: str) -> dict[str, Any]:
    """Dispatch to the route-specific claim ledger builder."""
    normalized = _normalize_claim_route(route)
    if normalized == "opc":
        return build_opc_claim_ledger(content)
    return build_news_claim_ledger(content)


def attach_claim_ledger(
    content: dict[str, Any] | None,
    *,
    route: str,
    env: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    """Attach claim_ledger only when STORY_PIPELINE_V2_ENABLED is on."""
    if content is None or not claim_ledger_enabled(env):
        return content
    if not isinstance(content, dict):
        raise ClaimLedgerError("content must be a dict or None")

    updated = deepcopy(content)
    updated["claim_ledger"] = build_claim_ledger(updated, route=route)
    return updated
