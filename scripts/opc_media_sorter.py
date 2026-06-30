#!/usr/bin/env python3
"""
opc_media_sorter.py — Daily Job Video Auto-Sorter (Phase 1)

Reads new videos from Mike's drop folder, extracts capture date + GPS via
ffprobe (range read), moves each file to YYYY-MM-DD/ProjectName/ inside the
OPC shared drive, and logs a row to 📸 Photo Catalog (video columns only).
Images are handled separately by photo_catalog_cloud.py — this script is VIDEOS ONLY.

Env vars:
  SHEETS_TOKEN_PATH  — path to sheets_token.json (from SHEETS_TOKEN GitHub secret)

IDs (verified 2026-06-30 against OPC shared drive 0AJp3Phs0wIBOUk9PVA):
  Drop folder  : 1dNmFflB0yS8Qc9A1-mfbMCIHOVZzcndb  (parent = shared drive root)
  Projects ref : 1t7bKvdaHCSQjiDeqtYQH7cG7mGoB3Bbu  (GPS registry source)
  New Const.   : 1nYPQmO7xb1m_8EKo3E_QbSpoYfkbO1yJ  (inside Projects)
"""

import json, math, os, re, subprocess, sys, tempfile, time
from datetime import date, datetime, timezone
from pathlib import Path
import urllib.request, urllib.parse

# ── Verified IDs (spec Sec 4 + Sec 13, confirmed 2026-06-30) ─────────────────
SHARED_DRIVE_ID    = "0AJp3Phs0wIBOUk9PVA"
DROP_FOLDER_ID     = "1dNmFflB0yS8Qc9A1-mfbMCIHOVZzcndb"
PROJECTS_FOLDER_ID = "1t7bKvdaHCSQjiDeqtYQH7cG7mGoB3Bbu"

SHEET_ID    = "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU"
CATALOG_TAB = "📸 Photo Catalog"
FAIL_TAB    = "🚨 Pipeline Failures"

VIDEO_MIMES = {
    "video/mp4", "video/quicktime", "video/x-m4v",
    "video/3gpp", "video/avi", "video/x-msvideo",
}
MAX_PER_RUN    = 30
MATCH_RADIUS_M = 150        # project GPS match radius in meters
RANGE_BYTES    = 1_048_576  # 1 MB range read for moov atom

TOKEN_FILE_PATH = os.environ.get("SHEETS_TOKEN_PATH", "")
_failures: list[str] = []


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_access_token() -> str:
    td = json.loads(Path(TOKEN_FILE_PATH).read_text())
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


# ── Drive helpers (all calls use supportsAllDrives=True) ──────────────────────

def drive_list(token: str, folder_id: str, mime_prefix: str | None = None) -> list[dict]:
    q = f"'{folder_id}' in parents and trashed=false"
    if mime_prefix:
        q += f" and mimeType contains '{mime_prefix}'"
    params = urllib.parse.urlencode({
        "q": q,
        "corpora": "allDrives",
        "includeItemsFromAllDrives": "true",
        "supportsAllDrives": "true",
        "fields": "files(id,name,mimeType,createdTime,size,imageMediaMetadata)",
        "pageSize": "200",
    })
    req = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files?{params}",
        headers={"Authorization": f"Bearer {token}"},
    )
    return json.loads(urllib.request.urlopen(req).read()).get("files", [])


def drive_create_folder(token: str, name: str, parent_id: str) -> str:
    """Create a folder inside parent (shared drive). Returns new folder ID."""
    body = json.dumps({
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }).encode()
    req = urllib.request.Request(
        "https://www.googleapis.com/drive/v3/files?supportsAllDrives=true",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())["id"]


def drive_ensure_folder(token: str, name: str, parent_id: str) -> str:
    """Return existing folder ID or create it. Case-sensitive match."""
    children = drive_list(token, parent_id, "application/vnd.google-apps.folder")
    for f in children:
        if f["name"] == name:
            return f["id"]
    return drive_create_folder(token, name, parent_id)


def drive_move_file(token: str, file_id: str, new_parent: str, old_parent: str) -> None:
    """Move a file by updating its parents. Ensures no collision by renaming if needed."""
    params = urllib.parse.urlencode({
        "addParents":    new_parent,
        "removeParents": old_parent,
        "supportsAllDrives": "true",
        "fields": "id,name,parents",
    })
    body = json.dumps({}).encode()
    req = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?{params}",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="PATCH",
    )
    urllib.request.urlopen(req).read()


