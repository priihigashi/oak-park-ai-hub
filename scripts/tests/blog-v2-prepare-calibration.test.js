const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { writeRun } = require('../blog-v2/pipeline');
const { prepareCalibration } = require('../blog-v2/prepare-calibration');

test('calibration packet requires distinct immutable real labels and rejects a false ready label', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-calibration-'));
  try {
    const entries = Array.from({ length: 6 }, (_, i) => {
      const ready = i < 3;
      const runDir = writeRun(root, {
        snapshot: {}, selection: { selected: { id: `topic-${i}` } }, brief: { intentKey: `topic-${i}` },
        draft: { title: `Article ${i}`, body: `Distinct body ${i}` }, sources: [],
        review: { decision: ready ? 'pass' : 'revise' },
        gate: ready ? [] : ['independent-review-blocked'],
        status: ready ? 'draft-ready-for-human-review' : 'review-required',
      });
      return { runDir, label: ready ? 'ready' : 'held' };
    });
    const packet = prepareCalibration(entries);
    assert.equal(packet.samples.length, 6);
    assert.equal(packet.samples.filter(sample => sample.label === 'held').length, 3);
    assert.throws(() => prepareCalibration([{ ...entries[0], label: 'held' }, ...entries.slice(1)]), /Label contradicts/);
    assert.throws(() => prepareCalibration([entries[0], entries[0], ...entries.slice(2)]), /Duplicate article body/);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
