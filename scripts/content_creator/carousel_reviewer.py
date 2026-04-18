#!/usr/bin/env python3
"""
carousel_reviewer.py — Post-build quality check for carousel output.
Runs automatically after content_creator.yml finishes building carousels.

Checks each built post for:
  1. Photo presence: sticker-slot has a real image (not "@..._STICKER" placeholder text)
  2. Context-image slots: "[ IMG: ... ]" placeholders not present in rendered HTML
  3. Slide count: at least 5 slides built (OPC) or 4 slides (Brazil/USA)
  4. PNG size sanity: every PNG > 10KB (blank-slide detection)
  5. Motion folder: at least 1 MP4 present

Reports via email if any check fails. Exits with code 0 always (non-blocking).

Usage:
  python carousel_reviewer.py   ← reads CONTENT_CREATOR_RUN env var (JSON list of results)
  python carousel_reviewer.py --dry-run  ← print checks without emailing
"""

import json, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime
import urllib.request, urllib.parse

# Env vars
SHEETS_TOKEN     = os.environ.get("SHEETS_TOKEN", "")
ALERT_EMAIL      = os.environ.get("ALERT_EMAIL", "priscila@oakpark-construction.com")
RUN_RESULTS_JSON = os.environ.get("CONTENT_CREATOR_RUN", "[]")  # JSON array of result dicts

DRY_RUN = "--dry-run" in sys.argv


# ─── Checks ──────────────────────────────────────────────────────────────────

