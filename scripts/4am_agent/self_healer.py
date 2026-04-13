"""
self_healer.py — End-of-run auto-fix for failed modules.
Runs last in main.py after everything else.

Flow per failure:
  transient (timeout/network) → log, notify, retry tomorrow
  script error (SyntaxError etc) → Haiku writes minimal fix → GitHub PR if confident
  config error (auth/missing key) → Calendar task with exact steps
  unknown → YouTube research loop + Calendar task

Dedup state files (W1/W2 fix):
  healed_modules.json    — tracks Calendar tasks created per module (skip if <7 days)
  researched_modules.json — tracks research triggers per module (skip if <7 days)
"""
import os, json, base64, requests
import pytz
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import anthropic

FAILURES_FILE    = ".github/agent_state/module_failures.json"
HEALED_FILE      = ".github/agent_state/healed_modules.json"
RESEARCHED_FILE  = ".github/agent_state/researched_modules.json"
GITHUB_REPO      = "priihigashi/oak-park-ai-hub"
GITHUB_TOKEN     = os.environ.get("GITHUB_TOKEN", "")
et               = pytz.timezone("America/New_York")
client           = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SCOPES = ["https://www.googleapis.com/auth/calendar"]

TRANSIENT = ["timeout", "connection", "503", "502", "rate limit", "429", "network", "socket"]
CONFIG    = ["not found", "missing secret", "401", "403", "credential", "permission", "forbidden"]
SCRIPT    = ["syntaxerror", "attributeerror", "keyerror", "typeerror", "nameerror",
             "indexerror", "valueerror", "jsondecodeerror", "json.loads"]

DEDUP_DAYS = 7


def _creds():
    return service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SA_KEY"]), scopes=SCOPES
    )


def _gh_headers():
    return {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}


# ─── GitHub state helpers (W1/W2 fix) ─────────────────────────────────────────

def _load_from_github(file_path):
    """Load JSON state file from GitHub. Returns {} if not found."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    r = requests.get(url, headers=_gh_headers())
    if r.status_code == 200:
        try:
            return json.loads(base64.b64decode(r.json()["content"]).decode())
        except Exception:
            return {}
    return {}


def _push_to_github(file_path, data):
    """Push JSON state file to GitHub."""
    url      = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    b64      = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
    existing = requests.get(url, headers=_gh_headers())
    payload  = {
        "message": f"agent: update {file_path.split('/')[-1]} [{datetime.now(et).strftime('%Y-%m-%d')}]",
        "content": b64,
    }
    if existing.status_code == 200:
        payload["sha"] = existing.json()["sha"]
    r = requests.put(url, headers=_gh_headers(), json=payload)
    if r.status_code not in (200, 201):
        print(f"[self_healer] WARNING: push failed for {file_path}: {r.status_code}")


def _days_since(date_str):
    """Return days since a YYYY-MM-DD string, or 999 if unparseable."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=et)
        return (datetime.now(et) - d).days
    except Exception:
        return 999


# ─── Categorization ───────────────────────────────────────────────────────────

def _categorize(error, tb):
    s = (error + tb).lower()
    if any(p in s for p in TRANSIENT): return "transient"
    if any(p in s for p in CONFIG):    return "config"
    if any(p in s for p in SCRIPT):    return "script"
    return "unknown"


def _haiku_fix(module_name, error, tb):
    """Ask Haiku for a minimal fix. Returns fix dict or confidence=0."""
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": f"""Python module failed in GitHub Actions.
Module: {module_name}
Error: {error}
Traceback: {tb[:1500]}

Write the MINIMAL fix (1-5 lines). Do not rewrite the module.
Return JSON only:
{{"confidence": 0-100, "fix_description": "one sentence",
  "file_to_edit": "scripts/4am_agent/{module_name}.py",
  "old_code": "exact string to replace", "new_code": "replacement"}}
