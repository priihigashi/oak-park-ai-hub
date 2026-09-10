"""Read-only month-to-date Google Ads spend monitor for Oak Park Construction.

This monitor intentionally has no campaign mutation path. It reports when the
account crosses a warning threshold or monthly cap so a separately approved
control can act on verified data.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ads_report import ads_search, load_config, micros_to_dollars


DEFAULT_WARNING_DOLLARS = 1450.0
DEFAULT_CAP_DOLLARS = 1500.0
OUTPUT_DIR = Path(
    os.environ.get("ADS_CAP_OUTPUT_DIR", "artifacts/ads-monthly-cap-monitor")
)


@dataclass(frozen=True)
class CapDecision:
    state: str
    spend_dollars: float
    warning_dollars: float
    cap_dollars: float
    remaining_to_cap_dollars: float
    action: str


def parse_dollars(name: str, default: float) -> float:
    raw = os.environ.get(name, str(default)).strip()
    try:
        value = float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number, got: {raw!r}") from exc
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero")
    return value


def decide_cap_state(
    spend_dollars: float,
    warning_dollars: float = DEFAULT_WARNING_DOLLARS,
    cap_dollars: float = DEFAULT_CAP_DOLLARS,
) -> CapDecision:
    if spend_dollars < 0:
        raise ValueError("spend_dollars cannot be negative")
    if warning_dollars <= 0 or cap_dollars <= 0:
        raise ValueError("warning and cap must be greater than zero")
    if warning_dollars >= cap_dollars:
        raise ValueError("warning must be lower than cap")

    if spend_dollars >= cap_dollars:
        state = "CAP_EXCEEDED"
        action = (
            "Do not assume delivery has stopped. Verify the live account now and "
            "request explicit approval for any campaign pause."
        )
    elif spend_dollars >= warning_dollars:
        state = "PAUSE_REVIEW_REQUIRED"
        action = (
            "Verify the live account now. A campaign pause still requires the "
            "separately approved control path."
        )
    else:
        state = "BELOW_WARNING"
        action = "No control action requested; continue monitoring."

    return CapDecision(
        state=state,
        spend_dollars=round(spend_dollars, 2),
        warning_dollars=round(warning_dollars, 2),
        cap_dollars=round(cap_dollars, 2),
        remaining_to_cap_dollars=round(max(cap_dollars - spend_dollars, 0.0), 2),
        action=action,
    )


def account_spend(raw_rows: list[dict[str, Any]]) -> float:
    if not raw_rows:
        raise RuntimeError("Google Ads returned no month-to-date customer metrics")
    return sum(
        micros_to_dollars((row.get("metrics") or {}).get("costMicros"))
        for row in raw_rows
    )


def build_markdown(payload: dict[str, Any]) -> str:
    decision = payload["decision"]
    return "\n".join(
        [
            "# OPC Google Ads Monthly Cap Monitor",
            "",
            f"- Generated: {payload['generated_at']}",
            f"- Customer: {payload['customer_id']}",
            f"- Month-to-date spend: ${decision['spend_dollars']:,.2f}",
            f"- Warning threshold: ${decision['warning_dollars']:,.2f}",
            f"- Monthly cap target: ${decision['cap_dollars']:,.2f}",
            f"- State: **{decision['state']}**",
            f"- Remaining to cap: ${decision['remaining_to_cap_dollars']:,.2f}",
            "",
            "## Next action",
            "",
            decision["action"],
            "",
            "## Safety and accuracy",
            "",
            "- Read-only: this monitor never pauses or changes a campaign.",
            "- Google Ads cost reporting and workflow execution can lag, so this is "
            "a warning system—not a guaranteed billing hard stop.",
            "- A native Google Ads billing limit, if available, remains the preferred route.",
            "- Any automated pause needs separate approval, failure alerts, and a tested resume path.",
            "",
        ]
    )


def main() -> int:
    warning_dollars = parse_dollars("ADS_WARNING_DOLLARS", DEFAULT_WARNING_DOLLARS)
    cap_dollars = parse_dollars("ADS_CAP_DOLLARS", DEFAULT_CAP_DOLLARS)
    config = load_config()

    query = """
        SELECT
          customer.id,
          metrics.cost_micros
        FROM customer
        WHERE segments.date DURING THIS_MONTH
    """
    spend_dollars = account_spend(ads_search(config, query))
    decision = decide_cap_state(spend_dollars, warning_dollars, cap_dollars)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "customer_id": config.customer_id,
        "date_range": "THIS_MONTH",
        "decision": asdict(decision),
        "mutation_performed": False,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "monthly_cap_status.json"
    markdown_path = OUTPUT_DIR / "monthly_cap_status.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    markdown_path.write_text(build_markdown(payload), encoding="utf-8")

    print(build_markdown(payload))
    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {markdown_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
