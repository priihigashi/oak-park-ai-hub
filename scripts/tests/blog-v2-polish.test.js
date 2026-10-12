const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const { writeRun } = require('../blog-v2/pipeline');
const { readVerifiedRun } = require('../blog-v2/batch-review');
const { parseOptions, polish } = require('../blog-v2/editorial-polish');

test('editorial polish preserves article and series lineage and independently gates an edited draft', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-polish-'));
  try {
    const priorRun = writeRun(path.join(root, 'articles'), {
      rawSnapshot: { snapshotAt: '2026-10-10T00:00:00Z' }, intake: null,
      snapshot: { snapshotAt: '2026-10-10T00:00:00Z' }, selection: { selected: { id: 'one' } },
      sources: [], brief: { id: 'one', intentKey: 'one', sourceIds: [] }, mediaPlan: { approved: false },
      draft: { title: 'Original', body: 'A private article' }, review: { decision: 'pass', findings: [] }, gate: [], status: 'draft-ready-for-human-review',
    });
    const prior = readVerifiedRun(priorRun);
    const batchAudit = writeRun(path.join(root, 'batches'), {
      snapshot: [{ id: prior.id, receiptHash: prior.receiptHash }], selection: { selected: null },
      runs: [], review: { decision: 'trial_ready', findings: [] }, gate: [], status: 'private-trial-ready',
    });
    const draftFile = path.join(root, 'edited.json');
    fs.writeFileSync(draftFile, JSON.stringify({ title: 'Edited', body: 'Still too short' }));
    let reviewCalls = 0;
    const result = polish({ priorRun, batchAudit, draftFile, out: path.join(root, 'polished'), changeNote: 'Tighten wording' }, () => {
      reviewCalls += 1;
      return { decision: 'pass', findings: [] };
    });
    assert.equal(reviewCalls, 1);
    assert.equal(result.status, 'review-required');
    assert.ok(result.gate.length > 0);
    const lineage = JSON.parse(fs.readFileSync(path.join(result.runDir, 'polishedFrom.json'), 'utf8'));
    assert.equal(lineage.id, prior.id);
    assert.equal(lineage.receiptHash, prior.receiptHash);
    assert.equal(lineage.submittedDraftSha256, crypto.createHash('sha256').update(fs.readFileSync(draftFile)).digest('hex'));
    const weekly = polish({ priorRun, batchAudit: null, draftFile, out: path.join(root, 'weekly-polished'), changeNote: 'Single weekly draft edit' }, () => ({ decision: 'pass', findings: [] }));
    const weeklyLineage = JSON.parse(fs.readFileSync(path.join(weekly.runDir, 'polishedFrom.json'), 'utf8'));
    assert.equal(weeklyLineage.batch, null);
    assert.equal(weekly.status, 'review-required');
    fs.writeFileSync(path.join(batchAudit, 'status.json'), '"batch-hold"\n');
    assert.throws(() => polish({ priorRun, batchAudit, draftFile, out: path.join(root, 'again'), changeNote: 'Retry' }, () => { throw new Error('Must not review'); }), /Batch audit changed/);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('editorial polish refuses publication paths and requires verified subscription route', () => {
  const prior = process.env.OPC_ALLOW_SUBSCRIPTION_CLI;
  process.env.OPC_ALLOW_SUBSCRIPTION_CLI = '1';
  try {
    assert.throws(() => parseOptions(['--prior-run', 'a', '--batch-audit', 'b', '--draft', 'c', '--out', 'wordpress-publish', '--change-note', 'wording']), /Refusing publication/);
  } finally {
    if (prior === undefined) delete process.env.OPC_ALLOW_SUBSCRIPTION_CLI;
    else process.env.OPC_ALLOW_SUBSCRIPTION_CLI = prior;
  }
});
