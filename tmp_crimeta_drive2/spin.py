import math,json
FPS=30;DUR=7.6
SP=[(0.4,3.4,2*360+22.5*3),(4.0,7.0,2*360+22.5*5)]  # (início, fim, graus)
def ease(x):return 1-(1-x)**3.2
def ang(t):
    a=0
    for s,e,d in SP:
        if t>=e:a+=d
        elif t>s:a+=d*ease((t-s)/(e-s))
    return a
ticks=[];prev=0
for n in range(int(DUR*1000)):
    t=n/1000;a=ang(t)
    if int(a//22.5)!=int(prev//22.5):ticks.append(t)
    prev=a
json.dump({'ticks':ticks,'stops':[e for s,e,d in SP]},open('spin_ticks.json','w'))
print(len(ticks))
