import asyncio, json, os, subprocess, sys, urllib.request, urllib.parse
import edge_tts

OUT = 'out'
os.makedirs(OUT, exist_ok=True)
JOB = json.load(open('job.json'))

def sh(*a):
    print('+', ' '.join(a)); subprocess.run(a, check=True)

def get(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (oak-park-ai-hub reel job)'})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, 'wb') as f:
        f.write(r.read())

# ---------- 1. source audio + clips ----------
src = None
for i, u in enumerate(JOB['sources']):
    p = f'src{i}'
    try:
        get(u, p); src = p; print('source ok', i, os.path.getsize(p)); break
    except Exception as e:
        print('source fail', i, e)
if src:
    sh('ffmpeg', '-y', '-v', 'error', '-i', src, '-ac', '1', '-ar', '44100', f'{OUT}/full.wav')
    for c in JOB['clips']:
        sh('ffmpeg', '-y', '-v', 'error', '-ss', str(c['a']), '-to', str(c['b']), '-i', f'{OUT}/full.wav',
           '-af', 'afade=t=in:d=0.03,areverse,afade=t=in:d=0.06,areverse', f"{OUT}/{c['id']}.wav")
    os.remove(f'{OUT}/full.wav')

# ---------- 2. narration (Edge TTS, word boundaries) ----------
async def tts(seg):
    kw = dict(voice=JOB['voice'], rate=JOB['rate'])
    try:
        com = edge_tts.Communicate(seg['spoken'], boundary='WordBoundary', **kw)
    except TypeError:
        com = edge_tts.Communicate(seg['spoken'], **kw)
    words = []
    with open(f"{OUT}/{seg['id']}.mp3", 'wb') as f:
        async for ch in com.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append([ch['text'], ch['offset'] / 1e7, ch['duration'] / 1e7])
    json.dump(words, open(f"{OUT}/{seg['id']}.json", 'w'), ensure_ascii=False)
    print(seg['id'], len(words), 'words')

async def all_tts():
    for s in JOB['narr']:
        for k in range(3):
            try:
                await tts(s); break
            except Exception as e:
                print('tts retry', s['id'], e); await asyncio.sleep(3)
asyncio.run(all_tts())

# ---------- 3. head cutouts ----------
if JOB.get('heads'):
    sh(sys.executable, 'heads.py')
