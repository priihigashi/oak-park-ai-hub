# Focus Partner — STATE (canonical local copy)

**Last updated: 2026-07-14 (rev15)** — bump the date AND increment (revN) by 1 on every push (never reuse a rev); "update" compares by date, then by rev. rev15 = installed the global `CLAUDE.md` rulebook on this Mac (`~/.claude/CLAUDE.md`, mirrored from GitHub repo root, CLAUDE.md itself was untouched by any other branch so this was a clean add) + added an explicit mirror rule at its top (edit either copy → push GitHub + re-sync local, same session, always) + audited this Mac against what CLAUDE.md assumes, logging real gaps in **Setup Gaps — this Mac** + 3 new Pending Tasks rows (Google Calendar/Sheets/Drive not connected here via any of the 3 documented routes; `~/ClaudeWorkspace/`+skills+`AGENTS.md`+memory-reference files all absent; calendar-link fix blocked on the same). Re-pulled HEAD first (rev7→rev14 had moved underneath this session via a 3-way merge across Windows/Mac/personal-chat branches) — synced local to true rev14 before adding anything, nothing overwritten. rev14 = 3-way MERGE-RECONCILE (git base=rev7 `1771cbee`): GitHub held a Mac/other-machine branch (its own rev8 exit-handoff + rev9 Goodcall build) this Windows local had never seen, while local had stacked rev8-ads through rev13 that GitHub never saw — unioned both via git 3-way merge, nothing lost. Folded in from the remote branch: **[remote rev9] the DECIDED AI-receptionist build — Goodcall** (Starter ~$59/mo; 7-step setup + paste-ready call script + number-wiring fix + Leads-Tracker auto-log) + automations health-check + **Phase 4** Google Ads conversion de-dupe (244-vs-20); **[remote rev8]** the earlier exit/handoff (pushed+byte-verified rev7, synced the Sheet, pulled local ~/.claude, wrote HANDOFF_2026-07-14). NOTE: "rev8"/"rev9" collided across machines — entries below are per-branch. rev13 = PERSONAL (robot-vacuum shopping chat, not focus work): researched a trustworthy, toy-avoiding robot vacuum under budget. Landed on **Roborock** (most trustworthy of the mostly-Chinese camera brands; also one of only 2 that can run fully offline via Valetudo). Key teaching moment: separated **pro/lab reviews** from **real owner ratings** at her prompting — the tester-loved Qrevo **Edge** actually has poor owner-reported obstacle avoidance, and the "Curv **2**" is a downgrade (16/24 toys, can't climb) despite the higher number. TOP PICK = **Qrevo CurvX** (20/24 toys, climbs 40mm, happy owners, ~$849 over her $600 budget); budget alt = **Qrevo S Pro** (~$500-595, well-liked, no camera). Also covered privacy: nearly all camera vacuums are Chinese (Dreame/Narwal/eufy/Ecovacs all flagged); only iRobot/Roomba is US + best security rating. Added both picks to her **Skincare + Injectables Shopping List** Sheet (`1QQN4LhgBWByMhuWBN9HzFa39YD3UDwJ5BpYptDnHAXs`, tab "Untitled", new ROBOT VACUUM section) via Composio googlesheets (priscila@) — write path works. Does NOT change Weekly 3. rev12 = PERSONAL (cruise-planning chat): captured her **2 cruise trips** (adults birthday Aug + family Disney Nov 25) as a new **🌍 Travel / Cruise** lane — added 6 cruise rows to Pending here + 7 Pending / 3 Backlog rows to the Sheet mirror. Created a teal **🚢 Cruises** Gmail label on BOTH accounts + labeled 13 existing cruise emails; the Gmail auto-FILTER is left as her 30-sec manual step (Composio Gmail can't create filters — hard 403 scope, even after re-auth). Key facts: free travel agent (Timeless Tales / Priscila Roque) quoting RC + Disney; **EXPIRING Virgin hold #2637267** (Key West & Bimini); RC Jewel Sep-11 hold; light-drinker → NO drink package; book DIRECT (not OTAs); seasickness → always midship + low-deck cabin; lives 40–60 min from ports. Does NOT change Weekly 3. rev11 = MERGE — folded in the **Mac** session's GitHub rev8 that this PC's local branch had never seen (a cross-machine **rev8 collision** the coordination rule caught before a push could lose it): [Mac] made the GitHub freshness check AUTOMATIC — sessions now compare local vs GitHub rev as **Step 0** every time (no "update" magic word needed) + set up `gh` push auth on the Mac; that Step-0 rule lives in the `/focus` skill + agent Session Protocol (already on GitHub). Everything below (RE-quiz, skincare, ads audit) was already stacked in local; this commit pushes it all up together so GitHub stops lagging at the Mac's rev8. rev10 = RE-QUIZ session (her RE-study chat, not core focus planning): shipped **review-previous-questions** (in-round ◀ Back button, read-only/locked, + end-of-round recap) and a **two-tab gabarito** (results sheet: "This session" / "Overall", only-answered = no spoilers, tap a tile → review modal + "See it in the book") into `real-estate-quiz.html`; audited both (271/271 book-proof + teach byte-identical, all scripts parse, 0 leaks, live-verified); fixed 2 review-logic bugs; wrote the **master manual** `real-estate-quiz.MANUAL.md` (canonical spec of every request + how the app should behave) to the repo. Does NOT change Weekly 3 or focus Pending. rev9 = PERSONAL session (not focus work): researched treatments for lines around her mouth — compared 3 local med spas (Sandbar / Medical Advanced / Icon), landed on skincare-first plan (retinal + SPF), baby Botox as the in-office step, filler NOT needed yet at 37 with soft lines. Built her a **Skincare + Injectables Shopping List** Google Sheet in the Captures/UGC drive (id `1QQN4LhgBWByMhuWBN9HzFa39YD3UDwJ5BpYptDnHAXs`). Does NOT change Weekly 3 or any Pending focus task. rev8 = RAN the Google Ads conversion **audit** (API quota cleared): tracking CONFIRMED recording real conversions on serving acct 8945889168; found 3 triple-counted page-load "Contact" conversions polluting bidding; confirmed good GA4 property 488744278 IS linked to Ads (events imported but HIDDEN) + a 2nd "oakpark-construction.com" GA4 feed (likely empty dup 506565672); Priscila chose **option 1** (calls + real form-submit = primary). Cleanup steps 1-3 unchanged; audit now done, Step 1 (confirm the dup property) is the immediate next. rev7 = fixed the false "can't write Sheets" rule (the googlesheets Composio connection as priscila@ is LIVE; the Sheet is read+writable from here) + Focus now keeps the Sheet mirror synced; captured the Google Ads/GA4 conversion-cleanup task from her ads chat. rev6 = added the Boletim Diario briefing as a 4th tab in the morning launcher + shipped Mac (scripts/focus-morning.command) & iPhone (Shortcuts) triggers. rev5 = merged Codex 2026-07-13/14 Sheet + calendar work into GitHub rev4: Library Index, 10:15 finance/stocks popup, Robinhood/Roth/Fidelity specifics, swing-trading/options safety, and manifestation photo-board project. rev4 = bulletproof multi-PC sync: re-pull HEAD before every commit + monotonic rev counter. rev3 = built the Morning command-center launcher (Windows) + weekly manifestation review + de-cluttered repeated Sheet-mirror notes. rev2 = enriched Pending Tasks + capture-specifics rule.

