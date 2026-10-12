/* engine.js — motor da Colagem Jornalística (extraído do reel.html v1, mesmo comportamento).
   Página define antes:  window.DUR = <segundos>;  (e qualquer gerador de elementos, ex. buildCols)
   Opcional: <script src="fx.js"></script> antes deste arquivo para o repertório extra.
   Expõe: window.render(T), window.EVENTS (para audio.py), window.READY, window.DUR. */
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const E={out:t=>1-Math.pow(1-t,3),back:t=>{const c1=2.0,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2)},
  bounce:t=>{const n=7.5625,d=2.75;if(t<1/d)return n*t*t;if(t<2/d)return n*(t-=1.5/d)*t+.75;if(t<2.5/d)return n*(t-=2.25/d)*t+.9375;return n*(t-=2.625/d)*t+.984375}};
const rnd=s=>{const x=Math.sin(s*12.9898+78.233)*43758.5453;return x-Math.floor(x)};
const fmt=(v,dec)=>v.toFixed(dec).replace('.',',');
const DUR=window.DUR||72;
const scenes=[...document.querySelectorAll('.scene')];
const EVENTS={whoosh:[],thud:[],slap:[],tick:[],pop:[],glitch:[]};
scenes.forEach(sc=>{
  const s=+sc.dataset.s; if(sc.dataset.in==='glitch') EVENTS.glitch.push(s); else EVENTS.whoosh.push(s);
  sc.querySelectorAll('[data-a]').forEach(el=>{
    const t=s+(+el.dataset.t||0), d=+(el.dataset.d||.4), a=el.dataset.a;
    if(a==='stamp') EVENTS.thud.push(t+d); else if(a==='slam') EVENTS.slap.push(t+d*.8); else if(a==='pop'||a==='drop') EVENTS.pop.push(t+d*.6);
    else if(a==='glitch') EVENTS.glitch.push(t);
  });
  sc.querySelectorAll('.cnt').forEach(el=>{const t=s+(+el.dataset.t),d=+el.dataset.d; EVENTS.tick.push([t,t+d]);});
});
window.EVENTS=EVENTS;

