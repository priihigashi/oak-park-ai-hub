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


# ---------- imagens do Commons (busca) ----------
import time, urllib.request, urllib.parse, io
UA = {'User-Agent': 'ReelResearchBot/1.0 (news reel image lookup; python-urllib)'}
def get(url):
    for a in range(6):
        try:
            time.sleep(2)
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(20*(a+1)); continue
            raise
from PIL import Image
lic={}
buscas = json.load(open('buscas.json'))
for k, termos in buscas.items():
    achou=[]
    for termo in termos:
        q = urllib.parse.urlencode({'action':'query','generator':'search','gsrsearch':'filetype:bitmap '+termo,'gsrnamespace':6,'gsrlimit':6,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1200,'format':'json'})
        try:
            j=json.loads(get('https://commons.wikimedia.org/w/api.php?'+q))
            for p in sorted(j.get('query',{}).get('pages',{}).values(), key=lambda x:x.get('index',99)):
                ii=p['imageinfo'][0]; m=ii.get('extmetadata',{})
                achou.append({'file':p['title'],'thumb':ii.get('thumburl'),'lic':m.get('LicenseShortName',{}).get('value'),'artist':m.get('Artist',{}).get('value'),'desc':(m.get('ImageDescription',{}).get('value') or '')[:200]})
        except Exception as e: achou.append({'err':str(e),'termo':termo})
    lic[k]=achou
    for n,a in enumerate([x for x in achou if x.get('thumb')][:4]):
        try:
            im=Image.open(io.BytesIO(get(a['thumb']))).convert('RGB'); im.thumbnail((1200,1200)); im.save(f'out/cand_{k}_{n}.jpg',quality=85)
        except Exception as e: a['err']=str(e)
json.dump(lic, open('out/candidatos.json','w'), ensure_ascii=False, indent=1)
