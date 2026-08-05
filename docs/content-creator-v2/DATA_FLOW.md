# Content Creator V2 — Data Flow

Date: 2026-08-05
Runtime code changed: no.

## Target pipeline

```text
Idea
  -> Script
  -> Shot Plan
  -> Semantic Clip Search
  -> Timeline JSON
  -> Human Approval
  -> Renderer
  -> Export / Provenance Log
```

The pipeline is offline-first where possible and must be workspace-safe before it saves anything.

## Creation Gate data flow

Before any artifact is created, moved, or saved:

```text
incoming item/request
  -> identify product/flow/doc/task/asset type
  -> search canonical registries
  -> search exact/similar Drive names
  -> search GitHub docs/code if technical
  -> classify target folder role
  -> duplicate decision
  -> save/update/link OR route to Duplicate Review
```

Creation Gate output:

```json
{
  "item_type": "product|flow|doc|tracker|asset|task|unknown",
  "canonical_owner_product": "string",
  "canonical_row": "Flow Plans Tracker / Focus / Drive Map reference or null",
  "canonical_folder": "Drive path or folder id or null",
  "folder_role": "ACTIVE|REFERENCE|ARCHIVE|BACKUP|SYSTEM|UNKNOWN",
  "related_focus_row": "string|null",
  "related_github_doc_repo": "string|null",
  "duplicate_status": "none|possible_duplicate|confirmed_duplicate|needs_review",
  "decision": "update_existing|create_new|link_existing|route_duplicate_review|refuse",
  "reason": "string"
}
```

## Stage 1 — Idea

Inputs:

- capture URL
- manual note
- local media selection
- content inspiration
- existing Focus row
- existing Flow Plans row

Required output:

```json
{
  "idea_id": "IDEA-YYYYMMDD-slug",
  "source_type": "capture|manual_note|local_media|reference",
  "source_ref": "url/path/doc id",
  "canonical_owner_product": "OPC|Brazil News|USA News|Jarvis|Athena|other",
  "niche": "opc|brazil|usa|cross|unknown",
  "creation_gate": {},
  "provenance": {}
}
```

Decision: `EXTEND` current capture pipeline.

## Stage 2 — Script

Inputs:

- Idea object
- transcript where available
- capture notes
- content format registry
- brand/editorial rules

Output:

```json
{
  "script_id": "SCRIPT-...",
  "idea_id": "IDEA-...",
  "language": "pt|en|mixed",
  "hook": "string",
  "body": ["line 1", "line 2"],
  "cta": "string|null",
  "claims": [],
  "source_requirements": [],
  "approval_status": "draft|approved|revision_requested"
}
```

Decision: `BUILD NEW` as a separate contract, not hidden inside template generation.

## Stage 3 — Shot Plan

Inputs:

- Script
- content format
- platform size
- available media index

Output:

```json
{
  "shot_plan_id": "SHOTPLAN-...",
  "script_id": "SCRIPT-...",
  "shots": [
    {
      "shot_id": "S001",
      "purpose": "hook|proof|context|transition|cta",
      "visual_query": "contractor measuring foundation",
      "required_media_type": "video|image|text|graphic|any",
      "duration_s": 2.5,
      "must_show": ["floor", "paint", "before/after"],
      "avoid": ["private faces", "license plates"],
      "fallback": "text_card|static_image|manual_review"
    }
  ]
}
```

Decision: `BUILD NEW`.

## Stage 4 — Semantic Clip Search

Inputs:

- Shot Plan
- local media index
- curated clip collections
- public/provenance-approved sources

Output:

```json
{
  "shot_id": "S001",
  "matches": [
    {
      "asset_id": "ASSET-...",
      "source_path_or_url": "string",
      "start_s": 10.2,
      "end_s": 13.4,
      "score": 0.84,
      "match_reason": "matches visual_query and contains visible tile floor",
      "license_or_rights": "owned|cc|stock|unknown",
      "safety_flags": []
    }
  ]
}
```

Decision: `BUILD NEW`, while adapting `motion_sources.py` source/provenance concepts.

## Stage 5 — Timeline JSON

Inputs:

- approved Script
- Shot Plan
- semantic matches
- brand/layout rules

Output: central contract.

Minimum structure:

```json
{
  "schema_version": "0.1.0",
  "project": {
    "project_id": "CCV2-...",
    "canonical_owner_product": "OPC",
    "platform": "instagram_reel",
    "canvas": {"width": 1080, "height": 1920, "fps": 30}
  },
  "script": {},
  "shot_plan": [],
  "assets": [],
  "tracks": [
    {
      "track_id": "video_1",
      "type": "video",
      "clips": [
        {
          "clip_id": "C001",
          "asset_id": "ASSET-001",
          "timeline_start_s": 0,
          "duration_s": 2.5,
          "source_start_s": 10.2,
          "source_end_s": 12.7,
          "transform": {"fit": "cover", "position": "center"}
        }
      ]
    }
  ],
  "captions": [],
  "overlays": [],
  "approval": {
    "status": "needs_review",
    "review_notes": []
  },
  "export_settings": {},
  "provenance": {}
}
```

Decision: `BUILD NEW` and freeze before runtime changes.

## Stage 6 — Human Approval

Inputs:

- timeline JSON
- contact sheet / preview proxy
- script and shot plan

Output:

```json
{
  "approval_status": "approved_to_render|revision_requested|rejected",
  "reviewer": "Priscila",
  "notes": [
    {"target": "shot:S003", "action": "replace_clip", "note": "use construction before/after not generic stock"}
  ]
}
```

Decision: `EXTEND` current approval handler.

## Stage 7 — Renderer

Inputs:

- approved timeline JSON
- local/proxy assets
- render profile

Potential engines:

- Remotion for programmatic layouts/motion graphics
- FFmpeg for deterministic trimming/concat/caption burns
- Playwright for HTML-to-PNG slides
- imageio_ffmpeg for simple MP4 assembly

Decision: `DO NOT TOUCH YET` until schema and test fixtures exist.

## Stage 8 — Export / Provenance Log

Output:

```json
{
  "export_id": "EXPORT-...",
  "timeline_hash": "sha256:...",
  "renderer": "ffmpeg|remotion|playwright|mixed",
  "renderer_version": "string",
  "input_assets": [],
  "output_files": [],
  "canonical_folder": "string",
  "folder_role": "ACTIVE",
  "approval_ref": "string",
  "created_at": "ISO-8601",
  "warnings": []
}
```

Decision: `BUILD NEW`.

## Failure routing

| Failure | Required route |
|---|---|
| no canonical home | Duplicate Review / canonical-home review |
| target folder is BACKUP | refuse; flag rescue if live file exists there |
| target folder is ARCHIVE | refuse unless archive action explicitly requested |
| low classifier confidence | Unrouted / Pipeline Failures |
| duplicate/similar doc exists | Duplicate Review |
| unknown rights/license | manual approval required |
| timeline schema invalid | block render |
| missing asset | block render or fallback according to shot plan |
| personal/private media uncertainty | manual review; do not commit/export publicly |
