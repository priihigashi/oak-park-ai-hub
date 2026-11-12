import json, os, re, time, io, requests
from PIL import Image
from rembg import remove, new_session

H = {"User-Agent": "midterms-reel-research/1.0 (priscila@oakpark-construction.com)"}
CROPS={"mamdani":(560,340,880,1440),"elsayed":(500,120,1030,455)}
ONLY=["bottoms2","hinojosa2"]
FILES = {
 "talarico": "File:James Talarico Open Congress Austin 2023.jpg",
 "bottoms2": "File:Keisha Lance Bottoms 2019.jpg",
 "hinojosa2": "File:Gina Hinojosa 16 February 2017 (cropped).jpg",
 "talarico2": "File:James Talarico Press Conference (cropped).jpg",
 "hinojosa": "File:Gina Hinojosa at the AFL-CIO COPE convention in 2024.jpg",
 "elsayed": "File:Abdul El-Sayed meet-and-greet by Conlan Houston 10.jpg",
 "andrews": "File:Annie Andrews at Gas, Grits and Groceries Tour in Abbeville (2026) (cropped).jpg",
 "jackson": "File:Troy Jackson in the Senate Chamber (cropped).jpg",
 "colom": "File:Scott Colom 2 (cropped).png",
 "bottoms": "File:Keisha Lance Bottoms in 2025.jpg",
 "mamdani": "File:Zohran Mamdani Campaigning in Flushing.jpg",
 "peltola": "File:Mary Peltola Congressional Member Portrait (2).jpeg",
 "turek": "File:Joshua Turek (cropped).jpg",
 "cooper": "File:Roy Cooper at Roy Cooper Rally April 2026-1.jpg",
 "brown": "File:Sherrod Brown official photo 2009.jpg",
 "hamilton": "File:Adam Hamilton campaign rally, Newton, Kansas, 30 Oct 2026.jpg",
 "kiros": "File:Melat Kiros Portrait (cropped).jpg",
 "aoc": "File:Alexandria Ocasio-Cortez Official Portrait.jpg",
 "moody": "File:Senator Ashley Moody from Florida.jpg",
 "donalds": "File:Rep. Byron Donalds official photo, 117th Congress.jpg",
 "philscott": "File:Phil Scott 2019 (3x4 cropped).png",
 "sullivan": "File:Senator Dan Sullivan official.jpg",
 "abbott": "File:Greg Abbott by Gage Skidmore.jpg",
 "paxton": "File:Ken Paxton 2024 (cropped).jpg",
 "collins": "File:Sen Susan Collins official.jpg",
 "hydesmith": "File:Cindy Hyde-Smith official photo (cropped).jpg",
 "chiproy": "File:Chip Roy, official portrait, 116th Congress (cropped 2).jpg",
}
os.makedirs("job/out", exist_ok=True)
sess = new_session("birefnet-portrait")
meta = {}
for k, t in [(k,FILES[k]) for k in ONLY]:
    for a in range(4):
        r = requests.get("https://commons.wikimedia.org/w/api.php", params={"action": "query", "titles": t, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1100, "format": "json"}, headers=H, timeout=30)
        if r.status_code == 200:
            break
        time.sleep(5)
    p = list(r.json()["query"]["pages"].values())[0]
    ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
    url = ii.get("thumburl") or ii["url"]
    for a in range(4):
        b = requests.get(url, headers=H, timeout=60)
        if b.status_code == 200:
            break
        time.sleep(5)
    img = Image.open(io.BytesIO(b.content)).convert("RGB")
    img.save(f"job/out/{k}_orig.jpg", quality=80)
    if k in CROPS: img = img.crop(CROPS[k])
    cut = remove(img, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
    bb = cut.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    if bb:
        cut = cut.crop(bb)
    h = 640
    if cut.height > h:
        cut = cut.resize((round(cut.width * h / cut.height), h), Image.LANCZOS)
    cut.save(f"job/out/{k}.webp", "WEBP", quality=78, method=6)
    meta[k] = {"title": t, "page": ii["descriptionurl"], "license": m.get("LicenseShortName", {}).get("value"), "artist": re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()[:80], "w": cut.width, "h": cut.height}
    print(k, meta[k]["license"], cut.size, flush=True)
    time.sleep(1)
old=json.load(open("job/out/meta.json"));old.update(meta);json.dump(old, open("job/out/meta.json", "w"), indent=1)
