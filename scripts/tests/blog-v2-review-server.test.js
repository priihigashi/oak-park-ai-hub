const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const { writeRun } = require('../blog-v2/pipeline');
const { enqueueReview, readQueue } = require('../blog-v2/review-queue');
const { createHandler, notifyDue } = require('../blog-v2/review-server');

test('Mac review page shows private preview and records a CSRF-protected decision once', async () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-review-page-'));
  const queue = path.join(temp, 'queue.json');
  const preview = path.join(temp, 'preview.html');
  fs.writeFileSync(preview, '<html><h1>Exact private preview</h1></html>');
  const hash = crypto.createHash('sha256').update(fs.readFileSync(preview)).digest('hex');
  const run = writeRun(path.join(temp, 'runs'), {
    snapshot: {}, selection: { selected: { id: 'topic' } }, brief: { intentKey: 'topic:broward' },
    draft: { title: '<script>Unsafe title</script>' }, sources: [], review: { decision: 'pass' },
    editorialScore: { score: 81 }, gate: [], status: 'draft-ready-for-human-review',
  });
  const item = enqueueReview(queue, run, preview, hash);
  const server = http.createServer(createHandler(queue, 'test-secret'));
  try {
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    const base = `http://127.0.0.1:${server.address().port}`;
    assert.equal((await fetch(base)).status, 400);
    const home = await (await fetch(`${base}/?token=test-secret`)).text();
    assert.match(home, /&lt;script&gt;Unsafe title&lt;\/script&gt;/);
    assert.doesNotMatch(home, /<script>Unsafe title/);
    assert.match(home, /Pedir ajustes/);
    assert.match(home, /Opção 1 · Dar feedback/);
    assert.match(home, /Opção 2 · Deixar seguir sozinho/);
    assert.match(home, /não precisa abrir esta página nem responder/);
    const shown = await (await fetch(`${base}/preview/${item.id}?token=test-secret`)).text();
    assert.match(shown, /Exact private preview/);
    const denied = await fetch(`${base}/action/${item.id}`, { method: 'POST', body: new URLSearchParams({ token: 'wrong', action: 'approved' }) });
    assert.equal(denied.status, 400);
    assert.equal(readQueue(queue).items[0].state, 'pending');
    const approved = await fetch(`${base}/action/${item.id}`, { method: 'POST', redirect: 'manual', body: new URLSearchParams({ token: 'test-secret', action: 'approved' }) });
    assert.equal(approved.status, 303);
    assert.equal(readQueue(queue).items[0].state, 'approved');
  } finally { await new Promise(resolve => server.close(resolve)); fs.rmSync(temp, { recursive: true, force: true }); }
});

test('Mac notification is emitted once and keeps pending item after notifier failure', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-review-alert-'));
  const queue = path.join(temp, 'queue.json');
  const preview = path.join(temp, 'preview.html');
  fs.writeFileSync(preview, '<html>Private</html>');
  const hash = crypto.createHash('sha256').update(fs.readFileSync(preview)).digest('hex');
  const run = writeRun(path.join(temp, 'runs'), {
    snapshot: {}, selection: { selected: { id: 'topic' } }, brief: { intentKey: 'topic:broward' },
    draft: { title: 'Review me' }, sources: [], review: { decision: 'pass' }, gate: [], status: 'draft-ready-for-human-review',
  });
  enqueueReview(queue, run, preview, hash);
  try {
    assert.throws(() => notifyDue(queue, 'http://127.0.0.1:1/', () => { throw new Error('Mac offline'); }), /Mac offline/);
    assert.equal(readQueue(queue).items[0].state, 'pending');
    let count = 0;
    notifyDue(queue, 'http://127.0.0.1:1/', () => { count += 1; });
    notifyDue(queue, 'http://127.0.0.1:1/', () => { count += 1; });
    assert.equal(count, 1);
    assert.equal(readQueue(queue).items[0].state, 'notified');
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});
