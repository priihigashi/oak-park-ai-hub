import asyncio, json, os, subprocess, glob, urllib.request
import edge_tts

os.makedirs('out', exist_ok=True)
job = json.load(open('job/job.json'))
sh = lambda c: subprocess.run(c, shell=True, check=True)

# ---- video processing
if job.get('video_url') and not os.path.exists('out/original_leve.mp4'):
    urllib.request.urlretrieve(job['video_url'], 'orig.mp4')
    # lightweight original for the "Video original" tab
    sh('ffmpeg -y -loglevel error -i orig.mp4 -vf scale=432:768,fps=24 -c:v libx264 -preset slow -crf 32 -g 48 -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart out/original_leve.mp4')
    sh('ffmpeg -y -loglevel error -ss 1 -i orig.mp4 -frames:v 1 -vf scale=432:768 -q:v 4 out/original_poster.jpg')
    # dense frames of the headline montage (0-13s), 1080 wide
    os.makedirs('out/fr', exist_ok=True)
    sh('ffmpeg -y -loglevel error -i orig.mp4 -t 13 -vf fps=4,scale=720:-2 -q:v 3 out/fr/f_%03d.jpg')
    # speech clips
    for c in job.get('clips', []):
        sh(f"ffmpeg -y -loglevel error -ss {c['s']} -to {c['e']} -i orig.mp4 -vf scale=540:960,fps=30 -c:v libx264 -preset slow -crf 27 -g 15 -pix_fmt yuv420p "
           f"-af highpass=f=90,acompressor,loudnorm=I=-13 -c:a aac -b:a 96k -movflags +faststart out/{c['key']}.mp4")
        sh(f"ffmpeg -y -loglevel error -ss {c['s']} -i orig.mp4 -frames:v 1 -vf scale=540:960 -q:v 4 out/{c['key']}_poster.jpg")
    # audio for whisper
    os.makedirs('job/audio', exist_ok=True)
    sh('ffmpeg -y -loglevel error -i orig.mp4 -ac 1 -ar 16000 job/audio/speech.wav')

for dl in job.get('downloads', []):
    try:
        rq = urllib.request.Request(dl['url'], headers={'User-Agent': 'Mozilla/5.0'})
        open('out/' + dl['out'], 'wb').write(urllib.request.urlopen(rq, timeout=60).read())
        print('downloaded', dl['out'])
    except Exception as ex:
        print('download failed', dl['url'], ex)

async def tts(key, text, voice, rate):
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary')
    words = []
    with open(f'out/{key}.mp3', 'wb') as f:
        async for ch in comm.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append({'w': ch['text'], 's': ch['offset'] / 1e7, 'e': (ch['offset'] + ch['duration']) / 1e7})
    json.dump(words, open(f'out/{key}.words.json', 'w'), ensure_ascii=False)

async def main():
    import random
    fails = []
    for it in job.get('tts', []):
        if os.path.exists(f"out/{it['key']}.mp3") and os.path.getsize(f"out/{it['key']}.mp3") > 1000 and not job.get('force'):
            continue
        for attempt in range(6):
            try:
                await tts(it['key'], it['text'], it.get('voice', 'pt-BR-ThalitaMultilingualNeural'), it.get('rate', '+12%'))
                break
            except Exception as ex:
                print('retry', it['key'], attempt, ex)
                await asyncio.sleep(4 + attempt * 5 + random.random() * 3)
        else:
            fails.append(it['key'])
        await asyncio.sleep(1.2)
    print('FAILED', fails)

asyncio.run(main())

aud = sorted(glob.glob('job/audio/*.wav'))
if aud and job.get('whisper', True):
    from faster_whisper import WhisperModel
    m = WhisperModel('medium', device='cpu', compute_type='int8')
    for a in aud:
        dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a]).decode().strip())
        segs, info = m.transcribe(a, language='pt', word_timestamps=True)
        res = {'duration': dur, 'words': []}
        for s in segs:
            for w in s.words:
                res['words'].append({'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)})
        json.dump(res, open('out/' + os.path.basename(a) + '.whisper.json', 'w'), ensure_ascii=False)
if job.get('render'):
    subprocess.run("tar xzf job/bundle.tgz -C job && sed -i -E 's#python \\$B/(gen|page|build)\\.py#/usr/bin/python3 $B/\\1.py#g' job/bundle/go.sh && grep -n usr/bin/python3 job/bundle/go.sh && sed -i 's#Vídeo: @nikolasferreiradm, 28/10/2026#Vídeo do deputado no Instagram, 28/10/2026#g' job/bundle/gen.py && sed -i 's#Vídeo original: @nikolasferreiradm#Vídeo original: post do deputado no Instagram#' job/bundle/page.py && sed -i 's#reel_plantou_v3#reel_plantou_v4#g; s#capa_plantou_v3#capa_plantou_v4#g' job/bundle/go.sh && ! grep -n nikolasferreiradm job/bundle/gen.py job/bundle/page.py && bash job/bundle/go.sh", shell=True, check=True)
print('done')
