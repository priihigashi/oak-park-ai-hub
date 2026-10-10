const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { selectTopic, validateDraft, formatErrors, terminalArtifactErrors, geographicErrors, claimGeographyErrors, diagramErrors, writeRun, bodyWordCount, sourceGeographyErrors } = require('../blog-v2/pipeline');
const { addReviewFigure } = require('../blog-v2/review-figure');
const { verifySources, needsRevision, loadPriorRun, generateBundle, bundleStatus, draftPrompt, reviewPrompt: articleReviewPrompt, revisionPrompt } = require('../blog-v2/cli');
const { batchGate, readVerifiedRun, reviewPrompt } = require('../blog-v2/batch-review');
const { verifiedCompanyService, standaloneTradeErrors } = require('../blog-v2/company-scope');
const { planMedia } = require('../blog-v2/media-plan');
const { nextSnapshot } = require('../blog-v2/next-snapshot');

test('draft and repair prompts prohibit sources outside the verified run', () => {
  const brief = { service: 'commercial build-out', area: 'Broward County', question: 'What should be checked?', readerDecision: 'Check accessibility scope' };
  const sources = [{ id: 'doj', url: 'https://www.ada.gov/resources/title-iii-primer/', retrievedExcerpt: 'Alterations can affect accessibility.' }];
  assert.match(draftPrompt(brief, sources), /EXCLUSIVE whitelist/);
  assert.match(draftPrompt(brief, sources), /standalone OPC services/);
  assert.match(draftPrompt(brief, sources), /never describe the research packet as 'supplied sources'/);
  assert.match(draftPrompt(brief, sources), /For national-only evidence, identify the federal source in the description/);
  assert.match(draftPrompt(brief, sources), /including conditional permit or approval requirements/);
  assert.match(draftPrompt(brief, sources), /state the source retrieval date from retrievedAt/);
  assert.match(articleReviewPrompt(brief, {}, sources), /matching claims\[\] entry/);
  assert.match(articleReviewPrompt(brief, {}, sources), /visible as-of retrieval date/);
  assert.match(revisionPrompt(brief, sources, {}, { decision: 'revise' }), /never add, recall, search for, or cite another source/);
});
test('company service scope is read from the existing knowledge file', () => {
  assert.equal(verifiedCompanyService('home addition'), true);
  assert.equal(verifiedCompanyService('commercial build-out'), true);
  assert.equal(verifiedCompanyService('standalone roofing'), false);
  assert.deepEqual(standaloneTradeErrors('Oak Park Construction offers standalone roofing services.'), ['unsupported-standalone-trade']);
  assert.deepEqual(standaloneTradeErrors('Roofing is coordinated inside a full renovation.'), []);
});
test('photo planning keeps uncleared or unrelated assets out and never auto-approves', () => {
  const cleared = { id: 'opc-1', projectId: 'job-1', sourceDriveId: 'drive-1', approvedForBlog: true, privacyChecked: true, rights: 'OPC-owned', serviceTags: ['home addition'], alt: 'Framing at an OPC addition', caption: 'OPC addition framing' };
  const plan = planMedia([cleared, { ...cleared, id: 'wrong-service', serviceTags: ['commercial build-out'] }, { ...cleared, id: 'uncleared', privacyChecked: false }], { service: 'home addition' });
  assert.deepEqual(plan.candidates.map(asset => asset.id), ['opc-1']);
  assert.equal(plan.approved, false);
  assert.equal(plan.chosenAssetId, null);
  assert.equal(planMedia([], { service: 'home addition' }).status, 'no-cleared-match');
});
test('repeated question headings from the failed acceptance batch violate a direct-answer format', () => {
  const selected = { formatKey: 'scope-map' };
  const oldPattern = { formatKey: 'scope-map', body: '## Which rules apply here?\n\nAsk the team.\n\n## What should the team verify?\n\nAsk the team.\n\n## Who reviews the plan?\n\nAsk the team.' };
  assert.ok(formatErrors(oldPattern, selected).includes('question-list-format-drift'));
  const revised = { formatKey: 'scope-map', body: '## Federal scope\n\nThe cited rule applies here.\n\n## Florida scope\n\nThe statute adds its own requirement.' };
  assert.deepEqual(formatErrors(revised, selected), []);
});
test('national guidance cannot license a Broward headline while county evidence can', () => {
  const draft = { title: 'Broward County Kitchen Exhaust Planning', slug: 'broward-kitchen-exhaust', description: 'Broward advice' };
  assert.deepEqual(geographicErrors(draft, { area: 'Broward County', evidenceScope: 'unscoped' }), ['unsupported-local-framing']);
  assert.deepEqual(geographicErrors(draft, { area: 'Broward County', evidenceScope: 'Broward County' }), []);
  const claim = { id: 'c1', text: 'Broward County requires this work.' };
  assert.deepEqual(claimGeographyErrors(claim, { coverageAreas: ['Florida'] }, { area: 'Broward County' }), ['unsupported-claim-geography:c1']);
  assert.deepEqual(claimGeographyErrors(claim, { coverageAreas: ['Broward County'] }, { area: 'Broward County' }), []);
});
test('a Florida statute cannot be cataloged as county-specific evidence', () => {
  const statute = { ...source, id: 'fl-statute', url: 'https://www.leg.state.fl.us/statutes/index.cfm?section=553.504', coverageAreas: ['Broward County'] };
  assert.deepEqual(sourceGeographyErrors(statute), ['state-statute-marked-county:fl-statute']);
  assert.throws(() => selectTopic({ ...snapshot, sources: [statute], candidates: [{ ...candidate, sourceIds: ['fl-statute'] }] }), /Invalid source geography/);
  assert.deepEqual(sourceGeographyErrors({ ...statute, coverageAreas: ['Florida'] }), []);
});
test('Council round five requires a reader artifact in the final section', () => {
  const selected = { formatKey: 'evidence-explainer' };
  assert.deepEqual(terminalArtifactErrors({ body: '## Planning consequence\n\nAsk the design team to verify the scope.' }, selected), ['missing-format-specific-reader-artifact']);
  assert.deepEqual(terminalArtifactErrors({ body: '## Planning consequence\n\n| Evidence establishes | Evidence does not establish |\n| --- | --- |\n| A relevant fact | A project-specific outcome |' }, selected), []);
  assert.deepEqual(terminalArtifactErrors({ body: '## Final scope\n\n- Use approval\n- Work approval' }, { formatKey: 'scope-map' }), ['missing-format-specific-reader-artifact']);
  assert.deepEqual(terminalArtifactErrors({ body: '## Final steps\n\n1. Gather the site plan.\n2. Compare the floor plan.' }, { formatKey: 'sequence-walkthrough' }), []);
});
test('original diagram binds sourced nodes to the reviewed claim and labels editorial nodes', () => {
  const draft = { title: 'A plan', formatKey: 'scope-map', body: 'Intro.\n\n## Source point\n\nThe cited rule applies. [Agency](https://example.gov/rule)\n\n## Design point\n\nRecord the layout.\n\n## Final point\n\nConfirm the scope.', claims: [{ id: 'c1', text: 'The cited rule applies.', sourceId: 's1', status: 'verified' }] };
  const result = addReviewFigure(draft, { enabled: true });
  assert.deepEqual(result.figures[0].steps.map(step => step.kind), ['source', 'editorial', 'editorial']);
  assert.deepEqual(diagramErrors(result, { formatKey: 'scope-map' }), []);
  result.figures[0].type = 'decision-flow';
  assert.ok(diagramErrors(result, { formatKey: 'scope-map' }).includes('figure-provenance-invalid'));
  result.figures[0].type = 'scope-map';
  result.figures[0].steps[0].sourceId = 'unsupplied';
  assert.ok(diagramErrors(result, { formatKey: 'scope-map' }).includes('unbound-source-step'));
});
test('a weak evidence explainer stays text-only after the kitchen figure review', () => {
  const draft = { formatKey: 'evidence-explainer', body: 'A sourced explanation.' };
  const result = addReviewFigure(draft, { enabled: true });
  assert.deepEqual(result.figures, []);
  assert.deepEqual(diagramErrors(result, { formatKey: 'evidence-explainer' }), []);
});
test('scope map can be text-only when an automatic figure adds no independent value', () => {
  const draft = { formatKey: 'scope-map', body: '## Use permission\n\nA CU addresses use.\n\n## Work permission\n\nRenovation approvals are separate.', figures: [] };
  assert.deepEqual(diagramErrors(draft, { formatKey: 'scope-map' }), []);
  assert.deepEqual(diagramErrors({ ...draft, body: `<!-- FIGURE:planning-map -->\n${draft.body}` }, { formatKey: 'scope-map' }), ['figure-marker-mismatch']);
});
test('series gate keeps factual-pass drafts held when independent editorial review finds repeated work', () => {
  const runs = ['scope-map', 'evidence-explainer', 'sequence-walkthrough'].map((formatKey, i) => ({ id: `run-${i}`, brief: { intentKey: `intent-${i}`, formatKey }, draft: { title: `Article ${i}`, body: 'A direct answer.' }, sources: [], articleReview: { decision: 'pass' } }));
  const review = { decision: 'hold', findings: [{ severity: 'major', issue: 'Three articles defer the answer', evidence: 'Repeated question lists' }] };
  assert.ok(batchGate(runs, review).includes('independent-batch-hold'));
  assert.match(reviewPrompt(runs), /direct source-supported answers/);
  assert.deepEqual(batchGate(runs, { decision: 'trial_ready', findings: [] }), []);
});
test('series review refuses a draft altered after its article receipt was written', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-batch-tamper-'));
  try {
    const run = writeRun(root, { snapshot: {}, selection: { selected: null }, brief: { intentKey: 'test' }, draft: { title: 'Original', body: 'Body' }, sources: [], review: { decision: 'pass' }, gate: [], status: 'draft-ready-for-human-review' });
    assert.equal(readVerifiedRun(run).draft.title, 'Original');
    fs.writeFileSync(path.join(run, 'draft.json'), JSON.stringify({ title: 'Changed' }));
    assert.throws(() => readVerifiedRun(run), /has changed/);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
test('an article-ready pilot moves its intent into the next private snapshot', () => {
  const input = { candidates: [{ id: 'pilot-a' }, { id: 'pilot-b' }], existing: [] };
  const run = { id: 'run-a', receiptHash: 'abc', brief: { id: 'pilot-a', intentKey: 'distinct-a', readerDecision: 'Answer A' }, draft: { title: 'Article A' } };
  const next = nextSnapshot(input, run);
  assert.equal(next.existing[0].type, 'queued');
  assert.equal(next.existing[0].receiptHash, 'abc');
  assert.throws(() => nextSnapshot(next, run), /already in the inventory/);
  assert.throws(() => nextSnapshot(input, { ...run, brief: { ...run.brief, id: 'missing' } }), /absent from input snapshot/);
});
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
test('v3 editorial floor counts visible words and rejects a 399-word draft', () => {
  const shortBody = Array(399).fill('guidance').join(' ');
  const longBody = Array(400).fill('guidance').join(' ');
  assert.equal(bodyWordCount(`[County guidance](https://example.gov/long/path) ${Array(398).fill('guidance').join(' ')}`), 400);
  assert.ok(validateDraft({ title: 'Guide', description: 'Guide', body: shortBody, claims: [], visuals: [] }, candidate, snapshot).includes('incomplete-article'));
  assert.ok(!validateDraft({ title: 'Guide', description: 'Guide', body: longBody, claims: [], visuals: [] }, candidate, snapshot).includes('incomplete-article'));
});
test('a linked publisher name counts as visible claim text', () => {
  const claim = { id: 'office', text: 'County guidance says home additions require a permit before construction begins.', sourceId: 's1', evidence: source.excerpt, checkedAt: '2026-10-10', status: 'verified' };
  const body = `[County guidance](${source.url}) says home additions require a permit before construction begins. ${'Owners should confirm the applicable local office. '.repeat(20)}`;
  const errors = validateDraft({ title: 'Addition guide', description: 'Guide', body, claims: [claim], visuals: [] }, candidate, snapshot);
  assert.ok(!errors.includes('claim-not-in-body:office'));
});
test('revised claim text must match a visible sentence with its citation in the same paragraph', () => {
  const claim = { id: 'permit', text: 'Home additions require a permit before construction begins.', sourceId: 's1', evidence: source.excerpt, checkedAt: '2026-10-10', status: 'verified' };
  const filler = Array(400).fill('guidance').join(' ');
  const paraphrased = { title: 'Guide', description: 'Guide', body: `Home additions need a permit before work starts. [County](${source.url})\n\n${filler}`, claims: [claim], visuals: [] };
  assert.ok(validateDraft(paraphrased, candidate, snapshot).includes('claim-not-in-body:permit'));
  const distantCitation = { ...paraphrased, body: `${claim.text}\n\n[County](${source.url})\n\n${filler}` };
  assert.ok(validateDraft(distantCitation, candidate, snapshot).includes('missing-inline-citation:permit'));
  const exact = { ...paraphrased, body: `${claim.text} [County](${source.url})\n\n${filler}` };
  const errors = validateDraft(exact, candidate, snapshot);
  assert.ok(!errors.includes('claim-not-in-body:permit'));
  assert.ok(!errors.includes('missing-inline-citation:permit'));
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
test('source receipt and reviewer context use a matched passage after long navigation', async () => {
  const original = global.fetch;
  const navigation = 'Navigation menu account services links '.repeat(110);
  const guidance = 'Home additions require a permit before construction begins and plans must be reviewed.';
  global.fetch = async () => ({ ok: true, status: 200, text: async () => `<html><body>${navigation}<main>${guidance}</main></body></html>` });
  try {
    const result = await verifySources([source]);
    assert.ok(result[0].retrievedExcerpt.includes(guidance));
    assert.ok(result[0].retrievedExcerpt.length <= 1600);
    assert.equal(result[0].retrieval, 'http');
  } finally { global.fetch = original; }
});
test('official PDF source is extracted and checked against the supplied excerpt', async () => {
  const original = global.fetch;
  const bytes = fs.readFileSync(path.join(__dirname, 'fixtures', 'blog-source.pdf'));
  const pdf = { ...source, id: 'county-patio-pdf', url: 'https://example.gov/patio.pdf', excerpt: 'A site plan and survey show property lines. The applicant should include the proposed patio dimensions and materials.' };
  global.fetch = async () => ({ ok: true, status: 200, headers: { get: () => 'application/pdf' }, arrayBuffer: async () => bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) });
  try {
    const result = await verifySources([pdf]);
    assert.equal(result[0].retrieval, 'http-pdf');
    assert.match(result[0].retrievedExcerpt, /proposed patio dimensions and materials/);
    await assert.rejects(verifySources([{ ...pdf, excerpt: 'Completely unrelated legal rules and fees for a different project' }]), /excerpt is not supported/);
  } finally { global.fetch = original; }
});
test('one bounded revision retains both independent reviews and rejects a second resume', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'opc-blog-revision-'));
  const originalArgs = process.argv;
  try {
    const draft = { title: 'Guide', description: 'Guide', body: Array(410).fill('guidance').join(' '), claims: [], visuals: [] };
    const blockedReview = { decision: 'revise', findings: [{ severity: 'major', issue: 'Unsupported sentence', evidence: 'Source passage' }], summary: 'Revise' };
    const revisedDraft = { ...draft, body: Array(420).fill('verified').join(' ') };
    const revisedReview = { decision: 'pass', findings: [], summary: 'Ready for human review' };
    const priorDir = writeRun(root, { rawSnapshot: snapshot, intake: null, snapshot, selection: { selected: candidate }, sources: [source], brief: candidate, draft, review: blockedReview, gate: ['independent-review-blocked'], status: 'review-required' });
    const prior = loadPriorRun(priorDir);
    const draftPath = path.join(root, 'revised-draft.json'), reviewPath = path.join(root, 'revised-review.json');
    fs.writeFileSync(draftPath, JSON.stringify(revisedDraft));
    fs.writeFileSync(reviewPath, JSON.stringify(revisedReview));
    process.argv = ['node', 'cli.js', '--fixture-revised-draft', draftPath, '--fixture-revised-review', reviewPath];
    const bundle = generateBundle('fixture', candidate, [source], prior);
    assert.equal(bundle.revision.attempts, 1);
    assert.deepEqual(bundle.originalReview, blockedReview);
    assert.deepEqual(bundle.revisedReview, revisedReview);
    assert.deepEqual(bundle.draft, revisedDraft);
    const revisedDir = writeRun(root, { ...bundle, rawSnapshot: snapshot, intake: null, snapshot, selection: { selected: candidate }, sources: [source], brief: candidate, priorRun: prior.priorRun, gate: [], status: 'review-required' });
    assert.throws(() => loadPriorRun(revisedDir), /already used its one revision attempt/);
    fs.writeFileSync(path.join(priorDir, 'draft.json'), '{}');
    assert.throws(() => loadPriorRun(priorDir), /hash mismatch/);
  } finally { process.argv = originalArgs; fs.rmSync(root, { recursive: true, force: true }); }
});
test('revision trigger includes reviewer decision or a major finding', () => {
  assert.equal(needsRevision({ decision: 'revise', findings: [] }), true);
  assert.equal(needsRevision({ decision: 'pass', findings: [{ severity: 'major' }] }), true);
  assert.equal(needsRevision({ decision: 'pass', findings: [{ severity: 'minor' }] }), false);
});
test('failed revised draft has explicit terminal gate status and one-pass prompt', () => {
  assert.equal(bundleStatus({ revisedDraft: {} }, ['claim-not-in-body:c1']), 'revision-gate-failed');
  assert.equal(bundleStatus({ draft: {} }, ['incomplete-article']), 'review-required');
  assert.equal(bundleStatus({ revisedDraft: {} }, []), 'draft-ready-for-human-review');
  const prompt = revisionPrompt(candidate, [source], { body: 'draft' }, { decision: 'revise', findings: [] });
  assert.match(prompt, /claim\.text exactly/);
  assert.match(prompt, /SAME paragraph/);
  assert.match(prompt, /air changes per hour/);
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
test('intake retains one candidate per reader intent and audits duplicate idea rows', () => {
  const sources = [{ ...source, id: 'broward-permit', sourceRole: 'topic-specific', themeTags: ['addition-planning'], coverageAreas: ['Broward County'] }];
  const rows = [
    { rowNumber: 12, rawIdea: 'Home addition in Fort Lauderdale' },
    { rowNumber: 131, rawIdea: 'Home addition planning in Broward', topicDirection: 'Permit planning before design' },
    { rowNumber: 348, rawIdea: 'Home addition cost in Broward' },
  ];
  const result = intakeIdeas(rows, sources);
  assert.equal(result.candidates.length, 1);
  assert.equal(result.candidates[0].id, 'content-ideas-row-131');
  assert.deepEqual(result.rejected.filter(item => item.reasons[0].startsWith('duplicate-idea-intent')).map(item => item.id), ['content-ideas-row-12', 'content-ideas-row-348']);
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
  assert.equal(supported.candidates[0].evidenceScope, 'unscoped');
  assert.doesNotMatch(supported.candidates[0].question, /Broward/);
  const florida = { ...source, id: 'florida-accessibility', sourceRole: 'topic-specific', themeTags: ['retail-accessibility'], coverageAreas: ['Florida'] };
  const statewide = intakeIdeas([row], [doj, florida]);
  assert.equal(statewide.candidates[0].evidenceScope, 'Florida');
  assert.match(statewide.candidates[0].question, /in Florida/);
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
