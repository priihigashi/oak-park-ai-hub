"""Visual-first adapter of registered OPC Tip templates; deterministic PNGs.

Font bytes stay in the transient browser input. Delivered review HTML contains
rendered cards and evidence, not font files or a text-to-image layout.
"""
from __future__ import annotations

import base64
import html
import json
import os
from pathlib import Path
import re

from opc_contract import GateError, digest_file, safe_relative

REPO = Path(__file__).resolve().parents[2]
THEMES = {'dark':'v1','cream':'v2','lime':'v3'}
OVERRIDES = '''
body{display:block;padding:0;margin:0;background:#191919}
.slide{margin:0;padding:108px;position:relative}
.corner.tl{top:40px;left:40px}.corner.tr{top:40px;right:40px}
.corner.bl{bottom:40px;left:40px}.corner.br{bottom:40px;right:40px}
.slide .tag{position:absolute;top:108px;left:108px;right:108px;height:26px;margin:0;font-size:20px;letter-spacing:.12em}
.slide .headline{position:absolute;top:177px;left:108px;right:108px;height:208px;margin:0;font-size:94px;line-height:1.04;max-width:none}
.slide .context-img-slot{position:absolute;top:423px;left:108px;width:864px;height:596px;min-height:596px;max-height:596px;margin:0;border-radius:0;border-width:1px}
.slide .context-img-slot img{height:100%;filter:none;object-fit:cover}
.slide .body-text{position:absolute;top:1074px;left:108px;right:108px;height:122px;margin:0;max-width:none;font-size:36px;line-height:1.13;padding:0}
.slide .source-mini{position:absolute;top:1035px;left:108px;right:108px;height:25px;font-family:'Roboto Condensed',sans-serif;font-size:20px;line-height:1.1;color:var(--c-body)}
.slide .slide-logo{bottom:106px;left:108px;font-family:'Roboto Condensed',sans-serif;font-size:18px;letter-spacing:.02em;line-height:1.1;max-width:600px;padding:0;background:none}
.slide .arrow{bottom:103px;right:108px;font-size:24px;background:none;padding:0;line-height:1}
.slide.v2{--c-body:#24231E;--c-tag:#635D51;--c-head:#0A0A0A;background:#F0EBE3}
.slide.v2 .headline{color:#0A0A0A}.slide.v2 .tag{color:#635D51}
.slide .image-note{position:absolute;top:983px;right:120px;background:rgba(10,10,10,.8);color:#F0EBE3;padding:5px 9px;font:18px 'Roboto Condensed',sans-serif}
'''


def data_uri(path: Path, mime: str) -> str:
    return f'data:{mime};base64,'+base64.b64encode(path.read_bytes()).decode()


def template_css() -> str:
    text = (REPO/'docs/templates/opc_tip.html').read_text(encoding='utf-8')
    match = re.search(r'<style>(.*?)</style>',text,re.S)
    if not match:
        raise GateError('Registered OPC Tip template stylesheet missing')
    fonts = REPO/'scripts/content_creator/fonts'
    css = match[1]
    for name, filename in [('Anton','Anton-Regular.woff2'),('Roboto Condensed','RobotoCondensed-Regular.woff2')]:
        p=fonts/filename
        if not p.is_file():
            raise GateError('Required OPC local font is unavailable; no unapproved font substitution')
        css += f'\n@font-face{{font-family:"{name}";src:url({data_uri(p,"font/woff2")});font-weight:100 900;font-display:block}}'
    return css+OVERRIDES


def card_html(card: dict, spec: dict, root: Path, theme: str) -> str:
    esc=html.escape
    asset=next(a for a in spec['assets'] if a['key']==card['visual_key'])
    image=data_uri(safe_relative(root,asset['path']),'image/jpeg')
    sources={s['id']:s for s in spec['sources']}
    names=' · '.join(sources[s]['name'] for s in card.get('source_ids',[]))
    if len(names)>85:
        names=' · '.join(card.get('source_ids',[]))+' · Sources in review pack'
    note='<div class="image-note">AI illustration</div>' if asset['kind']=='ai_illustration' else ''
    last=card['id']==len(spec['slides'])
    label='SAVE FOR YOUR REMODEL' if last else 'MATERIAL NOTES' if spec['kind']=='education' else 'PROJECT NOTES'
    return (f'<section class="slide {THEMES[theme]}" data-card="{card["id"]}">'
        '<div class="corner tl"></div><div class="corner tr"></div><div class="corner bl"></div><div class="corner br"></div>'
        f'<div class="tag" data-fit>{label} / {card["id"]:02d}</div>'
        f'<div class="headline" data-fit>{esc(card["headline"])}</div>'
        f'<div class="context-img-slot"><img alt="{esc(card.get("visual_description","Material illustration"))}" src="{image}"></div>{note}'
        f'<div class="source-mini" data-fit>{esc(names)}</div><div class="body-text" data-fit>{esc(card["body"])}</div>'
        f'<div class="slide-logo">{"@oakparkconstruction · LIC " if last else "OAK PARK CONSTRUCTION · "}CBC1263425</div>'
        f'<div class="arrow">{"SAVE" if last else "SWIPE →"}</div></section>')


