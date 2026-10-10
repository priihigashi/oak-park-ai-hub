// A shortlist for human review, never an asset approval or publication instruction.
function approvedCatalogRecord(asset, service) {
  if (!asset) return false;
  return [asset.approvedForBlog === true, asset.privacyChecked === true,
    asset.rights === 'OPC-owned', asset.sourceDriveId, asset.projectId,
    asset.serviceTags?.includes(service), asset.alt?.trim(), asset.caption?.trim()].every(Boolean);
}
function planMedia(catalog, brief) {
  const candidates = (Array.isArray(catalog) ? catalog : [])
    .filter(asset => approvedCatalogRecord(asset, brief.service))
    .map(asset => ({ id: asset.id, projectId: asset.projectId, sourceDriveId: asset.sourceDriveId, alt: asset.alt, caption: asset.caption, rights: asset.rights }));
  return {
    status: candidates.length ? 'candidate-review' : 'no-cleared-match',
    candidates,
    chosenAssetId: null,
    approved: false,
    fallback: 'text-only or independently reviewed original diagram',
    note: 'A human must check relevance, rights, privacy, and exact derivative before attaching media.',
  };
}
module.exports = { planMedia };
