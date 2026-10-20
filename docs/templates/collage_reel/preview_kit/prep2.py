import json,subprocess,re
U=json.load(open('/home/claude/work/athena_urls.json'))
out=[];T=0.0
ids=["v01","v02","v03","v04","v05","v06","v07","v07b","v08","v09","v10","v11","v12"]
for n,i in enumerate(ids):
    f=f'/home/claude/work/ath_p/{i}.wav'
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
    # detect internal silences to anchor sentence starts
    log=subprocess.run(['ffmpeg','-i',f,'-af','silencedetect=n=-38dB:d=0.12','-f','null','-'],capture_output=True,text=True).stderr
    ends=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',log)]
    text=U[i]['text']; words=text.split()
    # split into sentences/clauses at punctuation
    groups=[];cur=[]
    for w in words:
        cur.append(w)
        if re.search(r'[.:;?!,]$',w): groups.append(cur);cur=[]
    if cur: groups.append(cur)
    # assign group starts: first at 0, then use silence ends if count matches roughly, else proportional
    total=sum(len(''.join(g)) for g in groups)
    starts=[];acc=0
    for g in groups:
        starts.append(acc/total*d); acc+=len(''.join(g))+1
    # snap starts to nearest silence end within 0.6s
    for k in range(1,len(starts)):
        c=[e for e in ends if abs(e-starts[k])<0.6]
        if c: starts[k]=min(c,key=lambda e:abs(e-starts[k]))
    wl=[]
    for k,g in enumerate(groups):
        s0=starts[k]; s1=starts[k+1] if k+1<len(groups) else d
        L=sum(len(w)+1 for w in g); a=0
        for w in g:
            wl.append((w,s0+(s1-s0)*a/L)); a+=len(w)+1
    pre=0.15; post=1.2 if n==len(ids)-1 else (2.0 if i=='v11' else (1.2 if i=='v10' else 0.3))
    dur=pre+d+post
    out.append({"id":i,"s":round(T,3),"e":round(T+dur,3),"vstart":round(T+pre,3),"vdur":d,"words":[(w,round(pre+t,3)) for w,t in wl]})
    T+=dur
json.dump(out,open('timeline.json','w'),ensure_ascii=False,indent=1)
print(round(T,2))
