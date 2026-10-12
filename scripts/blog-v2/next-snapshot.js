#!/usr/bin/env node
// Advances a private research batch after an immutable article-ready run.
const fs = require('node:fs');
const { readVerifiedRun } = require('./batch-review');

function nextSnapshot(snapshot, run) {
  if (!snapshot.candidates?.some(candidate => candidate.id === run.brief.id)) throw new Error('Run topic is absent from input snapshot');
  if (snapshot.existing?.some(item => item.intentKey === run.brief.intentKey)) throw new Error('Run intent is already in the inventory');
  return {
    ...snapshot,
    existing: [...snapshot.existing, { id: run.id, title: run.draft.title, intent: run.brief.readerDecision, intentKey: run.brief.intentKey, type: 'queued', receiptHash: run.receiptHash }],
  };
}
function main() {
  const args = process.argv.slice(2);
  if (args.length !== 3) throw new Error('Usage: next-snapshot.js <input-snapshot.json> <article-ready-run-dir> <next-snapshot.json>');
  const [input, runDir, out] = args;
  if (/publish|wordpress|wp-content|wp-admin/i.test(out)) throw new Error('Refusing publication or WordPress output path');
  const snapshot = JSON.parse(fs.readFileSync(input, 'utf8'));
  const run = readVerifiedRun(runDir);
  const next = nextSnapshot(snapshot, run);
  fs.writeFileSync(out, `${JSON.stringify(next, null, 2)}\n`, { flag: 'wx' });
  console.log(JSON.stringify({ out, queuedIntent: run.brief.intentKey, remainingCandidates: next.candidates.length - 1 }));
}
if (require.main === module) try { main(); } catch (error) { console.error(error.message); process.exitCode = 1; }
module.exports = { nextSnapshot };
