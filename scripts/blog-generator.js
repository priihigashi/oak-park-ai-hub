const Anthropic = require('@anthropic-ai/sdk');
const fs = require('fs');
const { COMPANY } = require('./company-info.js');
const { selectApprovedBlogRow, buildWordPressDraftBody } = require('./blog-editorial-gate.js');

// ─── Configuration ────────────────────────────────────────────────────────────
const WP_URL          = process.env.WP_URL;
const WP_USERNAME     = process.env.WP_USERNAME;
const WP_APP_PASSWORD = process.env.WP_APP_PASSWORD;
const PEXELS_API_KEY  = process.env.PEXELS_API_KEY || '';
const MANUAL_TOPIC    = process.env.MANUAL_TOPIC || '';
const GOOGLE_SHEET_ID = process.env.GOOGLE_SHEET_ID;
const GOOGLE_SA_KEY   = process.env.GOOGLE_SA_KEY;
const ANTHROPIC_KEY   = (process.env.CLAUDE_KEY_4_CONTENT || process.env.ANTHROPIC_API_KEY || '').trim();
const OPENAI_API_KEY  = (process.env.OPENAI_API_KEY || '').trim();
const client = ANTHROPIC_KEY ? new Anthropic({ apiKey: ANTHROPIC_KEY }) : null;

async function callLlmText({ system, content, maxTokens = 4000, claudeModel = 'claude-sonnet-4-6', openaiModel = 'gpt-4o' }) {
  if (client) {
    try {
      const response = await client.messages.create({
        model: claudeModel,
        max_tokens: maxTokens,
        system,
        messages: [{ role: 'user', content }],
      });
      return response.content[0].text.trim();
    } catch (err) {
      console.log(`Claude failed (${err.message}); trying OpenAI fallback...`);
    }
  } else {
    console.log('Claude key missing; using OpenAI fallback...');
  }

  if (!OPENAI_API_KEY) throw new Error('No LLM provider available: set CLAUDE_KEY_4_CONTENT or OPENAI_API_KEY');
  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: openaiModel,
      max_tokens: maxTokens,
      temperature: 0.2,
      messages: [
        { role: 'system', content: system },
        { role: 'user', content },
      ],
    }),
  });
  if (!res.ok) throw new Error(`OpenAI fallback failed: ${await res.text()}`);
  const data = await res.json();
  return (data.choices?.[0]?.message?.content || '').trim();
}

// Column indexes (0-based) matching the 23-column sheet
const COL = {
  dateAdded: 0, addedBy: 1, source: 2, sourceLink: 3, rawIdea: 4,
  topicDirection: 5, crossSignal: 6, focusKeyword: 7, secondaryKeyword: 8,
  hookProfessional: 9, hookEmotional: 10, hookGenZ: 11, masterHook: 12,
  readerPayoff: 13, idealFor: 14, targetAudience: 15, imageDirection: 16,
  wpCategoryId: 17, socialOneLiner: 18, status: 19, blogUrl: 20, notes: 21,
  datePublished: 22,
};

// ─── Google Sheet helpers ─────────────────────────────────────────────────────
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
  if (!data.access_token) throw new Error(`Google auth failed: ${JSON.stringify(data)}`);
  return data.access_token;
}

