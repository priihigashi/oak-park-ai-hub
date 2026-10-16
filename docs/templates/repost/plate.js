// node plate.js specs.json outdir  → <id>.png por spec + slots.json {id:{x,y,w,h}}
const {chromium}=require('playwright'); const fs=require('fs'), path=require('path');
(async()=>{
  const specs=JSON.parse(fs.readFileSync(process.argv[2],'utf8')); const out=process.argv[3]; fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
  const page='file://'+path.join(__dirname,'plate.html'); const slots={};
  for(const s of specs){
    await p.goto(page+'?spec='+encodeURIComponent(JSON.stringify(s)));
    await p.evaluate(()=>window.READY); await p.waitForTimeout(80);
    slots[s.id]=await p.evaluate(()=>window.SLOT);
    await p.screenshot({path:path.join(out,s.id+'.png'),omitBackground:s.mode==='lt'});
  }
  fs.writeFileSync(path.join(out,'slots.json'),JSON.stringify(slots,null,1)); await b.close();
})();
