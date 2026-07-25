# Oak Park Inbox Operator — Instructions for Any AI Session

**Canonical source:** `email-ops/OPERATOR.md` in `priihigashi/oak-park-ai-hub`
**Human-readable master plan:** Google Drive doc `1lf0NJQlkFhHDZb5ldr0YVGKgBdFXj5L2T3MCo23dlds`
**Account:** priscila@oakpark-construction.com
**Created:** 2026-07-23 · **Transcribed to repo:** 2026-07-25

---

## Goal
Inbox at **0–10 threads** after morning check (hard cap 30). Remote-first — nothing depends on the Mac being awake.

---

## Mode selector (default: audit)

| Mode | What it does |
|---|---|
| `audit` | Read + report only. No changes. Output: inbox count, category breakdown, flagged threads. **DEFAULT — always start here.** |
| `review` | Audit + recommendations. Propose filter changes, label assignments, and task candidates. No writes. |
| `apply-approved` | Execute only changes that were explicitly approved in a prior `review` run or pre-approved in this file. Write labels, create filters, archive. |
| `morning-zero` | Apply safe archiving rules (automation noise) + surface uncertain threads for Priscila to decide. Never touches human mail or protected senders. |

**When in doubt, run `audit` first. Never execute `apply-approved` without a prior explicit approval.**

---

## The inbox rule

A thread **stays in the inbox** only if:
- A human needs a reply from Priscila
- A concrete action is required from Priscila (not delegatable to automation)
- It's a new lead or active client thread
- A NEW, unresolved system failure (not a repeat of a known issue)
- A security / billing / deadline item that needs verification

**Everything else: label + archive. Never delete.**

---

## Workflow labels (3 only)

| Label | Gmail ID | Purpose | Inbox? |
|---|---|---|---|
| ⚡ Action Items | (resolve at runtime) | Priscila must act | Stays temporarily |
| ↩️ Needs Reply | (resolve at runtime — create if missing) | Human awaiting reply | Stays temporarily |
| ⏳ Waiting | (resolve at runtime — create if missing) | Priscila acted, waiting on others | ARCHIVED — review weekly |

Category labels (Ads, Kids, docs, etc.) stay as-is. Do not rename or consolidate them — pipeline scripts reference current label names and must be updated in the same change.

---

## Pre-approved Gmail filters (safe to apply in `apply-approved` / `morning-zero`)

Each filter: skip inbox + apply label + mark read (unless noted).

| # | Matches | Action |
|---|---|---|
| 1 | Subject contains `QUOTA_EXCEEDED` from priscila's own automation | Label: 🚨 Automation Errors |
| 2 | Subject contains `Quota RESOLVED` from own automation | Label: 🚨 Automation Errors |
| 3 | From `mail.anthropic.com` — billing / access | **STAY IN INBOX — do not archive** |
| 4 | Subject contains `Focus audit` with no-change body | Label: Reports |
| 5 | Mac-restart repeat failures | Label: 🚨 Automation Errors (activate ONLY after a task is logged) |
| 6 | From `mcfollingproperties@gmail.com` with subject `Calendar Optimized` OR `Daily Advancer` | Label: 🤖 Automation/Daily Digests |
| 7 | Subject contains `Weekly Pipeline Report` OR `Inspiration Library` | Label: Reports (OPC Ads Weekly stays in inbox until reviewed, then archive same morning) |
| 8 | From Thumbtack promo senders | Label: THUMBTACK (verify real pro replies are not matched) |
| 9 | From `analytics-noreply@` or Reader Revenue onboarding | Label: 🔬 Promos & News (Google Pay / security mail NOT in this filter) |
| 10 | Approval reminder automation | Label: 🤖 Automation/Pending Approval — archive once the one project-level task is logged |

**Before applying any filter: verify the exact from/subject match against a real thread. A wrong filter can hide real mail.**

---

## Never auto-archive (protected categories)

Read `protected-senders.yaml` for the current list. Summary:
- Official Anthropic account mail (billing, access, security)
- Security or account-change notices from any provider
- Legal documents
- Active leads and active client threads
- Unknown senders with attachments
- Medical / school threads that are unresolved
- OPC Ads Weekly (until Priscila reviews it)

---

## Task rules

- One unresolved issue = **one task row**, regardless of how many emails reference it.
- Tasks go to the **📥 Inbox tab** of Ideas & Inbox spreadsheet (`1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU`).
- Calendar events: ONLY for real dates / appointments — never for reports, receipts, or promos.
- No tasks from: reports, receipts, confirmations, promos, duplicates.
- Read every candidate thread IN FULL before logging a task. Summaries are not enough.

