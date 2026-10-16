/* layout.js — auto-empilhamento vertical com espaçamento uniforme.
   Elementos com data-flow="grupo:ordem" são empilhados em ordem; mesma ordem = mesmo slot (trocas com data-o).
   data-ftop no primeiro elemento do grupo = y inicial; data-gap = espaço antes do slot (padrão 40); data-dy = deslocamento extra. */
(function(){
const GAP=40;
function layout(){
  document.querySelectorAll('.scene').forEach(sc=>{
    const prev=sc.style.display; sc.style.display='block';
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
