"""SH-145 — Story Outline Contract.

Additive story-outline helper for the content creator pipeline.

Design constraints from AIOX gate:
- Feature-flagged OFF by default (`STORY_PIPELINE_V2_ENABLED=0`).
- No LLM call. Outline is derived only from already-generated content fields.
- Backward-compatible: when disabled, callers can keep byte-identical output.
- Aligns to existing slide-purpose spine tokens from `_slide_purpose_block()`.

This module intentionally does not import carousel_builder.py. It must remain small,
pure, and testable so integration can add one safe hook later.
"""

from __future__ import annotations

import os
from copy import deepcopy
from typing import Any


_FLAG = "STORY_PIPELINE_V2_ENABLED"

OPC_SPINE = ["hook", "cost", "teach", "apply", "sources"]
NEWS_SPINE_5 = ["claim", "number", "evidence", "opposition+implication", "sources"]
NEWS_SPINE_6 = ["claim", "number", "evidence", "opposition", "implication", "sources"]

_OPC_GOALS = {
    "hook": "Stop the scroll with one homeowner risk, cost, or decision tension.",
    "cost": "Quantify the same risk or decision with a sourced number or grounded consequence.",
    "teach": "Explain the mechanism behind the risk with one simple, specific idea.",
    "apply": "Give the homeowner one action or decision that resolves the hook.",
    "sources": "Show citations and close with a save/share payoff.",
}

_NEWS_GOALS = {
    "claim": "State the claim being checked without overstating the evidence.",
    "number": "Size the claim with the key figure, date, or count.",
    "evidence": "Show the strongest primary or high-quality evidence.",
    "opposition": "Show meaningful counterpoint, opposition, or missing context.",
    "implication": "Explain the neutral consequence or why the fact pattern matters.",
    "opposition+implication": "Compress opposition/context and neutral implication into one slide.",
    "sources": "List sources and preserve claim-status nuance.",
}


class StoryOutlineError(ValueError):
    """Raised when callers ask for a story outline from invalid inputs."""


def story_pipeline_enabled(env: dict[str, str] | None = None) -> bool:
    """Return True only when the SH-145 story pipeline flag is explicitly enabled."""
    source = os.environ if env is None else env
    return str(source.get(_FLAG, "0")).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_niche(niche: str | None) -> str:
    value = (niche or "opc").strip().lower()
    if value in {"br", "brazil_news", "news_brazil"}:
        return "brazil"
    if value in {"us", "usa_news", "news_usa"}:
        return "usa"
    if value not in {"opc", "brazil", "usa"}:
        return "opc"
    return value


def default_spine(niche: str, slide_count: int) -> list[str]:
    """Return the approved spine tokens for a route and slide count."""
    normalized = _normalize_niche(niche)
    if normalized == "opc":
        return OPC_SPINE[:slide_count]
    if slide_count >= 6:
        return NEWS_SPINE_6[:slide_count]
    return NEWS_SPINE_5[:slide_count]


def _slide_purposes_from_content(content: dict[str, Any], niche: str, slide_count: int) -> list[str]:
    raw = content.get("slide_purposes")
    if isinstance(raw, list) and raw:
        ordered: dict[int, str] = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            try:
                slide_num = int(item.get("slide"))
            except Exception:
                continue
            purpose = str(item.get("purpose") or "").strip()
            if slide_num and purpose:
                ordered[slide_num] = purpose
        if ordered:
            fallback = default_spine(niche, slide_count)
            return [ordered.get(i, fallback[i - 1] if i <= len(fallback) else "middle") for i in range(1, slide_count + 1)]
    return default_spine(niche, slide_count)


def _field_snapshot(content: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: content.get(field) for field in fields if content.get(field) not in (None, "", [], {})}


