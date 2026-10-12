const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { readVerifiedRun } = require('./batch-review');

function readQueue(file) {
  if (!fs.existsSync(file)) return { version: 1, items: [] };
  const queue = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (queue.version !== 1 || !Array.isArray(queue.items)) throw new Error('Invalid blog review queue');
  return queue;
}
function verifyPreview(preview, expected) {
  if (!fs.existsSync(preview) || crypto.createHash('sha256').update(fs.readFileSync(preview)).digest('hex') !== expected) throw new Error('Private preview changed after queueing');
}

function mutateQueue(file, change) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const lock = `${file}.lock`;
  fs.mkdirSync(lock);
  try {
    const queue = readQueue(file);
    const result = change(queue);
    const temporary = `${file}.${process.pid}.tmp`;
    fs.writeFileSync(temporary, JSON.stringify(queue, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
    fs.renameSync(temporary, file);
    return result;
  } finally { fs.rmdirSync(lock); }
}

function enqueueReview(file, articleRun, preview, previewSha256) {
  const run = readVerifiedRun(articleRun);
  if (!preview || !fs.existsSync(preview) || !/^[a-f0-9]{64}$/.test(previewSha256 || '')) throw new Error('Private preview and digest required');
  verifyPreview(preview, previewSha256);
  const item = {
    id: run.id, articleRun: path.resolve(articleRun), articleReceiptHash: run.receiptHash,
    title: run.draft.title, intentKey: run.brief.intentKey, editorialScore: run.editorialScore?.score ?? null,
    preview: path.resolve(preview), previewSha256, state: 'pending', createdAt: new Date().toISOString(),
  };
  return mutateQueue(file, queue => {
    const existing = queue.items.find(entry => entry.id === item.id);
    if (existing) {
      if (existing.articleReceiptHash !== item.articleReceiptHash) throw new Error('Queue item version changed');
      return existing;
    }
    queue.items.push(item);
    return item;
  });
}

function dueNotices(file, now = new Date()) {
  return readQueue(file).items.filter(item => item.state === 'pending'
    || (item.state === 'snoozed' && Date.parse(item.snoozedUntil) <= now.getTime()));
}

function recordAction(file, id, action, { snoozedUntil, now = new Date() } = {}) {
  if (!['notified', 'approved', 'rejected', 'snoozed', 'queued'].includes(action)) throw new Error('Invalid review action');
  return mutateQueue(file, queue => {
    const item = queue.items.find(entry => entry.id === id);
    if (!item) throw new Error('Unknown review item');
    if (['approved', 'rejected'].includes(item.state)) throw new Error('Review decision is final');
    const run = readVerifiedRun(item.articleRun);
    if (run.receiptHash !== item.articleReceiptHash) throw new Error('Article version changed after queueing');
    verifyPreview(item.preview, item.previewSha256);
    if (action === 'snoozed') {
      const until = Date.parse(snoozedUntil);
      if (!Number.isFinite(until) || until <= now.getTime() || until > now.getTime() + 30 * 86400000) throw new Error('Snooze must be within 30 days');
      item.snoozedUntil = new Date(until).toISOString();
    } else delete item.snoozedUntil;
    item.state = action;
    item.updatedAt = now.toISOString();
    return item;
  });
}

module.exports = { readQueue, enqueueReview, dueNotices, recordAction };
