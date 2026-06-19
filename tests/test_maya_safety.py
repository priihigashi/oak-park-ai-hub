"""Tests for safety/compliance controls (RM6, RM11, RM12, RM14, RE1, RE2, RE4)."""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from maya import safety


# ---- Consent (RM6/RE2) ----
def test_consent_yes_records():
    assert safety.handle_recording_consent("yes that's fine") == safety.RECORD


def test_consent_no_stops_recording():
    assert safety.handle_recording_consent("no, please don't") == safety.STOP_RECORDING


def test_consent_ambiguous_fails_safe_to_stop():
    assert safety.handle_recording_consent("uhh who is this") == safety.STOP_RECORDING


# ---- Outbound AI-call compliance gate (RE4) ----
def test_gate_blocks_without_basis():
    assert safety.outbound_call_allowed("+13055551234", None) is False
    assert safety.outbound_call_allowed("+13055551234", "no_reason") is False


def test_gate_blocks_without_number():
    assert safety.outbound_call_allowed("", "business_to_business") is False


def test_gate_allows_with_basis_and_number():
    assert safety.outbound_call_allowed("+13055551234", "business_to_business") is True


# ---- Errand authorization (RE1) ----
def test_errand_info_only_allowed():
    assert safety.errand_action_allowed("ask which insurance they accept") is True


def test_errand_booking_refused():
    for bad in ["book the appointment", "pay the invoice", "purchase 2 tickets", "sign the contract"]:
        assert safety.errand_action_allowed(bad) is False, bad


# ---- Rate / cost / kill switch (RM11/RM12) ----
def test_rate_limiter_caps_calls():
    rl = safety.RateLimiter(daily_call_cap=2, daily_cost_cap=100.0)
    assert rl.allowed(kill_switch=lambda: False)
    rl.record_call(); rl.record_call()
    assert rl.allowed(kill_switch=lambda: False) is False


def test_rate_limiter_caps_cost():
    rl = safety.RateLimiter(daily_call_cap=100, daily_cost_cap=1.0)
    rl.record_call(cost=1.5)
    assert rl.allowed(kill_switch=lambda: False) is False


def test_kill_switch_blocks_calls():
    rl = safety.RateLimiter()
    assert rl.allowed(kill_switch=lambda: True) is False


# ---- Retention / PII (RM14) ----
def test_redact_pii():
    out = safety.redact_pii("call me at 305-555-1234 or jane@example.com")
    assert "305-555-1234" not in out and "jane@example.com" not in out


def test_redact_ssn_and_card():
    out = safety.redact_pii("SSN 123-45-6789 card 4111 1111 1111 1111")
    assert "123-45-6789" not in out and "[redacted-ssn]" in out
    assert "4111 1111 1111 1111" not in out and "[redacted-card]" in out


def test_killswitch_env_wires_to_rate_limiter(monkeypatch):
    # Verify the REAL default kill switch (env-based) is honored, not just an injected lambda.
    rl = safety.RateLimiter()
    monkeypatch.setenv("MF_MAYA_KILL_SWITCH", "1")
    assert rl.allowed() is False
    monkeypatch.delenv("MF_MAYA_KILL_SWITCH", raising=False)
    assert rl.allowed() is True


def test_purge_expired_respects_ttl_and_hold():
    now = datetime(2026, 6, 19, tzinfo=timezone.utc)
    old = (now - timedelta(days=120)).isoformat()
    recent = (now - timedelta(days=5)).isoformat()
    records = [
        {"timestamp": old, "msg": "old"},
        {"timestamp": recent, "msg": "recent"},
        {"timestamp": old, "msg": "legal-hold", "hold": True},
    ]
    kept, deleted = safety.purge_expired(records, ttl_days=90, now=now)
    assert {r["msg"] for r in deleted} == {"old"}
    assert {r["msg"] for r in kept} == {"recent", "legal-hold"}
