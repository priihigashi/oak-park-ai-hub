import subprocess, sys, os, re, json, glob
os.makedirs('out/clip', exist_ok=True)
log=[]
def sh(c):
    r=subprocess.run(c,shell=True,capture_output=True,text=True); log.append('$ '+c[:150]+'\n'+(r.stdout[-800:]+r.stderr[-1500:])); return r
sh('pip install -q -U yt-dlp')
def t2s(t):
    h,m,s=t.replace(',','.').split(':'); return int(h)*3600+int(m)*60+float(s)
found=None
for vid in ['j4cghMn_i_k','N6f6L80pXns']:
    for client in ['default','mweb','tv','web_safari']:
        ea='' if client=='default' else f'--extractor-args "youtube:player_client={client}"'
        r=sh(f'yt-dlp {ea} --skip-download --write-auto-subs --write-subs --sub-langs "pt.*" --convert-subs srt -o "out/clip/{vid}.%(ext)s" https://www.youtube.com/watch?v={vid}')
        subs=glob.glob(f'out/clip/{vid}*.srt')
        if subs: break
    if not subs: continue
    txt=open(subs[0]).read()
    blocks=re.split(r'\n\n+',txt)
    hits=[]
    for b in blocks:
        m=re.search(r'(\d\d:\d\d:\d\d[,.]\d+) --> (\d\d:\d\d:\d\d[,.]\d+)',b)
        if m and re.search(r'vingan',b,re.I): hits.append(t2s(m.group(1)))
    log.append(f'{vid} hits {hits}')
    if hits:
        found=(vid,hits[0],ea); break
if found:
    vid,t,ea=found; a=max(0,t-25); b=t+25
    sh(f'yt-dlp {ea} -f "bv*[height<=720]+ba/b[height<=720]/b" --download-sections "*{a}-{b}" --force-keyframes-at-cuts --merge-output-format mp4 -o "out/clip/mae_raw.%(ext)s" https://www.youtube.com/watch?v={vid}')
    json.dump({'vid':vid,'t':t,'a':a},open('out/clip/info.json','w'))
open('out/log.txt','w').write('\n'.join(log)[-20000:]); print('\n'.join(log)[-6000:])
