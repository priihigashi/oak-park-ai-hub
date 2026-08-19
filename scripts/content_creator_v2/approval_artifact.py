"""
Content Creator V2 — approval artifact (coding order step 7 of 10).

Generates a JSON approval manifest linking each ShotRequest to its top
clip candidates so Priscila can review and approve/reject them before
the edit decision is locked.

Workflow:
    1. shot_planner.py  → shot_plan.json         (list of ShotRequests)
    2. approval_artifact.py generate             → approval_manifest.json
    3. Edit manifest: set "decision": "approve" and "selected_candidate_id" per shot
    4. approval_artifact.py apply                → edit_decision.json

Usage:
    python -m scripts.content_creator_v2.approval_artifact generate shot_plan.json
    python -m scripts.content_creator_v2.approval_artifact apply approval_manifest.json
    python -m scripts.content_creator_v2.approval_artifact generate shot_plan.json --top-k 3

Master plan: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .catalog import DEFAULT_DB, Catalog
from .contracts import ApprovedShot, ClipCandidate, EditDecision, ShotRequest

_DEFAULT_CANDIDATES_PER_SHOT = 5
_SHOT_REQUEST_FIELDS = {f.name for f in dataclasses.fields(ShotRequest)}
_CLIP_CANDIDATE_FIELDS = {f.name for f in dataclasses.fields(ClipCandidate)}


def _search_candidates(
    shot: ShotRequest,
    catalog: Catalog,
    *,
    top_k: int = _DEFAULT_CANDIDATES_PER_SHOT,
) -> list[ClipCandidate]:
    """Return top-k ClipCandidates for a shot by searching the catalog."""
    from .search import search

    results = search(shot.visual_query, catalog, top_k=top_k)
    candidates: list[ClipCandidate] = []
    for i, r in enumerate(results):
        # Nudge score down when the source doesn't match the shot's preference
        source_tag = "personal" if (r.asset_path and not r.asset_path.startswith("http")) else "licensed"
        penalty = 0.0 if source_tag in [shot.preferred_source] + list(shot.fallback_sources) else 0.2

        candidates.append(
            ClipCandidate(
                candidate_id=f"{shot.shot_id}_c{i + 1:02d}",
                scene_id=r.scene_id,
                public_url=None,
                score=round(max(0.0, r.score - penalty), 4),
                reason=(
                    f"visual={r.visual_score:.3f} text={r.text_score:.3f}"
                    + (f" source_penalty={penalty:.1f}" if penalty else "")
                ),
                thumbnail=r.thumbnail,
                trim_start=r.start_time,
                trim_end=r.end_time,
                provenance={"asset_path": r.asset_path, "source": source_tag},
            )
        )
    # Re-sort after penalty adjustment so the manifest is already ranked
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates


def generate_manifest(
    shots: list[ShotRequest],
    catalog: Catalog,
    *,
    top_k: int = _DEFAULT_CANDIDATES_PER_SHOT,
) -> dict:
    """Search the catalog for each shot and return a review-ready manifest dict."""
    manifest_shots = []
    for shot in shots:
        candidates = _search_candidates(shot, catalog, top_k=top_k)
        manifest_shots.append(
            {
                "shot_id": shot.shot_id,
                "voiceover_text": shot.voiceover_text,
                "visual_query": shot.visual_query,
                "duration_seconds": shot.duration_seconds,
                "preferred_source": shot.preferred_source,
                "must_show": shot.must_show,
                "avoid": shot.avoid,
                # ── Fill these in when reviewing ──────────────────────────
                "decision": "pending",          # "approve" | "reject" | "swap"
                "selected_candidate_id": None,  # e.g. "shot_001_c02"
                "notes": "",                    # crop, caption, or swap reason
                # ─────────────────────────────────────────────────────────
                "candidates": [dataclasses.asdict(c) for c in candidates],
            }
        )

    return {
        "schema_version": "1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_shots": len(shots),
        "pending": len(shots),
        "approved": 0,
        "shots": manifest_shots,
    }


def apply_decisions(manifest: dict) -> EditDecision:
    """Convert a reviewed manifest (decisions filled in) into an EditDecision."""
    approved_shots: list[ApprovedShot] = []

    for entry in manifest.get("shots", []):
        if entry.get("decision") != "approve":
            continue
        selected_id = entry.get("selected_candidate_id")
        if not selected_id:
            continue

        candidate_data = next(
            (c for c in entry.get("candidates", []) if c.get("candidate_id") == selected_id),
            None,
        )
        if not candidate_data:
            continue

        candidate = ClipCandidate(**{k: v for k, v in candidate_data.items() if k in _CLIP_CANDIDATE_FIELDS})

        approved_shots.append(
            ApprovedShot(
                shot_id=entry["shot_id"],
                selected_candidate=candidate,
                final_trim_start=float(candidate.trim_start or 0.0),
                final_trim_end=float(candidate.trim_end or 0.0),
                caption=entry.get("notes") or None,
            )
        )

    return EditDecision(
        project_id=f"project_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        created_at=datetime.now(timezone.utc).isoformat(),
        approved_shots=approved_shots,
    )


# ── CLI ──────────────────────────────────────────────────────────────────────

def _cmd_generate(args: argparse.Namespace) -> None:
    shot_plan_path = Path(args.shot_plan)
    if not shot_plan_path.exists():
        sys.exit(f"shot plan not found: {shot_plan_path}")

    with open(shot_plan_path) as f:
        shot_dicts = json.load(f)

    shots = [ShotRequest(**{k: v for k, v in d.items() if k in _SHOT_REQUEST_FIELDS}) for d in shot_dicts]

    catalog = Catalog(Path(args.db) if args.db else DEFAULT_DB)
    manifest = generate_manifest(shots, catalog, top_k=args.top_k)

    out_path = (
        Path(args.output)
        if args.output
        else shot_plan_path.with_name(shot_plan_path.stem + "_approval_manifest.json")
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Manifest → {out_path}")
    print(f"Shots: {manifest['total_shots']} | Candidates per shot: {args.top_k}")
    empty = sum(1 for s in manifest["shots"] if not s["candidates"])
    if empty:
        print(f"Warning: {empty} shot(s) returned no candidates — catalog may be empty or not indexed.")
    print(
        f"\nReview {out_path}:\n"
        f"  • Set \"decision\": \"approve\" and \"selected_candidate_id\": \"<id>\" per shot\n"
        f"  • Then: python -m scripts.content_creator_v2.approval_artifact apply {out_path}"
    )


def _cmd_apply(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        sys.exit(f"manifest not found: {manifest_path}")

    with open(manifest_path) as f:
        manifest = json.load(f)

    pending = [s for s in manifest.get("shots", []) if s.get("decision") == "pending"]
    if pending:
        print(f"Warning: {len(pending)} shot(s) still 'pending' — they will be skipped.")

    decision = apply_decisions(manifest)

    stem = manifest_path.stem.replace("_approval_manifest", "")
    out_path = Path(args.output) if args.output else manifest_path.with_name(stem + "_edit_decision.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dataclasses.asdict(decision), f, indent=2, ensure_ascii=False)

    print(f"Edit decision → {out_path}")
    print(f"Approved shots: {len(decision.approved_shots)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Content Creator V2 — approval artifact (step 7 of 10)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen_p = sub.add_parser("generate", help="Generate approval manifest from a shot plan")
    gen_p.add_argument("shot_plan", help="Path to shot_plan.json (output of shot_planner.py)")
    gen_p.add_argument("--db", help="Catalog DB path (default: library.db)")
    gen_p.add_argument("--top-k", type=int, default=_DEFAULT_CANDIDATES_PER_SHOT, metavar="N")
    gen_p.add_argument("--output", help="Output path for manifest JSON")

    apply_p = sub.add_parser("apply", help="Convert a reviewed manifest to an EditDecision")
    apply_p.add_argument("manifest", help="Path to reviewed approval_manifest.json")
    apply_p.add_argument("--output", help="Output path for edit_decision.json")

    args = parser.parse_args()
    {"generate": _cmd_generate, "apply": _cmd_apply}[args.command](args)


if __name__ == "__main__":
    main()
