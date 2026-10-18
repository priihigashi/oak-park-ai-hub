"""Abertura do reel de SP: mapa do Brasil (estilo dos fundos de mapa do reel do Rio: fundo escuro, estados com linha creme,
estado em destaque vermelho com pontos + brilho) em alta resolução, para a câmera dar zoom do país até o estado.
Fontes dos contornos: IBGE via click_that_hood (UFs) e tbrugz/geodata-br (municípios de SP).
Uso: python3 maps.py <brazil-states.geojson> <geojs-35-mun.json>   → grava ../../assets/sp/mapa_br.jpg + mapa_br.json (geometria)"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.dirname(os.path.dirname(D))
OUT = os.path.join(KIT, 'assets/sp'); os.makedirs(OUT, exist_ok=True)
UF = json.load(open(sys.argv[1]))['features']; MUN = json.load(open(sys.argv[2]))['features']
S = 3240                      # imagem quadrada: o país inteiro cabe em 1080 px com escala 1/3
LON0, LAT0, SPAN = -54.0, -14.5, 42.0   # centro e largura (graus de longitude) do quadro
K = math.cos(math.radians(LAT0))
def P(lon, lat): return ((lon - LON0) * K / SPAN + .5) * S, (-(lat - LAT0) * K / SPAN + .5) * S
def rings(f):
    g = f['geometry']; ps = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for p in ps:
        for r in p: yield r

yy, xx = np.mgrid[0:S, 0:S]
spc = P(-48.6, -22.3)
g = np.clip(1 - np.hypot((xx - spc[0]) / S * 1.3, (yy - spc[1]) / S * 1.3), 0, 1) ** 1.6
arr = np.stack([8 + 30 * g, 9 + 12 * g, 11 + 10 * g], -1).astype(np.float32)
land = Image.new('L', (S, S), 0); dl = ImageDraw.Draw(land)
edge = Image.new('L', (S, S), 0); de = ImageDraw.Draw(edge)
hi = Image.new('L', (S, S), 0); dh = ImageDraw.Draw(hi)
mun = Image.new('L', (S, S), 0); dm = ImageDraw.Draw(mun)
for f in UF:
    sp = f['properties']['sigla'] == 'SP'
    for r in rings(f):
        pts = [P(a, b) for a, b in r]
        if len(pts) < 3: continue
        dl.polygon(pts, fill=255); de.line(pts + [pts[0]], fill=150, width=3)
        if sp: dh.polygon(pts, fill=255)
for f in MUN:
    for r in rings(f):
        pts = [P(a, b) for a, b in r]
        if len(pts) > 2: dm.line(pts + [pts[0]], fill=90, width=1)
L = np.asarray(land, np.float32)[..., None] / 255
arr = arr * (1 - L * .55) + np.array([26, 28, 32]) * L * .55
RED = np.array([255, 74, 61])
M = np.asarray(hi, np.float32) / 255
G = np.asarray(hi.filter(ImageFilter.GaussianBlur(60)), np.float32)[..., None] / 255
arr = arr + RED * G * .22
dots = ((((xx % 18) - 9) ** 2 + ((yy % 18) - 9) ** 2) < 3.4 ** 2).astype(np.float32)
Pm = (dots * .5 + .12) * M
arr = arr * (1 - Pm[..., None]) + RED * Pm[..., None]
Mu = np.asarray(mun, np.float32)[..., None] / 255 * M[..., None]
arr = arr * (1 - Mu * .35) + np.array([255, 190, 180]) * Mu * .35
E = np.asarray(edge, np.float32)[..., None] / 255
arr = arr * (1 - E * .55) + np.array([242, 236, 224]) * E * .55
ed = np.clip(np.asarray(hi.filter(ImageFilter.MaxFilter(7)), np.float32) / 255 - np.asarray(hi.filter(ImageFilter.MinFilter(7)), np.float32) / 255, 0, 1)[..., None]
arr = arr * (1 - ed) + RED * ed
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(img)
x, y = P(-46.633, -23.55)   # capital
for rr, w in ((40, 4), (22, 4)):
    d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 211, 77), width=w)
d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(255, 211, 77))
a = np.asarray(img).astype(np.float32); a[::6] *= .95
a += np.random.default_rng(35).normal(0, 4, a.shape[:2])[..., None]
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(f'{OUT}/mapa_br.jpg', quality=84)
# caixa do estado (px na imagem) para o zoom
xs, ys = np.nonzero(M.T)
json.dump(dict(size=S, sp_box=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], capital=[round(x), round(y)]),
          open(f'{D}/mapa_br.json', 'w'))
print('ok', xs.min(), ys.min(), xs.max(), ys.max())
