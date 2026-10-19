# ---------- c1 · gancho: o comentário real ----------
s = 'c1'; o = S[s]
BRA = frame(['rs', 'rr', 'ac', 'pb'], w=760, h=760, fy=1080)
CAM += [[0] + BRA, [o['e'] - .2] + [BRA[0] * 1.06] + BRA[1:]]
HL += [[G(s, 'bahia', 0, -.1), 'ba', 'esq', .5], [G(s, 'santa', 0, -.1), 'sc', 'dir', .5]]
LAB += [lab(G(s, 'bahia', 0, .1), o['e'], 'ba', 'BAHIA<small>PT ' + ESQ + ' DESDE 2007</small>', 'r'),
        lab(G(s, 'santa', 0, .1), o['e'], 'sc', 'SANTA CATARINA<small>NUNCA TEVE O PT</small>', 'b')]
H.append(scene(s, f'''
{eb(0, 'O COMENTÁRIO QUE RECEBEMOS', top=300)}
<div class="el cmt" data-flow="m:2" data-gap="26" data-a="up" data-t="{W(s, 'recebemos', 0, -.1)}" style="left:80px;width:920px"><i class="av"></i><div><div class="who"><span></span>46 min</div><div class="ct">Faz um POST sobre Pt 20 anos na Bahia consecutivos e na presidência alternados versus SC nunca governada pelo pt, onde está melhor ??</div></div></div>
<div class="el h" data-flow="m:3" data-gap="34" data-a="slam" data-t="{W(s, 'onde', 0, -.12)}" data-shake="1" style="left:80px;width:920px;font-size:110px;color:#fff">ONDE ESTÁ <span class="hl">MELHOR?</span></div>
''', 'COMENTÁRIO RECEBIDO NO NOSSO PERFIL (NOME OCULTO) · TSE', shade='shadeMapH'))

# ---------- c2 · ninguém começou do mesmo lugar ----------
s = 'c2'; o = S[s]
CAM += [[o['s'] + .1] + [BRA[0] * 1.1] + BRA[1:], [o['e'] - .1] + [BRA[0] * 1.18] + BRA[1:]]
SIL = '<svg viewBox="0 0 200 240"><circle cx="100" cy="78" r="52"/><path d="M8 240c4-70 44-104 92-104s88 34 92 104z"/></svg>'
H.append(scene(s, rail(1) + f'''
{eb(1, 'PONTO DE PARTIDA')}
<div class="el duo" data-flow="m:2" data-gap="40" style="left:80px;width:920px">
  <div class="who2" data-a="up" data-t="{W(s, 'média', 0, -.2)}"><div class="cut you">{SIL}</div><b>VOCÊ</b><small>R$ 3.722 POR MÊS<br>MÉDIA DO BRASIL</small></div>
  <div class="vs" data-a="pop" data-t="{W(s, 'justus', 0, -.4)}">×</div>
  <div class="who2" data-a="up" data-t="{W(s, 'roberto', 0, -.15)}"><div class="cut jus">{SIL}<em>FOTO</em></div><b>ROBERTO JUSTUS</b><small>EMPRESÁRIO</small></div>
</div>
<div class="el h" data-flow="m:3" data-gap="44" data-a="up" data-t="{W(s, 'cobrar', 0, -.2)}" style="left:80px;width:920px;font-size:62px;color:#fff">“POR QUE VOCÊ NÃO TEM A MANSÃO DELE?”</div>
<div class="el h" data-flow="m:4" data-gap="34" data-a="slam" data-t="{W(s, 'começaram', 0, -.3)}" data-shake="1" style="left:80px;width:920px;font-size:88px;color:#fff">NINGUÉM COMEÇOU <span class="hl">DO MESMO LUGAR.</span></div>
<div class="el fine" data-flow="m:5" data-gap="26" data-a="fade" data-t="{W(s, 'começaram', 0, .4)}" style="left:80px">RENDIMENTO MÉDIO DO TRABALHO, 1º TRIMESTRE DE 2026 (IBGE, PNAD CONTÍNUA).</div>
''', 'IBGE, PNAD CONTÍNUA (1º TRI/2026)', shade='shadeMapF'))

