#!/usr/bin/env bash
# Instala fontes/emojis/playwright e monta assets/ para o motor de colagem.
set -e
cd "$(dirname "$0")"
[ -f package.json ] || npm init -y >/dev/null
npm i -s @fontsource/anton @fontsource/fraunces @fontsource/jetbrains-mono @twemoji/svg playwright
mkdir -p assets
F=node_modules/@fontsource
cp $F/anton/files/anton-latin-400-normal.woff2 $F/fraunces/files/fraunces-latin-900-normal.woff2 \
   $F/fraunces/files/fraunces-latin-700-italic.woff2 $F/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2 \
   $F/jetbrains-mono/files/jetbrains-mono-latin-700-normal.woff2 assets/
for e in 1f34c 1f33e 1fad7 1f9c5 1f345 1fad8 2615 1f69c 23f0 1f37d 1f50e; do cp node_modules/@twemoji/svg/$e.svg assets/; done
python3 - <<'PY'
import numpy as np; from PIL import Image; from scipy.ndimage import gaussian_filter
r=np.random.default_rng(7)
n=r.normal(128,40,(600,600)).clip(0,255).astype(np.uint8); a=(np.abs(r.normal(0,1,(600,600)))*60).clip(0,255).astype(np.uint8)
Image.fromarray(np.dstack([n,n,n,a])).save('assets/grain.png')
f=np.zeros((800,800),np.float32)
for i in range(900):
  x,y=r.integers(0,800,2); L=r.integers(10,60); ang=r.uniform(0,np.pi)
  for k in range(L): f[int(y+k*np.sin(ang))%800,int(x+k*np.cos(ang))%800]+=1
f=gaussian_filter(f,0.7); f=(f/f.max()*255*1.8).clip(0,255).astype(np.uint8)
Image.fromarray(np.dstack([np.full_like(f,90),np.full_like(f,80),np.full_like(f,60),f])).save('assets/fibers.png')
PY
echo "OK. Rostos: coloque PNGs recortados em assets/ (ex.: assets/lula.png) — use cutout.py ou remove-bg. Fotos de terceiros NÃO vão pro repo."
