"""Owner-directed paint revision: reuse verified evidence, generate only replacement visuals.

No text model calls. Explicitly revises the already-filed paint sample after owner feedback.
Nothing is published or approved.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from googleapiclient.http import MediaIoBaseDownload

from opc_contract import GateError, STATUS, digest_file, tracker_row, validate
from opc_media import ReplicateImages
from opc_render import export, review
from opc_store import Store, CONTROL, CONTROL_TAB, FLOW

SOURCE_FOLDER_ID = "1T_2e8JHybyo7Qd59xW_v2_6SsIU44ZAo"
SOURCE_RUN_KEY = "pr300-paint-idea-20260920"
RUN_KEY = "pr300-paint-owner-revision-20260921"
CONTROL_ROW = 429
FLOW_ROW = 171
NEW_IMAGE_KEYS = ("A1", "A2", "A4", "A5")


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def download_bytes(store: Store, file_id: str, target: Path) -> None:
    meta = store.drive.files().get(
        fileId=file_id, fields="id,name,size,md5Checksum,mimeType", supportsAllDrives=True
    ).execute()
    if int(meta.get("size", 0)) > 15_000_000:
        raise GateError("Owner-revision source file exceeds bounded size")
    request = store.drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as stream:
        dl = MediaIoBaseDownload(stream, request)
        done = False
        while not done:
            _, done = dl.next_chunk()
    if hashlib.md5(target.read_bytes()).hexdigest() != meta.get("md5Checksum"):
        raise GateError("Owner-revision source checksum mismatch")


def source_pack(store: Store, root: Path) -> tuple[dict, dict]:
    folder = store.drive.files().get(
        fileId=SOURCE_FOLDER_ID, fields="id,name,parents,appProperties", supportsAllDrives=True
    ).execute()
    props = folder.get("appProperties", {})
    if props.get("opcPrintRun") != SOURCE_RUN_KEY:
        raise GateError("Paint source run identity mismatch")
    resources = [x for x in store.list_children(SOURCE_FOLDER_ID) if x["name"] == "resources"]
    cards = [x for x in store.list_children(SOURCE_FOLDER_ID) if x["name"] == "cards.json"]
    if len(resources) != 1 or len(cards) != 1:
        raise GateError("Paint source pack is ambiguous")
    children = store.list_children(resources[0]["id"])
    by_name = {x["name"]: x for x in children}
    required = ["evidence.json", "A3.jpg", "proof-S1.png", "proof-S2.png", "proof-S3.png", "proof-S4.png"]
    if any(name not in by_name for name in required):
        raise GateError("Paint source pack is incomplete")
    for name in required:
        download_bytes(store, by_name[name]["id"], root / "resources" / name)
    download_bytes(store, cards[0]["id"], root / "source-cards.json")
    evidence = json.loads((root / "resources/evidence.json").read_text(encoding="utf-8"))
    prior = json.loads((root / "source-cards.json").read_text(encoding="utf-8"))
    urls = {s.get("id"): s.get("url", "") for s in evidence.get("sources", [])}
    if "sherwin-williams" not in urls.get("S2", "") or "benjaminmoore" not in urls.get("S3", "") or "benjaminmoore" not in urls.get("S4", ""):
        raise GateError("Expected manufacturer evidence IDs changed")
    return evidence, prior


def draft() -> dict:
    return {
        "title": "Why Paint Looks Different at Home",
        "caption": "A paint chip is only the start. Check the room light, finish, and a movable sample in your own space before you decide.",
        "hashtags": "#PaintingTips #HomeRenovation #SouthFloridaHomes #OakParkConstruction",
        "slides": [
            {
                "id": 1, "layout": "cover",
                "headline": "Same paint. Different look.",
                "body": "Light and finish can change how a color looks in your room.",
                "source_ids": ["S2", "S3"], "visual_key": "A1",
                "visual_description": "Current contemporary South Florida living room with well-kept modern furniture and a neutral painted wall in natural daylight."
            },
            {
                "id": 2, "layout": "compare",
                "headline": "Same wall. Three lights.",
                "body": "Daylight and room lighting can make the same paint look different. Check it in sun, cloud, and evening light.",
                "source_ids": ["S2", "S4"], "visual_key": "A2",
                "visual_description": "Controlled three-panel comparison of the identical room and wall under sunny daylight, overcast daylight, and evening artificial light."
            },
            {
                "id": 3, "layout": "compare",
                "headline": "Finish changes the look.",
                "body": "Matte and higher-sheen finishes reflect light differently, which can change how the color appears.",
                "source_ids": ["S3"], "visual_key": "A3",
                "visual_description": "Close detail of the same neutral color in matte and glossier finishes under the same light."
            },
            {
                "id": 4, "layout": "point",
                "headline": "Test a movable sample.",
                "body": "Paint a white foam board, then move it around the room to see it under different lighting.",
                "source_ids": ["S4"], "visual_key": "A4",
                "visual_description": "Hands actively brushing a generic neutral test coat onto white foam board near a window; process demonstration, not an exact manufacturer color."
            },
            {
                "id": 5, "layout": "close",
                "headline": "Check before you commit.",
                "body": "Compare daylight, room lighting, finish, and a movable sample in your own space.",
                "source_ids": ["S2", "S3", "S4"], "visual_key": "A5",
                "visual_description": "Distinct overhead planning scene with a white foam board, brush, matte and glossier sample surfaces, and daylight plus a small lamp as visual cues."
            },
        ],
        "visuals": [
            {
                "key": "A1",
                "subject": "Eye-level wide photograph from the doorway of a contemporary South Florida living room. Current well-kept cream sofa with clean modern lines, light oak accents, uncluttered decor, large window, neutral painted wall. Soft natural daylight, realistic material texture, no worn or distressed furniture. Foreground: edge of a modern chair; midground: sofa and wall; background: window. Teaching purpose: attractive current room context without suggesting a specific paint brand."
            },
            {
                "key": "A2",
                "subject": "One controlled triptych comparison image made of three equal vertical photographic panels with the IDENTICAL South Florida room, identical neutral wall, identical camera position and furnishings in every panel. Left: bright sunny daylight through the same window. Center: soft overcast daylight. Right: evening with the same room lit by a warm interior lamp/fixture. Only lighting changes; architecture, wall, furniture and camera remain fixed. No text or labels. Teaching purpose: prove that lighting changes perceived color."
            },
            {
                "key": "A3",
                "subject": "REUSE_VERIFIED_PRIOR_SHEEN_VISUAL"
            },
            {
                "key": "A4",
                "subject": "Close three-quarter documentary photograph of two hands actively applying a generic muted-neutral test coat with a small brush onto a clean white foam-core board beside an interior window. The board is visibly a work-in-progress with brush strokes and white border, not a finished branded swatch. Small unbranded sample pot nearby. Natural daylight. Teaching purpose: demonstrate the movable-board sampling process without claiming an exact paint color."
            },
            {
                "key": "A5",
                "subject": "Overhead bird's-eye documentary photograph of a clean light-oak work surface arranged as a paint-decision toolkit: plain white foam-core board, small unbranded brush, two unlabeled neutral finish sample pieces showing matte versus subtle sheen, and a small simple lamp switched on at one edge while soft window daylight crosses the table from the other side. No text, labels, logos, color codes, or paint brand. Teaching purpose: visually summarize light, finish, and movable sampling in one distinct closing composition."
            },
        ],
    }


def make_assets(store: Store, root: Path, prior: dict) -> list[dict]:
    prior_assets = {a["key"]: a for a in prior.get("assets", [])}
    old = prior_assets.get("A3")
    if not old or digest_file(root / "resources/A3.jpg") != old.get("sha256"):
        raise GateError("Prior sheen visual checksum mismatch")
    provider = ReplicateImages("google/nano-banana-pro", root, max_images=4)
    a1 = provider.generate("A1", draft()["visuals"][0]["subject"])
    anchor = root / a1["path"]
    a2 = provider.generate("A2", draft()["visuals"][1]["subject"], anchor)
    a4 = provider.generate("A4", draft()["visuals"][3]["subject"], anchor)
    a5 = provider.generate("A5", draft()["visuals"][4]["subject"], anchor)
    a3 = dict(old)
    a3["path"] = "resources/A3.jpg"
    a3["reused_from_run"] = SOURCE_RUN_KEY
    a3["owner_feedback_keep"] = True
    return [a1, a2, a3, a4, a5]


def build_spec(evidence: dict, assets: list[dict]) -> dict:
    d = draft()
    editorial = {
        "passed": True,
        "english": True,
        "provider": "owner-feedback-assisted",
        "model": "no new text model",
        "independent_council": False,
        "automated_review_passed": False,
        "method": "Source-checked against the saved manufacturer evidence; copy and visual direction revised from Priscila's review. No new text API calls.",
    }
    spec = {
        "project": "opc", "language": "en", "kind": "education", "status": STATUS,
        "approved": False, "title": d["title"], "caption": d["caption"], "hashtags": d["hashtags"],
        "slides": d["slides"], "sources": [
            {k: s[k] for k in ("id", "name", "url", "screenshot", "observed_in_search", "heading") if k in s}
            for s in evidence["sources"]
        ],
        "assets": assets, "editorial_review": editorial, "video": None, "source_url": "",
        "template": "opc_tip / FORMAT-030 visual PRINT",
        "reference_media_status": "not_applicable",
        "motion": {"requested": False, "status": "static_owner_revision", "reason": "Owner requested a revised static carousel review."},
        "build_mode": "owner_revision_no_text_api",
        "source_run": SOURCE_RUN_KEY,
    }
    return spec


def replace_tracker_rows(store: Store, spec: dict, folder: dict, links: dict) -> dict:
    rows = store.read_rows(CONTROL, CONTROL_TAB, "M")
    headers = rows[0]
    current = rows[CONTROL_ROW - 1]
    title_i = headers.index("Title")
    if len(current) <= title_i or current[title_i] != "Why Paint Looks Different at Home":
        raise GateError("Content row 429 no longer matches the paint review")
    values = {
        "# Reviews": current[headers.index("# Reviews")] if len(current) > headers.index("# Reviews") else "0",
        "Title": spec["title"], "Post Type": "Homeowner education",
        "Format": "FORMAT-030 OPC visual PRINT", "Content Type": "Carousel", "Status": STATUS,
        "Drive Folder Link": folder["webViewLink"], "Caption": spec["caption"], "Hashtags": spec["hashtags"],
        "Output Link": links["review.html"], "Date Created": datetime.now(timezone.utc).date().isoformat(),
        "Research Doc Link": links["resources/evidence.json"], "Original Source Video Link": "",
    }
    row = tracker_row(headers, values)
    a1 = f"'{CONTROL_TAB}'!A{CONTROL_ROW}:M{CONTROL_ROW}"
    store.sheets.spreadsheets().values().update(
        spreadsheetId=CONTROL, range=a1, valueInputOption="RAW", body={"values": [row]}
    ).execute()
    got = store.sheets.spreadsheets().values().get(spreadsheetId=CONTROL, range=a1).execute().get("values", [[]])[0]
    if [str(x) for x in got] + [""] * (len(row) - len(got)) != row:
        raise GateError("Content row replacement readback mismatch")

    flow_rows = store.read_rows(FLOW, "All Docs", "I")
    fh = flow_rows[0]
    fcur = flow_rows[FLOW_ROW - 1]
    if not fcur or not str(fcur[0]).startswith("OPC PRINT — Why Paint Looks Different at Home"):
        raise GateError("Flow Plans row 171 no longer matches the paint review")
    fv = {
        "NAME": "OPC PRINT — " + spec["title"], "TYPE": "Content review", "NICHE": "OPC",
        "STATUS": "READY FOR PRISCILA REVIEW",
        "DESCRIPTION": "Owner-revised visual feed; saved evidence reused; no new text API; not approved or published.",
        "OPEN": links["review.html"], "DOC_ID": folder["id"], "TABS": "",
        "LAST UPDATED": datetime.now(timezone.utc).date().isoformat(),
    }
    frow = [fv.get(h, "") for h in fh]
    fa1 = f"'All Docs'!A{FLOW_ROW}:I{FLOW_ROW}"
    store.sheets.spreadsheets().values().update(
        spreadsheetId=FLOW, range=fa1, valueInputOption="RAW", body={"values": [frow]}
    ).execute()
    fgot = store.sheets.spreadsheets().values().get(spreadsheetId=FLOW, range=fa1).execute().get("values", [[]])[0]
    if [str(x) for x in fgot] + [""] * (len(frow) - len(fgot)) != frow:
        raise GateError("Flow row replacement readback mismatch")
    return {"content_row": a1, "flow_row": fa1}


def main() -> None:
    store = Store()
    store.preflight()
    root = Path("opc-paint-owner-revision")
    (root / "resources").mkdir(parents=True, exist_ok=True)
    (root / "motion").mkdir(exist_ok=True)
    evidence, prior = source_pack(store, root)
    folder = store.start_run("Why Paint Looks Different at Home owner revision", RUN_KEY)
    try:
        assets = make_assets(store, root, prior)
        spec = build_spec(evidence, assets)
        save(root / "cards.json", spec)
        save(root / "resources/content-gates.json", validate(spec, root, []))
        save(root / "resources/owner-review-applied.json", {
            "source": "Priscila review 2026-09-20",
            "applied": [
                "current well-kept room staging",
                "same-room sunny/cloudy/evening lighting comparison",
                "kept sheen concept",
                "sampling shown as process, not exact AI paint color",
                "distinct closing visual",
                "no loud public AI boilerplate",
                "copy-to-chat review UX",
            ],
            "new_text_api_calls": 0, "max_new_image_requests": 4,
            "approved": False, "published": False,
        })
        export(spec, root)
        page = review(spec, root)
        page.write_text(
            page.read_text(encoding="utf-8").replace(
                "READY FOR PRISCILA REVIEW · NOT APPROVED · NOT PUBLISHED",
                "OWNER REVISION · READY FOR PRISCILA REVIEW · NOT APPROVED"
            ),
            encoding="utf-8",
        )
        (root / "motion/README.md").write_text("Static owner-review revision; no motion claim.\n", encoding="utf-8")
        store.rename_run(folder, spec["title"] + " owner revision")
        links = store.upload_tree(root, folder)
        receipt = replace_tracker_rows(store, spec, folder, links)
        receipt.update({
            "build_mode": spec["build_mode"], "source_run": SOURCE_RUN_KEY,
            "new_text_api_calls": 0, "new_image_requests": 4,
            "approved": False, "published": False, "folder": folder["webViewLink"],
        })
        save(root / "resources/revision-receipt.json", receipt)
        resources = next(x for x in store.list_children(folder["id"]) if x["name"] == "resources")
        store.upsert_run_file(root / "resources/revision-receipt.json", resources["id"])
        store.finish(folder, "OWNER_REVISION_READY_NOT_APPROVED")
        print(json.dumps(receipt))
    except Exception:
        store.finish(folder, "OWNER_REVISION_BLOCKED_NOT_APPROVED")
        raise


if __name__ == "__main__":
    main()
