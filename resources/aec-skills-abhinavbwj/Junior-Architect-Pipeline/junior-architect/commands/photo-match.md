---
description: Visualisation and presentation: photo match (RIBA stage 2, 3; ceiling A2). A gated pipeline run with checker check_metrics.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **photo-match** task of the Junior Architect Pipeline. Engage the `visualisation` and `jap-core` skills, and delegate the work to the **visualiser** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start photo-match <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have a site photograph with its camera position if known, and the model. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Mark three fixed points in the photo (a corner, a kerb, a roofline) that the model must line up with.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The visualiser agent produces `.jap/runs/<run>/match_metrics.json`. Hosts: Rhino, Revit. Capabilities needed: place a reference image; match the camera to a photograph; compare a capture with the photograph. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: camera matched by eye only; lens of the photo unknown; verified view not reproducible.
5. **The check.** Run `check <run>/match_metrics.json <run>/match_rules.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
