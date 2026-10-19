
const fr=document.getElementById('frame'),st=document.getElementById('scaler'),a=document.getElementById('vo'),b=document.getElementById('play'),sk=document.getElementById('seek'),tm=document.getElementById('tm');
function fit(){const H=Math.min(innerHeight-130,1920),W=Math.min(document.body.clientWidth-32,520);let s=Math.min(H/1920,W/1080);fr.style.width=1080*s+'px';fr.style.height=1920*s+'px';st.style.transform='scale('+s+')'}
addEventListener('resize',fit);fit();
// áudio carregado inteiro como blob: a barra e os pulos funcionam em qualquer ponto, mesmo sem suporte a Range no servidor
const ready=fetch('narracao.mp3?v='+Date.now()).then(r=>r.blob()).then(bl=>{a.src=URL.createObjectURL(bl);return new Promise(r=>a.addEventListener('loadedmetadata',r,{once:true}))}).catch(()=>{a.src='narracao.mp3?v='+Date.now()});
a.onplay=()=>{b.textContent='❚❚ Pausa'};a.onpause=()=>{b.textContent='▶ Play'};
b.onclick=()=>{if(a.paused){const go=()=>a.play().catch(()=>{b.textContent='carregando…';a.load();a.addEventListener('canplay',()=>a.play().catch(()=>{b.textContent='▶ Play'}),{once:true})});if(a.ended||a.currentTime>=a.duration-.05)a.currentTime=0;go()}else a.pause()};
document.querySelectorAll('.sp').forEach(x=>x.onclick=()=>{a.playbackRate=+x.dataset.r;a.preservesPitch=true;document.querySelectorAll('.sp').forEach(y=>y.classList.toggle('on',y===x))});
a.onended=()=>{b.textContent='▶ Play'};
sk.oninput=()=>{const t=+sk.value;ready.then(()=>{a.currentTime=t;render(t)})};
const jump=d=>{ready.then(()=>{const t=Math.max(0,Math.min(window.DUR-0.05,(a.currentTime||0)+d));a.currentTime=t;sk.value=t;render(t)})};
document.querySelectorAll('.sk[data-d]').forEach(x=>x.onclick=()=>jump(+x.dataset.d));
addEventListener('keydown',e=>{if(e.target===sk)return;if(e.key==='ArrowLeft'){jump(e.shiftKey?-10:-5);e.preventDefault()}else if(e.key==='ArrowRight'){jump(e.shiftKey?10:5);e.preventDefault()}else if(e.key===' '){b.click();e.preventDefault()}});
const f=t=>Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0');
window.__tick=T=>{if(document.activeElement!==sk)sk.value=T;tm.textContent=f(T)+' / '+f(window.DUR)};
