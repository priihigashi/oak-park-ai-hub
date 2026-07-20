#!/usr/bin/env python3
"""Rebuild the OPC addition COVER (slide 1) — split before/foundation, clean labels, v3 lime-on-dark."""
import pathlib
from playwright.sync_api import sync_playwright
OUT = pathlib.Path(__file__).parent
LIME="#CBCC10"; CREAM="#F0EBE3"; BLACK="#0A0A0A"; W,H=1080,1350
FONTS = """
@font-face{font-family:'Anton';src:url('fonts/Anton-Regular.woff2')}
@font-face{font-family:'RC';font-weight:400;src:url('fonts/RobotoCondensed-Regular.woff2')}
@font-face{font-family:'JBM';font-weight:500;src:url('fonts/JBM-Medium.woff2')}
@font-face{font-family:'JBM';font-weight:700;src:url('fonts/JBM-Bold.woff2')}
"""
HTML = f"""<!doctype html><html><head><meta charset=utf-8><style>
*{{margin:0;padding:0;box-sizing:border-box}}{FONTS}
.cov{{width:{W}px;height:{H}px;position:relative;overflow:hidden;background:{BLACK};font-family:'RC',sans-serif}}
.br{{position:absolute;width:30px;height:30px;border:3px solid {LIME}}}
.br.tl{{top:40px;left:40px;border-right:0;border-bottom:0}}.br.tr{{top:40px;right:40px;border-left:0;border-bottom:0}}
.br.bl{{bottom:40px;left:40px;border-right:0;border-top:0}}.br.brr{{bottom:40px;right:40px;border-left:0;border-top:0}}
.kick{{position:absolute;top:96px;left:72px;font-family:'JBM';font-weight:500;font-size:23px;letter-spacing:.2em;color:{LIME};text-transform:uppercase}}
.title{{position:absolute;top:132px;left:70px;right:72px;font-family:'Anton';font-size:104px;line-height:.92;letter-spacing:-.01em;text-transform:uppercase}}
.title .l{{color:{LIME}}} .title .c{{color:{CREAM}}}
.sub{{position:absolute;top:300px;left:72px;font-family:'JBM';font-weight:500;font-size:24px;letter-spacing:.16em;color:{LIME};text-transform:uppercase}}
.pair{{position:absolute;top:360px;left:72px;right:72px;height:760px;display:flex;gap:22px}}
.ph{{flex:1;position:relative;border-radius:10px;overflow:hidden;border:1px solid rgba(203,204,16,.25)}}
.ph.b{{background:url('before.jpg') center/cover}}
.ph.f{{background:url('foundation.jpg') center 42%/cover}}
.tag{{position:absolute;left:50%;transform:translateX(-50%);bottom:22px;white-space:nowrap;font-family:'JBM';font-weight:700;font-size:19px;letter-spacing:.14em;color:{LIME};background:rgba(10,10,10,.82);border:1px solid {LIME};padding:9px 18px}}
.foot{{position:absolute;left:72px;right:72px;bottom:70px;display:flex;justify-content:space-between;align-items:center}}
.lic{{font-family:'JBM';font-weight:700;font-size:19px;letter-spacing:.12em;color:{LIME}}}
.swipe{{font-family:'JBM';font-weight:700;font-size:20px;letter-spacing:.12em;color:{CREAM}}}
</style></head><body>
<div class="cov">
<div class="br tl"></div><div class="br tr"></div><div class="br bl"></div><div class="br brr"></div>
<div class="kick">Progress &middot; Oak Park Construction</div>
<div class="title"><span class="l">The</span> <span class="c">Addition</span> <span class="l">Begins</span></div>
<div class="sub">Home Addition &middot; Pompano Beach, FL</div>
<div class="pair">
  <div class="ph b"><div class="tag">BEFORE</div></div>
  <div class="ph f"><div class="tag">FOUNDATION</div></div>
</div>
<div class="foot"><div class="lic">OAK PARK &middot; CBC1263425</div><div class="swipe">SWIPE &rarr;</div></div>
</div></body></html>"""
with sync_playwright() as pw:
    b=pw.chromium.launch(); pg=b.new_page(viewport={"width":W,"height":H}, device_scale_factor=1)
    p=OUT/"cover.html"; p.write_text(HTML); pg.goto(p.as_uri()); pg.wait_for_timeout(450)
    pg.locator(".cov").screenshot(path=str(OUT/"1_cover_v2.png")); b.close()
print("COVER DONE")
