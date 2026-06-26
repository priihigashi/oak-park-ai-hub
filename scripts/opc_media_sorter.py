#!/usr/bin/env python3
"""
opc_media_sorter.py — Sort Mike's job video dumps into date/project subfolders.

Reads from DROP_FOLDER_ID, moves each new VIDEO into:
  DROP_FOLDER/YYYY-MM-DD/<ProjectName>/   (GPS within 150 m of a known project)
  DROP_FOLDER/YYYY-MM-DD/_needs-review/   (GPS present but no project match)
  DROP_FOLDER/YYYY-MM-DD/_no-location/    (no GPS in file)

Logs each sorted video to "📸 Photo Catalog" in Ideas & Inbox (adds 5 new columns).
Deduplicates by Drive File ID — not filename (collision-proof across jobs).
VIDEOS ONLY — images remain the responsibility of photo_catalog_cloud.py.

Env vars (same pattern as photo_catalog_cloud.py):
  SHEETS_TOKEN_PATH  — path to sheets_token.json written from SHEETS_TOKEN secret
  GITHUB_RUN_ID      — injected automatically by GitHub Actions
"""

import json, math, os, re, subprocess, sys, tempfile, time, urllib.parse, urllib.request
from datetime import datetime, timezone, date

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
OPC_SHARED_DRIVE = "0AJp3Phs0wIBOUk9PVA"
DROP_FOLDER_ID   = "1dNmFflB0yS8Qc9A1-mfbMCIHOVZzcndb"   # "Daily Job Videos - DROP HERE (Mike)"
PROJECTS_FOLDER  = "1t7bKvdaHCSQjiDeqtYQH7cG7mGoB3Bbu"   # OPC Projects folder
SHEET_ID         = "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU"  # Ideas & Inbox
CATALOG_TAB      = "📸 Photo Catalog"
FAILURES_TAB     = "🚨 Pipeline Failures"
WORKFLOW_NAME    = "opc_media_sorter.yml"
MATCH_RADIUS_M   = 150   # metres — nearest project within this radius counts as a match
MAX_PER_RUN      = 100   # safety cap; raise after first stable run

TOKEN_FILE_PATH  = os.environ.get("SHEETS_TOKEN_PATH", "")
GHA_RUN_ID       = os.environ.get("GITHUB_RUN_ID", "")

VIDEO_MIMES = {
    "video/mp4", "video/quicktime", "video/x-msvideo",
    "video/3gpp", "video/3gpp2", "video/webm", "video/mpeg",
    "video/x-ms-wmv",
}

# 5 new sorter-only columns appended AFTER the 20 existing photo catalog columns.
# photo_catalog_cloud.py appends to A:T — it never touches U:Y — so this is safe.
NEW_SORTER_COLS = ["File ID", "Media Type", "GPS", "Day Folder Link", "Sort Status"]

PIPELINE_FAILURES = []


# ── AUTH ──────────────────────────────────────────────────────────────────────
def _refresh_token():
    td = json.loads(open(TOKEN_FILE_PATH).read())
    data = urllib.parse.urlencode({
        "client_id":     td["client_id"],
        "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"],
        "grant_type":    "refresh_token",
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    ).read())
    return resp["access_token"], td


def get_credentials():
    from google.oauth2.credentials import Credentials
    access_token, td = _refresh_token()
    return Credentials(
        token=access_token,
        refresh_token=td["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=td["client_id"],
        client_secret=td["client_secret"],
        scopes=td.get("scopes", [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ]),
    )


def get_sheets_token():
    access_token, _ = _refresh_token()
    return access_token


# ── DRIVE HELPERS ─────────────────────────────────────────────────────────────
def list_folder(drive, folder_id, mime_types=None):
    """List direct children of a folder. mime_types: set of strings or None for all."""
    results, page_token = [], None
    while True:
        kwargs = dict(
            q=f"'{folder_id}' in parents and trashed=false",
            corpora="allDrives",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields="nextPageToken,files(id,name,mimeType,createdTime,imageMediaMetadata)",
            pageSize=200,
        )
        if page_token:
            kwargs["pageToken"] = page_token
        resp = drive.files().list(**kwargs).execute()
        results.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    if mime_types:
        results = [f for f in results if f.get("mimeType") in mime_types]
    return results


def get_or_create_folder(drive, name, parent_id, folder_cache):
    """Return folder ID for name under parent_id, creating it if absent. Cached."""
    key = (parent_id, name)
    if key in folder_cache:
        return folder_cache[key]
    existing = list_folder(drive, parent_id,
                           mime_types={"application/vnd.google-apps.folder"})
    for f in existing:
        if f["name"] == name:
            folder_cache[key] = f["id"]
            return f["id"]
    folder = drive.files().create(
        body={"name": name,
              "mimeType": "application/vnd.google-apps.folder",
              "parents": [parent_id]},
        fields="id",
        supportsAllDrives=True,
    ).execute()
    folder_cache[key] = folder["id"]
    return folder["id"]


def move_file(drive, file_id, new_parent_id, old_parent_id):
    """Move file to new_parent_id (same shared drive — atomic parent swap)."""
    drive.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=old_parent_id,
        supportsAllDrives=True,
        fields="id,parents",
    ).execute()


