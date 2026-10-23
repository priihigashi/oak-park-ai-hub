import json, re, os, asyncio, subprocess, sys, traceback
J = json.load(open('job/script.json'))
os.makedirs('res', exist_ok=True)

def spoken(t):
    return re.sub(r'\{([^|}]*)\|([^}]*)\}', r'\2', t)

async def tts(key, text):
    import edge_tts
    c = edge_tts.Communicate(spoken(text), J['voice'], rate=J['rate'], boundary='WordBoundary')
    words = []
    with open(f'res/{key}.mp3', 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append([ch['text'], ch['offset'] / 1e7, (ch['offset'] + ch['duration']) / 1e7])
    json.dump(words, open(f'res/{key}.json', 'w'), ensure_ascii=False)

def do_tts():
    for k, t in J['scenes'].items():
        if os.path.exists(f'res/{k}.json'):
            continue
        for a in range(3):
            try:
                asyncio.run(tts(k, t)); break
            except Exception as e:
                print('tts fail', k, e)

def do_whisper():
    if os.path.exists('res/clips.json'):
        return
    from faster_whisper import WhisperModel
    m = WhisperModel('medium', compute_type='int8')
    out = {}
    for k, (a, b) in J['windows'].items():
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(a), '-to', str(b), '-i', 'out/orig.mp4', '-ar', '16000', '-ac', '1', f'/tmp/{k}.wav'], check=True)
        segs, _ = m.transcribe(f'/tmp/{k}.wav', language='pt', word_timestamps=True)
        W = []
        for s in segs:
            for w in s.words:
                W.append([w.word.strip(), round(w.start + a, 3), round(w.end + a, 3)])
        out[k] = W
    json.dump(out, open('res/clips.json', 'w'), ensure_ascii=False)

def do_heads():
    import requests
    from PIL import Image
    from rembg import remove, new_session
    import numpy as np
    sess = new_session('isnet-general-use')
    H = {'User-Agent': 'TentandoChegarReelBot/1.0 (https://github.com/priihigashi/oak-park-ai-hub; bot@users.noreply.github.com) python-requests'}
    for k, title in J['heads'].items():
        try:
            url = None
            for lang in ('pt', 'en'):
                r = requests.get(f'https://{lang}.wikipedia.org/w/api.php', params={'action':'query','titles':title,'prop':'pageimages','piprop':'thumbnail','pithumbsize':1400,'format':'json','redirects':1}, headers=H, timeout=30).json()
                for pg in r['query']['pages'].values():
                    url = (pg.get('thumbnail') or {}).get('source')
                if url: break
            print('url', k, url)
            img = requests.get(url, headers=H, timeout=60).content
            open(f'res/{k}_src.jpg', 'wb').write(img)
            im = Image.open(f'res/{k}_src.jpg').convert('RGB')
            if max(im.size) > 1600:
                im.thumbnail((1600, 1600))
            cut = remove(im, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
            cut.save(f'res/{k}_full.png')
            # head only via mediapipe landmarks
            import mediapipe as mp
            arr = np.array(im)
            with mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as fm:
                res = fm.process(arr)
            if not res.multi_face_landmarks:
                print('no face', k); continue
            lm = res.multi_face_landmarks[0].landmark
            w, h = im.size
            P = lambda i: (lm[i].x * w, lm[i].y * h)
            chin = P(152); top = P(10); L = P(234); R = P(454)
            facew = R[0] - L[0]
            A = np.array(cut)
            # jaw curve: cut below polygon following jaw landmarks
            jaw = [234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454]
            pts = [P(i) for i in jaw]
            from PIL import ImageDraw
            mask = Image.new('L', (w, h), 255)
            d = ImageDraw.Draw(mask)
            off = 0.05 * (chin[1] - top[1])
            poly = [(x, y + off) for x, y in pts]
            poly = [(poly[0][0] - facew * 0.6, poly[0][1] - off), *poly, (poly[-1][0] + facew * 0.6, poly[-1][1] - off), (w, poly[-1][1] - off), (w, h), (0, h), (0, poly[0][1] - off)]
            d.polygon(poly, fill=0)
            from PIL import ImageFilter
            mask = mask.filter(ImageFilter.GaussianBlur(1.5))
            a = np.minimum(A[:, :, 3], np.array(mask))
            A[:, :, 3] = a
            out = Image.fromarray(A)
            bb = out.getbbox()
            out = out.crop(bb)
            out.thumbnail((520, 640))
            out.save(f'res/{k}.png')
        except Exception:
            traceback.print_exc()

for f in (do_heads,):
    try:
        f()
    except Exception:
        traceback.print_exc()
