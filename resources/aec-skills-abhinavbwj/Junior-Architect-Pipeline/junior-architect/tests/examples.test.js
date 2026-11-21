#!/usr/bin/env node
/**
 * Junior Architect Pipeline. Copyright (c) 2026 Abhinav Bhardwaj. MIT licence.
 * Runs every checker on the seeded-fault examples and asserts exactly which faults are reported.
 *   node tests/examples.test.js
 * Uses a temporary project folder; the examples are never modified.
 */
"use strict";
const fs = require("fs"), os = require("os"), path = require("path");
const { execFileSync } = require("child_process");

const PLUGIN = path.resolve(__dirname, "..");
const JAP = path.join(PLUGIN, "scripts", "jap.js");
const dir = fs.mkdtempSync(path.join(os.tmpdir(), "jap-test-"));
fs.cpSync(path.join(PLUGIN, "examples"), dir, { recursive: true });
const env = { ...process.env, JAP_PROJECT: dir };
const jap = (...a) => { try { return execFileSync("node", [JAP, ...a], { cwd: dir, env, encoding: "utf8" }); } catch (e) { return (e.stdout || "") + (e.stderr || ""); } };

jap("init");
// project settings the examples are written against
const pj = path.join(dir, ".jap", "project.json");
const proj = JSON.parse(fs.readFileSync(pj, "utf8"));
proj.view_requirements.levels = ["Level 00", "Level 01"];
proj.ifc_schema = "IFC4X3";
fs.writeFileSync(pj, JSON.stringify(proj, null, 2));

const CASES = [
  ["area-schedule", ["area-schedule/rooms.json", "area-schedule/targets.csv"], ["unit-trap", "open-boundary", "duplicate", "wrong-layer", "name-typo", "arcs", "nested", "area-definition", "no-target", "deviation"]],
  ["door-schedule", ["door-schedule/door_schedule.csv", "door-schedule/model_doors.json", "doors"], ["duplicate-mark", "missing-in-schedule", "missing-in-model", "empty-field", "value-mismatch"]],
  ["code-research", ["code-research/code_notes.md", "code-research/code_text.txt"], ["quote-not-in-code", "missing-field"]],
  ["drawing-qa", ["drawing-qa/sheets.csv"], ["dead-reference", "self-checked", "empty-field", "status-code", "naming"]],
  ["meeting-minutes", ["meeting-minutes/minutes.md", "meeting-minutes/transcript.txt"], ["no-owner", "no-date"]],
  ["brief-digest", ["brief-digest/brief_digest.md", "brief-digest/brief.txt"], ["quote-not-in-source", "untraced"]],
  ["spec-section", ["spec-section/spec_section.md", "spec-section/standards_register.csv", "spec-section/ironmongery.csv"], ["standard-unknown", "product-orphan"]],
  ["rfi-response", ["rfi-response/rfi_response.md", "drawing-qa/sheets.csv"], ["superseded", "dead-reference", "commitment"]],
  ["stairs-and-cores", ["stairs/stairs.json"], ["blondel", "riser", "going", "width", "headroom", "flight", "total-rise", "uneven-risers", "pitch"]],
  ["facade-and-curtain-wall", ["facade/panels.json"], ["not-planar", "too-wide", "sliver", "no-stock"]],
  ["grasshopper-definition", ["grasshopper/gh_export.json"], ["runtime-error", "runtime-warning", "unconnected", "unnamed-slider", "internalised"]],
  ["view-set", ["views/views.json"], ["missing-plan", "few-sections", "few-elevations", "default-name", "no-template", "scale", "duplicate-name", "not-on-sheet"]],
  ["annotation", ["annotation/annotation.json"], ["untagged", "no-dimensions", "overlap"]],
  ["rhino-2d-drawings", ["dxf/drawing.dxf"], ["units", "layer-name", "empty-layer", "layer-0", "text-height"]],
  ["ifc-export", ["ifc/model.ifc", "ifc/expected_counts.json"], ["schema", "count", "proxies", "storey", "space-name"]],
  ["quantity-takeoff", ["quantities/takeoff.csv", "402.10"], ["unit", "no-unit", "quantity", "duplicate"]],
  ["sun-shadow-study", ["render/renders.json"], ["eye-level", "lens", "sun-position", "projection", "missing", "resolution"]],
  ["presentation-board", ["board/board.json"], ["source", "scale-bar", "north", "text-size"]],
  ["clash-detection", ["clash/clashes.json"], ["unassigned", "approval"]],
  ["massing-study", ["massing/massing_metrics.json", "massing/massing_rules.json"], ["rule-failed", "unsourced-rule"]],
];

let fail = 0;
for (const [task, inputs, expect] of CASES) {
  fs.rmSync(path.join(dir, ".jap", "state.json"), { force: true });
  jap("start", task, "A3");
  jap("check", ...inputs);
  const st = JSON.parse(fs.readFileSync(path.join(dir, ".jap", "state.json"), "utf8"));
  const rep = JSON.parse(fs.readFileSync(path.join(dir, ".jap", "runs", st.run, "report.json"), "utf8"));
  const got = new Set(rep.issues.map((i) => i.code));
  const missing = expect.filter((c) => !got.has(c));
  const extra = [...got].filter((c) => !expect.includes(c));
  const ok = !missing.length && rep.status === "fail";
  if (!ok) fail++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${task.padEnd(24)} ${rep.checker.padEnd(16)} ${rep.errors} errors ${rep.warnings} warnings` +
    (missing.length ? `  missing: ${missing.join(", ")}` : "") + (extra.length ? `  also: ${extra.join(", ")}` : ""));
}
fs.rmSync(dir, { recursive: true, force: true });
console.log(fail ? `\n${fail} case(s) failed` : `\nall ${CASES.length} cases passed`);
process.exit(fail ? 1 : 0);
