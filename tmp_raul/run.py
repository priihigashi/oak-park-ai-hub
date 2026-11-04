import json, os, subprocess, asyncio, urllib.request, urllib.parse, re, unicodedata, traceback
J = json.load(open('tmp_raul/job.json'))
OUT = 'tmp_raul/out'; os.makedirs(OUT, exist_ok=True)
def sh(c): print('+', c[:200]); subprocess.run(c, shell=True, check=True)

# ---------- 1. TTS (edge-tts, word boundaries) ----------
async def tts():
    import edge_tts
    for sc in J['scenes']:
        mp3 = f"{OUT}/{sc['id']}.mp3"
        words = []
        c = edge_tts.Communicate(sc['text'], J['voice'], rate=J['rate'], boundary='WordBoundary')
        with open(mp3, 'wb') as f:
            async for ch in c.stream():
                if ch['type'] == 'audio': f.write(ch['data'])
                elif ch['type'] == 'WordBoundary':
                    words.append({'w': ch['text'], 's': ch['offset']/1e7, 'e': (ch['offset']+ch['duration'])/1e7})
        json.dump(words, open(f"{OUT}/{sc['id']}.json", 'w'), ensure_ascii=False)
        print(sc['id'], len(words))
try:
    asyncio.run(tts())
except Exception:
    traceback.print_exc()

# ---------- 2. Video from Drive ----------
def token():
    td = json.loads(os.environ['SHEETS_TOKEN'])
    data = urllib.parse.urlencode({'client_id': td['client_id'], 'client_secret': td['client_secret'],
                                   'refresh_token': td['refresh_token'], 'grant_type': 'refresh_token'}).encode()
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data=data)).read())['access_token']
try:
    tk = token()
    req = urllib.request.Request(f"https://www.googleapis.com/drive/v3/files/{J['drive_video']}?alt=media&supportsAllDrives=true",
                                 headers={'Authorization': 'Bearer ' + tk})
    with urllib.request.urlopen(req) as r, open('orig.mp4', 'wb') as f:
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b)
    sh('ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of json orig.mp4 > tmp_raul/out/probe.json')
    # light original for preview tab
    sh(f"ffmpeg -y -loglevel error -i orig.mp4 -vf scale=432:768,fps=24 -c:v libx264 -preset slow -crf 32 -g 48 -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart {OUT}/original_leve.mp4")
    sh(f"ffmpeg -y -loglevel error -ss 2 -i orig.mp4 -frames:v 1 -vf scale=432:768 {OUT}/original_poster.jpg")
    # contact sheet to see layout
    sh(f"ffmpeg -y -loglevel error -i orig.mp4 -vf fps=1/15,scale=216:384,tile=5x3 -frames:v 1 {OUT}/sheet.jpg")
    # word timestamps of the original
    sh('ffmpeg -y -loglevel error -i orig.mp4 -ac 1 -ar 16000 orig.wav')
    from faster_whisper import WhisperModel
    m = WhisperModel('medium', device='cpu', compute_type='int8')
    segs, _ = m.transcribe('orig.wav', language='pt', word_timestamps=True, vad_filter=False)
    W = []
    for s in segs:
        for w in s.words: W.append({'w': w.word.strip(), 's': w.start, 'e': w.end})
    json.dump(W, open(f'{OUT}/orig_words.json', 'w'), ensure_ascii=False)
    def norm(x):
        x = unicodedata.normalize('NFD', x.lower()); x = ''.join(ch for ch in x if unicodedata.category(ch) != 'Mn')
        return re.sub(r'[^a-z0-9]', '', x)
    NW = [norm(w['w']) for w in W]
    def find(seq, start=0):
        seq = [norm(s) for s in seq]
        for i in range(start, len(NW) - len(seq) + 1):
            if NW[i:i+len(seq)] == seq: return i
        return -1
    clips = {}
    for c in J['clips']:
        i = find(c['words'])
        if i < 0: print('NOT FOUND', c['id']); continue
        j = i + len(c['words']) - 1
        if 'until' in c:
            k = find(c['until'], i)
            if k >= 0: j = k + len(c['until']) - 1
        st = max(0, W[i]['s'] - c['pre']); en = W[j]['e'] + c['post']
        dur = en - st
        clips[c['id']] = {'start': st, 'end': en, 'words': [dict(w, s=w['s']-st, e=w['e']-st) for w in W[i:j+1]]}
        fo = max(0, dur - 0.45)
        sh(f"ffmpeg -y -loglevel error -ss {st:.3f} -t {dur:.3f} -i orig.mp4 -vf \"scale=540:960,fps=30,fade=t=out:st={fo:.3f}:d=0.45:color=0x121214\" "
           f"-af \"highpass=f=90,acompressor=threshold=-20dB:ratio=3,loudnorm=I=-13,afade=t=out:st={max(0,dur-0.3):.3f}:d=0.3\" "
           f"-c:v libx264 -crf 27 -g 15 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart {OUT}/{c['id']}.mp4")
        sh(f"ffmpeg -y -loglevel error -ss 0.05 -i {OUT}/{c['id']}.mp4 -frames:v 1 {OUT}/{c['id']}.jpg")
        sh(f"ffmpeg -y -loglevel error -i {OUT}/{c['id']}.mp4 -vn -ar 48000 -ac 2 {OUT}/{c['id']}.wav")
    json.dump(clips, open(f'{OUT}/clips.json', 'w'), ensure_ascii=False, indent=1)
