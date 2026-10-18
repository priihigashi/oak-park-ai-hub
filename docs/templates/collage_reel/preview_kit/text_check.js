// verifica cada LINHA de texto (Range rects): fora da margem, overflow do box e linhas desequilibradas
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(process.argv[2]));await p.evaluate(()=>window.READY);await new Promise(r=>setTimeout(r,1500));
const res=await p.evaluate(()=>{const out=[];const seen=new Set();
 document.querySelectorAll('.scene').forEach(sc=>{const prev=sc.style.display;sc.style.display='block';
  sc.querySelectorAll('.h,.sub,.label,.chip,.stamp-r,.mono,.src,.glass .h').forEach(el=>{
   if(el.closest('.kar'))return; const st=getComputedStyle(el); if(st.display==='none')return;
   // linhas
   const r=document.createRange(); r.selectNodeContents(el); const rects=[...r.getClientRects()].filter(x=>x.width>2);
   const lines={}; rects.forEach(x=>{const k=Math.round(x.top/10);lines[k]=lines[k]||{l:1e9,r:-1e9};lines[k].l=Math.min(lines[k].l,x.left);lines[k].r=Math.max(lines[k].r,x.right)});
   const L=Object.values(lines).map(x=>x.r-x.l); const txt=el.textContent.trim().slice(0,40);
   const minL=Math.min(...rects.map(x=>x.left)),maxR=Math.max(...rects.map(x=>x.right));
   if(minL<60||maxR>1020) out.push(`${sc.dataset.s} FORA «${txt}» L${Math.round(minL)} R${Math.round(maxR)}`);
   if(el.scrollWidth>el.clientWidth+2) out.push(`${sc.dataset.s} OVERFLOW «${txt}» ${el.scrollWidth}>${el.clientWidth}`);
   if(L.length>=2&&(el.classList.contains('h')||el.classList.contains('sub'))){const last=L[L.length-1],mx=Math.max(...L);
     if(last<mx*0.55) out.push(`${sc.dataset.s} DESEQUILIBRADO «${txt}» linhas ${L.map(Math.round).join('/')}`);}
  });
  sc.style.display=prev;});
 return out;});
console.log(res.length?res.join('\n'):'ZERO problemas de texto');await b.close();})();
