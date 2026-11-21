---
description: Brief and site: brief digest (RIBA stage 0, 1; ceiling A2). A gated pipeline run with checker check_trace.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **brief-digest** task of the Junior Architect Pipeline. Engage the `brief-and-site` and `jap-core` skills, and delegate the work to the **brief-analyst** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start brief-digest <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the client brief as plain text (brief.txt, extracted from the PDF). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Before reading the digest, rank the three requirements that will drive the plan and say why.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The brief-analyst agent produces `.jap/runs/<run>/brief_digest.md`. Hosts: none (document task). Watch for: dropped requirement; invented requirement; requirement paraphrased into a different meaning.
5. **The check.** Run `check <run>/brief_digest.md brief.txt` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
