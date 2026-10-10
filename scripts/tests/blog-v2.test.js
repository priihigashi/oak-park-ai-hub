const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { selectTopic, validateDraft, writeRun } = require('../blog-v2/pipeline');
const { verifySources } = require('../blog-v2/cli');
const { intakeIdeas } = require('../blog-v2/intake');

const source = { id: 's1', url: 'https://example.gov/additions', publisher: 'County', title: 'Addition guidance', excerpt: 'Home additions require a permit before construction begins and plans must be reviewed.', capturedAt: '2026-10-09' };
const candidate = { id: 'c1', question: 'What must I check before a home addition in Broward County?', readerDecision: 'Understand permit sequence before pricing a home addition', service: 'home addition', area: 'Broward County', sourceIds: ['s1'] };
const snapshot = { snapshotAt: '2026-10-10', sources: [source], candidates: [candidate], existing: [] };
test('selects an autonomous sourced in-scope topic and retains rejections', () => {
  const result = selectTopic({ ...snapshot, candidates: [{ ...candidate, id: 'out', service: 'standalone roofing' }, candidate] });
  assert.equal(result.selected.id, 'c1');
  assert.equal(result.rejected[0].id, 'out');
  assert.ok(result.rejected[0].reasons.includes('unverified-service'));
});
test('deduplicates current, legacy, and queued intent from supplied inventory', () => {
  for (const type of ['live', 'legacy', 'queued']) {
    const result = selectTopic({ ...snapshot, existing: [{ id: type, title: candidate.question, intent: candidate.readerDecision }] });
    assert.equal(result.selected, null);
    assert.ok(result.rejected[0].reasons.includes(`duplicate:${type}`));
  }
});
test('intent keys suppress equivalent pilot questions without excluding a different service', () => {
  const addition = { ...candidate, intentKey: 'residential-permit-office:broward county' };
  const screen = { ...candidate, id: 'screen', question: 'Where should an owner check permit requirements before a screen porch enclosure in Broward County?', readerDecision: 'Find the permit office for a screen enclosure', service: 'screen porch enclosure', intentKey: 'screen-enclosure-planning:broward county' };
  const result = selectTopic({ ...snapshot, candidates: [addition, screen], existing: [{ id: 'pilot-1', title: addition.question, intent: addition.readerDecision, intentKey: addition.intentKey }] });
  assert.equal(result.selected.id, 'screen');
  assert.ok(result.rejected.some(item => item.id === addition.id && item.reasons.includes('duplicate:pilot-1')));
});
test('hyphenated verified service and area remain eligible', () => {
  const commercial = { ...candidate, service: 'commercial build-out', area: 'Miami-Dade County', question: 'Where should a Miami-Dade business check retail build-out permitting?' };
  assert.equal(selectTopic({ ...snapshot, candidates: [commercial] }).selected.id, 'c1');
});
test('rejects unsupported commercial, visual and source claims', () => {
  const draft = { title: 'Addition guide', description: 'Guide', body: `<h2>Plan the work</h2><p>${'A practical step for owners. '.repeat(35)}</p><p>Oak Park Construction guaranteed a result.</p>`, claims: [{ id: 'c', text: 'A permit is needed', sourceId: 's1', evidence: 'unrelated nonsense phrase', checkedAt: '2026-10-10', status: 'verified' }], visuals: [{ type: 'photo', alt: 'house' }] };
  const errors = validateDraft(draft, candidate, snapshot);
  assert.ok(errors.includes('unsupported-commercial-claim'));
  assert.ok(errors.includes('irrelevant-evidence:c'));
  assert.ok(errors.includes('missing-inline-citation:c'));
  assert.ok(errors.includes('unverified-visual'));
});
test('Markdown draft requires each cited claim in body and source-supported numbers', () => {
  const numbered = { ...source, excerpt: 'Home additions require a permit and review takes 10 days before construction starts.' };
  const claim = { id: 'permit-time', text: 'Review takes 14 days', sourceId: 's1', evidence: 'Review takes 14 days before construction starts.', checkedAt: '2026-10-10', status: 'verified' };
  const draft = { title: 'Addition guide', description: 'Guide', body: `## What to check\n\n${'A practical step for owners. '.repeat(35)}\n\nReview takes 14 days [County guidance](${source.url}).`, claims: [claim], visuals: [] };
  const errors = validateDraft(draft, candidate, { sources: [numbered] });
  assert.ok(errors.includes('unsupported-number:permit-time'));
  assert.ok(!errors.includes('html-or-wordpress-content'));
  const revised = { ...draft, body: draft.body.replace('14 days', '10 days'), claims: [{ ...claim, text: 'Review takes 10 days', evidence: 'review takes 10 days before construction starts' }] };
  assert.ok(!validateDraft(revised, candidate, { sources: [numbered] }).some(e => e.startsWith('unsupported-number')));
});
test('a linked publisher name counts as visible claim text', () => {
  const claim = { id: 'office', text: 'County guidance says home additions require a permit before construction begins.', sourceId: 's1', evidence: source.excerpt, checkedAt: '2026-10-10', status: 'verified' };
  const body = `[County guidance](${source.url}) says home additions require a permit before construction begins. ${'Owners should confirm the applicable local office. '.repeat(20)}`;
  const errors = validateDraft({ title: 'Addition guide', description: 'Guide', body, claims: [claim], visuals: [] }, candidate, snapshot);
  assert.ok(!errors.includes('claim-not-in-body:office'));
});
test('retains immutable audit files with hashes', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-blog-test-'));
  try {
    const dir = writeRun(root, { snapshot, selection: { selected: candidate }, status: 'review-required' });
    const receipt = JSON.parse(fs.readFileSync(path.join(dir, 'receipt.json')));
    assert.equal(receipt.selectedId, 'c1');
    assert.equal(receipt.status, 'review-required');
    assert.ok(receipt.fileHashes['snapshot.json']);
    assert.throws(() => fs.writeFileSync(path.join(dir, 'snapshot.json'), '', { flag: 'wx' }), /EEXIST/);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
test('verifies HTTP source content and rejects stale excerpt', async () => {
  const original = global.fetch;
  global.fetch = async () => ({ ok: true, status: 200, text: async () => `<html><body>${source.excerpt} ${'Additional county guidance. '.repeat(8)}</body></html>` });
  try { assert.equal((await verifySources([source]))[0].retrieval, 'http'); }
  finally { global.fetch = original; }
  global.fetch = async () => ({ ok: true, status: 200, text: async () => '<html><body>' + 'Unrelated material '.repeat(20) + '</body></html>' });
  try { await assert.rejects(verifySources([source]), /excerpt is not supported/); }
  finally { global.fetch = original; }
});
test('intake turns raw hook into a safe question and preserves only row provenance', () => {
  const rows = [{ rowNumber: 120, rawIdea: 'Complete guide to a home addition in Fort Lauderdale', topicDirection: 'Guaranteed 30-day addition at $50,000', hookProfessional: 'We built 500 additions', readerPayoff: 'Get your permit in one day', sourceLink: 'https://youtube.com/watch?v=example', status: '🆕 Idea' }];
  const sources = [{ ...source, id: 'broward-permit', url: 'https://www.broward.org/Building', publisher: 'Broward County', title: 'Permit office', sourceRole: 'topic-specific', themeTags: ['addition-planning'], coverageAreas: ['Broward County'] }];
  const result = intakeIdeas(rows, sources, { spreadsheetId: 'sheet-1' });
  assert.equal(result.candidates.length, 1);
  assert.equal(result.candidates[0].service, 'home addition');
  assert.deepEqual(result.candidates[0].sourceIds, ['broward-permit']);
  assert.equal(result.candidates[0].inputProvenance.row, 120);
  assert.equal(result.candidates[0].inputProvenance.inspirationUrl, rows[0].sourceLink);
  assert.doesNotMatch(JSON.stringify(result.candidates[0]), /Guaranteed|\$50,000|500 additions|one day/);
});
test('intake covers screen enclosure, commercial build-out and permit themes', () => {
  const sources = [
    { ...source, id: 'miami-permit', publisher: 'Miami-Dade County', title: 'Permit applications', url: 'https://miamidade.gov/permit', sourceRole: 'topic-specific', themeTags: ['screen-enclosure-planning', 'commercial-retail-buildout'], coverageAreas: ['Miami-Dade County'] },
    { ...source, id: 'broward-building', publisher: 'Broward County', title: 'Building permits', url: 'https://broward.org/building', sourceRole: 'topic-specific', themeTags: ['permit-lookup'], coverageAreas: ['Broward County'] },
  ];
  const rows = [
    { rowNumber: 2, rawIdea: 'Screened porch in Miami-Dade' },
    { rowNumber: 3, rawIdea: 'Retail tenant improvement in Miami' },
    { rowNumber: 4, rawIdea: 'Permit lookup for a Broward renovation' },
  ];
  const result = intakeIdeas(rows, sources);
  assert.deepEqual(result.candidates.map(c => c.theme), ['screen-enclosure-planning', 'commercial-retail-buildout', 'permit-lookup']);
  assert.equal(result.candidates[0].area, 'Miami-Dade County');
});
test('intake rejects used rows and themes without area-specific official sources', () => {
  const result = intakeIdeas([{ rowNumber: 7, rawIdea: 'Screen porch in Miami', status: 'Draft Created' }, { rowNumber: 8, rawIdea: 'Screen porch in Palm Beach' }], [source]);
  assert.equal(result.candidates.length, 0);
  assert.ok(result.rejected[0].reasons.includes('already-used-row'));
  assert.ok(result.rejected[1].reasons.includes('no-topic-relevant-official-source'));
});
test('generic county pages cannot qualify a theme without a topic-specific source', () => {
  const row = { rowNumber: 4, rawIdea: 'Boutique retail accessibility layout in Broward' };
  const generic = { ...source, id: 'broward-building', sourceRole: 'general-permit', themeTags: ['retail-accessibility'], coverageAreas: ['Broward County'] };
  const empty = intakeIdeas([row], [generic]);
  assert.equal(empty.candidates.length, 0);
  assert.ok(empty.rejected[0].reasons.includes('no-topic-relevant-official-source'));
  const doj = { ...source, id: 'doj-ada', publisher: 'US Department of Justice', sourceRole: 'topic-specific', themeTags: ['retail-accessibility'], coverageAreas: ['national'] };
  const supported = intakeIdeas([row], [generic, doj]);
  assert.deepEqual(supported.candidates[0].sourceIds, ['doj-ada']);
});
test('kitchen exhaust is in full renovation scope; patio cover remains ineligible', () => {
  const doe = { ...source, id: 'doe-kitchen-exhaust', sourceRole: 'topic-specific', themeTags: ['kitchen-exhaust'], coverageAreas: ['national'] };
  const rows = [{ rowNumber: 14, rawIdea: 'Kitchen exhaust redesign for a full home renovation in Broward' }, { rowNumber: 115, rawIdea: 'Patio cover wind connections in Broward' }];
  const result = intakeIdeas(rows, [doe]);
  assert.equal(result.candidates[0].theme, 'kitchen-exhaust');
  assert.equal(result.candidates[0].service, 'home renovation');
  assert.equal(result.rejected[0].id, 'content-ideas-row-115');
});
test('source-gated themes safely reframe boutique remodel, kitchen hosting, and addition HVAC rows', () => {
  const catalog = [
    { ...source, id: 'doj-ada', sourceRole: 'topic-specific', themeTags: ['retail-accessibility'], coverageAreas: ['national'] },
    { ...source, id: 'doe-kitchen', sourceRole: 'topic-specific', themeTags: ['kitchen-exhaust'], coverageAreas: ['national'] },
    { ...source, id: 'doe-hvac', sourceRole: 'topic-specific', themeTags: ['addition-hvac-planning'], coverageAreas: ['national'] },
  ];
  const rows = [
    { rowNumber: 4, rawIdea: 'Boutique retail remodel in Broward', readerPayoff: 'Guaranteed ADA compliance' },
    { rowNumber: 14, rawIdea: 'Kitchen renovation for hosting in Broward', readerPayoff: 'Improves air quality by 90%' },
    { rowNumber: 98, rawIdea: 'HVAC coordination for a room addition in Broward', topicDirection: 'Standalone HVAC referral and exact tonnage advice' },
  ];
  const result = intakeIdeas(rows, catalog);
  assert.deepEqual(result.candidates.map(c => c.theme), ['retail-accessibility', 'kitchen-exhaust', 'addition-hvac-planning']);
  assert.deepEqual(result.candidates.map(c => c.sourceIds[0]), ['doj-ada', 'doe-kitchen', 'doe-hvac']);
  assert.doesNotMatch(JSON.stringify(result.candidates), /Guaranteed|90%|Standalone HVAC|tonnage/);
  assert.equal(result.candidates[2].service, 'home addition');
});
test('peripheral investment, showroom and cost mentions cannot inherit a targeted angle', () => {
  const catalog = [
    { ...source, id: 'doj-ada', sourceRole: 'topic-specific', themeTags: ['retail-accessibility'], coverageAreas: ['national'] },
    { ...source, id: 'doe-hvac', sourceRole: 'topic-specific', themeTags: ['addition-hvac-planning'], coverageAreas: ['national'] },
  ];
  const rows = [
    { rowNumber: 522, rawIdea: 'Retail center acquisition', topicDirection: 'Renovation demand may follow' },
    { rowNumber: 1073, rawIdea: 'Cost breakdown for home additions', topicDirection: 'Mention HVAC sizing' },
    { rowNumber: 1132, rawIdea: 'Virginia showroom relocation', topicDirection: 'Retail renovation and accessibility' },
  ];
  const result = intakeIdeas(rows, catalog);
  assert.equal(result.candidates.length, 0);
  assert.ok(result.rejected.every(item => item.reasons.some(reason => reason.startsWith('missing-raw-idea-anchor'))));
});
