# Focus Partner — STATE (canonical local copy)

**Last updated: 2026-07-14 (rev9)** — bump the date AND increment (revN) by 1 on every push (never reuse a rev); "update" compares by date, then by rev. rev9 = captured the DECIDED AI-receptionist build: **Goodcall** (Starter ~$59/mo) full 7-step setup + paste-ready call script + number-wiring fix + auto-log to her Leads Tracker; added the automations health-check + the Phase 4 Google Ads conversion de-dupe (244-vs-20). rev8 = exit/handoff: pushed & byte-verified rev7, synced the Sheet (Today -> 2026-07-14 + 3 Google Ads/GA4 rows in Pending), pulled local ~/.claude to match GitHub, and wrote the HANDOFF_2026-07-14 doc. rev7 = fixed the false "can't write Sheets" rule (the googlesheets Composio connection as priscila@ is LIVE; the Sheet is read+writable from here) + Focus now keeps the Sheet mirror synced; captured the Google Ads/GA4 conversion-cleanup task from her ads chat. rev6 = added the Boletim Diario briefing as a 4th tab in the morning launcher + shipped Mac (scripts/focus-morning.command) & iPhone (Shortcuts) triggers. rev5 = merged Codex 2026-07-13/14 Sheet + calendar work into GitHub rev4: Library Index, 10:15 finance/stocks popup, Robinhood/Roth/Fidelity specifics, swing-trading/options safety, and manifestation photo-board project. rev4 = bulletproof multi-PC sync: re-pull HEAD before every commit + monotonic rev counter. rev3 = built the Morning command-center launcher (Windows) + weekly manifestation review + de-cluttered repeated Sheet-mirror notes. rev2 = enriched Pending Tasks + capture-specifics rule.

Canonical state lives in this Markdown file on GitHub. (A human-readable Google Sheet mirror also exists — see the **Google Sheet mirror** line just below for its URL/IDs.)

- **Last check:** 2026-07-14 (Tue — exit/handoff: rev7 pushed + byte-verified, Google Sheet synced, local ~/.claude synced, HANDOFF_2026-07-14 doc written). Prev 2026-07-13 (Monday — huge session: `/focus` shortcut + portable install + Codex-ready `FOCUS-PARTNER.md`; Google Ads DONE; ADS-videos vertical redo; Monday patterns; broke ALL backlog into sub-steps; timezone Miami/Eastern; two websites separated; mined Drive/repo → Finance Dashboard/Investments/Ads-tracking/Content-pipeline; TASK-BRAIN rule; ROOM_VISION; **guided Manifestation Module + "update" mechanism**; Library Index created; 10:15 finance/stocks popup added; manifestation photo-board idea captured)
- **Timezone:** America/New_York — **Eastern (Miami), confirmed by Priscila 2026-07-13**
- **Journal folder:** `📓 Daily Journal — DROP HERE` (id `1eknXv30UHtuDVDDRJpyt3eBLqsxhjABB`)
- **Google Sheet mirror:** `_Focus Partner — STATE` (`https://docs.google.com/spreadsheets/d/1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c`) in folder `Focus Partner` (`18API545Cqh0k7V2PPG3hnEeTRJHz7jZO`) under `Productivity & Routine`. Lightweight human-readable mirror only; GitHub Markdown remains canonical.
- **Tool usage:** Priscila will use this Focus Partner in both Codex and Claude. Any assistant must read/update this Markdown state and keep the Sheet mirror current. The Sheet IS writable from here via the `googlesheets` Composio connection (account `googlesheets_allyl-rearm` = priscila@; sheet id `1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c`) — when the Markdown changes, push the same change to the Sheet so it never goes stale.
- **Library / Index:** The Google Sheet now has a `Library Index` tab. Keep it mirrored here: every master plan, dashboard, important Drive folder, website/login portal, stock/finance sheet, handoff, and project tracker that may be needed for planning should be added to both places.

## Library Index — master links for planning
Use this as the map before searching randomly. Add new resources here when they become important.

