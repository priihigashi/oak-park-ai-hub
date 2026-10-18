"""Reel v4 — Bahia e Norte (explicativo). Redesenho editorial: uma linha de alinhamento à esquerda,
sem caixas (texto direto sobre a foto escurecida), eyebrow numerado por capítulo, tabelas com filete,
fonte da informação embaixo do @, sem aviso de IA na tela. Gera ../bahia.html."""
import json, html, re, os
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open('/home/claude/work/v3/timeline.json'))
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
CH = ["HISTÓRIA", "COMPARAR", "TENTOU", "GARGALOS", "SAÍDAS", "TRAVADO"]
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
FT = json.load(open('/home/claude/work/v3/ftop.json')) if os.path.exists('/home/claude/work/v3/ftop.json') else {}
H = []

s = 'v01'; CUR['s'] = s
H.append(scene(s, f'''
{eb(0, f'BAHIA · PT {ESQ} DESDE 2007', top=330)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'mais',0,-.15)}" data-shake="1" style="left:80px;width:880px;font-size:118px;color:#fff">ONDE MAIS SE <span class="hl">MATA</span> NO BRASIL</div>
<div class="el h redtxt" data-flow="m:3" data-gap="30" data-a="slam" data-t="{W(s,'culpa',0,-.1)}" data-d=".35" style="left:80px;font-size:96px;width:880px">CULPA DA ESQUERDA?</div>
<div class="el body" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'números',0,-.1)}" style="left:80px;width:820px">Os números sozinhos enganam. <b>Vamos entender o porquê.</b></div>
''', 'i01', 'FBSP, ANUÁRIO 2026 · ' + IDS, kbo='70% 70%'))

s = 'v02'; CUR['s'] = s
H.append(scene(s, rail(0)+f'''
{eb(1, 'POR QUE O NORDESTE EXPLODIU', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t="{W(s,'até',0,-.2)}" style="left:80px">
  {row('ATÉ 2006', 'N, NE E SE ≈ 25', None, WH, 0)}
  {row('DEPOIS', 'PCC E CV SAEM DO SUDESTE', None, Y, 0, fade=W(s,'pcc',0,-.1))}
  {row('2015', 'NASCE O BDM, NA BAHIA', None, WH, 0, fade=W(s,'migrou',0,-.3))}</div>
<div class="el h" data-flow="m:3" data-gap="50" data-a="slam" data-t="{W(s,'migrou',0,-.15)}" style="left:80px;width:880px;font-size:84px;color:{Y}">A VIOLÊNCIA MIGROU.</div>
<div class="el body" data-flow="m:4" data-gap="26" data-a="up" data-t="{W(s,'bahia',0,-.15)}" style="left:80px;width:860px">Na Bahia, 2003 → 2006: <b>15,8 → 23,1</b> homicídios por 100 mil. Antes do PT.</div>
''', 'i04', 'IPEA/FBSP, ATLAS 2018 (VIA BBC) · CIÊNC. SAÚDE COLETIVA, 2014', kbo='50% 70%'))

s = 'v03'; CUR['s'] = s
H.append(scene(s, rail(1)+f'''
{eb(2, 'NORDESTE · MORTES POR 100 MIL · 2025', top=320)}
<div class="el body" data-flow="m:2" data-gap="28" data-a="up" data-t=".2" style="left:80px;width:860px;font-size:36px">O PT só governa estados do Nordeste, a região mais violenta.</div>
<div class="el rows" data-flow="m:3" data-gap="40" data-a="fade" data-t="{W(s,'estados',0,-.2)}" style="left:80px">
  {row('ESTADOS DO PT', '29,4', 1, R, W(s,'estados',0), sub=f'BA · CE · PI · RN {ESQ}')}
  {row('OUTROS PARTIDOS', '28,5', 28.5/29.4, WH, W(s,'estados',1), sub=f'AL · PE · SE {DIR}<br>MA · PB {CESQ}')}
  {row('BRASIL', '19,1', 19.1/29.4, 'rgba(242,236,224,.45)', W(s,'estados',1,.4))}</div>
<div class="el h" data-flow="m:4" data-gap="50" data-a="slam" data-t="{W(s,'mesma',0,-.1)}" style="left:80px;width:880px;font-size:80px;color:{Y}">MESMA REGIÃO,<br>MESMO PATAMAR.</div>
''', 'i09', 'FBSP, ANUÁRIO 2026 (MÉDIA SIMPLES, CÁLCULO NOSSO) · ' + IDS, kbo='70% 60%'))

