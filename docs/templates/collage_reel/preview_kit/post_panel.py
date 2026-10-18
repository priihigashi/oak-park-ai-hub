"""Painel de postagem para TODA prévia de reel: botões de download (vídeo, áudio, roteiro) + campos
com botão Copiar para a legenda do post e o primeiro comentário.
Uso (dentro de um mkpreview_*.py):  page = add_panel(page, OUT, '<pasta data/slug>')
Lê <pasta>/post/legenda.txt, primeiro_comentario.txt e roteiro.txt; copia para OUT. O MP4 aparece quando OUT/video.mp4 existir."""
import html, os, shutil

CSS = """<style>
.pp{max-width:430px;margin:18px auto 40px;font-family:system-ui,-apple-system,sans-serif;color:#F2ECE0}
.pp h2{font-size:15px;letter-spacing:.08em;text-transform:uppercase;color:#FFD34D;margin:22px 0 8px}
.pp .dl{display:flex;flex-wrap:wrap;gap:8px}
.pp .dl a,.pp .dl span{flex:1 1 30%;text-align:center;padding:12px 8px;border-radius:12px;background:#1c1d21;border:1px solid #33343a;color:#F2ECE0;text-decoration:none;font-weight:700;font-size:14px}
.pp .dl a:active{background:#FFD34D;color:#111}
.pp .dl span{opacity:.45}
.pp textarea{width:100%;box-sizing:border-box;min-height:150px;background:#111215;color:#F2ECE0;border:1px solid #33343a;border-radius:12px;padding:12px;font:14px/1.45 system-ui,sans-serif;resize:vertical}
.pp button.cp{margin-top:6px;width:100%;padding:12px;border:0;border-radius:12px;background:#FFD34D;color:#111;font-weight:800;font-size:15px}
</style>"""

def _rd(p):
    try: return open(p, encoding='utf-8').read().strip()
    except Exception: return ''

def add_panel(page, OUT, D):
    P = os.path.join(D, 'post')
    for f in ('roteiro.txt',):
        if os.path.exists(os.path.join(P, f)): shutil.copy(os.path.join(P, f), os.path.join(OUT, f))
    vid = os.path.exists(os.path.join(OUT, 'video.mp4'))
    dl = (('<a href="video.mp4" download="reel.mp4">⬇ Vídeo MP4</a>' if vid else '<span>MP4 sai após aprovação</span>')
          + '<a href="narracao.mp3" download>⬇ Áudio</a>'
          + ('<a href="roteiro.txt" download>⬇ Roteiro</a>' if os.path.exists(os.path.join(OUT, 'roteiro.txt')) else ''))
    box = lambda i, t, v: (f'<h2>{t}</h2><textarea id="{i}" readonly>{html.escape(v)}</textarea>'
                           f'<button class="cp" onclick="ppCopy(\'{i}\',this)">Copiar</button>')
    panel = (CSS + '<div class="pp"><h2>Baixar</h2><div class="dl">' + dl + '</div>'
             + box('ppLeg', 'Legenda do post', _rd(os.path.join(P, 'legenda.txt')))
             + box('ppCom', 'Primeiro comentário', _rd(os.path.join(P, 'primeiro_comentario.txt')))
             + '</div><script>function ppCopy(id,b){const t=document.getElementById(id);'
             'const done=()=>{const o=b.textContent;b.textContent="Copiado ✓";setTimeout(()=>b.textContent=o,1500)};'
             'try{navigator.clipboard.writeText(t.value).then(done,()=>{t.select();document.execCommand("copy");done()})}'
             'catch(e){t.select();document.execCommand("copy");done()}}</script>')
    return page.replace('</body>', panel + '</body>') if '</body>' in page else page + panel
