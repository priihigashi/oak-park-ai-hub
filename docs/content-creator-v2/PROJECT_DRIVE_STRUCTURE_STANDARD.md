# Active Product Drive Structure Standard

Created: 2026-08-05
Corrected: 2026-08-05
Scope: Content Creator V2 first, then every active product that needs human-visible organization, agent handoff and recovery.

## Purpose

Every active product needs a visual Google Drive home, a one-page human README, a tracker, stable links to canonical docs, and GitHub Markdown backups for the product brain. This prevents product knowledge from living only in chat, local agent memory, a Mac workspace, or scattered spreadsheets.

## Canonical pattern

Use the existing shared workspace when available:

`Claude Code Workspace / _Active Products / <Clear Product Name>`

This folder was corrected from `_Active Projects` to `_Active Products` because Priscila wants product homes, not loose project buckets. Treat the first level under `_Active Products` as active products/systems. Each product can contain many workstreams, modules, agents, trackers and plans.

Do not move or rename older canonical documents casually. When an important document already lives in `_Master Plans & Docs`, GitHub, Focus, Flow Plans Tracker, or another established folder, preserve it there and link to it from the product home. Prefer links/shortcuts and index rows over moving source files.

## Required product folders

Each active product should use this structure:

```text
00_README_AND_INDEX
01_Master_Plans_AND_Strategy
02_Modules_AND_Workstreams
03_Trackers_AND_Status
04_Research_AND_Benchmarks
05_Assets_AND_Storage_Map
```

Optional product-specific subfolders can be added under `02_Modules_AND_Workstreams` when the product has multiple brains/modules.

For Content Creation System, the initial module folders are:

```text
02_01_Storytelling_AND_Scripts
02_02_Media_Retrieval_AND_Clip_Finder
02_03_Editing_AND_Rendering
02_04_AI_Generation_AND_Assets
02_05_Routing_Agents_AND_Automation
02_06_Publishing_AND_Status
```

## Required README

Every active product folder must include a one-page human README that answers:

1. What is this product/system in plain language?
2. What are the active modules/workstreams?
3. Where is the master plan?
4. Where is the GitHub backup?
5. Where is the Focus task row?
6. Where are assets stored?
7. What must not be moved, renamed, deleted, or committed?
8. What is the current next execution step?
9. What should a future agent read first?

## Required tracker

Each active product should have a tracker spreadsheet for human visibility. Focus remains the operational master task list; the product tracker is the visual product map. A higher-level tracker may live at the `_Active Products` level later; until then, existing Flow Plans Tracker and Focus remain the cross-product operating index.

Recommended tabs:

- Overview
- Modules
- Decisions
- Links
- Risks
- Changelog

Recommended columns:

- Workstream
- Module / Brain
- Status
- Owner / Agent
- Canonical Doc / Link
- GitHub Doc / Link
- Focus Row(s)
- Next Action
- Notes / Risks

## GitHub rule

GitHub stores:

- Markdown plans
- code
- schemas
- prompts
- tests
- tiny fixtures
- audit/status files

GitHub must not store:

- real job videos
- Apple Photos exports
- personal media libraries
- generated reels
- large thumbnails
- embeddings from personal footage
- local SQLite catalogs from personal media
- OAuth tokens
- cookies
- credentials
- generated caches

## Agent start rule

When Priscila says “go,” “vai,” or “continue” on an active product, the agent must:

1. Open the product README.
2. Open the product tracker.
3. Read the master Google Doc.
4. Read GitHub docs under the stable product path.
5. Check relevant Focus rows.
6. Continue from the current next action.
7. Avoid asking Priscila to repeat context that is already documented.

## Content Creation System current state

A visual product home exists at:

`Claude Code Workspace / _Active Products / Content Creation System`

The next execution step remains Package 0 real audit. Before runtime coding, Codex or Claude must create real `CODE_AUDIT.md` and `STATUS.md`, then decide for every component whether to REUSE, EXTEND, ADAPT, REPLACE LATER, or create NEW.

## Later dashboard direction

Later, this Drive + GitHub + Focus structure can become a proper product dashboard/app showing progress, blockers, open decisions, docs, commits, tests, and owners. Until that app exists, the Drive product home plus Focus rows are the visual operating system.
