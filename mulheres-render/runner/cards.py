"""Versão bonita nos templates do Painel da Manhã (pedido dela 22/11): cenas do tipo "card".

Cena: {"type": "card", "card": "05", "campos": {...}, "fala": "...", "source": "..."}.
Os cards e os campos de cada um estão em anim/cards.js (SCHEMA) e no prompt (CATALOGO abaixo).
"entra" (em itens, pessoas, barras, e "entra_depois" no card 05) é um trecho EXATO da fala da cena: o item aparece
quando a voz fala esse trecho (animação ligada à fala). producao.montar_manifesto troca por "t" (segundo absoluto).
Sem "entra", o item entra espalhado pela cena.
"""
from __future__ import annotations

import base64
import json
import pathlib
import re

ANIM = pathlib.Path(__file__).resolve().parent.parent / "anim"

CATALOGO = {
    "01": ("Chamada amarela com mídia em moldura", "abertura com foto/clipe", "rotulo, titulo, destaque, apoio, pessoa, etiqueta, midia(url opcional), icone"),
    "02": ("Papel bege com recortes de rosto", "quem decide / quem está envolvido", "rotulo, titulo, destaque, pessoas[2]{nome,cargo,chip,lado:esq|dir|neu,foto?,entra}"),
    "03": ("Abertura vermelha com pergunta", "1ª cena: pergunta que prende", "rotulo, titulo, destaque, apoio, etiqueta, midia?, icone"),
    "04": ("Número gigante em fundo claro", "número, lei, placar", "rotulo, titulo, destaque, numero, sufixo, apoio"),
    "05": ("Ícones com seta (antes/depois)", "antes e depois sem foto", "rotulo, titulo, destaque, antes, depois, icone_antes, icone_depois, etiqueta, entra_depois"),
    "06": ("Lista com filetes que acendem", "resumo, o que fica igual, o que fazer", "rotulo, titulo, destaque, itens[2-4]{texto,entra}"),
    "07": ("CTA vermelho Reposta", "fim: reposta/segue", "rotulo, titulo(1 palavra), icone, apoio, link"),
    "10": ("Infográfico amarelo com ícones", "mecanismo (como funciona)", "rotulo, titulo, destaque, itens[2-3]{texto,destaque,icone,entra}"),
    "11": ("Número de impacto no escuro", "número que mexe no bolso/na vida", "rotulo, apoio_topo, icone, numero, sufixo, titulo, destaque, apoio"),
    "12": ("Mapa de conexões com rostos", "quem está ligado a quem", "rotulo, titulo, destaque, pessoas[2-4]{nome,chip,lado,aspas,foto?,entra}"),
    "16": ("Duelo de rostos com barra", "comparar dois lados", "titulo, destaque, pessoas[2]{nome,chip,lado}, barras[1-2]{rotulo,a,b,a_txt,b_txt,entra}, etiqueta"),
    "17": ("Celular mostrando o site", "divulgar site, consulta, enquete", "rotulo, titulo, destaque, site, tela_titulo, itens[1-3]{texto,entra}"),
    "20": ("Cartaz bege com sol (pergunta calma)", "abertura calma, dúvida honesta", "titulo, destaque, apoio"),
    "22": ("Terracota com ícone (fato principal)", "fato principal da notícia", "rotulo, titulo, destaque, icone, nota, foto?"),
    "24": ("Serifa com brilhinhos (respiro)", "respiro / pergunta pro público pensar", "titulo"),
    "26": ("Cartaz estrela + título gigante (CTA)", "final que pede ação", "titulo, destaque, itens[1-3]{texto(verbo),sub,entra}"),
}
OBRIG = {"01": ["titulo"], "02": ["titulo", "pessoas"], "03": ["titulo"], "04": ["titulo", "numero"], "05": ["titulo", "antes", "depois"],
         "06": ["titulo", "itens"], "07": ["titulo"], "10": ["titulo", "itens"], "11": ["numero", "titulo"], "12": ["pessoas"],
         "16": ["titulo", "pessoas", "barras"], "17": ["titulo", "itens"], "20": ["titulo"], "22": ["titulo"], "24": ["titulo"],
         "26": ["titulo", "itens"]}
