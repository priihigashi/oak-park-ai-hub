import json, os, io, requests, numpy as np
from PIL import Image, ImageFilter
from rembg import remove, new_session
import mediapipe as mp
UA={'User-Agent':'reel-heads/1.0 (priscila@oakpark-construction.com)'}
job=json.load(open('tmp_rj/heads.json'))
os.makedirs('tmp_rj/heads',exist_ok=True)
sess=new_session('birefnet-portrait')
fm=mp.solutions.face_mesh.FaceMesh(static_image_mode=True,max_num_faces=1,refine_landmarks=False)
JAW=[454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234]
def search(q,n):
    r=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','format':'json','generator':'search','gsrsearch':q+' filetype:bitmap','gsrnamespace':6,'gsrlimit':n,'prop':'imageinfo','iiprop':'url|size','iiurlwidth':1400},headers=UA,timeout=60).json()
    pages=sorted(r.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',99))
    return [(p['title'],p['imageinfo'][0].get('thumburl') or p['imageinfo'][0]['url']) for p in pages]
log=[]
for who,q,n in job['people']:
    k=0
    for title,url in search(q,n):
        try:
            img=Image.open(io.BytesIO(requests.get(url,headers=UA,timeout=60).content)).convert('RGB')
            W,H=img.size; a=np.array(img)
            res=fm.process(a)
            if not res.multi_face_landmarks: log.append([who,title,'noface']); continue
            L=res.multi_face_landmarks[0].landmark
            pts=np.array([[L[i].x*W,L[i].y*H] for i in range(468)])
            fh=pts[152,1]-pts[10,1]; fw=pts[454,0]-pts[234,0]
            if fw<220: log.append([who,title,'small',int(fw)]); continue
            cut=remove(img,session=sess,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=10)
            al=np.array(cut)[:,:,3].astype(np.float32)
            jaw=pts[JAW].copy(); jaw[:,1]+=fh*0.05
            poly=[(jaw[0,0]+fw*0.25,jaw[0,1]-fh*0.35),(W*2,-H),(-W,-H),(jaw[-1,0]-fw*0.25,jaw[-1,1]-fh*0.35)]
            from PIL import ImageDraw
            m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
            d.polygon([tuple(p) for p in jaw]+[(jaw[-1,0]-fw*0.25,jaw[-1,1]-fh*0.35),(-W,-H*2),(W*2,-H*2),(jaw[0,0]+fw*0.25,jaw[0,1]-fh*0.35)],fill=255)
            m=m.filter(ImageFilter.GaussianBlur(1.5))
            al=al*np.array(m,dtype=np.float32)/255
            out=np.dstack([a,al.clip(0,255).astype(np.uint8)])
            o=Image.fromarray(out,'RGBA'); bb=o.getbbox(); o=o.crop(bb)
            if o.width>900: o=o.resize((900,int(o.height*900/o.width)),Image.LANCZOS)
            fn=f'tmp_rj/heads/{who}_{k}.png'; o.save(fn,optimize=True); k+=1
            log.append([who,title,'ok',fn,int(fw)])
        except Exception as e: log.append([who,title,'err',str(e)[:120]])
json.dump(log,open('tmp_rj/heads/log.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(log,ensure_ascii=False,indent=1))
