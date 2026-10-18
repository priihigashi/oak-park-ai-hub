"""Reel São Paulo — culpa da esquerda? (timeline jornalística, mesmo kit do reel da Bahia v10). Redesenho editorial: uma linha de alinhamento à esquerda,
sem caixas (texto direto sobre a foto escurecida), eyebrow numerado por capítulo, tabelas com filete,
fonte da informação embaixo do @, sem aviso de IA na tela. Gera ../bahia.html."""
import json, html, re, os
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(KIT, 'data/sp/timeline.json')))
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
CH = ["QUEM MANDA", "MITO", "FACÇÃO", "POLÍCIA", "SEM RESPOSTA", "RUA"]
def rail(active, t=.1):
    xs = [110+i*172 for i in range(6)]
    dots = ''.join(f'<div class="st{" on" if i==active else ""}{" past" if i<active else ""}" style="left:{x}px"><i></i><b>{y}</b></div>' for i, (x, y) in enumerate(zip(xs, CH)))
    return f'<div class="rail el" data-a="fade" data-t="{t}" data-d=".3" style="left:0;top:150px"><div class="line"></div><div class="fill" style="width:{xs[active]-60}px"></div>{dots}</div>'
def scene(sid, inner, bg, src, kbo='60% 50%', kb=1.08):
    o = S[sid]
    b = f'<img class="bgimg" src="assets/sp/{bg}.jpg" data-kb="{kb}" data-kbo="{kbo}"><div class="shadeX"></div>' + ('<div style="position:absolute;inset:0;background:rgba(6,7,9,.6)"></div>' if bg in DIM else '')
    s = f'<div class="el srcline" data-a="fade" data-t=".4" style="left:130px;top:1640px;width:820px">FONTE: {src}</div>'
    return f'<section class="scene" data-s="{o["s"]}" data-e="{o["e"]}" data-in="cut" data-theme="dark">{b}<div class="safe">{inner}</div>{kar(sid)}{s}</section>\n'
CUR = {'s': None}
DIM = {'pm2'}
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
FT = json.load(open(os.path.join(KIT, 'data/sp/ftop.json'))) if os.path.exists(os.path.join(KIT, 'data/sp/ftop.json')) else {}
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
        dash = ' stroke-dasharray="10 8"' if s.get('dash') else ''
        segs = [[]]
        for i, v in enumerate(s['v']):
            if v is None: segs.append([])
            else: segs[-1].append(f'{X(i):.1f},{Yv(v):.1f}')
        for sg in segs:
            if len(sg) > 1:
                lines += f'<polyline points="{" ".join(sg)}" fill="none" stroke="{s["c"]}" stroke-width="{s.get("w",5)}" stroke-linejoin="round" stroke-linecap="round"{dash}/>'
        for (i, txt) in s.get('dots', []):
            lines += (f'<circle cx="{X(i):.1f}" cy="{Yv(s["v"][i]):.1f}" r="9" fill="{s["c"]}" stroke="#0b0c0e" stroke-width="3"/>'
                      f'<text x="{X(i):.1f}" y="{Yv(s["v"][i])-18:.1f}" text-anchor="middle" font-family="Rub" font-weight="900" font-size="30" fill="{s["c"]}" stroke="#0b0c0e" stroke-width="6" paint-order="stroke">{txt}</text>')
    labels = ''
    # posições dos rótulos sem colisão: ordena pela altura e garante espaço mínimo
    want = sorted([(Yv(s['v'][-1]), i) for i, s in enumerate(series) if not s.get('nolab')])
    pos = {}; last = -1e9
    for y, i in want:
        sb_ = series[i].get('sub'); hgt = 34 + (28 * (sb_.count('<br>') + 1) if sb_ else 0)
        y = max(y, last); pos[i] = y; last = y + hgt + 8
    for i, s in enumerate(series):
        if s.get('nolab'): continue
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
EXT = PFLX
AT = json.load(open(os.path.join(KIT, 'data/sp/atlas_sp.json')))
YA = [str(y) for y in AT['anos']]; i10 = YA.index('2010'); iL = len(YA)-1
YM = [str(y) for y in range(2014, 2026)]
MDIP = [879, 832, 857, 940, 851, 867, 814, 570, 419, 504, 813, 835]

def g(v): return f'{v:.1f}'.replace('.', ',')

