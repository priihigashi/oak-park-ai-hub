---
description: Specification and construction administration: meeting minutes (RIBA stage 0, 1, 2, 3, 4, 5, 6; ceiling A3). A gated pipeline run with checker check_minutes.
argument-hint: [autonomy A0-A3] [notes]
---

You are running the **meeting-minutes** task of the Junior Architect Pipeline. Engage the `records-and-correspondence` and `jap-core` skills, and delegate the work to the **document-controller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start meeting-minutes <level>`. The level is the one in the arguments, or the ceiling A3, and never above it.
2. **Inputs.** Confirm you have the meeting transcript or notes (transcript.txt). If anything is missing, ask the junior.
3. **The junior first.** At A3 no prediction is required. If the junior runs it at A1 or A2, ask them: **Flag every decision that changes scope, cost or programme.**
4. **The work.** The document-controller agent produces `.jap/runs/<run>/minutes.md`. Hosts: none (document task). Watch for: decision attributed to the wrong person; action without owner or date; quote not in the transcript.
5. **The check.** Run `check <run>/minutes.md transcript.txt` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