def rename_file(drive, file_id, new_name):
    drive.files().update(
        fileId=file_id,
        body={"name": new_name},
        supportsAllDrives=True,
        fields="id",
    ).execute()


# ── SHEETS HELPERS ────────────────────────────────────────────────────────────
def _col_letter(idx):
    """0-based column index → letter (A=0, Z=25, AA=26, …)."""
    result, idx = "", idx + 1
    while idx:
        idx, rem = divmod(idx - 1, 26)
        result = chr(65 + rem) + result
    return result


def _sheets_req(token, method, range_, body=None, extra_params=""):
    enc = urllib.parse.quote(range_, safe="!:'")
    url = (f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
           f"/values/{enc}{extra_params}")
    kwargs = {"headers": {"Authorization": f"Bearer {token}"}}
    if body is not None:
        kwargs["data"] = json.dumps(body).encode()
        kwargs["headers"]["Content-Type"] = "application/json"
    req = urllib.request.Request(url, method=method, **kwargs)
    return json.loads(urllib.request.urlopen(req).read())


def sheets_get(token, range_):
    return _sheets_req(token, "GET", range_)


def sheets_append(token, range_, values):
    _sheets_req(token, "POST", range_,
                body={"values": values},
                extra_params=":append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS")


def sheets_put(token, range_, values):
    _sheets_req(token, "PUT", range_,
                body={"values": values},
                extra_params="?valueInputOption=RAW")


def ensure_sorter_columns(token):
    """Add NEW_SORTER_COLS to the Photo Catalog header if missing. Returns 0-based index of 'File ID'."""
    result = sheets_get(token, f"'{CATALOG_TAB}'!1:1")
    existing = [c for row in result.get("values", []) for c in row]
    if "File ID" in existing:
        return existing.index("File ID")
    missing = [c for c in NEW_SORTER_COLS if c not in existing]
    if not missing:
        return existing.index("File ID") if "File ID" in existing else len(existing)
    next_idx  = len(existing)
    start_col = _col_letter(next_idx)
    end_col   = _col_letter(next_idx + len(missing) - 1)
    sheets_put(token, f"'{CATALOG_TAB}'!{start_col}1:{end_col}1", [missing])
    print(f"[catalog] Added sorter columns: {missing}")
    return next_idx


def get_cataloged_file_ids(token, file_id_col_idx):
    """Return set of Drive File IDs already in Photo Catalog (strong dedup)."""
    col = _col_letter(file_id_col_idx)
    result = sheets_get(token, f"'{CATALOG_TAB}'!{col}:{col}")
    rows = result.get("values", [])
    return {r[0].strip() for r in rows[1:] if r and r[0].strip()}


# ── VIDEO METADATA ────────────────────────────────────────────────────────────
def extract_date_gps_ffprobe(path):
    """
    Run ffprobe on a local file. Returns (date_str, lat, lon) — any may be None.
    date_str is YYYY-MM-DD.
    """
    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            return None, None, None
        tags = json.loads(out.stdout).get("format", {}).get("tags", {})

        date_str = None
        for key in ("com.apple.quicktime.creationdate", "creation_time", "date"):
            val = tags.get(key, "")
            if val:
                try:
                    date_str = val[:10]
                    datetime.strptime(date_str, "%Y-%m-%d")
                    break
                except ValueError:
                    date_str = None

        lat, lon = None, None
        loc = tags.get("com.apple.quicktime.location.ISO6709", "")
        if loc:
            # e.g. "+26.1134-080.1951+003.952/"
            m = re.match(r'^([+-]\d+\.?\d*)([+-]\d+\.?\d*)', loc)
            if m:
                try:
                    lat, lon = float(m.group(1)), float(m.group(2))
                except ValueError:
                    pass

        return date_str, lat, lon
    except Exception:
        return None, None, None


