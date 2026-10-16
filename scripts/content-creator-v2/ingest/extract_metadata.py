"""
S1-B: Extract ffprobe metadata for media files and output the 13-field schema.
Usage: python extract_metadata.py <file_path>
Outputs JSON to stdout.
"""

import json
import hashlib
import subprocess
import sys
import os
from datetime import datetime, timezone


FIELDS = [
    "file_path", "file_hash", "duration_sec", "width", "height",
    "aspect_ratio", "fps", "has_audio", "codec_video", "codec_audio",
    "size_bytes", "last_modified", "indexed_at",
]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path: str) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", "-show_format", path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def fps_float(r_frame_rate: str) -> float:
    """Convert '30000/1001' → 29.97"""
    num, den = r_frame_rate.split("/")
    return round(int(num) / int(den), 3)


def extract(path: str) -> dict:
    path = os.path.abspath(path)
    data = probe(path)

    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)

    width = int(video["width"]) if video else None
    height = int(video["height"]) if video else None
    aspect = f"{width}:{height}" if width and height else None

    stat = os.stat(path)

    return {
        "file_path": path,
        "file_hash": sha256(path),
        "duration_sec": float(data["format"].get("duration", 0)),
        "width": width,
        "height": height,
        "aspect_ratio": aspect,
        "fps": fps_float(video["r_frame_rate"]) if video else None,
        "has_audio": audio is not None,
        "codec_video": video["codec_name"] if video else None,
        "codec_audio": audio["codec_name"] if audio else None,
        "size_bytes": stat.st_size,
        "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "indexed_at": datetime.now(tz=timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_metadata.py <file_path>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(extract(sys.argv[1]), indent=2))
