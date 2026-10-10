# OPC Blog v2 draft runner

This runner produces a review bundle only. It has no publishing or WordPress operation. The legacy `blog-generator.js` remains separate and must stay disabled for v2.

Operating cadence, company scope, media fallback, and cost decision: [BLOG_V2_OPERATING_POLICY.md](BLOG_V2_OPERATING_POLICY.md). The present public frequency is zero while the independent series review remains HOLD. The target after a clean acceptance batch and release interlock is one approved article per week, with skipped weeks when quality is insufficient.

## Input snapshot

Save a JSON file with `snapshotAt`, `candidates`, `existing`, and `sources`:

```json
{
  "snapshotAt": "2026-10-10T16:00:00-04:00",
  "candidates": [{"id":"sheet-row-12","question":"What should I check before a home addition in Broward County?","readerDecision":"Understand permit sequence before pricing an addition","service":"home addition","area":"Broward County","sourceIds":["county-addition-page"],"priority":0,"provenance":{"sheetRow":12,"sheetStatus":"Raw Idea"}}],
  "existing": [{"id":"live-1","title":"Existing article title","intent":"What reader decision this answers","slug":"existing-article"}],
  "sources": [{"id":"county-addition-page","url":"https://example.gov/official-guidance","publisher":"County building division","title":"Official guidance","excerpt":"Specific text copied from the official page that answers this question.","capturedAt":"2026-10-10T15:00:00-04:00"}]
}
```

`existing` must contain queued topics and any manually researched duplicate intents. A new Codex draft run also requires the checked-out React site's `frontend` directory: the runner reads its current `posts.json` and `legacyBlogPaths.json`, refreshes matching entries, and adds every live and legacy route to `existing`. It records both file hashes and counts in the immutable snapshot. Missing or malformed site inventory stops drafting; a revision reuses the original immutable inventory. The Content Ideas sheet can supply questions and provenance, but it does not establish construction facts. Every candidate needs at least one topic-relevant official source. The runner fetches public sources at run time, checks status and excerpt overlap, and records a retrieval digest. Internal company facts may use `access: "internal-preverified"` with `evidenceId`, `verifiedBy`, `capturedAt`, and `excerpt`; this cannot support external technical or legal assertions.

Official PDF sources are now read with local Python `pypdf`; the file is limited to 10 MiB and the first 30 pages. The extracted text receives the same excerpt-overlap check and content digest as HTML, with `retrieval: "http-pdf"` in the receipt. If `pypdf` is unavailable or text cannot be extracted, the source fails closed before drafting. Check the actual PDF date and jurisdiction; a successful text match does not make an old checklist current law.

For autonomous intake directly from the Content Ideas export, use `{snapshotAt, ideaRows, sourceCatalog, existing}`. Each `ideaRows` entry may be a 23-column sheet row array or an object with `rowNumber`, `rawIdea`, `topicDirection`, `sourceLink`, `status`, and `blogUrl`. The intake adapter classifies supported themes into safe question templates. It never passes raw hooks or payoffs into the draft brief; source links stay as inspiration provenance only. It requires a topic-specific source whose stated coverage includes the county or the nation and stores all intake rejections in `intake.json`.

Each qualifying source catalog record must explicitly set `sourceRole: "topic-specific"`, `themeTags` (matching the intake theme), and `coverageAreas` (the county or `national`). Generic portal and jurisdiction pages may remain in the catalog but cannot alone qualify a candidate. The intake also recognizes boutique retail accessibility, kitchen exhaust planning for a full renovation, and HVAC sizing discussion within a room addition. These themes frame questions for the design team; they do not advertise standalone HVAC work or assert a technical result. A patio cover remains ineligible without verified company service scope and a matching specific source.

The runner reads `scripts/company-info.js` for the existing OPC core-service and within-project trade boundaries. It records a digest of that policy in each brief, feeds it to the drafter and independent reviewer, and rejects positive standalone roofing/plumbing/electrical promises. An optional `mediaCatalog` in the input snapshot yields a `mediaPlan.json` shortlist only for records marked OPC-owned, blog-approved, privacy-checked, project-bound, and service-matched. The plan never chooses or approves an image; no photo is required for a draft. A human checks the exact candidate and derivative before a later site release.

When multiple Content Ideas rows resolve to the same theme and area, intake now keeps one candidate per `intentKey` (highest planning signal, earliest row on ties) and records the other rows as `duplicate-idea-intent` rejections with their sheet provenance. This prevents repeated rows from masquerading as fresh weekly topics. The existing live, legacy, and queued inventory remains a separate duplicate check.

Allowed services: `home renovation`, `home addition`, `shell construction`, `concrete work`, `deck construction`, `screen porch enclosure`, `commercial renovation`, `commercial build-out`, `commercial construction`. Allowed areas: `Broward County`, `Miami-Dade County`, `Palm Beach County`. The selector ranks eligible questions autonomously and stores the full rejected pool, including duplicates and out-of-scope topics.

## Run

After verifying that the installed Codex and Claude CLIs use existing subscriptions and no paid API key, run:

```sh
OPC_ALLOW_SUBSCRIPTION_CLI=1 node scripts/blog-v2/cli.js --input /path/to/snapshot.json --site-frontend /path/to/opc-website-v1/frontend --out /path/to/draft-bundles --provider codex
```

