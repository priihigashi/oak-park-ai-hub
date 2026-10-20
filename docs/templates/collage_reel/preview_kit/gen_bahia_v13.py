"""Reel v5 (mitos) — Bahia e Norte (explicativo). Redesenho editorial: uma linha de alinhamento à esquerda,
sem caixas (texto direto sobre a foto escurecida), eyebrow numerado por capítulo, tabelas com filete,
fonte da informação embaixo do @, sem aviso de IA na tela. Gera ../bahia.html."""
import json, html, re, os
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open('/home/claude/work/v9/timeline.json'))
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
KAR_MAX = 60   # 2 linhas cheias de 860 px; cor segue a voz palavra por palavra
def _kar_part(n, N, pre):
    INF = 1e9; best = [[INF]*(N+1) for _ in range(n+1)]; cut = [[0]*(N+1) for _ in range(n+1)]
    best[0][0] = 0
    for k in range(1, n+1):
        for j in range(1, N+1):
            for i in range(k-1, j):
                v = max(best[k-1][i], pre[j]-pre[i])
                if v < best[k][j]: best[k][j] = v; cut[k][j] = i
    cuts = []; j = N
    for k in range(n, 0, -1): i = cut[k][j]; cuts.append(i); j = i
    return best[n][N], sorted(cuts[:-1])
def kar(sid):
    """Páginas equilibradas (partição ótima): menor número de páginas com no máximo KAR_MAX caracteres,
    repartidas para todas terem tamanho parecido; nenhuma página com 1 linha curta ou palavra sozinha."""
    import math
    ws = S[sid]['words']; L = [len(w) + 1 for w, t in ws]; N = len(L)
    pre = [0]
    for x in L: pre.append(pre[-1] + x)
    n = max(1, math.ceil(pre[-1] / KAR_MAX))
    while True:
        mx, cuts = _kar_part(n, N, pre)
        if mx <= KAR_MAX + 2 or n >= N: break
        n += 1
    cuts = set(cuts); toks = []
    for i, (w, t) in enumerate(ws):
        if i in cuts: toks.append('/')
        toks.append(f"{html.escape(w.replace(':', ''))}:{t}")
    return f'<div class="kar karfull el" data-words="{" ".join(toks)}" style="left:110px;top:1438px;width:860px"></div>'
DUR = TL[-1]['e']
CH = ["MITO 1", "CAUSA", "PROVA", "MITO 2", "MESMO PL", "BAHIA"]
def rail(active, t=.1):
    xs = [110+i*172 for i in range(6)]
    dots = ''.join(f'<div class="st{" on" if i==active else ""}{" past" if i<active else ""}" style="left:{x}px"><i></i><b>{y}</b></div>' for i, (x, y) in enumerate(zip(xs, CH)))
    return f'<div class="rail el" data-a="fade" data-t="{t}" data-d=".3" style="left:0;top:150px"><div class="line"></div><div class="fill" style="width:{xs[active]-60}px"></div>{dots}</div>'
def scene(sid, inner, bg, src, kbo='60% 50%', kb=1.08):
    o = S[sid]
    b = f'<img class="bgimg" src="assets/bn/{bg}.jpg" data-kb="{kb}" data-kbo="{kbo}"><div class="shadeX"></div>'
    s = f'<div class="el srcline" data-a="fade" data-t=".4" style="left:110px;top:1656px;width:860px">FONTE: {src}</div>'
    return f'<section class="scene" data-s="{o["s"]}" data-e="{o["e"]}" data-in="cut" data-theme="dark">{b}<div class="safe">{inner}</div>{kar(sid)}{s}</section>\n'
CUR = {'s': None}
def eb(n, txt, t=.05, top=None, flow='m:1'):
    top = 330
    ft = f' data-ftop="{top}"' if top else ''
    num = f'<b>{n:02d}</b>' if n else ''
    return f'<div class="el eyebrow" data-flow="{flow}"{ft} data-a="left" data-t="{t}" style="left:60px">{num}{txt}</div>'
def ide(k, lab): return f'<i class="ide {k}">{lab}</i>'
ESQ, CESQ, DIR, CDIR = ide('esq', 'ESQUERDA'), ide('esq', 'CENTRO-ESQUERDA'), ide('dir', 'DIREITA'), ide('dir', 'CENTRO-DIREITA')
Y, R, WH = '#FFD34D', '#FF4A3D', '#F2ECE0'
BARMAX = 370
def row(k, v, frac, color, t, sub='', fade=None):
    sb = f'<small>{sub}</small>' if sub else ''
    fa = f' data-a="fade" data-t="{fade}"' if fade is not None else ''
    col = color if color != WH else '#fff'
    if frac is None:
        num = ' num' if re.fullmatch(r'[\d.,→ ·º%+−-]+', v) else ''
        return f'<div class="row txt{num}"{fa}><div class="k">{k}{sb}</div><div class="v" style="color:{col}">{v}</div></div>'
    bar = f'<div class="track"><div class="bar" data-t="{t}" data-d=".7" data-to="{int(BARMAX*frac)}" style="background:{color}"></div></div>'
    return f'<div class="row"{fa}><div class="k">{k}{sb}</div>{bar}<div class="v" style="color:{col}">{v}</div></div>'
def item(kick, txt, t, color='#fff'):
    return f'<div class="item" data-a="up" data-t="{t}"><div class="kick">{kick}</div><div class="t" style="color:{color}">{txt}</div></div>'
IDS = 'IDEOLOGIA: BOLOGNESI ET AL. (DADOS, 2023)'
FT = json.load(open('/home/claude/work/v9/ftop.json')) if os.path.exists('/home/claude/work/v9/ftop.json') else {}
H = []


