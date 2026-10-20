/* fx2.js — "Kit Vox/documentário" (aprendido dos tutoriais tut_01–06 + refs 12–14, 2026-10-12).
   Carregar DEPOIS de fx.js e ANTES de engine.js:  <script src="fx.js"></script><script src="fx2.js"></script><script src="engine.js"></script>
   Tudo é aditivo: nada aqui muda cenas que não usam estes atributos.

   CENA (na .scene):
     data-fps="8|12"      POSTERIZE TIME — a cena anda em 8 ou 12 quadros/s (stop-motion orgânico). (tut_02/03)
     data-in="curve"      CORTE NA CURVA — entra em zoom com easing forte, já em alta velocidade, e freia. (tut_02)
     data-outcurve="1"    a cena sai acelerando o zoom nos últimos .3s — o corte acontece no pico de velocidade.
     data-crt="1"         TELA DE TV ANTIGA — scanlines + faixa escura rolando + cor de fósforo + vinheta. (tut_04)

   ELEMENTOS:
     .tintbg  data-tint="#0b3d2e"   FUNDO EM CAMADAS (favorito da Priih) — fotos do tema (prédio, jornal, arquitetura)
              empilhadas, P&B, contraste baixo (pretos → cinza-escuro, brancos levemente acima), tinta de cor por cima
              + textura. Nunca fundo chapado sem identidade. (tut_06)
     .parallax > [data-depth="0..1"]  PARALLAX — camadas (fundo/meio/frente) se movem em velocidades diferentes;
              data-pan="-60,0" na .parallax = quanto a camada da frente anda na cena. (tut_01)
     .pageturn data-t data-d        PÁGINA VIRANDO — dobra 3D do canto, com sombra; combine com data-fps="8". (tut_03)
     .cursor  data-path="x,y,t; x,y,t; ..."  data-click="t1 t2"   CURSOR que anda e clica (ripple + som de clique).
              Use com gráfico: o cursor vai até o ano/pico, clica, abre .popup. (tut_05, ref_14)
     .popup   data-a="pop" ...      (usa as entradas normais)
     .waves   data-t data-n="3"     ONDAS DE RÁDIO — anéis saindo de um ponto (marcador de local / chamar atenção). (tut_05)
     .focus   data-path="x%,y%,t; ..." data-r="260"   FOCO DE MAPA — escurece/desfoca tudo fora de um círculo que
              anda até onde o olho deve ir. (ref_12)
     .trim    (svg path)  data-t data-d  LINHA QUE SE DESENHA (trim paths) — rotas, fronteiras, setas. (ref_12)
     .cnt     contador: agora sempre monoespaçado (tabular-nums) pra não tremer. (tut_05)
*/
(function(){
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const ease={out:p=>1-Math.pow(1-p,4),in:p=>p*p*p,expo:p=>p>=1?1:1-Math.pow(2,-10*p),io:p=>p<.5?8*p*p*p*p:1-Math.pow(-2*p+2,4)/2};
const css=`
.cnt{font-variant-numeric:tabular-nums}
.tintbg{position:absolute;inset:0;overflow:hidden}
.tintbg img{position:absolute;filter:grayscale(1) contrast(.5) brightness(1.05) blur(1.2px);opacity:.55}
.tintbg .tint{position:absolute;inset:0;mix-blend-mode:color}
.tintbg .shade{position:absolute;inset:0;mix-blend-mode:multiply}
.tintbg .tex{position:absolute;inset:-40px;background:url(assets/grain.png);opacity:.35;mix-blend-mode:overlay}
.parallax{position:absolute;inset:0;overflow:hidden}
.parallax>[data-depth]{position:absolute;will-change:transform}
.pageturn{transform-origin:0% 50%;backface-visibility:hidden}
.pt-wrap{perspective:1600px}
.cursor{position:absolute;left:0;top:0;width:70px;height:90px;z-index:50;filter:drop-shadow(3px 4px 0 rgba(0,0,0,.35))}
.cursor .rip{position:absolute;left:-30px;top:-30px;width:60px;height:60px;border-radius:50%;border:5px solid currentColor;opacity:0}
.waves{position:absolute;width:0;height:0}
.waves i{position:absolute;left:-10px;top:-10px;width:20px;height:20px;border-radius:50%;border:5px solid currentColor;opacity:0}
.focus{position:absolute;inset:0;pointer-events:none}
.fx-crt{position:absolute;inset:0;pointer-events:none;z-index:40}
.fx-crt .sl{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.38) 0 3px,transparent 3px 6px)}
.fx-crt .roll{position:absolute;left:0;width:100%;height:420px;background:linear-gradient(transparent,rgba(0,0,0,.35),transparent)}
.fx-crt .vig{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 55%,rgba(0,0,0,.65) 100%)}
.fx-crt .ph{position:absolute;inset:0;background:#9fd6b4;mix-blend-mode:soft-light;opacity:.45}
`;
const st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);

/* monta componentes uma vez */
document.querySelectorAll('.tintbg').forEach(el=>{
  if(!el.querySelector('.tint')){const tc=el.dataset.tint||'#0b3d2e';
    el.insertAdjacentHTML('beforeend',`<div class="shade" style="background:${tc};opacity:.32"></div><div class="tint" style="background:${tc};opacity:.45"></div><div class="tex"></div>`);}
});
document.querySelectorAll('.cursor').forEach(el=>{
  el.innerHTML=`<svg viewBox="0 0 70 90" width="70" height="90"><path d="M4 4 L4 74 L22 57 L34 86 L46 81 L34 53 L60 53 Z" fill="#fff" stroke="#111" stroke-width="5" stroke-linejoin="round"/></svg><div class="rip"></div>`;
  el._path=(el.dataset.path||'540,960,0').split(';').map(s=>s.trim().split(',').map(Number));
  el._clicks=(el.dataset.click||'').split(/\s+/).filter(Boolean).map(Number);
});
document.querySelectorAll('.waves').forEach(el=>{const n=+(el.dataset.n||3); el.innerHTML='<i></i>'.repeat(n)});
document.querySelectorAll('.focus').forEach(el=>{el._path=(el.dataset.path||'50,50,0').split(';').map(s=>s.trim().split(',').map(Number))});
document.querySelectorAll('.trim').forEach(p=>{p.style.visibility='hidden'});
// sons: cliques do cursor e ondas entram no EVENTS que o engine cria depois → guardamos e o engine junta
window.FX2_EVENTS={tick:[],pop:[]};
document.querySelectorAll('.scene').forEach(sc=>{const s=+sc.dataset.s;
  sc.querySelectorAll('.cursor').forEach(c=>c._clicks.forEach(t=>FX2_EVENTS.pop.push(s+t)));
  sc.querySelectorAll('.waves').forEach(w=>FX2_EVENTS.pop.push(s+(+w.dataset.t||0)));
});

function along(path,t){ // [x,y,t] keyframes, easing in-out entre pontos
  if(t<=path[0][2]) return path[0];
  for(let i=1;i<path.length;i++){const a=path[i-1],b=path[i]; if(t<=b[2]){const p=ease.io((t-a[2])/Math.max(.001,b[2]-a[2])); return [a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p]}}
  return path[path.length-1];
}

function frame(sc,t,T,dur){
  // corte na curva
  if(sc.dataset.in==='curve'){const p=clamp(t/.45); const s=1+.55*(1-ease.expo(p)); sc.style.transform=`scale(${s.toFixed(4)})`; sc.style.opacity=1; sc.style.clipPath='none';}
  if(sc.dataset.outcurve){const q=clamp((t-(dur-.3))/.3); if(q>0){const s=1+.55*ease.in(q); sc.style.transform=`scale(${s.toFixed(4)})`; sc.style.filter=`blur(${(q*3).toFixed(1)}px)`;} else if(sc.dataset.in!=='curve'){sc.style.transform='';sc.style.filter=''}}
  // CRT
  if(sc.dataset.crt){let c=sc.querySelector(':scope > .fx-crt');
    if(!c){c=document.createElement('div');c.className='fx-crt';c.innerHTML='<div class="ph"></div><div class="sl"></div><div class="roll"></div><div class="vig"></div>';sc.appendChild(c)}
    c.querySelector('.roll').style.top=(((T*260)%2340)-420)+'px';}
  // parallax
  sc.querySelectorAll('.parallax').forEach(px=>{const [dx,dy]=(px.dataset.pan||'-80,0').split(',').map(Number); const p=ease.io(clamp(t/dur));
    px.querySelectorAll('[data-depth]').forEach(l=>{const d=+l.dataset.depth; const s=1+.06*d*p;
      l.style.transform=`translate(${(dx*d*p).toFixed(2)}px,${(dy*d*p).toFixed(2)}px) scale(${s.toFixed(4)})`;});});
  // tint bg: deriva lenta das fotos (vida sem distrair)
  sc.querySelectorAll('.tintbg img').forEach((im,i)=>{const p=t/dur; im.style.transform=`translate(${((i%2?-1:1)*30*p).toFixed(1)}px,${(-12*p).toFixed(1)}px) scale(${(1.04+.04*p).toFixed(4)})`;});
  // página virando
  sc.querySelectorAll('.pageturn').forEach(pg=>{const t0=+(pg.dataset.t||0), d=+(pg.dataset.d||1); const p=ease.io(clamp((t-t0)/d));
    pg.style.transform=`rotateY(${(-178*p).toFixed(2)}deg)`; pg.style.boxShadow=`${(-40*Math.sin(p*Math.PI)).toFixed(0)}px 0 60px rgba(0,0,0,${(.45*Math.sin(p*Math.PI)).toFixed(2)})`;
    pg.style.filter=`brightness(${(1-.35*Math.sin(p*Math.PI)).toFixed(3)})`; pg.style.visibility=p>=.999?'hidden':'visible';});
  // cursor
  sc.querySelectorAll('.cursor').forEach(c=>{const [x,y]=along(c._path,t); let s=1, ro=0, rs=1;
    c._clicks.forEach(k=>{const q=t-k; if(q>=0&&q<.18) s=1-.18*Math.sin(q/.18*Math.PI); if(q>=0&&q<.5){ro=1-q/.5; rs=1+q*4}});
    c.style.opacity=t<c._path[0][2]?0:1; c.style.transform=`translate(${x.toFixed(1)}px,${y.toFixed(1)}px) scale(${s.toFixed(3)})`;
    const r=c.querySelector('.rip'); r.style.opacity=ro.toFixed(3); r.style.transform=`scale(${rs.toFixed(3)})`;});
  // ondas
  sc.querySelectorAll('.waves').forEach(w=>{const t0=+(w.dataset.t||0); const per=+(w.dataset.per||1.2);
    [...w.children].forEach((ring,i)=>{const q=t-t0-i*per/w.children.length; if(q<0){ring.style.opacity=0;return}
      const ph=(q%per)/per; ring.style.opacity=(1-ph).toFixed(3); ring.style.transform=`scale(${(1+ph*9).toFixed(3)})`;});});
  // foco de mapa (escurece + desfoca fora do círculo)
  sc.querySelectorAll('.focus').forEach(f=>{const [x,y]=along(f._path,t); const r=+(f.dataset.r||260); const on=clamp((t-f._path[0][2])/.4);
    const g=`radial-gradient(circle ${r}px at ${x}% ${y}%, transparent 0, transparent 70%, rgba(0,0,0,${(.62*on).toFixed(2)}) 100%)`;
    f.style.background=g; f.style.backdropFilter=`blur(${(5*on).toFixed(1)}px)`;
    f.style.webkitMaskImage=f.style.maskImage=`radial-gradient(circle ${r}px at ${x}% ${y}%, transparent 60%, #000 100%)`;});
  // linhas que se desenham
  sc.querySelectorAll('.trim').forEach(p=>{if(!p._L){try{const L=p.getTotalLength(); if(!L)return; p._L=L; p.style.strokeDasharray=L; p.style.visibility='visible'}catch(e){return}} const q=ease.io(clamp((t-(+p.dataset.t||0))/(+(p.dataset.d||1)))); p.style.strokeDashoffset=(p._L*(1-q)).toFixed(1);});
}
// encadeia no FX existente
const base=window.FX||{enter(){},exit(){return false},frame(){}};
window.FX={enter:base.enter,exit:base.exit,frame(sc,t,T,dur){base.frame(sc,t,T,dur); frame(sc,t,T,dur);}};
})();
