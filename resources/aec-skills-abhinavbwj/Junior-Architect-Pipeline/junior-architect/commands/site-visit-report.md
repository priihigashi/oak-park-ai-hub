---
description: Specification and construction administration: site visit report (RIBA stage 5, 6; ceiling A2). A gated pipeline run with checker check_minutes.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **site-visit-report** task of the Junior Architect Pipeline. Engage the `construction-admin` and `jap-core` skills, and delegate the work to the **document-controller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start site-visit-report <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have site photos and notes (site_notes.txt). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Write your three observations first; then compare with the agent's report of the photos and notes.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The document-controller agent produces `.jap/runs/<run>/site_visit_report.md`. Hosts: none (document task). Watch for: observation without a location; defect without an owner or date; photo misattributed.
5. **The check.** Run `check <run>/site_visit_report.md site_notes.txt` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
