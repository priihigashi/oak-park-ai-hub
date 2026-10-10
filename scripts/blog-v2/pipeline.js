const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { verifiedCompanyService, standaloneTradeErrors } = require('./company-scope');

const AREAS = new Set(['broward county', 'miami dade county', 'palm beach county', 'fort lauderdale']);
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
function sourceGeographyErrors(source) {
  let host;
  try { host = new URL(source.url).hostname.toLowerCase(); } catch { return ['invalid-source-url']; }
  const countyTags = (source.coverageAreas || []).filter(area => /\bcounty\b/i.test(area));
  if (/^(?:www\.)?leg\.state\.fl\.us$/.test(host) && countyTags.length) return [`state-statute-marked-county:${source.id}`];
  return [];
}
function assertSnapshot(snapshot) {
  if (!['candidates', 'existing', 'sources'].every(key => Array.isArray(snapshot[key]))) throw new Error('Snapshot requires candidates, existing, and sources arrays');
  if (!snapshot.snapshotAt || Number.isNaN(Date.parse(snapshot.snapshotAt))) throw new Error('Snapshot needs a dated snapshotAt');
  for (const s of snapshot.sources) {
    if (!validSource(s)) throw new Error(`Invalid source ${s.id || 'unknown'}: URL, publisher, title, excerpt and capture date required`);
    const geographyErrors = sourceGeographyErrors(s);
    if (geographyErrors.length) throw new Error(`Invalid source geography: ${geographyErrors.join(', ')}`);
  }
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
function candidateReasons(candidate, snapshot, byId, researchMode = false) {
  const reasons = [];
  if (![candidate.id, candidate.question, candidate.readerDecision].every(Boolean)) reasons.push('missing-reader-question-or-decision');
  if (!verifiedCompanyService(candidate.service)) reasons.push('unverified-service');
  if (!AREAS.has(normalize(candidate.area))) reasons.push('unverified-area');
  if (forbidden.test(`${candidate.question} ${candidate.service} ${candidate.area}`)) reasons.push('out-of-scope');
  if (!researchMode) reasons.push(...sourceReasons(candidate, snapshot, byId));
  const duplicate = findDuplicate(candidate, snapshot.existing);
  if (duplicate) reasons.push(`duplicate:${duplicate.id || duplicate.slug || duplicate.title}`);
  return reasons;
}
function selectTopic(snapshot, { researchMode = false } = {}) {
  assertSnapshot(snapshot);
  const byId = new Map(snapshot.sources.map(s => [s.id, s]));
  const rejected = [], eligible = [];
  for (const c of snapshot.candidates) {
    const reasons = candidateReasons(c, snapshot, byId, researchMode);
    if (reasons.length) rejected.push({ id: c.id, question: c.question || '', reasons });
    else eligible.push({ candidate: c, score: (researchMode ? 0 : Math.min(c.sourceIds.length, 4) * 10) + Math.min(tokens(c.readerDecision).size, 12) + (c.priority || 0) });
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
  errors.push(...standaloneTradeErrors(draft.body));
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
function claimGeographyErrors(claim, source, selected) {
  if (!source) return [];
  const county = String(selected.area || '').replace(/\s+County$/i, '');
  if (!county) return [];
  const namesCounty = new RegExp(county.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i').test(claim.text);
  return namesCounty && !(source.coverageAreas || []).includes(selected.area) ? [`unsupported-claim-geography:${claim.id}`] : [];
}
function claimErrors(claim, draft, allowed, sources, selected) {
  const errors = [];
  if (![claim.id, claim.text, claim.sourceId, claim.evidence, claim.checkedAt].every(Boolean) || !allowed.has(claim.sourceId) || !['verified', 'uncertain'].includes(claim.status)) errors.push(`invalid-claim:${claim.id || 'unknown'}`);
  if (claim.status !== 'verified') errors.push(`unverified-claim:${claim.id}`);
  const citedParagraph = draft.body.split(/\n\s*\n/).find(paragraph => paragraph.replace(/\[([^\]]+)\]\(https:\/\/[^)]+\)/g, '$1').includes(claim.text));
  if (!citedParagraph) errors.push(`claim-not-in-body:${claim.id}`);
  const source = sources.find(s => s.id === claim.sourceId);
  if (source) errors.push(...claimEvidenceErrors(claim, source, citedParagraph || ''));
  errors.push(...claimGeographyErrors(claim, source, selected));
  return errors;
}
function validDraftShape(draft) {
  return Boolean(draft) && [draft.title, draft.description, draft.body].every(Boolean) && Array.isArray(draft.claims) && Array.isArray(draft.visuals);
}
function visualErrors(visuals) {
  return visuals.filter(visual => ![visual.type, visual.alt, visual.provenance, visual.rights].every(Boolean)).map(() => 'unverified-visual');
}
function formatErrors(draft, selected) {
  if (!selected.formatKey) return [];
  const errors = [];
  if (draft.formatKey !== selected.formatKey) errors.push('format-contract-mismatch');
  const headings = draft.body.match(/^#{2,3}\s+.+$/gm) || [];
  if (headings.length < 2) errors.push('missing-article-structure');
  if (headings.length && headings.filter(heading => /\?\s*$/.test(heading)).length > headings.length / 2) errors.push('question-list-format-drift');
  return errors;
}
function hasReaderTable(last) {
  const tableRows = last.split('\n').filter(line => /^\s*\|[^\n]+\|\s*$/.test(line));
  return tableRows.length >= 3 && tableRows.some(line => /^\s*\|[\s:|-]+\|\s*$/.test(line));
}
function decisionBulletErrors(last) {
  const bullets = last.split('\n').filter(line => /^\s*[-*]\s+\S/.test(line));
  const finalLine = last.trim().split('\n').at(-1) || '';
  return bullets.length >= 2 && !hasReaderTable(last) && !/^\s*\|/.test(finalLine)
    ? [] : ['missing-decision-bullets-ending'];
}
function sequenceArtifactErrors(last) {
  return /^\s*1\.\s+\S/m.test(last) && /^\s*2\.\s+\S/m.test(last) ? [] : ['missing-format-specific-reader-artifact'];
}
function terminalArtifactErrors(draft, selected) {
  if (!selected.formatKey) return [];
  const sections = String(draft.body || '').split(/^##\s+.+$/gm);
  const last = sections.at(-1) || '';
  if (selected.formatKey === 'scope-map' && selected.endingStyle === 'decision-bullets') return decisionBulletErrors(last);
  if (['scope-map', 'evidence-explainer'].includes(selected.formatKey)) return hasReaderTable(last) ? [] : ['missing-format-specific-reader-artifact'];
  if (selected.formatKey === 'sequence-walkthrough') return sequenceArtifactErrors(last);
  return /(?:^|\n)(?:\s*[-*]\s+|\s*\d+\.\s+|\s*\|[^\n]+\|)/m.test(last) ? [] : ['missing-reader-artifact'];
}
function geographicErrors(draft, selected) {
  if (!selected.evidenceScope || selected.evidenceScope === selected.area) return [];
  const county = String(selected.area || '').replace(/\s+County$/i, '');
  if (!county) return [];
  return new RegExp(county.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i').test(`${draft.title} ${draft.slug || ''} ${draft.description}`) ? ['unsupported-local-framing'] : [];
}
function validEditorialStep(step, draft) {
  const headings = (draft.body.match(/^##\s+.+$/gm) || []).map(h => h.slice(3).trim());
  return !step.claimId && !step.sourceId && !step.label && headings.includes(step.text);
}
function validSourceStep(step, draft) {
  const claim = draft.claims.find(item => item.id === step.claimId);
  const headings = (draft.body.match(/^##\s+.+$/gm) || []).map(h => h.slice(3).trim());
  return claim?.status === 'verified' && claim.text === step.text && claim.sourceId === step.sourceId && headings.includes(step.label);
}
function diagramStepErrors(step, draft) {
  if (!step || typeof step.text !== 'string' || !step.text.trim()) return ['invalid-figure-step'];
  if (step.kind === 'editorial') return validEditorialStep(step, draft) ? [] : ['unbound-editorial-step'];
  return step.kind === 'source' && validSourceStep(step, draft) ? [] : ['unbound-source-step'];
}
function diagramMetadataErrors(figure, selected) {
  const types = { 'scope-map': 'scope-map', 'evidence-explainer': 'evidence-map', 'sequence-walkthrough': 'decision-flow' };
  return figure.type === types[selected.formatKey] && figure.approved === false && figure.rights === 'OPC original diagram'
    && [figure.title, figure.alt, figure.caption, figure.provenance].every(Boolean) ? [] : ['figure-provenance-invalid'];
}
function diagramMarkerErrors(draft, figure) {
  const marker = `<!-- FIGURE:${figure.id} -->`;
  const errors = draft.body.split(marker).length === 2 ? [] : ['figure-marker-mismatch'];
  const bodyDigest = crypto.createHash('sha256').update(draft.body.replaceAll(marker, '').replace(/\n{3,}/g, '\n\n')).digest('hex').slice(0, 16);
  if (!String(figure.provenance || '').includes(bodyDigest)) errors.push('figure-provenance-mismatch');
  return errors;
}
function diagramStepsErrors(draft, figure) {
  if (!Array.isArray(figure.steps) || figure.steps.length < 3 || figure.steps.length > 5) return ['figure-step-count'];
  return figure.steps.flatMap(step => diagramStepErrors(step, draft));
}
function threeViewErrors(draft, selected, figure) {
  const errors = [];
  if (!validThreeViewMetadata(selected, figure)) errors.push('figure-provenance-invalid');
  const claim = (draft.claims || []).find(item => item.id === figure.claimId);
  if (!validThreeViewClaim(draft, claim, figure)) errors.push('unbound-three-view-source');
  return errors;
}
function validThreeViewMetadata(selected, figure) {
  return selected.figureConcept === 'addition-three-views' && selected.formatKey === 'sequence-walkthrough'
    && figure.approved === false && figure.rights === 'OPC original diagram'
    && [figure.title, figure.alt, figure.caption, figure.provenance].every(Boolean);
}
function validThreeViewClaim(draft, claim, figure) {
  return Boolean(claim && claim.sourceId === figure.sourceId && claim.status === 'verified'
    && draft.body.includes(claim.text) && ['site plan', 'floor plan', 'elevation plan'].every(term => claim.text.toLowerCase().includes(term)));
}
function missingDiagramErrors(draft, selected) {
  if (selected.figureConcept === 'addition-three-views') return ['missing-required-concept-figure'];
  return /<!-- FIGURE:[^>]+ -->/.test(draft.body || '') ? ['figure-marker-mismatch'] : [];
}
function diagramErrors(draft, selected) {
  if (!selected.formatKey) return [];
  const figure = draft.figures?.[0];
  if (!figure && !draft.figures?.length) return missingDiagramErrors(draft, selected);
  if (!figure || draft.figures.length !== 1) return ['missing-in-body-figure'];
  if (figure.type === 'three-view-diagram') return [...diagramMarkerErrors(draft, figure), ...threeViewErrors(draft, selected, figure)];
  return [...diagramMarkerErrors(draft, figure), ...diagramMetadataErrors(figure, selected), ...diagramStepsErrors(draft, figure)];
}
function validateDraft(draft, selected, snapshot) {
  if (!validDraftShape(draft)) return ['draft-schema'];
  const errors = draftBaseErrors(draft);
  errors.push(...formatErrors(draft, selected));
  errors.push(...terminalArtifactErrors(draft, selected));
  errors.push(...geographicErrors(draft, selected));
  errors.push(...diagramErrors(draft, selected));
  const allowed = new Set(selected.sourceIds);
  for (const claim of draft.claims) errors.push(...claimErrors(claim, draft, allowed, snapshot.sources, selected));
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
module.exports = { selectTopic, validateDraft, formatErrors, terminalArtifactErrors, geographicErrors, claimGeographyErrors, diagramErrors, writeRun, sha, similarity, bodyWordCount, sourceGeographyErrors };
