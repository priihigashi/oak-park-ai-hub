"""Reel v1 — Rio de Janeiro (mesmo kit da Bahia v9) (explicativo). Redesenho editorial: uma linha de alinhamento à esquerda,
sem caixas (texto direto sobre a foto escurecida), eyebrow numerado por capítulo, tabelas com filete,
fonte da informação embaixo do @, sem aviso de IA na tela. Gera ../bahia.html."""
import json, html, re, os
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/rj/timeline.json')))
S = {o['id']: o for o in TL}
def norm(w): return re.sub(r'[^\wÀ-ú]', '', w.lower())
for o in TL:
    ws = o['words']
    for i in range(1, len(ws)):
        if ws[i][1] - ws[i-1][1] < 0.09:
            j = i
            while j < len(ws) and ws[j][1] - ws[i-1][1] < 0.09: j += 1
            t0 = ws[i-1][1]; t1 = ws[j][1] if j < len(ws) else t0 + 0.25*(j-i+1); n = j-i+1
            for k in range(i, j): ws[k] = [ws[k][0], round(t0 + (t1-t0)*(k-i+1)/n, 3)]
def W(sid, tok, n=0, off=0.0):
    for mode in ('eq', 'sw'):
        k = 0
        for w, t in S[sid]['words']:
            ok = norm(w) == norm(tok) if mode == 'eq' else norm(w).startswith(norm(tok))
            if ok:
                if k == n: return round(max(0, t+off), 2)
                k += 1
    raise SystemExit(f'word {tok} not in {sid}')
def kar(sid, per=6):
    ws = S[sid]['words']; toks = []; n = 0
    for i, (w, t) in enumerate(ws):
        if i and (n >= per or (re.search(r'[.?!:;]$', ws[i-1][0]) and n >= 3)): toks.append('/'); n = 0
        toks.append(f"{html.escape(w.replace(':', ''))}:{t}"); n += 1
    return f'<div class="kar karfull el" data-words="{" ".join(toks)}" style="left:130px;top:1410px;width:820px"></div>'
DUR = TL[-1]['e']
CH = ["QUEM", "CURVA", "TERRITÓRIO", "POLÍTICA", "POLÍCIA", "UNIÃO"]
def rail(active, t=.1):
    xs = [110+i*172 for i in range(6)]
    dots = ''.join(f'<div class="st{" on" if i==active else ""}{" past" if i<active else ""}" style="left:{x}px"><i></i><b>{y}</b></div>' for i, (x, y) in enumerate(zip(xs, CH)))
    return f'<div class="rail el" data-a="fade" data-t="{t}" data-d=".3" style="left:0;top:150px"><div class="line"></div><div class="fill" style="width:{xs[active]-60}px"></div>{dots}</div>'
def scene(sid, inner, bg, src, kbo='60% 50%', kb=1.08, bghtml=None):
    o = S[sid]
    b = (bghtml if bghtml else f'<img class="bgimg" src="assets/rj/{bg}.jpg" data-kb="{kb}" data-kbo="{kbo}">') + '<div class="shadeX"></div>'
    s = f'<div class="el srcline" data-a="fade" data-t=".4" style="left:130px;top:1640px;width:820px">FONTE: {src}</div>'
    return f'<section class="scene" data-s="{o["s"]}" data-e="{o["e"]}" data-in="cut" data-theme="dark">{b}<div class="safe">{inner}</div>{kar(sid)}{s}</section>\n'
CUR = {'s': None}
def eb(n, txt, t=.05, top=None, flow='m:1'):
    top = FT.get(CUR['s'], top)
    ft = f' data-ftop="{top}"' if top else ''
    num = f'<b>{n:02d}</b>' if n else ''
    return f'<div class="el eyebrow" data-flow="{flow}"{ft} data-a="left" data-t="{t}" style="left:80px">{num}{txt}</div>'
def ide(k, lab): return f'<i class="ide {k}">{lab}</i>'
ESQ, CESQ, DIR, CDIR = ide('esq', 'ESQUERDA'), ide('esq', 'CENTRO-ESQUERDA'), ide('dir', 'DIREITA'), ide('dir', 'CENTRO-DIREITA')
Y, R, WH = '#FFD34D', '#FF4A3D', '#F2ECE0'
BARMAX = 330
def row(k, v, frac, color, t, sub='', fade=None):
    sb = f'<small>{sub}</small>' if sub else ''
    fa = f' data-a="fade" data-t="{fade}"' if fade is not None else ''
    col = color if color != WH else '#fff'
    if frac is None:
        return f'<div class="row txt"{fa}><div class="k">{k}{sb}</div><div class="v" style="color:{col}">{v}</div></div>'
    bar = f'<div class="track"><div class="bar" data-t="{t}" data-d=".7" data-to="{int(BARMAX*frac)}" style="background:{color}"></div></div>'
    return f'<div class="row"{fa}><div class="k">{k}{sb}</div>{bar}<div class="v" style="color:{col}">{v}</div></div>'
def item(kick, txt, t, color='#fff'):
    return f'<div class="item" data-a="up" data-t="{t}"><div class="kick">{kick}</div><div class="t" style="color:{color}">{txt}</div></div>'
IDS = 'IDEOLOGIA: BOLOGNESI ET AL. (DADOS, 2023)'
FT = json.load(open('/home/claude/work/rj/ftop.json')) if os.path.exists('/home/claude/work/rj/ftop.json') else {}
H = []