s = 's01'; CUR['s'] = s
MZ = json.load(open(os.path.join(KIT, 'data/sp/mapa_br.json')))
bx = MZ['sp_box']; cxs, cys = (bx[0]+bx[2])/2, (bx[1]+bx[3])/2
zk = f"0,.31,1620,1620,540,1060; .45,.31,1620,1620,540,1060; 2.7,1.3,{cxs:.0f},{cys:.0f},560,1210; {S[s]['e']-S[s]['s']:.2f},1.42,{cxs:.0f},{cys:.0f},560,1210"
o = S[s]
H.append(f'''<section class="scene" data-s="{o["s"]}" data-e="{o["e"]}" data-in="cut" data-theme="dark">
<div class="zoomer" data-z="{zk}" style="position:absolute;left:0;top:0;width:3240px;height:3240px;transform-origin:0 0"><img src="assets/sp/mapa_br.jpg" style="width:3240px;height:3240px;display:block"></div>
<div class="shadeMap"></div>
<div class="safe">
{eb(0, 'SÃO PAULO · O ESTADO MAIS POPULOSO', top=330)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'celular',0,-.15)}" data-shake="1" style="left:80px;width:880px;font-size:88px;color:#fff">CELULAR ROUBADO E <span class="hl">CRIME NA FARIA LIMA</span></div>
<div class="el h redtxt" data-flow="m:3" data-gap="30" data-a="slam" data-t="{W(s,'culpa',0,-.1)}" data-d=".35" style="left:80px;font-size:96px;width:880px">E A CULPA É DA ESQUERDA.</div>
<div class="el body" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'vamos',0,-.2)}" style="left:80px;width:820px"><b>Vamos aos fatos.</b></div>
</div>{kar(s)}<div class="el srcline" data-a="fade" data-t=".4" style="left:130px;top:1640px;width:820px">FONTE: FBSP, ANUÁRIO 2026 · RECEITA FEDERAL E MP-SP (CARBONO OCULTO, 2025) · MAPA: IBGE</div></section>
''')

s = 's02'; CUR['s'] = s
H.append(scene(s, rail(0)+f'''
{eb(1, 'QUEM MANDA NA POLÍCIA', top=300)}
<div class="el h" data-flow="m:2" data-gap="30" data-a="slam" data-t="{W(s,'governador',0,-.15)}" style="left:80px;width:880px;font-size:72px;color:#fff">QUEM MANDA NA POLÍCIA É <span class="hl">O GOVERNADOR.</span></div>
<div class="el rows" data-flow="m:3" data-gap="36" data-a="fade" data-t="{W(s,'desde',0,-.2)}" style="left:80px">
  {row('1995–2006', 'COVAS · ALCKMIN · LEMBO', None, '#fff', 0, sub=f'PSDB {DIR} · PFL {PFLX}')}
  {row('2007–2018', 'SERRA · ALCKMIN (2 MANDATOS)', None, '#fff', 0, sub=f'PSDB {DIR}', fade=W(s,'psdb',0,-.1))}
  {row('2019–2022', 'DORIA · RODRIGO GARCIA', None, '#fff', 0, sub=f'PSDB {DIR}', fade=W(s,'psdb',0,.3))}
  {row('2023–2030', 'TARCÍSIO (2 MANDATOS)', None, Y, 0, sub=f'REPUBLICANOS {DIR}', fade=W(s,'republicanos',0,-.2))}</div>
<div class="el body" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'esquerda',0,-.2)}" style="left:80px;width:860px">A esquerda só teve <b>a prefeitura da capital e o governo federal.</b></div>
<div class="el fine" data-flow="m:5" data-gap="22" data-a="fade" data-t="{W(s,'esquerda',0,.5)}" style="left:80px">MÁRCIO FRANÇA (PSB {CESQ}) GOVERNOU 9 MESES EM 2018, COMO VICE QUE ASSUMIU. POLÍCIAS CIVIL E MILITAR E PRESÍDIOS SÃO DO ESTADO (CONSTITUIÇÃO, ART. 144).</div>
''', 'bandeirantes', 'TSE · GOVERNO DE SP · ' + IDS, kbo='50% 55%'))

s = 's03'; CUR['s'] = s
c3 = chart(s, YA, [
    dict(n='', v=AT['sp_a'], c=Y, w=7, nolab=True, dots=[(0, '28,2'), (i10, '13,7')]),
    dict(n='SÃO PAULO', sub=f'PSDB {DIR}<br>→ REPUBLICANOS {DIR}', v=AT['sp_b'], c=Y, w=7, lt=W(s,'depois',0), dots=[(iL, '6,6')]),
    dict(n='', v=AT['br_a'], c='rgba(242,236,224,.55)', dash=True, w=4, nolab=True),
    dict(n='BRASIL', v=AT['br_b'], c='rgba(242,236,224,.55)', dash=True, w=4, lt=W(s,'olha',0,.3)),
], 40, [0, 10, 20, 30, 40], 0, 0,
   stages=[(0, i10, W(s,'cai',0,-.1), 2.4), (i10, iL, W(s,'depois',0,-.1), 2.6)],
   notes=[(0, 37, '2000: 42,2 · O PICO', '#fff', W(s,'pico',0,-.3), 0, -10),
          (2, 24, '↘ 10 ANOS EM QUEDA', Y, W(s,'dez',0,-.2), 10, 0)]).replace('{flow}', 'm:3')
