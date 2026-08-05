# Drive Structure Decision — Active Products

Created: 2026-08-05
Status: DECIDED for operational use
Scope: Claude Code Workspace, active product organization, Content Creation System handoff.

## Decision

Use this as the canonical operational path for active product work:

```text
Claude Code Workspace / _Active Products / <Product Name>
```

For the current product:

```text
Claude Code Workspace / _Active Products / Content Creation System
```

Future agents should start here:

```text
Claude Code Workspace / _Active Products / Content Creation System / 00_README_AND_INDEX / Content Creation System — README & Project Index
```

## Why this is the decision

A workspace audit confirmed that `Claude Code Workspace` already contains many older operational folders and planning areas, but no older clearly canonical folder named `Active Products`, `Produtos Ativos`, `Active Projects`, or equivalent active-product index was found during the correction pass.

The workspace already has these top-level areas:

- `_Master Plans & Docs`
- `Flow Plans Tracker — Master Index`
- `ContentAutomation`
- `Content Hub`
- `Content - Reels & TikTok`
- `Content - Blog`
- `Content - YouTube`
- `Story Creation`
- `Website Projects`
- `Oak Park Construction`
- `OPC PM Tool — Mike Build`
- `Contractor AI`
- `Productivity & Routine`
- `Agents & Skills`
- `4AM Agent Reports`
- `Resources`
- `Content Scraper Resources`
- `_Shared`
- other brand, research and content folders

These are useful existing folders, but they serve mixed purposes: channels, operations, resources, brands, historical plans, reports, or app-specific areas. They are not a single visual list of active products.

Therefore `_Active Products` is now the product-level index. It is not a replacement for `_Master Plans & Docs`.

## Roles of each layer

### `_Active Products`

Purpose: visual home for live products.

Rules:

- one folder per active product;
- first-level children are products, not loose projects;
- each product folder must include README, tracker, modules/workstreams, research, storage map and links to source documents;
- it may contain shortcuts/links to older docs rather than moving everything.

### `_Master Plans & Docs`

Purpose: vault/canonical archive for master plans and durable planning documents.

Rules:

- keep historical/master docs here when they already live here;
- do not move master plans casually;
- product folders should point back to the master docs with links or shortcuts;
- this is not the day-to-day visual product dashboard.

### `Flow Plans Tracker — Master Index`

Purpose: cross-flow index/tracker.

Rules:

- preserve it as an existing master index;
- do not replace it with product trackers;
- product trackers can link to it when relevant.

### Channel / operational folders

Examples: `ContentAutomation`, `Content Hub`, `Content - Reels & TikTok`, `Content - Blog`, `Content - YouTube`, `Story Creation`.

Purpose: production areas, channel-specific storage, content outputs, automation artifacts, and historical workflow folders.

Rules:

- do not move them into `_Active Products` without explicit approval;
- link to them from the active product README/module folders when they are relevant;
- treat them as working/storage zones, not product brains.

## Product folder standard

Each product folder under `_Active Products` should use:

```text
00_README_AND_INDEX
01_Master_Plans_AND_Strategy
02_Modules_AND_Workstreams
03_Trackers_AND_Status
04_Research_AND_Benchmarks
05_Assets_AND_Storage_Map
```

For Content Creation System, the module folders are:

```text
02_01_Storytelling_AND_Scripts
02_02_Media_Retrieval_AND_Clip_Finder
02_03_Editing_AND_Rendering
02_04_AI_Generation_AND_Assets
02_05_Routing_Agents_AND_Automation
02_06_Publishing_AND_Status
```

## What Claude/Codex should read first

When asked to continue Content Creation System work, start here:

1. `Claude Code Workspace / _Active Products / Content Creation System / 00_README_AND_INDEX / Content Creation System — README & Project Index`
2. `Claude Code Workspace / _Active Products / Content Creation System / 03_Trackers_AND_Status / Content Creation System — Project Tracker`
3. `Claude Code Workspace / _Master Plans & Docs / CONTENT CREATOR V2 — IMPLEMENTATION PACKAGES FOR CODEX & CLAUDE — 2026-08-05`
4. GitHub branch `content-creator-v2/docs-source-of-truth-2026-08-05`, folder `docs/content-creator-v2/`
5. Focus Sheet rows 1110 onward.

## What not to do

- Do not create another top-level folder for the same product.
- Do not move master plans out of `_Master Plans & Docs` just to make the active product folder look complete.
- Do not delete or rename older operational folders.
- Do not put real media, Apple Photos exports, personal SQLite indexes, generated videos, thumbnails, credentials, tokens, cookies or secrets in GitHub.
- Do not start Package 1 implementation before Package 0 real audit creates `CODE_AUDIT.md` and `STATUS.md`.

## Current Content Creation System status

Active product home:

```text
Claude Code Workspace / _Active Products / Content Creation System
```

Master plan vault:

```text
Claude Code Workspace / _Master Plans & Docs
```

Next execution order:

1. Public repo/app acceleration audit.
2. Package 0 real repo/code audit.
3. Create `CODE_AUDIT.md`.
4. Create real `STATUS.md`.
5. Only then start Package 1 contracts.

## Final call

This decision is now operationally final unless Priscila explicitly changes it after reviewing the Drive visually.