// ─── Read sheet and return a human-approved brief only ──────────────────────
async function getApprovedTopicFromSheet() {
  if (!GOOGLE_SHEET_ID || !GOOGLE_SA_KEY) return null;
  try {
    const saKey = JSON.parse(Buffer.from(GOOGLE_SA_KEY, 'base64').toString('utf8'));
    const token = await getGoogleToken(saKey);

    const res = await fetch(
      `https://sheets.googleapis.com/v4/spreadsheets/${GOOGLE_SHEET_ID}/values/Content%20Ideas!A:V`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (!res.ok) { console.log('Could not read approved briefs in the sheet.'); return null; }
    const data = await res.json();
    const rows = (data.values || []).slice(1); // skip header

    const selected = selectApprovedBlogRow(rows, COL);
    if (selected) {
      console.log(`Approved brief selected (row ${selected.rowIndex + 2}): "${selected.row[COL.topicDirection] || selected.row[COL.rawIdea]}"`);
      return buildSheetData(selected.row, selected.rowIndex, token, '✅ Approved');
    }

    console.log('No human-approved blog brief found.');
    return null;
  } catch (e) {
    console.log(`Sheet read failed: ${e.message}`);
    return null;
  }
}

function buildSheetData(row, i, token, originalStatus) {
  return {
    rowIndex: i,
    sheetRow: i + 2,
    token,
    originalStatus,
    // Pass every researched column so Claude has full context
    source:           row[COL.source]           || '',
    sourceLink:       row[COL.sourceLink]       || '',
    rawIdea:          row[COL.rawIdea]          || '',
    topicDirection:   row[COL.topicDirection]   || row[COL.rawIdea] || '',
    focusKeyword:     row[COL.focusKeyword]     || '',
    secondaryKeyword: row[COL.secondaryKeyword] || '',
    hookProfessional: row[COL.hookProfessional] || '',
    hookEmotional:    row[COL.hookEmotional]    || '',
    hookGenZ:         row[COL.hookGenZ]         || '',
    masterHook:       row[COL.masterHook]       || '',
    readerPayoff:     row[COL.readerPayoff]     || '',
    idealFor:         row[COL.idealFor]         || 'Both',
    targetAudience:   row[COL.targetAudience]   || 'Homeowner',
    imageDirection:   row[COL.imageDirection]   || '',
    wpCategoryId:     row[COL.wpCategoryId]     || '',
    socialOneLiner:   row[COL.socialOneLiner]   || '',
  };
}

// After posting, update the sheet row status and Blog URL
async function markSheetRowPosted(sheetData, blogUrl) {
  const newStatus = '✍️ Draft Created';
  try {
    const { token, sheetRow } = sheetData;
    const colLetter = (i) => {
      let r = '', n = i + 1;
      while (n > 0) { r = String.fromCharCode(64 + (n % 26 || 26)) + r; n = Math.floor((n - 1) / 26); }
      return r;
    };
    const updates = [
      { range: `Content Ideas!${colLetter(COL.status)}${sheetRow}`,        values: [[newStatus]] },
      { range: `Content Ideas!${colLetter(COL.blogUrl)}${sheetRow}`,       values: [[blogUrl]] },
    ];
    const res = await fetch(
      `https://sheets.googleapis.com/v4/spreadsheets/${GOOGLE_SHEET_ID}/values:batchUpdate`,
      {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ valueInputOption: 'USER_ENTERED', data: updates }),
      }
    );
    if (res.ok) console.log(`Sheet row ${sheetRow} updated → ${newStatus}`);
    else console.log(`Sheet update failed: ${await res.text()}`);
  } catch (e) {
    console.log(`Could not update sheet: ${e.message}`);
  }
}

