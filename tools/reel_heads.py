import json, os, io
import requests, numpy as np
from PIL import Image
cfg = json.load(open('tools/reel_juros.json'))
os.makedirs('reel_out/heads', exist_ok=True)
UA = {'User-Agent': 'tentandochegaratevoce-reel/1.0 (mcfollingproperties@gmail.com)'}
from rembg import remove, new_session
import mediapipe as mp, cv2
sess = new_session('isnet-general-use')
OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
def cands(lang, title, q):
    if lang == 'url': return [title]
    return []
def score(im):
    res = fm.process(np.array(im))
    if not res.multi_face_landmarks: return None, None
    lm = res.multi_face_landmarks[0].landmark
    l, r, n = lm[234].x, lm[454].x, lm[1].x
    asym = abs((n - l) - (r - n)) / max(1e-3, (r - l))
    return asym - (r - l) * 0.5, lm
for key, spec in cfg['heads'].items():
    best = None
    for i, u in enumerate(cands(spec[0], spec[1], spec[2])):
        raw = requests.get(u, headers=UA, timeout=60).content
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        im.thumbnail((1400, 1400))
        s, lm = score(im)
        print(key, i, s)
        if s is None: continue
        im.save(f'reel_out/heads/{key}_c{i}.jpg', quality=80)
        best = (s, im, lm, u)
    if not best: print('none', key); continue
    s, im, lm, u = best
    open(f'reel_out/heads/{key}_src.txt', 'w').write(u)
    cut = remove(im, session=sess)
    a = np.array(cut); H, W = a.shape[:2]
    pts = np.array([[lm[i].x*W, lm[i].y*H] for i in OVAL])
    c = pts.mean(0)
    pts2 = c + (pts - c) * np.array([1.10, 1.04])
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, [pts2.astype(np.int32)], 255)
    xs = pts2[:, 0]; fw = xs.max() - xs.min()
    ytop = int(lm[168].y * H)
    x0 = int(max(0, xs.min() - fw * 0.18)); x1 = int(min(W, xs.max() + fw * 0.18))
    hair = np.zeros_like(mask); hair[:ytop, x0:x1] = 255
    ell = np.zeros_like(mask)
    cv2.ellipse(ell, (int(c[0]), ytop), (int((x1 - x0) / 2), int(fw * 1.1)), 0, 180, 360, 255, -1)
    hair = cv2.bitwise_and(hair, ell)
    mask = cv2.bitwise_or(mask, hair)
    mask = cv2.GaussianBlur(mask, (7, 7), 0)
    a[..., 3] = (a[..., 3].astype(float) * mask / 255).astype(np.uint8)
    ys, xs_ = np.where(a[..., 3] > 25)
    a = a[ys.min():ys.max()+1, xs_.min():xs_.max()+1]
    out = Image.fromarray(a); out.thumbnail((700, 700)); out.save(f'reel_out/heads/{key}.png')
    print('ok', key, u)