# ---------- gráfico de linhas animado (revela da esquerda pra direita via .bar) ----------
def _colat(i, segs):
    col = segs[0][1]
    for a0, cc in segs:
        if i >= a0: col = cc
    return col
def _chart_grid(px0, px1, py0, py1, ticks, years, h, ymin, ymax):
    def X(i): return px0 + (px1 - px0) * i / (len(years) - 1)
    def Yv(v): return py1 - (py1 - py0) * (v - ymin) / (ymax - ymin)
    g = ''.join(f'<line x1="{px0}" x2="{px1}" y1="{Yv(v):.1f}" y2="{Yv(v):.1f}" stroke="rgba(242,236,224,.14)" stroke-width="1.5"/>'
                f'<text x="{px0-12}" y="{Yv(v)+7:.1f}" text-anchor="end" font-family="JBM" font-weight="700" font-size="19" fill="#9F988A">{v}</text>' for v in ticks)
    lab_i = [0, len(years)//2, len(years)-1]
    g += ''.join(f'<text x="{X(i):.1f}" y="{h-12}" text-anchor="middle" font-family="JBM" font-weight="700" font-size="19" fill="#9F988A">{years[i]}</text>' for i in lab_i)
    return g
def _chart_marks(marks, years, px0, px1, py0, py1, ymin, ymax):
    def X(i): return px0 + (px1 - px0) * i / (len(years) - 1)
    def Yv(v): return py1 - (py1 - py0) * (v - ymin) / (ymax - ymin)
    mk = ''
    for yr, txt, col in marks:
        i = years.index(yr)
        mk += (f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{py0}" y2="{py1}" stroke="{col}" stroke-width="2" stroke-dasharray="6 6"/>'
               f'<text x="{X(i)+10:.1f}" y="{py1-12}" font-family="JBM" font-weight="700" font-size="18" fill="{col}">{txt}</text>')
    return mk
def _chart_series(series, years, px0, px1, py0, py1, ymin, ymax):
    def X(i): return px0 + (px1 - px0) * i / (len(years) - 1)
    def Yv(v): return py1 - (py1 - py0) * (v - ymin) / (ymax - ymin)
    lines = ''
    for s in series:
        segs = s.get('segs') or [(0, s['c'])]
        if segs: s['c'] = segs[-1][1]
        dash = ' stroke-dasharray="10 8"' if s.get('dash') else (' stroke-dasharray="2 10"' if s.get('dot') else '')
        for k, (a0, cc) in enumerate(segs):
            b0 = segs[k+1][0] if k+1 < len(segs) else len(s['v']) - 1
            pts = ' '.join(f'{X(i):.1f},{Yv(s["v"][i]):.1f}' for i in range(a0, b0 + 1))
            lines += f'<polyline points="{pts}" fill="none" stroke="{cc}" stroke-width="{s.get("w",5)}" stroke-linejoin="round" stroke-linecap="round"{dash}/>'
        for (i, txt) in s.get('dots', []):
            cc = _colat(i, segs)
            lines += (f'<circle cx="{X(i):.1f}" cy="{Yv(s["v"][i]):.1f}" r="9" fill="{cc}" stroke="#0b0c0e" stroke-width="3"/>'
                      f'<text x="{X(i):.1f}" y="{Yv(s["v"][i])-18:.1f}" text-anchor="middle" font-family="Rub" font-weight="900" font-size="30" fill="{cc}" stroke="#0b0c0e" stroke-width="6" paint-order="stroke">{txt}</text>')
    return lines
def _chart_label_pos(series, py0, py1, ymin, ymax):
    def Yv(v): return py1 - (py1 - py0) * (v - ymin) / (ymax - ymin)
    want = sorted([(Yv(s['v'][-1]), i) for i, s in enumerate(series)])
    pos = {}; last = -1e9
    for y, i in want:
        sb_ = series[i].get('sub'); hgt = 34 + (28 * (sb_.count('<br>') + 1) if sb_ else 0)
        y = max(y, last); pos[i] = y; last = y + hgt + 8
    return pos
def chart(sid, years, series, ymax, ticks, t0, dur, marks=(), w=960, h=600, lw=230, stages=None, notes=(), ymin=0):
    px0, px1, py0, py1 = 56, w - lw - 20, 14, h - 46
    def X(i): return px0 + (px1 - px0) * i / (len(years) - 1)
    def Yv(v): return py1 - (py1 - py0) * (v - ymin) / (ymax - ymin)
    grid = _chart_grid(px0, px1, py0, py1, ticks, years, h, ymin, ymax)
    mk = _chart_marks(marks, years, px0, px1, py0, py1, ymin, ymax)
    lines = _chart_series(series, years, px0, px1, py0, py1, ymin, ymax)
    pos = _chart_label_pos(series, py0, py1, ymin, ymax)
    labels = ''
    for i, s in enumerate(series):
        ly = pos[i]
        sub = f'<small>{s["sub"]}</small>' if s.get('sub') else ''
        labels += (f'<div class="clab" data-a="fade" data-t="{s.get("lt", t0+dur):.2f}" style="left:{px1+18}px;top:{ly-16:.0f}px;color:{s["c"]}">'
                   f'<b>{s["n"]}</b>{sub}</div>')
    return (f'<div class="el chart" data-flow="{{flow}}" style="left:60px;width:{w}px;height:{h}px">'
            f'<svg class="cgrid" width="{w}" height="{h}">{grid}{mk}</svg>'
            + (''.join(f'<div class="bar crev" data-t="{st}" data-d="{sd}" data-to="{(X(b)+40 if b < len(years)-1 else px1+48) - (X(a) if a else 0):.0f}" style="height:{h}px;left:{X(a) if a else 0:.0f}px"><svg width="{w}" height="{h}" style="margin-left:-{X(a) if a else 0:.0f}px">{lines}</svg></div>'
                       for (a, b, st, sd) in stages) if stages else
               f'<div class="bar crev" data-t="{t0}" data-d="{dur}" data-to="{px1+12}" style="height:{h}px"><svg width="{w}" height="{h}">{lines}</svg></div>')
            + ''.join(f'<div class="clab cnote" data-a="fade" data-t="{nt:.2f}" style="left:{X(ni)+dx:.0f}px;top:{Yv(nv)+dy:.0f}px;color:{nc}">{ntx}</div>' for (ni, nv, ntx, nc, nt, dx, dy) in notes)
            + f'{labels}</div>')

def quote(txt, t, flow, gap=34, size=58):
    return f'<div class="el h quote" data-flow="{flow}" data-gap="{gap}" data-a="up" data-t="{t}" style="left:60px;width:960px;font-size:{size}px">{txt}</div>'

PFLX = ide('dir', 'EXTREMA-DIREITA')
YRS1 = [str(y) for y in range(2000, 2015)]
BA1 = [9.46,12.27,13.2,16.12,16.69,20.85,23.73,25.98,33.23,37.11,41.69,39.36,43.37,37.85,40.01]
AL1 = [26.55,29.06,34.32,35.61,35.11,39.89,53.1,59.51,60.33,59.35,66.88,71.39,64.63,65.07,62.78]
MA1 = [6.42,9.82,10.44,13.54,12.32,15.32,15.67,17.99,20.25,21.96,23.1,23.94,26.47,31.84,35.94]
BR1 = [27.35,27.86,28.53,29.14,26.94,26.13,26.61,26.2,26.72,27.18,27.8,27.45,29.41,28.55,29.82]
YRS2 = [str(y) for y in range(2014, 2026)]
CE2 = [50.8,46.4,39.8,59.1,52.8,25.8,45.5,39.0,35.5,33.9,37.5,34.7]
BA2 = [42.1,41.3,46.4,45.5,42.8,40.4,44.8,50.0,47.1,44.4,40.7,36.8]
BR2 = [29.5,28.6,29.9,30.9,27.5,22.7,23.8,23.9,23.6,21.9,20.8,19.1]

s = 'v01'; CUR['s'] = s
H.append(scene(s, f'''
{eb(0, f'BAHIA · PT {ESQ} DESDE 2007', top=330)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'lidera',0,-.15)}" data-shake="1" style="left:60px;width:960px;font-size:92px;color:#fff">LÍDER EM <span class="hl">MORTES VIOLENTAS</span> NO BRASIL</div>
<div class="el h redtxt" data-flow="m:3" data-gap="30" data-a="slam" data-t="{W(s,'culpa',0,-.1)}" data-d=".35" style="left:60px;font-size:96px;width:960px">E A CULPA É DA ESQUERDA.</div>
<div class="el body" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'vamos',0,-.2)}" style="left:60px;width:960px"><b>Vamos aos fatos.</b></div>
<div class="el fine" data-flow="m:5" data-gap="26" data-a="fade" data-t="{W(s,'vamos',0,.2)}" style="left:60px">EM NÚMERO DE MORTES: 5.473 EM 2025, O MAIOR DO PAÍS. EM TAXA POR 100 MIL, É A 2ª, ATRÁS DO AMAPÁ.</div>
''', 'i01', 'FBSP, ANUÁRIO 2026 · BAHIA NOTÍCIAS, JUL/2026 · ' + IDS, kbo='70% 70%'))

s = 'v02'; CUR['s'] = s
c1 = chart(s, YRS1, [
    dict(n='ALAGOAS', sub=f'PSB {CESQ}<br>→ PSDB {DIR} 2007', v=AL1, c=R, segs=[(0,'#FF9A8E'),(7,'#A8BCFF')], lt=W(s,'alagoas',0,-.1), dots=[(11, '71,4')]),
    dict(n='BAHIA', sub=f'PFL {PFLX}<br>→ PT {ESQ}', v=BA1, c=Y, w=7, segs=[(0,'#5B7CFF'),(7,'#FF4A3D')], lt=W(s,'bahia',0,-.1), ly=-8),
    dict(n='MARANHÃO', sub=f'PFL/PMDB {DIR}<br>→ PDT {CESQ}', v=MA1, c='#fff', segs=[(0,'#5EC8FF'),(7,'#FF5C8A'),(9,'#5EC8FF')], lt=W(s,'maranhão',0,-.1), ly=14),
    dict(n='BRASIL', v=BR1, c='rgba(242,236,224,.55)', dash=True, w=4, lt=W(s,'olha',0,.6), ly=24),
], 80, [0, 25, 50, 75], W(s,'olha',0,-.1), 4.2, marks=[('2007', 'PT ASSUME A BAHIA', '#fff')]).replace('{flow}', 'm:3')
H.append(scene(s, rail(0)+f'''
{eb(1, 'MITO 1 · HOMICÍDIOS POR 100 MIL', top=300)}
{quote('“A ESQUERDA CAUSOU A VIOLÊNCIA.”', W(s,'mito',0), 'm:2', gap=26)}
<div class="el body" data-flow="m:2.5" data-gap="20" data-a="fade" data-t=".3" style="left:60px;width:960px;font-size:26px"><span class="lg"><i style="background:#FF4A3D"></i>ESQUERDA</span><span class="lg"><i style="background:#5B7CFF"></i>DIREITA</span><span class="lg"><i style="background:#9A9A9A"></i>BRASIL</span><span class="lgn">A COR MUDA QUANDO MUDA O GOVERNO</span></div>
{c1}
<div class="el stamp-r" data-flow="m:4" data-gap="36" data-a="stamp" data-t="{W(s,'mesmo',0,-.05)}" data-d=".35" data-r="-2" style="left:60px;white-space:nowrap;font-size:46px">OS DADOS NÃO SUSTENTAM</div>
''', 'i04', 'IPEA/FBSP, ATLAS DA VIOLÊNCIA (SIM/DATASUS) · ' + IDS, kbo='50% 70%'))

s = 'v03'; CUR['s'] = s
H.append(scene(s, rail(1)+f'''
{eb(2, 'O QUE MUDOU FOI O CRIME', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t="{W(s,'pcc',0,-.2)}" style="left:60px">
  {row('PCC E CV', 'SAEM DO SUDESTE ATRÁS DE ROTAS E PORTOS', None, '#fff', 0)}
  {row('PRESÍDIOS', 'VIRAM CENTRO DE RECRUTAMENTO', None, '#fff', 0, fade=W(s,'recrutaram',0,-.2))}
  {row('2015', 'NASCE O BDM, NA BAHIA', None, Y, 0, fade=W(s,'recrutaram',0,.6))}</div>
<div class="el h" data-flow="m:3" data-gap="50" data-a="slam" data-t="{W(s,'nordestinação',0,-.2)}" style="left:60px;width:960px;font-size:76px;color:{Y}">A “NORDESTINAÇÃO” DA VIOLÊNCIA.</div>
<div class="el note" data-flow="m:4" data-gap="22" data-a="fade" data-t="{W(s,'nordestinação',0,.3)}" style="left:60px">TERMO USADO POR PESQUISADORES DA SEGURANÇA PÚBLICA NO NORDESTE</div>
<div class="el fine" data-flow="m:5" data-gap="20" data-a="fade" data-t="{W(s,'nordestinação',0,.8)}" style="left:60px">QUEM CUIDA DO QUÊ: POLÍCIAS CIVIL E MILITAR, PRESÍDIOS E INVESTIGAÇÃO SÃO DO ESTADO. FRONTEIRAS, PORTOS, CONTROLE DE ARMAS E POLÍCIA FEDERAL SÃO DA UNIÃO.</div>
''', 'i10', 'REV. BRAS. DE SEGURANÇA PÚBLICA, 2024 · FÓRUM POPULAR DE SEG. PÚBLICA DO NE, 2019', kbo='60% 55%'))

s = 'v04'; CUR['s'] = s
c2 = chart(s, YRS2, [
    dict(n='CEARÁ', sub=f'PT {ESQ}<br>MESMO GOV. 2015–22', v=CE2, c='#FF9A8E', w=7, lt=W(s,'ceará',0,-.1), dots=[(3, '59,1'), (5, '25,8'), (6, '45,5')]),
    dict(n='BAHIA', sub=f'PT {ESQ}', v=BA2, c=R, lt=W(s,'prova',0,.5), ly=-6),
    dict(n='BRASIL', v=BR2, c='rgba(242,236,224,.55)', dash=True, w=4, lt=W(s,'prova',0,.5), ly=4),
], 70, [0, 20, 40, 60], W(s,'prova',0), 3.0, marks=[('2017', 'GUERRA DE FACÇÕES', '#fff')]).replace('{flow}', 'm:2')
H.append(scene(s, rail(2)+f'''
{eb(3, 'A PROVA · MORTES VIOLENTAS POR 100 MIL', top=320)}
<div class="el body" data-flow="m:1.5" data-gap="22" data-a="fade" data-t=".3" style="left:60px;width:960px;font-size:26px"><span class="lg"><i style="background:#FF4A3D"></i>ESQUERDA</span><span class="lg"><i style="background:#5B7CFF"></i>DIREITA</span><span class="lg"><i style="background:#9A9A9A"></i>BRASIL</span></div>
{c2}
<div class="el body" data-flow="m:3" data-gap="36" data-a="up" data-t="{W(s,'ritmo',0,-.2)}" style="left:60px;width:960px">O que move a curva: <b>tréguas e guerras entre facções.</b></div>
<div class="el fine" data-flow="m:4" data-gap="22" data-a="fade" data-t="{W(s,'ritmo',0,.4)}" style="left:60px">EM 2017, O RECORDE DO PAÍS FOI NO RIO GRANDE DO NORTE (67,2), GOVERNADO PELO PSD {DIR}. AS FACÇÕES NÃO ESCOLHEM PARTIDO. A BASE DE POPULAÇÃO DO FBSP MUDA EM 2021 E 2023 (CENSO 2022).</div>
''', 'i05', 'FBSP, ANUÁRIOS 2016–2026 (MVI) · FBSP, 2021 (MOTIM DA PM E GUERRA CV × GDE NO CE)', kbo='50% 70%'))

s = 'v05'; CUR['s'] = s
H.append(scene(s, rail(2)+f'''
{eb(4, 'QUEM GOVERNA HOJE · MORTES POR 100 MIL · 2025', top=320)}
<div class="el h" data-flow="m:2" data-gap="40" data-a="up" data-t=".3" data-o="{W(s,'média',0,-.4)}" style="left:60px;width:960px;font-size:76px;color:#fff">PARTIDO SE COMPARA <span class="hl">NA MESMA REGIÃO.</span></div>
<div class="el rows" data-flow="m:2" data-a="fade" data-t="{W(s,'média',0,-.3)}" data-o="{W(s,'nordeste',0,-.4)}" style="left:60px">
  {row('BRASIL · DIREITA', '14,8', 14.8/23.4, '#5B7CFF', W(s,'direita',0), sub='SUL E SUDESTE: QUASE TODOS DE DIREITA')}
  {row('BRASIL · ESQUERDA', '23,4', 1, R, W(s,'direita',0,.3), sub='PODER360, 2026 · SEM MORTES PELA POLÍCIA')}</div>
<div class="el rows" data-flow="m:2" data-a="fade" data-t="{W(s,'nordeste',0,-.2)}" style="left:60px">
  {row(f'NE · ESQUERDA', '28,7', 28.7/29.4, R, W(s,'esquerda',0), sub=f'BA · CE · PI · RN · PT {ESQ}<br>MA · PB · PSB {CESQ}')}
  {row(f'NE · DIREITA', '29,4', 1, '#5B7CFF', W(s,'direita',1), sub=f'AL · MDB {DIR}<br>PE · SE · PSD {DIR}')}</div>
<div class="el note" data-flow="m:3" data-gap="16" data-a="fade" data-t="{W(s,'direita',1,.3)}" style="left:60px">MÉDIA SIMPLES DOS ESTADOS · CÁLCULO NOSSO COM DADOS DO FBSP</div>
<div class="el rows" data-flow="m:4" data-gap="40" data-a="fade" data-t="{W(s,'melhor',1,-.2)}" style="left:60px">
  {row('PIAUÍ', '17,1', None, '#fff', 0, sub=f'MENOR TAXA DO NE · PT {ESQ}', fade=W(s,'piauí',0,-.2))}
  {row('BAHIA', '36,8', None, R, 0, sub=f'MAIOR TAXA DO NE · PT {ESQ}', fade=W(s,'bahia',0,-.2))}</div>
<div class="el fine" data-flow="m:5" data-gap="24" data-a="fade" data-t="{W(s,'bahia',0,.4)}" style="left:60px">DESDE QUANDO: BA PT DESDE 2007 · CE PT DESDE 2015 · PI PT DESDE 2015 (E 2003–10) · RN PT DESDE 2019 · PB PSB DESDE 2011 · MA PCDOB/PSB DESDE 2015 · AL MDB DESDE 2015 · SE MDB/PSD DESDE 2013 (ANTES PT) · PE PSD DESDE 2023 (ANTES PSB, 2007–22). A GAZETA DO POVO USA OUTRA BASE (MJ, SÓ HOMICÍDIOS).</div>
''', 'i09', 'FBSP, ANUÁRIO 2026 · PODER360 E GAZETA DO POVO, 2026 · ' + IDS, kbo='70% 60%'))

s = 'v06'; CUR['s'] = s
H.append(scene(s, rail(3)+f'''
{eb(5, 'MITO 2', top=300)}
{quote('“ENTÃO O GOVERNO NÃO TEM CULPA.”', W(s,'mito',0), 'm:2', gap=26)}
<div class="el stamp-r" data-flow="m:3" data-gap="30" data-a="stamp" data-t="{W(s,'também',0,-.05)}" data-d=".35" data-r="-2" style="left:60px;white-space:nowrap;font-size:46px">TAMBÉM NÃO</div>
<div class="el rows" data-flow="m:4" data-gap="44" data-a="fade" data-t="{W(s,'pernambuco',0,-.3)}" style="left:60px">
  {row('PERNAMBUCO', '52,2 → 33,9', None, '#fff', 0, sub=f'2007–2013 · PSB {CESQ}')}
  {row('PARAÍBA', '42,6 → 23,4', None, '#fff', 0, sub=f'2011–2019 · PSB {CESQ}', fade=W(s,'paraíba',0,-.2))}
  {row('PARÁ', '56,6 → 29,5', None, '#fff', 0, sub=f'2018–2024 · MDB {DIR}', fade=W(s,'pará',0,-.2))}</div>
<div class="el note" data-flow="m:5" data-gap="22" data-a="fade" data-t="{W(s,'pará',0,.3)}" style="left:60px">POR 100 MIL · HOMICÍDIOS (PE, PB) E MORTES VIOLENTAS (PA)</div>
''', 'i03', 'ATLAS DA VIOLÊNCIA · FBSP (GAZETA DO POVO, 2019) · FBSP, ANUÁRIO 2025 · ' + IDS, kbo='40% 55%'))

s = 'v07'; CUR['s'] = s
YPE = [str(y) for y in range(2004, 2014)]
PE = [49.2, 50.2, 51.7, 52.2, 50.2, 44.4, 38.3, 38.2, 36.3, 33.9]
c7 = chart(s, YPE, [
    dict(n='PERNAMBUCO', sub=f'PSB {CESQ}', v=PE, c=R, w=7, lt=W(s,'pernambuco',0), dots=[(3, '52,2'), (9, '33,9')]),
], 60, [20, 30, 40, 50, 60], 0, 0, h=500, ymin=20, marks=[('2007', 'PACTO PELA VIDA', '#fff')],
   stages=[(0, 3, W(s,'vinha',0,-.1), 2.2), (3, 4, W(s,'primeiro',0,-.1), 1.6), (4, 9, W(s,'depois',0,-.1), 2.4)],
   notes=[(0, 49.2, '↗ SUBINDO', '#fff', W(s,'subindo',0,-.2), 4, 26),
          (3, 30, '1 ANO PARA<br>MONTAR', '#fff', W(s,'primeiro',0,.2), 14, 0),
          (6, 46, '↘ 6 ANOS EM QUEDA', Y, W(s,'seis',0,-.2), 0, 0)]).replace('{flow}', 'm:3')
H.append(scene(s, rail(3)+f'''
{eb(6, 'POR QUE FUNCIONOU · HOMICÍDIOS POR 100 MIL', top=300)}
<div class="el h" data-flow="m:2" data-gap="28" data-a="slam" data-t="{W(s,'governador',0,-.15)}" style="left:60px;width:960px;font-size:64px;color:#fff;white-space:nowrap">O GOVERNADOR <span class="hl">NO COMANDO</span></div>
{c7}
<div class="el h" data-flow="m:4" data-gap="30" data-a="up" data-t="{W(s,'pico',0,-.25)}" style="left:60px;width:960px;font-size:54px;color:#fff">NÃO OLHE SÓ O PICO.<br><span class="hl">OLHE A DIREÇÃO.</span></div>
<div class="el note" data-flow="m:5" data-gap="26" data-a="fade" data-t="{W(s,'pará',0,-.2)}" style="left:60px">PARÁ (TERPAZ): OBRAS E SERVIÇOS NOS BAIRROS, JUNTO COM A POLÍCIA. A PARAÍBA USOU O MODELO DE PERNAMBUCO.</div>
<div class="el fine" data-flow="m:6" data-gap="16" data-a="fade" data-t="{W(s,'pará',0,.6)}" style="left:60px">NA DIREITA, GOIÁS TAMBÉM CAIU: 46,4 → 21,4 (2013–2023). MESMA LIÇÃO: GESTÃO.</div>
''', 'i12', 'IPEA/FBSP, ATLAS DA VIOLÊNCIA 2016 E 2025 · INSTITUTO IGARAPÉ (RATTON ET AL., 2014)', kbo='50% 60%'))

s = 'v08'; CUR['s'] = s
H.append(scene(s, rail(5)+f'''
{eb(8, 'BAHIA · O QUE AINDA PRECISA MELHORAR', top=320)}
<div class="el rows big" data-flow="m:2" data-gap="36" data-a="fade" data-t="{W(s,'homicídios',0,-.3)}" style="left:60px">
  {row('HOMICÍDIOS ESCLARECIDOS', '13%', 13/36, R, W(s,'treze',0), sub='BRASIL: 36%')}
  {row('MORTES EM AÇÃO POLICIAL', '28,7%', .287/.35, R, W(s,'polícia',0,-.3), sub='DAS MORTES VIOLENTAS DA BA, 2025')}</div>
<div class="el fine" data-flow="m:3" data-gap="24" data-a="fade" data-t="{W(s,'polícia',0,.3)}" style="left:60px">INVESTIGAÇÃO E POLÍCIA SÃO RESPONSABILIDADE DO GOVERNO DO ESTADO.</div>
''', 'i07', 'INSTITUTO SOU DA PAZ (OUT/2025) · FBSP, ANUÁRIO 2026', kbo='60% 55%'))

s = 'v10'; CUR['s'] = s
H.append(scene(s, rail(5)+f'''
{eb(9, 'BAHIA · O QUE ESTÁ FUNCIONANDO', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t=".2" style="left:60px">
  {row('2011', 'PACTO PELA VIDA · METAS POR TERRITÓRIO', None, '#fff', 0)}
  {row('2024', 'BAHIA PELA PAZ · ASSISTÊNCIA NOS BAIRROS', None, '#fff', 0, fade=W(s,'bahia',0,-.2))}</div>
<div class="el rows" data-flow="m:3" data-gap="44" data-a="fade" data-t="{W(s,'três',0,-.2)}" style="left:60px">
  {row('2023', '−6,0%', 6.0/9.6, Y, W(s,'três',0), sub='QUEDA NAS MORTES VIOLENTAS')}
  {row('2024', '−8,2%', 8.2/9.6, Y, W(s,'queda',0))}
  {row('2025', '−9,6%', 1, Y, W(s,'aumenta',0))}</div>
<div class="el body" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'aumenta',0,.4)}" style="left:60px;width:960px">A queda <b>aumenta a cada ano</b>: a medida começa a pegar.</div>
<div class="el h" data-flow="m:5" data-gap="34" data-a="slam" data-t="{W(s,'direção',0,-.1)}" style="left:60px;font-size:84px;width:960px;color:{Y}">A DIREÇÃO É DE QUEDA.</div>
<div class="el fine" data-flow="m:6" data-gap="22" data-a="fade" data-t="{W(s,'direção',0,.4)}" style="left:60px">A CONTA INCLUI AS MORTES PELA POLÍCIA: A QUEDA NÃO VEM DE TROCAR UM TIPO DE MORTE POR OUTRO.</div>
''', 'i02', 'GOVERNO DA BAHIA · SSP-BA (2023–2024) · FBSP, ANUÁRIO 2026', kbo='60% 55%'))

s = 'v12'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(7, 'MESMO PARTIDO, OUTRO RESULTADO · 2025', top=320)}
<div class="el note" data-flow="m:2" data-gap="30" data-a="fade" data-t="{W(s,'catarina',0,-.4)}" style="left:60px">MORTES VIOLENTAS A CADA 100 MIL HABITANTES</div>
<div class="el rows big" data-flow="m:3" data-gap="16" data-a="fade" data-t="{W(s,'catarina',0,-.3)}" style="left:60px">
  {row('SANTA CATARINA', '7,6', 7.6/22.6, '#5B7CFF', W(s,'catarina',1), sub=f'PL {DIR} · NUNCA TEVE GOVERNO DO PT')}
  {row('RIO DE JANEIRO', '22,6', 1, '#5B7CFF', W(s,'triplo',0,-.6), sub=f'PL {DIR} · DIREITA DESDE 2003')}</div>
