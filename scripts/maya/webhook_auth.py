"""
Webhook signature verification (RM9).

Inbound webhooks from the selected telephony provider (Retell required; Twilio only if
adopted) must be authenticated before we act on them. HMAC-SHA256 over the raw body with
a constant-time compare. Unsigned / mismatched / unconfigured -> rejected (fail closed).
"""
from __future__ import annotations

import hashlib
import hmac


def verify_signature(secret: str | None, payload: bytes, signature: str | None) -> bool:
    """Return True only if `signature` is a valid HMAC-SHA256 of `payload` under `secret`.

    Fails closed: missing secret, missing signature, or non-bytes payload -> False.
    """
    if not secret or not signature:
        return False
    if not isinstance(payload, (bytes, bytearray)):
        return False
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    # Accept "sha256=..." prefixed headers as well as bare hex.
    candidate = signature.split("=", 1)[1] if signature.lower().startswith("sha256=") else signature
    try:
        return hmac.compare_digest(expected, candidate.strip())
    except (AttributeError, TypeError):
        return False
