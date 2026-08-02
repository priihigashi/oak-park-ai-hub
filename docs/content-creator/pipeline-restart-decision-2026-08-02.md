# OPC Content Pipeline — Restart Decision Brief
Daily Advancer — 2026-08-02

Everything needed to restart is now ready. This doc gives Priscila one place to say yes.

---

## The one decision needed: restart the OPC cron

The pipeline has been paused since 2026-06-26. All prerequisites are met. The only thing missing
is Priscila confirming she wants it back on.

To restart, Priscila (or a Claude session) runs:
  GitHub → priihigashi/oak-park-ai-hub → Actions → content_creator.yml → Run workflow
  OR re-enable the cron schedule in .github/workflows/content_creator.yml (remove the # comment
  on the schedule: block) and merge to main.

Before re-enabling the cron, run one manual dry-run first (step below).

---

## What's verified ready (no further build work needed)

Carousel reviewer — Phase 1 gaps: ALL 4 FIXED (audit 2026-07-29)
  carousel_reviewer.py handles both local + Drive paths, auto-fix wiring, Pillow fallback,
  legacy subfolder fallback.

Classifier: classifier.py exists and implements Phase 1 Task 2 spec
  (confidence gate, format registry, manual-review fallback, DRAFT format guard).

OPC tip posts approved and ready: 14+ posts in Content Queue (approved, not yet published)
  Full list: Ideas & Inbox spreadsheet → Content Queue tab → status = approved, niche = OPC.
  Week 1 freshened captions ready: opc-week1-fresh-captions-2026-07-29.md
  Week 2-3 freshened captions ready: opc-week2-week3-fresh-captions-2026-08-02.md (this session)

Carousel briefs written for 9720 SW 92nd Ter:
  Carousel A: New Construction v6 (10 photos, ready to build)
  Carousel B: Concrete Work v1 — new post type, 8 photos, ready to build (build this one first)
  Full brief: docs/content-creator/9720-sw-92nd-carousel-brief-2026-07-29.md
  NOTE: Both are blocked on pipeline restart + manual build session (photos must be supplied by
  Priscila; Claude cannot access local Drive originals in remote execution).

OPC Design System doc: docs/OPC_DESIGN_SYSTEM.md — complete as of 2026-07-16.

---

## Recommended restart sequence (3 steps)

Step 1 — Manual dry-run (one session, ~30 min):
  Run content_creator.yml manually with a single OPC tip post from the approved queue.
  Verify: Drive folder created, slides rendered, email preview fires, no Pipeline Failures tab errors.
  This is Action 2 from rebuild-phase-decision-2026-07-09.md.

Step 2 — Review 3 renders visually:
  Open the html/ and png/ files in Drive for the dry-run post.
  Check per pre-publish checklist: no placeholders, correct colors, footer has CBC1263425.
  If clean → approve. If issues → fix before re-enabling cron.

Step 3 — Re-enable cron:
  After dry-run passes, uncomment the schedule in content_creator.yml and merge.
  Pipeline will run on its normal cadence again.

---

## What Priscila needs to decide (the short list)

1. Restart the OPC pipeline? (yes / not yet — if yes, run the dry-run above)
2. Cuba EP.1 (Brazil niche): include when Brazil pipeline resumes? (yes / no / later)
3. Wealth/Power deck (Phase 2): pick the first Brazil topic from Content Queue.
   The deck format is fully specced in rebuild-phase-decision-2026-07-09.md Phase 2 section.
   A Claude session can build the HTML template once Priscila gives the go.

---

## What is NOT ready yet (so Claude doesn't accidentally push it)

Content automation crons: still PAUSED (content_creator, build-carousels, blog-generator,
  daily-content-processor, 4am_agent auto-retry). Do NOT re-enable without the dry-run passing.

WordPress blog publish: broken (returns HTML not JSON). Independent side fix — do not block
  the OPC tip restart on this.

Buffer auto-schedule: do NOT use Buffer until Priscila has reviewed at least 3 renders from
  the approved queue post-restart (per approved-queue-brief-2026-07-27.md).

Brazil pipeline: keep paused until Priscila confirms Cuba EP.1 and Wealth/Power topic.

---

## Links

Approved queue brief: docs/content-creator/approved-queue-brief-2026-07-27.md
Carousel reviewer audit: docs/content-creator/carousel-reviewer-gap-audit-2026-07-29.md
Phase 1 action brief: docs/content-creator/phase1-action-brief-2026-07-20.md
Rebuild phase decision: docs/content-creator/rebuild-phase-decision-2026-07-09.md
9720 SW 92nd briefs: docs/content-creator/9720-sw-92nd-carousel-brief-2026-07-29.md
Week 1 captions: docs/content-creator/opc-week1-fresh-captions-2026-07-29.md
Week 2-3 captions: docs/content-creator/opc-week2-week3-fresh-captions-2026-08-02.md
OPC Design System: docs/OPC_DESIGN_SYSTEM.md
Content Queue: Ideas & Inbox spreadsheet (1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU)
