"""Reel timeline v3: violência na Bahia e no Norte — explicativo (história, comparação justa, o que tentaram,
por que não deu certo, o que funciona, educação, o que está travado). Gera ../bahia.html.
Timeline: /home/claude/work/v3/timeline.json. Imagens: ../assets/bn/iNN.jpg (IA, uma por cena)."""
import json, html, re, os
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open('/home/claude/work/v3/timeline.json'))
S = {o['id']: o for o in TL}

def norm(w): return re.sub(r'[^\wÀ-ú]', '', w.lower())

for o in TL:  # espalha palavras empilhadas no mesmo instante
    ws = o['words']
    for i in range(1, len(ws)):
        if ws[i][1] - ws[i-1][1] < 0.09:
            j = i
            while j < len(ws) and ws[j][1] - ws[i-1][1] < 0.09: j += 1
            t0 = ws[i-1][1]; t1 = ws[j][1] if j < len(ws) else t0 + 0.25*(j-i+1)
            n = j - i + 1
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
    return f'<div class="kar karfull el" data-words="{" ".join(toks)}" style="left:130px;top:1480px;width:820px"></div>'

DUR = TL[-1]['e']
RAIL = ["HISTÓRIA", "COMPARAR", "TENTOU", "GARGALOS", "SAÍDAS", "TRAVADO"]
def rail(active, t=.15):
    xs = [110+i*172 for i in range(6)]
    dots = ''.join(f'<div class="st{" on" if i==active else ""}{" past" if i<active else ""}" style="left:{x}px"><i></i><b>{y}</b></div>' for i, (x, y) in enumerate(zip(xs, RAIL)))
    return f'<div class="rail el" data-a="left" data-t="{t}" data-d=".35" style="left:0;top:150px"><div class="line"></div><div class="fill" style="width:{xs[active]-60}px"></div>{dots}</div>'

AIW = '<div class="el aiwarn" data-a="fade" data-t=".3" style="left:80px;top:1700px">imagens ilustrativas geradas por IA</div>'
def src(txt, t=.6):
    return f'<div class="el src" data-a="fade" data-t="{t}" style="left:80px;top:1450px">{txt}</div>'
def scene(sid, inner, bg, kb=1.10, kbo='50% 45%', dim=0.95):
    o = S[sid]
    b = f'<img class="bgimg" src="assets/bn/{bg}.jpg" data-kb="{kb}" data-kbo="{kbo}"><div class="shadeg" style="opacity:{dim}"></div>'
    return f'<section class="scene" data-s="{o["s"]}" data-e="{o["e"]}" data-in="cut" data-theme="dark">{b}<div class="safe">{inner}{AIW}</div>{kar(sid)}</section>\n'
def brow(lab, val, w, color, t, sub='', lw=330):
    sb = f'<small>{sub}</small>' if sub else ''
    return (f'<div class="brow hb"><span style="width:{lw}px;flex:0 0 {lw}px">{lab}{sb}</span><div class="bar bfill" data-t="{t}" data-d=".7" data-to="{w}" style="background:{color}"></div><em>{val}</em></div>')
def ide(k, lab): return f'<i class="ide {k}">{lab}</i>'
ESQ, CESQ, DIR, CDIR = ide('esq', 'ESQUERDA'), ide('esq', 'CENTRO-ESQUERDA'), ide('dir', 'DIREITA'), ide('dir', 'CENTRO-DIREITA')
Y, R, WH = '#FFD34D', '#FF4A3D', '#F2ECE0'
IDS = 'IDEOLOGIA: BOLOGNESI ET AL. (DADOS, 2023)'
H = []

s = 'v01'
H.append(scene(s, f'''
<div class="el label gold" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">BAHIA · PT {ESQ} DESDE 2007</div>
<div class="el h" data-flow="m:2" data-gap="44" data-a="slam" data-t="{W(s,'mais',0,-.15)}" data-shake="1" style="left:80px;width:900px;font-size:112px;color:#fff">ONDE MAIS SE <span class="hl">MATA</span> NO BRASIL</div>
<div class="el h redtxt" data-flow="m:3" data-gap="40" data-a="slam" data-t="{W(s,'culpa',0,-.1)}" data-d=".35" style="left:80px;font-size:104px;width:900px">CULPA DA ESQUERDA?</div>
<div class="el cta" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'números',0,-.1)}" style="left:80px">OS NÚMEROS SOZINHOS ENGANAM ↓</div>
{src('FBSP · ANUÁRIO 2026 · ' + IDS)}
''', 'i01', kbo='50% 70%'))

