# Research Agent — YouTube & Website Research

When invoked, immediately execute. No preamble.

---

## PRIMARY FLOW — YouTube Video Research (default when given a topic)

`/research [topic]` → Find 15 YouTube videos, transcribe all, create report, save to Drive Resources folder.

### The 3-Round Flow:
**Round 1:** Search 5 videos on initial topic → transcribe → Claude analyzes each (relevance score 1-10)
**Round 2:** Claude generates 5 new keywords from Round 1 findings → search 5 more videos → transcribe + analyze
**Round 3:** Claude generates 5 more keywords from cumulative findings → search 5 more → transcribe + analyze
**Result:** 15 total transcribed videos → master report → saved to Drive Resources/Video Creation Flow folder + Inspiration Library tab

### How to trigger:
**Via GitHub Action (preferred — runs in cloud):**
```
~/bin/gh workflow run video-research.yml \
  --repo priihigashi/oak-park-ai-hub \
  --field topic="gmail claude automation" \
  --field queries="gmail automation with claude AI 2025,claude AI email management" \
  --field max_per_query=5
```

**Script lives only in the repo** (not mirrored locally). For a local run, clone first:
```
cd /tmp && gh repo clone priihigashi/oak-park-ai-hub -- --depth=1
python3 /tmp/oak-park-ai-hub/scripts/youtube_research.py --topic "..." --queries "..." --max 5
```
Preferred route is the GitHub Action above — it already has all secrets.

### Script location:
- GitHub: `scripts/youtube_research.py` in priihigashi/oak-park-ai-hub
- Workflow: `.github/workflows/video-research.yml`
- Secrets needed: PRI_OP_ANTHROPIC_API_KEY, PRI_OP_GOOGLE_SA_KEY, PRI_OP_DRIVE_OAUTH_TOKEN

### Report output:
- Drive: Resources/Video Creation Flow folder (ID: 1-QRf4xToJf_7cnS5UW7BiDUjd6lXot6o)
- Filename: `research_[topic]_[timestamp].txt`
- Sheet: Ideas & Inbox (1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU) → 📥 Inspiration Library tab
- Report sections: BEST IDEAS TO IMPLEMENT NOW (score 7+) → ALL VIDEOS ANALYZED

### After research:
- Show top 3 implementable ideas (score 7+) directly in chat
- Confirm report saved to Drive with folder link
- Ask: "Want me to run /brand-archetype-consultant on this?"

---

## WEBSITE / DESIGN RESEARCH

`/research [URL1] [URL2]` → Analyzes those sites.

**When she drops URLs:**
1. WebFetch each URL
2. Extract: hero design, sections, color palette, fonts, animations, CTAs, mobile notes
3. Save findings to Google Sheet (Main: 1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU → Website Research tab)
4. Summarize top 3 patterns to steal

**Find examples:**
`/research find luxury construction websites` → WebSearch → return 3-5 results with: site name, URL, what's notable, why it fits her vision → ask which to dig deeper on

**Platform research:**
`/research Sanity CMS vs Contentful` → compare features, pricing, Brazil support, ease of use

**GitHub Action research (batch URLs):**
`/research run github action [opc_urls] [brazil_urls]`
```
~/bin/gh workflow run website-research.yml \
  --repo priihigashi/oak-park-ai-hub \
  --field opc_urls="URL1" \
  --field brazil_urls="URL1"
```

---

## KEY CONTEXT
OPC style: Modern, sleek, luxurious, blueprint animations. Colors: #000000, #CBCC10, #e0ede7
Brazil RE style: Luxury real estate, PT-BR, cinematic, scroll-triggered video, Cormorant serif
Master Plan Doc: 1uxHmQtYfqel6X9MgFoXF-L_Y3rBhlenhG9sZo9ifuGU
Resources Drive folder: 1-QRf4xToJf_7cnS5UW7BiDUjd6lXot6o (Resources/Video Creation Flow)

---

## DECISION TREE
- Got a URL → website/design research flow
- Got a topic (no URL) → YouTube 3-round research flow
- Got "find [examples]" → WebSearch examples flow
- Got "run github action" → trigger workflow

## AFTER ANY RESEARCH
Save findings → update master plan doc if relevant → ask "want me to run /brand-archetype-consultant on this?"
