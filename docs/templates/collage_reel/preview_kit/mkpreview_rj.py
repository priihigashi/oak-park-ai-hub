import re,os,shutil,subprocess
SRC='/home/claude/hub/docs/templates/collage_reel'; OUT='/home/claude/work/rj/preview'
h=open(f'{SRC}/rj.html').read()
style=re.search(r'<style>(.*?)</style>',h,re.S).group(1)
style=style.replace('html,body{width:1080px;height:1920px;overflow:hidden;background:#050608}','')
stage=re.search(r'(<div id="stage">.*?</div></div>)\s*<script>',h,re.S).group(1)
dur=re.search(r'window.DUR=([\d.]+)',h).group(1)
ZJS=re.search(r'<script>(\s*/\* zoom da abertura.*?)</script>',h,re.S).group(1)
# assets
os.makedirs(f'{OUT}/assets/rj',exist_ok=True)
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
# a narração vem SEMPRE do mix.py (data/rj): antes copiava um MP3 velho de /home/claude/work/rj e a voz ficava 30 s fora da linha do tempo
NARR=f'{SRC}/data/rj/narracao.mp3'
shutil.copy(NARR,f'{OUT}/narracao.mp3')
_d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',NARR]))
assert abs(_d-float(dur))<0.3, f'narracao.mp3 tem {_d:.2f}s mas a linha do tempo tem {dur}s: rode build.py e mix.py de novo'
ZD='/home/claude/work/rj/zf'; os.makedirs(f'{OUT}/assets/rj/zoom',exist_ok=True)
ZN=int(os.environ.get('ZN','0')) or len([f for f in os.listdir(ZD) if f.endswith('.jpg')])
for f in (os.listdir(ZD) if os.path.isdir(ZD) else []):
    if f.endswith('.jpg'): shutil.copy(f'{ZD}/{f}',f'{OUT}/assets/rj/zoom/{f}')
