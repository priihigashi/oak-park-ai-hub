"""Reel v5 (mitos) — Bahia e Norte (explicativo). Redesenho editorial: uma linha de alinhamento à esquerda,
sem caixas (texto direto sobre a foto escurecida), eyebrow numerado por capítulo, tabelas com filete,
fonte da informação embaixo do @, sem aviso de IA na tela. Gera ../bahia.html."""
import json, html, re, os
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open('/home/claude/work/v7/timeline.json'))
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
CH = ["MITO 1", "CAUSA", "PROVA", "MITO 2", "BAHIA", "NORTE"]
def rail(active, t=.1):
    xs = [110+i*172 for i in range(6)]
    dots = ''.join(f'<div class="st{" on" if i==active else ""}{" past" if i<active else ""}" style="left:{x}px"><i></i><b>{y}</b></div>' for i, (x, y) in enumerate(zip(xs, CH)))
    return f'<div class="rail el" data-a="fade" data-t="{t}" data-d=".3" style="left:0;top:150px"><div class="line"></div><div class="fill" style="width:{xs[active]-60}px"></div>{dots}</div>'
def scene(sid, inner, bg, src, kbo='60% 50%', kb=1.08):
    o = S[sid]
    b = f'<img class="bgimg" src="assets/bn/{bg}.jpg" data-kb="{kb}" data-kbo="{kbo}"><div class="shadeX"></div>'
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
FT = json.load(open('/home/claude/work/v7/ftop.json')) if os.path.exists('/home/claude/work/v7/ftop.json') else {}
H = []


# ---------- gráfico de linhas animado (revela da esquerda pra direita via .bar) ----------
def chart(sid, years, series, ymax, ticks, t0, dur, marks=(), w=880, h=600, lw=250, stages=None, notes=(), ymin=0):
    px0, px1, py0, py1 = 56, w - lw - 20, 14, h - 46
    def X(i): return px0 + (px1 - px0) * i / (len(years) - 1)
    def Yv(v): return py1 - (py1 - py0) * (v - ymin) / (ymax - ymin)
    grid = ''.join(f'<line x1="{px0}" x2="{px1}" y1="{Yv(v):.1f}" y2="{Yv(v):.1f}" stroke="rgba(242,236,224,.14)" stroke-width="1.5"/>'
                   f'<text x="{px0-12}" y="{Yv(v)+7:.1f}" text-anchor="end" font-family="JBM" font-weight="700" font-size="19" fill="#9F988A">{v}</text>' for v in ticks)
    lab_i = [0, len(years)//2, len(years)-1]
    grid += ''.join(f'<text x="{X(i):.1f}" y="{h-12}" text-anchor="middle" font-family="JBM" font-weight="700" font-size="19" fill="#9F988A">{years[i]}</text>' for i in lab_i)
    mk = ''
    for yr, txt, col in marks:
        i = years.index(yr)
        mk += (f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{py0}" y2="{py1}" stroke="{col}" stroke-width="2" stroke-dasharray="6 6"/>'
               f'<text x="{X(i)+10:.1f}" y="{py1-12}" font-family="JBM" font-weight="700" font-size="18" fill="{col}">{txt}</text>')
    lines = ''
    for s in series:
        pts = ' '.join(f'{X(i):.1f},{Yv(v):.1f}' for i, v in enumerate(s['v']))
        dash = ' stroke-dasharray="10 8"' if s.get('dash') else ''
        lines += f'<polyline points="{pts}" fill="none" stroke="{s["c"]}" stroke-width="{s.get("w",5)}" stroke-linejoin="round" stroke-linecap="round"{dash}/>'
        for (i, txt) in s.get('dots', []):
            lines += (f'<circle cx="{X(i):.1f}" cy="{Yv(s["v"][i]):.1f}" r="9" fill="{s["c"]}" stroke="#0b0c0e" stroke-width="3"/>'
                      f'<text x="{X(i):.1f}" y="{Yv(s["v"][i])-18:.1f}" text-anchor="middle" font-family="Rub" font-weight="900" font-size="30" fill="{s["c"]}" stroke="#0b0c0e" stroke-width="6" paint-order="stroke">{txt}</text>')
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
            + (''.join(f'<div class="bar crev" data-t="{st}" data-d="{sd}" data-to="{(X(b)+40 if b < len(years)-1 else px1+48) - (X(a) if a else 0):.0f}" style="height:{h}px;left:{X(a) if a else 0:.0f}px"><svg width="{w}" height="{h}" style="margin-left:-{X(a) if a else 0:.0f}px">{lines}</svg></div>'
                       for (a, b, st, sd) in stages) if stages else
               f'<div class="bar crev" data-t="{t0}" data-d="{dur}" data-to="{px1+12}" style="height:{h}px"><svg width="{w}" height="{h}">{lines}</svg></div>')
            + ''.join(f'<div class="clab cnote" data-a="fade" data-t="{nt:.2f}" style="left:{X(ni)+dx:.0f}px;top:{Yv(nv)+dy:.0f}px;color:{nc}">{ntx}</div>' for (ni, nv, ntx, nc, nt, dx, dy) in notes)
            + f'{labels}</div>')

