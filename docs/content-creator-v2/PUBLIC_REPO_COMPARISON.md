# Content Creator V2 — Public Repo / Commercial Tool Comparison

Created: 2026-08-05
Status: architecture-freeze input. Research only; no code copied, vendored, installed, or run.

## Executive conclusion

The strongest pattern is not `prompt → final video`. The strongest pattern is:

```text
editable project
→ structured command/action log
→ human-readable timeline state
→ reversible AI edits
→ human approval
→ render/export
```

Content Creator V2 should therefore keep a **Timeline JSON / Edit Decision JSON** as the contract between modules. Remotion can remain the first renderer because the current repo already has Remotion/FFmpeg work, but the system should not become React-composition-first. It should be **timeline-data-first**.

Frozen architecture direction:

```text
Idea
→ Script
→ Shot Plan
→ Semantic Clip Search
→ Timeline JSON
→ Human Approval
→ Renderer
→ Export / Provenance Log
```

## Comparison matrix

| Candidate / pattern | What it proves | What to adopt | What not to adopt | Decision |
|---|---|---|---|---|
| OpenChatCut | Local-first, agent-native video editor. AI works on an editable timeline through structured tools/MCP rather than returning a flattened video. | Agent action model, editable timeline, project state, explicit tool interface, rollback/review mindset. | Do not replace our content system with its full editor. Do not make V2 depend on a heavy UI before MVP. | ADAPT pattern |
| OpenReelio | Desktop NLE + AI assistant + inspectable command log + FFmpeg/GPU export + SQLite project storage. | Inspectable command log, local project storage, reversible edits, plugin/provider boundaries. | Do not build a full desktop NLE now. Do not add Tauri/Rust burden to MVP. | ADAPT pattern later |
| Remotion / Remotion Timeline | Existing mature programmatic renderer and possible timeline UI components. | Keep Remotion as first renderer / preview target. Use a JSON adapter into Remotion. | Do not lock core data model to React components. | REUSE/EXTEND |
| PySceneDetect | Mature scene detection CLI/Python API; can save scene lists and representative images. | Use for scene boundaries and keyframes/contact sheets in MVP. | Do not over-tune scene detection before testing with 10–20 clips. | ADAPT / likely dependency |
| CLIP / CLIP4Clip / video-text retrieval patterns | Text-video retrieval can be based on CLIP-style embeddings; image-frame features are a practical MVP baseline. | Start with per-scene keyframe embeddings using OpenCLIP/SigLIP-style model; add transcript/keyword hybrid ranking. | Do not train a video retrieval model. Do not require GPU-heavy video-CLIP. | BUILD LIGHT MVP |
| B-Script / transcript-based B-roll research | B-roll timing/content is easier with transcript + recommendations; transcript interface can beat raw timeline work. | Script/shot planner should decide B-roll positions before searching clips. | Do not build a full transcript editor first. | ADAPT concept |
| B-Roll Me / ScenePull / Magicroll-style products | The commercial workflow is script → identify moments → query assets → score/select → package/place B-roll. | Use script-to-shot and B-roll density concepts; generate shot requests per sentence/scene. | Do not make public stock footage the primary source; OPC footage stays first. | ADAPT workflow |
| MoneyPrinterTurbo / short-video factories | Pipeline order: script, assets, voice/subtitles/music/render. Good orchestration reference. | Failure handling, staged jobs, generated artifact tracking. | Do not copy stock-first strategy or generic faceless-video bias. | REFERENCE only |

## Architecture decisions from research

1. **Timeline JSON is mandatory.**
   - It is the interface between clip search, approval, rendering and future editors.
   - It makes changes inspectable and reversible.

2. **Human approval stays before render/export.**
   - Agent-native editors prove that editable state plus review beats opaque generation.

3. **V2 must be provider-based.**
   - Personal media provider first.
   - Curated clips second.
   - Public fallback third.
   - Existing `motion_sources.py` becomes a fallback adapter later, not the center of V2.

4. **MVP uses lightweight local retrieval.**
   - PySceneDetect or FFmpeg for scene splits.
   - Keyframes/contact sheet for review.
   - OpenCLIP/SigLIP-style embeddings for scene search.
   - SQLite + FTS/vector extension where practical.

5. **Do not build a full editor first.**
   - MVP should create static/contact-sheet approval plus Timeline JSON.
   - A full timeline UI is a later product layer.

## Recommended MVP slice after this research

```text
One approved OPC media folder
→ ingest 10–20 videos
→ ffprobe metadata
→ scene/keyframe extraction
→ transcript if audio exists
→ local catalog
→ shot plan from one script
→ semantic + keyword search
→ contact sheet approval
→ Timeline JSON
→ Remotion/FFmpeg draft render
→ provenance log
```

## Immediate changes to implementation packages

- Package 0 must include existing code audit plus external-pattern reconciliation.
- Package 1 contracts must define `TimelineDecision` / `EditDecision` as first-class output.
- Package 2 storage must store project, asset, scene, transcript, embedding metadata, and timeline decisions.
- Package 4 scene/keyframe work should prefer PySceneDetect or FFmpeg CLI first.
- Package 5 search should be hybrid: semantic visual + transcript/keyword + source/quality/ranking.
- Package 8 approval artifact must review candidate scenes and proposed timeline, not just a clip list.
- Package 9 Remotion adapter should consume Timeline JSON; no hard-coding search logic into Remotion.

## Explicit non-goals

- No full desktop editor in MVP.
- No replacing current production content creator pipeline.
- No writing into backup/archive folders.
- No committing media, embeddings, caches, tokens, OAuth, or private footage.
- No public stock-first architecture.

## Sources reviewed / concepts captured

- OpenChatCut: local-first conversational AI video editor, agent-native timeline, MCP/Codex/Claude workflow.
- OpenReelio: desktop open-source AI editor, inspectable command log, FFmpeg/GPU export, SQLite project storage.
- Remotion: programmatic React-based video rendering; existing project can remain render target.
- Remotion Timeline: purchasable/copyable timeline UI pattern for Remotion-based editor.
- PySceneDetect: scene detection CLI/Python API, scene lists, keyframe images, FFmpeg splitting.
- CLIP4Clip / video-text retrieval research: validates CLIP-style retrieval as the conceptual basis.
- B-Script: transcript-based B-roll editing and recommendations.
- Commercial B-roll workflows: B-Roll Me, ScenePull, Magicroll.