# 24/11 (ela: "não está igual aos favoritos"): os FAVORITOS e 4-5 estrelas do Painel desenhados DE VERDADE (anim/cards.js,
# C['pN'] = card N do Painel; só a cor vira cor_tema e o texto vira os campos). Mesma lista de CARDS.painel/painelSchema
# (teste confere). Campos completos: anim/TEMPLATES-PAINEL.md.
PAINEL = {
    "p89": ("Card 89 · capa: pergunta + foto em moldura de filete (favorito)", "capa / abertura com foto",
            "rotulo, serie, titulo, destaque, midia(foto), legenda_foto, apoio"),
    "p134": ("Card 134 · capa escura: foto P&B a 15% em meio-tom + janela com foto (favorito)", "capa forte com pessoa/lugar",
             "rotulo, serie, titulo, destaque, foto_fundo, midia(foto da janela), faixa?"),
    "p79": ("Card 79 · foto de fundo + gráfico de barras que cresce (favorito)", "número / comparação de valores",
            "rotulo, titulo, destaque, foto_fundo, grafico_titulo, unidade(R$|%|texto), barras[2-5]{rotulo,valor,entra}, nota"),
    "p92": ("Card 92 · guia prático: passos numerados que acendem com a voz (favorito)", "lista / passo a passo",
            "rotulo, serie, titulo, destaque, itens[2-4]{texto,sub,entra}, apoio"),
    "p112": ("Card 112 · CTA: cartaz com estrela + verbos que entram com a voz (favorito)", "ação / CTA final",
             "rotulo, serie, titulo, destaque, itens[1-4]{texto(verbo),sub,entra}, apoio"),
    "p118": ("Card 118 · citação: colagem de 2 fotos + papel rasgado com megafone (favorito)", "citação real publicada",
             "rotulo, serie, titulo, destaque, foto, foto2, citacao, autor, contexto, pessoa{nome,partido,ideologia}, apoio"),
    "p98": ("Card 98 · etapas: 3 retratos P&B em degrau + colchete que liga (favorito)", "linha do tempo / quem faz o quê",
            "rotulo, serie, titulo, destaque, itens[2-3]{rotulo,texto,foto,nome,partido,ideologia,entra}, nota, apoio"),
    "p143": ("Card 143 · retrato recortado que cai e assenta no papel (favorito)", "pessoa (quem é)",
             "rotulo, serie, titulo, destaque, pessoa{nome,cargo,partido,ideologia,foto(PNG recortado)}, apoio"),
    "p160": ("Card 160 · uma pessoa em foco, duas desfocadas atrás (favorito)", "pessoa no centro da notícia",
             "rotulo, serie, titulo, destaque, foto_fundo, pessoa{nome,cargo,partido,ideologia,foto}, fundo_pessoas[0-2]{foto}"),
    "p162": ("Card 162 · dois lados; o foco passa de um pro outro com a voz (favorito)", "antes/depois, dois lados",
             "rotulo, serie, titulo, destaque, pessoas[2]{nome,cargo,partido,ideologia,foto,entra}, fundo_pessoa{foto}"),
    "p117": ("Card 117 · foto com bloco de cor girado atrás (favorito)", "capa / lugar", "rotulo, serie, titulo, destaque, midia, legenda_foto, apoio"),
    "p119": ("Card 119 · sol grande atrás + foto com passe-partout (favorito)", "capa com pessoa no lugar", "rotulo, serie, titulo, destaque, midia, legenda_foto, apoio"),
    "p81": ("Card 81 · foto inteira + título em serifa embaixo (favorito)", "abertura calma, lugar", "rotulo, titulo, destaque, foto_fundo, apoio"),
    "p84": ("Card 84 · foto + serifa centralizada com brilhos (favorito)", "abertura calma, respiro", "rotulo, titulo, destaque, foto_fundo, apoio"),
    "p114": ("Card 114 · foto escurecida + serifa creme com brilhos (favorito)", "respiro / frase forte", "rotulo, serie, titulo, destaque, foto_fundo, apoio"),
    "p115": ("Card 115 · igual ao 114 em azul (favorito)", "respiro / frase forte", "rotulo, serie, titulo, destaque, foto_fundo, apoio"),
    "p82": ("Card 82 · colagem: foto girada com borda de papel + recorte + sol (favorito)", "lugar + personagem", "rotulo, titulo, destaque, foto, recorte(PNG), pessoa{nome,cargo,partido,ideologia}"),
    "p83": ("Card 83 · cartaz com objeto recortado sobre o sol (favorito)", "objeto símbolo da notícia", "rotulo, titulo, destaque, recorte(PNG do objeto) ou icone, apoio"),
    "p85": ("Card 85 · mapa do Brasil + título condensado gigante (favorito)", "manchete nacional / cartaz", "rotulo, titulo, destaque, apoio"),
    "p116": ("Card 116 · mapa na cor + título Inter Tight gigante + selo (favorito)", "manchete nacional / cartaz", "rotulo, serie, titulo, destaque, etiqueta, apoio, entra_etiqueta, entra_apoio"),
    "p86": ("Card 86 · pessoa recortada na frente do sol + faixa de paisagem (favorito)", "pessoa comum / trabalhador", "rotulo, titulo, destaque, foto_fundo, lugar, pessoa{nome,cargo,partido,ideologia,foto}"),
    "p142": ("Card 142 · pontos que crescem: cena 1 vira cena 2 (favorito)", "troca de bloco / capítulo", "rotulo, serie, titulo, destaque, foto, apoio, depois{rotulo,serie,titulo,destaque,foto,apoio}, entra_depois"),
    "p41": ("Card 41 · minimalista: bonequinho + um ponto de cor (favorito)", "pergunta simples, quem é", "rotulo, serie, titulo (frase), pergunta"),
    "p125": ("Card 125 · lista no quadriculado com letra de marcador (5 estrelas)", "lista do dia a dia", "rotulo, serie, titulo, destaque, itens[3-5]{texto,circular,entra}, nota"),
    "p137": ("Card 137 · lista no quadriculado, itálico, último circulado (5 estrelas)", "lista / ranking", "rotulo, serie, titulo, destaque, foto_fundo, itens[3-5]{texto,circular,entra}, apoio"),
    "p148": ("Card 148 · elenco corpo inteiro com fade, fundo cheio na cor (5 estrelas)", "uma pessoa em destaque", "rotulo, serie, titulo, destaque, pessoa{nome,cargo,partido,ideologia,foto}, fundo_pessoas[0-2]{foto}"),
    "p149": ("Card 149 · elenco duotone em camadas (5 estrelas)", "uma pessoa + coadjuvantes", "rotulo, serie, titulo, destaque, pessoa{...}, fundo_pessoas[0-3]{foto}"),
    "p150": ("Card 150 · só cabeças em camadas: ganhou x perdeu (5 estrelas)", "resultado de eleição/votação", "rotulo, serie, titulo, destaque, pessoas[2]{...foto(cabeça)}, fundo_pessoas[0-5]{foto}"),
    "p151": ("Card 151 · dois meio-corpos com fade (5 estrelas)", "duas pessoas lado a lado", "rotulo, serie, titulo, destaque, pessoas[2]{nome,cargo,partido,ideologia,foto}"),
    "p152": ("Card 152 · elenco com cor seletiva (5 estrelas)", "a pessoa que importa em cor", "rotulo, serie, titulo, destaque, pessoa{...}, fundo_pessoas[0-3]{foto}"),
}
OBRIG_PAINEL = {"p89": ["titulo"], "p134": ["titulo"], "p79": ["titulo", "barras"], "p92": ["titulo", "itens"],
                "p112": ["titulo", "itens"], "p118": ["titulo", "citacao"], "p98": ["titulo", "itens"],
                "p143": ["titulo", "pessoa"], "p160": ["titulo", "pessoa"], "p162": ["titulo", "pessoas"],
                "p81": ["titulo"], "p82": ["titulo"], "p83": ["titulo"], "p84": ["titulo"], "p85": ["titulo"], "p86": ["titulo", "pessoa"],
                "p114": ["titulo"], "p115": ["titulo"], "p116": ["titulo"], "p117": ["titulo"], "p119": ["titulo"], "p142": ["titulo"],
                "p41": ["titulo"], "p125": ["titulo", "itens"], "p137": ["titulo", "itens"], "p148": ["titulo", "pessoa"],
                "p149": ["titulo", "pessoa"], "p150": ["titulo", "pessoas"], "p151": ["titulo", "pessoas"], "p152": ["titulo", "pessoa"]}
