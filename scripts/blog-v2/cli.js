#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const { selectTopic, validateDraft, writeRun, sha } = require('./pipeline');
const { intakeIdeas } = require('./intake');
const { addReviewFigure } = require('./review-figure');
const { addThreeViewFigure } = require('./three-view-figure');
const { companyScope } = require('./company-scope');
const { planMedia } = require('./media-plan');
const { addSiteInventory } = require('./site-inventory');

function option(name) { const i = process.argv.indexOf(name); return i < 0 ? null : process.argv[i + 1]; }
function parseJson(text, label) { try { return JSON.parse(text.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '')); } catch (error) { throw new Error(`${label} did not return JSON: ${error.message}`); } }
function decodeEntity(match, name, entities) {
  if (entities[name.toLowerCase()]) return entities[name.toLowerCase()];
  const code = name.startsWith('#') ? Number(name.slice(1)) : 0;
  return code > 0 && code <= 0x10ffff ? String.fromCodePoint(code) : match;
}
function textOnly(html) {
  const entities = { nbsp: ' ', amp: '&', quot: '"', apos: "'", rsquo: '’', lsquo: '‘', ldquo: '“', rdquo: '”', ndash: '–', mdash: '—' };
  return html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, ' ').replace(/<style[^>]*>[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]*>/g, ' ')
    .replace(/&([a-z]+|#\d+);/gi, (match, name) => decodeEntity(match, name, entities))
    .replace(/\s+/g, ' ').trim();
}
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
function extractPdfText(bytes) {
  if (bytes.length > 10 * 1024 * 1024) throw new Error('PDF source exceeds 10 MiB research limit');
  const script = 'import io,sys\nfrom pypdf import PdfReader\nr=PdfReader(io.BytesIO(sys.stdin.buffer.read()), strict=False)\nprint(" ".join((p.extract_text() or "") for p in r.pages[:30]))';
  const result = spawnSync('python3', ['-c', script], { input: bytes, encoding: 'utf8', timeout: 15000, maxBuffer: 1024 * 1024 });
  if (result.error || result.status !== 0) throw new Error(`PDF text extraction failed: ${(result.error?.message || result.stderr || '').slice(0, 300)}`);
  return result.stdout.replace(/\s+/g, ' ').trim().slice(0, 500000);
}
async function fetchOfficialSource(source) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  let response;
  try { response = await fetch(source.url, { signal: controller.signal, headers: { 'user-agent': 'OPC-Blog-Research/2.0' } }); }
  finally { clearTimeout(timeout); }
  if (!response.ok) throw new Error(`Source ${source.id} returned HTTP ${response.status}`);
  const isPdf = /\.pdf(?:$|\?)/i.test(source.url) || /application\/pdf/i.test(response.headers?.get('content-type') || '');
  const body = isPdf ? extractPdfText(Buffer.from(await response.arrayBuffer())) : textOnly((await response.text()).slice(0, 500000));
  if (body.length < 100) throw new Error(`Source ${source.id} has insufficient retrieved text`);
  const retrievedExcerpt = matchedPassage(source, body);
  return { ...source, retrieval: isPdf ? 'http-pdf' : 'http', httpStatus: response.status, finalUrl: response.url, retrievedAt: new Date().toISOString(), contentDigest: sha(body), retrievedExcerpt };
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
const FORMAT_GUIDANCE = {
  'evidence-explainer': 'Explain the mechanism and its planning consequences in direct statements. Close with a compact two-column Markdown table contrasting what the supplied evidence establishes with what it cannot establish for this project. Do not end with a document-gathering checklist or repeated questions for a contractor.',
  'sequence-walkthrough': 'Walk through the sequence from existing conditions to design inputs and the owner decision. Close with a numbered Markdown sequence; each stage must name its input and the source-supported result or decision it enables. Do not call a document packet a sequence or add unsupported timing/causality.',
  'scope-map': 'Map two genuinely different scope areas and show their boundaries. Close with a Markdown comparison table contrasting those areas, the rule or evidence for each, and the owner consequence. Do not end with a sequential checklist disguised as a map.',
};
function formatGuidance(brief) {
  if (brief.formatKey === 'scope-map' && brief.endingStyle === 'decision-bullets') {
    return 'Map the use-approval and physical-work boundaries in direct prose. Finish with two short Markdown decision bullets, one for unresolved business use and one for planned physical work, followed by one concrete reader action. Do not put a comparison table in the final section.';
  }
  return FORMAT_GUIDANCE[brief.formatKey] || 'Give direct, source-supported answers rather than a repetitive question list.';
}
function draftPrompt(brief, sources) {
  return `Return ONLY JSON with title, slug, category, description, formatKey:"${brief.formatKey || 'unspecified'}", body (Markdown using the site's existing post format), claims [{id,text,sourceId,evidence,checkedAt,status:"verified"}], visuals [{type,alt,provenance,rights}]. Write a complete useful article for Oak Park Construction readers. Target 450–650 visible body words when the sources support them, without padding; fewer than 400 words fails the editorial floor. If the evidence cannot support a useful full answer, do not invent detail to meet length. Verified service is ${brief.service}; target readers are in ${brief.area}. Company scope boundary (editorial policy, not evidence for external factual claims): ${JSON.stringify(companyScope())}. Never advertise roofing, plumbing, or electrical as standalone OPC services; those trades appear only inside a larger project. Do not invent OPC project experience or licensing details from this policy. Evidence scope is ${brief.evidenceScope || 'unverified'}. Never put the target county in the title, slug, or description unless evidence scope equals that county; if no geography is supported, omit geography rather than widening the claim. Question: ${brief.question}. Reader decision: ${brief.readerDecision}. Format contract: ${formatGuidance(brief)} Use at least two descriptive, non-question section headings. Every section must answer a part of the reader decision using supplied evidence or explicitly identify the decision that remains open. Do not add concrete numbers solely to satisfy a quota. Sources: ${JSON.stringify(sources)}. The supplied Sources array is an EXCLUSIVE whitelist. Every claims[].sourceId and every factual citation must use an id and URL from that array. Do not recall, search for, cite, or add outside sources even if they are real official pages. If the supplied excerpts do not establish Florida or Broward law, do not state that law; identify the gap once without inventing an answer. Cite consequential factual claims inline using Markdown links to the exact supporting primary source and list each in claims, including conditional permit or approval requirements. Each claim text must appear verbatim in the body; each numeric claim must reproduce a number visible in its cited source excerpt. Cite only what the supplied source excerpt directly supports; omit unsupported code, permit, legal, price, or technical assertions. When two official sources describe separate approvals, explain each independently; never infer that one replaces or does not replace the other unless a verified source explicitly states that relationship. If a rule has an effective date, cutoff, or transitional exemption, identify it as time-sensitive and state the source retrieval date from retrievedAt; do not present a transition as a permanent rule. No invented OPC projects, commercial results, numbers, guarantees, license numbers, or stock photo claims. The final substantive section must deliver the format-specific reader artifact above, grounded in supplied sources; independent review judges whether it adds value. Avoid repeating a generic 'ask the design team' handoff. In reader-facing title, description, and body, never describe the research packet as 'supplied sources', 'supplied excerpts', or 'the brief'; cite the actual institution instead. State a material evidence limit once in plain language unless a different limit changes another decision. For national-only evidence, identify the federal source in the description rather than implying a local rule. A CTA is optional; include one only if OPC has a truthful, topic-specific next step, and do not imply unverified certifications. No publication or WordPress instructions.`;
}
function reviewPrompt(brief, draft, sources) {
  return `Act as an independent OPC editorial and factual reviewer. Return ONLY JSON: {"decision":"pass"|"revise","findings":[{"severity":"blocker"|"major"|"minor","issue":"...","claimId":"... or null","evidence":"..."}],"summary":"..."}. Verify every consequential assertion against the supplied source excerpts, flag source relevance gaps, fabricated OPC experience or commercial claims, bad area/service scope against ${JSON.stringify(companyScope())}, especially standalone trade promises, duplicate intent, incomplete reader answer, and unsupported numbers. If a reader-facing claim or inference maps a document to a regulatory review topic without direct source support, mark it major and return revise; a qualifying caveat elsewhere does not cure it. Never return pass while describing an unsupported factual inference, even if the claim ledger sentence itself overlaps a cited excerpt. Require every consequential regulatory or conditional approval statement to have a matching claims[] entry; mark an uncovered one major and request revision. For time-sensitive cutoffs or transitional exemptions, require a visible as-of retrieval date and mark its absence major. Independently check whether the article fulfills formatKey and gives direct, useful, source-supported answers rather than only telling the reader what to ask a third party. Treat a repeated question-list structure or mostly deferred answer as a major editorial finding. When an official source directly states a permit trigger or required action, mark a draft major/revise if it only tells the reader to ask an agency whether that trigger applies instead of stating the sourced rule and its practical consequence. Check title, slug, and description geography against evidenceScope; a Broward title cannot be justified by a national or Florida-only source. Review every in-body diagram node: verify claimId and sourceId bindings for source nodes, challenge any unsupported sequence/causality implied by the order or arrows, and assess whether editorial nodes are visibly labeled and useful. A figure is not approved simply because it repeats article text. Do not require arbitrary numbers or sources when evidence does not support them. Do not assume citations prove their claims. Brief: ${JSON.stringify(brief)}. Sources: ${JSON.stringify(sources)}. Draft: ${JSON.stringify(draft)}`;
}
function revisionPrompt(brief, sources, draft, review) {
  return `Return ONLY a complete revised draft JSON with the same schema as the original: title, slug, category, description, formatKey, body (Markdown), claims, visuals. Keep formatKey exactly "${brief.formatKey || 'unspecified'}". This is the sole repair attempt. Address every independent review finding with source evidence or remove unsupported text; do not silently preserve uncited consequential claims. If the review flags deferred answers or question-list repetition, rewrite sections as direct source-supported explanations with descriptive non-question headings. The Verified sources array is an EXCLUSIVE whitelist: never add, recall, search for, or cite another source, including real official Florida or Broward pages. Use only its sourceIds and exact URLs. Remove an unsupported local or legal assertion instead of supplying a new source from memory. If two verified sources discuss separate approvals without stating their relationship, describe each independently and delete any substitution or non-substitution claim rather than inferring it. Claim ledger rule: for EVERY claims[] item, copy claim.text exactly from one contiguous visible-body sentence after removing Markdown link syntax; keep punctuation identical and put a Markdown citation to that claim's sourceId URL in the SAME paragraph. Do not paraphrase claim.text in the ledger. Example body: "The permit office reviews plans before construction. [County](https://example.gov/permit)"; claim.text: "The permit office reviews plans before construction.". Before returning JSON, check every claim this way and delete or rewrite any claim that fails. Prefer omitting ambiguous performance numbers such as air changes per hour when the source lacks usable measurement context; never imply a national guide is local code. Keep a useful answer of at least 400 visible words without padding or invention. Preserve the reader decision and approved scope. Follow this format-specific ending instead of a generic checklist: ${formatGuidance(brief)} Do not refer to "supplied excerpts" or "the brief" in reader-facing copy; cite the real institution and state each material limit once. If evidence is national-only, identify that source in the description. A CTA is optional and must not imply unverified OPC credentials. Do not add publication instructions. Brief: ${JSON.stringify(brief)}. Verified sources: ${JSON.stringify(sources)}. Original draft: ${JSON.stringify(draft)}. Independent findings: ${JSON.stringify(review)}`;
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
  const input = JSON.parse(fs.readFileSync(options.input, 'utf8'));
  const rawSnapshot = options.siteFrontend ? addSiteInventory(input, options.siteFrontend) : input;
  const { intake, snapshot, selection } = prepareSelection(rawSnapshot);
  return { rawSnapshot, intake, snapshot, selection };
}
async function main() {
  const options = parseOptions();
  const context = prepareContext(options);
  const { rawSnapshot, intake, snapshot, selection, priorRun } = context;
  const sources = priorRun ? context.sources : await verifySources(snapshot.sources.filter(s => selection.selected.sourceIds.includes(s.id)));
  const brief = priorRun ? context.brief : { ...selection.selected, selectedAutonomously: true, selectionScore: selection.score, sourceIds: sources.map(s => s.id), rulesVersion: 'blog-v2-2026-10-10', companyScopeDigest: sha(companyScope()) };
  const bundle = generateBundle(options.provider, brief, sources, priorRun ? context : null);
  const { draft, review } = bundle;
  const mediaPlan = planMedia(rawSnapshot.mediaCatalog, brief);
  const gate = reviewGate(draft, brief, sources, review);
  const status = bundleStatus(bundle, gate);
  const runDir = writeRun(options.out, { rawSnapshot, intake, snapshot, selection, sources, brief, mediaPlan, ...bundle, ...(priorRun ? { priorRun } : {}), gate, status });
  console.log(JSON.stringify({ runDir, selectedId: brief.id, status, gate, provider: options.provider, revisionAttempted: Boolean(bundle.revisedDraft) }));
  if (gate.length) process.exitCode = 2;
}
function parseOptions() {
  const input = option('--input'), resumeRun = option('--resume-run'), out = option('--out'), provider = option('--provider'), siteFrontend = option('--site-frontend');
  if (Boolean(input) === Boolean(resumeRun) || !out || !['codex', 'fixture'].includes(provider)) throw new Error('Usage: cli.js (--input snapshot.json | --resume-run prior-run-dir) --out draft-bundles --provider codex|fixture [--site-frontend /path/to/site/frontend]');
  validateSiteOption({ input, resumeRun, provider, siteFrontend });
  if (/publish|wordpress|wp-content|wp-admin/i.test(out)) throw new Error('Refusing publication or WordPress output path');
  if (provider === 'codex' && process.env.OPC_ALLOW_SUBSCRIPTION_CLI !== '1') throw new Error('Codex/Claude CLI model calls require OPC_ALLOW_SUBSCRIPTION_CLI=1 after subscription cost verification');
  return { input, resumeRun, out, provider, siteFrontend };
}
function validateSiteOption({ input, resumeRun, provider, siteFrontend }) {
  if (resumeRun && siteFrontend) throw new Error('A revision resumes its immutable site inventory; omit --site-frontend');
  if (provider === 'codex' && input && !siteFrontend) throw new Error('Autonomous drafting requires --site-frontend to verify live and legacy blog inventory');
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
function claudeProgram() {
  if (process.env.OPC_CLAUDE_CLI) return process.env.OPC_CLAUDE_CLI;
  const local = path.join(os.homedir(), '.local/bin/claude');
  return fs.existsSync(local) ? local : 'claude';
}
function claudeReview(brief, draft, sources) {
  return parseJson(runModel(claudeProgram(), ['-p', '--no-session-persistence', '--tools', '', '--output-format', 'text'], reviewPrompt(brief, draft, sources), 'Claude'), 'Claude');
}
function initialPair(provider, brief, sources, prior) {
  if (prior) return { draft: prior.draft, review: prior.review };
  if (provider === 'fixture') {
    return { draft: JSON.parse(fs.readFileSync(option('--fixture-draft'), 'utf8')), review: JSON.parse(fs.readFileSync(option('--fixture-review'), 'utf8')) };
  }
  const draft = addThreeViewFigure(addReviewFigure(codexJson(draftPrompt(brief, sources), 'Codex draft')), brief);
  return { draft, review: claudeReview(brief, draft, sources) };
}
function revisedPair(provider, brief, sources, draft, review) {
  if (provider === 'fixture') return { draft: JSON.parse(fs.readFileSync(option('--fixture-revised-draft'), 'utf8')), review: JSON.parse(fs.readFileSync(option('--fixture-revised-review'), 'utf8')) };
  const revisedDraft = addThreeViewFigure(addReviewFigure(codexJson(revisionPrompt(brief, sources, draft, review), 'Codex revision')), brief);
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
function bundleStatus(bundle, gate) {
  if (!gate.length) return 'draft-ready-for-human-review';
  return bundle.revisedDraft ? 'revision-gate-failed' : 'review-required';
}
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
module.exports = { verifySources, textOnly, draftPrompt, reviewPrompt, revisionPrompt, needsRevision, loadPriorRun, generateBundle, reviewGate, claudeProgram, claudeReview, bundleStatus };