// ─── Step 2: Generate blog post with Claude ───────────────────────────────────
async function generatePost(topic, sheetData = null) {
  console.log('Calling LLM API...');

  // If we have pre-researched sheet data, give Claude the full context
  const keywordInstructions = sheetData && sheetData.focusKeyword
    ? `PRE-RESEARCHED CONTENT BRIEF (use this — don't ignore it):
- Original source: ${sheetData.source || 'research'} ${sheetData.sourceLink ? `(${sheetData.sourceLink})` : ''}
- Raw idea: "${sheetData.rawIdea}"
- Topic direction: "${sheetData.topicDirection}"
- Focus keyword: "${sheetData.focusKeyword}" ← use only where it reads naturally
- Secondary keyword: "${sheetData.secondaryKeyword || ''}"
- Target audience: ${sheetData.targetAudience || 'Homeowner'}
- Reader payoff: "${sheetData.readerPayoff || ''}" ← this is what the reader walks away knowing — make sure the post delivers it
- Ideal format: ${sheetData.idealFor || 'Both'}
- Featured image concept: "${sheetData.imageDirection || ''}"

TITLE — choose the strongest option from these pre-written hooks, or combine them:
  Hook A (professional): "${sheetData.hookProfessional || ''}"
  Hook B (emotional):    "${sheetData.hookEmotional || ''}"
  Hook C (Gen Z/casual): "${sheetData.hookGenZ || ''}"
  Master hook:           "${sheetData.masterHook || ''}"

Adapt the best hook into a precise, useful title that describes the actual answer. Do not force a keyword or a power word.`
    : `Choose a clear homeowner question and a precise title. Use search terms naturally; do not write for a keyword quota.`;

  const system = `You are the content writer for ${COMPANY.name}, a Florida construction company based in ${COMPANY.location.headquarters}, serving ${COMPANY.location.primaryMarket} and surrounding areas.

COMPANY:
${COMPANY.origin}
Team: ${COMPANY.team.contractor} (contractor) and ${COMPANY.team.projectManager} (PM) — brothers.
Services: ${COMPANY.services.core.join(', ')}.

VOICE: Practical, direct, calm, contractor-led, homeowner-friendly. Expert without being technical. Persuasive without hype.
Good: "Here's what affects cost." / "Here's what to verify before hiring." / "Here's why this matters in Broward."
Bad: hype, vague dream-project language, robotic SEO phrasing, "we go above and beyond."

EDITORIAL STANDARD — every post must do all 5:
1. Attract search traffic (title/topic matches a real search query)
2. Educate clearly (plain but expert language)
3. Prove local relevance (South Florida conditions must actually CHANGE the advice — not just be mentioned)
4. Build trust in Oak Park (sounds like a contractor who knows the work, not a generic writer)
5. Convert the right reader (CTA matches the exact article topic)

REQUIRED ARTICLE STRUCTURE (adapt freely — this is a guide, not a template):
- Intro: Name the reader's exact problem → tie it to South Florida immediately → explain the consequence of misunderstanding it → promise what the article will clarify
- Section 1: Define the term or frame the decision in plain language
- Section 2: Break down the main drivers (cost, structure, timeline, code, materials)
- Section 3: South Florida-specific realities — hurricanes, flood zones, concrete block expectations, water table, insurance impact, permitting, coastal exposure (pick what's relevant)
- Section 4: Decision guidance — when it makes sense, when it doesn't, what to ask a contractor, what mistakes to avoid
- Section 5 (optional): What owners often miss or underestimate
- Closing: ONE topic-specific CTA that finishes: "If you're trying to figure out [exact article problem], the next step is…"

USEFUL DETAIL — include only details supported by the approved brief or a named source. These never replace citations:
- A real-world scenario or common mistake homeowners make
- A permit, inspection, or code note specific to South Florida
- A contractor-selection tip (what to verify, what to ask)
- A scope distinction (what's included vs. what gets added later)
- A cost driver that reflects real local tradeoffs
- A market-specific warning ("In Broward, flood zone requirements mean…")
Examples of good authority signals:
"This is where homeowners usually underestimate the cost."
"This is one of the first things to confirm before signing a contract."
"The total shifts fast when you add a bathroom, second story, or panel upgrade."
"This matters more in South Florida because…"

PRICING LANGUAGE RULE — critical:
Do not invent dollar amounts, ranges, percentages, project results, or timelines. Explain the decisions that change a quote. If an approved brief supplies a current local figure, preserve its source, scope, date, and uncertainty; otherwise omit the number.

HEADING RULES:
- WordPress adds the post title as H1 automatically — do NOT use any H1 tags in the HTML body
- Start body HTML with H2 for main sections, H3 for subsections
- Headings must be natural and readable — written for humans first
- Good: "What Affects the Cost of a Home Addition in Broward County?" / "What to Ask Before Hiring a Contractor"
- Bad: "Home Addition Cost Broward County Florida Contractor Services Near Me"
- H3 should feel calmer and more functional than H2 — not competing for attention
- Do not make every section feel like a new headline moment — some content should breathe

CTA RULE: The closing CTA must match the article topic exactly. Never use generic "contact us" language alone.
- Shell article → "Bring your plans so the shell scope can be discussed"
- Addition cost → "Discuss the project scope before requesting comparable estimates"
- Comparison → "Talk through which option makes sense for your lot and budget"

FEATURED IMAGE RULE — the image_search_query you return must follow this hierarchy:
The featured image must match the article in: property type, project type, project stage, and reader expectation.
If the article is residential (home addition, remodel, kitchen, patio, etc.):
  GOOD search terms: "home addition exterior renovation", "house framing addition", "residential contractor house plans", "single family home remodel", "homeowner contractor exterior"
  BAD search terms: "construction building", "concrete building", "commercial construction", "high rise", "parking garage", "crane tower"
If someone sees the image alone, they should roughly guess: house, renovation/addition, homeowner project, residential scale.
For commercial articles: office renovation, retail build-out, commercial interior framing — not residential.
Quick approval test: Does the image match the building type? The job type? The project scale? If 2 of 3 are wrong, find a better search term.

FRESHNESS AND ATTRIBUTION RULE — for current-event, enforcement, or policy topics:
Do not write time-sensitive claims as if they are permanent facts.
Use anchored or softened language:
  Good: "as enforcement pressure increases" / "in the current environment" / "in some recent cases" / "depending on how enforcement plays out locally"
  Risky: "contractors across Broward are experiencing this" / "the effects are measurable and ongoing" — only use these if there is clear current basis
When making a market-wide local claim, either attach it to a named source/reporting pattern OR write it as a practical risk rather than a declared county-wide fact.
Current-event posts should be reviewed at 30–60 days — add a note at the end of the article's HTML: <!-- FRESHNESS CHECK: review this post by [month 60 days out] -->

CONTENT RULES:
- LOCATION: South Florida, ${COMPANY.location.primaryMarket}, or specific local cities ONLY. Never imply the company is in Illinois. Illinois is origin story only.
- COMPETITORS: Never name any competitor.
- TRADE REFERRALS: Never tell readers to "hire a roofer/plumber" as standalone advice. Oak Park handles those as part of full projects.
- POLITICAL NEUTRALITY: ${COMPANY.contentRules.politicalNeutrality}`;

  const userPrompt = `Topic: "${topic}"

${keywordInstructions}

ARTICLE REQUIREMENTS:
- Answer the homeowner's actual question. Include practical decisions, tradeoffs, and a next step.
- Be as long as needed to answer well; do not pad to a target word count.
- Use natural headings and a concise, accurate meta description.
- Mention a South Florida city only when the location changes the advice.
- Cite an authoritative primary source beside each consequential code, permit, price, legal, or technical claim. If the approved brief lacks evidence, omit or mark the claim for review.
- Never fabricate an OPC project, customer, quote, statistic, guarantee, or first-hand experience.
- Use only the approved brief's image facts. An image concept is a request for editorial review, not proof that an OPC project exists.
- Mark a mid-article visual only if it helps explain a decision: <!-- INLINE_IMAGE: [specific educational concept] -->. A human must review the asset, caption, alt text, provenance, and rights before publication.

READABILITY:
- Lead with the answer, use concrete language, vary rhythm, and remove filler.
- Favor a scope checklist, comparison, or decision tree when it genuinely helps the reader.
- Do not force sentence length, transition-word, location, or keyword quotas.

FORMAT: HTML only — h2, h3, p, ul, ol, li, a tags. No html/head/body wrappers. NO h1 tags — WordPress outputs the title as h1 automatically.

Return ONLY this exact JSON (no markdown fences, no extra text):
{
  "title": "accurate descriptive title",
  "focus_keyword": "exact focus keyword",
  "meta_description": "concise accurate summary",
  "image_search_query": "3-5 words MAX, plain ASCII only, no punctuation (e.g. 'residential concrete patio slab')",
  "html_content": "<h2>...</h2><p>...</p>"
}`;

  let raw = await callLlmText({
    system,
    content: userPrompt,
    maxTokens: 8000,
    claudeModel: 'claude-opus-4-6',
    openaiModel: 'gpt-4o',
  });
  raw = raw.replace(/^```[a-z]*\n?/i, '').replace(/```$/, '').trim();

  // Extract first JSON object if the model adds prose, then fix literal control
  // chars inside JSON string values (unescaped newlines/tabs from model).
  function fixJsonControlChars(str) {
    const start = str.indexOf('{');
    const end = str.lastIndexOf('}');
    if (start !== -1 && end !== -1 && end > start) {
      str = str.slice(start, end + 1);
    }
    let inStr = false, escaped = false, out = '';
    for (const c of str) {
      if (escaped) { out += c; escaped = false; continue; }
      if (c === '\\') { escaped = true; out += c; continue; }
      if (c === '"') { inStr = !inStr; out += c; continue; }
      if (inStr) {
        if (c === '\n') { out += '\\n'; continue; }
        if (c === '\r') { out += '\\r'; continue; }
        if (c === '\t') { out += '\\t'; continue; }
      }
      out += c;
    }
    return out;
  }

  let post;
  try {
    post = JSON.parse(fixJsonControlChars(raw));
  } catch (err) {
    const preview = raw.slice(0, 600).replace(/\s+/g, ' ');
    throw new Error(`Blog JSON parse failed: ${err.message}. Raw preview: ${preview}`);
  }
  console.log(`Post generated: "${post.title}"`);
  console.log(`Meta description: ${post.meta_description.length} chars`);
  console.log(`Focus keyword: "${post.focus_keyword}"`);

  // ── Safety check ──────────────────────────────────────────────────────────
  const content = (post.title + post.html_content + post.meta_description).toLowerCase();
  const locationFlags = ['oak park il', 'oak park, il', 'illinois', 'chicagoland', 'chicago area'];
  const flagged = locationFlags.filter(f => content.includes(f));
  if (flagged.length > 0) throw new Error(`Safety check failed — wrong location: ${flagged.join(', ')}`);

  return post;
}

