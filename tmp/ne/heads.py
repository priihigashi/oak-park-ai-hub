import json,os,sys,glob,numpy as np
from PIL import Image,ImageDraw,ImageFilter
from rembg import remove,new_session
import mediapipe as mp
D=sys.argv[1]; os.makedirs(f'{D}/out/heads',exist_ok=True)
sess=new_session('birefnet-portrait')
fm=mp.solutions.face_mesh.FaceMesh(static_image_mode=True,max_num_faces=3,refine_landmarks=False)
OVAL=[10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
rep={}
for f in sorted(glob.glob(f'{D}/cands/*.jpg')):
    k=os.path.basename(f)[:-4]
    try:
        im=Image.open(f).convert('RGB'); W,H=im.size
        r=fm.process(np.asarray(im))
        if not r.multi_face_landmarks: rep[k]='noface'; continue
        L=max(r.multi_face_landmarks,key=lambda L:max(p.x for p in L.landmark)-min(p.x for p in L.landmark)).landmark
        pts=[(L[i].x*W,L[i].y*H) for i in OVAL]
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; fw=max(xs)-min(xs); fh=max(ys)-min(ys); cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2
        x0=max(0,int(cx-fw*1.4)); x1=min(W,int(cx+fw*1.4)); y0=max(0,int(cy-fh*1.5)); y1=min(H,int(cy+fh*1.1))
        sub=im.crop((x0,y0,x1,y1))
        cut=remove(sub,session=sess,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=10)
        a=np.asarray(cut.split()[3]).astype(float)/255
        ex=[(cx+(x-cx)*1.05-x0,cy+(y-cy)*1.04-y0) for x,y in pts]
        n=len(ex); le=min(range(n),key=lambda i:ex[i][0]); ri=max(range(n),key=lambda i:ex[i][0])
        arc=[]; i=ri
        while True:
            arc.append(ex[i])
            if i==le: break
            i=(i+1)%n
        poly=[(ex[ri][0]+fw,-10),(ex[ri][0]+fw,ex[ri][1])]+arc+[(ex[le][0]-fw,ex[le][1]),(ex[le][0]-fw,-10)]
        reg=Image.new('L',sub.size,0); ImageDraw.Draw(reg).polygon(poly,fill=255); reg=reg.filter(ImageFilter.GaussianBlur(2))
        a=a*(np.asarray(reg)/255.0)
        al=Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))
        out=sub.copy(); out.putalpha(al); bb=al.point(lambda v:255 if v>40 else 0).getbbox(); out=out.crop(bb)
        s=600/out.height; out=out.resize((int(out.width*s),600),Image.LANCZOS)
        out.save(f'{D}/out/heads/{k}.png'); rep[k]='ok'
        for bg,name in [((255,211,77),'y'),((18,18,20),'k')]:
            c=Image.new('RGB',(out.width+40,out.height+40),bg); c.paste(out,(20,20),out); c.save(f'{D}/out/heads/{k}_chk_{name}.jpg',quality=80)
    except Exception as e: rep[k]='err '+str(e)[:200]
json.dump(rep,open(f'{D}/out/heads/report.json','w'),indent=1); print(rep)
