"""Deterministic voice/personality gate for generated carousel content.

Rule source: FORMAT-021 + NONNEGOTIABLES voice locks (2026-06-08).

The gate is intentionally pure: callers provide the content dict and, when
available, recent hashtag sets from the Project Content Catalog. No network,
filesystem, or Sheets access happens here.
"""

from __future__ import annotations

import os
import re
from copy import deepcopy
from dataclasses import dataclass
from typing import Any


_FLAG = "VOICE_GATE_ENABLED"

_BANNED_HOOK_RE = re.compile(
    r"\b("
    r"did\s+you\s+know"
    r"|most\s+people\s+(?:do\s+not|don't)\s+know"
    r"|have\s+you\s+ever\s+heard"
    r"|you\s+won['’]t\s+believe"
    r")\b",
    re.IGNORECASE,
)

_DATE_RE = re.compile(
    r"\b("
    r"\d{4}(?:-\d{2}-\d{2})?"
    r"|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
    r"|(?:\d{1,2}\s+)?(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)[a-zç]*\.?\s+\d{4}"
    r")\b",
    re.IGNORECASE,
)

_DASH_RE = re.compile(r"\s+(?:-|–|—)\s+")
_HASHTAG_RE = re.compile(r"#[\wÀ-ÿ]+", re.UNICODE)


class VoicePersonalityGateError(ValueError):
    """Raised when the voice/personality gate cannot run."""


@dataclass(frozen=True)
class VoiceViolation:
    kind: str
    reason: str


def voice_gate_enabled(env: dict[str, str] | None = None) -> bool:
    source = os.environ if env is None else env
    return str(source.get(_FLAG, "0")).strip().lower() in {"1", "true", "yes", "on"}


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _iter_strings(v)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def _hook_candidates(content: dict[str, Any]) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for key in ("cover_pt", "cover_en", "hook", "headline", "cover_hook", "caption", "caption_pt", "caption_en"):
        value = _as_str(content.get(key)).strip()
        if value:
            candidates.append((key, value))

    slides = content.get("slides")
    if isinstance(slides, list) and slides:
        first = slides[0]
        if isinstance(first, dict):
            for key in ("hook", "heading_pt", "heading_en", "headline", "title", "cover_hook"):
                value = _as_str(first.get(key)).strip()
                if value:
                    candidates.append((f"slides[0].{key}", value))
        else:
            value = _as_str(first).strip()
            if value:
                candidates.append(("slides[0]", value))
    return candidates


def _check_banned_hooks(content: dict[str, Any]) -> list[VoiceViolation]:
    violations = []
    for label, text in _hook_candidates(content):
        match = _BANNED_HOOK_RE.search(text)
        if match:
            violations.append(
                VoiceViolation(
                    kind="banned_hook",
                    reason=f"{label} uses banned robotic hook phrase: {match.group(0)!r}",
                )
            )
    return violations


def _source_entries(content: dict[str, Any]) -> list[str]:
    entries: list[str] = []
    for key in ("sources", "source_lines", "citations"):
        val = content.get(key)
        if isinstance(val, list):
            entries.extend(_as_str(x).strip() for x in val if _as_str(x).strip())
        elif isinstance(val, str) and val.strip():
            entries.extend(x.strip() for x in re.split(r"\n+|;", val) if x.strip())

    for slide in content.get("slides", []) if isinstance(content.get("slides"), list) else []:
        if not isinstance(slide, dict):
            continue
        blob = " ".join(_as_str(slide.get(k)) for k in ("type", "slide_purpose", "heading_pt", "heading_en", "title")).lower()
        if "source" not in blob and "fonte" not in blob:
            continue
        for key in ("sources", "source_lines", "items", "items_pt", "items_en"):
            val = slide.get(key)
            if isinstance(val, list):
                entries.extend(_as_str(x).strip() for x in val if _as_str(x).strip())
            elif isinstance(val, str) and val.strip():
                entries.extend(x.strip() for x in re.split(r"\n+|;", val) if x.strip())
    return [e for e in entries if e]


def _looks_like_bibliography_line(text: str) -> bool:
    clean = re.sub(r"\s+", " ", text or "").strip()
    if not clean or len(clean) > 95:
        return False
    if not _DASH_RE.search(clean) or not _DATE_RE.search(clean):
        return False
    # A context sentence usually has a clause after the citation. Bare outlet-date
    # entries are the sterile failure mode Priscila flagged.
    if re.search(r"\b(shows?|explains?|found|reported|diz|mostra|explica|segundo|because|why|context)\b", clean, re.I):
        return False
    return True


def _check_bibliography_sources(content: dict[str, Any]) -> list[VoiceViolation]:
    entries = _source_entries(content)
    if len(entries) < 2:
        return []
    bare = [e for e in entries if _looks_like_bibliography_line(e)]
    if len(bare) == len(entries):
        return [
            VoiceViolation(
                kind="bibliography_sources",
                reason="sources slide is only outlet/date bibliography lines; add one-line context for each source",
            )
        ]
    return []


