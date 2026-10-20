// node capture.js <saida.mp4> [pagina.html] [fps]   — render quadro a quadro; DUR vem da página (window.DUR)
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs=require('fs'); const path=require('path');
(async()=>{
  const out=process.argv[2], page=path.resolve(process.argv[3]||path.join(__dirname,'reel.html')), FPS=+(process.argv[4]||30);
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'}).catch(()=>chromium.launch());
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+page); await p.evaluate(()=>window.READY); const DUR=await p.evaluate(()=>window.DUR);
  fs.writeFileSync(path.join(path.dirname(page),'events.json'), JSON.stringify(await p.evaluate(()=>window.EVENTS)));
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out]);
  for(let f=0; f<FPS*DUR; f++){
    await p.evaluate(t=>render(t), f/FPS);
    const buf=await p.screenshot({type:'jpeg',quality:93});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if(f%300==0) console.log('frame',f,'/',FPS*DUR);
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done',out);
})();
