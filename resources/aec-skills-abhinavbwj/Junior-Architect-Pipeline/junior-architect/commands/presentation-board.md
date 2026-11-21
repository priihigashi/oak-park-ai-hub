---
description: Visualisation and presentation: presentation board (RIBA stage 2, 3, 4; ceiling A2). A gated pipeline run with checker check_board.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **presentation-board** task of the Junior Architect Pipeline. Engage the `visualisation` and `jap-core` skills, and delegate the work to the **visualiser** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start presentation-board <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the checked drawings and images, captions and sources; compose with scripts/board.js. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Lay out the board's reading order on paper: what a reviewer must see first, second, third.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The visualiser agent produces `.jap/runs/<run>/board.json`. Hosts: none (document task). Watch for: images without captions or sources; drawings without scale bars or north; text too small at print size.
5. **The check.** Run `check <run>/board.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
