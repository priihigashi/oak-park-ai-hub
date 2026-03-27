// ─────────────────────────────────────────────────────────────────────────────
// Import existing WordPress posts into the Google Sheet
// Run once manually via GitHub Actions
// Fetches all published posts from WordPress, adds them to the sheet
// Skips any post whose URL is already in the sheet
// ─────────────────────────────────────────────────────────────────────────────

const GOOGLE_SHEET_ID  = process.env.GOOGLE_SHEET_ID;
const GOOGLE_SA_KEY    = process.env.GOOGLE_SA_KEY;
const WP_URL           = process.env.WP_URL;
const WP_USERNAME      = process.env.WP_USERNAME;
const WP_APP_PASSWORD  = process.env.WP_APP_PASSWORD;

const TODAY = new Date().toLocaleDateString('en-US', { timeZone: 'America/New_York' });

async function getGoogleToken(saKey) {
  const now = Math.floor(Date.now() / 1000);
  const header  = { alg: 'RS256', typ: 'JWT' };
  const payload = {
    iss: saKey.client_email,
    scope: 'https://www.googleapis.com/auth/spreadsheets',
    aud: 'https://oauth2.googleapis.com/token',
    exp: now + 3600, iat: now,
  };
  const enc = (obj) => Buffer.from(JSON.stringify(obj)).toString('base64url');
  const signingInput = `${enc(header)}.${enc(payload)}`;
  const { createSign } = await import('node:crypto');
  const sign = createSign('SHA256');
  sign.update(signingInput);
  const sig = sign.sign(saKey.private_key, 'base64url');
  const jwt = `${signingInput}.${sig}`;
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${jwt}`,
  });
  const data = await res.json();
  if (!data.access_token) throw new Error(`Auth failed: ${JSON.stringify(data)}`);
  return data.access_token;
}

async function getExistingSheetURLs(token) {
  const res = await fetch(
    `https://sheets.googleapis.com/v4/spreadsheets/${GOOGLE_SHEET_ID}/values/Content%20Ideas!U:U`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  if (!res.ok) throw new Error(`Sheet read failed: ${await res.text()}`);
  const data = await res.json();
  const urls = new Set();
  for (const row of (data.values || []).slice(1)) {
    if (row[0]) urls.add(row[0].trim());
  }
  return urls;
}

async function getWordPressPosts() {
  const credentials = Buffer.from(`${WP_USERNAME}:${WP_APP_PASSWORD}`).toString('base64');
  const posts = [];
  let page = 1;

  while (true) {
    const res = await fetch(
      `${WP_URL}/wp-json/wp/v2/posts?status=publish&per_page=100&page=${page}&_fields=id,title,link,date,excerpt,categories`,
      { headers: { Authorization: `Basic ${credentials}` } }
    );
    if (!res.ok) break;
    const batch = await res.json();
    if (!Array.isArray(batch) || batch.length === 0) break;
    posts.push(...batch);
    if (batch.length < 100) break;
    page++;
  }

  return posts;
}

async function appendRows(token, rows) {
  const res = await fetch(
    `https://sheets.googleapis.com/v4/spreadsheets/${GOOGLE_SHEET_ID}/values/Content%20Ideas!A:V:append?valueInputOption=USER_ENTERED`,
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ values: rows }),
    }
  );
  if (!res.ok) throw new Error(`Sheet append failed: ${await res.text()}`);
}

(async () => {
  try {
    const saKey = JSON.parse(Buffer.from(GOOGLE_SA_KEY, 'base64').toString('utf8'));
    const token = await getGoogleToken(saKey);

    console.log('Reading existing sheet URLs...');
    const existingURLs = await getExistingSheetURLs(token);
    console.log(`Found ${existingURLs.size} existing URLs in sheet.`);

    console.log('Fetching published posts from WordPress...');
    const posts = await getWordPressPosts();
    console.log(`Found ${posts.length} published posts in WordPress.`);

    const newPosts = posts.filter(p => !existingURLs.has(p.link));
    console.log(`${newPosts.length} posts not yet in sheet — adding them...`);

    if (newPosts.length === 0) {
      console.log('All posts are already in the sheet. Nothing to do.');
      process.exit(0);
    }

    const rows = newPosts.map(post => {
      const title = post.title?.rendered
        ? post.title.rendered.replace(/<[^>]+>/g, '') // strip HTML tags
        : 'Untitled';
      const date = new Date(post.date).toLocaleDateString('en-US', { timeZone: 'America/New_York' });

      return [
        date,            // A: Date Added
        'WordPress',     // B: Added By
        'WordPress',     // C: Source
        post.link,       // D: Source Link
        title,           // E: Raw Idea
        title,           // F: Topic Direction (same as title for existing posts)
        '',              // G: Cross-Signal?
        '',              // H: Focus Keyword (GSC will show what's working)
        '',              // I: Secondary Keyword
        '',              // J: Hook: Professional
        '',              // K: Hook: Emotional
        '',              // L: Hook: GenZ
        '',              // M: Master Hook
        '',              // N: Reader Payoff
        '',              // O: Ideal For
        '',              // P: Target Audience
        '',              // Q: Image Direction
        '',              // R: WP Category ID
        '',              // S: Social One-Liner
        '📤 Published',  // T: Status
        post.link,       // U: Blog URL
        '',              // V: Notes
      ];
    });

    await appendRows(token, rows);
    console.log(`✓ Added ${rows.length} existing posts to the sheet.`);
    console.log('Now run the GSC Performance Sync workflow to pull their search data.');

  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
})();
