# Content Creator V2 — Planning Closure Checklist

Created: 2026-08-05
Status: planning artifact only. No production code, secrets, workflows, media, or main branch changes.

## Purpose

Close the remaining planning gap so Codex, Claude, Athena, or a future agent can continue the project without reconstructing this chat.

The goal is not to claim the software is done. The goal is to make the planning layer close to complete: source of truth, package order, safety gates, external tool/repo evaluation, dataset plan, manual bridges, and handoff rules.

## Current readiness estimate

- Planning before this closure pass: about 70–75%.
- Planning target after this closure pass: about 90–95%.
- Actual working MVP remains about 25–35% built until Package 0 and implementation packages are executed.
- Full product vision remains much earlier stage.

## What was still missing from planning

| Gap | Status | Where it is handled |
| --- | --- | --- |
| Package 0 real audit requirement | Captured | Implementation packages doc + ATHENA_FOCUS_HANDOFF.md |
| Source of truth and recovery plan | Captured | SOURCE_OF_TRUTH_AND_STORAGE.md |
| Athena/Focus handoff | Captured | ATHENA_FOCUS_HANDOFF.md |
| Apple Photos / job-site index loose ends | Captured | ATHENA_FOCUS_HANDOFF.md + this checklist |
| External apps and public repos research plan | Captured now | EXTERNAL_APPS_AND_REPOS_RESEARCH_PLAN.md |
| Reusable project execution formula | Captured now | PROJECT_EXECUTION_PLAYBOOK.md |
| Manual bridge recommendations | Captured now | EXTERNAL_APPS_AND_REPOS_RESEARCH_PLAN.md |
| Tracker/Jira question | Resolved for now | Focus remains operational tracker; GitHub docs remain specs; GitHub issues optional later |
| Dataset manifest | Still next-step doc | DATASET_MANIFEST.md should be created after Package 0 or from Apple Photos index results |
| Benchmark protocol | Still next-step doc | BENCHMARK_PROTOCOL.md should compare CapCut, Premiere, Descript/Gling, and internal V2 |
| CODE_AUDIT.md | Still first implementation artifact | Must be created by Package 0 before runtime coding |
| STATUS.md | Still first implementation artifact | Must be created by Package 0 and updated after every package |

## Non-negotiable order

1. Read source-of-truth docs.
2. Read Focus rows 1104–1114 and related rows recovered in the addenda.
3. Run Package 0 as a real repository audit.
4. Create CODE_AUDIT.md and STATUS.md.
5. Only then start Package 1 contracts/enums.
6. Do not touch production runtime, secrets, main branch, GitHub Actions, media files, Drive routing, approval email flows, or existing motion_sources behavior before the audit allows it.

## Apple Photos / job-site index items captured

- The other chat found a bug: the scanner looked at albums but should scan containers; smart albums were skipped.
- `Videos — last 30 days` already exists and reads quickly.
- A broad Smart Album such as Date Captured after 2000-01-01 may make near-total library coverage possible.
- The job-site index is useful but not the finished Content Creator: it finds likely clips, but does not show thumbnails, fetch originals, plan shots, approve selections, or render posts.
- Thumbnails are a V2 need and may require slow iCloud downloads.
- Original file fetching is not proven.
- Mike's clips are separate and depend on his phone/library workflow.
- The Apple Photos index should feed DATASET_MANIFEST.md and later the personal-library provider.

## Manual bridge policy

Manual tools are allowed as practical bridges, not replacements for the internal system.

- Apple Photos/job-site index: find clips by address/date now.
- CapCut: fast manual/mobile assembly when a post must ship.
- Adobe Premiere Media Intelligence: benchmark for semantic media search.
- Descript or Gling: talking-head cleanup benchmark.
- FFmpeg: local mechanical processing, trimming, resizing, caption burn-in, and exports.
- Remotion/manual builder: existing owned rendering benchmark.

## External tool policy

Every app/repo/tool must be classified before adoption:

- MANUAL BRIDGE — use manually when stuck.
- BENCHMARK — compare against our internal build.
- REFERENCE — learn patterns only.
- ADAPT — wrap or clean-room implement a bounded piece.
- ADOPT — only after license, privacy, cost, security, and pilot pass.
- REJECT — not aligned, too risky, or duplicates better owned route.

## Done when planning is effectively closed

Planning is close enough when these files exist and are linked from Focus:

- SOURCE_OF_TRUTH_AND_STORAGE.md
- ATHENA_FOCUS_HANDOFF.md
- PLANNING_CLOSURE_CHECKLIST.md
- PROJECT_EXECUTION_PLAYBOOK.md
- EXTERNAL_APPS_AND_REPOS_RESEARCH_PLAN.md
- CODE_AUDIT.md template or first real CODE_AUDIT.md
- STATUS.md template or first real STATUS.md
- DATASET_MANIFEST.md or explicit task to create it from Apple Photos index
- BENCHMARK_PROTOCOL.md or explicit task to run it

At that point the next work is implementation, not more abstract planning.
