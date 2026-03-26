const EVERGREEN_TOPICS = [
  "How to choose the right contractor for a home addition",
  "What to expect during a commercial renovation project",
  "Shell construction explained: what it is and when to use it",
  "The benefits of concrete construction for commercial buildings",
  "How to plan a residential renovation without losing your mind",
  "New addition vs. moving: which makes more financial sense?",
  "What questions to ask a general contractor before hiring",
  "How long does a home addition really take?",
  "Understanding building permits in Illinois",
  "5 signs your commercial property needs a renovation",
  "The difference between renovation and remodeling",
  "How to budget for a construction project realistically",
  "Why experienced contractors matter for concrete work",
  "What is a shell build and who is it for?",
  "How to stage your home during a major renovation",
];

function getRandomTopic() {
  return EVERGREEN_TOPICS[Math.floor(Math.random() * EVERGREEN_TOPICS.length)];
}

module.exports = { EVERGREEN_TOPICS, getRandomTopic };
