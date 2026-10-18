// node capseg.js <saida.mp4> <pagina.html> <frameIni> <frameFim> [fps]
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const path=require('path');
(async()=>{
  const [out,pg,a,z]=process.argv.slice(2), FPS=+(process.argv[6]||30);
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+path.resolve(pg)); await p.evaluate(()=>window.READY); await p.waitForTimeout(1500);
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out]);
  for(let f=+a; f<+z; f++){
    await p.evaluate(t=>render(t), f/FPS);
    const buf=await p.screenshot({type:'jpeg',quality:92});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done',out);
})();
