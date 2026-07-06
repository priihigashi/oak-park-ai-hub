#!/usr/bin/env python3
"""
opc_media_sorter.py — Daily Job-Video Auto-Sorter
Build spec: docs/pipeline-fix/daily-job-video-auto-sorter-audit-2026-06-25.md
Drive doc:  1cSsxJ0NtrjrHKjPbrPdgyZCN6uJoc8D3hf-AvfkOQ2k

What it does:
  1. Lists video files in the drop folder (not yet cataloged by Drive FILE ID)
  2. Reads capture date + GPS via ffprobe (with Drive-metadata fallbacks)
  3. Creates YYYY-MM-DD subfolders under the drop parent; GPS-matched files also
     go into a ProjectName/ subfolder; unmatched go into _no-location/
  4. Moves (not copies) each file into its destination folder
  5. Appends a row to the Photo Catalog tab (new File ID / media-type / GPS columns)
  6. Logs pipeline failures and exits non-zero so the GitHub Action flips red

Division of labor (no double-cataloging):
  photo_catalog_cloud.py  — scans PROJECT folders, images only
  opc_media_sorter.py     — scans DROP folder, videos only, then moves into projects
"""

import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime

# ── Key IDs (verified 2026-06-25 per build spec §4) ────────────────────────
SHEET_ID      = "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU"  # Ideas & Inbox
CATALOG_TAB   = "📸 Photo Catalog"
FAILURES_TAB  = "🚨 Pipeline Failures"
DROP_FOLDER   = "1dNmFflB0yS8Qc9A1-mfbMCIHOVZzcndb"  # "Daily Job Videos - DROP HERE (Mike)"
OPC_DRIVE_ID  = "0AJp3Phs0wIBOUk9PVA"

# Maximum videos processed per run (cost + runtime guard)
MAX_PER_RUN   = 30

# New catalog columns added by this sorter (appended to existing A-T header)
NEW_COL_NAMES = ["File ID", "Media Type", "GPS Lat,Lon", "Day Folder Link", "Sorter Status"]

# Video MIME types we move; images are left for photo_catalog_cloud.py
VIDEO_MIMES = {
    "video/mp4", "video/quicktime", "video/x-msvideo", "video/mpeg",
    "video/3gpp", "video/webm", "video/x-matroska",
}

# GitHub Actions run ID for failure log URLs
_GHA_RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
_SCRIPT     = "opc_media_sorter.py"

# ── Auth ────────────────────────────────────────────────────────────────────

TOKEN_FILE = os.environ.get("SHEETS_TOKEN_PATH", "")


def _get_access_token() -> str:
    if not TOKEN_FILE or not os.path.exists(TOKEN_FILE):
        raise RuntimeError(f"SHEETS_TOKEN_PATH not set or file missing: {TOKEN_FILE}")
    td = json.loads(open(TOKEN_FILE).read())
    data = urllib.parse.urlencode({
        "client_id":     td["client_id"],
        "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"],
        "grant_type":    "refresh_token",
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    ).read())
    return resp["access_token"]


# ── Drive helpers ────────────────────────────────────────────────────────────

def _drive_request(method: str, url: str, token: str, body=None) -> dict:
    data = json.dumps(body).encode() if body else None
    headers = {"Authorization": f"Bearer {token}"}
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Drive HTTP {e.code}: {e.read().decode()[:300]}")


def _list_files(token: str, parent_id: str, mime_filter: str = None) -> list:
    q = f"'{parent_id}' in parents and trashed=false"
    if mime_filter:
        q += f" and mimeType='{mime_filter}'"
    params = urllib.parse.urlencode({
        "q": q,
        "corpora": "allDrives",
        "includeItemsFromAllDrives": "true",
        "supportsAllDrives": "true",
        "fields": "files(id,name,mimeType,createdTime,videoMediaMetadata)",
        "pageSize": "200",
    })
    url = f"https://www.googleapis.com/drive/v3/files?{params}"
    result = _drive_request("GET", url, token)
    return result.get("files", [])


