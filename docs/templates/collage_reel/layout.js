/* layout.js — auto-empilhamento vertical com espaçamento uniforme.
   Elementos com data-flow="grupo:ordem" são empilhados em ordem; mesma ordem = mesmo slot (trocas com data-o).
   data-ftop no primeiro elemento do grupo = y inicial; data-gap = espaço antes do slot (padrão 40); data-dy = deslocamento extra. */
(function(){
const GAP=40;
/* fitHeads — títulos (.el.h) sempre "cheios": sem palavra órfã, sem linha curta sobrando.
   Para cada título testa 1..4 linhas, acha o MAIOR tamanho de fonte que cabe naquela quantidade de linhas
   (com text-wrap:balance para as linhas ficarem parecidas) e escolhe a menor quantidade de linhas que
   não encolha a fonte mais que 18%. Títulos nowrap só encolhem se estourarem a largura.
   data-nofit="1" desliga. data-fitmax / data-fitmin = limites (fração da fonte original). */
(function(){const s=document.createElement('style');s.textContent='.el{text-wrap:pretty}.el.h{text-wrap:balance}';document.head.appendChild(s)})();
function fitHeads(sc){
  sc.querySelectorAll('.el.h:not([data-nofit]):not(.cnt)').forEach(el=>{
    const cs=getComputedStyle(el);
    if(!el.style.width) return;
    if(!el.dataset.fs0) el.dataset.fs0=parseFloat(cs.fontSize);
    const f0=+el.dataset.fs0, W=el.clientWidth||parseFloat(el.style.width)||880;
    const hi=f0*(+el.dataset.fitmax||1.15), lo=f0*(+el.dataset.fitmin||.55);
    const set=f=>{el.style.fontSize=f+'px'};
    const lh=()=>{const v=parseFloat(getComputedStyle(el).lineHeight);return isNaN(v)?parseFloat(el.style.fontSize)*1.1:v};
    const lines=()=>Math.round(el.offsetHeight/lh());
    const over=()=>el.scrollWidth>el.clientWidth+1;
    if(cs.whiteSpace==='nowrap'){ set(f0); let f=f0; while(over()&&f>lo){f-=2;set(f)} return; }
    el.style.textWrap='balance';
    const best=n=>{let a=lo,b=hi; set(a); if(lines()>n||over()) return 0;
      for(let i=0;i<14;i++){const m=(a+b)/2; set(m); if(lines()<=n&&!over()) a=m; else b=m;} return Math.floor(a);};
    const widths=()=>{const r=document.createRange(); r.selectNodeContents(el); const L={};
      [...r.getClientRects()].forEach(q=>{if(q.width<2)return; const k=Math.round(q.top/8); L[k]=L[k]||[1e9,-1e9]; L[k][0]=Math.min(L[k][0],q.left); L[k][1]=Math.max(L[k][1],q.right)});
      return Object.values(L).map(v=>v[1]-v[0]);};
    const even=()=>{const w=widths(); return w.length<2?1:Math.min(...w)/Math.max(...w)};
    const res=[1,2,3,4].map(n=>{const f=best(n); if(!f) return {f:0,ev:0}; set(f); return {f,ev:even()}});
    let pick=res.findIndex(r=>r.f>=f0*.74&&r.ev>=.55);
    if(pick<0) pick=res.findIndex(r=>r.f>=f0*.82);
    if(pick<0){const m=Math.max(...res.map(r=>r.f)); pick=res.findIndex(r=>r.f===m)}
    set(res[pick].f||f0);
  });
}


/* vfill — distribui o bloco na ALTURA livre (ela, 19/out/2026: "tá tudo apertado lá em cima e sobra espaço antes da legenda").
   Ativa com window.VFILL = y limite (em coordenadas da cena, ex. 1390) ou data-vfill na cena; data-vfill="0" desliga na cena.
   O 1º slot (título do capítulo) fica onde está; a sobra vira espaço extra IGUAL entre os slots seguintes
   (até +MAXX px por espaço) e o que ainda sobrar desce o corpo, dividindo metade em cima e metade embaixo. */
const MAXX=120;
function vfill(sc,G,keys,yEnd){
  const lim=+(sc.dataset.vfill!==undefined?sc.dataset.vfill:(window.VFILL||0));
  if(!lim||keys.length<2) return;
  const free=lim-yEnd; if(free<12) return;
  const n=keys.length-1, per=Math.min(MAXX,free/n), rest=free-per*n;
  const top0=rest>0?rest/2:0;
  keys.forEach((k,i)=>{ if(!i) return; const add=top0+per*i;
    G[k].forEach(e=>{e.style.top=(parseFloat(e.style.top)+add)+"px"}); });
  sc.dataset.vfillAdd=Math.round(free);
}

function layout(){
  document.querySelectorAll('.scene').forEach(sc=>{
    const prev=sc.style.display; sc.style.display='block'; fitHeads(sc);
    const els=[...sc.querySelectorAll('[data-flow]')];
    const groups={};
    els.forEach(el=>{const [g,n]=el.dataset.flow.split(':');(groups[g]=groups[g]||{});(groups[g][n]=groups[g][n]||[]).push(el)});
    Object.values(groups).forEach(G=>{
      const keys=Object.keys(G).sort((a,b)=>+a-+b); let y=null;
      keys.forEach((k,i)=>{
        const slot=G[k]; const f=slot.find(e=>e.dataset.ftop);
        if(y===null) y=f?+f.dataset.ftop:330; else { const gp=slot.find(e=>e.dataset.gap); y+= gp?+gp.dataset.gap:GAP; }
        let h=0; slot.forEach(e=>{e.style.top=(y+(+e.dataset.dy||0))+"px"; if(!e.dataset.nosize) h=Math.max(h,e.offsetHeight,+(e.dataset.minh||0))});
        y+=h;
      });
      vfill(sc,G,keys,y);
      sc.dataset.flowEnd=(sc.dataset.flowEnd?Math.max(+sc.dataset.flowEnd,y):y);
    });
    sc.style.display=prev;
  });
}
const FONTS=['900 60px Rub','800 60px Rub','700 60px Rub','500 60px Rub','700 60px Hand','700 30px JBM','500 30px JBM'];
const r=window.READY||Promise.resolve();
window.READY=r.then(()=>Promise.all(FONTS.map(f=>document.fonts.load(f).catch(()=>0)))).then(()=>{layout(); window.LAYOUT_DONE=1;});
if(document.fonts&&document.fonts.addEventListener) document.fonts.addEventListener('loadingdone',()=>layout());
setTimeout(layout,1500);
window.relayout=layout;
})();
