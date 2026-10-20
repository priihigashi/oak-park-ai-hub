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

CH = ['PERGUNTA', 'PARTIDA', 'HISTÓRIA', 'RENDA', 'PARTIDO', 'REGIÃO']
def rail(active):
    xs = [110 + i * 172 for i in range(6)]
    dots = ''.join(f'<div class="st{" on" if i == active else ""}{" past" if i < active else ""}" style="left:{x}px"><i></i><b>{y}</b></div>' for i, (x, y) in enumerate(zip(xs, CH)))
    return f'<div class="rail el" data-a="fade" data-t=".05" data-d=".3" style="left:0;top:150px"><div class="line"></div><div class="fill" style="width:{xs[active] - 60}px"></div>{dots}</div>'

def scene(sid, inner, src, shade='shadeMapT', bg=None, lite=False):
    o = S[sid]
    s = f'<div class="el srcline" data-a="fade" data-t=".4" style="left:110px;top:1640px;width:860px">FONTE: {src}</div>'
    flat = f'<div class="flat" style="background:{bg}"></div><div class="paper"></div><div class="capband"></div>' if bg else f'<div class="{shade}"></div>'
    cls = 'scene mapsc' + (' flatsc' if bg else '') + (' lite' if lite else '')
    return f'<section class="{cls}" data-s="{o["s"]}" data-e="{o["e"]}" data-in="cut" data-theme="dark" data-vfill="{1330 if bg else 0}">{flat}<div class="safe">{inner}</div>{kar(sid)}{s}</section>\n'

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

# ---------- c1 · gancho: o comentário real ----------
s = 'c1'; o = S[s]
BRA = frame(['rs', 'rr', 'ac', 'pb'], w=760, h=760, fy=1080)
CAM += [[0] + BRA, [o['e'] - .2] + [BRA[0] * 1.06] + BRA[1:]]
HL += [[G(s, 'bahia', 0, -.1), 'ba', 'esq', .5], [G(s, 'sc', 0, -.1), 'sc', 'dir', .5]]
LAB += [lab(G(s, 'bahia', 0, .1), o['e'], 'ba', 'BAHIA<small>PT ' + ESQ + ' DESDE 2007</small>', 'r'),
        lab(G(s, 'sc', 0, .1), o['e'], 'sc', 'SANTA CATARINA<small>NUNCA TEVE O PT</small>', 'b')]
H.append(scene(s, f'''
{eb(0, 'O COMENTÁRIO QUE RECEBEMOS', top=300)}
<div class="el cmt" data-flow="m:2" data-gap="26" data-a="up" data-t="{W(s, 'recebemos', 0, -.1)}" style="left:80px;width:920px"><i class="av"></i><div><div class="who"><span></span>46 min</div><div class="ct">Faz um POST sobre Pt 20 anos na Bahia consecutivos e na presidência alternados versus SC nunca governada pelo pt, onde está melhor ??</div></div></div>
<div class="el h" data-flow="m:3" data-gap="34" data-a="slam" data-t="{W(s, 'onde', 0, -.12)}" data-shake="1" style="left:80px;width:920px;font-size:110px;color:#fff">ONDE ESTÁ <span class="hl">MELHOR?</span></div>
''', 'COMENTÁRIO RECEBIDO NO NOSSO PERFIL (NOME OCULTO) · TSE', shade='shadeMapH'))

# ---------- c2 · ninguém começou do mesmo lugar (azul vivo) ----------
s = 'c2'; o = S[s]
CAM += [[o['s'] + .1] + BRA, [o['e'] - .1] + BRA]
HOL = ('<div class="hol"><div class="ht">CONTRACHEQUE</div><div class="hl1"><span>RENDIMENTO</span><span>R$ 3.722,00</span></div>'
       '<div class="hl1 m"><span>INSS · IR</span><span>········</span></div><div class="hl1 m"><span>VALE-TRANSPORTE</span><span>······</span></div>'
       '<div class="hliq"><span>MÉDIA BR</span><b>R$ 3.722</b></div></div>')
