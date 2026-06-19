"""Tests for guest notes: urgency classify + schema + dedup (RM1, RM5, RM7, RM8)."""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from maya.notes import GuestNote, NoteStore, classify_urgency, URGENT, ROUTINE


def test_urgent_rubric_matches():
    for msg in ["I'm locked out!", "there's no heat", "the unit is flooding",
                "I smell gas", "AC is broken and it's 95 degrees",
                "someone broke in", "the smoke alarm is going off"]:
        assert classify_urgency(msg) == URGENT, msg


def test_routine_messages():
    for msg in ["what's the wifi password?", "where do I park?", "what time is checkout?"]:
        assert classify_urgency(msg) == ROUTINE, msg


def test_benign_hazard_words_not_urgent():
    # These contain hazard nouns but are NOT emergencies — must stay ROUTINE (alarm fatigue guard).
    for msg in ["do you have a gas stove?", "where is the fire pit?",
                "the smoke detector keeps beeping", "is there a fireplace?",
                "does the kitchen have a gas range?"]:
        assert classify_urgency(msg) == ROUTINE, msg


def test_note_schema_fields_and_row():
    n = GuestNote.create("MID1", "Jane", "PROP-1", "what's the wifi?", intent="wifi",
                         now=datetime(2026, 6, 19, tzinfo=timezone.utc))
    assert n.urgency == ROUTINE
    row = n.as_row()
    assert row[1] == "PROP-1" and row[2] == "Jane" and row[6] == "MID1"
    assert len(row) == 7


def test_dedup_by_message_id():
    store = NoteStore()
    a = GuestNote.create("MID-DUP", "Jane", "P1", "hello")
    b = GuestNote.create("MID-DUP", "Jane", "P1", "different text body")
    assert store.add(a) is not None
    assert store.add(b) is None       # same id -> duplicate
    assert len(store.notes) == 1


def test_dedup_by_content_hash_when_ids_differ():
    store = NoteStore()
    a = GuestNote.create("MID1", "Jane", "P1", "Wifi please")
    b = GuestNote.create("MID2", "Jane", "P1", "wifi please")  # same content, diff id
    assert store.add(a) is not None
    assert store.add(b) is None
    assert len(store.notes) == 1


def test_distinct_notes_both_kept():
    store = NoteStore()
    assert store.add(GuestNote.create("M1", "Jane", "P1", "wifi?")) is not None
    assert store.add(GuestNote.create("M2", "Bob", "P1", "parking?")) is not None
    assert len(store.notes) == 2
