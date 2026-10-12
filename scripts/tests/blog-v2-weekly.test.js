const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { writeRun } = require('../blog-v2/pipeline');
const { parseOptions, queuedRuns, reviewedRuns, weekStart, runAttempt } = require('../blog-v2/weekly-private');

test('weekly boundary follows New York Monday across UTC and daylight saving time', () => {
  assert.equal(weekStart(new Date('2026-10-11T23:00:00Z')), weekStart(new Date('2026-10-12T01:00:00Z')));
  assert.notEqual(weekStart(new Date('2026-10-12T01:00:00Z')), weekStart(new Date('2026-10-12T13:00:00Z')));
  assert.equal(weekStart(new Date('2026-11-01T05:30:00Z')), weekStart(new Date('2026-11-01T06:30:00Z')));
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
    review: { decision: 'pass' }, gate: [], status: 'draft-ready-for-human-review',
  });
  const calls = [];
  const runner = (script, args) => {
    calls.push(path.basename(script));
    if (script.endsWith('discover-sources.js')) {
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
    assert.match(status.previewSha256, /^[a-f0-9]{64}$/);
    assert.deepEqual(calls, ['discover-sources.js', 'cli.js', 'generate-blog-review-preview.mjs']);
    assert.deepEqual(queuedRuns(out).map(item => item.intentKey), ['commercial-cu:fort-lauderdale']);
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