function anim(el,t,T,idx){
  const a=el.dataset.a, t0=+(el.dataset.t||0), d=+(el.dataset.d||.4), r0=+(el.dataset.r||0);
  const c={o:1,tx:0,ty:0,sc:1,r:r0,filter:'',clip:''};
  if(a){
    if(t<t0){el.style.opacity=0;return}
    const p=clamp((t-t0)/d);
    switch(a){
      case 'slam': {const q=E.back(p); c.sc=1.9-.9*q; c.o=clamp(p*4); c.r=r0+(1-q)*-6; break}
      case 'pop': {c.sc=E.back(p); c.o=clamp(p*3); break}
      case 'stamp': {const q=E.out(p); c.sc=2.8-1.8*q; c.o=clamp(p*3); break}
      case 'up': c.ty=(1-E.out(p))*110; c.o=p; break;
      case 'left': c.tx=(1-E.out(p))*-140; c.o=p; break;
      case 'fade': c.o=clamp((t-t0)/(+(el.dataset.d||.35))); break;
      case 'drop': c.ty=-(1-E.bounce(p))*1100; c.o=clamp(p*5); break;
      default: if(window.FX) FX.enter(a,p,el,t,c);
    }
    const to=el.dataset.o;
    if(to!==undefined){const q=clamp((t-+to)/(+(el.dataset.od||.22))); if(q>=1){el.style.opacity=0;return}
      if(!(window.FX&&el.dataset.out&&FX.exit(el.dataset.out,q,el,t,c))){c.o*=1-q; c.sc*=1-.25*q; c.ty-=q*60;}}
  }
  if(el.dataset.bob){ // stop-motion jitter @12fps + gentle bob
    const step=Math.floor(T*12); c.ty+=Math.sin(T*2*Math.PI/1.4+idx)*7; c.r+= (rnd(step*7+idx)-.5)*1.4;
  }
  el.style.opacity=c.o;
  el.style.transform=`translate(${c.tx}px,${c.ty}px) rotate(${c.r}deg) scale(${c.sc}) ${el._fxTr||''}`;
  el._fxFilter=c.filter; if(!el.dataset.boil&&!el.dataset.rough) el.style.filter=c.filter; el.style.clipPath=c.clip||'';
}
function render(T){
  let shake=0; let theme='dark';
  scenes.forEach(sc=>{
    const s=+sc.dataset.s,e=+sc.dataset.e, vis=T>=s&&T<e; sc.style.display=vis?'block':'none'; if(!vis)return;
    theme=sc.dataset.theme; const t=T-s;
    if(!sc.dataset.in||sc.dataset.in==='wipe'){ // entry wipe (paper slide) first .18s
      const w=clamp(t/.18); sc.style.clipPath= w<1?`inset(${(1-E.out(w))*100}% 0 0 0)`:'none';}
    if(window.FX) FX.frame(sc,t,T,e-s);
    sc.querySelectorAll('[data-a]').forEach((el,i)=>{anim(el,t,T,i);
      if(el.dataset.shake){const land=+el.dataset.t+(+el.dataset.d||.4); const k=t-land; if(k>=0&&k<.35) shake=Math.max(shake,(1-k/.35)*14*(+el.dataset.shake));}});
    sc.querySelectorAll('.el[data-bob]:not([data-a])').forEach((el,i)=>anim(el,t,T,i));
    sc.querySelectorAll('.cnt').forEach(el=>{
      const p=clamp((t-+el.dataset.t)/+el.dataset.d); const v=+el.dataset.from+(+el.dataset.to-+el.dataset.from)*E.out(p);
      if(el.dataset.o&&t>=+el.dataset.o){el.style.opacity=Math.max(0,1-(t-+el.dataset.o)/.22)}else el.style.opacity=t<+el.dataset.t?0:1; el.textContent=(el.dataset.pre||'')+fmt(v,+el.dataset.dec)+(el.dataset.suf||'');
      if(el.dataset.shakeEnd){const k=t-(+el.dataset.t+ +el.dataset.d); if(k>=0&&k<.35) shake=Math.max(shake,(1-k/.35)*16);}
    });
    sc.querySelectorAll('.bar').forEach(el=>{const p=clamp((t-+el.dataset.t)/+el.dataset.d); el.style.width=(E.out(p)*+el.dataset.to)+'px'});
    sc.querySelectorAll('.col').forEach(el=>{const p=E.out(clamp((t-+el.dataset.t)/+el.dataset.d)); const v=+el.dataset.v, k=+el.dataset.k, base=+el.dataset.base;
      const h=Math.abs(v)*k*p; el.style.height=Math.max(h,0)+'px'; el.style.top=(v>=0?base-h:base)+'px'; if(v<0) el.style.background='#ff6b5e';});
  });
  const st=document.getElementById('stage'); const sx=(rnd(Math.floor(T*30))-.5)*2*shake, sy=(rnd(Math.floor(T*30)+99)-.5)*2*shake;
  st.style.transform=`translate(${sx}px,${sy}px)`;
  const pi=document.querySelector('#prog i'); if(pi) pi.style.width=(T/DUR*100)+'%';
  const dark=theme==='dark'; const pr=document.getElementById('prog'); if(pr) pr.className=dark?'':'dark';
  ['foot','tick'].forEach(id=>{const n=document.getElementById(id); if(n) n.style.color=dark?'#F2ECE0':'#0E0D0B'});
  const g=document.getElementById('grain'); if(g) g.style.transform=`translate(${(rnd(Math.floor(T*12))*40)|0}px,${(rnd(Math.floor(T*12)+5)*40)|0}px)`;
}
window.render=render; window.DUR=DUR;
window.READY=Promise.all([document.fonts.ready,...[...document.images].map(i=>i.complete?1:new Promise(r=>{i.onload=i.onerror=r}))]);
render(0);
if(!navigator.webdriver){let t0=performance.now();(function loop(){render(((performance.now()-t0)/1000)%DUR);requestAnimationFrame(loop)})()}
