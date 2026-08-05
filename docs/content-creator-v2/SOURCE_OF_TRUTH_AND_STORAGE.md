# Content Creator V2 — Source of Truth, Storage, and Recovery Plan

Created: 2026-08-05
Repository: `priihigashi/oak-park-ai-hub`
Branch created for this documentation copy: `content-creator-v2/docs-source-of-truth-2026-08-05`
Primary Google Doc: `CONTENT CREATOR V2 — IMPLEMENTATION PACKAGES FOR CODEX & CLAUDE — 2026-08-05`
Google Doc URL: https://docs.google.com/document/d/1l_hrf-ppXwIMRA5h61dZQ4z_pY_r8XYrLSq9_ZSBKM4/edit
Focus Sheet: `_Focus Partner — STATE`, tab `Pending`

## 1. Why this file exists

Priscila raised the correct risk: if the Mac is reset, local agents are deleted, Claude/Codex sessions disappear, or the computer loses a local workspace, the system must not lose the brain behind the flow.

This project cannot depend on chat history, local `/mnt/data`, desktop files, transient agent memory, or one untracked Markdown file. The architecture, storage paths, naming rules, recovery strategy, and implementation packages must exist in at least two durable places:

1. Google Drive / Google Docs — human-readable project planning and decisions.
2. GitHub Markdown — implementation-facing, versioned, reviewable, diffable documentation.

The Focus Sheet should point to these durable documents. It should not be the full source of truth for the architecture.

## 2. Canonical source-of-truth structure

### Human-readable master location

Google Drive folder:

`Marketing Shared Drive / Claude Code Workspace / _Master Plans & Docs`

Primary document:

`CONTENT CREATOR V2 — IMPLEMENTATION PACKAGES FOR CODEX & CLAUDE — 2026-08-05`

Purpose:

- explain the project in natural language;
- preserve decisions from chat;
- store implementation packages;
- store Package 0 pre-audit;
- store current estimates and missing work;
- store links to deep research and related docs;
- stay readable for Priscila.

### GitHub implementation-facing location

Repository:

`priihigashi/oak-park-ai-hub`

Canonical docs directory:

`docs/content-creator-v2/`

Initial file:

`docs/content-creator-v2/SOURCE_OF_TRUTH_AND_STORAGE.md`

Future files should use stable names and should not be renamed casually:

- `SOURCE_OF_TRUTH_AND_STORAGE.md`
- `IMPLEMENTATION_PACKAGES.md`
- `CODE_AUDIT.md`
- `STATUS.md`
- `PACKAGE_00_REPOSITORY_AUDIT.md`
- `PACKAGE_01_CONTRACTS.md`
- `PACKAGE_02_CATALOG_SQLITE.md`
- `DATASET_MANIFEST.md`
- `BENCHMARK_PROTOCOL.md`
- `EXTERNAL_REPO_EVALUATION.md`
- `SECURITY_AND_STORAGE_GATES.md`

Rule: once these names are introduced, prefer appending versioned sections over renaming paths. If a rename becomes unavoidable, add a redirect note in the old file path first.

### Focus Sheet role

Focus Sheet should contain:

- one active task pointing to the Google Doc and GitHub path;
- individual done rows for completed blocks;
- next action only;
- links to supporting docs.

Focus Sheet should not be the only place where logic, architecture, or prompts live.

## 3. Storage and size policy

This project must not blow up GitHub, the Mac, or Drive storage.

### GitHub may store

- Markdown documentation;
- source code;
- small JSON schemas;
- small test fixtures;
- small synthetic media used only for tests;
- migration files;
- prompt templates;
- scripts.

### GitHub must not store

- real client/job videos;
- Apple Photos exports;
- full generated reels;
- large thumbnails/contact sheets;
- large embeddings/vector indexes;
- local SQLite databases built from the personal library;
- secrets;
- cookies;
- raw OAuth tokens;
- Drive or Apple private media dumps;
- generated cache directories.

### Recommended limits