except Exception:
    traceback.print_exc()

# ---------- 3. Head cutouts ----------
try:
    import numpy as np
    from PIL import Image, ImageFilter
    from rembg import remove, new_session
    import mediapipe as mp
    sess = new_session('birefnet-portrait')
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=False)
    OVAL = sorted({a for a, b in mp.solutions.face_mesh.FACEMESH_FACE_OVAL})
    UA = {'User-Agent': 'reel-builder/1.0 (contact via github priihigashi)'}
    sheet = []
    for f in J['faces']:
        try:
            api = 'https://pt.wikipedia.org/w/api.php?action=query&prop=pageimages&piprop=original&format=json&titles=' + urllib.parse.quote(f['page'])
            d = json.loads(urllib.request.urlopen(urllib.request.Request(api, headers=UA)).read())
            src = list(d['query']['pages'].values())[0]['original']['source']
            raw = urllib.request.urlopen(urllib.request.Request(src, headers=UA)).read()
            open(f"{OUT}/{f['id']}_src.jpg", 'wb').write(raw)
            im = Image.open(f"{OUT}/{f['id']}_src.jpg").convert('RGB')
            if max(im.size) > 1600: im.thumbnail((1600, 1600))
            cut = remove(im, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240,
                         alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
            A = np.array(cut); h, w = A.shape[:2]
            res = fm.process(np.array(im))
            if res.multi_face_landmarks:
                L = res.multi_face_landmarks[0].landmark
                P = {k: (L[k].x * w, L[k].y * h) for k in OVAL}
                chin = L[152].y * h; top = L[10].y * h; fh = chin - top
                side = (L[234].y * h + L[454].y * h) / 2
                low = sorted([p for p in P.values() if p[1] > side], key=lambda p: p[0])
                xs = np.array([p[0] for p in low]); ys = np.array([p[1] for p in low])
                X = np.arange(w); yj = np.interp(X, xs, ys) + 0.05 * fh
                Y = np.arange(h)[:, None]
                A[..., 3] = np.where(Y > yj[None, :], 0, A[..., 3])
            al = Image.fromarray(A[..., 3]).filter(ImageFilter.GaussianBlur(1.2))
            A[..., 3] = np.array(al)
            img = Image.fromarray(A)
            bb = img.getbbox(); img = img.crop(bb)
            img.thumbnail((640, 640)); img.save(f"{OUT}/{f['id']}_head.png")
            sheet.append(img)
            print('face ok', f['id'], src)
        except Exception:
            traceback.print_exc()
    if sheet:
        W2 = 300 * len(sheet); S = Image.new('RGB', (W2, 600), '#4ADE80')
        for i, im in enumerate(sheet):
            t = im.copy(); t.thumbnail((280, 280))
            S.paste(t, (i * 300 + 10, 10), t)
            bg = Image.new('RGB', (300, 300), '#121214'); S.paste(bg, (i * 300, 300)); S.paste(t, (i * 300 + 10, 310), t)
        S.save(f'{OUT}/faces_check.jpg')
except Exception:
    traceback.print_exc()
print('DONE')
