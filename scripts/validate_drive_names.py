#!/usr/bin/env python3
"""
Validate shared-drive labels in routing.py and drive_map_builder.py.

This is read-only: it calls Drive drives().get(...) for each configured shared
drive and fails if any local label drifts from the live Drive name.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import drive_map_builder  # noqa: E402
import routing  # noqa: E402

DEFAULT_TOKEN_FILE = os.environ.get(
    "SHEETS_TOKEN_PATH",
    "/Users/priscilahigashi/ClaudeWorkspace/Credentials/sheets_token.json",
)


def collect_expected_names() -> dict[str, dict[str, set[str]]]:
    expected: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    for key, route in routing.ROUTES.items():
        drive_id = route.get("drive_id")
        drive_name = route.get("drive_name")
        if drive_id and drive_name:
            expected[drive_id][drive_name].add(f"routing.ROUTES[{key!r}].drive_name")

    for drive_id, drive_name in drive_map_builder.DRIVES.items():
        expected[drive_id][drive_name].add("drive_map_builder.DRIVES")

    return {drive_id: dict(names) for drive_id, names in expected.items()}


def find_internal_conflicts(
    expected: dict[str, dict[str, set[str]]],
) -> list[str]:
    conflicts = []
    for drive_id, names in sorted(expected.items()):
        if len(names) <= 1:
            continue
        details = "; ".join(
            f"{name!r} from {', '.join(sorted(sources))}"
            for name, sources in sorted(names.items())
        )
        conflicts.append(f"{drive_id}: conflicting local names: {details}")
    return conflicts


def fetch_live_names(drive_svc, drive_ids: Iterable[str]) -> tuple[dict[str, str], list[str]]:
    live = {}
    errors = []
    for drive_id in sorted(drive_ids):
        try:
            resp = (
                drive_svc.drives()
                .get(driveId=drive_id, fields="id,name")
                .execute()
            )
            live[drive_id] = resp["name"]
        except Exception as exc:
            message = str(exc).splitlines()[0]
            errors.append(f"{drive_id}: could not fetch live Drive name: {message}")
    return live, errors


def find_live_mismatches(
    expected: dict[str, dict[str, set[str]]],
    live_names: dict[str, str],
) -> list[str]:
    mismatches = []
    for drive_id, names in sorted(expected.items()):
        live_name = live_names.get(drive_id)
        if live_name is None:
            continue
        for expected_name, sources in sorted(names.items()):
            if expected_name != live_name:
                source_list = ", ".join(sorted(sources))
                mismatches.append(
                    f"{drive_id}: {source_list} has {expected_name!r}; "
                    f"live Drive name is {live_name!r}"
                )
    return mismatches


def build_drive_service(token_file: str):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(token_file)
    return build("drive", "v3", credentials=creds)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate configured shared-drive names against live Drive names."
    )
    parser.add_argument(
        "--token-file",
        default=DEFAULT_TOKEN_FILE,
        help="OAuth token JSON path. Defaults to SHEETS_TOKEN_PATH or Priscila's sheets_token.json.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Only check that local config files agree with each other; skip Drive API.",
    )
    args = parser.parse_args()

    expected = collect_expected_names()
    failures = find_internal_conflicts(expected)

    if not args.local_only and not failures:
        drive_svc = build_drive_service(args.token_file)
        live_names, fetch_errors = fetch_live_names(drive_svc, expected.keys())
        failures.extend(fetch_errors)
        failures.extend(find_live_mismatches(expected, live_names))

    if failures:
        print("Drive name validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    checked = len(expected)
    mode = "local config" if args.local_only else "live Drive"
    print(f"Drive name validation passed ({checked} shared drives, {mode}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
