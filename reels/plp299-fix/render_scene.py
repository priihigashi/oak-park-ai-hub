import sys, os, json, subprocess, http.server, threading, functools
from playwright.sync_api import sync_playwright
ROOT = sys.argv[1]; LAB = sys.argv[2]; OUT = sys.argv[3]
FPS = 30; SPEED = 1.15
LIMIT = int(sys.argv[4]) if len(sys.argv) > 4 else None
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]
SETUP = r"""
(lab)=>{
 window.requestAnimationFrame=()=>0; for(let i=1;i<100000;i++){clearInterval(i)}
 document.querySelectorAll('audio').forEach(a=>{a.pause();a.muted=true});
 const st=document.getElementById('stage'); const w=document.getElementById('wrap');
 w.style.width='1080px'; w.style.maxWidth='none'; st.style.transform='scale(1)';
 [...st.children].forEach(c=>{ if(!c.classList.contains('sc') && !c.classList.contains('paper') && !c.classList.contains('paperL') && c.id!=='cap' && !c.querySelector('#cap')) { const t=(c.textContent||''); if(t.includes('não sai no vídeo')||t.includes('só esta cena')) c.style.display='none'; } });
 document.querySelectorAll('div').forEach(d=>{ if(d.childElementCount===0 && /não sai no vídeo|só esta cena/.test(d.textContent||'')) d.style.display='none'; });
 const sc=[...document.querySelectorAll('.sc')].find(s=>s.dataset.lab===lab);
 window.__t0=+sc.dataset.t0; window.__t1=+sc.dataset.t1; window.__seen=new Map();
 return [window.__t0, window.__t1];
}"""
STEP = r"""
([v,vt])=>{
 window.render(v);
 document.querySelectorAll('.kb').forEach(k=>{const s=k.closest('.sc');const on=v>=+s.dataset.t0&&v<+s.dataset.t1; const e=on?Math.min(1,((v-(+s.dataset.t0))/1.15)/8):0; k.style.transition='none'; k.style.transform='scale('+(1+0.08*e)+')';});
 document.body.offsetHeight;
 for(const a of document.getAnimations()){
   if(!window.__seen.has(a)) window.__seen.set(a, vt);
   a.pause();
   const ms=(vt-window.__seen.get(a))*1000;
   try{a.currentTime=ms}catch(e){}
 }
 return 1;
}"""
os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1200, 'height': 2100}, device_scale_factor=1)
    pg.goto(f'http://127.0.0.1:{port}/index.html'); pg.wait_for_timeout(2500)
    t0, t1 = pg.evaluate(SETUP, LAB)
    pg.wait_for_timeout(300)
    n = round((t1 - t0) / SPEED * FPS)
    if LIMIT: n = min(n, LIMIT)
    st = pg.query_selector('#stage')
    for f in range(n):
        vt = f / FPS
        v = t0 + vt * SPEED + 0.0005
        pg.evaluate(STEP, [v, vt])
        st.screenshot(path=f'{OUT}/f{f:05d}.jpg', type='jpeg', quality=92)
        if f % 150 == 0: print(LAB, f, '/', n, flush=True)
    b.close()
json.dump({'t0': t0, 't1': t1, 'frames': n}, open(f'{OUT}/meta.json', 'w'))
