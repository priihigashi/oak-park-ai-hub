"""SH-147 — Named-person face gate contract.

Detects when a slide names a person and verifies a face treatment exists
on the same slide. Pure validation helper. No LLM, no integration into
production reviewer/auditor yet — that ships as a separate audit-required PR.

Face rule source: CLAUDE.md "NAMED-PERSON -> FACE RULE" section +
~/.claude/projects/-Users-priscilahigashi/memory/project_visual_sticker_system.md
Accepted face treatments: .sticker-slot photo, .bio-card with .bio-photo,
.bio-initials fallback card.
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


class NamedPersonFaceGateError(ValueError):
    """Raised when the face gate cannot run for the requested route."""


def face_gate_enabled(env: dict[str, str] | None = None) -> bool:
    """Return True only when the storytelling pipeline flag is explicitly enabled."""
    source = os.environ if env is None else env
    return str(source.get(_FLAG, "0")).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_face_route(route: str) -> str:
    value = (route or "").strip().lower()
    if value in _OPC_ALIASES:
        return "opc"
    if value in _NEWS_ALIASES:
        return "news"
    if value == "unrouted":
        raise NamedPersonFaceGateError("Cannot run face gate for unrouted content")
    raise NamedPersonFaceGateError(f"Unknown face gate route: {route!r}")


@dataclass(frozen=True)
class FaceViolation:
    slide_index: int
    person_name: str
    reason: str


# Matches <strong>FirstName LastName</strong> with optional lowercase particles
# (de/da/do/dos/von/van/der/etc.) between capitalized words — handles names like
# "Lula da Silva", "Ludwig van Beethoven", "Carlos de Souza".
_NAME_PARTICLES = r"(?:de|da|do|das|dos|di|del|della|la|le|van|von|der|den|du|y|of)"
_CAP_WORD = r"[A-ZÀ-ÚÁ-Ý][A-Za-zÀ-ÿ'\-]+"
_NAMED_PERSON_RE = re.compile(
    rf"<strong>\s*({_CAP_WORD}(?:\s+(?:{_NAME_PARTICLES}\s+{_CAP_WORD}|{_CAP_WORD}))+)\s*</strong>"
)

_TEXT_FIELDS = (
    "body", "body_pt", "body_en",
    "text", "text_pt", "text_en",
    "headline", "headline_pt", "headline_en",
    "subhead", "subhead_pt", "subhead_en",
    "rendered_html", "html",
)


def _extract_named_people(slide: dict[str, Any]) -> list[str]:
    blob_parts = []
    for key in _TEXT_FIELDS:
        value = slide.get(key)
        if isinstance(value, str):
            blob_parts.append(value)
    blob = " ".join(blob_parts)
    seen: list[str] = []
    for match in _NAMED_PERSON_RE.findall(blob):
        name = match.strip()
        if name and name not in seen:
            seen.append(name)
    return seen


def _bio_card_has_face(card: Any) -> bool:
    if not isinstance(card, dict):
        return False
    photo = card.get("photo") or card.get("photo_url") or card.get("bio_photo")
    initials = card.get("initials") or card.get("bio_initials")
    return bool(photo or initials)


def _has_face_treatment(slide: dict[str, Any]) -> bool:
    """True when slide carries at least one accepted face treatment."""
    if slide.get("sticker_slot") or slide.get("sticker_image") or slide.get("sticker_url"):
        return True

    bio_cards = slide.get("bio_cards")
    if isinstance(bio_cards, list) and any(_bio_card_has_face(c) for c in bio_cards):
        return True

    single_card = slide.get("bio_card")
    if _bio_card_has_face(single_card):
        return True

    for key in ("rendered_html", "html"):
        html = slide.get(key)
        if isinstance(html, str) and any(
            marker in html for marker in ("sticker-slot", "bio-photo", "bio-initials")
        ):
            return True

    return False


def check_named_person_face_coverage(
    content: dict[str, Any], *, route: str
) -> list[FaceViolation]:
    """Return one FaceViolation per named person missing a face treatment.

    Empty list = pass. Slide index defaults to the slide's own ``slide`` field
    when present, otherwise the 1-based position in the slides list.
    """
    _normalize_face_route(route)  # raises for unrouted/unknown
    if not isinstance(content, dict):
        raise NamedPersonFaceGateError("content must be a dict")

    violations: list[FaceViolation] = []
    slides = content.get("slides")
    if not isinstance(slides, list):
        return violations

    for idx, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            continue
        people = _extract_named_people(slide)
        if not people:
            continue
        if _has_face_treatment(slide):
            continue
        slide_index = slide.get("slide") if isinstance(slide.get("slide"), int) else idx
        for person in people:
            violations.append(
                FaceViolation(
                    slide_index=slide_index,
                    person_name=person,
                    reason="named person has no face treatment (sticker/bio-card/initials)",
                )
            )
    return violations


def attach_face_gate_report(
    content: dict[str, Any] | None,
    *,
    route: str,
    env: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    """Attach a ``face_gate`` report when STORY_PIPELINE_V2_ENABLED is on.

    Flag OFF -> returns the input object unchanged (same identity).
    Flag ON  -> deep-copies, attaches ``face_gate`` schema, returns the copy.
    """
    if content is None or not face_gate_enabled(env):
        return content
    if not isinstance(content, dict):
        raise NamedPersonFaceGateError("content must be a dict or None")

    normalized = _normalize_face_route(route)
    violations = check_named_person_face_coverage(content, route=route)
    updated = deepcopy(content)
    updated["face_gate"] = {
        "schema_version": "face_gate.v0.1",
        "sh_id": "SH-147",
        "route": normalized,
        "violations": [
            {
                "slide_index": v.slide_index,
                "person_name": v.person_name,
                "reason": v.reason,
            }
            for v in violations
        ],
        "pass": len(violations) == 0,
    }
    return updated
