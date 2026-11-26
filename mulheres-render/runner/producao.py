"""Camada 9, parte que o Actions executa (sem modelo): voz grátis, manifesto do player, quadros e transcrição.

Entra: pecas/<ID>/cenas.json + fala.txt (escritos pelo Claude em camadas.producao_cenas).
Sai em pecas/<ID>/v<N>/:
  voz.mp3            voz grátis da Microsoft (Thalita; nunca Francisca), take único
  palavras.json      tempos de cada palavra (marcas da própria voz)
  transcricao.json   transcrição INDEPENDENTE do áudio real (faster-whisper), pra auditoria comparar com o roteiro
  manifest.json      formato do player /reel?id=ID&v=N (validado pelo news-flow.js)
  quadros/*.png      1 por segundo + 1 no meio de cada cena (renderizados do manifesto, não MP4)
  tira.png           tira de contato (1 quadro por cena) pro ritmo de cor
  prova-sync.json    diferença entre palavras da voz e transcrição real (sync fica pendente sem prova)
Nada de MP4 aqui (MP4 só depois do Sim, camada 12).
"""
from __future__ import annotations

import asyncio
import difflib
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import estado  # noqa: E402
import cards  # noqa: E402
import ritmo_cor  # noqa: E402
from comum import estado_dir, gravar_json, publicar_estado, sha256_bytes, sha256_texto  # noqa: E402

VOZ = os.environ.get("VOZ_GRATIS", "pt-BR-ThalitaMultilingualNeural")
assert "Francisca" not in VOZ, "Francisca é proibida"
AQUI = pathlib.Path(__file__).resolve().parent


def _norm(w: str) -> str:
    return re.sub(r"[^\wà-úÀ-Ú]", "", w.lower())


def _chave_voz(texto: str) -> str:
    import hashlib
    rate = os.environ.get("VOZ_RATE", "+8%")
    return hashlib.sha256(f"{VOZ}|{rate}|{texto}".encode("utf-8")).hexdigest()[:20]


def _cache_dir() -> pathlib.Path | None:
    """Rota sem Actions (24/11): voz e transcrição feitas fora (Composio workbench) e guardadas em
    automacao-estado:voz-cache/<chave>.mp3|.json|.trans.json. Falta no cache vira pedido em voz-cache/pedidos/."""
    c = os.environ.get("VOZ_CACHE")
    return pathlib.Path(c) if c else None


class VozPendente(RuntimeError):
    pass


