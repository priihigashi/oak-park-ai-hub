# Content Creator V2 — MVP Acceleration Repo / App Research

Created: 2026-08-05
Status: research/planning only. Do not install, vendor, clone into production, or copy code before audit.

## Purpose

Priscila challenged the 2–4 week MVP estimate and asked whether public repos / real-world apps can shorten the build.

Answer: yes, but by adapting proven patterns, not by blindly copying a whole repo.

The fastest route is a thin vertical slice:

```text
one approved OPC folder
10–20 videos only
ffprobe metadata
thumbnail/contact sheet
simple search/filter
manual clip selection
edit_decision.json
Remotion/FFmpeg render draft
```

This can potentially reduce the first usable slice from weeks to days if the existing repo cooperates and we do not attempt full Apple Photos/library automation first.

---

## Research categories

### A. Local-first AI video editors / timeline patterns

Use for:
- timeline JSON
- project state model
- hot-reload preview
- edit decision format
- local-first UX
- Remotion or FFmpeg render adapter ideas

Candidates found:
- OpenChatCut: local-first conversational AI video editor, MCP/agent-native, multi-track timeline, Remotion-powered rendering.
- Vanta: open-source AI video engine built on Remotion; its timeline serializes into JSON that Remotion renders to MP4.
- OpenReelio: open-source desktop AI video editor concept with timeline, captions, GPU export.
- Framedeck: open-source AI video editor concept with prompt timeline edits and Remotion rendering.
- openvideodev/react-video-editor: React video editor using Remotion; CapCut/Canva-clone style timeline.
- FableCut pattern: browser editor where the whole timeline is one project.json that AI agents can edit.
- VideoFlow pattern: JSON-first video rendering model rather than React-first timeline.

Adoption target:
- Do not replace our content system.
- Extract timeline/edit-decision schema ideas.
- Compare with our planned `edit_decision.json`.
- Decide whether the approval artifact should be static HTML + JSON instead of a full editor.

### B. Script/topic to short-video factory patterns

Use for:
- topic/script pipeline
- B-roll source orchestration
- subtitle/voice/render order
- job queue ideas
- failure handling

Candidates found:
- MoneyPrinterTurbo: AI LLM one-click short-video generator; script, footage matching, voice/subtitles/background music/render.
- AI-Video-Editor style repos: transcript/structured JSON edit plan/B-roll/FFmpeg or MoviePy output.

Adoption target:
- Use as pipeline order reference only.
- Do not copy stock-media-first logic as the main OPC system.
- Our priority remains personal construction footage first, curated clips second, public fallback last.

### C. Transcript / talking-head cleanup tools

Use for:
- Mike talking-head cleanup
- silence/filler removal
- transcript-driven edit decisions

Candidates / benchmark tools:
- Descript
- Gling
- ClipsAI

Adoption target:
- Benchmark for talking-head only.
- Do not use as the core b-roll search layer.

### D. Semantic video search / thumbnails / embeddings

Use for:
- local media search
- clip candidate retrieval
- thumbnails/contact sheet
- OpenCLIP/SigLIP embeddings
- SQLite/vector DB approach

Candidates / patterns:
- local multimodal video search repos using CLIP/Chroma/frame extraction.
- edit-mind / local semantic video search style patterns.
- CLIP2Video and related retrieval research for query-to-video retrieval.
- dynamic thumbnail generation research as future inspiration, not MVP.

Adoption target:
- Start with keyframes + thumbnails + metadata + transcript.
- Add embeddings only after a small dataset works.
- Avoid heavy vector DB before the Mac M3 8GB path is proven.

### E. Product/app benchmarks

Use for:
- what the user experience should feel like
- what manual fallback to recommend when automation is not ready

Benchmarks:
- Apple Photos + Smart Album + local job-site index
- CapCut
- Adobe Premiere Media Intelligence
- Descript
- Gling
- Remotion/manual builder
- Viewmax, OpenArt Director, Sandcastles, Blotato and other Focus-captured tools later

Adoption target:
- Compare time-to-first-draft.
- Compare clip-finding quality.
- Compare manual effort.
- Compare storage/privacy risk.

---

## Repo evaluation table skeleton

| Candidate | Category | URL | License | Activity | Install risk | Privacy risk | What to copy | What not to copy | Decision |
|---|---|---|---|---|---|---|---|---|---|
| OpenChatCut | local-first editor | TBD | TBD | TBD | TBD | TBD | timeline/agent/MCP patterns | whole app until audit | REVIEW |
| Vanta | Remotion AI engine | TBD | TBD | TBD | TBD | TBD | JSON-to-Remotion pipeline | voice/avatar extras | REVIEW |
| FableCut | JSON timeline concept | TBD | MIT claimed in Reddit post; verify | TBD | TBD | TBD | single project.json editing model | unverified code until audit | REVIEW |
| MoneyPrinterTurbo | short-video factory | TBD | TBD | TBD | medium | stock/public-media workflow | pipeline order, task queue, render sequence | stock-media-first assumptions | REVIEW |
| ClipsAI | transcript clipping | TBD | TBD | TBD | low/medium | transcript/audio focus | transcript clipping methods | visual b-roll claims | REVIEW |
| react-video-editor | Remotion editor | TBD | TBD | TBD | medium | low if local | UI/timeline components | replacing internal renderer | REVIEW |
| Local semantic search repos | retrieval | TBD | TBD | TBD | medium/high | personal media risk | CLIP/frame extraction pattern | committing private caches | REVIEW |

---

## Shortest MVP hypothesis

If we avoid full Apple Photos and full semantic embeddings at first:

```text
Input: one approved OPC local/Drive folder with 10–20 videos.
Step 1: metadata scan with ffprobe.
Step 2: generate one thumbnail/contact sheet per video or scene.
Step 3: generate manual searchable HTML index.
Step 4: script-to-shot prompt creates a visual wish list.
Step 5: Priscila picks clips from contact sheet.
Step 6: save edit_decision.json.
Step 7: render one 9:16 draft via existing Remotion/FFmpeg route.
```

Estimated time if Package 0 audit finds reusable render pieces:

```text
Fast slice: 2–5 focused coding days.
Safer slice: 3–7 focused coding days.
Full reliable MVP: 2–4 weeks.
```

---

## What Package 0 must decide from this research

Package 0 must answer:

1. Does our existing Remotion/manual builder already support an edit JSON shape?
2. Can we create a minimal `edit_decision.json` without a full editor?
3. Can a static HTML contact sheet replace an approval UI for the first slice?
4. Can ffprobe + thumbnails solve enough before embeddings?
5. Which repo pattern is closest to our stack: Remotion JSON timeline, FFmpeg script, or browser project.json?
6. Which external tool can act as manual bridge when automation stalls?

---

## Decision rule

A repo can shorten the MVP only if it helps one of these immediate missing pieces:

- contact sheet
- edit JSON
- timeline JSON
- Remotion render mapping
- transcript cleanup
- scene/keyframe extraction
- local semantic search

Everything else is later research.
