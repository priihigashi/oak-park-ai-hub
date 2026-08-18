# Pipeline Registry — Single Source of Truth
# oak-park-ai-hub · updated 2026-08-18
# Every template, format, and pipeline stage is listed here.
# Before adding a new template or format: add a row here first.
# Before running the pipeline: verify the template key matches an ACTIVE row.

---

## INSPIRATION REFERENCE GOVERNANCE — 2026-08-18

Canonical searchable reference index:
- Spreadsheet: **Ideas & Inbox** `1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU`
- Tab: **📥 Inspiration Library** (sheetId `1694604172`)

Processing intake:
- **📲 Capture Queue** (sheetId `124307869`)

These are complementary:
- Capture Queue = work needing media processing, transcription, frame/audio/duration/creator verification.
- Inspiration Library = durable searchable index of references Priscila intentionally wants available for reuse.
- A reference may be present in both. Never force a template/design/audio reference into only the processing queue.

When the user identifies a URL as template/design/visual/font/typography/sound/audio/caption/motion/editing inspiration, upsert the normalized URL into Inspiration Library immediately. Preserve the user's raw reason for liking it. If analysis is still needed, also queue capture work; when processing finishes, enrich the same Inspiration Library row rather than appending a duplicate.

Reusable-reference fields:
`Visual Template?`, `Font / Typography?`, `Sound / Audio?`, `Caption Style?`, `Motion / Editing?`, `Duration Bucket`, `Exact Duration (sec)`, `Best Placement`, `Style Tags`, `Template Scope`, `Reference Status`, `Track Creator / Account?`.

The five inspiration-type fields are independent Yes/No/Unknown values. Do not guess exact duration, creator/account, font name or audio title when inaccessible.

Reference lifecycle:
`Link only` → `Needs frame capture` → `Frames captured` → `Analyzed` → `Template built`.

Drive stores screenshots, extracted frames, transcripts/audio references and built template assets. Inspiration Library is the index future content/template agents search before creating a new treatment.

---

## ACTIVE TEMPLATES

| template_key | niche | function | format_id | scenario | status |
|---|---|---|---|---|---|
| tip | opc | _build_opc_html | FORMAT-010 | Tip of the Week — 5-slide how-to with stat + list + tip | ACTIVE |
| progress | opc | _build_opc_progress_html | FORMAT-011 | Before/After project progress — 4-6 photos + captions | ACTIVE |
| illustrated | opc | _build_opc_illustrated_html | FORMAT-012 | Illustrated explainer — icon panels + copy | ACTIVE |
| cutout | opc | _build_opc_cutout_html | FORMAT-014 | Cutout/sticker style — floating person + background | ACTIVE |
| quem-decidiu | brazil | _build_brazil_html | FORMAT-002 | Quem Decidiu Isso? — political breakdown carousel | ACTIVE |
| verificamos | brazil | _build_news_shared_template_html | FORMAT-013A | Fact-check carousel — original claim + source overlay | ACTIVE |
| a-conta | brazil | _build_news_shared_template_html | FORMAT-013B | Expert debunk / institutional source carousel | ACTIVE |
| dados-ou-agenda | brazil | generate_dados_content | FORMAT-019 | Influencer/public figure bias check — REQUIRES /capture brief | ACTIVE |
| fact-checked | usa | _build_news_shared_template_html | FORMAT-001 | Split Screen + Sources — USA news fact-check | ACTIVE |
| the-chain | usa | _build_news_shared_template_html | FORMAT-016 | Bilingual carousel — same builder as Brazil | ACTIVE |
| who-is | brazil | _build_who_is_html | FORMAT-020 | Who Is This Person? — profile carousel for any public figure (politician, rabbi, influencer). Cover: hook + sticker + air-quote + CTA. Slides: bio grid, quote, law, money/PAC, network, controversy. | ACTIVE |
| the-case | brazil | _build_the_case_html | FORMAT-021 | O Caso / The Case — topic/case-centric investigation carousel. The CASE is the subject; a key person appears as context. Cover: case title + status pill + person attribution + hook. Slides: timeline, responsible party, person background, network, money trail. | ACTIVE |