# ---------- c3 · a história ----------
s = 'c3'; o = S[s]
BSC = frame(['ba', 'sc', 'mg', 'sp'], w=700, h=620, fy=1130)
CAM += [[o['s'] + .1] + BSC, [o['e'] - .1] + [BSC[0] * 1.06] + BSC[1:]]
H.append(scene(s, rail(2) + f'''
{eb(2, 'A HISTÓRIA DE CADA UM')}
<div class="el rows" data-flow="m:2" data-gap="34" data-a="fade" data-t="{W(s, 'bahia', 0, -.2)}" style="left:80px">
  <div class="row txt"><div class="k" style="color:#FF7A6E">BAHIA<small>SÉCULOS XVI A XIX</small></div><div class="v">SÉCULOS DE ESCRAVIDÃO E LATIFÚNDIO: <span style="color:#FF7A6E">A TERRA NA MÃO DE POUCOS</span></div></div>
  <div class="row txt" data-a="fade" data-t="{W(s, 'santa', 0, -.2)}"><div class="k" style="color:#9DB0FF">SANTA CATARINA<small>SÉCULO XIX</small></div><div class="v">COLÔNIAS DE IMIGRANTES COM <span style="color:#9DB0FF">ACESSO A TERRA PRA PLANTAR</span></div></div></div>
<div class="el h" data-flow="m:3" data-gap="40" data-a="slam" data-t="{W(s, 'frente', 0, -.3)}" style="left:80px;width:920px;font-size:84px;color:#fff">E SAIU <span class="hl">NA FRENTE.</span></div>
<div class="el fine" data-flow="m:4" data-gap="26" data-a="fade" data-t="{W(s, 'frente', 0, .3)}" style="left:80px">A ESCRAVIDÃO SÓ ACABOU EM 1888. NAS COLÔNIAS DE SC, OS LOTES ERAM PEQUENOS E, EM GERAL, PAGOS A PRAZO (LEI DE TERRAS, 1850).</div>
''', 'IBGE · LEI Nº 601/1850 (LEI DE TERRAS) · LEI ÁUREA (1888)', shade='shadeMapF'))

# ---------- c4 · a renda até hoje ----------
s = 'c4'; o = S[s]
CAM += [[o['s'] + .1] + BSC, [o['e'] - .1] + [BSC[0] * 1.1] + BSC[1:]]
def money(name, sub, val, frac, color, t):
    return (f'<div class="tile"><div class="tk">{name}<small>{sub}</small></div>'
            f'<div class="tv" style="color:{color};font-size:120px"><span class="cnt" data-t="{t}" data-d=".9" data-from="0" data-to="{val}" data-dec="0" data-thou="1" data-pre="R$ ">0</span></div>'
            f'<div class="ttrack"><div class="bar" data-t="{t}" data-d=".9" data-to="{int(400 * frac)}" style="background:{color}"></div></div></div>')
H.append(scene(s, rail(3) + f'''
{eb(3, 'ATÉ HOJE · RENDA POR PESSOA, POR MÊS · 2025')}
{tiles(money('SANTA CATARINA', '4ª MAIOR DO BRASIL', 2809, 1, BL, W(s, 'santa', 0, -.2)),
       money('BAHIA', 'ABAIXO DA MÉDIA (R$ 2.316)', 1465, 1465 / 2809, R, W(s, 'bahia', 0, -.2)), W(s, 'renda', 0, -.2), 'm:2', 34)}
<div class="el stamp-r" data-flow="m:3" data-gap="34" data-a="stamp" data-t="{W(s, 'dobro', 0, -.15)}" data-d=".35" data-r="-2" style="left:80px;white-space:nowrap;font-size:54px">QUASE O DOBRO</div>
<div class="el h" data-flow="m:4" data-gap="40" data-a="slam" data-t="{W(s, 'ponto', 0, -.15)}" style="left:80px;width:920px;font-size:84px;color:#fff">PONTO DE PARTIDA, <span class="hl">NÃO GOVERNO.</span></div>
''', 'IBGE, RENDIMENTO DOMICILIAR PER CAPITA 2025 (PNAD CONTÍNUA)', shade='shadeMapF'))

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
<div class="el h" data-flow="m:2" data-gap="30" data-a="slam" data-t="{W(s, 'presidência', 0, -.15)}" style="left:80px;width:920px;font-size:72px;color:#fff">A PRESIDÊNCIA FOI <span class="hl">A MESMA</span> PARA OS DOIS ESTADOS.</div>
<div class="el stamp-o" data-flow="m:3" data-gap="30" data-a="stamp" data-t="{W(s, 'polícia', 0, -.1)}" data-d=".35" data-r="-1.5" style="left:80px;font-size:40px;width:920px">POLÍCIA, PRESÍDIOS E INVESTIGAÇÃO SÃO DO GOVERNO DO ESTADO</div>
<div class="el h" data-flow="m:4" data-gap="34" data-a="up" data-t="{W(s, 'compare', 0, -.15)}" style="left:80px;width:920px;font-size:64px;color:{Y}">COMPARE ESTADOS DA MESMA REGIÃO.</div>
<div class="el fine" data-flow="m:5" data-gap="22" data-a="fade" data-t="{W(s, 'região', 0, .3)}" style="left:80px">NORDESTE, MORTES VIOLENTAS (2025): MEDIANA DOS ESTADOS DE ESQUERDA 29,4 × DIREITA 33,0. MESMO PATAMAR.</div>
<div class="el repost" data-flow="m:6" data-gap="30" data-a="slam" data-t="{W(s, 'vídeo', 0, -.15)}" data-shake="1" style="left:80px;width:920px;font-size:50px">VÍDEO COMPLETO NO PERFIL<small>Parte 1: Bahia e Norte, culpa da esquerda?</small></div>
''', FB + ' · CONSTITUIÇÃO, ART. 144 · ' + IDS, shade='shadeMapF'))

