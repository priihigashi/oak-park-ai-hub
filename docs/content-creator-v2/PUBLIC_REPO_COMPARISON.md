# Content Creator V2 — Public Repo and Tool Comparison

Date: 2026-08-05
Scope: public research for local-first Content Creator V2 architecture.
Runtime code changed: no.

## Research conclusion

The strongest pattern is not a single monolithic AI editor. The useful pattern is:

1. local media index
2. transcript and scene boundaries
3. semantic search over clips/frames/transcripts
4. JSON timeline as the edit contract
5. human review UI over the JSON plan
6. deterministic renderer/exporter
7. provenance log

This matches the target architecture:

`Idea -> Script -> Shot Plan -> Semantic Clip Search -> Timeline JSON -> Human Approval -> Renderer -> Export / Provenance Log`

## Comparison table

| Tool / pattern | Relevant finding | Adopt for V2 | Decision |
|---|---|---:|---:|
| Remotion | Programmatic video rendering and editor/app embedding are mature patterns. | Use as renderer after Timeline JSON is approved. | REUSE LATER |
| Remotion Timeline / React timelines | Timeline UI is a reusable pattern, but not necessary for Package 0. | Use as reference for review UI, not immediate build target. | REPLACE LATER / DO NOT TOUCH YET |
| FableCut | JSON timeline as editable project contract is directly aligned with V2. | Copy the JSON-first mental model. | ADAPT |
| OpenChatCut | Local-first editor + agent + timeline + Remotion stack matches the long-term direction. | Study architecture; do not clone wholesale. | ADAPT |
| OpenCut AI | Local/self-hosted editor with AI features and FFmpeg export validates privacy-first direction. | Use as product-pattern reference. | ADAPT |
| FFmpegLab | Offline-first FFmpeg-native editing emphasizes transparent commands. | Copy command/provenance transparency. | ADAPT |
| Kinocut | Guardrailed MCP/CLI video editing and video receipts match agent safety goals. | Copy guardrail + receipt pattern. | ADAPT |
| PySceneDetect | Established scene boundary detection with CLI/API and contact-image support. | Use for scene segmentation and thumbnails/contact sheets. | REUSE |
| CLIP / image-text embeddings | Core pattern for semantic image/video search. | Use local embeddings over sampled frames and metadata. | REUSE |
| WhisperX | Word-level timestamps and VAD/forced alignment improve transcript-to-edit accuracy. | Replace/extend basic transcript timing where precise caption/edit boundaries matter. | EXTEND |
| osxphotos | Safe Apple Photos export with metadata sidecars avoids fragile direct database reads. | Use export-driven Apple Photos integration; do not read Photos.sqlite directly. | REUSE |
| Descript | Transcript-based editing and scenes are useful UX patterns. | Copy script-first review pattern, not cloud dependency. | ADAPT |
| Adobe Premiere | Scene Edit Detection and text-based editing validate cut-detection + transcript edit workflow. | Use as pattern only. | ADAPT |
| CapCut / Gling | Fast creator UX proves demand, but they are not reliable canonical storage or local-first infrastructure. | Use as benchmarking reference only. | DO NOT BUILD AGAINST NOW |

## Public patterns to copy

### 1. JSON timeline as the source of truth

Copy this pattern immediately. The plan should not be hidden inside Python function calls or one-off HTML.

Required object families:

- `project`
- `script`
- `shot_plan`
- `assets`
- `semantic_matches`
- `tracks`
- `clips`
- `captions`
- `overlays`
- `approval`
- `export_settings`
- `provenance`

### 2. Agent writes JSON; renderer executes deterministically

The AI should plan and rank. It should not directly mutate videos in opaque ways.

Renderer should read a validated timeline and produce the same output for the same inputs.

### 3. Local media index first

V2 should index local/exported media before using cloud content sources.

Index should include:

- file path or stable exported asset ID
- media type
- duration
- capture date
- album/project labels
- transcript where available
- scene boundaries
- sampled frame thumbnails
- embedding references
- provenance and permissions

### 4. Scene detection and contact sheets

Before semantic search, generate cheap visual review artifacts:

- scene boundaries
- representative frames
- contact sheet
- low-res proxy files

This gives human-review visibility before expensive rendering.

### 5. Transcript-based edit controls

Script and transcript should remain first-class objects. Text editing should map to clip/caption/timing patches.

### 6. Human approval before render/export

Approval should happen at the timeline level, not after the render is already expensive.

Recommended statuses:

- `draft_timeline`
- `needs_review`
- `revision_requested`
- `approved_to_render`
- `rendered_preview`
- `approved_to_export`
- `exported`

### 7. Provenance receipt

Every export should produce a receipt:

- timeline hash
- input assets
- source URLs or local source references
- transcript source
- embedding index version
- renderer version
- ffmpeg/remotion command/version
- output path
- approval timestamp

## What not to copy

### Do not copy full editor scope now

A full CapCut/Premiere clone is out of scope. Package 0 needs contracts and safety, not an editor UI.

### Do not copy cloud-first product assumptions

Descript/CapCut/Premiere are useful UX references, but V2 must protect private media and preserve canonical workspace routing.

### Do not copy direct Apple Photos database access

Use export-driven workflows and sidecars. Direct reads of Photos internals are fragile and risky.

### Do not copy provider sprawl

Do not rebuild the retired 8-tier video source cascade. Keep V2 clean:

1. local/exported media
2. curated clip collections
3. approved public/stock fallbacks where licensing/provenance is clear

## Candidate dependencies to evaluate in Package 0/1

| Dependency | Purpose | Risk |
|---|---|---|
| `PySceneDetect` | scene boundaries, representative frames | Low; mature, Python-friendly. |
| `ffmpeg` / `imageio_ffmpeg` | deterministic render/export operations | Low; already part of existing manual builder guidance. |
| `osxphotos` | Apple Photos export with sidecars | Medium; macOS dependency but safer than Photos.sqlite. |
| CLIP / OpenCLIP / MobileCLIP-like model | local semantic search | Medium; model size/performance on M3 8GB must be tested. |
| SQLite + sqlite-vec/FAISS/Chroma | local index | Medium; choose simplest local index first. |
| WhisperX | word-level transcript alignment | Medium; heavier than Whisper API; use when timing needs precision. |
| Remotion | final programmatic renderer | Medium; keep frozen until timeline schema is stable. |

## Package recommendation

Package 0 should not add these dependencies yet except schemas/tests. Package 1 can prototype local indexing with tiny sample fixtures and no personal media committed.

## Reference URLs

- Remotion: https://www.remotion.dev/
- React Video Editor / Remotion clone pattern: https://github.com/openvideodev/react-video-editor
- FableCut JSON timeline pattern: https://github.com/ronak-create/FableCut
- OpenChatCut: https://github.com/0xsline/OpenChatCut
- OpenCut AI: https://github.com/Ekaanth/OpenCut-AI
- PySceneDetect docs: https://www.scenedetect.com/docs/latest/
- CLIP: https://github.com/openai/CLIP
- WhisperX: https://github.com/m-bain/whisperX
- osxphotos: https://github.com/RhetTbull/osxphotos
- Descript help: https://help.descript.com/
- Adobe Scene Edit Detection: https://helpx.adobe.com/premiere/desktop/edit-projects/change-clip-sequence/detect-edit-points-using-scene-edit-detection.html
