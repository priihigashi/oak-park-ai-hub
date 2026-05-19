# Claude Global Rules — Oak Park Construction / Priscila
# Every Claude session reads this first. These rules are non-negotiable.
# Shared task skills live in ~/.agents/skills/<name>/SKILL.md (symlinked into ~/.claude/skills/ and ~/.codex/skills/).
# Codex mirror: ~/AGENTS.md. Repo source of truth: priihigashi/oak-park-ai-hub.

## PIPELINE REFERENCE DOC — END-TO-END SYSTEM MAP
Single source of truth for the content automation pipeline: URL drop → capture → 4AM agent → carousel build → approval → Buffer → posted.
Doc: https://docs.google.com/document/d/1XGmbnvyS_WomKl3USVFz-pPg-3agTn5Bl0QpyMbeHs4/edit
Use it for cold-start orientation, stage ownership, IDs/env vars, failure modes, recovery steps, and manual gaps. Built from live script audit 2026-04-19. Step F compressed 2026-05-19.

## CONNECTIONS — always active, never ask for access

### ROUTING RULE — CLOUD FIRST (added 2026-04-12)
For every Google service: try Google Cloud OAuth / MCP first. Composio = fallback only.
Composio is ONLY required for: (1) Google Docs writes (GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN) and (2) Instagram posting. Everything else has a Cloud/MCP route.
GitHub scripts already follow this — they use SHEETS_TOKEN (Google OAuth) directly, never Composio.

Google Sheets:
  ROUTE A (preferred): Google Sheets API via OAuth — curl/python with SHEETS_TOKEN
  ROUTE B (fallback): Composio MCP (session_id "cook") — GOOGLESHEETS_* tools
Google Docs:
  ROUTE A (only option): Composio MCP — GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN ✅
  (No simple REST equivalent for Docs content injection)
Google Drive:
  ROUTE A (preferred): mcp__claude_ai_Google_Drive__ tools (DEFERRED — load via ToolSearch)
  ROUTE B: mcp__gdrive__search (skip on -32603 error)
  ROUTE C: OAuth Python curl with supportsAllDrives=true
Google Calendar:
  ROUTE A (preferred): mcp__claude_ai_Google_Calendar__ tools (DEFERRED — load via ToolSearch) ✅
  ROUTE B: Composio MCP — GOOGLECALENDAR_CREATE_EVENT
  ROUTE C: Python OAuth — build('calendar','v3',credentials=creds) — sheets_token.json HAS calendar scope
Gmail (read/write/draft):
  ROUTE A (preferred): mcp__claude_ai_Gmail__ tools (DEFERRED — load via ToolSearch; DRAFT only)
  ROUTE B: GitHub Actions send_email.yml (ACTUALLY SENDS — preferred for real sends)
  ROUTE C: Python smtplib with PRI_OP_GMAIL_APP_PASSWORD
Gmail (filter creation):
  ROUTE A (preferred): Python Gmail API — sheets_token.json now has gmail.settings.basic + gmail.modify ✅ (fixed 2026-04-12)
  service = build('gmail','v1',credentials=creds); service.users().settings().filters().create(userId='me', body={...}).execute()
  SHEETS_TOKEN GitHub secret also updated — workflows can create filters too

