"""STORY-001 route-specific editorial contract loader.

This is intentionally a stub boundary. Operational routing stays in
``scripts/routing.py``; downstream storytelling phases can depend on this module
without learning file paths or touching the ROUTES dict.
"""

from __future__ import annotations


_STUB_VERSION = "0.1.0-stub"

_NEWS_ALIASES = {"news", "brazil", "usa", "br", "us", "brazil_news", "usa_news", "news_brazil", "news_usa"}
_OPC_ALIASES = {"opc", "content", "oak_park", "oak-park"}


def _normalize_story_route(route: str) -> str:
    value = (route or "").strip().lower()
    if value in _OPC_ALIASES:
        return "opc"
    if value in _NEWS_ALIASES:
        return "news"
    if value == "unrouted":
        raise ValueError("Cannot load storytelling contract for unrouted content")
    raise ValueError(f"Unknown storytelling route: {route!r}")


def load_contract(route: str) -> dict:
    """Return the route-specific editorial contract stub for STORY-001.

    STORY-002/003 will replace this stub content with real OPC/News contract
    fields. Until then, this function only proves the route-specific boundary.
    """
    normalized = _normalize_story_route(route)
    return {
        "route": normalized,
        "version": _STUB_VERSION,
        "loaded": False,
    }
