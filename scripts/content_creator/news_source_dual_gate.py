"""SH-151 — News source dual-gate contract.

Validates that News-route confirmed claims have at least 2 independent
outlets and that banned/inspiration-only sources are never cited.
Pure validation helper. No LLM, no integration into production
reviewer/auditor yet — that ships as a separate audit-required PR.

Rule sources:
- CLAUDE.md "NEWS source dual-gate" — confirmed claims need 2+ independent sources
- CLAUDE.md "FORMAT-024 / Verdade Pela Metade" — do NOT cite @marceloem23 as source
- memory feedback_per_post_editorial_log.md
- memory project_series_quem_decidiu_isso.md

Validator inputs (caller-provided dict shape):

    content = {
        "claims": [
            {
                "text": "...",
                "status": "confirmed" | "allegation" | "interpretation" | ...,
                "sources": ["Folha", "G1", ...],
            },
            ...
        ]
    }

OPC route is a no-op (rule doesn't apply). News routes (brazil/usa)
enforce the dual-source rule. Unrouted raises.

Violation kinds:
- ``banned_source_used``: claim cites a source on the banned list (e.g. @marceloem23)
- ``insufficient_independent_sources``: confirmed claim has fewer than 2 unique
  outlets after normalization (covers zero-source, single-source, and
  duplicate-outlet cases)
"""

from __future__ import annotations

import os
import re
from copy import deepcopy
from dataclasses import dataclass
from typing import Any


_FLAG = "STORY_PIPELINE_V2_ENABLED"

_NEWS_ALIASES = {
    "news", "brazil", "usa", "br", "us",
    "brazil_news", "usa_news", "news_brazil", "news_usa",
}
_OPC_ALIASES = {"opc", "content", "oak_park", "oak-park"}

# Statuses that mean "this claim is presented as confirmed fact".
# Caller-supplied status string is lowercased + trimmed before comparison.
_CONFIRMED_STATUSES = {
    "confirmed", "confirm", "correct", "true", "fact", "verified",
    "confirmado", "correto", "verdadeiro", "verificado", "fato",
}

# Sources that must NEVER be cited as primary evidence.
# FORMAT-024 (Verdade Pela Metade): cite original source/evidence, not
# inspiration accounts.
_DEFAULT_BANNED_SOURCES = frozenset({
    "@marceloem23",
})

# Outlet-suffix tokens stripped during normalization so "G1 Globo" and "G1"
# count as the same outlet, and parenthetical context "(Brasil)" is ignored.
_NORMALIZATION_STRIP = re.compile(r"\b(globo|brasil|news|com|br|globe|press|jornal|paper)\b", re.IGNORECASE)
_PUNCT_RE = re.compile(r"[^\w@\-]+", re.UNICODE)
_SPACE_RUN = re.compile(r"\s+")


class NewsSourceDualGateError(ValueError):
    """Raised when the news source dual-gate cannot run for the requested route."""


def news_source_dual_gate_enabled(env: dict[str, str] | None = None) -> bool:
    """Return True only when the storytelling pipeline flag is explicitly enabled."""
    source = os.environ if env is None else env
    return str(source.get(_FLAG, "0")).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_news_route(route: str) -> str:
    value = (route or "").strip().lower()
    if value in _OPC_ALIASES:
        return "opc"
    if value in _NEWS_ALIASES:
        return "news"
    if value == "unrouted":
        raise NewsSourceDualGateError("Cannot run news source dual-gate for unrouted content")
    raise NewsSourceDualGateError(f"Unknown news source dual-gate route: {route!r}")


@dataclass(frozen=True)
class SourceViolation:
    kind: str
    claim_index: int
    claim_text: str
    detail: str


def _normalize_source(raw: str) -> str:
    """Return a normalized outlet key for independence comparison.

    Handles case, common suffixes (Globo / Brasil / News), punctuation,
    leading-``@`` handles (preserved so banned-source detection still
    works on the unnormalized form).
    """
    if not isinstance(raw, str):
        return ""
    s = raw.strip().lower()
    if not s:
        return ""
    # Preserve handle marker @ so banned-list matching still works.
    s = _PUNCT_RE.sub(" ", s)
    s = _NORMALIZATION_STRIP.sub(" ", s)
    s = _SPACE_RUN.sub(" ", s).strip()
    return s