s = 'v04'; CUR['s'] = s
H.append(scene(s, rail(2)+f'''
{eb(3, 'O QUE O GOVERNO TENTOU', top=320)}
<div class="el items" data-flow="m:2" data-gap="40" style="left:80px">
  {item('2011 · PACTO PELA VIDA · WAGNER', 'Metas e comitês por território. <span class="mut">Segurou a alta: crimes letais −12,6% (2012–2020).</span>', W(s,'pacto',0,-.2))}
  {item('2024 · BAHIA PELA PAZ · JERÔNIMO', 'Assistência nos bairros mais violentos. <span class="mut">22 mil atendimentos em 2025.</span>', W(s,'bahia',0,-.2))}</div>
''', 'i02', 'UFPB, 2022 · ALBA/CORREIO, MAI/2024 · GOVERNO DA BAHIA, MAR/2026', kbo='60% 55%'))

s = 'v05'; CUR['s'] = s
H.append(scene(s, rail(2)+f'''
{eb(4, 'ESTÁ MELHORANDO?', top=320)}
<div class="el rows" data-flow="m:2" data-gap="36" data-a="fade" data-t="{W(s,'três',0,-.2)}" style="left:80px">
  {row('2023', '−6,0%', 6.0/9.6, Y, W(s,'três',0))}
  {row('2024', '−8,2%', 8.2/9.6, Y, W(s,'três',0,.3))}
  {row('2025', '−9,6%', 1, Y, W(s,'três',0,.6))}</div>
<div class="el note" data-flow="m:3" data-gap="16" data-a="fade" data-t="{W(s,'três',0,.2)}" style="left:80px">QUEDA NAS MORTES VIOLENTAS, ANO A ANO</div>
<div class="el h redtxt" data-flow="m:4" data-gap="56" data-a="slam" data-t="{W(s,'devagar',0,-.1)}" style="left:80px;font-size:100px">MAS DEVAGAR.</div>
<div class="el body" data-flow="m:5" data-gap="20" data-a="up" data-t="{W(s,'segunda',0,-.15)}" style="left:80px;width:860px">36,8 por 100 mil: <b>a 2ª pior taxa do país.</b></div>
''', 'i03', 'SSP-BA (2023–2024) · FBSP, ANUÁRIO 2026', kbo='40% 55%'))

s = 'v06'; CUR['s'] = s
H.append(scene(s, rail(3)+f'''
{eb(5, 'GARGALO 1 · INVESTIGAÇÃO', top=320)}
<div class="el h cnt" data-flow="m:2" data-gap="30" data-t="{W(s,'treze',0,-.15)}" data-d=".9" data-from="0" data-to="13" data-dec="0" data-suf="%" style="left:72px;font-size:260px;color:{R};width:880px;line-height:.82;height:214px"></div>
<div class="el body" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'homicídios',0,-.1)}" style="left:80px;width:860px">dos homicídios de 2023 foram esclarecidos até o fim de 2024. <b>Pior índice do país.</b></div>
<div class="el rows" data-flow="m:4" data-gap="40" data-a="fade" data-t="{W(s,'média',0,-.2)}" style="left:80px">
  {row('BAHIA', '13%', 13/36, R, W(s,'média',0))}
  {row('BRASIL', '36%', 1, WH, W(s,'média',0,.2))}</div>
''', 'i06', 'INSTITUTO SOU DA PAZ, ONDE MORA A IMPUNIDADE (OUT/2025)', kbo='50% 75%'))

s = 'v07'; CUR['s'] = s
H.append(scene(s, rail(3)+f'''
{eb(6, 'GARGALO 2 · A POLÍCIA', top=320)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'mais',0,-.15)}" data-shake="1" style="left:80px;width:880px;font-size:92px;color:#fff">A QUE <span class="hl">MAIS MATA</span> NO BRASIL</div>
<div class="el rows" data-flow="m:3" data-gap="36" data-a="fade" data-t="{W(s,'três',0,-.2)}" style="left:80px">
  {row('AÇÃO POLICIAL', '28,7%', .287/.35, R, W(s,'três',0), sub='DAS MORTES VIOLENTAS DA BA')}</div>
<div class="el counter" data-flow="m:4" data-gap="44" data-minh="150" data-a="up" data-t="{W(s,'mil',0,-.2)}" style="left:80px;width:880px"><span class="cnt" data-t="{W(s,'mil',0,-.1)}" data-d="1" data-from="0" data-to="1263" data-dec="0" data-thou="1" style="color:#fff"></span><b>câmeras corporais<br>distribuídas</b></div>
<div class="el stamp-r" data-flow="m:5" data-gap="50" data-a="stamp" data-t="{W(s,'sete',0,-.05)}" data-d=".35" data-r="-2" style="left:80px;white-space:nowrap">SÓ 7,5% EM USO</div>
''', 'i07', 'FBSP, ANUÁRIO 2026 · MP-BA, INSPEÇÃO EM 15 UNIDADES (OUT/2025)', kbo='70% 55%'))