H.append(scene(s, rail(1)+f'''
{eb(2, 'MITO 1 · HOMICÍDIOS POR 100 MIL', top=300)}
{quote('“A DIREITA RESOLVEU.”', W(s,'mito',0), 'm:2', gap=26)}
{c3}
<div class="el body" data-flow="m:4" data-gap="24" data-a="up" data-t="{W(s,'estatuto',0,-.2)}" style="left:80px;width:900px;font-size:38px">+ AJUDA FEDERAL: <b class="hl">ESTATUTO DO DESARMAMENTO</b>, 2003, sancionado pelo presidente 🦑 · <b>464 mil armas</b> recolhidas</div>
<div class="el stamp-r" data-flow="m:5" data-gap="30" data-a="stamp" data-t="{W(s,'nenhum',0,-.05)}" data-d=".35" data-r="-2" style="left:80px;white-space:nowrap;font-size:44px">NENHUM GOVERNO FEZ SOZINHO</div>
<div class="el fine" data-flow="m:6" data-gap="22" data-a="fade" data-t="{W(s,'funcionou',0,-.1)}" style="left:80px">QUEDA ATRAVESSA COVAS, ALCKMIN, SERRA, DORIA E TARCÍSIO. ESTATUTO: BRASIL 28,9 (2003) → 25,8 (2005), MAPA DA VIOLÊNCIA; A DIREITA DIZ QUE A CAUSA NÃO ESTÁ PROVADA. ATLAS: EDIÇÕES 2016 E 2024/26, LINHA SEPARADA.</div>
''', 'skyline', 'IPEA/FBSP, ATLAS DA VIOLÊNCIA (SIM/DATASUS) · ' + IDS, kbo='50% 60%'))

s = 's04'; CUR['s'] = s
H.append(scene(s, rail(2)+f'''
{eb(3, 'O LADO ESCURO DA QUEDA', top=320)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'pcc',0,-.15)}" style="left:80px;width:880px;font-size:80px;color:#fff">1993: <span class="hl">O PCC NASCE</span> NUM PRESÍDIO PAULISTA</div>
<div class="el body" data-flow="m:3" data-gap="40" data-a="up" data-t="{W(s,'pesquisadores',0,-.2)}" style="left:80px;width:860px">Pesquisadores dizem que a facção <b>proíbe mortes sem autorização.</b></div>
<div class="el h redtxt" data-flow="m:4" data-gap="40" data-a="slam" data-t="{W(s,'menos',0,-.1)}" style="left:80px;width:880px;font-size:72px">MENOS HOMICÍDIO, FACÇÃO MAIS RICA.</div>
<div class="el fine" data-flow="m:5" data-gap="24" data-a="fade" data-t="{W(s,'rica',0,.2)}" style="left:80px">HIPÓTESE DEBATIDA (NEV-USP, CAMBRIDGE). UM ESTUDO DA UNICAMP NÃO ACHOU EVIDÊNCIA ESTATÍSTICA. PRESÍDIO É RESPONSABILIDADE DO ESTADO.</div>
''', 'se', 'C. NUNES DIAS (NEV-USP) · G. WILLIS (CAMBRIDGE) · UNICAMP, TD 276', kbo='50% 50%'))

