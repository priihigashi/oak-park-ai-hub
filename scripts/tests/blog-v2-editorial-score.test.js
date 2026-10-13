const test = require('node:test');
const assert = require('node:assert/strict');
const { CRITERIA, scoreEditorial, scoreDualEditorial } = require('../blog-v2/editorial-score');

function review(rating) {
  return { decision: 'pass', ratings: Object.fromEntries(Object.keys(CRITERIA).map(key => [key, { rating, evidence: `Observed ${key} in the exact draft` }])) };
}

test('editorial score records weighted evidence without granting auto publication', () => {
  const high = scoreEditorial(review(4), []);
  assert.equal(high.score, 100);
  assert.equal(high.route, 'human-review');
  assert.deepEqual(high.reasons, ['auto-publication-threshold-uncalibrated']);
  assert.equal(scoreEditorial(review(3), []).score, 75);
});

test('hard gate blocks routing even with a perfect editorial score', () => {
  const blocked = scoreEditorial(review(4), ['unsupported-claim']);
  assert.equal(blocked.score, 100);
  assert.equal(blocked.route, 'blocked');
  assert.ok(blocked.reasons.includes('article-gate-blocked'));
});

test('missing or unsupported ratings cannot silently earn a score', () => {
  const incomplete = review(4);
  delete incomplete.ratings.factualSupport;
  assert.equal(scoreEditorial(incomplete, []).score, null);
  const vague = review(4);
  vague.ratings.clarity.evidence = '';
  assert.equal(scoreEditorial(vague, []).route, 'human-review');
  const outOfRange = review(5);
  assert.equal(scoreEditorial(outOfRange, []).score, null);
});

test('dual editorial score uses the lower independent rating and never overrides a veto', () => {
  const scored = scoreDualEditorial(review(4), review(3), []);
  assert.equal(scored.score, 75);
  assert.deepEqual(scored.providerScores, { claude: 100, codex: 75 });
  assert.equal(scored.route, 'human-review');
  assert.equal(scoreDualEditorial(review(4), review(4), ['codex:independent-review-findings']).route, 'blocked');
  assert.equal(scoreDualEditorial(review(4), null, []).score, null);
});
