"""Sprint 2-C: tests for search.search() — similarity ranking over vector embeddings.

All tests use tmp_path for SQLite isolation. embed_text is patched so no
open_clip_torch or GPU is required in CI.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.content_creator_v2.catalog import Catalog
from scripts.content_creator_v2.contracts import MediaAsset, Scene
from scripts.content_creator_v2.search import search


# ---------------------------------------------------------------------------
# fixtures / helpers
# ---------------------------------------------------------------------------

EMBED_PATCH = "scripts.content_creator_v2.search.embed_text"

# Unit query vector used across most tests
QUERY_VEC = [1.0, 0.0, 0.0]


def _asset(asset_id: str, path: str) -> MediaAsset:
    return MediaAsset(
        asset_id=asset_id,
        path=path,
        source="personal",
        owner="priscila",
        captured_at=None,
        duration=10.0,
        width=1080,
        height=1920,
        orientation="portrait",
        checksum=asset_id,  # reuse id as checksum — unique per test
    )


def _scene(
    scene_id: str,
    asset_id: str,
    *,
    visual_emb=None,
    text_emb=None,
    start: float = 0.0,
    end: float = 5.0,
) -> Scene:
    return Scene(
        scene_id=scene_id,
        asset_id=asset_id,
        start_time=start,
        end_time=end,
        transcript=None,
        keyframe_paths=[],
        visual_embedding=visual_emb,
        text_embedding=text_emb,
    )


def _build_ranked_catalog(tmp_path: Path) -> Catalog:
    """
    3-asset catalog with visual-only embeddings at known cosine distances from [1,0,0].

    Query [1, 0, 0]:
      asset-high:  [1.0, 0.0, 0.0] → cosine 1.0
      asset-mid:   [0.6, 0.8, 0.0] → cosine 0.6  (unit vector, dot = 0.6)
      asset-low:   [0.0, 0.0, 1.0] → cosine 0.0
    """
    cat = Catalog(tmp_path / "catalog.db")
    specs = [
        ("asset-high", [1.0, 0.0, 0.0]),
        ("asset-mid",  [0.6, 0.8, 0.0]),
        ("asset-low",  [0.0, 0.0, 1.0]),
    ]
    for asset_id, vec in specs:
        cat.upsert_asset(_asset(asset_id, f"/videos/{asset_id}.mp4"))
        cat.upsert_scene(_scene(f"scene-{asset_id}", asset_id, visual_emb=vec))
    return cat


# ---------------------------------------------------------------------------
# ranking
# ---------------------------------------------------------------------------

class TestRanking:
    def test_top_result_is_closest_match(self, tmp_path):
        with _build_ranked_catalog(tmp_path) as cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                results = search("construction roof", cat)

        assert results[0].scene_id == "scene-asset-high"

    def test_results_are_sorted_descending_by_score(self, tmp_path):
        with _build_ranked_catalog(tmp_path) as cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                results = search("construction roof", cat)

        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_all_three_assets_returned_by_default(self, tmp_path):
        with _build_ranked_catalog(tmp_path) as cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                results = search("construction roof", cat)

        assert len(results) == 3


# ---------------------------------------------------------------------------
# top_k
# ---------------------------------------------------------------------------

class TestTopK:
    def test_top_k_limits_result_count(self, tmp_path):
        with _build_ranked_catalog(tmp_path) as cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                results = search("construction roof", cat, top_k=2)

        assert len(results) == 2

    def test_top_k_keeps_highest_scoring(self, tmp_path):
        with _build_ranked_catalog(tmp_path) as cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                all_r = search("roof", cat)
                top2  = search("roof", cat, top_k=2)

        assert top2[0].scene_id == all_r[0].scene_id
        assert top2[1].scene_id == all_r[1].scene_id


# ---------------------------------------------------------------------------
# embedding variants
# ---------------------------------------------------------------------------

class TestEmbeddingVariants:
    def test_visual_only_score_equals_visual_score(self, tmp_path):
        """A scene with only visual_embedding: score must equal visual_score."""
        cat = Catalog(tmp_path / "db")
        cat.upsert_asset(_asset("a-vis", "/v/vis.mp4"))
        cat.upsert_scene(_scene("s-vis", "a-vis", visual_emb=[1.0, 0.0, 0.0]))

        with cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                results = search("roof tiles", cat)

        assert len(results) == 1
        r = results[0]
        assert abs(r.score - r.visual_score) < 1e-9

    def test_text_only_score_equals_text_score(self, tmp_path):
        """A scene with only text_embedding: score must equal text_score."""
        cat = Catalog(tmp_path / "db")
        cat.upsert_asset(_asset("a-txt", "/v/txt.mp4"))
        cat.upsert_scene(_scene("s-txt", "a-txt", text_emb=[1.0, 0.0, 0.0]))

        with cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                results = search("spoken content", cat)

        assert len(results) == 1
        r = results[0]
        assert abs(r.score - r.text_score) < 1e-9

    def test_scene_without_any_embedding_excluded(self, tmp_path):
        """Scenes with no embeddings must not appear in results."""
        cat = Catalog(tmp_path / "db")
        cat.upsert_asset(_asset("a-bare", "/v/bare.mp4"))
        cat.upsert_scene(_scene("s-bare", "a-bare"))  # no embeddings

        with cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                results = search("anything", cat)

        assert results == []


# ---------------------------------------------------------------------------
# empty catalog
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_catalog_returns_empty_list(self, tmp_path):
        with Catalog(tmp_path / "db") as cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                results = search("anything", cat)

        assert results == []

    def test_search_result_fields_populated_correctly(self, tmp_path):
        """SearchResult carries the right asset_id, path, and time bounds."""
        cat = Catalog(tmp_path / "db")
        cat.upsert_asset(_asset("a-chk", "/videos/check.mp4"))
        cat.upsert_scene(
            _scene("s-chk", "a-chk", visual_emb=[1.0, 0.0, 0.0], start=2.0, end=7.5)
        )

        with cat:
            with patch(EMBED_PATCH, return_value=QUERY_VEC):
                results = search("test", cat)

        r = results[0]
        assert r.scene_id == "s-chk"
        assert r.asset_id == "a-chk"
        assert r.asset_path == "/videos/check.mp4"
        assert r.start_time == 2.0
        assert r.end_time == 7.5