H.append(scene(s, rail(1) + f'''
{eb(1, 'PONTO DE PARTIDA')}
<div class="el h" data-flow="m:2" data-gap="30" data-a="up" data-t="{W(s, 'cobrar', 0, -.2)}" style="left:80px;width:920px;font-size:66px;color:#fff">“POR QUE VOCÊ NÃO TEM A <span class="hl">MANSÃO DELE?”</span></div>
<div class="el" data-flow="m:3" data-gap="40" data-a="drop" data-t="{W(s, 'média', 0, -.25)}" data-d=".6" data-r="-4" data-bob="1" style="left:70px;width:400px">{HOL}<div class="tag2">VOCÊ · MÉDIA DO BRASIL</div></div>
<div class="el headcut" data-flow="m:3" data-dy="-40" data-a="pop" data-t="{W(s, 'roberto', 0, -.2)}" data-d=".45" data-bob="1" style="left:520px;width:500px"><img class="headimg" src="assets/justus_head.png" alt=""><div class="tag2 y">ROBERTO JUSTUS</div></div>
<div class="el h" data-flow="m:4" data-gap="44" data-a="slam" data-t="{W(s, 'começaram', 0, -.3)}" data-shake="1" style="left:80px;width:920px;font-size:90px;color:#fff">NINGUÉM COMEÇOU <span class="hl">DO MESMO LUGAR.</span></div>
''', 'IBGE, PNAD CONTÍNUA (RENDIMENTO MÉDIO DO TRABALHO, 1º TRI/2026) · FOTO: WIKIMEDIA COMMONS (CC0)', bg='#2442E6'))

# ---------- c3 · a história (papel) ----------
s = 'c3'; o = S[s]
mini = ''.join(f'<path class="{ {"ba":"mba","sc":"msc"}.get(l["id"],"")}" d="{l["path"]}"/>' for l in MAP['locations'])
H.append(scene(s, rail(2) + f'''
{eb(2, 'A HISTÓRIA DE CADA UM')}
<div class="el rows" data-flow="m:2" data-gap="30" data-a="fade" data-t="{W(s, 'bahia', 0, -.2)}" style="left:80px">
  <div class="row txt"><div class="k" style="color:#D8322A">BAHIA<small>SÉCULOS XVI A XIX</small></div><div class="v">ESCRAVIDÃO E LATIFÚNDIO: <span style="color:#D8322A">A TERRA NA MÃO DE POUCOS</span></div></div>
  <div class="row txt" data-a="fade" data-t="{W(s, 'santa', 0, -.2)}"><div class="k" style="color:#2442E6">SANTA CATARINA<small>SÉCULO XIX</small></div><div class="v">COLÔNIAS DE IMIGRANTES COM <span style="color:#2442E6">ACESSO A TERRA PRA PLANTAR</span></div></div></div>
<div class="el h" data-flow="m:4" data-gap="30" data-a="slam" data-t="{W(s, 'frente', 0, -.3)}" style="left:80px;width:920px;font-size:84px;color:#111">E SAIU <span class="hl">NA FRENTE.</span></div>
<div class="el fine" data-flow="m:5" data-gap="20" data-a="fade" data-t="{W(s, 'frente', 0, .3)}" style="left:80px">A ESCRAVIDÃO SÓ ACABOU EM 1888. NAS COLÔNIAS DE SC, OS LOTES ERAM PEQUENOS E, EM GERAL, PAGOS A PRAZO (LEI DE TERRAS, 1850).</div>
<div class="el minimap" data-flow="m:3" data-gap="24" data-a="fade" data-t=".3" style="left:330px;width:420px;height:400px"><svg viewBox="372 200 250 380" width="420" height="400" preserveAspectRatio="xMidYMid meet">{mini}</svg><b class="mlb" style="left:330px;top:40px;color:#D8322A">BAHIA</b><b class="mlb" style="left:-250px;top:330px;color:#2442E6">SANTA CATARINA</b></div>
''', 'IBGE · LEI Nº 601/1850 (LEI DE TERRAS) · LEI ÁUREA (1888)', bg='#F1EADB', lite=True).replace('data-vfill="1330"','data-vfill="0"'))

