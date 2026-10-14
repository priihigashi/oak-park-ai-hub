#!/usr/bin/env python3
"""Repost renderer — vídeo de outra página + tarja discreta de referência + coletânea dos clipes reais.

Usado pelo workflow .github/workflows/repost_render.yml. Nada de mídia de terceiros entra no repo:
tudo é baixado no runner e sobe só pro Drive.

  python render.py <job.json> <workdir>

Saídas em <workdir>/out/: reel_com_tarja.mp4, reel_sem_tarja.mp4, sheet_*.jpg, clips_report.json
"""
import json, os, re, subprocess, sys, unicodedata, glob, shutil, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

JOB = json.load(open(sys.argv[1]))
WD = os.path.abspath(sys.argv[2]); os.makedirs(WD, exist_ok=True)
OUT = os.path.join(WD, "out"); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
INK, PAPER, GOLD, SLATE, RED = "#0E0D0B", "#F2ECE0", "#C9A84C", "#3B5470", "#C8352B"
F = {
    "anton": "fonts/Anton-Regular.ttf",
    "bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "xbold": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "med": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "mono": "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
}
for k, p in list(F.items()):
    if not os.path.isabs(p) or not os.path.exists(p):
        hits = glob.glob(os.path.join(WD, "fonts", os.path.basename(p))) + glob.glob(f"/usr/share/fonts/**/{os.path.basename(p)}", recursive=True)
        F[k] = hits[0] if hits else p

def font(k, s): return ImageFont.truetype(F[k], s)
def sh(cmd, check=True):
    print("+", cmd if isinstance(cmd, str) else " ".join(cmd), flush=True)
    return subprocess.run(cmd, shell=isinstance(cmd, str), check=check, capture_output=False)
def probe_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)
def norm(s):
    s = unicodedata.normalize("NFKD", s.lower()); return "".join(c for c in s if not unicodedata.combining(c))

ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]

# ---------------------------------------------------------------- main video
def prep_main():
    src = os.path.join(WD, "main_src.mp4")
    dst = os.path.join(WD, "main.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf",
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={FPS}",
        "-af", "aresample=48000", *ENC, dst])
    return dst

# ---------------------------------------------------------------- lower third (discreto)
def lower_third_png(lt, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fk, fw, fq = font("mono", 21), font("bold", 29), font("med", 24)
    k = lt["kicker"]; who = lt["who"]; line2 = f'{lt["what"]}  ·  {lt["src"]}'
    pad = 22
    tw = max(d.textlength(k + "   " + who, font=fw) + 40, d.textlength(line2, font=fq))
    bw = int(min(W - 120, tw + pad * 2 + 6)); bh = 98
    x0 = 60; y0 = int(JOB.get("lt_y", 1410))
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 18, fill=(14, 13, 11, 196))
    d.rectangle([x0, y0 + 14, x0 + 5, y0 + bh - 14], fill=GOLD)
    d.text((x0 + pad, y0 + 15), k, font=fk, fill=GOLD)
    d.text((x0 + pad + d.textlength(k, font=fk) + 14, y0 + 10), who, font=fw, fill="#FFFFFF")
    # encolhe line2 se precisar
    s = 24
    while d.textlength(line2, font=fq) > bw - pad * 2 and s > 17:
        s -= 1; fq = font("med", s)
    d.text((x0 + pad, y0 + 56), line2, font=fq, fill=(242, 236, 224, 225))
    img.save(path)

def burn_lower_thirds(main, dst):
    lts = JOB.get("lower_thirds", [])
    if not lts:
        shutil.copy(main, dst); return dst
    dur = probe_dur(main)
    inputs, chains = ["-i", main], []
    last = "0:v"
    for i, lt in enumerate(lts):
        p = os.path.join(WD, f"lt_{i}.png"); lower_third_png(lt, p)
        inputs += ["-loop", "1", "-t", f"{dur:.2f}", "-i", p]
        a, b = lt["t0"], lt["t1"]
        chains.append(f"[{i+1}:v]format=rgba,fade=t=in:st={a}:d=0.3:alpha=1,fade=t=out:st={b-0.3}:d=0.3:alpha=1[l{i}]")
        chains.append(f"[{last}][l{i}]overlay=0:0:enable='between(t,{a},{b})'[v{i}]")
        last = f"v{i}"
    sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chains),
        "-map", f"[{last}]", "-map", "0:a", "-t", f"{dur:.2f}", *ENC, dst])
    return dst

