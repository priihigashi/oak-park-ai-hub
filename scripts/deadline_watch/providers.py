"""Read-only mailbox providers for Gmail and Outlook through existing credentials."""

from __future__ import annotations

import base64
import json
import os
import urllib.request
from datetime import datetime
from email.utils import parsedate_to_datetime

from .core import Message


def _text(payload: dict) -> str:
    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data + "===").decode("utf-8", "replace")
    return "\n".join(_text(part) for part in payload.get("parts", []))


def gmail_messages(hours: int = 36) -> list[Message]:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    token = json.loads(os.environ["SHEETS_TOKEN"])
    creds = Credentials(
        token=token.get("token"), refresh_token=token.get("refresh_token"),
        token_uri=token.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token.get("client_id"), client_secret=token.get("client_secret"),
        scopes=token.get("scopes"),
    )
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    response = service.users().messages().list(userId="me", q=f"newer_than:{max(1, hours // 24 + 1)}d", maxResults=100).execute()
    results = []
    for item in response.get("messages", []):
        raw = service.users().messages().get(userId="me", id=item["id"], format="full").execute()
        headers = {h["name"].lower(): h["value"] for h in raw.get("payload", {}).get("headers", [])}
        received = parsedate_to_datetime(headers.get("date", ""))
        results.append(Message(
            mailbox="opc_gmail", message_id=item["id"], sender=headers.get("from", ""),
            subject=headers.get("subject", ""), body=_text(raw.get("payload", {})),
            received_at=received, source_url=f"https://mail.google.com/mail/u/0/#all/{item['id']}",
        ))
    return results


def _post(url: str, api_key: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def _query_outlook(api_key: str, account_id: str, folder: str, sender: str) -> list[dict]:
    payload = {
        "connected_account_id": account_id,
        "arguments": {
            "folder": folder,
            "filter": f"from/emailAddress/address eq '{sender}'",
            "select": ["id", "subject", "receivedDateTime", "isRead", "from", "bodyPreview", "webLink"],
            "top": 100,
        },
    }
    data = _post(
        "https://backend.composio.dev/api/v3.1/tools/execute/OUTLOOK_QUERY_EMAILS?toolkit_versions=latest",
        api_key,
        payload,
    )
    if data.get("successful") is False:
        raise RuntimeError(f"OUTLOOK_QUERY_EMAILS failed: {data.get('error', 'unknown error')}")
    result = data.get("data", data)
    if isinstance(result, dict) and isinstance(result.get("data"), dict):
        result = result["data"]
    return result.get("value", result.get("messages", [])) if isinstance(result, dict) else result


def outlook_messages(hours: int = 36) -> list[Message]:
    api_key = os.environ["COMPOSIO_KEY"]
    account_id = os.environ["DEADLINE_OUTLOOK_ALIAS"]
    senders = [item.lower() for item in json.loads(os.environ["DEADLINE_ALLOWED_SENDERS_JSON"]) if "@" in item]
    if not senders:
        raise RuntimeError("Outlook requires at least one exact sender address")
    items = []
    for folder in ("inbox", "junkemail"):
        for sender in senders:
            items.extend(_query_outlook(api_key, account_id, folder, sender))
    messages = []
    for item in items:
        sender = item.get("from", {}).get("emailAddress", {}).get("address", "")
        messages.append(Message(
            mailbox="hotmail", message_id=item["id"], sender=sender,
            subject=item.get("subject", ""), body=item.get("bodyPreview", ""),
            received_at=datetime.fromisoformat(item["receivedDateTime"].replace("Z", "+00:00")),
            source_url=item.get("webLink", ""),
        ))
    return messages
