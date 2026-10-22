import json, os, asyncio, io, sys, traceback
import requests
J=json.load(open('tmpjob/job.json'))
os.makedirs('out/tts',exist_ok=True); os.makedirs('out/img',exist_ok=True)
log=[]
async def tts_one(it):
    import edge_tts
    try: c=edge_tts.Communicate(it['text'],J['voice'],rate=J['rate'],boundary='WordBoundary')
    except TypeError: c=edge_tts.Communicate(it['text'],J['voice'],rate=J['rate'])
    words=[]; audio=b''
    async for ch in c.stream():
        if ch['type']=='audio': audio+=ch['data']
        elif ch['type']=='WordBoundary': words.append({'w':ch['text'],'s':ch['offset']/1e7,'d':ch['duration']/1e7})
    open(f"out/tts/{it['id']}.mp3",'wb').write(audio)
    json.dump(words,open(f"out/tts/{it['id']}.json",'w'),ensure_ascii=False)
    log.append(f"tts {it['id']} {len(audio)}B {len(words)}w")
async def tts_all():
    for it in J['tts']: await tts_one(it)
try: asyncio.run(tts_all())
except Exception: log.append('TTS FAIL '+traceback.format_exc())
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
from PIL import Image, ImageFilter
import numpy as np
def fetch(it):
    url=it.get('url')
    if it.get('wiki'):
        r=requests.get('https://pt.wikipedia.org/api/rest_v1/page/summary/'+it['wiki'],headers=UA,timeout=30).json()
        url=(r.get('originalimage') or r.get('thumbnail'))['source']
    b=requests.get(url,headers=UA,timeout=60).content
    im=Image.open(io.BytesIO(b)).convert('RGB'); log.append(f"img {it['name']} {url} {im.size}")
    return im
def head(im,name):
    from rembg import remove, new_session
    import mediapipe as mp
    sess=new_session('birefnet-portrait')
    cut=remove(im,session=sess,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=10)
    cut.save(f'out/img/{name}_full.png')
    a=np.array(cut); H,W=a.shape[:2]
    fm=mp.solutions.face_mesh.FaceMesh(static_image_mode=True,max_num_faces=1,refine_landmarks=False)
    res=fm.process(np.array(im))
    if not res.multi_face_landmarks: log.append(f'NO FACE {name}'); return
    L=res.multi_face_landmarks[0].landmark
    P=lambda i:(L[i].x*W,L[i].y*H)
    jaw=[234,93,132,58,172,136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454]
    pts=[P(i) for i in jaw]
    top=P(10); chin=P(152); fh=chin[1]-top[1]; off=0.05*fh
    xs=np.array([p[0] for p in pts]); ys=np.array([p[1] for p in pts])
    o=np.argsort(xs); xs,ys=xs[o],ys[o]
    yy=np.arange(H)[:,None]; xx=np.arange(W)[None,:]
    jy=np.interp(np.arange(W),xs,ys)+off
    # outside face span: cut at ear level + 30% face height
    lim=np.where((np.arange(W)<xs[0])|(np.arange(W)>xs[-1]), min(ys[0],ys[-1])+0.30*fh, jy)
    keep=(yy<=lim[None,:])
    al=a[:,:,3].astype(float)*keep
    a[:,:,3]=al.astype(np.uint8)
    img=Image.fromarray(a)
    alpha=img.split()[3].filter(ImageFilter.GaussianBlur(1.2)); img.putalpha(alpha)
    bb=img.getbbox(); img=img.crop(bb)
    s=700/img.height; img=img.resize((int(img.width*s),700),Image.LANCZOS)
    pad=24; c=Image.new('RGBA',(img.width+2*pad,img.height+2*pad),(0,0,0,0)); c.paste(img,(pad,pad),img)
    al=c.split()[3].point(lambda v:255 if v>60 else 0)
    ol=al.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1))
    white=Image.new('RGBA',c.size,(255,255,255,255)); base=Image.new('RGBA',c.size,(0,0,0,0)); base.paste(white,(0,0),ol)
    base.alpha_composite(c); base.save(f'out/img/{name}_head.png'); log.append(f'head {name} ok {base.size}')
for it in J['images']:
    try:
        im=fetch(it)
        im.save(f"out/img/{it['name']}.jpg",quality=92)
        if it.get('head'): head(im,it['name'])
    except Exception: log.append(f"IMG FAIL {it['name']} "+traceback.format_exc()[-600:])
open('out/log.txt','w').write('\n'.join(log)); print('\n'.join(log))
