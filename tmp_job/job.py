import json, os, subprocess, sys, urllib.request, urllib.parse, io
os.makedirs('out', exist_ok=True)
UA = {'User-Agent': 'oak-park-ai-hub reel bot (priscila@oakpark-construction.com)'}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=60).read()

# ---------- 1) word timestamps ----------
try:
    from faster_whisper import WhisperModel
    m = WhisperModel('medium', device='cpu', compute_type='int8')
    segs, info = m.transcribe('audio.m4a', language='pt', word_timestamps=True, beam_size=5,
        initial_prompt='Mensalão, triplex, sítio de Atibaia, Sergio Moro, Vorcaro, Flávio Bolsonaro, rachadinha, Willer Tomaz, offshore, Mauro Cid, Alckmin, Alexandre de Moraes, Punhal Verde e Amarelo, Palácio da Alvorada.')
    out = []
    for s in segs:
        out.append({'s': s.start, 'e': s.end, 't': s.text, 'w': [[w.word, round(w.start, 3), round(w.end, 3)] for w in s.words]})
    json.dump({'duration': info.duration, 'segs': out}, open('out/words.json', 'w'), ensure_ascii=False)
    print('whisper ok', info.duration)
except Exception as e:
    print('whisper fail', e)

# ---------- 2) head cutouts ----------
people = json.load(open('people.json'))
from rembg import remove, new_session
import numpy as np
from PIL import Image, ImageFilter
import mediapipe as mp
sess = new_session('birefnet-portrait')
fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=False)

def candidates(q):
    urls = []
    for lang in ('pt', 'en'):
        try:
            api = f'https://{lang}.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&piprop=original&generator=search&gsrlimit=3&gsrsearch=' + urllib.parse.quote(q)
            d = json.loads(get(api))
            for p in sorted(d.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 9)):
                o = p.get('original', {}).get('source')
                if o and o not in urls: urls.append(o)
        except Exception as e:
            print('api', e)
    try:
        api = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=6&prop=imageinfo&iiprop=url&iiurlwidth=1200&gsrsearch=' + urllib.parse.quote(q)
        d = json.loads(get(api))
        for p in sorted(d.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 9)):
            ii = p.get('imageinfo', [{}])[0]
            u = ii.get('thumburl') or ii.get('url')
            if u and u.lower().split('?')[0].endswith(('.jpg', '.jpeg', '.png')) and u not in urls: urls.append(u)
    except Exception as e:
        print('commons', e)
    return urls

def headcut(img):
    img = img.convert('RGB')
    if max(img.size) > 1600:
        img.thumbnail((1600, 1600))
    rgba = remove(img, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240,
                  alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
    a = np.array(img)
    res = fm.process(a)
    if not res.multi_face_landmarks:
        return None
    lm = res.multi_face_landmarks[0].landmark
    W, H = img.size
    P = lambda i: (lm[i].x * W, lm[i].y * H)
    chin = P(152); top = P(10)
    face_h = chin[1] - top[1]
    # jaw curve points
    jaw = [234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454]
    pts = [P(i) for i in jaw]
    cx = sum(p[0] for p in pts) / len(pts)
    off = face_h * 0.05
    pts2 = [(x + (x - cx) * 0.02, y + off) for x, y in pts]
    from PIL import ImageDraw
    mask = Image.new('L', img.size, 0)
    d = ImageDraw.Draw(mask)
    left = pts2[0]; right = pts2[-1]
    poly = [(left[0] - face_h, -10), (left[0] - face_h, left[1])] + pts2 + [(right[0] + face_h, right[1]), (right[0] + face_h, -10)]
    d.polygon(poly, fill=255)
    al = np.minimum(np.array(rgba)[:, :, 3], np.array(mask))
    out = np.array(rgba); out[:, :, 3] = al
    o = Image.fromarray(out).filter(ImageFilter.SMOOTH)
    o.putalpha(Image.fromarray(al).filter(ImageFilter.GaussianBlur(1.2)))
    bb = o.getbbox()
    if not bb: return None
    o = o.crop(bb)
    if o.height > 640:
        o = o.resize((int(o.width * 640 / o.height), 640), Image.LANCZOS)
    return o

for key, q in people.items():
    n = 0
    for u in candidates(q)[:6]:
        try:
            im = Image.open(io.BytesIO(get(u)))
            h = headcut(im)
            if h is None: continue
            h.save(f'out/{key}_{n}.png')
            json.dump({'url': u}, open(f'out/{key}_{n}.json', 'w'))
            n += 1
            if n >= 3: break
        except Exception as e:
            print(key, u, e)
    print(key, n)
