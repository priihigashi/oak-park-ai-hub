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

function normalize(s) { return String(s || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim(); }
function tokens(s) { return new Set(normalize(s).split(' ').filter(w => w.length > 3 && !['what', 'when', 'with', 'from', 'your', 'home', 'florida', 'south'].includes(w))); }
function similarity(a, b) { const x = tokens(a), y = tokens(b); if (!x.size || !y.size) return 0; const common = [...x].filter(t => y.has(t)).length; return common / Math.min(x.size, y.size); }
function sha(value) { return crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex'); }
function assertSnapshot(snapshot) {
  if (!Array.isArray(snapshot.candidates) || !Array.isArray(snapshot.existing) || !Array.isArray(snapshot.sources)) throw new Error('Snapshot requires candidates, existing, and sources arrays');
  if (!snapshot.snapshotAt || Number.isNaN(Date.parse(snapshot.snapshotAt))) throw new Error('Snapshot needs a dated snapshotAt');
  for (const s of snapshot.sources) if (!s.id || !/^https:\/\//.test(s.url || '') || !s.capturedAt || !s.title || !s.publisher || !s.excerpt) throw new Error(`Invalid source ${s.id || 'unknown'}: URL, publisher, title, excerpt and capture date required`);
}
function selectTopic(snapshot) {
  assertSnapshot(snapshot);
  const byId = new Map(snapshot.sources.map(s => [s.id, s]));
  const rejected = [], eligible = [];
  for (const c of snapshot.candidates) {
    const reasons = [];
    const title = c.question || '';
    if (!c.id || !title || !c.readerDecision) reasons.push('missing-reader-question-or-decision');
    if (!SERVICES.has(normalize(c.service))) reasons.push('unverified-service');
    if (!AREAS.has(normalize(c.area))) reasons.push('unverified-area');
    if (forbidden.test(title + ' ' + c.service + ' ' + c.area)) reasons.push('out-of-scope');
    if (!Array.isArray(c.sourceIds) || !c.sourceIds.length || c.sourceIds.some(id => !byId.has(id))) reasons.push('missing-source');
    const duplicate = snapshot.existing.find(p => c.intentKey && p.intentKey
      ? p.intentKey === c.intentKey
      : similarity(title + ' ' + c.readerDecision, (p.title || '') + ' ' + (p.intent || '')) >= 0.75);
    if (duplicate) reasons.push(`duplicate:${duplicate.id || duplicate.slug || duplicate.title}`);
    const freshness = (c.sourceIds || []).every(id => byId.get(id) && Date.parse(byId.get(id).capturedAt) <= Date.parse(snapshot.snapshotAt));
    if (!freshness) reasons.push('source-after-snapshot');
    if (reasons.length) rejected.push({ id: c.id, question: title, reasons });
    else eligible.push({ candidate: c, score: Math.min(c.sourceIds.length, 4) * 10 + Math.min(tokens(c.readerDecision).size, 12) + (c.priority || 0) });
  }
  eligible.sort((a, b) => b.score - a.score || String(a.candidate.id).localeCompare(String(b.candidate.id)));
  if (!eligible.length) return { selected: null, rejected, ranked: [] };
  const [first, ...rest] = eligible;
  rejected.push(...rest.map(item => ({ id: item.candidate.id, question: item.candidate.question, reasons: ['lower-ranked-eligible'], score: item.score })));
  return { selected: first.candidate, score: first.score, rejected, ranked: eligible.map(({ candidate, score }) => ({ id: candidate.id, score })) };
}
function validateDraft(draft, selected, snapshot) {
  const errors = [];
  if (!draft || !draft.title || !draft.description || !draft.body || !Array.isArray(draft.claims) || !Array.isArray(draft.visuals)) return ['draft-schema'];
  if (forbidden.test(draft.title + ' ' + draft.body)) errors.push('out-of-scope-language');
  if (commercialClaim.test(draft.body)) errors.push('unsupported-commercial-claim');
  if (numericClaim.test(draft.body) && !draft.claims.some(cl => numericClaim.test(cl.text || ''))) errors.push('unledgered-numeric-claim');
  if (draft.body.length < 700) errors.push('incomplete-article');
  if (/<[a-z][\s\S]*?>|wp-json|wordpress/i.test(draft.body)) errors.push('html-or-wordpress-content');
  const allowed = new Set(selected.sourceIds);
  for (const claim of draft.claims) {
    if (!claim.id || !claim.text || !claim.sourceId || !allowed.has(claim.sourceId) || !claim.evidence || !claim.checkedAt || !['verified', 'uncertain'].includes(claim.status)) errors.push(`invalid-claim:${claim.id || 'unknown'}`);
    if (claim.status !== 'verified') errors.push(`unverified-claim:${claim.id}`);
    const visibleBody = draft.body.replace(/\[([^\]]+)\]\(https:\/\/[^)]+\)/g, '$1');
    if (!visibleBody.includes(claim.text)) errors.push(`claim-not-in-body:${claim.id}`);
    const source = snapshot.sources.find(s => s.id === claim.sourceId);
    if (source) {
      const evidenceTerms = tokens(claim.evidence);
      const sourceTerms = tokens(source.excerpt + ' ' + (source.retrievedExcerpt || ''));
      const overlap = [...evidenceTerms].filter(term => sourceTerms.has(term)).length;
      if (evidenceTerms.size < 3 || overlap / evidenceTerms.size < 0.5) errors.push(`irrelevant-evidence:${claim.id}`);
      if (!draft.body.includes(source.url)) errors.push(`missing-inline-citation:${claim.id}`);
      const sourceQuantities = new Set(quantities(source.excerpt + ' ' + (source.retrievedExcerpt || '')).map(quantityKey));
      for (const number of quantities(claim.text)) {
        if (!sourceQuantities.has(quantityKey(number)) || !quantities(claim.evidence).map(quantityKey).includes(quantityKey(number))) errors.push(`unsupported-number:${claim.id}`);
      }
    }
  }
  const sourceIds = new Set(snapshot.sources.map(s => s.id));
  if (draft.claims.some(c => !sourceIds.has(c.sourceId))) errors.push('unknown-claim-source');
  for (const visual of draft.visuals) if (!visual.type || !visual.alt || !visual.provenance || !visual.rights) errors.push('unverified-visual');
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
module.exports = { selectTopic, validateDraft, writeRun, sha, similarity };
