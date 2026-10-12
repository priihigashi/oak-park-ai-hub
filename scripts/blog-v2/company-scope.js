const { COMPANY } = require('../company-info');

const SERVICE_PREFIX = {
  'home renovation': 'Full home renovation',
  'home addition': 'New additions',
  'shell construction': 'Shell construction',
  'concrete work': 'Concrete work',
  'deck construction': 'Deck construction',
  'screen porch enclosure': 'Screen porch enclosures',
  'commercial renovation': 'Commercial renovation and build-outs',
  'commercial build out': 'Commercial renovation and build-outs',
  'commercial construction': 'Commercial construction',
};
const normalize = value => String(value || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();

function verifiedCompanyService(service) {
  const prefix = SERVICE_PREFIX[normalize(service)];
  return Boolean(prefix && COMPANY.services.core.some(item => item.startsWith(prefix)));
}
function companyScope() {
  return {
    source: 'scripts/company-info.js',
    core: COMPANY.services.core,
    onlyWithinFullProjects: COMPANY.services.includedAsPartOfFullProject,
    doNotTarget: COMPANY.doNotTarget,
    voice: COMPANY.brandVoice.contentPhilosophy,
  };
}
function standaloneTradeErrors(body) {
  const claimsStandalone = /\b(?:we|oak park construction|opc)\s+(?:offers?|provides?|handles?|performs?|does|do)\s+(?:standalone\s+|stand-alone\s+|roofing-only\s+|plumbing-only\s+|electrical-only\s+)(?:roofing|plumbing|electrical)?(?:\s+(?:jobs|work|services))?\b/i;
  return claimsStandalone.test(String(body || '')) ? ['unsupported-standalone-trade'] : [];
}
module.exports = { verifiedCompanyService, companyScope, standaloneTradeErrors };
