const { chromium } = require('/home/claude/hub/docs/templates/collage_reel/node_modules/playwright');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file:///home/claude/hub/docs/templates/collage_reel/qamiga.html');await p.evaluate(()=>window.READY);
const res=await p.evaluate(()=>{
 const SKIP=['gov','dimmer','fullimg','shadeg2','bigline','st','mst','ball','ball2','rail','col','aiwarn'];
 const out={};
 for(let t=0;t<window.DUR;t+=0.25){ render(t);
  const sc=[...document.querySelectorAll('.scene')].find(s=>getComputedStyle(s).display!=='none'); if(!sc) continue;
  const els=[...sc.querySelectorAll('.el')].filter(e=>!SKIP.some(c=>e.classList.contains(c)) && !e.parentElement.closest('.el'));
  const vis=els.filter(e=>{let o=1,n=e;while(n&&n!==sc){o*=+getComputedStyle(n).opacity;n=n.parentElement}const tf=getComputedStyle(e).transform; let sc1=1; if(tf&&tf!=='none'){const m=tf.match(/matrix\(([^)]+)\)/); if(m){const v=m[1].split(',').map(Number); sc1=Math.hypot(v[0],v[1]);}}
   return o>0.95 && Math.abs(sc1-1)<0.02 && (e.textContent.trim()||e.classList.contains('cnt'))});
  const dim=[...sc.querySelectorAll('.dimmer')].find(d=>+getComputedStyle(d).opacity>0.5);
  if(dim){ const all=[...sc.querySelectorAll('.el')]; const di=all.indexOf(dim); for(let q=vis.length-1;q>=0;q--) if(all.indexOf(vis[q])<di) vis.splice(q,1); }
  const R=vis.map(e=>{const r=e.getBoundingClientRect();return {e,r}});
  for(let i=0;i<R.length;i++)for(let j=i+1;j<R.length;j++){const a=R[i].r,c=R[j].r;
    const w=Math.min(a.right,c.right)-Math.max(a.left,c.left), h=Math.min(a.bottom,c.bottom)-Math.max(a.top,c.top);
    if(w>6&&h>6){ const k=sc.dataset.s+' | '+R[i].e.className.slice(0,25)+' «'+R[i].e.textContent.trim().slice(0,22)+'» x '+R[j].e.className.slice(0,25)+' «'+R[j].e.textContent.trim().slice(0,22)+'»';
      if(!out[k]) out[k]=[t.toFixed(2),Math.round(w)+'x'+Math.round(h)]; }}
  // out of safe frame check
  R.forEach(({e,r})=>{ if(r.left<60||r.right>1020){const k='EDGE '+sc.dataset.s+' '+e.className.slice(0,20)+' «'+e.textContent.trim().slice(0,22)+'» L'+Math.round(r.left)+' R'+Math.round(r.right); if(!out[k]) out[k]=[t.toFixed(2)];}});
 }
 return out;});
for(const [k,v] of Object.entries(res)) console.log(v.join(' '),k);
await b.close();})();
