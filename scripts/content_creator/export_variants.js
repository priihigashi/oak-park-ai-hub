#!/usr/bin/env node
/**
 * export_variants.js — Screenshot each .slide element as its own PNG.
 * Usage: node export_variants.js <input.html> <output_dir>
 * Each .slide gets its label (v1/v2/v3) or index captured as filename.
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function run(htmlPath, outputDir) {
  const abs = path.resolve(htmlPath);
  if (!fs.existsSync(abs)) { console.error(`Not found: ${abs}`); process.exit(1); }
  fs.mkdirSync(outputDir, { recursive: true });
  const base = path.basename(abs, '.html');

  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const page = await browser.newPage({ viewport: { width: 1200, height: 1400 } });
  await page.goto(`file://${abs}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1800);

  const slides = page.locator('.slide');
  const n = await slides.count();
  console.log(`${n} slides in ${base}`);

  // Naming convention: <color>_<NN>_<slide-name>_<tool>.png (see project_png_naming_convention.md)
  // Color mapping — update per niche / brand when adding more variants
  const COLOR_MAP = {
    v1: 'black',   // Brazil: obsidian
    v2: 'cream',   // Brazil: paper
    v3: 'blue',    // USA archive blue OR OPC lime (override per-project if needed)
  };
  const tool = 'html';
  // Track per-color slide index so numbering restarts per variant set (black_01, black_02... cream_01...)
  const counters = {};
  for (let i = 0; i < n; i++) {
    const el = slides.nth(i);
    const cls = await el.getAttribute('class') || '';
    const variantKey = (cls.match(/\bv\d+\b/) || ['v1'])[0];
    const color = COLOR_MAP[variantKey] || variantKey;
    const slideType = (cls.match(/slide-([a-z0-9]+)/) || [null, String(i+1).padStart(2,'0')])[1];
    counters[color] = (counters[color] || 0) + 1;
    const nn = String(counters[color]).padStart(2, '0');
    const out = path.join(outputDir, `${color}_${nn}_${slideType}_${tool}.png`);
    await el.screenshot({ path: out, type: 'png' });
    const size = fs.statSync(out).size;
    console.log(`  ${color} ${nn} ${slideType} → ${path.basename(out)} (${(size/1024).toFixed(1)} KB)`);
  }

  await browser.close();
}

const [, , input, output] = process.argv;
if (!input || !output) { console.log('Usage: node export_variants.js <input.html> <output_dir>'); process.exit(1); }
run(input, output);
