# email-ops/change-log.md
# Account: priscila@oakpark-construction.com
# Format: date | author | change description

---

- **2026-07-29** — Routing corrected: actionable email work now goes to Focus → Pending; Calendar is only a genuine date/appointment reminder; Ideas & Inbox is reserved for content references/someday ideas. A failed Focus write keeps the email visibly labeled and is reported—never silently rerouted to Inbox.

- **2026-07-26** — Daily Advancer (automated): created `task-routing.yaml` (when to create tasks vs archive, dedup rules, routing to ⚡/↩️/⏳), `pipelines.yaml` (pipeline → email subject map for all 15 workflows; flags unconfirmed email outputs), `runbook.md` (8-procedure operational guide covering morning routine, filter additions, pipeline mapping, repeat failure handling, weekly sweep, escalation), and this `change-log.md`. All 4 files referenced in OPERATOR.md Architecture table but missing from repo. WP-3 scaffold now complete.

- **2026-07-25** — Claude Code (manual session): created initial repo scaffold — OPERATOR.md, inbox-policy.yaml, filters.yaml, labels.yaml, protected-senders.yaml. Transcribed from EMAIL_OPS_MASTER_PLAN v5 (Drive `1lf0NJQlkFhHDZb5ldr0YVGKgBdFXj5L2T3MCo23dlds`). WP-3 kickoff.

- **2026-07-23** — Daily Advancer (automated): created `pipeline-control/pipelines.yaml` — master API budget registry for all 15 workflows. WP-0 completed (cron dedup + 4AM dispatch gate). WP-1 done.