// ─── Step 3: Fetch featured image from Pexels ────────────────────────────────
async function fetchFeaturedImage(query) {
  if (!PEXELS_API_KEY) { console.log('No Pexels API key — skipping featured image.'); return null; }
  // Sanitize: replace em/en dash, strip all non-ASCII, collapse spaces, cap at 60 chars
  const safeQuery = query
    .replace(/[\u2013\u2014]/g, '-')
    .replace(/[^\x00-\x7F]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 60);
  console.log(`Searching Pexels for: "${safeQuery}"...`);
  const res = await fetch(
    `https://api.pexels.com/v1/search?query=${encodeURIComponent(safeQuery)}&per_page=1&orientation=landscape`,
    { headers: { Authorization: PEXELS_API_KEY } }
  );
  if (!res.ok) { console.log('Pexels search failed, skipping image.'); return null; }
  const data = await res.json();
  if (!data.photos || data.photos.length === 0) { console.log('No Pexels results, skipping.'); return null; }
  const photo = data.photos[0];
  return { url: photo.src.large, photographer: photo.photographer, alt: safeQuery };
}

// ─── Step 4: Upload image to WordPress ───────────────────────────────────────
async function uploadImageToWordPress(imageInfo, filename = 'featured-image.jpg') {
  if (!imageInfo) return null;
  const credentials = Buffer.from(`${WP_USERNAME}:${WP_APP_PASSWORD}`).toString('base64');
  const imgRes = await fetch(imageInfo.url);
  if (!imgRes.ok) { console.log('Failed to download image.'); return null; }
  const buffer = await imgRes.arrayBuffer();
  const uploadRes = await fetch(`${WP_URL}/wp-json/wp/v2/media`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${credentials}`,
      'Content-Disposition': `attachment; filename="${filename}"`,
      'Content-Type': 'image/jpeg',
      'X-WP-Alt-Text': imageInfo.alt || '',
    },
    body: buffer,
  });
  if (!uploadRes.ok) { console.log('Image upload failed, skipping.'); return null; }
  await assertJsonResponse(uploadRes, `POST /wp-json/wp/v2/media`);
  const media = await uploadRes.json();
  console.log(`Image uploaded: ${filename} → media ID ${media.id}`);
  return { id: media.id, url: media.source_url, alt: imageInfo.alt };
}

// ─── Step 4b: Resolve inline image placeholders ───────────────────────────────
async function resolveInlineImages(html) {
  if (!PEXELS_API_KEY) return html;
  const pattern = /<!-- INLINE_IMAGE: ([^>]+) -->/g;
  const matches = [...html.matchAll(pattern)];
  if (matches.length === 0) return html;
  let result = html;
  for (const match of matches) {
    const query = match[1].trim();
    console.log(`Fetching inline image: "${query}"...`);
    const imgInfo = await fetchFeaturedImage(query);
    if (!imgInfo) { result = result.replace(match[0], ''); continue; }
    const media = await uploadImageToWordPress(imgInfo, `inline-${Date.now()}.jpg`);
    if (!media) { result = result.replace(match[0], ''); continue; }
    result = result.replace(match[0], `<figure class="wp-block-image"><img src="${media.url}" alt="${query}" /></figure>`);
  }
  return result;
}

// ─── WordPress content-type guard ─────────────────────────────────────────────
// Throws a descriptive error when WP returns HTML (wrong URL, redirect, expired
// app password) instead of the cryptic SyntaxError from .json().
async function assertJsonResponse(response, context) {
  const ct = response.headers.get('content-type') || '';
  if (ct.includes('text/html')) {
    const preview = (await response.text()).slice(0, 300).replace(/\s+/g, ' ');
    throw new Error(
      `WordPress returned HTML instead of JSON at ${context}.\n` +
      `  WP_URL="${WP_URL}" | WP_USERNAME="${WP_USERNAME}" | app-password set=${!!WP_APP_PASSWORD}\n` +
      `  Common causes: wrong WP_URL, expired app password, 301 redirect, maintenance mode.\n` +
      `  HTML preview: ${preview}`
    );
  }
}

// ─── WP pre-flight: fail fast before spending LLM credits ────────────────────
// Returns immediately with a clear diagnostic if credentials or URL are wrong.
async function checkWordPressCredentials() {
  if (!WP_URL || !WP_USERNAME || !WP_APP_PASSWORD) {
    throw new Error('Missing WordPress credentials: WP_URL, WP_USERNAME, or WP_APP_PASSWORD not set.');
  }
  const credentials = Buffer.from(`${WP_USERNAME}:${WP_APP_PASSWORD}`).toString('base64');
  const res = await fetch(`${WP_URL}/wp-json/wp/v2/users/me`, {
    headers: { Authorization: `Basic ${credentials}` },
  });
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('text/html')) {
    const preview = (await res.text()).slice(0, 200).replace(/\s+/g, ' ');
    throw new Error(
      `WordPress pre-flight FAILED — returned HTML instead of JSON.\n` +
      `  WP_URL="${WP_URL}" | HTTP status=${res.status}\n` +
      `  Common causes: WP_URL uses http:// (should be https://), expired app password, wrong username.\n` +
      `  Fix: WP Admin → Users → Profile → Application Passwords → revoke old + generate new → update WP_APP_PASSWORD secret.\n` +
      `  HTML preview: ${preview}`
    );
  }
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`WordPress pre-flight FAILED — HTTP ${res.status}: ${body.slice(0, 200)}`);
  }
  const data = await res.json();
  console.log(`WordPress credentials OK — authenticated as "${data.name}" (${data.slug}).`);
}

