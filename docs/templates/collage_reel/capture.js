const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs=require('fs');
(async()=>{
  const FPS=30, DUR=72, out=process.argv[2];
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+__dirname+'/reel.html'); await p.evaluate(()=>window.READY);
  fs.writeFileSync(__dirname+'/events.json', JSON.stringify(await p.evaluate(()=>window.EVENTS)));
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out]);
  for(let f=0; f<FPS*DUR; f++){
    await p.evaluate(t=>render(t), f/FPS);
    const buf=await p.screenshot({type:'jpeg',quality:93});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if(f%300==0) console.log('frame',f);
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done');
})();
