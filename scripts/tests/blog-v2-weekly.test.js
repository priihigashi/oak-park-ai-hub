const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const { writeRun } = require('../blog-v2/pipeline');
const { readQueue } = require('../blog-v2/review-queue');
const { parseOptions, queuedRuns, heldRuns, reviewedRuns, stagedInput, weekStart, dayStart, runAttempt } = require('../blog-v2/weekly-private');

test('weekly boundary follows New York Monday across UTC and daylight saving time', () => {
  assert.equal(weekStart(new Date('2026-10-11T23:00:00Z')), weekStart(new Date('2026-10-12T01:00:00Z')));
  assert.notEqual(weekStart(new Date('2026-10-12T01:00:00Z')), weekStart(new Date('2026-10-12T13:00:00Z')));
  assert.equal(weekStart(new Date('2026-11-01T05:30:00Z')), weekStart(new Date('2026-11-01T06:30:00Z')));
});

test('cadence allows one attempt per New York day', () => {
  assert.equal(dayStart(new Date('2026-10-14T03:30:00Z')), dayStart(new Date('2026-10-13T13:00:00Z')));
  assert.notEqual(dayStart(new Date('2026-10-14T13:00:00Z')), dayStart(new Date('2026-10-13T13:00:00Z')));
});

test('weekly private coordinator links verified research, article, and preview without publishing', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-weekly-'));
  const input = path.join(temp, 'ideas.json');
  const out = path.join(temp, 'private');
  const siteFrontend = path.join(temp, 'site', 'frontend');
  fs.mkdirSync(siteFrontend, { recursive: true });
  fs.writeFileSync(input, JSON.stringify({ snapshotAt: new Date().toISOString(), candidates: [], existing: [], sources: [] }));
  const articleRun = writeRun(path.join(temp, 'fixture-runs'), {
    snapshot: { snapshotAt: new Date().toISOString() }, selection: { selected: { id: 'topic-1' } },
    brief: { intentKey: 'commercial-cu:fort-lauderdale', readerDecision: 'Choose the approval track' },
    draft: { title: 'CU and work approval', body: 'A private draft.' }, sources: [],
    review: { decision: 'pass' }, editorialScore: { score: 88, route: 'human-review' }, gate: [], status: 'draft-ready-for-human-review',
  });
  const calls = [];
  const runner = (script, args) => {
    calls.push(path.basename(script));
    if (script.endsWith('discover-sources.js')) {
      if (calls.filter(name => name === 'discover-sources.js').length === 2) return { output: { status: 'research-hold', sourceCount: 0, runDir: path.join(temp, 'research-hold') } };
      const snapshot = path.join(temp, 'prepared.json');
      fs.writeFileSync(snapshot, '{}');
      return { output: { status: 'source-shortlist-ready', sourceCount: 2, runDir: path.join(temp, 'research-receipt'), snapshot } };
    }
    if (script.endsWith('cli.js')) return { output: { status: 'draft-ready-for-human-review', runDir: articleRun, selectedId: 'topic-1' } };
    fs.writeFileSync(args[1], '<html>Private preview</html>');
    return { output: args[1] };
  };
  try {
    const status = runAttempt({ input, siteFrontend, out }, runner);
    assert.equal(status.status, 'ready-for-human-review');
    assert.equal(status.editorialScore, 88);
    assert.match(status.previewSha256, /^[a-f0-9]{64}$/);
    assert.deepEqual(calls, ['discover-sources.js', 'cli.js', 'generate-blog-review-preview.mjs', 'discover-sources.js']);
    assert.deepEqual(queuedRuns(out).map(item => item.intentKey), ['commercial-cu:fort-lauderdale']);
    assert.deepEqual(queuedRuns(out).map(item => item.editorialScore), [88]);
    assert.equal(readQueue(path.join(out, 'review-queue.json')).items[0].state, 'pending');
    assert.equal(fs.existsSync(path.join(out, '.weekly-private.lock')), false);
    const second = runAttempt({ input, siteFrontend, out }, () => { throw new Error('A second draft should not start this week'); });
    assert.equal(second.status, 'already-prepared-this-week');
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});