# ---------- gráfico de linhas animado (revela da esquerda pra direita via .bar) ----------
def chart(sid, years, series, ymax, ticks, t0, dur, marks=(), w=880, h=600, lw=250, stages=None, notes=(), ymin=0, tfmt=None, per_line=False):
    px0, px1, py0, py1 = 56, w - lw - 20, 14, h - 46
    def X(i): return px0 + (px1 - px0) * i / (len(years) - 1)
    def Yv(v): return py1 - (py1 - py0) * (v - ymin) / (ymax - ymin)
    grid = ''.join(f'<line x1="{px0}" x2="{px1}" y1="{Yv(v):.1f}" y2="{Yv(v):.1f}" stroke="rgba(242,236,224,.14)" stroke-width="1.5"/>'
                   f'<text x="{px0-12}" y="{Yv(v)+7:.1f}" text-anchor="end" font-family="JBM" font-weight="700" font-size="19" fill="#9F988A">{tfmt(v) if tfmt else f"{v:,}".replace(",",".")}</text>' for v in ticks)
    lab_i = list(range(len(years))) if len(years) <= 6 else [0, len(years)//2, len(years)-1]
    grid += ''.join(f'<text x="{X(i):.1f}" y="{h-12}" text-anchor="middle" font-family="JBM" font-weight="700" font-size="19" fill="#9F988A">{years[i]}</text>' for i in lab_i)
    mk = ''
    for yr, txt, col in marks:
        i = years.index(yr)
        mk += (f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{py0}" y2="{py1}" stroke="{col}" stroke-width="2" stroke-dasharray="6 6"/>'
               f'<text x="{X(i)+10:.1f}" y="{py1-12}" font-family="JBM" font-weight="700" font-size="18" fill="{col}">{txt}</text>')
    lines = ''; each = []
    for s in series:
        n0 = len(lines)
        pts = ' '.join(f'{X(i):.1f},{Yv(v):.1f}' for i, v in enumerate(s['v']))
        dash = ' stroke-dasharray="10 8"' if s.get('dash') else ''
        lines += f'<polyline points="{pts}" fill="none" stroke="{s["c"]}" stroke-width="{s.get("w",5)}" stroke-linejoin="round" stroke-linecap="round"{dash}/>'
        for (i, txt) in s.get('dots', []):
            lines += (f'<circle cx="{X(i):.1f}" cy="{Yv(s["v"][i]):.1f}" r="9" fill="{s["c"]}" stroke="#0b0c0e" stroke-width="3"/>'
                      f'<text x="{X(i):.1f}" y="{Yv(s["v"][i])-18:.1f}" text-anchor="middle" font-family="Rub" font-weight="900" font-size="30" fill="{s["c"]}" stroke="#0b0c0e" stroke-width="6" paint-order="stroke">{txt}</text>')
        each.append((s.get('lt', t0), lines[n0:]))
    labels = ''
    # posições dos rótulos sem colisão: ordena pela altura e garante espaço mínimo
    want = sorted([(Yv(s['v'][-1]), i) for i, s in enumerate(series)])
    pos = {}; last = -1e9
    for y, i in want:
        sb_ = series[i].get('sub'); hgt = 34 + (28 * (sb_.count('<br>') + 1) if sb_ else 0)
        y = max(y, last); pos[i] = y; last = y + hgt + 8
    for i, s in enumerate(series):
        ly = pos[i]
        sub = f'<small>{s["sub"]}</small>' if s.get('sub') else ''
        labels += (f'<div class="clab" data-a="fade" data-t="{s.get("lt", t0+dur):.2f}" style="left:{px1+18}px;top:{ly-16:.0f}px;color:{s["c"]}">'
                   f'<b>{s["n"]}</b>{sub}</div>')
    return (f'<div class="el chart" data-flow="{{flow}}" style="left:80px;width:{w}px;height:{h}px">'
            f'<svg class="cgrid" width="{w}" height="{h}">{grid}{mk}</svg>'
            + (''.join(f'<div class="bar crev" data-t="{lt:.2f}" data-d="1.1" data-to="{px1+12}" style="height:{h}px"><svg width="{w}" height="{h}">{one}</svg></div>' for lt, one in each) if per_line else
               ''.join(f'<div class="bar crev" data-t="{st}" data-d="{sd}" data-to="{(X(b)+40 if b < len(years)-1 else px1+48) - (X(a) if a else 0):.0f}" style="height:{h}px;left:{X(a) if a else 0:.0f}px"><svg width="{w}" height="{h}" style="margin-left:-{X(a) if a else 0:.0f}px">{lines}</svg></div>'
                       for (a, b, st, sd) in stages) if stages else
               f'<div class="bar crev" data-t="{t0}" data-d="{dur}" data-to="{px1+12}" style="height:{h}px"><svg width="{w}" height="{h}">{lines}</svg></div>')
            + ''.join(f'<div class="clab cnote" data-a="fade" data-t="{nt:.2f}" style="left:{X(ni)+dx:.0f}px;top:{Yv(nv)+dy:.0f}px;color:{nc}">{ntx}</div>' for (ni, nv, ntx, nc, nt, dx, dy) in notes)
            + f'{labels}</div>')


# ---------- linha com trechos coloridos por governo (vermelho = esquerda, azul = direita) ----------
def segchart(years, lines, ymin, ymax, ticks, t0, dur, w=880, h=620, lw=270, tfmt=None, xl=None, plabels=(), flow='m:3'):
    px0, px1, py0, py1 = 70, w - lw - 16, 16, h - 46
    X = lambda i: px0 + (px1 - px0) * i / (len(years) - 1)
    Yv = lambda v: py1 - (py1 - py0) * (v - ymin) / (ymax - ymin)
    g = ''.join(f'<line x1="{px0}" x2="{px1}" y1="{Yv(v):.1f}" y2="{Yv(v):.1f}" stroke="rgba(242,236,224,.14)" stroke-width="1.5"/>'
                f'<text x="{px0-12}" y="{Yv(v)+7:.1f}" text-anchor="end" font-family="JBM" font-weight="700" font-size="19" fill="#9F988A">{tfmt(v) if tfmt else v}</text>' for v in ticks)
    for i in (xl if xl is not None else [0, len(years)//2, len(years)-1]):
        g += f'<text x="{X(i):.1f}" y="{h-12}" text-anchor="middle" font-family="JBM" font-weight="700" font-size="19" fill="#9F988A">{years[i]}</text>'
    ln = ''
    for L in lines:
        dash = ' stroke-dasharray="10 8"' if L.get('dash') else ''
        for a, b, col in L['segs']:
            pts = ' '.join(f'{X(i):.1f},{Yv(L["v"][i]):.1f}' for i in range(a, b+1) if L['v'][i] is not None)
            ln += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{L.get("w",6)}" stroke-linejoin="round" stroke-linecap="round"{dash}/>'
    want = sorted([(Yv([x for x in L['v'] if x is not None][-1]), k) for k, L in enumerate(lines)]); pos = {}; last = -1e9
    for y, k in want:
        hh = 30 + (26 if lines[k].get('sub') else 0); y = max(y, last); pos[k] = y; last = y + hh + 6
    lab = ''.join(f'<div class="clab" data-a="fade" data-t="{L.get("lt", t0+dur):.2f}" style="left:{px1+16}px;top:{pos[k]-15:.0f}px;color:{L.get("lc","#fff")}"><b>{L["n"]}</b>'
                  + (f'<small>{L["sub"]}</small>' if L.get('sub') else '') + '</div>' for k, L in enumerate(lines))
    pl = ''
    for P_ in plabels:
        k, i, txt, col, dy, t = P_[:6]; dx = P_[6] if len(P_) > 6 else 0
        v = lines[k]['v'][i]
        pl += (f'<div class="clab plab" data-a="fade" data-t="{t:.2f}" style="left:{X(i)-70+dx:.0f}px;width:140px;text-align:center;top:{Yv(v)+dy:.0f}px;color:{col}">{txt}</div>'
               f'<div class="pdot" data-a="fade" data-t="{t:.2f}" style="left:{X(i)-7:.0f}px;top:{Yv(v)-7:.0f}px;background:{col}"></div>')
    if all('rt' in L for L in lines):
        rev = ''
        for L in lines:
            one = ''
            dash = ' stroke-dasharray="10 8"' if L.get('dash') else ''
            for a, b, col in L['segs']:
                pts = ' '.join(f'{X(i):.1f},{Yv(L["v"][i]):.1f}' for i in range(a, b+1) if L['v'][i] is not None)
                one += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{L.get("w",6)}" stroke-linejoin="round" stroke-linecap="round"{dash}/>'
            rev += f'<div class="bar crev" data-t="{L["rt"]:.2f}" data-d="1.2" data-to="{px1+12}" style="height:{h}px"><svg width="{w}" height="{h}">{one}</svg></div>'
    else:
        rev = f'<div class="bar crev" data-t="{t0}" data-d="{dur}" data-to="{px1+12}" style="height:{h}px"><svg width="{w}" height="{h}">{ln}</svg></div>'
    return (f'<div class="el chart" data-flow="{flow}" style="left:80px;width:{w}px;height:{h}px">'
            f'<svg class="cgrid" width="{w}" height="{h}">{g}</svg>'
            f'{rev}{pl}{lab}</div>')

def quote(txt, t, flow, gap=34, size=58):
    return f'<div class="el h quote" data-flow="{flow}" data-gap="{gap}" data-a="up" data-t="{t}" style="left:80px;width:880px;font-size:{size}px">{txt}</div>'


# ===================== CENAS — RIO DE JANEIRO =====================
CESQ_, DIR_ = CESQ, DIR
SQUID = '🦑'
UNI = ide('dir', 'DIREITA')
YSIM = [str(y) for y in range(2000, 2010)]
SIM = [51.0, 50.5, 56.5, 52.7, 49.2, 46.1, 45.8, 40.1, 34.0, 31.8]
YF = [str(y) for y in range(2013, 2026)]
MVI = [5348, 5719, 5010, 6262, 6749, 6714, 5980, 4907, 4762, 4485, 4270, 3809, 3890]
MDIP = [416, 584, 645, 925, 1127, 1534, 1814, 1245, 1356, 1330, 871, 703, 798]
BLUE = '#5B7CFF'

s = 'v01'; CUR['s'] = s
H.append(scene(s, f'''
{eb(0, 'RIO DE JANEIRO · SEGURANÇA', top=330)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'quatro',0,-.1)}" data-shake="1" style="left:80px;width:880px;font-size:112px;color:#fff"><span class="hl">4 MILHÕES</span> SOB FACÇÕES E MILÍCIAS</div>
<div class="el h redtxt" data-flow="m:3" data-gap="30" data-a="slam" data-t="{W(s,'culpa',0,-.1)}" data-d=".35" style="left:80px;font-size:96px;width:880px">E A CULPA É DA ESQUERDA.</div>
<div class="el body" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'vamos',0,-.2)}" style="left:80px;width:820px"><b>Vamos aos fatos.</b></div>
<div class="el fine" data-flow="m:5" data-gap="26" data-a="fade" data-t="{W(s,'vamos',0,.2)}" style="left:80px">34,9% DA POPULAÇÃO DA REGIÃO METROPOLITANA VIVE SOB DOMÍNIO OU INFLUÊNCIA DE GRUPOS ARMADOS (DADOS DE 2024).</div>
''', None, 'GENI/UFF + FOGO CRUZADO, MAPA DOS GRUPOS ARMADOS (DEZ/2025) · MAPA: IBGE', bghtml='<div class="zbg"></div>'+open('/home/claude/work/rj/geo/zoom_svg.html').read()+'<img class="zseq" alt="" style="position:absolute;left:0;top:0;width:1080px;height:1920px;display:none">'))

s = 'v02'; CUR['s'] = s
def gov(yrs, nome, partido, idl, t, col='#fff', sub=''):
    if sub.startswith('!'):   # selo vermelho: entra quando a narração fala de presos/afastados/inelegíveis
        sb = f'<small class="selo" data-a="pop" data-t="{W(s,"presos",0,-.1)}">{sub[1:]}</small>'
    else: sb = f'<small>{sub}</small>' if sub else ''
    return f'<div class="row txt" data-a="fade" data-t="{t}"><div class="k">{yrs}{sb}</div><div class="v" style="color:{col}">{nome} <span class="pt">{partido}</span> {idl}</div></div>'
H.append(scene(s, rail(0)+f'''
{eb(1, 'QUEM GOVERNOU O ESTADO', top=320)}
<div class="el rows govs" data-flow="m:2" data-gap="34" style="left:80px">
  {gov('1999–2002', 'GAROTINHO', 'PDT→PSB', CESQ, W(s,'garotinho',0,-.2), sub='!PRESO EM 2016–17')}
  {gov('2002', 'BENEDITA', 'PT', ESQ, W(s,'benedita',0,-.2), sub='VICE QUE ASSUMIU')}
  {gov('2003–2006', 'ROSINHA', 'PSB→MDB', CESQ + DIR, W(s,'rosinha',0,-.2), sub='!PRESA EM 2017')}
  {gov('2007–2014', 'CABRAL', 'PMDB', DIR, W(s,'cabral',0,-.2), col=Y, sub='!PRESO EM 2016')}
  {gov('2014–2018', 'PEZÃO', 'MDB', DIR, W(s,'pezão',0,-.2), col=Y, sub='!PRESO EM 2018 · ABSOLVIDO')}
  {gov('2019–2020', 'WITZEL', 'PSC', DIR, W(s,'witzel',0,-.2), col=Y, sub='!AFASTADO E CASSADO')}
  {gov('2020–2026', 'CASTRO', 'PSC→PL', DIR, W(s,'castro',0,-.2), col=Y, sub='!INELEGÍVEL ATÉ 2030')}</div>
<div class="el h" data-flow="m:3" data-gap="34" data-a="slam" data-t="{W(s,'castro',0,.5)}" style="left:80px;width:880px;font-size:64px;color:#fff">23 ANOS DE <span class="hl">DIREITA</span></div>
<div class="el fine" data-flow="m:4" data-gap="20" data-a="fade" data-t="{W(s,'lados',0,.2)}" style="left:80px">MDB = 7,01 NA ESCALA, NO LIMITE DA DIREITA. ROSINHA ENTROU NO MDB EM AGO/2003. O PT TEVE SECRETARIAS NO GOVERNO CABRAL ATÉ NOV/2013. GAROTINHO FOI SECRETÁRIO DE SEGURANÇA DE ROSINHA (2003–04). ANTES DELE: MARCELLO ALENCAR (PSDB, DIREITA) E BRIZOLA (PDT, CENTRO-ESQUERDA). HOJE GOVERNA O INTERINO RICARDO COUTO (TJ-RJ). PREFEITOS DA CAPITAL DESDE 1993: CESAR MAIA (PMDB/PFL/PTB), CONDE (PFL), PAES (MDB/DEM/PSD), CRIVELLA (PRB), CAVALIERE (PSD): DE CENTRO-DIREITA A EXTREMA-DIREITA. PM E POLÍCIA CIVIL SÃO DO ESTADO (CONSTITUIÇÃO, ART. 144).</div>
''', 'i02', 'TSE · TJ-RJ · ' + IDS, kbo='60% 50%'))

s = 'v03'; CUR['s'] = s
XM = ['ANTES', '1º ANO', '2º', '3º', '4º']
L1, L2 = '#FF4A3D', '#FF9C8F'
c3 = chart(s, XM, [
    dict(n='GAROTINHO +26%', v=[0, .5, 9.8, 11.2, 26.2], c=L1, w=7, lt=W(s,'garotinho',0,-.1)),
    dict(n='ROSINHA −5%', sub='PSB→MDB', v=[0, .1, -4.9, -.7, -4.9], c=L2, w=6, lt=W(s,'rosinha',0,-.1)),
    dict(n='CABRAL 1 −24%', v=[0, .7, -6.7, -7.1, -23.8], c=BLUE, w=6, lt=W(s,'cabral',0,-.1)),
    dict(n='CABRAL 2 −2%', v=[0, -14.9, -19.9, -8.2, -1.9], c=BLUE, w=4, dash=True, lt=W(s,'cabral',0,.4)),
    dict(n='PEZÃO +17%', v=[0, -12.4, 9.5, 18.0, 17.4], c='#AFC0FF', w=5, lt=W(s,'pezão',0,-.1)),
    dict(n='WITZEL/CASTRO −33%', v=[0, -10.9, -26.9, -29.1, -33.2], c='#38BDF8', w=7, lt=W(s,'witzel',0,-.1)),
    dict(n='CASTRO 2 −13%', sub='3 ANOS', v=[0, -4.8, -15.1, -13.3, -13.3], c='#38BDF8', w=4, dash=True, lt=W(s,'castro',0,-.1)),
], 40, [-40, -20, 0, 20, 40], 0, 0, h=640, lw=290, ymin=-40,
   tfmt=lambda v: (f'+{v}%' if v > 0 else f'{v}%'.replace('-', '−')),
   per_line=True).replace('{flow}', 'm:3')
H.append(scene(s, rail(1)+f'''
{eb(2, 'MANDATO POR MANDATO · MORTES VIOLENTAS', top=290)}
<div class="el body" data-flow="m:2" data-gap="22" data-a="fade" data-t=".2" style="left:80px;width:880px;font-size:32px"><b style="color:{L1}">━ ESQUERDA</b> &nbsp;&nbsp; <b style="color:{BLUE}">━ DIREITA</b> &nbsp;&nbsp; <span style="color:#A9A291;font-size:24px">┅ 2º MANDATO</span></div>
{c3}
<div class="el fine" data-flow="m:4" data-gap="22" data-a="fade" data-t="{W(s,'linha',0,.4)}" style="left:80px">VARIAÇÃO NO NÚMERO DE MORTES VIOLENTAS ATÉ O FIM DO MANDATO, CONTRA O ANO ANTES DA POSSE. MESMA BASE DE 1998 A 2025 (ISP-RJ). BENEDITA (PT) GOVERNOU 9 MESES EM 2002; PEZÃO ASSUMIU EM ABR/2014; CASTRO EM AGO/2020. ANTES DE 1999, MARCELLO ALENCAR (PSDB, DIREITA): −26%. BRASIL ENTRE 2018 E 2022: CERCA DE −17% (FBSP, NÚMERO DE MORTES). OS +26% DE GAROTINHO INCLUEM OS 9 MESES DE BENEDITA (PT).</div>
''', 'i03', 'ISP-RJ, LETALIDADE VIOLENTA (1998–2020) · FBSP, ANUÁRIOS 2022–2026 · ' + IDS, kbo='55% 60%'))

s = 'v04'; CUR['s'] = s
YC = [str(y) for y in range(1998, 2026)]
VC = [6371,6401,6993,7083,8043,8054,7645,7987,7649,7699,7134,7106,5828,4960,4666,5348,5719,5010,6262,6749,6714,5980,4907,4762,4485,4270,3809,3890]
ix = lambda y: y - 1998
VB = [None, None, None, None, None, None, 7645, 7524, 7769, 7537, 7919, 8135, 8287, 8254, 8917, 8972, 9453, 9235, 9772, 10254, 9059, 7113, 7795, 7479, 7254, 7151, 6657, None]
c4 = segchart(YC, [dict(n='', v=VB, segs=[(6, 26, '#8C8C8C')], w=5, dash=True, lt=W(s,'brasil',0)), dict(n='', v=VC, segs=[(0, 1, BLUE), (1, 5, L1), (5, 27, BLUE)], w=7, lt=W(s,'linha',0))],
    3000, 11000, [3000, 5000, 7000, 9000, 11000], W(s,'linha',0,-.2), 5.5, h=680, lw=40, tfmt=lambda v: f"{v:,}".replace(",", "."),
    xl=[ix(1998), ix(2006), ix(2014), ix(2022)],
    plabels=[(1, ix(2002), 'GAROTINHO<br>8.043', L1, -30, W(s,'linha',0,.6), -100),
             (1, ix(2003), '8.054<br>ROSINHA', BLUE, -62, W(s,'rosinha',0,-.2)),
             (1, ix(2012), 'CABRAL<br>4.666', BLUE, 18, W(s,'cabral',0,-.2)),
             (1, ix(2017), '6.749<br>PEZÃO', BLUE, -62, W(s,'pezão',0,-.2)),
             (1, ix(2020), 'WITZEL/CASTRO<br>4.762', BLUE, -62, W(s,'witzel',0,-.1), 64),
             (1, ix(2025), 'CASTRO<br>3.890', BLUE, 18, W(s,'voltou',0,-.2)),
             (0, ix(2017), 'BRASIL', '#B5B5B5', -48, W(s,'brasil',0,.2))]).replace('{flow}', 'm:3')
c4 = c4[:-6] + f'<div class="big23" data-a="up" data-t="{W(s,"rosinha",0,-.1):.2f}"><b>23 ANOS</b><span>DE GOVERNOS DE DIREITA</span><small>DESDE 2003 · MDB CONTA COMO DIREITA</small></div></div>'
H.append(scene(s, rail(1)+f'''
{eb(3, 'A LINHA INTEIRA · 1998–2025', top=290)}
<div class="el body" data-flow="m:2" data-gap="22" data-a="fade" data-t=".2" style="left:80px;width:880px;font-size:32px"><b style="color:{L1}">━ ESQUERDA</b> &nbsp;&nbsp; <b style="color:{BLUE}">━ DIREITA</b> &nbsp;&nbsp; <b style="color:#B5B5B5">┅ BRASIL</b></div>
{c4}
<div class="el h" data-flow="m:4" data-gap="30" data-a="up" data-t="{W(s,'subiu',0,-.2)}" style="left:80px;width:880px;font-size:58px;color:#fff">SUBIU E CAIU <span class="hl">COM OS DOIS LADOS.</span></div>
<div class="el fine" data-flow="m:5" data-gap="20" data-a="fade" data-t="{W(s,'série',0,.1)}" style="left:80px">MESMA BASE DE 1998 A 2025 (ISP-RJ, NÚMERO DE MORTES VIOLENTAS). 2025: RIO +2,1% (MORTES PELA POLÍCIA +13%), BRASIL −8,2%, MENOR TAXA DA SÉRIE (FBSP). A QUEDA DEPOIS DE 2018 VEIO COM O RECORDE DE MORTES PELA POLÍCIA (1.814 EM 2019). BRASIL: ATLAS DA VIOLÊNCIA (SIM), 2004–2024, NA MESMA ESCALA DO RIO EM 2004 (SÓ A FORMA DA CURVA). MDB = DIREITA NA ESCALA DE BOLOGNESI (7,01); AZUL DESDE AGO/2003.</div>
''', 'i04', 'ISP-RJ, LETALIDADE VIOLENTA · FBSP, ANUÁRIO 2026', kbo='60% 45%'))

s = 'v05'; CUR['s'] = s
YS = [str(y) for y in range(2013, 2026)]
c5 = segchart(YS, [
    dict(n='RIO 22,6', sub='PL', v=[31.8,33.9,29.5,36.7,39.5,39.2,34.8,28.5,27.7,26.1,24.8,22.1,22.6], segs=[(0, 12, BLUE)], w=9, lc=BLUE, lt=W(s,'rio',0,.4), rt=W(s,'rio',0,-.2)),
    dict(n='ES 22,0', sub='PSB', v=[43.7,42.9,38.1,33.8,38.6,30.1,26.8,30.1,29.0,27.8,26.9,24.0,22.0], segs=[(0, 2, L1), (2, 6, '#2DD4BF'), (6, 12, L1)], w=6, lc='#2DD4BF', lt=W(s,'espírito',0,.6), rt=W(s,'espírito',0,-.2)),
    dict(n='MINAS 12,9', sub='NOVO', v=[21.0,21.7,21.3,21.2,20.0,15.5,13.5,12.9,11.9,13.9,14.4,15.1,12.9], segs=[(0, 2, '#38BDF8'), (2, 6, '#FF9C8F'), (6, 12, '#38BDF8')], w=6, lc='#38BDF8', lt=W(s,'minas',0,.6), rt=W(s,'minas',0,-.2)),
    dict(n='SP 7,8', sub='REPUBLICANOS', v=[12.6,13.3,11.8,11.1,10.8,9.6,9.0,9.1,8.0,8.2,7.6,8.2,7.8], segs=[(0, 12, '#B9CCFF')], w=6, lc='#B9CCFF', lt=W(s,'paulo',0,.6), rt=W(s,'paulo',0,-.2)),
], 0, 45, [0, 15, 30, 45], W(s,'linha',0,-.2), 2.4, h=620, lw=230, xl=[0, 3, 6, 9, 12]).replace('{flow}', 'm:3')
H.append(scene(s, rail(1)+f'''
{eb(4, 'SUDESTE · MORTES VIOLENTAS POR 100 MIL', top=290)}
<div class="el body" data-flow="m:2" data-gap="22" data-a="fade" data-t=".2" style="left:80px;width:880px;font-size:30px"><b style="color:{L1}">━ GOVERNO DE ESQUERDA</b> &nbsp; <b style="color:{BLUE}">━ GOVERNO DE DIREITA</b><br><span style="color:#A9A291;font-size:24px">CADA ESTADO TEM SEU TOM</span></div>
{c5}
<div class="el h" data-flow="m:4" data-gap="30" data-a="up" data-t="{W(s,'topo',0,-.3)}" style="left:80px;width:880px;font-size:54px;color:#fff">PARTIDO SOZINHO <span class="hl">NÃO DECIDE.</span></div>
<div class="el fine" data-flow="m:5" data-gap="20" data-a="fade" data-t="{W(s,'topo',0,.3)}" style="left:80px">ES: CASAGRANDE (PSB, CENTRO-ESQUERDA) 2013–14 E 2019–25; HARTUNG (MDB, DIREITA) 2015–18 — CAIU NOS DOIS. MG: PIMENTEL (PT, ESQUERDA) 2015–18; ZEMA (NOVO, DIREITA) 2019–25. SP: PSDB E REPUBLICANOS (DIREITA); MÁRCIO FRANÇA (PSB) GOVERNOU 9 MESES EM 2018. A REVISTA OESTE (DADOS DO PODER360) DIZ “ESQUERDA 23,4 × DIREITA 14,8”: USA MÉDIA DO PAÍS INTEIRO E TIRA AS MORTES PELA POLÍCIA. MESMO PARTIDO, OUTRO RESULTADO: SC (PL) 7,6 × RIO (PL) 22,6.</div>
''', 'i05', 'FBSP, ANUÁRIO 2026 (TABELA 02, SÉRIE 2013–2025) · ' + IDS, kbo='55% 50%'))

s = 'v06'; CUR['s'] = s
H.append(scene(s, rail(2)+f'''
{eb(5, 'PROBLEMA 1 · TERRITÓRIO', top=320)}
<div class="el h cnt" data-flow="m:2" data-gap="30" data-t="{W(s,'quatro',0,-.15)}" data-d=".9" data-from="0" data-to="34.9" data-dec="1" data-suf="%" style="left:72px;font-size:230px;color:{R};width:880px;line-height:.82;height:190px"></div>
<div class="el body" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'metropolitana',0,-.1)}" style="left:80px;width:860px">da região metropolitana vive sob grupos armados, <b>tráfico e milícia: cerca de 4 milhões de pessoas.</b></div>
<div class="el rows" data-flow="m:4" data-gap="40" data-a="fade" data-t="{W(s,'milícia',0,-.3)}" style="left:80px">
  {row('MILÍCIA', 'QUASE METADE DA ÁREA · RECUA DESDE 2020', None, '#fff', 0, fade=W(s,'policiais',0,-.2), sub='POLICIAIS E EX-POLICIAIS QUE COBRAM<br>TAXA E CONTROLAM GÁS, VAN E INTERNET')}
  {row('COMANDO VERMELHO', 'CRESCE · MAIOR POPULAÇÃO DOMINADA', None, R, 0, fade=W(s,'comando',0,-.2))}</div>
<div class="el note" data-flow="m:5" data-gap="24" data-a="fade" data-t="{W(s,'cresce',0,.2)}" style="left:80px">QUEM CUIDA: POLICIAMENTO E INVESTIGAÇÃO = ESTADO. FRONTEIRA, PORTOS, ARMAS E LAVAGEM = UNIÃO (PF).</div>
''', 'i06', 'GENI/UFF + FOGO CRUZADO (DEZ/2025)', kbo='55% 50%'))

s = 'v07'; CUR['s'] = s
H.append(scene(s, rail(3)+f'''
{eb(6, 'PROBLEMA 2 · MILÍCIA E POLÍTICA', top=320)}
<div class="el items" data-flow="m:2" data-gap="36" style="left:80px">
  {item('CPI DAS MILÍCIAS · ALERJ, 2008', 'Mais de 200 indiciamentos pedidos, entre eles 5 parlamentares.', W(s,'cpi',0,-.2))}
  {item('FLÁVIO BOLSONARO · PL ' + DIR, 'Medalha a Adriano da Nóbrega, depois apontado como chefe do Escritório do Crime. Mãe e ex-mulher dele no gabinete.', W(s,'flávio',0,-.2))}</div>
<div class="el note" data-flow="m:3" data-gap="24" data-a="fade" data-t="{W(s,'nega',0,-.2)}" style="left:80px">FLÁVIO E JAIR NEGAM LIGAÇÃO COM A MILÍCIA (ADRIANO MORREU EM 2020). RACHADINHAS: PROVAS ANULADAS E DENÚNCIA ARQUIVADA, SEM JULGAMENTO DE MÉRITO.</div>
<div class="el fine" data-flow="m:4" data-gap="18" data-a="fade" data-t="{W(s,'nega',0,.6)}" style="left:80px">DO OUTRO LADO: NÃO ACHAMOS POLÍTICO DO PT, PSOL OU PDT DO RIO LIGADO A MILÍCIA OU FACÇÃO EM REPORTAGEM OU PROCESSO. NA BASE DO GOVERNO ATUAL {SQUID}: CHIQUINHO BRAZÃO FOI SECRETÁRIO DE PAES (PSD {DIR}) ATÉ 2024; O VEREADOR SALVINO (PSD) FOI PRESO EM 2026, SUSPEITO DE LIGAÇÃO COM O CV, E NEGA.</div>
''', 'i07', 'ALERJ, CPI 2008 · MP-RJ · CONGRESSO EM FOCO · STF (FEV/2025)', kbo='60% 50%'))

s = 'v09'; CUR['s'] = s
H.append(scene(s, rail(3)+f'''
{eb(7, 'O CRIME CHEGOU AO PODER', top=320)}
<div class="el items" data-flow="m:2" data-gap="36" style="left:80px">
  {item('PRESIDENTE DA ALERJ · UNIÃO ' + UNI + ' · ALIADO DE CASTRO', 'Preso pela PF, suspeito de avisar um deputado alvo de operação contra o Comando Vermelho.', W(s,'presidente',0,-.2))}
  {item('CASO MARIELLE · STF, FEV/2026', 'Irmãos Brazão condenados como mandantes: 76 anos.', W(s,'supremo',0,-.2), color=R)}</div>
<div class="el note" data-flow="m:3" data-gap="24" data-a="fade" data-t="{W(s,'negam',0,-.2)}" style="left:80px">TODOS NEGAM. OS BRAZÃO SÃO EX-MDB E EX-UNIÃO BRASIL. O CHEFE DA POLÍCIA CIVIL, NOMEADO NA INTERVENÇÃO FEDERAL (GOVERNO TEMER, MDB {DIR}), PEGOU 18 ANOS POR ATRAPALHAR A INVESTIGAÇÃO.</div>
<div class="el fine" data-flow="m:4" data-gap="18" data-a="fade" data-t="{W(s,'negam',0,.2)}" style="left:80px">TAMBÉM PRESOS: UM EX-CHEFE DA POLÍCIA CIVIL DE CASTRO (PROPINA DO JOGO DO BICHO, 2022) E UM DEPUTADO EXPULSO DO MDB (SUSPEITO DE AGIR PARA O CV). DO OUTRO LADO, O VEREADOR SALVINO (PSD, ALIADO DE PAES) FOI PRESO EM 2026, SUSPEITO DE NEGOCIAR COM O CV, E SOLTO 2 DIAS DEPOIS (O TJ VIU FUNDAMENTO “PRECÁRIO”). TODOS NEGAM. DOMINGOS BRAZÃO FEZ CAMPANHA PARA DILMA (2014, PELO MDB); CHIQUINHO, PARA BOLSONARO (2022) (COMPROVA). UNIÃO BRASIL = FUSÃO DE DEM E PSL.</div>
''', 'i09', 'PF · STF (FEV/2026) · MP-RJ · BRASIL DE FATO (2022) · DIÁRIO DO NORDESTE (2026)', kbo='65% 50%'))

s = 'v10'; CUR['s'] = s
c10 = chart(s, YF, [
    dict(n='AÇÕES', sub='POLICIAIS · RJ<br>MORTES POR ANO', v=MDIP, c=R, w=7, lt=W(s,'polícia',0), dots=[(6, '1.814'), (12, '798')]),
], 2000, [0, 500, 1000, 1500, 2000], 0, 0, h=560, marks=[('2018', 'INTERV.', '#fff'), ('2020', 'STF', Y)],
   stages=[(0, 6, W(s,'chegaram',0,-.2), 2.2), (6, 11, W(s,'caíram',0,-.2), 2.0), (11, 12, W(s,'voltaram',0,-.2), 1.0)]).replace('{flow}', 'm:2')
H.append(scene(s, rail(4)+f'''
{eb(8, 'PROBLEMA 3 · A POLÍCIA', top=300)}
{c10}
<div class="el h" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'três',0,-.25)}" style="left:80px;width:880px;font-size:56px;color:#fff">2019: <span style="color:{R}">3 EM CADA 10</span> MORTES VIOLENTAS</div>
<div class="el fine" data-flow="m:4" data-gap="22" data-a="fade" data-t="{W(s,'letal',0,.2)}" style="left:80px">AS 6 OPERAÇÕES MAIS LETAIS DESDE 2007 FORAM NO GOVERNO CASTRO (PL {DIR}). POLÍCIA MILITAR E CIVIL SÃO DO ESTADO. “O STF PROIBIU OPERAÇÕES” É DISTORCIDO (AOS FATOS): LIMITOU NA PANDEMIA, COM EXCEÇÕES, E EM ABR/2025 DERRUBOU AS PRINCIPAIS RESTRIÇÕES; A OPERAÇÃO MAIS LETAL VEIO DEPOIS.</div>
''', 'i10', 'FBSP, ANUÁRIOS 2015–2026 · GENI/UFF', kbo='55% 50%'))

s = 'v11'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(9, 'OPERAÇÃO CONTENÇÃO · 28/10/2025', top=320)}
<div class="el h" data-flow="m:2" data-gap="30" data-a="slam" data-t="{W(s,'resolveu',0,-.2)}" style="left:80px;width:880px;font-size:96px;color:#fff">NÃO <span class="hl">RESOLVEU.</span></div>
<div class="el rows" data-flow="m:3" data-gap="36" data-a="fade" data-t="{W(s,'nenhum',0,-.3)}" style="left:80px">
  {row('ALVOS DA LISTA', 'NENHUM DOS 69 ENTRE AS MORTES', None, '#fff', 0)}
  {row('CHEFE PRINCIPAL', 'FUGIU', None, '#fff', 0, fade=W(s,'chefe',0,-.2))}
  {row('BALANÇO OFICIAL', '99 PRESOS · 91 FUZIS', None, '#fff', 0, sub='POLÍCIA CIVIL-RJ', fade=W(s,'fugiu',0,.1))}</div>
<div class="el fine" data-flow="m:4" data-gap="26" data-a="fade" data-t="{W(s,'fugiu',0,.4)}" style="left:80px">121 MORTES PELA CONTA DO GOVERNO, 132 PELA DEFENSORIA, QUE VÊ INDÍCIOS DE ILEGALIDADE. O GOVERNO DIZ QUE 108 DOS 115 IDENTIFICADOS TINHAM VÍNCULO COM O CV E QUE 4 POLICIAIS MORRERAM. 55% A 70% DOS CARIOCAS APOIARAM.</div>
''', 'i11', 'REUTERS · POLÍCIA CIVIL-RJ · DEFENSORIA · DATAFOLHA', kbo='60% 50%'))

s = 'v11b'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(10, 'O QUE INCENTIVA O CONFRONTO', top=300)}
<div class="el items tight" data-flow="m:2" data-gap="30" style="left:80px">
  {item('2019 · WITZEL · PSC ' + DIR, 'Mortes por policiais saem da conta do bônus das polícias. No mesmo ano: recorde de 1.814.', W(s,'witzel',0,-.2))}
  {item('2025 · DEPUTADOS DO PL ' + DIR, 'Volta a gratificação faroeste. Castro vetou; a Alerj derrubou o veto.', W(s,'deputados',0,-.2), color=R)}
  {item('2020 · GOVERNO BOLSONARO · ' + DIR, 'Revoga regras de rastreio de munição. O STF suspendeu em 2021.', W(s,'bolsonaro',0,-.2))}
  {item('PROJETO DAS BALAS · PL 3.723/2019', 'Tira a marcação das balas das polícias. Parado no Senado.', W(s,'projeto',0,-.2))}</div>
<div class="el fine" data-flow="m:3" data-gap="22" data-a="fade" data-t="{W(s,'senado',0,.1)}" style="left:80px">NOS ANOS 1990, COM A FAROESTE (MARCELLO ALENCAR, PSDB), DOBROU O NÚMERO DE MORTOS PARA CADA FERIDO EM CONFRONTO. O PSOL ACIONOU O STF EM 2026, SEM DECISÃO. O PL 3.723 FOI ENVIADO PELO GOVERNO BOLSONARO; O FIM DA MARCAÇÃO ENTROU POR EMENDA NA CÂMARA. FLÁVIO, NO JN (16/10/2026), CHAMOU A MARCAÇÃO DE “DETALHEZINHO”. A GUARDA DE PAES (PSD) RECEBE GRATIFICAÇÃO FIXA DE R$ 10,3 MIL POR PORTAR ARMA, NÃO POR MORTE. CÂMERAS NAS FARDAS VIERAM EM 2022, POR ORDEM DO STF. É FALSO QUE OS FUZIS DA OPERAÇÃO ERAM DE CACS (AOS FATOS).</div>
''', 'i08', 'JB (2019) · AGÊNCIA BRASIL E METRÓPOLES (2025) · CONGRESSO EM FOCO · METRÓPOLES (OUT/2026) · ALMA PRETA', kbo='55% 50%'))

