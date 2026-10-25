import json, urllib.request, io
from PIL import Image
from rembg import remove, new_session
sess = new_session("u2net_human_seg")
T = json.load(open("tmp_v2/heads/titles.json"))
UA = {"User-Agent": "reelbot/1.0 (priscila@oakpark-construction.com)"}
for key, title in T.items():
    try:
        s = json.load(urllib.request.urlopen(urllib.request.Request(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}", headers=UA)))
        url = s.get("originalimage", s.get("thumbnail"))["source"]
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if max(im.size) > 1200: im.thumbnail((1200, 1200))
        im.save(f"tmp_v2/heads/{key}_orig.jpg", quality=88)
        remove(im, session=sess).save(f"tmp_v2/heads/{key}_cut.png")
        print(key, "ok", url, flush=True)
    except Exception as e:
        print(key, "FAIL", e, flush=True)
