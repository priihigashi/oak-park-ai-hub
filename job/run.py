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

# 1) video from Drive
try:
    if 'video' not in job.get('only',['video']): raise SystemExit
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    info = json.loads(os.environ['SHEETS_TOKEN'])
    creds = Credentials.from_authorized_user_info(info)
    drive = build('drive', 'v3', credentials=creds)
    req = drive.files().get_media(fileId=job['drive_id'], supportsAllDrives=True)
    fh = io.FileIO('orig.mp4', 'wb'); d = MediaIoBaseDownload(fh, req); done = False
    while not done: _, done = d.next_chunk()
    fh.close(); L('downloaded', os.path.getsize('orig.mp4'))
except BaseException as e:
    L('drive skip/fail', repr(e))

ONLY=job.get('only',['video','tts','heads'])
if 'video' in ONLY and os.path.exists('orig.mp4'):
    sh('ffprobe -v error -show_entries stream=width,height,r_frame_rate,codec_type -show_entries format=duration -of compact orig.mp4 > out/probe.txt 2>&1')
    sh("ffmpeg -y -i orig.mp4 -vf fps=1/3,scale=180:-2,tile=8x6 -frames:v 1 out/sheet.jpg")
    sh("ffmpeg -y -ss 30 -i orig.mp4 -frames:v 1 -vf scale=540:-2 out/frame30.jpg")
    sh("ffmpeg -y -ss 90 -i orig.mp4 -frames:v 1 -vf scale=540:-2 out/frame90.jpg")
    sh("ffmpeg -y -i orig.mp4 -vf scale=432:768,fps=24 -c:v libx264 -preset slow -crf 32 -g 48 -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart out/original_leve.mp4")
    sh("ffmpeg -y -ss 3 -i orig.mp4 -frames:v 1 -vf scale=432:-2 -q:v 4 out/original_poster.jpg")
    for c in job['clips']:
        a, b, sp, bg = c['a'], c['b'], c['speed'], c.get('bg', '0x121214')
        dur = (b - a) / sp; fo = max(0, dur - 0.45)
        vf = f"setpts=PTS/{sp},scale=540:960:force_original_aspect_ratio=increase,crop=540:960,fps=30,fade=t=out:st={fo:.2f}:d=0.45:color={bg}"
        af = f"atempo={sp},highpass=f=90,acompressor=threshold=-20dB:ratio=3,loudnorm=I=-13,afade=t=out:st={max(0,dur-0.3):.2f}:d=0.3"
        sh(f"ffmpeg -y -ss {a} -to {b} -i orig.mp4 -vf \"{vf}\" -af \"{af}\" -c:v libx264 -preset slow -crf 27 -g 15 -pix_fmt yuv420p -c:a aac -b:a 96k -ar 44100 -movflags +faststart out/{c['id']}.mp4")
        sh(f"ffmpeg -y -i out/{c['id']}.mp4 -frames:v 1 -q:v 4 out/{c['id']}.jpg")
    # whisper words for clips (captions of the speaker)
    try:
        from faster_whisper import WhisperModel
        m = WhisperModel('medium', device='cpu', compute_type='int8')
        W = {}
        for c in job['clips']:
            segs, _ = m.transcribe(f"out/{c['id']}.mp4", language='pt', word_timestamps=True)
            W[c['id']] = [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)} for s in segs for w in s.words]
        json.dump(W, open('out/clip_words.json', 'w'), ensure_ascii=False, indent=0)
    except Exception as e:
        L('whisper fail', repr(e))

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
    sess = new_session('isnet-general-use')
    for h in (job['heads'] if 'heads' in ONLY else []):
        try:
            url = h.get('url') or wiki_img(h['wiki'])
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
log.close()
