import json, os, glob, subprocess, urllib.request
from faster_whisper import WhisperModel
os.makedirs("out/mark", exist_ok=True)
urls = json.load(open("mark.json"))
for k, u in urls.items():
    if u.startswith("parts:"):
        name, a, b = u[6:].split(":")
        raw = b"".join(open(p, "rb").read() for p in sorted(glob.glob(f"clips/{name}.mp4.part*")))
        open("/tmp/src.mp4", "wb").write(raw)
        subprocess.run(["ffmpeg","-v","error","-y","-ss",a,"-t",str(float(b)-float(a)),"-i","/tmp/src.mp4","-ac","1","-ar","16000",f"out/mark/{k}.wav"],check=True)
    else:
        open(f"out/mark/{k}.mp3", "wb").write(urllib.request.urlopen(u, timeout=60).read())
m = WhisperModel("medium", device="cpu", compute_type="int8")
for k, u in urls.items():
    f = f"out/mark/{k}.wav" if u.startswith("parts:") else f"out/mark/{k}.mp3"
    off = float(u.split(":")[2]) if u.startswith("parts:") else 0.0
    segs, _ = m.transcribe(f, language="pt", word_timestamps=True, beam_size=5)
    words = [{"w": w.word.strip(), "s": round(w.start + off, 3), "d": round(w.end - w.start, 3)} for s in segs for w in s.words]
    json.dump(words, open(f"out/mark/{k}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(k, len(words))
