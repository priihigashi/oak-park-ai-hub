#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const { selectTopic, validateDraft, writeRun, sha } = require('./pipeline');
const { intakeIdeas } = require('./intake');

function option(name) { const i = process.argv.indexOf(name); return i < 0 ? null : process.argv[i + 1]; }
function parseJson(text, label) { try { return JSON.parse(text.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '')); } catch (error) { throw new Error(`${label} did not return JSON: ${error.message}`); } }
function textOnly(html) { return html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, ' ').replace(/<style[^>]*>[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' '); }
function excerptTerms(excerpt) {
  return [...new Set(excerpt.toLowerCase().split(/\W+/).filter(w => w.length > 5))];
}
function passageCandidates(body, terms) {
  const lower = body.toLowerCase();
  const passages = [];
  for (const term of terms) {
    let position = 0;
    for (let count = 0; count < 20; count += 1) {
      position = lower.indexOf(term, position);
      if (position < 0) break;
      passages.push(body.slice(Math.max(0, position - 300), position + 1300));
      position += term.length;
    }
  }
  return passages;
}
function matchedPassage(source, body) {
  const terms = excerptTerms(source.excerpt);
  const passages = passageCandidates(body, terms);
  const score = passage => terms.filter(term => passage.toLowerCase().includes(term)).length / terms.length;
  passages.sort((a, b) => score(b) - score(a));
  if (!passages.length || score(passages[0]) < 0.5) throw new Error(`Source ${source.id} excerpt is not supported by a retrieved passage`);
  return passages[0];
}
async function fetchOfficialSource(source) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  let response;
  try { response = await fetch(source.url, { signal: controller.signal, headers: { 'user-agent': 'OPC-Blog-Research/2.0' } }); }
  finally { clearTimeout(timeout); }
  if (!response.ok) throw new Error(`Source ${source.id} returned HTTP ${response.status}`);
  const body = textOnly((await response.text()).slice(0, 500000));
  if (body.length < 100) throw new Error(`Source ${source.id} has insufficient retrieved text`);
  const retrievedExcerpt = matchedPassage(source, body);
  return { ...source, retrieval: 'http', httpStatus: response.status, retrievedAt: new Date().toISOString(), contentDigest: sha(body), retrievedExcerpt };
}
async function verifySource(source) {
  if (source.access !== 'internal-preverified') return fetchOfficialSource(source);
  if (![source.evidenceId, source.verifiedBy, source.excerpt, source.capturedAt].every(Boolean)) throw new Error(`Internal source ${source.id} lacks verification record`);
  return { ...source, retrieval: 'internal-preverified', contentDigest: sha(source.excerpt) };
}
async function verifySources(sources) {
  const verified = [];
  for (const source of sources) verified.push(await verifySource(source));
  return verified;
}
function runModel(program, args, prompt, label) {
  const safeEnv = Object.fromEntries(Object.entries(process.env).filter(([key]) => !/^(WP_|WORDPRESS_|PEXELS_API_KEY|GOOGLE_SA_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|CLAUDE_KEY_4_CONTENT)/i.test(key)));
  const result = spawnSync(program, args, { input: prompt, encoding: 'utf8', timeout: 180000, maxBuffer: 4 * 1024 * 1024, env: safeEnv });
  if (result.error || result.status !== 0) throw new Error(`${label} CLI unavailable or failed: ${(result.error?.message || result.stderr || '').slice(0, 500)}`);
  return result.stdout.trim();
}
function draftPrompt(brief, sources) {
  return `Return ONLY JSON with title, slug, category, description, body (Markdown using the site's existing post format), claims [{id,text,sourceId,evidence,checkedAt,status:"verified"}], visuals [{type,alt,provenance,rights}]. Write a complete useful article for Oak Park Construction readers. Target 450–650 visible body words when the sources support them, without padding; fewer than 400 words fails the editorial floor. If the evidence cannot support a useful full answer, do not invent detail to meet length. Scope is ${brief.service} in ${brief.area}. Question: ${brief.question}. Reader decision: ${brief.readerDecision}. Sources: ${JSON.stringify(sources)}. Cite consequential factual claims inline using Markdown links to the exact supporting primary source and list each in claims. Each claim text must appear verbatim in the body; each numeric claim must reproduce a number visible in its cited source excerpt. Cite only what the supplied source excerpt directly supports; omit unsupported code, permit, legal, price, or technical assertions. No invented OPC projects, commercial results, numbers, guarantees, license numbers, or stock photo claims. One topic-specific CTA. No publication or WordPress instructions.`;
}
function reviewPrompt(brief, draft, sources) {
  return `Act as an independent OPC editorial and factual reviewer. Return ONLY JSON: {"decision":"pass"|"revise","findings":[{"severity":"blocker"|"major"|"minor","issue":"...","claimId":"... or null","evidence":"..."}],"summary":"..."}. Verify every consequential assertion against the supplied source excerpts, flag source relevance gaps, fabricated OPC experience or commercial claims, bad area/service scope, duplicate intent, incomplete reader answer, and unsupported numbers. Do not assume citations prove their claims. Brief: ${JSON.stringify(brief)}. Sources: ${JSON.stringify(sources)}. Draft: ${JSON.stringify(draft)}`;
}
function revisionPrompt(brief, sources, draft, review) {
  return `Return ONLY a complete revised draft JSON with the same schema as the original: title, slug, category, description, body (Markdown), claims, visuals. This is the sole repair attempt. Address every independent review finding with source evidence or remove unsupported text; do not silently preserve uncited consequential claims. Keep a useful answer of at least 400 visible words without padding or invention. Preserve the reader decision and approved scope. Do not add publication instructions. Brief: ${JSON.stringify(brief)}. Verified sources: ${JSON.stringify(sources)}. Original draft: ${JSON.stringify(draft)}. Independent findings: ${JSON.stringify(review)}`;
}
function needsRevision(review) {
  return review?.decision === 'revise' || review?.findings?.some(f => ['major', 'blocker'].includes(f.severity));
}
function readRunFile(dir, name) { return JSON.parse(fs.readFileSync(path.join(dir, `${name}.json`), 'utf8')); }
function loadPriorRun(dir) {
  const receipt = readRunFile(dir, 'receipt');
  for (const [name, expected] of Object.entries(receipt.fileHashes)) {
    const actual = crypto.createHash('sha256').update(fs.readFileSync(path.join(dir, name))).digest('hex');
    if (actual !== expected) throw new Error(`Prior run hash mismatch: ${name}`);
  }
  if (receipt.status !== 'review-required') throw new Error('Only a blocked review-required run may be resumed');
  if (receipt.fileHashes['revision.json']) throw new Error('Prior run already used its one revision attempt');
  if (!needsRevision(readRunFile(dir, 'review'))) throw new Error('Prior run has no independent-review revision finding');
  return { rawSnapshot: readRunFile(dir, 'rawSnapshot'), intake: readRunFile(dir, 'intake'), snapshot: readRunFile(dir, 'snapshot'), selection: readRunFile(dir, 'selection'), sources: readRunFile(dir, 'sources'), brief: readRunFile(dir, 'brief'), draft: readRunFile(dir, 'draft'), review: readRunFile(dir, 'review'), priorRun: { id: receipt.id, receiptHash: crypto.createHash('sha256').update(fs.readFileSync(path.join(dir, 'receipt.json'))).digest('hex'), mode: 'revision-only' } };
}
function prepareContext(options) {
  if (options.resumeRun) return loadPriorRun(options.resumeRun);
  const rawSnapshot = JSON.parse(fs.readFileSync(options.input, 'utf8'));
  const { intake, snapshot, selection } = prepareSelection(rawSnapshot);
  return { rawSnapshot, intake, snapshot, selection };
}
async function main() {
  const options = parseOptions();
  const context = prepareContext(options);
  const { rawSnapshot, intake, snapshot, selection, priorRun } = context;
  const sources = priorRun ? context.sources : await verifySources(snapshot.sources.filter(s => selection.selected.sourceIds.includes(s.id)));
  const brief = priorRun ? context.brief : { ...selection.selected, selectedAutonomously: true, selectionScore: selection.score, sourceIds: sources.map(s => s.id), rulesVersion: 'blog-v2-2026-10-10' };
  const bundle = generateBundle(options.provider, brief, sources, priorRun ? context : null);
  const { draft, review } = bundle;
  const gate = reviewGate(draft, brief, sources, review);
  const status = gate.length ? 'review-required' : 'draft-ready-for-human-review';
  const runDir = writeRun(options.out, { rawSnapshot, intake, snapshot, selection, sources, brief, ...bundle, ...(priorRun ? { priorRun } : {}), gate, status });
  console.log(JSON.stringify({ runDir, selectedId: brief.id, status, gate, provider: options.provider, revisionAttempted: Boolean(bundle.revisedDraft) }));
  if (gate.length) process.exitCode = 2;
}
function parseOptions() {
  const input = option('--input'), resumeRun = option('--resume-run'), out = option('--out'), provider = option('--provider');
  if (Boolean(input) === Boolean(resumeRun) || !out || !['codex', 'fixture'].includes(provider)) throw new Error('Usage: cli.js (--input snapshot.json | --resume-run prior-run-dir) --out draft-bundles --provider codex|fixture');
  if (/publish|wordpress|wp-content|wp-admin/i.test(out)) throw new Error('Refusing publication or WordPress output path');
  if (provider === 'codex' && process.env.OPC_ALLOW_SUBSCRIPTION_CLI !== '1') throw new Error('Codex/Claude CLI model calls require OPC_ALLOW_SUBSCRIPTION_CLI=1 after subscription cost verification');
  return { input, resumeRun, out, provider };
}
function prepareSelection(rawSnapshot) {
  const intake = Array.isArray(rawSnapshot.ideaRows) ? intakeIdeas(rawSnapshot.ideaRows, rawSnapshot.sourceCatalog || rawSnapshot.sources, { spreadsheetId: rawSnapshot.spreadsheetId }) : null;
  const snapshot = intake ? { snapshotAt: rawSnapshot.snapshotAt, candidates: intake.candidates, existing: rawSnapshot.existing, sources: rawSnapshot.sourceCatalog || rawSnapshot.sources } : rawSnapshot;
  const selection = selectTopic(snapshot);
  if (!selection.selected) throw new Error(`No eligible autonomous topic: ${JSON.stringify(selection.rejected)}`);
  return { intake, snapshot, selection };
}
function codexJson(prompt, label) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-blog-v2-'));
  const output = path.join(temp, 'draft.json');
  try {
    runModel('codex', ['exec', '--sandbox', 'read-only', '--skip-git-repo-check', '--ephemeral', '--output-last-message', output, '-'], prompt, label);
    return parseJson(fs.readFileSync(output, 'utf8'), label);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
}
function claudeReview(brief, draft, sources) {
  return parseJson(runModel(process.env.OPC_CLAUDE_CLI || 'claude', ['-p', '--no-session-persistence', '--tools', '', '--output-format', 'text'], reviewPrompt(brief, draft, sources), 'Claude'), 'Claude');
}
function initialPair(provider, brief, sources, prior) {
  if (prior) return { draft: prior.draft, review: prior.review };
  if (provider === 'fixture') {
    return { draft: JSON.parse(fs.readFileSync(option('--fixture-draft'), 'utf8')), review: JSON.parse(fs.readFileSync(option('--fixture-review'), 'utf8')) };
  }
  const draft = codexJson(draftPrompt(brief, sources), 'Codex draft');
  return { draft, review: claudeReview(brief, draft, sources) };
}
function revisedPair(provider, brief, sources, draft, review) {
  if (provider === 'fixture') return { draft: JSON.parse(fs.readFileSync(option('--fixture-revised-draft'), 'utf8')), review: JSON.parse(fs.readFileSync(option('--fixture-revised-review'), 'utf8')) };
  const revisedDraft = codexJson(revisionPrompt(brief, sources, draft, review), 'Codex revision');
  return { draft: revisedDraft, review: claudeReview(brief, revisedDraft, sources) };
}
function generateBundle(provider, brief, sources, prior) {
  const original = initialPair(provider, brief, sources, prior);
  if (!needsRevision(original.review)) return original;
  const revised = revisedPair(provider, brief, sources, original.draft, original.review);
  return { draft: revised.draft, review: revised.review, originalDraft: original.draft, originalReview: original.review, revisedDraft: revised.draft, revisedReview: revised.review, revision: { attempts: 1, trigger: 'independent-review', originalDecision: original.review.decision } };
}
function reviewGate(draft, brief, sources, review) {
  const gate = validateDraft(draft, brief, { sources });
  if (!['pass', 'revise'].includes(review?.decision) || !Array.isArray(review.findings)) gate.push('invalid-independent-review');
  if (review?.findings?.some(f => ['blocker', 'major'].includes(f.severity))) gate.push('independent-review-findings');
  if (review?.decision !== 'pass') gate.push('independent-review-blocked');
  return gate;
}
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
module.exports = { verifySources, draftPrompt, reviewPrompt, revisionPrompt, needsRevision, loadPriorRun, generateBundle };
