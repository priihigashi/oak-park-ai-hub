import asyncio,os,subprocess,json
from playwright.async_api import async_playwright
from spin import ang,DUR,FPS
T=json.load(open('spin_ticks.json'))['ticks']
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch();pg=await br.new_page(viewport={'width':1080,'height':1350})
        await pg.goto('file://'+os.path.abspath('crimeta_video.html')+'?export');await pg.wait_for_selector('html[data-ready]')
        await pg.evaluate("""(()=>{const s=document.querySelector('#s1');document.querySelectorAll('#deck>.slide').forEach(e=>{if(e!==s)e.style.display='none'});s.style.cssText+='position:fixed;left:0;top:0';document.body.style.overflow='hidden';
          document.getAnimations().forEach(a=>{a.pause();a.currentTime=0});const g=s.querySelector('g.spin');g.style.animation='none';g.style.transformBox='view-box';
          window.__g=g;window.__p=[...s.querySelectorAll('g[transform]')].find(e=>e.getAttribute('transform')=='translate(540 498)');})()""")
        ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','p1spin.mkv'],stdin=subprocess.PIPE)
        for n in range(int(DUR*FPS)):
            t=n/FPS;a=ang(t)
            last=max([x for x in T if x<=t],default=-9);fl=-18*max(0,1-(t-last)/0.08) if t-last<0.08 else 0
            await pg.evaluate(f"(()=>{{__g.style.transform='rotate({a}deg)';__g.style.transformOrigin='540px 738px';__p.setAttribute('transform','translate(540 498) rotate({fl})');document.getAnimations().forEach(x=>{{x.pause();x.currentTime={t*1000}}})}})()")
            ff.stdin.write(await pg.screenshot(type='jpeg',quality=92,clip={'x':0,'y':0,'width':1080,'height':1350}))
        ff.stdin.close();ff.wait();await br.close()
asyncio.run(main())
