#!/usr/bin/env python3
"""Retícula de linhas (estilo gravura / "line-screen halftone") para fotos e recortes.

Transforma qualquer foto/recorte em linhas horizontais que engrossam no escuro —
o visual do repertório "Antídoto" (duotone vermelho/azul, B&W de jornal, amarelo-bandeira).

Uso:
  python3 linescreen.py in.png out.png                      # tinta preta em papel transparente? não: B&W (linhas brancas no preto)
  python3 linescreen.py in.png out.png --ink "#E0201B"      # linhas vermelhas, fundo transparente (p/ duotone)
  python3 linescreen.py in.png out.png --ink "#F4D21F" --bg "#1d3a16"   # bandeira: amarelo sobre verde escuro
  opções: --period 7 (px entre linhas, na resolução final) --wave 0.6 (ondulação) --angle 0 --gamma 1.0 --invert

Regras: --ink = cor das LINHAS (as luzes da foto). Fundo transparente por padrão.
A transparência do PNG de entrada (recorte) é preservada.
"""
import argparse, numpy as np
from PIL import Image, ImageFilter

def hexrgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))

ap=argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('dst')
ap.add_argument('--ink',default='#FFFFFF'); ap.add_argument('--bg',default=None)
ap.add_argument('--period',type=float,default=7); ap.add_argument('--wave',type=float,default=0.6)
ap.add_argument('--angle',type=float,default=0); ap.add_argument('--gamma',type=float,default=1.0)
ap.add_argument('--invert',action='store_true'); ap.add_argument('--width',type=int,default=0)
ap.add_argument('--mode',default='lines',choices=['lines','rings','dots'],help='lines = linhas retas onduladas · rings = anéis concêntricos (gravura de rosto, ref 01) · dots = retícula de pontos (objetos, ref 01)')
ap.add_argument('--center',default='1.35,-0.25',help='rings: centro dos anéis em fração (x,y) — fora do rosto fica mais bonito')
a=ap.parse_args()

im=Image.open(a.src).convert('RGBA')
if a.width: im=im.resize((a.width,int(im.height*a.width/im.width)),Image.LANCZOS)
alpha=np.asarray(im)[...,3].astype(np.float32)/255
g=np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(a.period*0.25))).astype(np.float32)/255
# contraste automático
lo,hi=np.percentile(g[alpha>.5] if (alpha>.5).any() else g,[2,98]); g=np.clip((g-lo)/max(hi-lo,1e-3),0,1)**a.gamma
if a.invert: g=1-g
H,W=g.shape; yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
th=np.deg2rad(a.angle)
if a.mode=='dots':   # retícula de pontos: raio do ponto cresce com a luz
    u=xx*np.cos(th)-yy*np.sin(th); w=xx*np.sin(th)+yy*np.cos(th)
    du=(u/a.period)%1-.5; dw=(w/a.period)%1-.5; dist=np.sqrt(du*du+dw*dw)*2   # 0 centro → ~1.41 canto
    r=np.sqrt(g)*0.78
    cov=np.clip((r-dist)*a.period*0.9+0.5,0,1)
else:
    if a.mode=='rings':
        cx,cy=[float(v) for v in a.center.split(',')]; v=np.sqrt((xx-cx*W)**2+(yy-cy*H)**2)
        v=v+np.sin(np.arctan2(yy-cy*H,xx-cx*W)*3)*a.wave*a.period*0.8
    else:
        v=yy*np.cos(th)+xx*np.sin(th)
        v=v+np.sin(xx/(W/9.0))*a.wave*a.period+np.sin(xx/(W/2.3)+1.3)*a.wave*a.period*0.6   # ondulação "gravura"
    phase=(v/a.period)%1.0
    d=np.abs(phase-0.5)*2                      # 0 no centro da linha, 1 na borda
    cov=np.clip((g-d)*a.period*0.9+0.5,0,1)    # mais claro = linha mais grossa (antialias)
cov=cov*alpha
out=np.zeros((H,W,4),np.float32); ink=np.array(hexrgb(a.ink),np.float32)
if a.bg:
    bg=np.array(hexrgb(a.bg),np.float32)
    out[...,:3]=bg*(1-cov[...,None])+ink*cov[...,None]; out[...,3]=alpha*255
else:
    out[...,:3]=ink; out[...,3]=cov*255
Image.fromarray(out.clip(0,255).astype(np.uint8)).save(a.dst)
print('ok',a.dst,W,H)
