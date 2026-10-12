#!/usr/bin/env node
// One private research -> draft -> preview attempt. No publication operation exists here.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const { readVerifiedRun } = require('./batch-review');

function option(name, args) {
  const index = args.indexOf(name);
  return index < 0 ? null : args[index + 1];
}
function parseOptions(args) {
  const input = option('--input', args);
  const siteFrontend = option('--site-frontend', args);
  const out = option('--out', args);
  const suggestionsFile = option('--research-suggestions-file', args);
  const reviewRunsFile = option('--review-runs-file', args);
  if (!input || !siteFrontend || !out) throw new Error('Usage: weekly-private.js --input snapshot.json --site-frontend site/frontend --out private-runs [--research-suggestions-file saved.json] [--review-runs-file reviewed-runs.json]');
  if (/publish|wordpress|wp-content|wp-admin/i.test(out)) throw new Error('Refusing publication or WordPress output path');
  if (process.env.OPC_ALLOW_SUBSCRIPTION_CLI !== '1') throw new Error('Verified subscription CLI flag required');
  return { input: path.resolve(input), siteFrontend: path.resolve(siteFrontend), out: path.resolve(out), suggestionsFile, reviewRunsFile: reviewRunsFile ? path.resolve(reviewRunsFile) : null };
}
function digestFile(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}
function commandFailure(result, script) {
  return path.basename(script) + ' failed: ' + (result.error?.message || result.stderr || result.stdout || '').slice(0, 600);
}
function command(script, args, { timeout = 600000, json = true } = {}) {
  const result = spawnSync(process.execPath, [script, ...args], { encoding: 'utf8', timeout, maxBuffer: 4 * 1024 * 1024, env: process.env });
  if (result.error || ![0, 2].includes(result.status)) throw new Error(commandFailure(result, script));
  const lines = result.stdout.trim().split('\n').filter(Boolean);
  const output = json ? JSON.parse(lines.at(-1)) : lines.at(-1);
  return { output, exitCode: result.status };
}
function readAttemptStatus(file) {
  const receipt = JSON.parse(fs.readFileSync(path.join(path.dirname(file), 'receipt.json'), 'utf8'));
  if (digestFile(file) !== receipt.statusSha256) throw new Error('Weekly attempt status changed after receipt');
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}
function queuedRuns(out) {
  if (!fs.existsSync(out)) return [];
  const items = [];
  for (const name of fs.readdirSync(out)) {
    const statusPath = path.join(out, name, 'status.json');
    if (!fs.existsSync(statusPath)) continue;
    const status = readAttemptStatus(statusPath);
    if (status.status !== 'ready-for-human-review') continue;
    const run = readVerifiedRun(status.articleRun);
    items.push({ id: 'queued:' + run.id, intentKey: run.brief.intentKey, title: run.draft.title, intent: run.brief.readerDecision, type: 'queued', receiptHash: run.receiptHash });
  }
  return items;
}
function reviewedRuns(file) {
  if (!file) return [];
  const paths = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (!Array.isArray(paths) || !paths.every(item => typeof item === 'string' && item.trim())) throw new Error('Review runs file must be a JSON array of run paths');
  return paths.map(item => {
    const run = readVerifiedRun(path.resolve(path.dirname(file), item));
    return { id: 'reviewed:' + run.id, intentKey: run.brief.intentKey, title: run.draft.title, intent: run.brief.readerDecision, type: 'reviewed-private', receiptHash: run.receiptHash };
  });
}
function weekStart(date) {
  const day = date.getUTCDay();
  return Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate() - ((day + 6) % 7));
}
function preparedThisWeek(out, now = new Date()) {
  if (!fs.existsSync(out)) return null;
  for (const name of fs.readdirSync(out)) {
    const file = path.join(out, name, 'status.json');
    if (!fs.existsSync(file)) continue;
    const status = readAttemptStatus(file);
    if (status.status === 'ready-for-human-review' && weekStart(new Date(status.createdAt)) === weekStart(now)) return status;
  }
  return null;
}
function attemptedThisWeek(out, now = new Date()) {
  if (!fs.existsSync(out)) return null;
  for (const name of fs.readdirSync(out).sort().reverse()) {
    const file = path.join(out, name, 'status.json');
    if (!fs.existsSync(file)) continue;
    const status = readAttemptStatus(file);
    if (['ready-for-human-review', 'research-hold', 'article-hold', 'failed'].includes(status.status)
      && weekStart(new Date(status.createdAt)) === weekStart(now)) return status;
  }
  return null;
}
function skippedAttempt(prior) {
  return {
    status: prior.status === 'ready-for-human-review' ? 'already-prepared-this-week' : 'already-attempted-this-week',
    priorStatus: prior.status,
    priorArticleRun: prior.articleRun || null,
  };
}
function stagedInput(raw, queued) {
  const existing = [...(raw.existing || [])];
  const seen = new Set(existing.map(item => item.intentKey).filter(Boolean));
  for (const item of queued) if (!seen.has(item.intentKey)) { existing.push(item); seen.add(item.intentKey); }
  return { ...raw, snapshotAt: new Date().toISOString(), existing };
}
function writeStatus(dir, status) {
  const stamped = { ...status, createdAt: new Date().toISOString() };
  const file = path.join(dir, 'status.json');
  fs.writeFileSync(file, JSON.stringify(stamped, null, 2) + '\n', { flag: 'wx' });
  fs.writeFileSync(path.join(dir, 'receipt.json'), JSON.stringify({ rulesVersion: 'weekly-private-v1', statusSha256: digestFile(file) }, null, 2) + '\n', { flag: 'wx' });
  return stamped;
}
function runAttempt(options, runner = command) {
  const raw = JSON.parse(fs.readFileSync(options.input, 'utf8'));
  fs.mkdirSync(options.out, { recursive: true });
  const lock = path.join(options.out, '.weekly-private.lock');
  fs.mkdirSync(lock);
  let dir;
  try {
    dir = path.join(options.out, new Date().toISOString().replace(/[:.]/g, '-') + '-' + crypto.randomBytes(4).toString('hex'));
    fs.mkdirSync(dir);
    const queued = [...queuedRuns(options.out), ...reviewedRuns(options.reviewRunsFile)];
    const prior = attemptedThisWeek(options.out);
    if (prior) return writeStatus(dir, skippedAttempt(prior));
    const staged = path.join(dir, 'input.json');
    fs.writeFileSync(staged, JSON.stringify(stagedInput(raw, queued), null, 2) + '\n', { flag: 'wx' });
    const researchArgs = ['--input', staged, '--site-frontend', options.siteFrontend, '--out', path.join(dir, 'research')];
    if (options.suggestionsFile) researchArgs.push('--suggestions-file', path.resolve(options.suggestionsFile));
    const research = runner(path.join(__dirname, 'discover-sources.js'), researchArgs).output;
    const base = { inputSha256: digestFile(staged), researchRun: research.runDir, sourceCount: research.sourceCount, queuedIntentCount: queued.length };
    if (research.status !== 'source-shortlist-ready') return writeStatus(dir, { ...base, status: 'research-hold' });
    const article = runner(path.join(__dirname, 'cli.js'), ['--input', research.snapshot, '--site-frontend', options.siteFrontend, '--out', path.join(dir, 'drafts'), '--provider', 'codex']).output;
    if (article.status !== 'draft-ready-for-human-review') return writeStatus(dir, { ...base, articleRun: article.runDir, status: 'article-hold', gate: article.gate });
    const articleRun = readVerifiedRun(article.runDir);
    const preview = path.join(dir, 'preview.html');
    runner(path.join(options.siteFrontend, 'scripts/generate-blog-review-preview.mjs'), [article.runDir, preview], { json: false });
    return writeStatus(dir, { ...base, articleRun: article.runDir, articleReceiptHash: articleRun.receiptHash, selectedId: article.selectedId, intentKey: articleRun.brief.intentKey, preview, previewSha256: digestFile(preview), status: 'ready-for-human-review' });
  } catch (error) {
    if (dir && !fs.existsSync(path.join(dir, 'status.json'))) writeStatus(dir, { status: 'failed', error: error.message });
    throw error;
  } finally { fs.rmdirSync(lock); }
}
if (require.main === module) {
  try {
    const status = runAttempt(parseOptions(process.argv.slice(2)));
    console.log(JSON.stringify(status));
    if (status.status !== 'ready-for-human-review') process.exitCode = 2;
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
module.exports = { parseOptions, queuedRuns, reviewedRuns, preparedThisWeek, attemptedThisWeek, stagedInput, runAttempt };