def download_video_header(drive, file_id, dest_path):
    """Download first 2 MB of a video for metadata extraction via ffprobe."""
    import io
    from googleapiclient.http import MediaIoBaseDownload
    request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    request.headers["Range"] = "bytes=0-2097151"
    buf = io.BytesIO()
    try:
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    except Exception:
        pass  # HTTP 206 is normal for range requests; proceed with what we got
    open(dest_path, "wb").write(buf.getvalue())


# ── PROJECT REGISTRY ──────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlam = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def build_project_registry(drive):
    """
    Scan PROJECTS_FOLDER subfolders. For each project, look at contained files for
    Drive imageMediaMetadata.location. Returns {project_name: (lat, lon)}.
    An empty dict is valid — matching simply routes everything to _no-location.
    """
    registry = {}
    try:
        projects = list_folder(drive, PROJECTS_FOLDER,
                               mime_types={"application/vnd.google-apps.folder"})
        for proj in projects:
            kids = drive.files().list(
                q=f"'{proj['id']}' in parents and trashed=false",
                corpora="allDrives",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                fields="files(id,name,mimeType,imageMediaMetadata)",
                pageSize=50,
            ).execute().get("files", [])
            for kid in kids:
                loc = kid.get("imageMediaMetadata", {}).get("location", {})
                lat, lon = loc.get("latitude"), loc.get("longitude")
                if lat is not None and lon is not None:
                    registry[proj["name"]] = (float(lat), float(lon))
                    break  # one GPS anchor per project is enough
    except Exception as e:
        print(f"⚠️  Project registry build failed (non-fatal): {e}")
    print(f"[registry] {len(registry)} project(s) with GPS: {list(registry.keys()) or 'none yet'}")
    return registry


def match_project(lat, lon, registry):
    """Return (project_name, dist_m) for nearest project ≤ MATCH_RADIUS_M, or (None, dist_m)."""
    best_name, best_dist = None, float("inf")
    for name, (plat, plon) in registry.items():
        d = haversine(lat, lon, plat, plon)
        if d < best_dist:
            best_dist, best_name = d, name
    return (best_name, best_dist) if best_dist <= MATCH_RADIUS_M else (None, best_dist)