def _ensure_folder(token: str, name: str, parent_id: str) -> str:
    """Return folder ID, creating the folder if it doesn't already exist."""
    q = (f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' "
         f"and name='{name.replace(chr(39), chr(39)+chr(39))}' and trashed=false")
    params = urllib.parse.urlencode({
        "q": q,
        "corpora": "allDrives",
        "includeItemsFromAllDrives": "true",
        "supportsAllDrives": "true",
        "fields": "files(id)",
    })
    url = f"https://www.googleapis.com/drive/v3/files?{params}"
    result = _drive_request("GET", url, token)
    files = result.get("files", [])
    if files:
        return files[0]["id"]
    body = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
        "driveId": OPC_DRIVE_ID,
    }
    created = _drive_request("POST",
        "https://www.googleapis.com/drive/v3/files?supportsAllDrives=true",
        token, body)
    return created["id"]


def _move_file(token: str, file_id: str, new_parent_id: str, old_parent_id: str) -> str:
    """Move file to new_parent, removing old_parent. Returns new web-view URL."""
    params = urllib.parse.urlencode({
        "addParents": new_parent_id,
        "removeParents": old_parent_id,
        "supportsAllDrives": "true",
        "fields": "id,webViewLink",
    })
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?{params}"
    result = _drive_request("PATCH", url, token, body={})
    return result.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")


def _get_file_metadata(token: str, file_id: str) -> dict:
    params = urllib.parse.urlencode({
        "fields": "id,name,mimeType,createdTime,parents",
        "supportsAllDrives": "true",
    })
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?{params}"
    return _drive_request("GET", url, token)


# ── Sheets helpers ───────────────────────────────────────────────────────────

def _sheets_get(token: str, range_: str) -> list:
    enc = urllib.parse.quote(range_, safe="!:'")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{enc}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp.get("values", [])


def _sheets_append(token: str, tab: str, rows: list):
    enc = urllib.parse.quote(f"'{tab}'!A:Z", safe="!:'")
    url = (f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{enc}"
           f":append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS")
    body = json.dumps({"values": rows}).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    urllib.request.urlopen(req).read()


def _sheets_update(token: str, cell_range: str, values: list):
    enc = urllib.parse.quote(cell_range, safe="!:'")
    url = (f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{enc}"
           f"?valueInputOption=USER_ENTERED")
    body = json.dumps({"values": values}).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="PUT")
    urllib.request.urlopen(req).read()


# ── Pipeline failure log ─────────────────────────────────────────────────────

def log_pipeline_failure(token: str, stage: str, error: str):
    """Append a row to Pipeline Failures tab. Non-fatal if this itself errors."""
    try:
        run_url = (f"https://github.com/priihigashi/oak-park-ai-hub/actions/runs/{_GHA_RUN_ID}"
                   if _GHA_RUN_ID else "")
        row = [
            datetime.utcnow().isoformat() + "Z",
            _SCRIPT,
            _GHA_RUN_ID,
            stage,
            str(error)[:500],
            run_url,
            "",  # RESOLVED (blank = open)
        ]
        _sheets_append(token, FAILURES_TAB, [row])
    except Exception as e:
        print(f"  [warn] Could not log to Pipeline Failures: {e}")


# ── Catalog dedup ─────────────────────────────────────────────────────────────

def get_cataloged_file_ids(token: str) -> set:
    """Return the set of Drive file IDs already in the catalog (column U = File ID)."""
    try:
        rows = _sheets_get(token, f"'{CATALOG_TAB}'!1:1")
        if not rows:
            return set()
        header = rows[0]
        # Find the 'File ID' column index
        try:
            file_id_col = header.index("File ID")
        except ValueError:
            return set()  # column not yet added
        col_letter = chr(ord('A') + file_id_col)
        data = _sheets_get(token, f"'{CATALOG_TAB}'!{col_letter}:{col_letter}")
        return {r[0] for r in data[1:] if r}
    except Exception as e:
        print(f"  [warn] Could not read cataloged file IDs: {e}")
        return set()