s = 'v12'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(11, 'PROBLEMA 4 · INVESTIGAÇÃO', top=320)}
<div class="el h cnt" data-flow="m:2" data-gap="30" data-t="{W(s,'vinte',0,-.15)}" data-d=".9" data-from="0" data-to="23" data-dec="0" data-suf="%" style="left:72px;font-size:260px;color:{R};width:880px;line-height:.82;height:214px"></div>
<div class="el body" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'homicídios',0,-.1)}" style="left:80px;width:860px">dos homicídios do Rio são esclarecidos. <b>Investigar é trabalho da Polícia Civil, do estado.</b></div>
<div class="el rows" data-flow="m:4" data-gap="40" data-a="fade" data-t="{W(s,'contra',0,-.3)}" style="left:80px">
  {row('RIO', '23%', 23/36, R, W(s,'contra',0))}
  {row('SÃO PAULO', '31%', 31/36, WH, W(s,'contra',0,.2))}
  {row('BRASIL', '36%', 1, WH, W(s,'brasil',0))}</div>
''', 'i12', 'INSTITUTO SOU DA PAZ, ONDE MORA A IMPUNIDADE (OUT/2025, DADOS DE 2023)', kbo='55% 50%'))

s = 'v13'; CUR['s'] = s
H.append(scene(s, rail(5)+f'''
{eb(12, 'E O GOVERNO FEDERAL?', top=300)}
<div class="el rows" data-flow="m:2" data-gap="34" data-a="fade" data-t="{W(s,'porto',0,-.3)}" style="left:80px">
  {row('É DA UNIÃO', 'FRONTEIRA, PORTO, ARMAS, PF, FUNDOS', None, Y, 0)}</div>