def quote(txt, t, flow, gap=34, size=58):
    return f'<div class="el h quote" data-flow="{flow}" data-gap="{gap}" data-a="up" data-t="{t}" style="left:80px;width:880px;font-size:{size}px">{txt}</div>'

PFLX = ide('dir', 'EXTREMA-DIREITA')
YRS1 = [str(y) for y in range(2000, 2015)]
BA1 = [9.46,12.27,13.2,16.12,16.69,20.85,23.73,25.98,33.23,37.11,41.69,39.36,43.37,37.85,40.01]
AL1 = [26.55,29.06,34.32,35.61,35.11,39.89,53.1,59.51,60.33,59.35,66.88,71.39,64.63,65.07,62.78]
MA1 = [6.42,9.82,10.44,13.54,12.32,15.32,15.67,17.99,20.25,21.96,23.1,23.94,26.47,31.84,35.94]
BR1 = [27.35,27.86,28.53,29.14,26.94,26.13,26.61,26.2,26.72,27.18,27.8,27.45,29.41,28.55,29.82]
YRS2 = [str(y) for y in range(2014, 2022)]
CE2 = [52.31,46.75,40.63,60.2,54.0,26.2,45.2,37.0]
BA2 = [40.01,39.54,46.94,48.8,45.8,39.2,44.9,44.9]
BR2 = [29.82,28.89,30.33,31.6,27.8,22.7,23.6,22.3]

s = 'v01'; CUR['s'] = s
H.append(scene(s, f'''
{eb(0, f'BAHIA · PT {ESQ} DESDE 2007', top=330)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'mais',0,-.15)}" data-shake="1" style="left:80px;width:880px;font-size:118px;color:#fff">ONDE MAIS SE <span class="hl">MATA</span> NO BRASIL</div>
<div class="el h redtxt" data-flow="m:3" data-gap="30" data-a="slam" data-t="{W(s,'culpa',0,-.1)}" data-d=".35" style="left:80px;font-size:96px;width:880px">E A CULPA É DA ESQUERDA.</div>
<div class="el body" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'vamos',0,-.2)}" style="left:80px;width:820px"><b>Vamos aos fatos.</b></div>
''', 'i01', 'FBSP, ANUÁRIO 2026 · ' + IDS, kbo='70% 70%'))

s = 'v02'; CUR['s'] = s
c1 = chart(s, YRS1, [
    dict(n='ALAGOAS', sub=f'PSDB {DIR}', v=AL1, c=R, lt=W(s,'alagoas',0,-.1), dots=[(11, '71,4')]),
    dict(n='BAHIA', sub=f'PFL {PFLX}<br>→ PT {ESQ}', v=BA1, c=Y, w=7, lt=W(s,'bahia',0,-.1), ly=-8),
    dict(n='MARANHÃO', sub=f'PMDB {DIR}', v=MA1, c='#fff', lt=W(s,'maranhão',0,-.1), ly=14),
    dict(n='BRASIL', v=BR1, c='rgba(242,236,224,.55)', dash=True, w=4, lt=W(s,'olha',0,.6), ly=24),
], 80, [0, 25, 50, 75], W(s,'olha',0,-.1), 4.2, marks=[('2007', 'PT ASSUME A BAHIA', Y)]).replace('{flow}', 'm:3')
H.append(scene(s, rail(0)+f'''
{eb(1, 'MITO 1 · HOMICÍDIOS POR 100 MIL', top=300)}
{quote('“A ESQUERDA CAUSOU A VIOLÊNCIA.”', W(s,'mito',0), 'm:2', gap=26)}
{c1}
<div class="el stamp-r" data-flow="m:4" data-gap="36" data-a="stamp" data-t="{W(s,'mesmo',0,-.05)}" data-d=".35" data-r="-2" style="left:80px;white-space:nowrap;font-size:46px">OS DADOS NÃO SUSTENTAM</div>
''', 'i04', 'IPEA/FBSP, ATLAS DA VIOLÊNCIA (SIM/DATASUS) · ' + IDS, kbo='50% 70%'))

