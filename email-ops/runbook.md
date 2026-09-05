# email-ops/runbook.md — Operational Procedures
# Account: priscila@oakpark-construction.com
# Created: 2026-07-26 by Daily Advancer
# Source: EMAIL_OPS_MASTER_PLAN v5 + OPERATOR.md

---

## 1. Morning inbox zero (~5–10 min)

**Start every session with an audit before touching anything.**

1. Run `audit` mode: count threads, categorize, flag uncertain ones.
2. Process **⚡ Action Items** — do items that take <5 min now; archive on completion.
3. Process **↩️ Needs Reply** — reply, then move to **⏳ Waiting** + archive.
4. Any item that takes >5 min → log ONE task in Focus Pending, verify the write, then archive the email.
5. Label + archive everything else per `filters.yaml` rules.
6. Target: 0–10 threads remaining (hard cap: 30).

**Modes:**
- `audit` — read-only report. Always start here.
- `morning-zero` — apply safe archiving rules (automation noise only) + surface uncertain threads.
- `apply-approved` — execute only changes approved in a prior review run. Never skip to this.

---

## 2. Adding a new Gmail filter

1. Identify the exact from-address + subject pattern by reading a real thread (not a snippet).
2. Check `email-ops/protected-senders.yaml` — if the sender is listed, STOP. No filter.
3. Check `email-ops/pipelines.yaml` — confirm which pipeline sends these emails and that it's safe to filter.
4. Add the filter definition to `email-ops/filters.yaml` with status `pre_approved_with_verification`.
5. Test: run `audit` on a thread matching the pattern to confirm before applying.
6. Apply via `apply-approved` mode.
7. Update `email-ops/change-log.md` with date + description.

---

## 3. Adding a new pipeline to the email map

1. Read the workflow YAML source in `.github/workflows/` to find every `send_email.yml` dispatch call and its subject.
2. Add the pipeline entry to `email-ops/pipelines.yaml` under the correct section.
3. If the pipeline's emails need a filter, add it to `email-ops/filters.yaml`.
4. Check `pipeline-control/pipelines.yaml` for the pipeline's WP-0 status and pause recommendation.
5. Update `email-ops/change-log.md`.

---

## 4. Handling a repeat pipeline failure email

**Only the FIRST occurrence creates a task. Repeats get archived.**

1. Check Focus Pending — does an open task for this failure already exist?
   - YES → Read the new email for any new information. Add a note if useful. Archive the email. Do not create a second task.
   - NO → Create one Focus Pending task. Apply label **⚡ Action Items**. Keep the email visible until the Focus write is verified.
2. If the failure is from a pipeline flagged `ACTIVE_RECOMMENDED_PAUSE` in `pipeline-control/pipelines.yaml` → add to the existing WP-0 follow-up task, do not open a new task.

---

## 5. Weekly ⏳ Waiting sweep

1. List all threads labeled **⏳ Waiting**.
2. For each: check if the awaited action has happened.
   - Resolved → archive and close the task in Focus.
   - Still waiting → leave as-is or nudge if overdue.
   - Dropped → archive + mark task Done with note "dropped / not actioned".

---

## 6. Never-do list

- Never apply `apply-approved` mode without a prior explicit approval in the current session.
- Never add Anthropic credits or enable any paused workflow — see `pipeline-control/pipelines.yaml` WP-0 rules.
- Never create a Gmail filter for a sender listed in `protected-senders.yaml`.
- Never log a task from: reports, receipts, confirmations, promos, duplicate emails about known issues.
- Never delete any email (archive only).
- Never trigger capture or content pipelines as part of inbox cleanup.

---

## 7. Escalation: something doesn't fit the rules

If a thread doesn't clearly match any category:
- Default to **keep in inbox** and flag for Priscila in the audit report.
- If a Focus write fails, keep the email visibly labeled, report the failure and do not substitute an Inbox task.
- State exactly: what the email is, why it's uncertain, and the two most likely actions.
- Do NOT archive uncertain threads during `morning-zero` — only automation-noise threads are safe to auto-archive.

---

## 8. References

| Resource | Path / ID |
|---|---|
| AI instructions (this system) | `email-ops/OPERATOR.md` |
| Inbox policy (structured) | `email-ops/inbox-policy.yaml` |
| Pre-approved filters | `email-ops/filters.yaml` |
| Task routing rules | `email-ops/task-routing.yaml` |
| Pipeline email map | `email-ops/pipelines.yaml` |
| Protected senders | `email-ops/protected-senders.yaml` |
| Label IDs | `email-ops/labels.yaml` (resolve at runtime) |
| This runbook | `email-ops/runbook.md` |
| Change log | `email-ops/change-log.md` |
| Master pipeline registry (LLM costs) | `pipeline-control/pipelines.yaml` |
| Human-readable master plan | Drive doc `1lf0NJQlkFhHDZb5ldr0YVGKgBdFXj5L2T3MCo23dlds` |
| Task destination sheet | Spreadsheet `1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c`, tab Pending |
