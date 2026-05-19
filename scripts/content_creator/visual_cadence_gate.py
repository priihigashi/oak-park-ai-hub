"""SH-148 — Visual cadence gate contract.

Detects when a carousel ships with more than one consecutive text-only
middle slide. Pure validation helper. No LLM, no integration into
production reviewer/auditor yet — that ships as a separate audit-required PR.

Rule source: CLAUDE.md "VISUAL-EVERY-OTHER-SLIDE" section +
~/.claude/projects/-Users-priscilahigashi/memory/feedback_visual_every_other_slide.md

Reading of the rule (strictest interpretation):
- Cover slide (index 1 / slide=1) and sources slide are exempt
- For middle slides, max 1 consecutive ``visual_hint == "none"`` allowed
- 2+ consecutive ``none`` middle slides => violation

``carousel_builder.py`` emits ``visual_hint`` per slide with values:
``bio-card`` / ``product-photo`` / ``context-image`` / ``icon-row`` / ``none``.
Missing or empty visual_hint is treated as ``none`` (conservative).
"""

from __future__ import annotations

import os
from copy import deepcopy
from dataclasses import dataclass
from typing import Any


_FLAG = "STORY_PIPELINE_V2_ENABLED"

_NEWS_ALIASES = {
    "news", "brazil", "usa", "br", "us",
    "brazil_news", "usa_news", "news_brazil", "news_usa",
}
_OPC_ALIASES = {"opc", "content", "oak_park", "oak-park"}

# Hints that count as carrying a visual anchor
_VISUAL_ANCHOR_HINTS = {"bio-card", "product-photo", "context-image", "icon-row"}

# Maximum allowed consecutive text-only middle slides
_MAX_CONSECUTIVE_TEXT_ONLY = 1


class VisualCadenceGateError(ValueError):
    """Raised when the cadence gate cannot run for the requested route."""


def cadence_gate_enabled(env: dict[str, str] | None = None) -> bool:
    """Return True only when the storytelling pipeline flag is explicitly enabled."""
    source = os.environ if env is None else env
    return str(source.get(_FLAG, "0")).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_cadence_route(route: str) -> str:
    value = (route or "").strip().lower()
    if value in _OPC_ALIASES:
        return "opc"
    if value in _NEWS_ALIASES:
        return "news"
    if value == "unrouted":
        raise VisualCadenceGateError("Cannot run cadence gate for unrouted content")
    raise VisualCadenceGateError(f"Unknown cadence gate route: {route!r}")


@dataclass(frozen=True)
class CadenceViolation:
    start_slide_index: int
    end_slide_index: int
    consecutive_count: int
    reason: str


def _is_cover_slide(slide: dict[str, Any], position: int) -> bool:
    if position == 1:
        return True
    if slide.get("slide") == 1:
        return True
    if str(slide.get("type") or "").strip().lower() == "cover":
        return True
    if str(slide.get("slide_purpose") or "").strip().lower() == "hook" and position <= 1:
        return True
    return False


def _is_sources_slide(slide: dict[str, Any]) -> bool:
    purpose = str(slide.get("slide_purpose") or "").strip().lower()
    if purpose == "sources":
        return True
    slide_type = str(slide.get("type") or "").strip().lower()
    if slide_type in {"sources", "source"}:
        return True
    return False


def _has_visual_anchor(slide: dict[str, Any]) -> bool:
    hint = str(slide.get("visual_hint") or "").strip().lower()
    if hint in _VISUAL_ANCHOR_HINTS:
        return True
    # Defensive: a slide that already carries a sticker, bio_card, or product
    # photo without an explicit visual_hint still counts as a visual anchor.
    if slide.get("sticker_slot") or slide.get("sticker_image") or slide.get("sticker_url"):
        return True
    if slide.get("bio_card") or slide.get("bio_cards"):
        return True
    if slide.get("product_photo") or slide.get("product_image"):
        return True
    return False


def _slide_index(slide: dict[str, Any], position: int) -> int:
    raw = slide.get("slide")
    if isinstance(raw, int):
        return raw
    return position


def check_visual_cadence(
    content: dict[str, Any], *, route: str
) -> list[CadenceViolation]:
    """Return one CadenceViolation per stretch of 2+ consecutive text-only middle slides.

    Empty list = pass. Cover and sources slides are exempt.
    """
    _normalize_cadence_route(route)  # raises for unrouted/unknown
    if not isinstance(content, dict):
        raise VisualCadenceGateError("content must be a dict")

    violations: list[CadenceViolation] = []
    slides = content.get("slides")
    if not isinstance(slides, list):
        return violations

    run_start_pos: int | None = None
    run_start_index: int | None = None
    run_end_index: int | None = None
    run_count = 0

    def flush_run() -> None:
        nonlocal run_start_pos, run_start_index, run_end_index, run_count
        if run_count > _MAX_CONSECUTIVE_TEXT_ONLY:
            assert run_start_index is not None and run_end_index is not None
            violations.append(
                CadenceViolation(
                    start_slide_index=run_start_index,
                    end_slide_index=run_end_index,
                    consecutive_count=run_count,
                    reason=(
                        f"{run_count} consecutive text-only middle slides "
                        f"(max {_MAX_CONSECUTIVE_TEXT_ONLY} allowed)"
                    ),
                )
            )
        run_start_pos = None
        run_start_index = None
        run_end_index = None
        run_count = 0

    for position, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            flush_run()
            continue
        if _is_cover_slide(slide, position) or _is_sources_slide(slide):
            flush_run()
            continue
        if _has_visual_anchor(slide):
            flush_run()
            continue
        # Middle slide with no visual anchor -> extend the run
        idx = _slide_index(slide, position)
        if run_start_pos is None:
            run_start_pos = position
            run_start_index = idx
        run_end_index = idx
        run_count += 1

    flush_run()
    return violations


def attach_cadence_report(
    content: dict[str, Any] | None,
    *,
    route: str,
    env: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    """Attach a ``visual_cadence`` report when STORY_PIPELINE_V2_ENABLED is on.

    Flag OFF -> returns the input object unchanged (same identity).
    Flag ON  -> deep-copies, attaches ``visual_cadence`` schema, returns the copy.
    """
    if content is None or not cadence_gate_enabled(env):
        return content
    if not isinstance(content, dict):
        raise VisualCadenceGateError("content must be a dict or None")

    normalized = _normalize_cadence_route(route)
    violations = check_visual_cadence(content, route=route)
    updated = deepcopy(content)
    updated["visual_cadence"] = {
        "schema_version": "visual_cadence.v0.1",
        "sh_id": "SH-148",
        "route": normalized,
        "max_consecutive_text_only": _MAX_CONSECUTIVE_TEXT_ONLY,
        "violations": [
            {
                "start_slide_index": v.start_slide_index,
                "end_slide_index": v.end_slide_index,
                "consecutive_count": v.consecutive_count,
                "reason": v.reason,
            }
            for v in violations
        ],
        "pass": len(violations) == 0,
    }
    return updated
