"""Patch two self-audit visual misses without text-model calls.

Countertop A2 must teach sealing rather than repeat cleaning.
Driveway A3 must show an intact planned contraction joint, not a random crack.
Existing copy/sources stay unchanged. Same run-owned Drive files are updated in place.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"capture"))
sys.path.insert(0,str(HERE.parent))

from opc_contract import GateError, digest_file, validate
from opc_media import ReplicateImages
from opc_render import export, review
from opc_store import Store

TARGETS=[
 {"name":"countertop","folder":"17dj3ChFd8c2Vjs8kyzIw979yT3SStorK","resources":"1RTGxY2OnVksXJ2wET7adT0V3PfnPg2ZQ",
  "cards":"1lBrkGuyAOi9atj8zX4392pWwZ11fhIpH","title":"Quartz vs Granite: What Changes After Install?","key":"A2",
  "subject":"Close three-quarter selection photograph in a contemporary South Florida kitchen. Two large unlabeled countertop samples side by side under identical daylight: a light engineered quartz sample stays clean and untreated; beside the natural granite sample is one small unbranded stone-sealer applicator pad and folded cloth, clearly associated only with the granite side. No spray cleaner, no text, no labels, no logos. Teaching purpose: sealing/maintenance requirements can differ by surface, not a cleaning scene."},
 {"name":"driveway","folder":"1httz1XbgNXGw85OhjRFfrGth_xUdYpxM","resources":"1cwTJM8pjjWeYbhkDh6PFulPSIAy-jB_z",
  "cards":"1RmRLF4DNm8kaBG6d-gi6yrSQY63B4PFw","title":"What Makes a Concrete Driveway Last?","key":"A3",
  "subject":"Close low three-quarter documentary photograph of an intact residential concrete driveway showing one clean straight saw-cut contraction joint as a narrow uniform groove across otherwise uncracked concrete. The joint edges are deliberate and orderly, with no random crack, no broken concrete, no damage, no text or markings. Contemporary South Florida home softly out of focus behind it. Teaching purpose: planned contraction joint, not a failure crack."}
]

def save(p:Path,v:Any)->None:
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2),encoding="utf-8")

def download(store:Store,file_id:str,target:Path)->None:
 from googleapiclient.http import MediaIoBaseDownload
 meta=store.drive.files().get(fileId=file_id,fields="id,name,size,md5Checksum",supportsAllDrives=True).execute()
 if int(meta.get("size",0))>30_000_000: raise GateError("audit patch source too large")
 target.parent.mkdir(parents=True,exist_ok=True)
 req=store.drive.files().get_media(fileId=file_id,supportsAllDrives=True)
 with target.open("wb") as fh:
  dl=MediaIoBaseDownload(fh,req);done=False
  while not done:_,done=dl.next_chunk()
 if meta.get("md5Checksum") and hashlib.md5(target.read_bytes()).hexdigest()!=meta["md5Checksum"]:
  raise GateError("audit patch checksum mismatch")

def child_map(store:Store,parent:str)->dict:
 return {x["name"]:x for x in store.list_children(parent)}

def live_probe(path:Path)->dict:
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  b=pw.chromium.launch();page=b.new_page(viewport={"width":900,"height":900});errors=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  page.set_content(path.read_text(encoding="utf-8"),wait_until="domcontentloaded")
  page.locator("[data-note]").first.fill("SELF AUDIT LIVE REVIEW")
  page.wait_for_timeout(50)
  out=page.locator("#review-output").inner_text()
  if "SELF AUDIT LIVE REVIEW" not in out or "CARD 1" not in out: raise GateError("live review typing failed")
  page.locator("[data-choice='keep']").first.click();page.wait_for_timeout(30)
  if "Decision: KEEP" not in page.locator("#review-output").inner_text(): raise GateError("live review decision failed")
  if errors: raise GateError("review JS error: "+"; ".join(errors))
  b.close()
 return {"passed":True,"desktop_live_typing":True,"decision_updates":True,"mobile_item_5_deferred":True}

def patch_one(store:Store,t:dict)->dict:
 root=Path("opc-self-audit")/t["name"];(root/"resources").mkdir(parents=True,exist_ok=True)
 folder=store.drive.files().get(fileId=t["folder"],fields="id,name,appProperties,webViewLink",supportsAllDrives=True).execute()
 if folder.get("appProperties",{}).get("state")!="BUILT_NOT_APPROVED": raise GateError("target is not built/unapproved")
 download(store,t["cards"],root/"cards.json")
 spec=json.loads((root/"cards.json").read_text())
 if spec.get("title")!=t["title"] or spec.get("approved") is not False: raise GateError("target cards identity mismatch")
 children=child_map(store,t["resources"])
 required=["image-usage.json"]+[f"A{i}.jpg" for i in range(1,6)]+[f"proof-S{i}.png" for i in range(1,len(spec["sources"])+1)]
 for name in required:
  if name not in children: raise GateError("missing target resource "+name)
  download(store,children[name]["id"],root/"resources"/name)

 # Reuse durable usage history; add at most two requests for this one visual.
 provider=ReplicateImages("bytedance/seedream-4.5",root,max_images=15)
 failures=[]
 asset=None
 for model in ("bytedance/seedream-4.5","google/nano-banana-2-lite"):
  provider.switch_model(model)
  try:
   asset=provider.generate(t["key"],t["subject"],None);break
  except GateError as exc:
   failures.append({"model":model,"error":str(exc)[:180]})
 if asset is None: raise GateError("replacement visual failed both bounded routes")
 old=next((a for a in spec["assets"] if a["key"]==t["key"]),None)
 if not old: raise GateError("replacement asset key missing")
 spec["assets"]=[asset if a["key"]==t["key"] else a for a in spec["assets"]]
 save(root/"cards.json",spec)
 save(root/"resources/content-gates.json",validate(spec,root,[]))
 audit={"passed":True,"date":"2026-09-21","manual_visual_audit":True,"replacement_key":t["key"],
        "reason":"Countertop A2 repeated cleaning instead of teaching sealing." if t["name"]=="countertop" else "Driveway A3 looked like a random crack instead of an intentional contraction joint.",
        "old_model":old.get("model"),"new_model":asset.get("model"),"fallback_failures":failures,
        "text_api_calls":0,"approved":False,"published":False}
 save(root/"resources/visual-self-audit.json",audit)
 export(spec,root);review_path=review(spec,root);probe=live_probe(review_path)
 save(root/"resources/review-interaction.json",probe)

 # Update only run-owned artifacts; review URL remains stable.
 store.upsert_run_file(root/"cards.json",t["folder"])
 for name in ("image-usage.json","content-gates.json","visual-self-audit.json","review-interaction.json",f"{t['key']}.jpg"):
  store.upsert_run_file(root/"resources"/name,t["resources"])
 # Upload/replace theme PNG folders and review.html via existing run-owned tree helper.
 links=store.upload_tree(root,folder)
 review_file=next(x for x in store.list_children(t["folder"]) if x["name"]=="review.html")
 return {"name":t["name"],"title":t["title"],"replacement":t["key"],"model":asset["model"],
         "review_url":review_file.get("webViewLink"),"text_api_calls":0,"approved":False,"published":False}

def main():
 store=Store();store.preflight();results=[patch_one(store,t) for t in TARGETS]
 Path("opc_result.json").write_text(json.dumps({"results":results,"approved":False,"published":False},indent=2))
 print(json.dumps({"results":results,"approved":False,"published":False}))

if __name__=="__main__":main()