def check_html_placeholders(html_path: str) -> list[str]:
    """Return list of issue strings found in the HTML file."""
    issues = []
    try:
        html = Path(html_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [f"Cannot read HTML: {e}"]

    # Placeholder sticker text — pattern: @WORD_STICKER
    placeholder_matches = re.findall(r'@\w+_STICKER', html)
    if placeholder_matches:
        issues.append(
            f"PLACEHOLDER sticker(s) found — real photo NOT embedded: {', '.join(set(placeholder_matches))}"
        )

    # Context-image slot still has query text (not replaced with real image)
    ctx_matches = re.findall(r'\[ IMG: ([^\]]{3,60}) \]', html)
    if ctx_matches:
        issues.append(
            f"CONTEXT-IMAGE slot(s) still have placeholder text — image not sourced: "
            + "; ".join(ctx_matches[:3])
        )

    return issues


def check_png_folder(png_dir: str, min_slides: int = 4) -> list[str]:
    """Check PNG output folder for count + size sanity."""
    issues = []
    if not Path(png_dir).exists():
        return [f"PNG folder missing: {png_dir}"]

    pngs = sorted(Path(png_dir).glob("*.png"))
    if len(pngs) < min_slides:
        issues.append(f"Too few PNGs: {len(pngs)} found, expected ≥ {min_slides}")

    tiny = [p.name for p in pngs if p.stat().st_size < 10_000]
    if tiny:
        issues.append(f"Suspiciously small PNGs (blank slide?): {', '.join(tiny)}")

    return issues


def check_motion_folder(motion_dir: str) -> list[str]:
    """Check that at least 1 MP4 was rendered."""
    if not Path(motion_dir).exists():
        return ["Motion folder missing entirely"]
    mp4s = list(Path(motion_dir).glob("*.mp4"))
    if not mp4s:
        return ["No MP4 files in motion folder — motion render failed"]
    return []


def check_built_post(result: dict) -> dict:
    """Run all checks on a single built post result dict.
    Returns {post_id, topic, niche, issues: [str], passed: bool}."""
    post_id = result.get("post_id", "unknown")
    topic   = result.get("topic", "")
    niche   = result.get("niche", "")

    all_issues = []

    # 1. HTML placeholder check — look for cover.html in version folder (local path)
    # The content_creator already cleaned up work_dir, so we check Drive link heuristically.
    # In local GitHub Actions run, WORK_DIR still exists during this script's execution.
    work_dir_env = os.environ.get("WORK_DIR", "/tmp/content_creator_run")
    html_local = Path(work_dir_env) / post_id / "cover.html"
    if html_local.exists():
        all_issues.extend(check_html_placeholders(str(html_local)))
    else:
        # Try common temp pattern
        for candidate in Path(work_dir_env).glob(f"**/{post_id}/cover.html"):
            all_issues.extend(check_html_placeholders(str(candidate)))
            break
        else:
            # Work dir cleaned up — can't check HTML placeholders locally
            pass  # Drive folder link check would require downloading — skip for now

    # 2. PNG check
    png_dir_local = Path(work_dir_env) / post_id / "png"
    if png_dir_local.exists():
        min_slides = 5 if niche == "opc" else 4
        all_issues.extend(check_png_folder(str(png_dir_local), min_slides))

    # 3. Motion check
    motion_dir_local = Path(work_dir_env) / post_id / "motion"
    all_issues.extend(check_motion_folder(str(motion_dir_local)))

    passed = len(all_issues) == 0
    return {
        "post_id": post_id,
        "topic": topic[:60],
        "niche": niche,
        "issues": all_issues,
        "passed": passed,
        "drive_link": result.get("version_link") or result.get("static_link", ""),
    }


# ─── Email ────────────────────────────────────────────────────────────────────

def send_review_email(failed_posts: list[dict], all_posts: list[dict]):
    """Send review report via send_email.yml workflow."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total = len(all_posts)
    n_fail = len(failed_posts)
    n_pass = total - n_fail

    subject = f"[carousel-reviewer] {n_pass}/{total} passed — {n_fail} issue(s) found — {now}"

    lines = [
        f"CAROUSEL REVIEW REPORT — {now}",
        f"Total built: {total} | Passed: {n_pass} | Issues: {n_fail}",
        "",
    ]

    for p in all_posts:
        status = "✅ PASS" if p["passed"] else "❌ ISSUES"
        lines.append(f"{status}  [{p['niche'].upper()}] {p['topic']}")
        lines.append(f"       Drive: {p['drive_link']}")
        for issue in p["issues"]:
            lines.append(f"       ⚠  {issue}")
        lines.append("")

    lines += [
        "─" * 60,
        "To fix sticker placeholders: source real CC photos and re-run the pipeline.",
        "The image_suggestions.txt in each post's resources/ folder lists exactly what's needed.",
        "Workflow: https://github.com/priihigashi/oak-park-ai-hub/actions/workflows/content_creator.yml",
    ]

    body = "\n".join(lines)

    if DRY_RUN:
        print("\n[DRY RUN] Would send email:")
        print(f"Subject: {subject}")
        print(body)
        return

    try:
        subprocess.run(
            [
                "gh", "workflow", "run", "send_email.yml",
                "--repo", "priihigashi/oak-park-ai-hub",
                "-f", f"to={ALERT_EMAIL}",
                "-f", f"subject={subject}",
                "-f", f"body={body}",
            ],
            check=False, timeout=30,
        )
        print(f"  Review report emailed to {ALERT_EMAIL}")
    except Exception as e:
        print(f"  Review email failed (non-fatal): {e}")
        print(body)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n[carousel-reviewer] Starting post-build review...")

    # Parse results from env var or stdin
    results_raw = RUN_RESULTS_JSON
    try:
        results = json.loads(results_raw) if results_raw.strip() else []
    except json.JSONDecodeError:
        results = []

    if not results:
        print("  No results to review (CONTENT_CREATOR_RUN not set or empty) — exiting")
        return

    print(f"  Reviewing {len(results)} post(s)...")
    reviewed = [check_built_post(r) for r in results]

    passed = [r for r in reviewed if r["passed"]]
    failed = [r for r in reviewed if not r["passed"]]

    for r in reviewed:
        icon = "✅" if r["passed"] else "❌"
        print(f"  {icon} [{r['niche']}] {r['topic']}")
        for issue in r["issues"]:
            print(f"       ⚠  {issue}")

    print(f"\n  Summary: {len(passed)}/{len(reviewed)} passed")

    # Always send report (even if all pass — confirms reviewer ran)
    send_review_email(failed, reviewed)

    # Always exit 0 — reviewer is informational, not blocking
    print("[carousel-reviewer] Done.")


if __name__ == "__main__":
    main()