- Markdown planning files: keep each under ~200 KB when possible.
- Test fixtures: keep total fixture media under ~10 MB unless a specific test requires more and the reason is documented.
- Real media: store in Drive, Apple Photos, shared libraries, or approved asset folders, not GitHub.
- Local caches: rebuildable and ignored by Git.
- SQLite catalog: local runtime artifact; do not commit personal catalog data.
- Embeddings: local rebuildable artifacts; do not commit real personal-library embeddings.

### Required `.gitignore` patterns for this project

Package 0 should verify or add ignore rules for:

```gitignore
# Content Creator V2 generated media and caches
/content_creator_cache/
/.content_creator_cache/
/.clip_finder/
*.clip_finder.sqlite
*.clip_finder.sqlite-shm
*.clip_finder.sqlite-wal
*.embeddings.jsonl
*.embeddings.npy
*.contact-sheet.html
*.contact-sheet.json
*.edit-session.json

# Generated media outputs
**/generated_reels/
**/rendered_videos/
**/working_media/
**/transcoded/
**/keyframes/
**/thumbnails/
```

Package 0 must inspect the existing `.gitignore` before adding anything.

## 4. Recovery rule

A fresh machine should be able to recover the project brain from:

1. GitHub repo documentation under `docs/content-creator-v2/`.
2. Google Drive master plan under `_Master Plans & Docs`.
3. Focus Sheet row pointing to the current active doc and next action.

No required project decision should exist only in a chat reply.

## 5. How much of the existing flow should be reused

Priscila correctly warned that the old flow has not reliably worked. Therefore the project must not blindly preserve the old system as-is.

Use the existing flow as audited components, not as unquestioned architecture.

### Reuse or adapt if verified

- Remotion renderer and design-system integration.
- FFmpeg utilities and installed local binary knowledge.
- Whisper/transcription routes.
- SRT/caption parsing.
- Capture pipeline concepts: Apify metadata, yt-dlp download, routing, transcripts.
- Drive routing and folder IDs, after audit.
- `motion_sources.py` public/curated fallback chain, wrapped behind an adapter.
- Gmail approval handler concepts, but not necessarily the final UI.
- Manual builder rules and OPC design system.

### Do not blindly keep

- Any unclear 4AM orchestration behavior.
- Any pipeline path that hides failures.
- Any route that relies on undocumented spreadsheet/Drive assumptions.
- Any agent behavior that does not read the canonical knowledge pack.
- Any workflow that requires Priscila to remember scattered instructions.
- Any flow that says it worked without a small reproducible end-to-end test.

### New layer required

The missing brain is:

1. stable job object;
2. personal media index;
3. scene-level catalog;
4. semantic search;
5. script assistant;
6. shot planner;
7. candidate ranking;
8. approval/contact sheet;
9. edit decision JSON;
10. Remotion/FFmpeg first-cut rendering;
11. provenance and cost logs.

## 6. Current completeness estimate

Planning/documentation readiness: ~70–75% done.
Reusable infrastructure: ~40–50% done.
New clip-finder MVP: ~25–35% done.
Full dream product vision: ~10–20% done.

Interpretation: the project is not close to finished as software, but it is not starting from zero. The old infrastructure may provide useful pipes, but the actual value layer — personal media retrieval plus script-to-shot planning plus approval — is still mostly missing.

## 7. External repository adoption policy

Priscila’s instinct is correct: if a public repo already solved a component, inspect it and borrow patterns rather than reinventing everything.

But do not wholesale install a repo into production.

Policy:

1. Identify the exact repo, license, recent maintenance status, dependencies, and runtime model/API requirements.
2. Run it only in an isolated sandbox with synthetic or approved assets.
3. Extract patterns, contracts, functions, and test ideas.
4. Prefer clean-room reimplementation when license, quality, privacy, or dependency risk is unclear.
5. Never connect private assets, production OAuth, paid API keys, or publishing permissions during first evaluation.
6. Compare output against the current internal pipeline and manual tools.
7. Record KEEP / ADAPT / RECREATE / REJECT.

High-value references already identified:

