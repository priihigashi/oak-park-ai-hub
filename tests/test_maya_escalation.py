"""Tests for the Maya escalation engine (RM3, RM10, RM11)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from maya import escalation as esc
from maya.escalation import ANSWERED, VOICEMAIL, NO_ANSWER


def _dialer(script):
    """Return a dialer that yields outcomes from `script` (a list) in order."""
    seq = iter(script)
    return lambda target: next(seq)


def test_priscila_answers_first_attempt():
    r = esc.run_escalation(is_urgent=True, dialer=_dialer([ANSWERED]), kill_switch=lambda: False)
    assert r.reached == "priscila"
    assert r.failed_over is False
    assert len(r.attempts) == 1


def test_retries_priscila_three_times_then_michael():
    # Priscila: no_answer, voicemail, no_answer (3) -> Michael answers
    script = [NO_ANSWER, VOICEMAIL, NO_ANSWER, ANSWERED]
    r = esc.run_escalation(is_urgent=True, dialer=_dialer(script), kill_switch=lambda: False)
    assert r.reached == "michael"
    assert r.failed_over is True
    # 3 priscila attempts + 1 michael
    assert len([a for a in r.attempts if a["target"] == "priscila"]) == 3
    assert r.attempts[-1]["target"] == "michael"


def test_voicemail_is_not_answered():
    # Priscila voicemail x3, Michael voicemail x3 -> nobody reached
    script = [VOICEMAIL] * 6
    sms = []
    held = []
    r = esc.run_escalation(
        is_urgent=True, dialer=_dialer(script), kill_switch=lambda: False,
        notify_sms=lambda m: sms.append(m), leave_guest_holding=lambda: held.append(True),
    )
    assert r.reached is None
    assert r.failure_handled is True
    assert sms and held  # failure behavior fired


def test_interval_respected_between_attempts():
    sleeps = []
    esc.run_escalation(
        is_urgent=True, dialer=_dialer([NO_ANSWER, NO_ANSWER, ANSWERED]),
        sleeper=lambda s: sleeps.append(s), kill_switch=lambda: False,
    )
    assert sleeps == [esc.config.ESCALATION_INTERVAL_SECONDS] * 2


def test_interval_between_priscila_and_michael():
    # 3 Priscila no-answers, then Michael answers. Expect 2 intra-Priscila sleeps + 1 cross-target sleep = 3.
    sleeps = []
    esc.run_escalation(
        is_urgent=True, dialer=_dialer([NO_ANSWER, NO_ANSWER, NO_ANSWER, ANSWERED]),
        sleeper=lambda s: sleeps.append(s), kill_switch=lambda: False,
    )
    assert sleeps == [esc.config.ESCALATION_INTERVAL_SECONDS] * 3


def test_kill_switch_aborts():
    called = []
    r = esc.run_escalation(is_urgent=True, dialer=lambda t: called.append(t) or ANSWERED,
                           kill_switch=lambda: True)
    assert r.aborted_kill_switch is True
    assert r.reached is None
    assert called == []  # no dial happened


def test_non_urgent_does_not_escalate():
    called = []
    r = esc.run_escalation(is_urgent=False, dialer=lambda t: called.append(t) or ANSWERED,
                           kill_switch=lambda: False)
    assert r.reached is None
    assert called == []