s = 'v03'; CUR['s'] = s
H.append(scene(s, rail(1)+f'''
{eb(2, 'O QUE MUDOU FOI O CRIME', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t="{W(s,'pcc',0,-.2)}" style="left:80px">
  {row('PCC E CV', 'SAEM DO SUDESTE ATRÁS DE ROTAS E PORTOS', None, '#fff', 0)}
  {row('PRESÍDIOS', 'VIRAM CENTRO DE RECRUTAMENTO', None, '#fff', 0, fade=W(s,'recrutaram',0,-.2))}
  {row('2015', 'NASCE O BDM, NA BAHIA', None, Y, 0, fade=W(s,'recrutaram',0,.6))}</div>
<div class="el h" data-flow="m:3" data-gap="50" data-a="slam" data-t="{W(s,'nordestinação',0,-.2)}" style="left:80px;width:880px;font-size:76px;color:{Y}">A “NORDESTINAÇÃO” DA VIOLÊNCIA.</div>
<div class="el note" data-flow="m:4" data-gap="22" data-a="fade" data-t="{W(s,'nordestinação',0,.3)}" style="left:80px">TERMO USADO POR PESQUISADORES DA SEGURANÇA PÚBLICA NO NORDESTE</div>
''', 'i10', 'REV. BRAS. DE SEGURANÇA PÚBLICA, 2024 · FÓRUM POPULAR DE SEG. PÚBLICA DO NE, 2019', kbo='60% 55%'))

s = 'v04'; CUR['s'] = s
c2 = chart(s, YRS2, [
    dict(n='CEARÁ', sub=f'MESMO GOVERNADOR · PT {ESQ}', v=CE2, c=R, w=7, lt=W(s,'ceará',0,-.1), dots=[(3, '60'), (5, '26'), (6, '45')]),
    dict(n='BAHIA', v=BA2, c=Y, lt=W(s,'prova',0,.5), ly=-6),
    dict(n='BRASIL', v=BR2, c='rgba(242,236,224,.55)', dash=True, w=4, lt=W(s,'prova',0,.5), ly=4),
], 70, [0, 20, 40, 60], W(s,'prova',0), 3.0, marks=[('2017', 'GUERRA DE FACÇÕES', '#fff')]).replace('{flow}', 'm:2')
H.append(scene(s, rail(2)+f'''
{eb(3, 'A PROVA · HOMICÍDIOS POR 100 MIL', top=320)}
{c2}
<div class="el body" data-flow="m:3" data-gap="36" data-a="up" data-t="{W(s,'ritmo',0,-.2)}" style="left:80px;width:860px">O que move a curva: <b>tréguas e guerras entre facções.</b></div>
''', 'i05', 'IPEA/FBSP, ATLAS DA VIOLÊNCIA · FBSP, 2021 (MOTIM DA PM E GUERRA CV × GDE NO CE)', kbo='50% 70%'))

