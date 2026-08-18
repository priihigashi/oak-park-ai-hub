"""
Content Creator V2 — shot planner (coding order step 6 of 10).

Converts a script (list of text beats) into a list of ShotRequests — one per beat.
Uses Claude to infer the ideal visual for each beat and assign source preferences.

Usage:
    python -m scripts.content_creator_v2.shot_planner script.txt
    python -m scripts.content_creator_v2.shot_planner --text "Apply epoxy. Let it cure overnight."
    echo '["Beat one", "Beat two"]' | python -m scripts.content_creator_v2.shot_planner --stdin-json

Master plan: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
"""

from __future__ import annotations

import dataclasses
import json
import re
import sys
from pathlib import Path
from typing import Optional

from .contracts import ShotRequest

_SPEAKING_RATE_WPM = 130  # conservative rate for voiceover timing
_MIN_SHOT_DURATION = 3.0
_DEFAULT_SHOT_DURATION = 5.0

_NICHE_SOURCES: dict[str, tuple[str, list[str]]] = {
    "opc": ("personal", ["approved_collection", "licensed"]),
    "brazil": ("licensed", ["approved_collection", "personal"]),
    "usa": ("licensed", ["approved_collection", "personal"]),
}

_PLANNER_PROMPT = """You are a video shot planner for short-form social media content.

Niche: {niche}

For each script beat below, produce one JSON object describing the ideal shot:
{{
  "visual_query": "<concrete, searchable description — what the camera sees>",
  "must_show": ["<mandatory element if one exists, else empty list>"],
  "avoid": ["<banned element if relevant, else empty list>"]
}}

Return a JSON array with exactly {n} objects, one per beat, in the same order. No other text.

Rules:
- visual_query must be specific enough to drive a vector search (e.g. "worker in safety gear applying epoxy to concrete garage floor", not "construction scene")
- For OPC niche: favor hands-on construction, before/after reveals, client spaces, outdoor sites
- For Brazil/USA niches: favor documentary footage, landmarks, crowds, news-style B-roll
- must_show: include only when one element is visually non-negotiable for the beat to make sense
- avoid: flag competitor branding, sensitive imagery, or anything that breaks the content policy

Script beats (JSON array):
{beats_json}"""


def _estimate_duration(text: str) -> float:
    words = len(text.split())
    seconds = (words / _SPEAKING_RATE_WPM) * 60.0
    return max(_MIN_SHOT_DURATION, round(seconds, 1))


def _split_text(text: str) -> list[str]:
    """Split a raw script string into beats at sentence boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def plan_shots(beats: list[str], *, niche: str = "opc") -> list[ShotRequest]:
    """Convert script beats to ShotRequests. Makes one Claude call for all beats."""
    if not beats:
        return []

    import anthropic

    client = anthropic.Anthropic()
    preferred, fallbacks = _NICHE_SOURCES.get(niche, _NICHE_SOURCES["opc"])

    prompt = _PLANNER_PROMPT.format(
        niche=niche,
        n=len(beats),
        beats_json=json.dumps(beats, ensure_ascii=False, indent=2),
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    analyses: list[dict] = json.loads(raw)

    shots: list[ShotRequest] = []
    for i, (beat, analysis) in enumerate(zip(beats, analyses)):
        shots.append(
            ShotRequest(
                shot_id=f"shot_{i + 1:03d}",
                voiceover_text=beat,
                visual_query=analysis["visual_query"],
                preferred_source=preferred,
                fallback_sources=list(fallbacks),
                duration_seconds=_estimate_duration(beat),
                must_show=analysis.get("must_show", []),
                avoid=analysis.get("avoid", []),
            )
        )

    return shots


def shots_to_json(shots: list[ShotRequest]) -> str:
    return json.dumps([dataclasses.asdict(s) for s in shots], indent=2, ensure_ascii=False)


def _print_pretty(shots: list[ShotRequest]) -> None:
    for s in shots:
        print(f"\n[{s.shot_id}]  {s.duration_seconds}s  |  source: {s.preferred_source}")
        print(f"  voiceover : {s.voiceover_text}")
        print(f"  visual    : {s.visual_query}")
        if s.must_show:
            print(f"  must_show : {', '.join(s.must_show)}")
        if s.avoid:
            print(f"  avoid     : {', '.join(s.avoid)}")


def _build_parser():
    import argparse

    parser = argparse.ArgumentParser(
        description="Shot planner — map script beats to ShotRequests"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "script_file",
        nargs="?",
        metavar="FILE",
        help=".txt (sentences split to beats) or .json (array of beat strings)",
    )
    source.add_argument("--text", metavar="TEXT", help="Inline script text")
    source.add_argument(
        "--stdin-json",
        action="store_true",
        help='Read a JSON array of beat strings from stdin (e.g. echo \'["a","b"]\' | ...)',
    )
    parser.add_argument(
        "--niche",
        default="opc",
        choices=list(_NICHE_SOURCES),
        help="Content niche — controls source preference order (default: opc)",
    )
    parser.add_argument(
        "--output",
        default="pretty",
        choices=["pretty", "json"],
        help="Output format (default: pretty)",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.stdin_json:
        beats = json.load(sys.stdin)
    elif args.text:
        beats = _split_text(args.text)
    else:
        content = Path(args.script_file).read_text(encoding="utf-8")
        beats = json.loads(content) if args.script_file.endswith(".json") else _split_text(content)

    if not beats:
        print("No beats found — nothing to plan.", file=sys.stderr)
        sys.exit(1)

    shots = plan_shots(beats, niche=args.niche)

    if args.output == "json":
        print(shots_to_json(shots))
    else:
        _print_pretty(shots)


if __name__ == "__main__":
    main()