s = 's05'; CUR['s'] = s
H.append(scene(s, rail(2)+f'''
{eb(4, 'PROBLEMA 1 · O PCC VIROU EMPRESA', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t="{W(s,'operação',0,-.3)}" style="left:80px">
  {row('CARBONO OCULTO<small>AGO/2025</small>', 'POSTOS DE COMBUSTÍVEL E FINTECHS · 42 ALVOS NA FARIA LIMA', None, '#fff', 0)}</div>
<div class="el h" data-flow="m:3" data-gap="40" data-a="slam" data-t="{W(s,'oito',0,-.15)}" style="left:80px;width:880px;font-size:96px;color:{Y}">R$ 8,67 BILHÕES</div>
<div class="el note" data-flow="m:4" data-gap="14" data-a="fade" data-t="{W(s,'pagos',0,-.2)}" style="left:80px">EM IMPOSTOS NÃO PAGOS · ESTIMATIVA DA RECEITA FEDERAL</div>
<div class="el rows" data-flow="m:5" data-gap="40" data-a="fade" data-t="{W(s,'ônibus',0,-.3)}" style="left:80px">
  {row('FIM DA LINHA<small>ABR/2024</small>', 'ÔNIBUS PAGOS PELA PREFEITURA SOB SUSPEITA DE LAVAR DINHEIRO DA FACÇÃO', None, '#fff', 0)}</div>
<div class="el fine" data-flow="m:6" data-gap="22" data-a="fade" data-t="{W(s,'facção',0,.2)}" style="left:80px">CARBONO OCULTO = MP-SP + RECEITA FEDERAL (A PF FEZ AS OPERAÇÕES QUASAR E TANK). A REGRA DA RECEITA QUE APERTAVA AS FINTECHS FOI REVOGADA EM JAN/2025, APÓS VÍDEOS VIRAIS, E REEDITADA DEPOIS DA OPERAÇÃO.</div>
''', 'farialima', 'RECEITA FEDERAL E MP-SP, AGO/2025 · MP-SP, OPERAÇÃO FIM DA LINHA', kbo='55% 50%'))

s = 's06'; CUR['s'] = s
H.append(scene(s, rail(2)+f'''
{eb(5, 'POLÍTICOS DOS DOIS LADOS · ÔNIBUS DA CAPITAL', top=300)}
<div class="el rows" data-flow="m:2" data-gap="30" data-a="fade" data-t="{W(s,'vereador',0,-.3)}" style="left:80px">
  {row('JUN/2026', 'SENIVAL MOURA · VEREADOR', None, '#fff', 0, sub=f'PT {ESQ} · SOLTO POR HC')}
  {row('SET/2026', 'MILTON LEITE · EX-PRES. DA CÂMARA', None, '#fff', 0, sub=f'UNIÃO BRASIL {DIR}', fade=W(s,'setembro',0,-.2))}
  {row('SET/2026', 'DANILO MORGADO · CANDIDATO', None, '#fff', 0, sub=f'PL {EXT}', fade=W(s,'candidato',0,-.2))}</div>
<div class="el stamp-r" data-flow="m:3" data-gap="30" data-a="stamp" data-t="{W(s,'negam',0,-.1)}" data-d=".35" data-r="-2" style="left:80px;white-space:nowrap;font-size:42px">TODOS NEGAM</div>
<div class="el eyebrow" data-flow="m:4" data-gap="44" data-a="left" data-t="{W(s,'investigadas',0,-.2)}" style="left:80px">COMO ENTRARAM NA PREFEITURA</div>
<div class="el rows" data-flow="m:5" data-gap="18" data-a="fade" data-t="{W(s,'perueiros',0,-.3)}" style="left:80px">
  {row('2003', 'PERUEIROS VIRAM COOPERATIVAS OFICIAIS', None, '#fff', 0, sub=f'GESTÃO MARTA · PT {ESQ}')}
  {row('2019', 'AS MESMAS EMPRESAS GANHAM A NOVA LICITAÇÃO', None, '#fff', 0, sub=f'GESTÃO COVAS · PSDB {DIR}', fade=W(s,'licitação',0,-.2))}</div>
<div class="el fine" data-flow="m:6" data-gap="20" data-a="fade" data-t="{W(s,'covas',0,.2)}" style="left:80px">SEGUNDO O PROMOTOR LINCOLN GAKIYA (GAECO), INTEGRANTES DA FACÇÃO COMPRARAM COTAS DAS COOPERATIVAS. NINGUÉM ACUSA MARTA OU COVAS. CONTRATO DE ÔNIBUS É DA PREFEITURA (HOJE, NUNES, MDB {DIR}). SÓ CASOS COM OPERAÇÃO OU PROCESSO.</div>
''', 'camara', 'MP-SP E POLÍCIA CIVIL (2024–2026) · DIÁRIO DO TRANSPORTE, MAR/2019 · O TEMPO, SET/2026 · ' + IDS, kbo='50% 50%'))