ICONES = ["doc", "lei", "dinheiro", "pessoa", "pessoas", "celular", "alerta", "voto", "relogio", "martelo", "megafone",
          "check", "x", "grafico", "casa", "tela", "barril"]  # barril: anim/cards.js desde 25/11 (A2 PLP299)
LIMITE = {"titulo": 60, "apoio": 120, "rotulo": 40, "texto": 60, "aspas": 50, "etiqueta": 40, "nota": 110}
FONTES = [("Rubik", 400, "rubik-latin-400-normal.woff2"), ("Rubik", 600, "rubik-latin-600-normal.woff2"),
          ("Rubik", 800, "rubik-latin-800-normal.woff2"), ("Rubik", 900, "rubik-latin-900-normal.woff2"),
          ("JetBrains Mono", 700, "jetbrains-mono-latin-700-normal.woff2"), ("Anton", 400, "anton-latin-400-normal.woff2"),
          ("DM Serif Display", 400, "dm-serif-display-latin-400-normal.woff2"),
          ("Inter Tight", 700, "inter-tight-latin-700-normal.woff2"), ("JetBrains Mono", 400, "jetbrains-mono-latin-400-normal.woff2"),
          ("Patrick Hand SC", 400, "patrick-hand-sc-latin-400-normal.woff2")]


# 23/11 (palavras dela: "o template e só inspiration, não é pra usar igual"): variação por cena e card "livre".
# Mesmas listas de anim/cards.js (CARDS.variacoes); test_variacao confere que batem.
PALETAS = {"creme-amarelo": "#F2E6D0", "creme-rosa": "#F7EFE3", "branco-verde": "#F7F8FA", "branco-laranja": "#FAF7F2",
           "amarelo": "#FFD34D", "rosa": "#FF8FC3", "verde": "#7BE3A0", "laranja": "#FF9F5A", "lilas": "#C9AEFF",
           "grafite-amarelo": "#17171A", "grafite-verde": "#141A16", "grafite-rosa": "#1A1418", "terracota": "#B5482E",
           "vinho": "#6E1E2B", "vermelho": "#D9362B", "mata": "#1F3A2B"}
