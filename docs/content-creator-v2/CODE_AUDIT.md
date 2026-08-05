# Content Creator V2 — Code Audit (Package 0)

Date: 2026-08-05
Repo: `priihigashi/oak-park-ai-hub`
Branch: `claude/content-creation-system-audit-4xuawe`
Auditor: Claude Code (Package 0 real repository audit)
Scope: Full read-only audit of the existing content/media pipeline to decide, per component, whether V2 should REUSE / EXTEND / ADAPT / RECREATE / REPLACE LATER / NEW — before any runtime code is written.
Production impact: **Documentation only. No runtime code changed. No secrets, workflows, Drive routes, Sheets, media, or approval flows touched.**

---

## Executive summary

The project is **not starting from zero**, and — most importantly — **it is further along than the planning docs assume**. Three findings dominate this audit:

1. **The V2 data contracts already exist.** `scripts/content_creator_v2/contracts.py` already defines dataclasses for `MediaAsset`, `Scene`, `ShotRequest`, `ClipCandidate`, `ApprovedShot`, and `EditDecision`. Package 1 is therefore **not a green-field "create contracts" task** — it is a **reconcile-and-harden** task. Treating Package 1 as NEW would create a duplicate contract module (exactly the collision Package 0 exists to prevent).

2. **A different master-plan doc is already wired into code.** `contracts.py` points to master-plan Google Doc `1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU`, which is **not** the source-of-truth doc for this branch (`1l_hrf-ppXwIMRA5h61dZQ4z_pY_r8XYrLSq9_ZSBKM4`). Two master plans are live at once. This must be reconciled before Package 1, or field definitions will drift between the doc and the code.

3. **The render + transcription + provider-fallback layers are mature and reusable; the missing "brain" is the personal-media retrieval middle.** A full Whisper transcription cascade (`scripts/research/transcription.py`), an 8-tier motion/source cascade with provenance sidecars (`scripts/content_creator/motion_sources.py`), a paid/free route-fallback singleton (`scripts/research/route_state.py`), a manifest→Remotion props bridge (`scripts/research/manifest_renderer.py`), and a Remotion render-props builder (`scripts/remotion/build_render_props.py`) all already exist and work. What does **not** exist anywhere in the repo: **scene segmentation, keyframe extraction, visual/semantic embeddings + search, a script-line→shot planner, a clip contact-sheet approval artifact, and a local SQLite catalog.** That gap is precisely the "value layer" the plan identifies as ~25–35% built.