<div class="el rows" data-flow="m:3" data-gap="34" data-a="fade" data-t="{W(s,'ministério',0,-.3)}" style="left:80px">
  {row('ENVIADO', 'R$ 288 MI', 1, WH, W(s,'mandado',0), sub='FUNDO NACIONAL, DESDE 2019')}
  {row('PARADO NA CONTA', 'R$ 174 MI', 174/331, R, W(s,'parados',0,-.2), sub='COM RENDIMENTOS · MINISTÉRIO DA JUSTIÇA')}</div>
<div class="el body" data-flow="m:4" data-gap="30" data-a="up" data-t="{W(s,'blindados',0,-.2)}" style="left:80px;width:860px">Blindados: negados porque a lei exige <b>GLO, que o estado não pediu desta vez.</b></div>
<div class="el rows" data-flow="m:5" data-gap="30" data-a="fade" data-t="{W(s,'mantém',0,-.3)}" style="left:80px">
  {row('CRÉDITO', 'FORÇA NACIONAL NO RIO DESDE 2023', None, Y, 0, sub=f'GOVERNO ATUAL {SQUID}')}
  {row('CRÉDITO', 'COMPRA DE ARMAS POR ATIRADORES CAIU 91%', None, Y, 0, sub='448 MIL → 40 MIL · 2022–24', fade=W(s,'atiradores',0,-.2))}
  {row('CONTA', 'CORTOU VERBA DA SEGURANÇA', None, R, 0, sub='~R$ 500 MI CONTINGENCIADOS', fade=W(s,'cortou',0,-.2))}</div>