PALETAS_ESCURAS = {"grafite-amarelo", "grafite-verde", "grafite-rosa", "terracota", "vinho", "vermelho", "mata"}
PALETAS_GRAFITE = {"grafite-amarelo", "grafite-verde", "grafite-rosa"}
FUNDOS = ["chapado", "papel", "quadriculado", "pontilhado", "listras", "gradiente", "foto"]
MOLDURAS = ["limpa", "filete", "cantos", "fita", "carimbo"]
ENTRADAS = ["baixo", "cima", "esquerda", "direita", "escala"]
ALINHAMENTOS = ["esq", "centro", "dir"]
LAYOUTS = ["pilha", "centro", "base", "faixa", "colunas", "diagonal", "cartao", "manchete"]
DISPOSICAO = {"itens": ["lista", "numerada", "grade", "linha-tempo", "chips"], "pessoas": ["linha", "grade", "lista"],
              "antes_depois": ["lado", "empilhado"]}
BLOCOS = ["titulo", "numero", "texto", "itens", "pessoas", "antes_depois", "citacao", "conexao", "icone", "etiqueta"]
ESCUROS = {"03", "05", "11", "17", "22", "24", "26"}  # cards do acervo com fundo escuro (texto claro)
ORIGINAL = {"01": "#FFD34D", "02": "#F2E6D0", "03": "#C0262D", "04": "#F7F8FA", "05": "#161B2A", "06": "#FFD34D",
            "07": "#FF4A3D", "10": "#FFD34D", "11": "#0B0B0C", "12": "#FFD34D", "16": "#F7F4EE", "17": "#1F2A22",
            "20": "#F2E6D0", "22": "#B5482E", "24": "#0B0B0C", "26": "#E4382E"}
OBRIG_BLOCO = {"titulo": ["texto"], "numero": ["valor"], "texto": ["texto"], "itens": ["itens"], "pessoas": ["pessoas"],
               "antes_depois": ["antes", "depois"], "citacao": ["texto"], "conexao": ["de", "para"], "icone": ["icone"],
               "etiqueta": ["texto"]}
LIMITE_BLOCO = {"titulo": 60, "texto": 120, "citacao": 120, "etiqueta": 40, "legenda": 60, "rotulo": 60, "antes": 60, "depois": 60}
LIVRE_DESC = ("card livre: você monta a cena por blocos (campos.blocos, 1 a 5, de cima pra baixo) e escolhe o layout em "
              "'composicao'. Blocos: titulo{texto,destaque,letra:rubik|anton (nada de serifa),tamanho:g|m|p}, numero{valor,sufixo,"
              "tamanho:gigante|grande|medio,legenda}, texto{texto,destaque}, itens{itens[1-4]{texto,destaque,icone,entra},"
              "disposicao:lista|numerada|grade|linha-tempo|chips}, pessoas{pessoas[1-4]{nome,cargo,chip,lado,foto?,entra},"
              "disposicao:linha|grade|lista}, antes_depois{antes,depois,icone_antes,icone_depois,entra_depois,disposicao:"
              "lado|empilhado}, citacao{texto,autor} (só fala real publicada), conexao{de{nome,chip,lado},para{nome,chip,lado},"
              "rotulo,destaque,entra} (mapa cabeça a cabeça), icone{icone,tamanho:g|m|p}, etiqueta{texto}. Layouts: "
              "pilha (empilha do topo, alinhado à esquerda), centro (centralizado no meio), base (conteúdo embaixo; foto em "
              "círculo em cima só se a cena tiver campos.imagem), faixa (1º título numa faixa de cor atravessando a tela), colunas (1º bloco compacto, como número, "
              "ícone ou pessoa, numa coluna estreita à esquerda; 2º bloco curto à direita (título de até 30 caracteres, senão o renderizador descarta colunas e desenha em pilha), com destaque curto; do 3º em diante, largura toda embaixo), diagonal (blocos alternam esquerda/direita), cartao (tudo num cartão de papel "
              "sobre o fundo), manchete (título condensado gigante, blocos separados por filetes de jornal).")


def _norm(w: str) -> str:
    return re.sub(r"[^\wà-úÀ-Ú]", "", w.lower())


def _seq(t: str) -> list[str]:
    return [x for x in (_norm(w) for w in str(t or "").split()) if x]


def _achar(alvo: list[str], s: list[str]) -> int | None:
    for i in range(len(alvo) - len(s) + 1):
        if s and alvo[i:i + len(s)] == s:
            return i
    return None


