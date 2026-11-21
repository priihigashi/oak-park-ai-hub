"use strict";
/**
 * Junior Architect Pipeline. Copyright (c) 2026 Abhinav Bhardwaj. MIT licence.
 * Documentation checkers: view sets, annotation coverage, CAD (DXF) files, IFC exchange files, quantity takeoffs.
 */
const fs = require("fs");
const path = require("path");
const { collector, load, norm, readText, die } = require("../lib");

/**
 * check_views <views.json>
 * views: [{"id": 1, "name": "Level 01 - Plan", "type": "FloorPlan", "level": "Level 01", "scale": 100,
 *          "template": "A-PLAN-100", "on_sheet": "A-101"}]   (exported from the model's view list)
 * Requirements from project.json "view_requirements":
 *   {"levels": ["Level 00","Level 01"], "min_sections": 2, "min_elevations": 4, "scales": {"FloorPlan": [50,100]},
 *    "require_template": true, "require_on_sheet": ["FloorPlan","Section","Elevation","Detail"]}
 */
function check_views(proj, args, ctx) {
  const views = load(ctx, args[0], "views JSON");
  const q = { min_sections: 2, min_elevations: 4, require_template: true, require_on_sheet: ["FloorPlan", "Section", "Elevation", "Detail"], ...(proj.view_requirements || {}) };
  const { issues, err, warn } = collector();
  const by = (t) => views.filter((v) => v.type === t);
  for (const lv of q.levels || []) if (!by("FloorPlan").some((v) => norm(v.level) === norm(lv))) err("missing-plan", lv, "no floor plan for this level");
  if (by("Section").length < q.min_sections) err("few-sections", `${by("Section").length} sections`, `at least ${q.min_sections} required`);
  if (by("Elevation").length < q.min_elevations) err("few-elevations", `${by("Elevation").length} elevations`, `at least ${q.min_elevations} required`);
  const names = new Map();
  for (const v of views) {
    names.set(norm(v.name), (names.get(norm(v.name)) || 0) + 1);
    if (/(^copy of|\bcopy \d+$|^section \d+$|^elevation \d+$|^3d view \d+$|^\{3d\}$)/i.test(v.name)) warn("default-name", v.name, "default or copied view name");
    if (q.require_template && ["FloorPlan", "Section", "Elevation", "CeilingPlan"].includes(v.type) && !v.template) err("no-template", v.name, "no view template: graphics will drift between views");
    const allowed = (q.scales || {})[v.type];
    if (allowed && v.scale && !allowed.includes(Number(v.scale))) err("scale", v.name, `1:${v.scale} not in ${allowed.map((s) => "1:" + s).join(", ")}`);
    if (q.require_on_sheet.includes(v.type) && !v.on_sheet) warn("not-on-sheet", v.name, "view is not placed on any sheet");
  }
  for (const [n, c] of names) if (c > 1) err("duplicate-name", n, `${c} views share this name`);
  return { metrics: { views: views.length, plans: by("FloorPlan").length, sections: by("Section").length, elevations: by("Elevation").length }, issues };
}

/**
 * check_annotation <annotation.json>
 * [{"view": "Level 01 - Plan", "type": "FloorPlan", "dimensions": 42,
 *   "categories": {"Doors": {"elements": 24, "tagged": 22}, "Rooms": {"elements": 18, "tagged": 18}}}]
 */
function check_annotation(proj, args, ctx) {
  const rows = load(ctx, args[0], "annotation JSON");
  const need = proj.tag_coverage || { Doors: 1, Windows: 1, Rooms: 1 };
  const { issues, err, warn } = collector();
  for (const v of rows) {
    for (const [cat, c] of Object.entries(v.categories || {})) {
      const want = need[cat];
      if (want == null || !c.elements) continue;
      const cov = c.tagged / c.elements;
      if (cov < want) err("untagged", `${v.view}: ${cat}`, `${c.tagged} of ${c.elements} tagged (${(cov * 100).toFixed(0)}%, need ${(want * 100).toFixed(0)}%)`);
    }
    if (["FloorPlan", "Section", "Elevation", "Detail"].includes(v.type) && !v.dimensions) err("no-dimensions", v.view, "no dimensions in a documentation view");
    if (v.overlapping_tags) warn("overlap", v.view, `${v.overlapping_tags} tags overlap other annotation`);
  }
  return { metrics: { views: rows.length }, issues };
}