// ─── Step 5: Post to WordPress as Draft ──────────────────────────────────────
async function postToWordPress(post, featuredMediaId, wpCategoryId) {
  console.log('Saving WordPress draft...');
  const credentials = Buffer.from(`${WP_USERNAME}:${WP_APP_PASSWORD}`).toString('base64');
  const body = buildWordPressDraftBody(post, featuredMediaId, wpCategoryId);
  const response = await fetch(`${WP_URL}/wp-json/wp/v2/posts`, {
    method: 'POST',
    headers: { Authorization: `Basic ${credentials}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`WordPress API error ${response.status}: ${await response.text()}`);
  await assertJsonResponse(response, `POST /wp-json/wp/v2/posts`);
  const result = await response.json();
  console.log(`Draft created! ID: ${result.id}`);
  return {
    id: result.id,
    title: post.title,
    link: result.link,
    editLink: `${WP_URL}/wp-admin/post.php?post=${result.id}&action=edit`,
  };
}

// ─── Main ─────────────────────────────────────────────────────────────────────
(async () => {
  try {
    // 0. Validate WordPress credentials before any LLM work
    await checkWordPressCredentials();

    // 1. Determine topic source: manual → human-approved sheet brief
    let topic, sheetData;

    if (MANUAL_TOPIC.trim()) {
      topic = MANUAL_TOPIC.trim();
      console.log(`Topic: manual — "${topic}"`);
    } else {
      sheetData = await getApprovedTopicFromSheet();
      if (!sheetData) throw new Error('No approved blog brief found. Add a reviewed brief or provide a manual topic; no random fallback.');
      topic = sheetData.topicDirection;
    }

    // 2. Generate post
    const post = await generatePost(topic, sheetData);

    // 3. Images — wrapped in try/catch so a bad image query never kills the post
    let featuredMedia = null;
    try {
      const imageQuery = (sheetData?.imageDirection) || post.image_search_query || topic;
      const imageInfo = await fetchFeaturedImage(imageQuery);
      featuredMedia = await uploadImageToWordPress(imageInfo, 'featured-image.jpg');
      post.html_content = await resolveInlineImages(post.html_content);
    } catch (imgErr) {
      console.log(`Image step failed (${imgErr.message}) — continuing without image.`);
    }

    // 4. This legacy path is draft-only. Publication requires separate editorial approval.
    const result = await postToWordPress(post, featuredMedia?.id || null, sheetData?.wpCategoryId);

    // 5. Update sheet row if topic came from sheet
    if (sheetData) {
      await markSheetRowPosted(sheetData, result.link || result.editLink);
    }

    // 6. Save output for workflow notification
    fs.writeFileSync('scripts/output.json', JSON.stringify(result, null, 2));

    console.log('\n✓ Done! Post saved as draft for review.');
    console.log(`  Title: ${result.title}`);
    console.log(`  Edit:  ${result.editLink}`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
})();