def validar_variacao(c: dict, n: str) -> list[str]:
    """Campos de variação da cena (composicao, variante, fundo, paleta, entrada): valores conhecidos e combinações que
    o renderizador desenha direito (paleta clara/escura igual ao card do acervo; foto só com asset; sem preto liso)."""
    pr, card = [], str(c.get("card", ""))
    comp = c.get("composicao")
    if comp is not None:
        ok = LAYOUTS if card == "livre" else ALINHAMENTOS
        if comp not in ok:
            pr.append(f"{n}: composicao {comp!r} não existe pro card {card} (use {', '.join(ok)})")
    for campo, lista in (("variante", MOLDURAS), ("fundo", FUNDOS), ("entrada", ENTRADAS), ("paleta", list(PALETAS))):
        if c.get(campo) is not None and c[campo] not in lista:
            pr.append(f"{n}: {campo} {c[campo]!r} não existe (use {', '.join(lista)})")
    pal = c.get("paleta")
    if pal in PALETAS and card in ESCUROS | set(CATALOGO) and card != "livre" and (pal in PALETAS_ESCURAS) != (card in ESCUROS):
        pr.append(f"{n}: paleta {pal} é {'escura' if pal in PALETAS_ESCURAS else 'clara'} e o card {card} é "
                  f"{'escuro' if card in ESCUROS else 'claro'} (texto ficaria sem contraste)")
    if c.get("fundo") == "foto" and not (c.get("foto_fundo") or (c.get("campos") or {}).get("midia")):
        pr.append(f"{n}: fundo foto sem asset aprovado (foto_fundo ou campos.midia)")
    if pal in PALETAS_GRAFITE and c.get("fundo") in (None, "chapado"):
        pr.append(f"{n}: paleta {pal} com fundo chapado = fundo preto liso (regra dela); use papel, pontilhado, quadriculado, listras ou gradiente")
    return pr


def validar_livre(c: dict, n: str) -> list[str]:
    pr, campos = [], c.get("campos") or {}
    bl = campos.get("blocos")
    if not isinstance(bl, list) or not bl:
        return [f"{n} (livre): falta campos.blocos (1 a 5 blocos)"]
    if len(bl) > 5:
        pr.append(f"{n} (livre): no máximo 5 blocos")
    fala = _seq(c.get("fala", ""))
    for j, b in enumerate(bl):
        m = f"{n} bloco {j + 1}"
        if not isinstance(b, dict) or b.get("tipo") not in BLOCOS:
            pr.append(f"{m}: tipo {(b or {}).get('tipo') if isinstance(b, dict) else b!r} não existe (use {', '.join(BLOCOS)})")
            continue
        t = b["tipo"]
        for o in OBRIG_BLOCO[t]:
            if not b.get(o):
                pr.append(f"{m} ({t}): falta {o}")
        for k, lim in LIMITE_BLOCO.items():
            if isinstance(b.get(k), str) and len(b[k]) > (lim if not (k == "texto" and t == "titulo") else LIMITE_BLOCO["titulo"]):
                pr.append(f"{m} ({t}): {k} com mais de {lim if not (k == 'texto' and t == 'titulo') else 60} caracteres")
        if t == "titulo" and b.get("letra") not in (None, "rubik", "anton"):
            pr.append(f"{m} (titulo): letra {b['letra']!r} não existe (use rubik ou anton; nada de serifa, regra dela)")
        if t in ("titulo", "texto") and j == 1 and c.get("composicao") == "colunas" and len(str(b.get("texto", ""))) > 30:
            pr.append(f"{m}: na composição colunas o 2º bloco fica numa coluna estreita; texto com mais de 30 caracteres "
                      "não cabe legível (título mínimo 64 px). Use outra composição ou encurte")
        if t in DISPOSICAO and b.get("disposicao") is not None and b["disposicao"] not in DISPOSICAO[t]:
            pr.append(f"{m} ({t}): disposicao {b['disposicao']!r} não existe (use {', '.join(DISPOSICAO[t])})")
        if b.get("icone") and b["icone"] not in ICONES:
            pr.append(f"{m}: ícone {b['icone']!r} não existe")
        for k in ("icone_antes", "icone_depois"):
            if b.get(k) and b[k] not in ICONES:
                pr.append(f"{m}: ícone {b[k]!r} não existe")
        for lista in ("itens", "pessoas"):
            v = b.get(lista)
            if v is None:
                continue
            if not isinstance(v, list) or len(v) > 4:
                pr.append(f"{m}: {lista} precisa ser lista de 1 a 4")
                continue
            for q, it in enumerate(v):
                if not isinstance(it, dict):
                    pr.append(f"{m}: {lista}[{q}] não é objeto")
                    continue
                if isinstance(it.get("texto"), str) and len(it["texto"]) > LIMITE["texto"]:
                    pr.append(f"{m}: {lista}[{q}].texto longo demais (máx {LIMITE['texto']})")
                if it.get("icone") and it["icone"] not in ICONES:
                    pr.append(f"{m}: ícone {it['icone']!r} não existe")
                if it.get("entra") and _achar(fala, _seq(it["entra"])) is None:
                    pr.append(f"{m}: {lista}[{q}].entra não está na fala da cena")
        for k in ("entra", "entra_depois"):
            if b.get(k) and _achar(fala, _seq(b[k])) is None:
                pr.append(f"{m}: {k} não está na fala da cena")
        if t == "conexao":
            for k in ("de", "para"):
                if b.get(k) is not None and not (isinstance(b[k], dict) and b[k].get("nome")):
                    pr.append(f"{m} (conexao): {k} precisa de nome")
    return pr


