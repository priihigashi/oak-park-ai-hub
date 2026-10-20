"""Reel timeline: violência na Bahia e no Norte — culpa do PT ou estrutural? (v1, out/2026)
Gera ../bahia.html a partir de /home/claude/work/timeline.json (tempos por palavra da narração).
Imagens em ../assets/bn/iNN.jpg (IA, flux-1.1-pro, uma por cena, sem repetir)."""
import json, html, re, os
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open('/home/claude/work/timeline.json'))
S = {o['id']: o for o in TL}

def norm(w): return re.sub(r'[^\wÀ-ú]', '', w.lower())

# suaviza palavras empilhadas no mesmo instante (estimativa por caracteres)
for o in TL:
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
RAIL = ["2003", "2007", "2015", "2023", "VIZINHOS", "NORTE"]
def rail(active, t=.15):
    xs = [110+i*172 for i in range(6)]
    dots = ''.join(f'<div class="st{" on" if i==active else ""}{" past" if i<active else ""}" style="left:{x}px"><i></i><b>{y}</b></div>' for i, (x, y) in enumerate(zip(xs, RAIL)))
    return f'<div class="rail el" data-a="left" data-t="{t}" data-d=".35" style="left:0;top:150px"><div class="line"></div><div class="fill" style="width:{xs[active]-60}px"></div>{dots}</div>'

AIW = '<div class="el aiwarn" data-a="fade" data-t=".3" style="left:80px;top:1700px">imagens ilustrativas geradas por IA</div>'
def src(txt, t=.6, o=None):
    oo = f' data-o="{o}"' if o is not None else ''
    return f'<div class="el src" data-a="fade" data-t="{t}"{oo} style="left:80px;top:1450px">{txt}</div>'

def scene(sid, inner, bg, kb=1.10, kbo='50% 45%', dim=0.92, inmode='cut', tint=None):
    o = S[sid]
    b = f'<img class="bgimg" src="assets/bn/{bg}.jpg" data-kb="{kb}" data-kbo="{kbo}">'
    if tint: b += f'<div class="tintc" style="background:{tint}"></div>'
    b += f'<div class="shadeg" style="opacity:{dim}"></div>'
    return f'<section class="scene" data-s="{o["s"]}" data-e="{o["e"]}" data-in="{inmode}" data-theme="dark">{b}<div class="safe">{inner}{AIW}</div>{kar(sid)}</section>\n'

def brow(lab, val, w, color, t, sub=''):
    sb = f'<small>{sub}</small>' if sub else ''
    return (f'<div class="brow hb"><span>{lab}{sb}</span><div class="bar bfill" data-t="{t}" data-d=".7" data-to="{w}" style="background:{color}"></div>'
            f'<em>{val}</em></div>')

