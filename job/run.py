import os, json, subprocess, asyncio, io, sys, urllib.request, urllib.parse
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
job = json.load(open('job/job.json'))
log = open(f'{OUT}/log.txt', 'w')
def L(*a):
    print(*a); log.write(' '.join(map(str, a)) + '\n'); log.flush()
def sh(c):
    L('$', c); r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode: L('ERR', r.stderr[-1500:])
    return r

ONLY=job.get('only',['tts','heads'])
# 2) voice (edge-tts)
import edge_tts
async def tts(i, text, voice, rate):
    try:
        c = edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary')
    except TypeError:
        c = edge_tts.Communicate(text, voice, rate=rate)
    words = []
    with open(f'{OUT}/{i}.mp3', 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio': f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append({'w': ch['text'], 's': ch['offset'] / 1e7, 'e': (ch['offset'] + ch['duration']) / 1e7})
    json.dump(words, open(f'{OUT}/{i}.json', 'w'), ensure_ascii=False)
for n in (job['narr'] if 'tts' in ONLY else []):
    try:
        asyncio.run(tts(n['id'], n['text'], job['voice'], job['rate']))
        L('tts ok', n['id'])
    except Exception as e:
        L('tts fail', n['id'], repr(e))

# 3) heads
def wiki_img(title):
    u = 'https://pt.wikipedia.org/w/api.php?action=query&prop=pageimages&piprop=original&format=json&titles=' + urllib.parse.quote(title)
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'reelbot/1.0'})))
    for p in r['query']['pages'].values():
        return p['original']['source']
try:
    import numpy as np, cv2
    from PIL import Image, ImageFilter
    from rembg import remove, new_session
    import mediapipe as mp
    sess = new_session('birefnet-portrait')
    def commons(q):
        u='https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrlimit=6&prop=imageinfo&iiprop=url&iiurlwidth=1400&format=json&gsrsearch='+urllib.parse.quote(q)
        r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'reelbot/1.0'})))
        out=[]
        for p in sorted(r.get('query',{}).get('pages',{}).values(), key=lambda p:p.get('index',99)):
            ii=p.get('imageinfo',[{}])[0]; t=p['title'].lower()
            if t.endswith(('.jpg','.jpeg','.png')): out.append(ii.get('thumburl') or ii.get('url'))
        return out
    jobs=[]
    for h in (job['heads'] if 'heads' in ONLY else []):
        c=[]
        try: c.append(wiki_img(h['wiki']))
        except Exception as e: L('wiki fail',h['id'],repr(e))
        try: c+= [x for x in commons(h['q']) if x not in c]
        except Exception as e: L('commons fail',h['id'],repr(e))
        for k,u in enumerate(c[:4]): jobs.append({'id':f"{h['id']}_{k}",'url':u})
    for h in jobs:
        try:
            url = h['url']
            L('head src', h['id'], url)
            raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'reelbot/1.0'})).read()
            img = Image.open(io.BytesIO(raw)).convert('RGB')
            if max(img.size) > 1600: img.thumbnail((1600, 1600))
            img.save(f"{OUT}/src_{h['id']}.jpg", quality=88)
            cut = remove(img, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
            arr = np.array(cut); H, Wd = arr.shape[:2]
            fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=False)
            res = fm.process(np.array(img))
            if not res.multi_face_landmarks: L('no face', h['id']); continue
            lm = res.multi_face_landmarks[0].landmark
            P = lambda k: (lm[k].x * Wd, lm[k].y * H)
            OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
            pts = np.array([P(k) for k in OVAL], np.float32)
            cx, cy = pts.mean(0); fw = pts[:, 0].max() - pts[:, 0].min()
            grow = 1.06
            pts2 = ((pts - [cx, cy]) * grow + [cx, cy]).astype(np.int32)
            ear_y = (P(234)[1] + P(454)[1]) / 2
            al = arr[:, :, 3]
            ys, xs = np.where(al[:int(ear_y), :] > 128)
            cand = np.concatenate([pts2, np.stack([xs, ys], 1).astype(np.int32)[::7]], 0)
            hull = cv2.convexHull(cand)
            keep = np.zeros((H, Wd), np.uint8)
            cv2.fillConvexPoly(keep, hull, 255)
            chin = P(152)[1]
            jaw = np.zeros((H, Wd), np.uint8)
            cv2.fillPoly(jaw, [((pts - [cx, cy]) * 1.04 + [cx, cy]).astype(np.int32)], 255)
            low = int((ear_y + chin) / 2)
            keep[low:, :] = np.minimum(keep[low:, :], jaw[low:, :])
            keep[int(chin + 0.03 * fw):, :] = 0
            a = (al.astype(np.float32) * keep.astype(np.float32) / 255).astype(np.uint8)
            n, lab, stats, _ = cv2.connectedComponentsWithStats((a > 40).astype(np.uint8), 8)
            if n > 1:
                big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
                a[lab != big] = 0
            a = cv2.GaussianBlur(a, (3, 3), 0)
            arr[:, :, 3] = a
            out = Image.fromarray(arr)
            bb = out.getbbox(); out = out.crop(bb)
            out.thumbnail((620, 620))
            alpha = out.split()[3].filter(ImageFilter.GaussianBlur(0.8))
            out.putalpha(alpha)
            out.save(f"{OUT}/head_{h['id']}.png")
            L('head ok', h['id'], out.size)
        except Exception as e:
            L('head fail', h['id'], repr(e))
except Exception as e:
    L('heads setup fail', repr(e))

# 4) extra: fonts + PL text
if 'extra' in ONLY:
    os.makedirs(f'{OUT}/fonts',exist_ok=True)
    import re
    for fam in ['Figtree:wght@600;800;900','Instrument+Serif:ital@1']:
        try:
            css=urllib.request.urlopen(urllib.request.Request('https://fonts.googleapis.com/css2?family='+fam+'&display=swap',headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'})).read().decode()
            open(f"{OUT}/fonts/{fam.split(':')[0]}.css",'w').write(css)
            for i,u in enumerate(re.findall(r'url\((https://[^)]+\.woff2)\)',css)):
                open(f"{OUT}/fonts/{fam.split(':')[0]}_{i}.woff2",'wb').write(urllib.request.urlopen(u).read())
            L('font ok',fam)
        except Exception as e: L('font fail',fam,repr(e))
    try:
        d=urllib.request.urlopen(urllib.request.Request('https://legis.senado.leg.br/sdleg-getter/documento?dm=10231180&disposition=inline',headers={'User-Agent':'Mozilla/5.0'})).read()
        open(f'{OUT}/PL_2608_2026_texto_inicial.pdf','wb').write(d); L('pdf ok',len(d))
    except Exception as e: L('pdf fail',repr(e))
log.close()
