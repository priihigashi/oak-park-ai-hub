#!/usr/bin/env python3
"""Build the corrected OPC addition REEL — vertical 9:16, 4 scenes, crossfades. No 'poured'."""
import pathlib, numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import imageio_ffmpeg as iio

OUT = pathlib.Path(__file__).parent
LIME="#CBCC10"; CREAM="#F0EBE3"; BLACK="#0A0A0A"
W,H = 1080,1920

FONTS = """
@font-face{font-family:'Anton';src:url('fonts/Anton-Regular.woff2')}
@font-face{font-family:'RC';font-weight:400;src:url('fonts/RobotoCondensed-Regular.woff2')}
@font-face{font-family:'RC';font-weight:700;src:url('fonts/RobotoCondensed-Bold.woff2')}
@font-face{font-family:'JBM';font-weight:500;src:url('fonts/JBM-Medium.woff2')}
@font-face{font-family:'JBM';font-weight:700;src:url('fonts/JBM-Bold.woff2')}
"""
BASE = f"""*{{margin:0;padding:0;box-sizing:border-box}}{FONTS}
.f{{width:{W}px;height:{H}px;position:relative;overflow:hidden;background:{BLACK};font-family:'RC',sans-serif}}
.br{{position:absolute;width:34px;height:34px;border:3px solid {LIME}}}
.br.tl{{top:56px;left:56px;border-right:0;border-bottom:0}}
.br.tr{{top:56px;right:56px;border-left:0;border-bottom:0}}
.br.bl{{bottom:56px;left:56px;border-right:0;border-top:0}}
.br.brr{{bottom:56px;right:56px;border-left:0;border-top:0}}
.kick{{font-family:'JBM';font-weight:500;font-size:26px;letter-spacing:.22em;color:{LIME};text-transform:uppercase}}
"""
BR='<div class="br tl"></div><div class="br tr"></div><div class="br bl"></div><div class="br brr"></div>'
def doc(style, body):
    return f"<!doctype html><html><head><meta charset=utf-8><style>{BASE}{style}</style></head><body><div class=f>{BR}{body}</div></body></html>"

S1 = doc(f"""
.hd{{position:absolute;top:140px;left:90px;right:90px}}
.hd .t{{font-family:'Anton';font-size:112px;line-height:.9;letter-spacing:-.01em;text-transform:uppercase;margin:22px 0 20px}}
.hd .t .l{{color:{LIME}}} .hd .t .c{{color:{CREAM}}}
.hd .sub{{font-family:'JBM';font-weight:500;font-size:26px;letter-spacing:.16em;color:{LIME};text-transform:uppercase}}
.pair{{position:absolute;top:600px;left:90px;right:90px;height:960px;display:flex;gap:24px}}
.ph{{flex:1;position:relative;border-radius:12px;overflow:hidden;border:1px solid rgba(203,204,16,.25)}}
.ph.pb{{background:url('before.jpg') center/cover}}
.ph.pf{{background:url('foundation.jpg') center 42%/cover}}
.tag{{position:absolute;left:50%;transform:translateX(-50%);bottom:26px;white-space:nowrap;font-family:'JBM';font-weight:700;font-size:22px;letter-spacing:.14em;color:{LIME};background:rgba(10,10,10,.82);border:1px solid {LIME};padding:11px 20px}}
.logo{{position:absolute;left:90px;bottom:132px;width:300px}}
""", """<div class="hd"><div class="kick">Progress &middot; Oak Park Construction</div>
<div class="t"><span class="l">The</span> <span class="c">Addition</span> <span class="l">Begins</span></div>
<div class="sub">Home Addition &middot; Pompano Beach, FL</div></div>
<div class="pair"><div class="ph pb"><div class="tag">BEFORE</div></div><div class="ph pf"><div class="tag">FOUNDATION</div></div></div>
<img class="logo" src="logo-white.png">""")

S2 = doc(f"""
.photo{{position:absolute;inset:0;background:url('foundation.jpg') center 40%/cover}}
.scrim{{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(10,10,10,.18) 0%,rgba(10,10,10,0) 30%,rgba(10,10,10,.4) 62%,rgba(10,10,10,.94) 100%)}}
.c{{position:absolute;left:90px;right:90px;bottom:230px}}
h1{{font-family:'Anton';font-size:120px;line-height:.9;color:{CREAM};text-transform:uppercase;letter-spacing:-.01em;margin:18px 0 16px;text-shadow:0 4px 34px rgba(0,0,0,.6)}}
.s{{font-family:'RC';font-weight:400;font-size:39px;color:{LIME};text-shadow:0 2px 14px rgba(0,0,0,.7)}}
""", """<div class="photo"></div><div class="scrim"></div>
<div class="c"><div class="kick">02 &middot; Current Stage &middot; July 2026</div>
<h1>Foundation In Progress.</h1>
<div class="s">Layout set, forms built, rebar tied &mdash; pour comes next.</div></div>""")

