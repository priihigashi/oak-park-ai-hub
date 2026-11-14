import json,re,html,sys,unicodedata
P='/home/claude/v2/duv/'
W=json.load(open(sys.argv[1])); rot=open(sys.argv[2]).read()
def n(s): return re.sub(r'[^a-z0-9%]','',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode())
segs=[re.sub(r'^\[\d+\]\s*','',l) for l in rot.strip().split('\n') if l.strip()]
SEG=[];pos=0
for s in segs:
    toks=[n(x) for x in s.split() if n(x)][:3]
    for i in range(pos,len(W)-2):
        if [n(W[i]['w']),n(W[i+1]['w']),n(W[i+2]['w'])]==toks: SEG.append(i);pos=i+1;break
    else: raise SystemExit('seg nao achado: '+s[:40])
stoks=[x for x in re.sub(r'\[\d+\]','',rot).split() if n(x)]
ends=set()
if len(stoks)==len(W):
    for i,x in enumerate(stoks):
        if x[-1] in '.?!:': ends.add(i)
else: print('AVISO tokens', len(stoks), len(W))
if len(stoks)==len(W):
    for i,x in enumerate(stoks): W[i]['w']=x
# caption pages: 2 lines, ~30 chars each, break at sentence end or pause
pages=[];cur=[[]];ln=0
def flush():
    global cur
    lines=[l for l in cur if l]
    if lines: pages.append(lines)
    cur=[[]]
for i,w in enumerate(W):
    L=cur[-1]; txt=' '.join(W[j]['w'] for j in L)
    if len(txt)+len(w['w'])+1>30 and L:
        if len(cur)==2: flush()
        else: cur.append([])
    cur[-1].append(i)
    gap = W[i+1]['t']-(w['t']+w['d']) if i+1<len(W) else 9
    if (i+1 in SEG) or gap>0.45 or i in ends: flush()
flush()
merged=[]
for p in pages:
    flat=[i for l in p for i in l]
    if merged and len(flat)<3 and flat[0] not in SEG and merged[-1][-1] and [i for l in merged[-1] for i in l][-1] not in ends:
        prev=[i for l in merged[-1] for i in l]
        if len(' '.join(W[j]['w'] for j in prev+flat))<=64: merged[-1]=[prev,flat] if False else [prev+flat[:0],flat]; merged[-1]=[prev+flat,[]] ; continue
    merged.append(p)
pages=[]
for p in merged:
    flat=[i for l in p for i in l]
    if len(' '.join(W[j]['w'] for j in flat))>30: pages.append([flat[:1],flat[1:]])
    else: pages.append([flat])
fixed=[]
for p in pages:
    flat=[i for l in p for i in l]
    if fixed and len(flat)==1:
        prev=[i for l in fixed[-1] for i in l]
        if len(prev)>=4 and prev[-1] not in ends and prev[-1]+1 not in SEG:
            fixed[-1]=[prev[:-2]]; flat=prev[-2:]+flat
    fixed.append([flat])
pages=[]
for p in fixed:
    flat=p[0]
    if len(' '.join(W[j]['w'] for j in flat))>30: pages.append([flat[:1],flat[1:]])
    else: pages.append([flat])
# balance 2 lines
bal=[]
for p in pages:
    if len(p)==2:
        allw=p[0]+p[1];best=None
        for k in range(1,len(allw)):
            a=' '.join(W[j]['w'] for j in allw[:k]);b=' '.join(W[j]['w'] for j in allw[k:])
            sc=abs(len(a)-len(b))+ (99 if max(len(a),len(b))>34 else 0)
            if best is None or sc<best[0]: best=(sc,k)
        p=[allw[:best[1]],allw[best[1]:]]
    bal.append({'t0':W[p[0][0]]['t'],'t1':W[p[-1][-1]]['t']+W[p[-1][-1]]['d'],'lines':p})
t=open(P+'template.html').read()
info='<div class="box"><h3>Roteiro (narração)</h3><pre>'+html.escape(rot)+'</pre></div>'+open('/home/claude/v2/info_duv.html').read()
t=t.replace('__SCENES__',open(P+'scenes.html').read()).replace('__WORDS__',json.dumps(W,ensure_ascii=False)).replace('__SEG__',json.dumps(SEG)).replace('__CAPS__',json.dumps(bal))
t=t.replace('__LEG__',html.escape(open(P+'leg.txt').read())).replace('__COM__',html.escape(open(P+'com.txt').read())).replace('__ORIG__',html.escape(open('/home/claude/v2/orig.txt').read())).replace('__INFO__',info)
open(P+'index.html','w').write(t); print('ok',len(SEG),len(bal), 'dur', W[-1]['t'])
