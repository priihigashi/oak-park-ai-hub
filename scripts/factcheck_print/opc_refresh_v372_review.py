"""Rebuild only the v372 paint review HTML with the current live-review UI.

No image/text generation and no content changes. The existing cards and rendered
PNGs are downloaded, the review wrapper is regenerated, interaction-probed on a
desktop browser, and the same Drive review.html is replaced in place.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"capture"))
sys.path.insert(0,str(HERE.parent))

from opc_contract import GateError
from opc_curated_batch import download_drive, review_probe
from opc_render import review
from opc_store import Store

FOLDER_ID="1gnjGkxUF9i9XT6NZFCs9Qnyh-mhxSw6j"
RUN_KEY="pr300-paint-owner-revision-20260921"
REVIEW_ID="1XbEXQbM8hVG7mevyW-LtSiBP5dz2zIDZ"


def one_child(store: Store, parent: str, name: str, folder: bool | None=None) -> dict:
    matches=[f for f in store.list_children(parent) if f.get("name")==name]
    if folder is True:
        matches=[f for f in matches if f.get("mimeType")=="application/vnd.google-apps.folder"]
    if folder is False:
        matches=[f for f in matches if f.get("mimeType")!="application/vnd.google-apps.folder"]
    if len(matches)!=1:
        raise GateError(f"Expected one run-owned {name}")
    return matches[0]


def main() -> None:
    store=Store()
    folder=store.drive.files().get(
        fileId=FOLDER_ID,fields="id,name,appProperties",supportsAllDrives=True
    ).execute()
    props=folder.get("appProperties",{})
    if props.get("opcPrintRun")!=RUN_KEY or props.get("state")!="OWNER_REVISION_READY_NOT_APPROVED":
        raise GateError("v372 run identity/state mismatch")
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        resources=root/"resources";resources.mkdir()
        cards=one_child(store,FOLDER_ID,"cards.json",False)
        download_drive(store,cards["id"],root/"cards.json")
        spec=json.loads((root/"cards.json").read_text(encoding="utf-8"))

        drive_resources=one_child(store,FOLDER_ID,"resources",True)
        resource_files={f["name"]:f for f in store.list_children(drive_resources["id"])}
        for source in spec["sources"]:
            name=Path(source["screenshot"]).name
            if name not in resource_files: raise GateError("Missing v372 proof screenshot")
            download_drive(store,resource_files[name]["id"],resources/name)

        drive_png=one_child(store,FOLDER_ID,"png",True)
        for theme in ("dark","cream","lime"):
            local=root/"png"/theme;local.mkdir(parents=True)
            tdir=one_child(store,drive_png["id"],theme,True)
            files={f["name"]:f for f in store.list_children(tdir["id"])}
            for i in range(1,len(spec["slides"])+1):
                name=f"card_{i:02d}.png"
                if name not in files: raise GateError("Missing v372 rendered card")
                download_drive(store,files[name]["id"],local/name)

        path=review(spec,root)
        report=review_probe(path,root)
        target=one_child(store,FOLDER_ID,"review.html",False)
        if target["id"]!=REVIEW_ID: raise GateError("v372 review target changed")
        result=store.upsert_run_file(path,FOLDER_ID)
        print(json.dumps({"status":"refreshed","review":result["webViewLink"],"probe":report,
                          "approved":False,"published":False}))


if __name__=="__main__":
    main()