s = 'v05'; CUR['s'] = s
H.append(scene(s, rail(2)+f'''
{eb(4, 'NORDESTE · MORTES VIOLENTAS POR 100 MIL · 2025', top=320)}
<div class="el rows" data-flow="m:2" data-gap="40" data-a="fade" data-t="{W(s,'esquerda',0,-.3)}" style="left:80px">
  {row(f'ESQUERDA', '28,7', 28.7/29.4, R, W(s,'esquerda',0), sub=f'BA · CE · PI · RN · PT {ESQ}<br>MA · PB · PSB {CESQ}')}
  {row(f'DIREITA', '29,4', 1, '#5B7CFF', W(s,'direita',0), sub=f'AL · MDB {DIR}<br>PE · SE · PSD {DIR}')}
  {row('BRASIL', '19,1', 19.1/29.4, 'rgba(242,236,224,.45)', W(s,'direita',0,.4))}</div>
<div class="el note" data-flow="m:3" data-gap="16" data-a="fade" data-t="{W(s,'direita',0,.3)}" style="left:80px">MÉDIA SIMPLES DOS ESTADOS · CÁLCULO NOSSO COM DADOS DO FBSP</div>
<div class="el h" data-flow="m:4" data-gap="54" data-a="slam" data-t="{W(s,'mesmo',0,-.1)}" style="left:80px;width:880px;font-size:96px;color:{Y}">MESMO PATAMAR.</div>
''', 'i09', 'FBSP, ANUÁRIO 2026 · ' + IDS, kbo='70% 60%'))

s = 'v06'; CUR['s'] = s
H.append(scene(s, rail(3)+f'''
{eb(5, 'MITO 2', top=300)}
{quote('“ENTÃO O GOVERNO NÃO TEM CULPA.”', W(s,'mito',0), 'm:2', gap=26)}
<div class="el stamp-r" data-flow="m:3" data-gap="30" data-a="stamp" data-t="{W(s,'também',0,-.05)}" data-d=".35" data-r="-2" style="left:80px;white-space:nowrap;font-size:46px">TAMBÉM NÃO</div>
<div class="el rows" data-flow="m:4" data-gap="44" data-a="fade" data-t="{W(s,'pernambuco',0,-.3)}" style="left:80px">
  {row('PERNAMBUCO', '52,2 → 33,9', None, '#fff', 0, sub=f'2007–2013 · PSB {CESQ}')}
  {row('PARAÍBA', '42,6 → 23,4', None, '#fff', 0, sub=f'2011–2019 · PSB {CESQ}', fade=W(s,'paraíba',0,-.2))}
  {row('PARÁ', '56,6 → 29,5', None, '#fff', 0, sub=f'2018–2024 · MDB {DIR}', fade=W(s,'pará',0,-.2))}</div>
<div class="el note" data-flow="m:5" data-gap="22" data-a="fade" data-t="{W(s,'pará',0,.3)}" style="left:80px">POR 100 MIL · HOMICÍDIOS (PE, PB) E MORTES VIOLENTAS (PA)</div>
''', 'i03', 'ATLAS DA VIOLÊNCIA · FBSP (GAZETA DO POVO, 2019) · FBSP, ANUÁRIO 2025 · ' + IDS, kbo='40% 55%'))

s = 'v07'; CUR['s'] = s
YPE = [str(y) for y in range(2004, 2014)]
PE = [49.2, 50.2, 51.7, 52.2, 50.2, 44.4, 38.3, 38.2, 36.3, 33.9]
c7 = chart(s, YPE, [
    dict(n='PERNAMBUCO', sub=f'PSB {CESQ}', v=PE, c=Y, w=7, lt=W(s,'pernambuco',0), dots=[(3, '52,2'), (9, '33,9')]),
], 60, [20, 30, 40, 50, 60], 0, 0, h=500, ymin=20, marks=[('2007', 'PACTO PELA VIDA', '#fff')],
   stages=[(0, 3, W(s,'vinha',0,-.1), 2.2), (3, 4, W(s,'primeiro',0,-.1), 1.6), (4, 9, W(s,'depois',0,-.1), 2.4)],
   notes=[(0, 49.2, '↗ SUBINDO', '#fff', W(s,'subindo',0,-.2), 4, 26),
          (3, 30, '1 ANO PARA<br>MONTAR', '#fff', W(s,'primeiro',0,.2), 14, 0),
          (6, 46, '↘ 6 ANOS EM QUEDA', Y, W(s,'seis',0,-.2), 0, 0)]).replace('{flow}', 'm:3')
