#!/usr/bin/env python3
"""
email_preview.py — Sends preview email with all 3 variant covers for each post.
Priscila replies "black approved" or gives feedback.
"""
import json, os, base64, urllib.request, urllib.parse, time
from pathlib import Path

SHEET_ID = os.environ.get("CONTENT_SHEET_ID", "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU")
CATALOG_TAB = "📸 Project Content Catalog"


def get_token():
    raw = os.environ.get("SHEETS_TOKEN", "")
    if not raw:
        raise RuntimeError("No SHEETS_TOKEN set")
    td = json.loads(raw)
    data = urllib.parse.urlencode({
        "client_id": td["client_id"],
        "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)).read())
    return resp["access_token"], td


def make_cover_thumbnails_public(folder_id, token):
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials

    creds = Credentials(token=token)
    drive = build("drive", "v3", credentials=creds)

    files = drive.files().list(
        q=f"'{folder_id}' in parents and trashed=false and name contains '_01_cover'",
        supportsAllDrives=True, includeItemsFromAllDrives=True,
        fields="files(id,name,webContentLink)",
    ).execute().get("files", [])

    urls = {}
    for f in files:
        try:
            drive.permissions().create(
                fileId=f["id"], supportsAllDrives=True,
                body={"type": "anyone", "role": "reader"},
            ).execute()
        except Exception:
            pass
        name = f["name"].lower()
        variant = "black" if "black" in name else "cream" if "cream" in name else "lime"
        urls[variant] = f"https://drive.google.com/uc?id={f['id']}&export=download"

    return urls


def _build_reply_guide(post):
    cv = post.get("cover_visual", {})
    people = post.get("mentioned_people", [])
    clips = post.get("clip_suggestions", [])
    topic = post.get("topic", "")

    # Cover visual options
    opt_a = cv.get("option_a", {})
    opt_b = cv.get("option_b", {})
    opt_c = cv.get("option_c", {})
    recommended = cv.get("recommended", "?")
    rec_reason = cv.get("reason", "")
    subject_type = cv.get("subject_type", "unknown")

    cover_block = ""
    if cv:
        a_query = opt_a.get("search_query", "search Wikimedia Commons / Agência Brasil")
        b_prompt = opt_b.get("prompt", "")[:100]
        b_tool = opt_b.get("tool_hint", "seedream")
        c_concept = opt_c.get("concept", "typography + color block")
        cover_block = f"""COVER IMAGE — subject: {subject_type}
  A) CC photo    → search: "{a_query}"
  B) AI generate → tool: {b_tool}
               prompt: "{b_prompt}"
  C) Graphic design only → {c_concept}
  → recommended: {recommended.upper()} ({rec_reason})
  → MY PICK: ___"""
    else:
        cover_block = """COVER IMAGE:
  A) CC photo    → search: ___________________________
  B) AI generate → tool: openai / seedream / nb2
               prompt: ___________________________
  C) Graphic design only
  → MY PICK: ___"""

    # Named people block
    if people:
        people_list = "\n  ".join(f"[ ] {p} → initials card / AI portrait (seedream) / CC photo URL: ___" for p in people)
        people_block = f"NAMED PEOPLE — add face to slide:\n  {people_list}"
    else:
        people_block = "NAMED PEOPLE: none detected — check slides manually if someone is named"

    # Clip suggestions
    clips_block = ""
    if clips:
        clip_lines = "\n  ".join(f"Slide {c.get('slide','?')}: \"{c.get('youtube_query','')}\" ({c.get('duration_hint','')})" for c in clips[:3])
        clips_block = f"\nYOUTUBE CLIPS (short, for relevant slides):\n  {clip_lines}\n  → ADD / SKIP: ___"

    guide_text = f"""── REPLY GUIDE: {topic[:55]} ──

APPROVE (approval_handler → parse_reply):
  black approved  /  cream approved  /  lime approved  /  not ready

COVER IMAGE (carousel_builder → cover_visual  |  subject: {subject_type}):
  A) Real photo → search: "{opt_a.get("search_query", "Wikimedia Commons / Agência Brasil CC")}"
  B) AI generate → {opt_b.get("tool_hint","seedream")}: "{opt_b.get("prompt","")[:80]}"
  C) No photo — graphic design only
  Recommended: {recommended.upper()} — {rec_reason}
  My pick: ___

FACES (carousel_builder → mentioned_people  |  html → .bio-card):
  People named in slides: {", ".join(people) if people else "none detected — check manually"}
  → initials card  /  AI portrait (seedream)  /  I'll send photo
  Who needs what: ___

SLIDE IMAGES (carousel_builder → visual_hint / context_image_query):
  Slide ___ missing → show: ___  tool: openai / seedream / nb2
  Slide ___ missing → show: ___  tool: ___
  Screenshot/receipt needed on slide: ___
{clips_block}
TEXT FIX (carousel_builder → slides[N]):
  Slide ___ → change to: "___"

skip this post  /  other: ___
── END ──"""

    return f"""
    <tr><td colspan="3" style="padding:0 8px 20px;">
      <div style="background:#111111;border-left:3px solid #CBCC10;border-radius:0 4px 4px 0;padding:16px 20px;margin-top:8px;">
        <div style="font-family:monospace;font-size:11px;color:#CBCC10;font-weight:bold;margin-bottom:10px;letter-spacing:1px;">REPLY GUIDE — copy below, fill in, send as reply</div>
        <pre style="margin:0;white-space:pre-wrap;font-family:'Courier New',monospace;font-size:12px;color:#cccccc;line-height:1.6;">{guide_text}</pre>
      </div>
    </td></tr>"""


def build_preview_html(posts):
    rows = ""
    for post in posts:
        covers = post.get("cover_urls", {})
        topic = post.get("topic", "Untitled")
        niche = post.get("niche", "").upper()
        post_id = post.get("post_id", "")

        img_cells = ""
        for variant in ["black", "cream", "lime"]:
            url = covers.get(variant, "")
            if url:
                img_cells += f"""
                <td style="padding:8px;text-align:center;">
                  <img src="{url}" width="200" style="border:2px solid #333;border-radius:4px;"/><br/>
                  <span style="font-family:monospace;font-size:14px;color:#CBCC10;">{variant}</span>
                </td>"""
            else:
                img_cells += f'<td style="padding:8px;text-align:center;color:#666;">no {variant}</td>'

        rows += f"""
        <tr><td colspan="3" style="padding:16px 8px 4px;font-family:sans-serif;font-size:18px;font-weight:bold;color:#F0EBE3;border-top:1px solid #333;">
          [{niche}] {topic}<br/>
          <span style="font-size:12px;color:#888;font-weight:normal;">ID: {post_id} | Static: <a href="{post.get('static_link','')}" style="color:#CBCC10;">folder</a> | Motion: <a href="{post.get('motion_link','')}" style="color:#CBCC10;">folder</a></span>
        </td></tr>
        <tr>{img_cells}</tr>
        {_build_reply_guide(post)}"""

    return f"""<html><body style="background:#0A0A0A;padding:24px;">
    <h1 style="font-family:sans-serif;color:#CBCC10;margin-bottom:4px;">Daily Content Preview</h1>
    <p style="font-family:sans-serif;color:#ccc;margin-top:0;">See the REPLY GUIDE below each post — copy, fill in what's missing, send as reply.</p>
    <table style="border-collapse:collapse;width:100%;">{rows}</table>
    <p style="font-family:monospace;color:#555;font-size:11px;margin-top:24px;">
      Auto-generated by content_creator pipeline · Oak Park AI Hub
    </p>
    </body></html>"""


def send_preview(posts, date_str):
    html = build_preview_html(posts)
    subject = f"DAILY CONTENT — {date_str} — approve or change"

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    gmail_user = "priscila@oakpark-construction.com"
    gmail_pass = os.environ.get("PRI_OP_GMAIL_APP_PASSWORD", "")

    if not gmail_pass:
        print("  No Gmail app password — falling back to send_email workflow trigger")
        return _send_via_workflow(subject, html)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg["X-Content-Creator-Batch"] = date_str
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, gmail_user, msg.as_string())

    print(f"  Preview email sent: {subject}")
    return True


def _send_via_workflow(subject, html_body):
    gh_token = os.environ.get("GH_TOKEN", "")
    if not gh_token:
        print("  No GH_TOKEN — cannot send email")
        return False

    payload = json.dumps({
        "ref": "main",
        "inputs": {
            "to": "priscila@oakpark-construction.com",
            "subject": subject,
            "html_body": html_body[:60000],
        },
    }).encode()

    req = urllib.request.Request(
        "https://api.github.com/repos/priihigashi/oak-park-ai-hub/actions/workflows/send_email.yml/dispatches",
        data=payload,
        headers={
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    urllib.request.urlopen(req)
    print(f"  Preview email triggered via send_email.yml")
    return True


def update_catalog_status(post_id, status="pending_approval"):
    token, td = get_token()
    enc = urllib.parse.quote(f"'{CATALOG_TAB}'!A:M", safe="!:'")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{enc}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    rows = json.loads(urllib.request.urlopen(req).read()).get("values", [])

    for i, row in enumerate(rows):
        if len(row) > 0 and row[0].strip() == post_id:
            cell = f"'{CATALOG_TAB}'!M{i+1}"
            enc2 = urllib.parse.quote(cell, safe="!:'")
            url2 = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{enc2}?valueInputOption=USER_ENTERED"
            payload = json.dumps({"values": [[status]]}).encode()
            req2 = urllib.request.Request(url2, data=payload, method="PUT",
                                         headers={"Authorization": f"Bearer {token}",
                                                   "Content-Type": "application/json"})
            urllib.request.urlopen(req2)
            print(f"  Catalog updated: {post_id} → {status}")
            return