def _banned_match(raw_source: str, banned: frozenset[str]) -> bool:
    if not isinstance(raw_source, str):
        return False
    canon = raw_source.strip().lower()
    for ban in banned:
        if canon == ban.lower():
            return True
        # Also catch wraps like "Inspired by @marceloem23"
        if ban.lower() in canon:
            return True
    return False


def _is_confirmed_status(status: Any) -> bool:
    if not isinstance(status, str):
        return False
    return status.strip().lower() in _CONFIRMED_STATUSES


def check_news_source_dual_gate(
    content: dict[str, Any],
    *,
    route: str,
    banned_sources: frozenset[str] | None = None,
) -> list[SourceViolation]:
    """Validate News claims against the dual-source + banned-source rules.

    Empty list = pass. OPC route returns []. News routes enforce the rule.
    """
    normalized_route = _normalize_news_route(route)
    if not isinstance(content, dict):
        raise NewsSourceDualGateError("content must be a dict")

    # Rule is News-only. OPC content is exempt.
    if normalized_route != "news":
        return []

    banned = banned_sources if banned_sources is not None else _DEFAULT_BANNED_SOURCES

    violations: list[SourceViolation] = []
    claims = content.get("claims")
    if not isinstance(claims, list):
        return violations

    for idx, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        text = str(claim.get("text") or claim.get("claim") or "").strip()
        sources_raw = claim.get("sources") or []
        if not isinstance(sources_raw, list):
            sources_raw = []

        # banned-source detection always runs (any status)
        banned_hits = [s for s in sources_raw if _banned_match(s, banned)]
        for hit in banned_hits:
            violations.append(
                SourceViolation(
                    kind="banned_source_used",
                    claim_index=idx,
                    claim_text=text,
                    detail=f"banned source {hit!r} cited — FORMAT-024 forbids inspiration accounts as evidence",
                )
            )

        # dual-source check only fires for confirmed claims
        if not _is_confirmed_status(claim.get("status")):
            continue

        # filter out banned + empty before counting independents
        clean_raw_sources = [s for s in sources_raw if isinstance(s, str) and s.strip() and not _banned_match(s, banned)]
        independent_outlets: list[str] = []
        seen_keys: set[str] = set()
        for raw in clean_raw_sources:
            key = _normalize_source(raw)
            if not key or key in seen_keys:
                continue
            seen_keys.add(key)
            independent_outlets.append(raw)

        if len(independent_outlets) < 2:
            violations.append(
                SourceViolation(
                    kind="insufficient_independent_sources",
                    claim_index=idx,
                    claim_text=text,
                    detail=(
                        f"confirmed claim has {len(independent_outlets)} independent outlet(s) "
                        f"(need >=2). Raw sources: {sources_raw!r}"
                    ),
                )
            )

    return violations


def attach_news_source_dual_gate_report(
    content: dict[str, Any] | None,
    *,
    route: str,
    env: dict[str, str] | None = None,
    banned_sources: frozenset[str] | None = None,
) -> dict[str, Any] | None:
    """Attach ``news_source_dual_gate`` when STORY_PIPELINE_V2_ENABLED is on.

    Flag OFF -> returns the input object unchanged (same identity).
    Flag ON  -> deep-copies, attaches schema, returns the copy.
    """
    if content is None or not news_source_dual_gate_enabled(env):
        return content
    if not isinstance(content, dict):
        raise NewsSourceDualGateError("content must be a dict or None")

    normalized = _normalize_news_route(route)
    violations = check_news_source_dual_gate(content, route=route, banned_sources=banned_sources)
    updated = deepcopy(content)
    updated["news_source_dual_gate"] = {
        "schema_version": "news_source_dual_gate.v0.1",
        "sh_id": "SH-151",
        "route": normalized,
        "applies": normalized == "news",
        "violations": [
            {
                "kind": v.kind,
                "claim_index": v.claim_index,
                "claim_text": v.claim_text,
                "detail": v.detail,
            }
            for v in violations
        ],
        "pass": len(violations) == 0,
    }
    return updated