s = 'v02'
H.append(scene(s, rail(0)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">POR QUE O NORDESTE EXPLODIU</div>
<div class="el glass" data-flow="m:2" data-gap="34" data-a="up" data-t="{W(s,'até',0,-.2)}" style="left:80px;width:920px;padding:18px 30px">
  <div class="brow" style="margin-top:0"><span style="width:220px">ATÉ 2006</span><em style="font-size:32px">N, NE E SUDESTE: ~25 POR 100 MIL</em></div>
  <div class="brow" data-a="fade" data-t="{W(s,'pcc',0,-.1)}"><span style="width:220px">DEPOIS</span><em style="font-size:32px;color:{Y}">PCC E CV SAEM ATRÁS DE ROTAS</em></div>
  <div class="brow" data-a="fade" data-t="{W(s,'migrou',0,-.3)}"><span style="width:220px">2015</span><em style="font-size:32px">NASCE O BDM, EM PRESÍDIO BAIANO</em></div></div>
<div class="el h" data-flow="m:3" data-gap="44" data-a="slam" data-t="{W(s,'migrou',0,-.15)}" style="left:80px;font-size:84px;color:{Y}">A VIOLÊNCIA MIGROU.</div>
<div class="el sub" data-flow="m:4" data-gap="30" data-a="up" data-t="{W(s,'bahia',0,-.15)}" style="left:80px;width:900px">Bahia, 2003 → 2006: <b>15,8 → 23,1</b> por 100 mil. Antes do PT.</div>
{src('IPEA/FBSP · ATLAS 2018 (VIA BBC) · CIÊNC. SAÚDE COLETIVA 2014 · BNEWS')}
''', 'i04', kbo='50% 70%'))

s = 'v03'
H.append(scene(s, rail(1)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">NORDESTE · MORTES VIOLENTAS POR 100 MIL · 2025</div>
<div class="el mono" data-flow="m:2" data-gap="30" data-a="fade" data-t=".2" style="left:80px;font-size:24px;color:#ddd;width:900px;line-height:1.4">O PT SÓ GOVERNA ESTADOS DO NORDESTE, A REGIÃO MAIS VIOLENTA</div>
<div class="el chartcard vz" data-flow="m:3" data-gap="24" data-a="fade" data-t="{W(s,'estados',0,-.2)}" style="left:80px;width:920px">
  {brow('ESTADOS DO PT', '29,4', int(380*29.4/29.4), R, W(s,'estados',0), sub=f'BA · CE · PI · RN {ESQ}', lw=380)}
  {brow('OUTROS PARTIDOS', '28,5', int(380*28.5/29.4), WH, W(s,'estados',1), sub=f'AL · PE · SE {DIR} MA · PB {CESQ}', lw=380)}
  <div class="mono" data-a="fade" data-t="{W(s,'mesma',0)}" style="font-size:22px;color:#ddd;margin-top:16px">BRASIL: 19,1 · MÉDIA SIMPLES DOS ESTADOS (CÁLCULO NOSSO)</div></div>
<div class="el h" data-flow="m:4" data-gap="50" data-a="slam" data-t="{W(s,'mesma',0,-.1)}" style="left:80px;width:900px;font-size:84px;color:{Y}">MESMA REGIÃO, MESMO PATAMAR.</div>
{src('FBSP · ANUÁRIO 2026 · ' + IDS)}
''', 'i09', kbo='50% 60%', dim=1.0))

