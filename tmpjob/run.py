import json, re, asyncio, os, subprocess, sys, traceback
os.makedirs('out', exist_ok=True)
log = open('out/log.txt','w')
def L(*a):
    print(*a); print(*a, file=log); log.flush()
# ---------- TTS ----------
async def tts():
    import edge_tts
    d = json.load(open('tmpjob/script.json'))
    for s in d['scenes']:
        spoken = re.sub(r'\{[^|}]*\|([^}]*)\}', r'\1', s['text'])
        c = edge_tts.Communicate(spoken, d['voice'], rate=d['rate'], boundary="WordBoundary")
        words=[]; audio=bytearray()
        async for ch in c.stream():
            if ch['type']=='audio': audio+=ch['data']
            elif ch['type']=='WordBoundary':
                words.append({'t':ch['offset']/1e7,'d':ch['duration']/1e7,'w':ch['text']})
        open(f"out/{s['id']}.mp3",'wb').write(audio)
        json.dump(words, open(f"out/{s['id']}.json",'w'), ensure_ascii=False)
        L('tts', s['id'], len(words))
try: asyncio.run(tts())
except Exception: L(traceback.format_exc())
# ---------- photos ----------
import requests
UA={'User-Agent':'reel-bot/1.0 (priscila@oakpark-construction.com)'}
people={'nikolas':'Nikolas_Ferreira','bolsonaro':'Jair_Bolsonaro','temer':'Michel_Temer'}
for k,t in people.items():
    try:
        r=requests.get('https://pt.wikipedia.org/w/api.php',params={'action':'query','titles':t,'prop':'pageimages','piprop':'original','format':'json'},headers=UA,timeout=30).json()
        p=list(r['query']['pages'].values())[0]; url=p['original']['source']
        img=requests.get(url,headers=UA,timeout=60).content
        open(f'out/orig_{k}.jpg','wb').write(img); L('photo',k,url,len(img))
    except Exception: L('photo fail',k,traceback.format_exc())
# extra Nikolas candidates from commons search
try:
    r=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','generator':'search','gsrsearch':'Nikolas Ferreira','gsrnamespace':6,'gsrlimit':8,'prop':'imageinfo','iiprop':'url|size','iiurlwidth':1600,'format':'json'},headers=UA,timeout=30).json()
    i=0
    for p in r['query']['pages'].values():
        ii=p['imageinfo'][0]; u=ii.get('thumburl') or ii['url']
        if not re.search(r'\.(jpe?g|png)$',u,re.I): continue
        img=requests.get(u,headers=UA,timeout=60).content
        open(f'out/cand_nikolas_{i}.jpg','wb').write(img); L('cand',i,p['title'],ii['width'],ii['height']); i+=1
except Exception: L('commons fail',traceback.format_exc())
# ---------- cutouts ----------
def cut(src, dst):
    from rembg import remove, new_session
    from PIL import Image, ImageFilter, ImageDraw
    import numpy as np, mediapipe as mp
    global SESSION
    if 'SESSION' not in globals(): SESSION=new_session('birefnet-portrait')
    im=Image.open(src).convert('RGB')
    if max(im.size)>1800: im.thumbnail((1800,1800))
    rgba=remove(im,session=SESSION,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=10)
    W,H=im.size; arr=np.array(im)
    fm=mp.solutions.face_mesh.FaceMesh(static_image_mode=True,max_num_faces=1,refine_landmarks=False)
    res=fm.process(arr)
    if not res.multi_face_landmarks: L('noface',src); rgba.save(dst.replace('.png','_full.png')); return
    lm=res.multi_face_landmarks[0].landmark
    P=lambda i:(lm[i].x*W,lm[i].y*H)
    jaw=[234,93,132,58,172,136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454]
    top=P(10); chin=P(152); fh=chin[1]-top[1]; off=0.05*fh
    pts=[(x,y+off) for x,y in map(P,jaw)]
    poly=[(0,0),(W,0),(W,pts[-1][1])]+list(reversed(pts))+[(0,pts[0][1])]
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon(poly,fill=255)
    m=m.filter(ImageFilter.GaussianBlur(2))
    a=np.minimum(np.array(rgba.split()[3]),np.array(m))
    a=np.array(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1)))
    rgba.putalpha(Image.fromarray(a))
    bb=rgba.getbbox(); rgba=rgba.crop(bb)
    if max(rgba.size)>900: rgba.thumbnail((900,900))
    rgba.save(dst); L('cut',dst,rgba.size)
for f in sorted(os.listdir('out')):
    if f.startswith(('orig_','cand_')) and f.endswith('.jpg'):
        try: cut('out/'+f,'out/head_'+f[:-4].replace('orig_','').replace('cand_','')+'.png')
        except Exception: L('cut fail',f,traceback.format_exc())
# ---------- IG reference ----------
try:
    subprocess.run(['yt-dlp','-o','out/ref.%(ext)s','-f','mp4/best','https://www.instagram.com/reel/DfN9e43P9jD/'],timeout=300)
    vids=[f for f in os.listdir('out') if f.startswith('ref.')]
    L('ig',vids)
    if vids:
        from faster_whisper import WhisperModel
        m=WhisperModel('medium',compute_type='int8')
        segs,info=m.transcribe('out/'+vids[0],language='pt')
        open('out/ref_transcript.txt','w').write('\n'.join(f"[{s.start:.1f}] {s.text}" for s in segs))
        subprocess.run(['ffmpeg','-y','-i','out/'+vids[0],'-vf','fps=1/3,scale=240:-2,tile=6x4','-frames:v','1','out/ref_sheet.jpg'])
        subprocess.run(['ffmpeg','-y','-i','out/'+vids[0],'-vf','scale=432:768,fps=24','-c:v','libx264','-preset','slow','-crf','32','-g','48','-pix_fmt','yuv420p','-c:a','aac','-b:a','64k','-ac','1','-movflags','+faststart','out/original_leve.mp4'])
        os.remove('out/'+vids[0])
except Exception: L('ig fail',traceback.format_exc())
