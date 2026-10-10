const crypto = require('node:crypto');

const MARKER = '<!-- FIGURE:addition-three-views -->';
function addThreeViewFigure(draft, brief) {
  if (brief.figureConcept !== 'addition-three-views') return draft;
  const cleanBody = String(draft.body || '').replaceAll(MARKER, '').replace(/\n{3,}/g, '\n\n');
  const claim = (draft.claims || []).find(item => /site plan/i.test(item.text) && /floor plan/i.test(item.text) && /elevation plan/i.test(item.text) && item.status === 'verified');
  const heading = cleanBody.match(/^## .*views.*$/im);
  if (!claim || !heading) return { ...draft, body: cleanBody, figures: [] };
  const digest = crypto.createHash('sha256').update(cleanBody).digest('hex').slice(0, 16);
  const figure = {
    id: 'addition-three-views', type: 'three-view-diagram',
    title: 'One addition in three conceptual views',
    alt: 'Three simplified views show the same proposed addition beside an existing home: property footprint, interior floor arrangement, and exterior form.',
    caption: 'Concept illustration only. These are not permit drawings and do not show zoning compliance.',
    provenance: `OPC original conceptual diagram; County checklist claim ${claim.id}; body SHA-256 ${digest}; no external asset`,
    rights: 'OPC original diagram', approved: false, claimId: claim.id, sourceId: claim.sourceId,
  };
  const position = heading.index + heading[0].length;
  return { ...draft, body: cleanBody.slice(0, position) + '\n\n' + MARKER + cleanBody.slice(position), figures: [figure] };
}
module.exports = { addThreeViewFigure, MARKER };
