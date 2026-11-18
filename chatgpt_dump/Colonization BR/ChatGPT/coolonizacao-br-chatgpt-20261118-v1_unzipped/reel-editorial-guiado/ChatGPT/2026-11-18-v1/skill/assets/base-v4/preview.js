'use strict';
const data=window.PREVIEW_DATA,$=id=>document.getElementById(id),audio=$('audio');
let scene=-1,ac,oscillators=[],previewTime=0;
const burst='<svg viewBox="0 0 200 200" aria-hidden="true"><path d="M100 0 115 62 162 19 138 80 200 85 143 112 186 158 124 139 110 200 88 143 36 182 62 123 0 109 62 88 17 38 79 62Z" fill="currentColor"/></svg>';
const docSvg='<svg viewBox="0 0 720 230" aria-hidden="true"><path d="M25 15H165L195 45V205H25Z M165 15V45H195 M55 80H165 M55 112H165 M55 144H135" fill="none" stroke="currentColor" stroke-width="6"/><path d="M250 110H450 M425 85L450 110 425 135" fill="none" stroke="#FFD34D" stroke-width="8"/><path d="M520 15H660L690 45V205H520Z M660 15V45H690 M550 80H660 M550 112H660 M550 144H630" fill="none" stroke="currentColor" stroke-width="6"/></svg>';
function image(name,cls,top,height){return `<div class="window ${cls||''}" style="height:${height}px"><img src="${data.images[name]}" alt="Recorte autêntico do site" style="top:${top}px"></div>`}
function m(html,delay=0){return `<div class="motion" data-delay="${delay}">${html}</div>`}
function render(i){
 $('stage').className='stage '+data.scenes[i].theme;
 $('chapter').textContent=data.scenes[i].chapter;$('counter').textContent=String(i+1).padStart(2,'0')+' / '+data.scenes.length;
 $('source').textContent=data.scenes[i].source;$('handle').textContent=i===11?'@tentandochegaratevoce':'';
 const templates=[
 m('<span class="smalltag">UMA LEITURA PRA GENTE</span><div class="giant">299<span>/2026</span></div><h2 class="headline small">Entender<br>cada parte.</h2>')+m(image('01-site.png','paper-a',-285,440),.15)+`<div class="burst">${burst}</div>`,
 m('<span class="smalltag">INFORMAÇÃO MAIS PERTO</span><h2 class="headline">Parte<br>por parte.</h2>')+m('<div style="margin-top:65px">'+docSvg+'</div>',.2)+m('<div class="stamp">Facilitar o acesso</div>',.4),
 m('<h2 class="headline small">Leitura<br>comentada.</h2><p class="description">Por trechos, com acesso<br>ao texto integral.</p>')+m(image('02-oficial.png','',-410,590),.2),
 m('<h2 class="headline small">Aprender<br>de outro jeito.</h2>')+m(image('03-analise.png','',-330,650),.2)+m('<div class="stamp">Abra as explicações</div>',.6),
 m('<h2 class="headline small">Volte<br>à fonte.</h2>')+m(image('04-fontes.png','',-700,630),.2)+m('<p class="description">Documentos originais.<br>Links para conferir.</p>',.35),
 m('<h2 class="headline small">Uma hipótese<br>muda a conta.</h2><p class="description">Efeito estimado desta regra<br>no mínimo da saúde.</p>')+m('<div class="scene-two"><div class="measure"><b>5,8<span style="display:inline;font-size:48px"> bi</span></b><div class="bar" data-bar="full"></div><span>R$ · ano inteiro<br>na média de 2026</span></div><div class="measure"><b>0,0<span style="display:inline;font-size:48px"> bi</span></b><div class="bar" data-bar="zero"></div><span>R$ · sem imposto<br>em 2027</span></div></div>',.2)+m('<div class="quote" style="margin-top:65px">Hipóteses.<br>Não cortes realizados.</div>',2.2),
 m('<h2 class="headline">Ainda em<br>revisão.</h2><div class="rule"></div>')+m('<div style="margin-top:50px">'+docSvg+'</div><div class="stamp">Conferir e melhorar</div>',.15),
 m('<h2 class="headline">A gente<br>precisa<br>de você.</h2>')+`<div class="burst" style="top:610px;color:#171c2b">${burst}</div>`,
 m('<h2 class="headline small">Sua experiência<br>pode ajudar.</h2>')+m('<div class="word-list"><div class="word-item"><span>Pergunta</span><i>?</i></div></div>',1.1)+m('<div class="word-item"><span>Sugestão</span><i>↗</i></div>',2.1)+m('<div class="word-item"><span>Fato ou caso</span><i>+</i></div>',3.1),
 m('<h2 class="headline small">Participar<br>deste ponto.</h2>')+m(image('10-participar.png','',-595,550),.2)+m('<p class="description">Abra o formulário.<br>Mande seu feedback.</p>',.5),
 m('<h2 class="headline small">Pode ser<br>sem seu nome.</h2>')+m('<div style="margin:50px 0;color:#FFD34D">'+docSvg+'</div>',.3)+m('<div class="rule"></div><p class="description" style="font-size:63px">Sua contribuição<br>fica privada.</p>',2.45),
 m('<span class="smalltag">A LEITURA CONTINUA COM VOCÊ</span><h2 class="headline">Explore.<br>Questione.<br>Participe.</h2>')+m('<div class="cta-url">plp299-2026.<br>vercel.app</div>',.25)+`<div class="burst" style="top:740px;right:10px">${burst}</div>`
 ];$('visual').innerHTML=templates[i];
 document.querySelectorAll('.headline').forEach(heading=>{let count=0;for(const node of [...heading.childNodes])if(node.nodeType===3){const fragment=document.createDocumentFragment();for(const token of node.textContent.split(/(\s+)/)){if(!token.trim()){fragment.append(document.createTextNode(token));continue}const mask=document.createElement('span'),ink=document.createElement('span');mask.className='word-mask';ink.className='word-ink';ink.dataset.word=count++;ink.textContent=token;mask.append(ink);fragment.append(mask)}node.replaceWith(fragment)}});
}
function spring(x){return x<=0?0:1-Math.exp(-8*x)*(Math.cos(11*x)+.35*Math.sin(11*x))}
function size(){$('stage').style.transform=`scale(${document.querySelector('.phone').clientWidth/1080})`}
new ResizeObserver(size).observe(document.querySelector('.phone'));size();
window.seek=async function(t){
 let i=data.scenes.findLastIndex(s=>s.at<=t);i=Math.max(0,i);if(i!==scene){scene=i;render(i)}
 const age=t-data.scenes[i].at,reduced=matchMedia('(prefers-reduced-motion:reduce)').matches;
 document.querySelectorAll('.motion').forEach(el=>{const a=age-Number(el.dataset.delay||0),v=i===0?1:reduced?Number(a>=0):spring(a);el.style.opacity=i===0?1:Math.min(1,Math.max(0,a*5));el.style.transform=`translateY(${(1-v)*85}px) rotate(${(1-v)*2}deg)`});
 document.querySelectorAll('.burst').forEach(el=>{el.style.transform=`rotate(${age*9}deg) scale(${.95+.05*Math.sin(age*2)})`});
 document.querySelectorAll('.word-ink').forEach(el=>{const parent=el.closest('.motion'),delay=Number(parent?.dataset.delay||0),a=age-delay-Number(el.dataset.word)*.055,v=i===0||reduced?1:spring(a);el.style.transform=`translateY(${(1-v)*110}%) rotate(${(1-v)*3}deg)`});
 document.querySelectorAll('.bar').forEach(el=>{el.style.transform=`scaleX(${el.dataset.bar==='zero'?.025:Math.min(1,Math.max(0,spring(age-.5)))})`});
 document.querySelector('.orbit-a').style.transform=`translate(${Math.sin(t*.3)*25}px,${Math.cos(t*.3)*18}px)`;
 const page=data.pages.find(p=>t>=p.start&&t<p.end);$('caption').replaceChildren();
 if(page)for(const line of page.lines){const l=document.createElement('span');l.className='line';for(const w of line){const s=document.createElement('span');s.textContent=w.text+' ';s.className=t>=w.t&&t<w.t+w.d?'spoken':'';l.append(s)}$('caption').append(l)}
 $('progress').style.transform=`scaleX(${Math.min(1,t/data.duration)})`;
};
function mm(t){return Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0')}
function draw(){if(!audio.paused)previewTime=audio.currentTime;window.seek(previewTime);$('seek').value=previewTime;$('time').textContent=mm(previewTime)+' / '+mm(audio.duration||data.duration);requestAnimationFrame(draw)}
function jump(t){previewTime=Math.max(0,Math.min(audio.duration||data.duration,t));audio.currentTime=previewTime;window.seek(previewTime)}
$('play').onclick=async()=>{if(audio.paused){if(previewTime>=(audio.duration||data.duration))previewTime=0;audio.currentTime=previewTime;await audio.play();music()}else audio.pause()};
audio.onplay=()=>$('play').textContent='Ⅱ Pausar';audio.onpause=()=>{$('play').textContent='▶ Continuar';stopMusic()};audio.onended=()=>{$('play').textContent='↻ Assistir de novo';previewTime=data.duration;stopMusic()};audio.onloadedmetadata=()=>$('seek').max=audio.duration;
$('seek').oninput=()=>jump(+$('seek').value);
for(const n of [-30,-10,-5,5,10,30]){const b=document.createElement('button');b.textContent=(n>0?'+':'')+n+' s';b.onclick=()=>jump(previewTime+n);$('skip').append(b)}
for(const n of [1,1.05,1.1,1.2,1.5,2,3]){const b=document.createElement('button');b.className='speed';b.textContent=String(n).replace('.',',')+'x';b.setAttribute('aria-pressed',String(n===1));b.onclick=()=>{audio.playbackRate=n;document.querySelectorAll('.speed').forEach(x=>x.setAttribute('aria-pressed',String(x===b)))};$('speeds').append(b)}
async function copy(text){try{await navigator.clipboard.writeText(text);$('status').textContent='Copiado.'}catch{$('status').textContent='Selecione o texto para copiar.'}}
$('copyNotes').onclick=()=>copy('PLP 299 · leitura em construção\nID PLP299-SITE-V4\n'+location.href.split('#')[0]+'\n\n'+$('notes').value);document.querySelectorAll('[data-copy]').forEach(b=>b.onclick=()=>copy($(b.dataset.copy).value));
try{$('notes').value=localStorage.getItem('plp299-v4-notes')||''}catch{}$('notes').oninput=()=>{try{localStorage.setItem('plp299-v4-notes',$('notes').value)}catch{}};
$('script').textContent=data.script;
function stopMusic(){oscillators.forEach(o=>{try{o.stop()}catch{}});oscillators=[]}
function music(){stopMusic();if($('music').value==='none'||audio.paused)return;ac=ac||new AudioContext();ac.resume();const frequencies=$('music').value==='soft'?[174.61,261.63,349.23]:[220,329.63,440];frequencies.forEach((f,i)=>{const o=ac.createOscillator(),g=ac.createGain();o.type='sine';o.frequency.value=f;g.gain.setValueAtTime(0,ac.currentTime);g.gain.linearRampToValueAtTime(.004,ac.currentTime+2+i*.2);o.connect(g).connect(ac.destination);o.start();oscillators.push(o)})}
$('music').onchange=music;
Promise.all([document.fonts.ready,...Object.values(data.images).map(src=>new Promise(resolve=>{const img=new Image();img.onload=resolve;img.onerror=resolve;img.src=src}))]).then(()=>{window.ready=true;draw()});
