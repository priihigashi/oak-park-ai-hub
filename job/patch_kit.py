import sys,os
D=sys.argv[1]
R={
'template.html':[
 ('#topline{left:108px;right:108px;top:96px','#topline{left:108px;right:108px;top:176px'),
 ('#vbox{left:108px;top:158px','#vbox{left:108px;top:236px'),
 ('#vbox{left:108px;top:236px;width:864px;height:520px}','#vbox{left:108px;top:236px;width:864px;height:540px}'),
 ('#score{left:108px;right:108px;top:730px}','#score{left:108px;right:108px;top:840px}'),
 ('#panel{left:108px;width:864px;top:902px;height:446px}','#panel{left:108px;width:864px;top:1000px;height:460px}'),
 ('#cap{left:108px;right:150px;top:1404px','#cap{left:108px;right:150px;top:1500px'),
 ('#handle{left:0;right:0;top:1626px','#handle{left:0;right:0;top:1690px'),
 ('#src{left:108px;right:108px;top:1668px','#src{left:108px;right:108px;top:1734px'),
 ('.ch-rep{background:#fff;color:var(--ink);border-color:var(--ink)}','.ch-rep{background:#fff;color:#141416;border-color:#141416}'),
],
'audit.py':[('1360','1472')],
'make_page.py':[('top:1626px','top:1690px')],
}

R['template.html']+= [
 ('<div id="phone"><div id="stage"','<div id="phone"><video id="mp4" playsinline preload="auto" hidden></video><div id="stage"'),
 ("const aud=$('#aud'),","const MP4='__MP4__';const mp4el=document.getElementById('mp4');if(MP4){mp4el.src=MP4;mp4el.hidden=false;document.getElementById('stage').style.display='none'}\nconst aud=MP4?mp4el:$('#aud'),"),
 ("function loop(){render(aud.currentTime);requestAnimationFrame(loop)}","function loop(){if(MP4){$('#seek').value=Math.round(aud.currentTime/D.total*1000);$('#time').textContent=fmt(aud.currentTime)+' / '+fmt(D.total)}else render(aud.currentTime);requestAnimationFrame(loop)}"),
 ("#phone{position:relative;","#mp4{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:5;background:#000}\n#phone{position:relative;"),
 ("if(!vid.seeking&&(lastClip!==s.key||(drift>0.6&&performance.now()-lastSeek>1500)))","if(!vid.seeking&&(lastClip!==s.key||(drift>1.2&&performance.now()-lastSeek>3000)))"),
]
R['make_page.py']+= [(".replace('__BG__',os.environ.get('BG','branco'))",".replace('__BG__',os.environ.get('BG','branco')).replace('__MP4__',os.environ.get('MP4',''))")]
R['render.py']=[("%1384","%NF"),("D=json.load(open('data.json'));FPS=30","D=json.load(open('data.json'));FPS=30\nimport glob;NF=len(glob.glob('fr/*.jpg'))")]
R['recut.py']=[('crop=540:404:0:4,delogo=x=426:y=150:w=96:h=34','delogo=x=426:y=150:w=96:h=34,crop=540:480:0:20,split[a][b];[a]scale=768:480:force_original_aspect_ratio=increase,crop=768:480,boxblur=20:2,eq=brightness=-0.08[bg];[bg][b]overlay=(W-w)/2:0')]

for f,reps in R.items():
    p=os.path.join(D,f)
    if not os.path.exists(p): print('nofile',f); continue
    s=open(p).read()
    for a,b in reps:
        if a in s: s=s.replace(a,b)
        else: print('MISS',f,a[:50])
    open(p,'w').write(s); print('ok',f)
