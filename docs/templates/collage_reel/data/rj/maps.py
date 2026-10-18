"""Gera fundos editoriais (1080x1920) a partir de mapas reais (IBGE via tbrugz/geodata-br).
Cada cena tem enquadramento/realce diferente: nenhuma imagem repetida."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'bg'); os.makedirs(OUT, exist_ok=True)
W, H, SS = 1080, 1920, 2
RJ = json.load(open(f'{D}/rj_mun.json'))['features']
OTH = {k: json.load(open(f'{D}/uf{k}.json'))['features'] for k in ('35', '31', '32')}
RM = {'Rio de Janeiro','Belford Roxo','Cachoeiras de Macacu','Duque de Caxias','Guapimirim','Itaboraí','Itaguaí','Japeri','Magé',
      'Maricá','Mesquita','Nilópolis','Niterói','Nova Iguaçu','Paracambi','Petrópolis','Queimados','Rio Bonito','São Gonçalo',
      'São João de Meriti','Seropédica','Tanguá'}
BAIX = {'Belford Roxo','Duque de Caxias','Japeri','Magé','Mesquita','Nilópolis','Nova Iguaçu','Queimados','São João de Meriti','Guapimirim','Seropédica','Itaguaí','Paracambi'}

def rings(f):
    g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for p in polys:
        for r in p: yield r

def proj(lon, lat, c, z, rot):
    # equiretangular local, z = pixels por grau (antes do supersample)
    k = math.cos(math.radians(c[1]))
    x = (lon - c[0]) * k * z; y = -(lat - c[1]) * z
    if rot:
        a = math.radians(rot); x, y = x*math.cos(a) - y*math.sin(a), x*math.sin(a) + y*math.cos(a)
    return ((W*cx_ + x) * SS, (H*cy_ + y) * SS)

def render(name, center, zoom, hi=(), hi2=(), hicol=(255, 74, 61), hi2col=(255, 211, 77), rot=0, anchor=(.62, .52),
           others=False, tint=(16, 22, 34), line=(242, 236, 224), glow=True, dots=(), p1='hatch', p2='dots'):
    global cx_, cy_
    cx_, cy_ = anchor
    img = Image.new('RGB', (W*SS, H*SS), (8, 9, 11))
    # fundo: gradiente frio + mar levemente texturizado
    yy, xx = np.mgrid[0:H*SS, 0:W*SS]
    g = np.clip(1 - np.hypot((xx/(W*SS) - anchor[0])*1.1, (yy/(H*SS) - anchor[1])*0.7), 0, 1)**1.6
    base = np.stack([8 + tint[0]*g, 9 + tint[1]*g, 11 + tint[2]*g], -1)
    img = Image.fromarray(base.astype(np.uint8))
    land = Image.new('L', img.size, 0); dl = ImageDraw.Draw(land)
    edges = Image.new('L', img.size, 0); de = ImageDraw.Draw(edges)
    hl = Image.new('L', img.size, 0); dh = ImageDraw.Draw(hl)
    hl2 = Image.new('L', img.size, 0); dh2 = ImageDraw.Draw(hl2)
    feats = [(f, 'rj') for f in RJ]
    if others:
        for k, fs in OTH.items(): feats += [(f, k) for f in fs]
    for f, uf in feats:
        nm = f['properties']['name']
        for r in rings(f):
            pts = [proj(lon, lat, center, zoom, rot) for lon, lat in r]
            if len(pts) < 3: continue
            dl.polygon(pts, fill=255 if uf == 'rj' else 150)
            de.line(pts + [pts[0]], fill=110 if uf == 'rj' else 50, width=SS)
            if uf == 'rj' and nm in hi: dh.polygon(pts, fill=255)
            if uf == 'rj' and nm in hi2: dh2.polygon(pts, fill=255)
            if uf != 'rj' and uf in hi: dh.polygon(pts, fill=150)
    arr = np.asarray(img).astype(np.float32)
    L = np.asarray(land, np.float32)[..., None]/255
    arr = arr*(1 - L*.55) + np.array([24, 26, 30])*L*.55
    yy2, xx2 = np.mgrid[0:H*SS, 0:W*SS]
    pats = {'dots': (((xx2 % (14*SS)) - 7*SS)**2 + ((yy2 % (14*SS)) - 7*SS)**2 < (2.6*SS)**2).astype(np.float32),
            'hatch': (((xx2 + yy2) % (16*SS)) < 3*SS).astype(np.float32),
            'cross': ((((xx2 + yy2) % (22*SS)) < 2*SS) | (((xx2 - yy2) % (22*SS)) < 2*SS)).astype(np.float32)}
    for m, col, pat in ((hl, hicol, p1), (hl2, hi2col, p2)):
        M = np.asarray(m, np.float32)/255
        if M.max() == 0: continue
        if glow:
            G = np.asarray(m.filter(ImageFilter.GaussianBlur(30*SS)), np.float32)[..., None]/255
            arr = arr + np.array(col)*G*.16
        P = (pats[pat]*.42 + .10)*M
        arr = arr*(1 - P[..., None]) + np.array(col)*P[..., None]
        ed = np.asarray(m.filter(ImageFilter.MaxFilter(5)), np.float32)/255 - np.asarray(m.filter(ImageFilter.MinFilter(5)), np.float32)/255
        ed = np.clip(ed, 0, 1)[..., None]*.95
        arr = arr*(1 - ed) + np.array(col)*ed
    E = np.asarray(edges, np.float32)[..., None]/255
    arr = arr*(1 - E*.5) + np.array(line)*E*.5
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for lon, lat, col in dots:
        x, y = proj(lon, lat, center, zoom, rot)
        for rr, al in ((26, 40), (14, 90), (7, 255)):
            d.ellipse([x-rr*SS, y-rr*SS, x+rr*SS, y+rr*SS], outline=col if al == 255 else None, fill=col if al == 255 else None, width=3*SS)
    img = img.resize((W, H), Image.LANCZOS)
    # linhas de varredura discretas + grão
    a = np.asarray(img).astype(np.float32)
    a[::4] *= .94
    rng = np.random.default_rng(abs(hash(name)) % 2**32)
    a += rng.normal(0, 5, a.shape[:2])[..., None]
    # vinheta
    vy, vx = np.mgrid[0:H, 0:W]
    v = np.clip(1 - .55*np.hypot((vx/W - .5)*1.2, (vy/H - .5))**2*2, .35, 1)[..., None]
    img = Image.fromarray(np.clip(a*v, 0, 255).astype(np.uint8))
    img.save(f'{OUT}/{name}.jpg', quality=86)
    print(name)

RIO = (-43.40, -22.90); STATE = (-42.65, -22.25); NIT = (-43.10, -22.88)
ALL = {f['properties']['name'] for f in RJ}
render('i01', (-43.35, -22.80), 560, hi=RM, rot=-8, anchor=(.56, .46), p1='dots')
render('i02', STATE, 240, hi2={'Rio de Janeiro'}, anchor=(.60, .50), tint=(14, 20, 40))
render('i03', (-43.45, -22.92), 900, hi2={'Rio de Janeiro'}, rot=12, anchor=(.58, .56), tint=(26, 18, 12), p2='hatch')
render('i04', (-42.2, -21.6), 330, rot=-20, anchor=(.70, .40), tint=(10, 18, 28))
render('i05', (-45.5, -20.5), 115, hi={'35', '31', '32'}, hi2=ALL, others=True, hicol=(91, 124, 255), anchor=(.60, .48), glow=False, p1='dots', p2='hatch')
render('i06', (-43.30, -22.78), 760, hi=BAIX, hi2={'Rio de Janeiro'}, rot=-30, anchor=(.55, .50), p1='cross', p2='dots')
render('i07', (-43.50, -22.90), 1100, hi={'Rio de Janeiro'}, rot=25, anchor=(.64, .48), tint=(30, 14, 12), p1='cross')
render('i08', (-43.10, -22.70), 620, hi2={'Rio de Janeiro', 'Niterói'}, rot=-45, anchor=(.60, .55), tint=(12, 12, 22), glow=False, p2='hatch')
render('i09', (-43.20, -22.88), 1500, anchor=(.66, .50), tint=(22, 16, 26), dots=[(-43.1745, -22.9035, (255, 211, 77))])
render('i10', (-43.29, -22.84), 1250, hi={'Rio de Janeiro'}, rot=60, anchor=(.52, .54), tint=(34, 10, 10), glow=False, p1='hatch')
render('i11', (-43.27, -22.86), 1700, rot=-15, anchor=(.62, .50), tint=(30, 8, 8), dots=[(-43.2780, -22.8410, (255, 74, 61)), (-43.2690, -22.8600, (255, 74, 61))])
render('i12', (-43.60, -22.75), 520, hi2=RM - {'Rio de Janeiro'}, rot=-60, anchor=(.78, .62), tint=(18, 18, 18), p2='cross')
render('i13', (-48.0, -15.8), 60, hi={'35', '31', '32'}, hi2=ALL, others=True, hicol=(91, 124, 255), anchor=(.66, .62), glow=False, tint=(10, 14, 30), p1='hatch', p2='dots')
render('i14', NIT, 1150, hi={'Niterói', 'São Gonçalo'}, rot=35, anchor=(.58, .50), tint=(14, 22, 30), p1='dots')
render('i15', STATE, 300, hi=RM, hi2={'Rio de Janeiro'}, rot=-10, anchor=(.55, .60), tint=(20, 20, 26), p1='hatch', p2='dots')
