#!/usr/bin/env python3
"""Gate de overflow de card. Roda ANTES de publicar qualquer pagina de carrossel.
Uso: python3 card_overflow_gate.py <arquivo.html> [--pad-side 7.5] [--pad-top 7.5] [--pad-bot 6.5]
Sai com codigo 1 se algum card estoura a caixa ou passa de 35 palavras.
Regra da casa: NUNCA diminuir a fonte para caber. Corta copy ou abre outro card."""
import re, sys, html, argparse
W, H = 1080.0, 1350.0
SIZES = [('hd',8.5,1.06),('hl',9.5,1.03),('bd',4.6,1.36),('sub',4.5,1.34),
         ('jg',3.1,1.35),('cnote',2.7,1.32),('note',2.3,1.3),('eb',2.2,1.3),
         ('kick',2.2,1.3),('bar',2.2,1.3),('ft',2.1,1.4),('foot',2.0,1.4)]
def strip(t): return html.unescape(re.sub(r'<[^>]+>', ' ', t))
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file'); ap.add_argument('--pad-side', type=float, default=7.5)
    ap.add_argument('--pad-top', type=float, default=7.5); ap.add_argument('--pad-bot', type=float, default=6.5)
    a = ap.parse_args()
    s = open(a.file, encoding='utf-8').read()
    cards = re.findall(r'<div class="pad">(.*?)</div>\s*</div>', s, re.S)
    inner_w = W - 2*(a.pad_side/100*W)
    avail_h = H - (a.pad_top/100*W) - (a.pad_bot/100*W)
    bad = 0
    print(f"caixa util {inner_w:.0f}x{avail_h:.0f}px · {len(cards)} cards")
    for i, c in enumerate(cards, 1):
        h = 0.0; words = 0
        for cls, cqw, lh in SIZES:
            for m in re.findall(r'class="[^"]*\b%s\b[^"]*"[^>]*>(.*?)(?=<div|<h4|<p class|</div>)' % cls, c, re.S):
                txt = strip(m).strip()
                if not txt: continue
                words += len(txt.split())
                px = cqw/100*W
                cpl = max(1, int(inner_w/(px*0.5)))
                h += max(1, -(-len(txt)//cpl))*px*lh + px*0.45
        pct = 100*h/avail_h
        if pct > 100 or words > 35:
            bad += 1
            print(f"  ✗ card {i:2d}: {pct:5.1f}% da altura · {words} palavras")
    if bad:
        print(f"\nFALHOU: {bad} card(s). Corte copy ou abra outro card. NAO diminua a fonte.")
        sys.exit(1)
    print("\nPASSOU: nenhum card estoura e nenhum passa de 35 palavras.")
main()
