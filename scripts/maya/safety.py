"""
Safety + compliance controls (RM6, RM11, RM12, RM14, RE1, RE2, RE4).

- Consent: AI + recording disclosure, capture/decline, decline -> stop recording (RM6/RE2).
- Outbound AI-call compliance gate: FCC/TCPA treat AI voice as artificial/prerecorded;
  require a lawful basis before dialing a number (RE4).
- Errand authorization: only Priscila-initiated; booking/payment/commitment are prohibited (RE1).
- RateLimiter: per-day call cap + cost cap, honors kill switch (RM11/RM12).
- Retention: TTL purge + PII redaction (RM14).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

from . import config

# ---- Consent (RM6 / RE2) ----
DISCLOSURE = (
    "Hi, this is Maya, an AI assistant for McFolling Properties. "
    "This call is recorded for quality and safety — is that okay?"
)
_YES = re.compile(r"\b(yes|yeah|yep|sure|ok(ay)?|that'?s fine|go ahead|fine)\b", re.IGNORECASE)
_NO = re.compile(r"\b(no|nope|don'?t|do not|stop|not okay|decline)\b", re.IGNORECASE)

RECORD = "record"
STOP_RECORDING = "stop_recording"


def handle_recording_consent(response: str) -> str:
    """Map a caller's reply to a recording action. Default (ambiguous) = STOP (fail safe)."""
    if response and _NO.search(response):
        return STOP_RECORDING
    if response and _YES.search(response):
        return RECORD
    return STOP_RECORDING


# ---- Outbound AI-call compliance gate (RE4) ----
# A call may only be placed if there is a lawful basis for an AI/prerecorded-voice call.
ALLOWED_BASES = {
    "business_to_business",     # calling a vendor/business line for info (errand use case)
    "prior_express_consent",    # the called party consented
    "existing_relationship",    # established business relationship within rules
}


def outbound_call_allowed(number: str | None, basis: str | None) -> bool:
    """RE4 gate: require a non-empty number AND a recognized lawful basis before dialing."""
    if not number or not str(number).strip():
        return False
    return basis in ALLOWED_BASES


# ---- Errand authorization (RE1) ----
_PROHIBITED = re.compile(r"\b(book|reserve|pay|purchase|buy|sign|agree to|commit|deposit|order)\b",
                         re.IGNORECASE)


def errand_action_allowed(instruction: str) -> bool:
    """RE1: errand agent gathers info only. Any booking/payment/commitment intent -> refused."""
    if not instruction:
        return False
    return not _PROHIBITED.search(instruction)


# ---- Rate / cost limiter + kill switch (RM11 / RM12) ----
@dataclass
class RateLimiter:
    daily_call_cap: int = config.DAILY_OUTBOUND_CALL_CAP
    daily_cost_cap: float = config.DAILY_COST_CAP_USD
    calls_today: int = 0
    cost_today: float = 0.0

    def allowed(self, kill_switch=config.kill_switch_active) -> bool:
        if kill_switch():
            return False
        if self.calls_today >= self.daily_call_cap:
            return False
        if self.cost_today >= self.daily_cost_cap:
            return False
        return True

    def record_call(self, cost: float = 0.0) -> None:
        self.calls_today += 1
        self.cost_today += cost


# ---- Retention / privacy (RM14) ----
# Order matters: SSN before phone (so the 3-2-4 SSN isn't shadowed), card anchored to
# grouped-4 formats so it doesn't swallow arbitrary 13-16 digit runs.
_PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[redacted-ssn]"),
    (re.compile(r"\b(?:\d{4}[ -]){3}\d{1,4}\b"), "[redacted-card]"),
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[redacted-phone]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[redacted-email]"),
]


def redact_pii(text: str) -> str:
    if not text:
        return text
    for rx, repl in _PII_PATTERNS:
        text = rx.sub(repl, text)
    return text


def purge_expired(records: Iterable[dict], ttl_days: int = config.GUEST_DATA_TTL_DAYS,
                  now: datetime | None = None, ts_key: str = "timestamp") -> tuple[list, list]:
    """Split records into (kept, deleted) by TTL. Records flagged {'hold': True} are never purged."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=ttl_days)
    kept, deleted = [], []
    for r in records:
        if r.get("hold"):
            kept.append(r)
            continue
        ts = r.get(ts_key)
        try:
            dt = datetime.fromisoformat(ts) if isinstance(ts, str) else ts
        except (ValueError, TypeError):
            # Unparseable timestamp -> never silently delete; keep for human review.
            r["_retention_review"] = True
            kept.append(r)
            continue
        if dt is not None and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        (deleted if (dt is not None and dt < cutoff) else kept).append(r)
    return kept, deleted