test('weekly coordinator records research hold and refuses publication paths', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-weekly-hold-'));
  const input = path.join(temp, 'ideas.json');
  const out = path.join(temp, 'private');
  fs.writeFileSync(input, JSON.stringify({ snapshotAt: new Date().toISOString(), candidates: [], existing: [], sources: [] }));
  const previous = process.env.OPC_ALLOW_SUBSCRIPTION_CLI;
  process.env.OPC_ALLOW_SUBSCRIPTION_CLI = '1';
  try {
    assert.throws(() => parseOptions(['--input', input, '--site-frontend', temp, '--out', path.join(temp, 'wordpress-publish')]), /Refusing publication/);
    const status = runAttempt({ input, siteFrontend: temp, out }, () => ({ output: { status: 'research-hold', sourceCount: 0, runDir: path.join(temp, 'research') } }));
    assert.equal(status.status, 'research-hold');
    assert.equal(queuedRuns(out).length, 0);
    const second = runAttempt({ input, siteFrontend: temp, out }, () => { throw new Error('Blocked week must not call a model again'); });
    assert.equal(second.status, 'already-attempted-this-week');
    assert.equal(second.priorStatus, 'research-hold');
  } finally {
    if (previous === undefined) delete process.env.OPC_ALLOW_SUBSCRIPTION_CLI;
    else process.env.OPC_ALLOW_SUBSCRIPTION_CLI = previous;
    fs.rmSync(temp, { recursive: true, force: true });
  }
});

test('held article triggers a different topic and continues after a reviewable draft', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-weekly-retry-'));
  const input = path.join(temp, 'ideas.json');
  const out = path.join(temp, 'private');
  fs.writeFileSync(input, JSON.stringify({ snapshotAt: new Date().toISOString(), candidates: [], existing: [], sources: [] }));
  const makeRun = (id, status) => writeRun(path.join(temp, 'articles'), {
    snapshot: { snapshotAt: new Date().toISOString() }, selection: { selected: { id } },
    brief: { intentKey: `${id}:broward`, readerDecision: `Decide ${id}` },
    draft: { title: `Draft ${id}`, body: 'Private article.' }, sources: [],
    review: { decision: status === 'draft-ready-for-human-review' ? 'pass' : 'revise' },
    gate: status === 'draft-ready-for-human-review' ? [] : ['review-blocked'], status,
  });
  const heldRun = makeRun('topic-a', 'revision-gate-failed');
  const readyRun = makeRun('topic-b', 'draft-ready-for-human-review');
  let searches = 0;
  try {
    const result = runAttempt({ input, siteFrontend: temp, out }, (script, args) => {
      if (script.endsWith('discover-sources.js')) {
        const staged = JSON.parse(fs.readFileSync(args[1], 'utf8'));
        assert.deepEqual(staged.existing.map(item => item.intentKey), searches === 0 ? [] : searches === 1 ? ['topic-a:broward'] : ['topic-b:broward', 'topic-a:broward']);
        searches += 1;
        if (searches === 3) return { output: { status: 'research-hold', sourceCount: 0, runDir: path.join(temp, 'research-3') } };
        return { output: { status: 'source-shortlist-ready', sourceCount: 2, runDir: path.join(temp, `research-${searches}`), snapshot: input } };
      }
      if (script.endsWith('cli.js')) return { output: searches === 1
        ? { status: 'revision-gate-failed', runDir: heldRun, selectedId: 'topic-a', gate: ['review-blocked'] }
        : { status: 'draft-ready-for-human-review', runDir: readyRun, selectedId: 'topic-b' } };
      fs.writeFileSync(args[1], '<html>Private preview</html>');
      return { output: args[1] };
    });
    assert.equal(searches, 3);
    assert.equal(result.status, 'ready-for-human-review');
    assert.equal(result.attempt, 2);
    assert.deepEqual(heldRuns(out).map(item => item.intentKey), ['topic-a:broward']);
    assert.deepEqual(queuedRuns(out).map(item => item.intentKey), ['topic-b:broward']);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});