s = 'v04'
H.append(scene(s, rail(2)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">O QUE O GOVERNO TENTOU</div>
<div class="el glass" data-flow="m:2" data-gap="34" data-a="up" data-t="{W(s,'pacto',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">2011 · PACTO PELA VIDA (WAGNER)</div>
  <div class="h" style="font-size:52px;color:#fff;margin-top:8px">METAS E COMITÊS POR TERRITÓRIO</div>
  <div class="vsub">segurou a alta: crimes letais −12,6% (2012–2020)</div></div>
<div class="el glass" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'bahia',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">2024 · BAHIA PELA PAZ (JERÔNIMO)</div>
  <div class="h" style="font-size:52px;color:#fff;margin-top:8px">ASSISTÊNCIA NOS BAIRROS MAIS VIOLENTOS</div>
  <div class="vsub">22 mil atendimentos em 2025 · meta: 24 núcleos em 2026</div></div>
{src('UFPB 2022 · ALBA/CORREIO (MAI/2024) · GOVERNO DA BAHIA (MAR/2026)')}
''', 'i02', kbo='50% 55%'))

s = 'v05'
H.append(scene(s, rail(2)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">ESTÁ MELHORANDO?</div>
<div class="el chartcard vz" data-flow="m:2" data-gap="34" data-a="fade" data-t="{W(s,'três',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:#ddd">QUEDA NAS MORTES VIOLENTAS, ANO A ANO</div>
  {brow('2023', '−6,0%', int(380*6.0/9.6), Y, W(s,'três',0), lw=200)}
  {brow('2024', '−8,2%', int(380*8.2/9.6), Y, W(s,'três',0,.3), lw=200)}
  {brow('2025', '−9,6%', 380, Y, W(s,'três',0,.6), lw=200)}</div>
<div class="el h redtxt" data-flow="m:3" data-gap="50" data-a="slam" data-t="{W(s,'devagar',0,-.1)}" style="left:80px;font-size:96px">MAS DEVAGAR.</div>
<div class="el sub" data-flow="m:4" data-gap="24" data-a="up" data-t="{W(s,'segunda',0,-.15)}" style="left:80px;width:900px">36,8 por 100 mil: <b>2ª maior taxa do país</b></div>
{src('SSP-BA (2023–2024) · FBSP · ANUÁRIO 2026 (2025)')}
''', 'i03', kbo='50% 55%'))

s = 'v06'
H.append(scene(s, rail(3)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">GARGALO 1 · INVESTIGAÇÃO</div>
<div class="el h cnt" data-flow="m:2" data-gap="40" data-t="{W(s,'treze',0,-.15)}" data-d=".9" data-from="0" data-to="13" data-dec="0" data-suf="%" style="left:80px;font-size:250px;color:{R};width:880px;line-height:.85;height:215px"></div>
<div class="el sub" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'homicídios',0,-.1)}" style="left:80px;width:900px">dos homicídios de 2023 esclarecidos até o fim de 2024. <b>Pior do país.</b></div>
<div class="el glass vz" data-flow="m:4" data-gap="34" data-a="fade" data-t="{W(s,'média',0,-.2)}" style="left:80px;width:920px">
  {brow('BAHIA', '13%', int(380*13/36), R, W(s,'média',0), lw=220)}
  {brow('BRASIL', '36%', 380, WH, W(s,'média',0,.2), lw=220)}</div>