s = 'v08'; CUR['s'] = s
H.append(scene(s, rail(3)+f'''
{eb(7, 'GARGALO 3 · O QUE TEM PROCESSO', top=320)}
<div class="el items" data-flow="m:2" data-gap="40" style="left:80px">
  {item('PMs · OPERAÇÃO FOGO AMIGO (2024)', '10 presos por vender armas a facção.', W(s,'dez',0,-.2))}
  {item('RUI COSTA · RESPIRADORES (R$ 48,7 MI)', 'TCU inocentou. Inquérito segue sem acusação.', W(s,'respiradores',0,-.2))}
  {item('JAQUES WAGNER · DELAÇÃO NA LAVA JATO', 'Arquivado no STF em 2019.', W(s,'wagner',0,-.2))}</div>
''', 'i08', 'PF · CORREIO, 2024 · TCU, 2025 · STF, INQ 4325 · CORREIO DA MANHÃ, JUN/2026', kbo='50% 80%'))

s = 'v09'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(8, 'DÁ PRA CAIR? DÁ.', top=320)}
<div class="el items" data-flow="m:2" data-gap="40" style="left:80px">
  {item(f'PERNAMBUCO · PSB {CESQ}', '53 → 33,9 <span class="mut">(2007–2013)</span><br><span class="mut sm">O governador saiu, o programa perdeu força: 57,2 em 2017.</span>', W(s,'pernambuco',0,-.2))}
  {item(f'PARÁ · MDB {DIR}', '56,6 → 29,5 <span class="mut">(2018–2024)</span><br><span class="mut sm">Obras e serviços nos bairros (TerPaz) junto com polícia.</span>', W(s,'pará',0,-.2))}</div>
<div class="el note" data-flow="m:3" data-gap="24" data-a="fade" data-t="{W(s,'metade',0,.2)}" style="left:80px">POR 100 MIL · HOMICÍDIOS (PE) E MORTES VIOLENTAS (PA)</div>
''', 'i05', 'FBSP (GAZETA DO POVO, 2019) · FBSP, ANUÁRIO 2025 · ' + IDS, kbo='60% 50%'))

s = 'v10'; CUR['s'] = s
H.append(scene(s, rail(4)+f'''
{eb(9, 'E A EDUCAÇÃO?', top=320)}
<div class="el h" data-flow="m:2" data-gap="34" data-a="slam" data-t="{W(s,'quarto',0,-.15)}" style="left:80px;width:880px;font-size:84px;color:#fff">4º ESTADO EM <span class="hl">TEMPO INTEGRAL</span></div>
<div class="el body" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'integral',0,-.1)}" style="left:80px;width:860px"><b>140 mil alunos</b>, 34% da rede estadual. Brasil: 26%.</div>
<div class="el rows" data-flow="m:4" data-gap="40" data-a="fade" data-t="{W(s,'nota',0,-.2)}" style="left:80px">
  {row('IDEB ENS. MÉDIO', '4,0', 4.0/4.5, Y, W(s,'nota',0), sub='BAHIA · +0,6 DESDE 2019')}
  {row('NORDESTE', '4,3', 4.3/4.5, WH, W(s,'nota',0,.2))}
  {row('BRASIL', '4,5', 1, WH, W(s,'nota',0,.4))}</div>
<div class="el note" data-flow="m:5" data-gap="24" data-a="fade" data-t="{W(s,'estudos',0,-.1)}" style="left:80px;color:{Y}">+1 PONTO EM EDUCAÇÃO ≈ −25% HOMICÍDIOS NA CIDADE (ASSOCIAÇÃO, NÃO PROVA DE CAUSA)</div>
''', 'i14', 'CENSO ESCOLAR 2025 · INEP, IDEB 2025 · INSPER/INSTITUTO NATURA, 2022', kbo='60% 55%'))

s = 'v11'; CUR['s'] = s
H.append(scene(s, f'''
{eb(10, 'E NO NORTE?', top=260)}
<div class="el rows" data-flow="m:2" data-gap="34" data-a="fade" data-t="{W(s,'amapá',0,-.2)}" style="left:80px">
  {row('AMAPÁ', '42,5 · 1º', None, '#fff', 0, sub=f'SOLIDARIEDADE {CDIR}')}
  {row('LETALIDADE POLICIAL', '17,1 · 1º', None, R, 0, fade=W(s,'letalidade',0,-.1))}</div>