def _extract_people(content: dict[str, Any], slide_num: int) -> list[dict[str, Any]]:
    people = content.get("mentioned_people") or []
    if not isinstance(people, list):
        return []
    result: list[dict[str, Any]] = []
    for person in people:
        if not isinstance(person, dict):
            continue
        try:
            person_slide = int(person.get("slide", 0))
        except Exception:
            person_slide = 0
        if person_slide == slide_num:
            result.append({
                "name": person.get("name"),
                "role": person.get("role") or person.get("role_en"),
                "image_hint": person.get("image_hint"),
            })
    return result


def build_story_outline(
    content: dict[str, Any],
    *,
    topic: str = "",
    niche: str = "opc",
    template_key: str | None = None,
    slide_count: int | None = None,
) -> dict[str, Any]:
    """Build the additive SH-145 story outline from existing content.

    The output is metadata only. Renderers/reviewers may consume it later, but the
    outline itself must not change visible carousel output.
    """
    if not isinstance(content, dict):
        raise StoryOutlineError("content must be a dict")

    normalized = _normalize_niche(niche)
    slides = content.get("slides") if isinstance(content.get("slides"), list) else []
    inferred_count = slide_count or len(slides) + 2  # cover + sources when middle slides are in slides[]
    if not inferred_count or inferred_count < 1:
        inferred_count = 5 if normalized == "opc" else 5

    purposes = _slide_purposes_from_content(content, normalized, inferred_count)
    goals = _OPC_GOALS if normalized == "opc" else _NEWS_GOALS

    outline_slides: list[dict[str, Any]] = []
    for index, purpose in enumerate(purposes, start=1):
        slide_meta: dict[str, Any] = {
            "slide": index,
            "purpose": purpose,
            "goal": goals.get(purpose, "Support the story spine without introducing a new topic."),
        }
        if index == 1:
            slide_meta["source_fields"] = _field_snapshot(content, ["headline", "subhead", "hook_frame", "viewer_question"])
        elif index == inferred_count:
            slide_meta["source_fields"] = _field_snapshot(content, ["sources", "cta", "caption"])
        else:
            middle = slides[index - 2] if index - 2 < len(slides) and isinstance(slides[index - 2], dict) else {}
            slide_meta["source_fields"] = {
                **_field_snapshot(content, [f"slide{index}_headline", f"slide{index}_stat", f"slide{index}_label"]),
                **_field_snapshot(middle, ["visual_hint", "context_image_query", "context_image_query_alt"]),
            }
        people = _extract_people(content, index)
        if people:
            slide_meta["mentioned_people"] = people
        outline_slides.append(slide_meta)

    route_extension: dict[str, Any]
    if normalized == "opc":
        route_extension = _field_snapshot(content, [
            "hook_frame", "viewer_question", "payoff", "why_this_matters_now", "proof_needed",
        ])
    else:
        route_extension = _field_snapshot(content, [
            "cover_claim", "claim_status", "source_needs", "template_signal",
        ])

    return {
        "schema_version": "story_outline.v0.1",
        "sh_id": "SH-145",
        "feature_flag": _FLAG,
        "route": normalized,
        "template_key": template_key,
        "topic": topic,
        "slide_count": inferred_count,
        "spine": purposes,
        "slides": outline_slides,
        "route_extension": route_extension,
    }


def attach_story_outline(
    content: dict[str, Any] | None,
    *,
    topic: str = "",
    niche: str = "opc",
    template_key: str | None = None,
    slide_count: int | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    """Attach `story_outline` only when SH-145 feature flag is enabled.

    When disabled, return the original object unchanged so legacy output remains
    byte-identical for callers that serialize the returned content.
    """
    if content is None or not story_pipeline_enabled(env):
        return content
    if not isinstance(content, dict):
        raise StoryOutlineError("content must be a dict or None")

    updated = deepcopy(content)
    updated["story_outline"] = build_story_outline(
        updated,
        topic=topic,
        niche=niche,
        template_key=template_key,
        slide_count=slide_count,
    )
    return updated
