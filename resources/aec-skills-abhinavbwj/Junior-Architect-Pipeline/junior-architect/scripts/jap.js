#!/usr/bin/env node
/**
 * Junior Architect Pipeline. Copyright (c) 2026 Abhinav Bhardwaj. MIT licence.
 * Junior Architect Pipeline: state machine and deterministic checkers.
 * Node only, no dependencies (Node ships with Claude Code).
 *
 *   jap init                         create .jap/ in the project (project.json, runs/, learning_log.csv)
 *   jap start <task> [A0-A4]          open a run; autonomy is capped at the task's ceiling in pipeline.json
 *   jap predict "<text>"              the JUNIOR records a prediction (hooks stop Claude from writing it)
 *   jap check [inputs...]             run the active task's checker; writes report.json (only this writes it)
 *   jap review "<text>"               the JUNIOR records the review of the agent's output
 *   jap close                         close the run; appends to the learning log
 *   jap status | jap tasks | jap log  show state, the task map, the learning curve
 *
 * Every checker recomputes from raw data. None of them trusts a number the agent wrote.
 */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const PIPE = JSON.parse(fs.readFileSync(path.join(ROOT, "pipeline.json"), "utf8"));
const CWD = process.env.JAP_PROJECT || process.cwd();
const JAP = path.join(CWD, ".jap");
const STATE = path.join(JAP, "state.json");
const LEVELS = ["A0", "A1", "A2", "A3", "A4"];

// ---------- small helpers ----------
const die = (m) => { console.error("jap: " + m); process.exit(1); };
const readJSON = (p, d) => (fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : d);
const writeJSON = (p, o) => { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, JSON.stringify(o, null, 2) + "\n"); };
const readText = (p) => (fs.existsSync(p) ? fs.readFileSync(p, "utf8") : "");
const norm = (s) => String(s).toLowerCase().replace(/[‘’“”]/g, "'").replace(/["']/g, "").replace(/\s+/g, " ").trim();
const now = () => new Date().toISOString().replace(/\.\d+Z$/, "Z");

function csv(p) {
  const t = readText(p).replace(/^﻿/, "");
  if (!t.trim()) return [];
  const rows = [];
  for (const line of t.split(/\r?\n/)) {
    if (!line.trim()) continue;
    const out = []; let cur = "", q = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (c === '"') { if (q && line[i + 1] === '"') { cur += '"'; i++; } else q = !q; }
      else if (c === "," && !q) { out.push(cur); cur = ""; }
      else cur += c;
    }
    out.push(cur);
    rows.push(out.map((x) => x.trim()));
  }
  const head = rows.shift().map((h) => h.toLowerCase());
  return rows.map((r) => Object.fromEntries(head.map((h, i) => [h, r[i] ?? ""])));
}

function lev(a, b) {
  a = a.toLowerCase(); b = b.toLowerCase();
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++)
    for (let j = 1; j <= b.length; j++)
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return d[a.length][b.length];
}

function project() { return readJSON(path.join(JAP, "project.json"), null) || die("no .jap/project.json here; run `jap init` first"); }
function state() { return readJSON(STATE, null); }
function runDir(st) { return path.join(JAP, "runs", st.run); }