def check_browser(page, expected: int) -> list[dict]:
    page.evaluate('document.fonts.ready')
    missing=page.evaluate('''()=>[...document.images].filter(i=>!i.complete||i.naturalWidth<300).length''')
    if missing:
        raise GateError('Browser found missing/invalid image resources')
    checks=page.evaluate('''()=>[...document.querySelectorAll('.slide')].map(s=>({
      id:Number(s.dataset.card),width:s.clientWidth,height:s.clientHeight,
      overflows:[...s.querySelectorAll('[data-fit]')].filter(e=>e.scrollHeight>e.clientHeight+2||e.scrollWidth>e.clientWidth+2).map(e=>e.className)
    }))''')
    if len(checks)!=expected or any(c['width']!=1080 or c['height']!=1350 or c['overflows'] for c in checks):
        raise GateError('Browser geometry/text overflow gate failed: '+json.dumps(checks))
    return checks


def export(spec: dict, root: Path) -> dict:
    from playwright.sync_api import sync_playwright
    css=template_css()
    report={'template':'docs/templates/opc_tip.html','adapter':'opc_print_visual','variants':{}}
    launch={'headless':True}
    if os.getenv('OPC_CHROMIUM_EXECUTABLE'):
        launch['executable_path']=os.environ['OPC_CHROMIUM_EXECUTABLE']
    with sync_playwright() as pw:
        browser=pw.chromium.launch(**launch)
        try:
            for theme in THEMES:
                page=browser.new_page(viewport={'width':1080,'height':1350},device_scale_factor=1)
                content=''.join(card_html(c,spec,root,theme) for c in spec['slides'])
                page.set_content('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                    '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=block" rel="stylesheet">'
                    f'<style>{css}</style></head><body>{content}</body></html>',wait_until='networkidle')
                page.evaluate('document.fonts.ready')
                page.evaluate("""()=>document.querySelectorAll('.headline').forEach(e=>{
                  for(const size of [94,86,78]){e.style.fontSize=size+'px';if(e.scrollHeight<=e.clientHeight+2)break;}
                })""")
                metrics=check_browser(page,len(spec['slides']))
                loaded=page.evaluate('''()=>[...document.fonts].filter(f=>['Anton','Roboto Condensed','JetBrains Mono'].includes(f.family.replaceAll('"',''))).map(f=>({family:f.family,status:f.status}))''')
                families={f['family'].strip('"') for f in loaded if f['status']=='loaded'}
                if not {'Anton','Roboto Condensed','JetBrains Mono'}.issubset(families):
                    raise GateError('A required OPC font did not load in the renderer')
                folder=root/'png'/theme;folder.mkdir(parents=True,exist_ok=True)
                for i,element in enumerate(page.locator('.slide').all(),1):
                    target=folder/f'card_{i:02d}.png';element.screenshot(path=str(target))
                    if target.stat().st_size<15000:
                        raise GateError('Suspiciously empty rendered card')
                    metrics[i-1]['sha256']=digest_file(target)
                report['variants'][theme]={'cards':metrics,'fonts':loaded}
                page.close()
        finally:
            browser.close()
    (root/'resources/browser-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


REVIEW_CSS='''
*{box-sizing:border-box}body{margin:0;background:#101010;color:#f0ebe3;font:16px/1.5 Arial,sans-serif}
main{max-width:1120px;margin:auto;padding:24px}h1{font-size:clamp(26px,5vw,44px);line-height:1.1;margin:10px 0}
a{color:#d5d650;overflow-wrap:anywhere}video{display:block;width:100%;max-height:460px;background:#000;margin:16px 0}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}button{font:inherit;padding:10px 16px;background:#242424;color:#fff;border:1px solid #666;cursor:pointer;border-radius:6px}
button.active,button[aria-pressed=true]{background:#cbcc10;color:#0a0a0a;border-color:#cbcc10}
.deck{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.card img{width:100%;height:auto;display:block}.choices{display:flex;gap:8px;padding:10px 0}
[hidden]{display:none!important}.status{color:#cbcc10;font-weight:bold}details{margin-top:28px;padding:18px;background:#202020}summary{cursor:pointer;font-weight:bold}
.proof img{width:100%;max-width:650px;display:block}.proof{margin:18px 0}.caption{white-space:pre-wrap;padding:16px;background:#202020}
textarea{width:100%;min-height:60px;background:#191919;color:#fff;border:1px solid #555;padding:10px;font:inherit}
@media(max-width:680px){main{padding:14px}.deck{grid-template-columns:1fr}button{padding:10px 12px}}
'''
REVIEW_JS='''
const feedback={version:1,approved:false,cards:{},variant:'dark'};
document.querySelectorAll('[data-theme]').forEach(b=>b.addEventListener('click',()=>{
 feedback.variant=b.dataset.theme;
 document.querySelectorAll('[data-deck]').forEach(d=>d.hidden=d.dataset.deck!==feedback.variant);
 document.querySelectorAll('[data-theme]').forEach(x=>x.classList.toggle('active',x===b));
}));
document.querySelectorAll('[data-choice]').forEach(b=>b.addEventListener('click',()=>{
 const id=b.dataset.card;feedback.cards[id]={choice:b.dataset.choice,note:document.querySelector(`[data-note="${id}"]`).value};
 b.parentNode.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
}));
document.getElementById('export-feedback').addEventListener('click',()=>{
 document.querySelectorAll('[data-note]').forEach(t=>{const v=feedback.cards[t.dataset.note];if(v)v.note=t.value;});
 const blob=new Blob([JSON.stringify(feedback,null,2)],{type:'application/json'});
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='opc-review-feedback.json';a.click();URL.revokeObjectURL(a.href);
});
'''


def review(spec: dict, root: Path) -> Path:
    esc=html.escape
    video=spec.get('video')
    player=''
    if video:
        player=f'<video controls autoplay muted playsinline preload="metadata" src="{data_uri(safe_relative(root,video["file"]),"video/mp4")}"></video>'
    parts=[f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{esc(spec["title"])} — OPC review</title><style>{REVIEW_CSS}</style><main>'
           f'<p class="status">READY FOR PRISCILA REVIEW · NOT APPROVED · NOT PUBLISHED</p><h1>{esc(spec["title"])}</h1>'
           f'{player}<p>Source video is a private research reference, not the public OPC cover.</p>'
           '<nav>'+''.join(f'<button data-theme="{t}" class="{"active" if t=="dark" else ""}">{t.title()}</button>' for t in THEMES)+'</nav>']
    for theme in THEMES:
        parts.append(f'<section class="deck" data-deck="{theme}" {"" if theme=="dark" else "hidden"}>')
        for c in spec['slides']:
            key=f'{theme}-{c["id"]}';png=root/'png'/theme/f'card_{c["id"]:02d}.png'
            parts.append(f'<article class="card"><img alt="{esc(c["headline"])}" src="{data_uri(png,"image/png")}">'
                f'<div class="choices"><button data-card="{key}" data-choice="keep">Keep</button><button data-card="{key}" data-choice="redo">Redo</button></div>'
                f'<textarea data-note="{key}" placeholder="What should change?"></textarea></article>')
        parts.append('</section>')
    parts.append('<h2>Caption</h2><div class="caption">'+esc(spec['caption']+'\n\n'+spec.get('hashtags',''))+'</div>'
                 '<p>Feedback stays in this page until exported. Keep is not publication approval.</p><button id="export-feedback">Export review feedback</button>'
                 '<details><summary>PRINT evidence pack — full sources and screenshots</summary>')
    for source in spec['sources']:
        parts.append(f'<article class="proof"><h3>{esc(source["name"])}</h3><p>{esc(source.get("heading",""))}</p>'
                     f'<a href="{esc(source["url"],quote=True)}" target="_blank" rel="noopener noreferrer">{esc(source["url"])}</a>'
                     f'<img alt="Actual source screenshot" src="{data_uri(safe_relative(root,source["screenshot"]),"image/png")}"></article>')
    parts.append('</details></main><script>'+REVIEW_JS+'</script></html>')
    path=root/'review.html';path.write_text(''.join(parts),encoding='utf-8');return path
