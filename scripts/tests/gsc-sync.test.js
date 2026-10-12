const test = require('node:test');
const assert = require('node:assert/strict');

process.env.GSC_SITE_URL = 'sc-domain:oakpark-construction.com';
const { fetchGSCData } = require('../gsc-sync.js');

test('permission errors fail instead of being reported as pages without data', async () => {
  const originalFetch = global.fetch;
  global.fetch = async () => ({ ok: false, status: 403, text: async () => 'Permission denied' });
  try {
    await assert.rejects(
      fetchGSCData('token', 'https://oakpark-construction.com/example/'),
      /GSC API error 403.*Permission denied/
    );
  } finally {
    global.fetch = originalFetch;
  }
});

test('a successful empty Search Console response remains no page data', async () => {
  const originalFetch = global.fetch;
  global.fetch = async () => ({ ok: true, json: async () => ({ rows: [] }) });
  try {
    assert.equal(await fetchGSCData('token', 'https://oakpark-construction.com/example/'), null);
  } finally {
    global.fetch = originalFetch;
  }
});
