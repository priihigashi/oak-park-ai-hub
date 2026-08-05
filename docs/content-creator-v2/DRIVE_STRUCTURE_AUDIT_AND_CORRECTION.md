# Content Creator V2 — Drive Structure Audit and Correction Plan

Created: 2026-08-05
Status: required before more Drive folder creation or project-home standardization.

## Why this exists

Priscila correctly flagged that the assistant created `_Active Projects` on 2026-08-05 without first proving it was the pre-existing or canonical project folder.

This must be corrected as process debt before the folder standard becomes permanent.

## Confirmed facts

- `Claude Code Workspace` existed before this session.
- `_Active Projects` was created on 2026-08-05 under `Claude Code Workspace`.
- `_Active Projects` currently contains `Content Creation System` only at the time of this correction note.
- The workspace already contains several adjacent folders and files that may represent older active projects, project homes, trackers or source-of-truth areas.

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

Do not create more folders or move documents as if `_Active Projects` is canonical until this audit is complete.

Treat `_Active Projects / Content Creation System` as a provisional visual staging/index layer.

## Audit goal

Decide the official Drive standard for active projects:

1. KEEP `_Active Projects` as canonical.
2. MOVE `Content Creation System` into an existing better folder.
3. CONVERT `_Active Projects` into a shortcut/index-only layer pointing to existing project homes.
4. ARCHIVE `_Active Projects` if duplicative.

## Audit method

For each candidate folder/file, record:

| Folder/File | Existing purpose | Current contents | Owner/project | Active? | Duplicates with Content Creation System? | Recommended action |
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

### Option A — Keep Active Projects as canonical index

Use if no older canonical active-project folder exists.

Rules:
- Keep one folder per active project.
- Project folder may contain human README, tracker and shortcuts to canonical docs.
- Do not duplicate master docs if they already live in `_Master Plans & Docs`.
- Use shortcuts instead of moving stable documents unless Priscila approves.

### Option B — Convert Active Projects to shortcut dashboard

Use if older folders already hold project materials.

Rules:
- `_Active Projects` contains only project folders with README/index and shortcuts.
- Real documents stay in original stable homes.
- Each README explains where the real project lives.

### Option C — Move into existing canonical folder

Use if a better project-home folder already exists.

Rules:
- Create an index/shortcut from `_Active Projects` if useful.
- Do not break links.
- Record all moves in Focus and README.

### Option D — Archive new layer

Use if `_Active Projects` creates confusion.

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

Use `_Active Projects / Content Creation System` only as a visual staging index until this audit is complete. Do not assume it is final.
