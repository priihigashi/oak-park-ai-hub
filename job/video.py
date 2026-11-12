import os, subprocess, requests, time, glob, json
from PIL import Image
from rembg import remove, new_session

H = {"User-Agent": "midterms-reel-research/1.0 (priscila@oakpark-construction.com)"}
T = "File:National Run for Office Day 2018- Sherrod Brown.webm"
os.makedirs("job/vid", exist_ok=True)
r = requests.get("https://commons.wikimedia.org/w/api.php", params={"action": "query", "titles": T, "prop": "imageinfo", "iiprop": "url|extmetadata", "format": "json"}, headers=H, timeout=30).json()
ii = list(r["query"]["pages"].values())[0]["imageinfo"][0]
url = ii["url"]
open("job/vid/meta.json", "w").write(json.dumps({"title": T, "page": ii["descriptionurl"], "license": ii["extmetadata"].get("LicenseShortName", {}).get("value")}))
for a in range(4):
    b = requests.get(url, headers=H, timeout=120)
    if b.status_code == 200:
        break
    time.sleep(10)
open("/tmp/src.webm", "wb").write(b.content)
# low-res preview of the whole clip (to pick segments + transcription)
subprocess.run(["ffmpeg", "-y", "-i", "/tmp/src.webm", "-vf", "scale=-2:360", "-c:v", "libvpx-vp9", "-b:v", "300k", "-c:a", "libopus", "-b:a", "48k", "job/vid/full_360.webm"], check=True)
subprocess.run(["ffmpeg", "-y", "-i", "/tmp/src.webm", "-vn", "-ac", "1", "-ar", "16000", "job/vid/audio16k.wav"], check=True)
# frames of first 24 s at 15 fps, 720 tall
os.makedirs("/tmp/fr", exist_ok=True); os.makedirs("/tmp/co", exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-i", "/tmp/src.webm", "-t", "24", "-vf", "fps=15,scale=-2:720", "/tmp/fr/%04d.png"], check=True)
s = None
for a in range(5):
    try:
        s = new_session("birefnet-portrait"); break
    except Exception as e:
        print("retry", e); time.sleep(30)
for f in sorted(glob.glob("/tmp/fr/*.png")):
    im = Image.open(f).convert("RGB")
    out = remove(im, session=s)
    out.save("/tmp/co/" + os.path.basename(f))
    print(f, flush=True)
subprocess.run(["ffmpeg", "-y", "-framerate", "15", "-i", "/tmp/co/%04d.png", "-i", "/tmp/src.webm", "-map", "0:v", "-map", "1:a", "-t", "24", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "900k", "-auto-alt-ref", "0", "-c:a", "libopus", "-b:a", "64k", "job/vid/brown_cut.webm"], check=True)
subprocess.run(["ffmpeg", "-y", "-i", "/tmp/co/0010.png", "job/vid/frame10.png"], check=True)
