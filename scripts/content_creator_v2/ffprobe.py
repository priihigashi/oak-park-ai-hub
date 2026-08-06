"""
Content Creator V2 — ffprobe metadata extraction (Sprint 1).
Wraps ffprobe JSON output into a MediaAsset contract.

Master plan: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import uuid
from pathlib import Path
from typing import Optional

from .contracts import MediaAsset


def _sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while data := f.read(chunk):
            h.update(data)
    return h.hexdigest()


def _run_ffprobe(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def _video_stream(streams: list[dict]) -> Optional[dict]:
    for s in streams:
        if s.get("codec_type") == "video":
            return s
    return None


def _orientation(width: int, height: int) -> str:
    if width > height:
        return "landscape"
    if height > width:
        return "portrait"
    return "square"


def extract(
    path: Path,
    *,
    source: str = "personal",
    owner: str = "priscila",
    asset_id: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> MediaAsset:
    """
    Run ffprobe on `path` and return a MediaAsset.
    Caller supplies source/owner/location since ffprobe cannot read iPhone GPS reliably
    when files have been copied (EXIF stripped). Pass latitude/longitude explicitly
    from ExifTool output when available.
    """
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(path)

    probe = _run_ffprobe(path)
    fmt = probe.get("format", {})
    streams = probe.get("streams", [])
    video = _video_stream(streams)

    duration: Optional[float] = None
    raw_dur = fmt.get("duration")
    if raw_dur is not None:
        try:
            duration = float(raw_dur)
        except (ValueError, TypeError):
            pass

    width: Optional[int] = None
    height: Optional[int] = None
    orientation: Optional[str] = None
    if video:
        try:
            width = int(video["width"])
            height = int(video["height"])
            orientation = _orientation(width, height)
        except (KeyError, ValueError):
            pass

    # creation_time tag, ISO-8601 string or None
    tags = fmt.get("tags", {})
    captured_at: Optional[str] = tags.get("creation_time") or None

    checksum = _sha256(path)

    return MediaAsset(
        asset_id=asset_id or str(uuid.uuid4()),
        path=str(path),
        source=source,
        owner=owner,
        captured_at=captured_at,
        duration=duration,
        width=width,
        height=height,
        orientation=orientation,
        checksum=checksum,
        latitude=latitude,
        longitude=longitude,
    )
