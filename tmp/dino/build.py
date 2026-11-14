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
subprocess.run(['ffmpeg','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','0.10','-q:a','9','out/gap.mp3'],check=True)
try:
    asyncio.run(main())
except Exception:
    import traceback; open('out/log.txt','a').write('TTS\n'+traceback.format_exc())
try:
  subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i','out/list.txt','-ac','1','-b:a','64k','out/narracao.mp3'],check=True)
except Exception:
  import traceback; open('out/log.txt','a').write('CONCAT\n'+traceback.format_exc())
for f in os.listdir('out'):
    if (f.startswith('s') and f.endswith('.mp3')) or f in ('gap.mp3','list.txt'): os.remove('out/'+f)

UA = {'User-Agent': 'priih-reel-bot/1.0 (news reel research)'}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
def pageimage(lang, title):
    q = urllib.parse.urlencode({'action':'query','titles':title,'prop':'pageimages','piprop':'original|name','format':'json','redirects':1})
    j = json.loads(get(f'https://{lang}.wikipedia.org/w/api.php?{q}'))
    p = list(j['query']['pages'].values())[0]
    return p.get('original',{}).get('source'), p.get('pageimage')
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
for k,(lang,title) in targets.items():
    try:
        src, name = pageimage(lang, title)
        if not src: continue
        im = Image.open(io.BytesIO(get(src))).convert('RGB')
        im.thumbnail((1400,1400))
        im.save(f'out/raw_{k}.jpg', quality=85)
        try: lic[k] = {'file': name, 'src': src, **license_of(name)}
        except Exception as e: lic[k] = {'file': name, 'src': src, 'err': str(e)}
    except Exception as e:
        import traceback; lic[k] = {'err': traceback.format_exc()[-600:]}
json.dump(lic, open('out/licencas.json','w'), ensure_ascii=False, indent=1)

import cv2, numpy as np
try:
    from rembg import remove, new_session
    sess = new_session('u2net_human_seg')
except Exception:
    import traceback; open('out/log.txt','a').write('REMBG\n'+traceback.format_exc())
casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def headcut(k):
    p = f'out/raw_{k}.jpg'
    if not os.path.exists(p): return
    im = Image.open(p).convert('RGB')
    cut = remove(im, session=sess, alpha_matting=False)
    g = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
    faces = casc.detectMultiScale(g, 1.1, 5, minSize=(60,60))
    if len(faces)==0: cut.save(f'out/cut_{k}_full.png'); return
    x,y,w,h = max(faces, key=lambda f:f[2]*f[3])
    x0,x1 = int(x-0.45*w), int(x+1.45*w); y0,y1 = int(y-0.75*h), int(y+1.18*h)
    W,H = im.size; x0,y0 = max(0,x0),max(0,y0); x1,y1 = min(W,x1),min(H,y1)
    c = np.array(cut.crop((x0,y0,x1,y1))).astype(np.float32)
    hh,ww = c.shape[:2]
    yy,xx = np.mgrid[0:hh,0:ww]
    cx, cy = (x+w/2-x0), (y+h*0.42-y0)
    rx, ry = w*0.78, h*0.80
    d = ((xx-cx)/rx)**2 + ((yy-cy)/ry)**2
    m = np.clip((1.12-d)/0.12,0,1)
    m[yy < cy] = 1.0
    c[...,3] = c[...,3]*m
    out = Image.fromarray(c.astype(np.uint8),'RGBA')
    bb = out.getbbox()
    if bb: out = out.crop(bb)
    out.thumbnail((700,700)); out.save(f'out/head_{k}.png')
for k in ('dino','moraes','carmen','motta','gilmar'):
    try: headcut(k)
    except Exception:
        import traceback; open('out/log.txt','a').write('HEAD '+k+'\n'+traceback.format_exc())
print(open('out/licencas.json').read())
