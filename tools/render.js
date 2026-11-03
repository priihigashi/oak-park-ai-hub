const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
(async()=>{const J=JSON.parse(fs.readFileSync('render_job.json'));const FPS=30;const N=J.n,I=+process.env.I;
const TF=Math.round(J.total*FPS);const i0=Math.floor(TF*I/N),i1=Math.floor(TF*(I+1)/N);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
await p.goto('http://localhost:8799/'+J.file);await p.waitForTimeout(3000);
await p.evaluate(()=>{window.MANUAL=true;try{au.pause()}catch(e){};const st=document.getElementById('st');document.body.innerHTML='';document.body.style.margin=0;document.body.style.background='#000';document.body.appendChild(st);st.style.transform='none';st.style.position='relative'});
const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-r',String(FPS),'chunk.mp4'],{stdio:['pipe','inherit','inherit']});
const t0=Date.now();
for(let i=i0;i<i1;i++){await p.evaluate(async t=>{window.seek(t);const vs=[...document.querySelectorAll('.sc.on video[data-clip]')];await Promise.all(vs.map(v=>v.seeking?new Promise(r=>{const to=setTimeout(r,1500);v.addEventListener('seeked',()=>{clearTimeout(to);r()},{once:true})}):0));if(vs.length)await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))},i/FPS);
 const buf=await p.screenshot({type:'jpeg',quality:93});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
 if((i-i0)%600===0)console.log(I,i-i0,'/',i1-i0,((Date.now()-t0)/1000).toFixed(0)+'s');}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done',((Date.now()-t0)/1000).toFixed(0)+'s')})();
