"""Reel Parte 2 — Bahia × Santa Catarina. Estilo do Reel Rio / São Paulo (mapa escuro com estado aceso)
+ kit da Bahia (eyebrow, rows, stamp, legenda karaokê 2 linhas). Gera out/index.html (prévia com controles)."""
import json, html, re, os
B = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(f'{B}/timeline.json'))
S = {o['id']: o for o in TL}
DUR = TL[-1]['e']
MS = 5  # mapa base = 613x639 * 5
BOX = json.load(open(f'{B}/bbox.json'))
MAP = json.load(open(f'{B}/brazil.json'))
def norm(w): return re.sub(r'[^\wÀ-ú]', '', w.lower())
def W(sid, tok, n=0, off=0.0):
    k = 0
    for w, t in S[sid]['words']:
        if norm(w) == norm(tok) or norm(w).startswith(norm(tok)):
            if k == n: return round(max(0, t + off), 2)
            k += 1
    raise SystemExit(f'word {tok} not in {sid}')
def G(sid, tok, n=0, off=0.0): return round(S[sid]['s'] + W(sid, tok, n, off), 2)  # tempo global

def kar(sid, maxc=54):
    """Legenda: páginas de 2 linhas cheias (~62 caracteres), divididas por igual (sem página com 1 palavra); só a cor anda."""
    ws = S[sid]['words']; tot = sum(len(w) + 1 for w, _ in ws)
    n = max(1, -(-tot // maxc)); tgt = tot / n; toks = []; cur = 0; pg = 1
    for i, (w, t) in enumerate(ws):
        L = len(w) + 1
        if i and pg < n and cur + L / 2 > tgt * pg and cur > 0: toks.append('/'); pg += 1
        toks.append(f"{html.escape(w.replace(':', ''))}:{t}"); cur += L
    return f'<div class="kar karfull el" data-words="{" ".join(toks)}" style="left:110px;top:1410px;width:860px"></div>'

CH = ['PERGUNTA', 'PL', 'PT', 'REGIÃO', '2025']
def rail(active):
    xs = [110 + i * 215 for i in range(5)]
    dots = ''.join(f'<div class="st{" on" if i == active else ""}{" past" if i < active else ""}" style="left:{x}px"><i></i><b>{y}</b></div>' for i, (x, y) in enumerate(zip(xs, CH)))
    return f'<div class="rail el" data-a="fade" data-t=".05" data-d=".3" style="left:0;top:150px"><div class="line"></div><div class="fill" style="width:{xs[active] - 60}px"></div>{dots}</div>'

def scene(sid, inner, src, shade='shadeMapT'):
    o = S[sid]
    s = f'<div class="el srcline" data-a="fade" data-t=".4" style="left:110px;top:1640px;width:860px">FONTE: {src}</div>'
    return f'<section class="scene mapsc" data-s="{o["s"]}" data-e="{o["e"]}" data-in="cut" data-theme="dark" data-vfill="0"><div class="{shade}"></div><div class="safe">{inner}</div>{kar(sid)}{s}</section>\n'

def eb(n, txt, t=.05, top=300):
    num = f'<b>{n:02d}</b>' if n else ''
    return f'<div class="el eyebrow" data-flow="m:1" data-ftop="{top}" data-a="left" data-t="{t}" style="left:80px">{num}{txt}</div>'
def ide(k, lab): return f'<i class="ide {k}">{lab}</i>'
ESQ, CESQ, DIR = ide('esq', 'ESQUERDA'), ide('esq', 'CENTRO-ESQUERDA'), ide('dir', 'DIREITA')
Y, R, BL = '#FFD34D', '#FF4A3D', '#4D6BFF'
IDS = 'IDEOLOGIA: BOLOGNESI ET AL. (DADOS, 2023)'
FB = 'FBSP, ANUÁRIO 2026 (MORTES VIOLENTAS INTENCIONAIS, 2025)'

def tile(name, sub, val, frac, color, t, x):
    v = str(val).replace('.', ',')
    return (f'<div class="tile">'
            f'<div class="tk">{name}<small>{sub}</small></div>'
            f'<div class="tv" style="color:{color}"><span class="cnt" data-t="{t}" data-d=".9" data-from="0" data-to="{val}" data-dec="1">0</span></div>'
            f'<div class="ttrack"><div class="bar" data-t="{t}" data-d=".9" data-to="{int(400 * frac)}" style="background:{color}"></div></div></div>')
def tiles(a, b, t, flow, gap=34):
    return f'<div class="el tiles" data-flow="{flow}" data-gap="{gap}" data-a="fade" data-t="{t}" style="left:80px">{a}{b}</div>'
def row(k, v, frac, color, t, sub='', fade=None):
    sb = f'<small>{sub}</small>' if sub else ''
    fa = f' data-a="fade" data-t="{fade}"' if fade is not None else ''
    bar = f'<div class="track"><div class="bar" data-t="{t}" data-d=".7" data-to="{int(330 * frac)}" style="background:{color}"></div></div>'
    return f'<div class="row"{fa}><div class="k">{k}{sb}</div>{bar}<div class="v" style="color:{color}">{v}</div></div>'

def center(ufs):
    x0 = min(BOX[u][0] for u in ufs); y0 = min(BOX[u][1] for u in ufs); x1 = max(BOX[u][2] for u in ufs); y1 = max(BOX[u][3] for u in ufs)
    return (x0 + x1) / 2 * MS, (y0 + y1) / 2 * MS, (x1 - x0) * MS, (y1 - y0) * MS
def frame(ufs, w=820, h=None, fy=1110):
    cx, cy, bw, bh = center(ufs); s = w / bw
    if h: s = min(s, h / bh)
    return [round(s, 4), round(cx), round(cy), 540, fy]
def lab(t0, t1, uf, txt, cls='', dx=0, dy=0):
    cx, cy, _, _ = center([uf]); return [t0, t1, cx + dx * MS, cy + dy * MS, txt, cls]

NE_ESQ = ['ba', 'ce', 'pi', 'rn', 'ma', 'pb']; NE_DIR = ['al', 'pe', 'se']; NE = NE_ESQ + NE_DIR
CAM, HL, LAB, H = [], [], [], []

# ---------- c1 · gancho ----------
s = 'c1'; o = S[s]
BRA = frame(['rs', 'rr', 'ac', 'pb'], w=760, h=760, fy=1060)
CAM += [[0] + BRA, [o['e'] - .2] + [BRA[0] * 1.06] + BRA[1:]]
HL += [[G(s, 'bahia', 0, -.1), 'ba', 'esq', .5], [G(s, 'santa', 0, -.1), 'sc', 'dir', .5]]
LAB += [lab(G(s, 'bahia', 0, .1), o['e'], 'ba', 'BAHIA<small>PT ' + ESQ + ' DESDE 2007</small>', 'r', 0, 0),
        lab(G(s, 'santa', 0, .1), o['e'], 'sc', 'SANTA CATARINA<small>NUNCA TEVE O PT</small>', 'b', 0, 0)]
H.append(scene(s, f'''
{eb(0, 'O COMENTÁRIO QUE RECEBEMOS', top=300)}
<div class="el cmt" data-flow="m:2" data-gap="26" data-a="up" data-t="{W(s, 'recebemos', 0, -.1)}" style="left:80px;width:920px"><i class="av"></i><div><div class="who"><span></span>agora mesmo</div><div class="ct">PT há 20 anos na Bahia × Santa Catarina, nunca governada pelo PT: onde está melhor?</div></div></div>
<div class="el h" data-flow="m:3" data-gap="34" data-a="slam" data-t="{W(s, 'onde', 0, -.12)}" data-shake="1" style="left:80px;width:920px;font-size:110px;color:#fff">ONDE ESTÁ <span class="hl">MELHOR?</span></div>
''', 'COMENTÁRIO RECEBIDO NO NOSSO PERFIL · TSE', shade='shadeMapH'))

# ---------- c2 · mesmo partido, PL ----------
s = 'c2'; o = S[s]
SCF = frame(['sc'], w=700, fy=1150); RJF = frame(['rj'], w=640, fy=1150); BOTH = frame(['sc', 'rj', 'sp', 'pr'], w=900, h=560, fy=1150)
CAM += [[o['s'] + .1] + SCF, [G(s, 'mas', 0, -.2)] + SCF, [G(s, 'rio', 0, .1)] + RJF, [G(s, 'triplo', 0, -.4)] + RJF, [o['e'] - .1] + BOTH]
HL += [[G(s, 'rio', 0, -.1), 'rj', 'dir', .5]]
LAB += [lab(o['s'] + .3, G(s, 'rio', 0, -.1), 'sc', 'SC <b>7,6</b>', 'b big', 6, 4),
        lab(G(s, 'rio', 0, .5), G(s, 'triplo', 0, -.3), 'rj', 'RJ <b>22,6</b>', 'b big', 0, 10),
        lab(G(s, 'triplo', 0, .1), o['e'], 'sc', 'SC 7,6', 'b', 0, 0), lab(G(s, 'triplo', 0, .1), o['e'], 'rj', 'RJ 22,6', 'b', 0, 0)]
H.append(scene(s, rail(1) + f'''
{eb(1, f'MESMO PARTIDO · PL {DIR}')}
<div class="el note" data-flow="m:2" data-gap="22" data-a="fade" data-t=".2" style="left:80px">MORTES VIOLENTAS A CADA 100 MIL HABITANTES · 2025</div>
{tiles(tile('SANTA CATARINA', f'PL {DIR} · MENOR DO BRASIL', 7.6, 7.6 / 22.6, BL, W(s, 'menor', 0, -.2), 0),
       tile('RIO DE JANEIRO', f'PL {DIR} EM 2025', 22.6, 1, BL, W(s, 'rio', 0, -.05), 470), W(s, 'santa', 0, -.2), 'm:3', 30)}
<div class="el stamp-r" data-flow="m:4" data-gap="34" data-a="stamp" data-t="{W(s, 'triplo', 0, -.1)}" data-d=".35" data-r="-2" style="left:80px;white-space:nowrap;font-size:54px">QUASE O TRIPLO</div>
<div class="el fine" data-flow="m:5" data-gap="26" data-a="fade" data-t="{W(s, 'triplo', 0, .4)}" style="left:80px">O RIO TEM MILÍCIAS E FACÇÕES HÁ DÉCADAS, COM GOVERNOS DE VÁRIOS PARTIDOS: O PONTO DE PARTIDA PESA MAIS QUE A SIGLA. RJ HOJE: CASTRO (PL) RENUNCIOU EM MAR/2026; DOUGLAS RUAS (PL) FOI ELEITO EM 04/10/2026.</div>
''', FB + ' · TSE · ' + IDS))

# ---------- c3 · do outro lado, PT ----------
s = 'c3'; o = S[s]
PIF = frame(['pi'], w=560, h=500, fy=1170); PB = frame(['pi', 'ba'], w=800, h=560, fy=1160)
CAM += [[o['s'] + .1] + PIF, [G(s, 'bahia', 0, -.3)] + PIF, [G(s, 'bahia', 0, .5)] + PB, [o['e'] - .1] + [PB[0] * 1.04] + PB[1:]]
HL += [[G(s, 'piauí', 0, -.1), 'pi', 'esq', .5]]
LAB += [lab(G(s, 'piauí', 0, .2), o['e'], 'pi', 'PI 17,1', 'r', 0, 6), lab(G(s, 'bahia', 0, .3), o['e'], 'ba', 'BA 36,8', 'r', 0, 0)]
H.append(scene(s, rail(2) + f'''
{eb(2, f'MESMO PARTIDO · PT {ESQ}')}
<div class="el note" data-flow="m:2" data-gap="22" data-a="fade" data-t=".2" style="left:80px">MORTES VIOLENTAS A CADA 100 MIL HABITANTES · 2025</div>
{tiles(tile('PIAUÍ', f'PT {ESQ} · MENOR DO NORDESTE', 17.1, 17.1 / 36.8, R, W(s, 'piauí', 0, -.1), 0),
       tile('BAHIA', f'PT {ESQ} · MAIOR DO NORDESTE', 36.8, 1, R, W(s, 'bahia', 0, -.05), 470), W(s, 'piauí', 0, -.3), 'm:3', 30)}
<div class="el stamp-r" data-flow="m:4" data-gap="34" data-a="stamp" data-t="{W(s, 'dobro', 0, -.1)}" data-d=".35" data-r="-2" style="left:80px;white-space:nowrap;font-size:54px">MAIS QUE O DOBRO</div>
<div class="el fine" data-flow="m:5" data-gap="26" data-a="fade" data-t="{W(s, 'dobro', 0, .4)}" style="left:80px">O PT GOVERNA O PIAUÍ DESDE 2015 E A BAHIA DESDE 2007. A BAHIA É A 2ª MAIOR TAXA DO PAÍS, ATRÁS DO AMAPÁ (42,5), GOVERNADO PELO SOLIDARIEDADE (CENTRO-DIREITA).</div>
''', FB + ' · ' + IDS))

# ---------- c4 · não é o partido ----------
s = 'c4'; o = S[s]
NEF = frame(NE, w=760, h=640, fy=1100)
CAM += [[o['s'] + .1] + NEF, [o['e'] - .1] + [NEF[0] * 1.05] + NEF[1:]]
HL += [[G(s, 'nordeste', 0, .2 + i * .08), u, 'esq', .4] for i, u in enumerate(NE_ESQ) if u not in ('pi', 'ba')]
HL += [[G(s, 'direita', 0, -.1 + i * .08), u, 'dir', .4] for i, u in enumerate(NE_DIR)]
H.append(scene(s, rail(3) + f'''
{eb(3, 'NORDESTE · MORTES VIOLENTAS POR 100 MIL · 2025')}
<div class="el h" data-flow="m:2" data-gap="30" data-a="slam" data-t="{W(s, 'então', 0, -.1)}" style="left:80px;width:920px;font-size:76px;color:#fff">NÃO É O PARTIDO. <span class="hl">É A REGIÃO E O PONTO DE PARTIDA.</span></div>
<div class="el rows" data-flow="m:3" data-gap="34" data-a="fade" data-t="{W(s, 'nordeste', 0, -.2)}" style="left:80px">
  {row('ESTADOS DE ESQUERDA', '28,7', 28.7 / 29.4, R, W(s, 'esquerda', 0), sub='BA · CE · PI · RN · PT ' + ESQ + '<br>MA · PB · PSB ' + CESQ)}
  {row('ESTADOS DE DIREITA', '29,4', 1, BL, W(s, 'direita', 0), sub='AL · MDB ' + DIR + '<br>PE · SE · PSD ' + DIR)}</div>
<div class="el stamp-o" data-flow="m:4" data-gap="34" data-a="stamp" data-t="{W(s, 'polícia', 0, -.1)}" data-d=".35" data-r="-1.5" style="left:80px;font-size:40px;width:920px">POLÍCIA, PRESÍDIOS E INVESTIGAÇÃO SÃO DO GOVERNO DO ESTADO, NÃO DO PRESIDENTE</div>
<div class="el fine" data-flow="m:5" data-gap="24" data-a="fade" data-t="{W(s, 'patamar', 0, .2)}" style="left:80px">MÉDIA SIMPLES DOS ESTADOS (CÁLCULO NOSSO, FBSP). PELA MEDIANA: 29,4 × 33,0. A MÉDIA NACIONAL QUE CIRCULA (PODER360: DIREITA 14,8 × ESQUERDA 23,4) MISTURA REGIÕES: SUL E SUDESTE SÃO QUASE TODOS DE DIREITA.</div>
''', FB + ' · PODER360, 2026 · CONSTITUIÇÃO, ART. 144 · ' + IDS, shade='shadeMapF'))

# ---------- c5 · fechamento pra cima ----------
s = 'c5'; o = S[s]
CAM += [[o['s'] + .1] + NEF, [o['e'] - .1] + [NEF[0] * 1.08] + NEF[1:]]
DOWN = ['pi', 'ba', 'pe', 'ce', 'al', 'pb', 'se', 'ma']
t0 = G(s, 'reduziram', 0, -.3)
HL += [[o['s'] + .05, u, 'off', .3] for u in NE] + [[t0 + i * .12, u, 'yel', .35] for i, u in enumerate(DOWN)] + [[t0 + 1.0, 'rn', 'esq', .4]]
LAB += [lab(t0 + 1.1, o['e'], 'rn', 'RN +19,6%', 'r', 6, -2), lab(t0 + .4, o['e'], 'ba', 'BA −9,6%', 'y', 0, 0), lab(t0 + .6, o['e'], 'pi', 'PI −15,7%', 'y', 0, 4)]
H.append(scene(s, rail(4) + f'''
{eb(4, 'EM 2025 · MORTES VIOLENTAS')}
<div class="el counter" data-flow="m:2" data-gap="22" data-a="up" data-t="{W(s, 'oito', 0, -.2)}" data-o="{W(s, 'comparar', 0, -.3)}" style="left:80px;width:920px"><span class="big">8 DE 9</span><b>ESTADOS DO NORDESTE<br>REDUZIRAM AS MORTES</b></div>
<div class="el h" data-flow="m:2" data-a="slam" data-t="{W(s, 'comparar', 0, -.15)}" style="left:80px;width:920px;font-size:74px;color:#fff">COMPARAR SUL COM NORDESTE É COMPARAR <span class="hl">PONTO DE PARTIDA,</span> NÃO GOVERNO.</div>
<div class="el fine" data-flow="m:3" data-gap="26" data-a="fade" data-t="{W(s, 'mortes', 0, .3)}" style="left:80px">SÓ O RIO GRANDE DO NORTE SUBIU (+19,6%). A BAHIA CAI HÁ 3 ANOS, E A QUEDA AUMENTA: −6,0% (2023), −8,2% (2024), −9,6% (2025).</div>
<div class="el repost" data-flow="m:4" data-gap="40" data-a="slam" data-t="{W(s, 'vídeo', 0, -.15)}" data-shake="1" style="left:80px;width:920px;font-size:54px">VÍDEO COMPLETO NO PERFIL<small>Parte 1: Bahia e Norte, culpa da esquerda?</small></div>
''', FB + ' · SSP-BA (2023–2024)'))

# ---------- mapa ----------
paths = ''.join(f'<path data-uf="{l["id"]}" d="{l["path"]}"/>' for l in MAP['locations'])
MAPSVG = (f'<div id="map" style="width:{613*MS}px;height:{639*MS}px"><svg viewBox="0 0 613 639" width="{613*MS}" height="{639*MS}">'
          '<defs><pattern id="hR" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3" height="3" fill="rgba(255,74,61,.22)"/><line x1="0" y1="0" x2="0" y2="3" stroke="rgba(255,74,61,.75)" stroke-width=".7"/></pattern>'
          '<pattern id="hB" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3" height="3" fill="rgba(77,107,255,.22)"/><line x1="0" y1="0" x2="0" y2="3" stroke="rgba(110,135,255,.8)" stroke-width=".7"/></pattern>'
          '<pattern id="hY" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3" height="3" fill="rgba(255,211,77,.2)"/><line x1="0" y1="0" x2="0" y2="3" stroke="rgba(255,211,77,.8)" stroke-width=".7"/></pattern></defs>'
          f'<g class="states">{paths}</g></svg></div><div class="mapvig"></div>')

CSS = open(f'{B}/base.css').read() + open(f'{B}/extra.css').read()
CFG = f'<script>window.DUR={DUR:.2f};window.MAPCAM={json.dumps(CAM)};window.MAPHL={json.dumps(HL)};window.MAPLAB={json.dumps(LAB, ensure_ascii=False)};</script>'
PP = open(f'{B}/pp.html').read()
CTRL = open(f'{B}/ctrl.html').read().replace('{DUR}', f'{DUR:.2f}')
page = f'''<meta charset="utf-8"><title>Bahia × SC · Prévia</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="fx.css">
<style>{CSS}</style>
<div class="pv-head"><h1>Bahia × Santa Catarina · prévia</h1><small id="ver">v1 · 19/10/2026 · voz provisória</small></div>
<div class="pv-frame" id="frame"><div id="scaler"><div id="stage">
<div id="mapwrap">{MAPSVG}</div>
{"".join(H)}
<div id="maplabs"></div>
<div id="grain"></div><div id="foot">@tentandochegaratevoce</div></div></div></div>
{CTRL}
{CFG}<script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script><script src="map.js"></script><script src="fit.js"></script><script src="layout.js"></script>
<script src="player.js"></script>
{PP}'''
os.makedirs(f'{B}/out', exist_ok=True)
open(f'{B}/out/index.html', 'w').write(page)
print('ok', round(DUR, 2))
