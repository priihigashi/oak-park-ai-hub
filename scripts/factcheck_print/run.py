#!/usr/bin/env python3
"""transcribe-comment-create-print pipeline (GitHub Actions / any machine).

URL in -> transcript -> claims -> per-claim research with web search (verify-first, benefit of the doubt)
-> real article screenshots -> deck.html + one PNG per card -> Drive folder -> email to Priscila.

Stance rules mirror ~/.agents/skills/transcribe-comment-create-print/SKILL.md (private repo priscila-workspace).
Review UI is done later in a chat (publish deck.html from the Drive folder as an artifact); this job does the heavy lifting.
"""
import argparse, base64, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time, urllib.parse, urllib.request
from datetime import datetime

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "scripts" / "capture"))
import render_deck  # noqa: E402

MODEL = os.getenv("FACTCHECK_MODEL", "claude-sonnet-4-6")
KEY = os.getenv("CLAUDE_KEY_4_CONTENT") or os.getenv("ANTHROPIC_API_KEY", "")
UA_MOBILE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

STANCE = """You are a fact-checker for a Brazilian news brand. RULES, non-negotiable:
1. VERIFY, do not debunk. Goal: confirm what the speaker said. Only say something is false when the evidence for that is solid.
2. NO false balance. Do not add "both sides" caveats. Only add a caveat that is a legal-accuracy fact about a named person.
3. Give the speaker the benefit of the doubt. For each claim keep searching for the strongest evidence that PROVES it, including other people/periods (a claim about "the candidate" may really be about his father's government), before ever calling it unconfirmed. The wording may be inexact; use the closest real fact.
4. Unproven is not false: mark it 'unconfirmed' and list what you searched. Never invent a source, a quote, a number or a URL. Every URL you output must have been returned by your search tool.
5. Sources: prefer primary (court, agency, official) then BIG outlets (Globo, CNN Brasil, Folha, Jovem Pan, SBT, Record, Terra, Poder360, Agência Brasil, Estado de Minas). Skip niche/partisan outlets unless nothing bigger has it.
6. Explain legal/technical words in one plain clause for laypeople.
7. Answer WHO / WHAT / WHERE in the first lines. Lead with the LINK between the people in the story, background stays short.
8. No em dashes. Portuguese (pt-BR) is primary, English mirrors it. Highlight key people names with <span class="y2">Name</span>. Allowed HTML: <b>, <i>, <br>, <span class="y2">.
9. Never write 'we did not find' inside card text."""


def claude(system, user, web=False, max_tokens=6000, uses=8):
    import anthropic
    c = anthropic.Anthropic(api_key=KEY)
    kw = dict(model=MODEL, max_tokens=max_tokens, system=system, messages=[{"role": "user", "content": user}])
    if web:
        kw["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": uses}]
    for attempt in range(3):
        try:
            msgs = list(kw["messages"])
            text = ""
            for _ in range(6):  # server-side web search may return pause_turn: resend to continue
                r = c.messages.create(**{**kw, "messages": msgs})
                text += "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
                if getattr(r, "stop_reason", "") != "pause_turn":
                    return text
                msgs = msgs + [{"role": "assistant", "content": r.content}]
            return text
        except Exception as e:  # rate limit / overload
            print(f"  claude retry {attempt + 1}: {str(e)[:120]}")
            time.sleep(20 * (attempt + 1))
    raise RuntimeError("Claude call failed 3 times")


def jload(text):
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    s = m.group(1) if m else text
    dec = json.JSONDecoder()
    for opener in "{[":  # objects first (every reply we ask for is an object); skips prose citations like "[1]"
        for i, ch in enumerate(s):
            if ch == opener:
                try:
                    return dec.raw_decode(s[i:])[0]
                except ValueError:
                    continue
    raise ValueError("no JSON in model reply")


ALLOWED = re.compile(r"</?(b|i|br)\s*/?>|<span class=\"y2\">|</span>")


def clean_html(t):
    """Model text -> only <b>, <i>, <br>, <span class="y2"> survive; everything else is escaped."""
    t = t or ""
    out, pos = [], 0
    for m in re.finditer(r"<[^>]*>", t):
        out.append(t[pos:m.start()].replace("<", "&lt;"))
        out.append(m.group(0) if ALLOWED.fullmatch(m.group(0)) else m.group(0).replace("<", "&lt;").replace(">", "&gt;"))
        pos = m.end()
    out.append(t[pos:].replace("<", "&lt;"))
    return "".join(out)


def safe_url(u):
    import ipaddress, socket
    from urllib.parse import urlparse
    p = urlparse(u or "")
    if p.scheme != "https" or not p.hostname:
        return False
    try:
        for info in socket.getaddrinfo(p.hostname, 443):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
    except Exception:
        return False
    return True