| Area | Type | Title | Link / ID | Status | Use / why |
|------|------|-------|-----------|--------|-----------|
| Focus system | Sheet | `_Focus Partner — STATE` | https://docs.google.com/spreadsheets/d/1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c | Active mirror | Human scanning: Today, Weekly 3, Pending, Backlog, Manifestation, Source of Truth, Library Index. |
| Focus system | GitHub Markdown | `focus-partner-state.md` | https://github.com/priihigashi/oak-park-ai-hub/blob/main/.claude/focus-partner-state.md | Canonical | Claude/Codex source of truth. Update this so another computer/tool can continue. |
| Focus system | Folder | Focus Partner Drive folder | https://drive.google.com/drive/folders/18API545Cqh0k7V2PPG3hnEeTRJHz7jZO | Active | Shared folder for Focus Partner state/support docs. |
| Focus system | Folder | Daily Journal — DROP HERE | https://drive.google.com/drive/folders/1eknXv30UHtuDVDDRJpyt3eBLqsxhjABB | Active | Drop handwritten 5-line daily log scans/photos here. |
| Finance | Doc | FINANCE_DASHBOARD_MASTER_PLAN | https://docs.google.com/document/d/1OsTy3PQEps-lKP_lS9IDapPOT6Rvv32NWBMezKWP6Mg | Master plan | Defines finance dashboard goals and the money questions it should answer. |
| Finance | Sheet | Finance Dashboard — PRI 2026 | https://docs.google.com/spreadsheets/d/1U7n7OttHExXOmMtusu-3PuI4xBqzGz8LSiISfIMxu64 | Built; inputs needed | Main personal money dashboard. |
| Finance | Sheet | Priscila McFolling's Tiller Spreadsheet | https://docs.google.com/spreadsheets/d/1_MPBggWbWKgnxwhm3kR7gmGjKGkzgsgZuKSjxymUjYc | Source data | Transactions, accounts, balances, subscriptions/spending source. |
| Investing | Doc | Stock_Master_Plan | https://docs.google.com/document/d/1ljE6pOWh4bHsPPcbhEq2-1cm-46BLafmUgAj9oWC5Vs | Master plan | AI stock tracking/watchlist system plan. |
| Investing | Sheet | Copy of Stock_Tracker_PRO_v3_FIXED2 | https://docs.google.com/spreadsheets/d/1BIn7vFU3M2ZvFbEfQtIE5-uHQNo3xUn1yxaovSZdikA | Active tracker candidate | Stock tracker with watchlist/signals/technical indicators. |
| Investing | Sheet | Stock Tracker 2026 | https://docs.google.com/spreadsheets/d/154GxPT8dOLEjEQXwJrL-sU7H5yKaUCcawQUmzrh_XV8 | Reference | Stock watch/research workbook; points to Originals - Stock folder. |
| Investing | Sheet | Google Finance Investment Tracker - Pri | https://docs.google.com/spreadsheets/d/11CJMSbKpleV8lZxcaG_Qcus1zOGv_ZhSahlDZ7qokuc | Reference/watchlist | Google Finance powered investment tracker/watchlist. |
| Investing | Doc | Stock_Research_Report | https://docs.google.com/document/d/1ESsRvyDd2NR4cwi4xA5ZjfwaCRl5cXxyyXIGR5V2Jvc | Research | Resources and stack ideas for AI stock tracking/analysis. |
| Investing | Website | Robinhood | https://robinhood.com | Needs login | Review ~$10k holdings inventory. No buy/sell without inventory and rules. |
| Investing | Website | Fidelity | https://www.fidelity.com | Needs reactivation | Old employer account; identify account type/balance and decide leave/rollover/transfer after tax/retirement review. |
| Oak Park | Sheet | Oak Park — Content Control | https://docs.google.com/spreadsheets/d/1C1CAZ8lSgeVLSSCYIg-D9XPJcSLHyIOh1okKtvhZZQg | Active/reference | Oak Park content control/tracking. |
| Oak Park | Sheet | OPC Website — Build Tracker | https://docs.google.com/spreadsheets/d/1q0_v9qYDXKURo59xoS-WISFdHbZWIdc9ukdCDbdDaUQ | Reference | Oak Park Construction website build tracker. |
| Oak Park | Doc | ROOM_VISION — Build Plan & Handoff | https://docs.google.com/document/d/1NjbadQhzsCA6NmQWq9RheUcEyxQWsGRzWFCeMY9PSvg | Confirm alive/dead | Customer-facing room/space visualization plan for website. |
| Oak Park | Sheet | Drive Map — OPC | https://docs.google.com/spreadsheets/d/1_bl6jNHT8Jl7h8S9uoiGVLOl5fxVkpoImvwfUliE0Pk | Index | OPC Drive map/index. |
| Oak Park / Ads | Folder | MARKETING ADS (shared Drive) | (get link/ID) | Active; she owns, full access | Ad project files incl. Goodcall Setup doc + Leads Tracker. Add Mike explicitly if she asks. |
| Oak Park / Ads | Sheet | Leads Tracker (live) | (get link/ID) | Shared editor; Mike's account owns it | Every Goodcall call auto-logs here: Name · Phone · City/Area · What they need. |
| Oak Park / Ads | Doc | Ads Master Plan (AI-receptionist §5) | (get link/ID) | Reference | Full Goodcall vs Rosie comparison; Goodcall recommended (auto-logs + screens job-seekers). |
| Content | Sheet | Flow Plans Tracker — Master Index | https://docs.google.com/spreadsheets/d/1fggy918FgPfnMQ-dzGQk2zx9uhi2_-uWXMKGW4MA47k | Existing index | Existing master index for flow plans. |
| Content | Sheet | Project tracking - Blog and Social | https://docs.google.com/spreadsheets/d/1CrVHlIe8u1bo_1W0iU0O3WKv2JUrm0-UO76y4p5NC_c | Active/reference | Blog/social content tracking. |
| Content | Sheet | Pipeline Fix Master Checklist — Done Current Next | https://docs.google.com/spreadsheets/d/1yh9C7KU9OlqCdHNDI9mbZ6ldqLA3bAR3uENXUh37bkQ | Reference | Content pipeline fix checklist. |
| Content | Doc | OPC Carousel Pipeline — Audit Remediation Plan 2026-05-12 | https://docs.google.com/document/d/16ngxy_4U-KhyNXqNi7mfWAJbAfh35QDIGjEATQZCWlM | Reference | OPC carousel pipeline remediation plan. |
| Real estate | Doc | HANDOFF_2026-07-01_real-estate-quiz-tallahassee-check | https://docs.google.com/document/d/1g3INH7MQwFgfkSeK0u5cU9K8U8iMOQqhHeq0yEpM5b0 | Reference | RE quiz / Tallahassee check handoff. |
| Manifestation / travel | Website | Walmart Photo | https://photos3.walmart.com/ | Possible print vendor | Print photos for manifestation/travel vision board. |
| Manifestation / travel | Project | Photo collage / vision board | No link yet | Pending | Pick travel/money/family images and put the board where Priscila sees it each morning. |

## This Week (week of 2026-07-13)
- **Focus:** the 3 below. Everything else is PARKED in the Backlog — not this week.
- **Next review due:** morning-review reminder ~10:00
- **Note:** Google Ads rep call = ✅ DONE last week — it is NO LONGER a focus item. That fire is out.

## Planning Frame — Rule of 3 + Matrix (agent leads this WITH her — never a blank template)

### This Week's 3 (week of 2026-07-13)
1. [ ] **Study for the RE exam** — a focused block every day (questions already exist)  (Q2, non-negotiable)
2. [ ] **ADS videos — redo in VERTICAL format** (Oak Park; work + personal). Was on hold, blocked on the missing vertical format — this week is the redo.  (Q2, needle-mover)
3. [ ] **Daily log** — 5 lines by hand each day so the system can track her  (Q2)

### Weekly Matrix (Covey names + his ideal split: ~20% Q1 · 65% Q2 · 10% Q3 · 5% Q4)
- **Q1 — Important + Urgent** = *Necessity* (do now): — (nothing on fire this week — Google Ads call is done. Good place to be.)
- **Q2 — Important + NOT Urgent** = *Effectiveness* ⭐ (PROTECT — live here): RE exam study (daily) · ADS videos vertical redo · Daily 5-line log (daily)
- **Q3 — Urgent + NOT Important** = *Distraction* (minimize/delegate): occasional "ask Mike" items · random interruptions · long Mike calls (cap them)
- **Q4 — NOT important + NOT urgent** = *Waste* (delete): —

