const { chromium } = require('playwright');
(async()=>{
  const times=process.argv.slice(3).map(Number); const out=process.argv[2];
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'}).catch(()=>chromium.launch());
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+__dirname+'/reel.html'); await p.evaluate(()=>window.READY);
  for(const t of times){ await p.evaluate(t=>render(t),t); await p.screenshot({path:`${out}/s_${String(t).padStart(5,'0')}.jpg`,type:'jpeg',quality:80}); }
  await b.close();
})();
