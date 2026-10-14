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
def frame_bg(path, fr):
    """Fundo gradiente verde→amarelo com grão + @ da página em cima."""
    import random
    g1, g2 = fr.get("c1", (0, 122, 61)), fr.get("c2", (232, 196, 40))
    img = Image.new("RGB", (W, H)); px = img.load()
    for y in range(H):
        for x in range(0, W, 4):
            t = min(1, max(0, (0.35 * x / W + 0.85 * y / H) / 1.2))
            c = tuple(int(g1[i] + (g2[i] - g1[i]) * t) for i in range(3))
            for k in range(4): px[x + k, y] = c
    d = ImageDraw.Draw(img); random.seed(7)
    for _ in range(60000):
        x, y = random.randrange(W), random.randrange(H); v = random.randrange(-14, 14)
        r_, g_, b_ = px[x, y]; px[x, y] = (max(0, min(255, r_ + v)), max(0, min(255, g_ + v)), max(0, min(255, b_ + v)))
    tag = JOB.get("page_tag", ""); f = font("bold", 40)
    tw = d.textlength(tag, font=f); cx = W // 2; y0 = fr["y"] - 92
    d.rounded_rectangle([cx - tw / 2 - 30, y0, cx + tw / 2 + 30, y0 + 64], 32, fill=(14, 13, 11))
    d.text((cx, y0 + 32), tag, font=f, fill="#FFFFFF", anchor="mm")
    img.save(path)

def round_mask(path, w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); m.save(path)

def frame_layout(fr):
    sc = fr.get("scale", 0.80); vw, vh = int(W * sc) // 2 * 2, int(H * sc) // 2 * 2
    pad, top = fr.get("pad", 16), fr.get("top_pad", 52)
    cw, ch = vw + 2 * pad, vh + pad + top
    cx0, cy0 = (W - cw) // 2, fr.get("y", 120)
    return dict(vw=vw, vh=vh, vx=cx0 + pad, vy=cy0 + top, cx0=cx0, cy0=cy0, cw=cw, ch=ch)

def frame_bg(path, fr, L):
    """Fundo estilo cartão de vidro (ref. da Priih): manchas amarelo/verde/azul desfocadas,
    cartão translúcido de cantos arredondados com 3 pontinhos, @ da página embaixo."""
    sw, shh = W // 4, H // 4
    base = Image.new("RGB", (sw, shh), (38, 150, 72)); d = ImageDraw.Draw(base)
    for (cx, cy, r, col) in [(0.05, 0.12, 0.55, (226, 206, 60)), (0.95, 0.30, 0.40, (70, 175, 95)),
                             (0.15, 0.80, 0.45, (30, 128, 62)), (0.95, 0.88, 0.55, (34, 74, 190)),
                             (0.55, 0.55, 0.30, (52, 160, 80))]:
        d.ellipse([(cx - r) * sw, (cy - r * 0.56) * shh, (cx + r) * sw, (cy + r * 0.56) * shh], fill=col)
    base = base.filter(ImageFilter.GaussianBlur(sw * 0.12)).resize((W, H), Image.BICUBIC).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = ImageDraw.Draw(ov)
    x0, y0, x1, y1 = L["cx0"], L["cy0"], L["cx0"] + L["cw"], L["cy0"] + L["ch"]
    o.rounded_rectangle([x0, y0, x1, y1], 46, fill=(255, 255, 255, 46), outline=(255, 255, 255, 120), width=3)
    for k in range(3):
        cx = x0 + 34 + k * 26; cy = y0 + 27
        o.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255, 170))
    img = Image.alpha_composite(base, ov).convert("RGB"); d = ImageDraw.Draw(img)
    d.text((W // 2, y1 + 54), JOB.get("page_tag", ""), font=font("med", 34), fill=(255, 255, 255), anchor="mm")
    img.save(path)

def round_mask(path, w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); m.save(path)

def prep_main():
    src = os.path.join(WD, "main_src.mp4")
    dst = os.path.join(WD, "main.mp4")
    fr = JOB.get("frame")
    if not fr:
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf",
            f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={FPS}",
            "-af", "aresample=48000", *ENC, dst])
        return dst
    L = frame_layout(fr)
    JOB.setdefault("lt_y", int(L["vy"] + 0.80 * L["vh"])); JOB.setdefault("lt_x", L["vx"] + 22)
    bg, mk = os.path.join(WD, "frame_bg.png"), os.path.join(WD, "frame_mask.png")
    frame_bg(bg, fr, L); round_mask(mk, L["vw"], L["vh"], fr.get("radius", 32))
    sh(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", bg, "-i", src, "-loop", "1", "-i", mk, "-filter_complex",
        f"[1:v]scale={L['vw']}:{L['vh']}:force_original_aspect_ratio=increase,crop={L['vw']}:{L['vh']},setsar=1,format=rgba[v];"
        f"[2:v]format=gray,scale={L['vw']}:{L['vh']}[m];[v][m]alphamerge[rv];"
        f"[0:v][rv]overlay={L['vx']}:{L['vy']}:shortest=1,fps={FPS},format=yuv420p[o]",
        "-map", "[o]", "-map", "1:a", "-af", "aresample=48000", *ENC, dst])
    return dst