<div class="el fine" data-flow="m:6" data-gap="18" data-a="fade" data-t="{W(s,'segurança',0,.1)}" style="left:80px">O GOVERNO ATUAL DISSE EM 2023 QUE NÃO DECRETARIA GLO NO RIO, MAS DECRETOU GLO NOS PORTOS (2023) E NO BRICS (2025, A PEDIDO DE CASTRO). AOS FATOS: “GOVERNADOR NÃO PODE PEDIR GLO” É FALSO. O RIO GASTA R$ 17 BI POR ANO EM SEGURANÇA (FBSP). LEI ANTIFACÇÃO, SANCIONADA PELO PRESIDENTE.</div>
''', 'i13', 'MJSP (NOTA DE 28/10/2025) · FBSP, ANUÁRIO 2026 · AOS FATOS · PODER360', kbo='60% 60%'))

s = 'v15'; CUR['s'] = s
H.append(scene(s, f'''
{eb(0, 'RESUMINDO', top=300)}
<div class="el h" data-flow="m:2" data-gap="30" data-a="up" data-t="{W(s,'lado',0,-.3)}" style="left:80px;width:880px;font-size:66px;color:#fff">NÃO É CULPA <span class="hl">DE UM LADO SÓ.</span></div>
<div class="el rows" data-flow="m:3" data-gap="34" data-a="fade" data-t="{W(s,'combinação',0,-.2)}" style="left:80px">
  {row('HÁ DÉCADAS', 'FACÇÕES E MILÍCIAS', None, '#fff', 0)}
  {row('É DA UNIÃO', 'FRONTEIRAS E PORTOS POR ONDE ENTRAM ARMAS E DROGAS', None, Y, 0, fade=W(s,'armas',0,-.2))}
  {row('É DO ESTADO', 'AS ESCOLHAS SOBRE A POLÍCIA', None, R, 0, fade=W(s,'escolhas',0,-.2))}
  {row('É DA PREFEITURA', 'GUARDA E ORDEM URBANA', None, WH, 0, fade=W(s,'prefeitura',0,-.2))}</div>