s = 's07'; CUR['s'] = s
c7 = chart(s, YM, [
    dict(n='SÃO PAULO', sub='MORTES CAUSADAS<br>PELA POLÍCIA', v=MDIP, c=Y, w=7, lt=W(s,'olha',0), dots=[(3, '940'), (8, '419'), (11, '835')]),
], 1000, [0, 250, 500, 750, 1000], 0, 0, h=520, marks=[('2020', 'CÂMERAS', '#fff'), ('2023', 'TARCÍSIO', R)],
   stages=[(0, 6, W(s,'olha',0,-.2), 1.8), (6, 8, W(s,'desce',0,-.2), 1.6), (8, 11, W(s,'volta',0,-.2), 1.8)],
   notes=[(4, 470, '↘ CÂMERA<br>NA FARDA', '#fff', W(s,'desce',0,.2), -40, 0),
          (9, 330, '↗ VOLTA A<br>SUBIR', R, W(s,'subir',0,-.2), 14, 0)]).replace('{flow}', 'm:3')
H.append(scene(s, rail(3)+f'''
{eb(6, 'PROBLEMA 2 · A POLÍCIA (RESPONSABILIDADE DO ESTADO)', top=300)}
<div class="el h" data-flow="m:2" data-gap="28" data-a="slam" data-t="{W(s,'câmera',0,-.15)}" style="left:80px;width:880px;font-size:64px;color:#fff">COM CÂMERA, AS MORTES <span class="hl">CAÍRAM PELA METADE</span></div>
{c7}
<div class="el h" data-flow="m:4" data-gap="30" data-a="up" data-t="{W(s,'quatro',0,-.25)}" style="left:80px;width:880px;font-size:56px;color:#fff">2025: <span style="color:{R}">QUASE 1 EM CADA 4</span> MORTES VIOLENTAS DO ESTADO</div>
<div class="el fine" data-flow="m:5" data-gap="22" data-a="fade" data-t="{W(s,'quatro',0,.5)}" style="left:80px">835 DE 3.615 (23,1%). FGV: −57% NOS BATALHÕES COM CÂMERA. O GOVERNO DE SP DIZ QUE A SOMA DO MANDATO É MENOR QUE A DO ANTERIOR; A DIREÇÃO, DESDE 2023, É DE ALTA. OPERAÇÃO VERÃO (2024): A MAIS LETAL DESDE O CARANDIRU.</div>
''', 'pm', 'SSP-SP (VIA AGÊNCIA BRASIL E FBSP, 2014–2025) · FGV, 2022 · FBSP, ANUÁRIO 2026', kbo='50% 55%'))

s = 's07b'; CUR['s'] = s
H.append(scene(s, rail(3)+f'''
{eb(0, 'QUEM AJUDA A POLÍCIA A MATAR MENOS?', top=300)}
<div class="el rows" data-flow="m:2" data-gap="34" data-a="fade" data-t="{W(s,'governo',0,-.3)}" style="left:80px">
  {row('2024 · GOVERNO ATUAL 🦑', 'REGRAS NACIONAIS PARA CÂMERA NA FARDA E USO DA FORÇA', None, Y, 0, sub=f'TARCÍSIO DISSE QUE SP SEGUIRIA')}</div>
<div class="el rows" data-flow="m:3" data-gap="34" data-a="fade" data-t="{W(s,'bolsonaro',0,-.3)}" style="left:80px">
  {row('2020 · BOLSONARO', 'REVOGA AS REGRAS DE RASTREAMENTO DE ARMAS E MUNIÇÕES', None, '#5B7CFF', 0, sub=f'PL {EXT}')}
  {row('2019 · BOLSONARO', 'PROJETO QUE ACABA COM A MARCAÇÃO DAS BALAS DA POLÍCIA', None, '#5B7CFF', 0, sub='PL 3.723/2019', fade=W(s,'projeto',0,-.2))}</div>
<div class="el h" data-flow="m:4" data-gap="44" data-a="slam" data-t="{W(s,'flávio',0,-.2)}" style="left:80px;width:880px;font-size:62px;color:#fff">FLÁVIO BOLSONARO: <span class="hl">“DETALHEZINHO”</span></div>
<div class="el fine" data-flow="m:5" data-gap="24" data-a="fade" data-t="{W(s,'outubro',0,-.1)}" style="left:80px">TV GLOBO, 16/10/2026 (PL {EXT}). A MARCAÇÃO AJUDOU A ESCLARECER OS CASOS MARIELLE FRANCO E PATRÍCIA ACIOLI (MPF). EM SP, A POLÍCIA CAUSOU 23,1% DAS MORTES VIOLENTAS EM 2025.</div>
''', 'pm2', 'MJSP, PORTARIA DE CÂMERAS (MAI/2024) E DECRETO DO USO DA FORÇA (DEZ/2024) · EXÉRCITO/COLOG, ABR/2020 · PODER360 E METRÓPOLES, OUT/2026 · ' + IDS, kbo='50% 50%'))

