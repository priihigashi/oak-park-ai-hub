#!/usr/bin/env python3
"""Fetch a single public Instagram carousel via Apify, export images and OCR.
GitHub token is never printed; outputs are scoped to a run artifact only.
"""
import json, os, pathlib, re, sys, time
from urllib.parse import urlparse
import requests
from PIL import Image, ImageEnhance, ImageOps
import pytesseract

url = pathlib.Path("requests/instagram/DeUVhP7EdMC.txt").read_text().strip()
assert re.fullmatch(r"https://(www\\.)?instagram\\.com/p/[a-zA-Z0-9_-]+/?",url), "Invalid post URL"
token = os.getenv("APIFY_API_KEY")
if not token: sys.exit("APIFY_API_KEY not configured in this workflow environment")
out = pathlib.Path("carousel-output")
out.mkdir(exist_ok=True)
s = requests.Session()
s.headers["Authorization"]="Bearer "+token
base = "https://api.apify.com/v2"
input_data = {"directUrls":[url],"resultsType":"posts","resultsLimit":1}
resp = s.post(base+"/acts/apify~instagram-scraper/runs",json=input_data,timeout=60)
if not resp.ok: sys.exit("Apify start failed: HTTP "+str(resp.status_code))
runid = resp.json()["data"]["id"]
print("Apify run ID:",runid,flush=True)
status="RUNNING"; dataset_id=None
for i in range(40):
    r=s.get(base+"/actor-runs/"+runid,timeout=40)
    r.raise_for_status()
    data=r.json().get("data",{})
    status=data.get("status","UNKNOWN")
    dataset_id=data.get("defaultDatasetId")
    if status in ("SUCCEEDED","FAILED","ABORTED","TIMED-OUT"):break
    time.sleep(7)
print("Apify status:",status,flush=True)
if status!="SUCCEEDED" or not dataset_id: sys.exit("Actor incomplete: "+status)
q=s.get(base+"/datasets/"+dataset_id+"/items",params={"limit":5,"clean":"true"},timeout=60)
q.raise_for_status()
items=q.json()
if not items:sys.exit("Actor returned no post items")
p=next((x for x in items if x.get("shortCode")=="DeUVhP7EdMC"),items[0])
(out/"post.json").write_text(json.dumps(p,ensure_ascii=False,indent=2))
print("Username:",p.get("ownerUsername",p.get("username","unknown")))
print("Caption:",str(p.get("caption",""))[:3000],flush=True)
links=[]
def add(v):
    if isinstance(v,str) and v.startswith("https://"): links.append(v)
    if isinstance(v,dict):
        for field in ("url","imageUrl","displayUrl","src"):
            if isinstance(v.get(field),str) and v[field].startswith("https://"): links.append(v[field]);break
for field in ("images","imageUrls","sidecarImages","childPosts","carouselMedia","media"):
    val=p.get(field) or []
    if isinstance(val,list):
        for x in val:add(x)
if not links:add(p.get("displayUrl"))
links=list(dict.fromkeys(links))
(out/"image_links.txt").write_text("\n".join(links))
print("Image URLs:",len(links),flush=True)
texts=[]
for i,link in enumerate(links[:20],1):
    try:
        if urlparse(link).scheme!="https":continue
        rr=requests.get(link,timeout=40)
        rr.raise_for_status()
        if len(rr.content)>20000000:continue
        fn=out/f"slide-{i:02d}.img"
        fn.write_bytes(rr.content)
        im=Image.open(fn).convert("RGB")
        im=ImageEnhance.Contrast(ImageOps.contain(im,(2400,3400))).enhance(1.6)
        t=pytesseract.image_to_string(im,lang="por+eng").strip()
        texts.append({"slide":i,"text":t})
        print(f"---SLIDE {i}---\n{t[:4500]}\n---END SLIDE---",flush=True)
    except Exception as e:print("Slide",i,"failed:",type(e).__name__,flush=True)
(out/"ocr.json").write_text(json.dumps(texts,ensure_ascii=False,indent=2))
print("Completed with",len(texts),"downloaded slides",flush=True)