# ---------------------------------------------------------------- lower third (discreto)
def lower_third_png(lt, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fk, fw, fq = font("mono", 21), font("bold", 29), font("med", 24)
    k = lt["kicker"]; who = lt["who"]; line2 = f'{lt["what"]}  ·  {lt["src"]}'
    pad = 22
    tw = max(d.textlength(k + "   " + who, font=fw) + 40, d.textlength(line2, font=fq))
    bw = int(min(W - 2 * x0, tw + pad * 2 + 6)); bh = 98
    x0 = int(JOB.get("lt_x", 60)); y0 = int(JOB.get("lt_y", 1410))
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
        variants += [["--extractor-args", "youtube:player_client=android_vr"], ["--extractor-args", "youtube:player_client=mweb"], ["--extractor-args", "youtube:player_client=tv_embedded,web_safari"]]
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

def has_audio(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", p], capture_output=True, text=True)
    return bool(r.stdout.strip())

def get_clip(c):
    """Baixa o vídeo inteiro (fontes curtas no X/IG), acha o trecho pela fala e corta com ffmpeg."""
    cid = c["id"]; d = os.path.join(WD, "clips", cid); os.makedirs(d, exist_ok=True)
    rep = {"id": cid, "ok": False}
    for url in [c["url"]] + c.get("alt", []):
        for f in glob.glob(os.path.join(d, "*")): os.remove(f)
        r = ytdlp(["-f", "bv*[height<=1080]+ba/b", "--merge-output-format", "mp4", "-o", os.path.join(d, "full.%(ext)s"), url])
        full = (glob.glob(os.path.join(d, "full.*")) or [None])[0]
        if (r is None or r.returncode) or not full:
            rep.setdefault("errors", []).append(f"{url}: download fail {(r.stderr if r else '')[-300:]}"); continue
        if not has_audio(full):
            rep.setdefault("errors", []).append(f"{url}: no audio"); continue
        try:
            t, txt = find_moment(full, c["keywords"], c.get("start"))
        except Exception as e:
            rep.setdefault("errors", []).append(f"{url}: whisper {e}"); continue
        rep["url"] = url; rep["full_transcript"] = [f"[{s:7.2f}-{e:7.2f}] {x}" for s, e, x in txt]
        if t is None:
            rep.setdefault("errors", []).append(f"{url}: keyword not found"); continue
        ln = float(c.get("len", 9)); v = os.path.join(d, "v.mp4")
        if c.get("segments"):  # vários trechos colados (ex.: pular narração de terceiros)
            parts = []
            for k, (a, b) in enumerate(c["segments"]):
                pp = os.path.join(d, f"s{k}.mp4"); parts.append(pp)
                sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.2f}", "-i", full, "-t", f"{b - a:.2f}", *ENC, pp])
            lst = os.path.join(d, "segs.txt"); open(lst, "w").write("".join(f"file '{q}'\n" for q in parts))
            sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, *ENC, v])
            t, ln = c["segments"][0][0], sum(b - a for a, b in c["segments"])
        else:
            sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", full, "-t", f"{ln:.2f}", *ENC, v])
        rep.update(ok=True, t0=round(t, 2), t1=round(t + ln, 2), file=v)
        try:
            segs, _ = whisper("small").transcribe(v, language="pt")
            rep["cut_text"] = " ".join(s.text.strip() for s in segs)
        except Exception as e:
            rep["cut_text"] = ""
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
    if k.get("kind") == "fala":
        d.rectangle(bx, fill=PAPER)
        d.text((bx[0] + 40, bx[1] + 10), "\u201c", font=font("anton", 200), fill=GOLD)
        fq = font("xbold", 42); y = bx[1] + 170
        for ln in wrap(d, k["quote"].strip("\u201c\u201d"), fq, bx[2] - bx[0] - 80):
            d.text((bx[0] + 40, y), ln, font=fq, fill=INK); y += 54
        d.text((bx[0] + 40, bx[3] - 50), k.get("note", ""), font=font("mono", 22), fill="#6b665c")
        img.save(path); return
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
            r_ = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", r["file"]], capture_output=True, text=True)
            cw, ch = [int(x) for x in r_.stdout.strip().split(",")[:2]]
            mw, mh = W - 80, 900 if ch > cw else 620
            sc = min(mw / cw, mh / ch); bw_, bh_ = int(cw * sc) // 2 * 2, int(ch * sc) // 2 * 2
            x0 = (W - bw_) // 2
            bx = comp_bg(i, total, c, quote, bg, (x0, 380, x0 + bw_, 380 + bh_))
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


