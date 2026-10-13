"""Queue wrapper for the bounded OPC visual self-audit repair."""
import json
from pathlib import Path
from opc_self_audit_visual_fix import Store, TARGETS, patch_one

def main():
    store=Store();store.preflight()
    results=[patch_one(store,t) for t in TARGETS]
    payload={"status":"built_not_approved","results":results,
             "review_url":results[0]["review_url"],
             "review_urls":[x["review_url"] for x in results],
             "approved":False,"published":False}
    Path("opc_result.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload))

if __name__=="__main__":
    main()
