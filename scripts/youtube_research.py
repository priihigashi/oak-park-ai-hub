#!/usr/bin/env python3
"""
youtube_research.py — General-purpose YouTube/Shorts/Reels research agent

Searches for recent videos on any topic, pulls transcripts (no download needed),
Claude analyzes each for technique, tools, quality, key takeaways.

Saves to:
  - Drive: Resources/Video Creation Flow/<topic>/ → raw transcripts + master findings doc
  - Sheet: Ideas & Inbox → 📥 Inspiration Library tab (one row per video)

Usage (local):
  python youtube_research.py --topic "kling ai talking head" --queries "kling ai tutorial 2025,kling 3.0 video" --max 5

GitHub Action: trigger via video-research.yml with workflow_dispatch
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime

try:
    import anthropic
except ImportError:
    os.system("pip install anthropic -q")
    import anthropic

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    os.system("pip install youtube-transcript-api -q")
    from youtube_transcript_api import YouTubeTranscriptApi

try:
    import yt_dlp
except ImportError:
    os.system("pip install yt-dlp -q")
    import yt_dlp

try:
    import gspread
    from google.oauth2 import service_account
except ImportError:
    os.system("pip install gspread google-auth -q")
    import gspread
    from google.oauth2 import service_account

import urllib.request
import urllib.parse

# ── CONFIG ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_SA_KEY     = os.environ.get("GOOGLE_SA_KEY", "")
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")
SHEET_ID          = "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU"
DRIVE_FOLDER_ID   = "1-QRf4xToJf_7cnS5UW7BiDUjd6lXot6o"  # Resources/Video Creation Flow
INSP_TAB          = "📥 Inspiration Library"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── YOUTUBE SEARCH ────────────────────────────────────────────────────────────
def search_youtube(query: str, max_results: int = 5) -> list[dict]:
    """Use yt-dlp to search YouTube, return list of {url, title, id, duration}"""
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "default_search": f"ytsearch{max_results}",
        "match_filter": yt_dlp.utils.match_filter_func("duration < 900"),  # max 15min
    }
    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            for entry in info.get("entries", []):
                if entry:
                    results.append({
                        "id": entry.get("id", ""),
                        "title": entry.get("title", ""),
                        "url": f"https://youtube.com/watch?v={entry.get('id','')}",
                        "duration": entry.get("duration", 0),
                        "uploader": entry.get("uploader", ""),
                        "upload_date": entry.get("upload_date", ""),
                    })
        except Exception as e:
            print(f"  Search error for '{query}': {e}")
    return results

# ── TRANSCRIPT ────────────────────────────────────────────────────────────────
def get_transcript(video_id: str) -> str:
    """Pull transcript via youtube-transcript-api (no download)"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "pt", "es"])
        return " ".join(t["text"] for t in transcript_list)
    except Exception as e:
        return f"[transcript unavailable: {e}]"

# ── CLAUDE ANALYSIS ───────────────────────────────────────────────────────────
def analyze_with_claude(video: dict, transcript: str, research_context: str) -> dict:
    """Claude analyzes a single video transcript for the research context"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""You are analyzing a YouTube video for research on: {research_context}

Video: "{video['title']}" by {video.get('uploader', 'unknown')}
URL: {video['url']}

TRANSCRIPT:
{transcript[:4000]}

Extract and return JSON with:
{{
  "summary": "2-3 sentence summary of what this video shows/teaches",
  "tools_used": ["list of AI tools, software, platforms mentioned"],
  "technique": "specific technique or workflow demonstrated",
  "quality_assessment": "honest assessment of result quality shown",
  "key_tips": ["up to 5 actionable tips extracted"],
  "use_case": "what this is best for (talking head / house tour / job site / etc)",
  "relevant_to_us": true/false,
  "relevance_reason": "why or why not relevant to Oak Park Construction / Hig Negocios",
  "watch_priority": "high / medium / low"
}}

Return only valid JSON, no markdown."""

    try:
        msg = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)
    except Exception as e:
        return {"summary": f"Analysis failed: {e}", "watch_priority": "low"}

# ── GOOGLE SHEETS ─────────────────────────────────────────────────────────────
def get_sheet():
    if not GOOGLE_SA_KEY:
        return None
    try:
        creds_dict = json.loads(GOOGLE_SA_KEY)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(creds)
        return gc.open_by_key(SHEET_ID)
    except Exception as e:
        print(f"  Sheet error: {e}")
        return None