- `ClipsAI/clipsai` — transcript-based clip finding.
- `AgriciDaniel/claude-shorts` — Claude-scored candidates, boundary snapping, Remotion captions.
- `SamurAIGPT/AI-Youtube-Shorts-Generator` — highlight detection and vertical cropping.
- `deepsearch-ai/deepsearch` — multimodal semantic retrieval.
- `remotion-dev/template-prompt-to-video` — timeline JSON pattern.
- `ElMALIHI/SVM_AI` — script to stock footage to Whisper captions to Remotion.
- `harry0703/MoneyPrinterTurbo` — recovery/replacement pilot candidate because the current video pipeline is broken.
- `SamurAIGPT/Generative-Media-Skills` / Priscila fork — agent-native media route, likely paid via MuAPI.

## 8. Pending resources recovered during 2026-08-05 sweep

Relevant Focus Pending rows found by searching `video`, `clip`, and `security`:

- Row 35 — audit 10 open-source AI repos; includes MoneyPrinterTurbo, MarkItDown, codegraph, Understand-Anything, harness, cybersecurity skills; explicitly says current media pipeline is broken and needs recovery plan.
- Row 37 — cost-first route registry and Runway audit.
- Row 69 — controlled video editor pilot based on `bernardreacher/editor-de-video-claude`; clean-room only due license uncertainty.
- Row 81 — competitor-content database using Metricool + Apify + Whisper.
- Row 82 — canonical content-resources system; do not depend on chat history.
- Row 87 — mandatory 2FA-bypass/authentication security gate for every app.
- Row 103 — ffmpeg as Portuguese-driven mechanical video processor; steps 1–2 done, steps 3–7 open.
- Row 104 — MarkItDown + NotebookLM research/content ingestion system.
- Row 105 — JARVIS ↔ Content Creator Agent spoken route; includes Generative-Media-Skills and AI Clipping.
- Row 204 — teach agents about ffmpeg; current agents/skills did not mention it.
- Row 207 — Google AI tool round: AI Studio, Stitch, Antigravity, Pomelli, Opal, Flow, Mixboard, NotebookLM.
- Row 212 — OpenArt Director as modular route; no public API verified yet; MCP scope must be checked.
- Row 352 — Apple Photos search proven via AppleScript over 43,947 media items; GPS/date clustering works; actual file fetching still untested.
- Row 353 — Mike’s job clips are a people/process decision; options are Shared Album or Shared Photo Library.
- Row 354 — Google Photos route closed; do not reopen.
- Row 355 — Viewmax MCP saved for later evaluation as still-photo-to-video route.
- Row 358 — three Justyn.ai tools saved: IG saves→Notion pipeline, Sandcastles, Blotato; not evaluated.
- Row 359 — Priscila’s clearest statement of the actual goal: an AI assistant personalized for construction that helps edit videos with less work and gives ideas.
- Row 372 — urgent three-tool pilot: Apple Photos + CapCut, Adobe Premiere Media Intelligence, Gling/Descript.
- Rows 1104–1109 — AI clip-finder deep research, repo audit, architecture, documentation consolidation.
- Rows 1110–1111 — implementation packages and Package 0 pre-audit saved.

These rows must be reconciled before Package 1 coding so the project does not drop existing resources or re-research closed routes.

## 9. Immediate required next documents

Before runtime implementation, create or complete these under both Google Doc and GitHub:

1. `CODE_AUDIT.md` — exact existing-code decision table.
2. `EXTERNAL_REPO_EVALUATION.md` — public repos and tool candidates with KEEP / ADAPT / RECREATE / REJECT.
3. `DATASET_MANIFEST.md` — 20–40 approved OPC clips/photos for tests; no raw media in GitHub.
4. `BENCHMARK_PROTOCOL.md` — internal pipeline vs CapCut/InVideo/Premiere/Gling/Descript/OpenArt/etc.
5. `SECURITY_AND_STORAGE_GATES.md` — 2FA-bypass review, secrets, OAuth, media privacy, local cache cleanup, no-publication gates.

## 10. Next action

Execute Package 0 as a real audit, not code implementation:

- read repo files;
- map every existing entrypoint and media workflow;
- create `docs/content-creator-v2/CODE_AUDIT.md`;
- create `docs/content-creator-v2/STATUS.md`;
- decide for each component: REUSE, EXTEND, ADAPT, RECREATE, REPLACE LATER, or NEW;
- do not modify production runtime code;
- do not push to main;
- do not open PR until Priscila reviews the docs branch.