**Verdict: Package 1 can begin**, but re-scoped as "reconcile + version + complete the existing `content_creator_v2/contracts.py`," not "create new contracts." See [Package 1 readiness decision](#package-1-readiness-decision).

Decision counts (see full table): **REUSE ×3, EXTEND ×8, ADAPT ×11, RECREATE ×0, REPLACE LATER ×1, NEW ×11.** (Some requirements carry a dual decision, e.g. ADAPT-producer / NEW-contract.)

---

## Sources read

| Source | Read? | Notes |
| --- | --- | --- |
| NONNEGOTIABLES.md | Yes | LOCKED sections: content/carousel pipeline, image pipeline, Drive & storage, script editing, pipeline resilience (3-route min). Motion cascade V2 (NN-M1..M5) is current law; Ken Burns permanently removed; Remotion frozen at Phase 2. |
| AGENTS.md | Yes | Public stub; private rulebook migrated to `priihigashi/priscila-workspace`. OPC design rules mirror `docs/OPC_DESIGN_SYSTEM.md`. |
| CLAUDE.md | Yes | Public stub; same migration. |
| scripts/content_creator/main.py | Yes (scale + structure) | **2,966-line monolith** orchestrator. Uses ffmpeg, hashlib, yt-dlp refs. Single-file pipeline; high blast radius. |
| scripts/content_creator/motion_sources.py | Yes | `SOURCE_CHAIN` = 8 tier fns + static fallback; `TierFn = Callable[[dict, Path], bool]`; `_write_sidecar()` = provenance sidecar writer. Mature, observable adapter. |
| scripts/content_creator/approval_handler.py | Yes (API) | Gmail-reply parsing (SH-104), Buffer GraphQL posting, Drive render-copy. Mature but coupled to SH-104 + Buffer. |
| scripts/content_creator_v2/contracts.py | Yes (full) | **Existing V2 dataclasses** — see Executive Summary #1. |
| scripts/content_creator/contract_loader.py | Yes | `0.1.0-stub` editorial-contract loader for STORY-001 routing. Not the data-contract layer. |
| scripts/research/transcription.py | Yes | `transcribe_url()` cascade: YouTube/IG/TikTok → yt-dlp/Apify + Whisper. Returns `{transcript, source, duration, error}`. Mature. |
| scripts/research/candidate_collectors.py | Yes | keyword→candidate URLs (YT/IG/TikTok) + dedupe. Public-source retrieval only. |
| scripts/research/evidence_scoring.py | Yes | `score_candidate()` rubric scoring against a requirement; locked schema; `build_manifest()`/`write_manifest()`. |
| scripts/research/manifest_renderer.py | Yes | `evidence_manifest.json` → `carousel_content_spec.json` + `remotion_props.json` + `sources_block.txt`. Phase-3 scaffold. |
| scripts/research/route_state.py | Yes | `fallback_mode` singleton (auto/strict/no_paid) + per-route status. SH-104. |
| scripts/research/face_match.py | Yes | insightface scaffold; **no-op until dependency installed**. |
| scripts/capture/clips_manifest.py | Yes | JSON reader/writer for `resources/clips/clips.json` (`make_entry`/`upsert`). File-based, not SQLite. |
| scripts/capture/capture_pipeline.py | Yes (refs) | Uses ffprobe, ffmpeg, yt-dlp, SRT. Capture→Whisper→route entry path. |
| scripts/remotion/build_render_props.py | Yes | SRT + proof slides → Remotion render props JSON; voiceover gen + Drive audio upload. |
| scripts/remotion/src/parseSrt.ts | Yes (via refs) | SRT→captions for Remotion compositions. |
| docs/content-creator-rebuild-phase1-spec.md | Yes | Classifier + transcript-verification spec. `classifier.py` now exists in tree. |
| SOURCE_OF_TRUTH_AND_STORAGE.md | Yes | Storage policy, `.gitignore` patterns to verify, reuse-vs-rebuild guidance. |
| ATHENA_FOCUS_HANDOFF.md | Yes | Apple Photos/job-site index loose ends; Package 0-first rule. |
| PLANNING_CLOSURE_CHECKLIST.md | Yes | Non-negotiable order; readiness estimates. |
| PROJECT_EXECUTION_PLAYBOOK.md | Yes | Decision vocabulary + audit-before-build formula. |
| EXTERNAL_APPS_AND_REPOS_RESEARCH_PLAN.md | Yes | Candidate classification (MANUAL BRIDGE/BENCHMARK/REFERENCE/ADAPT/ADOPT/REJECT). |
| MVP_ACCELERATION_REPO_RESEARCH.md | Yes | Shortest-slice hypothesis + repo acceleration table. |
| Focus rows 1104–1117 | **No** | Focus Sheet not accessible from this non-interactive session. Reconstructed indirectly from SOURCE_OF_TRUTH §8, which enumerates the relevant rows. **Open item — must be confirmed against live Focus before Package 1.** |

---

## Existing system map

```
CAPTURE (scripts/capture/)
  capture_pipeline.py ─ ffprobe/ffmpeg/yt-dlp/SRT ─┐
  video_downloader.py ─ ffprobe                    │
  clips_manifest.py ─ resources/clips/clips.json   │  (file-based clip manifest)
                                                   ▼
TRANSCRIPTION (scripts/research/transcription.py)
  transcribe_url() → YouTube/IG/TikTok cascade → Whisper → {transcript,source,duration,error}
                                                   │
RETRIEVAL + SCORING (scripts/research/)  ← PUBLIC-source person-evidence flow, not personal library
  candidate_collectors.collect_candidates() → candidate URLs
  evidence_scoring.score_candidate() → rubric score → build_manifest()/write_manifest()
  route_state.RouteState → paid/free fallback modes
  face_match.* → insightface SCAFFOLD (no-op)
                                                   │
RENDER BRIDGE
  manifest_renderer.py → carousel_content_spec.json + remotion_props.json + sources_block.txt
  remotion/build_render_props.py → SRT+slides → render props JSON (+ voiceover, Drive audio upload)
  remotion/src/*.tsx (CarouselReel/NewsReel/EvidenceCompilation/CarouselMotion) + parseSrt.ts
  content_creator/export_slides.js (Playwright HTML→PNG — ONLY valid exporter per NONNEGOTIABLES)
                                                   │
CONTENT BUILD (scripts/content_creator/) — main.py 2,966-line monolith
  motion_sources.py SOURCE_CHAIN (8 tiers + static) + _write_sidecar (provenance)
  carousel_builder.py / manual_builder/* / opc_* templates / image_providers.py
                                                   │
APPROVAL + PUBLISH
  approval_handler.py → Gmail SH-104 reply parse → Drive render copy → Buffer GraphQL post
  email_preview.py / send_preview_emails.py → carousel PNG email previews

V2 CONTRACTS (scripts/content_creator_v2/contracts.py) — dataclasses already defined, unused, untested
```

**Key structural observations**
- The **person-evidence / SH-104 "research" flow** is the most V2-shaped code in the repo: it already does retrieve → transcribe → score → manifest → render-props. But it is aimed at **public footage of a named person**, not **Priscila's own construction library**. It is the best *pattern* source; it is not the personal-media retriever.
- `main.py` at 2,966 lines is the single biggest risk surface. Per NONNEGOTIABLES "NEVER REWRITE FROM SCRATCH" and "SCRIPTS ADD NEVER DELETE," it must be treated as **forbidden to edit** during the V2 build and wrapped behind adapters instead.
- `motion_sources.py` already emits **provenance sidecars** (`_write_sidecar`) — the seed of `ProvenanceRecord`.

---

## Requirement decision table

Decision vocabulary: REUSE · EXTEND · ADAPT · RECREATE · REPLACE LATER · NEW · FORBIDDEN UNTIL LATER.

| Requirement | Existing file/symbol | Decision | Reason | Allowed package | Risk | Tests required |
| --- | --- | --- | --- | --- | --- | --- |
| MediaAsset contract | `content_creator_v2/contracts.py::MediaAsset` | **EXTEND** | Dataclass exists; needs schema_version, orientation enum, checksum validation, tests | P1 | Med — drift vs master-plan doc | JSON round-trip; bad orientation; checksum format |
| Scene contract | `contracts.py::Scene` | **EXTEND** | Exists with embedding/quality fields; needs versioning + validation | P1 | Med | timestamp range invalid; JSON round-trip |
| TranscriptSegment contract | producer exists (`research/transcription.py`), **no typed contract** | **NEW (contract) / ADAPT (producer)** | Transcription returns an untyped dict; needs a typed segment schema | P1 / P4 | Low | empty/`[BLANK_AUDIO]` handling; word-level parse |
| Keyframe contract | `Scene.keyframe_paths: list[str]` only | **NEW** | No Keyframe type or extractor exists | P1 / P4 | Low | path/timecode round-trip |
| ShotRequest contract | `contracts.py::ShotRequest` | **EXTEND** | Exists; add orientation enum + validation + tests | P1 | Low | orientation enum; must_show/avoid |
| ClipCandidate contract | `contracts.py::ClipCandidate` | **EXTEND** | Exists (score/reason/provenance/trim); add versioning + validation | P1 | Low | score bounds 0–1; provenance isolation |
| ApprovedShot contract | `contracts.py::ApprovedShot` | **EXTEND** | Exists (crop/caption/transition) | P1 | Low | crop schema; transition enum |
| EditDecision contract (edit_decision.json) | `contracts.py::EditDecision` | **EXTEND** | **The edit-decision JSON shape is already designed** (approved_shots, audio, caption_settings, output_formats) | P1 | Low | JSON round-trip; empty shots; output-format enum |
| ProvenanceRecord contract | `motion_sources.py::_write_sidecar` + `ClipCandidate.provenance` dict | **NEW (formalize) / ADAPT (sidecar)** | Provenance exists as sidecars + a dict; no typed record | P1 | Med | missing-provenance rejected; license/source fields |
| ProcessingResult contract | NOT FOUND | **NEW** | No pipeline-result envelope exists | P1 | Low | ok/error variants |
| RenderResult contract | `build_render_props.py` output + upload path | **NEW (contract) / ADAPT (producer)** | Render emits props+path but no typed result | P1 / P9 | Low | success/failure fields |
| SQLite helper / catalog | NOT FOUND (`clips_manifest.py` is JSON-file) | **NEW / ADAPT** | No SQLite anywhere; `clips_manifest` is closest (JSON) | P2 | Med | schema create; upsert; reopen |
| Migrations | NOT FOUND | **NEW** | No migration system | P2 | Low | forward migration; version guard |
| Checksum / fingerprint | `hashlib` in `main.py`; `MediaAsset.checksum` field | **ADAPT / NEW** | Hashing used ad-hoc; needs shared sha256 helper | P2 | Low | deterministic hash; large file |
| ffprobe wrapper | inline in `motion_sources.py`, `video_downloader.py`, `capture_pipeline.py`, `opc_media_sorter.py` | **ADAPT** | ffprobe used 4× inline; extract one shared wrapper (do not edit call sites in place) | P3 | Med | metadata parse; missing-stream |
| Local media ingest | `opc_media_sorter.py`, `photo_matcher.py` | **ADAPT** | Sorting/matching exist; wrap for library ingest | P3 | Med | ingest one folder; dedupe by checksum |
| Apple Photos / job-site index | NOT in repo (AppleScript in separate chat per handoff) | **NEW / EXTERNAL** | Index lives outside repo; scanner has known `albums`→`containers` bug | P3 / Dataset | High (privacy, iCloud eviction) | container scan; GPS/date cluster |
| Scene segmentation | NOT FOUND | **NEW** | No PySceneDetect / scene splitter | P4 | Med | split a sample clip; boundary count |
| Keyframe extraction | NOT FOUND (ffmpeg present, no extractor) | **NEW** | No keyframe/thumbnail extractor | P4 | Med | extract N frames; portrait crop |
| Whisper / transcription adapter | `research/transcription.py::transcribe_url` | **ADAPT / REUSE** | Mature multi-route cascade already returns clean transcripts | P4 | Low | reuse existing route tests; empty-audio |
| Embeddings (visual/text) | `Scene.visual_embedding`/`text_embedding` fields; `face_match.py` scaffold | **NEW** | Fields declared; no OpenCLIP/SigLIP compute exists | P5 | High (Mac M3 8GB) | embed a keyframe; dim/size guard |
| Semantic search | NOT FOUND | **NEW** | No vector/index search | P5 | High | query→topK on tiny set |
| Ranking | `research/evidence_scoring.py::score_candidate` | **ADAPT** | Rubric-scoring pattern maps to ClipCandidate scoring | P5 | Med | score bounds; validate_score |
| Provider interface / fallback | `research/route_state.py` + `motion_sources.py::SOURCE_CHAIN` | **ADAPT / REUSE** | Fallback modes + tier chain already model providers | P6 | Med | fallback order; strict mode fails |
| motion_sources adapter | `motion_sources.py` (whole file) | **ADAPT — FORBIDDEN to edit until P6** | Locked by NONNEGOTIABLES NN-M1..M5; wrap behind interface, don't modify | P6 | High | sidecar written; static fallback |
| Script assistant | `story_outline.py`, `prompt_builder.py`, `topic_picker.py`, `classifier.py` | **ADAPT** | Story/prompt/topic building exists; reuse for beats | P7 | Med | outline from transcript |
| Shot planner (script line→shot) | NOT FOUND | **NEW** | No mapping from voiceover beats to ShotRequests | P7 | Med | script→ShotRequest list |
| Approval contact sheet | NOT FOUND (`email_preview.py` = carousel PNG preview) | **NEW** | No clip contact-sheet/approve-replace artifact | P8 | Med | render sheet from candidates |
| Existing Gmail approval flow | `approval_handler.py` (SH-104 + Buffer) | **ADAPT / REPLACE LATER — FORBIDDEN to edit until P8** | Works but coupled to SH-104 + Buffer; reuse parsing concepts only | P8+ | High | reply-parse fixtures only |
| Remotion adapter | `build_render_props.py` + `manifest_renderer.build_remotion_props` + `export_slides.js` | **EXTEND / ADAPT** | Props builder + manifest→props bridge already exist | P9 | Med | props schema; SRT captions |
| Export / provenance manifest | `evidence_scoring.write_manifest` + `manifest_renderer.py` | **ADAPT** | Manifest writer + renderer exist | P9–10 | Low | manifest audit gate |
| Security / storage gate | NOT FOUND; `.gitignore` missing V2 patterns | **NEW** | No `SECURITY_AND_STORAGE_GATES.md`; ignore rules incomplete (see Risks) | P10 | High | ignore-pattern check in CI |

---

## Reuse map (use directly)

- **`scripts/research/transcription.py`** — `transcribe_url()` and its route cascade. Already returns usable transcript text with source/duration/error. Reuse as the Package 4 transcription provider.
- **`scripts/research/route_state.py`** — `RouteState` / `fallback_mode`. Reuse as the Package 6 paid-vs-free fallback controller (already SH-104-proven).
- **`scripts/content_creator/export_slides.js`** — Playwright HTML→PNG. NONNEGOTIABLES makes this the *only* valid exporter; reuse unchanged.

## Extend map (works, bounded expansion)

- **`scripts/content_creator_v2/contracts.py`** — extend the 6 existing dataclasses; add the 5 missing (`TranscriptSegment`, `Keyframe`, `ProvenanceRecord`, `ProcessingResult`, `RenderResult`), a `schema_version`, enums, and errors. **This is the entire body of Package 1.**
- **`scripts/remotion/build_render_props.py`** — extend to consume a typed `EditDecision` instead of ad-hoc slide args.

## Adapt map (wrap behind a new interface; do not edit in place)

- **`scripts/content_creator/motion_sources.py`** — wrap `SOURCE_CHAIN` behind the Package 6 provider interface. **Do not modify** (NN-M1..M5 locked).
- **`scripts/research/evidence_scoring.py`** — adapt the rubric-scoring pattern into ClipCandidate ranking (Package 5).
- **`scripts/research/manifest_renderer.py`** — adapt `build_remotion_props()` as the EditDecision→Remotion bridge (Package 9).
- **`scripts/research/candidate_collectors.py`** — adapt as the *public-fallback* provider only (Tier: licensed/public), never the primary personal-library path.
- **`scripts/capture/clips_manifest.py`** — adapt the JSON manifest as a stopgap catalog until the Package 2 SQLite catalog exists.
- **ffprobe call sites** (`motion_sources.py`, `video_downloader.py`, `capture_pipeline.py`, `opc_media_sorter.py`) — extract a shared read-only wrapper (Package 3) without editing the existing callers.
- **`scripts/content_creator/approval_handler.py`** — adapt reply-parsing *concepts* for the Package 8 approval loop; do not reuse the Buffer/SH-104 coupling.

## Recreate map

- **None.** No component is broken enough to justify a clean rebuild *inside V2's scope*. (The plan's "current video pipeline is broken" refers to end-to-end reliability, which V2's new middle layer addresses by composition, not by deleting working parts.)

## Replace-later map

- **`scripts/content_creator/approval_handler.py`** (SH-104 Gmail + Buffer publish) — keep as-is for current operations; the V2 approval artifact (contact sheet + `edit_decision.json`) supersedes it later, after Package 8.

## New-build map (no usable implementation exists)

Scene segmentation · keyframe/thumbnail extraction · visual+text embeddings (OpenCLIP/SigLIP) · semantic/vector search · SQLite catalog + migrations · shot planner (beat→ShotRequest) · clip contact-sheet approval artifact · `SECURITY_AND_STORAGE_GATES.md` + `.gitignore` V2 patterns · typed `TranscriptSegment`/`Keyframe`/`ProvenanceRecord`/`ProcessingResult`/`RenderResult` contracts.

---

## Forbidden files until later packages

| File / path | Forbidden until | Why |
| --- | --- | --- |
| `scripts/content_creator/main.py` | P9+ (wrap only) | 2,966-line monolith; highest blast radius; NONNEGOTIABLES "never rewrite from scratch" |
| `scripts/content_creator/motion_sources.py` | P6 (adapt, don't edit) | Locked by NN-M1..M5; Ken Burns removal + tier chain must not regress |
| `scripts/content_creator/approval_handler.py` | P8 (adapt concepts only) | Live Gmail/Buffer publish path; editing risks real posts |
| `scripts/capture/capture_pipeline.py` | P3+ | Production capture→Whisper path |
| `scripts/content_creator/carousel_builder.py` / `manual_builder/*` | P9 | Live OPC render; brand-locked |
| GitHub workflows (`.github/workflows/*`) | Always (this project) | Package 0/1 are documentation + pure new modules; no CI changes |
| Production Sheets / Drive route IDs | Always | Secrets + routing; never guess (NONNEGOTIABLES) |
| Secrets / `.env` / cookies / OAuth tokens | Always | Security gate |
| Media folders / caches / generated reels | Always | Storage policy; never commit personal media |

---

## External evidence reconciliation

| Candidate | Classification | How it informs V2 | Pilot needed? |
| --- | --- | --- | --- |
| Apple Photos job-site index | MANUAL BRIDGE + future data source | Feeds `DATASET_MANIFEST.md`; later the personal-library provider. Scanner `albums`→`containers` bug + thumbnails + originals-fetch unproven. | Yes (Dataset) |
| CapCut | MANUAL BRIDGE / BENCHMARK | Ship-now route; time-to-first-draft baseline | No (manual) |
| Adobe Premiere Media Intelligence | BENCHMARK | Semantic media-search quality bar for Package 5 | Benchmark only |
| Descript | BENCHMARK (talking-head) | Filler/silence cleanup bar; not the b-roll layer | Benchmark only |
| Gling | BENCHMARK (talking-head) | Same as Descript | Benchmark only |
| FFmpeg | OWNED TOOL | Already used repo-wide; mechanical trim/keyframe/concat for P3/P4 | No |
| Remotion / manual builder | OWNED TOOL / BENCHMARK | Already the render engine; extend, don't replace | No |
| ClipsAI | REFERENCE / ADAPT | Transcript-clip pattern; our `transcription.py` already covers transcript side | Sandbox later |
| MoneyPrinterTurbo | REFERENCE | Pipeline-order + task-queue pattern; do **not** adopt stock-media-first assumption | Sandbox later |
| deepsearch (multimodal) | REFERENCE | Retrieval pattern for Package 5; audit activity/security first | Sandbox later |
| Remotion prompt-to-video template | REFERENCE / ADAPT | Timeline-JSON pattern — **already satisfied** by `EditDecision` + `manifest_renderer` | No (pattern only) |
| PySceneDetect / ffmpeg scene detect | ADAPT | Direct answer to the scene-segmentation NEW gap (Package 4) | Yes (small) |
| OpenCLIP / SigLIP | ADAPT | Direct answer to the embeddings NEW gap (Package 5); Mac M3 8GB constraint | Yes (small) |
| sqlite-vec / local SQLite | ADAPT | Package 2 catalog + optional vector store | Yes (small) |
| Apify / yt-dlp routes | REUSE / ADAPT | Already the capture+transcription backbone; do not create a second auth path | No |

---

## Public repo/app acceleration opportunities

The acceleration research asked whether public repos can shorten the 2–4 week MVP. This audit sharpens the answer against real code:

- **Already solved in-repo (do NOT import a repo for these):**
  - *Edit/timeline JSON* → `EditDecision` dataclass already designed.
  - *Remotion render mapping* → `build_render_props.py` + `manifest_renderer.build_remotion_props()`.
  - *Transcript cleanup* → `research/transcription.py` cascade.
  - *Provider fallback* → `route_state.py` + `motion_sources` SOURCE_CHAIN.
- **Genuine gaps where an external pattern *would* accelerate (adapt, don't adopt wholesale):**
  - *Scene/keyframe extraction* → PySceneDetect + ffmpeg (Package 4).
  - *Visual semantic search* → OpenCLIP/SigLIP + sqlite-vec (Package 5) — the single biggest time sink and the main MVP risk on Mac M3 8GB.
  - *Contact-sheet approval* → build in-house from keyframes (small); no repo needed.

**Net:** the fastest slice reuses far more of the existing repo than the acceleration doc assumed. External repos are most valuable as **reference patterns for scene detection and embeddings only.**

---

## Shortest MVP slice

Confirmed feasible because the render + transcription ends already exist:

```
1. One approved OPC folder, 10–20 videos (from DATASET_MANIFEST.md).
2. ffprobe metadata via a shared wrapper (ADAPT existing call sites).      [P3]
3. Keyframe/thumbnail per scene via ffmpeg (NEW, small).                    [P4]
4. Static HTML contact sheet from keyframes (NEW, small).                   [P8-lite]
5. Script beats → ShotRequests (NEW planner, small).                        [P7-lite]
6. Priscila picks clips → write edit_decision.json (EditDecision EXISTS).   [P1 shape]
7. Render one 9:16 draft via build_render_props.py + Remotion (EXTEND).     [P9]
```

Skip for the first slice: Apple Photos automation, embeddings/semantic search, SQLite. Add those only after the metadata+contact-sheet+manual-pick loop works end to end. **Estimate holds at ~2–5 focused coding days for the fast slice** given the reusable render pieces confirmed here.

---

## Required tests before Package 1 coding

1. **Contracts round-trip** — every dataclass in `content_creator_v2/contracts.py` serializes to JSON and back with no loss.
2. **Invalid timestamp ranges** — `Scene.end_time <= start_time` rejected.
3. **Schema version guard** — unsupported major version rejected (requires adding `schema_version`).
4. **Invalid orientation** — anything outside `portrait|landscape|square` rejected.
5. **Missing provenance** — a `ClipCandidate`/`ApprovedShot` without provenance is rejected.
6. **Provider-specific metadata isolation** — public-source fields do not leak into personal-library records.

(There are currently **zero tests** under `scripts/content_creator_v2/`. This test file is the first Package 1 artifact.)

---

## Risks and stop conditions

**Risks**
1. **Duplicate-contract collision** — if Package 1 creates contracts at `scripts/content_creator/clip_finder/contracts.py` as the prompt suggests, it duplicates `scripts/content_creator_v2/contracts.py`. *Mitigation:* consolidate on the existing `content_creator_v2/` module.
2. **Two master-plan docs** — `contracts.py` cites doc `1DjLeV5Ba5jXM4eY…`; this branch's source of truth is `1l_hrf-…`. *Mitigation:* reconcile before editing contracts; pick one canonical doc.
3. **`.gitignore` gap** — current `.gitignore` has none of the SOURCE_OF_TRUTH V2 patterns (`*.clip_finder.sqlite`, `*.embeddings.*`, `**/keyframes/`, `**/thumbnails/`, `**/generated_reels/`, `content_creator_cache/`, etc.). A careless later package could commit personal media/caches. *Mitigation:* add these ignore rules as the first Package 2 action (or a safe docs-adjacent commit now).
4. **Mac M3 8GB embeddings** — Package 5 (OpenCLIP/SigLIP + vector search) is the highest technical risk; may not fit memory. *Mitigation:* keyframes+metadata+transcript search first; embeddings gated behind a proven small dataset.
5. **`main.py` blast radius** — 2,966 lines; any in-place edit risks the live pipeline. *Mitigation:* wrap-only, forbidden to edit until P9+.
6. **Focus rows 1104–1117 unverified** — not readable from this session. *Mitigation:* confirm against live Focus before Package 1 so no closed route is reopened.

**Stop conditions for the next agent**
- Stop if Package 1 would create a second contracts module instead of extending `content_creator_v2/contracts.py`.
- Stop if the two master-plan docs are not reconciled.
- Stop before touching any FORBIDDEN file above.
- Stop if any change would write real media, secrets, or production Sheets/Drive.

---

## Package 1 readiness decision

**Can Package 1 start? YES — re-scoped.**

Package 1 is **not** "create contracts and enums from scratch." It is:

- **Required safe files:**
  - `scripts/content_creator_v2/contracts.py` — **EXTEND** (add `schema_version`; add `TranscriptSegment`, `Keyframe`, `ProvenanceRecord`, `ProcessingResult`, `RenderResult`).
  - `scripts/content_creator_v2/enums.py` — **NEW** (source, owner, orientation, transition, output_format).
  - `scripts/content_creator_v2/errors.py` — **NEW** (validation errors).
  - `scripts/content_creator_v2/__init__.py` — **NEW**.
  - `scripts/content_creator_v2/tests/test_contracts.py` — **NEW** (the 6 tests above).
- **Required tests:** the 6 listed in [Required tests](#required-tests-before-package-1-coding).
- **Blockers to clear first:** (1) reconcile the two master-plan docs; (2) confirm the `content_creator_v2/` location vs the prompt's `clip_finder/` suggestion with Priscila; (3) verify Focus rows 1104–1117.
- **Constraints:** no network, no Drive, no real media, no production Sheets; do not touch `main.py`, `motion_sources.py`, `approval_handler.py`, `capture_pipeline.py`, workflows, or secrets. Pydantic only if already available or explicitly approved — **current contracts use stdlib `dataclasses`; recommend staying on dataclasses to avoid a new dependency.**

---

## No-op / rollback statement

Package 0 changed **only documentation** under `docs/content-creator-v2/` (this file, `STATUS.md`, and a copy of the source-of-truth doc set onto the audit branch). **No runtime code, secrets, workflows, Drive routes, Sheets, media, or approval flows were modified.** No runtime rollback is required; reverting the docs commit fully undoes this package.
