#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawnSync } = require('node:child_process');
const { selectTopic, validateDraft, writeRun, sha } = require('./pipeline');
const { intakeIdeas } = require('./intake');

function option(name) { const i = process.argv.indexOf(name); return i < 0 ? null : process.argv[i + 1]; }
function parseJson(text, label) { try { return JSON.parse(text.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '')); } catch (error) { throw new Error(`${label} did not return JSON: ${error.message}`); } }
function textOnly(html) { return html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, ' ').replace(/<style[^>]*>[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' '); }
async function verifySources(sources) {
  const verified = [];
  for (const source of sources) {
    if (source.access === 'internal-preverified') {
      if (!source.evidenceId || !source.verifiedBy || !source.excerpt || !source.capturedAt) throw new Error(`Internal source ${source.id} lacks verification record`);
      verified.push({ ...source, retrieval: 'internal-preverified', contentDigest: sha(source.excerpt) });
      continue;
    }
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    let response;
    try { response = await fetch(source.url, { signal: controller.signal, headers: { 'user-agent': 'OPC-Blog-Research/2.0' } }); }
    finally { clearTimeout(timeout); }
    if (!response.ok) throw new Error(`Source ${source.id} returned HTTP ${response.status}`);
    const body = textOnly((await response.text()).slice(0, 500000));
    if (body.length < 100) throw new Error(`Source ${source.id} has insufficient retrieved text`);
    const terms = source.excerpt.toLowerCase().split(/\W+/).filter(w => w.length > 5);
    if (terms.length && terms.filter(w => body.toLowerCase().includes(w)).length / terms.length < 0.5) throw new Error(`Source ${source.id} excerpt is not supported by retrieved page`);
    verified.push({ ...source, retrieval: 'http', httpStatus: response.status, retrievedAt: new Date().toISOString(), contentDigest: sha(body), retrievedExcerpt: body.slice(0, 1200) });
  }
  return verified;
}
function runModel(program, args, prompt, label) {
  const safeEnv = Object.fromEntries(Object.entries(process.env).filter(([key]) => !/^(WP_|WORDPRESS_|PEXELS_API_KEY|GOOGLE_SA_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|CLAUDE_KEY_4_CONTENT)/i.test(key)));
  const result = spawnSync(program, args, { input: prompt, encoding: 'utf8', timeout: 180000, maxBuffer: 4 * 1024 * 1024, env: safeEnv });
  if (result.error || result.status !== 0) throw new Error(`${label} CLI unavailable or failed: ${(result.error?.message || result.stderr || '').slice(0, 500)}`);
  return result.stdout.trim();
}
function draftPrompt(brief, sources) {
  return `Return ONLY JSON with title, slug, category, description, body (Markdown; at least 700 characters, using the site's existing post format), claims [{id,text,sourceId,evidence,checkedAt,status:"verified"}], visuals [{type,alt,provenance,rights}]. Write a complete useful article for Oak Park Construction readers. Scope is ${brief.service} in ${brief.area}. Question: ${brief.question}. Reader decision: ${brief.readerDecision}. Sources: ${JSON.stringify(sources)}. Cite consequential factual claims inline using Markdown links to the exact supporting primary source and list each in claims. Each claim text must appear verbatim in the body; each numeric claim must reproduce a number visible in its cited source excerpt. Cite only what the supplied source excerpt directly supports; omit unsupported code, permit, legal, price, or technical assertions. No invented OPC projects, commercial results, numbers, guarantees, license numbers, or stock photo claims. One topic-specific CTA. No publication or WordPress instructions.`;
}
function reviewPrompt(brief, draft, sources) {
  return `Act as an independent OPC editorial and factual reviewer. Return ONLY JSON: {"decision":"pass"|"revise","findings":[{"severity":"blocker"|"major"|"minor","issue":"...","claimId":"... or null","evidence":"..."}],"summary":"..."}. Verify every consequential assertion against the supplied source excerpts, flag source relevance gaps, fabricated OPC experience or commercial claims, bad area/service scope, duplicate intent, incomplete reader answer, and unsupported numbers. Do not assume citations prove their claims. Brief: ${JSON.stringify(brief)}. Sources: ${JSON.stringify(sources)}. Draft: ${JSON.stringify(draft)}`;
}
async function main() {
  const input = option('--input'), out = option('--out'), provider = option('--provider');
  if (!input || !out || !['codex', 'fixture'].includes(provider)) throw new Error('Usage: cli.js --input snapshot.json --out draft-bundles --provider codex|fixture [--fixture-draft draft.json --fixture-review review.json]');
  if (/publish|wordpress|wp-content|wp-admin/i.test(out)) throw new Error('Refusing publication or WordPress output path');
  if (provider === 'codex' && process.env.OPC_ALLOW_SUBSCRIPTION_CLI !== '1') throw new Error('Codex/Claude CLI model calls require OPC_ALLOW_SUBSCRIPTION_CLI=1 after subscription cost verification');
  const rawSnapshot = JSON.parse(fs.readFileSync(input, 'utf8'));
  const intake = Array.isArray(rawSnapshot.ideaRows) ? intakeIdeas(rawSnapshot.ideaRows, rawSnapshot.sourceCatalog || rawSnapshot.sources, { spreadsheetId: rawSnapshot.spreadsheetId }) : null;
  const snapshot = intake ? { snapshotAt: rawSnapshot.snapshotAt, candidates: intake.candidates, existing: rawSnapshot.existing, sources: rawSnapshot.sourceCatalog || rawSnapshot.sources } : rawSnapshot;
  const selection = selectTopic(snapshot);
  if (!selection.selected) throw new Error(`No eligible autonomous topic: ${JSON.stringify(selection.rejected)}`);
  const sources = await verifySources(snapshot.sources.filter(s => selection.selected.sourceIds.includes(s.id)));
  const brief = { ...selection.selected, selectedAutonomously: true, selectionScore: selection.score, sourceIds: sources.map(s => s.id), rulesVersion: 'blog-v2-2026-10-10' };
  let draft, review;
  if (provider === 'fixture') {
    draft = JSON.parse(fs.readFileSync(option('--fixture-draft'), 'utf8'));
    review = JSON.parse(fs.readFileSync(option('--fixture-review'), 'utf8'));
  } else {
    const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-blog-v2-'));
    const output = path.join(temp, 'draft.json');
    try {
      runModel('codex', ['exec', '--sandbox', 'read-only', '--skip-git-repo-check', '--ephemeral', '--output-last-message', output, '-'], draftPrompt(brief, sources), 'Codex');
      draft = parseJson(fs.readFileSync(output, 'utf8'), 'Codex');
      review = parseJson(runModel(process.env.OPC_CLAUDE_CLI || 'claude', ['-p', '--no-session-persistence', '--tools', '', '--output-format', 'text'], reviewPrompt(brief, draft, sources), 'Claude'), 'Claude');
    } finally { fs.rmSync(temp, { recursive: true, force: true }); }
  }
  const gate = validateDraft(draft, brief, { sources });
  if (!['pass', 'revise'].includes(review?.decision) || !Array.isArray(review.findings)) gate.push('invalid-independent-review');
  if (review?.findings?.some(f => ['blocker', 'major'].includes(f.severity))) gate.push('independent-review-findings');
  if (review?.decision !== 'pass') gate.push('independent-review-blocked');
  const status = gate.length ? 'review-required' : 'draft-ready-for-human-review';
  const runDir = writeRun(out, { rawSnapshot, intake, snapshot, selection, sources, brief, draft, review, gate, status });
  console.log(JSON.stringify({ runDir, selectedId: brief.id, status, gate, provider }));
  if (gate.length) process.exitCode = 2;
}
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
module.exports = { verifySources, draftPrompt, reviewPrompt };