test('reviewable drafts stay queued while the coordinator tries distinct topics up to three attempts', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-weekly-ready-retry-'));
  const input = path.join(temp, 'ideas.json');
  const out = path.join(temp, 'private');
  fs.writeFileSync(input, JSON.stringify({ candidates: [], existing: [], sources: [] }));
  const runs = ['a', 'b', 'c'].map(id => writeRun(path.join(temp, 'articles'), {
    snapshot: { snapshotAt: new Date().toISOString() }, selection: { selected: { id } },
    brief: { intentKey: `${id}:broward`, readerDecision: `Decide ${id}` },
    draft: { title: `Draft ${id}`, body: 'Private article.' },
    review: { decision: 'pass' }, sources: [], gate: [], status: 'draft-ready-for-human-review',
  }));
  let searches = 0;
  try {
    const result = runAttempt({ input, siteFrontend: temp, out }, (script, args) => {
      if (script.endsWith('discover-sources.js')) {
        const staged = JSON.parse(fs.readFileSync(args[1], 'utf8'));
        assert.deepEqual(staged.existing.map(item => item.intentKey), ['a', 'b', 'c'].slice(0, searches).map(id => `${id}:broward`));
        searches += 1;
        return { output: { status: 'source-shortlist-ready', sourceCount: 2, runDir: path.join(temp, `research-${searches}`), snapshot: input } };
      }
      if (script.endsWith('cli.js')) return { output: { status: 'draft-ready-for-human-review', runDir: runs[searches - 1], selectedId: ['a', 'b', 'c'][searches - 1] } };
      fs.writeFileSync(args[1], '<html>Private preview</html>');
      return { output: args[1] };
    });
    assert.equal(searches, 3);
    assert.equal(result.status, 'ready-for-human-review');
    assert.equal(queuedRuns(out).length, 3);
    assert.equal(readQueue(path.join(out, 'review-queue.json')).items.length, 3);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});

test('weekly retries stop after three distinct held articles', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-weekly-cap-'));
  const input = path.join(temp, 'ideas.json');
  const out = path.join(temp, 'private');
  fs.writeFileSync(input, JSON.stringify({ snapshotAt: new Date().toISOString(), candidates: [], existing: [], sources: [] }));
  const runs = ['a', 'b', 'c'].map(id => writeRun(path.join(temp, 'articles'), {
    snapshot: { snapshotAt: new Date().toISOString() }, selection: { selected: { id } },
    brief: { intentKey: `${id}:broward`, readerDecision: `Decide ${id}` },
    draft: { title: `Held ${id}`, body: 'Private article.' },
    gate: ['review-blocked'], status: 'revision-gate-failed',
  }));
  let searches = 0;
  try {
    const result = runAttempt({ input, siteFrontend: temp, out }, script => {
      if (script.endsWith('discover-sources.js')) {
        searches += 1;
        return { output: { status: 'source-shortlist-ready', sourceCount: 1, runDir: path.join(temp, `research-${searches}`), snapshot: input } };
      }
      return { output: { status: 'revision-gate-failed', runDir: runs[searches - 1], selectedId: ['a', 'b', 'c'][searches - 1], gate: ['review-blocked'] } };
    });
    assert.equal(result.status, 'article-hold');
    assert.equal(result.attempt, 3);
    assert.equal(searches, 3);
    assert.equal(heldRuns(out).length, 3);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});