<div class="el h" data-flow="m:3" data-gap="56" data-a="slam" data-t="{W(s,'marajó',0,-.15)}" style="left:80px;font-size:96px;color:#fff">MARAJÓ (PA)</div>
<div class="el rows" data-flow="m:4" data-gap="26" data-a="fade" data-t="{W(s,'estupro',0,-.2)}" style="left:80px">
  {row('MARAJÓ', '69', 1, R, W(s,'estupro',0), sub='ESTUPRO DE VULNERÁVEL / 100 MIL')}
  {row('BRASIL (2022)', '28', 28/69, WH, W(s,'estupro',0,.2))}</div>
<div class="el body" data-flow="m:5" data-gap="34" data-a="up" data-t="{W(s,'sete',0,-.2)}" style="left:80px;width:860px"><b>73%</b> em situação de pobreza no CadÚnico. Brasil: 28%.</div>
''', 'i11', 'FBSP, ANUÁRIO 2026 · MP-PA · RELATÓRIO CIDADANIA MARAJÓ (DEZ/2022)', kbo='50% 60%'))

s = 'v12'; CUR['s'] = s
H.append(scene(s, rail(5)+f'''
{eb(11, 'O QUE ESTÁ TRAVADO', top=320)}
<div class="el items" data-flow="m:2" data-gap="40" style="left:80px">
  {item('PEC DA SEGURANÇA PÚBLICA', 'Aprovada na Câmara em mar/2026. <span style="color:{R}">Ainda no Senado.</span>', W(s,'pec',0,-.2))}
  {item('LEI ANTIFACÇÃO · 24/03/2026', '✓ Sancionada pelo presidente.', W(s,'lei',0,-.2))}
  {item('QUEM CUIDA DE QUÊ', 'Polícias Militar e Civil: governador.<br>PF, PRF, fronteiras e rios: União.', .8)}</div>
''', 'i12', 'CÂMARA · SENADO (CCJ, 14/10/2026) · LEI 15.358/2026 · CF, ART. 144', kbo='50% 60%'))

s = 'v13'; CUR['s'] = s
H.append(scene(s, f'''
{eb(0, 'RESUMINDO', top=300)}
<div class="el h" data-flow="m:2" data-gap="30" data-a="up" data-t="{W(s,'região',0,-.2)}" style="left:80px;width:880px;font-size:76px;color:#fff">REGIÃO E FACÇÕES <span style="color:{Y}">EXPLICAM O NÍVEL.</span></div>
<div class="el h" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'governo',0,-.2)}" style="left:80px;width:880px;font-size:76px;color:#fff">GOVERNO <span style="color:{R}">EXPLICA A DIFERENÇA.</span></div>
<div class="el note" data-flow="m:4" data-gap="26" data-a="fade" data-t="{W(s,'investigar',0,-.1)}" style="left:80px">INVESTIGAR · CONTROLAR A POLÍCIA · MANTER OS PROGRAMAS · EDUCAR</div>
<div class="el repost" data-flow="m:5" data-gap="56" data-a="slam" data-t="{W(s,'você',0,-.15)}" data-shake="1" style="left:80px;width:880px;font-size:58px">O QUE VOCÊ COBRARIA DO PRÓXIMO MANDATO?<small>Jerônimo foi reeleito em 04/10/2026 (2027–2030)</small></div>
''', 'i13', 'TSE · FBSP · IPEA · SOU DA PAZ · MP-BA', kbo='50% 60%'))

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
'''
page = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Bahia e Norte</title>
<link rel="stylesheet" href="fx.css"><style>{CSS}</style></head><body><div id="stage">
{"".join(H)}
<div id="grain"></div><div id="foot">@tentandochegaratevoce</div></div>
<script>window.DUR={DUR:.2f};</script><script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script><script src="layout.js"></script></body></html>'''
open(os.path.join(KIT, 'bahia.html'), 'w').write(page)
print('ok', DUR)
