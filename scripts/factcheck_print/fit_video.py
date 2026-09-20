"""Fit a video into the Instagram-carousel limit (60 s): keep the sentences that carry the checked claims, speed up <= 1.25x.

Learned 2026-09-19 (INSS deck): a tightly edited speaker has almost no silence (2.2 s of 213 s), so silence removal
alone does nothing. The lever is SEGMENT SELECTION (keep the claim sentences), then a comfortable speed-up (1.2x).
"""
import json
import subprocess

LIMIT = 60.0
SPEED = 1.2
MAX_SPEED = 1.25


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:  # ffprobe missing: read it from ffmpeg's banner
        err = subprocess.run(["ffmpeg", "-i", str(path)], capture_output=True, text=True).stderr
        h, m, s = err.split("Duration:")[1].split(",")[0].strip().split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)


def whisper_segments(path):
    """[(start, end, text)] with real timestamps (faster-whisper is already installed for capture)."""
    from faster_whisper import WhisperModel
    segs, _ = WhisperModel("base", device="cpu", compute_type="int8").transcribe(str(path), language="pt", vad_filter=True)
    return [(round(s.start, 2), round(s.end, 2), s.text.strip()) for s in segs]


def _valid(picks, segs, budget):
    ends = {round(b, 2) for _, b, _ in segs}
    starts = {round(a, 2) for a, _, _ in segs}
    ok = all(round(a, 2) in starts and round(b, 2) in ends and b > a for a, b in picks)
    return ok and picks == sorted(picks) and sum(b - a for a, b in picks) <= budget + 1.5


def _fallback(segs, budget):
    picks, used = [], 0.0
    for a, b, _ in segs:
        if used + (b - a) > budget:
            break
        picks.append((a, b))
        used += b - a
    return picks


def choose_segments(segs, claims, budget, ask):
    """Ask the model which whole segments to keep; validate; fall back to 'first N seconds'."""
    listing = "\n".join(f"{a:.2f}-{b:.2f} {t}" for a, b, t in segs)
    reply = ask(f"""Video transcript with timestamps:\n{listing}\n\nChecked claims (their sentences MUST stay):\n""" +
                "\n".join(f"- {c}" for c in claims) +
                f"""\n\nPick WHOLE segments (use the exact start/end numbers above) so the kept total is <= {budget:.0f} seconds.
Keep the hook, the claim sentences and their key numbers; drop explainer repetition and the outro/CTA. Keep chronological order.
Return JSON only: {{"keep": [[start, end], ...]}}""")
    try:
        picks = [tuple(x) for x in json.loads(reply[reply.index("{"):reply.rindex("}") + 1])["keep"]]
        if _valid(picks, segs, budget):
            return picks
    except (ValueError, KeyError, TypeError):
        pass
    return _fallback(segs, budget)


def merge_touching(picks):
    out = [list(picks[0])]
    for a, b in picks[1:]:
        if abs(a - out[-1][1]) < 0.05:
            out[-1][1] = b
        else:
            out.append([a, b])
    return out


def render(src, dst, picks, speed):
    m = merge_touching(picks)
    fc = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];" for i, (a, b) in enumerate(m))
    fc += "".join(f"[v{i}][a{i}]" for i in range(len(m))) + f"concat=n={len(m)}:v=1:a=1[v][a];[v]setpts=PTS/{speed}[vo];[a]atempo={speed}[ao]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]",
                    "-c:v", "libx264", "-crf", "30", "-preset", "medium", "-c:a", "aac", "-b:a", "56k", "-movflags", "+faststart", str(dst)], check=True)


def fit_to_limit(src, dst, claims, ask, limit=LIMIT, speed=SPEED):
    """Returns dict(duration_in, duration_out, kept, speed, fitted). Never exceeds `limit` (drops to MAX_SPEED then trims)."""
    dur = probe_duration(src)
    if dur <= limit:
        return {"duration_in": dur, "duration_out": dur, "fitted": False}
    picks = choose_segments(whisper_segments(src), claims, limit * speed, ask)
    render(src, dst, picks, speed)
    out = probe_duration(dst)
    if out > limit:  # last resort: comfortable max speed, same cut
        render(src, dst, picks, MAX_SPEED)
        out = probe_duration(dst)
    return {"duration_in": dur, "duration_out": out, "kept": [list(p) for p in picks], "speed": speed, "fitted": True}
