import subprocess, json, numpy as np
from faster_whisper import WhisperModel
raw = subprocess.run(["ffmpeg","-nostdin","-v","error","-i","tmp/tr/audio.ogg","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
A = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
m = WhisperModel("medium", device="cpu", compute_type="int8")
out = []
for a, b in [(3.0, 13.0), (91.0, 106.5)]:
    segs, _ = m.transcribe(A[int(a*16000):int(b*16000)], language="pt", word_timestamps=True)
    for s in segs:
        for w in s.words: out.append([w.word.strip(), round(w.start + a, 2), round(w.end + a, 2)])
json.dump(out, open("tmp/nd/out/clipwords.json", "w"), ensure_ascii=False)
