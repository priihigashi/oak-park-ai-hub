import os, subprocess, glob, requests, time, json, io
from PIL import Image
os.makedirs("job/refs", exist_ok=True)
URLS = {"antidoto1": "https://www.instagram.com/reel/DfpK21XRzPD/", "antidoto2": "https://www.instagram.com/reel/DfcI2Auxa1z/", "ref3": "https://www.instagram.com/p/De9f9xygFTW/"}
for k, u in URLS.items():
    r = subprocess.run(["yt-dlp", "-f", "mp4/best", "-o", f"/tmp/{k}.%(ext)s", u], capture_output=True, text=True)
    print(k, r.returncode, r.stderr[-400:], flush=True)
    f = glob.glob(f"/tmp/{k}.*")
    if not f:
        continue
    os.makedirs(f"/tmp/fr_{k}", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-i", f[0], "-vf", "select='gt(scene,0.25)',scale=240:-2", "-vsync", "vfr", f"/tmp/fr_{k}/s%03d.jpg"])
    subprocess.run(["ffmpeg", "-y", "-i", f[0], "-vf", "fps=1/1.5,scale=240:-2", f"/tmp/fr_{k}/t%03d.jpg"])
    ims = sorted(glob.glob(f"/tmp/fr_{k}/t*.jpg"))[:40]
    if ims:
        a = [Image.open(x) for x in ims]; w, h = a[0].size; cols = 8; rows = (len(a) + cols - 1) // cols
        S = Image.new("RGB", (cols * w, rows * h), "white")
        for i, im in enumerate(a):
            S.paste(im, ((i % cols) * w, (i // cols) * h))
        S.save(f"job/refs/{k}_sheet.jpg", quality=72)
    subprocess.run(["ffmpeg", "-y", "-i", f[0], "-vf", "scale=-2:480", "-c:v", "libx264", "-crf", "30", "-preset", "veryfast", "-c:a", "aac", "-b:a", "64k", f"job/refs/{k}_480.mp4"])
# free photo of Fernando Haddad for the 3D head (Agência Brasil, CC BY)
H = {"User-Agent": "reel-research/1.0 (priscila@oakpark-construction.com)"}
r = requests.get("https://commons.wikimedia.org/w/api.php", params={"action": "query", "generator": "search", "gsrsearch": "Fernando Haddad 2023 filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 5, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 900, "format": "json"}, headers=H, timeout=30).json()
cands = []
for p in r.get("query", {}).get("pages", {}).values():
    ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
    cands.append({"t": p["title"], "url": ii.get("thumburl"), "page": ii["descriptionurl"], "lic": m.get("LicenseShortName", {}).get("value")})
json.dump(cands, open("job/refs/haddad_cands.json", "w"), indent=1)
from rembg import remove, new_session
s = new_session("u2net_human_seg")
for i, c in enumerate(cands[:3]):
    b = requests.get(c["url"], headers=H, timeout=60).content
    im = Image.open(io.BytesIO(b)).convert("RGB")
    out = remove(im, session=s)
    out.save(f"job/refs/haddad{i}.png")
