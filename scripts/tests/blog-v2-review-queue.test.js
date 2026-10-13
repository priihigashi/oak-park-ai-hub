const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const { writeRun } = require('../blog-v2/pipeline');
const { readQueue, enqueueReview, replacePreview, dueNotices, markPreviewViewed, recordAction } = require('../blog-v2/review-queue');

test('private review queue persists one notice and supports snooze and final decision', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-review-queue-'));
  const file = path.join(temp, 'queue.json');
  const preview = path.join(temp, 'preview.html');
  fs.writeFileSync(preview, '<html>Private draft</html>');
  const previewHash = crypto.createHash('sha256').update(fs.readFileSync(preview)).digest('hex');
  const run = writeRun(path.join(temp, 'runs'), {
    snapshot: {}, selection: { selected: { id: 'topic' } }, brief: { intentKey: 'topic:broward', readerDecision: 'Choose path' },
    draft: { title: 'Private topic', body: 'Private body' }, sources: [], review: { decision: 'pass' },
    editorialScore: { score: 84, route: 'human-review' }, gate: [], status: 'draft-ready-for-human-review',
  });
  const now = new Date('2026-10-12T15:00:00Z');
  try {
    const item = enqueueReview(file, run, preview, previewHash);
    assert.equal(item.editorialScore, 84);
    assert.equal(enqueueReview(file, run, preview, previewHash).id, item.id);
    assert.equal(dueNotices(file, now).length, 1);
    recordAction(file, item.id, 'notified', { now });
    assert.equal(dueNotices(file, now).length, 0);
    recordAction(file, item.id, 'snoozed', { now, snoozedUntil: '2026-10-13T15:00:00Z' });
    assert.equal(dueNotices(file, now).length, 0);
    assert.equal(dueNotices(file, new Date('2026-10-13T15:00:00Z')).length, 1);
    assert.throws(() => recordAction(file, item.id, 'approved'), /Open the exact preview/);
    markPreviewViewed(file, item.id);
    recordAction(file, item.id, 'approved', { now: new Date('2026-10-13T16:00:00Z') });
    assert.equal(dueNotices(file).length, 0);
    assert.equal(readQueue(file).items[0].state, 'approved');
    assert.throws(() => recordAction(file, item.id, 'rejected'), /final/);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});

test('queue refuses changed preview and changed article before approval', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-review-queue-hash-'));
  const file = path.join(temp, 'queue.json');
  const preview = path.join(temp, 'preview.html');
  fs.writeFileSync(preview, '<html>Original</html>');
  const previewHash = crypto.createHash('sha256').update(fs.readFileSync(preview)).digest('hex');
  const run = writeRun(path.join(temp, 'runs'), {
    snapshot: {}, selection: { selected: { id: 'topic' } }, brief: { intentKey: 'topic:broward' },
    draft: { title: 'Original article' }, sources: [], review: { decision: 'pass' }, gate: [], status: 'draft-ready-for-human-review',
  });
  try {
    fs.writeFileSync(preview, '<html>Changed</html>');
    assert.throws(() => enqueueReview(file, run, preview, previewHash), /preview changed/);
    fs.writeFileSync(preview, '<html>Original</html>');
    const item = enqueueReview(file, run, preview, previewHash);
    fs.writeFileSync(path.join(run, 'draft.json'), '{"title":"Changed"}');
    assert.throws(() => recordAction(file, item.id, 'approved'), /changed/);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});

test('feedback is attached to the exact private draft and prevents approval of the old version', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-review-feedback-'));
  const file = path.join(temp, 'queue.json');
  const preview = path.join(temp, 'preview.html');
  fs.writeFileSync(preview, '<html>Private draft</html>');
  const previewHash = crypto.createHash('sha256').update(fs.readFileSync(preview)).digest('hex');
  const run = writeRun(path.join(temp, 'runs'), { snapshot: {}, selection: { selected: { id: 'topic' } }, brief: { intentKey: 'topic:broward' }, draft: { title: 'Draft requiring images' }, sources: [], review: { decision: 'pass' }, gate: [], status: 'draft-ready-for-human-review' });
  try {
    const item = enqueueReview(file, run, preview, previewHash);
    assert.throws(() => recordAction(file, item.id, 'feedback', { feedback: '  ' }), /Feedback must contain/);
    recordAction(file, item.id, 'feedback', { feedback: 'Add a relevant image and align title with article text.' });
    const saved = readQueue(file).items[0];
    assert.equal(saved.state, 'needs-revision');
    assert.equal(saved.feedback.articleReceiptHash, item.articleReceiptHash);
    assert.equal(saved.feedback.previewSha256, previewHash);
    assert.match(saved.feedback.note, /relevant image/);
    assert.equal(dueNotices(file).length, 0);
    assert.throws(() => recordAction(file, item.id, 'approved'), /final for this version/);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});

test('a refreshed layout keeps the earlier preview and requires opening the new one before approval', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-review-layout-'));
  const file = path.join(temp, 'queue.json');
  const oldPreview = path.join(temp, 'old.html');
  const newPreview = path.join(temp, 'new.html');
  fs.writeFileSync(oldPreview, '<html>Old layout</html>');
  fs.writeFileSync(newPreview, '<html>Aligned layout</html>');
  const hash = filePath => crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
  const run = writeRun(path.join(temp, 'runs'), { snapshot: {}, selection: { selected: { id: 'topic' } }, brief: { intentKey: 'topic:broward' }, draft: { title: 'Same article' }, sources: [], review: { decision: 'pass' }, gate: [], status: 'draft-ready-for-human-review' });
  try {
    const item = enqueueReview(file, run, oldPreview, hash(oldPreview));
    markPreviewViewed(file, item.id);
    replacePreview(file, item.id, newPreview, hash(newPreview));
    const saved = readQueue(file).items[0];
    assert.equal(saved.previewHistory[0].previewSha256, hash(oldPreview));
    assert.equal(saved.previewSha256, hash(newPreview));
    assert.equal(saved.previewOpenedAt, undefined);
    assert.throws(() => recordAction(file, item.id, 'approved'), /Open the exact preview/);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});
