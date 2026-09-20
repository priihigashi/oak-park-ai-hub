"""Render a fact-check deck.html from cards.json (see run.py). Also exports one PNG per card.

cards.json = {title, hook{pt,en}, video_url, meta{...}, sources[{name,date,url,title}], caption{pt,en},
              method{pt,en}, video{file,poster}|null, shots{key:relative jpg}, cards:[...]}
"""
import base64, json, pathlib, re, sys

HERE = pathlib.Path(__file__).parent


def _b64(p):
    return "data:image/jpeg;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def render(spec: dict, workdir: pathlib.Path) -> pathlib.Path:
    tpl = (HERE / "deck_template.html").read_text(encoding="utf-8")
    shots = {k: _b64(workdir / v) for k, v in (spec.get("shots") or {}).items() if (workdir / v).exists()}
    deck = {"shots": shots, "video": spec.get("video"), "cards": spec["cards"]}
    esc = lambda s: (s or "").replace("&", "&amp;").replace("<", "&lt;")
    meta = spec.get("meta", {})
    head = (f'<div class="prov"><span>Pipeline: <b>transcribe-comment-create-print</b></span>'
            f'<span>{esc(meta.get("date", ""))}</span><span>{esc(meta.get("run", ""))}</span></div>\n'
            f'  <h1>{esc(spec["title"])}</h1>\n'
            f'  <p class="sub" data-lang="pt">{esc(spec["hook"]["pt"])}</p><p class="sub" data-lang="en" hidden>{esc(spec["hook"]["en"])}</p>\n'
            f'  <span class="pill" data-lang="pt">Aguardando aprovação</span><span class="pill" data-lang="en" hidden>Pending approval</span>\n'
            f'  <div class="src"><h3 data-lang="pt">Vídeo original e fontes</h3><h3 data-lang="en" hidden>Original video and sources</h3><ul>\n'
            f'   <li><span class="lbl">Vídeo checado</span><a href="{spec["video_url"]}" target="_blank" rel="noopener">{esc(spec["video_url"])}</a></li>\n' +
            "".join(f'   <li><span class="lbl">{esc(s["name"])}, {esc(s.get("date", ""))}</span>'
                    f'<a href="{s["url"]}" target="_blank" rel="noopener">{esc(s.get("title") or s["url"])}</a></li>\n' for s in spec.get("sources", [])) +
            '  </ul></div>')
    cap = spec.get("caption", {})
    tail = ('<h2 class="sec" data-lang="pt">Legenda, pronta para postar</h2><h2 class="sec" data-lang="en" hidden>Caption, ready to post</h2>\n'
            f'<div class="cap-box" data-lang="pt">{esc(cap.get("pt", ""))}</div><div class="cap-box" data-lang="en" hidden>{esc(cap.get("en", ""))}</div>\n')
    m = spec.get("method", {})
    if m:
        tail += (f'<details><summary data-lang="pt">Como checamos</summary><summary data-lang="en" hidden>How we checked</summary>'
                 f'<div class="in" data-lang="pt">{m.get("pt", "")}</div><div class="in" data-lang="en" hidden>{m.get("en", "")}</div></details>')
    html = (tpl.replace("__TITLE__", esc(spec["title"])).replace("__HEAD__", head).replace("__TAIL__", tail)
            .replace("__CARDS_JS__", (HERE / "cards_runtime.js").read_text(encoding="utf-8"))
            .replace("__DECK_JSON__", json.dumps(deck, ensure_ascii=False).replace("</", "<\\/")))
    out = workdir / "deck.html"
    out.write_text(html, encoding="utf-8")
    return out


def export_pngs(deck_html: pathlib.Path, outdir: pathlib.Path, lang: str = "pt") -> list:
    from playwright.sync_api import sync_playwright
    outdir.mkdir(parents=True, exist_ok=True)
    files = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        pg.goto(deck_html.resolve().as_uri() + f"#{lang}")
        pg.wait_for_timeout(1500)
        pg.add_style_tag(content=".lang{display:none!important}.deck{grid-template-columns:1fr!important}.slide{width:1080px!important;box-shadow:none!important}")
        pg.wait_for_timeout(500)
        for i, el in enumerate(pg.query_selector_all(".slide"), 1):
            p = outdir / f"card_{i:02d}.png"
            el.screenshot(path=str(p))
            files.append(p)
        b.close()
    return files


if __name__ == "__main__":
    wd = pathlib.Path(sys.argv[1])
    spec = json.loads((wd / "cards.json").read_text(encoding="utf-8"))
    print(render(spec, wd))
