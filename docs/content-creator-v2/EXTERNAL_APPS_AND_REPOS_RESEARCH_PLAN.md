# External Apps and Public Repos Research Plan

Created: 2026-08-05
Scope: close the remaining planning gap by defining how real-world apps, official documentation and public repositories will be evaluated for Content Creator V2.

## Purpose

Priscila wants the system to use what already works in the real world instead of rebuilding everything from scratch. This plan defines which apps/repos are manual bridges, benchmarks, reference sources, or adoption candidates.

Package 0 still comes before runtime coding. External research informs the audit and implementation packages; it does not replace the audit.

## Evidence standard

For every app/repo/tool, capture:

- official website/docs;
- GitHub repo or source code if available;
- license;
- maintenance/activity;
- pricing/current plan limits;
- API/MCP/SDK/CLI availability;
- exportability;
- privacy and training/data-retention policy;
- commercial rights;
- Mac M3 8GB compatibility;
- install/runtime requirements;
- smallest pilot;
- rollback;
- exact role in the project.

## Classification

- MANUAL BRIDGE: use manually when Priscila needs to ship now.
- BENCHMARK: test against the internal V2 so we know if building saves time.
- REFERENCE: study patterns only.
- ADAPT: wrap or recreate a specific pattern cleanly.
- ADOPT: use directly only after license, security, cost and pilot pass.
- REJECT: not aligned, duplicates better option, or creates unacceptable risk.

## Current candidates

| Candidate | Initial role | Why it matters | Caution |
| --- | --- | --- | --- |
| Apple Photos job-site index | MANUAL BRIDGE + future data source | Already helps locate job footage by GPS/date | Needs containers bug fix, thumbnails, originals-fetch proof, Mike-source plan |
| CapCut | MANUAL BRIDGE / benchmark | Fast mobile assembly for urgent posts | Not the durable source of truth; manual cleanup expected |
| Adobe Premiere Media Intelligence | BENCHMARK | Semantic visual media search across imported footage; useful standard for our clip finder | Paid/subscription; English visual search; not automatically connected to our pipeline |
| Descript | BENCHMARK for talking-head | Text-based video editing and filler-word removal | Can be choppy; test with real Mike/Priscila footage before relying |
| Gling | BENCHMARK for talking-head | Removes bad takes/silence/filler words and helps captions/titles | Mainly creator/talking-head fit, not construction b-roll library search |
| FFmpeg | OWNED TOOL | Mechanical trim/resize/concat/captions/export | Not an editorial brain |
| Remotion/manual builder | OWNED TOOL / benchmark | Existing programmable renderer and manual route | Must not be broken by V2 |
| ClipsAI/clipsai | REFERENCE / ADAPT | Transcript-based clip finding for narrative videos | Audio-centric; not enough for visual construction b-roll |
| MoneyPrinterTurbo | REFERENCE / possible recovery pilot | End-to-end short video generation pipeline patterns | Do not adopt wholesale; sandbox only; license/cost/API review first |
| deepsearch-ai/deepsearch | REFERENCE | Multimodal semantic retrieval across video/audio/images | Need activity/security/runtime audit before adapting |
| Remotion prompt-to-video template | REFERENCE / ADAPT | Timeline JSON pattern for prompt-to-video rendering | Use pattern; do not force if existing renderer differs |
| PySceneDetect / FFmpeg scene detect | ADAPT | Scene splitting layer for searchable video units | Must be benchmarked on real OPC footage |
| OpenCLIP / SigLIP / embeddings | ADAPT | Visual/text search backbone | Mac M3 8GB constraints; cache and disk use required |
| sqlite-vec / local SQLite index | ADAPT | Lightweight local vector/index store | Confirm dependency, install and fallback |
| Apify / yt-dlp capture routes | REUSE/ADAPT after audit | Existing capture system already uses them | Do not create a second auth/capture path |
| Blotato / Sandcastles / Viewmax / OpenArt Director / Google Flow | RESEARCH LATER | Potential routes captured in Focus | Must be evaluated against the actual construction assistant requirement |

## Manual recommendations when Priscila is stuck

These are allowed practical paths while the full V2 is not built:

1. Need an OPC reel today from known clips: Apple Photos job-site index → open clips in Photos → CapCut → export 9:16.
2. Need to test semantic search quickly: import a controlled folder into Premiere and use Media Intelligence search as a benchmark.
3. Need talking-head cleanup: test the same Mike/Priscila clip in Descript and Gling; compare cuts, captions, cleanup and manual correction time.
4. Need mechanical local processing: use FFmpeg through the saved Portuguese prompt; original untouched; output to final folder.
5. Need owned repeatable rendering: use existing Remotion/manual builder and compare against the manual app result.

## Benchmark protocol to create next

Create BENCHMARK_PROTOCOL.md with one identical test asset set and script:

- Apple Photos + CapCut route;
- Premiere Media Intelligence route;
- Descript or Gling talking-head route;
- current manual builder / Remotion route;
- future internal V2 route.

Measure:

- time to find clips;
- search accuracy;
- number of manual corrections;
- visual quality;
- caption quality;
- export quality;
- privacy/data exposure;
- cost;
- repeatability;
- how much Priscila still has to think.

## Repo adoption rules

Never copy a repo directly into the system because it exists.

For every public repo:

1. Read README and license.
2. Check current activity/issues.
3. Identify exact reusable pattern.
4. Run with synthetic/approved assets only.
5. Write a KEEP/PILOT/REFERENCE/REJECT note.
6. Prefer clean-room adaptation for workflows, prompts and architecture.
7. Do not add secrets, billing or publishing rights during research.

## How this links to Package 0

Package 0 CODE_AUDIT.md must include a section called External Evidence Reconciliation:

- which candidates are immediate manual bridges;
- which candidates are benchmarks;
- which public repos are reference patterns;
- which are forbidden until later;
- which missing modules need additional repo research.

Package 1 can start only after Package 0 confirms no existing equivalent contracts or schemas already exist.
