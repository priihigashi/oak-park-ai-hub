import sys,os,numpy as np
from PIL import Image, ImageDraw, ImageFilter
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
D=os.path.dirname(os.path.abspath(__file__))
fl=vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path=f'{D}/face_landmarker.task'),num_faces=4))
sg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=mpt.BaseOptions(model_asset_path=f'{D}/selfie_multiclass.tflite'),output_confidence_masks=True))
OVAL=[10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
def head(k,pick=0,stroke=14,H_OUT=560):
    im=Image.open(f'{D}/src/{k}.img').convert('RGB'); im.thumbnail((1400,1400))
    if max(im.size)<700: im=im.resize((im.width*3,im.height*3),Image.LANCZOS)
    W,H=im.size; arr=np.ascontiguousarray(np.asarray(im))
    res=fl.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=arr))
    if not res.face_landmarks: return 'noface'
    faces=sorted(res.face_landmarks,key=lambda L:-(max(p.x for p in L)-min(p.x for p in L)))
    L=faces[pick]
    pts=[(L[i].x*W,L[i].y*H) for i in OVAL]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; fw=max(xs)-min(xs); fh=max(ys)-min(ys); cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2
    # crop around head first for better seg
    x0=max(0,int(cx-fw*1.3)); x1=min(W,int(cx+fw*1.3)); y0=max(0,int(cy-fh*1.4)); y1=min(H,int(cy+fh*1.0))
    sub=im.crop((x0,y0,x1,y1)); sa=np.ascontiguousarray(np.asarray(sub))
    cm=sg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=sa)).confidence_masks
    c=[np.squeeze(m.numpy_view()) for m in cm]
    headp=c[1]+c[3]+c[5]*0.6   # hair + face-skin + accessories
    a=np.clip((headp-0.35)/0.3,0,1)
    # jaw limit polygon (in sub coords)
    ex=[(cx+(x-cx)*1.06-x0,cy+(y-cy)*1.03-y0) for x,y in pts]
    n=len(ex); left=min(range(n),key=lambda i:ex[i][0]); right=max(range(n),key=lambda i:ex[i][0])
    arc=[]; i=right
    while True:
        arc.append(ex[i])
        if i==left: break
        i=(i+1)%n
    poly=[(ex[right][0]+fw*0.9,-10),(ex[right][0]+fw*0.9,ex[right][1])]+arc+[(ex[left][0]-fw*0.9,ex[left][1]),(ex[left][0]-fw*0.9,-10)]
    reg=Image.new('L',sub.size,0); ImageDraw.Draw(reg).polygon(poly,fill=255)
    el=Image.new('L',sub.size,0); ecx,ecy=cx-x0,cy-y0-0.22*fh; rx,ry=0.86*fw,1.0*fh
    ImageDraw.Draw(el).ellipse((ecx-rx,ecy-ry,ecx+rx,ecy+ry),fill=255)
    reg=Image.fromarray(np.minimum(np.asarray(reg),np.asarray(el.filter(ImageFilter.GaussianBlur(6)))))
    a=a*(np.asarray(reg)/255.0)
    from scipy import ndimage as nd
    b=a>0.5; lab,nl=nd.label(b)
    if nl>1:
        sizes=nd.sum(b,lab,range(1,nl+1)); b=lab==(1+np.argmax(sizes))
    b=nd.binary_fill_holes(b); a=a*b
    al=Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))
    rgba=sub.copy(); rgba.putalpha(al)
    bb=al.point(lambda v:255 if v>40 else 0).getbbox(); rgba=rgba.crop(bb)
    s=H_OUT/rgba.height; rgba=rgba.resize((max(1,int(rgba.width*s)),H_OUT),Image.LANCZOS)
    pad=stroke+6; cv=Image.new('RGBA',(rgba.width+2*pad,rgba.height+2*pad),(0,0,0,0)); cv.paste(rgba,(pad,pad),rgba)
    ol=cv.split()[3].point(lambda v:255 if v>70 else 0).filter(ImageFilter.MaxFilter(2*stroke+1)).filter(ImageFilter.GaussianBlur(1.2))
    out=Image.new('RGBA',cv.size,(0,0,0,0)); out.paste(Image.new('RGBA',cv.size,(255,255,255,255)),(0,0),ol); out.alpha_composite(cv)
    out.save(f'{D}/out/{k}.png'); return out.size
for arg in sys.argv[1:]:
    k,_,p=arg.partition(':')
    try: print(k,head(k,int(p or 0)),flush=True)
    except Exception as ex: print(k,'ERR',repr(ex)[:200],flush=True)