def latest_transcript():
    files = sorted(pathlib.Path("transcripts").glob("*_transcript.txt"), key=lambda p: p.stat().st_mtime)
    if not files:
        raise SystemExit("no transcript found in transcripts/ (capture step failed?)")
    return files[-1].read_text(encoding="utf-8")


def extract_claims(transcript, notes):
    out = claude(STANCE, f"""Transcript of a video:\n\n{transcript[:14000]}\n\nExtra context from the requester: {notes or '-'}\n
List the checkable FACTUAL claims (max 7), in the order spoken. Skip opinions, calls to action, hooks.
Return JSON only: {{"hook_pt": "<= 90 chars, starts with 'Conferimos a alegação'", "hook_en": "...", "title": "3-5 word name for the deck (pt)",
"claims": [{{"quote": "speaker's words, verbatim from transcript", "who": "...", "what": "...", "where": "..."}}]}}""", max_tokens=3000)
    return jload(out)


def research(claim, transcript_ctx):
    out = claude(STANCE, f"""Video context: {transcript_ctx[:1500]}\n\nCLAIM (verbatim): {claim['quote']}\nwho={claim.get('who')} what={claim.get('what')} where={claim.get('where')}\n
Use web search (Portuguese queries first). Find the article(s) that confirm it. Then return JSON only:
{{"status": "confirmed" | "partly" | "unconfirmed" | "false",
 "eb_pt": "A alegação", "eb_en": "The claim",
 "hd_pt": "title that carries the finding (<=60 chars)", "hd_en": "...",
 "chk_pt": "what we checked: who/what/where, numbers, dates, plain-language terms; <= 520 chars; html allowed", "chk_en": "mirror",
 "sources": [{{"name": "Outlet", "date": "DD/MM/YYYY", "url": "https://...", "title": "headline"}}],   // FIRST = best article to screenshot; others = names for the 'Também' line
 "searched": "what you searched and did not find (only used for the email, never on the card)"}}""", web=True, max_tokens=5000, uses=10)
    return jload(out)


def review(spec_cards, transcript):
    txt = json.dumps([{k: c.get(k) for k in ("id", "hd", "chk", "badge")} for c in spec_cards if c["type"] == "claim"], ensure_ascii=False)
    out = claude(STANCE, f"""Second-pass review, 'am I looking at half the story'. Video transcript:\n{transcript[:9000]}\n\nCARDS:\n{txt}\n
For each card: is a true claim wrongly softened, is unwarranted balance added, is a proof point of the speaker missing that you KNOW from the searched evidence? Return JSON only:
{{"fixes": [{{"id": <card id>, "chk_pt": "improved text or null", "chk_en": "improved text or null", "why": "one line"}}], "notes_for_priscila": "max 3 lines"}}""", max_tokens=3000)
    return jload(out)