If confidence < 70, return {{"confidence": 0, "fix_description": "cannot auto-fix",
  "file_to_edit": null, "old_code": null, "new_code": null}}"""}],
    )
    text = resp.content[0].text.strip()
    if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:   text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except Exception:
        return {"confidence": 0}


def _create_pr(module_name, fix, error):
    base = f"https://api.github.com/repos/{GITHUB_REPO}"
    try:
        main_sha = requests.get(f"{base}/git/ref/heads/main", headers=_gh_headers()).json()["object"]["sha"]
        fp       = fix["file_to_edit"]
        fr       = requests.get(f"{base}/contents/{fp}", headers=_gh_headers()).json()
        current  = base64.b64decode(fr["content"]).decode()
        if fix["old_code"] not in current:
            print(f"[self_healer] old_code not found in {fp} — skipping PR")
            return False
        new_content = current.replace(fix["old_code"], fix["new_code"], 1)
        branch = f"auto-fix/{module_name}_{datetime.now(et).strftime('%Y%m%d_%H%M')}"
        requests.post(f"{base}/git/refs", headers=_gh_headers(),
                      json={"ref": f"refs/heads/{branch}", "sha": main_sha})
        requests.put(f"{base}/contents/{fp}", headers=_gh_headers(), json={
            "message": f"auto-fix: {fix['fix_description']}",
            "content": base64.b64encode(new_content.encode()).decode(),
            "sha": fr["sha"], "branch": branch,
        })
        pr = requests.post(f"{base}/pulls", headers=_gh_headers(), json={
            "title": f"🔧 Auto-fix: {module_name} — {fix['fix_description']}",
            "body":  f"**Error:** `{error}`\n\n**Fix:** {fix['fix_description']}\n\n_Auto-generated by self_healer.py_",
            "head": branch, "base": "main",
        }).json()
        print(f"[self_healer] PR created: {pr.get('html_url', 'unknown')}")
        return True
    except Exception as e:
        print(f"[self_healer] PR failed: {e}")
        return False


def _calendar_task(calendar_svc, title, desc):
    date_str = datetime.now(et).strftime("%Y-%m-%d")
    try:
        calendar_svc.events().insert(
            calendarId="primary",
            body={"summary": title, "description": desc,
                  "start": {"date": date_str}, "end": {"date": date_str}, "colorId": "11"},
        ).execute()
    except Exception as e:
        print(f"[self_healer] Calendar failed: {e}")


def _trigger_research(module_name, error):
    """Trigger video-research.yml — self-learning research loop."""
    tool = module_name.replace("_", " ")
    queries = (
        f"how to implement {tool} with Claude code Python 2025,"
        f"{tool} {error[:40]} fix Python"
    )
    try:
        r = requests.post(
            f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/video-research.yml/dispatches",
            headers=_gh_headers(),
            json={"ref": "main", "inputs": {
                "topic": f"fix {tool} failure",
                "queries": queries,
                "max_per_query": "3",
            }},
        )
        ok = r.status_code == 204
        print(f"[self_healer] Research {'triggered' if ok else 'FAILED'} for {tool}")
        return ok
    except Exception as e:
        print(f"[self_healer] Research trigger error: {e}")
        return False


def run():
    """Main entry — reads failures and heals what it can. (C3: run_results param removed)"""
    if not os.path.exists(FAILURES_FILE):
        print("[self_healer] No failures file — nothing to heal.")
        return {"prs_created": 0, "researched": 0, "calendar_tasks": 0}

    with open(FAILURES_FILE) as f:
        failures = json.load(f)

    if not failures:
        print("[self_healer] No failures. All clear.")
        return {"prs_created": 0, "researched": 0, "calendar_tasks": 0}

    calendar_svc = build("calendar", "v3", credentials=_creds())

    # Load dedup state from GitHub (W1/W2 fix)
    today    = datetime.now(et).strftime("%Y-%m-%d")
    healed   = _load_from_github(HEALED_FILE)
    researched = _load_from_github(RESEARCHED_FILE)

    prs = cal_tasks = researched_count = 0

    for name, data in failures.items():
        err = data.get("error", "")
        tb  = data.get("traceback", "")
        cat = _categorize(err, tb)
        print(f"[self_healer] {name}: {cat} — {err[:80]}")

        if cat == "transient":
            print(f"[self_healer]   Transient — will retry tomorrow automatically.")

        elif cat == "script":
            fix = _haiku_fix(name, err, tb)
            if fix.get("confidence", 0) >= 70 and fix.get("old_code"):
                if _create_pr(name, fix, err):
                    prs += 1
                    continue
            # Not confident — research + calendar (with dedup)
            if _days_since(researched.get(name, {}).get("triggered", "")) >= DEDUP_DAYS:
                if _trigger_research(name, err):
                    researched[name] = {"triggered": today, "error": err[:100]}
                    researched_count += 1
            else:
                print(f"[self_healer]   Research already triggered for {name} — skipping.")

            if _days_since(healed.get(name, {}).get("task_created", "")) >= DEDUP_DAYS:
                _calendar_task(calendar_svc,
                    f"⚠️ SCRIPT ERROR: {name}",
                    f"Error: {err}\n\nAuto-fix attempted but not confident.\nResearch triggered — check Drive Resources for findings.")
                healed[name] = {"task_created": today, "type": "script"}
                cal_tasks += 1
            else:
                print(f"[self_healer]   Calendar task already exists for {name} — skipping.")

        elif cat == "config":
            if _days_since(healed.get(name, {}).get("task_created", "")) >= DEDUP_DAYS:
                _calendar_task(calendar_svc,
                    f"🔴 CONFIG FIX NEEDED: {name}",
                    f"Module failed with auth/config error.\n\nError: {err}\n\nCheck: GitHub secrets, API keys, sharing permissions on Google SA.")
                healed[name] = {"task_created": today, "type": "config"}
                cal_tasks += 1
            else:
                print(f"[self_healer]   Calendar task already exists for {name} — skipping.")

        else:  # unknown
            if _days_since(researched.get(name, {}).get("triggered", "")) >= DEDUP_DAYS:
                if _trigger_research(name, err):
                    researched[name] = {"triggered": today, "error": err[:100]}
                    researched_count += 1
            else:
                print(f"[self_healer]   Research already triggered for {name} — skipping.")

            if _days_since(healed.get(name, {}).get("task_created", "")) >= DEDUP_DAYS:
                _calendar_task(calendar_svc,
                    f"❓ UNKNOWN FAILURE: {name}",
                    f"Error: {err}\n\nResearch triggered. Check Drive Resources folder for findings from YouTube research.")
                healed[name] = {"task_created": today, "type": "unknown"}
                cal_tasks += 1
            else:
                print(f"[self_healer]   Calendar task already exists for {name} — skipping.")

    # Persist dedup state to GitHub
    _push_to_github(HEALED_FILE, healed)
    _push_to_github(RESEARCHED_FILE, researched)

    print(f"[self_healer] Done. PRs: {prs} | Research: {researched_count} | Calendar: {cal_tasks}")
    return {"prs_created": prs, "researched": researched_count, "calendar_tasks": cal_tasks}
