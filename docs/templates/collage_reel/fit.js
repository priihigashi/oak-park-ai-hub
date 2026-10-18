/* fit.js — títulos e textos sempre dentro da caixa e com linhas equilibradas.
   1) se alguma palavra estoura a largura, reduz a fonte (até 60%);
   2) equilibra as linhas: acha a menor largura que mantém o mesmo número de linhas
      (evita "linha comprida + palavra sozinha embaixo").
   Roda antes do layout.js (que recalcula as alturas). */
(function(){
const SEL='.h,.sub,.glass .h,.glass .sub,.glass .mono';
const FONTS=['900 60px Rub','800 60px Rub','700 60px Rub','500 60px Rub','700 30px JBM','500 30px JBM'];
function lines(el){const r=document.createRange();r.selectNodeContents(el);const tops=new Set();
  [...r.getClientRects()].forEach(x=>{if(x.width>1)tops.add(Math.round(x.top/8))});return tops.size||1}
function textRight(el){const r=document.createRange();r.selectNodeContents(el);let m=-1e9;[...r.getClientRects()].forEach(x=>{if(x.width>1)m=Math.max(m,x.right)});return m}
function fitOne(el){
  if(el.closest('.kar')||el.classList.contains('cnt')||el.dataset.nofit)return;
  el.style.maxWidth='';
  const box=el.getBoundingClientRect(); const W=el.clientWidth; if(!W)return; const k0=box.width/(el.offsetWidth||1);
  // 1) estouro
  let fs=parseFloat(getComputedStyle(el).fontSize), f0=fs, k=0;
  while(k++<30 && (el.scrollWidth>W+1 || textRight(el)>box.left+W*k0+1) && fs>f0*.6){fs*=.96; el.style.fontSize=fs+'px';}
  // 1b) se diminuir até 20% tira uma linha inteira, diminui (evita palavra sozinha numa linha)
  let n=lines(el);
  if(n>=2){const fb=fs; let f2=fs, ok=false;
    for(let i=0;i<10;i++){f2*=.978; el.style.fontSize=f2+'px'; if(lines(el)<n && el.scrollWidth<=W+1){ok=true;break}}
    if(ok){fs=f2;n=lines(el)} else {el.style.fontSize=fb+'px'}}
  // 2) equilíbrio
  if(n<2)return;
  let lo=W*.4, hi=W;
  for(let i=0;i<14;i++){const mid=(lo+hi)/2; el.style.maxWidth=mid+'px'; if(lines(el)>n||el.scrollWidth>mid+1) lo=mid; else hi=mid;}
  el.style.maxWidth=Math.ceil(hi+2)+'px';
}
function fitAll(){
  document.querySelectorAll('.scene').forEach(sc=>{const prev=sc.style.display; sc.style.display='block';
    const saved=[]; sc.querySelectorAll('.el').forEach(e=>{saved.push([e,e.style.transform,e.style.opacity]); e.style.transform='none';});
    sc.querySelectorAll(SEL).forEach(fitOne);
    saved.forEach(([e,t,o])=>{e.style.transform=t;});
    sc.style.display=prev;});
  window.FIT_DONE=1;
}
const r=window.READY||Promise.resolve();
window.READY=r.then(()=>Promise.all(FONTS.map(f=>document.fonts.load(f).catch(()=>0)))).then(fitAll);
window.refit=fitAll;
})();