page=f'''<title>Reel Rio de Janeiro</title>
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
.pv-copy{{width:100%;max-width:520px;display:flex;flex-direction:column;gap:12px}}.pv-cp{{display:flex;flex-direction:column;gap:6px}}.pv-cp-h{{display:flex;justify-content:space-between;align-items:center;font:600 14px system-ui}}.pv-cp textarea{{width:100%;box-sizing:border-box;background:#141518;color:var(--fg);border:1px solid var(--line);border-radius:10px;padding:10px;font:13px/1.45 system-ui;resize:vertical}}.cpb{{background:transparent;color:var(--fg);border:1px solid var(--line);border-radius:999px;padding:6px 14px;font:600 13px system-ui;cursor:pointer}}.cpb:focus-visible{{outline:2px solid var(--accent)}}
</style>
<div class="pv-head"><h1>Rio é culpa da esquerda? · prévia</h1><small id="ver">v1 · rodada 36</small></div>
<div class="pv-frame" id="frame"><div id="scaler">{stage}</div></div>
<div class="pv-bar"><button id="play" type="button">▶ Play</button><input id="seek" type="range" min="0" max="{dur}" step="0.05" value="0" aria-label="Posição"><output id="tm">0:00</output></div>
<div class="pv-bar pv-skip" role="group" aria-label="Pular"><button type="button" class="sk" data-d="-30">↺ 30s</button><button type="button" class="sk" data-d="-10">↺ 10s</button><button type="button" class="sk" data-d="-5">↺ 5s</button><button type="button" class="sk" data-d="5">5s ↻</button><button type="button" class="sk" data-d="10">10s ↻</button><button type="button" class="sk" data-d="30">30s ↻</button></div>
<div class="pv-bar" role="group" aria-label="Velocidade"><span class="pv-sp-l">Velocidade</span><button type="button" class="sp on" data-r="1">1x</button><button type="button" class="sp" data-r="1.2">1,2x</button><button type="button" class="sp" data-r="1.5">1,5x</button><button type="button" class="sp" data-r="2">2x</button><button type="button" class="sp" data-r="3">3x</button></div>
<p class="pv-note">Prévia ao vivo do reel (as animações rodam no navegador; o MP4 final sai do mesmo arquivo). Botões pulam 5/10/30s; setas ← → pulam 5s (Shift: 10s), espaço dá play/pausa. Recarregue para ver a última edição. Voz e fundos provisórios.</p>
<section class="pv-copy" aria-label="Textos do post"><div class="pv-cp"><div class="pv-cp-h"><b>Legenda</b><button type="button" class="cpb" data-for="cap">Copiar</button></div><textarea id="cap" readonly rows="14">COMPARTILHA NOS STORIES 🔁 e manda pros Melhores Amigos ⭐

O Rio é governado pela direita há 23 anos. Então a violência no estado é culpa da esquerda? 🤔

Fomos aos dados: quem manda na polícia, o que melhorou, o que piorou, quem ajudou e quem atrapalhou — dos dois lados.

✔️ A violência subiu e caiu com os dois lados, e depois de 2018 caiu junto com o Brasil
✔️ Com Rosinha e Cabral, o Rio caiu enquanto o país subia: ali o estado fez diferença
✔️ Em 2025, o Rio voltou a subir, puxado pelas mortes em ações policiais
✔️ 6 dos 7 governadores desde 1999 foram presos, afastados ou ficaram inelegíveis — dos dois lados

Quem governa leva o crédito do que melhora e a conta do que piora.

E você: o que cobraria do governador eleito? 👇

Dados, metodologia e fontes completas no primeiro comentário.

#RioDeJaneiro #SegurançaPública #FactCheck #Eleições2026 #DadosAbertos</textarea></div><div class="pv-cp"><div class="pv-cp-h"><b>Primeiro comentário</b><button type="button" class="cpb" data-for="com">Copiar</button></div><textarea id="com" readonly rows="14">COMENTA: o que você cobraria do governador eleito? 👇
.
.
📚 FONTES
• Mortes violentas no RJ (1998–2025): ISP-RJ, letalidade violenta; FBSP, Anuário Brasileiro de Segurança Pública 2026
• Homicídios no Brasil: Mapa da Violência 2006 e Atlas da Violência (SIM/Ministério da Saúde)
• Sudeste por 100 mil (2013–2025): FBSP, Anuário 2026 (tabela 02)
• Estatuto do Desarmamento e armas entregues: Senado/Exército (2004–2005)
• Grupos armados: GENI/UFF + Fogo Cruzado, Mapa dos Grupos Armados (dez/2025)
• Milícia e política: CPI das Milícias da Alerj (2008); MP-RJ; STF, caso Marielle (fev/2026)
• Mortes pela polícia: FBSP; MP-RJ/Cenpe, Letalidade Policial no RJ em 10 pontos (2019); Fórum Justiça/CESeC (2011–2021)
• Operação Contenção: Reuters; Polícia Civil-RJ; Defensoria Pública; Datafolha
• Câmeras e uso da força: MJSP (portaria mai/2024, decreto dez/2024); nota do Cosud (Poder360, dez/2024)
• Rastreio de munição e PL 3.723/2019: Exército/Colog (2020); STF; Congresso em Foco
• Esclarecimento de homicídios: Instituto Sou da Paz, Onde Mora a Impunidade (2025)
• Dinheiro federal: Ministério da Justiça, nota de 28/10/2025
• Checagens: Aos Fatos, Comprova
• Rosinha, 1ª governadora eleita do RJ: Poder360
• Ideologia dos partidos: Bolognesi, Ribeiro e Codato, Revista Dados (2023)

📝 NOTAS
• Governo do RJ: esquerda e centro-esquerda de 1999 a ago/2003 (Garotinho, PDT→PSB; Benedita, PT, 9 meses; Rosinha até entrar no MDB). Desde ago/2003, direita (MDB = 7,01 na escala de Bolognesi). Capital: nenhum prefeito de esquerda desde 1993.
• Polícia Militar, Polícia Civil e investigação são do estado (Constituição, art. 144). Fronteiras, portos, armas e Polícia Federal são da União. Guarda municipal e ordem urbana, da prefeitura.
• % de cada governador = mortes violentas no fim do mandato contra o ano antes da posse. Os +26% de Garotinho incluem os 9 meses de Benedita (PT).
• A linha do Brasil é de homicídios (SIM), ajustada à escala do Rio só para comparar a forma da curva. Mortes violentas (ISP/FBSP) e homicídios (SIM) são métricas diferentes.
• Prisão e afastamento não são condenação; Pezão foi absolvido. Investigação e denúncia também não são condenação. Todos os citados negam irregularidades.
• Siglas: quando o político mudou de partido, aparecem as duas (Castro: PSC → PL).</textarea></div><p class="pv-note">Download do vídeo: aparece aqui quando o MP4 for gerado, depois da sua aprovação.</p></section>
<audio id="vo" preload="auto" playsinline></audio>
<script>window.DUR={dur};window.VFILL=1390;window.__ZN={ZN};window.__ZF=k=>"assets/rj/zoom/f"+String(k).padStart(3,"0")+".jpg";for(let k=0;k<window.__ZN;k++){{const i=new Image();i.src=window.__ZF(k)}}</script><script src="fx.js"></script><script src="fx2.js"></script><script>{ZJS}</script><script src="engine.js"></script><script src="layout.js"></script>
<script>
const fr=document.getElementById('frame'),st=document.getElementById('scaler'),a=document.getElementById('vo'),b=document.getElementById('play'),sk=document.getElementById('seek'),tm=document.getElementById('tm');
function fit(){{const H=Math.min(innerHeight-130,1920),W=Math.min(document.body.clientWidth-32,520);let s=Math.min(H/1920,W/1080);fr.style.width=1080*s+'px';fr.style.height=1920*s+'px';st.style.transform='scale('+s+')'}}
addEventListener('resize',fit);fit();
// áudio carregado inteiro como blob: a barra e os pulos funcionam em qualquer ponto, mesmo sem suporte a Range no servidor
const ready=fetch('narracao.mp3?v='+Date.now()).then(r=>r.blob()).then(bl=>{{a.src=URL.createObjectURL(bl);return new Promise(r=>a.addEventListener('loadedmetadata',r,{{once:true}}))}}).catch(()=>{{a.src='narracao.mp3?v='+Date.now()}});
a.onplay=()=>{{b.textContent='❚❚ Pausa'}};a.onpause=()=>{{b.textContent='▶ Play'}};
b.onclick=()=>{{if(a.paused){{const go=()=>a.play().catch(()=>{{b.textContent='carregando…';a.load();a.addEventListener('canplay',()=>a.play().catch(()=>{{b.textContent='▶ Play'}}),{{once:true}})}});if(a.ended||a.currentTime>=a.duration-.05)a.currentTime=0;go()}}else a.pause()}};
document.querySelectorAll('.sp').forEach(x=>x.onclick=()=>{{a.playbackRate=+x.dataset.r;a.preservesPitch=true;document.querySelectorAll('.sp').forEach(y=>y.classList.toggle('on',y===x))}});
a.onended=()=>{{b.textContent='▶ Play'}};
sk.oninput=()=>{{const t=+sk.value;ready.then(()=>{{a.currentTime=t;render(t)}})}};
const jump=d=>{{ready.then(()=>{{const t=Math.max(0,Math.min({dur}-0.05,(a.currentTime||0)+d));a.currentTime=t;sk.value=t;render(t)}})}};
document.querySelectorAll('.sk[data-d]').forEach(x=>x.onclick=()=>jump(+x.dataset.d));
addEventListener('keydown',e=>{{if(e.target===sk)return;if(e.key==='ArrowLeft'){{jump(e.shiftKey?-10:-5);e.preventDefault()}}else if(e.key==='ArrowRight'){{jump(e.shiftKey?10:5);e.preventDefault()}}else if(e.key===' '){{b.click();e.preventDefault()}}}});
const f=t=>Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0');
window.__tick=T=>{{if(document.activeElement!==sk)sk.value=T;tm.textContent=f(T)+' / '+f({dur})}};
document.querySelectorAll('.cpb').forEach(b=>b.onclick=async()=>{{const t=document.getElementById(b.dataset.for);try{{await navigator.clipboard.writeText(t.value);b.textContent='Copiado'}}catch(e){{t.focus();t.select();b.textContent='Selecionado'}}setTimeout(()=>b.textContent='Copiar',1600)}});
</script>'''
open(f'{OUT}/index.html','w').write(page)
print(sorted(refs))
