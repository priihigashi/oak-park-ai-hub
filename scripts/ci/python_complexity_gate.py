#!/usr/bin/env python3
"""Python complexity no-regression gate.

Ruff has no equivalent of ESLint's native bulk suppressions, and baselining 150
findings with inline `# noqa: C901` would mean editing 150 live functions — a
behaviour-adjacent change the policy explicitly forbids (CLAUDE.md rule 5: "Do
not trigger a broad, behavior-changing refactor merely to satisfy a new metric").

So this reproduces the SAME guarantee the JS gate gives, deliberately and no
more: the number of C901 violations in a file may not increase, and a file with
no recorded debt may not acquire any.

It does NOT guarantee that an individual function cannot get worse — identical
to the ESLint suppressions limitation recorded in docs/QUALITY_GATE_ENFORCEMENT.md.
Do not describe it as more than that.

Usage:
    python3 scripts/ci/python_complexity_gate.py            # check against baseline
    python3 scripts/ci/python_complexity_gate.py --write    # (re)record the baseline
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE = REPO_ROOT / "python-complexity-baseline.json"


def current_counts() -> Counter[str]:
    """C901 violations per file, via ruff's JSON output."""
    proc = subprocess.run(
        ["ruff", "check", "--select", "C901", "--output-format", "json", "."],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    # ruff exits 1 when it finds violations — expected. Anything else is a real
    # failure (bad config, missing binary) and must not be read as "clean".
    if proc.returncode not in (0, 1):
        sys.exit(f"ruff failed (exit {proc.returncode}):\n{proc.stderr}")

    counts: Counter[str] = Counter()
    for item in json.loads(proc.stdout or "[]"):
        rel = Path(item["filename"]).resolve().relative_to(REPO_ROOT)
        counts[rel.as_posix()] += 1
    return counts


def write_baseline(counts: Counter[str]) -> None:
    BASELINE.write_text(json.dumps(dict(sorted(counts.items())), indent=2) + "\n")
    print(f"Recorded {sum(counts.values())} C901 findings across {len(counts)} files")
    print(f"  -> {BASELINE.relative_to(REPO_ROOT)}")


def check(counts: Counter[str]) -> int:
    if not BASELINE.exists():
        sys.exit(f"No baseline at {BASELINE}. Run with --write first.")
    recorded: dict[str, int] = json.loads(BASELINE.read_text())

    regressions = [
        (path, recorded.get(path, 0), n)
        for path, n in sorted(counts.items())
        if n > recorded.get(path, 0)
    ]
    # A file that improved should shrink the baseline, mirroring ESLint's
    # --prune-suppressions. Reported, never fatal: failing a build for making
    # the code better is how a gate gets switched off.
    improved = [
        (path, was, counts.get(path, 0))
        for path, was in sorted(recorded.items())
        if counts.get(path, 0) < was
    ]

    for path, was, now in improved:
        print(f"IMPROVED  {path}: {was} -> {now} (run --write to prune)")

    if not regressions:
        print(f"OK — {sum(counts.values())} C901 findings, none above baseline.")
        return 0

    print("\nComplexity regressions (C901, max-complexity=10):", file=sys.stderr)
    for path, was, now in regressions:
        label = "new file" if was == 0 else f"baseline {was}"
        print(f"  {path}: {was} -> {now}  ({label})", file=sys.stderr)
    print(
        "\nSplit the new function or reduce its branching. Raising the baseline "
        "is not a fix — see CLAUDE.md 'CODE-QUALITY GATES'.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="(re)record the baseline")
    args = ap.parse_args()

    counts = current_counts()
    if args.write:
        write_baseline(counts)
        return 0
    return check(counts)


if __name__ == "__main__":
    raise SystemExit(main())
