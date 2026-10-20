"""Mapa do Brasil (estados) + municípios do RJ em SVG, para o zoom da abertura (Brasil → estado do RJ).
Saída: zoom_svg.html (fragmento) e zoom_meta.json (enquadramentos inicial e final em coordenadas do SVG)."""
import json, math, os
D = os.path.dirname(os.path.abspath(__file__))
UF = json.load(open(f'{D}/br_uf.json'))['features']
RJM = json.load(open(f'{D}/rj_mun.json'))['features']
LAT0 = -15.0; K = math.cos(math.radians(LAT0)); S = 40.0   # 40 unidades SVG por grau

def P(lon, lat): return ((lon + 75) * K * S, (6 - lat) * S)

def rings(g):
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for p in polys:
        for r in p: yield r

def path(g, tol):
    out = []
    for r in rings(g):
        pts = [P(*c) for c in r]; keep = [pts[0]]
        for x, y in pts[1:]:
            if abs(x - keep[-1][0]) + abs(y - keep[-1][1]) >= tol: keep.append((x, y))
        if len(keep) < 3: continue
        out.append('M' + 'L'.join(f'{x:.2f},{y:.2f}' for x, y in keep) + 'Z')
    return ''.join(out)

states = []; rj = ''
for f in UF:
    sg = f['properties']['sigla']
    d = path(f['geometry'], 0.2 if sg in ('SP','MG','ES') else 1.6)
    if sg == 'RJ': rj = path(f['geometry'], 0.06)
    else: states.append(d)
mun = ''.join(path(f['geometry'], 0.1) for f in RJM)

def bbox(feats):
    xs = []; ys = []
    for f in feats:
        for r in rings(f['geometry']):
            for c in r: x, y = P(*c); xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)
BR = bbox(UF); RJB = bbox([f for f in UF if f['properties']['sigla'] == 'RJ'])
BW=BR[2]-BR[0]; RW=RJB[2]-RJB[0]
s0=940/BW; s1=2300/RW
FX,FY=P(-43.30,-22.86)  # foco final: capital e região metropolitana
CAM={'s0':s0,'x0':540-s0*(BR[0]+BR[2])/2,'y0':1060-s0*(BR[1]+BR[3])/2,'s1':s1,'x1':600-s1*FX,'y1':1100-s1*FY}
ps=14/s1; pr=2.4/s1
svg = f'''<svg class="zmap" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">
<defs>
<pattern id="zdots" width="{ps:.3f}" height="{ps:.3f}" patternUnits="userSpaceOnUse"><circle cx="{ps/2:.3f}" cy="{ps/2:.3f}" r="{pr:.3f}" fill="#FF4A3D"/></pattern>
<filter id="zglow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{10/s1:.3f}"/></filter>
</defs>
<g id="zcam" data-cam='{json.dumps(CAM)}'>
<path d="{''.join(states)}" fill="#1e2127" stroke="rgba(242,236,224,.5)" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
<path d="{rj}" fill="#FF4A3D" opacity=".35" filter="url(#zglow)"/>
<path d="{rj}" fill="url(#zdots)" opacity=".85"/>
<path class="zmun" d="{mun}" fill="none" stroke="rgba(255,74,61,.55)" stroke-width="1" vector-effect="non-scaling-stroke" opacity="0"/>
<path d="{rj}" fill="none" stroke="#FF4A3D" stroke-width="2.6" vector-effect="non-scaling-stroke"/>
</g></svg>'''
open(f'{D}/zoom_svg.html', 'w').write(svg)
json.dump({'br': BR, 'rj': RJB}, open(f'{D}/zoom_meta.json', 'w'))
print(len(svg), BR, RJB)