<div class="el h" data-flow="m:5" data-gap="40" data-a="slam" data-t="{W(s,'trinta',0,.4)}" style="left:80px;font-size:72px;color:{Y}">87% SEM SOLUÇÃO.</div>
{src('INSTITUTO SOU DA PAZ · ONDE MORA A IMPUNIDADE (OUT/2025)')}
''', 'i06', kbo='50% 60%', dim=1.0))

s = 'v07'
H.append(scene(s, rail(3)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">GARGALO 2 · A POLÍCIA</div>
<div class="el h" data-flow="m:2" data-gap="44" data-a="slam" data-t="{W(s,'mais',0,-.15)}" data-shake="1" style="left:80px;width:900px;font-size:88px;color:#fff">A QUE <span class="hl">MAIS MATA</span> NO BRASIL</div>
<div class="el chartcard vz" data-flow="m:3" data-gap="30" data-a="fade" data-t="{W(s,'três',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:22px;color:#ddd">PARTE DAS MORTES VIOLENTAS DO ESTADO (2025)</div>
  {brow('AÇÃO POLICIAL', '28,7%', int(380*.287/.35), R, W(s,'três',0), lw=280)}</div>
<div class="el counter" data-flow="m:4" data-gap="40" data-minh="150" data-a="pop" data-t="{W(s,'mil',0,-.2)}" style="left:80px;width:920px"><span class="cnt" data-t="{W(s,'mil',0,-.1)}" data-d="1" data-from="0" data-to="1263" data-dec="0" data-thou="1" style="color:#fff"></span><b>CÂMERAS<br>CORPORAIS</b></div>
<div class="el stamp-r" data-flow="m:5" data-gap="60" data-a="stamp" data-t="{W(s,'sete',0,-.05)}" data-d=".35" data-r="-3" style="left:80px;white-space:nowrap">SÓ 7,5% EM USO</div>
{src('FBSP · ANUÁRIO 2026 · MP-BA, 15 UNIDADES INSPECIONADAS (OUT/2025)')}
''', 'i07', kbo='50% 55%'))

s = 'v08'
H.append(scene(s, rail(3)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">GARGALO 3 · O QUE TEM PROCESSO</div>
<div class="el glass" data-flow="m:2" data-gap="34" data-a="up" data-t="{W(s,'dez',0,-.2)}" style="left:80px;width:920px;padding:20px 30px">
  <div class="mono" style="font-size:22px;color:{Y}">PMs · OPERAÇÃO FOGO AMIGO (PF + MP-BA, 2024)</div>
  <div class="h" style="font-size:48px;color:#fff;margin-top:8px">10 PRESOS POR VENDER ARMAS A FACÇÃO</div></div>
<div class="el glass" data-flow="m:3" data-gap="26" data-a="up" data-t="{W(s,'respiradores',0,-.2)}" style="left:80px;width:920px;padding:20px 30px">
  <div class="mono" style="font-size:22px;color:{Y}">RUI COSTA · RESPIRADORES (R$ 48,7 MI, NADA ENTREGUE)</div>
  <div class="h" style="font-size:48px;color:#fff;margin-top:8px">TCU INOCENTOU · INQUÉRITO SEM ACUSAÇÃO</div></div>
<div class="el glass" data-flow="m:4" data-gap="26" data-a="up" data-t="{W(s,'wagner',0,-.2)}" style="left:80px;width:920px;padding:20px 30px">
  <div class="mono" style="font-size:22px;color:{Y}">JAQUES WAGNER · DELAÇÃO DA LAVA JATO</div>
  <div class="h" style="font-size:48px;color:#fff;margin-top:8px">ARQUIVADO NO STF (2019)</div></div>
{src('PF · CORREIO 2024 · TCU 2025 · STF/INQ 4325 · CORREIO DA MANHÃ 06/2026')}
''', 'i08', kbo='50% 75%', dim=1.0))

s = 'v09'
H.append(scene(s, rail(4)+f'''
<div class="el label gold" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">DÁ PRA CAIR? DÁ.</div>
<div class="el glass" data-flow="m:2" data-gap="34" data-a="up" data-t="{W(s,'pernambuco',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">PERNAMBUCO · PSB {CESQ}</div>
  <div class="h" style="font-size:56px;color:#fff;margin-top:8px">53 → 33,9 <span style="font-size:32px">(2007–2013)</span></div>
  <div class="vsub" data-a="fade" data-t="{W(s,'voltou',0,-.1)}">o governador saiu, o programa perdeu força: 57,2 em 2017</div></div>
<div class="el glass" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'pará',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">PARÁ · MDB {DIR}</div>
  <div class="h" style="font-size:56px;color:#fff;margin-top:8px">56,6 → 29,5 <span style="font-size:32px">(2018–2024)</span></div>
  <div class="vsub">obras e serviços nos bairros (TerPaz) + polícia</div></div>
<div class="el mono" data-flow="m:4" data-gap="30" data-a="fade" data-t="{W(s,'metade',0,.2)}" style="left:80px;font-size:24px;color:#ddd;width:900px;line-height:1.4">HOMICÍDIOS (PE) E MORTES VIOLENTAS (PA) POR 100 MIL</div>
{src('FBSP (GAZETA DO POVO 2019) · ANUÁRIO 2025 · DADOS 2023')}
''', 'i05', kbo='50% 50%'))

s = 'v10'
H.append(scene(s, rail(4)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">E A EDUCAÇÃO?</div>
<div class="el h" data-flow="m:2" data-gap="40" data-a="slam" data-t="{W(s,'quarto',0,-.15)}" style="left:80px;width:900px;font-size:84px;color:#fff">4º ESTADO EM <span class="hl">TEMPO INTEGRAL</span></div>
<div class="el sub" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'integral',0,-.1)}" style="left:80px;width:900px"><b>140 mil alunos</b>, 34% da rede estadual (Brasil: 26%)</div>
<div class="el glass vz" data-flow="m:4" data-gap="34" data-a="fade" data-t="{W(s,'nota',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:22px;color:#ddd">IDEB 2025 · ENSINO MÉDIO (BAHIA: +0,6 DESDE 2019)</div>
  {brow('BAHIA', '4,0', int(380*4.0/4.5), Y, W(s,'nota',0), lw=240)}
  {brow('NORDESTE', '4,3', int(380*4.3/4.5), WH, W(s,'nota',0,.2), lw=240)}
  {brow('BRASIL', '4,5', 380, WH, W(s,'nota',0,.4), lw=240)}</div>
<div class="el mono" data-flow="m:5" data-gap="30" data-a="fade" data-t="{W(s,'estudos',0,-.1)}" style="left:80px;font-size:24px;color:{Y};width:900px;line-height:1.4">+1 PONTO EM EDUCAÇÃO ≈ −25% HOMICÍDIOS NA CIDADE (ASSOCIAÇÃO, NÃO PROVA DE CAUSA)</div>
{src('CENSO ESCOLAR 2025 · IDEB 2025 · INSPER/INST. NATURA 2022')}
''', 'i14', kbo='50% 55%'))