s = 's08'; CUR['s'] = s
YE = [str(y) for y in range(2016, 2024)]
ESC = [51, 54, 46, 34, 42, 47, 40, 31]
c8 = chart(s, YE, [
    dict(n='SÃO PAULO', sub='HOMICÍDIOS<br>ESCLARECIDOS (%)', v=ESC, c=R, w=7, lt=W(s,'olha',0,.2), dots=[(1, '54%'), (7, '31%')]),
], 60, [0, 20, 40, 60], 0, 0, h=430, marks=[('2019', 'DORIA', '#fff'), ('2023', 'TARCÍSIO', R)],
   stages=[(0, 1, W(s,'olha',0,-.1), 1.0), (1, 7, W(s,'vinte',0,-.3), 2.6)],
   notes=[(1, 22, '2017: MAIS<br>DA METADE', '#fff', W(s,'metade',0,-.2), -40, 0),
          (4, 22, '↘ 2023: 3 EM 10', R, W(s,'três',1,-.2), -20, 0)]).replace('{flow}', 'm:2')
H.append(scene(s, rail(4)+f'''
{eb(7, 'PROBLEMA 3 · HOMICÍDIOS ESCLARECIDOS (%)', top=300)}
{c8}
<div class="el h" data-flow="m:3" data-gap="40" data-a="slam" data-t="{W(s,'campeão',0,-.15)}" style="left:80px;width:880px;font-size:64px;color:#fff">CAMPEÃO DE MORTES <span class="hl">SEM CAUSA DEFINIDA</span></div>
<div class="el rows" data-flow="m:4" data-gap="30" data-a="fade" data-t="{W(s,'contando',0,-.3)}" style="left:80px">
  {row('TAXA OFICIAL', '6,6', 6.6/12.8, WH, W(s,'contando',0))}
  {row('COM HOMICÍDIOS OCULTOS', '12,8', 1, R, W(s,'dobra',0,-.2), sub='HOMICÍDIOS POR 100 MIL · 2024')}</div>
<div class="el fine" data-flow="m:5" data-gap="22" data-a="fade" data-t="{W(s,'campeão',0,.6)}" style="left:80px">ESCLARECIDO = VIROU DENÚNCIA DO MP. BRASIL EM 2023: 36%. A QUEDA COMEÇA EM 2018–2019 E VOLTA A CAIR DESDE 2021: NÃO É DE UM GOVERNO SÓ. HOMICÍDIOS OCULTOS: ESTIMATIVA DO ATLAS; SP LIDERA DESDE 2014. INVESTIGAÇÃO É DA POLÍCIA CIVIL (ESTADO).</div>
''', 'luz', 'INSTITUTO SOU DA PAZ, ONDE MORA A IMPUNIDADE (EDIÇÕES 2024 E 2025) · IPEA/FBSP, ATLAS 2026', kbo='50% 50%'))

s = 's09'; CUR['s'] = s
H.append(scene(s, rail(5)+f'''
{eb(8, 'PROBLEMA 4 · A RUA', top=320)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'cinco',1,-.15)}" style="left:80px;width:880px;font-size:66px;color:#fff">A CAPITAL TEM 5,6% DO PAÍS E <span class="hl">1 EM CADA 5 CELULARES</span> ROUBADOS OU FURTADOS</div>
<div class="el rows" data-flow="m:3" data-gap="40" data-a="fade" data-t="{W(s,'roubos',0,-.3)}" style="left:80px">
  {row('ROUBOS', 'CAÍRAM', None, Y, 0)}
  {row('FURTOS', 'SUBIRAM NA CAPITAL (+3,6%, 2025)', None, R, 0, fade=W(s,'furtos',0,-.2))}
  {row('VIOLÊNCIA SEXUAL', '+6% · 1º SEMESTRE DE 2026', None, R, 0, fade=W(s,'sexual',0,-.2))}
  {row('FEMINICÍDIOS', 'MAIOR 1º TRIMESTRE DESDE 2018', None, R, 0, fade=W(s,'feminicídios',0,-.2))}</div>
<div class="el fine" data-flow="m:4" data-gap="24" data-a="fade" data-t="{W(s,'dezoito',0,.2)}" style="left:80px">QUEM CUIDA: POLICIAMENTO E INVESTIGAÇÃO = ESTADO. GUARDA CIVIL, ILUMINAÇÃO E URBANISMO = PREFEITURA.</div>
''', 'viaduto', 'FBSP, ANUÁRIO 2026 · SSP-SP (2025 E 1º SEM/2026)', kbo='50% 50%'))

