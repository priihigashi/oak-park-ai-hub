"""
Content Creator V2 — script assistant (coding order step 5 of 10).

Converts a voiceover script into an EditDecision by:
  1. Splitting the script into beats (blank-line paragraphs or sentence boundaries).
  2. Generating a visual_query per beat via Claude (haiku) or a keyword fallback.
  3. Running search_scenes() to find matching ClipCandidates from the catalog.
  4. Auto-selecting the top candidate per beat.
  5. Writing an EditDecision JSON to disk or stdout.

Usage:
    python -m scripts.content_creator_v2.script_assistant script.txt --output edit.json
    python -m scripts.content_creator_v2.script_assistant --show-requests script.txt
    echo "We pour the concrete." | python -m scripts.content_creator_v2.script_assistant

Input: plain text (one beat per blank-line paragraph, or sentence-split if no blank lines)
       OR a JSON array of {"voiceover": "...", "visual_query": "..."} objects for pre-written queries.

Master plan: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .catalog import DEFAULT_DB
from .contracts import ApprovedShot, EditDecision, ShotRequest
from .search_cli import search_scenes


# ── beat splitter ──────────────────────────────────────────────────────────────

def _split_beats(text: str) -> list[str]:
    """Split voiceover text into beats: paragraphs first, then sentence boundaries."""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if len(paragraphs) > 1:
        return paragraphs
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s.strip()]


# ── visual query generator ─────────────────────────────────────────────────────

_FILLER_WORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "of",
    "for", "is", "are", "was", "were", "with", "we", "our", "this", "that",
    "then", "by", "from", "it", "its", "as", "be", "have", "has", "do",
    "not", "so", "up", "all", "out", "into", "just",
})


def _visual_query_from_voiceover(voiceover: str) -> str:
    """
    Derive a visual search query from a voiceover beat.

    Uses Claude claude-haiku-4-5-20251001 for speed and low cost. Falls back to keyword
    extraction when the Anthropic SDK is unavailable or the API returns an error.
    """
    try:
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=64,
            messages=[{
                "role": "user",
                "content": (
                    "Convert this voiceover line into a short visual search query "
                    "(5–10 words) describing what should appear on screen. "
                    "Return ONLY the query, no punctuation, no explanation.\n\n"
                    f"Voiceover: {voiceover}"
                ),
            }],
        )
        return resp.content[0].text.strip()
    except Exception:
        tokens = re.findall(r"\b[a-zA-Z]+\b", voiceover.lower())
        keywords = [t for t in tokens if t not in _FILLER_WORDS]
        return " ".join(keywords[:8]) if keywords else voiceover[:60]


# ── shot request builder ───────────────────────────────────────────────────────

def _build_shot_requests(
    beats: list[str],
    *,
    preferred_source: str = "personal",
    beat_duration: float = 5.0,
    precomputed_queries: Optional[list[str]] = None,
) -> list[ShotRequest]:
    requests: list[ShotRequest] = []
    for i, voiceover in enumerate(beats):
        if precomputed_queries and i < len(precomputed_queries) and precomputed_queries[i]:
            visual_query = precomputed_queries[i]
        else:
            visual_query = _visual_query_from_voiceover(voiceover)
        requests.append(ShotRequest(
            shot_id=f"shot_{i + 1:03d}",
            voiceover_text=voiceover,
            visual_query=visual_query,
            preferred_source=preferred_source,
            fallback_sources=["approved_collection", "licensed"],
            duration_seconds=beat_duration,
        ))
    return requests


# ── catalog matcher ────────────────────────────────────────────────────────────

def _match_candidates(
    requests: list[ShotRequest],
    *,
    db_path: Path = DEFAULT_DB,
    top_k: int = 1,
    source_filter: Optional[str] = None,
) -> list[tuple[ShotRequest, list]]:
    matched: list[tuple[ShotRequest, list]] = []
    for req in requests:
        candidates = search_scenes(
            req.visual_query,
            db_path=db_path,
            top_k=top_k,
            source_filter=source_filter,
        )
        matched.append((req, candidates))
    return matched


# ── edit decision assembler ────────────────────────────────────────────────────

def _assemble_edit_decision(
    matched: list[tuple[ShotRequest, list]],
) -> EditDecision:
    approved: list[ApprovedShot] = []
    for req, candidates in matched:
        if not candidates:
            continue
        top = candidates[0]
        trim_start = top.trim_start if top.trim_start is not None else 0.0
        trim_end = (
            top.trim_end
            if top.trim_end is not None
            else trim_start + req.duration_seconds
        )
        approved.append(ApprovedShot(
            shot_id=req.shot_id,
            selected_candidate=top,
            final_trim_start=trim_start,
            final_trim_end=trim_end,
            caption=req.voiceover_text,
        ))
    total = len(matched)
    hit = len(approved)
    return EditDecision(
        project_id=f"proj_{uuid.uuid4().hex[:8]}",
        created_at=datetime.now(timezone.utc).isoformat(),
        approved_shots=approved,
        output_formats=["9x16_1080p"],
        notes=f"Auto-generated by script_assistant. {hit}/{total} shots matched.",
    )


# ── public API ─────────────────────────────────────────────────────────────────

def script_to_edit_decision(
    script: str,
    *,
    db_path: Path = DEFAULT_DB,
    top_k: int = 1,
    preferred_source: str = "personal",
    beat_duration: float = 5.0,
    source_filter: Optional[str] = None,
) -> tuple[EditDecision, list[ShotRequest]]:
    """
    Convert a voiceover script into an EditDecision.

    Args:
        script:           Full voiceover text. Beats separated by blank lines
                          (paragraph mode) or detected sentence boundaries.
        db_path:          Catalog database path.
        top_k:            Candidates to retrieve per beat (1 = auto-select best).
        preferred_source: Source tier to annotate in ShotRequests.
        beat_duration:    Target seconds per shot when catalog has no trim info.
        source_filter:    If set, hard-filter catalog by this source string.

    Returns:
        (EditDecision, list[ShotRequest])
    """
    beats = _split_beats(script)
    requests = _build_shot_requests(
        beats,
        preferred_source=preferred_source,
        beat_duration=beat_duration,
    )
    matched = _match_candidates(
        requests,
        db_path=db_path,
        top_k=top_k,
        source_filter=source_filter,
    )
    decision = _assemble_edit_decision(matched)
    return decision, requests


# ── CLI ────────────────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ccv2-script",
        description=(
            "Turn a voiceover script into an EditDecision JSON by matching "
            "each beat to the best clip in the personal library."
        ),
        epilog=(
            "Plain-text example:\n"
            "  ccv2-script my_script.txt --output edit.json\n\n"
            "JSON beats with pre-written queries:\n"
            '  ccv2-script beats.json --show-requests'
        ),
    )
    parser.add_argument(
        "script", nargs="?",
        help="Script file (plain text or JSON array). Reads stdin if omitted.",
    )
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Catalog DB path")
    parser.add_argument("--output", "-o", help="Write EditDecision JSON here (default: stdout)")
    parser.add_argument(
        "--top", type=int, default=1,
        help="Candidates to retrieve per beat — 1 = auto-select best (default)",
    )
    parser.add_argument(
        "--source", default="personal",
        help="Preferred source: personal | approved_collection | licensed (default: personal)",
    )
    parser.add_argument(
        "--beat-duration", type=float, default=5.0,
        help="Default shot length in seconds when catalog has no trim info (default: 5.0)",
    )
    parser.add_argument(
        "--source-filter",
        help="Hard-filter catalog — skip scenes whose source doesn't match this value",
    )
    parser.add_argument(
        "--show-requests", action="store_true",
        help="Print each shot's beat + generated visual_query before the EditDecision",
    )
    args = parser.parse_args(argv)

    if args.script:
        text = Path(args.script).read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            print("Reading script from stdin (Ctrl-D when done)…", file=sys.stderr)
        text = sys.stdin.read()

    if not text.strip():
        print("Error: empty script.", file=sys.stderr)
        return 1

    # JSON beat list with optional pre-written visual queries
    beats_override: Optional[list[str]] = None
    precomputed_queries: Optional[list[str]] = None
    try:
        data = json.loads(text)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            beats_override = [str(d.get("voiceover", "")) for d in data]
            precomputed_queries = [str(d.get("visual_query", "")) for d in data]
    except (json.JSONDecodeError, TypeError):
        pass

    if beats_override:
        requests = _build_shot_requests(
            beats_override,
            preferred_source=args.source,
            beat_duration=args.beat_duration,
            precomputed_queries=precomputed_queries,
        )
        matched = _match_candidates(
            requests,
            db_path=Path(args.db),
            top_k=args.top,
            source_filter=args.source_filter,
        )
        decision = _assemble_edit_decision(matched)
    else:
        decision, requests = script_to_edit_decision(
            text,
            db_path=Path(args.db),
            top_k=args.top,
            preferred_source=args.source,
            beat_duration=args.beat_duration,
            source_filter=args.source_filter,
        )

    if args.show_requests:
        print("\n── Shot Requests ─────────────────────────────────────────────────")
        for req in requests:
            print(f"  {req.shot_id}  visual_query : {req.visual_query!r}")
            print(f"           voiceover   : {req.voiceover_text[:80]!r}")
        print()

    import dataclasses
    output_dict = dataclasses.asdict(decision)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(json.dumps(output_dict, indent=2), encoding="utf-8")
        hit = len(decision.approved_shots)
        total = len(requests)
        print(f"EditDecision → {out_path}  ({hit}/{total} shots matched)")
    else:
        print(json.dumps(output_dict, indent=2))

    return 0 if decision.approved_shots else 1


if __name__ == "__main__":
    sys.exit(main())
