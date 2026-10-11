#!/usr/bin/env node
// Re-review an edited, article-ready draft without altering its original audit.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { readVerifiedRun } = require('./batch-review');
const { addThreeViewFigure } = require('./three-view-figure');
const { writeRun } = require('./pipeline');
const { reviewGate, claudeReview } = require('./cli');

function option(name, args) { const index = args.indexOf(name); return index < 0 ? null : args[index + 1]; }
function parseOptions(args) {
  const priorRun = option('--prior-run', args), batchAudit = option('--batch-audit', args);
  const draftFile = option('--draft', args), out = option('--out', args), changeNote = option('--change-note', args);
  if (![priorRun, batchAudit, draftFile, out, changeNote].every(Boolean)) throw new Error('Usage: editorial-polish.js --prior-run ready-run --batch-audit ready-series --draft revised-draft.json --out review-bundles --change-note "specific edits"');
  if (/publish|wordpress|wp-content|wp-admin/i.test(out)) throw new Error('Refusing publication or WordPress output path');
  if (process.env.OPC_ALLOW_SUBSCRIPTION_CLI !== '1') throw new Error('Verified subscription CLI flag required');
  return { priorRun: path.resolve(priorRun), batchAudit: path.resolve(batchAudit), draftFile: path.resolve(draftFile), out: path.resolve(out), changeNote };
}
function digest(file) { return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'); }
function readJson(dir, name) { return JSON.parse(fs.readFileSync(path.join(dir, `${name}.json`), 'utf8')); }
function verifiedAudit(dir, prior) {
  const receipt = readJson(dir, 'receipt');
  for (const [file, expected] of Object.entries(receipt.fileHashes || {})) {
    if (digest(path.join(dir, file)) !== expected) throw new Error(`Batch audit changed: ${file}`);
  }
  if (readJson(dir, 'status') !== 'private-trial-ready' || receipt.status !== 'private-trial-ready') throw new Error('Batch is not private-trial-ready');
  if (readJson(dir, 'gate').length) throw new Error('Batch has gate findings');
  const member = readJson(dir, 'snapshot').some(item => item.id === prior.id && item.receiptHash === prior.receiptHash);
  if (!member) throw new Error('Prior article is not in this verified batch');
  return { id: receipt.id, receiptHash: digest(path.join(dir, 'receipt.json')) };
}
function polish(options, reviewer = claudeReview) {
  const prior = readVerifiedRun(options.priorRun);
  const batch = verifiedAudit(options.batchAudit, prior);
  const rawDraft = JSON.parse(fs.readFileSync(options.draftFile, 'utf8'));
  const brief = readJson(options.priorRun, 'brief');
  const sources = readJson(options.priorRun, 'sources');
  const draft = addThreeViewFigure(rawDraft, brief);
  const review = reviewer(brief, draft, sources);
  const gate = reviewGate(draft, brief, sources, review);
  const status = gate.length ? 'review-required' : 'draft-ready-for-human-review';
  const payload = {};
  for (const name of ['rawSnapshot', 'intake', 'snapshot', 'selection', 'sources', 'brief', 'mediaPlan']) {
    const file = path.join(options.priorRun, `${name}.json`);
    if (fs.existsSync(file)) payload[name] = readJson(options.priorRun, name);
  }
  Object.assign(payload, { polishedFrom: { id: prior.id, receiptHash: prior.receiptHash, batch, changeNote: options.changeNote, submittedDraftSha256: digest(options.draftFile) }, draft, review, gate, status });
  const runDir = writeRun(options.out, payload);
  return { runDir, status, gate, selectedId: brief.id, priorRun: prior.id, batchAudit: batch.id };
}
if (require.main === module) {
  try {
    const result = polish(parseOptions(process.argv.slice(2)));
    console.log(JSON.stringify(result));
    if (result.status !== 'draft-ready-for-human-review') process.exitCode = 2;
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
module.exports = { parseOptions, verifiedAudit, polish };
