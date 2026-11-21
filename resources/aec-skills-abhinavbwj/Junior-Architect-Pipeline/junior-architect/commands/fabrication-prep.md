---
description: 3D modelling, BIM and Grasshopper: fabrication prep (RIBA stage 4, 5; ceiling A2). A gated pipeline run with checker check_panels.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **fabrication-prep** task of the Junior Architect Pipeline. Engage the `facades-and-panels` and `jap-core` skills, and delegate the work to the **rhino-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start fabrication-prep <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the element to fabricate and the stock sheet sizes in project.json fabrication.stock. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Predict how many parts and sheets the element needs.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The rhino-modeller agent produces `.jap/runs/<run>/parts.json`. Hosts: Rhino. Capabilities needed: unroll developable surfaces; contour and section; label parts with text; measure parts; export cutting files. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: parts larger than the stock sheet; unlabelled parts; double-curved surfaces unrolled with distortion.
5. **The check.** Run `check <run>/parts.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
