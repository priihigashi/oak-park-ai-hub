"""
Content Creator V2 — extract scenes CLI (Sprint 2-B).

Runs ffprobe + scene detection on a local video file and prints a JSON array
of scene objects: scene_id, start_time, end_time, keyframe_paths,
quality_signals, and optional transcript.

Usage:
    python -m scripts.content_creator_v2.extract_scenes \\
        --source /path/to/video.mp4 [--threshold 0.3] \\
        [--min-scene-seconds 1.5] [--keyframe-dir ./keyframes] \\
        [--transcribe] [--whisper-model base] [--pretty]
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import tempfile
from pathlib import Path
from typing import Optional

from . import scene_extractor as _scene_ext_mod
from .ffprobe import extract as ffprobe_extract
from .scene_extractor import extract_scenes


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ccv2-extract-scenes",
        description="Detect and extract scenes from a video file.",
    )
    parser.add_argument("--source", required=True, help="Path to input video file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=_scene_ext_mod._SCENE_THRESHOLD,
        help=f"Scene-change sensitivity 0.0–1.0 (default {_scene_ext_mod._SCENE_THRESHOLD})",
    )
    parser.add_argument(
        "--min-scene-seconds",
        type=float,
        default=_scene_ext_mod._MIN_SCENE_SECONDS,
        help=f"Drop scenes shorter than N seconds (default {_scene_ext_mod._MIN_SCENE_SECONDS})",
    )
    parser.add_argument(
        "--keyframe-dir",
        default=None,
        help="Directory for keyframe PNGs (default: system temp dir)",
    )
    parser.add_argument(
        "--transcribe",
        action="store_true",
        help="Run Whisper transcription on each scene (requires whisper or whisper-mlx)",
    )
    parser.add_argument(
        "--whisper-model",
        default="base",
        help="Whisper model size: tiny, base, small, medium (default: base)",
    )
    parser.add_argument(
        "--source-tag",
        default="personal",
        help="Asset source tag passed to ffprobe (default: personal)",
    )
    parser.add_argument(
        "--owner",
        default="priscila",
        help="Asset owner tag passed to ffprobe (default: priscila)",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args(argv)

    source_path = Path(args.source).resolve()
    if not source_path.exists():
        print(f"error: file not found: {source_path}", file=sys.stderr)
        return 1

    # Apply --min-scene-seconds by patching the module constant before detection runs
    _scene_ext_mod._MIN_SCENE_SECONDS = args.min_scene_seconds

    asset = ffprobe_extract(
        source_path,
        source=args.source_tag,
        owner=args.owner,
    )

    if args.keyframe_dir:
        keyframe_dir = Path(args.keyframe_dir)
        keyframe_dir.mkdir(parents=True, exist_ok=True)
    else:
        keyframe_dir = Path(tempfile.mkdtemp(prefix="ccv2_kf_"))

    scenes = extract_scenes(
        asset,
        keyframe_dir,
        threshold=args.threshold,
        transcribe=args.transcribe,
        whisper_model=args.whisper_model,
    )

    indent = 2 if args.pretty else None
    print(json.dumps([dataclasses.asdict(s) for s in scenes], indent=indent))
    return 0 if scenes else 1


if __name__ == "__main__":
    sys.exit(main())
