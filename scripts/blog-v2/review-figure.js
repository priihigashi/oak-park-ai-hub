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
function figureTitle(type) {
  return { 'decision-flow': 'Planning sequence', 'scope-map': 'Scope areas to review', 'evidence-map': 'Evidence and planning map' }[type];
}
function selectSteps(parts, draft) {
  const allSteps = figureSteps(draft, parts);
  const sourced = allSteps.filter(step => step.kind === 'source');
  return sourced.length >= 3 ? sourced : allSteps;
}
function captionForSteps(steps) {
  return steps.some(step => step.kind === 'editorial')
    ? 'Original draft evidence map. Source claims and OPC planning notes are labeled separately.'
    : 'Original draft evidence map. Every node is a source-backed claim; no sequence is implied.';
}
function withoutFigure(draft, body) {
  return { ...draft, body, figures: [] };
}
function diagramEnabled(options) {
  return (options.enabled ?? (process.env.OPC_ENABLE_ORIGINAL_DIAGRAMS === '1')) === true;
}
function addReviewFigure(draft, options = {}) {
  if (!diagramEnabled(options)) return draft;
  if (!['scope-map', 'evidence-explainer'].includes(draft.formatKey)) return withoutFigure(draft, String(draft.body || '').replaceAll(MARKER, ''));
  const cleanBody = String(draft.body || '').replaceAll(MARKER, '').replace(/\n{3,}/g, '\n\n');
  const parts = sections(cleanBody);
  if (parts.length < 3 || parts.length > 5) return withoutFigure(draft, cleanBody);
  const firstSection = cleanBody.indexOf('\n\n## ');
  if (firstSection < 0) return withoutFigure(draft, cleanBody);
  const steps = selectSteps(parts, draft);
  const digest = crypto.createHash('sha256').update(cleanBody).digest('hex').slice(0, 16);
  const type = draft.formatKey === 'evidence-explainer' ? 'evidence-map' : 'scope-map';
  const title = figureTitle(type);
  const alt = `${title}: ${steps.map(step => step.label || step.text).join('; ')}`;
  const figure = { id: 'planning-map', type, title, alt, caption: captionForSteps(steps), provenance: `OPC draft runner from article sections; body SHA-256 ${digest}; no external asset`, rights: 'OPC original diagram', approved: false, steps };
  return { ...draft, body: cleanBody.slice(0, firstSection) + '\n\n' + MARKER + cleanBody.slice(firstSection), figures: [figure] };
}
module.exports = { addReviewFigure, MARKER };