async def _tts(texto: str, mp3: pathlib.Path) -> list[dict]:
    cd = _cache_dir()
    if cd is not None:
        k = _chave_voz(texto)
        if (cd / f"{k}.mp3").exists() and (cd / f"{k}.json").exists():
            mp3.write_bytes((cd / f"{k}.mp3").read_bytes())
            return json.loads((cd / f"{k}.json").read_text(encoding="utf-8"))
        (cd / "pedidos").mkdir(parents=True, exist_ok=True)
        (cd / "pedidos" / f"{k}.txt").write_text(f"{VOZ}\n{os.environ.get('VOZ_RATE', '+8%')}\n{texto}", encoding="utf-8")
        raise VozPendente(f"voz no cache pendente: {k}")
    import edge_tts
    com = edge_tts.Communicate(texto, VOZ, rate=os.environ.get("VOZ_RATE", "+8%"), boundary="WordBoundary")
    palavras = []
    with mp3.open("wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                ini = ch["offset"] / 1e7
                palavras.append({"text": ch["text"], "start": round(ini, 3), "end": round(ini + ch["duration"] / 1e7, 3)})
    return palavras


def transcrever(mp3: pathlib.Path) -> list[dict]:
    cd = _cache_dir()
    if cd is not None:
        import hashlib
        t = cd / f"{hashlib.sha256(mp3.read_bytes()).hexdigest()[:20]}.trans.json"
        if t.exists():
            return json.loads(t.read_text(encoding="utf-8"))
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return []
    import subprocess
    import numpy as np
    try:  # áudio decodificado pelo ffmpeg (PCM 16 kHz mono): evita a incompatibilidade do pacote av
        import shutil
        exe = shutil.which("ffmpeg")
        if not exe:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
        pcm = subprocess.run([exe, "-v", "error", "-i", str(mp3), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                             capture_output=True, check=True).stdout
        audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
        m = WhisperModel(os.environ.get("WHISPER_MODELO", "small"), device="cpu", compute_type="int8")
        segs, _ = m.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False)
        return [{"text": w.word.strip(), "start": round(float(w.start), 3), "end": round(float(w.end), 3)}
                for s in segs for w in (s.words or [])]
    except Exception as e:  # sem transcrição = sync fica PENDENTE (nunca "passou")
        print("transcrição falhou:", str(e)[:200], file=sys.stderr)
        return []


def _tokens_sync(textos: list[str]) -> list[str]:
    """24/11: compara no mesmo espaço o que a voz fala e o que a transcrição escreve: número em dígito vira palavra
    ("8" = "oito"), "pra" = "para", sem acento ("tráfico" = "trafico"). Não afrouxa limite: só não conta como
    diferença o que é o mesmo som escrito de outro jeito."""
    import unicodedata
    try:
        from num2words import num2words
    except ImportError:
        num2words = None
    out = []
    for t in textos:
        # 25/11: pontuação colada no número ("2018,", "80,9.") impedia a troca por extenso e "80,9." virava "809"
        t = re.sub(r"(\d%?)[.,;:!?…]+(?=\s|$)", r"\1", t)
        # 25/11 (Rota 2): a transcrição escreve "R $ 4 ,67" / "R$3" onde a voz fala "quatro e sessenta e sete" /
        # "três": junta o número partido e tira o símbolo (a palavra "reais" falada continua contando no texto).
        t = re.sub(r"(\d)\s+,(\d)", r"\1,\2", t)
        t = re.sub(r"(?:\b(?:R|US)\s*)?\$\s*(?=\d)", "", t)
        t = re.sub(r"(\d),(\d{2})(?!\d)", r"\1 e \2", t)
        for w in re.split(r"\s+", t):
            w = w.strip().lower()
            if num2words and re.fullmatch(r"\d+([.,]\d+)?%?", w):
                pct = w.endswith("%")
                n = w.rstrip("%").replace(".", "").replace(",", ".")
                try:
                    w = num2words(float(n) if "." in n else int(n), lang="pt_BR") + (" por cento" if pct else "")
                except (ValueError, NotImplementedError):
                    pass
            for x in re.split(r"[\s-]+", w):
                x = "".join(c for c in unicodedata.normalize("NFD", _norm(x)) if unicodedata.category(c) != "Mn")
                if x == "pra":
                    x = "para"
                if x:
                    out.append(x)
    return out


def _marcas_sync(palavras: list[dict]) -> tuple[list[str], dict[int, tuple[float, int]]]:
    """Expande a grafia sem atribuir tempos inventados às palavras interiores de um grupo."""
    tokens = []
    marcas = {}
    # 25/11 (Rota 2): o transcritor parte "R$ 4,67" em pedaços ("R", "$", "4", ",67"); junta antes de comparar,
    # mantendo o tempo do primeiro pedaço.
    juntas = []
    for palavra in palavras:
        tx = str(palavra.get("text", "")).strip()
        if juntas:
            ant = juntas[-1]["text"]
            if (re.fullmatch(r"(R|US)\$?", ant) and re.match(r"\$", tx)) or (re.fullmatch(r"(R|US)\$?", ant) and re.match(r"\$?\s*\d", tx)) or (re.fullmatch(r"(R|US)?\$", ant) and re.match(r"\d", tx)) \
                    or (re.search(r"\d$", ant) and re.fullmatch(r",\d+[.,;:!?…]*", tx)):
                juntas[-1] = {**juntas[-1], "text": ant + tx}
                continue
        juntas.append({**palavra, "text": tx})
    palavras = juntas
    for palavra in palavras:
        grupo = _tokens_sync([palavra["text"]])
        if grupo:
            marcas[len(tokens)] = (palavra["start"], len(tokens) + len(grupo))
            tokens.extend(grupo)
    return tokens, marcas


def prova_sync(palavras: list[dict], trans: list[dict], fala: str = "") -> dict:
    """Prova de sincronia (revisão ChatGPT item 7): (a) a transcrição INDEPENDENTE bate com a fala canônica;
    (b) os tempos da legenda (marcas da voz) batem com os tempos ouvidos, inclusive nos extremos (p95 e máximo).
    Falta qualquer prova = pendente. Isto NÃO mede o relógio do player (prova separada no Painel)."""
    if not trans:
        return {"ok": False, "motivo": "sem transcrição independente (NÃO OBSERVADO)"}
    canon = _tokens_sync([fala]) if fala.strip() else _tokens_sync([p["text"] for p in palavras])
    escritos, marcas_legenda = _marcas_sync(palavras)
    ouvido, marcas_voz = _marcas_sync(trans)
    sm_txt = difflib.SequenceMatcher(a=canon, b=ouvido, autojunk=False)
    sm = difflib.SequenceMatcher(a=escritos, b=ouvido, autojunk=False)
    difs = []
    # 25/11 (Rota 2): logo depois de um trecho que a transcrição engoliu ("cento a mais" sumiu), o transcritor estica
    # a palavra seguinte pra cobrir o buraco e o tempo dela não é medida do áudio. A 1ª palavra de um bloco que vem
    # depois de palavras faltando na transcrição não entra no desvio (continua contando no texto e na cobertura).
    casadas_fora = 0
    apos_buraco = {j2 for op, i1, i2, j1, j2 in sm.get_opcodes() if op == "delete" or (op == "replace" and (i2 - i1) > (j2 - j1))}
    for bloco in sm.get_matching_blocks():
        fim_legenda = bloco.a + bloco.size
        fim_voz = bloco.b + bloco.size
        for i, j in zip(range(bloco.a, fim_legenda), range(bloco.b, fim_voz)):
            if i in marcas_legenda and j in marcas_voz:
                tempo_legenda, fim_grupo_legenda = marcas_legenda[i]
                tempo_voz, fim_grupo_voz = marcas_voz[j]
                if fim_grupo_legenda <= fim_legenda and fim_grupo_voz <= fim_voz:
                    if j == bloco.b and j in apos_buraco:
                        casadas_fora += 1
                        continue
                    difs.append(abs(tempo_legenda - tempo_voz))
    difs.sort()
    trocadas = [(" ".join(canon[i1:i2]), " ".join(ouvido[j1:j2])) for op, i1, i2, j1, j2 in sm_txt.get_opcodes() if op != "equal"]
    if not difs:
        return {"ok": False, "motivo": "nenhuma palavra casou"}
    p95 = difs[min(len(difs) - 1, int(len(difs) * 0.95))]
    cobertura = (len(difs) + casadas_fora) / max(1, len(palavras))
    ok = sm_txt.ratio() >= 0.9 and cobertura >= 0.85 and p95 <= 0.35 and difs[-1] <= 1.0
    return {"ok": bool(ok), "semelhanca_com_roteiro": round(sm_txt.ratio(), 3), "cobertura_legenda": round(cobertura, 3),
            "desvio_mediano_s": round(difs[len(difs) // 2], 3), "desvio_p95_s": round(p95, 3), "desvio_max_s": round(difs[-1], 3),
            "trechos_diferentes": trocadas[:40], "limites": "texto>=0,9; cobertura>=0,85; p95<=0,35 s; máx<=1 s"}


def validar_cenas(cenas: list[dict], fala: str) -> list[str]:
    """Esquema de cenas.json antes da voz (item 23)."""
    probs = []
    if not cenas:
        probs.append("sem cenas")
    for i, c in enumerate(cenas, 1):
        if c.get("type") not in ("title", "quote", "bars", "card"):
            probs.append(f"cena {i}: tipo {c.get('type')!r} não suportado")
        if c.get("type") == "card":
            probs += cards.validar(c, i)
        if not str(c.get("fala", "")).strip():
            probs.append(f"cena {i}: sem fala")
        if c.get("type") == "bars" and not c.get("bars"):
            probs.append(f"cena {i}: bars sem barras")
        for campo in ("background", "color"):
            if c.get(campo) and not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(c[campo])):
                probs.append(f"cena {i}: {campo} inválida")
    juntas = " ".join(_norm(w) for c in cenas for w in str(c.get("fala", "")).split() if _norm(w))
    if juntas != " ".join(_norm(w) for w in fala.split() if _norm(w)):
        probs.append("a fala das cenas, junta, não é igual ao fala.txt")
    return probs


def _pauta(pid: str) -> dict:
    f = estado_dir() / "pecas" / pid / "PAUTA.json"
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    except ValueError:
        return {}


def _separar_palavras(palavras: list[dict]) -> list[dict]:
    """25/11 (A1 da peça BC): a voz grátis junta número e palavra num marcador só ("17 reuniões", "Em 2025").
    A contagem por cena conta palavras da fala; sem separar, cada junção atrasa o corte das cenas seguintes em uma
    palavra (10 junções = cena trocando 2 a 4 s depois da fala) e o 'entra' com número não acha o trecho."""
    out = []
    for p in palavras:
        partes = str(p.get("text", "")).split()
        if len(partes) <= 1:
            out.append(p)
            continue
        d = (p["end"] - p["start"]) / len(partes)
        out.extend({**p, "text": t, "start": round(p["start"] + j * d, 3), "end": round(p["start"] + (j + 1) * d, 3)}
                   for j, t in enumerate(partes))
    return out


def montar_manifesto(pid: str, v: int, cenas: list[dict], palavras: list[dict], audio_rel: str) -> dict:
    """Distribui as palavras da voz pelas cenas (pela fala de cada cena) e fecha a linha do tempo sem buraco."""
    palavras = _separar_palavras(palavras)
    tokens = [_norm(p["text"]) for p in palavras]
    i, cortes = 0, []
    for c in cenas:
        n = len([w for w in re.split(r"\s+", c.get("fala", "").strip()) if _norm(w)])
        i = min(len(tokens), i + n)
        cortes.append(i)
    cortes[-1] = len(tokens)
    fim_audio = palavras[-1]["end"] + 0.6
    scenes, ini_t, ini_w = [], 0.0, 0
    for k, (c, corte) in enumerate(zip(cenas, cortes)):
        fim_t = fim_audio if k == len(cenas) - 1 else (palavras[corte]["start"] if corte < len(palavras) else fim_audio)
        fim_t = max(fim_t, ini_t + 0.8)
        s = {"type": c.get("type", "title"), "start": round(ini_t, 3), "end": round(fim_t, 3)}
        for campo in ("title", "quote", "bars", "source", "background", "color", "card",
                      "composicao", "variante", "fundo", "paleta", "entrada", "foto_fundo",
                      "cor_tema", "legenda_estilo", "template_painel"):  # 23/11: variação por cena; 24/11: cor e legenda
            if c.get(campo) is not None:
                s[campo] = c[campo]
        if c.get("type") == "card":  # animação ligada à fala: "entra" vira o segundo em que a voz fala o trecho
            s["campos"] = cards.marcas(c, palavras[ini_w:corte])
            s.setdefault("title", cards.titulo_de(s["campos"]))
        for campo, chave in (("cor_tema", "cor_principal"), ("legenda_estilo", "legenda_estilo")):  # 24/11: regra 1 dela
            if campo not in s and _pauta(pid).get(chave):
                s[campo] = _pauta(pid)[chave]
        scenes.append(s)
        ini_t, ini_w = s["end"], corte
    words, pagina, linha, n_lin = [], 0, 0, 0
    inicios = set(cortes[:-1])  # legenda não mistura cenas: cena nova começa página nova
    # 25/11 (A2 v8 BIG-TECHS): grafia só de pronúncia na fala ("Cáde") não vai pra legenda.
    # PAUTA.json "legenda_trocas": {"Cáde": "Cade"}; sem o campo, nada muda.
    trocas = _pauta(pid).get("legenda_trocas") or {}
    for k, p in enumerate(palavras):  # duas linhas por página (regra dela), ~4 palavras por linha
        if k in inicios and (n_lin or linha):
            pagina, linha, n_lin = pagina + 1, 0, 0
        texto = p["text"]
        for de, para in trocas.items():
            texto = texto.replace(de, para)
        words.append({"text": texto, "start": p["start"], "end": min(p["end"], scenes[-1]["end"]), "page": pagina, "line": linha})
        n_lin += 1
        if n_lin >= 4:
            n_lin, linha = 0, linha + 1
            if linha > 1:
                linha, pagina = 0, pagina + 1
    titulo = cenas[0].get("title") or cards.titulo_de(cenas[0].get("campos") or {}) or pid
    man = {"id": pid, "version": v, "title": titulo, "audio": audio_rel, "scenes": scenes, "words": words}
    pend = pendencias(man)
    if pend:
        man["pendencias"] = pend
    return man


# régua da zona segura dela, no palco de auditoria 540x960 (metade de 1080x1920: x 150-915, y 268-1680)
ZS = {"x0": 75, "x1": 457.5, "y0": 134, "y1": 840}
ZS_REGRA = ("texto real (Range.getClientRects, tinta, destaque e sombra) entre x 150-915 e y 268-1680 no palco 1080x1920 "
            "(x 75-457 e y 134-840 em 540x960); @handle y 1626 e fonte y 1668 (até 3 linhas pequenas, sem '…') sem colidir; "
            "sem texto sobre texto/retrato, sem letra cortada; legenda no máximo 2 linhas")


def pendencias(manifest: dict) -> list[str]:
    """Pendências visíveis pra ela: pessoa mostrada só com iniciais (sem foto real verificada)."""
    out = []
    for i, s in enumerate(manifest.get("scenes") or [], 1):
        c = s.get("campos") or {}
        nomes = [p.get("nome") for p in c.get("pessoas") or [] if isinstance(p, dict) and p.get("nome") and not p.get("foto")]
        if c.get("pessoa") and not c.get("foto_pessoa"):
            nomes.append(c["pessoa"])
        for n in nomes:
            out.append(f"FALTA FOTO REAL: {n} (cena {i}, card {s.get('card')}) aparece só com as iniciais; "
                       "trocar por recorte de foto real verificada")
    return out


FONTES_JS = """async () => { if (!document.fonts) return; for (const f of ['400 50px Rubik', '600 50px Rubik', '700 50px Rubik',
  '800 50px Rubik', '900 50px Rubik', '400 50px Anton', '400 50px "DM Serif Display"', '700 50px "JetBrains Mono"',
  '400 50px "JetBrains Mono"', '700 50px "Inter Tight"', '400 50px "Patrick Hand SC"']) await document.fonts.load(f); await document.fonts.ready;
  if (window.CARDS && window.CARDS.pronto) await window.CARDS.pronto(); }"""


MAX_BYTES_QUADRO = 900 * 1024


def _limitar_png_auditoria(caminho: pathlib.Path) -> None:
    """Mantém PNGs grandes legíveis no pacote que passa pelo conector do GitHub."""
    if caminho.stat().st_size <= MAX_BYTES_QUADRO:
        return
    from io import BytesIO
    from PIL import Image

    with Image.open(caminho) as original:
        quadro = original.convert("RGB")
    quadro.thumbnail((540, 960), Image.Resampling.LANCZOS)
    with BytesIO() as imagem:
        quadro.save(imagem, format="PNG", optimize=True)
        if imagem.tell() > MAX_BYTES_QUADRO:
            imagem.seek(0)
            imagem.truncate()
            quadro.quantize(colors=256, dither=Image.Dither.NONE).save(imagem, format="PNG", optimize=True)
        caminho.write_bytes(imagem.getvalue())


def quadros(manifest: dict, mp3: pathlib.Path, saida: pathlib.Path) -> list[str]:
    """Renderiza o manifesto (mesmo desenho do player pros tipos title/quote/bars) e tira os PNG."""
    from playwright.sync_api import sync_playwright
    saida.mkdir(parents=True, exist_ok=True)
    html = (AQUI.parent / "anim" / "quadros.html").read_text(encoding="utf-8")
    tempos = sorted({float(t) for t in range(0, int(manifest["scenes"][-1]["end"]) + 1)} |
                    {round((s["start"] + s["end"]) / 2, 2) for s in manifest["scenes"]})
    feitos = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        pg = b.new_page(viewport={"width": 540, "height": 960}, device_scale_factor=2)
        pg.set_content(cards.injetar(html))
        pg.evaluate(FONTES_JS)  # todas as fontes antes de medir (canvas mede com a fonte real, não a reserva)
        pg.evaluate("m => window.carregar(m)", manifest)
        fora = []
        for t in tempos:
            pg.evaluate(f"window.desenhar({t})")
            nome = f"q_{int(t * 100):06d}.png"
            arquivo = saida / nome
            pg.screenshot(path=str(arquivo))
            _limitar_png_auditoria(arquivo)
            feitos.append(nome)
            # zona segura dela (palco 1080x1920): mede o TEXTO REAL de cada nó (Range.getClientRects + tinta da fonte
            # + fundo do destaque + sombra) no fim da animação, não os containers (23/11: containers davam "fora: []"
            # com "2374/202", e-mail e data cortados na borda). Falha em: texto fora de x 150-915 ou y 268-1680
            # (rodapé até 1730), texto sobre texto, texto sobre retrato, texto cortado por camada, "…", legenda > 2 linhas.
            med = pg.evaluate("() => window.CARDS.medir(document.getElementById('palco'))")
            for pr in med["problemas"]:
                fora.append({"t": t, **pr})
        cores = pg.evaluate("""scenes => scenes.map(({start, end}) => {
            window.desenhar((start + end) / 2);
            const cena = document.querySelector('#palco .cpalco, #palco .cena');
            const rgb = getComputedStyle(cena).backgroundColor.match(/[0-9]+/g).slice(0, 3);
            return '#' + rgb.map(value => Number(value).toString(16).padStart(2, '0')).join('');
        })""", manifest["scenes"])
        b.close()
    gravar_json(saida.parent / "zona-segura.json", {"ok": not fora, "regra": ZS_REGRA, "medida": "CARDS.medir (texto real)",
                                                    "fora": fora[:50]})
    gravar_json(saida.parent / "ritmo-cor.json", {"cores": cores, "problemas": ritmo_cor.conferir(cores)})
    return feitos


def tira(manifest: dict, qdir: pathlib.Path, destino: pathlib.Path) -> None:
    from PIL import Image
    fr = []
    for s in manifest["scenes"]:
        q = qdir / f"q_{int(round((s['start'] + s['end']) / 2, 2) * 100):06d}.png"
        if q.exists():
            fr.append(Image.open(q).resize((180, 320)))
    if not fr:
        return
    t = Image.new("RGB", (188 * len(fr), 320), "#222")
    for i, im in enumerate(fr):
        t.paste(im, (i * 188, 0))
    t.save(destino)


def arquivo_cenas(d: pathlib.Path) -> pathlib.Path:
    bonita = d / "cenas-bonita.json"
    return bonita if bonita.exists() else d / "cenas.json"


def main(pid: str) -> str:
    d = estado_dir() / "pecas" / pid
    arq_cenas = arquivo_cenas(d)
    cenas = json.loads(arq_cenas.read_text(encoding="utf-8"))["cenas"]
    fala = (d / "fala.txt").read_text(encoding="utf-8").strip()
    probs = validar_cenas(cenas, fala)
    if probs:
        estado.registrar(pid, "camada_erro", camada="producao", erro="; ".join(probs)[:300])
        publicar_estado(f"{pid}: cenas inválidas")
        return "erro"
    v = (estado.derivar(pid)["versao_previa"] or 0) + 1
    vd = d / f"v{v}"
    vd.mkdir(parents=True, exist_ok=True)
    mp3 = vd / "voz.mp3"
    palavras = asyncio.run(_tts(fala, mp3))
    if not palavras:
        estado.registrar(pid, "camada_erro", camada="producao", erro="voz grátis sem marcas de palavra")
        publicar_estado(f"{pid}: producao erro")
        return "erro"
    h = sha256_bytes(mp3.read_bytes())
    man = montar_manifesto(pid, v, cenas, palavras, f"/previews/news-assets/{pid}/v{v}/{h}.mp3")
    gravar_json(vd / "palavras.json", palavras)
    gravar_json(vd / "manifest.json", man)
    trans = transcrever(mp3)
    gravar_json(vd / "transcricao.json", trans)
    ps = prova_sync(palavras, trans, fala)
    gravar_json(vd / "prova-sync.json", ps)
    feitos = quadros(man, mp3, vd / "quadros")
    tira(man, vd / "quadros", vd / "tira.png")
    ritmo = json.loads((vd / "ritmo-cor.json").read_text(encoding="utf-8"))["problemas"]
    hc = sha256_texto(json.dumps(man, sort_keys=True))
    estado.registrar(pid, "versao_nova", versao=v, hash_candidato=hc)
    estado.registrar(pid, "prova", prova="sync", ok=ps["ok"], hash_candidato=hc, arquivo=f"v{v}/prova-sync.json")
    estado.registrar(pid, "prova", prova="ritmo_cor", ok=not ritmo, hash_candidato=hc, arquivo=f"v{v}/ritmo-cor.json")
    zs = vd / "zona-segura.json"
    estado.registrar(pid, "prova", prova="safeZone", hash_candidato=hc, arquivo=f"v{v}/zona-segura.json",
                     ok=bool(zs.exists() and json.loads(zs.read_text(encoding="utf-8")).get("ok")))
    estado.registrar(pid, "camada_ok", camada="producao", versao=v, hash_entrada=sha256_texto(fala),
                     hash_saida=hc, arquivo_saida=f"v{v}/manifest.json")
    publicar_estado(f"{pid}: prévia v{v} ({len(feitos)} quadros, sync={'ok' if ps['ok'] else 'pendente'})")
    return f"v{v}"


if __name__ == "__main__":
    print(main(sys.argv[1]))
