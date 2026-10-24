import sys,os,re
D=sys.argv[1]
def ed(f,fn):
    p=os.path.join(D,f); s=open(p).read(); n=fn(s); open(p,'w').write(n); print('ok',f, 'changed' if n!=s else 'same')
def tpl(s):
    s=re.sub(r'#topline\{left:108px;right:108px;top:\d+px','#topline{left:108px;right:108px;top:170px',s)
    s=re.sub(r'#vbox\{left:108px;top:\d+px;width:864px;height:\d+px\}','#vbox{left:108px;top:226px;width:864px;height:540px}',s)
    s=re.sub(r'#score\{left:108px;right:108px;top:\d+px\}','#score{left:108px;right:108px;top:822px}',s)
    s=re.sub(r'#panel\{left:108px;width:864px;top:\d+px;height:\d+px\}','#panel{left:108px;width:864px;top:976px;height:434px}',s)
    s=re.sub(r'#cap\{left:108px;right:150px;top:\d+px','#cap{left:108px;right:150px;top:1436px',s)
    s=re.sub(r'#handle\{left:0;right:0;top:\d+px','#handle{left:0;right:0;top:1650px',s)
    s=re.sub(r'#src\{left:108px;right:108px;top:\d+px','#src{left:108px;right:108px;top:1694px',s)
    a="const chip=$('#spkchip');if(s.type==='clip'&&s.spk==='reporter')"
    b="const chip=$('#spkchip');const cs=s.type==='clip'?s:(lastClipBefore(t)||D.segs.find(x=>x.type==='clip'));if(cs&&cs.spk==='reporter')"
    s=s.replace(a,b); print('chip', b in s, 'mp4', "__MP4__" in s, 'rep', '.ch-rep{background:#fff;color:#141416' in s)
    return s
ed('template.html',tpl)
ed('audit.py',lambda s:re.sub(r'\b1(360|472)\b','1422',s))
ed('make_page.py',lambda s:re.sub(r'top:1(626|690|712)px','top:1650px',s))