Gmail (mcfollingproperties@gmail.com — McFolling/Airbnb inbox, added 2026-04-13):
  Local token: /Users/priscilahigashi/ClaudeWorkspace/Credentials/mcfolling_token.json
  GitHub secret: MCFOLLING_TOKEN (in priihigashi/oak-park-ai-hub)
  OAuth client: nano Project (same as sheets_token.json), test user mcfollingproperties@gmail.com added to Audience
  Scopes: drive, spreadsheets, calendar, gmail.modify, gmail.settings.basic, gmail.send
  Use for: Airbnb bookings/guest emails, maintenance tickets, Google Ads API approval email, Maya voice agent inbox context
  NOT the same as matthew@oakpark-construction.com domain-wide delegation (that's Workspace-only)
Google Ads:
  ROUTE A (preferred): Google Ads MCP server — google-ads in ~/.claude.json (read-only: list_accessible_customers, search via GAQL)
  Auth chain: OAuth (nano Project) + Developer Token (from MCC 587-071-3494) → sub-account 894-588-9168
  GitHub secrets: GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_MCC_ID
  priscila@oakpark-construction.com = sub-account admin. mcfollingproperties@gmail.com = MCC owner. No extra sharing needed.
GitHub: ~/bin/gh authenticated as priihigashi, repo priihigashi/oak-park-ai-hub ✅
Vercel: mcp__vercel__ tools ✅ (DEFERRED — load via ToolSearch; user-scope MCP at https://mcp.vercel.com, authed 2026-04-14)
  Capabilities: list_projects, list_deployments, get_deployment_build_logs, get_runtime_logs, deploy_to_vercel, check_domain_availability_and_price, search_vercel_documentation, list_teams
  Use for: OPC website deploy monitoring. Higashi site is GitHub Pages (not Vercel) unless migrated.
Instagram: Composio MCP ✅ (only option — no Google Cloud equivalent)
Canva: mcp__claude_ai_Canva__ tools ✅ (DEFERRED — load via ToolSearch)
Full details: ~/.claude/projects/-Users-priscilahigashi/memory/reference_active_connections.md

## PLAN-FIRST RULE (added 2026-05-18, from Anthropic Talks — Boris)
Before any non-trivial or irreversible work, write a 3–5 line plan FIRST and show it to Priscila.
Plan must include: (1) what I'm about to do, (2) which files/IDs/tools I'll touch, (3) what could break, (4) the success check.
Proceed without waiting only for: read-only checks, reversible formatting, single-file dry-run edits, or clearly requested execution.
NEVER skip plan-first for: production scripts, GitHub Actions, Drive writes, content rendering, spreadsheet structural changes, ad/account changes, sending emails, posting to social, schema changes.
Boris's quote: "for any non-trivial change, prompt 'before you write code, make a plan' — single biggest accuracy lever."

## BEFORE TOUCHING ANY SCRIPT
0. Read NONNEGOTIABLES.md first (~/ClaudeWorkspace/oak-park-ai-hub/NONNEGOTIABLES.md) — verify change does not break a locked rule
1. Read the full script first
2. Extract and list every spreadsheet ID, folder ID, file path, and env var referenced
3. Show what you are about to change and why BEFORE making any change
4. Never assume a variable value — verify it from the source file
→ See memory: feedback_script_investigation_rule.md
→ NONNEGOTIABLES.md updated nightly — locked rules that must never be removed

## REPORT FORMAT (every status update)
✅ Done — completed (specific)
🔴 Blocked — exact technical reason (one sentence)
⚠️ Only YOU can do — minimum items, must include: what/why/where/exact steps (3+)
Never list "next steps" — either do it or explain why it's blocked.

## SELF-SUFFICIENCY
Asking Priscila = last resort. Before asking:
- Check ~/.claude/projects/-Users-priscilahigashi/memory/ for credentials/paths
- Check ~/ClaudeWorkspace/.env and ~/ClaudeWorkspace/Credentials/
- Try an alternative tool or API
Only ask if she must physically log in or provide content that was never sent.

## LESSONS LEARNED LOOP
When a mistake is identified or a rule is established:
1. Save to memory file in ~/.claude/projects/-Users-priscilahigashi/memory/
2. Update 📋 Claude Rules tab: spreadsheet 1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU
3. Update this CLAUDE.md if it's a rule that should be global
4. The 4AM agent (pattern_learner.py) runs daily and propagates patterns to skills automatically

## SPREADSHEET HUB — source of truth for all tabs
Every spreadsheet and every tab is indexed in the Spreadsheet Hub (Marketing → Resource Hub → Spreadsheet Hub, ID `1qDbO6JQX0cKbZ9rHjiM7a4U_p7OOddZ3k3Sp30JJoqo`).
RULE: Any new spreadsheet created OR any new tab added → immediately add a row. One row per tab. Never skip this step.
Columns: SPREADSHEET | TAB | PURPOSE | LINK | SPREADSHEET ID

## KEY IDs — verified
Core: Ideas & Inbox `1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU`; Content Queue/Blog `1C1CAZ8lSgeVLSSCYIg-D9XPJcSLHyIOh1okKtvhZZQg`; Spreadsheet Hub `1qDbO6JQX0cKbZ9rHjiM7a4U_p7OOddZ3k3Sp30JJoqo`; repo `priihigashi/oak-park-ai-hub`; workspace `~/ClaudeWorkspace/`; credentials `~/ClaudeWorkspace/Credentials/`.
Service account: `oak-park-sheets@gen-lang-client-0364933181.iam.gserviceaccount.com` — already shared on core sheets. If a script gets a 403, share it using OAuth token instructions in `reference_credentials.md`; NEVER ask Priscila to do this manually.
Routing IDs: capture/carousel/reels parents live in `scripts/routing.py` and should be resolved with `capture_folder(project)` / `get_route(niche)`, not copied from memory. Current carousel production writes to `get_route(niche)["carousel_folder_id"]`; old `_TEMPLATE_CAROUSEL` anchors are legacy/template references. Step F compressed 2026-05-19.
OPC Content Creation workspace: `1um7y2Yt8zi9KGxev6kfFJYgrkMYwrCNh` (Art/Caption/Reel + Claude brief).

## HIG NEGÓCIOS IMOBILIÁRIOS — ROUTING (mom's Brazil RE site)
Any time she mentions: "Hig", "Higashi site", "mom's site", "Brazil website", "hig-negocios", "Alexandra's site" → use these locations ONLY:
- GitHub repo: priihigashi/hig-negocios-imobiliarios (NOT oak-park-ai-hub)
- Live site: https://priihigashi.github.io/hig-negocios-imobiliarios/
- Drive folder: Website — Hig Negócios Imobiliários (ID: 1CKWTojSg2uQmXjNnKlAaSBCTfxtSQBvH) inside Claude Flow (100f_O62MvH61Htv2ykjebJeDcfV_zSf0) in Higashi shared drive (0AN7aea2IZzE0Uk9PVA)
- Tracker spreadsheet: 1qJnILSR_XOgRaPdTHYy1Qx1gnSyzQTj2E04u8kErfYw (Higashi Imobiliária — Website Tracker)
- Local code: /tmp/hig-repo/ (cloned from GitHub repo)
- Design system: --sand:#f0e8d6; --gold:#9a6b2f; --dark:#1c1409; --brown:#5b3c1f / Cormorant Garamond serif + Inter
- Agent: Alexandra Higashi, Instagram @alexandrahigashi
- Domain (future): hignegociosimobiliarios.com.br
- Phase as of 2026-04-12: MAINTENANCE — all 5 pages live (index, imoveis, imovel, sobre, contato). No longer building. Now: replacing wrong images + feeding real property data when Sanity CMS is set up.
RULE: NEVER save Higashi website files to Marketing/Claude Code Workspace or oak-park-ai-hub. Always use the Higashi-specific paths above.

## FLOW PLANS TRACKER — LOG EVERY NEW FLOW DOC
Every new flow doc, master plan, process doc, how-to, or niche strategy doc → add a row to the Flow Plans Tracker — Master Index (`1fggy918FgPfnMQ-dzGQk2zx9uhi2_-uWXMKGW4MA47k`, Marketing > Claude Code Workspace). All Docs tab is the master index — every doc goes there regardless of type.
RULE: NEVER skip this step. The 4AM agent reads All Docs as its manifest; missing rows = the agent can't see the doc.
Tab guide + column schema → memory `reference_flow_plans_tracker.md`. Phase 2 H2 migration 2026-05-19.

## GITHUB SECRETS NAMING CONVENTION
All secrets in priihigashi/oak-park-ai-hub use the prefix that identifies the account:
- PRI_OP_ = Priscila / Oak Park Construction (priscila@oakpark-construction.com)
Example: PRI_OP_GMAIL_APP_PASSWORD = Gmail App Password for OPC email via SMTP
When adding a new secret, use the correct prefix — never a generic name like GMAIL_APP_PASSWORD.
Full list → reference_credentials.md

## SESSION PERMISSIONS — ASK THIS AT THE START OF EVERY CHAT

After the status report, ask exactly:

"Bypass mode?
  Y = skip all approval prompts — I execute everything without asking
  N = I ask before risky actions (default)
  S = smart — I look at what you're doing today and recommend a level
Reply Y / N / S"

→ Bypass level guide (Y/N/S recommendations + SAFE-TO-BYPASS list + DO-NOT-BYPASS list including Gmail / Instagram / destructive git ops / McFolling client data): see `/session-start` SKILL.md step 6. Step C migration 2026-05-18.

## SESSION START — see `/session-start` SKILL.md
TRIGGERS: first message of new chat, "morning", "let's start", "what's on today", "where did we leave off", after context compression. Skill steps: Calendar → Inspiration Library → Chat Logs → status report → bypass question (exact text above). Step C migration 2026-05-18.
Key Drive docs: Content_Creation_Master_Plan.docx (_Master Plans & Docs), SKILL_daily_planner.md (Agents & Skills), AI_Content_Ideas_April2026.docx (Content-Creation), Ads_Strategy.docx (root of ClaudeWorkspace)
Key spreadsheets: Ideas & Inbox 1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU (tabs: Inspiration Library, Content Queue, Scraping Targets, Clip Collections) | Content Control 1C1CAZ8lSgeVLSSCYIg-D9XPJcSLHyIOh1okKtvhZZQg
Flow Plans Tracker (all master/flow docs indexed): 1fggy918FgPfnMQ-dzGQk2zx9uhi2_-uWXMKGW4MA47k

## WHEN SHE DROPS A URL — see `/capture` skill
DEFAULT: queue to `📲 Capture Queue` tab in Ideas & Inbox (sheetId 124307869), pass `project=auto`, NO pipeline trigger unless she explicitly asks ("run capture pipeline" / "capture this now" / "run it now"). Articles, tools, GitHub links, plain text ideas → log to `📥 Inbox` tab directly. **Calendar task created ONLY when she explicitly says "remind me" / "schedule" / "follow up" / "do this later" / gives a deadline** (E1 amendment 2026-05-19). Step E1 migration 2026-05-19.

## CALENDAR — see `/calendar-create` SKILL.md
Every calendar event MUST include: source URLs, numbered action steps, tools to use, Drive links. 3-route fallback (MCP deferred-load / Composio / Python OAuth). sheets_token.json HAS calendar scope (confirmed 2026-04-12 — see Known Mistake #14). NEVER tell Priscila to add the event herself unless all 3 routes fail. Step D migration 2026-05-18.

## WHEN SHE SAYS "add a column" or "fix the spreadsheet"
Do it immediately. Confirm with cell reference. Do NOT create a task — execute now.

## CONTENT CATEGORIES — see `/content-chief` skill
3 OPC categories: (1) Talking Head/Expert — Mike <1 min, 4AM agent finds topic | (2) Project Progress/Before-After — min 4 photos or 2 for before-after only | (3) Product Tips — single image or carousel OK. **Three-step approval flow: idea → production → final → Buffer schedules.** Full per-niche details in `/content-chief` skill. Step E2 migration 2026-05-19.

## SCRAPING — see `/content-chief` skill
Scraping Targets tab = matrix of niches × targets (Oak Park, Brazil, UGC, News). Clip Collections tab = topics collecting clips, **min 8-10 clips before editing**. 4AM agent reads Scraping Targets every nightly run. Step E2 migration 2026-05-19.

## BUSINESSES
Oak Park Construction: license CBC1263425, priscila@oakpark-construction.com
McFolling Properties: Michael McFolling PM, Matthew McFolling GC
Mike has outdoor videos for HeyGen avatar. Matt has photos only for D-ID.

## STYLE
Direct, no preamble, execute first then confirm. Check Content_Creation_Master_Plan.docx before asking her to repeat anything.
ADHD: one clear next action, short responses on mobile. Done = rename calendar event to start with DONE.

## ADHD SUPPORT
When she starts a thought and connects to another idea mid-sentence — capture BOTH.
Save new idea to 📥 Inbox tab in Ideas & Inbox (1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU) immediately before continuing.
If she says "I had another idea" — ask what it was before moving on. Never let an idea get lost.

## CONTEXT FULL / NEW CHAT HANDOFF — see `/session-exit` SKILL.md STEP 3
TRIGGER (stays global so the assistant catches it): "start new chat", "context is full", "I'm gonna start a new chat", or session summary auto-generated → invoke `/session-exit` immediately. The skill creates HANDOFF_YYYY-MM-DD doc (folder 1b8Cfc8lJhu5unDaxDQIdo4xdN6X7n1nS) + chat log + Productivity & Routine update. Never leave a new chat cold. Step C migration 2026-05-18.

## SESSION EXIT LOG — see `/session-exit` SKILL.md
TRIGGER (stays global): "exit", "closing", "done for today", "bye", "I'm closing", "see you later". Skill runs 3 steps in order: (1) chat log to Drive Chat Logs folder (1qitnbz5_8tfZI2rnTogV1zLLLLOwFVCw), (2) Productivity & Routine update (doc 1wVBuNOuOufT8WP4KCrrlVbKWRmQZjKvqmia1soUEBZE — source of truth for in-progress across all projects), (3) handoff if context near limit. All 3 routes (Composio / OAuth Docs API / plain text upload) covered. Never give up — try all 3 before saying blocked. Keep 7 days, delete older. Step C migration 2026-05-18.

## TASKS STAY IN FLOW UNTIL DONE
A task is only removed from the pending list when it is confirmed complete with evidence (cell ref, file path, run success). Never mark done by assumption.

## BEFORE WRITING "ONLY YOU CAN DO"
Check these in order — if any apply, DO IT YOURSELF instead:
1. YouTube URL → run `youtube-transcript-api` (installed) — instant transcript, no download
2. Instagram/TikTok URL → run `/capture` skill with yt-dlp + Whisper
3. Any tool/connection question → check reference_active_connections.md first
4. Spreadsheet access → check reference_credentials.md, share SA automatically if 403
"Only YOU can do" = physical login OR content that was never provided. Nothing else.

## DRIVE — SHARED DRIVE IS DEFAULT, NEVER MY DRIVE

ROUTING BY TOPIC — each topic has its own shared drive (source of truth) + a shortcut in a working cross-ref folder:

| Topic | Source-of-truth drive | Drive ID | Shortcut goes to |
|---|---|---|---|
| Higashi / Hig Negócios / mom's site / Alexandra | Higashi Imobiliária - Claude | 0AN7aea2IZzE0Uk9PVA | Website folder 1CKWTojSg2uQmXjNnKlAaSBCTfxtSQBvH |
| OPC / Oak Park Construction | Oak Park Construction | 0AJp3Phs0wIBOUk9PVA | TBD |
| News (Brazil/USA news niche) | News | 0AH7_C87G0ZwgUk9PVA | TBD |
| Stocks / investing / Robinhood | Stocks | 0AF6S_f8PH2_aUk9PVA | Originals - Stock (1JFndBkUh6Bac6MD7JKgIns2xgO188b1T) in Marketing |
| Content / marketing / McFolling / general | Marketing | 0AIPzwsJD_qqzUk9PVA | n/a (self) |
| AI Content / AI-generated assets / auto-captured content | AI Content | 0ACJVarTjgmFUUk9PVA | TBD (added 2026-04-14) |
| UGC / user-generated content / creator clips | UGC | 0AEz0NlGr3tlLUk9PVA | TBD (added 2026-04-14) |

RULE — TOPIC DRIVE + SHORTCUT (added + tested 2026-04-14):
- The **file lives in the topic's shared drive** = single source of truth
- A **shortcut** is placed in the working cross-ref folder for easy daily access
- When Priscila mentions a topic (stocks, news, OPC, Higashi, content), route there — never mix topics
- NEVER upload to My Drive as the final destination. My Drive = transient staging only (e.g. phone uploads before routing).

Automation for phone uploads: `drive_route_file.yml` workflow in priihigashi/oak-park-ai-hub. Inputs: filename + topic → moves from My Drive to topic drive + creates shortcut. Triggered via `gh workflow run drive_route_file.yml -f filename=... -f topic=...` or from github.com/Actions UI on phone browser.

### ⛔ DRIVE UPLOAD — BANNED METHODS (always creates empty files / fails silently)

These methods are **banned** for uploading file bytes. They "succeed" but the file ends up empty. Every chat that has struggled with Drive uploads has been reaching for these:

1. ❌ `GOOGLEDRIVE_CREATE_FILE` with `content=...` (Composio) — silently creates an empty file
2. ❌ `mcp__claude_ai_Google_Drive__create_file` with `content=...` — same bug, silently creates empty file
3. ❌ Any MCP `create_file` variant with file content embedded — there is no MCP tool that correctly uploads binary content

MCP `create_file` is ONLY for: empty folders (`mimeType: application/vnd.google-apps.folder`) or empty Google Docs to be filled separately via GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN. Never for file content.

### ✅ DRIVE UPLOAD — CORRECT METHOD (the only one that works)

**OAuth Python + googleapiclient + `supportsAllDrives=True` + SHARED drive folder ID.**

Works from Claude Code (Bash tool) and from phone/web Claude (via `proxy_execute` / remote Python). Same pattern, same result.

→ See `~/.agents/skills/drive-upload/SKILL.md` for the Python implementation (3 routes, all anti-bug rules, verification step). Step B migration 2026-05-18.

Non-negotiable rules (apply to EVERY Drive call — create, list, update, delete):
- `supportsAllDrives=True` on every call. Missing = 404 on shared drives.
- `includeItemsFromAllDrives=True` on `files().list` when searching shared drives.
- Use a SHARED DRIVE folder ID, never a My Drive folder ID (OAuth + My Drive folder = file silently lands in My Drive).
- Files >5MB: use resumable upload → `POST /upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true`.
- After upload, VERIFY the file appears in the correct shared drive path before reporting done.

Tool rules for Drive (quick summary):
- CREATE folders → `mcp__claude_ai_Google_Drive__create_file` (mimeType: folder) ✅
- WRITE content to a Google Doc → `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN` via Composio ✅
- UPLOAD binary files (PNG, PDF, MP4, etc.) → OAuth Python googleapiclient as shown above ✅
- Anything else with MCP `create_file` + `content=` → ❌ BANNED

Full skill: `~/.agents/skills/drive-upload/SKILL.md`

## EMAIL SENDING — see `/email-send` SKILL.md
Gmail MCP = DRAFT only (no send tool exists). For actual delivery: GitHub Actions `send_email.yml` (Route B, preferred — uses PRI_OP_GMAIL_APP_PASSWORD) or SMTP fallback (Route C). DEFERRED TOOL RULE: load Gmail MCP schema via ToolSearch before calling — they are deferred, not absent. McFolling inbox has separate token (MCFOLLING_TOKEN). Step D migration 2026-05-18.

## DRIVE SEARCH — FALLBACK ORDER (added 2026-04-12 — prevents MCP error -32603 from blocking work)
Always try all 3 routes before blocked: A `mcp__claude_ai_Google_Drive__search_files` → B `mcp__gdrive__search` (skip immediately on `-32603`; server failure, not query formatting) → C OAuth Python/curl with `supportsAllDrives=true&includeItemsFromAllDrives=true`.
Doc writes: use `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN`, NEVER markdown tables, and read existing Docs first because this tool overwrites the whole document. Full Drive search + Doc creation flow lives in memory: `feedback_drive_oauth_vs_mcp.md`. Phase 2 O migration 2026-05-19.

## NAMED-PERSON → FACE RULE, NON-NEGOTIABLE (added 2026-04-17)

When content names a person (politician, business owner, accused, witness, victim, worker), their face MUST appear on that slide/frame. No exceptions.

Pre-render checklist (run before exporting PNGs):
1. Scan the HTML/script for every `<strong>FirstName LastName</strong>` or named subject in body copy
2. For each named person, verify one of these exists on the same slide:
   - a `.sticker-slot` with real photo (cover / hero slide — primary subject), OR
   - a `.bio-card` with 3×4 `.bio-photo` (multi-person slide — 110×130px minimum), OR
   - a `.bio-initials` fallback card (same size, 2-letter initials) — ONLY when no licensed photo exists
3. If a name has NO face treatment → STOP. Source the photo (Wikimedia Commons CC, Agência Brasil CC BY 3.0, editorial fair-use) OR add initials card. Never render without.

CSS reference — reuse these classes across carousels (locked from EP001 Rachadinha V2):
`.bio-grid` (2-col grid) · `.bio-card` · `.bio-photo` · `.bio-initials` · `.bio-name` · `.bio-role` · `.bio-fact`
Template: `Carousel/Brazil/Quem-Decidiu-Isso/_TEMPLATE_CAROUSEL/v2_rachadinha/cover.html`

Source of directive: `~/.claude/projects/-Users-priscilahigashi/memory/project_visual_sticker_system.md`
Quote: *"every time we're talking about someone I would like an image so people know their face and this is mandatory. I want this for all of the brands. This is mine."*

## CAROUSEL OUTPUT ROUTING — see `/template-carousel` SKILL.md
**CURRENT canonical render/write destination (confirmed 2026-05-19):** `scripts/content_creator/main.py` reads `routing.py::get_route(niche)["carousel_folder_id"]` at runtime. Write shape: `<carousel_folder_id>/v<N>_<slug>/{cover.html, png/, motion/, resources/, story doc}`. Per main.py line 47: *"No more `_TEMPLATE_CAROUSEL` middle folder. No more `<series>/` middle folder."* — old `_TEMPLATE_CAROUSEL` anchor list is LEGACY (template/series-metadata references, kept in skill for archaeology + Remotion / Content/Series/ workflows).

**Current `carousel_folder_id` per niche** (resolve at runtime via routing.py, do NOT hardcode):
- OPC → `16P2JN74JAAW3HKnmNqPGPrAq7N5jDNii` (Marketing/Content/carousel)
- Brazil → `1gDOjtW_X-_jWtu94pffbDaUsw6VGCKuA` (News/Brazil/Carousel)
- USA → `1lRfZE5XC_gL57pUiiWu0Lhar9wfyCtFw` (News/USA/Carousel)

**Anti-bug rules (stay global):**
- Version `<slug>` = topic slug only, no date/post_id prefix. Auto-increment v1→v2 on re-build, NEVER overwrite.
- `png/` + `motion/` + `resources/` + story doc all live INSIDE `v<N>_<slug>/` (NEW shape — no longer siblings outside).
- **NEVER save PNG/MP4/GIF to local computer as final destination.** `/tmp` is ephemeral; Drive is source of truth.

## MOTION IS DEFAULT ON — see `/template-carousel` SKILL.md
RULE (stays global, non-negotiable): every carousel build ships BOTH static PNGs AND motion (MP4 + GIF + preview frame + non-cover PNGs duplicated). Motion = default ON. Off ONLY when Priscila explicitly says "static only" for that specific post. Applies to scripts, email preview, manual chat, any content-producing skill. Pre-ship audit: if `motion/` is empty → build incomplete, do NOT email preview. Source: Priscila 2026-04-17 *"we always create a motion one as well unless I say to you to not do it."* Memory: `feedback_both_versions_always.md`. Step E3 migration 2026-05-19.

## VISUAL-EVERY-OTHER-SLIDE — see `/content-chief` skill
RULE (anti-bug, stays global): carousels must NEVER ship with 3+ consecutive text-only slides between cover and sources. At least every-other middle slide carries a visual anchor. `carousel_builder.py` emits `visual_hint` per slide (`bio-card` / `product-photo` / `context-image` / `icon-row` / `none`); never ship with `none` on >1 consecutive slide. Per-niche visual catalog in skill. Memory: `feedback_visual_every_other_slide.md`. Step E2 migration 2026-05-19.

## HTML → IMAGE — see `/html-to-image` SKILL.md
TRIGGER: "turn this HTML into image", "convert to png", "export slides", "save the carousel", "approve this design + render". RULE (anti-bug, stays global): html→image = DETERMINISTIC via Playwright (`/html-to-image` skill, `export_slides.js`). NEVER substitute with text-to-image AI (OpenAI, Ideogram, Recraft, Seedream, Canva AI, Nano Banana) — they hallucinate the design, text drifts, layouts drift. Remotion is sibling deterministic path for React-source templates. Default Drive destination: Marketing > Image Creation > html to image (folder 1tE-2Ps8V8ZKQ4etyvzk47ZWyzeHAD2nk). Step E4 migration 2026-05-19.

## CONTENT FORMATS — living registry of approved post formats
**File (authoritative):** `~/ClaudeWorkspace/_Master Plans & Docs/CONTENT_FORMATS.md` | **Drive Doc:** `1XqXSyJC_iHMTrmMxpM5ZR7S-WQxz19HhDJO1HomdncM`
**RULE (stays global):** READ this file before producing any content (carousel, reel, hooks, copy). WRITE to it whenever Priscila names a new format — same session. NEVER produce content without checking if a format already exists for that niche. `/capture` checks on every video ingest and flags format matches in the Inbox row. Trigger phrases: "format", "same style", "like the X one", "series", "split screen". Full per-format detail (FORMAT-001+) in `/content-chief` skill + the registry file. Step E2 migration 2026-05-19.

## PER-POST EDITORIAL LOG — see `/content-chief` skill
RULE (stays global, applies to ALL content-producing skills): every series episode or standalone post gets a dedicated Google Doc editorial log. **4 sub-rules:** CREATE on new post (`EP001 — [Title] — Editorial Log`) · APPEND dated NOTE on every feedback · READ before touching any post · INBOX row for any research task generated. Example: EP001 Rachadinha doc `1SgVAxHCARMuFcd3xvAJs0fsBwGU9wS3ZdlcC6QgtHcU`. Step E2 migration 2026-05-19.

## CAPTURE — AUTO-DETECT — see `/capture` skill
RULE (anti-bug, stays global): chat NEVER picks the project — always pass `project=auto`. Runner uses 3-tier classify (notes-keyword → Claude Haiku → unrouted at conf <0.70). **Default fallback is NEVER `book` and NEVER `opc` — it is `unrouted`.** See `scripts/routing.py::get_route()` + `scripts/capture/capture_pipeline.py::detect_project()`. Step E1 migration 2026-05-19.

## CAPTURE — CONTENT IDEA GENERATION — see `/capture` skill
RULE (stays global, fires on every video capture): every /capture of a video MUST auto-produce content ideas from TOPICS (even if the clip is not used). Minimum: 1 carousel + 1 reel + 2-3 topic breakdowns. NEVER use the captured person's clip unless Priscila explicitly says to (topics = raw material, posts = original). Every topic idea = "explain one thing, explain it simply". Step E1 migration 2026-05-19.

## 4AM AGENT — see `/4am-agent` skill
Runs nightly 4AM ET (8:00 UTC) via GitHub Actions on `priihigashi/oak-park-ai-hub`. 3-tier cost gate (Sheets → Drive → Haiku LLM only when needed) keeps 90%+ of nights at zero LLM tokens. Reads Flow Plans Tracker `All Docs` tab (1fggy918FgPfnMQ-dzGQk2zx9uhi2_-uWXMKGW4MA47k) as agent manifest. State files in `.github/agent_state/`. **RULE (stays global): when you create a new flow/master/process doc, SHARE it with `oak-park-sheets@gen-lang-client-0364933181.iam.gserviceaccount.com` or the agent silently skips it (403 on read).** Step E5 migration 2026-05-19.

## AIOX AGENT AUDIT — REQUIRED BEFORE AUTOMATION IS "DONE"
New automations (GitHub Actions workflows, Python scripts, integrations, routing logic) are NOT done until audited by `/AIOX-architect` → `/AIOX-devops` → `/AIOX-dev` in that order. Fix any flag before marking done.
Skip only for minor edits (typo fixes, copy changes, formatting). Phase 2 H6 migration 2026-05-19.

## CLAUDE.MD DRIVE MIRROR — see `/4am-agent` skill
Read-only nightly mirror at Marketing > Claude Code Workspace > _Master Plans & Docs > `CLAUDE_MD_MIRROR`. Local file is authoritative — NEVER edit from Drive (next nightly push overwrites). Use mirror for phone access. Full detail (folder, doc-ID storage, failure modes) in `/4am-agent` skill. Phase 2 H7 migration 2026-05-19.

## SCRIPT / CODE EDITING RULE — NON-NEGOTIABLE
Never rewrite a working script from scratch. Only change what is strictly necessary.
Before any edit: read the full file, list what you're changing and why.
Good things already in the script must be preserved. When in doubt — don't touch it.

## CODE FIX AUDIT — NON-NEGOTIABLE (added 2026-05-05)
Before committing ANY fix to validation, checking, or reviewer logic, run this checklist:
1. Trace BOTH execution paths — local build path (check_built_post / CONTENT_CREATOR_RUN) AND Drive/manual path (check_drive_folder / REVIEW_DRIVE_FOLDERS). Fix must fire on both, or explicitly document why one is exempt.
2. Every issue detected must also be auto-fixed (when FIX_MODE=analyze_and_fix) — not just reported. Trace the issue token all the way to auto_fix_drive_folder().
3. Every dependency (Pillow, API key, folder path, env var) must have a warning or fallback — never silently skip.
4. If the fix touches a path assumption (folder name, subfolder structure), add a fallback for legacy/edge layouts.
Skipping this checklist = the next audit will find the same gaps. Discovered 2026-05-05 after missing all 4 on carousel_reviewer.py image validation.

## SKILLS & AGENTS DIRECTORY
Full index of skills (/command) and agents (@name) lives in Drive Map — ALL DRIVES `10qxtM_s22Z9HNVXsnBJa1WjTYCsraPa8O2uI0VEa1Zo`, tab `🤖 Skills & Agents` (`sheetId=806704177`). Columns: CATEGORY | SUB-CATEGORY | TYPE | COMMAND | DESCRIPTION | GOOD FOR.
RULE: Before starting a task, check this tab; a specialized skill/agent may already exist. When she says "do we have a skill for X" → check this tab first before saying no. 4AM agent invokes `/content-chief` (Vera) for Talking Head script generation. Step F compressed 2026-05-19.

## AI ANALYSIS — EVIDENCE-DRIVEN RULE (global, added 2026-04-29)
Applies to ads dashboards, weekly reports, keyword alerts, content insights — any surface where Claude outputs analysis or a recommendation.
RULE (stays global): Investigate first. Surface only concrete findings (name + date + number, 1–2 max). Generic possibilities are an internal checklist — NEVER print them to Priscila.
14-day Smart Bidding rule: a recent change (≤14 days old) → Wait. Reverting destroys the signal. Re-evaluate at +14d.
Banned phrases: "Could be seasonal", "Maybe a competitor change", "Tracking changes…", any (a)(b)(c) list of possibilities, "Open the table below and look for X".
4-step flow + data sources + reference implementation (OPC ads dashboard `investigateMOM()`) → memory `feedback_evidence_driven_ai_insights.md`. Phase 2 K migration 2026-05-19.

## KNOWN REPEAT MISTAKES — read and prevent
Full lessons live in `~/.claude/projects/-Users-priscilahigashi/memory/` plus `NONNEGOTIABLES.md`. Keep these global anti-bug reminders visible:
1. Never say "I may not have access" before checking `reference_active_connections.md`.
2. Do completed tasks now; do not list them as "next steps."
3. "Only YOU can do" must include why / where / what / exact steps.
4. Explain error codes in plain language.
5. Before editing scripts, read the full file and list every ID/path/env var.
6. Never guess a GitHub secret name or which spreadsheet it maps to; run `~/bin/gh secret list --repo priihigashi/oak-park-ai-hub` and document confirmed mappings in `reference_credentials.md`.
7. Drive uploads/searches: shared-drive folder ID + `supportsAllDrives=true`; list/search also needs `includeItemsFromAllDrives=true`; verify final shared-drive path before reporting upload done.
8. `mcp__gdrive__search` `-32603` is server-side; switch routes immediately and try OAuth before reporting blocked.
9. Deferred Gmail/Calendar/Drive/Canva/Vercel MCP tools are not absent; load schema via ToolSearch first.
10. Gmail MCP drafts only. To send, use `send_email.yml` or SMTP fallback with `PRI_OP_GMAIL_APP_PASSWORD`.
11. Never use markdown tables in `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN`; use plain text labels.
12. Never write to an existing Google Doc before reading it first; that tool overwrites the whole doc.
13. GitHub Actions green check is not proof; inspect logs for `failed|error|401|403|skipped|unauthorized|exception` and check `🚨 Pipeline Failures`.
Step F compressed 2026-05-19; no anti-bug reminders intentionally removed.

## PIPELINE FAILURE LOG — 🚨 Pipeline Failures tab (added 2026-04-27)
Every pipeline writes silent + loud failures to ONE place: `Ideas & Inbox` → `🚨 Pipeline Failures` tab (sheetId 448272280).
Columns: TIMESTAMP_UTC | WORKFLOW | RUN_ID | STAGE | ERROR | RUN_URL | RESOLVED | NOTE
- Every workflow that catches an exception MUST also call a `log_pipeline_failure(stage, error, sheet)` helper that appends a row.
- Workflow YML MUST emit `if: failure()` SMTP alert to priscila@oakpark-construction.com via PRI_OP_GMAIL_APP_PASSWORD.
- Script MUST exit non-zero when any failure was recorded → GitHub run flips ❌ → email fires.
- Session-start: scan `🚨 Pipeline Failures` for unresolved rows (RESOLVED column blank) and report them as part of the status report.
- First implementation: `scripts/youtube_research.py` + `.github/workflows/video-research.yml` (commit d7c1bbb).
- Wire this into every other pipeline: capture_pipeline.yml, content_creator.yml, ads_pulse.yml, drive_route_file.yml, etc. — same helper, same tab.
