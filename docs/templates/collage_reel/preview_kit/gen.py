import json,html,re
TL=json.load(open('/home/claude/work/build/timeline.json'))
S={o['id']:o for o in TL}
def norm(w): return re.sub(r'[^\wÀ-ú]','',w.lower())
def W(sid,tok,n=0,off=0.0):
    for mode in ('eq','sw'):
        k=0
        for w,t in S[sid]['words']:
            ok=norm(w)==norm(tok) if mode=='eq' else norm(w).startswith(norm(tok))
            if ok:
                if k==n: return round(t+off,2)
                k+=1
    raise SystemExit(f'word {tok} not in {sid}')
def kar(sid,per=7):
    ws=S[sid]['words']; toks=[]; n=0
    for i,(w,t) in enumerate(ws):
        if i and (n>=per or (re.search(r'[.?!:;]$',ws[i-1][0]) and n>=3)): toks.append('/'); n=0
        toks.append(f"{html.escape(w.replace(':',''))}:{t}"); n+=1
    return f'<div class="kar karfull el" data-words="{" ".join(toks)}" style="left:130px;top:1468px;width:820px"></div>'
DUR=TL[-1]['e']
RAIL=["2015","2019","ABR/24","OUT/24","2026","PARADO"]
def rail(active,t=.15):
    xs=[110+i*172 for i in range(6)]
    dots=''.join(f'<div class="st{" on" if i==active else ""}{" past" if i<active else ""}" style="left:{x}px"><i></i><b>{y}</b></div>' for i,(x,y) in enumerate(zip(xs,RAIL)))
    return f'<div class="rail el" data-a="left" data-t="{t}" data-d=".35" style="left:0;top:150px"><div class="line"></div><div class="fill" style="width:{xs[active]-60}px"></div>{dots}</div>'
def scene(sid,inner,bg=None,tint=None,kb=1.10,kbo='50% 40%',extra='',dim=0.80,inmode='cut'):
    o=S[sid]; b=''
    if bg:
        b+=f'<img class="bgimg" src="assets/qa/{bg}.jpg" data-kb="{kb}" data-kbo="{kbo}">'
    if tint:
        b+=f'<div class="tintc" style="background:{tint}"></div>'
    b+=f'<div class="shadeg" style="opacity:{dim}"></div>'
    return f'<section class="scene" data-s="{o["s"]}" data-e="{o["e"]}" data-in="{inmode}" data-theme="dark">{b}<div class="safe">{inner}</div>{kar(sid)}{extra}</section>\n'
