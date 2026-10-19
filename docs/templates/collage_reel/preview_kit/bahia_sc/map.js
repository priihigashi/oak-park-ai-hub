/* map.js — mapa do Brasil vetorial atrás das cenas (estilo "Reel Rio": escuro, fronteira fina, estado aceso com hachura + brilho).
   window.MAPCAM = [[T, escala, ix, iy, fx, fy], ...]   T = tempo global (s); (ix,iy) ponto do mapa (px do mapa base) que fica em (fx,fy) do quadro 1080x1920.
   window.MAPHL  = [[T, 'uf', 'dir'|'esq'|'yel'|'off', dur], ...]  acende/troca o estilo de um estado a partir de T.
   window.MAPLAB = [[t0, t1, ix, iy, html, cls], ...]  rótulo preso ao mapa (não escala com o zoom).
   Carregar DEPOIS do engine.js. */
(function(){
  const ease=p=>p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2;
  const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
  const map=document.getElementById('map'), labs=document.getElementById('maplabs');
  const P={}; map.querySelectorAll('path[data-uf]').forEach(p=>{P[p.dataset.uf]=p});
  const HL={}; (window.MAPHL||[]).forEach(e=>{(HL[e[1]]=HL[e[1]]||[]).push(e)});
  Object.values(HL).forEach(a=>a.sort((x,y)=>x[0]-y[0]));
  const L=(window.MAPLAB||[]).map(r=>{const d=document.createElement('div'); d.className='mlab '+(r[5]||''); d.innerHTML=r[4]; labs.appendChild(d); return {r,d}});
  function cam(T){const k=window.MAPCAM; let a=k[0],b=k[0],p=0;
    for(let i=0;i<k.length;i++){ if(T>=k[i][0]){a=k[i];b=k[i+1]||k[i];p=b===a?0:clamp((T-a[0])/(b[0]-a[0]));} }
    const q=ease(p), I=(x,y)=>x+(y-x)*q; const s=Math.exp(I(Math.log(a[1]),Math.log(b[1])));
    return {s,ix:I(a[2],b[2]),iy:I(a[3],b[3]),fx:I(a[4],b[4]),fy:I(a[5],b[5])};}
  function upd(T){
    const c=cam(T); const tx=c.fx-c.ix*c.s, ty=c.fy-c.iy*c.s;
    map.style.transform=`translate(${tx.toFixed(1)}px,${ty.toFixed(1)}px) scale(${c.s.toFixed(4)})`;
    map.style.setProperty('--sw',(1.5/(5*c.s)).toFixed(4));
    for(const uf in P){const ev=HL[uf]; let cls='', o=0;
      if(ev){let cur=null; for(const e of ev){if(T>=e[0]) cur=e;} if(cur&&cur[2]!=='off'){cls=cur[2]; o=clamp((T-cur[0])/(cur[3]||.45));}}
      const p=P[uf]; if(p._c!==cls){p.setAttribute('class',cls?('on '+cls):''); p._c=cls}
      p.style.opacity=cls?(0.25+0.75*o).toFixed(3):''; p.style.strokeWidth=cls?(4.5/(5*c.s)).toFixed(4):'';}
    L.forEach(({r,d})=>{const on=T>=r[0]&&T<r[1]; d.style.display=on?'block':'none'; if(!on) return;
      const k=clamp((T-r[0])/.35)*clamp((r[1]-T)/.25);
      d.style.opacity=k.toFixed(3); d.style.transform=`translate(${(tx+r[2]*c.s).toFixed(1)}px,${(ty+r[3]*c.s).toFixed(1)}px) translate(-50%,-50%) scale(${(.85+.15*k).toFixed(3)})`;});
  }
  const r0=window.render; window.render=function(T){r0(T);upd(T)}; upd(0);
})();
