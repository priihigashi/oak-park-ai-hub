---
description: 3D modelling, BIM and Grasshopper: massing study (RIBA stage 2; ceiling A2). A gated pipeline run with checker check_metrics.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **massing-study** task of the Junior Architect Pipeline. Engage the `massing-and-envelope` and `jap-core` skills, and delegate the work to the **rhino-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start massing-study <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the brief areas, the buildable envelope and the site model; massing_rules.json (GFA target, height, coverage, FAR, sun to the court). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Sketch two alternative massings by hand and predict which meets the brief with more daylight.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The rhino-modeller agent produces `.jap/runs/<run>/massing_metrics.json`. Hosts: Rhino, Revit. Capabilities needed: create and extrude footprints; boolean solids; slice masses into floors; measure floor areas and heights; save named views; capture a viewport. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: options that differ only in form, not in strategy; GFA counted to the wrong standard; massing exceeds the envelope; triangular or token forms with no reasoning about access and circulation.
5. **The check.** Run `check <run>/massing_metrics.json <run>/massing_rules.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
