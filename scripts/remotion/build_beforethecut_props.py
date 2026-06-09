#!/usr/bin/env python3
"""
build_beforethecut_props.py — Generate Remotion render props JSON for FORMAT-025
"Before The Cut" (deceptive-edit debunk reel). Outputs JSON to stdout (captured by
render-beforethecut.yml).

MANUAL MVP: the original-clip sourcing/alignment is supplied by hand (workflow inputs).
The AUTO original_source_finder is a separate Phase-2 module — NOT built yet.

Mirrors build_render_props.py patterns (SRT parse, PT translation via Haiku) but for
the dual-video BeforeTheCut composition.

Usage:
  python build_beforethecut_props.py \\
    --story-id NWS-2026... --language pt \\
    --original-start-frame 0 --reveal-frame 150 --total-frames 900 \\
    --hook "Cortaram o começo deste vídeo." \\
    --context-text "Ele falava sobre X quando..." \\
    --source-label "Fonte: TV Câmara — 14:32" \\
    --creator-handle someaccount \\
    [--srt-file /tmp/original_captions.srt] [--translate]
"""

import argparse
import json
import os
import re
import sys

FPS = 30

# Local file names the workflow drops into scripts/remotion/public/ before render.
MANIPULATED_SRC = "./public/manipulated.mp4"
ORIGINAL_SRC = "./public/original.mp4"


def srt_time_to_frames(ts: str) -> int:
    """Convert SRT timestamp HH:MM:SS,mmm to frame number at 30fps."""
    hms, ms = ts.split(",")
    h, m, s = hms.split(":")
    total_sec = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return round(total_sec * FPS)


def parse_srt(srt_path: str) -> list:
    """Parse an SRT into phase-2-local CaptionEntry list.

    Captions describe the ORIGINAL clip. The original plays from frame 0 of the
    downloaded window in phase 2, so SRT frames map directly to phase-2-local frames.
    """
    if not srt_path or not os.path.exists(srt_path):
        return []
    with open(srt_path, encoding="utf-8") as f:
        content = f.read()
    blocks = re.split(r"\n\n+", content.strip())
    captions = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        match = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})", lines[1]
        )
        if not match:
            continue
        captions.append({
            "startFrame": srt_time_to_frames(match.group(1)),
            "endFrame":   srt_time_to_frames(match.group(2)),
            "text":       " ".join(lines[2:]).strip(),
        })
    return captions


def translate_captions(captions: list, target_lang: str = "pt") -> list:
    """Translate caption text to target language via Claude Haiku. Non-fatal if fails."""
    api_key = os.environ.get("CLAUDE_KEY_4_CONTENT", "")
    if not api_key or not captions:
        return captions
    try:
        import urllib.request
        texts = [c["text"] for c in captions]
        prompt = (
            "Translate these subtitle lines to Brazilian Portuguese. "
            "Keep each line SHORT (subtitle length). Output ONLY a JSON array of strings, same order.\n\n"
            + json.dumps(texts)
        )
        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
        translated = json.loads(resp["content"][0]["text"])
        if len(translated) == len(captions):
            return [{**c, "text": t} for c, t in zip(captions, translated)]
    except Exception as e:
        print(f"WARNING: caption translation failed: {e}", file=sys.stderr)
    return captions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--story-id", required=True)
    parser.add_argument("--language", choices=["en", "pt"], default="pt")
    parser.add_argument("--original-start-frame", type=int, default=0,
                        help="Playback offset inside original.mp4. Default 0 — preroll is "
                             "baked into the yt-dlp --download-sections window.")
    parser.add_argument("--reveal-frame", type=int, default=150,
                        help="Frame when the split appears (default 150 = 5s, after hook).")
    parser.add_argument("--total-frames", type=int, default=900)
    parser.add_argument("--hook", default="")
    parser.add_argument("--context-text", default="",
                        help="Plain-language 'what they were actually talking about'.")
    parser.add_argument("--source-label", default="",
                        help="e.g. 'Fonte: TV Câmara — 14:32'")
    parser.add_argument("--creator-handle", default="",
                        help="Handle that posted the manipulated cut (shown on phase-1 chip).")
    parser.add_argument("--srt-file", default="",
                        help="Optional SRT of the ORIGINAL clip (phase-2 captions).")
    parser.add_argument("--translate", action="store_true",
                        help="Translate captions to PT (use with --language pt).")
    args = parser.parse_args()

    captions = parse_srt(args.srt_file)
    if args.translate and args.language == "pt":
        captions = translate_captions(captions, "pt")

    props = {
        "manipulatedSrc":     MANIPULATED_SRC,
        "originalSrc":        ORIGINAL_SRC,
        "originalStartFrame": args.original_start_frame,
        "revealFrame":        args.reveal_frame,
        "totalFrames":        args.total_frames,
        "hook":               args.hook,
        "contextText":        args.context_text,
        "captions":           captions,
        "language":           args.language,
        "creatorHandle":      args.creator_handle or None,
        "sourceLabel":        args.source_label,
    }
    # strip None — Remotion ignores missing optional props cleanly
    props = {k: v for k, v in props.items() if v is not None}
    print(json.dumps(props, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
