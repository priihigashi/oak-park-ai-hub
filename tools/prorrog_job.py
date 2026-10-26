import asyncio, json, os, sys, urllib.request, urllib.parse, io
import edge_tts

OUT = "out"
os.makedirs(OUT, exist_ok=True)
job = json.load(open("job.json", encoding="utf-8"))

async def tts(key, text, voice, rate):
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    audio = bytearray(); words = []
    async for ch in com.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            words.append({"w": ch["text"], "s": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
    open(f"{OUT}/{key}.mp3", "wb").write(audio)
    json.dump(words, open(f"{OUT}/{key}.json", "w", encoding="utf-8"), ensure_ascii=False)

async def main():
    for s in job["scenes"]:
        for attempt in range(3):
            try:
                await tts(s["id"], s["text"], job["voice"], job["rate"]); break
            except Exception as e:
                print("tts retry", s["id"], e)
                await asyncio.sleep(3)
asyncio.run(main())

UA = {"User-Agent": "Mozilla/5.0 (oak-park-ai-hub reel job)"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=40).read()

os.makedirs(f"{OUT}/raw", exist_ok=True)
for p in job["people"]:
    data = None
    for wiki in p.get("wiki", []):
        try:
            lang, title = wiki.split(":", 1)
            api = f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&piprop=original&titles=" + urllib.parse.quote(title)
            js = json.loads(get(api))
            for pg in js["query"]["pages"].values():
                src = pg.get("original", {}).get("source")
                if src:
                    data = get(src); print("wiki ok", p["id"], src); break
            if data: break
        except Exception as e:
            print("wiki fail", p["id"], e)
    if not data:
        for h in p.get("x", []):
            for u in [f"https://unavatar.io/x/{h}?fallback=false", f"https://unavatar.io/twitter/{h}?fallback=false"]:
                try:
                    data = get(u); print("avatar ok", p["id"], u); break
                except Exception as e:
                    print("avatar fail", p["id"], u, e)
            if data: break
    if data:
        open(f"{OUT}/raw/{p['id']}.jpg", "wb").write(data)

# cutouts: rembg + head-only crop using mediapipe
from PIL import Image, ImageFilter
from rembg import remove, new_session
import numpy as np
sess = new_session("isnet-general-use")
try:
    import mediapipe as mp
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
except Exception as e:
    print("mediapipe missing", e); fm = None
os.makedirs(f"{OUT}/heads", exist_ok=True)
for fn in os.listdir(f"{OUT}/raw"):
    pid = fn.rsplit(".", 1)[0]
    try:
        im = Image.open(f"{OUT}/raw/{fn}").convert("RGB")
        if max(im.size) > 1600:
            im.thumbnail((1600, 1600))
        cut = remove(im, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240,
                     alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
        arr = np.array(cut)
        if fm is not None:
            res = fm.process(np.array(im))
            if res.multi_face_landmarks:
                lm = res.multi_face_landmarks[0].landmark
                W, H = im.size
                chin = lm[152].y * H; top = lm[10].y * H
                lx, rx = lm[234].x * W, lm[454].x * W
                cut_y = int(chin + (chin - top) * 0.06)
                # remove everything below jaw line (curve from ear to chin)
                yy, xx = np.mgrid[0:H, 0:W]
                cx = (lx + rx) / 2; half = max(1, (rx - lx) / 2)
                jaw = cut_y - (1 - np.clip(((xx - cx) / half) ** 2, 0, 1)) * 0 - np.clip(np.abs(xx - cx) - half * 0.55, 0, None) * 0.9
                arr[..., 3] = np.where(yy > jaw, 0, arr[..., 3])
        a = Image.fromarray(arr)
        alpha = a.split()[3].filter(ImageFilter.GaussianBlur(1.2))
        a.putalpha(alpha)
        bb = a.getbbox()
        if bb: a = a.crop(bb)
        a.thumbnail((700, 700))
        a.save(f"{OUT}/heads/{pid}.png")
        print("head ok", pid, a.size)
    except Exception as e:
        print("head fail", pid, e)
