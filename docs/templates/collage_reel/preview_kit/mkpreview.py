import re,os,shutil,subprocess
SRC='/home/claude/hub/docs/templates/collage_reel'; OUT='/home/claude/work/preview'
h=open(f'{SRC}/qamiga.html').read()
style=re.search(r'<style>(.*?)</style>',h,re.S).group(1)
style=style.replace('html,body{width:1080px;height:1920px;overflow:hidden;background:#050608}','')
stage=re.search(r'(<div id="stage">.*?</div></div>)\s*<script>',h,re.S).group(1)
dur=re.search(r'window.DUR=([\d.]+)',h).group(1)
# assets
os.makedirs(f'{OUT}/assets/qa',exist_ok=True)
refs=set(re.findall(r'assets/[\w/.-]+',h+open(f'{SRC}/fx.css').read()))
for r in refs:
    s=f'{SRC}/{r}'; d=f'{OUT}/{r}'
    if not os.path.exists(s): continue
    if r.endswith('.jpg'):
        if not os.path.exists(d): subprocess.run(['ffmpeg','-v','error','-y','-i',s,'-vf','scale=1080:-2','-q:v','5',d])
    else: shutil.copy(s,d)
for f in ['fx.js','fx2.js','fx.css','layout.js']: shutil.copy(f'{SRC}/{f}',f'{OUT}/{f}')
e=open(f'{SRC}/engine.js').read()
e=e.replace("if(!navigator.webdriver){let t0=performance.now();(function loop(){render(((performance.now()-t0)/1000)%DUR);requestAnimationFrame(loop)})()}",
"(function loop(){const a=document.getElementById('vo');let T=a?a.currentTime:0;render(Math.min(T,DUR-0.01));if(window.__tick)__tick(T);requestAnimationFrame(loop)})();")
open(f'{OUT}/engine.js','w').write(e)
shutil.copy('/home/claude/work/preview_audio.mp3',f'{OUT}/narracao.mp3')
page=f'''<title>Querida Amiga · Prévia</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="fx.css">
<style>
{style}
:root{{--bg:#0b0c0e;--fg:#f2ece0;--muted:#9a978f;--accent:#FFD34D;--line:#2a2b2e;color-scheme:dark}}
html,body{{height:100%}}
body{{background:var(--bg);color:var(--fg);font-family:system-ui,sans-serif;margin:0;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:12px;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;gap:10px}}
.pv-head{{width:100%;max-width:520px;display:flex;justify-content:space-between;align-items:baseline;gap:12px}}
.pv-head h1{{font:700 16px/1.2 system-ui;margin:0}} .pv-head small{{color:var(--muted);font:12px ui-monospace,monospace}}
.pv-frame{{position:relative;overflow:hidden;border-radius:14px;border:1px solid var(--line);flex:0 0 auto}}
#scaler{{position:absolute;left:0;top:0;width:1080px;height:1920px;transform-origin:0 0}}
.pv-bar{{width:100%;max-width:520px;display:flex;gap:10px;align-items:center}}
.pv-bar button{{background:var(--accent);color:#111;border:0;border-radius:999px;font:700 14px system-ui;padding:10px 18px;cursor:pointer;min-width:92px}}
.pv-bar button:focus-visible{{outline:2px solid var(--fg);outline-offset:2px}}
.pv-bar input{{flex:1;min-width:0;accent-color:#FFD34D}}
.pv-bar output{{font:12px ui-monospace,monospace;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}}
.pv-bar .sp{{min-width:0;padding:8px 12px;background:transparent;color:var(--fg);border:1px solid var(--line)}}.pv-bar .sp.on{{background:var(--accent);color:#111;border-color:var(--accent)}}.pv-sp-l{{font:12px ui-monospace,monospace;color:var(--muted)}}
.pv-skip{{justify-content:space-between}}.pv-bar .sk{{flex:1;min-width:0;padding:10px 6px;background:transparent;color:var(--fg);border:1px solid var(--line);font-variant-numeric:tabular-nums}}
.pv-note{{max-width:520px;color:var(--muted);font-size:12px;line-height:1.4;margin:0}}
</style>
<div class="pv-head"><h1>Querida amiga · prévia</h1><small id="ver">versão em edição</small></div>
<div class="pv-frame" id="frame"><div id="scaler">{stage}</div></div>
<div class="pv-bar"><button id="play" type="button">▶ Play</button><input id="seek" type="range" min="0" max="{dur}" step="0.05" value="0" aria-label="Posição"><output id="tm">0:00</output></div>
<div class="pv-bar pv-skip" role="group" aria-label="Pular"><button type="button" class="sk" data-d="-10">↺ 10s</button><button type="button" class="sk" data-d="-5">↺ 5s</button><button type="button" class="sk" data-d="5">5s ↻</button><button type="button" class="sk" data-d="10">10s ↻</button></div>
<div class="pv-bar" role="group" aria-label="Velocidade"><span class="pv-sp-l">Velocidade</span><button type="button" class="sp on" data-r="1">1x</button><button type="button" class="sp" data-r="1.2">1,2x</button><button type="button" class="sp" data-r="1.5">1,5x</button><button type="button" class="sp" data-r="2">2x</button><button type="button" class="sp" data-r="3">3x</button></div>
<p class="pv-note">Prévia ao vivo do reel (as animações rodam no navegador; o MP4 final sai do mesmo arquivo). Setas ← → pulam 5s (Shift: 10s), espaço dá play/pausa. Recarregue para ver a última edição.</p>
<audio id="vo" src="narracao.mp3?v={int(__import__("time").time())}" preload="auto" playsinline></audio>
<script>window.DUR={dur};</script><script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script><script src="layout.js"></script>
<script>
const fr=document.getElementById('frame'),st=document.getElementById('scaler'),a=document.getElementById('vo'),b=document.getElementById('play'),sk=document.getElementById('seek'),tm=document.getElementById('tm');
function fit(){{const H=Math.min(innerHeight-130,1920),W=Math.min(document.body.clientWidth-32,520);let s=Math.min(H/1920,W/1080);fr.style.width=1080*s+'px';fr.style.height=1920*s+'px';st.style.transform='scale('+s+')'}}
addEventListener('resize',fit);fit();
a.onplay=()=>{{b.textContent='❚❚ Pausa'}};a.onpause=()=>{{b.textContent='▶ Play'}};
b.onclick=()=>{{if(a.paused){{const go=()=>a.play().catch(()=>{{b.textContent='carregando…';a.load();a.addEventListener('canplay',()=>a.play().catch(()=>{{b.textContent='▶ Play'}}),{{once:true}})}});if(a.ended||a.currentTime>=a.duration-.05)a.currentTime=0;go()}}else a.pause()}};
document.querySelectorAll('.sp').forEach(x=>x.onclick=()=>{{a.playbackRate=+x.dataset.r;a.preservesPitch=true;document.querySelectorAll('.sp').forEach(y=>y.classList.toggle('on',y===x))}});
a.onended=()=>{{b.textContent='▶ Play'}};
sk.oninput=()=>{{a.currentTime=+sk.value}};
const jump=d=>{{a.currentTime=Math.max(0,Math.min({dur},(a.currentTime||0)+d));sk.value=a.currentTime}};
document.querySelectorAll('.sk[data-d]').forEach(x=>x.onclick=()=>jump(+x.dataset.d));
addEventListener('keydown',e=>{{if(e.target===sk)return;if(e.key==='ArrowLeft'){{jump(e.shiftKey?-10:-5);e.preventDefault()}}else if(e.key==='ArrowRight'){{jump(e.shiftKey?10:5);e.preventDefault()}}else if(e.key===' '){{b.click();e.preventDefault()}}}});
const f=t=>Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0');
window.__tick=T=>{{if(document.activeElement!==sk)sk.value=T;tm.textContent=f(T)+' / '+f({dur})}};
</script>'''
open(f'{OUT}/qamiga_preview.html','w').write(page)
print(sorted(refs))
