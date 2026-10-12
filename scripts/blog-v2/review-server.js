#!/usr/bin/env node
const http = require('node:http');
const fs = require('node:fs');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const { readQueue, dueNotices, markPreviewViewed, recordAction } = require('./review-queue');

const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function verifiedPreview(item) {
  const bytes = fs.readFileSync(item.preview);
  if (digest(bytes) !== item.previewSha256) throw new Error('Private preview changed');
  return bytes;
}
function activeItems(queueFile) {
  return readQueue(queueFile).items.filter(item => !['approved', 'rejected'].includes(item.state));
}
function card(item, token) {
  const form = (action, label, extra = '') => `<form method="post" action="/action/${encodeURIComponent(item.id)}"><input type="hidden" name="token" value="${token}"><input type="hidden" name="action" value="${action}">${extra}<button type="submit">${label}</button></form>`;
  const snooze = `<label>Adiar até <input type="datetime-local" name="until" required></label>`;
  const feedback = `<label for="feedback-${escapeHtml(item.id)}">O que precisa mudar?</label><textarea id="feedback-${escapeHtml(item.id)}" name="feedback" minlength="5" maxlength="2000" required placeholder="Ex.: adicionar uma imagem pertinente e alinhar título e texto."></textarea>`;
  const states = { pending: 'aguardando aviso', notified: 'aguardando sua decisão', snoozed: 'adiado', queued: 'na fila', 'needs-revision': 'ajustes solicitados' };
  const score = item.editorialScore == null ? 'Nota editorial ainda não calculada' : `Nota editorial: ${escapeHtml(item.editorialScore)}/100`;
  const actions = item.state === 'needs-revision' ? `<p class="saved-feedback">Seu feedback: ${escapeHtml(item.feedback?.note || '')}</p><p>Esta versão aguarda ajustes e não pode ser aprovada.</p>` : `<div class="actions">${form('approved', 'Aprovar rascunho')}${form('rejected', 'Rejeitar')}${form('queued', 'Deixar na fila')}${form('snoozed', 'Adiar', snooze)}</div><div class="feedback-form">${form('feedback', 'Pedir ajustes', feedback)}</div>`;
  return `<article><h2>${escapeHtml(item.title)}</h2><p>${score} · ${states[item.state] || escapeHtml(item.state)}</p><a class="preview" href="/preview/${encodeURIComponent(item.id)}?token=${token}" target="_blank" rel="noopener noreferrer">Abrir prévia</a>${actions}</article>`;
}
function page(queueFile, token) {
  const items = activeItems(queueFile);
  return `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Revisão do blog OPC</title><style>body{font:16px system-ui;background:#f0ebe3;color:#111;margin:0 auto;max-width:900px;padding:32px}h1{font-size:2rem}article{background:white;border-left:5px solid #cbcc10;padding:24px;margin:18px 0;border-radius:8px}h2{margin-top:0}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}form{display:flex;gap:8px;align-items:center}button,.preview{border:0;border-radius:5px;background:#111;color:white;padding:10px 14px;font:inherit;cursor:pointer;text-decoration:none}.preview{display:inline-block;background:#555}button:hover,.preview:hover{background:#666}label{display:flex;gap:6px;align-items:center}input,textarea{font:inherit}.feedback-form{margin-top:22px;padding-top:18px;border-top:1px solid #ddd}.feedback-form form{display:block}.feedback-form label{display:block;margin-bottom:8px}.feedback-form textarea{display:block;width:100%;min-height:96px;padding:10px;margin-bottom:10px;border:1px solid #aaa;border-radius:5px;resize:vertical}.saved-feedback{padding:12px;background:#f0ebe3;white-space:pre-wrap}</style><h1>Artigos para revisar</h1><p>Abra a prévia antes de decidir. A aprovação registra a versão exata do rascunho; a publicação ainda passa pela etapa de liberação.</p>${items.length ? items.map(item => card(item, token)).join('') : '<p>Nenhum artigo aguardando revisão.</p>'}</html>`;
}
function findItem(queueFile, id) { return readQueue(queueFile).items.find(item => item.id === id); }
function postBody(request) {
  return new Promise((resolve, reject) => {
    let body = '';
    request.on('data', chunk => { body += chunk; if (body.length > 8192) { reject(new Error('Request too large')); request.destroy(); } });
    request.on('end', () => resolve(new URLSearchParams(body)));
    request.on('error', reject);
  });
}
function snoozeDate(value) {
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) throw new Error('Invalid snooze date');
  return new Date(parsed).toISOString();
}
function servePreview(queueFile, id, response) {
  const item = findItem(queueFile, decodeURIComponent(id));
  if (!item) throw new Error('Unknown article');
  markPreviewViewed(queueFile, item.id);
  response.writeHead(200, { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'referrer-policy': 'no-referrer', 'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:;" });
  response.end(verifiedPreview(item));
}
async function serveAction(queueFile, token, id, request, response) {
  const fields = await postBody(request);
  if (fields.get('token') !== token) throw new Error('Invalid request token');
  const action = fields.get('action');
  recordAction(queueFile, decodeURIComponent(id), action, { snoozedUntil: action === 'snoozed' ? snoozeDate(fields.get('until')) : undefined, feedback: fields.get('feedback') });
  response.writeHead(303, { location: `/?token=${token}`, 'cache-control': 'no-store' });
  response.end();
}
function requireGetToken(request, url, token) {
  if (request.method === 'GET' && url.searchParams.get('token') !== token) throw new Error('Invalid review link');
}
async function routeRequest(queueFile, token, request, response) {
  const url = new URL(request.url, 'http://127.0.0.1');
  requireGetToken(request, url, token);
  if (request.method === 'GET' && url.pathname === '/') {
    response.writeHead(200, { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'referrer-policy': 'no-referrer' });
    response.end(page(queueFile, token));
    return;
  }
  const previewId = url.pathname.match(/^\/preview\/([^/]+)$/)?.[1];
  if (request.method === 'GET' && previewId) return servePreview(queueFile, previewId, response);
  const actionId = url.pathname.match(/^\/action\/([^/]+)$/)?.[1];
  if (request.method === 'POST' && actionId) return serveAction(queueFile, token, actionId, request, response);
  response.writeHead(404); response.end('Not found');
}
function createHandler(queueFile, token) {
  return (request, response) => routeRequest(queueFile, token, request, response)
    .catch(error => { response.writeHead(400, { 'content-type': 'text/plain; charset=utf-8' }); response.end(error.message); });
}
function macNotify(item, url) {
  const script = 'on run argv\ndisplay notification (item 1 of argv) with title "OPC Blog" subtitle "Artigo para revisar"\nend run';
  const result = spawnSync('osascript', ['-e', script, `${item.title} — abra a fila para decidir.`], { encoding: 'utf8', timeout: 10000 });
  if (result.error || result.status !== 0) throw new Error(`Mac notification failed: ${result.error?.message || result.stderr}`);
  const opened = spawnSync('open', [url], { encoding: 'utf8', timeout: 10000 });
  if (opened.error || opened.status !== 0) throw new Error(`Review page failed to open: ${opened.error?.message || opened.stderr}`);
}
function notifyDue(queueFile, url, notify = macNotify) {
  for (const item of dueNotices(queueFile)) {
    notify(item, url);
    recordAction(queueFile, item.id, 'notified');
  }
}
function startServer(queueFile, port = 43127, notify = macNotify) {
  const token = crypto.randomBytes(32).toString('hex');
  const server = http.createServer(createHandler(queueFile, token));
  const reviewUrl = () => `http://127.0.0.1:${server.address().port}/?token=${token}`;
  server.listen(port, '127.0.0.1', () => {
    fs.writeFileSync(`${queueFile}.link`, reviewUrl() + '\n', { mode: 0o600 });
    notifyDue(queueFile, reviewUrl(), notify);
  });
  const timer = setInterval(() => notifyDue(queueFile, reviewUrl(), notify), 60000);
  server.on('close', () => clearInterval(timer));
  return server;
}
if (require.main === module) {
  const index = process.argv.indexOf('--queue');
  const queueFile = index < 0 ? null : process.argv[index + 1];
  if (!queueFile) { console.error('Usage: review-server.js --queue private-runs/review-queue.json [--port 43127] [--open]'); process.exitCode = 1; }
  else if (process.argv.includes('--open')) {
    const url = fs.readFileSync(`${queueFile}.link`, 'utf8').trim();
    const opened = spawnSync('open', [url], { encoding: 'utf8', timeout: 10000 });
    if (opened.error || opened.status !== 0) { console.error(opened.error?.message || opened.stderr); process.exitCode = 1; }
  }
  else {
    const portIndex = process.argv.indexOf('--port');
    const port = portIndex < 0 ? 43127 : Number(process.argv[portIndex + 1]);
    startServer(queueFile, port);
  }
}
module.exports = { escapeHtml, page, createHandler, notifyDue, startServer, verifiedPreview };
