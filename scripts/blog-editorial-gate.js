// A topic classifier can suggest ideas; it cannot approve an article or publish it.
// The old 🚀 Queued status may have been set by a classifier, so it is excluded.
function selectApprovedBlogRow(rows, columns) {
  for (let rowIndex = 0; rowIndex < rows.length; rowIndex += 1) {
    const row = rows[rowIndex];
    if ((row[columns.status] || '').trim() !== '✅ Approved') continue;
    if ((row[columns.blogUrl] || '').trim()) continue;
    if (!(row[columns.rawIdea] || '').trim()) continue;
    return { row, rowIndex };
  }
  return null;
}

function buildWordPressDraftBody(post, featuredMediaId, wpCategoryId) {
  const body = {
    title: post.title,
    content: post.html_content,
    excerpt: post.meta_description,
    status: 'draft',
    categories: wpCategoryId ? [Number.parseInt(wpCategoryId, 10)] : [],
  };
  if (featuredMediaId) body.featured_media = featuredMediaId;
  return body;
}

module.exports = { selectApprovedBlogRow, buildWordPressDraftBody };
