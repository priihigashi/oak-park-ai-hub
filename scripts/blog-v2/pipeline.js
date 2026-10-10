const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const SERVICES = new Set(['home renovation', 'home addition', 'shell construction', 'concrete work', 'deck construction', 'screen porch enclosure', 'commercial renovation', 'commercial build out', 'commercial construction']);
const AREAS = new Set(['broward county', 'miami dade county', 'palm beach county']);
const forbidden = /\b(roofing.only|plumbing.only|electrical.only|handyman|sink install|chicago|illinois)\b/i;
const commercialClaim = /\b(we|oak park construction|opc)\s+(guarantee(?:d|s)?|completed|built|saved|charge|offer|have done)\b/i;
const numericClaim = /(?:\$\s*\d|\b\d+(?:\.\d+)?\s*(?:%|percent|days|weeks|months|years)\b)/i;
function quantities(s) { return String(s || '').match(/(?:\$\s*\d[\d,.]*|\b\d+(?:\.\d+)?\s*(?:%|percent|days|weeks|months|years)\b)/gi) || []; }
function quantityKey(s) { return s.toLowerCase().replace(/[\s,$]/g, ''); }
function bodyWordCount(body) {
  const visible = body.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/https?:\/\/\S+/g, ' ');
  return visible.match(/[\p{L}\p{N}][\p{L}\p{N}'’-]*/gu)?.length || 0;
}

function normalize(s) { return String(s || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim(); }
function tokens(s) { return new Set(normalize(s).split(' ').filter(w => w.length > 3 && !['what', 'when', 'with', 'from', 'your', 'home', 'florida', 'south'].includes(w))); }
function similarity(a, b) { const x = tokens(a), y = tokens(b); if (!x.size || !y.size) return 0; const common = [...x].filter(t => y.has(t)).length; return common / Math.min(x.size, y.size); }
function sha(value) { return crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex'); }
function validSource(s) {
  return [s.id, s.capturedAt, s.title, s.publisher, s.excerpt].every(Boolean) && /^https:\/\//.test(s.url || '');
}
function assertSnapshot(snapshot) {
  if (!['candidates', 'existing', 'sources'].every(key => Array.isArray(snapshot[key]))) throw new Error('Snapshot requires candidates, existing, and sources arrays');
  if (!snapshot.snapshotAt || Number.isNaN(Date.parse(snapshot.snapshotAt))) throw new Error('Snapshot needs a dated snapshotAt');
  for (const s of snapshot.sources) if (!validSource(s)) throw new Error(`Invalid source ${s.id || 'unknown'}: URL, publisher, title, excerpt and capture date required`);
}
function findDuplicate(candidate, existing) {
  return existing.find(p => candidate.intentKey && p.intentKey
    ? p.intentKey === candidate.intentKey
    : similarity(candidate.question + ' ' + candidate.readerDecision, (p.title || '') + ' ' + (p.intent || '')) >= 0.75);
}
function sourceReasons(candidate, snapshot, byId) {
  const reasons = [];
  if (!candidate.sourceIds?.length || candidate.sourceIds.some(id => !byId.has(id))) reasons.push('missing-source');
  const fresh = (candidate.sourceIds || []).every(id => byId.get(id) && Date.parse(byId.get(id).capturedAt) <= Date.parse(snapshot.snapshotAt));
  if (!fresh) reasons.push('source-after-snapshot');
  return reasons;
}
function candidateReasons(candidate, snapshot, byId) {
  const reasons = [];
  if (![candidate.id, candidate.question, candidate.readerDecision].every(Boolean)) reasons.push('missing-reader-question-or-decision');
  if (!SERVICES.has(normalize(candidate.service))) reasons.push('unverified-service');
  if (!AREAS.has(normalize(candidate.area))) reasons.push('unverified-area');
  if (forbidden.test(`${candidate.question} ${candidate.service} ${candidate.area}`)) reasons.push('out-of-scope');
  reasons.push(...sourceReasons(candidate, snapshot, byId));
  const duplicate = findDuplicate(candidate, snapshot.existing);
  if (duplicate) reasons.push(`duplicate:${duplicate.id || duplicate.slug || duplicate.title}`);
  return reasons;
}
function selectTopic(snapshot) {
  assertSnapshot(snapshot);
  const byId = new Map(snapshot.sources.map(s => [s.id, s]));
  const rejected = [], eligible = [];
  for (const c of snapshot.candidates) {
    const reasons = candidateReasons(c, snapshot, byId);
    if (reasons.length) rejected.push({ id: c.id, question: c.question || '', reasons });
    else eligible.push({ candidate: c, score: Math.min(c.sourceIds.length, 4) * 10 + Math.min(tokens(c.readerDecision).size, 12) + (c.priority || 0) });
  }
  eligible.sort((a, b) => b.score - a.score || String(a.candidate.id).localeCompare(String(b.candidate.id)));
  if (!eligible.length) return { selected: null, rejected, ranked: [] };
  const [first, ...rest] = eligible;
  rejected.push(...rest.map(item => ({ id: item.candidate.id, question: item.candidate.question, reasons: ['lower-ranked-eligible'], score: item.score })));
  return { selected: first.candidate, score: first.score, rejected, ranked: eligible.map(({ candidate, score }) => ({ id: candidate.id, score })) };
}
function draftBaseErrors(draft) {
  const errors = [];
  if (forbidden.test(draft.title + ' ' + draft.body)) errors.push('out-of-scope-language');
  if (commercialClaim.test(draft.body)) errors.push('unsupported-commercial-claim');
  if (numericClaim.test(draft.body) && !draft.claims.some(cl => numericClaim.test(cl.text || ''))) errors.push('unledgered-numeric-claim');
  if (bodyWordCount(draft.body) < 400) errors.push('incomplete-article');
  if (/<[a-z][\s\S]*?>|wp-json|wordpress/i.test(draft.body)) errors.push('html-or-wordpress-content');
  return errors;
}
function claimEvidenceErrors(claim, source, body) {
  const errors = [];
  const evidenceTerms = tokens(claim.evidence);
  const sourceTerms = tokens(source.excerpt + ' ' + (source.retrievedExcerpt || ''));
  const overlap = [...evidenceTerms].filter(term => sourceTerms.has(term)).length;
  if (evidenceTerms.size < 3 || overlap / evidenceTerms.size < 0.5) errors.push(`irrelevant-evidence:${claim.id}`);
  if (!body.includes(source.url)) errors.push(`missing-inline-citation:${claim.id}`);
  const sourceQuantities = new Set(quantities(source.excerpt + ' ' + (source.retrievedExcerpt || '')).map(quantityKey));
  for (const number of quantities(claim.text)) {
    if (!sourceQuantities.has(quantityKey(number)) || !quantities(claim.evidence).map(quantityKey).includes(quantityKey(number))) errors.push(`unsupported-number:${claim.id}`);
  }
  return errors;
}
function claimErrors(claim, draft, allowed, sources) {
  const errors = [];
  if (![claim.id, claim.text, claim.sourceId, claim.evidence, claim.checkedAt].every(Boolean) || !allowed.has(claim.sourceId) || !['verified', 'uncertain'].includes(claim.status)) errors.push(`invalid-claim:${claim.id || 'unknown'}`);
  if (claim.status !== 'verified') errors.push(`unverified-claim:${claim.id}`);
  const visibleBody = draft.body.replace(/\[([^\]]+)\]\(https:\/\/[^)]+\)/g, '$1');
  if (!visibleBody.includes(claim.text)) errors.push(`claim-not-in-body:${claim.id}`);
  const source = sources.find(s => s.id === claim.sourceId);
  if (source) errors.push(...claimEvidenceErrors(claim, source, draft.body));
  return errors;
}
function validDraftShape(draft) {
  return Boolean(draft) && [draft.title, draft.description, draft.body].every(Boolean) && Array.isArray(draft.claims) && Array.isArray(draft.visuals);
}
function visualErrors(visuals) {
  return visuals.filter(visual => ![visual.type, visual.alt, visual.provenance, visual.rights].every(Boolean)).map(() => 'unverified-visual');
}
function validateDraft(draft, selected, snapshot) {
  if (!validDraftShape(draft)) return ['draft-schema'];
  const errors = draftBaseErrors(draft);
  const allowed = new Set(selected.sourceIds);
  for (const claim of draft.claims) errors.push(...claimErrors(claim, draft, allowed, snapshot.sources));
  const sourceIds = new Set(snapshot.sources.map(s => s.id));
  if (draft.claims.some(c => !sourceIds.has(c.sourceId))) errors.push('unknown-claim-source');
  errors.push(...visualErrors(draft.visuals));
  return [...new Set(errors)];
}
function writeRun(outDir, payload) {
  fs.mkdirSync(outDir, { recursive: true });
  const id = `${new Date().toISOString().replace(/[:.]/g, '-')}-${sha(payload).slice(0, 12)}`;
  const runDir = path.join(outDir, id);
  fs.mkdirSync(runDir, { recursive: false });
  for (const [name, value] of Object.entries(payload)) fs.writeFileSync(path.join(runDir, `${name}.json`), JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
  fs.writeFileSync(path.join(runDir, 'receipt.json'), JSON.stringify({ id, createdAt: new Date().toISOString(), inputHash: sha(payload.snapshot), selectedId: payload.selection.selected?.id || null, status: payload.status, fileHashes: Object.fromEntries(Object.keys(payload).map(name => [name + '.json', crypto.createHash('sha256').update(fs.readFileSync(path.join(runDir, `${name}.json`))).digest('hex')])) }, null, 2) + '\n', { flag: 'wx' });
  return runDir;
}
module.exports = { selectTopic, validateDraft, writeRun, sha, similarity, bodyWordCount };
