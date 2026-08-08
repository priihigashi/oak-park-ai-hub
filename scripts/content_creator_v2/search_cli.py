"""
Content Creator V2 — natural-language scene search CLI (Sprint 2).

Accepts a text query and returns ranked ClipCandidates from the local catalog.

Ranking strategy (in priority order):
  1. Cosine similarity on text_embedding (semantic, requires embeddings indexed).
  2. Keyword match on transcript text (always available when scenes are transcribed).
  3. Quality-signal boost: +0.05 for blur_score > 1000, +0.03 for brightness 0.25–0.75.

Coding order step 4 of 10.
Master plan: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .catalog import Catalog, DEFAULT_DB
from .contracts import ClipCandidate, Scene


# ── scoring constants ─────────────────────────────────────────────────────────

_EMBEDDING_WEIGHT = 0.70  # share of the final score when embeddings are present
_KEYWORD_WEIGHT   = 0.25  # transcript keyword-hit share
_QUALITY_BLUR_BOOST      = 0.05   # added when blur_score > 1000 (sharp frame)
_QUALITY_BRIGHTNESS_BOOST = 0.03  # added when brightness is in 0.25–0.75 range
_MIN_SCORE = 0.01  # drop results below this — avoids returning completely unrelated clips


# ── embedding helper ──────────────────────────────────────────────────────────

def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _embed_query(query: str) -> Optional[list[float]]:
    """
    Embed `query` using sentence-transformers (all-MiniLM-L6-v2).
    Returns None if the library is not installed — search falls back to keywords.
    """
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        model = SentenceTransformer("all-MiniLM-L6-v2")
        vec = model.encode(query, normalize_embeddings=True)
        return vec.tolist()
    except Exception:
        return None


# ── keyword search ────────────────────────────────────────────────────────────

def _keyword_score(query: str, transcript_json: Optional[str]) -> float:
    """
    Simple TF-style score: fraction of query tokens that appear in the transcript.
    Returns 0.0 if no transcript is available.
    """
    if not transcript_json:
        return 0.0
    try:
        data = json.loads(transcript_json)
        text = data.get("text", "") if isinstance(data, dict) else str(data)
    except Exception:
        text = transcript_json

    text_lower = text.lower()
    tokens = [t for t in re.split(r"\W+", query.lower()) if t]
    if not tokens:
        return 0.0
    hits = sum(1 for tok in tokens if tok in text_lower)
    return hits / len(tokens)


# ── quality boost ─────────────────────────────────────────────────────────────

def _quality_boost(quality_signals: dict) -> float:
    boost = 0.0
    blur = quality_signals.get("blur_score", 0)
    if blur > 1000:
        boost += _QUALITY_BLUR_BOOST
    brightness = quality_signals.get("brightness", -1)
    if 0.25 <= brightness <= 0.75:
        boost += _QUALITY_BRIGHTNESS_BOOST
    return boost


# ── public search function ────────────────────────────────────────────────────

def search_scenes(
    query: str,
    *,
    db_path: Path = DEFAULT_DB,
    top_k: int = 10,
    source_filter: Optional[str] = None,
) -> list[ClipCandidate]:
    """
    Search the catalog for scenes matching `query`.

    Args:
        query:         Natural-language description, e.g. "outdoor kitchen tiles".
        db_path:       Path to the SQLite catalog (default ~/.content_creator_v2/catalog.db).
        top_k:         Maximum number of results to return.
        source_filter: If set, only consider scenes whose asset.source matches this string.

    Returns:
        Ranked list of ClipCandidates, best first.  Empty if catalog has no scenes.
    """
    with Catalog(db_path) as catalog:
        rows = catalog.conn.execute("""
            SELECT s.scene_id, s.asset_id, s.start_time, s.end_time,
                   s.transcript, s.keyframe_paths, s.visual_embedding,
                   s.text_embedding, s.quality_signals,
                   a.source, a.path
            FROM scenes s
            JOIN assets a ON a.asset_id = s.asset_id
        """).fetchall()

    if not rows:
        return []

    query_vec = _embed_query(query)

    candidates: list[tuple[float, Scene, str, str]] = []  # (score, scene, asset_path, asset_source)

    for row in rows:
        asset_source = row["source"]
        asset_path   = row["path"]

        if source_filter and asset_source != source_filter:
            continue

        scene = Scene(
            scene_id=row["scene_id"],
            asset_id=row["asset_id"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            transcript=row["transcript"],
            keyframe_paths=json.loads(row["keyframe_paths"]),
            visual_embedding=json.loads(row["visual_embedding"]) if row["visual_embedding"] else None,
            text_embedding=json.loads(row["text_embedding"]) if row["text_embedding"] else None,
            quality_signals=json.loads(row["quality_signals"]),
        )

        # --- semantic score (0.0 if either side lacks an embedding) ---
        sem_score = 0.0
        if query_vec and scene.text_embedding:
            sem_score = max(0.0, _cosine(query_vec, scene.text_embedding))

        # --- keyword score ---
        kw_score = _keyword_score(query, scene.transcript)

        # --- combined base score ---
        if query_vec and scene.text_embedding:
            base = sem_score * _EMBEDDING_WEIGHT + kw_score * _KEYWORD_WEIGHT
        else:
            base = kw_score  # no embeddings → keyword only

        score = base + _quality_boost(scene.quality_signals)

        if score >= _MIN_SCORE:
            candidates.append((score, scene, asset_path, asset_source))

    candidates.sort(key=lambda t: t[0], reverse=True)
    candidates = candidates[:top_k]

    results: list[ClipCandidate] = []
    for score, scene, asset_path, asset_source in candidates:
        thumbnail = scene.keyframe_paths[0] if scene.keyframe_paths else None
        reason = _build_reason(query, score, scene)
        results.append(ClipCandidate(
            candidate_id=scene.scene_id,
            scene_id=scene.scene_id,
            public_url=None,
            score=round(score, 4),
            reason=reason,
            thumbnail=thumbnail,
            trim_start=scene.start_time,
            trim_end=scene.end_time,
            provenance={"source": asset_source, "asset_path": asset_path},
        ))

    return results


def _build_reason(query: str, score: float, scene: Scene) -> str:
    parts = [f"score={score:.3f}"]
    if scene.text_embedding:
        parts.append("semantic-match")
    if scene.transcript:
        kw = _keyword_score(query, scene.transcript)
        if kw > 0:
            parts.append(f"keyword-hit={kw:.0%}")
    qs = scene.quality_signals
    if qs.get("blur_score", 0) > 1000:
        parts.append("sharp")
    br = qs.get("brightness", -1)
    if 0.25 <= br <= 0.75:
        parts.append("good-exposure")
    return "; ".join(parts)


# ── CLI entry point ───────────────────────────────────────────────────────────

def _print_results(results: list[ClipCandidate], *, verbose: bool = False) -> None:
    if not results:
        print("No matching scenes found.")
        return
    for i, c in enumerate(results, 1):
        duration = ""
        if c.trim_start is not None and c.trim_end is not None:
            duration = f"  [{c.trim_start:.1f}s–{c.trim_end:.1f}s]"
        asset = c.provenance.get("asset_path", "")
        thumb = f"  thumbnail={c.thumbnail}" if verbose and c.thumbnail else ""
        print(f"{i:>3}. score={c.score:.3f}{duration}  {asset}")
        print(f"       {c.reason}{thumb}")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ccv2-search",
        description="Search the Content Creator V2 catalog with a natural-language query.",
    )
    parser.add_argument("query", nargs="+", help="Natural-language search query")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to catalog.db")
    parser.add_argument("--top", type=int, default=10, help="Max results (default 10)")
    parser.add_argument("--source", default=None, help="Filter by asset source (e.g. 'personal')")
    parser.add_argument("--verbose", action="store_true", help="Show thumbnail paths")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    query = " ".join(args.query)
    results = search_scenes(
        query,
        db_path=Path(args.db),
        top_k=args.top,
        source_filter=args.source,
    )

    if args.as_json:
        import dataclasses
        print(json.dumps([dataclasses.asdict(r) for r in results], indent=2))
    else:
        _print_results(results, verbose=args.verbose)

    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
