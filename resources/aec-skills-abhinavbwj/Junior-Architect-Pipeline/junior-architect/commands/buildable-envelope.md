---
description: Regulation and envelope: buildable envelope (RIBA stage 2; ceiling A2). A gated pipeline run with checker check_metrics.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **buildable-envelope** task of the Junior Architect Pipeline. Engage the `massing-and-envelope` and `jap-core` skills, and delegate the work to the **bim-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start buildable-envelope <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the verified planning constraints (planning_constraints.md, checked) turned into envelope_rules.json with a source per rule. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Predict the maximum gross floor area the envelope allows before the model computes it.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The bim-modeller agent produces `.jap/runs/<run>/envelope_metrics.json`. Hosts: Rhino, Revit. Capabilities needed: offset and extrude boundary curves; boolean solids; cut solids with planes (height and angle planes); measure volumes and floor areas; capture a viewport. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: rule entered without a source clause; height plane from the wrong datum; envelope ignores daylight or angle planes; setback from kerb instead of boundary.
5. **The check.** Run `check <run>/envelope_metrics.json <run>/envelope_rules.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