test('held article intent joins next research input only after receipt verification', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-weekly-held-'));
  const out = path.join(temp, 'private');
  const run = writeRun(path.join(temp, 'articles'), {
    snapshot: { snapshotAt: new Date().toISOString() }, selection: { selected: { id: 'retail' } },
    brief: { intentKey: 'retail-accessibility:broward', readerDecision: 'Choose a scope' },
    draft: { title: 'Held retail article', body: 'Do not publish.' },
    gate: ['independent-review-blocked'], status: 'revision-gate-failed',
  });
  const attempt = path.join(out, 'attempt');
  fs.mkdirSync(attempt, { recursive: true });
  const statusPath = path.join(attempt, 'status.json');
  fs.writeFileSync(statusPath, JSON.stringify({ status: 'article-hold', articleRun: run, createdAt: new Date().toISOString() }));
  const hash = crypto.createHash('sha256').update(fs.readFileSync(statusPath)).digest('hex');
  fs.writeFileSync(path.join(attempt, 'receipt.json'), JSON.stringify({ statusSha256: hash }));
  try {
    const held = heldRuns(out);
    assert.deepEqual(held.map(item => item.intentKey), ['retail-accessibility:broward']);
    assert.deepEqual(stagedInput({ existing: [] }, held).existing.map(item => item.intentKey), ['retail-accessibility:broward']);
    fs.writeFileSync(path.join(run, 'draft.json'), '{}');
    assert.throws(() => heldRuns(out), /Held article changed after receipt/);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});

test('weekly coordinator preserves a failed attempt and releases its lock', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-weekly-fail-'));
  const input = path.join(temp, 'ideas.json');
  const out = path.join(temp, 'private');
  fs.writeFileSync(input, JSON.stringify({ snapshotAt: new Date().toISOString(), candidates: [], existing: [], sources: [] }));
  try {
    assert.throws(() => runAttempt({ input, siteFrontend: temp, out }, () => { throw new Error('research unavailable'); }), /research unavailable/);
    const attempts = fs.readdirSync(out).filter(name => !name.startsWith('.'));
    assert.equal(attempts.length, 1);
    assert.equal(JSON.parse(fs.readFileSync(path.join(out, attempts[0], 'status.json'))).status, 'failed');
    assert.equal(fs.existsSync(path.join(out, '.weekly-private.lock')), false);
    const second = runAttempt({ input, siteFrontend: temp, out }, () => { throw new Error('Failed week must not call a model again'); });
    assert.equal(second.status, 'already-attempted-this-week');
    assert.equal(second.priorStatus, 'failed');
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});


test('weekly research imports only receipt-verified private review topics before model calls', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-weekly-reviewed-'));
  const input = path.join(temp, 'ideas.json');
  const reviewRunsFile = path.join(temp, 'reviewed-runs.json');
  const out = path.join(temp, 'private');
  fs.writeFileSync(input, JSON.stringify({ snapshotAt: new Date().toISOString(), candidates: [], existing: [], sources: [] }));
  const runDir = writeRun(path.join(temp, 'fixture-runs'), {
    snapshot: { snapshotAt: new Date().toISOString() }, selection: { selected: { id: 'topic-1' } },
    brief: { intentKey: 'lead-safe:florida', readerDecision: 'Choose a certified firm' },
    draft: { title: 'Lead-safe hiring', body: 'A private draft.' }, sources: [],
    review: { decision: 'pass' }, gate: [], status: 'draft-ready-for-human-review',
  });
  fs.writeFileSync(reviewRunsFile, JSON.stringify([path.relative(temp, runDir)]));
  try {
    assert.deepEqual(reviewedRuns(reviewRunsFile).map(item => item.intentKey), ['lead-safe:florida']);
    const status = runAttempt({ input, siteFrontend: temp, out, reviewRunsFile }, (script, args) => {
      const staged = JSON.parse(fs.readFileSync(args[1], 'utf8'));
      assert.deepEqual(staged.existing.map(item => item.intentKey), ['lead-safe:florida']);
      return { output: { status: 'research-hold', sourceCount: 0, runDir: path.join(temp, 'research') } };
    });
    assert.equal(status.queuedIntentCount, 1);
    fs.writeFileSync(path.join(runDir, 'draft.json'), '{}');
    assert.throws(() => reviewedRuns(reviewRunsFile), /hash|changed|receipt/i);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});
