"""Tests for webhook signature verification (RM9)."""
import hashlib
import hmac
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from maya.webhook_auth import verify_signature

SECRET = "test-webhook-secret"


def _sign(secret, payload):
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def test_valid_signature_accepted():
    payload = b'{"event":"call_ended"}'
    assert verify_signature(SECRET, payload, _sign(SECRET, payload)) is True


def test_sha256_prefixed_header_accepted():
    payload = b'{"event":"x"}'
    assert verify_signature(SECRET, payload, "sha256=" + _sign(SECRET, payload)) is True


def test_wrong_secret_rejected():
    payload = b'{"event":"x"}'
    assert verify_signature(SECRET, payload, _sign("other", payload)) is False


def test_tampered_payload_rejected():
    good = _sign(SECRET, b'{"amount":1}')
    assert verify_signature(SECRET, b'{"amount":9999}', good) is False


def test_missing_secret_or_signature_fails_closed():
    payload = b"x"
    assert verify_signature(None, payload, _sign(SECRET, payload)) is False
    assert verify_signature(SECRET, payload, None) is False
    assert verify_signature("", payload, "abc") is False


def test_non_bytes_payload_rejected():
    assert verify_signature(SECRET, "not-bytes", "abc") is False
