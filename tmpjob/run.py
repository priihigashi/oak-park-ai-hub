import json, re, asyncio, os, subprocess, sys, traceback
os.makedirs('out', exist_ok=True)
log = open('out/log.txt','w')
def L(*a):
    print(*a); print(*a, file=log); log.flush()
async def tts():
  import edge_tts
  d = json.load(open('tmpjob/script.json'))
  for s in d['scenes']:
    if d.get('only') and s['id'] not in d['only']: continue
    spoken = re.sub(r'\{[^|}]*\|([^}]*)\}', r'\1', s['text']).replace('¦','')
    for attempt in range(3):
      try:
        c = edge_tts.Communicate(spoken, d['voice'], rate=d['rate'], boundary="WordBoundary")
        words=[]; audio=bytearray()
        async for ch in c.stream():
            if ch['type']=='audio': audio+=ch['data']
            elif ch['type']=='WordBoundary': words.append({'t':ch['offset']/1e7,'d':ch['duration']/1e7,'w':ch['text']})
        open(f"out/{s['id']}.mp3",'wb').write(audio); json.dump(words, open(f"out/{s['id']}.json",'w'), ensure_ascii=False)
        L('tts', s['id'], len(words)); break
      except Exception: L('retry', s['id'], traceback.format_exc()[-200:])
try: asyncio.run(tts())
except Exception: L(traceback.format_exc())
try:
    subprocess.run([sys.executable,'-m','pip','install','-q','rembg[cpu]','mediapipe==0.10.14','pillow','numpy'],check=False)
    import requests
    UA={'User-Agent':'reel-bot/1.0'}
    r=requests.get('https://pt.wikipedia.org/w/api.php',params={'action':'query','titles':'Ronaldo_Caiado','prop':'pageimages','piprop':'original','format':'json'},headers=UA,timeout=30).json()
    p=list(r['query']['pages'].values())[0]; url=p['original']['source']
    open('out/orig_caiado.jpg','wb').write(requests.get(url,headers=UA,timeout=60).content); L('photo',url)
except Exception: L('photo fail',traceback.format_exc())
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

try: cut('out/orig_caiado.jpg','out/head_caiado.png')
except Exception: L('cut fail',traceback.format_exc())
