"""
Pilot configuration — constants + secret NAMES (never values).

Locked decisions (Priscila, 2026-06-19):
  - Escalation: Priscila first, 3 calls 2 min apart; if unanswered -> Michael.
  - Telephony: Retell-managed number is the pilot default. Twilio optional.
  - Compliance gates mandatory.
  - One pilot property only until acceptance tests pass.
"""
from __future__ import annotations

import os

# ---- Secret NAMES (resolved from env/GitHub secrets at runtime; never hardcode values) ----
SECRET_RETELL_API_KEY = "MF_RETELL_API_KEY"          # required to go live
SECRET_RETELL_WEBHOOK = "MF_RETELL_WEBHOOK_SECRET"   # webhook signature verification
SECRET_TWILIO_SID = "MF_TWILIO_ACCOUNT_SID"          # optional (only if Twilio adopted)
SECRET_TWILIO_AUTH = "MF_TWILIO_AUTH_TOKEN"          # optional
SECRET_TWILIO_NUMBER = "MF_TWILIO_PHONE_NUMBER"      # optional
SECRET_MCFOLLING_TOKEN = "MCFOLLING_TOKEN"           # McFolling-owned Gmail/Drive/Sheets
SECRET_SHEETS_TOKEN = "SHEETS_TOKEN"                 # Priscila-owned surfaces (Ideas & Inbox)

# Contact slots are secret NAMES too — phone numbers are PII, never stored in code.
SECRET_PRISCILA_PHONE = "MF_PRISCILA_PHONE"
SECRET_MICHAEL_PHONE = "MF_MICHAEL_PHONE"

# ---- Escalation policy (locked) ----
ESCALATION_PRIMARY = "priscila"
ESCALATION_FALLBACK = "michael"
ESCALATION_MAX_ATTEMPTS = 3          # per target
ESCALATION_INTERVAL_SECONDS = 120    # 2 minutes apart

# ---- Rate / cost guardrails ----
DAILY_OUTBOUND_CALL_CAP = 50         # hard cap of outbound calls/day (pilot)
DAILY_COST_CAP_USD = 25.0            # spend alert/stop threshold (pilot)

# ---- Retention (privacy) ----
GUEST_DATA_TTL_DAYS = 90             # purge guest notes after 90 days unless flagged

# ---- Kill switch ----
KILL_SWITCH_ENV = "MF_MAYA_KILL_SWITCH"   # set to "1"/"true" to stop ALL calls immediately

# ---- Telephony ----
TELEPHONY_DEFAULT = "retell_managed"  # pilot default; "twilio" only if explicitly adopted

# ---- Pilot scope ----
PILOT_PROPERTY_LIMIT = 1


def kill_switch_active() -> bool:
    """True if the kill switch env flag is set — blocks all outbound calls."""
    return os.environ.get(KILL_SWITCH_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def has_live_voice_credentials() -> bool:
    """True only if the Retell API key is present (required to place real calls)."""
    return bool(os.environ.get(SECRET_RETELL_API_KEY, "").strip())