def _candidate_grids(content: dict[str, Any]) -> list[dict[str, Any]]:
    grids = []
    for key in ("comparison_grid", "parallel_grid"):
        val = content.get(key)
        if isinstance(val, dict):
            grids.append(val)
    for slide in content.get("slides", []) if isinstance(content.get("slides"), list) else []:
        if isinstance(slide, dict):
            stype = _as_str(slide.get("type") or slide.get("template_id")).lower()
            if "comparison_grid" in stype or "parallel" in stype:
                grids.append(slide)
    return grids


def _grid_labels_and_counts(grid: dict[str, Any]) -> tuple[list[str], list[int]]:
    labels: list[str] = []
    counts: list[int] = []
    columns = grid.get("columns")
    if isinstance(columns, list):
        for col in columns:
            if not isinstance(col, dict):
                continue
            labels.append(_as_str(col.get("label") or col.get("title") or col.get("heading")).strip())
            items = col.get("items") or col.get("bullets") or col.get("points")
            counts.append(len(items) if isinstance(items, list) else (1 if _as_str(items).strip() else 0))
    else:
        for side in ("left", "right", "before", "after", "a", "b"):
            val = grid.get(side)
            if isinstance(val, dict):
                labels.append(_as_str(val.get("label") or val.get("title") or side).strip())
                items = val.get("items") or val.get("bullets") or val.get("points")
                counts.append(len(items) if isinstance(items, list) else (1 if _as_str(items).strip() else 0))
    if not labels:
        label_list = grid.get("labels")
        if isinstance(label_list, list):
            labels = [_as_str(x).strip() for x in label_list]
            counts = [len(grid.get("items") or [])] * len(labels)
    return [x for x in labels if x], counts


def _check_parallel_bland_grid(content: dict[str, Any]) -> list[VoiceViolation]:
    violations = []
    for grid in _candidate_grids(content):
        labels, counts = _grid_labels_and_counts(grid)
        if len(labels) < 2:
            continue
        max_items = max(counts or [0])
        if all(len(label) < 12 for label in labels) and max_items <= 2:
            violations.append(
                VoiceViolation(
                    kind="parallel_bland_grid",
                    reason=f"comparison grid labels are too thin ({', '.join(labels[:4])}) and columns have <=2 items",
                )
            )
    return violations


def normalize_hashtag_set(text: str) -> frozenset[str]:
    return frozenset(tag.lower() for tag in _HASHTAG_RE.findall(text or ""))


def _content_hashtag_set(content: dict[str, Any]) -> frozenset[str]:
    parts = []
    for key in ("hashtags", "in_post_hashtags", "first_comment_hashtags", "caption", "caption_pt", "caption_en"):
        parts.append(_as_str(content.get(key)))
    return normalize_hashtag_set("\n".join(parts))


def _check_recycled_hashtag_block(
    content: dict[str, Any],
    recent_hashtag_sets: list[frozenset[str]] | None,
) -> list[VoiceViolation]:
    current = _content_hashtag_set(content)
    if len(current) < 3:
        return []
    for idx, old in enumerate(recent_hashtag_sets or [], start=1):
        if current == old:
            return [
                VoiceViolation(
                    kind="recycled_hashtag_block",
                    reason=f"caption hashtag set is identical to recent catalog post #{idx} of last 5",
                )
            ]
    return []


def check_voice_personality(
    content: dict[str, Any],
    *,
    route: str = "",
    recent_hashtag_sets: list[frozenset[str]] | None = None,
) -> list[VoiceViolation]:
    """Return voice/personality violations. Empty list means pass."""
    if not isinstance(content, dict):
        raise VoicePersonalityGateError("content must be a dict")
    violations: list[VoiceViolation] = []
    violations.extend(_check_banned_hooks(content))
    violations.extend(_check_bibliography_sources(content))
    violations.extend(_check_parallel_bland_grid(content))
    violations.extend(_check_recycled_hashtag_block(content, recent_hashtag_sets))
    return violations


def attach_voice_personality_report(
    content: dict[str, Any] | None,
    *,
    route: str = "",
    env: dict[str, str] | None = None,
    recent_hashtag_sets: list[frozenset[str]] | None = None,
) -> dict[str, Any] | None:
    if content is None or not voice_gate_enabled(env):
        return content
    if not isinstance(content, dict):
        raise VoicePersonalityGateError("content must be a dict or None")
    violations = check_voice_personality(
        content,
        route=route,
        recent_hashtag_sets=recent_hashtag_sets,
    )
    updated = deepcopy(content)
    updated["voice_personality_gate"] = {
        "schema_version": "voice_personality.v0.1",
        "route": (route or "").strip().lower(),
        "violations": [{"kind": v.kind, "reason": v.reason} for v in violations],
        "pass": len(violations) == 0,
    }
    return updated