<div class="el h" data-flow="m:4" data-gap="32" data-a="slam" data-t="{W(s,'vinte',0,-.15)}" style="left:80px;width:880px;font-size:54px;color:#fff">23 ANOS DE <span style="color:#5B7CFF">DIREITA.</span><br><span class="hl">E A CULPA É DA ESQUERDA?</span></div>
<div class="el repost" data-flow="m:5" data-gap="32" data-a="slam" data-t="{W(s,'cobraria',0,-.3)}" data-shake="1" style="left:80px;width:880px;font-size:44px">O QUE VOCÊ COBRARIA DO GOVERNADOR ELEITO?<small>Douglas Ruas (PL, direita) · posse em 06/01/2027</small></div>
<div class="el fine" data-flow="m:6" data-gap="20" data-a="fade" data-t="{W(s,'grupo',0,.2)}" style="left:80px">DESDE AGO/2003 (ROSINHA NO MDB), O RIO É GOVERNADO PELA DIREITA (MDB = DIREITA NA ESCALA, 7,01). RUAS FOI ELEITO NO 1º TURNO DEPOIS QUE O TSE ANULOU OS VOTOS DE GAROTINHO; É DO GRUPO DE CASTRO E BACELLAR, SEGUNDO A IMPRENSA.</div>
''', 'i15', 'TSE · TRE-RJ · FBSP · ISP-RJ · GENI/UFF · SOU DA PAZ', kbo='55% 55%'))

CSS = open(os.path.join(KIT, 'preview_kit/style.css')).read() + '''
.shadeX{position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,7,9,.9) 0%,rgba(6,7,9,.72) 48%,rgba(6,7,9,.42) 100%),linear-gradient(180deg,rgba(6,7,9,.75) 0%,rgba(6,7,9,0) 22%,rgba(6,7,9,0) 58%,rgba(6,7,9,.96) 80%)}
.eyebrow{display:flex;align-items:center;gap:14px;font-family:JBM;font-weight:700;font-size:24px;letter-spacing:3px;color:#FFD34D;text-transform:uppercase;white-space:nowrap}
.eyebrow::before{content:"";width:40px;height:4px;border-radius:2px;background:#FFD34D}
.eyebrow b{font-family:Rub;font-weight:900;font-size:26px;color:#F2ECE0;letter-spacing:0}
.eyebrow .ide{font-size:19px;padding:2px 9px;letter-spacing:1px}
.body{font-family:Rub;font-weight:500;font-size:40px;line-height:1.22;color:#E9E4D8;text-shadow:0 2px 14px rgba(0,0,0,.6);text-wrap:pretty}
.body b{font-weight:800;color:#fff}
.fine{font-family:JBM;font-weight:500;font-size:20px;letter-spacing:1px;line-height:1.5;color:#A39C8E;width:860px;text-transform:uppercase}.fine .ide{font-size:13px}
.note{font-family:JBM;font-weight:700;font-size:21px;letter-spacing:1.5px;line-height:1.5;color:#BDB6A6;width:860px}
.rows{width:880px;display:flex;flex-direction:column}
.row{display:grid;grid-template-columns:300px 340px 1fr;align-items:center;column-gap:22px;padding:16px 0;border-top:1px solid rgba(242,236,224,.2)}
.row:last-child{border-bottom:1px solid rgba(242,236,224,.2)}
.row .k{font-family:JBM;font-weight:700;font-size:23px;letter-spacing:1.5px;color:#E9E4D8;line-height:1.25}
.row .k small{display:block;font-size:17px;letter-spacing:1px;color:#A9A291;margin-top:6px;line-height:1.5}
.row .k .ide{font-size:15px;padding:1px 7px;margin-left:4px;letter-spacing:.5px}
.row .track{height:20px;width:330px;background:rgba(242,236,224,.1);border-radius:3px;overflow:hidden}
.row .track .bar{height:20px;border-radius:3px}
.row .v{font-family:Rub;font-weight:900;font-size:44px;white-space:nowrap;text-align:right}
.row.txt{grid-template-columns:300px 1fr}.row.txt .v{text-align:left;font-size:36px;font-weight:800;white-space:normal;line-height:1.1}
.items{width:880px;display:flex;flex-direction:column}
.item{padding:20px 0 22px;border-top:1px solid rgba(242,236,224,.22)}
.item:last-child{border-bottom:1px solid rgba(242,236,224,.22)}
.item .kick{font-family:JBM;font-weight:700;font-size:21px;letter-spacing:2px;color:#FFD34D;text-transform:uppercase}
.item .kick .ide{font-size:16px;padding:1px 8px;margin-left:6px}
.item .t{font-family:Rub;font-weight:800;font-size:46px;line-height:1.1;margin-top:10px;text-wrap:balance;text-shadow:0 3px 16px rgba(0,0,0,.55)}
.mut{color:#BDB6A6;font-weight:500}.mut.sm{font-size:30px;line-height:1.3}
.counter{display:flex;align-items:center;gap:26px}.counter .cnt{font-size:150px}.counter b{font-family:Rub;font-weight:600;font-size:34px;line-height:1.15;color:#E9E4D8;white-space:nowrap}
.srcline{font-family:JBM;font-weight:500;font-size:19px;letter-spacing:1px;line-height:1.45;color:rgba(242,236,224,.62);text-align:center;text-transform:uppercase}
#foot{bottom:auto;top:1592px;font-size:22px;opacity:.85}
.kar{font-size:48px}
.rail .line,.rail .fill{height:4px;top:24px}
.st i{width:28px;height:28px;left:-14px;top:12px;border-width:5px}
.st b{font-size:17px;top:50px;letter-spacing:1.5px}.st.on b{font-size:19px}
.repost{font-size:58px;border-radius:16px;padding:26px 24px 28px}
.plab{font-size:16px;line-height:1.2;letter-spacing:.5px}.pdot{position:absolute;width:14px;height:14px;border-radius:50%;border:3px solid #0b0c0e}
.big23{position:absolute;left:84px;top:-6px;color:#5B7CFF;font-family:Rub,sans-serif;line-height:.95}.big23 b{display:block;font-size:92px;font-weight:900;letter-spacing:-2px}.big23 span{display:block;font-size:30px;font-weight:800;color:#fff;margin-top:6px}.big23 small{display:block;font-family:JBM,monospace;font-size:17px;color:#A9A291;margin-top:6px;letter-spacing:.5px}
.items.tight .item{padding:14px 0 16px}.items.tight .item .t{font-size:36px}.items.tight .item .kick{font-size:19px}
.zbg{position:absolute;inset:0;background:radial-gradient(ellipse at 55% 58%,#14192a 0%,#0a0b0e 62%)}
.govs .row{padding:11px 0}.govs .selo{display:block;width:max-content;margin-top:6px;background:#FF4A3D;color:#0b0c0e!important;font-weight:700;padding:3px 9px;border-radius:5px;letter-spacing:1px}.govs .row.txt .v{font-size:38px}.row .v .pt{font-family:JBM;font-weight:700;font-size:21px;color:#BDB6A6;letter-spacing:1px}
.row .v .ide{font-size:15px;padding:1px 7px;vertical-align:middle}

.chart{position:absolute}.chart svg{position:absolute;left:0;top:0;overflow:visible}
.crev{position:absolute;left:0;top:0;overflow:hidden;width:0}
.cnote{font-size:20px;line-height:1.25}
.clab{position:absolute;font-family:JBM;font-weight:700;font-size:22px;letter-spacing:1.5px;white-space:nowrap;line-height:1.2;text-shadow:0 2px 10px rgba(0,0,0,.8)}
.clab small{display:block;font-size:15px;line-height:1.6;letter-spacing:.5px;color:#BDB6A6;margin-top:4px}.clab small .ide{font-size:13px;padding:1px 6px}
.quote{color:#F2ECE0;font-weight:800;text-shadow:0 3px 18px rgba(0,0,0,.6)}
.pull{font-family:Rub;font-weight:700;font-style:italic;font-size:50px;line-height:1.15;color:#fff;padding-left:30px;border-left:6px solid #FFD34D;text-shadow:0 3px 16px rgba(0,0,0,.6)}
.pull small{display:block;font-family:JBM;font-style:normal;font-weight:700;font-size:20px;letter-spacing:1.5px;color:#BDB6A6;margin-top:16px}
'''
page = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Rio de Janeiro</title>
<link rel="stylesheet" href="fx.css"><style>{CSS}</style></head><body><div id="stage">
{"".join(H)}
<div id="grain"></div><div id="foot">@tentandochegaratevoce</div></div>
<script>window.DUR={DUR:.2f};</script><script src="fx.js"></script><script src="fx2.js"></script><script>
/* zoom da abertura: Brasil -> estado do RJ (g#zcam data-cam). Roda dentro do FX.frame do motor, então vale na prévia e no MP4. */
(function(){{const B=window.FX;const ease=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;const cl=x=>Math.max(0,Math.min(1,x));
window.FX=Object.assign({{}},B,{{frame(sc,t,T,dur){{B.frame(sc,t,T,dur);const g=sc.querySelector('#zcam');if(!g)return;const zi=sc.querySelector('.zseq');if(zi&&window.__ZN&&!navigator.webdriver&&!window.__ZLIVE){{const k=Math.max(0,Math.min(__ZN-1,Math.round(t*24)));if(zi._k!==k){{zi._k=k;zi.src=__ZF(k)}}zi.style.display='block';sc.querySelector('.zmap').style.display='none';return}}
const c=g._c||(g._c=JSON.parse(g.dataset.cam));const p=ease(cl((t-.15)/2.9)),pc=ease(cl((t-.15)/2.4));
const s=c.s0*Math.pow(c.s1/c.s0,p);
const k0={{x:(540-c.x0)/c.s0,y:(1060-c.y0)/c.s0}},k1={{x:(600-c.x1)/c.s1,y:(1100-c.y1)/c.s1}};
const cx=k0.x+(k1.x-k0.x)*pc,cy=k0.y+(k1.y-k0.y)*pc,ax=540+60*pc,ay=1060+40*pc;
g.setAttribute('transform',`translate(${{(ax-s*cx).toFixed(2)}},${{(ay-s*cy).toFixed(2)}}) scale(${{s.toFixed(4)}})`);
const m=g.querySelector('.zmun');if(m)m.setAttribute('opacity',cl((p-.75)/.25).toFixed(3));}}}});}})();
</script><script src="engine.js"></script><script src="layout.js"></script></body></html>'''
open(os.path.join(KIT, 'rj.html'), 'w').write(page)
print('ok', DUR)