---

## Morning routine (steady-state, 3–6 real emails/day)

1. ⚡ **Action Items**: do items that take <5 min now; archive on completion.
2. ↩️ **Needs Reply**: reply, move awaited-reply threads to ⏳ Waiting + archive.
3. **Over-5-min work** → one Inbox-tab row, archive the email.
4. **Weekly sweep**: ⏳ Waiting label — follow up or close.
5. **Label + archive** leftovers → target 0–10.

---

## Source-side fixes (automation reliability — WP-B)

These are PLANNED fixes to stop noise at the source. Do not skip this list when auditing pipelines.

1. Investigate `ads_pulse.yml` failed run `29748026426` and `approval_check.yml` failures (Jul 5–6); green badge ≠ no errors — grep logs.
2. Reconcile 🚨 Pipeline Failures tab (sheetId `448272280`) — close unresolved rows.
3. Quota/credit alert scripts → state machine (healthy/degraded/blocked/resolved); email ONLY on state CHANGE; every `catch` calls `log_pipeline_failure()` + non-zero exit.
4. Approval reminder → adaptive prioritized daily batch (~5) + backlog pruning (expired news, duplicates, outdated facts).
5. Fix or remove bounced `vtext.com` SMS route (AUP POL rejection).
6. Local Mac scripts: 5AM restart → alert once + weekly re-alert; 3AM Focus → exception-only + weekly summary.

---

## What only Priscila can do (Mac-only / account-only)

- **Anthropic API — DO NOT top up credits yet.** See `pipeline-control/pipelines.yaml` WP-0 remaining actions. Review actual usage first at `console.anthropic.com/settings/usage`, then disable the 5 ACTIVE_RECOMMENDED_PAUSE workflows, add budget limits, and add a global kill switch — BEFORE any credits are added. Auto-reload must stay OFF.
- Mac admin password (5AM restart job)
- yt-dlp cookies refresh (recurring ~bi-weekly)
- Healthcare.gov plan selection
- Call Paula Feghhi (Portuguese tutor) 650-804-3321
- Step Up For Students email verification mismatch

These items go to ⚡ Action Items and stay in the inbox until done. Never archive them prematurely.

## Pipeline-control rules (from pipeline-control/pipelines.yaml)

The Inbox Operator MUST also enforce these rules. Read `pipeline-control/pipelines.yaml` at the start of any pipeline-related task.

- NEVER enable a paused workflow without WP-0 complete + Priscila sign-off
- NEVER add Anthropic credits or enable auto-reload until after WP-3 (inbox operator = this build)
- NEVER assume a green last-run badge means no model call — check `dispatch_chain`
- NEVER trigger capture/content pipelines as part of inbox cleanup (separate command scopes)
- Inbox triage runs in no-paid-Anthropic mode (labels/archive need no API credits)
- Flag any workflow with `wp0_status: ACTIVE_RECOMMENDED_PAUSE` in every session report

---

## Architecture (for builder sessions)

| Component | Location |
|---|---|
| This file (AI instructions) | `email-ops/OPERATOR.md` |
| Inbox policy (structured) | `email-ops/inbox-policy.yaml` |
| Protected senders | `email-ops/protected-senders.yaml` |
| Label ID map | `email-ops/labels.yaml` (IDs resolved dynamically at runtime) |
| Filter definitions | `email-ops/filters.yaml` |
| Task routing rules | `email-ops/task-routing.yaml` |
| Pipeline → email map | `email-ops/pipelines.yaml` (verify before editing any pipeline) |
| Runbook | `email-ops/runbook.md` |
| Change log | `email-ops/change-log.md` |
| GitHub Actions workflow | `.github/workflows/email_triage.yml` (dry-run default; restricted secrets) |
| ALL pipeline registry + budgets + WP-0 | `pipeline-control/pipelines.yaml` (read this before any pipeline action) |

**Key label IDs (from Addendum v7):** ↩️ Needs Reply = `Label_32` · ⏳ Waiting = `Label_31` · both already exist.

**Claude Code** = builder + `/email-triage` skill (reads repo rules each run, never from chat memory).
**ChatGPT** = interactive reviewer via Project "Oak Park Inbox Operations" holding the same docs.
**Both** call the same GitHub workflows. Mac-only operations stay explicitly marked "Only-you."

---

## Changelog

- 2026-07-25: created from EMAIL_OPS_MASTER_PLAN v5 (Drive doc `1lf0NJQlkFhHDZb5ldr0YVGKgBdFXj5L2T3MCo23dlds`). WP-C kickoff — repo directory created, core operator instructions transcribed.