s = 's10'; CUR['s'] = s
H.append(scene(s, f'''
{eb(9, 'E O GOVERNO FEDERAL?', top=320)}
{quote('“O GOVERNO FEDERAL NÃO AJUDA.”', W(s,'governo',0), 'm:2', gap=26)}
<div class="el rows" data-flow="m:3" data-gap="36" data-a="fade" data-t="{W(s,'mandou',0,-.2)}" style="left:80px">
  {row('FUNDO NACIONAL 2024', 'R$ 45,8 MI · A MAIOR FATIA', None, Y, 0, sub='ORÇAMENTO DA PM PAULISTA: R$ 10,3 BI')}
  {row('PF E RECEITA', 'NA OPERAÇÃO DOS COMBUSTÍVEIS', None, Y, 0, fade=W(s,'polícia',0,-.2))}</div>
<div class="el h redtxt" data-flow="m:4" data-gap="44" data-a="slam" data-t="{W(s,'fronteira',0,-.15)}" style="left:80px;width:880px;font-size:66px">FRONTEIRA E PORTO DE SANTOS SÃO DA UNIÃO.</div>
<div class="el body" data-flow="m:5" data-gap="26" data-a="up" data-t="{W(s,'decretos',0,-.2)}" style="left:80px;width:860px">Com os decretos de armas do governo Bolsonaro, a facção passou a <b>comprar fuzis com nota fiscal.</b></div>
<div class="el fine" data-flow="m:6" data-gap="22" data-a="fade" data-t="{W(s,'registrados',0,.1)}" style="left:80px">FUZIL COM NOTA: R$ 12–15 MIL, CONTRA R$ 35–59 MIL NO CONTRABANDO (PROMOTOR LINCOLN GAKIYA, ESTADÃO, 2022). LEI ANTIFACÇÃO: PROPOSTA DO GOVERNO ATUAL 🦑, RELATOR DERRITE (PP {DIR}), SANCIONADA PELO PRESIDENTE. DERRITE RECUSOU APOIO DIRETO DA PF NO CASO RUY FERRAZ (SET/2025); NO SENADO, O RELATOR DISSE QUE A CÂMARA TIROU DO TEXTO PONTOS CONTRA CRIME DE COLARINHO BRANCO.</div>
''', 'santos', 'MJSP/FNSP, 2024 · TCE-SP, CONTAS 2023 · CÂMARA DOS DEPUTADOS, 2026', kbo='50% 50%'))

s = 's11'; CUR['s'] = s
H.append(scene(s, f'''
{eb(10, 'O DEBATE, CHECADO · GLOBO, 29/09/2026', top=320)}
<div class="el items" data-flow="m:2" data-gap="36" style="left:80px">
{item(f'TARCÍSIO · REPUBLICANOS {DIR}', '“MENOR HOMICÍDIO DA HISTÓRIA” → <span style="color:#FFD34D">VERDADE</span>', W(s,'tarcísio',0,-.1))}
{item(f'TARCÍSIO · REPUBLICANOS {DIR}', '“TODOS OS CRIMES CAÍRAM” → <span style="color:#FF4A3D">EXAGERO</span>', W(s,'exagerou',0,-.2))}
{item(f'HADDAD · PT {ESQ}', '“SÓ 1 EM 3 HOMICÍDIOS ESCLARECIDO” → <span style="color:#FFD34D">VERDADE</span>', W(s,'haddad',0,-.1))}</div>
<div class="el fine" data-flow="m:3" data-gap="26" data-a="fade" data-t="{W(s,'verdade',1,.2)}" style="left:80px">SUBIRAM EM 2025: TENTATIVA DE HOMICÍDIO (+5,7%) E LESÃO CORPORAL (+7,5%). “O PAÍS FUNCIONA, SP NÃO” (HADDAD): O PAÍS CAIU 8,2% E SP 3,9%, MAS SP PARTE DE UMA BASE 2,4 VEZES MENOR. “PCC FINANCIOU PESQUISA PARA O PRESIDENTE”: FALSO (AOS FATOS).</div>
''', 'alesp', 'AGÊNCIA LUPA, 29/09/2026 · G1 FATO OU FAKE · AOS FATOS · FBSP, ANUÁRIO 2026', kbo='50% 50%'))

