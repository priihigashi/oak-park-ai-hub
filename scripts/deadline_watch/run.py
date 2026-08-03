"""Run both readers, emit minimal alerts, and fail loudly if either reader fails."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .core import classify
from .providers import gmail_messages, outlook_messages


def _allowed() -> tuple[str, ...]:
    value = json.loads(os.environ["DEADLINE_ALLOWED_SENDERS_JSON"])
    if not isinstance(value, list) or not value:
        raise ValueError("DEADLINE_ALLOWED_SENDERS_JSON must be a non-empty JSON list")
    return tuple(str(item) for item in value)


def _notify(candidate: dict) -> None:
    topic = os.environ.get("NTFY_TOPIC", "")
    if not topic:
        return
    due = candidate["due_date"] or "review needed"
    message = f"{candidate['mailbox']} | {candidate['subject']} | due: {due}"
    request = urllib.request.Request(
        f"https://ntfy.sh/{topic}", data=message.encode(), method="POST",
        headers={"Title": "Deadline safety net", "Tags": "warning,calendar"},
    )
    with urllib.request.urlopen(request, timeout=20):
        pass


def main() -> int:
    now = datetime.now().astimezone()
    allowed = _allowed()
    messages = gmail_messages() + outlook_messages()
    candidates = [candidate for message in messages if (candidate := classify(message, allowed, now.date()))]
    output = {
        "checked_at": now.isoformat(timespec="seconds"), "mailboxes_ok": ["opc_gmail", "hotmail"],
        "messages_checked": len(messages), "candidates": [asdict(item) for item in candidates],
    }
    output_path = Path(os.environ.get("DEADLINE_OUTPUT", "deadline-watch-output.json"))
    output_path.write_text(json.dumps(output, default=str, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("DEADLINE_NOTIFY") == "1":
        for candidate in output["candidates"]:
            _notify(candidate)
    print(json.dumps({"checked_at": output["checked_at"], "messages_checked": len(messages), "candidate_count": len(candidates)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"DEADLINE WATCH FAILED: {exc}", file=sys.stderr)
        raise

