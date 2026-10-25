import json, sys, urllib.request, io, numpy as np, cv2
from PIL import Image, ImageFilter
from rembg import remove, new_session
sess = new_session("u2net_human_seg")
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
T = json.load(open("tmp_v2/heads/titles.json"))
UA = {"User-Agent": "reelbot/1.0 (priscila@oakpark-construction.com)"}
for key, title in T.items():
    try:
        s = json.load(urllib.request.urlopen(urllib.request.Request(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}", headers=UA)))
        url = s.get("originalimage", s.get("thumbnail"))["source"]
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if max(im.size) > 1400: im.thumbnail((1400, 1400))
        im.save(f"tmp_v2/heads/{key}_orig.jpg", quality=88)
        g = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
        f = casc.detectMultiScale(g, 1.1, 6, minSize=(60, 60))
        cut = remove(im, session=sess)
        a = np.array(cut)
        if len(f):
            x, y, w, h = max(f, key=lambda r: r[2] * r[3])
            cx = x + w / 2
            chin = int(y + h * 1.12)
            # head-only mask: ellipse around the head, cut below chin
            m = np.zeros(a.shape[:2], np.uint8)
            cv2.ellipse(m, (int(cx), int(y + h * 0.42)), (int(w * 0.78), int(h * 0.78)), 0, 0, 360, 255, -1)
            m[chin:, :] = 0
            a[..., 3] = np.minimum(a[..., 3], m)
            box = (max(0, int(cx - w * 0.9)), max(0, int(y - h * 0.55)), min(a.shape[1], int(cx + w * 0.9)), min(a.shape[0], chin + 4))
        else:
            box = (0, 0, a.shape[1], a.shape[0])
        head = Image.fromarray(a).crop(box)
        bb = head.getbbox(); head = head.crop(bb)
        head = head.resize((600, int(600 * head.height / head.width)), Image.LANCZOS)
        pad = 30
        c = Image.new("RGBA", (head.width + 2 * pad, head.height + 2 * pad))
        c.paste(head, (pad, pad), head)
        al = c.split()[3].point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(25))
        out = Image.new("RGBA", c.size, (255, 255, 255, 0))
        out.paste(Image.new("RGBA", c.size, (255, 255, 255, 255)), (0, 0), al)
        out.alpha_composite(c)
        out.save(f"tmp_v2/heads/{key}.png")
        print(key, "ok", len(f), url)
    except Exception as e:
        print(key, "FAIL", e)
