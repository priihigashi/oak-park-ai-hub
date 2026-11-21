"use strict";
/**
 * Junior Architect Pipeline. Copyright (c) 2026 Abhinav Bhardwaj. MIT licence.
 * Design and modelling checkers: metrics against rules, stairs, facade and fabrication panels, Grasshopper definitions.
 * Inputs are exports from Rhino, Revit or Grasshopper (through any connected MCP server, or exported by hand), written into the run folder.
 */
const { collector, load, norm } = require("../lib");

/**
 * check_metrics <measured.json> <rules.json>
 * measured: {"gfa_m2": 18420, "height_m": 27.4, ...}
 * rules: [{"metric": "height_m", "op": "<=", "value": 28, "source": "zoning plan §4.2"}, {"metric": "far", "op": "between", "min": 2, "max": 3.5}]
 * ops: <= >= < > == between within (value with tol_pct)
 */
function check_metrics(proj, args, ctx) {
  const m = load(ctx, args[0], "measured metrics JSON"), rules = load(ctx, args[1] || ".jap/rules.json", "rules JSON");
  const { issues, err, warn } = collector();
  let passed = 0;
  for (const r of rules) {
    const v = m[r.metric];
    const src = r.source ? ` [${r.source}]` : " [no source given]";
    if (v === undefined || v === null || Number.isNaN(Number(v))) { err("missing-metric", r.metric, `not in the measured export${src}`); continue; }
    const x = Number(v);
    let ok;
    switch (r.op) {
      case "<=": ok = x <= r.value; break;
      case ">=": ok = x >= r.value; break;
      case "<": ok = x < r.value; break;
      case ">": ok = x > r.value; break;
      case "==": ok = Math.abs(x - r.value) < 1e-9; break;
      case "between": ok = x >= r.min && x <= r.max; break;
      case "within": ok = Math.abs(x - r.value) <= Math.abs(r.value) * (r.tol_pct ?? 5) / 100; break;
      default: err("bad-rule", r.metric, `unknown op '${r.op}'`); continue;
    }
    const want = r.op === "between" ? `${r.min} to ${r.max}` : r.op === "within" ? `${r.value} ±${r.tol_pct ?? 5}%` : `${r.op} ${r.value}`;
    if (ok) passed++;
    else (r.level === "warn" ? warn : err)("rule-failed", r.metric, `${x} fails ${want}${src}`);
    if (!r.source) warn("unsourced-rule", r.metric, "rule has no source: a limit without a clause cannot be defended");
  }
  return { metrics: { rules: rules.length, passed }, issues };
}

/**
 * check_stairs <stairs.json>
 * stairs: [{"id": "ST-01", "use": "common", "risers": 17, "riser_mm": 176.5, "going_mm": 280, "width_mm": 1200,
 *           "headroom_mm": 2100, "max_flight_risers": 12, "floor_to_floor_mm": 3000}]
 * Limits from project.json "stair_rules" by use (common/private/public). Set them from your code: defaults are placeholders.
 */
function check_stairs(proj, args, ctx) {
  const stairs = load(ctx, args[0], "stairs JSON");
  const R = proj.stair_rules || {};
  const { issues, err, warn } = collector();
  for (const s of stairs) {
    const r = { blondel_min: 550, blondel_max: 700, max_riser_mm: 190, min_going_mm: 250, min_width_mm: 1000, min_headroom_mm: 2000, max_flight_risers: 16, max_pitch_deg: 42, ...(R.default || {}), ...(R[s.use] || {}) };
    const id = s.id || "(stair)";
    const R2G = 2 * s.riser_mm + s.going_mm;
    if (R2G < r.blondel_min || R2G > r.blondel_max) err("blondel", id, `2R+G = ${R2G.toFixed(0)} mm, outside ${r.blondel_min} to ${r.blondel_max} mm`);
    if (s.riser_mm > r.max_riser_mm) err("riser", id, `riser ${s.riser_mm} mm > ${r.max_riser_mm} mm`);
    if (s.going_mm < r.min_going_mm) err("going", id, `going ${s.going_mm} mm < ${r.min_going_mm} mm`);
    if (s.width_mm < r.min_width_mm) err("width", id, `clear width ${s.width_mm} mm < ${r.min_width_mm} mm`);
    if (s.headroom_mm != null && s.headroom_mm < r.min_headroom_mm) err("headroom", id, `headroom ${s.headroom_mm} mm < ${r.min_headroom_mm} mm`);
    const pitch = (Math.atan(s.riser_mm / s.going_mm) * 180) / Math.PI;
    if (pitch > r.max_pitch_deg) err("pitch", id, `pitch ${pitch.toFixed(1)}° > ${r.max_pitch_deg}°`);
    if (s.max_flight_risers != null && s.max_flight_risers > r.max_flight_risers) err("flight", id, `${s.max_flight_risers} risers in one flight > ${r.max_flight_risers}`);
    if (s.floor_to_floor_mm != null && s.risers) {
      const rise = s.risers * s.riser_mm;
      if (Math.abs(rise - s.floor_to_floor_mm) > 3) err("total-rise", id, `${s.risers} × ${s.riser_mm} = ${rise.toFixed(1)} mm, floor to floor is ${s.floor_to_floor_mm} mm`);
    }
    if (Array.isArray(s.risers_mm) && s.risers_mm.length) {
      const spread = Math.max(...s.risers_mm) - Math.min(...s.risers_mm);
      if (spread > 5) err("uneven-risers", id, `risers vary by ${spread.toFixed(1)} mm within the flight`);
    }
    if (!R[s.use] && !R.default) warn("default-limits", id, "checked against placeholder limits: set stair_rules in .jap/project.json from your code");
  }
  return { metrics: { stairs: stairs.length }, issues };
}

