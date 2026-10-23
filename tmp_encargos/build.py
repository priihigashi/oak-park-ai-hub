import asyncio, json, io, os, traceback
os.makedirs("out", exist_ok=True)
job = json.load(open("job.json", encoding="utf8"))
log = []
import edge_tts
async def tts():
    for t in job.get("tts", []):
        try:
            c = edge_tts.Communicate(t["text"], job["voice"], rate=job["rate"], boundary="WordBoundary")
            words = []
            with open(f"out/{t['name']}.mp3", "wb") as fh:
                async for ch in c.stream():
                    if ch["type"] == "audio": fh.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        words.append({"t": ch["offset"]/1e7, "d": ch["duration"]/1e7, "w": ch["text"]})
            json.dump(words, open(f"out/{t['name']}.json", "w"), ensure_ascii=False)
            log.append(f"tts ok {t['name']} {len(words)}")
        except Exception as e:
            log.append(f"tts FAIL {t['name']}: {e}")
if job.get("tts"): asyncio.run(tts())

if job.get("faces"):
    import requests, numpy as np
    from PIL import Image, ImageFilter
    from rembg import remove, new_session
    import mediapipe as mp
    H = {"User-Agent": "reel-bot/1.0 (contact: priscila@oakpark-construction.com)"}
    sess = new_session("isnet-general-use")
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
    for f in job["faces"]:
        try:
            url = f.get("url")
            if not url:
                s = requests.get(f"https://pt.wikipedia.org/api/rest_v1/page/summary/{f['wiki']}", headers=H, timeout=30).json()
                url = s.get("originalimage", {}).get("source") or s["thumbnail"]["source"]
            im = Image.open(io.BytesIO(requests.get(url, headers=H, timeout=60).content)).convert("RGB")
            if max(im.size) > 1600: im.thumbnail((1600, 1600))
            im.save(f"out/{f['name']}_orig.jpg", quality=90)
            cut = remove(im, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240,
                         alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
            arr = np.array(cut)
            res = fm.process(np.array(im))
            if res.multi_face_landmarks:
                lm = res.multi_face_landmarks[0].landmark
                W, Hh = im.size
                P = lambda i: (lm[i].x * W, lm[i].y * Hh)
                chin = P(152); L = P(234); R = P(454); top = P(10)
                fh_ = chin[1] - top[1]
                off = 0.05 * fh_
                ys = np.arange(Hh)[:, None]; xs = np.arange(W)[None, :]
                # jaw curve: parabola through L, chin(+off), R
                cx, cy = chin[0], chin[1] + off
                a = ((L[1] - cy) / max((L[0] - cx) ** 2, 1) + (R[1] - cy) / max((R[0] - cx) ** 2, 1)) / 2
                curve = cy + a * (xs - cx) ** 2
                mask = (ys > curve) & (ys > min(L[1], R[1]))
                arr[..., 3][mask] = 0
                x0 = int(max(0, L[0] - 0.35 * (R[0] - L[0]))); x1 = int(min(W, R[0] + 0.35 * (R[0] - L[0])))
                y0 = int(max(0, top[1] - 0.75 * fh_)); y1 = int(min(Hh, cy + 0.04 * fh_))
                arr = arr[y0:y1, x0:x1]
            out = Image.fromarray(arr)
            a = out.split()[3].filter(ImageFilter.GaussianBlur(1.2)); out.putalpha(a)
            bb = out.getbbox(); out = out.crop(bb) if bb else out
            out.save(f"out/{f['name']}.png")
            log.append(f"face ok {f['name']} {out.size}")
        except Exception as e:
            log.append(f"face FAIL {f['name']}: {e} {traceback.format_exc()[-300:]}")
open("out/_log.txt", "w").write("\n".join(log)); print("\n".join(log))
