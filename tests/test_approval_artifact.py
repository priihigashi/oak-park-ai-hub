"""Tests for content_creator_v2.approval_artifact (step 7 of 10)."""

from __future__ import annotations

import dataclasses
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.content_creator_v2.contracts import (
    ApprovedShot,
    ClipCandidate,
    EditDecision,
    ShotRequest,
)


def _make_shot(shot_id: str = "shot_001") -> ShotRequest:
    return ShotRequest(
        shot_id=shot_id,
        voiceover_text="Worker applies epoxy to garage floor.",
        visual_query="worker in safety gear applying epoxy to concrete garage floor",
        preferred_source="personal",
        fallback_sources=["approved_collection", "licensed"],
        duration_seconds=5.0,
        must_show=["safety gear"],
        avoid=["competitor logo"],
    )


def _make_candidate(candidate_id: str = "shot_001_c01", score: float = 0.85) -> ClipCandidate:
    return ClipCandidate(
        candidate_id=candidate_id,
        scene_id="scene_abc",
        public_url=None,
        score=score,
        reason="visual=0.90 text=0.70",
        thumbnail="/path/thumb.png",
        trim_start=2.0,
        trim_end=7.0,
        provenance={"asset_path": "/clips/floor.mp4", "source": "personal"},
    )


# ── generate_manifest ──────────────────────────────────────────────────────


def test_generate_manifest_structure():
    from scripts.content_creator_v2.approval_artifact import generate_manifest

    shot = _make_shot()
    mock_catalog = MagicMock()

    with patch("scripts.content_creator_v2.approval_artifact._search_candidates") as mock_search:
        mock_search.return_value = [_make_candidate()]
        manifest = generate_manifest([shot], mock_catalog, top_k=3)

    assert manifest["schema_version"] == "1"
    assert manifest["total_shots"] == 1
    assert manifest["pending"] == 1
    assert manifest["approved"] == 0
    assert len(manifest["shots"]) == 1

    entry = manifest["shots"][0]
    assert entry["shot_id"] == "shot_001"
    assert entry["decision"] == "pending"
    assert entry["selected_candidate_id"] is None
    assert len(entry["candidates"]) == 1
    assert entry["candidates"][0]["candidate_id"] == "shot_001_c01"


def test_generate_manifest_empty_shots():
    from scripts.content_creator_v2.approval_artifact import generate_manifest

    mock_catalog = MagicMock()
    manifest = generate_manifest([], mock_catalog)

    assert manifest["total_shots"] == 0
    assert manifest["shots"] == []


def test_generate_manifest_no_candidates():
    from scripts.content_creator_v2.approval_artifact import generate_manifest

    shot = _make_shot()
    mock_catalog = MagicMock()

    with patch("scripts.content_creator_v2.approval_artifact._search_candidates") as mock_search:
        mock_search.return_value = []
        manifest = generate_manifest([shot], mock_catalog)

    assert manifest["shots"][0]["candidates"] == []


# ── apply_decisions ────────────────────────────────────────────────────────


def _make_manifest_with_decision(decision: str = "approve") -> dict:
    candidate = dataclasses.asdict(_make_candidate())
    return {
        "schema_version": "1",
        "total_shots": 1,
        "shots": [
            {
                "shot_id": "shot_001",
                "voiceover_text": "Test beat.",
                "visual_query": "test query",
                "duration_seconds": 5.0,
                "preferred_source": "personal",
                "must_show": [],
                "avoid": [],
                "decision": decision,
                "selected_candidate_id": "shot_001_c01",
                "notes": "",
                "candidates": [candidate],
            }
        ],
    }


def test_apply_decisions_approve():
    from scripts.content_creator_v2.approval_artifact import apply_decisions

    manifest = _make_manifest_with_decision("approve")
    decision = apply_decisions(manifest)

    assert isinstance(decision, EditDecision)
    assert len(decision.approved_shots) == 1
    shot = decision.approved_shots[0]
    assert shot.shot_id == "shot_001"
    assert shot.selected_candidate.candidate_id == "shot_001_c01"
    assert shot.final_trim_start == 2.0
    assert shot.final_trim_end == 7.0


def test_apply_decisions_reject_skipped():
    from scripts.content_creator_v2.approval_artifact import apply_decisions

    manifest = _make_manifest_with_decision("reject")
    decision = apply_decisions(manifest)

    assert len(decision.approved_shots) == 0


def test_apply_decisions_pending_skipped():
    from scripts.content_creator_v2.approval_artifact import apply_decisions

    manifest = _make_manifest_with_decision("pending")
    decision = apply_decisions(manifest)

    assert len(decision.approved_shots) == 0


def test_apply_decisions_missing_candidate_id():
    from scripts.content_creator_v2.approval_artifact import apply_decisions

    candidate = dataclasses.asdict(_make_candidate())
    manifest = {
        "shots": [
            {
                "shot_id": "shot_001",
                "decision": "approve",
                "selected_candidate_id": None,  # not filled in
                "notes": "",
                "candidates": [candidate],
            }
        ]
    }
    decision = apply_decisions(manifest)
    assert len(decision.approved_shots) == 0


def test_apply_decisions_unknown_candidate_id():
    from scripts.content_creator_v2.approval_artifact import apply_decisions

    candidate = dataclasses.asdict(_make_candidate())
    manifest = {
        "shots": [
            {
                "shot_id": "shot_001",
                "decision": "approve",
                "selected_candidate_id": "shot_001_c99",  # doesn't exist
                "notes": "",
                "candidates": [candidate],
            }
        ]
    }
    decision = apply_decisions(manifest)
    assert len(decision.approved_shots) == 0


def test_apply_decisions_multi_shot_mixed():
    from scripts.content_creator_v2.approval_artifact import apply_decisions

    c1 = dataclasses.asdict(_make_candidate("shot_001_c01"))
    c2 = dataclasses.asdict(_make_candidate("shot_002_c01"))
    manifest = {
        "shots": [
            {
                "shot_id": "shot_001",
                "decision": "approve",
                "selected_candidate_id": "shot_001_c01",
                "notes": "looks good",
                "candidates": [c1],
            },
            {
                "shot_id": "shot_002",
                "decision": "reject",
                "selected_candidate_id": "shot_002_c01",
                "notes": "",
                "candidates": [c2],
            },
        ]
    }
    decision = apply_decisions(manifest)
    assert len(decision.approved_shots) == 1
    assert decision.approved_shots[0].shot_id == "shot_001"


# ── round-trip: generate → apply ──────────────────────────────────────────


def test_roundtrip_generate_then_apply():
    from scripts.content_creator_v2.approval_artifact import apply_decisions, generate_manifest

    shot = _make_shot()
    mock_catalog = MagicMock()

    with patch("scripts.content_creator_v2.approval_artifact._search_candidates") as mock_search:
        mock_search.return_value = [_make_candidate()]
        manifest = generate_manifest([shot], mock_catalog)

    # Simulate user approving the first candidate
    manifest["shots"][0]["decision"] = "approve"
    manifest["shots"][0]["selected_candidate_id"] = "shot_001_c01"

    decision = apply_decisions(manifest)

    assert len(decision.approved_shots) == 1
    assert decision.approved_shots[0].selected_candidate.score == 0.85