# ---------------------------------------------------------------- clips
COOK_YT = "/tmp/yt_cookies.txt"
COOK_IG = "/tmp/ig_cookies.txt"
def ytdlp(args):
    """Tenta várias combinações (YouTube bloqueia IP de runner; X/IG costumam passar)."""
    url = args[-1]; base = ["yt-dlp", "--no-playlist", "--no-warnings", "--retries", "3"]
    variants = []
    if "instagram.com" in url and os.path.exists(COOK_IG): variants.append(["--cookies", COOK_IG])
    if "youtu" in url:
        if os.path.exists(COOK_YT) and os.path.getsize(COOK_YT) > 0: variants.append(["--cookies", COOK_YT])
        variants += [["--extractor-args", "youtube:player_client=mweb"], ["--extractor-args", "youtube:player_client=tv_embedded,web_safari"]]
    variants.append([])
    r = None
    for v in variants:
        r = subprocess.run(base + v + args, capture_output=True, text=True)
        if r.returncode == 0: return r
    return r

_WM = {}
def whisper(name="small"):
    if name not in _WM:
        from faster_whisper import WhisperModel
        _WM[name] = WhisperModel(name, compute_type="int8")
    return _WM[name]

def find_moment(audio, keywords, override=None):
    segs, _ = whisper("small").transcribe(audio, language="pt", word_timestamps=True, vad_filter=True)
    segs = list(segs)
    txt = [(s.start, s.end, s.text.strip()) for s in segs]
    if override is not None:
        return float(override), txt
    kws = [norm(k) for k in keywords]
    for k in kws:  # ordem de prioridade
        for s in segs:
            if k in norm(s.text):
                # tenta achar a palavra exata pra começar um pouco antes da frase
                return max(0.0, s.start - 0.4), txt
    return None, txt

def get_clip(c):
    cid = c["id"]; d = os.path.join(WD, "clips", cid); os.makedirs(d, exist_ok=True)
    rep = {"id": cid, "ok": False}
    for url in [c["url"]] + c.get("alt", []):
        a = os.path.join(d, "a.m4a")
        for f in glob.glob(os.path.join(d, "*")): os.remove(f)
        r = ytdlp(["-f", "ba[ext=m4a]/ba/b", "--download-sections", f"*0-{c.get('search_max', 1500)}", "-x", "--audio-format", "m4a", "-o", os.path.join(d, "a.%(ext)s"), url])
        if r.returncode or not os.path.exists(a):
            rep.setdefault("errors", []).append(f"{url}: audio fail {r.stderr[-300:]}"); continue
        t, txt = find_moment(a, c["keywords"], c.get("start"))
        rep["url"] = url; rep["full_transcript"] = [f"[{s:7.2f}-{e:7.2f}] {x}" for s, e, x in txt]
        if t is None:
            rep.setdefault("errors", []).append(f"{url}: keyword not found"); continue
        ln = float(c.get("len", 9)); e = t + ln
        v = os.path.join(d, "v.mp4")
        r = ytdlp(["-f", "bv*[height<=1080]+ba/b", "--merge-output-format", "mp4", "--download-sections", f"*{t:.2f}-{e:.2f}",
                   "--force-keyframes-at-cuts", "-o", os.path.join(d, "v.%(ext)s"), url])
        vv = glob.glob(os.path.join(d, "v.*"))
        if r.returncode or not vv:
            rep.setdefault("errors", []).append(f"{url}: video fail {r.stderr[-300:]}"); continue
        if vv[0] != v: os.rename(vv[0], v)
        rep.update(ok=True, t0=round(t, 2), t1=round(e, 2), file=v)
        segs, _ = whisper("small").transcribe(v, language="pt")
        rep["cut_text"] = " ".join(s.text.strip() for s in segs)
        return rep
    return rep