def ensure_catalog_new_columns(token: str):
    """Append new column headers to Photo Catalog if not already present. Idempotent."""
    rows = _sheets_get(token, f"'{CATALOG_TAB}'!1:1")
    if not rows:
        print("  [warn] Photo Catalog header row not found — skipping column migration")
        return
    existing = rows[0]
    missing = [c for c in NEW_COL_NAMES if c not in existing]
    if not missing:
        return
    next_idx = len(existing)
    start = chr(ord('A') + next_idx)
    end   = chr(ord('A') + next_idx + len(missing) - 1)
    _sheets_update(token, f"'{CATALOG_TAB}'!{start}1:{end}1", [missing])
    print(f"  [catalog] Added columns: {missing}")


def append_catalog_row(token: str, row: list):
    _sheets_append(token, CATALOG_TAB, [row])


# ── Video metadata via ffprobe ───────────────────────────────────────────────

def _download_first_mb(token: str, file_id: str) -> bytes:
    """Download the first 1 MB of a Drive file for ffprobe metadata extraction."""
    url = (f"https://www.googleapis.com/drive/v3/files/{file_id}"
           f"?alt=media&supportsAllDrives=true")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Range": "bytes=0-1048575",
    })
    try:
        resp = urllib.request.urlopen(req)
        return resp.read()
    except urllib.error.HTTPError as e:
        if e.code in (206, 200):
            return e.read()
        raise


def _run_ffprobe(data: bytes) -> dict:
    """Run ffprobe on bytes piped through stdin. Returns parsed JSON tags."""
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", "-"],
            input=data, capture_output=True, timeout=15
        )
        if proc.returncode != 0:
            return {}
        return json.loads(proc.stdout.decode())
    except Exception:
        return {}


def _parse_iso6709(tag: str):
    """Parse com.apple.quicktime.location.ISO6709 → (lat, lon) or None."""
    # Format: +26.1134-080.1951+003.952/ or +26.1134-080.1951/
    m = re.match(r'^([+-]\d+\.?\d*)([+-]\d+\.?\d*)', tag.strip())
    if m:
        try:
            return float(m.group(1)), float(m.group(2))
        except ValueError:
            pass
    return None


def _parse_creation_date(raw: str) -> str:
    """Return YYYY-MM-DD or empty string from a ffprobe date tag."""
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw[:19], fmt[:len(raw[:19])])
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    # ISO-8601 prefix
    m = re.match(r'^(\d{4}-\d{2}-\d{2})', raw)
    if m:
        return m.group(1)
    return ""


def extract_video_metadata(token: str, file_id: str, drive_created: str) -> dict:
    """
    Returns:
        capture_date: YYYY-MM-DD  (flagged_upload if from Drive createdTime)
        gps:          (lat, lon) or None
        date_source:  'quicktime' | 'creation_time' | 'drive_upload'
    """
    result = {"capture_date": "", "gps": None, "date_source": "drive_upload"}
    try:
        data = _download_first_mb(token, file_id)
        info = _run_ffprobe(data)
    except Exception as e:
        print(f"    [ffprobe] Could not read metadata: {e}")
        # Fallback to Drive createdTime
        if drive_created:
            result["capture_date"] = _parse_creation_date(drive_created)
            result["date_source"]  = "drive_upload"
        return result

    tags = {}
    fmt = info.get("format", {})
    tags.update(fmt.get("tags", {}))
    for stream in info.get("streams", []):
        tags.update(stream.get("tags", {}))

    # GPS: prefer Apple QuickTime tag
    gps_tag = tags.get("com.apple.quicktime.location.ISO6709", "")
    if gps_tag:
        result["gps"] = _parse_iso6709(gps_tag)

    # Date: prefer com.apple.quicktime.creationdate (local time w/ tz)
    qt_date = tags.get("com.apple.quicktime.creationdate", "")
    if qt_date:
        parsed = _parse_creation_date(qt_date)
        if parsed:
            result["capture_date"] = parsed
            result["date_source"]  = "quicktime"
            return result

    # Fallback: creation_time (UTC)
    ct = tags.get("creation_time", "")
    if ct:
        parsed = _parse_creation_date(ct)
        if parsed:
            result["capture_date"] = parsed
            result["date_source"]  = "creation_time"
            return result

    # Last resort: Drive createdTime (upload time — flag it)
    if drive_created:
        result["capture_date"] = _parse_creation_date(drive_created)
        result["date_source"]  = "drive_upload"
    return result


