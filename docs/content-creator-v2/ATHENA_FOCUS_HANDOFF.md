# Content Creator V2 — Athena / Focus Handoff

Created: 2026-08-05
Repository: `priihigashi/oak-park-ai-hub`
Branch: `content-creator-v2/docs-source-of-truth-2026-08-05`

## Purpose

This file exists so Athena, Focus, Codex, Claude, and future agents can discover the current project brain without relying on chat history.

## Mandatory next rule

Before coding new Content Creator V2 runtime features, execute **Package 0 — Repository Baseline and Collision Audit**.

Do not start by building another system. Do not modify runtime code. Do not push to `main`. Do not open a PR before Priscila reviews the audit.

Package 0 must produce:

- `docs/content-creator-v2/CODE_AUDIT.md`
- `docs/content-creator-v2/STATUS.md`

For each requirement and existing component, mark one of:

- `REUSE`
- `EXTEND`
- `ADAPT`
- `RECREATE`
- `REPLACE LATER`
- `NEW`

## Stable pointers

- Google Doc: `CONTENT CREATOR V2 — IMPLEMENTATION PACKAGES FOR CODEX & CLAUDE — 2026-08-05`
- GitHub storage doc: `docs/content-creator-v2/SOURCE_OF_TRUTH_AND_STORAGE.md`
- This handoff: `docs/content-creator-v2/ATHENA_FOCUS_HANDOFF.md`
- Focus: `_Focus Partner — STATE`, tab `Pending`, rows `1104–1113`
- Main implementation repo: `priihigashi/oak-park-ai-hub`

## Security and audit gates

Two different gates now exist:

1. **Package 0 code/product audit gate** — prevents duplicate, broken, or shiny rebuilds before understanding existing code.
2. **Security/2FA-bypass gate** — Focus row 87; mandatory for app release/security surfaces.

Both must be preserved. Package 0 does not replace security review. Security review does not replace Package 0.

## Apple Photos / job-site index findings to reconcile

These came from adjacent chats and must be folded into Content Creator V2:

- A scanner bug was found: the previous scanner scanned `albums`, but should scan `containers`.
- Smart Albums do not appear under `albums`, so several containers were skipped.
- Missed containers include `POMPANO BROWN`, `Favorites`, `AMAZON - UGC`, `SOCIAL READY`, `DESIGN`, `KIDS`, and `WORLD`.
- The Smart Album `Videos — last 30 days` already exists and reads correctly: 172 items in about 1 second.
- A broad Smart Album such as `Date Captured is after 01/01/2000` may take coverage from about 14.75% to near-total coverage of roughly 43,960 items.
- Finding by GPS/date/site is partially solved, but thumbnails are not solved.
- Until thumbnails exist, the index tells what clip/date/site to open, not what the clip visually looks like.
- Fetching actual original files is still unproven because iCloud may have evicted originals.
- Mike’s clips are separate because they live on his phone/Apple ID.
- The job-site index currently stands alone. It is not yet connected to `/opc-carousel-creator`, Drive, Sheets, Remotion, CapCut, Premiere, Athena, or the Content Creator Agent.
- The index cannot yet distinguish home/residence from job site; site labels must be persisted after Priscila labels them.
- The index is a snapshot unless a refresh cadence exists.
- Any GPS/media-derived personal data must be treated as private and not blindly committed.
- OpenStreetMap reverse-geocoding was used; future use must consider privacy, caching, rate limits, and outbound-data minimization.

## Manual bridge tools to preserve in the plan

Manual or semiautomatic routes are not the owned final system, but they matter because posting cannot wait.

- Apple Photos + Smart Albums + local index: immediate footage finding by site/date.
- CapCut: immediate manual/semiautomatic phone-native b-roll route.
- Adobe Premiere Media Intelligence: candidate for semantic media search; evaluate before adopting.
- Gling or Descript: candidate for Mike/talking-head cleanup.
- FFmpeg: local mechanical processor for trim, resize, caption burn-in, concat, and exports; not editorial judgment.
- Remotion/manual builder: existing internal benchmark route.
- Viewmax, OpenArt Director, Sandcastles, Blotato, MoneyPrinterTurbo, Generative-Media-Skills: evaluate through external-tool policy before adoption.

## Automation north star

The owned assistant should help Priscila create construction content with as little manual effort as practical:

1. find real project clips;
2. generate content ideas from available footage;
3. create script/shot plan;
4. show candidate visuals with thumbnails/contact sheet;
5. allow quick approve/replace;
6. render/export without destroying originals;
7. preserve provenance, costs, rights, and storage boundaries.

## Do not skip loose ends

Before Package 1 coding:

- Reconcile Apple Photos/job-site index with the dataset plan.
- Update scanners to include containers, not only albums.
- Decide whether the broad “everything” Smart Album is required.
- Keep thumbnails as unsolved V2 work.
- Keep originals-fetching as unproven.
- Keep Mike’s clips as a separate device/human workflow.
- Include manual tool recommendations in the plan, but do not let tool shopping replace Package 0.
- Preserve Focus/Athena pointers so future agents can read more instead of relying on memory.

## Next agent command

Read the Google Doc, this handoff, and Focus rows 1104–1113. Then execute Package 0 as documentation-only audit. Stop after `CODE_AUDIT.md` and `STATUS.md` unless Priscila explicitly approves moving to Package 1.