/** Minimal ASCII DXF reader: group-code/value pairs into sections. */
function readDXF(text) {
  const lines = text.split(/\r?\n/);
  const pairs = [];
  for (let i = 0; i + 1 < lines.length; i += 2) pairs.push([parseInt(lines[i].trim(), 10), lines[i + 1].trim()]);
  const out = { header: {}, layers: [], entities: [] };
  let section = null, cur = null, inLayerTable = false;
  for (let i = 0; i < pairs.length; i++) {
    const [c, v] = pairs[i];
    if (c === 0 && v === "SECTION") { section = pairs[i + 1] && pairs[i + 1][1]; continue; }
    if (c === 0 && v === "ENDSEC") { section = null; cur = null; continue; }
    if (section === "HEADER" && c === 9) { const nxt = pairs[i + 1]; if (nxt) out.header[v] = nxt[1]; }
    if (section === "TABLES") {
      if (c === 0 && v === "TABLE") inLayerTable = pairs[i + 1] && pairs[i + 1][1] === "LAYER";
      if (c === 0 && v === "ENDTAB") inLayerTable = false;
      if (inLayerTable && c === 0 && v === "LAYER") { cur = { name: "" }; out.layers.push(cur); }
      if (inLayerTable && cur && c === 2) cur.name = v;
    }
    if (section === "ENTITIES") {
      if (c === 0) { cur = { type: v, layer: "0" }; out.entities.push(cur); }
      else if (cur && c === 8) cur.layer = v;
      else if (cur && c === 40 && (cur.type === "TEXT" || cur.type === "MTEXT")) cur.height = parseFloat(v);
    }
  }
  return out;
}

/**
 * check_dxf <drawing.dxf>
 * Rules from project.json "cad": {"layer_pattern": "^A-...", "insunits": 4, "plot_scale": 100,
 *   "text_heights_mm": [1.8, 2.5, 3.5, 5, 7, 10]}   (paper heights, ISO 3098 series; multiplied by the plot scale)
 */
function check_dxf(proj, args, ctx) {
  const file = path.resolve(ctx.cwd, args[0] || die("usage: check <drawing.dxf>"));
  const txt = readText(file);
  if (!txt.includes("SECTION")) die("not an ASCII DXF (export DXF in ASCII, or convert DWG to DXF first)");
  const d = readDXF(txt), cad = { insunits: 4, plot_scale: 100, text_heights_mm: [1.8, 2.5, 3.5, 5, 7, 10], ...(proj.cad || {}) };
  const { issues, err, warn } = collector();
  const units = Number(d.header.$INSUNITS);
  const UN = { 1: "inches", 2: "feet", 4: "millimetres", 5: "centimetres", 6: "metres" };
  if (units !== cad.insunits) err("units", "$INSUNITS", `drawing units are ${UN[units] || units || "unset"}, project uses ${UN[cad.insunits]}`);
  const pat = cad.layer_pattern ? new RegExp(cad.layer_pattern) : null;
  const used = new Map();
  for (const e of d.entities) used.set(e.layer, (used.get(e.layer) || 0) + 1);
  for (const l of d.layers) {
    if (l.name === "0" || l.name.toLowerCase() === "defpoints") continue;
    if (pat && !pat.test(l.name)) err("layer-name", l.name, `does not follow the layer convention ${pat}`);
    if (!used.has(l.name)) warn("empty-layer", l.name, "layer has no entities (purge)");
  }
  const on0 = used.get("0") || 0;
  if (on0) err("layer-0", "layer 0", `${on0} entities drawn on layer 0`);
  const allowed = cad.text_heights_mm.map((h) => h * cad.plot_scale);
  const bad = d.entities.filter((e) => e.height && !allowed.some((a) => Math.abs(a - e.height) / a < 0.02));
  if (bad.length) err("text-height", `${bad.length} texts`, `heights ${[...new Set(bad.map((b) => b.height))].slice(0, 6).join(", ")} are off the ${cad.text_heights_mm.join("/")} mm series at 1:${cad.plot_scale}`);
  return { metrics: { layers: d.layers.length, entities: d.entities.length, units: UN[units] || units }, issues };
}

/**
 * check_ifc <model.ifc> [expected.json]
 * expected: {"schema": "IFC4X3", "IfcWall": 120, "IfcDoor": 34, "IfcWindow": 60, "IfcSpace": 41, "storeys": ["Level 00","Level 01"]}
 */
