const { chromium } = require('playwright-core'); const C=require('@sparticuz/chromium'); const fs=require('fs');
(async()=>{const out=process.argv[3]; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:await C.executablePath(),args:C.args});
const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:2/3});
await p.goto('file://'+process.argv[2]); await p.waitForTimeout(1500);
await p.addStyleTag({content:'.safe,.kar,.srcline,#foot,#grain,.shadeX{display:none!important}'});
await p.evaluate(()=>{window.__ZLIVE=true});
for(let k=0;k<=73;k++){await p.evaluate(t=>render(t),k/24);await p.screenshot({path:`${out}/f${String(k).padStart(3,'0')}.jpg`,type:'jpeg',quality:78});}
await b.close()})();
