import asyncio, json, os, subprocess, urllib.request, urllib.parse, io
import edge_tts
os.makedirs('out', exist_ok=True)
VOICE = os.environ.get('VOICE', 'pt-BR-ThalitaMultilingualNeural')
RATE = os.environ.get('RATE', '+8%')
scenes = json.load(open('narration.json'))

async def tts(i, text):
    c = edge_tts.Communicate(text, VOICE, rate=RATE, boundary='WordBoundary')
    words, audio = [], b''
    async for ch in c.stream():
        if ch['type'] == 'audio': audio += ch['data']
        elif ch['type'] == 'WordBoundary':
            words.append({'w': ch['text'], 's': ch['offset']/1e7, 'e': (ch['offset']+ch['duration'])/1e7})
    open(f'out/s{i:02d}.mp3', 'wb').write(audio)
    return words

async def main():
    tl, t = [], 0.0
    lst = open('out/list.txt', 'w')
    for s in scenes:
        w = await tts(s['id'], s['text'])
        dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0', f"out/s{s['id']:02d}.mp3"]).decode())
        tl.append({'id': s['id'], 'start': round(t,3), 'dur': round(dur,3), 'words': [{'w':x['w'],'s':round(t+x['s'],3),'e':round(t+x['e'],3)} for x in w]})
        lst.write(f"file 's{s['id']:02d}.mp3'\nfile 'gap.mp3'\n"); t += dur + 0.10
    lst.close()
    json.dump(tl, open('out/timeline.json','w'), ensure_ascii=False)
SKIP_TTS=os.path.exists('out/timeline.json')
if not SKIP_TTS: subprocess.run(['ffmpeg','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','0.10','-q:a','9','out/gap.mp3'],check=True)
try:
    if not SKIP_TTS: asyncio.run(main())
except Exception:
    import traceback; open('out/log.txt','a').write('TTS\n'+traceback.format_exc())
try:
  if not SKIP_TTS: subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i','out/list.txt','-ac','1','-b:a','64k','out/narracao.mp3'],check=True)
except Exception:
  import traceback; open('out/log.txt','a').write('CONCAT\n'+traceback.format_exc())
for f in os.listdir('out'):
    if (f.startswith('s') and f.endswith('.mp3')) or f in ('gap.mp3','list.txt'): os.remove('out/'+f)

UA = {'User-Agent': 'ReelResearchBot/1.0 (news reel image lookup; python-urllib)'}
import time
def get(url):
    for a in range(6):
        try:
            time.sleep(3)
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(20*(a+1)); continue
            raise
    raise Exception('429 forever')
def pageimage(lang, title):
    q = urllib.parse.urlencode({'action':'query','titles':title,'prop':'pageimages','piprop':'thumbnail|name','pithumbsize':1200,'format':'json','redirects':1})
    j = json.loads(get(f'https://{lang}.wikipedia.org/w/api.php?{q}'))
    p = list(j['query']['pages'].values())[0]
    return p.get('thumbnail',{}).get('source'), p.get('pageimage')
def license_of(fname):
    q = urllib.parse.urlencode({'action':'query','titles':'File:'+fname,'prop':'imageinfo','iiprop':'extmetadata','format':'json'})
    j = json.loads(get(f'https://commons.wikimedia.org/w/api.php?{q}'))
    p = list(j['query']['pages'].values())[0]
    m = p.get('imageinfo',[{}])[0].get('extmetadata',{})
    return {k: m.get(k,{}).get('value') for k in ('LicenseShortName','Artist','Credit')}
targets = {
 'dino': ('pt','Flávio Dino'), 'moraes': ('pt','Alexandre de Moraes'), 'carmen': ('pt','Cármen Lúcia'),
 'stf': ('pt','Supremo Tribunal Federal'), 'congresso': ('pt','Palácio do Congresso Nacional'),
 'rua': ('pt','Rua 25 de Março'), 'motta': ('pt','Hugo Motta'), 'gilmar': ('pt','Gilmar Mendes'),
}
from PIL import Image
lic = {}
old = json.load(open('out/licencas.json')) if os.path.exists('out/licencas.json') else {}
for k,(lang,title) in targets.items():
    if os.path.exists(f'out/raw_{k}.jpg'):
        lic[k]=old.get(k,{}); continue
    try:
        src, name = pageimage(lang, title)
        if not src: continue
        im = Image.open(io.BytesIO(get(src))).convert('RGB')
        im.thumbnail((1200,1200))
        im.save(f'out/raw_{k}.jpg', quality=85)
        try: lic[k] = {'file': name, 'src': src, **license_of(name)}
        except Exception as e: lic[k] = {'file': name, 'src': src, 'err': str(e)}
    except Exception as e:
        import traceback; lic[k] = {'err': traceback.format_exc()[-600:]}
json.dump(lic, open('out/licencas.json','w'), ensure_ascii=False, indent=1)
print(open('out/licencas.json').read())
