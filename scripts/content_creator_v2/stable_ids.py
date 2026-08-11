"""Deterministic identifiers for Content Creator V2 assets and scenes.

Identity is derived from source identity and media boundaries. It must never
depend on wall-clock time, process state, or randomness because reruns need to
update the same catalog rows and preserve human corrections.
"""

from __future__ import annotations

import hashlib


_ALGORITHM_VERSION = "v1"


def _digest(namespace: str, *parts: str, length: int = 32) -> str:
    payload = "\x1f".join((_ALGORITHM_VERSION, namespace, *parts))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def _milliseconds(seconds: float) -> int:
    if seconds is None:
        raise ValueError("timestamp is required")
    value = float(seconds)
    if value < 0:
        raise ValueError(f"timestamp cannot be negative: {seconds}")
    return int(round(value * 1000))


def asset_id(source_key: str) -> str:
    """Return a stable ID for a source asset.

    ``source_key`` is the source system's durable identity. The folder indexer
    uses the resolved file path; a Photos adapter should pass the Photos UUID.
    Media content/version deliberately does not change the parent identity.
    """
    if not source_key:
        raise ValueError("source_key is required")
    return "A-" + _digest("asset", source_key)


def scene_id(
    parent_asset_id: str,
    start_seconds: float,
    end_seconds: float,
    *,
    media_version: str,
) -> str:
    """Return a stable ID for one scene in one version of an asset."""
    if not parent_asset_id:
        raise ValueError("parent_asset_id is required")
    if not media_version:
        raise ValueError("media_version is required")
    start_ms = _milliseconds(start_seconds)
    end_ms = _milliseconds(end_seconds)
    if end_ms <= start_ms:
        raise ValueError(
            f"scene end ({end_ms}ms) must be after start ({start_ms}ms)"
        )
    return "S-" + _digest(
        "scene", parent_asset_id, media_version, str(start_ms), str(end_ms)
    )


def keyframe_name(parent_scene_id: str, timestamp_seconds: float) -> str:
    """Return a deterministic, filesystem-safe PNG filename."""
    if not parent_scene_id:
        raise ValueError("parent_scene_id is required")
    return f"{parent_scene_id}_{_milliseconds(timestamp_seconds)}.png"
