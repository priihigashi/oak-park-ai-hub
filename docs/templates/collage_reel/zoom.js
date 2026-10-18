/* zoom.js — câmera sobre uma imagem grande (ex.: mapa do Brasil → estado).
   <div class="zoomer" data-z="t,escala,ix,iy,fx,fy; ..."><img ...></div>
   t = segundos desde o início da cena; (ix,iy) = ponto da imagem que fica em (fx,fy) do quadro 1080x1920.
   Entre quadros-chave: escala em log, pontos com easing suave. Carregar DEPOIS do engine.js. */
(function(){
  const ease=p=>p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2;
  const K=[...document.querySelectorAll('.zoomer')].map(el=>({el,s0:+el.closest('.scene').dataset.s,
    k:el.dataset.z.split(';').map(r=>r.trim().split(',').map(Number))}));
  function upd(T){K.forEach(({el,s0,k})=>{const t=T-s0; let a=k[0],b=k[0],p=0;
    for(let i=0;i<k.length;i++){ if(t>=k[i][0]){a=k[i];b=k[i+1]||k[i];p=b===a?0:Math.min(1,(t-a[0])/(b[0]-a[0]));} }
    if(t<k[0][0]){a=b=k[0];p=0}
    const q=ease(p), L=(x,y)=>x+(y-x)*q, s=Math.exp(L(Math.log(a[1]),Math.log(b[1])));
    const ix=L(a[2],b[2]),iy=L(a[3],b[3]),fx=L(a[4],b[4]),fy=L(a[5],b[5]);
    el.style.transform=`translate(${fx-ix*s}px,${fy-iy*s}px) scale(${s})`;});}
  const r0=window.render; window.render=function(T){r0(T);upd(T)}; upd(0);
})();