def drive_rename_file(token: str, file_id: str, new_name: str) -> None:
    body = json.dumps({"name": new_name}).encode()
    req = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?supportsAllDrives=true",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="PATCH",
    )
    urllib.request.urlopen(req).read()


def drive_range_read(token: str, file_id: str, num_bytes: int) -> bytes:
    """Read first num_bytes of a file using Range header (avoids full download)."""
    req = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&supportsAllDrives=true",
        headers={"Authorization": f"Bearer {token}", "Range": f"bytes=0-{num_bytes - 1}"},
    )
    try:
        return urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        if e.code == 416:  # range not satisfiable (file smaller than requested)
            req2 = urllib.request.Request(
                f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&supportsAllDrives=true",
                headers={"Authorization": f"Bearer {token}"},
            )
            return urllib.request.urlopen(req2).read()
        raise


# ── Sheets helpers ────────────────────────────────────────────────────────────

def _sheets_get(token: str, tab: str, range_a1: str) -> list[list]:
    enc = urllib.parse.quote(f"'{tab}'!{range_a1}", safe="!:'")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{enc}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    return json.loads(urllib.request.urlopen(req).read()).get("values", [])


def _sheets_append(token: str, tab: str, rows: list[list]) -> None:
    enc = urllib.parse.quote(f"'{tab}'!A:Z", safe="!:'")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{enc}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS"
    body = json.dumps({"values": rows}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    urllib.request.urlopen(req).read()


def get_cataloged_file_ids(token: str) -> set[str]:
    """Read File ID column (U = col 21, index 20) from Photo Catalog for dedup."""
    try:
        rows = _sheets_get(token, CATALOG_TAB, "U:U")
        return {r[0].strip() for r in rows[1:] if r and r[0].strip()}
    except Exception:
        return set()


def ensure_catalog_video_columns(token: str) -> None:
    """Append new video columns to Photo Catalog header if not already present. Idempotent."""
    NEW_COLS = ["File ID", "Media Type", "GPS lat,lon", "Day Folder Link", "Status"]
    try:
        rows = _sheets_get(token, CATALOG_TAB, "1:1")
        existing = rows[0] if rows else []
        missing = [c for c in NEW_COLS if c not in existing]
        if not missing:
            return
        next_idx = len(existing)
        start = _col_letter(next_idx)
        end = _col_letter(next_idx + len(missing) - 1)
        enc = urllib.parse.quote(f"'{CATALOG_TAB}'!{start}1:{end}1", safe="!:'")
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{enc}?valueInputOption=RAW"
        body = json.dumps({"values": [missing]}).encode()
        req = urllib.request.Request(
            url, data=body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="PUT",
        )
        urllib.request.urlopen(req).read()
        print(f"[catalog] Added header columns: {missing}")
    except Exception as e:
        print(f"[catalog] Warning — could not migrate header: {e}")


def _col_letter(idx: int) -> str:
    """0-based column index → A, B, ..., Z, AA, AB, ..."""
    result = ""
    idx += 1
    while idx:
        idx, rem = divmod(idx - 1, 26)
        result = chr(65 + rem) + result
    return result


def log_pipeline_failure(stage: str, error: str, token: str | None) -> None:
    _failures.append(f"{stage}: {error}")
    print(f"[FAILURE] {stage}: {error}", file=sys.stderr)
    if not token:
        return
    try:
        row = [date.today().isoformat(), "opc_media_sorter", stage, str(error), "", ""]
        _sheets_append(token, FAIL_TAB, [row])
    except Exception as e2:
        print(f"[FAILURE] Could not log to sheet: {e2}", file=sys.stderr)


# ── Video metadata extraction ─────────────────────────────────────────────────

def extract_video_metadata(token: str, file_id: str, drive_created: str) -> dict:
    """
    Returns {
      'capture_date': 'YYYY-MM-DD',
      'date_source': 'quicktime' | 'upload-time',
      'lat': float | None,
      'lon': float | None,
    }
    Tries range-read + ffprobe first; falls back to Drive createdTime.
    """
    result = {
        "capture_date": None,
        "date_source":  "upload-time",
        "lat": None,
        "lon": None,
    }

    # Use Drive createdTime as baseline fallback (upload time — flagged as such)
    if drive_created:
        try:
            result["capture_date"] = drive_created[:10]
        except Exception:
            result["capture_date"] = date.today().isoformat()

    # Attempt metadata extraction via ffprobe on range read
    try:
        raw = drive_range_read(token, file_id, RANGE_BYTES)
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tf:
            tf.write(raw)
            tmp_path = tf.name
        try:
            proc = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", tmp_path],
                capture_output=True, text=True, timeout=15,
            )
            if proc.returncode == 0:
                meta = json.loads(proc.stdout)
                tags = meta.get("format", {}).get("tags", {})
                # Priority: com.apple.quicktime.creationdate > creation_time
                cdate = (tags.get("com.apple.quicktime.creationdate")
                         or tags.get("creation_time", ""))
                if cdate:
                    # Format: 2026-06-25T08:32:11-0400 or 2026-06-25T12:32:11.000000Z
                    cdate_clean = re.sub(r"(T[\d:.]+).*", r"\1", cdate)[:10]
                    result["capture_date"] = cdate_clean
                    result["date_source"] = "quicktime"
                # GPS: com.apple.quicktime.location.ISO6709
                gps_str = tags.get("com.apple.quicktime.location.ISO6709", "")
                if gps_str:
                    parsed = parse_iso6709(gps_str)
                    if parsed:
                        result["lat"], result["lon"] = parsed
        finally:
            os.unlink(tmp_path)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # ffprobe not available or timed out — use Drive fallback
    except Exception as e:
        print(f"  [meta] ffprobe warning: {e}")

    if not result["capture_date"]:
        result["capture_date"] = date.today().isoformat()
        result["date_source"] = "upload-time"

    return result