BSC = frame(['ba','sc'], w=700, h=760, fy=1000)
# ---------- c4 · a renda até hoje ----------
s = 'c4'; o = S[s]
def money(name, sub, val, frac, color, t):
    return (f'<div class="tile"><div class="tk">{name}<small>{sub}</small></div>'
            f'<div class="tv" style="color:{color};font-size:92px;white-space:nowrap"><span class="cnt" data-t="{t}" data-d=".9" data-from="0" data-to="{val}" data-dec="0" data-thou="1" data-pre="R$ ">0</span></div>'
            f'<div class="ttrack"><div class="bar" data-t="{t}" data-d=".9" data-to="{int(400 * frac)}" style="background:{color}"></div></div></div>')
H.append(scene(s, rail(3) + f'''
{eb(3, 'ATÉ HOJE · RENDA POR PESSOA, POR MÊS · 2025')}
{tiles(money('SANTA CATARINA', '4ª MAIOR DO BRASIL', 2809, 1, '#2442E6', W(s, 'santa', 0, -.2)),
       money('BAHIA', 'ABAIXO DA MÉDIA (R$ 2.316)', 1465, 1465 / 2809, '#D8322A', W(s, 'bahia', 0, -.2)), W(s, 'renda', 0, -.2), 'm:2', 34)}
<div class="el stamp-r" data-flow="m:3" data-gap="34" data-a="stamp" data-t="{W(s, 'dobro', 0, -.15)}" data-d=".35" data-r="-2" style="left:80px;white-space:nowrap;font-size:54px">QUASE O DOBRO</div>
<div class="el h" data-flow="m:4" data-gap="40" data-a="slam" data-t="{W(s, 'ponto', 0, -.15)}" style="left:80px;width:920px;font-size:84px;color:#111">PONTO DE PARTIDA, <span class="hl">NÃO GOVERNO.</span></div>
''', 'IBGE, RENDIMENTO DOMICILIAR PER CAPITA 2025 (PNAD CONTÍNUA)', bg='#FFD34D', lite=True))

# ---------- c5 · o partido não explica ----------
s = 'c5'; o = S[s]
EAST = frame(['pi', 'ba', 'sc', 'rj', 'mg'], w=640, h=560, fy=1160)
CAM += [[o['s'] + .1] + EAST, [o['e'] - .1] + [EAST[0] * 1.05] + EAST[1:]]
HL += [[G(s, 'rio', 0, -.1), 'rj', 'dir', .5], [G(s, 'piauí', 0, -.1), 'pi', 'esq', .5]]
LAB += [lab(G(s, 'pl', 0, .2), o['e'], 'sc', 'SC 7,6', 'b'), lab(G(s, 'rio', 0, .1), o['e'], 'rj', 'RJ 22,6', 'b'),
        lab(G(s, 'piauí', 0, .1), o['e'], 'pi', 'PI 17,1', 'r', 0, 6), lab(G(s, 'bahia', 0, .1), o['e'], 'ba', 'BA 36,8', 'r')]
