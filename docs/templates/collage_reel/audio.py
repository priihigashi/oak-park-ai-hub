import json, numpy as np, wave, sys
SR=48000; DUR=float(sys.argv[3]) if len(sys.argv)>3 else 72.0;  # python3 audio.py events.json out.wav [duração]
N=int(SR*DUR)
rng=np.random.default_rng(3)
ev=json.load(open(sys.argv[1]))
mus=np.zeros(N); sfx=np.zeros(N)
def add(buf,t,sig,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i<N: buf[i:j]+=sig[:j-i]*g
def env(n,a=.005,r=None):
    t=np.arange(n)/SR; e=np.ones(n); na=int(a*SR); e[:na]=np.linspace(0,1,na)
    if r: e*=np.exp(-t/r)
    return e
def lp(x,k):  # simple one-pole lowpass
    y=np.zeros_like(x); a=k
    for i in range(1,len(x)): y[i]=y[i-1]+a*(x[i]-y[i-1])
    return y
# --- music: 100 bpm, A minor
bpm=100; beat=60/bpm
kick_n=int(.35*SR); tk=np.arange(kick_n)/SR
kick=np.sin(2*np.pi*(50+90*np.exp(-tk*30))*tk)*np.exp(-tk*9)
hat=rng.normal(0,1,int(.05*SR)); hat=np.diff(hat,prepend=0)*np.exp(-np.arange(len(hat))/SR*90)
bassnotes=[55.0,55.0,43.65,49.0]  # A1 A1 F1 G1 per bar
def tone(f,d,dec=3.0,harm=(1,.5,.25)):
    n=int(d*SR); t=np.arange(n)/SR
    s=sum(a*np.sin(2*np.pi*f*(k+1)*t) for k,a in enumerate(harm))
    return s*env(n,.01)*np.exp(-t*dec)
arp=[220,261.63,329.63,261.63, 174.61,220,261.63,220, 196,246.94,293.66,246.94]
quiet=[(60.5,61.6),(71.0,72)]
def in_quiet(t): return any(a<=t<b for a,b in quiet)
t=0.0; b=0
while t<DUR-1.0:
    bar=(b//4)%4
    if not in_quiet(t):
        sect_intense = 1.0 if (19<=t<44 or 61.6<=t<66) else .7
        if t>=3.4: add(mus,t,kick,.55*sect_intense)
        add(mus,t+beat/2,hat,.10)
        if b%4==0: add(mus,t,tone(bassnotes[bar],beat*4,dec=.6,harm=(1,.3,.1)),.35)
        if t>=6:
            for k in range(2):
                f=arp[((b*2+k)%12)]
                add(mus,t+k*beat/2,tone(f*2,beat/2,dec=7,harm=(1,.2)),.07)
    t+=beat; b+=1
# drone pad
tt=np.arange(N)/SR
pad=(np.sin(2*np.pi*110*tt)+.6*np.sin(2*np.pi*164.81*tt+.3)+.4*np.sin(2*np.pi*220.5*tt))*.04
padenv=np.clip(tt/2,0,1);
for a,bq in quiet: padenv[int(a*SR):int(bq*SR)]*=.15
mus+=pad*padenv
# riser before verdict
rn=int(2.0*SR); rt=np.arange(rn)/SR
riser=rng.normal(0,1,rn)*np.linspace(0,1,rn)**2
riser=lp(riser,.08)*1.4 + np.sin(2*np.pi*(200+600*rt**2)*rt)*np.linspace(0,.15,rn)
add(sfx,58.5,riser,.5)
# --- sfx
def whoosh():
    n=int(.28*SR); x=rng.normal(0,1,n); x=lp(x,.25); e=np.sin(np.linspace(0,np.pi,n))**2; return x*e
def slap():
    n=int(.22*SR); t=np.arange(n)/SR; x=rng.normal(0,1,n)*np.exp(-t*45)+np.sin(2*np.pi*90*t)*np.exp(-t*18)*1.2; return x
def thud():
    n=int(.9*SR); t=np.arange(n)/SR; x=np.sin(2*np.pi*(45+60*np.exp(-t*20))*t)*np.exp(-t*4.5)*1.6+lp(rng.normal(0,1,n),.3)*np.exp(-t*25); return x
def pop():
    n=int(.09*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*(700+900*t/.09)*t)*np.exp(-t*40)
def click():
    n=int(.012*SR); return rng.normal(0,1,n)*np.exp(-np.arange(n)/SR*600)
for s in ev['whoosh'][1:]: add(sfx,max(0,s-.06),whoosh(),.35)
for s in ev['slap']: add(sfx,s,slap(),.45)
for s in ev['thud']: add(sfx,s,thud(),.9)
for s in ev['pop']: add(sfx,s,pop(),.12)
def zap():  # glitch digital (repertório 01): bitcrush + ruído picotado
    n=int(.16*SR); t=np.arange(n)/SR; x=np.sign(np.sin(2*np.pi*(1800-9000*t)*t))*(rng.random(n)>.35)
    x=np.repeat(x[::24],24)[:n]; return x*np.exp(-t*14)*.6
for s in ev.get('glitch',[]): add(sfx,s,zap(),.22)
for a,bq in ev['tick']:
    x=a
    while x<bq: add(sfx,x,click(),.25); x+=1/16
mix=mus*.8+sfx
# soft clip + normalize
mix=np.tanh(mix*1.2); mix/=np.max(np.abs(mix))/0.89
fade=int(.8*SR); mix[-fade:]*=np.linspace(1,0,fade)
st=np.stack([mix,mix],1)
with wave.open(sys.argv[2],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())
print('ok')
