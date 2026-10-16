// node svg2png.js in.svg out.png [largura]  — rasteriza emoji/ícone SVG grande (para linescreen.py / silhuetas)
const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{const [i,o,w='1200']=process.argv.slice(2); const svg=fs.readFileSync(i,'utf8');
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'}).catch(()=>chromium.launch());
 const p=await b.newPage({viewport:{width:+w,height:+w}}); await p.setContent(`<body style="margin:0;background:transparent">${svg.replace('<svg','<svg width="'+w+'" height="'+w+'"')}</body>`);
 await p.screenshot({path:o,omitBackground:true}); await b.close();})();
