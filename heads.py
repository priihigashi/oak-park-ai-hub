"""Head-only cutouts: commons search -> rembg (alpha matting) -> cut below the jaw with Face Mesh -> white-outline check sheets."""
import json, os, io, urllib.request, urllib.parse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import mediapipe as mp
from rembg import remove, new_session

OUT = 'out/heads'; os.makedirs(OUT, exist_ok=True)
JOB = json.load(open('job.json'))
UA = {'User-Agent': 'oak-park-ai-hub/1.0 (reel head cutouts; github.com/priihigashi)'}
session = new_session('isnet-general-use')
mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=2, refine_landmarks=False)
# face-oval landmarks from left cheek (234) down around the chin (152) to right cheek (454)
JAW = [234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454]

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()

def commons(query, n):
    q = urllib.parse.urlencode({'action': 'query', 'generator': 'search', 'gsrsearch': f'filetype:bitmap {query}',
                                'gsrnamespace': 6, 'gsrlimit': n, 'prop': 'imageinfo', 'iiprop': 'url|size',
                                'iiurlwidth': 1600, 'format': 'json'})
    d = json.loads(fetch('https://commons.wikimedia.org/w/api.php?' + q))
    pages = sorted(d.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 0))
    return [(p['title'], p['imageinfo'][0].get('thumburl') or p['imageinfo'][0]['url']) for p in pages]

def cut(img):
    rgb = np.array(img.convert('RGB'))
    H, W = rgb.shape[:2]
    res = mesh.process(rgb)
    if not res.multi_face_landmarks:
        return None, 'no face'
    faces = res.multi_face_landmarks
    # biggest face
    def area(f):
        xs = [l.x for l in f.landmark]; ys = [l.y for l in f.landmark]
        return (max(xs) - min(xs)) * (max(ys) - min(ys))
    f = max(faces, key=area).landmark
    pts = np.array([[f[i].x * W, f[i].y * H] for i in JAW])
    top = min(l.y for l in f) * H
    chin = f[152].y * H
    fh = chin - top
    if fh < 260:
        return None, f'face too small ({fh:.0f}px)'
    fw = abs(f[454].x - f[234].x) * W
    yaw = ((f[1].x * W) - (f[234].x + f[454].x) / 2 * W) / fw
    mouth = abs(f[14].y - f[13].y) * H / fh
    smile = abs(f[291].x - f[61].x) * W / fw
    global SCORE; SCORE = dict(yaw=round(yaw, 3), mouth=round(mouth, 3), smile=round(smile, 3), face=round(fh))
    # push jaw points outward/down a little (4-6% of face height) so the chin is kept whole
    cx = pts[:, 0].mean(); cy = (top + chin) / 2
    v = pts - [cx, cy]; v /= (np.linalg.norm(v, axis=1, keepdims=True) + 1e-6)
    pts = pts + v * fh * 0.05
    cut_img = remove(img.convert('RGB'), session=session, alpha_matting=True,
                     alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10,
                     alpha_matting_erode_size=10)
    keep = Image.new('L', (W, H), 0)
    # JAW[3]=58 and JAW[-4]=288 sit below the earlobes: leave the sides open down to there so ears stay whole
    yl, yr = pts[3][1], pts[-4][1]
    poly = [(0, 0), (0, yl)] + [tuple(p) for p in pts[3:-3]] + [(W, yr), (W, 0)]
    ImageDraw.Draw(keep).polygon(poly, fill=255)
    keep = keep.filter(ImageFilter.GaussianBlur(1.5))
    a = np.minimum(np.array(cut_img.split()[-1]), np.array(keep))
    a = np.array(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.0)))
    a[a < 12] = 0
    out = cut_img.copy(); out.putalpha(Image.fromarray(a))
    bb = out.getbbox()
    if not bb:
        return None, 'empty'
    out = out.crop(bb)
    pad = int(max(out.size) * 0.04)
    canvas = Image.new('RGBA', (out.width + 2 * pad, out.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(out, (pad, pad))
    canvas.thumbnail((900, 900))
    return canvas, f'ok face {fh:.0f}px'

def outline(im, px=12):
    a = im.split()[-1]
    big = a.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new('RGBA', im.size, (255, 255, 255, 0)); base.putalpha(big)
    w = Image.new('RGBA', im.size, (255, 255, 255, 255)); w.putalpha(big)
    w.alpha_composite(im)
    return w

report = []
SCORE = {}
for h in JOB['heads']:
    cands = []
    for q in h['queries']:
        try:
            cands += commons(q, 8)
        except Exception as e:
            print('search fail', q, e)
    seen = set(); n = 0
    for title, url in cands:
        if url in seen or n >= h.get('max', 4) or not all(k.lower() in title.lower() for k in h.get('must', [])):
            continue
        seen.add(url)
        try:
            img = Image.open(io.BytesIO(fetch(url)))
            img.load()
        except Exception as e:
            print('dl fail', title, e); continue
        try:
            res, msg = cut(img)
        except Exception as e:
            res, msg = None, f'err {e}'
        print(h['id'], title, msg)
        report.append({'id': h['id'], 'n': n, 'title': title, 'url': url, 'msg': msg, **(SCORE if res is not None else {})})
        if res is None:
            continue
        name = f"{h['id']}_{n}"
        res.save(f'{OUT}/{name}.png')
        sheet = Image.new('RGB', (1000, 520), '#FFD34D')
        ImageDraw.Draw(sheet).rectangle([500, 0, 1000, 520], fill='#121214')
        o = outline(res, 10); o.thumbnail((440, 440))
        sheet.paste(o, (30, 40), o); sheet.paste(o, (530, 40), o)
        sheet.save(f'{OUT}/{name}_check.jpg', quality=82)
        n += 1
json.dump(report, open(f'{OUT}/report.json', 'w'), ensure_ascii=False, indent=1)
