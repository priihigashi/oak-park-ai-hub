// A score is evidence for routing, never publication authority by itself.
// The auto-publication threshold requires calibration against real reviewed articles.
const CRITERIA = Object.freeze({
  readerAnswer: 25,
  factualSupport: 25,
  serviceAndAreaFit: 15,
  clarity: 15,
  searchIntent: 10,
  visualIntegrity: 10,
});

function scoreEditorial(review, gate) {
  const ratings = review?.ratings;
  if (!ratings || Object.keys(CRITERIA).some(key =>
    !Number.isInteger(ratings[key]?.rating) || ratings[key].rating < 0 || ratings[key].rating > 4
    || typeof ratings[key].evidence !== 'string' || !ratings[key].evidence.trim())) {
    return { rubricVersion: 'opc-blog-editorial-v1', score: null, criteria: CRITERIA, route: gate.length ? 'blocked' : 'human-review', reasons: ['missing-or-invalid-editorial-ratings', 'auto-publication-threshold-uncalibrated'] };
  }
  const score = Math.round(Object.entries(CRITERIA).reduce((sum, [key, weight]) => sum + weight * ratings[key].rating / 4, 0));
  const reasons = ['auto-publication-threshold-uncalibrated'];
  if (gate.length) reasons.unshift('article-gate-blocked');
  return { rubricVersion: 'opc-blog-editorial-v1', score, criteria: CRITERIA, ratings, route: gate.length ? 'blocked' : 'human-review', reasons };
}

module.exports = { CRITERIA, scoreEditorial };
