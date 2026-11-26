"""Confere o ritmo de cor dos cards (regras/ritmo-de-cor.md). Entrada: lista de cores de fundo na ordem
(ex.: tirada da tira de contato) e, opcional, o capítulo de cada card. Saída: lista de problemas."""
from __future__ import annotations


def familia(cor: str) -> str:
    c = cor.strip().lower().lstrip("#")
    if len(c) != 6:
        return c
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    if max(r, g, b) < 60:
        return "preto"
    if min(r, g, b) > 200:
        return "claro"
    if r > 200 and g > 170 and b < 140:
        return "amarelo"
    if r > 180 and g < 130:
        return "vermelho-laranja"
    if g > r and g > b:
        return "verde"
    if b > r and b > g:
        return "azul"
    return "outra"


def conferir(cores: list[str], capitulos: list[str] | None = None, max_seguidos: int = 3) -> list[str]:
    fams = [familia(c) for c in cores]
    probs = []
    i = 0
    while i < len(fams):
        j = i
        while j + 1 < len(fams) and fams[j + 1] == fams[i]:
            j += 1
        if j - i + 1 > max_seguidos:
            probs.append(f"cards {i+1} a {j+1}: {j-i+1} seguidos em {fams[i]} (máx. {max_seguidos})")
        i = j + 1
    for k, f in enumerate(fams):
        if fams.count(f) == 1 and 0 < k < len(fams) - 1:
            probs.append(f"card {k+1}: cor solta ({f}) aparece uma vez só no meio")
    if capitulos:
        for k in range(1, len(fams)):
            if capitulos[k] == capitulos[k - 1] and fams[k] != fams[k - 1] and fams[k] != "preto" and fams[k - 1] != "preto":
                probs.append(f"card {k+1}: trocou de cor sem trocar de capítulo")
    return probs
