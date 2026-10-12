// node snap.js <pasta> <t1> <t2> ...   (PAGE=outra.html node snap.js ...)
const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{
  const out=process.argv[2]; const times=process.argv.slice(3).map(Number); fs.mkdirSync(out,{recursive:true});
  const page=path.resolve(process.env.PAGE||path.join(__dirname,'reel.html'));
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'}).catch(()=>chromium.launch());
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>console.error('PAGEERROR',e.message));
  await p.goto('file://'+page); await p.evaluate(()=>window.READY);
  for(const t of times){ await p.evaluate(t=>render(t),t); await p.screenshot({path:`${out}/s_${String(t).padStart(5,'0')}.jpg`,type:'jpeg',quality:80}); }
  await b.close();
})();
