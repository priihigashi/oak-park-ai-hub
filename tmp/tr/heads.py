import os, re, json, urllib.request, pathlib, io
import numpy as np, cv2
from PIL import Image
from rembg import remove, new_session
A=pathlib.Path('tmp/tr/out/assets'); H=pathlib.Path('tmp/tr/out/heads'); H.mkdir(parents=True,exist_ok=True)
UA={'User-Agent':'Mozilla/5.0'}
log={}
try:
    html=urllib.request.urlopen(urllib.request.Request('https://www.congressoemfoco.com.br/justica/lava-jato-so-deu-credito-a-empreiteiro-da-oas-apos-ele-incriminar-lula',headers=UA)).read().decode('utf8','ignore')
    m=re.search(r'property="og:image"\s+content="([^"]+)"',html) or re.search(r'content="([^"]+)"\s+property="og:image"',html)
    url=m.group(1); log['pinheiro_url']=url
    open(A/'pinheiro_cef.jpg','wb').write(urllib.request.urlopen(urllib.request.Request(url,headers=UA)).read())
except Exception as e: log['pinheiro_err']=str(e)
sess=new_session('u2net_human_seg')
casc=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
src={'lula':'lula_oficial.jpg','lula2':'lula2021.png','flavio':'flavio_agsen.jpg','flavio2':'flavio_n.png','queiroz':'queiroz.jpg','moro':'moro.jpg','moro2':'moroc_0.jpg','pinheiro':'pinheiro_cef.jpg','michelle':'michelle_0.jpg'}
for k,f in src.items():
    p=A/f
    if not p.exists(): log[k]='missing'; continue
    try:
        im=Image.open(p).convert('RGBA')
        bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im); rgb=np.array(bg.convert('RGB'))
        g=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        fs=casc.detectMultiScale(g,1.1,5,minSize=(60,60))
        if len(fs)==0: log[k]='noface'; continue
        x,y,w,h=max(fs,key=lambda r:r[2]*r[3])
        x0=max(0,int(x-0.6*w)); x1=min(rgb.shape[1],int(x+1.6*w)); y0=max(0,int(y-0.9*h)); y1=min(rgb.shape[0],int(y+1.35*h))
        crop=Image.fromarray(rgb[y0:y1,x0:x1])
        cut=remove(crop,session=sess).convert('RGBA')
        a=np.array(cut)[:,:,3].astype(np.float32)/255
        H_,W_=a.shape; yy,xx=np.mgrid[0:H_,0:W_]
        cx=(x+w/2)-x0; cy=(y+0.40*h)-y0; ax=0.80*w; ay=1.02*h
        ell=((xx-cx)/ax)**2+((yy-cy)/ay)**2
        mask=np.clip((1.08-ell)/0.08,0,1)
        a2=(a*mask*255).astype(np.uint8)
        out=np.array(cut); out[:,:,3]=a2
        img=Image.fromarray(out); bb=img.getbbox(); img=img.crop(bb)
        img.thumbnail((700,700)); img.save(H/f'{k}.png'); log[k]='ok'
    except Exception as e: log[k]=str(e)
json.dump(log,open(H/'log.json','w'),indent=1)