# ---------------------------------------------------------------- compilation frames
def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def comp_bg(idx, total, item, quote, path, box=None):
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    # grão leve
    import random; random.seed(idx)
    for _ in range(9000):
        x, y = random.randrange(W), random.randrange(H); g = random.randrange(18, 34)
        d.point((x, y), fill=(g, g - 1, g - 3))
    d.text((60, 150), "DE ONDE VEIO", font=font("anton", 70), fill=PAPER)
    d.text((60, 228), "CADA PIADA", font=font("anton", 70), fill=GOLD)
    d.text((W - 60, 168), f"{idx}/{total}", font=font("mono", 30), fill=(242, 236, 224, 160), anchor="ra")
    # moldura do vídeo (sticker branco)
    bx = box or (40, 400, W - 40, 400 + int((W - 80) * 9 / 16))
    d.rectangle([bx[0] - 8, bx[1] - 8, bx[2] + 8, bx[3] + 8], fill="#FFFFFF")
    d.rectangle(bx, fill="#000000")
    y = bx[3] + 60
    fq = font("xbold", 46)
    for ln in wrap(d, quote, fq, W - 120)[:6]:
        d.text((60, y), ln, font=fq, fill="#FFFFFF"); y += 58
    y += 22
    d.text((60, y), item["who"].upper(), font=font("anton", 44), fill=GOLD); y += 58
    d.text((60, y), item.get("role", ""), font=font("med", 28), fill=(242, 236, 224)); y += 40
    d.text((60, y), item["src"], font=font("mono", 25), fill=(170, 165, 155))
    d.text((W // 2, H - 250), JOB.get("page_tag", ""), font=font("mono", 24), fill=(150, 145, 135), anchor="ma")
    img.save(path); return bx

def card_frame(idx, total, k, path):
    bx = (40, 400, W - 40, 400 + int((W - 80) * 9 / 16))
    comp_bg(idx, total, k, k["quote"], path, bx)
    img = Image.open(path); d = ImageDraw.Draw(img)
    # cartão de post (texto refeito, sem print de terceiros)
    d.rectangle(bx, fill="#FFFFFF")
    d.ellipse([bx[0] + 40, bx[1] + 40, bx[0] + 120, bx[1] + 120], fill=SLATE)
    ini = "".join(p[0] for p in k["who"].split()[:2]).upper()
    d.text((bx[0] + 80, bx[1] + 80), ini, font=font("bold", 34), fill="#FFFFFF", anchor="mm")
    d.text((bx[0] + 140, bx[1] + 50), k["who"], font=font("bold", 34), fill="#111111")
    d.text((bx[0] + 140, bx[1] + 92), k["src"], font=font("mono", 22), fill="#666666")
    fq = font("med", 40); y = bx[1] + 160
    for ln in wrap(d, k["quote"], fq, bx[2] - bx[0] - 80):
        d.text((bx[0] + 40, y), ln, font=fq, fill="#111111"); y += 52
    d.text((bx[2] - 30, bx[3] - 40), "texto reproduzido do post", font=font("mono", 20), fill="#888888", anchor="ra")
    img.save(path)

def build_compilation(reps):
    items = [(c, r) for c, r in reps if r.get("ok")] + [(k, {"card": True}) for k in JOB.get("cards", [])]
    total = len(items); segs = []
    for i, (c, r) in enumerate(items, 1):
        seg = os.path.join(WD, f"comp_{i:02d}.mp4"); bg = os.path.join(WD, f"comp_{i:02d}.png")
        if r.get("card"):
            card_frame(i, total, c, bg)
            ln = c.get("len", 5)
            sh(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(ln), "-i", bg,
                "-f", "lavfi", "-t", str(ln), "-i", "anullsrc=r=48000:cl=stereo",
                "-vf", f"fps={FPS},format=yuv420p,fade=t=in:st=0:d=0.12:color=white", "-shortest", *ENC, seg])
        else:
            quote = c.get("quote") or r.get("cut_text", "")
            quote = quote if quote.startswith("“") else f"“{quote.strip()}”"
            bx = comp_bg(i, total, c, quote, bg)
            vw, vh = bx[2] - bx[0], bx[3] - bx[1]
            sh(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", bg, "-i", r["file"], "-filter_complex",
                f"[1:v]scale={vw}:{vh}:force_original_aspect_ratio=decrease,pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[c];"
                f"[0:v][c]overlay={bx[0]}:{bx[1]}:shortest=1,fps={FPS},fade=t=in:st=0:d=0.12:color=white[v];"
                f"[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]",
                "-map", "[v]", "-map", "[a]", "-shortest", *ENC, seg])
        segs.append(seg)
    return segs

def concat(parts, dst):
    lst = os.path.join(WD, os.path.basename(dst) + ".txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, *ENC, "-movflags", "+faststart", dst])

def sheet(src, prefix):
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", "fps=1,scale=180:-2,tile=8x4", "-q:v", "4", os.path.join(OUT, f"{prefix}_%02d.jpg")])

if __name__ == "__main__":
    main = prep_main()
    reps = [(c, get_clip(c)) for c in JOB.get("clips", [])]
    json.dump([{k: v for k, v in r.items() if k != "file"} for _, r in reps], open(os.path.join(OUT, "clips_report.json"), "w"), ensure_ascii=False, indent=1)
    comp = build_compilation(reps)
    with_lt = burn_lower_thirds(main, os.path.join(WD, "main_lt.mp4"))
    concat([with_lt] + comp, os.path.join(OUT, "reel_com_tarja.mp4"))
    concat([main] + comp, os.path.join(OUT, "reel_sem_tarja.mp4"))
    sheet(os.path.join(OUT, "reel_com_tarja.mp4"), "sheet_com_tarja")
    for f in sorted(glob.glob(os.path.join(OUT, "*"))): print("OUT", f, os.path.getsize(f))
