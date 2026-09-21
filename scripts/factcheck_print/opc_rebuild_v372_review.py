"""Rebuild v372 review.html with the current review UI only.

No text/image generation. Downloads the existing v372 cards, rendered PNGs and
proof screenshots, regenerates review.html with current opc_render.review(), and
replaces only the existing review file after run identity checks.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'capture'))
sys.path.insert(0,str(HERE.parent))

from opc_contract import GateError
from opc_render import review
from opc_store import Store

FOLDER_ID="1gnjGkxUF9i9XT6NZFCs9Qnyh-mhxSw6j"
RUN_KEY="pr300-paint-owner-revision-20260921"
REVIEW_ID="1XbEXQbM8hVG7mevyW-LtSiBP5dz2zIDZ"


def one(store:Store,parent:str,name:str)->dict:
    found=[x for x in store.list_children(parent) if x["name"]==name]
    if len(found)!=1:
        raise GateError(f"Expected exactly one {name}")
    return found[0]


def download(store:Store,file:dict,target:Path)->None:
    from googleapiclient.http import MediaIoBaseDownload
    meta=store.drive.files().get(fileId=file["id"],fields="id,size,md5Checksum",supportsAllDrives=True).execute()
    target.parent.mkdir(parents=True,exist_ok=True)
    request=store.drive.files().get_media(fileId=file["id"],supportsAllDrives=True)
    with target.open("wb") as stream:
        dl=MediaIoBaseDownload(stream,request);done=False
        while not done:_,done=dl.next_chunk()
    if int(meta.get("size",-1))!=target.stat().st_size:
        raise GateError("Review source size mismatch")
    if meta.get("md5Checksum") and hashlib.md5(target.read_bytes()).hexdigest()!=meta["md5Checksum"]:
        raise GateError("Review source checksum mismatch")


def materialize(store:Store,root:Path)->dict:
    import json
    cards=one(store,FOLDER_ID,"cards.json")
    download(store,cards,root/"cards.json")
    spec=json.loads((root/"cards.json").read_text(encoding="utf-8"))
    png=one(store,FOLDER_ID,"png")
    for theme in ("dark","cream","lime"):
        folder=one(store,png["id"],theme)
        for i in range(1,len(spec["slides"])+1):
            name=f"card_{i:02d}.png"
            download(store,one(store,folder["id"],name),root/"png"/theme/name)
    resources=one(store,FOLDER_ID,"resources")
    for source in spec["sources"]:
        rel=Path(source["screenshot"])
        download(store,one(store,resources["id"],rel.name),root/rel)
    return spec


def main()->None:
    store=Store()
    folder=store.drive.files().get(fileId=FOLDER_ID,fields="id,appProperties",supportsAllDrives=True).execute()
    props=folder.get("appProperties",{})
    if props.get("opcPrintRun")!=RUN_KEY or props.get("state")!="OWNER_REVISION_READY_NOT_APPROVED":
        raise GateError("v372 identity/state mismatch")
    current=store.drive.files().get(fileId=REVIEW_ID,fields="id,name,parents,mimeType",supportsAllDrives=True).execute()
    if current.get("name")!="review.html" or current.get("parents")!=[FOLDER_ID] or current.get("mimeType")!="text/html":
        raise GateError("v372 review target mismatch")
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        spec=materialize(store,root)
        path=review(spec,root)
        result=store.upsert_run_file(path,FOLDER_ID)
        check=store.drive.files().get(fileId=REVIEW_ID,fields="id,size,md5Checksum,modifiedTime",supportsAllDrives=True).execute()
        if result["id"]!=REVIEW_ID or int(check.get("size",0))!=path.stat().st_size:
            raise GateError("v372 review replacement readback mismatch")
    print({"status":"review_ui_rebuilt","review_id":REVIEW_ID,"approved":False,"published":False})


if __name__=="__main__":
    main()
