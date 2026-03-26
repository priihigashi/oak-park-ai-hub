const Anthropic = require('@anthropic-ai/sdk');
const fs = require('fs');
const { getRandomTopic } = require('./topics.js');

const client = new Anthropic();

// ─── Configuration ────────────────────────────────────────────────────────────
const WP_URL = process.env.WP_URL;
const WP_USERNAME = process.env.WP_USERNAME;
const WP_APP_PASSWORD = process.env.WP_APP_PASSWORD;
const PEXELS_API_KEY = process.env.PEXELS_API_KEY || '';
const MANUAL_TOPIC = process.env.MANUAL_TOPIC || '';

// ─── Step 1: Pick a topic ─────────────────────────────────────────────────────
const topic = MANUAL_TOPIC.trim() || getRandomTopic();
console.log(`Topic selected: ${topic}`);

// ─── Step 2: Generate blog post with Claude ───────────────────────────────────
async function generatePost(topic) {
  console.log('Calling Claude API...');

  const message = await client.messages.create({
    model: 'claude-opus-4-6',
    max_tokens: 3000,
    messages: [
      {
        role: 'user',
        content: `You are an expert SEO content writer for Oak Park Construction, a licensed general contractor serving Oak Park, Chicago, and the greater Chicagoland area. They specialize in residential construction, commercial construction, renovation, new additions, shell construction, and concrete construction.

Write a complete, highly SEO-optimized blog post about this topic:
"${topic}"

SEO REQUIREMENTS:
- Primary keyword: naturally use the main topic phrase 4-6 times throughout
- Secondary keywords: weave in terms like "Oak Park contractor", "Chicago construction company", "general contractor Oak Park IL", "home renovation Chicago", "licensed contractor Chicagoland" naturally — never forced
- Title: compelling, includes primary keyword, under 60 characters
- Meta description: exactly 150-160 characters, includes primary keyword and a call to action
- Headers: use H2 for main sections, H3 for subsections — include keywords naturally in at least 2 headers
- First paragraph: include the primary keyword in the first 100 words
- Content length: 1000-1200 words
- Lists: use bullet points or numbered lists for at least one section (helps with Google featured snippets)
- Local SEO: mention Oak Park, Chicago, or Illinois at least 3 times naturally
- Also return a short image_search_query (3-5 words) that describes the ideal featured photo for this post

CONTENT REQUIREMENTS:
- Format: HTML only (h2, h3, p, ul, ol, li tags — NO html/head/body tags)
- Tone: professional, trustworthy, expert — like advice from a knowledgeable contractor
- Structure: intro → 3-4 main sections → conclusion with strong CTA
- End with a call to action to contact Oak Park Construction for a free consultation

Return ONLY this exact JSON (no markdown fences, no extra text):
{
  "title": "SEO title under 60 chars",
  "meta_description": "Exactly 150-160 char description with keyword and CTA",
  "image_search_query": "3-5 word photo search term",
  "html_content": "<h2>...</h2><p>...</p>"
}`
      }
    ]
  });

  let raw = message.content[0].text.trim();
  raw = raw.replace(/^```[a-z]*\n?/i, '').replace(/```$/, '').trim();

  const post = JSON.parse(raw);
  console.log(`Post generated: "${post.title}"`);
  console.log(`Meta description: ${post.meta_description.length} chars`);
  console.log(`Image search query: "${post.image_search_query}"`);
  return post;
}

// ─── Step 3: Fetch featured image from Pexels ────────────────────────────────
async function fetchFeaturedImage(query) {
  if (!PEXELS_API_KEY) {
    console.log('No Pexels API key — skipping featured image.');
    return null;
  }
  console.log(`Searching Pexels for: "${query}"...`);
  const res = await fetch(
    `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=1&orientation=landscape`,
    { headers: { Authorization: PEXELS_API_KEY } }
  );
  if (!res.ok) { console.log('Pexels search failed, skipping image.'); return null; }
  const data = await res.json();
  if (!data.photos || data.photos.length === 0) { console.log('No Pexels results, skipping image.'); return null; }
  const photo = data.photos[0];
  console.log(`Found image: ${photo.src.large}`);
  return { url: photo.src.large, photographer: photo.photographer, alt: query };
}

// ─── Step 4: Upload image to WordPress media library ─────────────────────────
async function uploadImageToWordPress(imageInfo) {
  if (!imageInfo) return null;
  console.log('Downloading and uploading image to WordPress...');
  const credentials = Buffer.from(`${WP_USERNAME}:${WP_APP_PASSWORD}`).toString('base64');

  const imgRes = await fetch(imageInfo.url);
  if (!imgRes.ok) { console.log('Failed to download image.'); return null; }
  const buffer = await imgRes.arrayBuffer();

  const uploadRes = await fetch(`${WP_URL}/wp-json/wp/v2/media`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${credentials}`,
      'Content-Disposition': `attachment; filename="featured-image.jpg"`,
      'Content-Type': 'image/jpeg',
    },
    body: buffer,
  });
  if (!uploadRes.ok) { console.log('Image upload failed, skipping.'); return null; }
  const media = await uploadRes.json();
  console.log(`Image uploaded to WordPress, media ID: ${media.id}`);
  return media.id;
}

// ─── Step 5: Post to WordPress as Draft ──────────────────────────────────────
async function postToWordPress(post, featuredMediaId) {
  console.log('Posting to WordPress...');

  const credentials = Buffer.from(`${WP_USERNAME}:${WP_APP_PASSWORD}`).toString('base64');

  const body = {
    title: post.title,
    content: post.html_content,
    excerpt: post.meta_description,
    status: 'draft',
    categories: [],
    tags: [],
  };
  if (featuredMediaId) body.featured_media = featuredMediaId;

  const response = await fetch(`${WP_URL}/wp-json/wp/v2/posts`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${credentials}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`WordPress API error ${response.status}: ${error}`);
  }

  const result = await response.json();
  console.log(`Draft created! ID: ${result.id}`);

  return {
    id: result.id,
    title: post.title,
    link: result.link,
    editLink: `${WP_URL}/wp-admin/post.php?post=${result.id}&action=edit`
  };
}

// ─── Main ─────────────────────────────────────────────────────────────────────
(async () => {
  try {
    const post = await generatePost(topic);
    const imageInfo = await fetchFeaturedImage(post.image_search_query || topic);
    const featuredMediaId = await uploadImageToWordPress(imageInfo);
    const result = await postToWordPress(post, featuredMediaId);

    fs.writeFileSync('scripts/output.json', JSON.stringify(result, null, 2));

    console.log('\n✓ Done! Draft saved to WordPress.');
    console.log(`  Title: ${result.title}`);
    console.log(`  Edit:  ${result.editLink}`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
})();
