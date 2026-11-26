"""Peças comuns do runner da Automação News Brasil (rodada 4).

Regras que valem para todo o runner:
- Nada de segredo em arquivo ou log. Erro de API passa por `sanitizar` antes de ser gravado.
- Estado e orçamento moram numa pasta de dados (ESTADO_DIR), que no GitHub é um checkout do
  branch `automacao-estado`. Gravação = arquivo novo ou linha acrescentada (append-only);
  push com reconciliação (fetch + rebase), nunca force.
- Dia contado no horário de Brasília.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import pathlib
import re
import subprocess
import time
import uuid
from zoneinfo import ZoneInfo

BRT = ZoneInfo("America/Sao_Paulo")
RAIZ_REPO = pathlib.Path(__file__).resolve().parents[3]


def agora() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def agora_iso() -> str:
    return agora().strftime("%Y-%m-%dT%H:%M:%SZ")


def dia_brt(quando: _dt.datetime | None = None) -> str:
    return (quando or agora()).astimezone(BRT).strftime("%Y-%m-%d")


def estado_dir() -> pathlib.Path:
    d = pathlib.Path(os.environ.get("ESTADO_DIR", RAIZ_REPO / "_estado_local"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_texto(t: str) -> str:
    return sha256_bytes(t.encode("utf-8"))


def json_canonico(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def novo_id(prefixo: str) -> str:
    return f"{prefixo}-{agora().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"


_PADROES_SEGREDO = [
    re.compile(r"sk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{8,}"),
    re.compile(r"(?i)(x-api-key|api[_-]?key|authorization)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9._\-]{6,}"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----", re.S),
    re.compile(r"ya29\.[A-Za-z0-9._\-]{10,}"),
    re.compile(r"(?i)(api key provided:)\s*\S+"),
]


def sanitizar(msg: str, limite: int = 300) -> str:
    """Tira qualquer coisa com cara de chave e corta o tamanho. Usar em TODO erro gravado."""
    s = str(msg)
    for p in _PADROES_SEGREDO:
        s = p.sub("[removido]", s)
    for nome, valor in os.environ.items():
        if valor and len(valor) >= 12 and any(k in nome for k in ("KEY", "TOKEN", "SECRET", "COOKIE")):
            s = s.replace(valor, "[removido]")
    return s[:limite]


def acrescentar_linha(caminho: pathlib.Path, obj: dict) -> None:
    """Histórico só de acréscimo: uma linha JSON por evento."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(json_canonico(obj) + "\n")


def ler_linhas(caminho: pathlib.Path) -> list[dict]:
    if not caminho.exists():
        return []
    out = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha:
            out.append(json.loads(linha))
    return out


def gravar_json(caminho: pathlib.Path, obj) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(caminho)


# ---------- git do branch de estado (só roda quando ESTADO_GIT=1, ou seja, no GitHub) ----------

def _git(*args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd or estado_dir(), capture_output=True, text=True)


def garantir_union(d: pathlib.Path) -> None:
    """Arquivos .jsonl só recebem linha no fim: com merge=union o rebase junta as linhas de dois jobs em vez de
    falhar (run 44973092563, 22/11: preflight e conselho anotaram no orçamento ao mesmo tempo)."""
    ga = d / ".gitattributes"
    atual = ga.read_text(encoding="utf-8") if ga.exists() else ""
    if "*.jsonl merge=union" not in atual:
        ga.write_text(atual + ("" if not atual or atual.endswith("\n") else "\n") + "*.jsonl merge=union\n", encoding="utf-8")


# Arquivos de ideias/ que são dicionários por peça (ou por linha da planilha) e se recalculam a cada status.
# Conflito neles não é edição de verdade: junta as chaves dos dois lados (run 45118434948, 23/11: a sessão
# gravou status enquanto o job de produção da Semana e do PL rodava; o job caiu sem registrar tentativa).
DERIVADOS_JSON = {"ideias/revisao.json", "ideias/entregas-pendentes.json", "ideias/_status_escrito.json",
                  "ideias/links.json"}


def _juntar_dict(base: dict, meu: dict) -> dict:
    out = dict(base)
    for k, v in meu.items():
        out[k] = {**out[k], **v} if isinstance(out.get(k), dict) and isinstance(v, dict) else v
    return out


