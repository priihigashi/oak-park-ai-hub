---
description: Regulation and envelope: code research (RIBA stage 1, 2, 3; ceiling A1). A gated pipeline run with checker check_clauses.
argument-hint: [autonomy A0-A1] [notes]
---

You are running the **code-research** task of the Junior Architect Pipeline. Engage the `code-research` and `jap-core` skills, and delegate the work to the **code-researcher** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start code-research <level>`. The level is the one in the arguments, or the ceiling A1, and never above it.
2. **Inputs.** Confirm you have the question and the code documents in force as plain text (codes/*.txt) with editions in project.json. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Predict the governing clause and its threshold before the search; explain any disagreement with the agent's result.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The code-researcher agent produces `.jap/runs/<run>/code_notes.md`. Hosts: none (document task). Watch for: fabricated clause; real but irrelevant clause; wrong edition or jurisdiction; paraphrase that changes a threshold.
5. **The check.** Run `check <run>/code_notes.md codes/<document>.txt` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
