import asyncio, glob, json, os, re, subprocess
import imageio_ffmpeg, edge_tts

FF = imageio_ffmpeg.get_ffmpeg_exe()
cfg = json.load(open("tvbuild/segments.json"))
src = glob.glob("art/**/*.mp4", recursive=True)[0]
os.makedirs("out", exist_ok=True)
os.makedirs("work", exist_ok=True)


def run(args):
    p = subprocess.run([FF, "-y", "-loglevel", "error"] + args, capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(p.stderr)


def dur(path):
    p = subprocess.run([FF, "-i", path], capture_output=True, text=True)
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


TV = ("[0:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,boxblur=24:2,"
      "eq=brightness=-0.18:saturation=0.6[bg];[0:v]scale=-2:540[fg];[bg][fg]overlay=(W-w)/2:0,fps=30,format=yuv420p[v]")
AUD = "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100,aformat=channel_layouts=stereo"


async def tts(text, path):
    for voice in (cfg["voice"], cfg["fallback_voice"]):
        try:
            c = edge_tts.Communicate(text, voice, rate=cfg["rate"], boundary="WordBoundary")
            words = []
            with open(path, "wb") as f:
                async for ch in c.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        words.append({"w": ch["text"], "s": ch["offset"] / 1e7,
                                      "e": (ch["offset"] + ch["duration"]) / 1e7})
            return words, voice
        except Exception as ex:
            print("voice failed", voice, ex)
    raise SystemExit("tts failed")


from faster_whisper import WhisperModel
model = WhisperModel("large-v3", device="cpu", compute_type="int8")

timeline, words, parts, t = [], [], [], 0.0
for i, sg in enumerate(cfg["segments"]):
    out = f"work/{i:02d}.mp4"
    if sg["type"] == "clip":
        run(["-ss", str(sg["start"]), "-to", str(sg["end"]), "-i", src, "-filter_complex", TV,
             "-map", "[v]", "-map", "0:a", "-af", AUD, "-c:v", "libx264", "-preset", "veryfast",
             "-crf", "20", "-c:a", "aac", "-b:a", "160k", out])
        wav = f"work/{i:02d}.wav"
        run(["-i", out, "-vn", "-ac", "1", "-ar", "16000", wav])
        segs, _ = model.transcribe(wav, language="pt", word_timestamps=True, beam_size=5)
        for s in segs:
            for w in s.words:
                words.append({"w": w.word.strip(), "s": round(t + w.start, 3), "e": round(t + w.end, 3), "seg": sg["id"]})
        voice = None
    else:
        mp3 = f"work/{i:02d}.mp3"
        ws, voice = asyncio.run(tts(sg["text"], mp3))
        d = dur(mp3) + 0.35
        still = f"work/{i:02d}.png"
        run(["-ss", str(sg["still"]), "-i", src, "-frames:v", "1", "-filter_complex", TV.replace(",fps=30,format=yuv420p", ""), "-map", "[v]", still])
        run(["-loop", "1", "-t", f"{d:.3f}", "-i", still, "-i", mp3, "-filter_complex",
             "[0:v]fps=30,format=yuv420p[v];[1:a]" + AUD + ",apad[a]", "-map", "[v]", "-map", "[a]",
             "-t", f"{d:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-c:a", "aac", "-b:a", "160k", out])
        for w in ws:
            words.append({"w": w["w"], "s": round(t + w["s"], 3), "e": round(t + w["e"], 3), "seg": sg["id"]})
    d = dur(out)
    timeline.append({"id": sg["id"], "type": sg["type"], "start": round(t, 3), "end": round(t + d, 3),
                     "src": [sg.get("start"), sg.get("end")], "text": sg.get("text"), "voice": voice})
    parts.append(out)
    t += d

with open("work/list.txt", "w") as f:
    for p in parts:
        f.write(f"file '{os.path.abspath(p)}'\n")
run(["-f", "concat", "-safe", "0", "-i", "work/list.txt", "-c:v", "libx264", "-preset", "veryfast",
     "-crf", "26", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "128k", "out/tv.mp4"])
run(["-i", src, "-vf", "scale=360:-2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "32",
     "-movflags", "+faststart", "-c:a", "aac", "-b:a", "96k", "out/original_light.mp4"])
json.dump({"total": round(t, 3), "timeline": timeline, "words": words}, open("out/timeline.json", "w"),
          ensure_ascii=False, indent=1)
print("total", t)
