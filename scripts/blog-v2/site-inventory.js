const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

function readJson(file) { return JSON.parse(fs.readFileSync(file, 'utf8')); }
function fileHash(file) { return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'); }
function fromSite(frontendDir) {
  const postFile = path.join(frontendDir, 'src/blog/posts.json');
  const legacyFile = path.join(frontendDir, 'src/data/legacyBlogPaths.json');
  const posts = readJson(postFile);
  const legacy = readJson(legacyFile);
  if (!Array.isArray(posts) || !Array.isArray(legacy.paths)) throw new Error('Site blog inventory is malformed');
  const current = posts.map(post => {
    if (!post.slug || !post.title) throw new Error('Site blog post has no slug or title');
    return { id: `site:${post.slug}`, slug: post.slug, title: post.title, intent: post.description || '', sourceKind: 'react-site' };
  });
  const old = legacy.paths
    .map(value => value.replace(/^\/+|\/+$/g, ''))
    .filter(slug => slug && slug !== 'blog')
    .map(slug => ({ id: `legacy:${slug}`, slug, title: slug.replace(/-/g, ' '), intent: '', sourceKind: 'legacy-wordpress-route' }));
  const inventory = [...current, ...old];
  if (new Set(inventory.map(entry => entry.id)).size !== inventory.length) throw new Error('Site blog inventory contains duplicate routes');
  return { inventory, siteEvidence: { reactPosts: current.length, legacyRoutes: old.length, postsSha256: fileHash(postFile), legacySha256: fileHash(legacyFile) } };
}
function addSiteInventory(rawSnapshot, frontendDir) {
  const { inventory, siteEvidence } = fromSite(frontendDir);
  const existing = [...(rawSnapshot.existing || [])];
  const canonical = value => String(value || '').replace(/^\/+|\/+$/g, '');
  const bySlug = new Map(existing.map((item, index) => [canonical(item.slug), index]).filter(([slug]) => slug));
  for (const item of inventory) {
    const slug = canonical(item.slug);
    if (bySlug.has(slug)) {
      const index = bySlug.get(slug);
      existing[index] = { ...existing[index], ...item };
    } else {
      bySlug.set(slug, existing.length);
      existing.push(item);
    }
  }
  return { ...rawSnapshot, existing, siteEvidence };
}
module.exports = { fromSite, addSiteInventory };