### Today's 3 (2026-07-13, Mon) — pulled from Weekly 3, bias Q2
1. [ ] One RE study block
2. [ ] Start the ADS videos vertical redo — just the first cut/setup, not the whole thing
3. [ ] Jot today's 5-line log

### Sub-steps — ADS videos vertical redo (this week's needle-mover)
Each line = something she can finish and check off. She can reorder/edit; the agent keeps this current.
1. [ ] Gather what already exists — find the current ad videos + raw clips (one folder)
2. [ ] Lock the spec — vertical 9:16, length, captions on/off (agent proposes, she picks)
3. [ ] Redo ONE video first (the pilot) — reframe/re-edit to vertical
4. [ ] Look at the pilot → approve the format before doing the rest
5. [ ] Batch-redo the remaining videos in the approved format
6. [ ] Upload / hand off to the ad campaign
*Today only = steps 1–2. The rest are parked so they don't crowd her.*

### Schedule notes
- Mon 2026-07-13: new week. Google meeting already happened last week — don't re-plan it. **Monday = her highest-risk day for plan-paralysis — keep planning tiny, force a fast start (see Patterns).**

### Review log (did the 3 land? where did her time actually go?)
| Week | Weekly 3 done | Time went to (Q2 vs Q1/Q3) | Pattern (one line) |
|------|---------------|----------------------------|--------------------|
| 2026-07-06 | Google Ads call ✅ DONE (the Q1 fire) · RE study + daily log = partial | Q1 fire (the call) got handled; Q2 dailies inconsistent | The urgent thing got done — protect the Q2 dailies now that the fire's out |

## Daily Manifestation (log) — she writes this in the chat EVERY morning before her day
Morning ritual (her request 2026-07-13): run the **Manifestation Module** (see agent brain) — 4 guided steps, ≤10 min, BEFORE the report or Today's 3. She writes Step 3 ("I am / I have" + gratitude) in the chat. Log it verbatim, newest at top.
| Date | Her manifestation (Step 3, verbatim) |
|------|------------------------------|
| 2026-07-13 | i am very smart, i have a great family husband and kids, i feel i am walking towards the right direction, im grateful i saw a video that helped me add manifestation to my flow, im feeling confident it will work. |
| — | (starts tomorrow morning) |

### Weekly manifestation review (Sun/Mon — added 2026-07-14)
Each week the agent skims the entries above: what recurred, what is landing vs still just words, which fear/scarcity theme showed up. Reflect ONE pattern to her and fold it into the week's plan (and Patterns if persistent).
| Week | Themes / what recurred | Landing? | One pattern -> into the plan |
|------|------------------------|----------|-----------------------------|
| — | (first review this coming Sun/Mon) | — | — |

## Backlog — MASTER LIST (everything she wants to do; the POOL the matrix pulls from)
Captured 2026-07-07 from her brain-dump. Nothing here is scheduled yet — it's the full pile so nothing lives only in her head. Weekly 3 gets pulled FROM this. Every item is broken into sub-steps below (see Task Breakdowns).

**🎓 Real estate (exam)**
- Study for the FL RE exam — daily *(hers)*. Quiz-app *building* = Claude's, runs in her RE-study chat.

**🏗️ Oak Park Construction (business)**
- ~~Google Ads rep call — book + do~~ ✅ **DONE** (had the meeting, ~week of 2026-07-06). No longer pending.
- **ADS videos — redo in VERTICAL format** (work + personal — keep in focus, never lose it). Currently on HOLD only because it's missing the vertical format; the plan is to redo everything in vertical. *(promoted to This Week's 3, week of 2026-07-13; broken into 6 sub-steps.)*
- **AI receptionist — DECIDED: Goodcall** (Starter ~$59/mo) to stop missed calls (~$1,400/qtr leak). Recommended in the Ads Master Plan §5 (auto-logs every call to her Leads Tracker + screens job-seekers). Full 7-step setup + paste-ready script + number-wiring fix are in Task Breakdowns below. *(from her marketing/ads chat, 2026-07-14.)*
- Phone-number approach — decide.
- Verify the daily lead-follow-up email actually landed — confirm the "Lead follow-up routine is LIVE" test email hit her inbox.
- Oak Park Construction **BUSINESS website** (opc-website-v1, live) — revisit / improve. *(NOT her mom's site — different project; her mom's is under Personal.)*
- Oak Park Construction **app** — exists; husband didn't adopt it; revisit later.
- **Content / posting FOR construction** (social).
- **Ads tracking / dashboard** — some days logged ZERO leads (e.g. June 1 & 8): tracking broke, or ads paused? Diagnose. *(separate from the ADS videos creative above.)*
- **Automations health-check** — a week on, confirm the dashboard actually refreshed AND the daily follow-up routine has been running clean. *(Focus can do this without her; from ads chat 2026-07-14.)*
- **Phase 4 — Google Ads conversion de-dupe (244-vs-20)** — clean up the messy/duplicate conversion actions so reporting is trustworthy. *(relates to the GA4 cleanup below; from ads chat 2026-07-14.)*
- **Google Ads / GA4 conversion cleanup** — fix the bidding signal so ad money steers to REAL leads (calls + form submits), then remove a duplicate GA4 property + a stray GTM tag. *(from her ads chat, 2026-07-14; broken into 3 steps below.)*
- **ROOM_VISION** — a customer-facing tool for the website (her guess: lets website customers **visualize a room/space/design**). Build plan exists in her Drive. CONFIRM exact scope + whether it's still alive.

**🏠 McFolling Properties / Airbnb**
- **Guest-message monitor + escalation:** reads Airbnb/email guest messages → **phone-calls her** to say "someone's messaging you", tries to help/answer guests, and flags REAL emergencies (guest locked out, etc.) to reach her. (the "Maya" area.)

