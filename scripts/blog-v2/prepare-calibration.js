#!/usr/bin/env node
// Freeze real, immutable examples before asking reviewers for numeric ratings.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { readImmutableRun } = require('./batch-review');

const hash = value => crypto.createHash('sha256').update(value).digest('hex');

function prepareCalibration(entries) {
  if (!Array.isArray(entries) || entries.length < 6) throw new Error('At least six real examples required');
  const samples = entries.map(({ runDir, label }) => {
    if (!['ready', 'held'].includes(label)) throw new Error('Invalid calibration label');
    const run = readImmutableRun(path.resolve(runDir));
    const ready = run.status === 'draft-ready-for-human-review' && run.gate.length === 0 && run.read('review').decision === 'pass';
    if (ready !== (label === 'ready')) throw new Error(`Label contradicts verified run: ${run.id}`);
    if (!run.draft?.body || !run.draft?.title) throw new Error(`Incomplete example: ${run.id}`);
    return {
      id: run.id, runDir: path.resolve(runDir), label, title: run.draft.title,
      articleBodySha256: hash(run.draft.body), runReceiptSha256: run.receiptHash,
      originalDecision: run.read('review').decision, originalGate: run.gate,
    };
  });
  if (new Set(samples.map(sample => sample.articleBodySha256)).size !== samples.length) throw new Error('Duplicate article body in calibration set');
  if (samples.filter(sample => sample.label === 'ready').length < 3 || samples.filter(sample => sample.label === 'held').length < 3) throw new Error('Three ready and three held examples required');
  return { version: 1, createdAt: new Date().toISOString(), rubricVersion: 'opc-blog-editorial-v1', samples };
}

if (require.main === module) {
  const [input, output] = process.argv.slice(2);
  if (!input || !output) { console.error('Usage: prepare-calibration.js examples.json output.json'); process.exitCode = 1; }
  else try {
    const packet = prepareCalibration(JSON.parse(fs.readFileSync(input, 'utf8')));
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(packet, null, 2) + '\n', { mode: 0o600 });
    console.log(JSON.stringify({ samples: packet.samples.length, ready: packet.samples.filter(s => s.label === 'ready').length, held: packet.samples.filter(s => s.label === 'held').length }));
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}

module.exports = { prepareCalibration };