function check_ifc(proj, args, ctx) {
  const file = path.resolve(ctx.cwd, args[0] || die("usage: check <model.ifc> [expected.json]"));
  const txt = readText(file);
  if (!/ISO-10303-21/.test(txt)) die("not an IFC STEP file");
  const exp = args[1] ? load(ctx, args[1], "expected counts JSON") : {};
  const { issues, err, warn } = collector();
  const schema = (txt.match(/FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'/i) || [])[1] || "?";
  const want = exp.schema || proj.ifc_schema;
  if (want && norm(schema) !== norm(want)) err("schema", schema, `expected ${want}`);
  const count = {};
  for (const m of txt.matchAll(/^#\d+\s*=\s*(IFC[A-Z0-9_]+)\s*\(/gim)) { const k = m[1].toUpperCase(); count[k] = (count[k] || 0) + 1; }
  const n = (t) => (count[t.toUpperCase()] || 0) + (count[(t + "StandardCase").toUpperCase()] || 0);
  for (const [k, v] of Object.entries(exp)) {
    if (!/^Ifc/.test(k)) continue;
    const got = n(k);
    if (got !== v) err("count", k, `IFC has ${got}, the model has ${v}`);
  }
  const elems = ["IfcWall", "IfcSlab", "IfcDoor", "IfcWindow", "IfcColumn", "IfcBeam", "IfcStair", "IfcRoof", "IfcCovering", "IfcRailing", "IfcCurtainWall", "IfcMember", "IfcPlate"].reduce((s, t) => s + n(t), 0);
  const proxies = n("IfcBuildingElementProxy");
  if (elems + proxies && proxies / (elems + proxies) > 0.05) err("proxies", `${proxies} proxies`, `${((100 * proxies) / (elems + proxies)).toFixed(0)}% of elements exported as IfcBuildingElementProxy: check the category mapping`);
  const lenUnit = txt.match(/IFCSIUNIT\s*\([^;]*\.LENGTHUNIT\.\s*,\s*(\.[A-Z]+\.|\$)\s*,\s*\.METRE\./i);
  if (!lenUnit) warn("units", "length unit", "no SI length unit found (imperial export, or units missing)");
  const storeys = [...txt.matchAll(/IFCBUILDINGSTOREY\s*\(\s*'[^']*'\s*,\s*[^,]*,\s*'([^']*)'/gi)].map((m) => m[1]);
  for (const s of exp.storeys || []) if (!storeys.some((x) => norm(x) === norm(s))) err("storey", s, "storey missing from the IFC");
  const spaces = [...txt.matchAll(/IFCSPACE\s*\(\s*'[^']*'\s*,\s*[^,]*,\s*('([^']*)'|\$)/gi)];
  const unnamed = spaces.filter((m) => !m[2]).length;
  if (unnamed) err("space-name", `${unnamed} spaces`, "IfcSpace without a name");
  return { metrics: { schema, elements: elems, proxies, storeys: storeys.length, spaces: spaces.length }, issues };
}

/**
 * check_quantities <takeoff.csv|json> [area_schedule_total_m2]
 * rows: category,item,quantity,unit
 * Allowed units per category from project.json "quantity_units" (defaults below).
 */
function check_quantities(proj, args, ctx) {
  const rows = load(ctx, args[0], "takeoff");
  const U = { Walls: ["m2", "m3", "m"], Floors: ["m2", "m3"], Roofs: ["m2"], Doors: ["no"], Windows: ["no", "m2"], Rooms: ["m2"], Columns: ["no", "m3", "m"], Beams: ["m", "m3"], ...(proj.quantity_units || {}) };
  const { issues, err, warn } = collector();
  const seen = new Set(); let rooms = 0;
  for (const r of rows) {
    const id = `${r.category}: ${r.item}`;
    const q = Number(r.quantity);
    if (!r.unit) err("no-unit", id, "quantity has no unit");
    else if (U[r.category] && !U[r.category].includes(r.unit)) err("unit", id, `unit '${r.unit}' not valid for ${r.category} (${U[r.category].join(", ")})`);
    if (!(q > 0)) err("quantity", id, `quantity '${r.quantity}' is not positive`);
    if (seen.has(id)) err("duplicate", id, "line appears twice"); seen.add(id);
    if (r.category === "Rooms" && r.unit === "m2") rooms += q;
  }
  if (args[1]) {
    const t = Number(args[1]);
    if (Math.abs(rooms - t) / t > 0.005) err("area-mismatch", "Rooms total", `takeoff ${rooms.toFixed(2)} m², area schedule ${t} m²`);
  }
  return { metrics: { lines: rows.length, room_area_m2: +rooms.toFixed(2) }, issues };
}

module.exports = { check_views, check_annotation, check_dxf, check_ifc, check_quantities, readDXF };
