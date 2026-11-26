"""Estado da peça com trava, eventos só de acréscimo e reivindicação exclusiva (PLANO-FINAL §2, §10.14, §11.6, §11.8).

Pasta de estado:
  pecas/<ID>/eventos.jsonl   histórico (nunca apagado nem reescrito)
  pecas/<ID>/estado.json     foto derivada dos eventos (pode ser regerada a qualquer hora)
  claims/<chave>.json        reivindicação exclusiva do assunto (ato + evento material)
  locks/<ID>.json            trava com dono e validade

Regras:
- "ok" vale pra ID + versão + hash da entrada. Mudou a entrada, a camada e o que depende dela refazem.
- Camada com erro: tenta de novo nos próximos disparos até 2 vezes; na 3ª vira "pulada" com motivo.
  Camada OBRIGATÓRIA pulada bloqueia a publicação (a peça só pode ir pro Estúdio como diagnóstico).
- Estados finais (liberam a vaga): publicada, arquivada_sem_resposta, recusada, sem_peca_nova.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib
import re

from comum import acrescentar_linha, agora, agora_iso, estado_dir, gravar_json, ler_linhas, publicar_estado

CAMADAS = ["caca", "escolha", "pesquisa", "pessoas", "acao", "roteiro", "revisao-1", "revisao-2", "revisao-3",
           "clareza", "revisao-4", "referencias", "producao", "auditoria-1", "auditoria-2", "auditoria-3", "estudio"]
OBRIGATORIAS = {"pesquisa", "pessoas", "roteiro", "revisao-1", "revisao-2", "revisao-3", "producao",
                "auditoria-1", "auditoria-2", "auditoria-3"}
DEPENDE_DE = {c: CAMADAS[:i] for i, c in enumerate(CAMADAS)}
FINAIS = {"publicada", "arquivada_sem_resposta", "recusada", "sem_peca_nova"}
MAX_ERROS = 2


class JaReivindicado(Exception):
    pass


class Travado(Exception):
    pass


def _p(*partes) -> pathlib.Path:
    return estado_dir().joinpath(*partes)


def chave_canonica(ato: str, evento_material: str) -> str:
    """Ex.: ('PL 2374/2024', 'relator-designado-2026-06-09') -> 'pl-2374-2024__relator-designado-2026-06-09'."""
    norm = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return f"{norm(ato)}__{norm(evento_material)}"


def reivindicar(chave: str, peca_id: str, run_id: str) -> None:
    arq = _p("claims", f"{chave}.json")
    if arq.exists():
        dono = json.loads(arq.read_text(encoding="utf-8"))
        if dono["peca"] != peca_id:
            raise JaReivindicado(f"assunto {chave} já é da peça {dono['peca']}")
        return
    gravar_json(arq, {"chave": chave, "peca": peca_id, "run": run_id, "quando": agora_iso()})
    if publicar_estado(f"claim {chave} -> {peca_id}") is False:
        raise JaReivindicado(chave)
    # depois do rebase, quem ficou com o arquivo é o dono de verdade
    dono = json.loads(arq.read_text(encoding="utf-8"))
    if dono["peca"] != peca_id:
        raise JaReivindicado(f"assunto {chave} já é da peça {dono['peca']}")


def travar(peca_id: str, run_id: str, minutos: int = 90) -> None:
    arq = _p("locks", f"{peca_id}.json")
    if arq.exists():
        t = json.loads(arq.read_text(encoding="utf-8"))
        validade = _dt.datetime.fromisoformat(t["expira"].replace("Z", "+00:00"))
        if t["run"] != run_id and validade > agora():
            raise Travado(f"peça {peca_id} está com o disparo {t['run']} até {t['expira']}")
    expira = (agora() + _dt.timedelta(minutes=minutos)).strftime("%Y-%m-%dT%H:%M:%SZ")
    gravar_json(arq, {"peca": peca_id, "run": run_id, "expira": expira})
    publicar_estado(f"lock {peca_id} ({run_id})")
    if json.loads(arq.read_text(encoding="utf-8"))["run"] != run_id:
        raise Travado(peca_id)


def destravar(peca_id: str, run_id: str) -> None:
    arq = _p("locks", f"{peca_id}.json")
    if arq.exists() and json.loads(arq.read_text(encoding="utf-8"))["run"] == run_id:
        arq.unlink()
        publicar_estado(f"unlock {peca_id}")


def registrar(peca_id: str, tipo: str, **dados) -> dict:
    ev = {"tipo": tipo, "quando": agora_iso(), **dados}
    acrescentar_linha(_p("pecas", peca_id, "eventos.jsonl"), ev)
    gravar_json(_p("pecas", peca_id, "estado.json"), derivar(peca_id))
    return ev


def eventos(peca_id: str) -> list[dict]:
    return ler_linhas(_p("pecas", peca_id, "eventos.jsonl"))


def sufixo_reabertura(peca_id: str) -> str:
    """Identifica a rodada atual dos pedidos de uma peça reaberta."""
    numero = sum(e.get("tipo") == "reaberta" for e in eventos(peca_id))
    return f"r{numero}" if numero else ""


def derivar(peca_id: str) -> dict:
    est = {"id": peca_id, "camadas": {}, "pareceres": [], "aprovacoes": {}, "versao_previa": 0,
           "selo": None, "final": None, "custo_total_usd": 0.0, "provas": {}}
    for ev in eventos(peca_id):
        t = ev["tipo"]
        if t == "criada":
            est.update({k: ev[k] for k in ("slug", "tipo_peca", "premium", "vence_em", "chave", "modo") if k in ev})
            est["criado_em"] = ev["quando"]
        elif t.startswith("camada_"):
            c = est["camadas"].setdefault(ev["camada"], {"status": "pendente", "erros": 0})
            if t == "camada_ok":
                c.update(status="ok", versao=ev.get("versao"), hash_entrada=ev.get("hash_entrada"),
                         hash_saida=ev.get("hash_saida"), arquivo_saida=ev.get("arquivo_saida"), fim=ev["quando"])
            elif t == "camada_erro":
                c["erros"] += 1
                c.update(status="pulada" if c["erros"] > MAX_ERROS else "erro", erro=ev.get("erro"))
            elif t == "camada_inicio":
                c.update(status="rodando", inicio=ev["quando"])
            elif t == "camada_invalidada":
                c.update(status="pendente", invalidada_por=ev.get("motivo"), erros=0)
        elif t == "parecer":
            est["pareceres"].append({k: ev.get(k) for k in ("etapa", "quem", "modelo", "request_id", "status",
                                                             "hash_pacote", "hash_candidato", "material_aberto")})
        elif t == "versao_nova":
            est["versao_previa"] = ev["versao"]
            est["hash_candidato"] = ev.get("hash_candidato")
        elif t == "aprovacao":
            est["aprovacoes"][ev["campo"]] = {"versao": ev["versao"], "hash": ev.get("hash"), "quando": ev["quando"],
                                              "escopo": ev.get("escopo", "peca inteira")}
        elif t == "aprovacao_invalidada":
            est["aprovacoes"].pop(ev["campo"], None)
        elif t == "prova":
            est["provas"][ev["prova"]] = {"ok": bool(ev.get("ok")), "hash_candidato": ev.get("hash_candidato"),
                                          "arquivo": ev.get("arquivo"), "quando": ev["quando"]}
        elif t == "selo":
            est["selo"] = ev.get("selo")
        elif t == "custo":
            est["custo_total_usd"] = round(est["custo_total_usd"] + float(ev.get("usd", 0)), 4)
        elif t == "final":
            est["final"] = ev["estado"]
    estudio = est["camadas"].get("estudio", {})
    v_previa, v_estudio = est["versao_previa"], estudio.get("versao")
    if v_previa and v_estudio is not None and v_estudio != v_previa and estudio.get("status") == "ok":
        est["camadas"]["estudio"] = {"status": "pendente", "erros": 0}
    pend = [c for c in CAMADAS if est["camadas"].get(c, {}).get("status") != "ok"]
    est["camada_atual"] = pend[0] if pend else "fim"
    est["bloqueia_publicacao"] = sorted(c for c in OBRIGATORIAS if est["camadas"].get(c, {}).get("status") == "pulada")
    return est


def precisa_rodar(peca_id: str, camada: str, versao: int, hash_entrada: str) -> bool:
    c = derivar(peca_id)["camadas"].get(camada)
    if not c:
        return True
    if c["status"] == "ok":
        return not (c.get("versao") == versao and c.get("hash_entrada") == hash_entrada)
    return c["status"] != "pulada"


def invalidar_a_partir(peca_id: str, camada: str, motivo: str) -> None:
    """Mudou a entrada de `camada`: ela e tudo que depende dela voltam pra pendente; Sim de versão cai."""
    i = CAMADAS.index(camada)
    for c in CAMADAS[i:]:
        registrar(peca_id, "camada_invalidada", camada=c, motivo=motivo)
    # 25/11 (BB 256 bi): story-first e versao-bonita ficam fora de CAMADAS; um erro antigo delas sobrevivia à
    # reabertura e paradas.py mostrava "erro em story-first" com a peça parada em acao. Elas dependem da produção.
    if i <= CAMADAS.index("producao"):
        cam = derivar(peca_id)["camadas"]
        for c in ("story-first", "versao-bonita"):
            if c in cam and cam[c].get("status") != "pendente":
                registrar(peca_id, "camada_invalidada", camada=c, motivo=motivo)
    for campo in ("previewVersion", "freeFullVideoVersion", "publishVersion"):
        if campo in derivar(peca_id)["aprovacoes"]:
            registrar(peca_id, "aprovacao_invalidada", campo=campo, motivo=motivo)


def abertas() -> list[str]:
    base = _p("pecas")
    if not base.exists():
        return []
    # dia (DIA-*) e testes técnicos (NEWS-TESTE-*) não são peças e não ocupam vaga
    return sorted(d.name for d in base.iterdir() if d.is_dir() and not d.name.startswith(("DIA-", "NEWS-TESTE"))
                  and derivar(d.name)["final"] not in FINAIS)