**💰 Finance & investing** *(detail pulled from her FINANCE_DASHBOARD_MASTER_PLAN + Investments plan, 2026-07-13)*
- **Finance Dashboard — PRI 2026** (her personal money command center; already BUILT — "structure/design complete") — answers her 9 money questions: net position · month spend vs normal · where money went · money-in/receivables · debt by card · what's due · payoff plan · net positive? · next decision. Source = **Tiller**. Cards: Discover, Chase, BoA, Citi, Affirm (~$16k known debt). **Blocked on HER inputs** → per-card facts (APR/limit/minimum/due/statement date), Cash balance, Investments value, personal receivables, and the **Owner/Michael (Mike) classification rule**. *(Claude = read/UX only; Codex edits the sheet.)*
- Clean the **subscriptions/expenses spreadsheet** → total spend, what to cut. *(part of the finance picture; later an app.)* Priscila said 2026-07-13 her body says "yes" to getting finances in check: she needs daily visibility into subscriptions, what she is spending, what is unnecessary, and what changed.
- **Investments / stocks reset** — Robinhood + Fidelity 401k + crypto + Brazil/US allocation. Her words: *"5 years, no growth."* START with a one-page **inventory** (what she holds, where) before ANY reset — inventory first, not a reset plan.
  - 2026-07-13 update from Priscila: about **$10,000 in Robinhood stocks** spread around and dropping/stuck; **Roth IRA around $700** stuck; **Fidelity old-employer account deactivated/abandoned**; she works for herself now and does not know whether to reactivate, roll over, move, or leave it. These are now explicit Pending items.
  - Term she was reaching for: **swing trading** = holding for days/weeks, not day trading. Options/calls are parked until education + written risk limits. Rule: no impulsive trades; inventory, alerts, and rules first.

