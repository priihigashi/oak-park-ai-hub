#!/usr/bin/env python3
"""Moldura de repost (estilo vidro) em lote — sem tarja, sem coletânea.

  python render_frame.py <batch.json> <workdir>

batch.json: {"slug","page_tag","items":[{"drive_id","name"}]}; os arquivos já estão baixados em
<workdir>/src/<drive_id>.<ext>. Vídeo → MP4 1080×1920 com a moldura de vidro (a moldura segue a
proporção do vídeo). Imagem → PNG 1080×1920 com a mesma moldura. Também gera um frame .jpg de prévia
e a transcrição (faster-whisper) de cada vídeo em report.json.
"""
import json, os, sys, glob, subprocess
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = json.load(open(sys.argv[1])); WD = os.path.abspath(sys.argv[2]); OUT = os.path.join(WD, "out"); os.makedirs(OUT, exist_ok=True)
FPS = 30
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]
def sh(c): print("+", " ".join(c), flush=True); subprocess.run(c, check=True)
def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation:format=duration",
                        "-of", "json", p], capture_output=True, text=True); j = json.loads(r.stdout)
    st = j["streams"][0]; w, h = st["width"], st["height"]
    rot = abs(int(float(next((sd.get("rotation", 0) for sd in st.get("side_data_list", []) if "rotation" in sd), 0))))
    if rot in (90, 270): w, h = h, w
    return w, h, float(j.get("format", {}).get("duration", 0) or 0)
def has_audio(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", p], capture_output=True, text=True)
    return bool(r.stdout.strip())
def plate(spec, d):
    os.makedirs(d, exist_ok=True); sp = os.path.join(d, "specs.json"); json.dump([spec], open(sp, "w"), ensure_ascii=False)
    sh(["node", os.path.join(HERE, "plate.js"), sp, d]); return os.path.join(d, spec["id"] + ".png"), json.load(open(os.path.join(d, "slots.json")))[spec["id"]]
def mask(path, w, h, r=30):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); m.save(path)

report = []
_wm = None
for i, it in enumerate(JOB["items"], 1):
    src = (glob.glob(os.path.join(WD, "src", it["drive_id"] + ".*")) or [None])[0]
    base = os.path.splitext(it["name"])[0].replace(" ", "_")
    out_name = f"{i:02d}_{base}_frame"
    rec = {"i": i, "name": it["name"], "drive_id": it["drive_id"]}
    is_img = os.path.splitext(it["name"])[1].lower() in (".png", ".jpg", ".jpeg", ".webp")
    if is_img:
        im = Image.open(src); w, h = im.size
        bg, slot = plate({"id": f"p{i}", "mode": "main", "page_tag": JOB["page_tag"], "aspect": w / h, "scale": .80}, os.path.join(WD, f"pl{i}"))
        canvas = Image.open(bg).convert("RGBA"); pic = im.convert("RGB").resize((slot["w"], slot["h"]), Image.LANCZOS)
        mk = Image.new("L", (slot["w"], slot["h"]), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, slot["w"] - 1, slot["h"] - 1], 30, fill=255)
        canvas.paste(pic, (slot["x"], slot["y"]), mk); dst = os.path.join(OUT, out_name + ".png"); canvas.convert("RGB").save(dst)
        rec.update(kind="image", out=os.path.basename(dst), size=[w, h])
    else:
        w, h, dur = probe(src)
        bg, slot = plate({"id": f"p{i}", "mode": "main", "page_tag": JOB["page_tag"], "aspect": w / h, "scale": .80}, os.path.join(WD, f"pl{i}"))
        mk = os.path.join(WD, f"mask{i}.png"); mask(mk, slot["w"], slot["h"]); T = f"{dur:.3f}"
        aud = has_audio(src)
        inputs = ["-loop", "1", "-t", T, "-i", bg, "-i", src, "-loop", "1", "-t", T, "-i", mk]
        if not aud: inputs += ["-f", "lavfi", "-t", T, "-i", "anullsrc=r=48000:cl=stereo"]
        fc = (f"[1:v]scale={slot['w']}:{slot['h']}:force_original_aspect_ratio=increase,crop={slot['w']}:{slot['h']},setsar=1,format=rgba[v];"
              f"[2:v]format=gray,scale={slot['w']}:{slot['h']}[m];[v][m]alphamerge[rv];"
              f"[0:v][rv]overlay={slot['x']}:{slot['y']}:shortest=1,fps={FPS},format=yuv420p[o];"
              f"[{1 if aud else 3}:a]aresample=48000[a]")
        dst = os.path.join(OUT, out_name + ".mp4")
        sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[o]", "-map", "[a]", "-t", T, *ENC, dst])
        sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{min(2.0, dur / 3):.2f}", "-i", dst, "-frames:v", "1", "-vf", "scale=540:-2", "-q:v", "3", os.path.join(OUT, out_name + "_preview.jpg")])
        rec.update(kind="video", out=os.path.basename(dst), size=[w, h], dur=round(dur, 2), audio=aud)
        if aud:
            try:
                if _wm is None:
                    from faster_whisper import WhisperModel; _wm = WhisperModel("small", compute_type="int8")
                segs, _ = _wm.transcribe(src, language="pt", vad_filter=True)
                rec["transcript"] = [f"[{s.start:6.1f}] {s.text.strip()}" for s in segs]
            except Exception as e:
                rec["transcript_error"] = str(e)
    report.append(rec); print("DONE", rec.get("out"), flush=True)
json.dump(report, open(os.path.join(OUT, "report.json"), "w"), ensure_ascii=False, indent=1)
