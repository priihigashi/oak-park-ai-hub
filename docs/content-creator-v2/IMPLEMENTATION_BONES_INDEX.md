# Content Creator V2 — Implementation Bones Index

Created: 2026-08-05
Status: documentation skeleton. Package 0 must fill the real values.

## Purpose

This file lists the minimum structure that must exist so this project does not remain a vague plan.

It covers the seven missing pieces Priscila asked to lock down:

1. CODE_AUDIT.md
2. STATUS.md
3. DATASET_MANIFEST.md
4. BENCHMARK_PROTOCOL.md
5. Polished project tracker template
6. Dashboard idea
7. New-chat handoff prompt

---

## 1. CODE_AUDIT.md — required bones

File path:

```text
docs/content-creator-v2/CODE_AUDIT.md
```

Required sections:

```markdown
# Content Creator V2 — Code Audit

Date:
Repo:
Branch:
Auditor:
Scope:
Production impact: Documentation only / No runtime code changed.

## Executive summary

## Files inspected

## Existing system map

## Requirement decision table

| Requirement | Existing file/symbol | Decision | Reason | Allowed package | Risk | Tests required | Notes |
|---|---|---|---|---|---|---|---|

## Reuse map

## Extend map

## Adapt map

## Recreate map

## Replace-later map

## New-build map

## Forbidden files until later packages

## Package 1 safe file list

## Public repo/app acceleration opportunities

## Shortest MVP slice

## Required tests before coding

## Risks and stop conditions

## Recommendation
```

Decision vocabulary:

- REUSE
- EXTEND
- ADAPT
- RECREATE
- REPLACE LATER
- NEW

Required explicit answers:

- Does an equivalent of MediaAsset already exist?
- Does an equivalent of Scene already exist?
- Does an equivalent of ShotRequest already exist?
- Does an equivalent of ClipCandidate already exist?
- Does an equivalent of EditDecision already exist?
- Which old flow pieces are unreliable?
- What can be reused without preserving broken behavior?
- What is the fastest safe vertical slice?

---

## 2. STATUS.md — required bones

File path:

```text
docs/content-creator-v2/STATUS.md
```

Required sections:

```markdown
# Content Creator V2 — Status

Last updated:
Current branch:
Current package:
Current phase:
Last completed action:
Next action:

## Current state

## Source-of-truth links

## Files changed this session

## Commands run

## Tests run

## Test results

## Production-impact statement

## Secrets/media/storage statement

## Risks

## Open decisions

## Stop conditions

## Next prompt
```

Rules:

- Every coding or audit session updates STATUS.md.
- If STATUS.md is stale or missing, the next agent must stop and repair it first.
- STATUS.md is not a chat summary; it is the operational truth for implementation.

---

## 3. DATASET_MANIFEST.md — required bones

File path:

```text
docs/content-creator-v2/DATASET_MANIFEST.md
```

Required purpose:

Select 20–40 approved OPC clips/folders for testing without committing real videos, GPS cache, thumbnails, embeddings, or personal media catalogs.

Required sections:

```markdown
# Content Creator V2 — Dataset Manifest

Dataset version:
Owner approval:
Storage location type: Apple Photos / Drive / local folder / other
Media committed to GitHub: No
Private metadata committed to GitHub: No

## Test set goals

## Inclusion rules

## Exclusion rules

## Selected folders/assets

| ID | Human label | Source location reference | Media type | Approx count | Permission | Expected use | Privacy notes |
|---|---|---|---|---:|---|---|---|

## Expected search queries

| Query | Expected asset/site | Expected visual type | Must find? | Notes |
|---|---|---|---|---|

## Refresh rules

## Storage boundaries
```

Initial test categories:

- concrete / shell work
- kitchen renovation
- demolition
- exterior addition
- Mike inspecting work
- before/after
- tools/equipment
- finished detail
- job-site walk-through

---

## 4. BENCHMARK_PROTOCOL.md — required bones

File path:

```text
docs/content-creator-v2/BENCHMARK_PROTOCOL.md
```

Required purpose:

Measure whether the internal system actually saves time versus manual tools.

Required sections:

```markdown
# Content Creator V2 — Benchmark Protocol

Benchmark date:
Script/topic:
Dataset version:
Evaluator:

## Benchmark question

## Shared input

## Tools compared

| Tool | Purpose | Setup time | Clip-finding time | Editing time | Output quality | Manual burden | Storage/privacy risk | Verdict |
|---|---|---:|---:|---:|---|---|---|---|

## Required tools

- Apple Photos + Smart Album/job-site index
- CapCut
- Adobe Premiere Media Intelligence
- Descript or Gling
- Existing Remotion/manual builder
- Future internal V2

## Same-script test

## Scoring rubric

## Results

## Decision
```

Scoring categories:

- time to find footage
- time to first draft
- how much manual selection Priscila must do
- quality of b-roll match
- ease of changing a clip
- storage/privacy safety
- repeatability

---

## 5. Polished project tracker template — required bones

File path later:

```text
docs/project-management/PROJECT_TRACKER_TEMPLATE.md
```

Google Sheet later:

```text
Reusable Project Tracker Template
```

Required tabs:

- Overview
- Workstreams
- Tasks
- Decisions
- Risks
- Links
- Changelog
- Dashboard

Required columns for Tasks:

- ID
- Workstream
- Task
- Status
- Priority
- Difficulty
- Owner
- Next action
- Link
- Due/Target
- Risk
- Last updated
- Source

Required statuses:

- Not started
- Pending
- In progress
- Blocked
- Needs Priscila
- Done
- Archived

Required priority:

- P0 Critical
- P1 High
- P2 Medium
- P3 Low

Required difficulty:

- XS
- S
- M
- L
- XL

Rule:

Focus remains the operating tracker until this template is tested. Do not create duplicate Jira-like sheets per project unless explicitly needed.

---

## 6. Dashboard idea — required bones

File path later:

```text
docs/project-management/PROJECT_DASHBOARD_ROADMAP.md
```

Purpose:

Create a future live visual dashboard that reads from Focus, project trackers and GitHub status files.

Dashboard should show:

- active projects
- current package/phase
- blocked items
- next action
- stale docs/status
- risks
- last commit/branch
- Focus row links
- Drive doc links
- GitHub doc links

Phases:

1. Google Sheets dashboard.
2. Looker Studio or lightweight web dashboard.
3. App dashboard connected to Focus/GitHub/Drive.

Do not build now. Capture as future infrastructure.

---

## 7. New-chat handoff prompt — required bones

Current file:

```text
docs/content-creator-v2/NEW_CHAT_RECOVERY_AND_CODEX_PROMPTS.md
```

Must include:

- Drive anchors
- GitHub branch/path anchors
- Focus row anchors
- warning that `_Active Projects` is provisional
- Package 0 first rule
- no-new-folder-before-Drive-audit rule
- no-runtime-code-before-CODE_AUDIT rule
- Codex Package 0 prompt
- Package 1 prompt after audit passes

---

## Current closure status

Bones exist for all seven items.

The real missing work is filling them with actual code audit results and real dataset/benchmark entries.

Next required actions:

1. Run Drive Structure Audit.
2. Run public repo/app acceleration audit.
3. Run Package 0 real code audit.
4. Fill CODE_AUDIT.md and STATUS.md.
5. Only then begin Package 1.