H.append(scene(s, rail(3)+f'''
{eb(6, 'POR QUE FUNCIONOU · HOMICÍDIOS POR 100 MIL', top=300)}
<div class="el h" data-flow="m:2" data-gap="28" data-a="slam" data-t="{W(s,'governador',0,-.15)}" style="left:80px;width:880px;font-size:64px;color:#fff;white-space:nowrap">O GOVERNADOR <span class="hl">NO COMANDO</span></div>
{c7}
<div class="el h" data-flow="m:4" data-gap="30" data-a="up" data-t="{W(s,'pico',0,-.25)}" style="left:80px;width:880px;font-size:54px;color:#fff">NÃO OLHE SÓ O PICO.<br><span class="hl">OLHE A DIREÇÃO.</span></div>
<div class="el note" data-flow="m:5" data-gap="26" data-a="fade" data-t="{W(s,'pará',0,-.2)}" style="left:80px">PARÁ (TERPAZ): OBRAS E SERVIÇOS NOS BAIRROS, JUNTO COM A POLÍCIA. A PARAÍBA USOU O MODELO DE PERNAMBUCO.</div>
''', 'i12', 'IPEA/FBSP, ATLAS DA VIOLÊNCIA 2016 · INSTITUTO IGARAPÉ (RATTON ET AL., 2014)', kbo='50% 60%'))

s = 'v08'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(7, 'BAHIA · FALHA 1: INVESTIGAÇÃO', top=320)}
<div class="el h cnt" data-flow="m:2" data-gap="30" data-t="{W(s,'treze',0,-.15)}" data-d=".9" data-from="0" data-to="13" data-dec="0" data-suf="%" style="left:72px;font-size:260px;color:{R};width:880px;line-height:.82;height:214px"></div>
<div class="el body" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'homicídios',0,-.1)}" style="left:80px;width:860px">dos homicídios de 2023 foram esclarecidos até o fim de 2024. <b>Pior índice do país.</b></div>
<div class="el rows" data-flow="m:4" data-gap="40" data-a="fade" data-t="{W(s,'pior',0,-.3)}" style="left:80px">
  {row('BAHIA', '13%', 13/36, R, W(s,'pior',0))}
  {row('BRASIL', '36%', 1, WH, W(s,'pior',0,.2))}</div>
''', 'i06', 'INSTITUTO SOU DA PAZ, ONDE MORA A IMPUNIDADE (OUT/2025)', kbo='60% 55%'))

s = 'v09'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(8, 'BAHIA · FALHA 2: A POLÍCIA', top=320)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'mais',0,-.15)}" data-shake="1" style="left:80px;width:880px;font-size:92px;color:#fff">A QUE <span class="hl">MAIS MATA</span> NO BRASIL</div>
<div class="el rows" data-flow="m:3" data-gap="36" data-a="fade" data-t="{W(s,'três',0,-.2)}" style="left:80px">
  {row('AÇÃO POLICIAL', '28,7%', .287/.35, R, W(s,'três',0), sub='DAS MORTES VIOLENTAS DA BA, 2025')}</div>
<div class="el pull" data-flow="m:4" data-gap="44" data-a="up" data-t="{W(s,'pesquisadores',0,-.2)}" style="left:80px;width:880px">“Não há a produção de um novo modelo de polícia.”<small>FELIPE FREITAS, PESQUISADOR (FGV) · PONTE, 2022</small></div>
''', 'i07', 'FBSP, ANUÁRIO 2026 · PONTE JORNALISMO (MAR/2022)', kbo='70% 55%'))