def validar(c: dict, i: int = 0) -> list[str]:
    """Problemas de uma cena card (lista vazia = ok)."""
    pr, n = [], f"cena {i}"
    card = str(c.get("card", ""))
    if card == "livre":
        return validar_variacao(c, n) + validar_livre(c, n)
    if card in PAINEL:
        return validar_painel(c, n)
    if card not in CATALOGO:
        return [f"{n}: card {card!r} fora do acervo ({', '.join(CATALOGO)}), não é 'livre' nem card do Painel ({', '.join(PAINEL)})"]
    pr += validar_variacao(c, n)
    campos = c.get("campos") or {}
    for o in OBRIG[card]:
        v = campos.get(o)
        if not v or (isinstance(v, list) and not len(v)):
            pr.append(f"{n} (card {card}): falta {o}")
    for k, lim in LIMITE.items():
        if isinstance(campos.get(k), str) and len(campos[k]) > lim:
            pr.append(f"{n} (card {card}): {k} com mais de {lim} caracteres")
    for lista in ("itens", "pessoas", "barras"):
        for j, it in enumerate(campos.get(lista) or []):
            if not isinstance(it, dict):
                pr.append(f"{n}: {lista}[{j}] não é objeto")
                continue
            for k in ("texto", "aspas"):
                if isinstance(it.get(k), str) and len(it[k]) > LIMITE[k]:
                    pr.append(f"{n}: {lista}[{j}].{k} longo demais (máx {LIMITE[k]})")
            if it.get("entra") and _achar(_seq(c.get("fala", "")), _seq(it["entra"])) is None:
                pr.append(f"{n}: {lista}[{j}].entra não está na fala da cena")
            if it.get("icone") and it["icone"] not in ICONES:
                pr.append(f"{n}: ícone {it['icone']!r} não existe")
    if campos.get("entra_depois") and _achar(_seq(c.get("fala", "")), _seq(campos["entra_depois"])) is None:
        pr.append(f"{n}: entra_depois não está na fala da cena")
    for k in ("icone", "icone_antes", "icone_depois"):
        if campos.get(k) and campos[k] not in ICONES:
            pr.append(f"{n}: ícone {campos[k]!r} não existe")
    if len(campos.get("itens") or []) > 4 or len(campos.get("pessoas") or []) > 4:
        pr.append(f"{n}: no máximo 4 itens/pessoas por card")
    return pr



def validar_painel(c: dict, n: str) -> list[str]:
    """Card do Painel (pN): campos mínimos, limites de texto, 'entra' dentro da fala e pessoa com chip (regra dela)."""
    card, pr, campos = str(c.get("card")), [], c.get("campos") or {}
    for o in OBRIG_PAINEL[card]:
        v = campos.get(o)
        if not v or (isinstance(v, (list, dict)) and not len(v)):
            pr.append(f"{n} (card {card}): falta {o}")
    for k, lim in {**LIMITE, "citacao": 120, "legenda_foto": 60, "grafico_titulo": 44, "nota": 60, "serie": 16, "pergunta": 40, "lugar": 40}.items():
        if isinstance(campos.get(k), str) and len(campos[k]) > lim:
            pr.append(f"{n} (card {card}): {k} com mais de {lim} caracteres")
    fala = _seq(c.get("fala", ""))
    pessoas = [campos["pessoa"]] if isinstance(campos.get("pessoa"), dict) else []
    for lista in ("itens", "pessoas", "barras"):
        v = campos.get(lista)
        if v is None:
            continue
        if not isinstance(v, list) or len(v) > (5 if lista == "barras" else 4):
            pr.append(f"{n} (card {card}): {lista} precisa ser lista (máx {5 if lista == 'barras' else 4})")
            continue
        for j, it in enumerate(v):
            if not isinstance(it, dict):
                pr.append(f"{n}: {lista}[{j}] não é objeto")
                continue
            if isinstance(it.get("texto"), str) and len(it["texto"]) > LIMITE["texto"]:
                pr.append(f"{n}: {lista}[{j}].texto longo demais (máx {LIMITE['texto']})")
            if it.get("entra") and _achar(fala, _seq(it["entra"])) is None:
                pr.append(f"{n}: {lista}[{j}].entra não está na fala da cena")
            if lista == "barras" and not isinstance(it.get("valor"), (int, float)):
                pr.append(f"{n}: barras[{j}].valor precisa ser número")
            if lista == "pessoas" or (lista == "itens" and it.get("nome")):
                pessoas.append(it)
    for ps in pessoas:  # regra dela: toda pessoa na tela com nome + partido + ideologia
        if ps.get("nome") and not (ps.get("chip") or (ps.get("partido") and ps.get("ideologia"))):
            pr.append(f"{n} (card {card}): {ps['nome']} sem partido e ideologia (chip)")
    return pr