// ---------- geometry ----------
const UNIT_TO_M = { mm: 0.001, cm: 0.01, m: 1, ft: 0.3048, in: 0.0254 };
function shoelace(v) { let s = 0; for (let i = 0; i < v.length; i++) { const [x1, y1] = v[i], [x2, y2] = v[(i + 1) % v.length]; s += x1 * y2 - x2 * y1; } return Math.abs(s) / 2; }
function segX(p1, p2, p3, p4) {
  const o = (a, b, c) => Math.sign((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]));
  return o(p1, p2, p3) * o(p1, p2, p4) < 0 && o(p3, p4, p1) * o(p3, p4, p2) < 0;
}
function selfIntersects(v) {
  const n = v.length;
  for (let i = 0; i < n; i++) for (let j = i + 2; j < n; j++) {
    if (i === 0 && j === n - 1) continue;
    if (segX(v[i], v[(i + 1) % n], v[j], v[(j + 1) % n])) return true;
  }
  return false;
}
function inside(pt, poly) {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > pt[1]) !== (yj > pt[1]) && pt[0] < ((xj - xi) * (pt[1] - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
}

// ---------- checkers ----------
// Each returns {status, metrics, issues:[{level, code, item, detail}]}. level: error | warn.

function check_areas(proj, args) {
  const [roomsFile, targetsFile] = [args[0] || "rooms.json", args[1] || "targets.csv"];
  const rooms = readJSON(path.resolve(CWD, roomsFile), null) || die(`rooms file not found: ${roomsFile}`);
  const targets = csv(path.resolve(CWD, targetsFile));
  const tol = proj.area_tolerance_pct ?? 5, layer = proj.rooms_layer, defn = proj.area_definition;
  const issues = [], ok = [], skipped = new Set();
  const add = (level, code, item, detail) => issues.push({ level, code, item, detail });
  const polys = [];
  for (const r of rooms) {
    const id = r.number ? `${r.number} ${r.name}` : r.name;
    const u = r.units || proj.model_units || "m";
    if (!UNIT_TO_M[u]) { add("error", "units-unknown", id, `units '${u}'`); continue; }
    if (r.closed === false) { add("error", "open-boundary", id, "boundary curve is open: area undefined"); skipped.add(norm(r.name)); continue; }
    if (!Array.isArray(r.vertices) || r.vertices.length < 3) { add("error", "no-geometry", id, "fewer than 3 vertices"); continue; }
    const v = r.vertices.map(([x, y]) => [x * UNIT_TO_M[u], y * UNIT_TO_M[u]]);
    if (selfIntersects(v)) add("error", "self-intersection", id, "boundary crosses itself");
    if (layer && r.layer && r.layer !== layer) add("error", "wrong-layer", id, `on '${r.layer}', expected '${layer}'`);
    if (defn && r.boundary && r.boundary !== defn) add("error", "area-definition", id, `boundary drawn to '${r.boundary}', project measures '${defn}'`);
    if (r.has_arcs) add("warn", "arcs", id, "curved edges approximated by a polyline: area under-measured unless finely segmented");
    const a = shoelace(v);
    if (r.area_reported != null) {
      const rep = Number(r.area_reported), diff = Math.abs(rep - a) / Math.max(a, 1e-9);
      if (diff > 0.005) add("error", "reported-area", id, `reported ${rep.toFixed(2)} m², recomputed ${a.toFixed(2)} m²`);
    }
    if (u === "ft" && !proj.allow_imperial) add("warn", "imperial-source", id, "geometry arrived in feet (Revit stores length in feet internally); converted at the boundary");
    polys.push({ id, name: r.name, v, a });
  }
  // duplicates and nesting
  for (let i = 0; i < polys.length; i++) for (let j = i + 1; j < polys.length; j++) {
    const p = polys[i], q = polys[j];
    const same = Math.abs(p.a - q.a) / Math.max(p.a, 1e-9) < 0.001 && p.v.every((pt) => q.v.some((qt) => Math.hypot(pt[0] - qt[0], pt[1] - qt[1]) < 0.01));
    if (same) { add("error", "duplicate", `${p.id} / ${q.id}`, "same boundary drawn twice"); continue; }
    const [small, big] = p.a < q.a ? [p, q] : [q, p];
    if (small.v.every((pt) => inside(pt, big.v))) add("error", "nested", `${small.id} in ${big.id}`, "room lies inside another room: counted twice unless deducted");
  }
  // targets
  const tmap = new Map(targets.map((t) => [norm(t.room), Number(t.target_m2)]));
  const seen = new Set();
  let total = 0;
  for (const p of polys) {
    total += p.a;
    const key = norm(p.name);
    if (!tmap.has(key)) {
      const near = [...tmap.keys()].find((k) => lev(k, key) <= 2);
      add(near ? "error" : "warn", near ? "name-typo" : "no-target", p.id, near ? `no target for '${p.name}'; did you mean '${near}'?` : "room not in the brief");
      continue;
    }
    seen.add(key);
    const t = tmap.get(key), dev = ((p.a - t) / t) * 100;
    // Unit traps: an area off from its target by a units factor is a units error, whatever else it looks like.
    let trap = false;
    for (const [ratio, label] of [[10.7639, "ft² read as m²"], [1 / 10.7639, "m² read as ft²"], [1e6, "mm coordinates read as m"],
                                  [1e-6, "m coordinates read as mm"], [1 / 92903.04, "ft coordinates read as mm"], [92903.04, "mm coordinates read as ft"],
                                  [1 / 0.09290304, "ft coordinates read as m"], [0.09290304, "m coordinates read as ft"]]) {
      if (Math.abs(p.a / t / ratio - 1) < 0.08) { add("error", "unit-trap", p.id, `${p.a.toPrecision(4)} m² against ${t} m²: ratio ≈ ${ratio.toPrecision(4)}, ${label}`); trap = true; }
    }
    if (trap) continue;
    if (Math.abs(dev) > tol) add("error", "deviation", p.id, `${p.a.toFixed(2)} m² against ${t} m² target (${dev > 0 ? "+" : ""}${dev.toFixed(1)}%, tolerance ${tol}%)`);
    else ok.push(p.id);
  }
  for (const k of tmap.keys()) if (!seen.has(k) && !skipped.has(k) && !issues.some((i) => i.detail.includes(`'${k}'`))) add("error", "missing-room", k, "in the brief, not in the model");
  const tsum = [...tmap.values()].reduce((s, x) => s + x, 0);
  return { metrics: { rooms_in_model: rooms.length, rooms_measured: polys.length, total_m2: +total.toFixed(2), brief_total_m2: tsum, within_tolerance: ok.length }, issues };
}

function check_schedule(proj, args) {
  const [schedFile, modelFile, kind] = [args[0], args[1], args[2] || "doors"];
  if (!schedFile || !modelFile) die("usage: jap check <schedule.csv> <model_export.json> [doors|windows|rooms|audit]");
  const sched = csv(path.resolve(CWD, schedFile)), model = readJSON(path.resolve(CWD, modelFile), []);
  const req = (proj.required_fields || {})[kind] || [];
  const issues = []; const add = (l, c, i, d) => issues.push({ level: l, code: c, item: i, detail: d });
  const key = (r) => String(r.mark ?? r.number ?? r.id ?? "").trim();
  const counts = {};
  for (const r of sched) counts[key(r)] = (counts[key(r)] || 0) + 1;
  for (const [k, n] of Object.entries(counts)) if (n > 1) add("error", "duplicate-mark", k, `appears ${n} times in the schedule`);
  const m = new Map(model.map((e) => [key(e), e]));
  const s = new Map(sched.map((r) => [key(r), r]));
  for (const k of m.keys()) if (!s.has(k)) add("error", "missing-in-schedule", k, "in the model, not in the schedule");
  for (const k of s.keys()) if (!m.has(k)) add("error", "missing-in-model", k, "in the schedule, not in the model (stale schedule?)");
  for (const [k, r] of s) {
    for (const f of req) if (!String(r[f] ?? "").trim()) add("error", "empty-field", k, `required field '${f}' is empty`);
    const e = m.get(k); if (!e) continue;
    for (const [f, v] of Object.entries(e)) {
      if (f === "mark" || r[f] === undefined) continue;
      if (norm(r[f]) !== norm(v)) add("error", "value-mismatch", k, `${f}: schedule '${r[f]}', model '${v}'`);
    }
  }
  if (kind === "audit") for (const e of model) for (const flag of e.problems || []) add("error", "model-health", key(e), flag);
  return { metrics: { schedule_rows: sched.length, model_elements: model.length }, issues };
}

function quotes(text) { return [...text.matchAll(/"([^"\n]{12,})"|“([^”\n]{12,})”/g)].map((m) => m[1] || m[2]); }

function check_trace(proj, args) {
  const [docFile, sourceFile] = [args[0], args[1]];
  if (!docFile || !sourceFile) die("usage: jap check <digest.md> <source.txt>   (source = the brief or site text)");
  const doc = readText(path.resolve(CWD, docFile)), src = norm(readText(path.resolve(CWD, sourceFile)));
  const issues = []; let traced = 0, reqs = 0;
  const sec = doc.split(/\n(?=## )/).find((s) => /^## Requirements/i.test(s)) || doc;
  for (const line of sec.split("\n").filter((l) => /^\s*[-*] /.test(l))) {
    reqs++;
    const qs = quotes(line);
    if (!qs.length) { issues.push({ level: "error", code: "untraced", item: line.trim().slice(0, 80), detail: "requirement has no verbatim quote from the source" }); continue; }
    const bad = qs.filter((q) => !src.includes(norm(q)));
    if (bad.length) issues.push({ level: "error", code: "quote-not-in-source", item: line.trim().slice(0, 80), detail: `quote not found verbatim: "${bad[0].slice(0, 60)}"` });
    else traced++;
  }
  return { metrics: { requirements: reqs, traced }, issues };
}

function check_clauses(proj, args) {
  const [notesFile, ...sources] = args;
  if (!notesFile || !sources.length) die("usage: jap check <code_notes.md> <code_text.txt> [more.txt]   (plain text of the code documents)");
  const notes = readText(path.resolve(CWD, notesFile));
  const corpus = sources.map((s) => ({ name: s, text: norm(readText(path.resolve(CWD, s))) }));
  const issues = []; let n = 0, verified = 0;
  for (const block of notes.split(/\n(?=### )/).filter((b) => b.startsWith("### "))) {
    n++;
    const title = block.split("\n")[0].replace(/^### /, "");
    const field = (f) => (block.match(new RegExp(`^${f}:\\s*(.+)$`, "mi")) || [])[1];
    for (const f of ["Clause", "Edition", "Jurisdiction", "Quote"]) if (!field(f)) issues.push({ level: "error", code: "missing-field", item: title, detail: `no '${f}:' line` });
    const q = quotes(block);
    if (!q.length) { issues.push({ level: "error", code: "no-quote", item: title, detail: "no verbatim clause text in quotes" }); continue; }
    const hit = q.every((x) => corpus.some((c) => c.text.includes(norm(x))));
    if (!hit) issues.push({ level: "error", code: "quote-not-in-code", item: title, detail: "clause text does not appear verbatim in the supplied code documents: treat as unverified" });
    else verified++;
  }
  if (!n) issues.push({ level: "error", code: "no-entries", item: notesFile, detail: "no '### ' clause entries found" });
  return { metrics: { clauses: n, verified }, issues };
}

function check_sheets(proj, args) {
  const sheetsFile = args[0] || "sheets.csv";
  const rows = csv(path.resolve(CWD, sheetsFile));
  const pat = new RegExp(proj.sheet_name_pattern || ".+");
  const statuses = proj.status_codes || [];
  const req = (proj.required_fields || {}).sheets || ["number", "title", "revision", "status"];
  const issues = []; const add = (l, c, i, d) => issues.push({ level: l, code: c, item: i, detail: d });
  const nums = new Set(), dup = new Set();
  for (const r of rows) { if (nums.has(r.number)) dup.add(r.number); nums.add(r.number); }
  for (const d of dup) add("error", "duplicate-number", d, "sheet number used twice");
  for (const r of rows) {
    const id = r.number || "(no number)";
    for (const f of req) if (!String(r[f] ?? "").trim()) add("error", "empty-field", id, `title block field '${f}' is empty`);
    if (r.number && !pat.test(r.number)) add("error", "naming", id, `does not match the naming convention ${pat}`);
    if (statuses.length && r.status && !statuses.some((s) => new RegExp(`^${s}$`).test(r.status))) add("error", "status-code", id, `status '${r.status}' not in the office list`);
    for (const ref of String(r.references || "").split(/[;|]/).map((x) => x.trim()).filter(Boolean))
      if (!nums.has(ref)) add("error", "dead-reference", id, `references '${ref}', which is not in the register`);
    if (r.drawn_by && r.checked_by && norm(r.drawn_by) === norm(r.checked_by)) add("error", "self-checked", id, "drawn and checked by the same person");
  }
  return { metrics: { sheets: rows.length }, issues };
}

function check_spec(proj, args) {
  const [specFile, registerFile, scheduleFile] = args;
  if (!specFile || !registerFile) die("usage: jap check <spec_section.md> <standards_register.csv> [schedule.csv]");
  const spec = readText(path.resolve(CWD, specFile)), reg = csv(path.resolve(CWD, registerFile));
  const sched = scheduleFile ? csv(path.resolve(CWD, scheduleFile)) : [];
  const issues = []; const add = (l, c, i, d) => issues.push({ level: l, code: c, item: i, detail: d });
  const known = new Map(reg.map((r) => [norm(r.code), r]));
  const refs = [...new Set([...spec.matchAll(/\b((?:BS\s)?(?:EN\s)?(?:ISO|EN|BS|DIN|ASTM|ANSI|NFPA|CSA|AS|NZS|JIS)\s?[A-Z]?\s?\d[\d.\-:]*(?:\+A\d+)?)/g)].map((m) => m[1].trim().replace(/[.,;:)]+$/, "")))];
  for (const r of refs) {
    const k = norm(r).replace(/:\d{4}.*$/, "");
    const hit = [...known.entries()].find(([c]) => c.replace(/:\d{4}.*$/, "") === k);
    if (!hit) add("error", "standard-unknown", r, "not in the office standards register: verify it exists and is current");
    else if (/withdrawn|superseded/i.test(hit[1].status || "")) add("error", "standard-withdrawn", r, `register says '${hit[1].status}'${hit[1].replaced_by ? `, replaced by ${hit[1].replaced_by}` : ""}`);
  }
  const ids = new Set(sched.map((r) => norm(r.id || r.mark || r.type)));
  for (const m of spec.matchAll(/\[P:([^\]]+)\]/g)) if (sched.length && !ids.has(norm(m[1]))) add("error", "product-orphan", m[1], "product line has no matching schedule item");
  return { metrics: { standards_cited: refs.length }, issues };
}

function check_refs(proj, args) {
  const [docFile, sheetsFile] = args;
  if (!docFile || !sheetsFile) die("usage: jap check <rfi_or_submittal.md> <sheets.csv>");
  const doc = readText(path.resolve(CWD, docFile)), rows = csv(path.resolve(CWD, sheetsFile));
  const cur = new Map(rows.map((r) => [r.number, r.revision]));
  const pat = new RegExp(proj.sheet_ref_pattern || "\\b[A-Z]{1,3}-?\\d{2,4}\\b", "g");
  const issues = [];
  for (const m of doc.matchAll(new RegExp(`(${pat.source})(?:\\s*rev(?:ision)?\\.?\\s*([A-Z0-9]+))?`, "gi"))) {
    const num = m[1], rev = m[m.length - 1];
    if (!cur.has(num)) issues.push({ level: "error", code: "dead-reference", item: num, detail: "not in the current sheet register" });
    else if (rev && norm(rev) !== norm(cur.get(num))) issues.push({ level: "error", code: "superseded", item: `${num} rev ${rev}`, detail: `current revision is ${cur.get(num)}` });
  }
  if (/\b(we|the architect) (will|shall) (pay|accept liability|guarantee|warrant)\b/i.test(doc))
    issues.push({ level: "error", code: "commitment", item: docFile, detail: "wording commits the architect contractually: senior review required" });
  return { metrics: { references: [...doc.matchAll(pat)].length }, issues };
}

function check_minutes(proj, args) {
  const [docFile, transcript] = args;
  if (!docFile) die("usage: jap check <minutes.md> [transcript.txt]");
  const doc = readText(path.resolve(CWD, docFile)), tr = transcript ? norm(readText(path.resolve(CWD, transcript))) : "";
  const issues = []; let actions = 0;
  const sec = doc.split(/\n(?=## )/).find((s) => /^## (Actions|Defects|Observations)/i.test(s)) || "";
  for (const line of sec.split("\n").filter((l) => /^\|/.test(l) && !/^\|\s*-/.test(l)).slice(1)) {
    actions++;
    const cells = line.split("|").slice(1, -1).map((c) => c.trim());
    const [what, owner, due, where] = cells;
    if (!owner) issues.push({ level: "error", code: "no-owner", item: what, detail: "action or defect has no owner" });
    if (!/^\d{4}-\d{2}-\d{2}$/.test(due || "")) issues.push({ level: "error", code: "no-date", item: what, detail: `due date '${due || ""}' is not YYYY-MM-DD` });
    if (/^## (Defects|Observations)/im.test(sec) && cells.length >= 4 && !where) issues.push({ level: "error", code: "no-location", item: what, detail: "no location" });
  }
  if (tr) for (const q of quotes(doc)) if (!tr.includes(norm(q))) issues.push({ level: "error", code: "quote-not-in-transcript", item: q.slice(0, 60), detail: "attributed quote not found in the transcript" });
  if (!actions) issues.push({ level: "warn", code: "no-actions", item: docFile, detail: "no actions table found" });
  return { metrics: { actions }, issues };
}

const CHECKERS = { check_areas, check_schedule, check_trace, check_clauses, check_sheets, check_spec, check_refs };
CHECKERS.check_minutes = check_minutes;
// Production checkers live in scripts/checks/*.js; each module exports check_* functions (proj, args, ctx).
for (const f of fs.readdirSync(path.join(__dirname, "checks")).filter((f) => f.endsWith(".js")))
  for (const [k, fn] of Object.entries(require(path.join(__dirname, "checks", f)))) if (k.startsWith("check_")) CHECKERS[k] = fn;

// ---------- commands ----------
function init() {
  if (fs.existsSync(path.join(JAP, "project.json"))) return console.log(".jap/project.json exists; edit it to change project standards.");
  fs.mkdirSync(path.join(JAP, "runs"), { recursive: true });
  fs.copyFileSync(path.join(ROOT, "templates", "project.json"), path.join(JAP, "project.json"));
  fs.writeFileSync(path.join(JAP, "learning_log.csv"), "date,task,autonomy,run,checker_errors,junior_findings,prediction_note\n");
  console.log("Created .jap/ with project.json, runs/ and learning_log.csv. Edit .jap/project.json: units, area definition, jurisdiction, naming, status codes.");
}

function start(task, want) {
  const t = PIPE.tasks[task] || die(`unknown task '${task}'. Tasks: ${Object.keys(PIPE.tasks).join(", ")}`);
  project();
  const cur = state(); if (cur) die(`run '${cur.run}' is still open; close it first (jap close)`);
  let a = want && LEVELS.includes(want) ? want : t.ceiling;
  if (LEVELS.indexOf(a) > LEVELS.indexOf(t.ceiling)) { console.log(`autonomy ${a} exceeds the ceiling for ${task}; capped at ${t.ceiling}`); a = t.ceiling; }
  const n = fs.readdirSync(path.join(JAP, "runs")).filter((d) => d.includes(task)).length + 1;
  const run = `${new Date().toISOString().slice(0, 10)}-${task}-${String(n).padStart(2, "0")}`;
  const st = { run, task, autonomy: a, started: now(), checker: t.checker, deliverable: t.deliverable, needs_prediction: ["A1", "A2"].includes(a), needs_review: ["A1", "A2", "A3"].includes(a) };
  writeJSON(path.join(JAP, "runs", run, "run.json"), st);
  writeJSON(STATE, st);
  console.log([`Run ${run} open. Task: ${task}. Autonomy: ${a} (${PIPE.autonomy_levels[a]})`,
    st.needs_prediction ? `Junior first: ${t.junior_keeps}\n  Record it yourself: jap predict "<your prediction>"  (Claude is blocked from writing it)` : "",
    `Deliverable: .jap/runs/${run}/${t.deliverable}   Checker: ${t.checker}`,
    `Watch for: ${t.failure_modes.join("; ")}`].filter(Boolean).join("\n"));
}

function note(kind, text) {
  const st = state() || die("no open run");
  if (!text) die(`usage: jap ${kind} "<text>"`);
  const p = path.join(runDir(st), `${kind === "predict" ? "prediction" : "review"}.md`);
  fs.appendFileSync(p, `\n[${now()}]\n${text}\n`);
  console.log(`${kind === "predict" ? "Prediction" : "Review"} recorded in ${path.relative(CWD, p)}`);
}

function check(args) {
  const st = state() || die("no open run; jap start <task>");
  const fn = CHECKERS[st.checker] || die(`no checker '${st.checker}'`);
  const res = fn(project(), args, { cwd: CWD, root: ROOT, run: runDir(st) });
  const errors = res.issues.filter((i) => i.level === "error").length;
  const report = { run: st.run, task: st.task, checker: st.checker, inputs: args, at: now(), status: errors ? "fail" : "pass", errors, warnings: res.issues.length - errors, ...res };
  writeJSON(path.join(runDir(st), "report.json"), report);
  console.log(`${st.checker}: ${report.status.toUpperCase()}  ${errors} errors, ${report.warnings} warnings  ${JSON.stringify(res.metrics)}`);
  for (const i of res.issues) console.log(`  [${i.level}] ${i.code}: ${i.item}: ${i.detail}`);
  console.log(`report: .jap/runs/${st.run}/report.json`);
}

function close() {
  const st = state() || die("no open run");
  const d = runDir(st), rep = readJSON(path.join(d, "report.json"), null);
  if (!rep) die("no checker report: run `jap check` first");
  if (st.needs_prediction && !fs.existsSync(path.join(d, "prediction.md"))) die("no junior prediction recorded for this run");
  if (st.needs_review && !fs.existsSync(path.join(d, "review.md"))) die("no junior review recorded: jap review \"<accept/reject each item, with reasons>\"");
  const rv = readText(path.join(d, "review.md"));
  const found = (rv.match(/^\s*(found|missed by checker|extra):/gim) || []).length;
  const pred = readText(path.join(d, "prediction.md")).replace(/\s+/g, " ").trim().slice(0, 120).replace(/,/g, ";");
  fs.appendFileSync(path.join(JAP, "learning_log.csv"), `${now()},${st.task},${st.autonomy},${st.run},${rep.errors},${found},"${pred}"\n`);
  fs.unlinkSync(STATE);
  console.log(`Closed ${st.run}. Logged: checker errors ${rep.errors}, junior findings ${found}.`);
}

function status() {
  const st = state();
  if (!st) return console.log("No open run. Start one: jap start <task>");
  const d = runDir(st);
  const has = (f) => (fs.existsSync(path.join(d, f)) ? "yes" : "no");
  console.log(`Run ${st.run}: ${st.task} at ${st.autonomy}\n  prediction: ${has("prediction.md")}  report: ${has("report.json")}  review: ${has("review.md")}`);
}

function tasks() {
  let fam = "";
  for (const [k, t] of Object.entries(PIPE.tasks)) {
    if (t.family && t.family !== fam) { fam = t.family; console.log(`
${(PIPE.families || {})[fam] || fam}`); }
    console.log(`  ${k.padEnd(25)} stage ${t.stages.join(",").padEnd(14)} ceiling ${t.ceiling}  ${t.checker.padEnd(17)} ${t.agent}`);
  }
}

function log() {
  const rows = csv(path.join(JAP, "learning_log.csv"));
  if (!rows.length) return console.log("Learning log is empty.");
  for (const r of rows) console.log(`${r.date.slice(0, 10)}  ${r.task.padEnd(20)} ${r.autonomy}  checker errors ${r.checker_errors.padStart(3)}  junior findings ${r.junior_findings}`);
}

const [cmd, ...rest] = process.argv.slice(2);
({ init, start: () => start(rest[0], rest[1]), predict: () => note("predict", rest.join(" ")), review: () => note("review", rest.join(" ")),
   check: () => check(rest), close, status, tasks, log }[cmd] || (() => console.log("jap init | start <task> [A0-A4] | predict \"..\" | check [inputs] | review \"..\" | close | status | tasks | log")))();
