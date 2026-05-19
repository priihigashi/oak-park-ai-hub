"""SH-149 — Motion/static sibling folder gate contract.

Detects when a carousel build is missing the static or motion sibling
output. Pure validation helper. No LLM, no filesystem access, no integration
into production reviewer/auditor yet — that ships as a separate audit-required PR.

Rule source: CLAUDE.md "MOTION IS DEFAULT ON" + "CAROUSEL OUTPUT ROUTING".

The canonical build shape is::

    <carousel_folder_id>/v<N>_<slug>/
        cover.html
        png/        <- static slides (always required)
        motion/     <- MP4 + GIF + preview frame + duplicated non-cover PNGs
        resources/
        <story doc>

Validator inputs (provided by caller — this module does no I/O):
- ``content["static_only"]`` (bool, default False) — explicit override
- ``content["build_artifacts"]["static_files"]`` (list[str]) — filenames in png/
- ``content["build_artifacts"]["motion_files"]`` (list[str]) — filenames in motion/

Violations returned:
- ``missing_static``: png/ has no static files
- ``empty_motion``: motion/ has no files (and static_only override is not set)
- ``missing_mp4``: motion/ has files but no MP4
- ``missing_gif``: motion/ has files but no GIF
- ``missing_preview``: motion/ has files but no preview frame
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

# File-extension heuristics
_MP4_EXTS = {".mp4", ".m4v"}
_GIF_EXTS = {".gif"}
_PNG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# Preview frame is a still image whose name contains a known preview marker
_PREVIEW_MARKERS = re.compile(r"(?:^|[_\-/])(preview|cover|thumb|thumbnail|first[_\-]?frame)(?:[_\-.]|$)", re.IGNORECASE)


class MotionStaticSiblingGateError(ValueError):
    """Raised when the motion/static sibling gate cannot run for the requested route."""


def motion_static_gate_enabled(env: dict[str, str] | None = None) -> bool:
    """Return True only when the storytelling pipeline flag is explicitly enabled."""
    source = os.environ if env is None else env
    return str(source.get(_FLAG, "0")).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_motion_static_route(route: str) -> str:
    value = (route or "").strip().lower()
    if value in _OPC_ALIASES:
        return "opc"
    if value in _NEWS_ALIASES:
        return "news"
    if value == "unrouted":
        raise MotionStaticSiblingGateError("Cannot run motion/static gate for unrouted content")
    raise MotionStaticSiblingGateError(f"Unknown motion/static gate route: {route!r}")


@dataclass(frozen=True)
class MotionStaticViolation:
    kind: str
    reason: str


def _basename(path: str) -> str:
    if not isinstance(path, str):
        return ""
    return path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]


def _has_ext(filename: str, ext_set: set[str]) -> bool:
    name = _basename(filename).lower()
    for ext in ext_set:
        if name.endswith(ext):
            return True
    return False


def _is_preview_frame(filename: str) -> bool:
    """True when filename looks like a preview frame (still image marker)."""
    base = _basename(filename)
    if not base:
        return False
    if not _has_ext(base, _PNG_EXTS):
        return False
    return bool(_PREVIEW_MARKERS.search(base))


def _coerce_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return []


def check_motion_static_siblings(
    content: dict[str, Any], *, route: str
) -> list[MotionStaticViolation]:
    """Validate static/motion sibling folders against the build rule.

    Empty list = pass.
    """
    _normalize_motion_static_route(route)  # raises for unrouted/unknown
    if not isinstance(content, dict):
        raise MotionStaticSiblingGateError("content must be a dict")

    violations: list[MotionStaticViolation] = []

    static_only = bool(content.get("static_only"))
    build_artifacts = content.get("build_artifacts")
    if not isinstance(build_artifacts, dict):
        build_artifacts = {}

    static_files = _coerce_list(build_artifacts.get("static_files"))
    motion_files = _coerce_list(build_artifacts.get("motion_files"))

    # Static is always required
    if not static_files:
        violations.append(
            MotionStaticViolation(
                kind="missing_static",
                reason="png/ has no static files — every build needs at least one static slide",
            )
        )

    if static_only:
        # Explicit override — motion not required
        return violations

    # Motion folder must exist and be non-empty
    if not motion_files:
        violations.append(
            MotionStaticViolation(
                kind="empty_motion",
                reason=(
                    "motion/ is empty — motion default ON. Build is incomplete; "
                    "do NOT email preview. Set static_only=True only if explicitly told."
                ),
            )
        )
        return violations

    has_mp4 = any(_has_ext(f, _MP4_EXTS) for f in motion_files)
    has_gif = any(_has_ext(f, _GIF_EXTS) for f in motion_files)
    has_preview = any(_is_preview_frame(f) for f in motion_files)

    if not has_mp4:
        violations.append(
            MotionStaticViolation(
                kind="missing_mp4",
                reason="motion/ missing MP4 (required: MP4 + GIF + preview frame)",
            )
        )
    if not has_gif:
        violations.append(
            MotionStaticViolation(
                kind="missing_gif",
                reason="motion/ missing GIF (required: MP4 + GIF + preview frame)",
            )
        )
    if not has_preview:
        violations.append(
            MotionStaticViolation(
                kind="missing_preview",
                reason="motion/ missing preview frame still image (filename must contain preview/cover/thumb/first-frame)",
            )
        )

    return violations


def attach_motion_static_report(
    content: dict[str, Any] | None,
    *,
    route: str,
    env: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    """Attach a ``motion_static_sibling`` report when STORY_PIPELINE_V2_ENABLED is on.

    Flag OFF -> returns the input object unchanged (same identity).
    Flag ON  -> deep-copies, attaches schema, returns the copy.
    """
    if content is None or not motion_static_gate_enabled(env):
        return content
    if not isinstance(content, dict):
        raise MotionStaticSiblingGateError("content must be a dict or None")

    normalized = _normalize_motion_static_route(route)
    violations = check_motion_static_siblings(content, route=route)
    updated = deepcopy(content)
    updated["motion_static_sibling"] = {
        "schema_version": "motion_static_sibling.v0.1",
        "sh_id": "SH-149",
        "route": normalized,
        "static_only_override": bool(content.get("static_only")),
        "violations": [
            {"kind": v.kind, "reason": v.reason} for v in violations
        ],
        "pass": len(violations) == 0,
    }
    return updated