s = 'v10'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(9, 'O QUE O GOVERNO TENTOU', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t=".2" style="left:80px">
  {row('2011', 'PACTO PELA VIDA · METAS POR TERRITÓRIO', None, '#fff', 0)}
  {row('2024', 'BAHIA PELA PAZ · ASSISTÊNCIA NOS BAIRROS', None, '#fff', 0, fade=W(s,'bahia',0,-.2))}</div>
<div class="el rows" data-flow="m:3" data-gap="44" data-a="fade" data-t="{W(s,'três',0,-.2)}" style="left:80px">
  {row('2023', '−6,0%', 6.0/9.6, Y, W(s,'três',0), sub='QUEDA NAS MORTES VIOLENTAS')}
  {row('2024', '−8,2%', 8.2/9.6, Y, W(s,'queda',0))}
  {row('2025', '−9,6%', 1, Y, W(s,'aumenta',0))}</div>
<div class="el body" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'sinal',0,-.2)}" style="left:80px;width:860px">A queda <b>aumenta a cada ano</b>: sinal de que a medida começa a pegar.</div>
<div class="el h redtxt" data-flow="m:5" data-gap="34" data-a="slam" data-t="{W(s,'devagar',0,-.1)}" style="left:80px;font-size:84px">MAS AINDA DEVAGAR.</div>
''', 'i02', 'GOVERNO DA BAHIA · SSP-BA (2023–2024) · FBSP, ANUÁRIO 2026', kbo='60% 55%'))

s = 'v11'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(10, 'E CORRUPÇÃO? O QUE TEM PROCESSO', top=320)}
<div class="el items" data-flow="m:2" data-gap="40" style="left:80px">
  {item('PMs · OPERAÇÃO FOGO AMIGO (PF + MP-BA, 2024)', '10 presos por vender armas a facção.', W(s,'dez',0,-.2))}
  {item('RUI COSTA · RESPIRADORES (R$ 48,7 MI, NADA ENTREGUE)', 'TCU arquivou. Inquérito segue sem acusação.', W(s,'respiradores',0,-.2))}</div>
''', 'i08', 'PF · CORREIO, 2024 · TCU, 2025 · CORREIO DA MANHÃ, JUN/2026', kbo='50% 80%'))

s = 'v12'; CUR['s'] = s
H.append(scene(s, rail(5)+f'''
{eb(11, 'NORTE · A MESMA LÓGICA', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t="{W(s,'amapá',0,-.2)}" style="left:80px">
  {row('AMAPÁ', '42,5 · 1º', None, '#fff', 0, sub=f'MORTES / 100 MIL · SOLIDARIEDADE {CDIR}')}
  {row('LETALIDADE POLICIAL', '17,1 · 1º', None, R, 0, fade=W(s,'letal',0,-.1))}</div>
<div class="el h" data-flow="m:3" data-gap="56" data-a="slam" data-t="{W(s,'marajó',0,-.15)}" style="left:80px;font-size:96px;color:#fff">MARAJÓ (PA)</div>
<div class="el rows" data-flow="m:4" data-gap="26" data-a="fade" data-t="{W(s,'sete',0,-.2)}" style="left:80px">
  {row('MARAJÓ', '73%', 1, R, W(s,'sete',0), sub='EM SITUAÇÃO DE POBREZA (CADÚNICO)')}
  {row('BRASIL', '28%', 28/73, WH, W(s,'sete',0,.2))}</div>
<div class="el note" data-flow="m:5" data-gap="22" data-a="fade" data-t="{W(s,'rede',0,-.1)}" style="left:80px">COMUNIDADES ISOLADAS POR RIOS, LONGE DA REDE DE PROTEÇÃO</div>
''', 'i11', 'FBSP, ANUÁRIO 2026 · RELATÓRIO CIDADANIA MARAJÓ (DEZ/2022) · CNMP, 2026', kbo='50% 60%'))

s = 'v13'; CUR['s'] = s
H.append(scene(s, f'''
{eb(12, 'O QUE RESOLVE DE VEZ: PREVENÇÃO', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t="{W(s,'estudos',0,-.2)}" style="left:80px">
  {row('BOLSA FAMÍLIA', '+1% → −0,3%', None, Y, 0, sub='COBERTURA → HOMICÍDIOS · PLOS ONE, 2018')}
  {row('EDUCAÇÃO', '+1 PONTO → −25%', None, Y, 0, sub='INDICADOR → HOMICÍDIOS · INSPER, 2022')}</div>
<div class="el note" data-flow="m:3" data-gap="18" data-a="fade" data-t="{W(s,'homicídio',0,-.2)}" style="left:80px">ASSOCIAÇÃO, NÃO PROVA DE CAUSA</div>
<div class="el h" data-flow="m:4" data-gap="50" data-a="slam" data-t="{W(s,'quarto',0,-.15)}" style="left:80px;width:880px;font-size:84px;color:#fff">BAHIA: 4º ESTADO EM <span class="hl">TEMPO INTEGRAL</span></div>
<div class="el body" data-flow="m:5" data-gap="24" data-a="up" data-t="{W(s,'efeito',0,-.2)}" style="left:80px;width:860px"><b>140 mil alunos</b>, 34% da rede estadual. <b>O efeito leva anos.</b></div>
''', 'i14', 'PLOS ONE (MACHADO ET AL., 2018) · INSPER/INST. NATURA, 2022 · MEC, CENSO ESCOLAR 2025', kbo='60% 55%'))