If Claude requests revision, the runner makes at most one Codex repair pass and asks Claude to review the revision independently. It preserves `originalDraft.json`, `originalReview.json`, `revisedDraft.json`, `revisedReview.json`, and `revision.json` in the new immutable bundle; `draft.json` and `review.json` are the final version used by the gate. To repair an existing blocked run without paying for another first draft or source retrieval, use `--resume-run /path/to/prior-run-dir` in place of `--input`. The new receipt links the prior run by ID and hash. A run that already used its one repair attempt cannot be resumed for another automatic repair.

For a multi-topic private batch, after an article-ready run, use `node scripts/blog-v2/next-snapshot.js <input-snapshot.json> <run-dir> <next-snapshot.json>`. It verifies the immutable receipt, adds that topic to `existing` as queued with its receipt hash, and writes a new snapshot without replacing the old one. Re-run the drafter on the new snapshot to select the next nonduplicate topic. A blocked run cannot advance this helper; investigate its failure and preserve its bundle. No schedule or publication operation is involved.

The repair prompt requires every `claims[].text` to match a contiguous visible sentence in `draft.body`, with that source's Markdown link in the same paragraph. The deterministic gate enforces this. If the repaired draft still fails a deterministic or independent review gate, its terminal status is `revision-gate-failed`; it receives no further automatic repair.

The draft comes from Codex; Claude independently reviews factual support and editorial quality. A failing source fetch, unavailable CLI, invalid JSON, unsupported claim, or reviewer finding stops readiness. No API fallback is configured. A fixture provider exists only for automated tests and does not count as an acceptance pilot.

The bundle contains `snapshot.json`, `selection.json`, `sources.json`, `brief.json`, `draft.json`, `review.json`, `gate.json`, `status.json`, and `receipt.json`. `receipt.json` records file hashes. Preserve the bundle in the shared editorial workspace; verify hashes when transferring it. `draft-ready-for-human-review` is an editorial handoff, never publication approval. Publication requires a separate per-version human approval and website release workflow.

`draft.body` is Markdown, matching the existing website posts. Every listed claim must appear in the body with an inline Markdown source link. Numeric claims must have the same quantity in the cited source excerpt and the claim evidence. Visuals are provenance records for review, not automatic assets.

The v3 editorial gate counts visible article words. A body under 400 words is `incomplete-article`; the drafting prompt targets a useful 450–650 words when evidence supports it and forbids padding or invented detail.

## Format and series review

The intake now assigns a `formatKey` to each supported theme: an evidence explainer, sequence walkthrough, or scope map. The draft and independent review must address that format with direct, source-supported answers. The deterministic gate rejects a mismatched format key or a draft that returns to mostly question headings. This guard addresses the repeated question-list failure in the first acceptance batch; independent review still judges whether the substance is useful.

After three distinct article-ready runs, evaluate the series with the existing Claude subscription route:

```sh
OPC_ALLOW_SUBSCRIPTION_CLI=1 node scripts/blog-v2/batch-review.js /path/to/run-1 /path/to/run-2 /path/to/run-3 --out /path/to/batch-audits
```

The command checks each immutable receipt, rejects blocked or duplicate runs, and records Claude's separate program-level review, findings, and a new hashed receipt. `private-trial-ready` permits only a private draft-generation trial; it never approves an article, a schedule, or publication. A `batch-hold` keeps recurrence off. Do not substitute three article-level passes for this series review. The site review preview can render a structured in-body decision diagram with provenance and rights metadata, but diagram content still needs factual and editorial review before it counts toward readiness.

Council round 4 requires jurisdiction metadata to describe the source's actual coverage. A Florida statute is tagged `Florida`, not `Broward County`. The intake can use statewide sources for a Broward reader, but its question and the draft title may claim county specificity only with county-level topic evidence. With national-only guidance, omit geography from the headline. Original in-body diagrams remain an explicit `OPC_ENABLE_ORIGINAL_DIAGRAMS=1` trial. A text-only scope map is now valid: the Fort Lauderdale CU pilot passed article review but its auto-built figure repeated headings and implied a sequence the sources did not establish. The evidence-explainer kitchen diagram likewise failed independent review for duplicated text and a misleading caption. Every source node in any future figure must repeat an exact reviewed claim and source ID; unsourced sections are visibly labeled OPC planning notes. The independent review sees a proposed diagram before deciding, and its receipt preserves the exact figure. No external image asset is fetched or licensed.

The snapshot validator now rejects a `leg.state.fl.us` statute whose `coverageAreas` includes a county. This enforces the observed Council round 4 correction before selection or model calls. It is a targeted guard against the exact misclassification in the retail pilot; other source coverage still requires editorial verification against the page itself.

Council round 5 adds a geographic check to each claim and a last-section reader artifact gate. A Markdown list or table is only a deterministic proxy; the independent series reviewer still decides whether it is useful and distinct across articles. The three pilots that prompted these gates remain immutable and held. Numeric publisher, claim, and figure quotas are not active. The source-poor HVAC sequence needs explicit order/dependency evidence or a narrower explainer before another acceptance batch. Publication requires a separate exact-content-hash human approval path, which is not present in the runner.

## Rollback

Disable any separate schedule and stop invoking this CLI. Existing site content is not changed by a run. Keep bundles and receipts for audit. Revert the v2 runner commit to remove the code; do not re-enable the old WordPress workflow.
