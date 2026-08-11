"""
Content Creator V2 — scene extraction (Sprint 2).
Splits a video into scenes, extracts one keyframe per scene,
and optionally transcribes each segment using Whisper.

Coding order step 3 of 10.
Master plan: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from .contracts import MediaAsset, Scene


_SCENE_THRESHOLD = 0.30   # FFmpeg scene-change score (0.0–1.0); raise to merge short cuts
_MIN_SCENE_SECONDS = 1.5  # drop scenes shorter than this
_MAX_SCENES = 200          # safety cap — avoids runaway on very choppy footage
_KEYFRAME_OFFSET = 0.2    # fraction into the scene for the keyframe (20% = skip the cut)


def detect_scenes(
    asset: MediaAsset,
    *,
    threshold: float = _SCENE_THRESHOLD,
) -> list[tuple[float, float]]:
    """
    Run FFmpeg scene detection and return (start, end) second pairs.
    Uses the 'select' filter with 'showinfo' to read scene-change timestamps
    from stderr — no third-party library required.
    Fallback: if no cuts are detected, the whole video is returned as one scene.
    """
    if asset.duration is None or asset.duration <= 0:
        return []

    cmd = [
        "ffmpeg", "-hide_banner",
        "-i", asset.path,
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-vsync", "vfr",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    timestamps: list[float] = [0.0]
    for m in re.finditer(r"pts_time:([\d.]+)", result.stderr):
        ts = float(m.group(1))
        if ts > timestamps[-1] + _MIN_SCENE_SECONDS:
            timestamps.append(ts)

    duration = asset.duration
    pairs: list[tuple[float, float]] = []
    for i, start in enumerate(timestamps):
        end = timestamps[i + 1] if i + 1 < len(timestamps) else duration
        if end - start >= _MIN_SCENE_SECONDS:
            pairs.append((round(start, 3), round(end, 3)))
        if len(pairs) >= _MAX_SCENES:
            break

    return pairs or [(0.0, round(duration, 3))]


def extract_keyframe(video_path: str, timestamp: float, output_dir: Path) -> str:
    """
    Seek to `timestamp` seconds in the video and save one frame as PNG.
    Returns the absolute path to the PNG.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{uuid.uuid4().hex}.png"
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-ss", str(timestamp),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, timeout=60)
    return str(out_path)


def _quality_signals(keyframe_path: str) -> dict:
    """
    Compute blur score and brightness from a keyframe PNG using Pillow.
    Returns an empty dict if Pillow is not installed.

    blur_score: variance of pixel values in grayscale (higher = sharper).
    brightness: mean pixel value normalised to 0.0–1.0.
    """
    try:
        import statistics
        from PIL import Image

        img = Image.open(keyframe_path).convert("L")
        pixels = list(img.getdata())
        mean = sum(pixels) / len(pixels)
        return {
            "blur_score": float(statistics.variance(pixels, mean)),
            "brightness": round(mean / 255.0, 4),
        }
    except Exception:
        return {}


def _whisper_segment(
    video_path: str,
    start: float,
    end: float,
    *,
    model: str = "base",
) -> Optional[str]:
    """
    Export the audio from [start, end] and run Whisper on it.
    Tries 'whisper-mlx' first (faster on Apple Silicon), then 'whisper'.
    Returns raw JSON string from Whisper or None on failure.
    """
    whisper_bin = shutil.which("whisper-mlx") or shutil.which("whisper")
    if not whisper_bin:
        return None

    duration = end - start
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_wav = Path(tmp_dir) / "segment.wav"
        # Export mono 16 kHz WAV — the format Whisper expects
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", str(start), "-t", str(duration),
            "-i", video_path,
            "-ar", "16000", "-ac", "1",
            "-f", "wav", str(tmp_wav), "-y",
        ], check=True, timeout=120)

        result = subprocess.run([
            whisper_bin, str(tmp_wav),
            "--model", model,
            "--output_format", "json",
            "--output_dir", tmp_dir,
        ], capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return None

        json_path = tmp_wav.with_suffix(".json")
        if json_path.exists():
            return json_path.read_text(encoding="utf-8")
        return None


def extract_scenes(
    asset: MediaAsset,
    keyframe_dir: Path,
    *,
    threshold: float = _SCENE_THRESHOLD,
    transcribe: bool = False,
    whisper_model: str = "base",
) -> list[Scene]:
    """
    Detect scenes in `asset`, extract one keyframe per scene, compute quality
    signals, and optionally transcribe each segment with Whisper.

    Args:
        asset:          MediaAsset returned by ffprobe.extract().
        keyframe_dir:   Directory where PNG keyframes will be written.
        threshold:      FFmpeg scene-change sensitivity (0.0–1.0, default 0.30).
        transcribe:     Set True to run Whisper on each scene. Adds ~2–5 s per
                        scene on M3 Mac with 'base' model. Leave False when
                        only building the visual index.
        whisper_model:  Whisper model size ('tiny', 'base', 'small', …).

    Returns:
        List of Scene dataclasses ready to be passed to catalog.upsert_scene().
    """
    pairs = detect_scenes(asset, threshold=threshold)
    scenes: list[Scene] = []

    for start, end in pairs:
        kf_ts = start + (end - start) * _KEYFRAME_OFFSET
        keyframe_paths: list[str] = []
        quality: dict = {}

        try:
            kf_path = extract_keyframe(asset.path, kf_ts, keyframe_dir)
            keyframe_paths = [kf_path]
            quality = _quality_signals(kf_path)
        except Exception:
            pass

        transcript: Optional[str] = None
        if transcribe and (end - start) >= 0.5:
            try:
                transcript = _whisper_segment(
                    asset.path, start, end, model=whisper_model
                )
            except Exception:
                pass

        scenes.append(Scene(
            scene_id=str(uuid.uuid4()),
            asset_id=asset.asset_id,
            start_time=start,
            end_time=end,
            transcript=transcript,
            keyframe_paths=keyframe_paths,
            quality_signals=quality,
        ))

    return scenes
