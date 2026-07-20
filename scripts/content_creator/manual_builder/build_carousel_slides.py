#!/usr/bin/env python3
"""Re-render OPC addition post slides 3 (foundation) + 4 (what's next) — corrected copy, v3 lime-on-dark."""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
LIME = "#CBCC10"; CREAM = "#F0EBE3"; BLACK = "#0A0A0A"

FONT_FACES = """
@font-face{font-family:'Anton';src:url('fonts/Anton-Regular.woff2')}
@font-face{font-family:'RC';font-weight:300;src:url('fonts/RobotoCondensed-Light.woff2')}
@font-face{font-family:'RC';font-weight:400;src:url('fonts/RobotoCondensed-Regular.woff2')}
@font-face{font-family:'RC';font-weight:700;src:url('fonts/RobotoCondensed-Bold.woff2')}
@font-face{font-family:'JBM';font-weight:500;src:url('fonts/JBM-Medium.woff2')}
@font-face{font-family:'JBM';font-weight:700;src:url('fonts/JBM-Bold.woff2')}
@font-face{font-family:'Cormorant';font-style:italic;src:url('fonts/Cormorant-Italic.ttf')}
"""

BASE = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
{FONT_FACES}
.slide{{width:1080px;height:1350px;position:relative;overflow:hidden;background:{BLACK};font-family:'RC',sans-serif}}
.br{{position:absolute;width:30px;height:30px;border:3px solid {LIME}}}
.br.tl{{top:40px;left:40px;border-right:0;border-bottom:0}}
.br.tr{{top:40px;right:40px;border-left:0;border-bottom:0}}
.br.bl{{bottom:40px;left:40px;border-right:0;border-top:0}}
.br.brr{{bottom:40px;right:40px;border-left:0;border-top:0}}
.kicker{{font-family:'JBM';font-weight:500;font-size:22px;letter-spacing:.2em;color:{LIME};text-transform:uppercase}}
"""

def brackets():
    return '<div class="br tl"></div><div class="br tr"></div><div class="br bl"></div><div class="br brr"></div>'

SLIDE3 = f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE}
.photo{{position:absolute;inset:0;background:url('foundation.jpg') center 42% / cover}}
.scrim{{position:absolute;inset:0;background:linear-gradient(to bottom, rgba(10,10,10,0) 40%, rgba(10,10,10,.35) 62%, rgba(10,10,10,.92) 100%)}}
.content{{position:absolute;left:72px;right:72px;bottom:170px}}
.content h1{{font-family:'Anton';font-size:100px;line-height:.9;letter-spacing:-.01em;color:{CREAM};text-transform:uppercase;margin:16px 0 14px;text-shadow:0 4px 34px rgba(0,0,0,.55)}}
.content .sub{{font-family:'RC';font-weight:400;font-size:31px;color:{LIME};text-shadow:0 2px 14px rgba(0,0,0,.6)}}
.foot{{position:absolute;left:72px;right:72px;bottom:70px;display:flex;justify-content:space-between;align-items:center}}
.pill{{font-family:'JBM';font-weight:700;font-size:19px;letter-spacing:.12em;color:{LIME};border:2px solid {LIME};padding:12px 20px}}
.swipe{{font-family:'JBM';font-weight:700;font-size:19px;letter-spacing:.12em;color:{BLACK};background:{LIME};padding:14px 22px}}
</style></head><body>
<div class="slide"><div class="photo"></div><div class="scrim"></div>
{brackets()}
<div class="content">
  <div class="kicker">02 &middot; Current Stage &middot; July 2026</div>
  <h1>Foundation In Progress.</h1>
  <div class="sub">Layout set, forms built, rebar tied &mdash; pour comes next.</div>
</div>
<div class="foot"><div class="pill">OAK PARK &middot; CBC1263425</div><div class="swipe">SWIPE &rarr;</div></div>
</div></body></html>"""

ROWS = [("01","POUR","concrete goes down"),
        ("02","BLOCK WALLS","after cure"),
        ("03","TIE BEAM","locks it together"),
        ("04","ROOF FRAMING","the shape appears")]
rows_html = "".join(
    f'<div class="row"><div class="lft"><span class="num">{n}</span>'
    f'<span class="lbl">{lbl}</span></div><span class="hint">{h}</span></div>'
    for n,lbl,h in ROWS)

SLIDE4 = f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE}
.wrap{{position:absolute;inset:0;padding:100px 72px 80px}}
.list{{margin-top:52px}}
.row{{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(203,204,16,.35);padding:20px 2px}}
.lft{{display:flex;align-items:baseline;gap:26px}}
.num{{font-family:'JBM';font-weight:700;font-size:24px;color:{LIME}}}
.lbl{{font-family:'Anton';font-size:60px;color:{LIME};text-transform:uppercase;line-height:1}}
.hint{{font-family:'RC';font-weight:400;font-size:25px;color:{LIME};opacity:.82}}
.midline{{position:absolute;left:72px;right:110px;top:726px;font-family:'Cormorant',Georgia,serif;font-style:italic;font-size:58px;color:{CREAM};line-height:1.05}}
.brand{{position:absolute;left:72px;bottom:130px}}
.brand .logo{{display:block;width:344px;height:auto}}
.brand .handle{{font-family:'Anton';font-size:30px;color:{CREAM};text-transform:lowercase;margin-top:18px;letter-spacing:.01em}}
.lic{{position:absolute;right:72px;bottom:80px;font-family:'JBM';font-weight:500;font-size:20px;letter-spacing:.14em;color:{LIME}}}
</style></head><body>
<div class="slide">{brackets()}
<div class="wrap">
  <div class="kicker">What's Next</div>
  <div class="list">{rows_html}</div>
</div>
<div class="midline">Real progress, posted as it happens.</div>
<div class="brand">
  <img class="logo" src="logo-white.png">
  <div class="handle">@oakparkconstruction</div>
</div>
<div class="lic">LIC &middot; CBC1263425</div>
</div></body></html>"""

def render(html, name):
    p = OUT/f"{name}.html"; p.write_text(html)
    page.set_viewport_size({"width":1080,"height":1350})
    page.goto(p.as_uri())
    page.wait_for_timeout(400)
    page.locator(".slide").screenshot(path=str(OUT/f"{name}.png"))
    print("rendered", name)

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(device_scale_factor=1)
    render(SLIDE3, "3_foundation_v2")
    render(SLIDE4, "4_whats_next_v2")
    browser.close()
print("DONE")
