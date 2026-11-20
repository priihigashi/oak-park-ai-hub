import json, os, asyncio, io
import requests, numpy as np
from PIL import Image
cfg = json.load(open('tools/reel_juros.json'))
os.makedirs('reel_out/heads', exist_ok=True)
# ---- voz
import edge_tts
async def gen(sid, text):
    try:
        c = edge_tts.Communicate(text, cfg['voice'], rate=cfg['rate'], boundary='WordBoundary')
    except TypeError:
        c = edge_tts.Communicate(text, cfg['voice'], rate=cfg['rate'])
    words = []
    with open(f'reel_out/{sid}.mp3', 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append({'t': ch['offset']/1e7, 'd': ch['duration']/1e7, 'w': ch['text']})
    json.dump(words, open(f'reel_out/{sid}.json', 'w'), ensure_ascii=False)
async def allv():
    for sid, text in cfg['scenes'].items():
        for k in range(3):
            try:
                await gen(sid, text); break
            except Exception as e:
                print('retry', sid, e)
asyncio.run(allv())
# ---- rostos
import sys
if cfg.get('skip_heads'): sys.exit(0)
UA = {'User-Agent': 'tentandochegaratevoce-reel/1.0 (mcfollingproperties@gmail.com)'}
from rembg import remove, new_session
import mediapipe as mp, cv2
sess = new_session('isnet-general-use')
OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=False)
for key, (lang, title) in cfg['heads'].items():
    try:
        r = requests.get(f'https://{lang}.wikipedia.org/w/api.php', params={'action':'query','titles':title,'prop':'pageimages','piprop':'original','format':'json','redirects':1}, headers=UA, timeout=30).json()
        page = list(r['query']['pages'].values())[0]
        url = page['original']['source']
        raw = requests.get(url, headers=UA, timeout=60).content
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        if max(im.size) > 1600:
            im.thumbnail((1600, 1600))
        im.save(f'reel_out/heads/{key}_orig.jpg', quality=88)
        open(f'reel_out/heads/{key}_src.txt', 'w').write(url)
        cut = remove(im, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
        a = np.array(cut)
        H, W = a.shape[:2]
        res = fm.process(np.array(im))
        if res.multi_face_landmarks:
            lm = res.multi_face_landmarks[0].landmark
            pts = np.array([[lm[i].x*W, lm[i].y*H] for i in OVAL])
            c = pts.mean(0)
            pts2 = c + (pts - c) * np.array([1.12, 1.05])
            mask = np.zeros((H, W), np.uint8)
            cv2.fillPoly(mask, [pts2.astype(np.int32)], 255)
            ymid = int(lm[168].y * H)
            mask[:ymid, :] = 255
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            a[..., 3] = (a[..., 3].astype(float) * mask / 255).astype(np.uint8)
        else:
            print('no face', key)
        ys, xs = np.where(a[..., 3] > 20)
        a = a[ys.min():ys.max()+1, xs.min():xs.max()+1]
        out = Image.fromarray(a)
        out.thumbnail((700, 700))
        out.save(f'reel_out/heads/{key}.png')
        print('ok', key, url)
    except Exception as e:
        print('fail', key, e)
