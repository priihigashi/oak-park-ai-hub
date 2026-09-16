---
name: feed-consistency-check
description: Scan the last 5 published posts for a content niche before creating any new carousel or thumbnail. Catches brand drift, overused hooks, visual inconsistencies, repeated hashtags, and posting gaps. Use BEFORE any opc-carousel-creator or news carousel build.
---

# Feed Consistency Check

**Trigger:** Before building any carousel, thumbnail, or post — or when Priscila asks "does this fit the feed?" / "check the feed first."

## Purpose
Prevent brand drift and repetition by comparing the pending post against recent output before any production work starts.

## When to run
- Any time `opc-carousel-creator` or a news/Brazil carousel is about to begin
- When a hook, angle, or format feels repeated
- When a new niche or visual style is being introduced

## Steps

### 1. Identify the niche and handle
Determine which feed this post targets:
- OPC — Oak Park Construction Instagram
- Brazil / News — Brazil news feed
- UGC — UGC / Amazon content feed
- Other (ask Priscila if unclear)

### 2. Locate the last 5 published posts
Search Drive in the relevant folder:
- OPC: Marketing SHARED drive → Content → Carousel (or Proof Posts)
- Brazil/News: Shared drives → News → Brazil → Published (or the Content Queue sheet)
- Use the Content Queue sheet (ID: `1C1CAZ8lSgeVLSSCYIg-D9XPJcSLHyIOh1okKtvhZZQg`) if Drive folders are unclear — filter by Niche + Status = Published, sort by Date DESC, take top 5

### 3. Check the 5-post window for each flag

**Hook repetition**
- Read the first-slide hook text for each of the 5 posts
- If the pending hook uses the same opening word/phrase as 2+ recent posts → flag it and suggest a replacement angle

**Visual format repetition**
- Note which template was used (opc_progress / opc_tip / news-fact-check / etc.)
- If the same template appeared 3+ times in 5 posts → flag it and note which template has been underused

**Color / aesthetic drift**
- If OPC: confirm the last posts used the approved palette (cream, dark, lime-on-dark) — not a custom improvised color
- If News/Brazil: confirm slide backgrounds follow the approved news template, not freestyle colors

**Topic overlap**
- Does the pending topic repeat a topic already covered in the last 5 posts?
- Even if the angle differs, flag close topic overlap so Priscila can decide

**Hashtag staleness**
- Pull the hashtag block from the last 3 captions
- Flag any hashtag that appears in all 3 (overused — rotate it out)

**Posting gap**
- Check the dates on the last 5 posts
- If the most recent post is more than 7 days old → note the gap in the report so Priscila knows context

### 4. Report format

Output a short plain-text report — NO markdown tables:

```
Feed Consistency Check — [Niche] — [Date]

Last 5 posts reviewed: [date range]

Hook: [PASS / FLAG — reason + suggested replacement]
Visual format: [PASS / FLAG — which template is overdue]
Color/aesthetic: [PASS / FLAG]
Topic overlap: [PASS / FLAG — which recent post covers similar ground]
Hashtags: [PASS / FLAG — list overused tags]
Posting gap: [PASS / X days since last post]

Recommendation: [one sentence — proceed / swap hook / change template / other]
```

### 5. Hand off to production
After check passes (or Priscila confirms she wants to proceed despite a flag), hand control to `opc-carousel-creator` or the relevant carousel workflow.

## Done check
- All 6 flags evaluated
- Report delivered before any design or copy work begins
- No design decisions made in this skill — report only