s = 'v11'
H.append(scene(s, f'''
<div class="el label" data-flow="m:1" data-ftop="250" data-a="left" data-t=".05" style="left:80px">E NO NORTE?</div>
<div class="el glass" data-flow="m:2" data-gap="30" data-a="up" data-t="{W(s,'amapá',0,-.2)}" style="left:80px;width:920px;padding:20px 30px">
  <div class="mono" style="font-size:22px;color:{Y}">AMAPÁ · SOLIDARIEDADE {CDIR} EM 2025</div>
  <div class="brow"><span style="width:380px">MORTES VIOLENTAS</span><em style="font-size:40px">42,5 · 1º</em></div>
  <div class="brow" data-a="fade" data-t="{W(s,'letalidade',0,-.1)}"><span style="width:380px">LETALIDADE POLICIAL</span><em style="font-size:40px;color:{R}">17,1 · 1º</em></div></div>
<div class="el h" data-flow="m:3" data-gap="44" data-a="slam" data-t="{W(s,'marajó',0,-.15)}" style="left:80px;font-size:92px;color:#fff">MARAJÓ (PA)</div>
<div class="el glass" data-flow="m:4" data-gap="20" data-a="up" data-t="{W(s,'estupro',0,-.2)}" style="left:80px;width:920px;padding:20px 30px">
  <div class="mono" style="font-size:22px;color:{Y}">ESTUPRO DE VULNERÁVEL POR 100 MIL HAB.</div>
  <div class="brow"><span style="width:380px">MARAJÓ</span><em style="font-size:44px;color:{R}">69</em></div>
  <div class="brow"><span style="width:380px">BRASIL (2022)</span><em style="font-size:44px">28</em></div></div>
<div class="el sub" data-flow="m:5" data-gap="24" data-a="up" data-t="{W(s,'sete',0,-.2)}" style="left:80px;width:900px;font-size:42px"><b>73%</b> em situação de pobreza no CadÚnico (Brasil: 28%)</div>
{src('FBSP 2026 · MP-PA · RELATÓRIO CIDADANIA MARAJÓ (DEZ/2022)')}
''', 'i11', kbo='50% 60%'))

