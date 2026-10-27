import asyncio, json, os, io, requests, traceback
import edge_tts

os.makedirs('out', exist_ok=True)
job = json.load(open('tmp_gringos/job.json'))

async def tts(i, text, voice, rate):
    c = edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary')
    words = []
    with open(f'out/s{i:02d}.mp3', 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append({'w': ch['text'], 's': ch['offset'] / 1e7, 'd': ch['duration'] / 1e7})
    json.dump(words, open(f'out/s{i:02d}.json', 'w'), ensure_ascii=False)

for i, t in enumerate(job['scenes']):
    try:
        asyncio.run(tts(i, t, job['voice'], job['rate']))
    except Exception:
        traceback.print_exc()

# face candidates from Wikimedia Commons
H = {'User-Agent': 'tentandochegaratevoce-bot/1.0 (priscila@oakpark-construction.com)'}
from PIL import Image
for name, files in job['faces'].items():
    for k, fn in enumerate(files):
        try:
            r = requests.get('https://commons.wikimedia.org/w/api.php', params={
                'action': 'query', 'titles': fn, 'prop': 'imageinfo', 'iiprop': 'url',
                'iiurlwidth': 1400, 'format': 'json'}, headers=H, timeout=30).json()
            pg = list(r['query']['pages'].values())[0]
            url = pg['imageinfo'][0]['thumburl']
            img = requests.get(url, headers=H, timeout=60).content
            open(f'out/{name}_{k}.jpg', 'wb').write(img)
            print('ok', name, k, url)
        except Exception as e:
            print('fail', name, fn, e)
    # also search
    try:
        r = requests.get('https://commons.wikimedia.org/w/api.php', params={
            'action': 'query', 'list': 'search', 'srnamespace': 6, 'srlimit': 8,
            'srsearch': job['search'][name], 'format': 'json'}, headers=H, timeout=30).json()
        json.dump([x['title'] for x in r['query']['search']], open(f'out/{name}_search.json', 'w'))
    except Exception as e:
        print('search fail', e)

# rembg cutouts of every candidate
try:
    from rembg import remove, new_session
    sess = new_session('birefnet-portrait')
    for fn in sorted(os.listdir('out')):
        if fn.endswith('.jpg'):
            im = Image.open('out/' + fn).convert('RGB')
            o = remove(im, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240,
                       alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
            o.save('out/' + fn.replace('.jpg', '_cut.png'))
            print('cut', fn)
except Exception:
    traceback.print_exc()
