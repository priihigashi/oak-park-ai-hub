/* fx.js — repertório de movimento extra para o motor de Colagem (reel.html).
   Referência 01: estilo "Antídoto" (kinetic type + retícula de linhas + legenda karaokê).
   Carregar DEPOIS do motor:  <script src="fx.js"></script>  — o motor chama FX.anim() e FX.frame().

   ENTRADAS novas (data-a=...):
     glitch    fatias horizontais + separação RGB, assenta em d segundos
     scatter   o texto/imagem nasce espalhado em pontinhos e se junta (NENHUM.)
     dissolve  aparece com desfoque → nítido (troca de foto tipo "cross-dissolve")
     iris      abre num círculo a partir do centro (olho / holofote)
     down      desce de cima (cartão de manchete)
     flash     estoura em branco e assenta
   SAÍDAS:  data-out="glitch|dissolve|scatter" + data-o="<seg>"
   CONTÍNUOS:
     data-boil="1"        borda de tinta "fervendo" a 8 fps (texto carimbado/serigrafia)
     data-rough="1"       borda fotocopiada PARADA (mesma textura, sem ferver)
     data-kb="1.08"       Ken Burns: zoom lento durante a cena (data-kbo="50% 30%" = origem)
     data-drift="-30,0"   deriva lenta em px durante a cena
     data-jit="2"         tremidinha de câmera na mão (px)
   COMPONENTES (classes):
     .kar    legenda karaokê: data-words="Eu:0 não:.25 tenho:.5 / dívida:1.1"  ("/" = nova página)
     .stack  palavra repetida enchendo a tela: data-word="VALORES." data-rows="22" data-t data-d
     .knock  texto em mix-blend difference (vira preto sobre a silhueta branca)
     .burst  balão de quadrinho estrelado (SVG gerado)  — data-spikes="18" data-tail="left|right|none"
     .torn   faixa de papel rasgado
   CENA:  data-in="cut|fade|glitch|wipe"   (padrão do motor = wipe)
          data-vhs="1"  linha de tracking + flicker (fita antiga)
*/
(function(){
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const rnd=s=>{const x=Math.sin(s*12.9898+78.233)*43758.5453;return x-Math.floor(x)};
const out3=t=>1-Math.pow(1-t,3);
const NS='http://www.w3.org/2000/svg';

/* ---------- filtros SVG compartilhados ---------- */
const svg=document.createElementNS(NS,'svg'); svg.setAttribute('width',0); svg.setAttribute('height',0);
svg.style.position='absolute';
let defs='';
for(let i=0;i<4;i++) defs+=`<filter id="boil${i}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="${i*7+3}"/><feDisplacementMap in="SourceGraphic" scale="7"/></filter>`;
svg.innerHTML=defs; document.body.appendChild(svg);
const scatterF=new Map();
function scatterFilter(el){ // um filtro por elemento (scale animado)
  if(scatterF.has(el)) return scatterF.get(el);
  const id='sc'+scatterF.size, f=document.createElementNS(NS,'filter');
  f.setAttribute('id',id); f.setAttribute('x','-30%'); f.setAttribute('y','-60%'); f.setAttribute('width','160%'); f.setAttribute('height','220%');
  f.innerHTML=`<feTurbulence type="turbulence" baseFrequency=".9" numOctaves="1" seed="${scatterF.size+1}"/><feDisplacementMap in="SourceGraphic" scale="0"/>`;
  svg.appendChild(f); const o={id,dm:f.querySelector('feDisplacementMap')}; scatterF.set(el,o); return o;
}

/* ---------- componentes gerados ---------- */
document.querySelectorAll('.burst').forEach((el,k)=>{
  const n=+(el.dataset.spikes||18), tail=el.dataset.tail||'left';
  const pts=[]; for(let i=0;i<n*2;i++){const a=i/(n*2)*Math.PI*2, r=i%2?40+rnd(k*31+i)*4:50; pts.push([50+Math.cos(a)*r*1.0,50+Math.sin(a)*r*0.82]);}
  let tailP=''; if(tail!=='none'){const s=tail==='left'?-1:1; tailP=`<polygon points="${50+s*8},78 ${50+s*30},${118} ${50+s*20},76" fill="#fff"/>`;}
  const bg=document.createElement('div'); bg.className='burst-bg';
  bg.innerHTML=`<svg viewBox="0 -5 100 125" preserveAspectRatio="none" style="width:100%;height:100%">${tailP}<polygon points="${pts.map(p=>p.map(v=>v.toFixed(1)).join(',')).join(' ')}" fill="#fff"/></svg>`;
  el.prepend(bg);
});
document.querySelectorAll('.torn').forEach((el,k)=>{
  let top='',bot=''; for(let i=0;i<=40;i++){const x=i*2.5; top+=`${x}% ${(rnd(k*9+i)*14).toFixed(1)}px,`; }
  for(let i=40;i>=0;i--){const x=i*2.5; bot+=`${x}% calc(100% - ${(rnd(k*17+i+50)*14).toFixed(1)}px),`;}
  el.style.clipPath=`polygon(${top}${bot.slice(0,-1)})`;
});
document.querySelectorAll('.stack').forEach(el=>{
  const w=el.dataset.word||'PALAVRA.', n=+(el.dataset.rows||20);
  el.innerHTML=Array.from({length:n},()=>`<div class="row">${w}</div>`).join('');
});
document.querySelectorAll('.kar').forEach(el=>{
  const pages=[[]]; (el.dataset.words||'').trim().split(/\s+/).forEach(tok=>{
    if(tok==='/'){pages.push([]);return}
    const i=tok.lastIndexOf(':'), tv=i>0?+tok.slice(i+1):NaN;   // palavra sem ":t" = anterior + .22 s
    const pg=pages[pages.length-1], prev=pg.length?pg[pg.length-1].t:(pages.length>1&&pages[pages.length-2].length?pages[pages.length-2].slice(-1)[0].t:0);
    pg.push(isNaN(tv)?{w:i>0?tok.slice(0,i):tok,t:prev+.22}:{w:tok.slice(0,i),t:tv});
  });
  el._pages=pages.map(p=>{const d=document.createElement('div'); d.className='kar-page';
    p.forEach(o=>{const s=document.createElement('span'); s.textContent=o.w+' '; o.s=s; d.appendChild(s)}); el.appendChild(d); return {words:p,el:d,t0:p.length?p[0].t:0};});
});

/* ---------- entradas / saídas ---------- */
function enter(a,p,el,t,ctx){ // ctx: {o,tx,ty,sc,r,filter,clip}
  switch(a){
    case 'glitch':{ if(p<1){const st=Math.floor(t*24); const amp=(1-p)*60;
        ctx.tx+=(rnd(st*3)-.5)*amp*2; const y1=rnd(st*5)*80, h=8+rnd(st*7)*30;
        ctx.clip=rnd(st*11)>.35?`inset(${y1}% 0 ${Math.max(0,100-y1-h)}% 0)`:'none';
        ctx.filter=`drop-shadow(${(amp*.4)|0}px 0 0 rgba(255,0,60,.9)) drop-shadow(${-(amp*.4)|0}px 0 0 rgba(0,200,255,.9))`;
        ctx.o=rnd(st*13)>.15?1:0;} return true;}
    case 'scatter':{ const f=scatterFilter(el); const q=out3(p); f.dm.setAttribute('scale',((1-q)*420).toFixed(1));
        ctx.filter=p<1?`url(#${f.id})`:''; ctx.o=clamp(p*2.2); return true;}
    case 'dissolve':{ ctx.o=out3(p); ctx.filter=p<1?`blur(${((1-p)*14).toFixed(1)}px)`:''; return true;}
    case 'iris':{ ctx.clip=p<1?`circle(${(out3(p)*80).toFixed(1)}% at 50% 50%)`:'none'; ctx.o=1; return true;}
    case 'down':{ ctx.ty+=-(1-out3(p))*160; ctx.o=clamp(p*2); return true;}
    case 'flash':{ ctx.o=1; ctx.filter=p<1?`brightness(${(1+(1-p)*4).toFixed(2)})`:''; ctx.sc*=1+(1-out3(p))*.08; return true;}
  }
  return false;
}
function exit(kind,q,el,t,ctx){
  if(kind==='dissolve'){ctx.o*=1-q; ctx.filter=`blur(${(q*14).toFixed(1)}px)`; return true}
  if(kind==='glitch'){const st=Math.floor(t*24); ctx.tx+=(rnd(st*3+1)-.5)*q*140; ctx.o*= rnd(st*5+2)>q?1:0;
    ctx.filter=`drop-shadow(${(q*24)|0}px 0 0 rgba(255,0,60,.9)) drop-shadow(${-(q*24)|0}px 0 0 rgba(0,200,255,.9))`; return true}
  if(kind==='scatter'){const f=scatterFilter(el); f.dm.setAttribute('scale',(q*420).toFixed(1)); ctx.filter=`url(#${f.id})`; ctx.o*=1-q*q; return true}
  return false;
}

/* ---------- por quadro ---------- */
function frame(sc,t,T,dur){
  // entrada da cena
  const mode=sc.dataset.in;
  if(mode){ sc.style.clipPath='none';
    if(mode==='fade'){sc.style.opacity=clamp(t/.35)}
    else if(mode==='glitch'){const st=Math.floor(T*24); const k=1-clamp(t/.22);
      sc.style.transform=k>0?`translateX(${((rnd(st)-.5)*80*k)|0}px)`:''; sc.style.filter=k>0?`hue-rotate(${(k*90)|0}deg) contrast(${1+k})`:'';}
    else {sc.style.opacity=1}
  }
  // VHS
  let v=sc.querySelector(':scope > .fx-vhs');
  if(sc.dataset.vhs){ if(!v){v=document.createElement('div'); v.className='fx-vhs'; sc.appendChild(v)}
    const st=Math.floor(T*12); v.style.top=((T*90)%1920)+'px'; v.style.opacity=.35+rnd(st)*.4;
    sc.style.filter=`brightness(${(1+(rnd(st+3)-.5)*.08).toFixed(3)})`; }
  // contínuos
  sc.querySelectorAll('[data-boil]').forEach((el,i)=>{el.style.filter=(el._fxFilter||'')+` url(#boil${(Math.floor(T*8)+i)%4})`});
  sc.querySelectorAll('[data-rough]:not([data-boil])').forEach(el=>{el.style.filter=(el._fxFilter||'')+' url(#boil1)'});   // borda fotocopiada parada
  sc.querySelectorAll('[data-kb],[data-drift],[data-jit]').forEach((el,i)=>{
    const p=clamp(t/dur); let tr='';
    if(el.dataset.drift){const [dx,dy]=el.dataset.drift.split(',').map(Number); tr+=`translate(${(dx*p).toFixed(1)}px,${(dy*p).toFixed(1)}px) `}
    if(el.dataset.jit){const st=Math.floor(T*12), a=+el.dataset.jit; tr+=`translate(${((rnd(st+i*5)-.5)*2*a).toFixed(1)}px,${((rnd(st+i*5+2)-.5)*2*a).toFixed(1)}px) `}
    if(el.dataset.kb){tr+=`scale(${(1+(+el.dataset.kb-1)*p).toFixed(4)})`; el.style.transformOrigin=el.dataset.kbo||'50% 50%'}
    el.style.translate='0px'; el.style.setProperty('--fx',tr);
    if(!el.dataset.a) el.style.transform=tr; else el._fxTr=tr;
  });
  // stack
  sc.querySelectorAll('.stack').forEach(el=>{
    const t0=+(el.dataset.t||0), d=+(el.dataset.d||.6); const rows=el.children, n=rows.length;
    for(let i=0;i<n;i++){rows[i].style.opacity=t>=t0+d*i/n?1:0}
    el.style.transform=`translateY(${(-(t-t0)*40).toFixed(1)}px)`; el.style.opacity=t<t0?0:1;
  });
  // karaokê
  sc.querySelectorAll('.kar').forEach(el=>{
    const pages=el._pages; let cur=-1; pages.forEach((pg,i)=>{if(t>=pg.t0) cur=i});
    pages.forEach((pg,i)=>{pg.el.style.display=i===cur?'block':'none'});
    if(cur<0) return;
    if(el.classList.contains('karfull')){ const W=pages[cur].words;   // legenda inteira visível; só a cor anda
      W.forEach((o,j)=>{ const nx=j+1<W.length?W[j+1].t:o.t+.5; o.s.style.opacity=1; o.s.className=(t>=o.t&&t<nx)?'kar-now':''; }); return; }
    pages[cur].words.forEach(o=>{ const k=t-o.t; o.s.style.opacity=k<0?0:1;
      o.s.className=k<0?'':(k<.14?'kar-now':'kar-lit'); });
  });
}
window.FX={enter,exit,frame};
})();