Canonical state lives in this Markdown file on GitHub. (A human-readable Google Sheet mirror also exists — see the **Google Sheet mirror** line just below for its URL/IDs.)

- **Last check:** 2026-07-14 (PERSONAL robot-vacuum shopping chat: researched a trustworthy, toy-avoiding robot vacuum; landed on **Roborock Qrevo CurvX** (top) / **Qrevo S Pro** (budget); taught her to weigh real owner ratings over lab reviews; added both to her shopping-list Sheet. No core-focus change.) Earlier same day: RE-study chat: shipped **review-previous-questions** + **two-tab gabarito** into the RE quiz, audited + live-verified, and wrote the **master manual** `real-estate-quiz.MANUAL.md` to the repo. Earlier same day: (1) ads chat — Google Ads conversion **audit** via API [tracking confirmed; 3 triple-counted Contact page-loads; GA4 488744278 linked; she picked option 1 = calls + form-submit primary; next = confirm empty dup GA4 506565672]; (2) PERSONAL — skincare/injectables research + shopping-list Sheet. No core-focus-task change.)
- **Prev check:** 2026-07-13 (Monday — huge session: `/focus` shortcut + portable install + Codex-ready `FOCUS-PARTNER.md`; Google Ads DONE; ADS-videos vertical redo; Monday patterns; broke ALL backlog into sub-steps; timezone Miami/Eastern; two websites separated; mined Drive/repo → Finance Dashboard/Investments/Ads-tracking/Content-pipeline; TASK-BRAIN rule; ROOM_VISION; **guided Manifestation Module + "update" mechanism**; Library Index created; 10:15 finance/stocks popup added; manifestation photo-board idea captured)
- **Timezone:** America/New_York — **Eastern (Miami), confirmed by Priscila 2026-07-13**
- **Journal folder:** `📓 Daily Journal — DROP HERE` (id `1eknXv30UHtuDVDDRJpyt3eBLqsxhjABB`)
- **Google Sheet mirror:** `_Focus Partner — STATE` (`https://docs.google.com/spreadsheets/d/1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c`) in folder `Focus Partner` (`18API545Cqh0k7V2PPG3hnEeTRJHz7jZO`) under `Productivity & Routine`. Lightweight human-readable mirror only; GitHub Markdown remains canonical.
- **Tool usage:** Priscila will use this Focus Partner in both Codex and Claude. Any assistant must read/update this Markdown state and keep the Sheet mirror current. The Sheet IS writable from here via the `googlesheets` Composio connection (account `googlesheets_allyl-rearm` = priscila@; sheet id `1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c`) — when the Markdown changes, push the same change to the Sheet so it never goes stale.
- **Library / Index:** The Google Sheet now has a `Library Index` tab. Keep it mirrored here: every master plan, dashboard, important Drive folder, website/login portal, stock/finance sheet, handoff, and project tracker that may be needed for planning should be added to both places.