H=[]
# ---- S1 hook
s='v01'
H.append(scene(s,f'''
<div class="el aiwarn" data-a="fade" data-t=".3" style="left:80px;top:1700px">imagens ilustrativas geradas por IA</div>
<div class="el letter" data-flow="m:1" data-ftop="260" data-a="drop" data-t=".05" data-d=".6" data-r="-3" style="left:80px;width:900px">
  <div class="hand" style="font-size:96px">Querida amiga,</div>
  <div class="hand" style="font-size:52px;color:#444;margin-top:6px">te mandaram isso no grupo:</div>
</div>
<div class="el h" data-flow="m:2" data-gap="70" data-a="slam" data-t="{W(s,'vetou',0,-.1)}" data-d=".4" data-shake="1" style="left:80px;width:930px;font-size:118px;color:#fff">"VETOU A <span class="hl">SAIDINHA</span> PRA ESTUPRADOR"</div>
<div class="el h redtxt" data-flow="m:3" data-a="left" data-t="{W(s,'feminicídio',0,-.5)}" style="left:80px;width:930px;font-size:76px">"E NINGUÉM ENDURECEU A PENA"</div>
<div class="el cta" data-flow="m:4" data-a="up" data-t="{W(s,'vamos')}" style="left:80px">VAMOS AOS FATOS ↓</div>
''',bg='w_gate',dim=0.87,kbo='50% 60%'))
# ---- S2
s='v02'
H.append(scene(s,f'''
<div class="el letter" data-flow="m:1" data-ftop="260" data-a="up" data-t=".1" data-r="2" style="left:80px;width:900px"><div class="hand" style="font-size:80px">Eu também tô preocupada.</div></div>
<div class="el h cnt" data-flow="m:2" data-gap="90" data-t="{W(s,'mil',0,-.2)}" data-d="1.4" data-from="0" data-to="1571" data-dec="0" data-thou="1" style="left:80px;font-size:250px;color:#fff;width:950px;line-height:.85;height:215px"></div>
<div class="el sub" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'mulheres',0,-.3)}" style="left:80px;width:900px">mulheres vítimas de feminicídio no Brasil em 2025</div>
<div class="el h" data-flow="m:4" data-a="slam" data-t="{W(s,'mentira',0,-.25)}" data-d=".35" style="left:80px;font-size:84px;color:#FFD34D">SEM CAIR EM MENTIRA.</div>
<div class="el src" data-a="fade" data-t="{W(s,'mulheres',0)}" style="left:80px;top:1450px">FBSP · ANUÁRIO BRASILEIRO DE SEGURANÇA PÚBLICA 2026</div>
<div class="el aiwarn" data-a="fade" data-t=".3" style="left:80px;top:1700px">imagens ilustrativas geradas por IA</div>
''',bg='w_park',dim=0.87))
# ---- S3 overview rail
s='v03'
xs=[110+i*172 for i in range(6)]
st=''.join(f'<div class="el st big" data-a="pop" data-t="{.05+i*.1:.2f}" style="left:{x}px;top:900px"><i></i><b>{y}</b></div>' for i,(x,y) in enumerate(zip(xs,RAIL)))
H.append(scene(s,f'''
<div class="el h" data-a="slam" data-t="0" data-d=".3" style="left:80px;top:540px;font-size:150px;color:#fff;width:950px">AS LEIS,<br><span style="color:#FFD34D">NA ORDEM.</span></div>
<div class="el bigline bar" data-t=".05" data-d=".6" data-to="860" style="left:110px;top:918px"></div>
{st}
''',bg='w_bus2',tint='#0E0D0B',dim=1.00,kb=1.15))
# ---- S4 2015
s='v04'
H.append(scene(s,rail(0)+f'''
<div class="el label" data-flow="m:1" data-ftop="300" data-a="left" data-t=".2" style="left:80px">09/03/2015 · LEI 13.104 · GOVERNO DILMA</div>
<div class="el h" data-flow="m:2" data-gap="18" data-a="slam" data-t="{W(s,'feminicídio',0,-.2)}" style="left:80px;width:940px;font-size:120px;color:#fff">O FEMINICÍDIO<br><span class="hl">GANHA NOME</span></div>
<div class="el sub" data-flow="m:3" data-gap="24" data-a="up" data-t="{W(s,'nome',0)}" style="left:80px">crime hediondo · pena de 12 a 30 anos</div>
<div class="el paper" data-flow="m:4" data-gap="50" data-a="pop" data-t="{W(s,'naquele',0)}" data-o="{W(s,'quarenta',0,-.35)}" data-r="-2" style="left:80px;width:860px">
  <div class="mono" style="font-size:26px;color:#666">BOLETIM DE OCORRÊNCIA · ANTES</div>
  <div class="h" style="font-size:78px;color:#111;margin-top:10px"><s class="strike">HOMICÍDIO COMUM</s></div></div>
<div class="el stamp-g" data-flow="m:4" data-nosize="1" data-dy="60" data-a="stamp" data-t="{W(s,'registrados',0)}" data-d=".35" data-r="-6" data-o="{W(s,'quarenta',0,-.35)}" style="left:200px">FEMINICÍDIO</div>
<div class="el chartcard" data-flow="m:4" data-a="up" data-t="{W(s,'quarenta',0,-.3)}" data-o="{W(s,'total',0,-.25)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:#ddd">ASSASSINATOS DE MULHERES REGISTRADOS COMO FEMINICÍDIO</div>
  <div class="brow"><span>2015</span><div class="bar bfill" data-t="{W(s,'quarenta',0,-.2)}" data-d=".6" data-to="{int(640*0.094/0.444)}" style="background:#9aa7b8"></div><em>9 em 100</em></div>
  <div class="brow"><span>2025</span><div class="bar bfill" data-t="{W(s,'quarenta',0)}" data-d=".7" data-to="640" style="background:#FFD34D"></div><em>44 em 100</em></div></div>
<div class="el chartcard" data-flow="m:4" data-a="up" data-t="{W(s,'total',0,-.1)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:#ddd">TOTAL DE MULHERES ASSASSINADAS NO BRASIL · 2023 → 2024</div>
  <div style="display:flex;align-items:baseline;gap:24px;margin-top:10px;font-family:Rub;font-weight:900;color:#fff;height:120px">
    <span style="font-size:70px;color:#9aa7b8">3.903</span><span style="font-size:50px">→</span><span class="cnt" data-t="{W(s,'caiu',0,-.2)}" data-d=".9" data-from="3903" data-to="3642" data-dec="0" data-thou="1" style="font-size:110px;color:#FFD34D"></span><span style="font-size:50px;color:#FFD34D">−6,7%</span></div>
  <div class="vchart"><div class="vcol"><b>3.806</b><i style="height:146px;background:#3156D3"></i><span>2022</span><small>BOLSONARO</small></div><div class="vcol"><b>3.903</b><i style="height:150px;background:#9aa7b8"></i><span>2023</span><small>GOVERNO ATUAL 🦑</small></div><div class="vcol"><b>3.642</b><i style="height:139px;background:#FFD34D"></i><span>2024</span><small>GOVERNO ATUAL 🦑</small></div></div></div>
<div class="el h" data-flow="m:5" data-gap="30" data-a="left" data-t="{W(s,'parte',0,-.1)}" data-o="{W(s,'total',0,-.25)}" style="left:80px;width:930px;font-size:56px;color:#FFD34D">PARTE É REGISTRO.<br>PARTE É VIOLÊNCIA REAL.</div>
<div class="el h redtxt" data-flow="m:5" data-gap="30" data-a="left" data-t="{W(s,'dentro',0,-.1)}" style="left:80px;width:930px;font-size:62px;white-space:nowrap">DENTRO DE CASA, NÃO CAIU.</div>
<div class="el src" data-a="fade" data-t="{W(s,'quarenta',0,-.3)}" data-o="{W(s,'total',0,-.25)}" style="left:80px;top:1450px">FBSP · RETRATO DOS FEMINICÍDIOS (MAR/2026) · ANUÁRIO 2026</div>
<div class="el src" data-a="fade" data-t="{W(s,'total',0,-.1)}" style="left:80px;top:1450px">IPEA/FBSP · ATLAS DA VIOLÊNCIA 2026 (MINISTÉRIO DA SAÚDE)</div>
''',bg='w_box',dim=0.97))
# ---- S5 2019 Bolsonaro
s='v05'
H.append(scene(s,rail(1)+f'''
<div class="el label slate" data-flow="m:1" data-ftop="300" data-a="left" data-t=".2" style="left:80px">24/12/2019 · LEI 13.964 · PACOTE ANTICRIME</div>
<div class="el webdark" data-flow="m:2" data-gap="40" data-a="drop" data-t=".35" data-d=".55" data-r="1" style="left:80px;width:900px">
    <div class="ini">JB</div>
    <div><div class="mono" style="font-size:24px;color:#FFD34D">DIÁRIO OFICIAL · SANCIONADO POR</div><div class="h" style="font-size:66px;color:#fff;text-shadow:none">JAIR BOLSONARO</div></div></div>
<div class="el sub" data-flow="m:3" data-gap="60" data-a="up" data-t="{W(s,'saidinha',0,-.1)}" style="left:80px;width:920px;font-size:50px;text-wrap:balance">saidinha proibida só pra crime hediondo</div>
<div class="el h" data-flow="m:4" data-gap="10" data-a="slam" data-t="{W(s,'com',0,-.05)}" data-shake="1" style="left:80px;font-size:150px;color:#fff">COM <span class="hl">MORTE</span></div>
<div class="el stamp-r" data-flow="m:5" data-gap="34" data-a="stamp" data-t="{W(s,'estuprador',0)}" data-d=".35" data-r="-3" style="left:80px;font-size:48px;white-space:nowrap">ESTUPRADOR AINDA PODIA SAIR</div>
<div class="el sub" data-flow="m:6" data-a="up" data-t="{W(s,'ficou',0,-.2)}" style="left:80px;font-size:42px">pena do feminicídio: <b>12 a 30 anos, ficou igual</b></div>
<div class="el src" data-a="fade" data-t=".8" style="left:80px;top:1450px">LEI 13.964/2019, ART. 122 §2º LEP · AGÊNCIA SENADO 26/12/2019</div>
''',bg='w_uber',tint='#3B5470',dim=0.95,kb=1.12))
# ---- S6 vetos 2019
s='v06'
H.append(scene(s,rail(1,0)+f'''
<div class="el label slate" data-flow="m:1" data-ftop="300" data-a="left" data-t=".1" style="left:80px">2019 · BOLSONARO VETOU DUAS PROTEÇÕES</div>
<div class="el glass" data-flow="m:2" data-gap="34" data-a="up" data-t="{W(s,'hospital',0,-.3)}" style="left:80px;width:920px"><div class="mono" style="font-size:22px;color:#FFD34D">PL 2538/2019 · VETO TOTAL</div><div class="h" style="font-size:48px;color:#fff;margin-top:8px">HOSPITAL TERIA QUE AVISAR A POLÍCIA</div><div class="vsub">quando atendesse mulher com sinais de violência</div><div class="vetado" data-a="stamp" data-t="{W(s,'agredida',0,.1)}" data-d=".3">VETADO</div></div>
<div class="el glass" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'outra',0,-.2)}" style="left:80px;width:920px"><div class="mono" style="font-size:22px;color:#FFD34D">LEI 13.894/2019 · VETO PARCIAL</div><div class="h" style="font-size:48px;color:#fff;margin-top:8px">DIVÓRCIO NO MESMO JUIZADO DA VIOLÊNCIA</div><div class="vsub">a vítima não precisaria abrir outro processo</div><div class="vetado" data-a="stamp" data-t="{W(s,'processo',0,.1)}" data-d=".3">VETADO</div></div>
<div class="el h redtxt" data-flow="m:4" data-gap="40" data-a="left" data-t="{W(s,'negativo',0,-.15)}" style="left:80px;font-size:68px">PONTO NEGATIVO.</div>
<div class="el h" data-flow="m:5" data-gap="26" data-a="up" data-t="{W(s,'derrubou',0)}" style="left:80px;font-size:44px;color:#fff;white-space:nowrap">O CONGRESSO DERRUBOU <span style="color:#FFD34D">OS DOIS VETOS</span>.</div>
<div class="el glass" data-flow="m:6" data-gap="34" data-a="up" data-t="{W(s,'pandemia',0,-.2)}" style="left:80px;width:920px;font-family:Rub;font-weight:800;font-size:30px;color:#fff;padding:16px 22px"><div style="color:#FFD34D;font-size:28px">2020, PANDEMIA, TODO MUNDO EM CASA:</div><div style="font-size:40px;margin-top:6px">FEMINICÍDIOS 1.330 → 1.354</div><div style="font-weight:500;font-size:28px;margin-top:6px">Agressões registradas na delegacia caíram: menos denúncia, não menos violência.</div></div>
<div class="el src" data-a="fade" data-t=".5" style="left:80px;top:1450px">LEI 13.931/2019 · LEI 13.894/2019 (PROMULG. 10/12/2019) · FBSP 2021/2026</div>
''',bg='w_clinic',tint='#3B5470',dim=1.00,kb=1.12,kbo='40% 75%'))
# ---- S7 saidinha 2024
s='v07'
H.append(scene(s,rail(2)+f'''
<div class="el label gold" data-flow="m:1" data-ftop="300" data-a="left" data-t=".2" style="left:80px">11/04/2024 · LEI 14.843 · SAIDINHA</div>
<div class="el card2" data-flow="m:2" data-gap="24" data-a="up" data-t="{W(s,'sancionou',0,-.1)}" style="left:80px;width:920px;border-left:16px solid #FFD34D">
  <div class="ini" style="position:absolute;right:26px;top:22px;width:96px;height:96px;font-size:52px;background:#FFD34D;box-shadow:0 0 0 4px #111;border-width:4px">🦑</div>
  <div class="mono" style="font-size:24px;color:#8a6d1f">✓ SANCIONADO PELO GOVERNO ATUAL</div>
  <div class="h" style="font-size:60px;color:#111;line-height:1.02;width:740px">SEM SAIDINHA PRA CRIME <span class="hl2">HEDIONDO</span> E <span class="hl2">VIOLENTO</span></div>
  <div class="tag">INCLUI ESTUPRO</div></div>
<div class="el lawquote" data-flow="m:3" data-a="left" data-t="{W(s,'incluindo',0,.2)}" data-o="{W(s,'vetou',0,-.25)}" style="left:80px;width:920px">"Não terá direito à saída temporária (...) o condenado que cumpre pena por praticar crime hediondo ou com violência ou grave ameaça contra pessoa."<div class="mono" style="font-size:22px;margin-top:12px;color:#FFD34D">LEP, ART. 122, § 2º (REDAÇÃO DA LEI 14.843/2024)</div></div>
<div class="el card2" data-flow="m:3" data-a="up" data-t="{W(s,'vetou',0,-.1)}" style="left:80px;width:920px;border-left:16px solid #9aa7b8">
  <div class="mono" style="font-size:26px;color:#555">✗ VETOU SÓ</div>
  <div class="h" style="font-size:56px;color:#111;line-height:1.02">O FIM DA VISITA À FAMÍLIA, PRA QUEM <u>NÃO</u> COMETEU CRIME VIOLENTO</div></div>
<div class="el glass" data-flow="m:4" data-a="up" data-t="{W(s,'crime',2,-.1)}" data-o="{W(s,'então',0,-.1)}" style="left:80px;width:920px;font-family:Rub;font-weight:800;font-size:36px;color:#fff;padding:16px 24px">CRIME DIFERENTE, PENA DIFERENTE.<div class="mono" data-a="fade" data-t="{W(s,'saidinha',1,-.1)}" style="font-size:22px;color:#FFD34D;margin-top:8px">LEP: A SAÍDA SERVE PRA PREPARAR A VOLTA AO CONVÍVIO SOCIAL</div></div>
<div class="el sub" data-flow="m:5" data-a="up" data-t="{W(s,'congresso',0)}" style="left:80px;font-size:36px;white-space:nowrap"><b style="color:#FFD34D">28/05/2024:</b> Congresso derruba o veto, <b><span class="cnt" data-t="{W(s,'derrubou',0)}" data-d=".8" data-from="0" data-to="314" data-dec="0"></span> × 126</b></div>
<div class="el dimmer" data-a="fade" data-t="{W(s,'então',0,-.1)}" data-d=".3"></div>
<div class="el h" data-a="slam" data-t="{W(s,'então',0)}" style="left:80px;top:560px;width:930px;font-size:112px;color:#fff">VETOU A SAIDINHA PRA ESTUPRADOR?</div>
<div class="el verdict red" data-a="stamp" data-t="{W(s,'não',1,-.05)}" data-d=".35" data-r="-8" data-shake="1.4" style="left:250px;top:930px">FALSO</div>
<div class="el src" data-a="fade" data-t=".8" style="left:80px;top:1450px">PLANALTO · LEI 14.843/2024 · AGÊNCIA CÂMARA · CONGRESSO EM FOCO</div>
''',bg='w_bar2',tint='#5a4413',dim=1.00,kb=1.12,kbo='60% 40%'))
# ---- S7b irretroatividade
s='v07b'
H.append(scene(s,rail(2)+f'''
<div class="el label slate" data-flow="m:1" data-ftop="300" data-a="left" data-t=".1" style="left:80px">"MAS UM ESTUPRADOR SAIU DEPOIS DA LEI!"</div>
<div class="el h" data-flow="m:2" data-gap="18" data-a="slam" data-t="{W(s,'lei',0,-.1)}" data-shake="1" style="left:80px;width:930px;font-size:100px;color:#fff">A LEI MAIS DURA <span class="hl">NÃO VOLTA NO TEMPO</span></div>
<div class="el glass" data-flow="m:3" data-gap="50" data-a="up" data-t="{W(s,'cometido',0,-.1)}" style="left:80px;width:920px">
  <div class="brow" style="margin-top:0"><span style="width:440px;font-size:26px">CRIME ANTES DE 11/04/24</span><em style="font-size:38px;color:#9aa7b8">REGRA ANTIGA</em></div>
  <div class="brow"><span style="width:440px;font-size:26px">CRIME DEPOIS</span><em style="font-size:38px;color:#FFD34D">SEM SAIDINHA</em></div></div>
<div class="el lawquote" data-flow="m:4" data-gap="24" data-a="left" data-t="{W(s,'antes',0,.2)}" style="left:80px;width:920px">"A lei penal não retroagirá, salvo para beneficiar o réu."<div class="mono" style="font-size:22px;margin-top:12px;color:#FFD34D">CONSTITUIÇÃO, ART. 5º, XL</div></div>
<div class="el h" data-flow="m:5" data-gap="50" data-a="left" data-t="{W(s,'governo',0,-.1)}" style="left:80px;font-size:47px;color:#FFD34D;white-space:nowrap">NÃO É O GOVERNO. É A CONSTITUIÇÃO.</div>
<div class="el src" data-a="fade" data-t=".6" style="left:80px;top:1450px">CF ART. 5º, XL · STJ, HC 932.864/SC (6ª TURMA, 10/09/2024)</div>
''',bg='w_street',tint='#3B5470',dim=1.00,kb=1.12,kbo='70% 60%'))
# ---- S8 20 a 40
s='v08'
H.append(scene(s,rail(3)+f'''
<div class="el label gold" data-flow="m:1" data-ftop="300" data-a="left" data-t=".2" style="left:80px">09/10/2024 · LEI 14.994 · PACOTE ANTIFEMINICÍDIO</div>
<div class="el h" data-flow="m:2" data-gap="60" data-a="slam" data-t="{W(s,'vinte',1,-.1)}" data-shake="1" style="left:72px;font-size:230px;color:#fff;line-height:.9">20 A 40<br><span style="color:#FFD34D">ANOS</span></div>
<div class="el rng" data-flow="m:3" data-a="up" data-t="{W(s,'quarenta',0,.3)}" style="left:80px;width:920px">
  <div class="rrow" style="margin-top:0"><span>ANTES</span><div class="track"><div class="seg" style="left:{12/40*560:.0f}px;width:{18/40*560:.0f}px;background:#9aa7b8"></div></div><em>12–30</em></div>
  <div class="rrow"><span>AGORA</span><div class="track"><div class="seg" style="left:{20/40*560:.0f}px;width:{20/40*560:.0f}px;background:#FFD34D"></div></div><em>20–40</em></div>
  <div class="mono" style="font-size:22px;color:#ccc;margin-top:12px">ANOS DE PRISÃO · A MAIOR PENA DO CÓDIGO PENAL</div></div>
<div class="el mono" data-flow="m:5" data-gap="40" data-a="up" data-t="{W(s,'sancionada',0,-.1)}" style="left:80px;font-size:28px;color:#FFD34D">✓ SANCIONADA PELO PRESIDENTE · 09/10/2024</div>
<div class="el stamp-o" data-flow="m:4" data-gap="64" data-a="stamp" data-t="{W(s,'sem',0)}" data-d=".35" data-r="-4" style="left:80px">SEM VETO</div>
<div class="el src" data-a="fade" data-t=".8" style="left:80px;top:1450px">LEI 14.994/2024 · PL 4266/2023 (SEN. MARGARETH BUZETTI, PSD-MT)</div>
''',bg='w_pool2',dim=0.91,kbo='50% 75%'))
# ---- S9 antifacção
s='v09'
base=1150; k=4.2
cols=''.join(f'''<div class="el col" data-t="{W(s,t0,0,dl)}" data-d=".8" data-v="{v}" data-k="{k}" data-base="{base}" style="left:{x}px;width:220px;background:{c}"></div>
<div class="el colv" data-a="pop" data-t="{W(s,t0,0,dl+.6)}" style="left:{x}px;top:{base-v*k-100}px;width:220px">{v}%</div>
<div class="el colx" data-a="fade" data-t="{W(s,t0,0,dl)}" style="left:{x}px;top:{base+16}px;width:220px">{lab}</div>''' for x,v,c,lab,t0,dl in [(80,50,'#3156D3','2019','eram',0),(430,55,'#9aa7b8','2024','feminicida',.2),(780,75,'#FFD34D','2026','setenta',0)])
H.append(scene(s,rail(4)+f'''
<div class="el label gold" data-flow="m:1" data-ftop="300" data-a="left" data-t=".2" style="left:80px">24/03/2026 · LEI 15.358 · LEI ANTIFACÇÃO</div>
<div class="el h" data-flow="m:2" data-gap="30" data-a="slam" data-t="{W(s,'projeto',0,-.1)}" style="left:80px;width:940px;font-size:76px;color:#fff">PROJETO DO <span class="hl">PRÓPRIO GOVERNO</span></div>
<div class="el glass" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'enviado',0,-.2)}" data-o="{W(s,'feminicida',0,-.35)}" style="left:80px;width:920px">
  <div class="brow" style="margin-top:0"><span style="width:300px;font-size:26px">31/10/2025</span><em style="font-size:36px">ENVIADO AO CONGRESSO</em></div>
  <div class="brow" data-a="fade" data-t="{W(s,'dezoito',0,-.1)}"><span style="width:300px;font-size:26px">18/11/2025</span><em style="font-size:36px;color:#FFD34D">CÂMARA APROVA · 18 DIAS</em></div>
  <div class="brow" data-a="fade" data-t="{W(s,'cinco',0,-.1)}"><span style="width:300px;font-size:26px">24/03/2026</span><em style="font-size:36px;color:#FFD34D">VIRA LEI · &lt; 5 MESES</em></div><div class="mono" data-a="fade" data-t="{W(s,'dezoito',0,.3)}" style="font-size:20px;color:#ddd;margin-top:12px;line-height:1.4">RELATORES: GUILHERME DERRITE (PP, OPOSIÇÃO) NA CÂMARA · ALESSANDRO VIEIRA (MDB) NO SENADO</div></div>
<div class="el sub" data-flow="m:3" data-gap="30" data-a="up" data-t="{W(s,'feminicida',0,-.2)}" style="left:80px;width:920px;font-size:38px">feminicida réu primário: quanto da pena cumpre no fechado antes de progredir</div>
{cols}
<div class="el mono" data-a="fade" data-t="{W(s,'fechado',0,.2)}" style="left:780px;top:{base+62}px;width:220px;text-align:center;font-size:22px;color:#FFD34D">+ SEM LIVRAMENTO</div>
<div class="el mono" data-a="up" data-t="{W(s,'sancionada',0,-.1)}" style="left:80px;top:1300px;font-size:28px;color:#FFD34D">✓ SANCIONADA PELO PRESIDENTE · 24/03/2026</div>
<div class="el src" data-a="fade" data-t=".8" style="left:80px;top:1450px">LEP ART. 112 · LEIS 13.964/2019 · 14.994/2024 · 15.358/2026</div>
''',bg='w_friends',tint='#0E0D0B',dim=1.00,kb=1.12,kbo='50% 70%'))
# ---- S10 1112
s='v10'
stops=[("CÂMARA",130),("SENADO",400),("SANÇÃO",670),("LEI",930)]
st=''.join(f'<div class="el mst" data-a="pop" data-t="{.2+i*.2:.1f}" style="left:{x}px;top:470px"><i></i><b>{n}</b></div>' for i,(n,x) in enumerate(stops))
det=[("MUDOU O TEXTO? ⤺ VOLTA",'volta',0,'-1'),("VETO? ⤺ CONGRESSO VOTA DE NOVO",'aí',0,'.8'),("INCONSTITUCIONAL? ⤺ STF DERRUBA",'confusão',0,'-.8'),("SEM RELATOR? ⏸ GAVETA",'espalha',0,'1')]
dd=''.join(f'<div class="el detour" data-flow="d:{i+1}" data-ftop="620" data-gap="22" data-a="left" data-t="{W(s,w,n,-.2)}" data-o="{W(s,"projeto",0,-.15)}" data-r="{r}" style="left:80px">{t}</div>' for i,(t,w,n,r) in enumerate(det))
H.append(scene(s,f'''
<div class="el label gold" data-a="left" data-t=".1" style="left:80px;top:150px">COMO UM PROJETO VIRA LEI (OU NÃO)</div>
<div class="el h" data-a="up" data-t=".2" style="left:80px;top:212px;font-size:96px;color:#fff;width:950px">LEI VAI E VOLTA.</div>
<div class="el bigline bar" data-t=".1" data-d="1" data-to="800" style="left:130px;top:488px"></div>
{st}{dd}
<div class="el card2" data-flow="m:1" data-ftop="620" data-nosize="1" data-a="up" data-t="{W(s,'mil',0,-.2)}" data-o="{W(s,'antifacção',0,-.2)}" style="left:80px;width:920px;border-left:16px solid #C8352B">
  <div class="mono" style="font-size:26px;color:#555">PL 1112/2023 · DEP. ALFREDO GASPAR (UNIÃO-AL)</div>
  <div class="h" style="font-size:64px;color:#111;line-height:1.02">80% DA PENA NO FECHADO PRA <span class="hl2">TODO CRIME HEDIONDO</span></div>
  <div class="tag">INCLUSIVE FEMINICÍDIO</div><div class="mono" data-a="fade" data-t="{W(s,'câmara',0,-.1)}" style="font-size:24px;color:#555;margin-top:14px">CÂMARA 02/07/2025 · 334 × 65 · NÃO: PT E PSOL · SIM: PCDOB, PSB, PDT</div><div data-a="fade" data-t="{W(s,'pt',0,-.1)}" style="font-family:Rub;font-weight:700;font-size:28px;color:#C8352B;margin-top:8px;line-height:1.2">PT CONTRA: "MESMA REGRA PRA TUDO LOTA PRESÍDIO E ALIMENTA FACÇÃO"</div><div class="mono" data-a="fade" data-t="{W(s,'falsificar',0,-.1)}" style="font-size:20px;color:#333;margin-top:8px;line-height:1.35">TAMBÉM É HEDIONDO: PORTE DE ARMA DE USO PROIBIDO, FALSIFICAR REMÉDIO OU COSMÉTICO.<br>O STF JÁ DERRUBOU REGRA ÚNICA PRA TODO HEDIONDO (2006 E 2012): FERE A INDIVIDUALIZAÇÃO DA PENA.</div></div>
<div class="el glass" data-flow="m:1" data-a="up" data-t="{W(s,'antifacção',0,-.1)}" style="left:80px;width:920px">
  <div class="mono" style="font-size:24px;color:#FFD34D">LEI ANTIFACÇÃO · INICIATIVA DO GOVERNO FEDERAL · JÁ EM VIGOR</div><div class="mono" style="font-size:20px;color:#fff;margin-top:6px">SENADO: 64 × 0, EM 15 DIAS · PT VOTOU SIM</div><div class="mono" style="font-size:20px;color:#ddd;margin-top:6px">% DA PENA NO FECHADO, CONFORME A GRAVIDADE (NÃO 80% PRA TUDO)</div>
  <div class="brow"><span style="width:560px;font-size:28px">HEDIONDO, RÉU PRIMÁRIO</span><em>70%</em></div>
  <div class="brow"><span style="width:560px;font-size:28px">COM MORTE (INCL. FEMINICÍDIO)</span><em>75%</em></div>
  <div class="brow"><span style="width:560px;font-size:28px">REINCIDENTE</span><em>80%</em></div>
  <div class="brow"><span style="width:560px;font-size:28px">REINCIDENTE COM MORTE</span><em style="color:#FFD34D">85%</em></div></div>
<div class="el ball" data-a="pop" data-t="{W(s,'passou',0)}" style="left:{130-26}px;top:{488-26}px"></div>
<div class="el ball2" data-a="left" data-t="{W(s,'senado',0)}" data-d=".6" style="left:{400-26}px;top:{488-26}px"></div>
<div class="el gate" data-a="pop" data-t="{W(s,'relator',0)}" style="left:250px;top:390px">COMISSÃO DE SEGURANÇA · SENADO</div>
<div class="el counter" data-flow="m:2" data-gap="30" data-minh="160" data-a="pop" data-t="{W(s,'relator',0,.1)}" style="left:80px;width:920px"><span class="cnt" data-t="{W(s,'relator',0,.2)}" data-d="1.6" data-from="0" data-to="233" data-dec="0"></span><b>DIAS SEM RELATOR</b></div>
<div class="el sub" data-flow="m:3" data-gap="20" data-a="up" data-t="{W(s,'flávio',0)}" style="left:80px;font-size:36px;width:920px">presidente da comissão, <b>quem escolhe o relator: Flávio Bolsonaro (PL-RJ)</b></div>
<div class="el h redtxt" data-flow="m:4" data-gap="24" data-a="left" data-t="{W(s,'relator',0,.9)}" style="left:80px;font-size:52px;white-space:nowrap">SE É PRIORIDADE, CADÊ O RELATOR?</div>
<div class="el src" data-a="fade" data-t=".8" style="left:80px;top:1450px">SENADO · PL 1112/2023 (CSP DESDE 25/02/2026) · LEI 15.358/2026</div>
''',bg='w_run2',tint='#0E0D0B',dim=1.00,kb=1.1,kbo='50% 40%'))
# ---- S11 numbers
s='v11'
cards=[("SÃO PAULO","▲ 22%","221 → 270","TARCÍSIO","REPUBLICANOS <i class=\"ide dir\">DIREITA</i>",'#FF4A3D','são',0,0),("RIO DE JANEIRO","▲ 6%","99 → 105","CLÁUDIO CASTRO","PL <i class=\"ide dir\">DIREITA</i>",'#FF4A3D','são',0,.45),("SANTA CATARINA","▼ 7%","57 → 53","JORGINHO MELLO","PL <i class=\"ide dir\">DIREITA</i>",'#e9e3d3','são',0,.9),("BAHIA","▼ 11%","115 → 102","JERÔNIMO","PT <i class=\"ide esq\">ESQUERDA</i>",'#e9e3d3','bahia',0,0)]
cc=''
for i,(n,p_,v,g,pt,c,w,nn,dl) in enumerate(cards):
    x=80+(i%2)*470; y=380+(i//2)*340
    cc+=f'<div class="el scard" data-a="pop" data-t="{W(s,w,nn,dl-.1)}" style="left:{x}px;top:{y}px;height:310px"><div class="mono" style="font-size:24px;color:#bbb">{n}</div><div class="h" style="font-size:96px;color:{c}">{p_}</div><div class="mono" style="font-size:22px;color:#fff;white-space:nowrap">{v} vítimas (2023→25)</div></div>'
    cc+=f'<div class="el gov" data-a="up" data-t="{W(s,"quem",0,i*.12)}" style="left:{x+26}px;top:{y+196}px;width:420px"><b>{g}</b><span>{pt}</span></div>'
H.append(scene(s,f'''
<div style="position:absolute;left:-60px;top:340px;width:1200px;height:1080px;background:linear-gradient(180deg,rgba(5,6,8,0),rgba(5,6,8,.8) 10%,rgba(5,6,8,.8) 90%,rgba(5,6,8,0))"></div><div class="el label gold" data-a="left" data-t=".1" style="left:80px;top:150px">4 ESTADOS · 2023 → 2025</div>
<div class="el h" data-a="up" data-t="0" style="left:80px;top:212px;font-size:100px;color:#fff">E OS NÚMEROS?</div>
<div class="el mono" data-a="fade" data-t=".4" style="left:80px;top:322px;font-size:20px;color:#bbb">EXEMPLOS · OS 27 ESTADOS ESTÃO NO ANUÁRIO FBSP 2026</div>
{cc}
<div class="el sub" data-a="up" data-t="{W(s,'onze',0,.3)}" style="left:80px;top:1080px;font-size:38px"><b style="color:#FFD34D">Brasil, jan–jul:</b> 876 (2025) → 848 (2026), −3,2%</div>
<div class="el dimmer" data-a="fade" data-t="{W(s,'governador',0,-.05)}" data-d=".3" style="background:rgba(5,6,8,.97)"></div>
<div class="el mono" data-a="fade" data-t="{W(s,'governador',0,0)}" style="left:80px;top:430px;font-size:24px;color:#bbb">FEMINICÍDIOS 2023→2025 · QUEM GOVERNA</div>
<div class="el govlist" data-a="fade" data-t="{W(s,'governador',0,0)}" style="left:80px;top:480px;width:920px"><div class="glrow" data-a="left" data-t="{W(s,'governador',0,0.15)}"><em style="color:#FF4A3D">▲ 22%</em><div><b>TARCÍSIO</b><span>SP · REPUBLICANOS <i class="ide dir">DIREITA</i></span></div></div><div class="glrow" data-a="left" data-t="{W(s,'governador',0,0.33)}"><em style="color:#FF4A3D">▲ 6%</em><div><b>CLÁUDIO CASTRO</b><span>RJ · PL <i class="ide dir">DIREITA</i></span></div></div><div class="glrow" data-a="left" data-t="{W(s,'governador',0,0.51)}"><em style="color:#e9e3d3">▼ 7%</em><div><b>JORGINHO MELLO</b><span>SC · PL <i class="ide dir">DIREITA</i></span></div></div><div class="glrow" data-a="left" data-t="{W(s,'governador',0,0.69)}"><em style="color:#e9e3d3">▼ 11%</em><div><b>JERÔNIMO</b><span>BA · PT <i class="ide esq">ESQUERDA</i></span></div></div></div>
<div class="el h" data-a="left" data-t="{W(s,'quem',0,-.1)}" style="left:80px;top:1160px;font-size:58px;color:#FFD34D;width:930px">QUEM COMANDA A POLÍCIA É O GOVERNADOR.</div>
<div class="el mono" data-a="fade" data-t="{W(s,'governador',0,.4)}" style="left:80px;top:1300px;font-size:22px;color:#ddd">A UNIÃO FINANCIA E FAZ A LEI · O POLICIAMENTO É DO ESTADO</div>
<div class="el src" data-a="fade" data-t=".8" style="left:80px;top:1450px">FBSP · ANUÁRIO 2026 · SINESP/MJSP JAN–JUL 2026 · CF ART. 144, §6º</div>
''',bg='w_delegacia',tint='#0E0D0B',dim=1.00,kb=1.08,kbo='50% 85%'))
# ---- S12 close
s='v12'
H.append(scene(s,f'''
<div class="el letter" data-flow="m:1" data-ftop="230" data-a="drop" data-t=".05" data-d=".5" data-r="-2" style="left:80px;width:900px"><div class="hand" style="font-size:80px">Então, amiga:</div><div class="h" style="font-size:66px;color:#111;margin-top:10px">VETOU A SAIDINHA PRA ESTUPRADOR?</div></div>
<div class="el verdict red" data-flow="m:2" data-gap="44" data-a="stamp" data-t="{W(s,'não',0,-.05)}" data-d=".35" data-r="-6" data-shake="1.4" style="left:330px;font-size:140px">FALSO</div>
<div class="el h" data-flow="m:3" data-gap="44" data-a="slam" data-t="{W(s,'endureceu',0)}" style="left:80px;width:930px;font-size:86px;color:#fff">ENDURECEU A PENA?</div>
<div class="el h" data-flow="m:4" data-gap="10" data-a="slam" data-t="{W(s,'duas',0)}" data-shake="1" style="left:80px;font-size:120px;color:#FFD34D;white-space:nowrap">DUAS VEZES.</div>
<div class="el sub" data-flow="m:5" data-gap="44" data-a="up" data-t="{W(s,'vezes',0,.2)}" data-o="{W(s,'complicada',0,-.2)}" style="left:80px;width:900px;font-size:40px">20 a 40 anos (2024) · 75% no fechado (2026)</div>
<div class="el glass" data-flow="m:5" data-a="up" data-t="{W(s,'complicada',0,-.2)}" data-o="{W(s,'reposta',0,-.25)}" style="left:80px;width:920px;font-family:Rub;font-weight:800;font-size:40px;line-height:1.15">LEI É COMPLICADA. <span style="color:#FFD34D">CONFERE O QUE FOI SANCIONADO</span> E OUVE OS DOIS LADOS.</div>
<div class="el repost" data-flow="m:5" data-a="slam" data-t="{W(s,'reposta',0,-.1)}" data-shake="1" style="left:80px;width:920px">🔁 REPOSTA AGORA<small>essa desinformação tá rodando nos grupos</small></div>
<div class="el hand" data-flow="m:6" data-gap="16" data-a="up" data-t="{W(s,'grupos',0,.2)}" style="left:680px;font-size:70px;color:#fff">um beijo 💚</div>
''',bg='w_watch',dim=0.85,kb=1.06,kbo='50% 70%'))
CSS=open('/home/claude/work/build/style.css').read()
page=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Querida amiga</title>
<link rel="stylesheet" href="fx.css"><style>{CSS}</style></head><body><div id="stage">
{"".join(H)}
<div id="grain"></div><div id="foot">@tentandochegaratevoce</div></div>
<script>window.DUR={DUR:.2f};</script><script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script><script src="layout.js"></script></body></html>'''
open('/home/claude/hub/docs/templates/collage_reel/qamiga.html','w').write(page)
print('ok',DUR)