# ================================================================ estilo VIDRO (plate.html + plate.js)
HERE = os.path.dirname(os.path.abspath(__file__))
def plates(specs, tag):
    d = os.path.join(WD, "plates_" + tag); os.makedirs(d, exist_ok=True)
    sp = os.path.join(d, "specs.json"); json.dump(specs, open(sp, "w"), ensure_ascii=False)
    sh(["node", os.path.join(HERE, "plate.js"), sp, d])
    return d, json.load(open(os.path.join(d, "slots.json")))

def overlay_in_slot(bg, video, slot, dst, radius=30, extra_vf=""):
    mk = dst + ".mask.png"; round_mask(mk, slot["w"], slot["h"], radius); T = f"{probe_dur(video):.3f}"
    sh(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", T, "-i", bg, "-i", video, "-loop", "1", "-t", T, "-i", mk, "-filter_complex",
        f"[1:v]scale={slot['w']}:{slot['h']}:force_original_aspect_ratio=increase,crop={slot['w']}:{slot['h']},setsar=1,format=rgba[v];"
        f"[2:v]format=gray,scale={slot['w']}:{slot['h']}[m];[v][m]alphamerge[rv];"
        f"[0:v][rv]overlay={slot['x']}:{slot['y']}:shortest=1,fps={FPS},format=yuv420p{extra_vf}[o];"
        f"[1:a]aresample=48000[a]",
        "-map", "[o]", "-map", "[a]", "-t", T, *ENC, dst])

def round_mask(path, w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); m.save(path)

