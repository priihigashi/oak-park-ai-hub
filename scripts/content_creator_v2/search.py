"""
Content Creator V2 — semantic search CLI (coding order step 4 of 10).

Ranks indexed scenes against a natural-language query using OpenCLIP embeddings.
Visual and transcript embeddings share the same vector space, so one query
can match both what is seen and what is said in a clip.

Usage:
    python -m scripts.content_creator_v2.search "construction crew on roof" --top 10
    python -m scripts.content_creator_v2.search "tile work" --db ~/my-library.db --top 5

Prerequisites:
    1. Index a folder:  python -m scripts.content_creator_v2.catalog <folder>
    2. Extract scenes:  python -m scripts.content_creator_v2.scene_extractor <asset>
    3. Embed all:       python -m scripts.content_creator_v2.embedder --embed-all

Master plan: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .catalog import Catalog, DEFAULT_DB
from .embedder import embed_text

_VISUAL_WEIGHT = 0.7   # keyframe similarity carries more weight for video search
_TEXT_WEIGHT = 0.3     # transcript similarity is secondary but useful for spoken content


@dataclass
class SearchResult:
    scene_id: str
    asset_id: str
    asset_path: str
    start_time: float
    end_time: float
    score: float
    visual_score: float
    text_score: float
    thumbnail: Optional[str]
    transcript_snippet: Optional[str]


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two pre-normalised vectors (dot product)."""
    try:
        import numpy as np
        return float(np.dot(a, b))
    except ImportError:
        # Pure-Python fallback for environments without numpy
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(x * x for x in b) ** 0.5
        return dot / (na * nb) if na and nb else 0.0


def _snippet(transcript_json: Optional[str], max_chars: int = 80) -> Optional[str]:
    if not transcript_json:
        return None
    try:
        text = json.loads(transcript_json).get("text", "").strip()
    except (json.JSONDecodeError, TypeError):
        text = str(transcript_json).strip()
    if not text:
        return None
    return text[:max_chars] + ("…" if len(text) > max_chars else "")


def search(
    query: str,
    catalog: Catalog,
    *,
    top_k: int = 10,
    visual_weight: float = _VISUAL_WEIGHT,
    text_weight: float = _TEXT_WEIGHT,
) -> list[SearchResult]:
    """
    Search indexed scenes by natural-language query.

    Encodes the query with the OpenCLIP text encoder (same space as keyframe
    and transcript embeddings) and ranks scenes by weighted cosine similarity.
    Scenes with no embeddings are excluded from results.

    Args:
        query:          E.g. "roof tiles being installed" or "kitchen renovation".
        catalog:        Open Catalog instance.
        top_k:          Maximum results to return (default 10).
        visual_weight:  Weight for keyframe similarity (default 0.7).
        text_weight:    Weight for transcript similarity (default 0.3).

    Returns:
        List of SearchResult sorted by combined score, descending.
    """
    query_vec = embed_text(query)
    if query_vec is None:
        raise RuntimeError(
            "Could not encode query — is open_clip_torch installed? "
            "Run: pip install open_clip_torch torch"
        )

    asset_paths: dict[str, str] = {a.asset_id: a.path for a in catalog.all_assets()}

    results: list[SearchResult] = []
    for asset_id, asset_path in asset_paths.items():
        for scene in catalog.scenes_for_asset(asset_id):
            v_score = t_score = 0.0
            has_visual = bool(scene.visual_embedding)
            has_text = bool(scene.text_embedding)

            if not has_visual and not has_text:
                continue  # not embedded yet — run embed_all first

            if has_visual:
                v_score = _cosine(query_vec, scene.visual_embedding)
            if has_text:
                t_score = _cosine(query_vec, scene.text_embedding)

            if has_visual and has_text:
                total_w = visual_weight + text_weight
                score = (visual_weight * v_score + text_weight * t_score) / total_w
            elif has_visual:
                score = v_score
            else:
                score = t_score

            results.append(SearchResult(
                scene_id=scene.scene_id,
                asset_id=asset_id,
                asset_path=asset_path,
                start_time=scene.start_time,
                end_time=scene.end_time,
                score=score,
                visual_score=v_score,
                text_score=t_score,
                thumbnail=scene.keyframe_paths[0] if scene.keyframe_paths else None,
                transcript_snippet=_snippet(scene.transcript),
            ))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


def _print_results(results: list[SearchResult], query: str) -> None:
    print(f'\nSearch: "{query}" — {len(results)} result(s)\n')
    if not results:
        print("  No results. Run embed_all first, or try a different query.")
        print("  Example: python -m scripts.content_creator_v2.embedder --embed-all")
        return

    print(f"{'#':<3}  {'Score':>6}  {'V-sim':>6}  {'T-sim':>6}  {'Time range':>14}  Asset")
    print("─" * 94)
    for i, r in enumerate(results, 1):
        time_range = f"{r.start_time:6.1f}–{r.end_time:.1f}s"
        asset_name = Path(r.asset_path).name[:44]
        print(
            f"{i:<3}  {r.score:>6.3f}  {r.visual_score:>6.3f}  {r.text_score:>6.3f}"
            f"  {time_range:>14}  {asset_name}"
        )
        if r.thumbnail:
            print(f"       thumbnail  : {r.thumbnail}")
        if r.transcript_snippet:
            print(f"       transcript : {r.transcript_snippet}")
    print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Search the personal video library by natural-language query.",
        epilog='Example: python -m scripts.content_creator_v2.search "tile work on bathroom floor" --top 5',
    )
    parser.add_argument("query", help="Natural-language search query")
    parser.add_argument(
        "--db", default=str(DEFAULT_DB),
        help=f"Path to catalog DB (default: {DEFAULT_DB})",
    )
    parser.add_argument("--top", type=int, default=10, help="Results to return (default: 10)")
    parser.add_argument(
        "--visual-weight", type=float, default=_VISUAL_WEIGHT,
        help=f"Weight for visual similarity (default: {_VISUAL_WEIGHT})",
    )
    parser.add_argument(
        "--text-weight", type=float, default=_TEXT_WEIGHT,
        help=f"Weight for transcript similarity (default: {_TEXT_WEIGHT})",
    )
    args = parser.parse_args(argv)

    with Catalog(Path(args.db)) as catalog:
        stats = catalog.stats()
        print(f"Catalog: {stats['assets']} assets, {stats['scenes']} scenes")
        results = search(
            args.query,
            catalog,
            top_k=args.top,
            visual_weight=args.visual_weight,
            text_weight=args.text_weight,
        )
        _print_results(results, args.query)


if __name__ == "__main__":
    main()
