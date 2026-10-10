# OPC Blog v2 draft runner

This runner produces a review bundle only. It has no publishing or WordPress operation. The legacy `blog-generator.js` remains separate and must stay disabled for v2.

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

`existing` must contain the current React articles, legacy WordPress titles/intents, and queued topics. The Content Ideas sheet can supply questions and provenance, but it does not establish construction facts. Every candidate needs at least one topic-relevant official source. The runner fetches public sources at run time, checks status and excerpt overlap, and records a retrieval digest. Internal company facts may use `access: "internal-preverified"` with `evidenceId`, `verifiedBy`, `capturedAt`, and `excerpt`; this cannot support external technical or legal assertions.

For autonomous intake directly from the Content Ideas export, use `{snapshotAt, ideaRows, sourceCatalog, existing}`. Each `ideaRows` entry may be a 23-column sheet row array or an object with `rowNumber`, `rawIdea`, `topicDirection`, `sourceLink`, `status`, and `blogUrl`. The intake adapter classifies supported themes into safe question templates. It never passes raw hooks or payoffs into the draft brief; source links stay as inspiration provenance only. It requires a topic-specific source whose stated coverage includes the county or the nation and stores all intake rejections in `intake.json`.

Each qualifying source catalog record must explicitly set `sourceRole: "topic-specific"`, `themeTags` (matching the intake theme), and `coverageAreas` (the county or `national`). Generic portal and jurisdiction pages may remain in the catalog but cannot alone qualify a candidate. The intake also recognizes boutique retail accessibility, kitchen exhaust planning for a full renovation, and HVAC sizing discussion within a room addition. These themes frame questions for the design team; they do not advertise standalone HVAC work or assert a technical result. A patio cover remains ineligible without verified company service scope and a matching specific source.

Allowed services: `home renovation`, `home addition`, `shell construction`, `concrete work`, `deck construction`, `screen porch enclosure`, `commercial renovation`, `commercial build-out`, `commercial construction`. Allowed areas: `Broward County`, `Miami-Dade County`, `Palm Beach County`. The selector ranks eligible questions autonomously and stores the full rejected pool, including duplicates and out-of-scope topics.

## Run

After verifying that the installed Codex and Claude CLIs use existing subscriptions and no paid API key, run:

```sh
OPC_ALLOW_SUBSCRIPTION_CLI=1 node scripts/blog-v2/cli.js --input /path/to/snapshot.json --out /path/to/draft-bundles --provider codex
```

If Claude requests revision, the runner makes at most one Codex repair pass and asks Claude to review the revision independently. It preserves `originalDraft.json`, `originalReview.json`, `revisedDraft.json`, `revisedReview.json`, and `revision.json` in the new immutable bundle; `draft.json` and `review.json` are the final version used by the gate. To repair an existing blocked run without paying for another first draft or source retrieval, use `--resume-run /path/to/prior-run-dir` in place of `--input`. The new receipt links the prior run by ID and hash. A run that already used its one repair attempt cannot be resumed for another automatic repair.

The repair prompt requires every `claims[].text` to match a contiguous visible sentence in `draft.body`, with that source's Markdown link in the same paragraph. The deterministic gate enforces this. If the repaired draft still fails a deterministic or independent review gate, its terminal status is `revision-gate-failed`; it receives no further automatic repair.

The draft comes from Codex; Claude independently reviews factual support and editorial quality. A failing source fetch, unavailable CLI, invalid JSON, unsupported claim, or reviewer finding stops readiness. No API fallback is configured. A fixture provider exists only for automated tests and does not count as an acceptance pilot.

The bundle contains `snapshot.json`, `selection.json`, `sources.json`, `brief.json`, `draft.json`, `review.json`, `gate.json`, `status.json`, and `receipt.json`. `receipt.json` records file hashes. Preserve the bundle in the shared editorial workspace; verify hashes when transferring it. `draft-ready-for-human-review` is an editorial handoff, never publication approval. Publication requires a separate per-version human approval and website release workflow.

`draft.body` is Markdown, matching the existing website posts. Every listed claim must appear in the body with an inline Markdown source link. Numeric claims must have the same quantity in the cited source excerpt and the claim evidence. Visuals are provenance records for review, not automatic assets.

The v3 editorial gate counts visible article words. A body under 400 words is `incomplete-article`; the drafting prompt targets a useful 450–650 words when evidence supports it and forbids padding or invented detail.

## Rollback

Disable any separate schedule and stop invoking this CLI. Existing site content is not changed by a run. Keep bundles and receipts for audit. Revert the v2 runner commit to remove the code; do not re-enable the old WordPress workflow.
