#!/usr/bin/env node
/**
 * Junior Architect Pipeline. Copyright (c) 2026 Abhinav Bhardwaj. MIT licence.
 * Junior Architect Pipeline: gates (Claude Code hooks).
 *   node gate.js pre   PreToolUse  (Write | Edit | MultiEdit | mcp__.*)
 *   node gate.js stop  Stop
 *
 * PreToolUse exit code 2 blocks the tool call and shows stderr to Claude.
 * Stop prints {"decision":"block","reason":...} to keep Claude working until the checker has run.
 * The gates only act in projects that have a .jap/ folder, and only while a run is open (except G1 and G2).
 */
"use strict";
const fs = require("fs");
const path = require("path");

const mode = process.argv[2];
let input = {};
try { input = JSON.parse(fs.readFileSync(0, "utf8") || "{}"); } catch { process.exit(0); }

const cwd = input.cwd || process.cwd();
const jap = path.join(cwd, ".jap");
if (!fs.existsSync(jap)) process.exit(0);

const PLUGIN = path.resolve(__dirname, "..");
const CLI = `node "${path.join(PLUGIN, "scripts", "jap.js")}"`;
const state = fs.existsSync(path.join(jap, "state.json")) ? JSON.parse(fs.readFileSync(path.join(jap, "state.json"), "utf8")) : null;
const block = (msg) => { process.stderr.write(msg + "\n"); process.exit(2); };

if (mode === "pre") {
  const tool = input.tool_name || "";
  const ti = input.tool_input || {};
  const file = ti.file_path ? path.resolve(cwd, ti.file_path) : "";
  const rel = file ? path.relative(cwd, file).split(path.sep).join("/") : "";

  // G1 via the shell: Claude cannot record the junior's prediction or review through the CLI either.
  // (The junior's own `! node ... predict` runs outside Claude's tools, so hooks do not see it.)
  if (tool === "Bash" && /jap\.js["']?\s+(predict|review)\b/.test(ti.command || ""))
    block("Blocked by the Junior Architect Pipeline: predictions and reviews are recorded by the junior, not by Claude. " +
          `Ask the junior to type: ! ${CLI} predict "<their own words>"`);
  if (tool === "Bash" && /\.jap[\\/](runs[\\/][^ ]*[\\/](report|run|prediction|review)\.|state\.json|learning_log\.csv)/.test(ti.command || "") && />|tee|cp |mv |rm |sed -i|Set-Content|Out-File/.test(ti.command || ""))
    block("Blocked: pipeline evidence files are written only by the pipeline CLI.");

  if (/^(Write|Edit|MultiEdit)$/.test(tool) && file) {
    // G1: the junior's judgement is the junior's. Claude cannot write the prediction or the review.
    if (/^\.jap\/runs\/[^/]+\/(prediction|review)\.md$/.test(rel))
      block(`Blocked by the Junior Architect Pipeline: ${path.basename(rel)} is written by the junior, not by Claude. ` +
            `Ask the junior to run: ! ${CLI} ${rel.endsWith("prediction.md") ? "predict" : "review"} "<their own words>"`);
    // G2: evidence is produced by the checker only.
    if (/^\.jap\/(runs\/[^/]+\/(report|run)\.json|state\.json|learning_log\.csv)$/.test(rel))
      block(`Blocked: ${rel} is written only by the pipeline scripts. Run ${CLI} check ... to produce a report.`);
    if (file.startsWith(PLUGIN + path.sep)) block("Blocked: the pipeline's checkers and gates are read-only during a run.");
  }

  // G3: prediction first. At A1 and A2 nothing touches the model or the deliverable before the junior has predicted.
  if (state && state.needs_prediction) {
    const runDir = path.join(jap, "runs", state.run);
    const predicted = fs.existsSync(path.join(runDir, "prediction.md"));
    const touchesWork = tool.startsWith("mcp__") || (/^(Write|Edit|MultiEdit)$/.test(tool) && rel.startsWith(`.jap/runs/${state.run}/`));
    if (touchesWork && !predicted)
      block(`Prediction first (${state.task}, ${state.autonomy}). The junior records a prediction before the agent works: ` +
            `! ${CLI} predict "<estimate>". Then retry.`);
  }
  process.exit(0);
}

if (mode === "stop") {
  if (!state || input.stop_hook_active) process.exit(0);
  const runDir = path.join(jap, "runs", state.run);
  const deliverable = fs.existsSync(path.join(runDir, state.deliverable));
  const report = fs.existsSync(path.join(runDir, "report.json"));
  // G4: no deliverable leaves without a checker report.
  if (deliverable && !report) {
    process.stdout.write(JSON.stringify({ decision: "block", reason:
      `The ${state.task} deliverable exists but the checker has not run. Run ${CLI} check <inputs> and report every error to the junior. ` +
      `Never present a number the checker has not confirmed.` }));
  }
  process.exit(0);
}
process.exit(0);
