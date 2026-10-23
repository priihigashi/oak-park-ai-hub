import asyncio,os,sys,subprocess
from playwright.async_api import async_playwright
a,b,out=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3]
FPS=30
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch();pg=await br.new_page(viewport={'width':1080,'height':1350})
        await pg.goto('file://'+os.path.abspath('crimeta_video.html')+'?export');await pg.wait_for_selector('html[data-ready]')
        await pg.evaluate("document.body.style.overflow='hidden';document.querySelectorAll('.slide:not(#stage)').forEach(e=>{if(!e.closest('#stage'))e.style.display='none'});document.getElementById('stage').style.cssText+='position:fixed;left:0;top:0'")
        ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
        n0,n1=int(a*FPS),int(b*FPS)
        for n in range(n0,n1):
            t=n/FPS
            await pg.evaluate(f"(()=>{{render({t});document.getAnimations().forEach(x=>{{x.pause();x.currentTime={t*1000}}})}})()")
            ff.stdin.write(await pg.screenshot(type='jpeg',quality=92,clip={'x':0,'y':0,'width':1080,'height':1350}))
        ff.stdin.close();ff.wait();await br.close()
asyncio.run(main())
