# Anthropic Credit Consumer Registry
Generated: 2026-08-01 by Daily Advancer (EMAIL_OPS Phase 0)

Source of truth for all workflows in oak-park-ai-hub that call the Anthropic API
(via CLAUDE_KEY_4_CONTENT secret). Update this file whenever a new workflow is added
or a schedule changes.

---

## SCHEDULED CONSUMERS (auto-fire without human trigger)

### 1. 4am_agent.yml
- Schedule: Every other day at 08:00 UTC (4 AM ET)
- Script: scripts/4am_agent/main.py
- Anthropic key used: CLAUDE_KEY_4_CONTENT
- Also uses: OpenAI, Gemini, Replicate
- What it does: runs the main 4AM content agent (topic selection, brief writing, pattern learning)
- WP-0 note (2026-07-23): content_creator retry is NOW MANUAL ONLY — no longer auto-dispatched

### 2. research.yml
- Schedule: Every other day at 11:15 AM ET (15:15 UTC — alternates with 4am_agent)
- Script: scripts/research.js (via @anthropic-ai/sdk)
- Anthropic key used: CLAUDE_KEY_4_CONTENT
- Also uses: OpenAI, YouTube API, NewsAPI, SerpAPI
- What it does: content research feed for blog + social (writes to Inspiration Library)

### 3. capture_pipeline.yml (via scheduled_capture_poll.yml)
- Dispatch trigger: scheduled_capture_poll runs at 12:00 UTC + 17:00 UTC daily (8 AM + 1 PM ET)
- Script: scripts/capture/capture_pipeline.py
- Anthropic key used: CLAUDE_KEY_4_CONTENT
- Also uses: OpenAI (Whisper), Gemini
- What it does: downloads reel/article, transcribes, classifies niche, writes brief to Inspiration Library
- Max daily dispatches: 4 (2 poll runs x 2 max_dispatch each)
- HISTORY: Before WP-0 fix (2026-07-23) there were 4 duplicate DST-variant crons = 8 dispatches/day

---

## MANUAL / ON-DEMAND CONSUMERS (human must trigger)

### 4. content_creator.yml
- Schedule: PAUSED since 2026-06-26 (Priscila decision — no autonomous creation until rebuilt)
- Script: scripts/content_creator/main.py + scripts/content/content_auditor.py
- Anthropic key used: CLAUDE_KEY_4_CONTENT
- Also uses: OpenAI, Gemini
- What it does: full carousel pipeline (topic pick → slides → review → preview email)
- Token usage: HEAVY — runs main.py + carousel_reviewer + 3-agent content_auditor + retry job if fail
- Status: safe while paused; do NOT re-enable cron without budget cap in place

### 5. capture_pipeline.yml (manual triggers)
- Triggered by: capture_dispatcher.yml (GitHub issue /capture comment) or GitHub Actions UI
- Same script and Anthropic usage as the scheduled version above
- No daily cap on manual triggers — unlimited

---

## NOT USING ANTHROPIC (confirmed clean)

- scheduled_capture_poll.yml: Sheets API + GitHub only — no Anthropic
- capture_dispatcher.yml: command relay only — no Anthropic
- archive_inspiration.yml: Sheets API + Gmail only — no Anthropic
- send_email.yml: SMTP only — no Anthropic
- all ads_*.yml workflows: Google Ads API / Sheets only — no Anthropic

---

## PHASE 0 RECOMMENDATIONS

1. TOP UP CREDITS + AUTO-RELOAD: Go to console.anthropic.com/settings/billing
   Enable auto-reload so pipelines never hard-stop mid-run. (Only-Priscila — 2 min)

2. ADD PER-RUN TOKEN CAP to capture_pipeline.py:
   Pass max_tokens=4096 (or similar) on each Claude call so a runaway loop
   can't drain hundreds of dollars in one run.

3. VERIFY 4am_agent + research.yml don't stack on same days:
   4am_agent: cron "0 8 */2 * *" fires on days 1,3,5,7...
   research.yml: cron "15 11 */2 * *" fires on days 1,3,5,7...
   Both fire on ODD days — they share days but run hours apart (4 AM + 11 AM ET).
   This is fine for spend but means BOTH fire on some days, not strictly alternating.

4. RESTORE COMPOSIO GOOGLEDOCS CONNECTION:
   Composio googledocs has zero accounts — Daily Advancer cannot write to the
   Productivity doc until this is reconnected. Go to composio.dev and authorize
   with priscila@oakpark-construction.com.

---

## CHANGE LOG

| Date | Change | Author |
|------|--------|--------|
| 2026-08-01 | Initial registry created | Daily Advancer |
| 2026-07-23 | WP-0: reduced capture crons 4→2, gated content_creator retry | Email-Ops Phase 0 |
| 2026-06-26 | content_creator.yml cron paused | Priscila |
| 2026-05-07 | 4am_agent + research cut from daily to every-other-day | Cost cut |