s = 'v12'
H.append(scene(s, rail(5)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">O QUE ESTÁ TRAVADO</div>
<div class="el glass" data-flow="m:2" data-gap="34" data-a="up" data-t="{W(s,'pec',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">PEC DA SEGURANÇA PÚBLICA</div>
  <div class="brow"><span style="width:300px">CÂMARA</span><em style="font-size:34px">APROVADA · MAR/2026</em></div>
  <div class="brow"><span style="width:300px">SENADO</span><em style="font-size:34px;color:{R}">AINDA EM ANÁLISE</em></div></div>
<div class="el glass" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'lei',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">LEI ANTIFACÇÃO · 24/03/2026</div>
  <div class="h" style="font-size:44px;color:#fff;margin-top:8px">✓ SANCIONADA PELO PRESIDENTE</div></div>
<div class="el mono" data-flow="m:4" data-gap="34" data-a="fade" data-t=".8" style="left:80px;font-size:24px;color:#ddd;line-height:1.5;width:900px">POLÍCIAS MILITAR E CIVIL: GOVERNADOR<br>PF, PRF, FRONTEIRAS E RIOS: UNIÃO</div>
{src('CÂMARA · SENADO (CCJ 14/10/2026) · LEI 15.358/2026 · CF ART. 144')}
''', 'i12', kbo='50% 60%'))

s = 'v13'
H.append(scene(s, f'''
<div class="el h" data-flow="m:1" data-ftop="250" data-a="slam" data-t="{W(s,'resumindo',0,-.1)}" style="left:80px;font-size:100px;color:#fff">RESUMINDO</div>
<div class="el glass" data-flow="m:2" data-gap="36" data-a="up" data-t="{W(s,'região',0,-.2)}" style="left:80px;width:920px">
  <div class="h" style="font-size:40px;color:#fff">REGIÃO E FACÇÕES <span style="color:{Y}">→ EXPLICAM O NÍVEL</span></div></div>
<div class="el glass" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'governo',0,-.2)}" style="left:80px;width:920px">
  <div class="h" style="font-size:40px;color:#fff">GOVERNO <span style="color:{R}">→ EXPLICA A DIFERENÇA</span></div>
  <div class="vsub" data-a="fade" data-t="{W(s,'investigar',0,-.1)}">investigar · controlar a polícia · manter os programas · educar</div></div>
<div class="el repost" data-flow="m:4" data-gap="44" data-a="slam" data-t="{W(s,'você',0,-.15)}" data-shake="1" style="left:80px;width:920px;font-size:62px">💬 O QUE VOCÊ COBRARIA DO PRÓXIMO MANDATO?<small>Jerônimo foi reeleito em 04/10/2026 (2027–2030)</small></div>
{src('TSE · FBSP · IPEA · SOU DA PAZ · MP-BA · RESUMO DESTE VÍDEO')}
''', 'i13', kbo='50% 60%'))

CSS = open(os.path.join(KIT, 'preview_kit/style.css')).read() + '''
.bigpair{display:flex;align-items:baseline;gap:22px;font-family:Rub;font-weight:900;color:#fff;height:200px}
.brow.hb span{font-size:28px}.brow.hb small{display:block;font-size:20px;margin-top:6px;color:#ddd;white-space:nowrap}.brow.hb small .ide{font-size:17px;padding:1px 7px;margin:0 4px}
.label .ide{font-size:22px;padding:2px 10px;margin-left:6px;vertical-align:1px}.glass .mono .ide{font-size:20px;padding:1px 8px;margin-left:6px}
.vz .brow{margin-top:20px}.glass.vz{padding:18px 30px 24px}
.counter b{font-size:44px;line-height:1.05}
'''
page = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Bahia e Norte</title>
<link rel="stylesheet" href="fx.css"><style>{CSS}</style></head><body><div id="stage">
{"".join(H)}
<div id="grain"></div><div id="foot">@tentandochegaratevoce</div></div>
<script>window.DUR={DUR:.2f};</script><script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script><script src="layout.js"></script></body></html>'''
open(os.path.join(KIT, 'bahia.html'), 'w').write(page)
print('ok', DUR)