H.append(scene(s, rail(4) + f'''
{eb(4, 'E O PARTIDO NÃO EXPLICA')}
<div class="el note" data-flow="m:2" data-gap="22" data-a="fade" data-t=".2" style="left:80px">MORTES VIOLENTAS A CADA 100 MIL HABITANTES · 2025</div>
<div class="el rows" data-flow="m:3" data-gap="26" data-a="fade" data-t="{W(s, 'pl', 0, -.2)}" style="left:80px">
  {row('SANTA CATARINA', '7,6', 7.6 / 36.8, BL, W(s, 'santa', 0), sub='PL ' + DIR)}
  {row('RIO DE JANEIRO', '22,6', 22.6 / 36.8, BL, W(s, 'rio', 0), sub='PL ' + DIR + ' EM 2025')}
  {row('PIAUÍ', '17,1', 17.1 / 36.8, R, W(s, 'piauí', 0), sub='PT ' + ESQ)}
  {row('BAHIA', '36,8', 1, R, W(s, 'bahia', 0), sub='PT ' + ESQ)}</div>
<div class="el h" data-flow="m:4" data-gap="34" data-a="slam" data-t="{W(s, 'dobro', 0, -.2)}" style="left:80px;width:920px;font-size:64px;color:#fff">MESMO PARTIDO, <span class="hl">RESULTADO OPOSTO.</span></div>
<div class="el fine" data-flow="m:5" data-gap="24" data-a="fade" data-t="{W(s, 'dobro', 0, .4)}" style="left:80px">RJ HOJE: CASTRO (PL) RENUNCIOU EM MAR/2026; DOUGLAS RUAS (PL) FOI ELEITO EM 04/10/2026. O RIO TEM RENDA PARECIDA COM A DE SC (R$ 2.794), MAS TEM MILÍCIAS E FACÇÕES HÁ DÉCADAS.</div>
''', FB + ' · IBGE · TSE · ' + IDS, shade='shadeMapF'))

# ---------- c6 · mesma presidência, compare na mesma região ----------
s = 'c6'; o = S[s]
NEF = frame(NE, w=700, h=600, fy=1150)
CAM += [[o['s'] + .1] + NEF, [o['e'] - .1] + [NEF[0] * 1.06] + NEF[1:]]
HL += [[G(s, 'região', 0, -.1 + i * .06), u, 'esq', .4] for i, u in enumerate(NE_ESQ) if u not in ('pi', 'ba')]
HL += [[G(s, 'região', 0, .1 + i * .06), u, 'dir', .4] for i, u in enumerate(NE_DIR)]
H.append(scene(s, rail(5) + f'''
{eb(5, 'QUEM CUIDA DO QUÊ')}
<div class="el h" data-flow="m:2" data-gap="30" data-a="slam" data-t="{W(s, 'presidência', 0, -.15)}" style="left:80px;width:920px;font-size:72px;color:#fff">A PRESIDÊNCIA FOI <span class="hl">A MESMA</span> PROS DOIS ESTADOS.</div>
<div class="el stamp-o" data-flow="m:3" data-gap="30" data-a="stamp" data-t="{W(s, 'polícia', 0, -.1)}" data-d=".35" data-r="-1.5" style="left:80px;font-size:40px;width:920px">POLÍCIA, PRESÍDIOS E INVESTIGAÇÃO SÃO DO GOVERNO DO ESTADO</div>
<div class="el h" data-flow="m:4" data-gap="34" data-a="up" data-t="{W(s, 'compare', 0, -.15)}" style="left:80px;width:920px;font-size:64px;color:{Y}">COMPARE ESTADOS DA MESMA REGIÃO.</div>
<div class="el fine" data-flow="m:5" data-gap="22" data-a="fade" data-t="{W(s, 'região', 0, .3)}" style="left:80px">NORDESTE, MORTES VIOLENTAS (2025): MEDIANA DOS ESTADOS DE ESQUERDA 29,4 × DIREITA 33,0. MESMO PATAMAR.</div>
<div class="el repost" data-flow="m:6" data-gap="30" data-a="slam" data-t="{W(s, 'segue', 0, -.15)}" data-shake="1" style="left:80px;width:920px;font-size:50px">SEGUE A GENTE<small>No feed: São Paulo · Rio · Bahia e Norte</small></div>
''', FB + ' · CONSTITUIÇÃO, ART. 144 · ' + IDS, shade='shadeMapF'))

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