def parse_iso6709(s: str):
    """
    Parse ISO 6709 GPS string e.g. '+26.1134-080.1951+003.952/'
    Returns (lat, lon) floats or None.
    """
    m = re.match(r"([+-]\d+\.?\d*)([+-]\d+\.?\d*)", s)
    if not m:
        return None
    try:
        return float(m.group(1)), float(m.group(2))
    except ValueError:
        return None


# ── Project registry ──────────────────────────────────────────────────────────

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in meters between two GPS coordinates."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def load_project_registry(token: str) -> list[dict]:
    """
    Build project registry from GPS metadata of photos already in Projects folder.
    Each entry: {name, folder_id, lat, lon}
    Falls back to empty registry (no match → _needs-review) if none found.
    """
    registry = []
    try:
        project_folders = drive_list(token, PROJECTS_FOLDER_ID,
                                     "application/vnd.google-apps.folder")
        for pf in project_folders:
            images = drive_list(token, pf["id"])
            for img in images:
                loc = img.get("imageMediaMetadata", {}).get("location", {})
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                if lat is not None and lon is not None:
                    registry.append({
                        "name":      pf["name"],
                        "folder_id": pf["id"],
                        "lat":       lat,
                        "lon":       lon,
                    })
                    break  # one GPS anchor per project is enough
    except Exception as e:
        print(f"[registry] Warning loading project registry: {e}")
    print(f"[registry] {len(registry)} project(s) with GPS loaded")
    return registry


def match_project(lat: float, lon: float, registry: list[dict]) -> dict | None:
    """Return nearest project within MATCH_RADIUS_M, or None."""
    best = None
    best_dist = MATCH_RADIUS_M + 1
    for proj in registry:
        d = haversine(lat, lon, proj["lat"], proj["lon"])
        if d < best_dist:
            best_dist = d
            best = proj
    return best


# ── Collision-safe rename ─────────────────────────────────────────────────────

