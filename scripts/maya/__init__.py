"""
Maya / Call Assistants — minimum safe pilot software layer.

McFolling voice agents (APPROVED — ACTIVE 2026-06-19):
  (A) Errand agent — outbound info-gathering calls Priscila directs (never books/pays).
  (B) Maya — Airbnb guest line: capture notes, auto-answer common Qs, escalate urgent.

This package is the provider-agnostic logic + safety controls for the pilot. It is fully
unit-testable WITHOUT a live Retell/Twilio account. Going live additionally requires the
external accounts/secrets named in config.py (see README.md).
"""