---

## TEMPLATE RULES

1. dados-ou-agenda (FORMAT-019): NEVER build without a /capture brief.
   If capture_brief is None or empty → skip, log SKIP: no capture brief found.

2. Every template must emit: caption (150-200 chars) + hashtags + slide_texts.
   generate_caption() is called automatically in main.py after Drive upload.

3. Every template must have motion = ON by default.
   motion/ subfolder with MP4 + GIF + preview_frame.jpg is mandatory.

4. Named person on any slide → face required (bio-card or sticker-slot).
   No face = reviewer flags HIGH.

5. Before inventing a new visual/editing treatment, search 📥 Inspiration Library for relevant saved references. A saved reference does not become a new FORMAT unless it is analyzed and genuinely reusable as a production structure.

---

## POST-READY CHECKLIST (reviewer enforces all)

A carousel is POST-READY only when:
- [ ] Stat slide text fully visible (no clipping)
- [ ] SWIPE indicator does not overlap any text
- [ ] @HANDLE_PLACEHOLDER not in any rendered HTML
- [ ] All context-image slots have real images (not [ IMG: ... ] placeholder)
- [ ] caption.txt exists in version folder
- [ ] Motion folder has at least 1 MP4 over 500KB
- [ ] Reviewer passes ALL checks (0 issues)

---

## PIPELINE STAGE MAP

stage 0 — inspiration/reference intake
  /capture or the active content agent detects user-stated template/design/font/sound/caption/motion inspiration
  Normalize/dedupe source URL → upsert 📥 Inspiration Library immediately
  If screenshots/transcript/audio/duration/creator analysis is needed → also add/keep 📲 Capture Queue

stage 1 — topic_picker.py
  Reads Inspiration Library + Content Queue
  Clips gate: if clips_needed=true AND Clip Collections count < 8 → skip, trigger video-research.yml
  Output: list of topic dicts with niche, template_key, brief

stage 2 — carousel_builder.py
  generate_carousel_content() → routes to correct template function
  fetch_all_media() → images (catalog → Gemini → Seedream → Replicate → DALL-E → Pexels → Pixabay)
  fetch_clips() → Motion v2 clips (clip collections / YouTube / Instagram / Archive / Wikimedia → GIPHY → static PNG/no motion)
  resources/clips/clips.json bridge → STAGED/APPROVED target_slide clips from resource_downloader override fetch_clips() for covered slides; missing local clips are downloaded from Drive by drive_file_id before render
  build_html() → renders HTML
  render_pngs() → Playwright → PNG files
  build_motion_html() + record_motion.js → MP4 + GIF
  generate_caption() → caption.txt

stage 3 — carousel_reviewer.py
  check_built_post() — runs all checks, returns {passed, issues}
  If any issue → post marked needs_revision, alert email sent, NOT forwarded to approval

stage 4 — main.py upload
  Upload png/ + motion/ + resources/ + caption.txt to Drive version folder
  Create story Google Doc in Drive
  write_inspo_status() — update Inspiration Library row
  If an inspiration reference produced a durable reusable implementation, link the output back to the same row and advance Reference Status only to the achieved state

stage 5 — email_preview.py
  Send preview email with Drive link + thumbnail + caption
  Priscila replies "approved" → approval_handler.py picks up → schedules to Buffer

---

## LEGACY / RETIRED (do not use)

None identified yet. Add here when a template is retired.

---

## ADDING A NEW TEMPLATE

1. Search 📥 Inspiration Library and existing template assets first; reuse/extend when appropriate.
2. Add a row to ACTIVE TEMPLATES above.
3. Add the builder function to carousel_builder.py.
4. Add routing to generate_carousel_content() and build_html().
5. Add reviewer checks if the template has unique structural rules.
6. Add a row to the Templates Registry tab in Spreadsheet Hub (1qDbO6JQX0cKbZ9rHjiM7a4U_p7OOddZ3k3Sp30JJoqo).
7. Test with a manual run before enabling in the daily pipeline.
8. If the template came from a saved Inspiration Library reference, link the durable implementation back to that row and set `Reference Status = Template built` only after the implementation exists.
