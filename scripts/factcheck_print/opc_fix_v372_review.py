"""Repair the v372 review copy button in place. No AI, no paid APIs."""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'capture'))
sys.path.insert(0,str(HERE.parent))

from opc_contract import GateError
from opc_store import Store

FOLDER_ID="1gnjGkxUF9i9XT6NZFCs9Qnyh-mhxSw6j"
RUN_KEY="pr300-paint-owner-revision-20260921"
REVIEW_ID="1XbEXQbM8hVG7mevyW-LtSiBP5dz2zIDZ"

def main():
    store=Store()
    folder=store.drive.files().get(fileId=FOLDER_ID,fields="id,appProperties",supportsAllDrives=True).execute()
    props=folder.get("appProperties",{})
    if props.get("opcPrintRun")!=RUN_KEY or props.get("state")!="OWNER_REVISION_READY_NOT_APPROVED":
        raise GateError("v372 owner-revision identity/state mismatch")
    meta=store.drive.files().get(fileId=REVIEW_ID,fields="id,name,parents,md5Checksum,size,mimeType",supportsAllDrives=True).execute()
    if meta.get("parents")!=[FOLDER_ID] or meta.get("name")!="review.html" or meta.get("mimeType")!="text/html":
        raise GateError("review.html target mismatch")
    raw=store.drive.files().get_media(fileId=REVIEW_ID,supportsAllDrives=True).execute()
    if not isinstance(raw,bytes) or hashlib.md5(raw).hexdigest()!=meta.get("md5Checksum"):
        raise GateError("review.html download checksum mismatch")
    text=raw.decode("utf-8")
    broken="rows.length?rows.join('\\n\\n'):'No review notes yet.';"  # runtime contains literal newlines
    fixed="rows.length?rows.join('\\\\n\\\\n'):'No review notes yet.';"
    if text.count(broken)!=1:
        raise GateError("expected exactly one broken copy-review join")
    repaired=text.replace(broken,fixed)
    if broken in repaired or fixed not in repaired:
        raise GateError("copy-review repair invariant failed")
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"review.html"
        path.write_text(repaired,encoding="utf-8")
        result=store.upsert_run_file(path,FOLDER_ID)
        check=store.drive.files().get(fileId=REVIEW_ID,fields="md5Checksum,size,webViewLink",supportsAllDrives=True).execute()
        if check.get("md5Checksum")!=hashlib.md5(path.read_bytes()).hexdigest():
            raise GateError("repaired review readback checksum mismatch")
    print({"status":"fixed","review_id":REVIEW_ID,"size":check.get("size"),"approved":False,"published":False})

if __name__=="__main__":
    main()
