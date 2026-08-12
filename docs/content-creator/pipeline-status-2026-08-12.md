# OPC Content Pipeline — Status Update
Daily Advancer — 2026-08-12

Companion to: docs/content-creator/pipeline-restart-decision-2026-08-02.md

---

## Current status (2026-08-12): STILL PAUSED

The OPC content pipeline cron remains disabled. Confirmed by reading
.github/workflows/content_creator.yml — the schedule block is still commented out:

  # schedule:  # PAUSED 2026-06-26 (Priscila) — no autonomous creation;
  #   manual-only until content creator rebuilt for story-flow quality

The pipeline has been paused for 47 days (since 2026-06-26).
The Aug 2 restart brief laid out all prerequisites — they are still met:
  - carousel_reviewer.py: all 4 Phase 1 gaps fixed
  - classifier.py: Phase 1 spec implemented
  - 14+ approved OPC posts in Content Queue
  - Freshened captions through Week 3 (Aug 2 session)

---

## What's been done since the Aug 2 brief

Week 1 captions: ready (opc-week1-fresh-captions-2026-07-29.md)
Week 2-3 captions: ready (opc-week2-week3-fresh-captions-2026-08-02.md)
Content Creator V2: Sprint 3 complete (steps 1-4); Sprint 4 spec now written
                    (content-creator-v2-sprint4-brief-2026-08-12.md)
Captions for weeks 4+: not yet written (next advancer session)

---

## The one thing still needed from Priscila

The Aug 2 brief said: "Everything needed to restart is now ready. This doc gives
Priscila one place to say yes."

That is still true on Aug 12. Nothing has changed on the pipeline side.

To restart:
  Step 1 — Run a manual dry-run:
    GitHub → priihigashi/oak-park-ai-hub → Actions → content_creator.yml → Run workflow
  Step 2 — Review 3 renders visually (check Drive for html/ and png/ files)
  Step 3 — Re-enable cron (uncomment the schedule block in content_creator.yml)

Recommended first post to use for the dry-run:
  Any post in Ideas & Inbox → Content Queue with status = approved and niche = OPC.
  Concrete suggestion: start with a bathroom or drywall post (types that generated the
  most views historically, per approved-queue-brief-2026-07-27.md).

---

## OPC Ads report — overdue refresh

The OPC Ads Report July 2026 doc (ID: 17D2tEJfZx_pLGz7DFKiSueHxr1wt0OkTz_rzLUeuweQ)
noted: "refresh after Aug 1." Today is Aug 12 — the August refresh is 11 days overdue.

The ads_pulse.yml workflow runs every Monday at 8 AM ET. The script (ads_dashboard.py)
writes to docs/dashboard/index.html and docs/dashboard/dark.html. To get an August
snapshot, run ads_pulse.yml manually from GitHub Actions.

This is NOT blocked — just unscheduled. Low effort.

---

## What is still NOT ready

Content automation crons: content_creator, build-carousels, blog-generator,
  daily-content-processor, 4am_agent auto-retry — all still PAUSED.
  (Do not re-enable without the dry-run passing first — per Aug 2 brief.)

Brazil pipeline: still on hold pending Priscila's decision on Cuba EP.1 and
  Wealth/Power topic (from Aug 2 brief, no update since).

WordPress blog publish: independent issue; do not block OPC tip restart on this.

---

## Recommended Priscila actions this week (ranked)

1. Run content_creator.yml manual dry-run (30 min, unblocks 47 days of paused pipeline)
2. Trigger ads_pulse.yml manually (5 min, gets August ads snapshot)
3. Decide Cuba EP.1 + Wealth/Power topic for Brazil pipeline (gates the Brazil content restart)