def safe_filename(token: str, parent_id: str, original_name: str) -> str:
    """Return a filename that doesn't collide in the target folder."""
    existing = {f["name"] for f in drive_list(token, parent_id)}
    if original_name not in existing:
        return original_name
    stem, ext = os.path.splitext(original_name)
    suffix = 1
    while True:
        candidate = f"{stem}_{suffix}{ext}"
        if candidate not in existing:
            return candidate
        suffix += 1


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not TOKEN_FILE_PATH or not Path(TOKEN_FILE_PATH).exists():
        print("❌ SHEETS_TOKEN_PATH not set or file not found", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()
    print(f"\n🎥 OPC Media Sorter — {today}")

    token = get_access_token()

    # Ensure Photo Catalog has video columns (U–Y)
    ensure_catalog_video_columns(token)

    # Load already-cataloged file IDs (dedup key)
    cataloged_ids = get_cataloged_file_ids(token)
    print(f"[dedup] {len(cataloged_ids)} file IDs already cataloged")

    # Load project GPS registry
    registry = load_project_registry(token)

    # List videos in drop folder (top-level only — already-sorted date subfolders excluded)
    drop_files = drive_list(token, DROP_FOLDER_ID)
    new_videos = [
        f for f in drop_files
        if f.get("mimeType", "") in VIDEO_MIMES
        and f["id"] not in cataloged_ids
    ]
    print(f"[sort] {len(new_videos)} new video(s) to sort (max {MAX_PER_RUN})")

    catalog_rows = []

    for vid in new_videos[:MAX_PER_RUN]:
        fid   = vid["id"]
        fname = vid["name"]
        print(f"\n  → {fname}")

        try:
            # Step 1: extract metadata
            meta = extract_video_metadata(token, fid, vid.get("createdTime", ""))
            capture_date = meta["capture_date"]
            date_source  = meta["date_source"]
            lat, lon     = meta["lat"], meta["lon"]

            date_label = capture_date
            if date_source == "upload-time":
                date_label = f"⚠️upload-time:{capture_date}"
                print(f"     ⚠️  Stripped metadata — using upload date {capture_date}")

            # Step 2: resolve destination folder
            date_folder_id = drive_ensure_folder(token, capture_date, DROP_FOLDER_ID)
            date_folder_url = f"https://drive.google.com/drive/folders/{date_folder_id}"

            if lat is not None and lon is not None:
                gps_str = f"{lat:.6f},{lon:.6f}"
                matched = match_project(lat, lon, registry)
                if matched:
                    subfolder_name = matched["name"]
                    status = "sorted"
                else:
                    subfolder_name = "_no-location/_needs-review"
                    status = "needs-review"
                    print(f"     ⚠️  GPS present but no project within {MATCH_RADIUS_M}m")
            else:
                gps_str = ""
                subfolder_name = "_no-location"
                status = "no-location"

            # Handle two-level subfolder (_no-location/_needs-review)
            if "/" in subfolder_name:
                parts = subfolder_name.split("/")
                dest_id = date_folder_id
                for part in parts:
                    dest_id = drive_ensure_folder(token, part, dest_id)
            else:
                dest_id = drive_ensure_folder(token, subfolder_name, date_folder_id)

            # Step 3: ensure no filename collision, then move
            final_name = safe_filename(token, dest_id, fname)
            if final_name != fname:
                drive_rename_file(token, fid, final_name)
                print(f"     ↩  Renamed {fname} → {final_name} (collision)")

            drive_move_file(token, fid, dest_id, DROP_FOLDER_ID)
            drive_url = f"https://drive.google.com/file/d/{fid}/view"
            print(f"     ✅ {capture_date}/{subfolder_name} | gps={gps_str or 'none'} | status={status}")

            # Step 4: catalog row (video columns extend existing header to U:Y)
            catalog_rows.append([
                today,          # A Date Added
                subfolder_name.replace("/_needs-review", "").replace("_no-location", "no-location"),  # B Project Name
                "Video",        # C Service Type
                final_name,     # D Filename
                drive_url,      # E Drive URL
                "",             # F AI Description (not run for videos)
                "",             # G Phase
                "",             # H Quality ⭐
                "No",           # I Enhanced?
                "No",           # J Used In Post?
                date_label,     # K Date Taken
                "No",           # L Ideas Generated?
                "",             # M Suggested Post Date
                "Video",        # N Content Type
                "0",            # O Times Used
                "",             # P Room
                "",             # Q Trade
                "",             # R Materials
                "",             # S Quality Flag
                "",             # T Client Visible
                fid,            # U File ID  ← dedup key
                "video",        # V Media Type
                gps_str,        # W GPS lat,lon
                date_folder_url,# X Day Folder Link
                status,         # Y Status
            ])

        except Exception as e:
            log_pipeline_failure(f"sort:{fname}", str(e), token)
            time.sleep(1)
            continue

        time.sleep(0.3)

    # Bulk append catalog rows
    if catalog_rows:
        try:
            _sheets_append(token, CATALOG_TAB, catalog_rows)
            print(f"\n✅ Logged {len(catalog_rows)} video(s) to Photo Catalog")
        except Exception as e:
            log_pipeline_failure("catalog_write", str(e), token)

    summary = f"{len(catalog_rows)} sorted / {len(_failures)} failure(s)"
    print(f"\n📊 Done — {summary}")

    if _failures:
        print(f"\n❌ {len(_failures)} failure(s) logged to {FAIL_TAB}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
