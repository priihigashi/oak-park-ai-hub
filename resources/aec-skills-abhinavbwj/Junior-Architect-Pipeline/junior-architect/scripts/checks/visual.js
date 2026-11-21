"use strict";
/**
 * Junior Architect Pipeline. Copyright (c) 2026 Abhinav Bhardwaj. MIT licence.
 * Visualisation and coordination checkers: renders and captures (image size, camera, sun position), presentation boards,
 * clash reports.
 */
const fs = require("fs");
const path = require("path");
const { collector, load, deg, rad } = require("../lib");

/** Image size from the file header (PNG IHDR, JPEG SOFn). No decoding. */
function imageSize(file) {
  const b = fs.readFileSync(file);
  if (b.slice(0, 8).toString("hex") === "89504e470d0a1a0a") return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), fmt: "png" };
  if (b[0] === 0xff && b[1] === 0xd8) {
    let i = 2;
    while (i < b.length) {
      if (b[i] !== 0xff) { i++; continue; }
      const m = b[i + 1], len = b.readUInt16BE(i + 2);
      if (m >= 0xc0 && m <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(m)) return { h: b.readUInt16BE(i + 5), w: b.readUInt16BE(i + 7), fmt: "jpeg" };
      i += 2 + len;
    }
  }
  return null;
}

/**
 * Solar position (NOAA general solar position equations; accuracy about 0.5° for the years 1950-2050, enough to check a
 * render's sun). Returns {azimuth: degrees clockwise from north, altitude: degrees above the horizon}.
 * iso: local date-time "2026-03-21T12:00", tz: hours east of UTC, lat/lon in degrees (east positive).
 */
function sunPosition(iso, tz, lat, lon) {
  const [d, t] = iso.split("T");
  const [Y, M, D] = d.split("-").map(Number);
  const [hh, mm] = (t || "12:00").split(":").map(Number);
  const doy = Math.round((Date.UTC(Y, M - 1, D) - Date.UTC(Y, 0, 0)) / 864e5);
  const leap = (Y % 4 === 0 && Y % 100 !== 0) || Y % 400 === 0;
  const g = ((2 * Math.PI) / (leap ? 366 : 365)) * (doy - 1 + (hh - 12) / 24);
  const eqt = 229.18 * (0.000075 + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g) - 0.014615 * Math.cos(2 * g) - 0.040849 * Math.sin(2 * g));
  const decl = 0.006918 - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g) - 0.006758 * Math.cos(2 * g) + 0.000907 * Math.sin(2 * g) - 0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g);
  const tst = hh * 60 + mm + eqt + 4 * lon - 60 * tz;
  const ha = rad(tst / 4 - 180);
  const phi = rad(lat);
  const cosZ = Math.sin(phi) * Math.sin(decl) + Math.cos(phi) * Math.cos(decl) * Math.cos(ha);
  const zen = Math.acos(Math.min(1, Math.max(-1, cosZ)));
  let az = deg(Math.acos(Math.min(1, Math.max(-1, (Math.sin(phi) * Math.cos(zen) - Math.sin(decl)) / (Math.cos(phi) * Math.sin(zen))))));
  az = ha > 0 ? (az + 180) % 360 : (540 - az) % 360;
  return { azimuth: +az.toFixed(2), altitude: +(90 - deg(zen)).toFixed(2) };
}

/**
 * check_render <renders.json>
 * [{"file": "out/eye_01.png", "kind": "eye-level|aerial|axonometric|sun-study|diagram",
 *   "camera": {"height_m": 1.6, "focal_mm": 35, "projection": "perspective"},
 *   "sun": {"azimuth": 180.4, "altitude": 30.1}, "datetime": "2026-03-21T12:00", "tz": 1, "lat": 59.91, "lon": 10.75}]
 * Rules from project.json "render": {min_width: 3000, eye_level_m: [1.5, 1.75], focal_mm: [24, 50], sun_tolerance_deg: 2}
 */
