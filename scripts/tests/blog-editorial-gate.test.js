const test = require('node:test');
const assert = require('node:assert/strict');
const { selectApprovedBlogRow, buildWordPressDraftBody } = require('../blog-editorial-gate.js');

const columns = { rawIdea: 4, topicDirection: 5, status: 19, blogUrl: 20 };
const row = (status, idea, blogUrl = '') => {
  const values = Array(23).fill('');
  values[columns.status] = status;
  values[columns.rawIdea] = idea;
  values[columns.topicDirection] = idea;
  values[columns.blogUrl] = blogUrl;
  return values;
};

test('classifier-queued, raw, and already drafted rows cannot start a paid draft', () => {
  const rows = [
    row('🚀 Queued', 'Legacy auto-approved idea'),
    row('🆕 Idea', 'Unreviewed idea'),
    row('✅ Approved', 'Already drafted', 'https://example.com/draft'),
    row('✅ Approved', 'Owner-reviewed brief'),
  ];
  assert.equal(selectApprovedBlogRow(rows, columns)?.rowIndex, 3);
  assert.equal(selectApprovedBlogRow(rows.slice(0, 3), columns), null);
});

test('WordPress payload stays a draft regardless of post metadata', () => {
  const body = buildWordPressDraftBody({ title: 'Sample', html_content: '<p>Text</p>', meta_description: 'Summary', status: 'publish' }, 42, '7');
  assert.equal(body.status, 'draft');
  assert.equal(body.featured_media, 42);
  assert.deepEqual(body.categories, [7]);
});