## Setup Gaps — this Mac (found 2026-07-14 installing global `CLAUDE.md`)
`CLAUDE.md` (the global business-automation rulebook — content pipeline, Drive routing, ads, 4AM agent) is now installed at `~/.claude/CLAUDE.md`, mirrored from the GitHub repo root, with an explicit mirror rule added at its top (edit either copy → push GitHub + re-sync local, same session, every time). But it assumes infrastructure this Mac doesn't have yet. Checked directly, not assumed:
- ❌ `~/ClaudeWorkspace/` (workspace + credentials folder, incl. `sheets_token.json` / `SHEETS_TOKEN`) — does not exist here
- ❌ `~/.agents/skills/` and `~/.claude/skills/` (the `/session-start`, `/capture`, `/content-chief`, `/calendar-create`, `/4am-agent` etc. skills CLAUDE.md refers to) — does not exist here
- ❌ `~/AGENTS.md` (Codex mirror) — does not exist here
- ❌ `~/.claude/projects/.../memory/reference_active_connections.md`, `reference_credentials.md`, and the other `reference_*`/`feedback_*` memory files CLAUDE.md points to — memory folder is empty on this Mac
- ❌ **Google Calendar / Sheets / Drive access — NOT connected on this Mac**, checked via all 3 documented routes (per CLAUDE.md's own "not absent, check ToolSearch" rule): MCP deferred tools → zero found; Composio (`googlesheets_allyl-rearm` etc., which the Windows-side sessions clearly use successfully — see rev8-13 above) → zero found on this Mac; OAuth Python route needs `sheets_token.json` → the credentials folder doesn't exist here. Confirmed by searching, not a failure to look — this is a per-computer/per-login connection gap, not a missing-file gap.
- ✅ GitHub — fully working on this Mac (`gh` CLI installed + authenticated as priihigashi, push access confirmed).

**What this means:** this Mac can read/write the Focus Partner + CLAUDE.md GitHub files fine, but cannot yet touch Google Calendar/Sheets/Drive, run any CLAUDE.md skill, or use the OAuth credential route. That's a separate, bigger project (see Pending Tasks) — not done today.

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
- **RE quiz** — ✅ teach (271/271), reorder, 3-page book viewer, cross-device sync, review-previous + gabarito all shipped. Canonical spec: repo `real-estate-quiz.MANUAL.md`. Only small follow-ups left (button rename; p.541 boilerplate).

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
*(Audit DONE 2026-07-14: tracking confirmed recording; the 3 page-load Contact conversions triple-count; GA4 488744278 IS linked. Steps below are what's LEFT.)*
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
| 2026-07-14 | New Mac (Claude Code) install; Priscila asked whether she needs to say "update" every session | She confirmed twice that GitHub had newer revs (rev6, then rev7) she'd have missed without asking — the manual "say update" step was a gap against the system's own "she should never have to remember" rule. Also confirmed via full commit-history audit that no non-Priscila account has ever touched `.claude/` (only a `nonnegotiables-bot` on an unrelated file) — nothing suspicious. | Installed `gh` CLI + browser login on the Mac so it can push directly; added **Step 0 auto freshness-check** to `/focus` + the agent Session Protocol — every session now silently compares local vs GitHub rev and pulls if newer, no magic word; bumped to rev8 (Mac branch). *(folded into local at rev11 — this row was on GitHub but not in local until the merge.)* |
| 2026-07-14 | Google Ads serving acct 8945889168 via Composio GAQL (2 queries: conversion_action config + last-30d volume) | Google Ads API quota CLEARED (was rate-limited 07-09) → pulled it directly, no screenshots. **Tracking confirmed recording:** Calls from Smart Campaign Ads 15, Calls from ads 4, Contact-page-loads/Contact Us ~7 each, Request quote 7 (last 30d). 31 conversion actions = messy: **3 overlapping page-load "Contact" conversions triple-count** the same contact page. GA4 events imported from TWO properties (both HIDDEN): "MGC Account (web)" = good **488744278** (confirms Ads↔GA4 link ✅), "oakpark-construction.com (web)" = 2nd feed, likely empty dup 506565672. Priscila chose **option 1** (calls + real form-submit primary; realistic caveat: forms rarely fire → calls are the workhorse). | Ran the audit; gave her the 3-step plan; bumped to rev8. No live-account changes made (Step 2 bidding change is do-with-her-watching). |
| 2026-07-14 | PERSONAL (not focus work): 3 med-spa websites + reviews + retinoid/SPF/filler research | Priscila asked about lines around her mouth. Landed on: skincare-FIRST (prescription tretinoin 0.05% or Medik8 Crystal Retinal 10 / Avène RetrinAL 0.1% + EltaMD SPF 46) → baby Botox as the in-office step (~$150-300) → filler NOT needed yet (soft lines at 37). Compared **Sandbar** (Rachel Polazzi CRNA, ultrasound-guided = top pick), **Medical Advanced** (Cici, "never pushy"), **Icon** (Chad, CoolPeel laser). Noted my aggregator star ratings ≠ live Google Maps — she should trust Maps. | Built the **Skincare + Injectables Shopping List** Sheet (`1QQN4LhgBWByMhuWBN9HzFa39YD3UDwJ5BpYptDnHAXs`) in Captures/UGC drive. No change to Weekly 3 / Pending. Bumped to rev9. |
| 2026-07-14 | RE quiz `real-estate-quiz.html` (live HEAD, full audit) | RE-study chat. Built the two features Priscila asked for: (1) **review previous questions** — in-round ◀ Back button (read-only/locked, can re-read but never change a submitted answer) + end-of-round recap tiles; (2) **gabarito** results sheet in 📊 My Progress — two tabs (This session / Overall), only shows already-answered questions (no spoilers), green/red tiles + accuracy %, tap a tile → review modal with "📖 See it in the book". Audited: 271/271 book-proof + teach byte-identical, all scripts parse, 0 leaks, live-verified; fixed 2 review-logic bugs (`cbe9bc0`). | Committed features + audit fixes; then wrote **master manual** `real-estate-quiz.MANUAL.md` (commit `75f5f13`) = canonical spec of every request + how the app should behave; pointed the RE-quiz memory at it; bumped to rev10. |
| 2026-07-14 | GitHub `.claude/focus-partner-state.md` (pulled HEAD, byte-diffed) via Composio | **rev8 COLLISION found:** GitHub was at the **Mac's** rev8 (freshness automation), but this PC's local had independently gone rev8(ads)→rev9(skincare)→rev10(RE-quiz) — none of which were on GitHub, AND local was missing the Mac's rev8. The "pull only if GitHub newer" auto-check would NOT have caught it (local rev10 > remote rev8) → next push would have silently clobbered the Mac's freshness work. | Folded the Mac's rev8 into local (rev-history + its session-log row), bumped to **rev11**, pushed the merged file to GitHub so it holds everything (Mac freshness + ads audit + skincare + RE-quiz). Nothing lost. |
| 2026-07-14 | PERSONAL robot-vacuum shopping chat; deep-research workflow + live web/Amazon lookups; her shopping-list Sheet | Helped her pick a robot vacuum: trustworthy company, avoids kids' toys, "tank" (won't get stuck). Big teaching thread — she pushed me to separate **lab/pro reviews** from **real owner star ratings**; that flipped the tester-loved Qrevo **Edge** (owners report poor obstacle avoidance + smelly dock + buggy app) OUT, and exposed the "Curv **2**" as a downgrade (16/24 toys, 20mm climb only) despite the higher number. Privacy: nearly all camera vacuums are Chinese (Dreame=Xiaomi/Suzhou, Narwal=Tencent+ByteDance/Shenzhen, eufy, Ecovacs — all flagged for camera/data issues); only iRobot/Roomba is US + top security. She's fine with a camera, wants a trusted brand → **Roborock** (best of the Chinese group; Valetudo-offline option). Landed on **Qrevo CurvX** (top, ~$849) vs **Qrevo S Pro** (budget, ~$500-595). | Added a ROBOT VACUUM section (2 rows) to her **Skincare + Injectables Shopping List** Sheet (`1QQN4LhgBWByMhuWBN9HzFa39YD3UDwJ5BpYptDnHAXs`, tab "Untitled", range A28:F31) via Composio googlesheets/priscila@; added a personal Pending row. Bumped to **rev13**. No Weekly 3 change. |
| 2026-07-14 | PERSONAL cruise-planning chat + her Hotmail + both Gmails | Helped plan **2 cruises**: adults birthday (Aug) + family Disney (Nov 25, w/ 2 kids ages 4 & 6). Compared MSC/RC/Celebrity/Virgin/Carnival → ruled out party (Carnival), GTY-can't-pick-cabin (Celebrity), no-kids-for-family (Virgin); light-drinker → no drink package; book DIRECT; seasick → midship. Built a **Cruise Research Report** (Desktop `Cruise_Research_Report.html` + emailed to oakpark). Connected her **Hotmail**; scanned all 3 inboxes for cruise mail + promo codes (no codes — deals auto-apply). Found: free agent **Timeless Tales / Priscila Roque** quoting RC + Disney, **EXPIRING Virgin hold #2637267**, RC Jewel Sep-11 hold, MSC "$500 OBC" offer. | Added a **🌍 Travel/Cruise** lane to Pending (here) + Sheet (7 Pending + 3 Backlog rows); created teal **🚢 Cruises** Gmail label on both accounts + labeled 13 existing cruise emails; bumped to **rev12**. Gmail auto-filter left as her manual step (Composio Gmail integration lacks the create-filter scope; 403 even after re-auth). |
| 2026-07-14 | exit/handoff | Pushed rev7 (commit 1771cbee) + byte-verified: state identical, agent differs only by the intended "mirror to Sheet" clause; all Codex work intact. Synced the Sheet: Today -> 2026-07-14, +3 Google Ads/GA4 rows in Pending!A28:D30. Pulled local ~/.claude to rev7. | Bumped to rev8; wrote HANDOFF_2026-07-14 doc in Productivity & Routine. |
| 2026-07-14 | her marketing/ads chat (Goodcall build) | AI-receptionist decision is made = **Goodcall** (Starter ~$59/mo), recommended in Ads Master Plan §5. Got the full 7-step setup, the paste-ready call script (greeting + job-seeker screen + capture fields mapping to the Leads Tracker), and the number-wiring fix. Also: confirm the "Lead follow-up routine is LIVE" test email; a can-do-now automations health-check; Phase 4 Google Ads conversion de-dupe (244-vs-20). | Rewrote the AI-receptionist breakdown into the Goodcall 7-step build + script; added health-check + Phase 4 backlog lines; added 3 Library Index rows (MARKETING ADS folder, Leads Tracker, Ads Master Plan); +4 Pending rows; bumped to rev9. |
| 2026-07-14 | New Mac (Claude Code) — found + installed root `CLAUDE.md`; ToolSearch audit for Google Calendar/Sheets; caught a live rev13→rev14 collision mid-session | She asked to install `CLAUDE.md` too and pushed back on "no Calendar access," correctly pointing out the routes are documented in CLAUDE.md itself. Re-checked via ToolSearch (MCP + Composio) exactly as CLAUDE.md instructs — genuinely zero Google tools on this Mac/login, confirmed not assumed. Mid-edit, remote moved from rev7(base) to rev14 (a 3-way merge across this Windows PC's stacked rev8-13 and the Mac's own rev8/9) — caught it via the coordination rule's re-pull-before-push check before any of my pending edits could clobber it. | Installed `CLAUDE.md` to `~/.claude/CLAUDE.md` + added an explicit mirror rule at its top (CLAUDE.md itself was untouched by the other branches, clean add). Reset local to the true rev14, then re-applied only my own still-pending edits (Setup Gaps section + 3 Pending rows) on top — nothing from rev8-14 overwritten. Bumped to rev15. |

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
| RE quiz "teach" rollout | ✅ DONE | her request | teach live on all 271; ran in her RE-study chat |
| RE quiz — review + gabarito features | ✅ DONE (2026-07-14) | her request | Back-review + end-of-round recap + two-tab gabarito live; canonical spec at repo `real-estate-quiz.MANUAL.md`. Open follow-ups: rename "Sync now"→"Get my progress"; fix `book p.541` boilerplate page number |
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
| 🌍 Cruise — birthday trip (Aug): decide + BOOK | NEEDS HER DECISION | 2026-07-14 cruise chat | get agent quote prices (Timeless Tales, in Hotmail); pick MSC Aurea (adults Solarium+thermal ~$1,487) vs RC Wonder/Jewel (cheaper, CocoCay); book DIRECT; MIDSHIP low-deck cabin (she's seasick); light-drinker → NO drink package |
| 🌍 Cruise — Virgin hold #2637267 (Key West & Bimini) EXPIRING | DECIDE NOW | 2026-07-14 | book it or let the no-deposit courtesy hold lapse ("drifting away" reminder already sent) |
| 🌍 Cruise — RC Jewel of the Seas Sep-11 hold | DECIDE | 2026-07-14 | keep or release the no-deposit courtesy hold |
| 🌍 Cruise — Disney family trip (Nov 25) | NEEDS HER DECISION | 2026-07-14 | 2 adults + 2 kids (ages 4 & 6); Disney Fantasy 4-nt Bahamian; get quote; confirm cabin sleeps 4; book + travel insurance |
| 🌍 Cruise — travel insurance | TO BUY | 2026-07-14 | medical + EVACUATION (her HMO won't cover the Bahamas or the ship) |
| 🌍 Cruise — Gmail auto-filter | MANUAL STEP LEFT | 2026-07-14 | 🚢 Cruises label + 13 existing emails DONE on both Gmails; the FILTER must be clicked manually (Composio Gmail can't create filters — 403 scope) |
| 🛒 Robot vacuum — decide + buy (personal) | HER DECISION | 2026-07-14 vacuum chat | Both picks on her shopping-list Sheet. Choose: **stretch to Qrevo CurvX ~$849** (camera sees toys, climbs 40mm, happy owners) OR **stay in budget Qrevo S Pro ~$500-595** (well-liked, no camera = only OK at toys). Tip given: set a camelcamelcamel price alert ~$700 on the CurvX. Amazon CurvX: amazon.com/dp/B0DX1DQKMD |
| Connect Google Calendar/Sheets/Drive on this Mac | BLOCKED — needs her login | 2026-07-14 CLAUDE.md audit | none of the 3 documented routes (MCP/Composio/OAuth token file) are set up on this Mac; likely needs her to add the Google Workspace connector under Claude settings, or copy `~/ClaudeWorkspace/Credentials/sheets_token.json` from the Windows PC |
| Set up `~/ClaudeWorkspace/`, `~/.agents/skills/`, `~/AGENTS.md`, memory reference files on this Mac | PARKED — bigger project | 2026-07-14 CLAUDE.md audit | needed for CLAUDE.md's skills/pipeline rules to actually work here; not started, own session when she wants it |
| Calendar links not clickable (10:00 + 10:15 events, priscila@oakpark-construction.com) | BLOCKED on Calendar connection above | 2026-07-14 | paste-ready link text already handed to her as a stopgap; real fix needs Calendar write access on whichever computer has it |

## Patterns
- **Monday plan-paralysis (her #1, told me 2026-07-13):** every Monday she plans and plans and doesn't DO; very slow start. Example: 2026-07-13 spent ~3 hrs (till 12:23pm) on a 15-min laptop/email setup and got nothing done. → keep Monday planning <5 min; force ONE tiny start.
- **Setup rabbit-holes:** small admin tasks balloon into hours. → time-box them out loud.
- **Mike calls:** ~40 min, productive — don't cut, but cap/pair-with-walking.
- **Walking desk unused:** owns a treadmill w/ table → stack: walk WHILE studying RE or on Mike's call.
- **RE study:** she says it should be daily — flag missed days.
- **Manifestation patterns (from her source, 2026-07-13):** she drifts negative + can't visualize well + carries scarcity/abandonment/"love-unsafe" beliefs → CALM her nervous system, CATCH & FLIP negative self-talk, use feeling/other-senses over visualization, bring her back to positive daily (consistency > intensity).
- **Needs external prompts, not memory:** she explicitly compared the desired system to Alexa telling her medicine/bed/brush teeth. Build layered reminders that pop up in her face: Calendar + Mac startup/open link + optional Alexa/Siri/Reminders. Do not rely on her remembering to open the journal/dashboard.
- (more populates as entries are read — avoidance, hyperfocus, energy)