s = 'v14'; CUR['s'] = s
H.append(scene(s, f'''
{eb(0, 'RESUMINDO', top=300)}
<div class="el h" data-flow="m:2" data-gap="30" data-a="up" data-t="{W(s,'região',0,-.2)}" style="left:80px;width:880px;font-size:76px;color:#fff">REGIÃO E FACÇÕES <span style="color:{Y}">EXPLICAM O NÍVEL.</span></div>
<div class="el h" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'governo',0,-.2)}" style="left:80px;width:880px;font-size:76px;color:#fff">O GOVERNO <span style="color:{R}">EXPLICA A DIFERENÇA.</span></div>
<div class="el repost" data-flow="m:4" data-gap="56" data-a="slam" data-t="{W(s,'você',0,-.15)}" data-shake="1" style="left:80px;width:880px;font-size:58px">O QUE VOCÊ COBRARIA DO PRÓXIMO MANDATO?<small>Jerônimo foi reeleito em 04/10/2026 (2027–2030)</small></div>
''', 'i13', 'TSE · IPEA · FBSP · SOU DA PAZ · IGARAPÉ · RBSP', kbo='50% 60%'))

CSS = open(os.path.join(KIT, 'preview_kit/style.css')).read() + '''
.shadeX{position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,7,9,.9) 0%,rgba(6,7,9,.72) 48%,rgba(6,7,9,.42) 100%),linear-gradient(180deg,rgba(6,7,9,.75) 0%,rgba(6,7,9,0) 22%,rgba(6,7,9,0) 58%,rgba(6,7,9,.96) 80%)}
.eyebrow{display:flex;align-items:center;gap:14px;font-family:JBM;font-weight:700;font-size:24px;letter-spacing:3px;color:#FFD34D;text-transform:uppercase;white-space:nowrap}
.eyebrow::before{content:"";width:40px;height:4px;border-radius:2px;background:#FFD34D}
.eyebrow b{font-family:Rub;font-weight:900;font-size:26px;color:#F2ECE0;letter-spacing:0}
.eyebrow .ide{font-size:19px;padding:2px 9px;letter-spacing:1px}
.body{font-family:Rub;font-weight:500;font-size:40px;line-height:1.22;color:#E9E4D8;text-shadow:0 2px 14px rgba(0,0,0,.6);text-wrap:pretty}
.body b{font-weight:800;color:#fff}
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

.chart{position:absolute}.chart svg{position:absolute;left:0;top:0;overflow:visible}
.crev{position:absolute;left:0;top:0;overflow:hidden;width:0}
.cnote{font-size:20px;line-height:1.25}
.clab{position:absolute;font-family:JBM;font-weight:700;font-size:22px;letter-spacing:1.5px;white-space:nowrap;line-height:1.2;text-shadow:0 2px 10px rgba(0,0,0,.8)}
.clab small{display:block;font-size:15px;line-height:1.6;letter-spacing:.5px;color:#BDB6A6;margin-top:4px}.clab small .ide{font-size:13px;padding:1px 6px}
.quote{color:#F2ECE0;font-weight:800;text-shadow:0 3px 18px rgba(0,0,0,.6)}
.pull{font-family:Rub;font-weight:700;font-style:italic;font-size:50px;line-height:1.15;color:#fff;padding-left:30px;border-left:6px solid #FFD34D;text-shadow:0 3px 16px rgba(0,0,0,.6)}
.pull small{display:block;font-family:JBM;font-style:normal;font-weight:700;font-size:20px;letter-spacing:1.5px;color:#BDB6A6;margin-top:16px}
'''
page = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Bahia e Norte</title>
<link rel="stylesheet" href="fx.css"><style>{CSS}</style></head><body><div id="stage">
{"".join(H)}
<div id="grain"></div><div id="foot">@tentandochegaratevoce</div></div>
<script>window.DUR={DUR:.2f};</script><script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script><script src="layout.js"></script></body></html>'''
open(os.path.join(KIT, 'bahia.html'), 'w').write(page)
print('ok', DUR)
