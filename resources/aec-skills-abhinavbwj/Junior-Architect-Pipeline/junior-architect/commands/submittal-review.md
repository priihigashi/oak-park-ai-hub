---
description: Specification and construction administration: submittal review (RIBA stage 5; ceiling A1). A gated pipeline run with checker check_refs.
argument-hint: [autonomy A0-A1] [notes]
---

You are running the **submittal-review** task of the Junior Architect Pipeline. Engage the `construction-admin` and `jap-core` skills, and delegate the work to the **drawing-checker** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start submittal-review <level>`. The level is the one in the arguments, or the ceiling A1, and never above it.
2. **Inputs.** Confirm you have the submittal, the specification section and the current sheet register. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **List what you expect to be wrong in the submittal before the agent compares it with the specification.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The drawing-checker agent produces `.jap/runs/<run>/submittal_review.md`. Hosts: none (document task). Watch for: accepting a substitution silently; reviewing against a superseded specification; missing a performance requirement.
5. **The check.** Run `check <run>/submittal_review.md sheets.csv` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
