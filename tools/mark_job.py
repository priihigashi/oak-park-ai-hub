import json, os, urllib.request
from faster_whisper import WhisperModel
os.makedirs("out/mark", exist_ok=True)
urls = json.load(open("mark.json"))
for k, u in urls.items():
    open(f"out/mark/{k}.mp3", "wb").write(urllib.request.urlopen(u, timeout=60).read())
m = WhisperModel("medium", device="cpu", compute_type="int8")
for k in urls:
    segs, _ = m.transcribe(f"out/mark/{k}.mp3", language="pt", word_timestamps=True, beam_size=5)
    words = [{"w": w.word.strip(), "s": round(w.start, 3), "d": round(w.end - w.start, 3)} for s in segs for w in s.words]
    json.dump(words, open(f"out/mark/{k}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(k, len(words))