**🎬 Content & Monetization**
- **Content automation pipeline — BROKEN since ~May 28** — the auto-content system is DOWN; diagnose root cause (NB2 + Anthropic credit top-up?). Separate from making content by hand.
- **Bible dirty stories** — drafted; pick which become Reels, backfill Genesis ⚠️ flag, split long scripts *(not priority)*.
- **Personal content** (her own) — collect + create; uses content + bible material.
- **Merch** — merch links tied to the content/news topics, on a separate page.
- **Product-review page (Amazon Influencer** — she's registered) — dump products she buys, honest good/bad reviews; minimalistic to start; monetize.

**🖥️ Her apps (built — small steps left)**
- **Boletim Diário** — deploy feedback backend + iPhone shortcut / Add-to-Home-Screen.
- **"O que eu acho"** — done; just use it (Claude adds fact-checks on demand).
- **RE quiz** — teach rollout handed off; her "other complaints" pending.

**👩‍👧 Personal / family**
- **Mom's PERSONAL website** (totally separate from the Oak Park business site) — CHECK FIRST whether mom still wants it.

**📓 Focus system**
- Daily 5-line log habit · pick Notability vs Rocketbook + one-time backup · confirm timezone · use the walking desk (stack walk + study/call).
- **Daily MANIFESTATION ritual** — Manifestation Module (4 guided steps, ≤10 min) every morning before tasks; agent leads it and logs Step 3. *(her request 2026-07-13.)*
- **Google-Sheet mirror implemented** — `_Focus Partner — STATE` lives in Drive folder `Productivity & Routine / Focus Partner`. Use it for human scanning; GitHub Markdown remains canonical and must be updated for portability across Codex + Claude.
- **Library Index implemented** — Sheet tab `Library Index` + this Markdown section hold master plans, dashboards, folders, websites, and project trackers. Rule: when an assistant finds an important planning resource, add it to the index.
- **Morning command center / "pop up in my face" system** — required. Priscila needs the journal, Today’s 3, RE study, and money/subscriptions dashboard to appear automatically like Alexa-style reminders. 2026-07-13: updated daily 10:00 calendar event to open the Focus Partner Sheet + journal folder + money check. NEXT build layer: Mac startup/Login Item or macOS Shortcut that opens the command center when she starts work. 2026-07-14 (rev3): Windows launcher BUILT (`scripts/focus-morning.bat` + desktop "Start Focus" + daily 10:00 task). 2026-07-14 (rev6): added the **Boletim Diario** briefing as a 4th tab; shipped the **Mac** launcher (`scripts/focus-morning.command`) + **iPhone Shortcuts** steps (see `scripts/MORNING-COMMAND-CENTER.md`).
- **10:15 daily finance/stocks check** — calendar event created starting Tue 2026-07-14, 10:15-10:30 ET, with popups at 5 min and start. Opens Focus Partner/Library, Finance Dashboard, Tiller, and Stock Tracker; asks for one calm money action.
- **Windows launcher:** 2026-07-14 Claude PC layer is built: `scripts/focus-morning.bat` (portable, in repo) + desktop "Start Focus" shortcut + daily 10:00 task "Focus Morning"; opens journal + Focus sheet + money dashboard. Remaining: Mac Login Item + iPhone Shortcut.

**🎨 Skill development / hobbies**
- **Time awareness** — learn/practice checking time and noticing time passing without avoiding the clock or losing the day to rabbit holes. PARKED for now, but keep it visible.
- **Languages interest** — Chinese, Spanish, Japanese, French, Italian. Too many to actively pursue all at once; later pick ONE tiny starter lane. PARKED for now.

**🌍 Manifestation / travel / money vision**
- **Photo collage / vision board** — Priscila wants a visible board in her room, maybe around/near the TV, with photos of money/travel/family and places she has been or wants to return/go to. Possible print vendor: Walmart Photo. Purpose: morning visual cue that helps her keep facing the money/travel life she wants.

## Task Breakdowns — every backlog item, sub-stepped (added 2026-07-13, at her request)
Each task cut into tiny, finish-able steps. She should only ever look at the NEXT unchecked step, not the whole ladder. The agent keeps these current and pulls the active one into the weekly/daily plan.

**🎓 Study for the FL RE exam (daily habit — "done" = did today's block)**
1. [ ] Open the RE-study quiz on your phone
2. [ ] Do ONE block (~10 questions), timer on
3. [ ] Note the topics you missed in the daily log
4. [ ] (stack) do it ON the treadmill — study while walking

**🏗️ ADS videos → vertical redo** — see the 6 sub-steps in the Planning Frame (this week's active item).

**🎧 AI receptionist — Goodcall setup (DECIDED; Starter ~$59/mo)** — she signs up (outside service, needs her card); Focus preps every paste and walks it ONE step at a time. Never a blank page. The 7 steps (who does each):
1. [ ] **Sign up** at goodcall.com → Start free trial → pick **Starter (~$59/mo)**. *(She does it; she says "I'm in" when the account exists.)*
2. [ ] **Enter business info** — name, services, service area, hours. *(She types; Focus gives the exact text.)*
3. [ ] **Paste the AI script** — greeting + job-seeker screen + what to collect. *(Focus gives it → she pastes. Script saved below.)*
4. [ ] **Set the call flow** — ring **Mike first** → AI answers if no pickup / after-hours. *(She sets it; Focus guides.)*
5. [ ] **Connect Goodcall → Google Sheets (Leads Tracker)** so every call auto-logs. *(Together.)*
6. [ ] **Number wiring** — use **Goodcall's number as the permanent ad / GBP number** (the clean fix for the "saved wrong number" problem). *(She decides; Focus advises.)*
7. [ ] **Test call + confirm it logs** to the Leads Tracker sheet. *(Together.)*
   - **Paste-ready Step 3 script (tailored to her):**
     - *Greeting:* "Thanks for calling Oak Park Construction! I can help get your project started. First — are you looking for a quote on a project, or are you calling about something else?"
     - *If they want a quote (real customer):* collect → name · best callback number · project type (stucco, remodel, new construction, concrete/foundation, addition) · city · timeline. Then: "Perfect — Mike will call you right back today. Anything else you'd like him to know?"
     - *If they mention a job / working / hiring (job-seeker):* "Got it — we handle hiring separately, not through this line, so I won't take up your time here. Thanks for your interest!" → log as **'Not a lead — job seeker'**.
     - *Always capture:* Name · Phone · City/Area · What they need — these map 1:1 to the Leads Tracker columns.
   - Optional: save this as a **"Goodcall Setup"** doc in the MARKETING ADS project folder so it's there while she signs up.

**🏗️ Phone-number decision**
1. [ ] Write the options (keep current / new tracking number / port)
2. [ ] Note what each affects (ad tracking, missed calls)
3. [ ] Decide (or ask the agent for the recommendation)
4. [ ] Set it up with the carrier / receptionist tool

**🏗️ Verify the daily lead-follow-up email landed**
1. [ ] Find which automation sends it
2. [ ] Trigger a test lead OR open today's send log
3. [ ] Confirm the email actually arrived + reads right
4. [ ] If broken, note where it failed → becomes a fix task

**🏗️ Oak Park Construction BUSINESS website (opc-website-v1, live) — revisit** *(≠ mom's site)*
1. [ ] Open the live site; list 3 things to improve (one pass)
2. [ ] Pick the highest-impact one
3. [ ] Make that ONE change
4. [ ] Publish + check it live

**🏗️ Oak Park app (husband didn't adopt)**
1. [ ] One decision: revive or retire?
2. [ ] If revive: name the ONE reason he didn't use it
3. [ ] Fix that one thing — OR formally park the app

**🏗️ Social posting for construction**
1. [ ] Pick ONE platform to start (IG?)
2. [ ] Decide the post type (before/after job photos?)
3. [ ] Draft 3 posts from existing job photos
4. [ ] Post one / schedule them
5. [ ] Set a simple cadence (1×/week)

**🏠 Guest-message monitor ("Maya") — a BUILD project (hand the build to a Claude chat; you approve)**
1. [ ] Write the ONE sentence of what it must do (call me when a guest messages + flag real emergencies)
2. [ ] List the inputs it needs (Airbnb inbox / email access)
3. [ ] Decide: build it, or does an existing tool already do it?
4. [ ] Pilot: detect a new message → call/text you
5. [ ] Add the emergency-keyword flag (locked out, etc.)
6. [ ] Test with a real message

**💰 Clean the subscriptions/expenses sheet**
1. [ ] Find the sheet (or export from bank/card)
2. [ ] List every recurring charge in one column
3. [ ] Mark each: keep / cut / unsure
4. [ ] Cancel the "cut" ones (one sitting)
5. [ ] Total what's left → your real monthly number
6. [ ] (later, parked) turn it into an app

**💰 Subscriptions / spending dashboard — daily visibility**
1. [ ] Locate the current subscriptions/expenses source
2. [ ] Decide the daily view: subscriptions · spending today/this month · what to cut · unusual charges
3. [ ] Connect it to the Finance Dashboard or make a simple companion tab
4. [ ] Put the link in the Morning command center so it appears every day

**💰 Finance Dashboard — PRI 2026 (fill the inputs so it goes live)** — the dashboard is built; it's waiting on YOU. One sitting per card is fine.
1. [ ] Grab each card's statement/app and jot: balance · APR · limit · minimum · due date · statement date — for Discover, Chase, BoA, Citi, Affirm
2. [ ] Enter your **Cash** balance (checking/savings/cash)
3. [ ] Enter your **Investments** total (or link the inventory below)
4. [ ] List any **personal receivables** (who owes you, how much, when)
5. [ ] Decide the **Owner/Michael (Mike) rule** — which transactions are his vs yours
6. [ ] Hand the facts to the finance chat → Codex fills the sheet → dashboard goes fully live

**💰 Investments / stocks — inventory FIRST** *(the "5 years no growth" reset — map before moving anything)*
1. [ ] Robinhood: note holdings + current value
2. [ ] Fidelity 401k: note holdings + value
3. [ ] Crypto: note what/where + value
4. [ ] Brazil vs US: rough split
5. [ ] Put it on ONE page → THEN decide if/what to reset (separate task)

**💰 Robinhood / Roth / Fidelity review cluster** *(captured from Priscila 2026-07-13; planning + inventory first)*
1. [ ] Robinhood: open account and list holdings + current total value (~$10,000 per Priscila)
2. [ ] Roth IRA: identify custodian, holdings, value (~$700 per Priscila), and contribution setup
3. [ ] Fidelity old-employer account: reactivate/login and identify account type + value
4. [ ] Decide which questions need a retirement/tax/provider check before moving anything
5. [ ] Make a one-page decision list: leave / roll over / transfer / restart contributions / do nothing for now

**💰 Swing trading / options learning system — PARKED until rules**
1. [ ] Pick the tracker/watchlist source from Library Index
2. [ ] Write entry criteria, exit criteria, and stop/risk rule before any trade
3. [ ] Set target-price alerts instead of checking obsessively
4. [ ] Learn options/calls basics and define max loss before using real money
5. [ ] Review with a calm checklist; no impulsive buy/sell from anxiety or excitement

**🏗️ Ads tracking / dashboard (diagnose)**
1. [ ] Check: are the ads actually running, or paused?
2. [ ] Check: is the lead-tracking feed writing rows at all?
3. [ ] Name which of the two broke
4. [ ] Hand the fix to a Claude/Codex chat

**🏗️ Google Ads / GA4 conversion cleanup** *(LIVE ad-money change — do Step 2 WITH her, click-by-click, never blind API)*
1. [ ] Confirm the mystery GA4 property is the EMPTY duplicate `506565672` (NOT the good `488744278` / "MGC Account", which IS linked to Ads). Fast: authorize a Google Analytics connection and read it; OR manual: GA4 > Admin > "oakpark-construction.com" property > Property Settings > check Property ID = 506565672.
2. [ ] Fix bidding signals (Google Ads > Goals > Conversions): set **Calls from ads = Primary** (already recording); set **GA4 generate_lead (property 488744278) = Primary** (unhide it — rarely fires, but a real form submit then counts); demote the **3 page-load Contact conversions + Request quote to Secondary** (stay visible, stop steering bids). LIVE money — do it with her watching.
3. [ ] Cleanup (only after 1-2): delete empty property `506565672` + the stray Tag Manager tag `G-CNC2QMMSG8`.

**🏗️ ROOM_VISION (confirm before building)**
1. [ ] Open the ROOM_VISION build plan in Drive
2. [ ] Say in one line what it does for website customers
3. [ ] Decide: alive or dead?
4. [ ] If alive: name the ONE next step; if dead: park it

**🎬 Content automation pipeline (diagnose the ~May 28 break)**
1. [ ] Name what it's supposed to do end-to-end (input → post)
2. [ ] Find where it stops (credits? NB2? a broken step?)
3. [ ] Try the credit top-up / NB2 fix
4. [ ] Test one piece of content end-to-end
5. [ ] If still broken, hand the exact failure point to a build chat

**🎬 Bible dirty stories (Reels)**
1. [ ] Open the drafts
2. [ ] Checkmark which ones become Reels
3. [ ] Flag the Genesis ⚠️ item to fix
4. [ ] Split any long script into Reel length
5. [ ] Hand the shortlist to a content chat to produce

**🎬 Personal content (her own)**
1. [ ] Make one folder/note to collect ideas
2. [ ] Dump 5 ideas you already have
3. [ ] Pick one to make first
4. [ ] Draft it

**🎬 Merch page**
1. [ ] Decide the platform (print-on-demand?)
2. [ ] Pick 3 designs tied to your content topics
3. [ ] Set up the page + links
4. [ ] Link it from the content

**🎬 Amazon product-review page (you're registered)**
1. [ ] List 5 products you already bought + use
2. [ ] Write one honest good/bad line for each
3. [ ] Put them on a simple, minimal page
4. [ ] Add your affiliate links
5. [ ] Publish + share once

**🖥️ Boletim Diário — deploy feedback**
1. [ ] (agent) deploy the feedback backend
2. [ ] (agent) add the iPhone shortcut / Add-to-Home-Screen
3. [ ] You: tap it once to confirm it works

**🖥️ "O que eu acho"** — DONE. No steps — just use it; ask the agent to add a fact-check whenever you want.

**🖥️ RE quiz (teach rollout)** — HANDED OFF. Your one action: paste the "preserve-first" prompt into your RE-study chat.

**👩‍👧 Mom's PERSONAL website** *(separate from the OPC business site)*
1. [ ] Text mom: do you still want it? (2 min)
2. [ ] If yes: what's it for (one sentence)
3. [ ] Start it or park it based on her answer

**📓 Daily 5-line log**
1. [ ] Write 5 lines by hand each day
2. [ ] Drop the scan/photo in the Drive journal folder

**📓 Morning command center / pop-up system**
1. [x] Update daily 10:00 calendar reminder to point to Focus Partner Sheet + journal + money check
2. [x] Add daily 10:15 finance/stocks popup with Focus Partner/Library + Finance Dashboard + Tiller + Stock Tracker links
3. [x] Windows launcher BUILT (Claude PC): `scripts/focus-morning.bat` + desktop "Start Focus" shortcut + daily 10:00 task "Focus Morning" (opens journal + Focus sheet + money dashboard + Boletim)
4. [~] Mac launcher READY: `scripts/focus-morning.command` opens the 4 tabs; she adds it ONCE as a Login Item OR a Shortcuts automation @10:00 (steps in `scripts/MORNING-COMMAND-CENTER.md`)
4b. [~] iPhone launcher READY: Shortcuts automation @10:00 opening the 4 links (step-by-step in `scripts/MORNING-COMMAND-CENTER.md`)
5. [ ] Decide whether to add Alexa/Siri/Reminders nudges for medicine, bedtime, brushing teeth, and work start/stop
6. [ ] Test for 3 days: did it actually pop up enough to change behavior?

**🌍 Manifestation photo collage / vision board**
1. [ ] Pick 10-20 photos: money feeling, travel, family, places already visited, places to return/go next
2. [ ] Choose the physical location: bedroom/near TV/morning line of sight
3. [ ] Print photos (Walmart Photo is one option)
4. [ ] Make the board simple enough to finish in one sitting
5. [ ] Put it where Priscila sees it in the morning

**📓 Pick Notability vs Rocketbook**
1. [ ] Pick ONE
2. [ ] Do the one-time auto-backup setup on the device
3. [ ] Test that one entry syncs to Drive

**📓 Confirm timezone** — ✅ DONE: **Eastern (Miami)**, confirmed 2026-07-13. Reminders assume ET.

**🎨 Skill development / hobbies — PARKED**
1. [ ] Time awareness: create one tiny daily practice for noticing/checking time without shame or avoidance
2. [ ] Languages: park all options first — Chinese, Spanish, Japanese, French, Italian
3. [ ] Later: choose ONE language for a 7-day tiny experiment, not five at once

## Entry Index
| Date | File (id) | Type | Processed | Summary |
|------|-----------|------|-----------|---------|
| 2026-06-29 | Note Jun 29, 2026.pdf (`1o1hxUL42Q8xxNbPZowTUzD3lswgFrIN5`), in Planning/ | PDF | No | not read yet — pending Drive permission |

## Session Log
| Date | Files read | Found | Changed |
|------|-----------|-------|---------|
| 2026-06-30 | none | Built state system + exit/handoff protocol; deep-research COMPLETE | Created STATE files, agent Session+Exit protocols, /exit & /handoff commands, first HANDOFF doc, ideas doc |
| 2026-07-01 | real-estate-quiz.html BANK + render/refLine code | Full audit; only defect = leaked metadata | Stripped 187 leaks, commit `2e7a293`; handed file to teach chat |
| 2026-07-07 | state + agent + her 2 book screenshots | Set up Rule-of-3 + Covey/Eisenhower matrix; captured full backlog | Mirrored agent brain (was missing); planning frame + first weekly plan + master backlog |
| 2026-07-08 | state; her big verbal brain-dump | Explained matrix vs Rule-of-3; captured ALL 17 tasks; RE-quiz "preserve-first" prompt | Full backlog saved+mirrored; 3 calendar events; handwritten Matrix + Task PNGs → GitHub + Desktop + Drive |
| 2026-07-13 | state; her verbal Monday brain-dump; **mined Drive docs (FINANCE_DASHBOARD_MASTER_PLAN, WEEK_PLAN) + repo MDs** | BIG session. Google Ads DONE. ADS videos vertical redo + 6 sub-steps. Monday patterns. Broke ALL backlog into sub-steps. OPC vs mom's website; timezone Eastern (Miami). Archaeology → Finance Dashboard/Investments/Ads-tracking/Content-pipeline/ROOM_VISION. Added TASK-BRAIN rule, daily MANIFESTATION ritual + **guided Manifestation Module (10-min, 4 steps)**, and an **"update" re-sync mechanism + Last-updated stamps**. `/focus` + root `FOCUS-PARTNER.md` (Codex-friendly) shipped. | Mirrored EVERYTHING to GitHub (agent + state + commands + README) |
| 2026-07-13 | Focus Partner state + Drive | Priscila will use Focus Partner in both Codex and Claude. Created clean Google Sheet mirror in `Productivity & Routine / Focus Partner`, moved it out of heavy `Ideas & Inbox`, logged morning manifestation, and added skill-development/hobbies lane. | Sheet mirror implemented; state updated for portability |
| 2026-07-13 | Focus Partner Sheet + Calendar | Priscila said manifestation/body says yes to RE study and finances in check; she needs subscriptions/spending visibility and reminders that pop up like Alexa. | Updated 10:00 daily calendar event into Morning command center; added Mac startup/open shortcut and finance/subscriptions dashboard as next system tasks |
| 2026-07-14 | Focus Partner state + agent (re-audit) | Nothing changed since 07-13 except unrelated `NONNEGOTIABLES.md`; Priscila asked to improve pop-up system, deepen manifestation, de-clutter docs. | Built Windows Morning command-center launcher, added Weekly manifestation review, de-duplicated Sheet-mirror notes, bumped to rev3; all Codex work preserved. |
| 2026-07-14 | Focus Partner brain + state (rev4) | Priscila asked to bulletproof multi-PC sync (Claude + Codex across Windows + Mac). | Added coordination rule: re-pull HEAD before every commit, never force-push, byte-verify after; added monotonic rev counter; bumped to rev4. |
| 2026-07-14 | GitHub audit + Codex merge (rev5) | GitHub rev4 was newer than local and did not yet contain Codex's latest Sheet/calendar captures: Library Index, 10:15 finance popup, Robinhood/Roth/Fidelity details, swing/options safety, and manifestation photo-board. | Merged those items into rev5 instead of overwriting rev4. Sheet + calendar were already updated; Markdown now catches up. |
| 2026-07-14 | Focus Partner state + agent (rev6) | Coordination rule CAUGHT Codex's rev5 (Library Index + 10:15 finance popup + manifestation photo-board) before I pushed — merged onto it, nothing lost. | Added **Boletim Diario** as a 4th tab in the morning launcher; shipped **Mac** (`scripts/focus-morning.command`) + **iPhone** (Shortcuts) triggers; updated `scripts/MORNING-COMMAND-CENTER.md`; bumped to rev6; byte-verified. |
| 2026-07-14 | audit (code + Sheet); her ads-chat action plan | Code healthy (both rev6, byte-verified). BUG: docs said "can't write Sheets" but the googlesheets Composio connection (priscila@) is LIVE + the Sheet is read/writable; Today tab was a day stale. | Fixed the Sheets-write rule + added "keep the Sheet synced" rule; captured the **Google Ads/GA4 conversion cleanup** (3 steps) into Backlog + breakdown + Pending; refreshed the Sheet; bumped to rev7; byte-verified. |
| 2026-07-14 | exit/handoff | Pushed rev7 (commit 1771cbee) + byte-verified: state identical, agent differs only by the intended "mirror to Sheet" clause; all Codex work intact. Synced the Sheet: Today -> 2026-07-14, +3 Google Ads/GA4 rows in Pending!A28:D30. Pulled local ~/.claude to rev7. | Bumped to rev8; wrote HANDOFF_2026-07-14 doc in Productivity & Routine. |
| 2026-07-14 | her marketing/ads chat (Goodcall build) | AI-receptionist decision is made = **Goodcall** (Starter ~$59/mo), recommended in Ads Master Plan §5. Got the full 7-step setup, the paste-ready call script (greeting + job-seeker screen + capture fields mapping to the Leads Tracker), and the number-wiring fix. Also: confirm the "Lead follow-up routine is LIVE" test email; a can-do-now automations health-check; Phase 4 Google Ads conversion de-dupe (244-vs-20). | Rewrote the AI-receptionist breakdown into the Goodcall 7-step build + script; added health-check + Phase 4 backlog lines; added 3 Library Index rows (MARKETING ADS folder, Leads Tracker, Ads Master Plan); +4 Pending rows; bumped to rev9. |

Ideas doc: `Focus Partner — Research & Ideas` in journal folder. Suggested refinements (her call): weekly = highlights/lowlights/patterns · mid-day check-in · anchor morning review to an existing habit.

## Pending Tasks (near-term, actionable)
| Task | Status | Source | Next action |
|------|--------|--------|-------------|
| Google Ads rep call | ✅ DONE | 2026-07-07 planning | meeting happened last week — closed, not pending |
| ADS videos — vertical-format redo (Q2 this week) | IN FOCUS | 2026-07-13 | work+personal; redo everything vertical. See 6 sub-steps. Today = steps 1–2. Never drop from focus. |
| RE-quiz fixes prompt | READY TO PASTE | 2026-07-08 | give the "preserve-first" prompt to her RE-study chat |
| Study for RE exam (daily) | ONGOING | 2026-07-07 | a focused study block every day; track in daily log |
| Daily 5-line log habit | ONGOING | her system | write 5 lines by hand each day → syncs to Drive |
| Daily manifestation (Manifestation Module) | ONGOING | 2026-07-13 | agent runs the 4-step module each morning before planning; logs Step 3 verbatim |
| Focus Partner Google Sheet mirror | ✅ IMPLEMENTED | 2026-07-13 | `_Focus Partner — STATE` in Drive folder `Productivity & Routine / Focus Partner`; keep as a lightweight mirror, Markdown remains canonical |
| Library Index | ✅ IMPLEMENTED | 2026-07-13 | Sheet tab `Library Index` + Markdown Library Index now hold master plans, dashboards, folders, websites, and key docs |
| Morning command center / pop-up system | IN PROGRESS | 2026-07-13 | 10:00 calendar event updated; next build Mac startup/Login Item or Shortcut to auto-open Focus Partner Sheet/journal |
| 10:15 finance/stocks popup | ✅ ADDED | 2026-07-13 | daily 10:15-10:30 ET event starting Tue 2026-07-14; check subscriptions/spending + Robinhood/Fidelity/Roth inventory + one calm money action |
| Subscriptions/spending visibility | PRIORITY | 2026-07-13 | create/connect dashboard view for subscriptions, spending, what to cut, and daily money awareness |
| Skill development / hobbies | PARKED | 2026-07-13 | time awareness + language interests (Chinese, Spanish, Japanese, French, Italian); later pick ONE tiny experiment |
| RE quiz "teach" rollout | HANDED OFF | her request | runs in her RE-study chat via the paste-in prompt |
| Website for her mom | CHECK WITH HER | 2026-07-07 | ask if mom still wants it before any work |
| Finance Dashboard inputs | NEEDS HER DATA | 2026-07-13 mined | card facts + cash + investments + receivables + Mike rule so Codex can finish it |
| Investments inventory | NEEDS HER DATA | 2026-07-13 mined | one-page map of Robinhood + 401k + crypto + Brazil/US before any reset |
| Robinhood ~$10k stocks | NEEDS INVENTORY | 2026-07-13 Priscila | list holdings + current value; no buy/sell until inventory and rules |
| Roth IRA ~$700 | NEEDS REVIEW | 2026-07-13 Priscila | identify custodian/holdings/contribution setup |
| Fidelity old-employer account | NEEDS REACTIVATION/DECISION | 2026-07-13 Priscila | reactivate/login; identify account type/value; decide leave/rollover/transfer after checking implications |
| Swing trading/options idea | PARKED UNTIL RULES | 2026-07-13 Priscila | build watchlist, alerts, entry/exit/risk rules before considering trades; options/calls are high-risk |
| Manifestation photo collage board | PENDING | 2026-07-13 Priscila | choose photos + location, print via Walmart or similar, place where she sees it in the morning |
| Ads tracking broke | TO DIAGNOSE | 2026-07-13 mined | check ads-running vs tracking-feed; 0-row days June 1 & 8 |
| AI receptionist — Goodcall setup | DECIDED — her move | 2026-07-14 ads chat | She signs up (Starter ~$59/mo) + says "I'm in"; Focus walks steps 2-7 with the script ready. See breakdown. |
| Lead follow-up test email | CONFIRM | 2026-07-14 ads chat | check the "Lead follow-up routine is LIVE" test email landed in her inbox |
| Automations health-check | FOCUS CAN DO NOW | 2026-07-14 ads chat | confirm the dashboard actually refreshed + the daily follow-up routine ran clean (a week passed) |
| Google Ads Phase 4 conversion de-dupe (244-vs-20) | FOCUS CAN DO NOW | 2026-07-14 ads chat | de-dupe the messy/duplicate conversion actions so reporting is trustworthy |
| Google Ads: confirm duplicate GA4 property | NEEDS HER | 2026-07-14 ads chat | authorize a GA connection (fast) OR check GA4 > Admin > oakpark property > Property ID = 506565672 (empty dup) vs 488744278 (good, keep) |
| Google Ads: fix bidding signals | DO WITH HER | 2026-07-14 ads chat | Calls=Primary; GA4 generate_lead (488744278)=Primary; demote 3 Contact page-loads + Request quote to Secondary. LIVE money — click-by-click, not blind API |
| Google Ads/GTM cleanup | AFTER STEPS 1-2 | 2026-07-14 ads chat | delete empty GA4 property 506565672 + stray GTM tag G-CNC2QMMSG8 |
| Content pipeline broke (~May 28) | TO DIAGNOSE | 2026-07-13 mined | find where it stops (credits/NB2); test one piece end-to-end |
| ROOM_VISION scope | CONFIRM WITH HER | 2026-07-13 mined | open the Drive build plan; confirm what it is + alive/dead |
| Confirm timezone | ✅ DONE | — | Eastern (Miami), confirmed 2026-07-13 |
| Read + seed first entry (Jun 29) | NOT DONE | — | read PDF, summarize into Entry Index |

## Patterns
- **Monday plan-paralysis (her #1, told me 2026-07-13):** every Monday she plans and plans and doesn't DO; very slow start. Example: 2026-07-13 spent ~3 hrs (till 12:23pm) on a 15-min laptop/email setup and got nothing done. → keep Monday planning <5 min; force ONE tiny start.
- **Setup rabbit-holes:** small admin tasks balloon into hours. → time-box them out loud.
- **Mike calls:** ~40 min, productive — don't cut, but cap/pair-with-walking.
- **Walking desk unused:** owns a treadmill w/ table → stack: walk WHILE studying RE or on Mike's call.
- **RE study:** she says it should be daily — flag missed days.
- **Manifestation patterns (from her source, 2026-07-13):** she drifts negative + can't visualize well + carries scarcity/abandonment/"love-unsafe" beliefs → CALM her nervous system, CATCH & FLIP negative self-talk, use feeling/other-senses over visualization, bring her back to positive daily (consistency > intensity).
- **Needs external prompts, not memory:** she explicitly compared the desired system to Alexa telling her medicine/bed/brush teeth. Build layered reminders that pop up in her face: Calendar + Mac startup/open link + optional Alexa/Siri/Reminders. Do not rely on her remembering to open the journal/dashboard.
- (more populates as entries are read — avoidance, hyperfocus, energy)