<div class="el h" data-flow="m:4" data-gap="50" data-a="slam" data-t="{W(s,'triplo',0,-.15)}" style="left:60px;width:960px;font-size:84px;color:#fff">O <span class="hl">TRIPLO</span>, COM O MESMO PARTIDO.</div>
<div class="el fine" data-flow="m:5" data-gap="26" data-a="fade" data-t="{W(s,'triplo',0,.3)}" style="left:60px">RJ: ROSINHA (MDB DESDE AGO/2003), CABRAL E PEZÃO (MDB), WITZEL (PSC) E CASTRO (PL, 2021–26); O PT TEVE SECRETARIAS COM CABRAL ATÉ 2013. SC, DESDE 2003: MDB, DEM/PSD, PSL/REPUBLICANOS E PL, TODOS DE DIREITA.</div>
''', 'i15', 'FBSP, ANUÁRIO 2026 · FOTO: CHENSIYUAN, CC BY-SA 3.0 · ' + IDS, kbo='50% 55%'))

s = 'v13'; CUR['s'] = s
H.append(scene(s, f'''
{eb(10, 'BAHIA · A PREVENÇÃO JÁ COMEÇOU', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t="{W(s,'estudos',0,-.2)}" style="left:60px">
  {row('BOLSA FAMÍLIA', '+1% → −0,3%', None, Y, 0, sub='COBERTURA → HOMICÍDIOS · PLOS ONE, 2018')}
  {row('EDUCAÇÃO', '+1 PONTO → −25%', None, Y, 0, sub='INDICADOR → HOMICÍDIOS · INSPER, 2022')}</div>
<div class="el note" data-flow="m:3" data-gap="18" data-a="fade" data-t="{W(s,'homicídio',0,-.2)}" style="left:60px">ASSOCIAÇÃO, NÃO PROVA DE CAUSA</div>
<div class="el h" data-flow="m:4" data-gap="50" data-a="slam" data-t="{W(s,'quarto',0,-.15)}" style="left:60px;width:960px;font-size:84px;color:#fff">BAHIA: 4º ESTADO EM <span class="hl">TEMPO INTEGRAL</span></div>
<div class="el body" data-flow="m:5" data-gap="24" data-a="up" data-t="{W(s,'efeito',0,-.2)}" style="left:60px;width:960px"><b>140 mil alunos</b>, 34% da rede estadual. <b>O&nbsp;efeito leva anos, mas já&nbsp;começou.</b></div>
''', 'i14', 'PLOS ONE (MACHADO ET AL., 2018) · INSPER/INST. NATURA, 2022 · MEC, CENSO ESCOLAR 2025', kbo='60% 55%'))

s = 'v14'; CUR['s'] = s
H.append(scene(s, f'''
{eb(0, 'RESUMINDO', top=300)}
<div class="el h" data-flow="m:2" data-gap="30" data-a="up" data-t="{W(s,'região',0,-.2)}" style="left:60px;width:960px;font-size:76px;color:#fff">REGIÃO E FACÇÕES <span style="color:{Y}">EXPLICAM O NÍVEL.</span></div>
<div class="el h" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'oito',0,-.2)}" style="left:60px;width:960px;font-size:76px;color:#fff">EM 2025, <span style="color:{Y}">8 DE 9 ESTADOS DO NORDESTE</span> REDUZIRAM AS MORTES.</div>
<div class="el fine" data-flow="m:4" data-gap="20" data-a="fade" data-t="{W(s,'oito',0,.8)}" style="left:60px">SÓ O RIO GRANDE DO NORTE SUBIU (+19,6%). MORTES VIOLENTAS, FBSP, ANUÁRIO 2026.</div>
<div class="el repost" data-flow="m:5" data-gap="50" data-a="slam" data-t="{W(s,'você',0,-.15)}" data-shake="1" style="left:60px;width:960px;font-size:58px">O QUE VOCÊ COBRARIA DO PRÓXIMO MANDATO?<small>Jerônimo foi reeleito em 04/10/2026 (2027–2030)</small></div>
''', 'i13', 'FBSP, ANUÁRIO 2026 · TSE · IPEA · IGARAPÉ · RBSP', kbo='50% 60%'))

CSS = open(os.path.join(KIT, 'preview_kit/style.css')).read() + '''
.shadeX{position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,7,9,.9) 0%,rgba(6,7,9,.72) 48%,rgba(6,7,9,.42) 100%),linear-gradient(180deg,rgba(6,7,9,.75) 0%,rgba(6,7,9,0) 22%,rgba(6,7,9,0) 58%,rgba(6,7,9,.96) 80%)}
.eyebrow{display:flex;align-items:center;gap:14px;font-family:JBM;font-weight:700;font-size:24px;letter-spacing:3px;color:#FFD34D;text-transform:uppercase;white-space:nowrap}
.eyebrow::before{content:"";width:40px;height:4px;border-radius:2px;background:#FFD34D}
.eyebrow b{font-family:Rub;font-weight:900;font-size:26px;color:#F2ECE0;letter-spacing:0}
.eyebrow .ide{font-size:19px;padding:2px 9px;letter-spacing:1px}
.body{font-family:Rub;font-weight:500;font-size:40px;line-height:1.22;color:#E9E4D8;text-shadow:0 2px 14px rgba(0,0,0,.6);text-wrap:pretty}
.body b{font-weight:800;color:#fff}
.fine{font-family:JBM;font-weight:500;font-size:20px;letter-spacing:1px;line-height:1.5;color:#A39C8E;width:960px;text-transform:uppercase}.fine .ide{font-size:13px}
.note{font-family:JBM;font-weight:700;font-size:21px;letter-spacing:1.5px;line-height:1.5;color:#BDB6A6;width:860px}
.rows{width:960px;display:flex;flex-direction:column}
.row{display:grid;grid-template-columns:300px 340px 1fr;align-items:center;column-gap:22px;padding:16px 0;border-top:1px solid rgba(242,236,224,.2)}
.row:last-child{border-bottom:1px solid rgba(242,236,224,.2)}
.row .k{font-family:JBM;font-weight:700;font-size:23px;letter-spacing:1.5px;color:#E9E4D8;line-height:1.25}
.row .k small{display:block;font-size:17px;letter-spacing:1px;color:#A9A291;margin-top:6px;line-height:1.5}
.row .k .ide{font-size:15px;padding:1px 7px;margin-left:4px;letter-spacing:.5px}
.row .track{height:20px;width:330px;background:rgba(242,236,224,.1);border-radius:3px;overflow:hidden}
.row .track .bar{height:20px;border-radius:3px}
.row .v{font-family:Rub;font-weight:900;font-size:44px;white-space:nowrap;text-align:right}
.row.txt{grid-template-columns:300px 1fr}.row.txt .v{text-align:left;font-size:36px;font-weight:800;white-space:normal;line-height:1.1}
.items{width:960px;display:flex;flex-direction:column}
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
.lg{display:inline-flex;align-items:center;gap:10px;margin-right:24px;font-family:Rub;font-weight:800;color:#F2ECE0;white-space:nowrap}.lg i{display:inline-block;width:24px;height:24px;border-radius:6px}.lgn{font-family:JBM;font-weight:700;font-size:20px;color:#BDB6A6;white-space:nowrap}
.row.txt.num .v{text-align:right;font-size:48px;font-weight:900}
.rows.big .row{padding:26px 0}.rows.big .row .k{font-size:32px}.rows.big .row .k small{font-size:22px}.rows.big .row .v{font-size:64px}.rows.big .track{height:28px}.rows.big .track .bar{height:28px}
.rail .line,.rail .fill{height:4px;top:24px}
.st i{width:28px;height:28px;left:-14px;top:12px;border-width:5px}
.st b{font-size:17px;top:50px;letter-spacing:1.5px}.st.on b{font-size:19px}
.repost{font-size:58px;border-radius:16px;padding:26px 24px 28px}

.chart{position:absolute}.chart svg{position:absolute;left:0;top:0;overflow:visible}
.crev{position:absolute;left:0;top:0;overflow:hidden;width:0}
.cnote{font-size:20px;line-height:1.25}
.clab{position:absolute;font-family:JBM;font-weight:700;font-size:22px;letter-spacing:1.5px;white-space:nowrap;line-height:1.2;text-shadow:0 2px 10px rgba(0,0,0,.8)}
.clab small{display:block;font-size:15px;line-height:1.6;letter-spacing:.5px;color:#BDB6A6;margin-top:4px}.clab small .ide{font-size:13px;padding:1px 6px}
.quote{color:#F2ECE0;font-weight:800;text-shadow:0 3px 18px rgba(0,0,0,.6)}
.pull{font-family:Rub;font-weight:700;font-style:italic;font-size:50px;line-height:1.15;color:#fff;padding-left:30px;border-left:6px solid #FFD34D;text-shadow:0 3px 16px rgba(0,0,0,.6)}
.pull small{display:block;font-family:JBM;font-style:normal;font-weight:700;font-size:20px;letter-spacing:1.5px;color:#BDB6A6;margin-top:16px}
.fine,.note,.rows,.items{width:960px!important}
.eyebrow::before{display:none}
.st b{font-size:23px;top:48px;letter-spacing:0}.st.on b{font-size:25px}
.eyebrow{font-size:28px;letter-spacing:2px}.eyebrow b{font-size:30px}.eyebrow .ide{font-size:21px}
.clab{font-size:28px;letter-spacing:1px}.clab small{font-size:21px;line-height:1.45;color:#C9C2B3}.clab small .ide{font-size:17px}
.cnote{font-size:24px}
.row .k{font-size:26px;letter-spacing:1px}.row .k small{font-size:20px;color:#BDB6A6;line-height:1.4}.row .k .ide{font-size:18px}
.row{grid-template-columns:320px 380px 1fr;padding:14px 0}.row .track{width:370px}.row.txt{grid-template-columns:320px 1fr}
.item .kick{font-size:25px;letter-spacing:1.5px}.pull small{font-size:24px;letter-spacing:1px}
.fine{font-size:23px;letter-spacing:.4px;line-height:1.42;color:#B9B2A3}.fine .ide{font-size:16px}
.note{font-size:24px;letter-spacing:1px}
.srcline{font-size:22px;letter-spacing:.5px;color:rgba(242,236,224,.72)}
#foot{font-size:24px;top:1614px}
.kar{font-size:48px}
.row.txt.num .v{text-align:right;font-size:48px;font-weight:900}
.rows.big .row{padding:26px 0}.rows.big .row .k{font-size:32px}.rows.big .row .k small{font-size:22px}.rows.big .row .v{font-size:64px}.rows.big .track{height:28px}.rows.big .track .bar{height:28px}
.item .t,.item .kick,.row .v,.row .k,.body,.fine,.note{text-wrap:pretty!important}

'''
page = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Bahia e Norte</title>
<link rel="stylesheet" href="fx.css"><style>{CSS}</style></head><body><div id="stage">
{"".join(H)}
<div id="grain"></div><div id="foot">@tentandochegaratevoce</div></div>
<script>window.DUR={DUR:.2f};window.VFILL=1390;</script><script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script><script src="layout.js"></script></body></html>'''
open(os.path.join(KIT, 'bahia.html'), 'w').write(page)
print('ok', DUR)
