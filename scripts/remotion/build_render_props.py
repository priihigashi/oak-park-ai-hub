#!/usr/bin/env python3
"""
build_render_props.py — Generate Remotion render props JSON from SRT + proof slides.
Outputs JSON to stdout (captured by render-video.yml).

Usage:
  python build_render_props.py \\
    --story-id SVG-202604171927 \\
    --language en \\
    --proof-slides '[...]' \\
    --srt-file /tmp/captions.srt \\
    [--translate]  # when language=pt, translates EN captions via Claude Haiku
"""

import argparse
import json
import os
import re
import sys


FPS = 30


def srt_time_to_frames(ts: str) -> int:
    """Convert SRT timestamp HH:MM:SS,mmm to frame number at 30fps."""
    hms, ms = ts.split(",")
    h, m, s = hms.split(":")
    total_sec = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return round(total_sec * FPS)


def parse_srt(srt_path: str) -> list:
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
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or not captions:
        return captions
    try:
        import urllib.request
        texts = [c["text"] for c in captions]
        prompt = (
            f"Translate these subtitle lines to Brazilian Portuguese. "
            f"Keep each line SHORT (subtitle length). Output ONLY a JSON array of strings, same order.\n\n"
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
            return [
                {**c, "text": t} for c, t in zip(captions, translated)
            ]
    except Exception as e:
        print(f"WARNING: caption translation failed: {e}", file=sys.stderr)
    return captions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--story-id", required=True)
    parser.add_argument("--language", choices=["en", "pt"], default="en")
    parser.add_argument("--proof-slides", default="[]")
    parser.add_argument("--video-start-frame", type=int, default=0)
    parser.add_argument("--total-frames", type=int, default=900)
    parser.add_argument("--srt-file", default="")
    parser.add_argument("--translate", action="store_true",
                        help="Translate captions to PT (use with --language pt)")
    args = parser.parse_args()

    captions = parse_srt(args.srt_file)
    if args.translate and args.language == "pt":
        captions = translate_captions(captions, "pt")

    proof_slides = json.loads(args.proof_slides) if args.proof_slides.strip() != "[]" else []

    props = {
        "videoSrc":         "./public/source_clip.mp4",
        "videoStartFrame":  args.video_start_frame,
        "proofSlides":      proof_slides,
        "captions":         captions,
        "language":         args.language,
        "totalFrames":      args.total_frames,
    }
    print(json.dumps(props, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