def save_to_sheet(sheet, video: dict, analysis: dict, topic: str):
    try:
        ws = sheet.worksheet(INSP_TAB)
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            f"[VIDEO RESEARCH] {topic}",
            video["title"],
            video["url"],
            video.get("uploader", ""),
            analysis.get("summary", ""),
            ", ".join(analysis.get("tools_used", [])),
            analysis.get("technique", ""),
            analysis.get("quality_assessment", ""),
            analysis.get("watch_priority", ""),
            analysis.get("relevance_reason", ""),
        ]
        ws.append_row(row)
        print(f"  Saved to sheet: {video['title'][:50]}")
    except Exception as e:
        print(f"  Sheet save error: {e}")

# ── DRIVE UPLOAD ──────────────────────────────────────────────────────────────
def upload_to_drive(content: str, filename: str, folder_id: str, token: str):
    """Upload a text file to Drive using OAuth token"""
    if not token:
        print(f"  No Drive token — skipping upload of {filename}")
        return None
    
    metadata = json.dumps({
        "name": filename,
        "parents": [folder_id],
        "mimeType": "text/plain"
    }).encode()
    
    boundary = "boundary_xyz_123"
    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps({'name': filename, 'parents': [folder_id]})}\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: text/plain\r\n\r\n"
        f"{content}\r\n"
        f"--{boundary}--"
    ).encode()

    req = urllib.request.Request(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/related; boundary={boundary}",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            print(f"  Uploaded to Drive: {filename}")
            return result.get("id")
    except Exception as e:
        print(f"  Drive upload failed: {e}")
        return None

# ── MAIN ──────────────────────────────────────────────────────────────────────
def run(topic: str, queries: list[str], max_per_query: int = 5):
    print(f"\n=== VIDEO RESEARCH: {topic} ===")
    print(f"Queries: {queries}")
    print(f"Max per query: {max_per_query}\n")

    sheet = get_sheet()
    drive_token = os.environ.get("DRIVE_OAUTH_TOKEN", "")
    
    all_results = []
    seen_ids = set()

    for query in queries:
        print(f"\n--- Searching: {query} ---")
        videos = search_youtube(query, max_per_query)
        
        for video in videos:
            if video["id"] in seen_ids:
                continue
            seen_ids.add(video["id"])
            
            print(f"  [{video['id']}] {video['title'][:60]}")
            transcript = get_transcript(video["id"])
            
            if "[transcript unavailable" in transcript:
                print(f"    No transcript — skipping analysis")
                continue
            
            print(f"    Analyzing with Claude...")
            analysis = analyze_with_claude(video, transcript, topic)
            
            result = {**video, "analysis": analysis, "transcript_excerpt": transcript[:500]}
            all_results.append(result)
            
            if sheet:
                save_to_sheet(sheet, video, analysis, topic)
    
    # Build master findings doc
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    doc_lines = [
        f"# Research: {topic}",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Queries: {', '.join(queries)}",
        f"Videos analyzed: {len(all_results)}",
        "\n---\n",
    ]
    
    high = [r for r in all_results if r["analysis"].get("watch_priority") == "high"]
    if high:
        doc_lines.append("## HIGH PRIORITY FINDINGS\n")
        for r in high:
            doc_lines.append(f"### {r['title']}")
            doc_lines.append(f"URL: {r['url']}")
            doc_lines.append(f"Summary: {r['analysis'].get('summary','')}")
            doc_lines.append(f"Technique: {r['analysis'].get('technique','')}")
            doc_lines.append(f"Tools: {', '.join(r['analysis'].get('tools_used',[]))}")
            tips = r['analysis'].get('key_tips', [])
            if tips:
                doc_lines.append("Tips:")
                for tip in tips:
                    doc_lines.append(f"  - {tip}")
            doc_lines.append("")

    doc_lines.append("## ALL RESULTS\n")
    for r in all_results:
        doc_lines.append(f"**{r['title']}** [{r['analysis'].get('watch_priority','?')}]")
        doc_lines.append(f"  {r['url']}")
        doc_lines.append(f"  {r['analysis'].get('summary','')}")
        doc_lines.append("")

    doc_content = "\n".join(doc_lines)
    filename = f"research_{topic.replace(' ','_')}_{timestamp}.txt"
    
    print(f"\nSaving master findings doc: {filename}")
    if drive_token:
        upload_to_drive(doc_content, filename, DRIVE_FOLDER_ID, drive_token)
    else:
        # Save locally as artifact for GitHub Actions
        with open(f"/tmp/{filename}", "w") as f:
            f.write(doc_content)
        print(f"  Saved locally to /tmp/{filename} (no Drive token)")
    
    print(f"\n✅ Done. {len(all_results)} videos analyzed.")
    return all_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True, help="Research topic label (e.g. 'kling ai talking head')")
    parser.add_argument("--queries", required=True, help="Comma-separated search queries")
    parser.add_argument("--max", type=int, default=5, help="Max results per query")
    args = parser.parse_args()
    
    queries = [q.strip() for q in args.queries.split(",")]
    run(args.topic, queries, args.max)
