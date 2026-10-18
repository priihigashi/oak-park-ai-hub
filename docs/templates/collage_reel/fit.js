/* fit.js — ajusta o tamanho de cada título (.h / [data-fit]) para ocupar a largura sem palavra órfã.
   Regra: 1) prefere MENOS linhas, desde que a fonte não caia abaixo de 78% do tamanho base;
          2) com o nº de linhas fixo, cresce a fonte (até 118%) enquanto ainda couber nesse nº de linhas;
          3) text-wrap: balance deixa as linhas com largura parecida (nada de 1–2 palavras sozinhas embaixo).
   Rodar ANTES do layout.js (carregar fit.js antes). Ignora elementos com data-nofit. */
(function(){
function lines(el){
  const r=document.createRange(); r.selectNodeContents(el);
  const tops=[]; for(const q of r.getClientRects()){ if(q.width<2) continue; const t=Math.round(q.top/8); if(!tops.some(x=>Math.abs(x-t)<=2)) tops.push(t); }
  return Math.max(1,tops.length);
}
function tw(el){ const r=document.createRange(); r.selectNodeContents(el); let a=1e9,b=-1e9; for(const q of r.getClientRects()){ if(q.width<2) continue; a=Math.min(a,q.left); b=Math.max(b,q.right);} const k=(el.getBoundingClientRect().width/(el.offsetWidth||1))||1; return (b-a)/k; }
function fitOne(el){
  if(el.dataset.nofit!==undefined||el.dataset.fitted) return;
  const base=parseFloat(el.dataset.fs||getComputedStyle(el).fontSize); el.dataset.fs=base;
  el.style.textWrap='balance';
  const set=s=>{el.style.fontSize=s.toFixed(1)+'px'};
  const maxW=parseFloat(el.style.width)||900;
  const ok=l=>lines(el)<=l && tw(el)<=maxW+1;
  set(base); let L=lines(el);
  // 1) menos linhas, se der sem encolher demais
  let best=base;
  for(let s=base; s>=base*0.78; s-=base*0.02){ set(s); const l=lines(el); if(l<L){ L=l; best=s; break; } }
  // 2) maior fonte que mantém L linhas
  let lo=best, hi=base*1.18;
  set(hi); if(ok(L)) lo=hi; else { for(let i=0;i<12;i++){ const m=(lo+hi)/2; set(m); if(ok(L)) lo=m; else hi=m; } }
  set(lo); while(tw(el)>maxW+1 && lo>base*0.6){ lo-=base*0.02; set(lo); }
  set(lo); el.dataset.fitted=1; el.dataset.lines=L;
}
function fitAll(){
  document.querySelectorAll('.scene').forEach(sc=>{
    const prev=sc.style.display; sc.style.display='block';
    sc.querySelectorAll('.h:not(.glrow .h), [data-fit]').forEach(el=>{ if(el.closest('.govlist')) return; fitOne(el); });
    sc.querySelectorAll('.sub').forEach(el=>{el.style.textWrap='balance'});
    // listas (govlist): cada linha numa linha só; se não couber, a lista inteira diminui junto
    sc.querySelectorAll('.govlist').forEach(gl=>{
      const bs=[...gl.querySelectorAll('.glrow b')]; if(!bs.length) return;
      bs.forEach(b=>{b.style.whiteSpace='nowrap'});
      let fs=parseFloat(getComputedStyle(bs[0]).fontSize);
      const over=()=>bs.some(b=>{const row=b.closest('.glrow'); return row.scrollWidth>gl.clientWidth+1 || b.getBoundingClientRect().right>gl.getBoundingClientRect().right+1});
      while(over() && fs>44){ fs-=2; bs.forEach(b=>{b.style.fontSize=fs+'px'}); }
      if(over()) bs.forEach(b=>{b.style.whiteSpace='normal'; b.style.textWrap='balance'});
    });
    sc.style.display=prev;
  });
  window.FIT_DONE=1;
}
const FONTS=['900 60px Rub','800 60px Rub','700 60px Rub','500 60px Rub','700 30px JBM'];
const r=window.READY||Promise.resolve();
window.READY=r.then(()=>Promise.all(FONTS.map(f=>document.fonts.load(f).catch(()=>0)))).then(()=>document.fonts.ready).then(fitAll);
window.refit=()=>{document.querySelectorAll('[data-fitted]').forEach(e=>delete e.dataset.fitted);fitAll()};
})();