def _em_rebase(d: pathlib.Path) -> bool:
    g = d / ".git"
    return (g / "rebase-merge").exists() or (g / "rebase-apply").exists()


def _resolver_derivados(d: pathlib.Path) -> bool:
    """Reconcilia dicionários derivados e recalcula o estado das peças com os eventos unidos pelo Git."""
    for _ in range(50):
        if not _em_rebase(d):
            return True
        conflitos = [x for x in _git("diff", "--name-only", "--diff-filter=U", cwd=d).stdout.split() if x]
        if not conflitos and _git("diff", "--cached", "--quiet", cwd=d).returncode == 0:
            _git("rebase", "--skip", cwd=d)
            continue
        fotos = {c: m[1] for c in conflitos if (m := re.fullmatch(r"pecas/(NEWS-[A-Z0-9-]+)/estado\.json", c))}
        if any(c not in DERIVADOS_JSON and c not in fotos for c in conflitos):
            return False
        for c in conflitos:
            if c in fotos:
                from estado import derivar

                pid = fotos[c]
                if not (d / "pecas" / pid / "eventos.jsonl").is_file():
                    return False
                gravar_json(d / c, derivar(pid))
                _git("add", c, cwd=d)
                continue
            try:  # no rebase, :2 é o lado já publicado (upstream) e :3 é o commit deste job
                base = json.loads(_git("show", f":2:{c}", cwd=d).stdout or "{}")
                meu = json.loads(_git("show", f":3:{c}", cwd=d).stdout or "{}")
            except json.JSONDecodeError:
                return False
            if not isinstance(base, dict) or not isinstance(meu, dict):
                return False
            gravar_json(d / c, _juntar_dict(base, meu))
            _git("add", c, cwd=d)
        _git("-c", "core.editor=true", "rebase", "--continue", cwd=d)
    return False


def publicar_estado(mensagem: str, tentativas: int = 6, depois_do_rebase=None) -> bool:
    """Commit + push do branch de estado com reconciliação. Nunca usa force.

    `depois_do_rebase` é chamado depois de cada rebase pra revalidar regras que dependem do
    conteúdo dos outros (ex.: orçamento). Se ele devolver False, a mudança local é desfeita.
    """
    if os.environ.get("ESTADO_GIT") != "1":
        return True
    # mesma trava dos subagentes da sessão (flock /tmp/git.lock): checkout dividido quebrava push (25/11)
    import fcntl
    with open(os.environ.get("GIT_LOCK", "/tmp/git.lock"), "a") as trava:
        fcntl.flock(trava, fcntl.LOCK_EX)
        return _publicar_estado(mensagem, tentativas, depois_do_rebase)


def _publicar_estado(mensagem: str, tentativas: int = 6, depois_do_rebase=None) -> bool:
    d = estado_dir()
    garantir_union(d)
    esparso = _git("config", "--bool", "--get", "core.sparseCheckout", cwd=d).stdout.strip() == "true"
    # O checkout esparso deixa os renderizados novos fora do índice com git add -A.
    args = ("--sparse", "-A") if esparso else ("-A",)
    adicionados = _git("add", *args, cwd=d)
    if adicionados.returncode != 0:
        raise RuntimeError(f"não consegui preparar o commit de estado: {sanitizar(adicionados.stderr)}")
    if _git("diff", "--cached", "--quiet", cwd=d).returncode == 0:
        return True
    _git("commit", "-m", mensagem, cwd=d)
    for t in range(tentativas):
        if _git("push", "origin", "HEAD:automacao-estado", cwd=d).returncode == 0:
            return True
        _git("fetch", "origin", "automacao-estado", cwd=d)
        if _git("rebase", "origin/automacao-estado", cwd=d).returncode != 0 and not _resolver_derivados(d):
            conflitos = _git("diff", "--name-only", "--diff-filter=U", cwd=d).stdout.splitlines()
            _git("rebase", "--abort", cwd=d)
            detalhe = ", ".join(conflitos) or "sem caminhos em conflito no índice"
            raise RuntimeError(f"conflito no branch de estado: {detalhe}")
        if depois_do_rebase and depois_do_rebase() is False:
            _git("reset", "--hard", "origin/automacao-estado", cwd=d)
            return False
        time.sleep(2 * (t + 1))
    raise RuntimeError("não consegui publicar o estado depois de várias tentativas")