def marcas(cena: dict, palavras_cena: list[dict]) -> dict:
    """Troca 'entra' (trecho da fala) pelo segundo absoluto 't' em que a voz fala o trecho."""
    alvo = [_norm(p["text"]) for p in palavras_cena]
    campos = json.loads(json.dumps(cena.get("campos") or {}))

    def tempo(trecho):
        k = _achar(alvo, _seq(trecho))
        return round(palavras_cena[k]["start"], 3) if k is not None else None

    for lista in ("itens", "pessoas", "barras"):
        for it in campos.get(lista) or []:
            if isinstance(it, dict) and it.get("entra"):
                t = tempo(it["entra"])
                if t is not None:
                    it["t"] = t
    if campos.get("entra_depois"):
        t = tempo(campos["entra_depois"])
        if t is not None:
            campos["t_depois"] = t
    if campos.get("entra_nota"):  # 25/11 (A1 BC-ESCUTA): nota do p79 entra na fala
        t = tempo(campos["entra_nota"])
        if t is not None:
            campos["t_nota"] = t
    if campos.get("entra_apoio"):  # 25/11 (A2 EL-NINO): apoio do p83/p85 entra na fala (capa parada 5 s, cena 17 parada)
        t = tempo(campos["entra_apoio"])
        if t is not None:
            campos["t_apoio"] = t
    if campos.get("entra_etiqueta"):  # 25/11 (A3 BIG-TECHS): selo do p116 entra na fala (capa parada 7 s)
        t = tempo(campos["entra_etiqueta"])
        if t is not None:
            campos["t_etiqueta"] = t
    fx = campos.get("faixa")  # 25/11 (A1 BC-ESCUTA): faixa de referência no gráfico do p79, cada parte entra na fala
    if isinstance(fx, dict):
        for k, dest in (("entra", "t"), ("entra_teto", "t_teto"), ("entra_sub", "t_sub"), ("entra_depois", "t_depois")):
            if fx.get(k):
                t = tempo(fx[k])
                if t is not None:
                    fx[dest] = t
    for b in campos.get("blocos") or []:  # card livre: mesma regra dentro de cada bloco
        if not isinstance(b, dict):
            continue
        for lista in ("itens", "pessoas"):
            for it in b.get(lista) or []:
                if isinstance(it, dict) and it.get("entra"):
                    t = tempo(it["entra"])
                    if t is not None:
                        it["t"] = t
        for k, dest in (("entra", "t"), ("entra_depois", "t_depois")):
            if b.get(k):
                t = tempo(b[k])
                if t is not None:
                    b[dest] = t
    return campos


def titulo_de(campos: dict) -> str:
    """Título da cena (acervo: campos.titulo; livre: 1º bloco titulo, senão 1º texto)."""
    campos = campos or {}
    if campos.get("titulo"):
        return str(campos["titulo"])
    bl = [b for b in campos.get("blocos") or [] if isinstance(b, dict)]
    b = next((b for b in bl if b.get("tipo") == "titulo"), None) or next((b for b in bl if b.get("texto") or b.get("valor")), None)
    return str((b or {}).get("texto") or (b or {}).get("valor") or "")


def assinatura(c: dict) -> str:
    """Combinação visual da cena: card|composição|moldura|fundo|paleta (+ blocos e disposição no livre).
    Cena sem os campos novos = o card do acervo igual ao que ela já postou ("molde")."""
    card = str(c.get("card", ""))
    if card == "livre":
        bl = [b for b in ((c.get("campos") or {}).get("blocos") or []) if isinstance(b, dict)]
        miolo = "+".join(b.get("tipo", "?") + (":" + b["disposicao"] if b.get("disposicao") else "") for b in bl)
        comp = c.get("composicao") or "pilha"
        pal = c.get("paleta") or "creme-amarelo"
    elif card in PAINEL:  # card do Painel: o desenho é o do template; o que varia é a cor da peça
        miolo, comp, pal = "painel", "template", str(c.get("cor_tema") or "cor-original").lower()
    else:
        miolo, comp, pal = "acervo", c.get("composicao") or "esq", c.get("paleta") or "acervo"
    return "|".join([card, comp, c.get("variante") or "limpa", c.get("fundo") or "original", pal, miolo])


def nucleo(c: dict) -> str:
    """Só a composição (sem cor/fundo/moldura): igual em sequência = a mesma cara."""
    a = assinatura(c).split("|")
    return "|".join([a[0], a[1], a[5]])


