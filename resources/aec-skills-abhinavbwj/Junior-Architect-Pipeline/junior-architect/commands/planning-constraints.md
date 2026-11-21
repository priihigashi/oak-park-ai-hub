---
description: Regulation and envelope: planning constraints (RIBA stage 1, 2; ceiling A1). A gated pipeline run with checker check_clauses.
argument-hint: [autonomy A0-A1] [notes]
---

You are running the **planning-constraints** task of the Junior Architect Pipeline. Engage the `code-research` and `jap-core` skills, and delegate the work to the **code-researcher** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start planning-constraints <level>`. The level is the one in the arguments, or the ceiling A1, and never above it.
2. **Inputs.** Confirm you have the parcel and the zoning and planning documents as plain text (codes/*.txt). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Sketch the buildable envelope by hand first; compare it with the agent's envelope.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The code-researcher agent produces `.jap/runs/<run>/planning_constraints.md`. Hosts: none (document task). Watch for: missed overlay or conservation designation; height measured from the wrong datum; setback applied to the wrong boundary.
5. **The check.** Run `check <run>/planning_constraints.md codes/<document>.txt` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
