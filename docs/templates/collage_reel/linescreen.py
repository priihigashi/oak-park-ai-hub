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
a=ap.parse_args()

im=Image.open(a.src).convert('RGBA')
if a.width: im=im.resize((a.width,int(im.height*a.width/im.width)),Image.LANCZOS)
alpha=np.asarray(im)[...,3].astype(np.float32)/255
g=np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(a.period*0.25))).astype(np.float32)/255
# contraste automático
lo,hi=np.percentile(g[alpha>.5] if (alpha>.5).any() else g,[2,98]); g=np.clip((g-lo)/max(hi-lo,1e-3),0,1)**a.gamma
if a.invert: g=1-g
H,W=g.shape; yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
th=np.deg2rad(a.angle); v=yy*np.cos(th)+xx*np.sin(th)
v=v+np.sin(xx/(W/9.0))*a.wave*a.period+np.sin(xx/(W/2.3)+1.3)*a.wave*a.period*0.6   # ondulação "gravura"
phase=(v/a.period)%1.0
d=np.abs(phase-0.5)*2                      # 0 no centro da linha, 1 na borda
thick=g                                    # mais claro = linha mais grossa
cov=np.clip((thick-d)*a.period*0.9+0.5,0,1)  # antialias
cov=cov*alpha
out=np.zeros((H,W,4),np.float32); ink=np.array(hexrgb(a.ink),np.float32)
if a.bg:
    bg=np.array(hexrgb(a.bg),np.float32)
    out[...,:3]=bg*(1-cov[...,None])+ink*cov[...,None]; out[...,3]=alpha*255
else:
    out[...,:3]=ink; out[...,3]=cov*255
Image.fromarray(out.clip(0,255).astype(np.uint8)).save(a.dst)
print('ok',a.dst,W,H)