ROTACAO = [("centro", "creme-amarelo", "papel", "filete"), ("faixa", "grafite-rosa", "pontilhado", "cantos"),
           ("colunas", "branco-verde", "quadriculado", "fita"), ("base", "terracota", "listras", "limpa"),
           ("manchete", "amarelo", "gradiente", "filete"), ("diagonal", "mata", "quadriculado", "cantos"),
           ("cartao", "lilas", "pontilhado", "carimbo"), ("pilha", "creme-rosa", "papel", "fita"),
           ("centro", "grafite-verde", "gradiente", "limpa"), ("faixa", "branco-laranja", "listras", "carimbo"),
           ("base", "vinho", "pontilhado", "filete"), ("colunas", "rosa", "papel", "cantos")]


def converter(cenas: list[dict], rotulos: list[str] | None = None, evitar: set | None = None) -> list[dict]:
    """Plano B sem modelo (23/11: agora no card livre, variando composição/paleta/fundo/moldura e pulando as
    combinações de 'evitar' = usadas nas últimas peças). title/quote/bars viram blocos (número vira bloco numero)."""
    evitar, out, usadas, k = set(evitar or ()), [], set(), 0
    for i, c in enumerate(cenas):
        if c.get("type") == "card":
            out.append(c)
            usadas.add(assinatura(c))
            continue
        t = str(c.get("title") or c.get("quote") or "").strip()[:60]
        num = re.search(r"\d[\d.,]*", t)
        if i == 0:
            blocos = [{"tipo": "titulo", "texto": t, "letra": "anton", "tamanho": "g"}]
        elif c.get("type") == "quote":
            blocos = [{"tipo": "titulo", "texto": t, "tamanho": "m"}]  # 23/11: sem serifa (regra dela)
        elif c.get("type") == "bars" and c.get("bars"):
            blocos = [{"tipo": "titulo", "texto": t, "tamanho": "m"},
                      {"tipo": "itens", "disposicao": "numerada", "itens": [{"texto": f"{b.get('label')}: {b.get('value')}"[:60]} for b in c["bars"][:4]]}]
        elif num and len(t) < 60:
            resto = t.replace(num.group(0), "").strip(" :·-")
            blocos = [{"tipo": "numero", "valor": num.group(0), "tamanho": "grande"}] + ([{"tipo": "titulo", "texto": resto, "tamanho": "m"}] if resto else [])
        else:
            blocos = [{"tipo": "titulo", "texto": t, "tamanho": "g"}]
        base = {"type": "card", "card": "livre", "campos": {"blocos": blocos}, "fala": c.get("fala", ""), "source": c.get("source"),
                "inspiracao": ["plano B automático", "acervo coolonização BR"],
                "porque": "plano B sem modelo: composição em rodízio, pulando as combinações usadas nas últimas peças"}
        for _ in range(len(ROTACAO) * 2):
            comp, pal, fu, mol = ROTACAO[k % len(ROTACAO)]
            k += 1
            cand = dict(base, composicao=comp, paleta=pal, fundo=fu, variante=mol)
            ant = out[-1] if out else None
            if assinatura(cand) not in evitar | usadas and not (ant and nucleo(ant) == nucleo(cand)):
                break
        usadas.add(assinatura(cand))
        out.append({kk: v for kk, v in cand.items() if v is not None})
    return out


def fontes_css() -> str:
    partes = []
    for fam, peso, arq in FONTES:
        p = ANIM / "fonts" / arq
        if p.exists():
            b = base64.b64encode(p.read_bytes()).decode()
            partes.append(f"@font-face{{font-family:'{fam}';font-weight:{peso};src:url(data:font/woff2;base64,{b}) format('woff2')}}")
    return "\n".join(partes)


def bloco() -> str:
    """<style> com as fontes embutidas + <script> do renderizador (sem nada de fora: serve pro artefato e pro CI)."""
    js = (ANIM / "cards.js").read_text(encoding="utf-8").replace("</", "<\\/")
    return f"<style>{fontes_css()}</style><script>{js}</script>"


def injetar(html: str) -> str:
    return html.replace("<!--CARDS-->", bloco())


def texto_catalogo() -> str:
    return "\n".join(f"- card {k}: {n} (usar em: {u}). Campos: {c}" for k, (n, u, c) in CATALOGO.items())


def texto_painel() -> str:
    return "\n".join(f"- card \"{k}\": {n} (usar em: {u}). Campos: {c}" for k, (n, u, c) in PAINEL.items())


def texto_variacao() -> str:
    return (f"- {LIVRE_DESC}\n- composicao (card livre): {', '.join(LAYOUTS)}; composicao (card do acervo = alinhamento): {', '.join(ALINHAMENTOS)}\n"
            f"- variante (moldura): {', '.join(MOLDURAS)}\n- fundo: {', '.join(FUNDOS)} (foto só com asset aprovado)\n"
            f"- paleta: {', '.join(PALETAS)} (escuras: {', '.join(sorted(PALETAS_ESCURAS))}; card do acervo escuro ({', '.join(sorted(ESCUROS))}) só com paleta escura, claro só com clara; grafite nunca com fundo chapado)\n"
            f"- entrada (direção da animação): {', '.join(ENTRADAS)}")