# ── Project matching ─────────────────────────────────────────────────────────

MATCH_RADIUS_M = 150.0


def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def load_project_registry(token: str) -> list:
    """
    Build a registry of {name, lat, lon, folder_id} from the Projects folder.
    Reads Drive imageMediaMetadata.location from the first geotagged file in each
    project subfolder. Falls back to an empty list if Drive returns no GPS.
    """
    registry = []
    try:
        projects = _list_files(token, OPC_DRIVE_ID,
                               "application/vnd.google-apps.folder")
        for proj in projects:
            # Look for the first file that has GPS in imageMediaMetadata
            children = _list_files(token, proj["id"])
            for child in children[:20]:
                params = urllib.parse.urlencode({
                    "fields": "imageMediaMetadata",
                    "supportsAllDrives": "true",
                })
                url = f"https://www.googleapis.com/drive/v3/files/{child['id']}?{params}"
                try:
                    meta = _drive_request("GET", url, token)
                    loc = meta.get("imageMediaMetadata", {}).get("location", {})
                    lat = loc.get("latitude")
                    lon = loc.get("longitude")
                    if lat is not None and lon is not None:
                        registry.append({
                            "name":      proj["name"],
                            "folder_id": proj["id"],
                            "lat":       lat,
                            "lon":       lon,
                        })
                        break
                except Exception:
                    continue
    except Exception as e:
        print(f"  [registry] Could not build project registry: {e}")
    return registry


def match_project(lat: float, lon: float, registry: list):
    """Return (project_name, folder_id) or (None, None) if nothing within radius."""
    best_dist = float("inf")
    best = None
    for proj in registry:
        d = _haversine_m(lat, lon, proj["lat"], proj["lon"])
        if d < best_dist:
            best_dist = d
            best = proj
    if best and best_dist <= MATCH_RADIUS_M:
        return best["name"], best["folder_id"]
    return None, None


# ── Destination folder logic ─────────────────────────────────────────────────

def resolve_destination(token: str, capture_date: str, project_name: str,
                         date_source: str) -> tuple:
    """
    Create (if needed) and return (day_folder_id, day_folder_link, subfolder_id).
    Structure under DROP_FOLDER:
      YYYY-MM-DD/
        ProjectName/    ← GPS-matched
        _no-location/   ← no GPS or no match
        _flagged-date/  ← date came from drive_upload (unreliable capture date)
    """
    if not capture_date:
        capture_date = date.today().isoformat()

    day_name = capture_date
    if date_source == "drive_upload":
        day_name = f"{capture_date}_flagged-upload-date"

    day_folder_id = _ensure_folder(token, day_name, DROP_FOLDER)
    day_folder_link = f"https://drive.google.com/drive/folders/{day_folder_id}"

    if project_name:
        sub_id = _ensure_folder(token, project_name, day_folder_id)
    else:
        sub_id = _ensure_folder(token, "_no-location", day_folder_id)

    return day_folder_id, day_folder_link, sub_id


# ── Collision-safe file naming ────────────────────────────────────────────────

