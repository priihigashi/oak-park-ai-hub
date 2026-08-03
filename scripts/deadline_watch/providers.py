"""Read-only mailbox providers for Gmail and Outlook through existing credentials."""

from __future__ import annotations

import base64
import json
import os
import urllib.parse
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


def _request(url: str, api_key: str) -> dict:
    request = urllib.request.Request(url, headers={"x-api-key": api_key, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def _post(url: str, api_key: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def _outlook_account(api_key: str, alias: str) -> str:
    query = urllib.parse.urlencode({"toolkit_slugs": "outlook", "statuses": "ACTIVE"})
    data = _request(f"https://backend.composio.dev/api/v3.1/connected_accounts?{query}", api_key)
    accounts = data.get("items", data.get("connected_accounts", []))
    matches = [a for a in accounts if a.get("id") == alias or a.get("alias") == alias]
    if len(matches) != 1:
        raise RuntimeError(f"expected one active Outlook account for alias; found {len(matches)}")
    return matches[0]["id"]


def outlook_messages(hours: int = 36) -> list[Message]:
    api_key = os.environ["COMPOSIO_KEY"]
    account_id = _outlook_account(api_key, os.environ["DEADLINE_OUTLOOK_ALIAS"])
    payload = {
        "connected_account_id": account_id,
        "endpoint": "/v1.0/me/messages",
        "method": "GET",
        "parameters": [
            {"name": "$top", "value": "100", "in": "query"},
            {"name": "$select", "value": "id,subject,from,receivedDateTime,bodyPreview,webLink", "in": "query"},
            {"name": "$orderby", "value": "receivedDateTime desc", "in": "query"},
        ],
    }
    data = _post("https://backend.composio.dev/api/v3.1/tools/execute/proxy", api_key, payload)
    upstream = data.get("data", data)
    items = upstream.get("value", upstream.get("data", {}).get("value", []))
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

