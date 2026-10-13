"""Temporary PR-branch queue for ChatGPT → OPC review builds.

This keeps the chat flow usable before PR #300 is merged. A private Drive Doc
is renamed with one READY prefix; the owner-only PR label runs exactly that one
item. Topic specs and source-video requests are separate modes so topic builds
never receive text-model/capture credentials.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"capture"))
sys.path.insert(0,str(HERE.parent))

from opc_chat_build import CHAT_INTAKE_PARENT, download_spec
from opc_contract import GateError
from opc_store import Store
from resolve_inputs import video_url

PREFIXES={
    "chat":"READY — OPC CHAT — ",
    "link":"READY — OPC LINK — ",
}


def parse_args():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode",choices=sorted(PREFIXES),required=True)
    return ap.parse_args()


def pending(store:Store,mode:str)->dict:
    prefix=PREFIXES[mode]
    found=[]
    for item in store.list_children(CHAT_INTAKE_PARENT):
        state=item.get("appProperties",{}).get("opcChatState","")
        if item.get("name","").startswith(prefix) and state not in ("BUILT_NOT_APPROVED","DONE"):
            found.append(item)
    if len(found)!=1:
        raise GateError(f"Expected exactly one private READY {mode} item; found {len(found)}")
    return found[0]


def mark(store:Store,item:dict,state:str)->None:
    prefix=PREFIXES["chat"] if "OPC CHAT" in item["name"] else PREFIXES["link"]
    replacement=("DONE — " if state=="BUILT_NOT_APPROVED" else "BLOCKED — ")+item["name"][len(prefix):]
    props={**item.get("appProperties",{}),"opcChatState":state}
    store.drive.files().update(
        fileId=item["id"],body={"name":replacement,"appProperties":props},
        fields="id,name,appProperties",supportsAllDrives=True
    ).execute()


def run_chat(item:dict)->None:
    if "SELF-AUDIT-VISUAL-FIX" in item.get("name",""):
        cmd=[sys.executable,str(HERE/"opc_self_audit_queue.py")]
    else:
        cmd=[sys.executable,str(HERE/"opc_chat_build.py"),"--spec-drive-id",item["id"],"--out","factcheck_out"]
    subprocess.run(cmd,check=True)


def link_request(data:dict)->tuple[str,str]:
    if data.get("version")!=1 or data.get("project")!="opc":
        raise GateError("Unsupported private OPC link request")
    url=str(data.get("source_url","")).strip()
    notes=str(data.get("notes",""))[:4000]
    if not video_url(url):
        raise GateError("Private OPC link request must contain a supported HTTPS video URL")
    return url,notes


def run_link(store:Store,item:dict)->None:
    with tempfile.TemporaryDirectory() as tmp:
        data=download_spec(store,item["id"],Path(tmp)/"link-request.json")
    url,notes=link_request(data)
    cmd=[sys.executable,str(HERE/"opc.py"),"--project","opc","--url",url,"--notes",notes,
         "--out","factcheck_out","--run-key",f"chat-link-{item['id']}"]
    subprocess.run(cmd,check=True)


def main()->None:
    a=parse_args()
    store=Store();store.preflight()
    item=pending(store,a.mode)
    try:
        run_chat(item) if a.mode=="chat" else run_link(store,item)
        result=json.loads(Path("opc_result.json").read_text(encoding="utf-8"))
        if not result.get("review_url") or result.get("approved") is not False:
            raise GateError("Queue child did not produce a private unapproved review URL")
        mark(store,item,"BUILT_NOT_APPROVED")
        print(json.dumps({"mode":a.mode,"spec_id":item["id"],**result},ensure_ascii=False))
    except Exception:
        try:mark(store,item,"BLOCKED_NOT_APPROVED")
        except Exception:pass
        raise


if __name__=="__main__":
    main()
