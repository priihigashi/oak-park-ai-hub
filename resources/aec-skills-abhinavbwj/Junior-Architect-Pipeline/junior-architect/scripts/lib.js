// Junior Architect Pipeline. Copyright (c) 2026 Abhinav Bhardwaj. MIT licence.
"use strict";
/** Shared helpers for the pipeline's checkers. Node only, no dependencies. */
const fs = require("fs");
const path = require("path");

const die = (m) => { console.error("jap: " + m); process.exit(1); };
const readJSON = (p, d) => (fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8").replace(/^﻿/, "")) : d);
const writeJSON = (p, o) => { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, JSON.stringify(o, null, 2) + "\n"); };
const readText = (p) => (fs.existsSync(p) ? fs.readFileSync(p, "utf8") : "");
const norm = (s) => String(s ?? "").toLowerCase().replace(/[‘’“”]/g, "'").replace(/["']/g, "").replace(/\s+/g, " ").trim();

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

/** Collects issues in the common report shape. */
function collector() {
  const issues = [];
  const add = (level, code, item, detail) => issues.push({ level, code, item: String(item), detail });
  return { issues, add, err: (c, i, d) => add("error", c, i, d), warn: (c, i, d) => add("warn", c, i, d) };
}

/** Load a JSON or CSV input relative to the project. */
function load(ctx, file, what) {
  if (!file) die(`missing input: ${what}`);
  const p = path.resolve(ctx.cwd, file);
  if (!fs.existsSync(p)) die(`${what} not found: ${file}`);
  return p.toLowerCase().endsWith(".csv") ? csv(p) : readJSON(p);
}

const UNIT_TO_M = { mm: 0.001, cm: 0.01, m: 1, ft: 0.3048, in: 0.0254 };
const toM = (v, u) => Number(v) * (UNIT_TO_M[u || "m"] ?? NaN);
const deg = (r) => (r * 180) / Math.PI;
const rad = (d) => (d * Math.PI) / 180;

module.exports = { die, readJSON, writeJSON, readText, norm, csv, collector, load, UNIT_TO_M, toM, deg, rad };