SBEFORE = doc(f"""
.photo{{position:absolute;inset:0;background:url('before.jpg') center 45%/cover}}
.scrim{{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(10,10,10,.12) 0%,rgba(10,10,10,0) 32%,rgba(10,10,10,.38) 62%,rgba(10,10,10,.93) 100%)}}
.c{{position:absolute;left:90px;right:90px;bottom:230px}}
h1{{font-family:'Anton';font-size:120px;line-height:.9;color:{CREAM};text-transform:uppercase;letter-spacing:-.01em;margin:18px 0 16px;text-shadow:0 4px 34px rgba(0,0,0,.6)}}
.s{{font-family:'RC';font-weight:400;font-size:39px;color:{LIME};text-shadow:0 2px 14px rgba(0,0,0,.7)}}
""", """<div class="photo"></div><div class="scrim"></div>
<div class="c"><div class="kick">01 &middot; Before</div>
<h1>Where We Started.</h1>
<div class="s">Open side yard &mdash; the future footprint of the new addition.</div></div>""")

rows=[("01","POUR","concrete goes down"),("02","BLOCK WALLS","after cure"),("03","TIE BEAM","locks it together"),("04","ROOF FRAMING","the shape appears")]
rh="".join(f'<div class=r><div class=l><span class=n>{n}</span><span class=lb>{lb}</span></div><span class=h>{h}</span></div>' for n,lb,h in rows)
S3 = doc(f"""
.wrap{{position:absolute;inset:0;padding:160px 90px}}
.list{{margin-top:90px}}
.r{{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(203,204,16,.35);padding:44px 4px}}
.l{{display:flex;align-items:baseline;gap:34px}}
.n{{font-family:'JBM';font-weight:700;font-size:34px;color:{LIME}}}
.lb{{font-family:'Anton';font-size:90px;color:{LIME};text-transform:uppercase;line-height:1}}
.h{{font-family:'RC';font-weight:400;font-size:35px;color:{LIME};opacity:.82}}
""", f"""<div class="wrap"><div class="kick">What's Next</div><div class="list">{rh}</div></div>""")

S4 = doc(f"""
.wrap{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}}
.logo{{width:640px;margin-bottom:64px}}
.h{{font-family:'Anton';font-size:54px;color:{CREAM};text-transform:lowercase;letter-spacing:.01em}}
.cta{{font-family:'JBM';font-weight:500;font-size:28px;letter-spacing:.18em;color:{LIME};text-transform:uppercase;margin-top:44px}}
.lic{{position:absolute;left:0;right:0;bottom:130px;text-align:center;font-family:'JBM';font-weight:500;font-size:24px;letter-spacing:.16em;color:{LIME}}}
""", """<div class="wrap"><img class="logo" src="logo-white.png">
<div class="h">@oakparkconstruction</div><div class="cta">Follow the build &rarr;</div></div>
<div class="lic">LIC &middot; CBC1263425</div>""")

SCENES=[("s1",S1),("sb",SBEFORE),("s2",S2),("s3",S3),("s4",S4)]
imgs=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(); pg=b.new_page(viewport={"width":W,"height":H}, device_scale_factor=1)
    for name,html in SCENES:
        p=OUT/f"reel_{name}.html"; p.write_text(html)
        pg.goto(p.as_uri()); pg.wait_for_timeout(450)
        s=OUT/f"reel_{name}.png"; pg.locator(".f").screenshot(path=str(s))
        imgs.append(np.array(Image.open(s).convert("RGB")))
    b.close()
print("scenes rendered:", [im.shape for im in imgs])

fps=30
holds=[int(2.4*fps),int(2.7*fps),int(3.0*fps),int(3.5*fps),int(2.7*fps)]
fade=int(0.5*fps)
out=OUT/"reel_v2.mp4"
wr=iio.write_frames(str(out),(W,H),fps=fps,codec="libx264",quality=8,pix_fmt_in="rgb24",pix_fmt_out="yuv420p",macro_block_size=1)
wr.send(None)
n=len(imgs); total=0
for i in range(n):
    cur=imgs[i]
    for _ in range(holds[i]): wr.send(cur.tobytes()); total+=1
    if i<n-1:
        nxt=imgs[i+1]
        for f in range(1,fade+1):
            a=f/fade
            wr.send((cur.astype(np.float32)*(1-a)+nxt.astype(np.float32)*a).astype(np.uint8).tobytes()); total+=1
wr.close()
print(f"REEL DONE {out}  frames={total}  dur={total/fps:.1f}s")