H = []
Y, R, WH = '#FFD34D', '#FF4A3D', '#F2ECE0'
# ---- v01 gancho
s = 'v01'
H.append(scene(s, f'''
<div class="el label gold" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">BAHIA · PT <i class="ide esq">ESQUERDA</i> DESDE 2007</div>
<div class="el h" data-flow="m:2" data-gap="44" data-a="slam" data-t="{W(s,'mais',0,-.15)}" data-shake="1" style="left:80px;width:930px;font-size:112px;color:#fff">ONDE MAIS SE <span class="hl">MATA</span> NO BRASIL</div>
<div class="el h redtxt" data-flow="m:3" data-gap="40" data-a="slam" data-t="{W(s,'culpa',0,-.1)}" data-d=".35" style="left:80px;font-size:130px">CULPA DO PT?</div>
<div class="el cta" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'bora',0)}" style="left:80px">OS DADOS, DOA A QUEM DOER ↓</div>
{src('IDEOLOGIA DOS PARTIDOS: BOLOGNESI, RIBEIRO E CODATO (DADOS, 2023)')}
''', 'i01', kbo='50% 70%'))
# ---- v02 número
s = 'v02'
H.append(scene(s, f'''
<div class="el label" data-flow="m:1" data-ftop="320" data-a="left" data-t=".1" style="left:80px">MORTES VIOLENTAS INTENCIONAIS · 2025</div>
<div class="el h cnt" data-flow="m:2" data-gap="40" data-t="{W(s,'cinco',1,-.2)}" data-d="1.4" data-from="0" data-to="5473" data-dec="0" data-thou="1" style="left:80px;font-size:250px;color:#fff;width:880px;line-height:.85;height:215px"></div>
<div class="el sub" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'mortes',0,-.2)}" style="left:80px;width:900px">pessoas mortas na Bahia em um ano. <b>Nº 1 do país em números absolutos.</b></div>
<div class="el glass" data-flow="m:4" data-gap="50" data-a="up" data-t="{W(s,'nenhum',0,-.1)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">OS PRÓXIMOS DA LISTA</div>
  <div class="brow"><span style="width:420px">RIO DE JANEIRO</span><em>3.890</em></div>
  <div class="brow"><span style="width:420px">SÃO PAULO</span><em>3.615</em></div></div>
{src('FBSP · ANUÁRIO BRASILEIRO DE SEGURANÇA PÚBLICA 2026 (DADOS DE 2025)', W(s,'mortes',0,-.2))}
''', 'i02', kbo='50% 55%'))
# ---- v03 painel geral
s = 'v03'
xs = [110+i*172 for i in range(6)]
st = ''.join(f'<div class="el st big" data-a="pop" data-t="{.05+i*.12:.2f}" style="left:{x}px;top:900px"><i></i><b>{y}</b></div>' for i, (x, y) in enumerate(zip(xs, RAIL)))
H.append(scene(s, f'''
<div class="el h" data-a="slam" data-t="0" data-d=".3" style="left:80px;top:330px;font-size:140px;color:#fff;width:880px">GOVERNO<br><span style="color:{Y}">POR GOVERNO.</span></div>
<div class="el bigline bar" data-t=".05" data-d=".7" data-to="860" style="left:110px;top:918px"></div>
{st}
''', 'i03', dim=1.0, kb=1.15))
# ---- v04 Souto
s = 'v04'
H.append(scene(s, rail(0)+f'''
<div class="el label slate" data-flow="m:1" data-ftop="300" data-a="left" data-t=".1" style="left:80px">2003–2006 · PAULO SOUTO · PFL <i class="ide dir">EXTREMA-DIREITA</i></div>
<div class="el mono" data-flow="m:2" data-gap="50" data-a="fade" data-t="{W(s,'taxa',0,-.2)}" style="left:80px;font-size:26px;color:#ddd">HOMICÍDIOS POR 100 MIL HABITANTES</div>
<div class="el bigpair" data-flow="m:3" data-gap="14" data-a="up" data-t="{W(s,'quinze',0,-.2)}" style="left:80px;width:930px">
  <span class="old">15,8</span><span class="arr">→</span><span class="cnt" data-t="{W(s,'vinte',0,-.1)}" data-d=".9" data-from="15.8" data-to="23.1" data-dec="1">15,8</span></div>
<div class="el mono" data-flow="m:4" data-gap="10" data-a="fade" data-t="{W(s,'vinte',0,.2)}" style="left:80px;font-size:24px;color:#ddd">2003 → 2006 · +46% EM QUATRO ANOS</div>
<div class="el h" data-flow="m:5" data-gap="60" data-a="slam" data-t="{W(s,'alta',0,-.1)}" style="left:80px;width:930px;font-size:84px;color:{Y}">A ALTA COMEÇOU ANTES DO PT.</div>
{src('TAXA PADRONIZADA · CIÊNC. SAÚDE COLETIVA 2014 · IDEOLOGIA: DADOS 2023')}
''', 'i04', kbo='50% 70%'))
# ---- v05 Wagner
s = 'v05'
H.append(scene(s, rail(1)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".1" style="left:80px">2007–2014 · JAQUES WAGNER · PT <i class="ide esq">ESQUERDA</i></div>
<div class="el mono" data-flow="m:2" data-gap="50" data-a="fade" data-t="{W(s,'chega',0,-.2)}" style="left:80px;font-size:26px;color:#ddd">HOMICÍDIOS POR 100 MIL HABITANTES</div>
<div class="el bigpair" data-flow="m:3" data-gap="14" data-a="up" data-t="{W(s,'chega',0,-.1)}" style="left:80px;width:930px">
  <span class="old">24,1</span><span class="arr">→</span><span class="cnt" data-t="{W(s,'trinta',0,-.1)}" data-d=".9" data-from="24.1" data-to="38.9" data-dec="1">24,1</span></div>
<div class="el mono" data-flow="m:4" data-gap="10" data-a="fade" data-t="{W(s,'trinta',0,.3)}" style="left:80px;font-size:24px;color:#ddd">2007 → 2010</div>
<div class="el glass" data-flow="m:5" data-gap="60" data-a="up" data-t="{W(s,'pacto',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">2011 · PACTO PELA VIDA</div>
  <div class="h" style="font-size:56px;color:#fff;margin-top:10px">SEGUROU A ALTA.</div>
  <div class="h" data-a="fade" data-t="{W(s,'mas',0,-.05)}" style="font-size:56px;color:{R};margin-top:6px">NÃO VIROU O JOGO.</div></div>
{src('CIÊNC. SAÚDE COLETIVA 2014 · UFPB 2022 · IDEOLOGIA: DADOS 2023')}
''', 'i05', kbo='50% 50%'))
# ---- v06 Rui
s = 'v06'
H.append(scene(s, rail(2)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".1" style="left:80px">2015–2022 · RUI COSTA · PT <i class="ide esq">ESQUERDA</i></div>
<div class="el h" data-flow="m:2" data-gap="50" data-a="slam" data-t="{W(s,'pico',0,-.1)}" style="left:80px;font-size:96px;color:#fff">PICO EM 2017</div>
<div class="el h cnt" data-flow="m:3" data-gap="20" data-t="{W(s,'sete',0,-.1)}" data-d="1.3" data-from="0" data-to="7478" data-dec="0" data-thou="1" style="left:80px;font-size:220px;color:{R};width:880px;line-height:.85;height:190px"></div>
<div class="el sub" data-flow="m:4" data-gap="20" data-a="up" data-t="{W(s,'homicídios',0,-.2)}" style="left:80px">homicídios em um ano · 48,8 por 100 mil</div>
<div class="el stamp-r" data-flow="m:5" data-gap="50" data-a="stamp" data-t="{W(s,'ponto',0)}" data-d=".35" data-r="-3" style="left:80px;white-space:nowrap">PONTO NEGATIVO</div>
<div class="el sub" data-flow="m:6" data-gap="30" data-a="up" data-t="{W(s,'nove',0,-.1)}" style="left:80px;width:920px;font-size:42px"><b>2015 a 2023:</b> o estado com mais homicídios do Brasil, <b>61.249</b></div>
{src('IPEA/FBSP · ATLAS DA VIOLÊNCIA 2019 E 2025 · IDEOLOGIA: DADOS 2023')}
''', 'i06', kbo='50% 60%', dim=0.97))
# ---- v07 Jerônimo
s = 'v07'
H.append(scene(s, rail(3)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".1" style="left:80px">2023– · JERÔNIMO RODRIGUES · PT <i class="ide esq">ESQUERDA</i></div>
<div class="el chip gold" data-flow="m:2" data-gap="36" data-a="pop" data-t="{W(s,'caíram',0,-.1)}" style="left:80px">▼ 9,6% NAS MORTES VIOLENTAS EM 2025</div>
<div class="el h" data-flow="m:3" data-gap="56" data-a="slam" data-t="{W(s,'polícia',0,-.1)}" data-shake="1" style="left:80px;width:930px;font-size:96px;color:#fff">A POLÍCIA QUE <span class="hl">MAIS MATA</span> NO BRASIL</div>
<div class="el counter" data-flow="m:4" data-gap="40" data-minh="150" data-a="pop" data-t="{W(s,'mil',0,-.2)}" style="left:80px;width:920px"><span class="cnt" data-t="{W(s,'mil',0,-.1)}" data-d="1.1" data-from="0" data-to="1570" data-dec="0" data-thou="1"></span><b>MORTES EM<br>AÇÃO POLICIAL</b></div>
<div class="el glass" data-flow="m:5" data-gap="40" data-a="up" data-t="{W(s,'quase',1,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">PARTE DAS MORTES VIOLENTAS DA BAHIA EM 2025</div>
  {brow('POLÍCIA', '28,7%', int(560*.287/.35), R, W(s,'quase',1))}
  <div class="mono" style="font-size:20px;color:#ddd;margin-top:10px">QUEM COMANDA A PM É O GOVERNADOR</div></div>
{src('FBSP · ANUÁRIO 2026 · IDEOLOGIA: DADOS 2023')}
''', 'i07', kbo='50% 55%'))
# ---- v08 polícia e corrupção
s = 'v08'
H.append(scene(s, rail(3)+f'''
<div class="el label slate" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">O QUE TEM PROCESSO</div>
<div class="el glass" data-flow="m:2" data-gap="34" data-a="up" data-t=".1" style="left:80px;width:920px">
  <div class="mono" style="font-size:22px;color:{Y}">OPERAÇÃO FOGO AMIGO · PF + MP-BA (2024)</div>
  <div class="h" style="font-size:52px;color:#fff;margin-top:8px">10 PMs PRESOS POR VENDER ARMAS A FACÇÃO</div>
  <div class="vsub">armas apreendidas e de CACs iam para o BDM</div></div>
<div class="el glass" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'respiradores',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:22px;color:{Y}">RESPIRADORES · CONSÓRCIO NORDESTE (2020)</div>
  <div class="h" style="font-size:52px;color:#fff;margin-top:8px">R$ 48,7 MI PAGOS · 300 NUNCA ENTREGUES</div>
  <div class="vsub">Rui Costa presidia o consórcio</div></div>
<div class="el glass" data-flow="m:4" data-gap="30" data-a="up" data-t="{W(s,'tcu',0,-.2)}" style="left:80px;width:920px;padding:18px 30px">
  <div class="brow" style="margin-top:0"><span style="width:300px;font-size:26px">TCU · ABR/2025</span><em style="font-size:34px">ARQUIVOU PARA ELE (5 × 2)</em></div>
  <div class="brow" data-a="fade" data-t="{W(s,'acusação',0,-.2)}"><span style="width:300px;font-size:26px">INQUÉRITO PF</span><em style="font-size:34px;color:{Y}">SEGUE · SEM ACUSAÇÃO</em></div></div>
{src('PF · CORREIO 2024 · TCU · CORREIO DA MANHÃ 06/2026')}
''', 'i08', kbo='50% 75%', dim=0.97))
# ---- v09 vizinhos
s = 'v09'
mx = 36.8; FW = 400
rows = [("BAHIA", "PT", "esq", "ESQUERDA", 36.8, R, 'vizinhos'), ("CEARÁ", "PT", "esq", "ESQUERDA", 34.7, WH, 'ceará'), ("ALAGOAS", "MDB", "dir", "DIREITA", 33.1, WH, 'alagoas'),
        ("PERNAMBUCO", "PSD", "dir", "DIREITA", 33.0, WH, 'pernambuco'), ("PIAUÍ", "PT", "esq", "ESQUERDA", 17.1, Y, 'piauí')]
bb = ''.join(brow(n, f'{v:.1f}'.replace('.', ','), int(FW*v/mx), c, W(s, w, 0, -.15), sub=f'{p} <i class="ide {k}">{lab}</i>') for n, p, k, lab, v, c, w in rows)
H.append(scene(s, rail(4)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">MORTES VIOLENTAS POR 100 MIL · 2025</div>
<div class="el chartcard vz" data-flow="m:2" data-gap="34" data-a="fade" data-t=".1" style="left:80px;width:930px">{bb}
  <div class="mono" data-a="fade" data-t="{W(s,'piauí',0)}" style="font-size:22px;color:#ddd;margin-top:16px">MÉDIA DO BRASIL: 19,1 · NORDESTE: 31,6</div></div>
<div class="el h" data-flow="m:3" data-gap="50" data-a="slam" data-t="{W(s,'partido',0,-.1)}" style="left:80px;width:930px;font-size:80px;color:{Y}">PARTIDO SOZINHO NÃO EXPLICA.</div>
{src('FBSP · ANUÁRIO 2026 · IDEOLOGIA: BOLOGNESI ET AL. (DADOS, 2023)')}
''', 'i09', kbo='50% 60%', dim=1.0))
# ---- v10 estrutural
s = 'v10'
H.append(scene(s, f'''
<div class="el label gold" data-flow="m:1" data-ftop="250" data-a="left" data-t=".05" style="left:80px">O QUE É ESTRUTURAL</div>
<div class="el h" data-flow="m:2" data-gap="36" data-a="slam" data-t="{W(s,'facções',0,-.2)}" style="left:80px;width:930px;font-size:92px;color:#fff">O ESTADO COM <span class="hl">MAIS FACÇÕES</span> DO PAÍS</div>
<div class="el glass" data-flow="m:3" data-gap="40" data-a="up" data-t="{W(s,'bdm',0,-.2)}" style="left:80px;width:920px">
  <div class="brow" style="margin-top:0"><span style="width:250px">BDM</span><em style="font-size:34px">NASCEU EM PRESÍDIO DE SALVADOR (2015)</em></div>
  <div class="brow"><span style="width:250px">+ PCC</span><em style="font-size:34px">ALIADO: ROTAS E ARMAS</em></div>
  <div class="brow" data-a="fade" data-t="{W(s,'comando',0,-.1)}"><span style="width:250px;color:{R}">× CV</span><em style="font-size:34px;color:{R}">CHEGOU DISPUTANDO TERRITÓRIO</em></div></div>
<div class="el sub" data-flow="m:4" data-gap="40" data-a="up" data-t="{W(s,'corredor',0,-.2)}" style="left:80px;width:920px">rodovias e pelo menos <b>6 portos</b>: corredor do tráfico para o Nordeste inteiro</div>
{src('FBSP · IPEA (ATLAS 2025) · SENAPPEN · CORREIO · BNEWS')}
''', 'i10', kbo='50% 60%'))
# ---- v11 Norte
s = 'v11'
H.append(scene(s, rail(5)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".05" style="left:80px">NORTE</div>
<div class="el glass" data-flow="m:2" data-gap="30" data-a="up" data-t="{W(s,'amapá',0,-.2)}" style="left:80px;width:920px;padding:18px 30px">
  <div class="brow" style="margin-top:0"><span style="width:330px">AMAPÁ</span><em style="font-size:34px">42,5 · MAIOR TAXA DO PAÍS</em></div>
  <div class="brow" data-a="fade" data-t="{W(s,'letalidade',0,-.1)}"><span style="width:330px"></span><em style="font-size:34px;color:{R}">POLÍCIA MAIS LETAL: 17,1</em></div>
  <div class="brow" data-a="fade" data-t="{W(s,'pará',0,-.1)}"><span style="width:330px">PARÁ</span><em style="font-size:34px;color:{Y}">56,6 → 29,5 (2018–2024)</em></div></div>
<div class="el h" data-flow="m:3" data-gap="40" data-a="slam" data-t="{W(s,'marajó',0,-.15)}" style="left:80px;font-size:92px;color:#fff">MARAJÓ (PA)</div>
<div class="el glass" data-flow="m:4" data-gap="20" data-a="up" data-t="{W(s,'estupro',0,-.2)}" style="left:80px;width:920px;padding:18px 30px">
  <div class="mono" style="font-size:22px;color:{Y}">ESTUPRO DE VULNERÁVEL POR 100 MIL HABITANTES</div>
  <div class="brow"><span style="width:330px">MARAJÓ</span><em style="font-size:44px;color:{R}">69</em></div>
  <div class="brow"><span style="width:330px">BRASIL (2022)</span><em style="font-size:44px">28</em></div></div>
<div class="el sub" data-flow="m:5" data-gap="24" data-a="up" data-t="{W(s,'sete',0,-.2)}" style="left:80px;width:920px;font-size:42px"><b>73%</b> em situação de pobreza no CadÚnico (Brasil: 28%)</div>
{src('FBSP 2025/2026 · MP-PA · RELATÓRIO CIDADANIA MARAJÓ (DEZ/2022)')}
''', 'i11', kbo='50% 60%'))
# ---- v12 estado x união
s = 'v12'
H.append(scene(s, f'''
<div class="el label gold" data-flow="m:1" data-ftop="260" data-a="left" data-t=".05" style="left:80px">QUEM CUIDA DE QUÊ</div>
<div class="el glass" data-flow="m:2" data-gap="34" data-a="up" data-t=".1" style="left:80px;width:920px">
  <div class="h" style="font-size:54px;color:{Y}">GOVERNADOR</div>
  <div class="vsub" style="font-size:36px;margin-top:10px">Polícia Militar · Polícia Civil · presídios do estado</div></div>
<div class="el glass" data-flow="m:3" data-gap="26" data-a="up" data-t="{W(s,'fronteira',0,-.2)}" style="left:80px;width:920px">
  <div class="h" style="font-size:54px;color:#fff">UNIÃO</div>
  <div class="vsub" style="font-size:36px;margin-top:10px">Polícia Federal · PRF · fronteiras e rios · fundo nacional</div></div>
<div class="el mono" data-flow="m:4" data-gap="34" data-a="fade" data-t="{W(s,'união',0,-.1)}" style="left:80px;font-size:24px;color:#ddd;line-height:1.4;width:920px">PEC DA SEGURANÇA: APROVADA NA CÂMARA (MAR/2026), AGUARDA O SENADO</div>
{src('CONSTITUIÇÃO, ART. 144 · CÂMARA DOS DEPUTADOS · SENADO (CCJ, 14/10/2026)')}
''', 'i12', kbo='50% 60%'))
# ---- v13 fechamento
s = 'v13'
H.append(scene(s, f'''
<div class="el h" data-flow="m:1" data-ftop="240" data-a="slam" data-t="{W(s,'culpa',0,-.1)}" style="left:80px;font-size:120px;color:#fff">CULPA DO PT?</div>
<div class="el glass" data-flow="m:2" data-gap="40" data-a="up" data-t="{W(s,'explosão',0,-.2)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{Y}">ESTRUTURAL</div>
  <div class="h" style="font-size:48px;color:#fff;margin-top:8px">A ALTA FOI REGIONAL E COMEÇOU ANTES</div></div>
<div class="el glass" data-flow="m:3" data-gap="26" data-a="up" data-t="{W(s,'mas',0,-.15)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:{R}">DO GOVERNO</div>
  <div class="h" style="font-size:48px;color:#fff;margin-top:8px">19 ANOS NO PODER E A POLÍCIA QUE MAIS MATA</div></div>
<div class="el repost" data-flow="m:4" data-gap="44" data-a="slam" data-t="{W(s,'você',0,-.15)}" data-shake="1" style="left:80px;width:920px;font-size:66px">💬 O QUE VOCÊ COBRARIA DO PRÓXIMO MANDATO?<small>Jerônimo foi reeleito em 04/10/2026 (2027–2030)</small></div>
{src('TSE · FBSP · IPEA · RESUMO DESTE VÍDEO')}
''', 'i13', kbo='50% 60%'))

CSS = open(os.path.join(KIT, 'preview_kit/style.css')).read() + '''
.bigpair{display:flex;align-items:baseline;gap:22px;font-family:Rub;font-weight:900;color:#fff;height:200px;text-shadow:0 6px 30px rgba(0,0,0,.5)}
.bigpair .old{font-size:120px;color:rgba(242,236,224,.6)}.bigpair .arr{font-size:80px}.bigpair .cnt{font-size:200px;color:#FFD34D;line-height:.85}
.brow.hb span{width:330px;font-size:28px;flex:0 0 330px}.brow.hb small{display:block;font-size:20px;margin-top:6px;color:#ddd}.brow.hb small .ide{font-size:18px;padding:1px 8px;margin-left:6px}
.label .ide{font-size:22px;padding:2px 10px;margin-left:6px;vertical-align:1px}
.brow .pt{font-style:normal;font-size:20px;margin-left:8px;padding:2px 8px;border-radius:5px;background:rgba(242,236,224,.16);color:#F2ECE0}
.vz .brow{margin-top:20px}
.counter b{font-size:44px;line-height:1.05}
'''
page = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Bahia e Norte</title>
<link rel="stylesheet" href="fx.css"><style>{CSS}</style></head><body><div id="stage">
{"".join(H)}
<div id="grain"></div><div id="foot">@tentandochegaratevoce</div></div>
<script>window.DUR={DUR:.2f};</script><script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script><script src="layout.js"></script></body></html>'''
open(os.path.join(KIT, 'bahia.html'), 'w').write(page)
print('ok', DUR)
