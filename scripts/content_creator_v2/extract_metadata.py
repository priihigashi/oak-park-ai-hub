"""
CLI: extract ffprobe metadata from a media file and print a MediaAsset as JSON.

Usage:
    python -m scripts.content_creator_v2.extract_metadata <path> [options]

Options:
    --source    personal | approved_collection | licensed | ai_generated  (default: personal)
    --owner     priscila | mike | <collection_name>  (default: priscila)
    --lat       GPS latitude float (optional)
    --lon       GPS longitude float (optional)
    --pretty    pretty-print JSON (default: compact)
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from .ffprobe import extract


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="extract_metadata",
        description="Run ffprobe on a media file and output a MediaAsset JSON.",
    )
    p.add_argument("path", type=Path, help="Path to the media file.")
    p.add_argument("--source", default="personal",
                   choices=["personal", "approved_collection", "licensed", "ai_generated"])
    p.add_argument("--owner", default="priscila")
    p.add_argument("--lat", type=float, default=None, dest="latitude")
    p.add_argument("--lon", type=float, default=None, dest="longitude")
    p.add_argument("--pretty", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        asset = extract(
            args.path,
            source=args.source,
            owner=args.owner,
            latitude=args.latitude,
            longitude=args.longitude,
        )
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    indent = 2 if args.pretty else None
    print(json.dumps(dataclasses.asdict(asset), indent=indent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
