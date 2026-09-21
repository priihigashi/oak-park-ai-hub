"""Deterministic private-spec OPC builder for ChatGPT-assisted creation.

The chat does research/editorial judgment; this runner validates the supplied private
Drive spec, captures the cited public sources, generates only the declared visuals,
renders the review site, and files it as Built, NOT APPROVED. It never calls a text model.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'capture'))
sys.path.insert(0,str(HERE.parent))

from opc_contract import GateError, STATUS, check_copy, canonical_url, digest_file, plain, validate
from opc_media import ReplicateImages
from opc_network import screenshot_source
from opc_render import export, review
from opc_store import Store

CHAT_INTAKE_PARENT="1UJJPeilZ5deMFn4eca2J1KX4RhP3Sbdy"
MAX_SPEC_BYTES=120_000
SHADE_CODE=re.compile(r"\b(?:SW\s*\d{4}|OC-\d+|HC-\d+)\b",re.I)


def save(path:Path,value)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")


def args():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec-drive-id",required=True)
    ap.add_argument("--out",default="opc-chat-build")
    ap.add_argument("--image-model",default="google/nano-banana-pro")
    return ap.parse_args()


def google_doc_text(document:dict)->str:
    parts=[]
    for item in document.get("body",{}).get("content",[]):
        for element in item.get("paragraph",{}).get("elements",[]):
            parts.append(element.get("textRun",{}).get("content",""))
    return "".join(parts).strip()


def download_raw_spec(store:Store,file_id:str,target:Path,meta:dict)->None:
    from googleapiclient.http import MediaIoBaseDownload
    request=store.drive.files().get_media(fileId=file_id,supportsAllDrives=True)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("wb") as stream:
        dl=MediaIoBaseDownload(stream,request);done=False
        while not done:_,done=dl.next_chunk()
    if meta.get("md5Checksum") and hashlib.md5(target.read_bytes()).hexdigest()!=meta["md5Checksum"]:
        raise GateError("Chat spec checksum mismatch")


def download_spec(store:Store,file_id:str,target:Path)->dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]{20,100}",file_id):
        raise GateError("Invalid private chat spec id")
    fields="id,name,parents,size,md5Checksum,mimeType,appProperties"
    meta=store.drive.files().get(fileId=file_id,fields=fields,supportsAllDrives=True).execute()
    if meta.get("parents") != [CHAT_INTAKE_PARENT]:
        raise GateError("Chat spec is not in the verified private intake folder")
    if meta.get("mimeType")=="application/vnd.google-apps.document":
        text=google_doc_text(store.docs.documents().get(documentId=file_id).execute())
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(text,encoding="utf-8")
    else:
        size=int(meta.get("size",0))
        if size<50 or size>MAX_SPEC_BYTES:
            raise GateError("Chat spec size is outside the bounded intake limit")
        download_raw_spec(store,file_id,target,meta)
    if not 50<=target.stat().st_size<=MAX_SPEC_BYTES:
        raise GateError("Chat spec content is outside the bounded intake limit")
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError("Chat spec is not valid JSON") from exc

def audit_header(p:dict)->None:
    if p.get("version")!=1 or p.get("project")!="opc" or p.get("kind","education")!="education":
        raise GateError("Unsupported chat spec version/project/kind")
    audit=p.get("audit") or {}
    required=("sources_checked","copy_checked","visual_jobs_checked","no_repetition_checked")
    if not all(audit.get(k) is True for k in required):
        raise GateError("Chat spec is missing required research/editorial audit attestations")
    keywords=p.get("keywords") or []
    if len(keywords)!=3 or len({plain(x).casefold() for x in keywords})!=3:
        raise GateError("Chat spec requires exactly three distinct dedupe keywords")


def audit_shape(p:dict)->tuple[list,list,list]:
    slides=p.get("slides") or []
    visuals=p.get("visuals") or []
    sources=p.get("sources") or []
    if len(slides)!=5 or len(visuals)!=5 or not 2<=len(sources)<=4:
        raise GateError("Chat spec requires exactly five slides/visuals and 2-4 sources")
    if [v.get("key") for v in visuals]!=["A1","A2","A3","A4","A5"]:
        raise GateError("Chat visual keys must be A1-A5 exactly")
    slide_ids=[s.get("id") for s in slides]
    visual_keys=[s.get("visual_key") for s in slides]
    if slide_ids!=[1,2,3,4,5] or visual_keys!=["A1","A2","A3","A4","A5"]:
        raise GateError("Each chat slide must have its own sequential visual job")
    return slides,visuals,sources


def audit_sources(sources:list[dict],source_url:str)->set[str]:
    source_ids={s.get("id") for s in sources}
    if len(source_ids)!=len(sources) or None in source_ids:
        raise GateError("Duplicate/missing source ids")
    for source in sources:
        if not source.get("name") or not source.get("url"):
            raise GateError("Source name/url required")
        canonical_url(source["url"])
    if source_url:
        canonical_url(source_url)
    return source_ids


def audit_slides(slides:list[dict],source_ids:set[str])->None:
    for i,slide in enumerate(slides,1):
        errs=check_copy(slide,i)
        if errs:
            raise GateError("; ".join(errs))
        if i not in (1,5) and not slide.get("source_ids"):
            raise GateError(f"slide {i}: factual source required")
        if set(slide.get("source_ids",[]))-source_ids:
            raise GateError(f"slide {i}: unknown source id")


def audit_public_copy(p:dict,slides:list[dict])->None:
    parts=[str(p.get("title","")),str(p.get("caption","")),str(p.get("hashtags",""))]
    parts.extend(str(x.get("headline",""))+" "+str(x.get("body","")) for x in slides)
    if SHADE_CODE.search(" ".join(parts)):
        raise GateError("Brand-specific paint shade code is not allowed in generic homeowner education")


def audit_payload(p:dict)->None:
    audit_header(p)
    slides,_,sources=audit_shape(p)
    source_ids=audit_sources(sources,p.get("source_url",""))
    audit_slides(slides,source_ids)
    audit_public_copy(p,slides)

def capture_sources(p:dict,root:Path)->list[dict]:
    out=[]
    for src in p["sources"]:
        path=root/"resources"/f"proof-{src['id']}.png"
        shot=screenshot_source(src["url"],path)
        out.append({"id":src["id"],"name":plain(src["name"]),"url":src["url"],
                    "heading":shot["heading"],"excerpt":shot["excerpt"],
                    "screenshot":str(path.relative_to(root)),"observed_in_search":True,
                    "source_origin":"chat_verified_web_search"})
    return out


def generate_assets(p:dict,root:Path,model:str)->list[dict]:
    # Affordable default for generic OPC scenes. A private spec can explicitly
    # promote Nano Banana Pro when reference editing/consistency justifies it.
    chain=p.get("image_models") or [
        "bytedance/seedream-4.5",
        "google/nano-banana-2-lite",
        "google/imagen-4-fast",
    ]
    if not isinstance(chain,list) or not 1<=len(chain)<=3 or len(set(chain))!=len(chain):
        raise GateError("image_models must contain 1-3 distinct approved Replicate models")
    if any(m not in __import__("opc_contract").MODELS for m in chain):
        raise GateError("Unsupported image fallback model")
    provider=ReplicateImages(chain[0],root,max_images=15)
    assets=[]
    disabled=set()
    circuit=[]
    for visual in p["visuals"]:
        failures=[]
        for candidate in chain:
            if candidate in disabled:
                failures.append({"model":candidate,"status":"skipped_after_prior_failure"})
                continue
            provider.switch_model(candidate)
            try:
                assets.append(provider.generate(visual["key"],plain(visual["subject"]),None))
                break
            except GateError as exc:
                failures.append({"model":candidate,"status":"failed","error":str(exc)[:180]})
                # One provider/model failure opens a per-run circuit breaker so
                # five cards do not pay for the same known-bad route repeatedly.
                disabled.add(candidate)
                circuit.append({"model":candidate,"disabled_after":visual["key"]})
        else:
            save(root/"resources"/f"{visual['key']}-image-failures.json",failures)
            save(root/"resources"/"image-circuit-breakers.json",circuit)
            raise GateError(f"All declared image routes failed for {visual['key']}")
    save(root/"resources"/"image-circuit-breakers.json",circuit)
    return assets


def assemble(p:dict,sources:list[dict],assets:list[dict])->dict:
    audit=p["audit"]
    return {"project":"opc","language":"en","kind":"education","status":STATUS,"approved":False,
            "title":plain(p["title"]),"caption":plain(p["caption"]),"hashtags":plain(p.get("hashtags","")),
            "slides":p["slides"],"sources":sources,"assets":assets,
            "editorial_review":{"passed":True,"english":True,"provider":"ChatGPT-assisted",
                "model":"chat research + deterministic runtime","independent_council":False,
                "automated_review_passed":False,
                "method":"Private chat spec was source-checked and copy/visual-audited before this no-text-model build.",
                "audit_notes":audit.get("notes",[])},
            "video":None,"source_url":p.get("source_url",""),
            "template":"opc_tip / FORMAT-030 visual PRINT","reference_media_status":p.get("reference_media_status","not_applicable"),
            "motion":{"requested":False,"status":"static_chat_assisted","reason":"Private owner review carousel."},
            "build_mode":"chat_assisted_no_text_model","chat_spec_id":p.get("_spec_id","")}


def main()->None:
    a=args();root=Path(a.out);(root/"resources").mkdir(parents=True,exist_ok=True);(root/"motion").mkdir(exist_ok=True)
    store=Store();store.preflight()
    p=download_spec(store,a.spec_drive_id,root/"resources/chat-intake.json");p["_spec_id"]=a.spec_drive_id
    audit_payload(p)
    if store.duplicates(p["title"],p["keywords"],p.get("source_url","")):
        raise GateError("Topic/source already exists in Content Control")
    run_key=f"chat-spec-{a.spec_drive_id}"
    folder=store.start_run(p["title"],run_key)
    try:
        sources=capture_sources(p,root)
        assets=generate_assets(p,root,a.image_model)
        spec=assemble(p,sources,assets)
        save(root/"cards.json",spec);save(root/"resources/content-gates.json",validate(spec,root,[]))
        save(root/"resources/chat-audit.json",p["audit"])
        save(root/"resources/evidence.json",{"sources":spec["sources"],"audit":p["audit"],"retrieved_at":datetime.now(timezone.utc).isoformat()})
        export(spec,root);review(spec,root)
        (root/"motion/README.md").write_text("Static private owner review; no publication claim.\n",encoding="utf-8")
        store.rename_run(folder,spec["title"])
        links=store.upload_tree(root,folder)
        usage=json.loads((root/"resources/image-usage.json").read_text(encoding="utf-8")) if (root/"resources/image-usage.json").exists() else []
        receipt={"content_row":store.file_row(spec,folder,links),"flow_row":store.flow_row(spec,folder,links),
                 "build_mode":"chat_assisted_no_text_model","text_api_calls":0,"image_requests":len(usage),
                 "approved":False,"published":False,"review_url":links["review.html"],"folder_url":folder["webViewLink"]}
        save(root/"resources/filing-receipt.json",receipt)
        resources=next(x for x in store.list_children(folder["id"]) if x["name"]=="resources")
        store.upsert_run_file(root/"resources/filing-receipt.json",resources["id"])
        store.drive.files().update(fileId=a.spec_drive_id,body={"appProperties":{"opcChatState":"BUILT_NOT_APPROVED","outputFolder":folder["id"]}},
                                   fields="id,appProperties",supportsAllDrives=True).execute()
        store.finish(folder,"BUILT_NOT_APPROVED")
        result={"status":"built_not_approved","title":spec["title"],"review_url":links["review.html"],
                "folder_url":folder["webViewLink"],"cards":5,"text_api_calls":0,"image_requests":len(usage),
                "approved":False,"published":False}
        Path("opc_result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
        print(json.dumps(result))
    except Exception as exc:
        save(root/"resources/failure.json",{"status":"BLOCKED_NOT_APPROVED","error_type":type(exc).__name__,"message":str(exc)[:1000]})
        try:store.upload_tree(root,folder);store.finish(folder,"BLOCKED_NOT_APPROVED")
        except Exception:pass
        raise


if __name__=="__main__":main()