# ── PIPELINE FAILURE LOGGING ──────────────────────────────────────────────────
def log_pipeline_failure(stage, error, token=None):
    PIPELINE_FAILURES.append({"stage": stage, "error": str(error)[:500]})
    print(f"  ❌ FAILURE [{stage}]: {str(error)[:200]}")
    if not token:
        return
    try:
        run_url = (
            f"https://github.com/priihigashi/oak-park-ai-hub/actions/runs/{GHA_RUN_ID}"
            if GHA_RUN_ID else ""
        )
        sheets_append(token, f"'{FAILURES_TAB}'!A:H", [[
            datetime.now(timezone.utc).isoformat(),
            WORKFLOW_NAME,
            GHA_RUN_ID,
            stage,
            str(error)[:500],
            run_url,
            "",  # RESOLVED
            "",  # NOTE
        ]])
    except Exception as e:
        print(f"  (failure-log write itself failed: {e})")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    if not TOKEN_FILE_PATH or not os.path.exists(TOKEN_FILE_PATH):
        print("❌ SHEETS_TOKEN_PATH not set or file not found")
        sys.exit(1)

    print(f"\n🎬  OPC Media Sorter — {date.today()}")
    creds = get_credentials()
    from googleapiclient.discovery import build as gapi_build
    drive = gapi_build("drive", "v3", credentials=creds)
    token = get_sheets_token()

    # Ensure new catalog columns exist; get 0-based index of "File ID"
    file_id_col_idx = ensure_sorter_columns(token)

    # Load already-processed file IDs (strong dedup)
    known_ids = get_cataloged_file_ids(token, file_id_col_idx)
    print(f"📊 Already cataloged: {len(known_ids)} video File IDs")

    # Build project GPS registry from existing project folders
    registry = build_project_registry(drive)

    # List all direct children of drop folder; filter to new videos only
    all_files = list_folder(drive, DROP_FOLDER_ID)
    videos = [
        f for f in all_files
        if f.get("mimeType") in VIDEO_MIMES and f["id"] not in known_ids
    ]
    print(f"🎬 New videos to sort: {len(videos)} (max {MAX_PER_RUN} this run)")
    if not videos:
        print("✅ Nothing to do.")
        return

    folder_cache  = {}
    catalog_rows  = []
    today_iso     = date.today().isoformat()

    for vid in videos[:MAX_PER_RUN]:
        fname, fid = vid["name"], vid["id"]
        print(f"\n  → {fname}")

        try:
            # Download first 2 MB for ffprobe metadata extraction
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                download_video_header(drive, fid, tmp_path)
                date_str, lat, lon = extract_date_gps_ffprobe(tmp_path)
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

            # Date fallback — flag upload-time dates so they don't get silently trusted
            date_flag = ""
            if not date_str:
                date_str  = vid.get("createdTime", today_iso)[:10]
                date_flag = " [upload-time, not capture-time]"
                print(f"     ⚠️  No metadata date → using upload date {date_str}")
            else:
                print(f"     📅 Date: {date_str}")

            # GPS → project matching
            if lat is not None and lon is not None:
                print(f"     🌐 GPS: {lat:.4f}, {lon:.4f}")
                project_name, dist_m = match_project(lat, lon, registry)
                if project_name:
                    subfolder_name = project_name
                    sort_status    = "sorted"
                    print(f"     📌 Project: {project_name} ({dist_m:.0f} m)")
                else:
                    subfolder_name = "_needs-review"
                    sort_status    = "needs-review"
                    print(f"     ⚠️  No project within {MATCH_RADIUS_M} m (nearest {dist_m:.0f} m)")
                gps_str = f"{lat:.6f},{lon:.6f}"
            else:
                subfolder_name = "_no-location"
                sort_status    = "no-location"
                gps_str        = ""
                print("     ⚠️  No GPS — routing to _no-location")

            # Create YYYY-MM-DD and project subfolders under the drop folder
            date_folder_id = get_or_create_folder(drive, date_str, DROP_FOLDER_ID, folder_cache)
            dest_folder_id = get_or_create_folder(drive, subfolder_name, date_folder_id, folder_cache)

            # Resolve name collisions in destination — never overwrite
            dest_children   = {f["name"] for f in list_folder(drive, dest_folder_id)}
            final_name      = fname
            if fname in dest_children:
                stem, ext = os.path.splitext(fname)
                suffix = 1
                while f"{stem}_{suffix}{ext}" in dest_children:
                    suffix += 1
                final_name = f"{stem}_{suffix}{ext}"
                rename_file(drive, fid, final_name)

            # Move file (atomic parent swap — no copy, single source of truth)
            move_file(drive, fid, dest_folder_id, DROP_FOLDER_ID)

            drive_url      = f"https://drive.google.com/file/d/{fid}/view"
            day_folder_url = f"https://drive.google.com/drive/folders/{date_folder_id}"
            print(f"     ✅ Moved → {date_str}/{subfolder_name}/{final_name}")

            # Catalog row — A:T mirrors photo catalog layout; U:Y are new sorter columns.
            # photo_catalog_cloud.py appends rows of 20 values to A:T and never reads U:Y.
            catalog_rows.append([
                today_iso,                      # A Date Added
                subfolder_name.lstrip("_"),     # B Project Name
                "Video",                        # C Service Type
                final_name,                     # D Filename
                drive_url,                      # E Drive URL
                "",                             # F AI Description (not run for videos)
                "",                             # G Phase
                "",                             # H Quality ⭐
                "No",                           # I Enhanced?
                "No",                           # J Used In Post?
                date_str + date_flag,           # K Date Taken
                "No",                           # L Ideas Generated?
                "",                             # M Suggested Post Date
                "Video",                        # N Content Type
                "0",                            # O Times Used
                "",                             # P Room
                "",                             # Q Trade
                "",                             # R Materials
                "",                             # S Quality Flag
                "",                             # T Client Visible
                fid,                            # U File ID
                "video",                        # V Media Type
                gps_str,                        # W GPS lat,lon
                day_folder_url,                 # X Day Folder Link
                sort_status,                    # Y Sort Status
            ])
            time.sleep(0.3)

        except Exception as e:
            log_pipeline_failure(f"sort/{fname}", e, token)

    # Write all catalog rows in one API call
    if catalog_rows:
        try:
            sheets_append(token, f"'{CATALOG_TAB}'!A:Y", catalog_rows)
            print(f"\n✅ Logged {len(catalog_rows)} video(s) to Photo Catalog")
        except Exception as e:
            log_pipeline_failure("catalog_append", e, token)

    if PIPELINE_FAILURES:
        print(f"\n🚨 {len(PIPELINE_FAILURES)} failure(s) — see {FAILURES_TAB} tab")
        sys.exit(1)
    else:
        print("\n✅ OPC Media Sorter complete — no failures")


if __name__ == "__main__":
    main()