function check_render(proj, args, ctx) {
  const items = load(ctx, args[0], "renders JSON");
  const r = { min_width: 3000, eye_level_m: [1.5, 1.75], focal_mm: [24, 50], sun_tolerance_deg: 2, ...(proj.render || {}) };
  const { issues, err, warn } = collector();
  for (const it of items) {
    const id = it.file || "(image)";
    const p = path.resolve(ctx.cwd, it.file || "");
    if (!it.file || !fs.existsSync(p)) { err("missing", id, "image file not found"); continue; }
    const sz = imageSize(p);
    if (!sz) warn("format", id, "not PNG or JPEG: size not checked");
    else if (sz.w < r.min_width) err("resolution", id, `${sz.w} × ${sz.h} px, below the ${r.min_width} px minimum width`);
    const cam = it.camera || {};
    if (it.kind === "eye-level") {
      if (cam.height_m == null) err("camera", id, "eye-level image without a recorded camera height");
      else if (cam.height_m < r.eye_level_m[0] || cam.height_m > r.eye_level_m[1]) err("eye-level", id, `camera at ${cam.height_m} m, eye level is ${r.eye_level_m[0]} to ${r.eye_level_m[1]} m`);
      if (cam.focal_mm != null && (cam.focal_mm < r.focal_mm[0] || cam.focal_mm > r.focal_mm[1])) err("lens", id, `${cam.focal_mm} mm lens outside ${r.focal_mm[0]} to ${r.focal_mm[1]} mm: distorts how the space reads`);
    }
    if (it.kind === "axonometric" && cam.projection && cam.projection !== "parallel") err("projection", id, `axonometric drawn in ${cam.projection} projection`);
    if (it.datetime && it.lat != null && it.lon != null && it.tz != null) {
      const s = sunPosition(it.datetime, it.tz, it.lat, it.lon);
      if (!it.sun) err("sun", id, `no sun recorded; at ${it.datetime} the sun is at azimuth ${s.azimuth}°, altitude ${s.altitude}°`);
      else {
        const dAz = Math.abs(((it.sun.azimuth - s.azimuth + 540) % 360) - 180), dAlt = Math.abs(it.sun.altitude - s.altitude);
        if (dAz > r.sun_tolerance_deg || dAlt > r.sun_tolerance_deg)
          err("sun-position", id, `scene sun az ${it.sun.azimuth}° alt ${it.sun.altitude}°; real sun at ${it.datetime} is az ${s.azimuth}° alt ${s.altitude}° (lat ${it.lat}, lon ${it.lon})`);
        if (s.altitude < 0) warn("night", id, "the sun is below the horizon at this time");
      }
    } else if (it.kind === "sun-study") err("sun-study", id, "sun study without date, time, time zone and location");
  }
  return { metrics: { images: items.length }, issues };
}

/**
 * check_board <board.json>
 * {"size_mm": [841, 594], "min_text_mm": 3, "items": [{"type": "image|drawing|text", "file": "...", "caption": "...",
 *   "source": "...", "scale_bar": true, "north": true, "text_mm": 4}]}
 */
function check_board(proj, args, ctx) {
  const b = load(ctx, args[0], "board JSON");
  const base = path.dirname(path.resolve(ctx.cwd, args[0])); // same base as board.js: paths relative to board.json
  const { issues, err, warn } = collector();
  for (const [i, it] of (b.items || []).entries()) {
    const id = it.file || it.caption || `item ${i + 1}`;
    if (it.file && !fs.existsSync(path.resolve(base, it.file))) err("missing", id, "file not found");
    if (it.type !== "text" && !it.caption) err("caption", id, "no caption");
    if (it.type === "image" && !it.source) err("source", id, "no source or credit (own render, photo credit, data source)");
    if (it.type === "drawing" && !it.scale_bar) err("scale-bar", id, "drawing without a scale bar");
    if (it.type === "drawing" && it.plan && !it.north) err("north", id, "plan without a north point");
    if (it.text_mm != null && it.text_mm < (b.min_text_mm ?? 3)) err("text-size", id, `${it.text_mm} mm text, below ${b.min_text_mm ?? 3} mm at print size`);
  }
  return { metrics: { items: (b.items || []).length }, issues };
}

/**
 * check_clash <clashes.json>
 * [{"id": "C-014", "a": "Duct 600x400", "b": "Beam B12", "type": "hard|clearance", "depth_mm": 85, "status": "new|active|resolved|approved", "owner": "MEP"}]
 * Tolerance from project.json "clash_tolerance_mm" (default 10).
 */
function check_clash(proj, args, ctx) {
  const c = load(ctx, args[0], "clash JSON");
  const tol = proj.clash_tolerance_mm ?? 10;
  const { issues, err, warn } = collector();
  const pairs = {};
  for (const x of c) {
    const id = x.id || `${x.a} / ${x.b}`;
    const open = !["resolved", "approved"].includes(String(x.status).toLowerCase());
    pairs[`${x.a?.split(" ")[0]} vs ${x.b?.split(" ")[0]}`] = (pairs[`${x.a?.split(" ")[0]} vs ${x.b?.split(" ")[0]}`] || 0) + (open ? 1 : 0);
    if (open && x.type === "hard" && (x.depth_mm ?? Infinity) > tol && !x.owner) err("unassigned", id, `${x.depth_mm ?? "?"} mm hard clash with no owner`);
    if (String(x.status).toLowerCase() === "approved" && !x.approved_by) err("approval", id, "approved without a named approver");
    if (!["new", "active", "resolved", "approved", "reviewed"].includes(String(x.status).toLowerCase())) warn("status", id, `unknown status '${x.status}'`);
  }
  return { metrics: { clashes: c.length, open: c.filter((x) => !["resolved", "approved"].includes(String(x.status).toLowerCase())).length, by_pair: pairs }, issues };
}

module.exports = { check_render, check_board, check_clash, sunPosition, imageSize };
