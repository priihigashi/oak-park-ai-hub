#!/usr/bin/env node
/**
 * Junior Architect Pipeline. Copyright (c) 2026 Abhinav Bhardwaj. MIT licence.
 * Junior Architect Pipeline: compose a presentation board from board.json into PDF and PNG with headless Chrome.
 *
 *   board <board.json> [out_basename]
 *
 * board.json:
 * {"title": "Riverside housing, stage 2", "subtitle": "Concept design review, 2026-11-19", "size_mm": [841, 594],
 *  "columns": 3, "items": [
 *    {"type": "image", "file": "renders/eye_01.png", "caption": "Street view from the north", "source": "Own render, Rhino 8", "span": 2},
 *    {"type": "drawing", "file": "drawings/plan_l00.png", "caption": "Ground floor 1:200", "scale_bar": true, "north": true, "plan": true},
 *    {"type": "text", "caption": "Concept", "text": "Two wings around a south-facing court.", "text_mm": 4}]}
 * Check it first with check_board. The layout is a strict grid: no rounded corners, no shadows, one accent colour.
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { die, readJSON } = require("./lib");

const CWD = process.env.JAP_PROJECT || process.cwd();
const [file, outName] = process.argv.slice(2);
if (!file) die("usage: board <board.json> [out_basename]");
const b = readJSON(path.resolve(CWD, file)) || die(`not found: ${file}`);
const proj = readJSON(path.join(CWD, ".jap", "project.json"), {});
const chrome = (proj.render || {}).browser || ["C:/Program Files/Google/Chrome/Application/chrome.exe", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome"].find((p) => fs.existsSync(p));
if (!chrome) die('no Chrome found: set "render": {"browser": "<path to chrome>"} in .jap/project.json');

const [W, H] = b.size_mm || [841, 594];
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const base = path.dirname(path.resolve(CWD, file));
const url = (f) => "file:///" + path.resolve(base, f).split(path.sep).join("/");
const cells = (b.items || []).map((it) => {
  const span = `grid-column: span ${it.span || 1}; grid-row: span ${it.rows || 1};`;
  if (it.type === "text") return `<section style="${span}" class="t"><h3>${esc(it.caption)}</h3><p style="font-size:${it.text_mm || 4}mm">${esc(it.text)}</p></section>`;
  return `<figure style="${span}"><div class="img"><img src="${url(it.file)}"></div><figcaption><b>${esc(it.caption)}</b>${it.source ? `<span>${esc(it.source)}</span>` : ""}</figcaption></figure>`;
}).join("");
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@page { size: ${W}mm ${H}mm; margin: 0; }
* { box-sizing: border-box; margin: 0; }
body { width: ${W}mm; height: ${H}mm; padding: 14mm; font-family: "Inter Tight", "Segoe UI", Arial, sans-serif; color: #121212; background: #f4f3ef; display: flex; flex-direction: column; }
header { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 0.6mm solid #121212; padding-bottom: 4mm; margin-bottom: 6mm; }
header h1 { font-size: 13mm; letter-spacing: -0.02em; } header p { font-size: 4.5mm; color: #555; }
main { flex: 1; display: grid; grid-template-columns: repeat(${b.columns || 3}, 1fr); grid-auto-rows: minmax(0, 1fr); gap: 6mm; min-height: 0; }
figure { display: flex; flex-direction: column; min-height: 0; } .img { flex: 1; min-height: 0; background: #fff; display: flex; }
.img img { width: 100%; height: 100%; object-fit: contain; }
figcaption { font-size: 3.6mm; padding-top: 2mm; display: flex; justify-content: space-between; gap: 4mm; } figcaption span { color: #666; }
.t h3 { font-size: 5mm; border-top: 0.4mm solid #e0471f; padding-top: 2mm; margin-bottom: 2mm; } .t p { line-height: 1.35; }
</style></head><body><header><h1>${esc(b.title)}</h1><p>${esc(b.subtitle)}</p></header><main>${cells}</main></body></html>`;

const out = path.resolve(base, outName || path.basename(file, ".json"));
fs.writeFileSync(out + ".html", html);
const pxW = Math.round((W / 25.4) * 150), pxH = Math.round((H / 25.4) * 150); // 150 dpi preview
const run = (args) => execFileSync(chrome, ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files", "--virtual-time-budget=4000", ...args], { stdio: "ignore", timeout: 120000 });
run(["--no-pdf-header-footer", `--print-to-pdf=${out}.pdf`, "file:///" + (out + ".html").split(path.sep).join("/")]);
run([`--window-size=${Math.round(W * 3.78)},${Math.round(H * 3.78)}`, `--force-device-scale-factor=${(pxW / (W * 3.78)).toFixed(3)}`, `--screenshot=${out}.png`, "file:///" + (out + ".html").split(path.sep).join("/")]);
console.log(`board: ${out}.pdf and ${out}.png (${W} x ${H} mm)`);