def shoot(url, path):
    from playwright.sync_api import sync_playwright
    if not safe_url(url):
        print("  refusing non-https / private URL:", url[:80]); return False
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 760, "height": 1800}, device_scale_factor=3, user_agent=UA_MOBILE, is_mobile=True, has_touch=True)
        try:
            pg.goto(url, wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(4500)
            for s in ['button:has-text("Aceitar")', 'button:has-text("Concordo")', '#onetrust-accept-btn-handler', 'button:has-text("Accept")']:
                try:
                    e = pg.query_selector(s)
                    if e and e.is_visible():
                        e.click(); pg.wait_for_timeout(400)
                except Exception:
                    pass
            pg.evaluate("""()=>{document.querySelectorAll('*').forEach(e=>{const c=getComputedStyle(e);
              if(c.position==='fixed'||c.position==='sticky'||e.tagName==='IFRAME'||e.getAttribute('role')==='dialog')e.remove();
              if(/publicidade|advert|newsletter|paywall|subscribe|modal|overlay|popup|banner/i.test((e.className&&e.className.toString())||'')+(e.id||''))e.style.display='none';});
              document.documentElement.style.overflow='auto';document.body.style.overflow='auto';document.body.style.filter='none';window.scrollTo(0,0)}""")
            pg.wait_for_timeout(600)
            h = pg.query_selector("h1")
            box = h.bounding_box() if h else None
            y = max(0, box["y"] - 45) if box else 0
            pg.screenshot(path=str(path), clip={"x": 0, "y": y, "width": 760, "height": min(900, 1800 - y)})
            return True
        except Exception as e:
            print("  shoot failed:", url, str(e)[:100])
            return False
        finally:
            b.close()


def to_card_jpg(png, jpg):
    from PIL import Image
    im = Image.open(png).convert("RGB")
    im.thumbnail((1200, 1500))
    cv = Image.new("RGB", (1200, 1500), "white")
    cv.paste(im, (0, 0))
    cv.save(jpg, quality=92)


def drive_service():
    from googleapiclient.discovery import build
    from capture_pipeline import _get_creds
    return build("drive", "v3", credentials=_get_creds(["https://www.googleapis.com/auth/drive"]))


def mkfolder(svc, name, parent):
    return svc.files().create(body={"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent]},
                              fields="id,webViewLink", supportsAllDrives=True).execute()


def upload(svc, path, parent, mime=None):
    from googleapiclient.http import MediaFileUpload
    import mimetypes
    mime = mime or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    f = svc.files().create(body={"name": pathlib.Path(path).name, "parents": [parent]},
                           media_body=MediaFileUpload(str(path), mimetype=mime, resumable=True),
                           fields="id,webViewLink", supportsAllDrives=True).execute()
    return f


def email(subject, body, attach=()):
    import smtplib
    from email.message import EmailMessage
    pw = os.getenv("PRI_OP_GMAIL_APP_PASSWORD", "")
    if not pw:
        raise RuntimeError("no PRI_OP_GMAIL_APP_PASSWORD: cannot email the result")
    m = EmailMessage()
    m["Subject"], m["From"], m["To"] = subject, "priscila@oakpark-construction.com", "priscila@oakpark-construction.com"
    m.set_content(body)
    for p in attach:
        p = pathlib.Path(p)
        m.add_attachment(p.read_bytes(), maintype="image", subtype="png", filename=p.name)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login("priscila@oakpark-construction.com", pw); s.send_message(m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--notes", default="")
    ap.add_argument("--notes-file", default="")
    ap.add_argument("--project", default="brazil")
    ap.add_argument("--out", default="factcheck_out")
    ap.add_argument("--no-drive", action="store_true")
    a = ap.parse_args()
    if a.notes_file and pathlib.Path(a.notes_file).exists():
        a.notes = pathlib.Path(a.notes_file).read_text(encoding="utf-8")[:4000]
    if not KEY:
        raise SystemExit("no Claude key (CLAUDE_KEY_4_CONTENT / ANTHROPIC_API_KEY)")
    wd = pathlib.Path(a.out); wd.mkdir(parents=True, exist_ok=True)
    (wd / "shots").mkdir(exist_ok=True); (wd / "media").mkdir(exist_ok=True)

    tr = latest_transcript()
    print("transcript chars:", len(tr))
    plan = extract_claims(tr, a.notes)
    print("claims:", len(plan["claims"]))

    cards, sources, shots, gaps = [{"type": "open", "id": 1, "hd": {"pt": plan["hook_pt"], "en": plan["hook_en"]}}], [], {}, []
    cid = 2
    for n, cl in enumerate(plan["claims"], 1):
        print(f"[{n}/{len(plan['claims'])}] {cl['quote'][:70]}")
        try:
            r = research(cl, tr)
        except Exception as e:
            gaps.append(f"claim {n}: research failed ({e})"); continue
        if r["status"] in ("unconfirmed", "false"):
            gaps.append(f"claim {n} [{r['status']}]: {cl['quote'][:90]} | searched: {r.get('searched', '')}")
            if r["status"] == "unconfirmed":
                continue  # unproven never becomes a card
        srcs = [x for x in (r.get("sources") or []) if isinstance(x, dict) and safe_url(x.get("url"))]
        if not srcs:
            gaps.append(f"claim {n}: no usable https source"); continue
        try:
            key = f"s{n}"
            ok, main = False, srcs[0]
            for sr in srcs[:3]:
                png = wd / "shots" / f"{key}.png"
                if shoot(sr["url"], png):
                    to_card_jpg(png, wd / "shots" / f"{key}.jpg"); ok, main = True, sr; break
            if not ok:
                gaps.append(f"claim {n}: screenshot failed for all sources {[x['url'] for x in srcs[:3]]}")
            shots[key] = f"shots/{key}.jpg" if ok else ""
            badge = {"confirmed": "confirmed", "partly": "partly", "false": "false"}[r["status"]]
            cards.append({"type": "claim", "id": cid, "badge": badge,
                          "eb": {"pt": "A alegação", "en": "The claim"},
                          "hd": {"pt": clean_html(r["hd_pt"]), "en": clean_html(r.get("hd_en") or r["hd_pt"])},
                          "say": {"pt": "“" + clean_html(cl["quote"]).strip("“”\" ") + "”", "en": ""},
                          "chk": {"pt": clean_html(r["chk_pt"]), "en": clean_html(r.get("chk_en") or r["chk_pt"])}})
            others = [x["name"] for x in srcs if x["url"] != main["url"]][:3]
            cards.append({"type": "proof", "id": cid + 1, "key": key, "src": {"name": clean_html(main.get("name", "")), "date": clean_html(main.get("date", "")), "full": main["url"]},
                          "also": {"pt": "Também: " + " · ".join(clean_html(o) for o in others), "en": "Also: " + " · ".join(clean_html(o) for o in others)} if others else None})
            for sr in srcs:
                sources.append({"name": sr.get("name", ""), "date": sr.get("date", ""), "url": sr["url"], "title": sr.get("title")})
            cid += 2
        except KeyError as e:
            gaps.append(f"claim {n}: model reply missing field {e}")

    # second pass: half-the-story review
    notes_p = ""
    try:
        rv = review(cards, tr)
        for f in rv.get("fixes", []):
            for c in cards:
                if c["type"] == "claim" and c["id"] == f.get("id"):
                    if f.get("chk_pt"): c["chk"]["pt"] = clean_html(f["chk_pt"])
                    if f.get("chk_en"): c["chk"]["en"] = clean_html(f["chk_en"])
        notes_p = rv.get("notes_for_priscila", "")
    except Exception as e:
        gaps.append(f"review pass failed: {e}")

    # the original video, playable in card 1
    video = None
    try:
        import capture_pipeline as cp
        tmp = tempfile.mkdtemp()
        vp = cp.download_video(a.url, tmp)
        if vp:
            dst = wd / "media" / "original.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vp, "-vf", "scale=540:-2", "-c:v", "libx264", "-crf", "31", "-preset", "medium",
                            "-maxrate", "600k", "-bufsize", "1200k", "-c:a", "aac", "-b:a", "48k", "-movflags", "+faststart", str(dst)], check=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", str(dst), "-frames:v", "1", "-q:v", "4", str(wd / "media" / "poster.jpg")])
            video = {"file": "media/original.mp4", "poster": "media/poster.jpg"}
    except Exception as e:
        gaps.append(f"video download/compress failed (card 1 stays a placeholder): {str(e)[:120]}")

    today = datetime.now().strftime("%d/%m/%Y")
    spec = {"title": plan.get("title") or "Checagem", "hook": {"pt": plan["hook_pt"], "en": plan["hook_en"]}, "video_url": a.url,
            "meta": {"date": today, "run": os.getenv("GITHUB_RUN_ID", "local")}, "sources": sources, "video": video, "shots": shots,
            "cards": cards, "caption": {"pt": "", "en": ""}, "gaps": gaps}
    (wd / "cards.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    deck = render_deck.render(spec, wd)
    pngs = render_deck.export_pngs(deck, wd / "png")
    print("cards:", len(cards), "pngs:", len(pngs), "gaps:", len(gaps))

    link, drive_failed = "(Drive upload skipped)", False
    if not a.no_drive:
        try:
            from routing import get_route
            parent = get_route(a.project)["carousel_folder_id"]
            svc = drive_service()
            slug = re.sub(r"[^a-z0-9]+", "_", spec["title"].lower()).strip("_")[:40] or "checagem"
            n = 1 + len([f for f in svc.files().list(q=f"'{parent}' in parents and trashed=false and name contains 'v'", fields="files(name)", pageSize=1000,
                                                     supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get("files", []) if re.match(r"v\d+_", f["name"])])
            root = mkfolder(svc, f"v{n}_{slug}_print", parent)
            upload(svc, wd / "deck.html", root["id"]); upload(svc, wd / "cards.json", root["id"])
            png_f = mkfolder(svc, "png", root["id"])
            for p in pngs: upload(svc, p, png_f["id"])
            res = mkfolder(svc, "resources", root["id"])
            for p in (wd / "media").glob("*"): upload(svc, p, res["id"])
            for p in (wd / "shots").glob("*.jpg"): upload(svc, p, res["id"])
            link = root["webViewLink"]
        except Exception as e:
            link = f"(Drive upload FAILED: {e})"
            gaps.append("Drive upload FAILED")
            drive_failed = True
    body = (f"Fact-check deck ready (transcribe-comment-create-print).\n\nVideo: {a.url}\nDrive folder: {link}\nCards: {len(cards)} | PNGs: {len(pngs)}\n\n"
            f"To review: open a Claude chat and say: /transcribe-comment-create-print review {link}\n\n"
            f"NOTES FROM THE SECOND PASS:\n{notes_p or '-'}\n\nGAPS (not on the cards):\n" + ("\n".join("- " + g for g in gaps) or "- none") +
            f"\n\nRun: https://github.com/{os.getenv('GITHUB_REPOSITORY', '')}/actions/runs/{os.getenv('GITHUB_RUN_ID', '')}")
    email(f"Fact-check deck: {spec['title']}", body, pngs[:6])
    print(f"done: {len(cards)} cards, {len(pngs)} PNGs, {len(gaps)} gaps, drive_failed={drive_failed}")  # body (notes, link) stays out of the public log
    if drive_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
