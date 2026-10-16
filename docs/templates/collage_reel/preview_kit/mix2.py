import json,numpy as np,wave,subprocess,sys
SR=48000; TL=json.load(open('/home/claude/work/build/timeline.json')); DUR=TL[-1]['e']; N=int(SR*DUR)
ev=json.load(open('/home/claude/hub/docs/templates/collage_reel/events.json'))
rng=np.random.default_rng(5); t=np.arange(N)/SR
def rd(f):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',f,'-f','s16le','-ac','1','-ar',str(SR),'-'])
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768
voice=np.zeros(N,np.float32)
for o in TL:
    v=rd(f"/home/claude/work/ath_p/{o['id']}.wav"); i=int(o['vstart']*SR); j=min(N,i+len(v)); voice[i:j]+=v[:j-i]
voice/=np.max(np.abs(voice))/0.9
# music: warm sober pad in D minor-ish, chord changes every 4 s, soft pulse
chords=[[146.83,174.61,220.0],[116.54,146.83,174.61],[130.81,164.81,196.0],[110.0,138.59,164.81]]
mus=np.zeros(N,np.float32)
seg=4.0
for k in range(int(DUR/seg)+1):
    a=int(k*seg*SR); b=min(N,int((k+1)*seg*SR)+int(.6*SR))
    if a>=N: break
    tt=np.arange(b-a)/SR; c=chords[k%4]
    s=sum(np.sin(2*np.pi*f*tt)+.35*np.sin(2*np.pi*2*f*tt+.4)+.15*np.sin(2*np.pi*f*1.003*tt) for f in c)/3
    e=np.minimum(1,tt/1.2)*np.minimum(1,(len(tt)/SR-tt)/.6)
    mus[a:b]+=(s*e*.10).astype(np.float32)
# soft heartbeat-ish pulse every 0.75 s
beat=.75; kn=int(.25*SR); tk=np.arange(kn)/SR; kick=(np.sin(2*np.pi*(48+40*np.exp(-tk*25))*tk)*np.exp(-tk*12)).astype(np.float32)
x=2.0
while x<DUR-2:
    i=int(x*SR); j=min(N,i+kn); mus[i:j]+=kick[:j-i]*.16; x+=beat
mus*=np.minimum(1,t/2.0).astype(np.float32); mus[-int(2*SR):]*=np.linspace(1,0,int(2*SR)).astype(np.float32)
# sfx
sfx=np.zeros(N,np.float32)
def add(tm,sig,g):
    i=int(tm*SR); j=min(N,i+len(sig))
    if 0<=i<N: sfx[i:j]+=sig[:j-i]*g
def lp(x,a):
    y=np.zeros_like(x)
    for i in range(1,len(x)): y[i]=y[i-1]+a*(x[i]-y[i-1])
    return y
n=int(.3*SR); wh=lp(rng.normal(0,1,n).astype(np.float32),.2)*np.sin(np.linspace(0,np.pi,n))**2
n=int(.8*SR); tt=np.arange(n)/SR; thud=(np.sin(2*np.pi*(45+60*np.exp(-tt*20))*tt)*np.exp(-tt*5)*1.4).astype(np.float32)
n=int(.2*SR); tt=np.arange(n)/SR; slap=(rng.normal(0,1,n)*np.exp(-tt*50)+np.sin(2*np.pi*90*tt)*np.exp(-tt*18)).astype(np.float32)
n=int(.08*SR); tt=np.arange(n)/SR; pop=(np.sin(2*np.pi*(700+900*tt/.08)*tt)*np.exp(-tt*40)).astype(np.float32)
for s in ev['whoosh'][1:]: add(s-.06,wh,.22)
for s in ev['thud']: add(s,thud,.55)
for s in ev['slap']: add(s,slap,.25)
for s in ev['pop']: add(s,pop,.07)
for a,b in ev['tick']:
    x=a
    while x<b: add(x,(rng.normal(0,1,int(.01*SR))*.5).astype(np.float32),.12); x+=1/16
# ducking music under voice
env=np.abs(voice); k=int(.15*SR); env=np.convolve(env,np.ones(k)/k,'same'); duck=1-0.62*np.clip(env/0.05,0,1)
mix=voice*1.0+mus*duck*0.9+sfx*0.8
mix=np.tanh(mix*1.05); mix/=np.max(np.abs(mix))/0.95
st=np.stack([mix,mix],1)
with wave.open('/home/claude/work/audio2.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())
print('ok',DUR)