def safe_name(token: str, original_name: str, dest_folder_id: str) -> str:
    """Return original_name unless a file with that name exists in dest_folder — then append _2, _3 …"""
    existing = {f["name"] for f in _list_files(token, dest_folder_id)}
    if original_name not in existing:
        return original_name
    base, ext = os.path.splitext(original_name)
    i = 2
    while True:
        candidate = f"{base}_{i}{ext}"
        if candidate not in existing:
            return candidate
        i += 1


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n🎬  OPC Media Sorter — {date.today()}")

    if not TOKEN_FILE or not os.path.exists(TOKEN_FILE):
        print("❌ SHEETS_TOKEN_PATH not set or file not found")
        sys.exit(1)

    failures = []

    try:
        token = _get_access_token()
    except Exception as e:
        print(f"❌ Auth failed: {e}")
        sys.exit(1)

    # Ensure new catalog columns exist
    try:
        ensure_catalog_new_columns(token)
    except Exception as e:
        print(f"  [warn] Column migration failed: {e}")

    # Load already-processed file IDs
    cataloged_ids = get_cataloged_file_ids(token)
    print(f"📊 Already cataloged: {len(cataloged_ids)} file IDs")

    # List videos in drop folder
    try:
        all_files = _list_files(token, DROP_FOLDER)
    except Exception as e:
        err = f"list_drop_folder: {e}"
        print(f"❌ {err}")
        log_pipeline_failure(token, "list_drop_folder", err)
        sys.exit(1)

    videos = [f for f in all_files if f.get("mimeType") in VIDEO_MIMES]
    new_videos = [f for f in videos if f["id"] not in cataloged_ids]
    print(f"📊 Videos in drop: {len(videos)}  |  New (unprocessed): {len(new_videos)}  |  Processing: min({len(new_videos)}, {MAX_PER_RUN})")

    if not new_videos:
        print("✅ Nothing new to sort")
        return

    # Build project registry for GPS matching
    print("🗺️  Loading project registry …")
    registry = load_project_registry(token)
    print(f"   {len(registry)} project(s) in registry")

    processed = 0
    for vid in new_videos[:MAX_PER_RUN]:
        print(f"\n  🎥  {vid['name']} ({vid['mimeType']})")
        try:
            # Extract metadata
            meta = extract_video_metadata(token, vid["id"], vid.get("createdTime", ""))
            capture_date = meta["capture_date"]
            gps          = meta["gps"]
            date_source  = meta["date_source"]

            gps_str      = f"{gps[0]:.6f},{gps[1]:.6f}" if gps else ""
            project_name = None
            project_fid  = None

            if gps:
                project_name, project_fid = match_project(gps[0], gps[1], registry)

            print(f"     date={capture_date} ({date_source})  gps={gps_str or 'none'}  project={project_name or 'unmatched'}")

            # Resolve / create destination folders
            day_folder_id, day_folder_link, dest_folder_id = resolve_destination(
                token, capture_date, project_name, date_source
            )

            # Move file (collision-safe)
            dest_name = safe_name(token, vid["name"], dest_folder_id)
            file_link = _move_file(token, vid["id"], dest_folder_id, DROP_FOLDER)

            sorter_status = "sorted"
            if not gps:
                sorter_status = "no-location"
            elif not project_name:
                sorter_status = "no-project-match"
            if date_source == "drive_upload":
                sorter_status += "_flagged-date"

            print(f"     ✅ moved → {day_folder_link}  status={sorter_status}")

            # Log to Photo Catalog
            # Existing columns A-T are left blank (no image analysis done here)
            # New columns U-Y: File ID | Media Type | GPS Lat,Lon | Day Folder Link | Sorter Status
            row = [
                date.today().isoformat(),   # A Date Added
                project_name or "",         # B Project Name
                "",                         # C Service Type
                vid["name"],                # D Filename
                file_link,                  # E Drive URL
                "",                         # F AI Description
                "",                         # G Phase
                "",                         # H Quality ⭐
                "",                         # I Enhanced?
                "No",                       # J Used In Post?
                capture_date,               # K Date Taken
                "No",                       # L Ideas Generated?
                "",                         # M Suggested Post Date
                "Video",                    # N Content Type
                "0",                        # O Times Used
                "",                         # P Room
                "",                         # Q Trade
                "",                         # R Materials
                "",                         # S Quality Flag
                "",                         # T Client Visible
                vid["id"],                  # U File ID
                "video",                    # V Media Type
                gps_str,                    # W GPS Lat,Lon
                day_folder_link,            # X Day Folder Link
                sorter_status,              # Y Sorter Status
            ]
            append_catalog_row(token, row)
            processed += 1
            time.sleep(0.5)

        except Exception as e:
            err_msg = f"{vid['name']}: {e}"
            print(f"     ⚠️  Error: {err_msg}")
            failures.append(err_msg)
            try:
                log_pipeline_failure(token, f"sort_file.{vid['id']}", err_msg)
            except Exception:
                pass

    print(f"\n✅ Done — {processed} videos sorted, {len(failures)} errors")

    if failures:
        print("❌ Failures logged to Pipeline Failures tab")
        sys.exit(1)


if __name__ == "__main__":
    main()
