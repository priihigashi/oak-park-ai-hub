"""
Guest-notes capture: schema + urgency classification + deduplication (RM1, RM5, RM7, RM8).

- GuestNote: the defined note schema (RM7).
- classify_urgency: rubric — lockout / no-heat / no-AC / flood / leak / smoke / fire /
  gas / break-in / medical = URGENT; everything else routine (RM5).
- NoteStore: dedup by provider message id, falling back to a content hash (RM8).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional

URGENT = "urgent"
ROUTINE = "routine"

# RM5 rubric — hazard phrasing, case-insensitive. Tuned to avoid benign false positives
# ("gas stove", "fire pit", "smoke detector beeping") that would cause escalation alarm fatigue.
_URGENT_PATTERNS = [
    r"lock(ed)?\s*out", r"can'?t get in",
    r"no\s*heat", r"no\s*(a/?c|air)", r"no\s*(power|electric|water)",
    r"flood", r"leak", r"burst", r"sewage", r"overflow",
    r"\bfire\b(?!\s*(pit|place|works|wood))",
    r"\bsmoke\b(?!\s*(detector|alarm))",
    r"(smoke|fire)\s*alarm\s*(is\s*)?(going|won'?t|blaring|keeps)",
    r"gas\s*(leak|smell|smells|odor)", r"smell[a-z\s]*\bgas\b", r"carbon monoxide",
    r"break[\s-]?in", r"broke\s*in(to)?", r"intruder", r"emergency", r"injur", r"bleeding", r"911",
    # appliance failure in a climate/habitability sense (not a general "has A/C?" question)
    r"(a/?c|air\s*condition\w*|heat\w*|furnace|water\s*heater)\s*(is\s*)?(broke\w*|not\s*working|stopped|down|out|dead)",
    r"(broke\w*|not\s*working|stopped\s*working)\s*(the\s*)?(a/?c|air|heat|furnace)",
]
_URGENT_RE = re.compile("|".join(_URGENT_PATTERNS), re.IGNORECASE)


def classify_urgency(text: str) -> str:
    """URGENT if the message matches the safety/habitability rubric, else ROUTINE."""
    if not text:
        return ROUTINE
    return URGENT if _URGENT_RE.search(text) else ROUTINE


@dataclass
class GuestNote:
    source_msg_id: str           # provider message id (preferred dedup key)
    guest: str
    property_id: str
    message: str
    intent: str                  # e.g. wifi / checkin / parking / maintenance / other
    urgency: str                 # URGENT | ROUTINE
    timestamp: str               # ISO-8601 UTC

    @staticmethod
    def create(source_msg_id: str, guest: str, property_id: str, message: str,
               intent: str = "other", now: Optional[datetime] = None) -> "GuestNote":
        ts = (now or datetime.now(timezone.utc)).isoformat()
        return GuestNote(
            source_msg_id=source_msg_id, guest=guest, property_id=property_id,
            message=message, intent=intent, urgency=classify_urgency(message), timestamp=ts,
        )

    def as_row(self) -> list:
        d = asdict(self)
        return [d["timestamp"], d["property_id"], d["guest"], d["intent"],
                d["urgency"], d["message"], d["source_msg_id"]]


def _content_hash(guest: str, property_id: str, message: str) -> str:
    return hashlib.sha256(f"{guest}|{property_id}|{message.strip().lower()}".encode("utf-8")).hexdigest()


class NoteStore:
    """In-memory dedup index. add() returns the stored note, or None if it's a duplicate."""

    def __init__(self) -> None:
        self._seen_ids: set[str] = set()
        self._seen_hashes: set[str] = set()
        self.notes: list[GuestNote] = []

    def add(self, note: GuestNote) -> Optional[GuestNote]:
        key = note.source_msg_id.strip() if note.source_msg_id else ""
        chash = _content_hash(note.guest, note.property_id, note.message)
        if key and key in self._seen_ids:
            return None
        if chash in self._seen_hashes:
            return None
        if key:
            self._seen_ids.add(key)
        self._seen_hashes.add(chash)
        self.notes.append(note)
        return note
