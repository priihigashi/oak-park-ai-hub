#!/usr/bin/env node
/**
 * Junior Architect Pipeline. Copyright (c) 2026 Abhinav Bhardwaj. MIT licence.
 * Junior Architect Pipeline: SessionStart hook.
 * Tells Claude the pipeline is installed, where its CLI lives, and the open run (if any).
 */
"use strict";
const fs = require("fs");
const path = require("path");

let input = {};
try { input = JSON.parse(fs.readFileSync(0, "utf8") || "{}"); } catch {}
const cwd = input.cwd || process.cwd();
const cli = `node "${path.join(path.resolve(__dirname), "jap.js")}"`;
const board = `node "${path.join(path.resolve(__dirname), "board.js")}"`;
const stateFile = path.join(cwd, ".jap", "state.json");
const st = fs.existsSync(stateFile) ? JSON.parse(fs.readFileSync(stateFile, "utf8")) : null;

const note = [
  "The Junior Architect Pipeline plugin is active. It runs 45 junior-architect tasks as gated runs in eight families: brief and site; regulation and envelope; 3D modelling, BIM and Grasshopper; drafting and documentation; schedules and quantities; visualisation and presentation; analysis, coordination and exchange; specification and construction administration.",
  `Hosts: Rhino, Grasshopper, Revit and Blender through whichever MCP servers the user has connected (see the plugin's mcp/README.md). Each task in pipeline.json lists the capabilities it needs; use the connected server's tools that provide them, and if none is connected, work from exported files. Boards: ${board} <board.json>.`,
  `Pipeline CLI: ${cli} (init | start <task> [A0-A4] | check <inputs> | close | status | tasks | log). The junior records predictions and reviews with: ! ${cli} predict "..." and ! ${cli} review "...".`,
  "Rules: (1) start a run before doing a pipeline task; (2) at A1 and A2 wait for the junior's prediction; (3) recompute every number with the checker and never present an unchecked number; (4) never write prediction.md, review.md, report.json or the learning log (hooks block it); (5) code clauses are quoted verbatim with edition and jurisdiction, never paraphrased; (6) anything touching code compliance, fire, structure, contract or cost is escalated to a named senior.",
  st ? `Open run: ${st.run} (${st.task}, autonomy ${st.autonomy}).` : "No run is open in this project.",
  "For the task list and how to start: /junior-architect:help."
].join(" ");

process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: note } }));