/**
 * check_panels <panels.json>
 * panels: [{"id": "P-001", "type": "A", "w_mm": 1500, "h_mm": 3200, "planarity_mm": 2.1, "flat": true}]
 * Limits from project.json "fabrication": {max_w_mm, max_h_mm, min_w_mm, min_h_mm, max_types, max_planarity_mm, stock: [{w_mm, h_mm}]}
 */
function check_panels(proj, args, ctx) {
  const panels = load(ctx, args[0], "panels JSON");
  const f = { max_types: Infinity, ...(proj.fabrication || {}) };
  const { issues, err, warn } = collector();
  const types = new Set();
  for (const p of panels) {
    const id = p.id || "(panel)";
    types.add(p.type ?? `${Math.round(p.w_mm)}x${Math.round(p.h_mm)}`);
    if (f.max_w_mm && p.w_mm > f.max_w_mm) err("too-wide", id, `${p.w_mm} mm > ${f.max_w_mm} mm`);
    if (f.max_h_mm && p.h_mm > f.max_h_mm) err("too-tall", id, `${p.h_mm} mm > ${f.max_h_mm} mm`);
    if (f.min_w_mm && p.w_mm < f.min_w_mm) err("sliver", id, `${p.w_mm} mm < ${f.min_w_mm} mm`);
    if (f.min_h_mm && p.h_mm < f.min_h_mm) err("sliver", id, `${p.h_mm} mm < ${f.min_h_mm} mm`);
    if (f.max_planarity_mm != null && p.planarity_mm != null && p.planarity_mm > f.max_planarity_mm)
      err("not-planar", id, `deviation ${p.planarity_mm} mm > ${f.max_planarity_mm} mm: needs cold-bending or a curved panel`);
    if (p.flat && Array.isArray(f.stock) && f.stock.length) {
      const fits = f.stock.some((s) => (p.w_mm <= s.w_mm && p.h_mm <= s.h_mm) || (p.h_mm <= s.w_mm && p.w_mm <= s.h_mm));
      if (!fits) err("no-stock", id, `${p.w_mm} × ${p.h_mm} mm fits no stock sheet`);
    }
  }
  if (types.size > f.max_types) err("too-many-types", `${types.size} types`, `more than the ${f.max_types} the budget allows: rationalise`);
  return { metrics: { panels: panels.length, types: types.size }, issues };
}

/**
 * check_gh <gh_export.json>
 * {"components": [{"id": "...", "name": "Loft", "nickname": "Loft", "runtime": "ok|warning|error", "messages": [],
 *   "inputs": [{"name": "Curves", "sources": 1, "optional": false}], "internalised": false, "kind": "component|slider|param"}]}
 * Produced from the definition by the connected Grasshopper MCP server, or by a GhPython export script.
 */
function check_gh(proj, args, ctx) {
  const d = load(ctx, args[0], "Grasshopper export JSON");
  const comps = d.components || d;
  const { issues, err, warn } = collector();
  for (const c of comps) {
    const id = `${c.nickname || c.name} (${String(c.id || "").slice(0, 8)})`;
    if (c.runtime === "error") err("runtime-error", id, (c.messages || []).join("; ") || "component in error state");
    if (c.runtime === "warning") warn("runtime-warning", id, (c.messages || []).join("; ") || "component has warnings");
    for (const i of c.inputs || []) if (!i.optional && !i.sources && !i.has_data) err("unconnected", id, `required input '${i.name}' has no source and no data`);
    if (c.kind === "slider" && (!c.nickname || /^number slider$/i.test(c.nickname))) warn("unnamed-slider", id, "slider has no name: nobody can read the definition");
    if (c.internalised) warn("internalised", id, "geometry is internalised: the definition no longer follows the Rhino model");
  }
  return { metrics: { components: comps.length, errors: comps.filter((c) => c.runtime === "error").length }, issues };
}

module.exports = { check_metrics, check_stairs, check_panels, check_gh };
