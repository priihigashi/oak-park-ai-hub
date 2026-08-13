#!/usr/bin/env python3
"""Run the dedicated Food App recipe ingestion pipeline."""

from __future__ import annotations

import json
import sys

import food_app_recipe_core as core


def main() -> int:
    gc = core.cp.get_sheets_client()
    if not gc:
        raise RuntimeError("Google Sheets authentication unavailable")

    queue_ws = gc.open_by_key(core.IDEAS_INBOX_ID).worksheet(core.QUEUE_TAB)
    ingest_ws = core.ensure_ingest_sheet(gc)
    candidates = core.collect_candidates(queue_ws)
    summary = {
        "started_at": core.now_iso(),
        "candidate_count": len(candidates),
        "success": [],
        "failed": [],
    }
    print(f"[food-app] recipe candidates: {len(candidates)}")
    core.process_all(queue_ws, ingest_ws, core.existing_row_index(ingest_ws), candidates, summary)
    summary["finished_at"] = core.now_iso()
    (core.OUT_DIR / "batch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[food-app] done: {len(summary['success'])} staged, {len(summary['failed'])} failed")
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
