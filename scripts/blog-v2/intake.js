// Raw Content Ideas are inspiration only. Templates deliberately exclude hooks,
// payoffs, social assertions, and unverified project claims from the brief.
const THEMES = [
  { id: 'addition-planning', match: /\b(additions?|add on|second story|extra room|expand.*home)\b/i, service: 'home addition', question: area => `Which permit office should an owner check before planning a home addition in ${area}?`, decision: 'Identify the responsible permit office before defining an addition scope', sourceTags: ['permit', 'building'] },
  { id: 'screen-enclosure-planning', match: /\b(screen(?:ed)?\s*(?:porch|enclosure|patio)|porch enclosure|patio cover)\b/i, service: 'screen porch enclosure', question: area => `Where should an owner check permit requirements before planning a screen porch enclosure in ${area}?`, decision: 'Identify the responsible permit office before defining a screen enclosure scope', sourceTags: ['permit', 'building'] },
  { id: 'commercial-retail-buildout', match: /\b(retail|storefront|tenant improvement|commercial build.?out|office renovation)\b/i, service: 'commercial build-out', question: area => `Where should a business owner check permit and plan review requirements for a retail build-out in ${area}?`, decision: 'Identify the responsible permit office and plan review starting point before a retail build-out', sourceTags: ['permit', 'plan review', 'building'] },
  { id: 'permit-lookup', match: /\b(permit|license|licensed contractor|inspection|code review)\b/i, service: 'home renovation', question: area => `How can an owner find the correct permit office before a major home renovation in ${area}?`, decision: 'Find the correct local permit office before setting a renovation schedule', sourceTags: ['permit', 'building'] },
];
const AREAS = [
  { name: 'Miami-Dade County', test: /miami.dade|miami dade|\bmiami\b/i, source: /miami.?dade|miamidade/i },
  { name: 'Palm Beach County', test: /palm beach|boca raton/i, source: /palm beach/i },
  { name: 'Broward County', test: /broward|fort lauderdale|pompano|hollywood|deerfield|coral springs|parkland|weston/i, source: /broward/i },
];
const COL = { sourceLink: 3, rawIdea: 4, topicDirection: 5, hookProfessional: 9, hookEmotional: 10, hookGenZ: 11, masterHook: 12, readerPayoff: 13, status: 19, blogUrl: 20 };
function unpack(row, index) {
  if (Array.isArray(row)) return { rowNumber: index + 2, sourceLink: row[COL.sourceLink], rawIdea: row[COL.rawIdea], topicDirection: row[COL.topicDirection], hookProfessional: row[COL.hookProfessional], hookEmotional: row[COL.hookEmotional], hookGenZ: row[COL.hookGenZ], masterHook: row[COL.masterHook], readerPayoff: row[COL.readerPayoff], status: row[COL.status], blogUrl: row[COL.blogUrl] };
  return { ...row, rowNumber: row.rowNumber || row.row || index + 2 };
}
function relevantSources(sources, theme, area) {
  const areaPattern = AREAS.find(item => item.name === area).source;
  return sources.filter(source => {
    if (source.access === 'internal-preverified') return false;
    const searchable = [source.id, source.publisher, source.title, source.url, source.excerpt].join(' ').toLowerCase();
    return areaPattern.test(searchable) && theme.sourceTags.some(tag => searchable.includes(tag));
  });
}
function rowProvenance(row, options) {
  return { spreadsheetId: options.spreadsheetId || null, sheet: 'Content Ideas', row: row.rowNumber, status: row.status || '', inspirationUrl: row.sourceLink || '' };
}
function rowReasons(row, text, theme, sourceIds) {
  const reasons = [];
  if (/published|draft created|posted/i.test(row.status || '') || row.blogUrl) reasons.push('already-used-row');
  if (!text.trim()) reasons.push('empty-idea');
  if (!theme) reasons.push('unsupported-theme');
  if (theme && !sourceIds.length) reasons.push('no-topic-relevant-official-source');
  return reasons;
}
function classifyRow(row, sources, options) {
  const provenance = rowProvenance(row, options);
  const text = `${row.rawIdea || ''} ${row.topicDirection || ''}`;
  const theme = THEMES.find(item => item.match.test(text));
  const area = AREAS.find(item => item.test.test(text))?.name || options.defaultArea || 'Broward County';
  const sourceIds = theme ? relevantSources(sources, theme, area).map(s => s.id) : [];
  const reasons = rowReasons(row, text, theme, sourceIds);
  return { provenance, text, theme, area, sourceIds, reasons, id: `content-ideas-row-${row.rowNumber}` };
}
function toCandidate(classification) {
  const { id, theme, area, sourceIds, text, provenance } = classification;
  const planningSignals = ['permit', 'planning', 'process', 'requirements'].filter(term => new RegExp(`\\b${term}\\b`, 'i').test(text)).length;
  const intentFamily = ['addition-planning', 'permit-lookup'].includes(theme.id) ? 'residential-permit-office' : theme.id;
  return { id, question: theme.question(area), readerDecision: theme.decision, service: theme.service, area, sourceIds, theme: theme.id, intentKey: `${intentFamily}:${area.toLowerCase()}`, priority: planningSignals, inputProvenance: provenance };
}
function intakeIdeas(rows, sources, options = {}) {
  if (!Array.isArray(rows) || !Array.isArray(sources)) throw new Error('Intake requires raw idea rows and source catalog arrays');
  const candidates = [], rejected = [];
  rows.forEach((raw, index) => {
    const classification = classifyRow(unpack(raw, index), sources, options);
    if (classification.reasons.length) rejected.push({ id: classification.id, reasons: classification.reasons, provenance: classification.provenance });
    else candidates.push(toCandidate(classification));
  });
  return { candidates, rejected, rulesVersion: 'blog-v2-intake-2026-10-10' };
}
module.exports = { intakeIdeas, relevantSources };
