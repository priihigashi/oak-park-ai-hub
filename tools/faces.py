import json, os, requests, numpy as np, io
from PIL import Image, ImageFilter
job=json.load(open('job.json')); os.makedirs('out/faces',exist_ok=True)
H={'User-Agent':'oakpark-reel-bot/1.0 (priscila@oakpark-construction.com)'}
from rembg import remove, new_session
sess=new_session('birefnet-portrait')
import mediapipe as mp
fm=mp.solutions.face_mesh.FaceMesh(static_image_mode=True,max_num_faces=1,refine_landmarks=False)
OVAL=[234,93,132,58,172,136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454]
log={}
for k,title in job['photos'].items():
  try:
    j=requests.get(f'https://pt.wikipedia.org/api/rest_v1/page/summary/{title}',headers=H,timeout=30).json()
    url=j.get('originalimage',{}).get('source') or j['thumbnail']['source']
    raw=requests.get(url,headers=H,timeout=60).content
    im=Image.open(io.BytesIO(raw)).convert('RGB')
    if max(im.size)>1600: im.thumbnail((1600,1600))
    im.save(f'out/faces/{k}_orig.jpg',quality=90)
    cut=remove(im,session=sess,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=10)
    a=np.array(cut)
    res=fm.process(np.array(im))
    if res.multi_face_landmarks:
      lm=res.multi_face_landmarks[0].landmark; w,h=im.size
      pts=[(lm[i].x*w,lm[i].y*h) for i in OVAL]
      chin=lm[152].y*h; top=lm[10].y*h; fh=chin-top; extra=0.0*fh
      xs=np.array([p[0] for p in pts]); ys=np.array([p[1] for p in pts])+extra
      order=np.argsort(xs); xs,ys=xs[order],ys[order]
      Y=np.arange(h)[:,None]; X=np.arange(w)[None,:]
      cutoff=np.interp(np.arange(w),xs,ys)
      side=(np.arange(w)<xs[0])|(np.arange(w)>xs[-1])
      L=np.arange(w)<xs[0]; Rr=np.arange(w)>xs[-1]
      cutoff[L]=np.minimum(ys[0]+0.7*(xs[0]-np.arange(w)[L]),chin-0.12*fh)
      cutoff[Rr]=np.minimum(ys[-1]+0.7*(np.arange(w)[Rr]-xs[-1]),chin-0.12*fh)
      from scipy.ndimage import uniform_filter1d
      cutoff=uniform_filter1d(cutoff,size=max(3,int(0.06*w)))
      a[...,3]=np.where(Y>cutoff[None,:],0,a[...,3])
      al=Image.fromarray(a[...,3]).filter(ImageFilter.GaussianBlur(1.6)); a[...,3]=np.array(al)
      log[k]='ok'
    else: log[k]='noface'
    o=Image.fromarray(a); bb=o.getbbox(); o=o.crop(bb)
    o.thumbnail((900,900)); o.save(f'out/faces/{k}.png')
    log[k+'_src']=url
  except Exception as ex: log[k]='err '+repr(ex)
json.dump(log,open('out/faces/log.json','w'),indent=1)
