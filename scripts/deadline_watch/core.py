"""Deterministic deadline detection with no model calls or mailbox mutations."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from email.utils import parseaddr

KEYWORDS = (
    "action needed",
    "attestation",
    "deadline",
    "due date",
    "expires",
    "required",
    "verification",
)
MONTHS = {
    name.lower(): number
    for number, name in enumerate(
        (
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ),
        start=1,
    )
}
DATE_PATTERNS = (
    re.compile(
        r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2}|\d{4}))?\b"),
)


@dataclass(frozen=True)
class Message:
    mailbox: str
    message_id: str
    sender: str
    subject: str
    body: str
    received_at: datetime
    source_url: str = ""


@dataclass(frozen=True)
class Candidate:
    alert_id: str
    mailbox: str
    message_id: str
    sender: str
    subject: str
    due_date: date | None
    status: str
    reasons: tuple[str, ...]
    source_url: str


def sender_address(value: str) -> str:
    """Return a normalized address without trusting the display name."""
    return parseaddr(value)[1].strip().lower()


def sender_allowed(sender: str, allowed: tuple[str, ...]) -> bool:
    address = sender_address(sender)
    if "@" not in address:
        return False
    domain = address.rsplit("@", 1)[1]
    for rule in allowed:
        normalized = rule.strip().lower().lstrip("@")
        if "@" in normalized and address == normalized:
            return True
        if "@" not in normalized and (domain == normalized or domain.endswith("." + normalized)):
            return True
    return False


def _year(raw: str | None, received: date) -> int:
    if not raw:
        return received.year
    value = int(raw)
    return value + 2000 if value < 100 else value


def extract_dates(text: str, received: date) -> tuple[date, ...]:
    found: set[date] = set()
    for match in DATE_PATTERNS[0].finditer(text):
        try:
            found.add(date(_year(match.group(3), received), MONTHS[match.group(1).lower()], int(match.group(2))))
        except ValueError:
            continue
    for match in DATE_PATTERNS[1].finditer(text):
        try:
            found.add(date(_year(match.group(3), received), int(match.group(1)), int(match.group(2))))
        except ValueError:
            continue
    return tuple(sorted(found))


def _alert_id(message: Message, due_date: date | None) -> str:
    raw = f"{message.mailbox}|{message.message_id}|{due_date or 'review'}"
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def classify(
    message: Message,
    allowed_senders: tuple[str, ...],
    today: date,
    horizon_days: int = 30,
) -> Candidate | None:
    if not sender_allowed(message.sender, allowed_senders):
        return None
    searchable = f"{message.subject}\n{message.body}"
    matched = tuple(keyword for keyword in KEYWORDS if keyword in searchable.lower())
    dates = tuple(d for d in extract_dates(searchable, message.received_at.date()) if today <= d <= today + timedelta(days=horizon_days))
    if not matched and not dates:
        return None
    due_date = dates[0] if len(dates) == 1 else None
    status = "ready" if due_date else "review_needed"
    reasons = matched + (("one_date_within_horizon",) if due_date else ("ambiguous_or_missing_date",))
    return Candidate(
        alert_id=_alert_id(message, due_date), mailbox=message.mailbox,
        message_id=message.message_id, sender=sender_address(message.sender),
        subject=message.subject, due_date=due_date, status=status,
        reasons=reasons, source_url=message.source_url,
    )