s = 's12'; CUR['s'] = s
H.append(scene(s, f'''
{eb(11, 'MORTES VIOLENTAS POR 100 MIL · 2025', top=320)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'partido',0,-.15)}" style="left:80px;width:880px;font-size:84px;color:#fff">NÃO É SÓ <span class="hl">PARTIDO.</span></div>
<div class="el rows" data-flow="m:3" data-gap="36" data-a="fade" data-t="{W(s,'santa',0,-.3)}" style="left:80px">
  {row('SANTA CATARINA', '7,6', 7.6/36.8, WH, W(s,'santa',0), sub=f'PL {EXT}')}
  {row('SÃO PAULO', '7,8', 7.8/36.8, Y, W(s,'santa',0,.2), sub=f'REPUBLICANOS {DIR}')}
  {row('RIO DE JANEIRO', '22,6', 22.6/36.8, R, W(s,'rio',0), sub=f'PL {EXT}')}</div>
<div class="el rows" data-flow="m:4" data-gap="36" data-a="fade" data-t="{W(s,'piauí',0,-.3)}" style="left:80px">
  {row('PIAUÍ', '17,1', 17.1/36.8, WH, W(s,'piauí',0), sub=f'PT {ESQ}')}
  {row('BAHIA', '36,8', 1, R, W(s,'bahia',0), sub=f'PT {ESQ}')}</div>
''', 'marginal', 'FBSP, ANUÁRIO 2026 (MVI, INCLUI MORTES PELA POLÍCIA) · ' + IDS, kbo='50% 50%'))

s = 's13'; CUR['s'] = s
H.append(scene(s, f'''
{eb(0, 'RESUMINDO', top=300)}
<div class="el h" data-flow="m:2" data-gap="30" data-a="up" data-t="{W(s,'esquerda',0,-.2)}" style="left:80px;width:880px;font-size:72px;color:#fff">A ESQUERDA NÃO MANDA NA POLÍCIA DE SP <span style="color:{Y}">HÁ 30 ANOS.</span></div>
<div class="el h" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'queda',0,-.2)}" style="left:80px;width:880px;font-size:64px;color:#fff">A QUEDA FOI DE VÁRIOS GOVERNOS. <span style="color:{Y}">OS PROBLEMAS DE HOJE SÃO DO ESTADO.</span></div>
<div class="el repost" data-flow="m:4" data-gap="50" data-a="slam" data-t="{W(s,'você',0,-.15)}" data-shake="1" style="left:80px;width:880px;font-size:56px">O QUE VOCÊ COBRARIA NO SEGUNDO MANDATO?<small>Tarcísio foi reeleito em 04/10/2026 (2027–2030)</small></div>
''', 'ponte', 'FBSP · IPEA · SOU DA PAZ · TSE · LUPA', kbo='50% 50%'))

CSS = open(os.path.join(KIT, 'preview_kit/style.css')).read() + '''
.shadeMap{position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,7,9,.82) 0%,rgba(6,7,9,.35) 34%,rgba(6,7,9,0) 52%,rgba(6,7,9,0) 66%,rgba(6,7,9,.95) 82%)}
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

.chart{position:absolute}.chart svg{position:absolute;left:0;top:0;overflow:visible}
.crev{position:absolute;left:0;top:0;overflow:hidden;width:0}
.cnote{font-size:20px;line-height:1.25}
.clab{position:absolute;font-family:JBM;font-weight:700;font-size:22px;letter-spacing:1.5px;white-space:nowrap;line-height:1.2;text-shadow:0 2px 10px rgba(0,0,0,.8)}
.clab small{display:block;font-size:15px;line-height:1.6;letter-spacing:.5px;color:#BDB6A6;margin-top:4px}.clab small .ide{font-size:13px;padding:1px 6px}
.quote{color:#F2ECE0;font-weight:800;text-shadow:0 3px 18px rgba(0,0,0,.6)}
.pull{font-family:Rub;font-weight:700;font-style:italic;font-size:50px;line-height:1.15;color:#fff;padding-left:30px;border-left:6px solid #FFD34D;text-shadow:0 3px 16px rgba(0,0,0,.6)}
.pull small{display:block;font-family:JBM;font-style:normal;font-weight:700;font-size:20px;letter-spacing:1.5px;color:#BDB6A6;margin-top:16px}
'''
page = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>São Paulo</title>
<link rel="stylesheet" href="fx.css"><style>{CSS}</style></head><body><div id="stage">
{"".join(H)}
<div id="grain"></div><div id="foot">@tentandochegaratevoce</div></div>
<script>window.DUR={DUR:.2f};</script><script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script><script src="zoom.js"></script><script src="fit.js"></script><script src="layout.js"></script></body></html>'''
open(os.path.join(KIT, 'sp.html'), 'w').write(page)
print('ok', DUR)
