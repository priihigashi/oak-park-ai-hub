import json,os,io,requests,numpy as np
from PIL import Image,ImageFilter
os.makedirs('out/heads',exist_ok=True)
job=json.load(open('job/job.json'))
H={'User-Agent':'reelbot/1.0 (news reel research)'}
from rembg import remove,new_session
sess=new_session('birefnet-portrait')
import mediapipe as mp
fm=mp.solutions.face_mesh.FaceMesh(static_image_mode=True,max_num_faces=1,refine_landmarks=False)
JAW=[234,93,132,58,172,136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454]
def img_for(title,lang):
    r=requests.get(f'https://{lang}.wikipedia.org/w/api.php',params={'action':'query','titles':title,'prop':'pageimages','piprop':'original','format':'json'},headers=H).json()
    p=list(r['query']['pages'].values())[0]; u=p['original']['source']
    return Image.open(io.BytesIO(requests.get(u,headers=H).content)).convert('RGB'),u
log={}
for h in job.get('heads',[]):
    try:
        im,u=img_for(h['title'],h.get('lang','en'))
        if max(im.size)>1600: im.thumbnail((1600,1600))
        cut=remove(im,session=sess,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=10)
        a=np.array(cut); W,Hh=im.size
        res=fm.process(np.array(im))
        if res.multi_face_landmarks:
            L=res.multi_face_landmarks[0].landmark
            fh=(L[152].y-L[10].y)*Hh
            off=0.05*fh
            pts=[(L[i].x*W,L[i].y*Hh+off) for i in JAW]
            from PIL import ImageDraw
            m=Image.new('L',(W,Hh),255); d=ImageDraw.Draw(m)
            poly=[(0,pts[0][1])]+pts+[(W,pts[-1][1]),(W,Hh),(0,Hh)]
            d.polygon(poly,fill=0)
            m=m.filter(ImageFilter.GaussianBlur(1.5))
            a[...,3]=(a[...,3].astype(float)*np.array(m)/255).astype(np.uint8)
        else: log[h['id']+'_noface']=True
        o=Image.fromarray(a); bb=o.getbbox(); o=o.crop(bb)
        o.thumbnail((700,700)); o.save(f"out/heads/{h['id']}.png")
        log[h['id']]=u
    except Exception as e:
        log[h['id']]='ERR '+repr(e)[:200]
json.dump(log,open('out/heads/log.json','w'),indent=1)
