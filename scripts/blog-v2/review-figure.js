const crypto = require('node:crypto');

const MARKER = '<!-- FIGURE:planning-map -->';
function sections(body) {
  const blocks = String(body).replaceAll(MARKER, '').split(/\n\s*\n/).filter(Boolean);
  const result = [];
  for (let i = 0; i < blocks.length; i += 1) {
    if (!blocks[i].startsWith('## ')) continue;
    const start = i + 1;
    let end = start;
    while (end < blocks.length && !blocks[end].startsWith('## ')) end += 1;
    result.push({ heading: blocks[i].slice(3).trim(), text: blocks.slice(start, end).join('\n\n') });
  }
  return result;
}
function figureSteps(draft, parts) {
  return parts.map(part => {
    const claim = (draft.claims || []).find(item => part.text.includes(item.text));
    return claim ? { label: part.heading, text: claim.text, kind: 'source', claimId: claim.id, sourceId: claim.sourceId }
      : { text: part.heading, kind: 'editorial' };
  });
}
const TYPES = { 'scope-map': 'scope-map', 'evidence-explainer': 'evidence-map', 'sequence-walkthrough': 'decision-flow' };
function addReviewFigure(draft, options = {}) {
  if ((options.enabled ?? (process.env.OPC_ENABLE_ORIGINAL_DIAGRAMS === '1')) !== true) return draft;
  const cleanBody = String(draft.body || '').replaceAll(MARKER, '').replace(/\n{3,}/g, '\n\n');
  const parts = sections(cleanBody);
  if (parts.length < 3 || parts.length > 5) return { ...draft, body: cleanBody, figures: [] };
  const firstSection = cleanBody.indexOf('\n\n## ');
  if (firstSection < 0) return { ...draft, body: cleanBody, figures: [] };
  const allSteps = figureSteps(draft, parts);
  const steps = allSteps.filter(step => step.kind === 'source').length >= 3 ? allSteps.filter(step => step.kind === 'source') : allSteps;
  const digest = crypto.createHash('sha256').update(cleanBody).digest('hex').slice(0, 16);
  const type = TYPES[draft.formatKey] || 'evidence-map';
  const title = type === 'decision-flow' ? 'Planning sequence' : type === 'scope-map' ? 'Scope areas to review' : 'Evidence and planning map';
  const alt = `${title}: ${steps.map(step => step.label || step.text).join('; ')}`;
  const figure = { id: 'planning-map', type, title, alt, caption: 'Original draft diagram. Source claims and OPC planning notes are labeled separately.', provenance: `OPC draft runner from article sections; body SHA-256 ${digest}; no external asset`, rights: 'OPC original diagram', approved: false, steps };
  return { ...draft, body: cleanBody.slice(0, firstSection) + '\n\n' + MARKER + cleanBody.slice(firstSection), figures: [figure] };
}
module.exports = { addReviewFigure, MARKER };