def glass_main():
    fr = JOB.get("frame", {})
    d, sl = plates([{"id": "main", "mode": "main", "page_tag": JOB.get("page_tag", ""), "scale": fr.get("scale", .8), "y": fr.get("y", 110)}], "main")
    slot = sl["main"]; out = os.path.join(WD, "main.mp4")
    overlay_in_slot(os.path.join(d, "main.png"), os.path.join(WD, "main_src.mp4"), slot, out)
    # tarjas: PNG transparente, dentro do vídeo, abaixo da legenda queimada do esquete
    lts = JOB.get("lower_thirds", [])
    specs = [dict(lt, id=f"lt{i}", mode="lt", x=slot["x"] + 24, y=int(slot["y"] + JOB.get("lt_rel", .80) * slot["h"]), maxw=slot["w"] - 48) for i, lt in enumerate(lts)]
    lt_out = out
    if specs:
        d2, _ = plates(specs, "lt"); dur = probe_dur(out); inputs, chains, last = ["-i", out], [], "0:v"
        for i, lt in enumerate(lts):
            inputs += ["-loop", "1", "-t", f"{dur:.2f}", "-i", os.path.join(d2, f"lt{i}.png")]
            a, b = lt["t0"], lt["t1"]
            chains.append(f"[{i+1}:v]format=rgba,fade=t=in:st={a}:d=0.3:alpha=1,fade=t=out:st={b-0.3}:d=0.3:alpha=1[l{i}]")
            chains.append(f"[{last}][l{i}]overlay=0:0:enable='between(t,{a},{b})'[v{i}]"); last = f"v{i}"
        lt_out = os.path.join(WD, "main_lt.mp4")
        sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chains), "-map", f"[{last}]", "-map", "0:a", "-t", f"{dur:.2f}", *ENC, lt_out])
    return out, lt_out

def fetch_img(url, dst):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=60).read(); tmp = dst + ".src"; open(tmp, "wb").write(data)
    Image.open(tmp).convert("RGB").save(dst, quality=92); return dst

def glass_compilation():
    seq = JOB["seq"]; n = len(seq); report = []; segs = []
    for i, it in enumerate(seq, 1):
        base = dict(it, id=f"s{i:02d}", i=i, n=n, page_tag=JOB.get("page_tag", ""))
        seg = os.path.join(WD, f"seg_{i:02d}.mp4")
        if it["type"] == "clip":
            r = get_clip(it); report.append({k: v for k, v in r.items() if k != "file"})
            if not r.get("ok"):
                if it.get("fallback"): it = dict(it, **it["fallback"]); base.update(it["fallback"])
                else: continue
            else:
                pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", r["file"]], capture_output=True, text=True)
                cw, ch = [int(x) for x in pr.stdout.strip().split(",")[:2]]
                d, sl = plates([dict(base, mode="clip", aspect=cw / ch)], base["id"])
                overlay_in_slot(os.path.join(d, base["id"] + ".png"), r["file"], sl[base["id"]], seg, extra_vf=",fade=t=in:st=0:d=0.2")
                segs.append(seg); continue
        if it.get("type") == "image" or base.get("type") == "image":
            base["img"] = "file://" + fetch_img(base["img_url"], os.path.join(WD, base["id"] + "_img.jpg"))
            base["mode"] = "image"
        else:
            base["mode"] = "card"
        d, _ = plates([base], base["id"]); ln = float(base.get("len", 5))
        sh(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(ln), "-i", os.path.join(d, base["id"] + ".png"),
            "-f", "lavfi", "-t", str(ln), "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", f"fps={FPS},format=yuv420p,fade=t=in:st=0:d=0.2", "-shortest", *ENC, seg])
        segs.append(seg)
    json.dump(report, open(os.path.join(OUT, "clips_report.json"), "w"), ensure_ascii=False, indent=1)
    return segs

if __name__ == "__main__":
    if JOB.get("style") == "glass":
        main, with_lt = glass_main()
        comp = glass_compilation()
    else:
        main = prep_main()
        reps = [(c, get_clip(c)) for c in JOB.get("clips", [])]
        json.dump([{k: v for k, v in r.items() if k != "file"} for _, r in reps], open(os.path.join(OUT, "clips_report.json"), "w"), ensure_ascii=False, indent=1)
        comp = build_compilation(reps)
        with_lt = burn_lower_thirds(main, os.path.join(WD, "main_lt.mp4"))
    concat([with_lt] + comp, os.path.join(OUT, "reel_com_tarja.mp4"))
    concat([main] + comp, os.path.join(OUT, "reel_sem_tarja.mp4"))
    sheet(os.path.join(OUT, "reel_com_tarja.mp4"), "sheet_com_tarja")
    for f in sorted(glob.glob(os.path.join(OUT, "*"))): print("OUT", f, os.path.getsize(f))
