# Content Creator V2 — Drive Structure Audit and Correction Plan

Created: 2026-08-05
Corrected: 2026-08-05
Status: partially corrected; final cross-folder audit still required before declaring the Drive standard permanent.

## Why this exists

Priscila correctly flagged that the assistant created `_Active Projects` on 2026-08-05 without first proving it was the pre-existing or canonical product/project folder.

This was corrected immediately by renaming the folder to `_Active Products`, because Priscila wants active products/systems at the first level, not loose projects.

## Confirmed facts

- `Claude Code Workspace` existed before this session.
- `_Master Plans & Docs` existed before this session under `Claude Code Workspace`.
- A search did not find a pre-existing folder named `Produtos Ativos` or `Active Products`.
- `_Active Projects` was created on 2026-08-05 under `Claude Code Workspace` and then renamed to `_Active Products`.
- `_Active Products` currently contains `Content Creation System` only at the time of this correction note.
- The workspace already contains several adjacent folders and files that may represent older active products, project homes, trackers or source-of-truth areas.

Known adjacent candidates under `Claude Code Workspace` include:

- `_Master Plans & Docs`
- `Flow Plans Tracker — Master Index`
- `ContentAutomation`
- `Content Hub`
- `Story Creation`
- `Content - Reels & TikTok`
- `Content - Blog`
- `Content - YouTube`
- `Website Projects`
- `Oak Park Construction`
- `OPC PM Tool — Mike Build`
- `Contractor AI`
- `Productivity & Routine`
- `Agents & Skills`
- `4AM Agent Reports`
- `AI DUMP IDEAS`
- `Resources`
- `Content Scraper Resources`
- `_Shared`

## Immediate rule

Do not create more active-product folders or move documents as if `_Active Products` is fully permanent until the final audit is complete.

Treat `_Active Products / Content Creation System` as the corrected active-product staging/index layer.

## Target structure

```text
Claude Code Workspace
├── _Active Products
│   ├── Active Products — Tracker / index later if needed
│   └── Content Creation System
│       ├── 00_README_AND_INDEX
│       ├── 01_Master_Plans_AND_Strategy
│       ├── 02_Modules_AND_Workstreams
│       ├── 03_Trackers_AND_Status
│       ├── 04_Research_AND_Benchmarks
│       └── 05_Assets_AND_Storage_Map
├── _Master Plans & Docs
├── Flow Plans Tracker — Master Index
└── other existing workspace areas
```

## Audit goal

Decide the official Drive standard for active products:

1. KEEP `_Active Products` as canonical active-product index.
2. MOVE `Content Creation System` into an existing better folder.
3. CONVERT `_Active Products` into a shortcut/index-only layer pointing to existing product homes.
4. ARCHIVE `_Active Products` if duplicative.

## Audit method

For each candidate folder/file, record:

| Folder/File | Existing purpose | Current contents | Owner/product | Active? | Duplicates with Content Creation System? | Recommended action |
|---|---|---|---|---|---|---|

Minimum folders to inspect:

- Claude Code Workspace root
- `_Master Plans & Docs`
- `Flow Plans Tracker — Master Index`
- `ContentAutomation`
- `Content Hub`
- `Story Creation`
- `Content - Reels & TikTok`
- `Website Projects`
- `Oak Park Construction`
- `OPC PM Tool — Mike Build`
- `Contractor AI`
- `Productivity & Routine`
- `Agents & Skills`

## Correction options

### Option A — Keep Active Products as canonical index

Use if no older canonical active-product folder exists.

Rules:
- Keep one folder per active product/system.
- Product folder may contain human README, tracker and shortcuts to canonical docs.
- Do not duplicate master docs if they already live in `_Master Plans & Docs`.
- Use shortcuts instead of moving stable documents unless Priscila approves.

### Option B — Convert Active Products to shortcut dashboard

Use if older folders already hold product materials.

Rules:
- `_Active Products` contains only product folders with README/index and shortcuts.
- Real documents stay in original stable homes.
- Each README explains where the real product lives.

### Option C — Move into existing canonical folder

Use if a better product-home folder already exists.

Rules:
- Create an index/shortcut from `_Active Products` if useful.
- Do not break links.
- Record all moves in Focus and README.

### Option D — Archive new layer

Use if `_Active Products` creates confusion.

Rules:
- Move or delete only after Priscila explicitly approves.
- Preserve all links before any move.

## Required output

Create or update:

- `docs/content-creator-v2/DRIVE_STRUCTURE_DECISION.md`
- Google Doc addendum in the Content Creator V2 implementation package doc
- Focus row with the final decision

## Stop condition

If the audit shows multiple plausible canonical homes, stop and ask Priscila to choose between explicit options. Do not guess.

## Current provisional instruction for new agents

Use `_Active Products / Content Creation System` as the corrected active-product staging index until the final audit is complete. Do not assume it is final if the full cross-folder audit has not been completed.
