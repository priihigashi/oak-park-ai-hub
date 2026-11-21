---
description: Brief and site: site model (RIBA stage 1, 2; ceiling A2). A gated pipeline run with checker check_metrics.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **site-model** task of the Junior Architect Pipeline. Engage the `site-modelling` and `jap-core` skills, and delegate the work to the **rhino-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start site-model <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the parcel boundary and survey or terrain source; site_rules.json with the surveyed parcel area, levels and north angle. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Write the parcel area, the level difference across the site and true north before the model is built.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The rhino-modeller agent produces `.jap/runs/<run>/site_metrics.json`. Hosts: Rhino, Revit. Capabilities needed: set document units; create layers to the office standard; import open map data (buildings, streets, parcels); build terrain from survey points or a terrain dataset; measure areas and elevations; capture a viewport. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: model not georeferenced; true north and project north confused; terrain from a coarse dataset presented as survey; parcel traced from the wrong source.
5. **The check.** Run `check <run>/site_metrics.json <run>/site_rules.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
