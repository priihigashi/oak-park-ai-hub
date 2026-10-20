#!/usr/bin/env python3
"""Allowlisted skill distribution — the ONE sync step that was missing.

Installs skills named in skills/distribution-manifest.yaml into the shared skills
root, then points each runtime (Claude, Codex) at the shared copy via symlink.

Design rules (enforced in code, not just documented):
  * DRY RUN IS THE DEFAULT. --apply is required before anything is written.
  * A non-identical existing directory is NEVER silently overwritten. It is backed
    up and reported; replacing it additionally requires --approve-overwrite.
  * Every write is verified by re-hashing the destination afterwards.
  * Runtime symlinks must resolve to the shared copy, or the run reports FAIL.
  * Only manifest-listed IDs are touched. No wildcard, no bulk import.

Usage:
    python3 scripts/skills_sync.py                      # dry run (default)
    python3 scripts/skills_sync.py --apply              # install additive/identical only
    python3 scripts/skills_sync.py --apply --approve-overwrite
    python3 scripts/skills_sync.py --verify             # check installed state only
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "skills" / "distribution-manifest.yaml"


def load_manifest():
    import yaml
    return yaml.safe_load(MANIFEST.read_text())


def expand(p: str) -> Path:
    return Path(os.path.expanduser(p))


def dir_hash(d: Path) -> str | None:
    """Stable hash of a directory's relative paths + contents. None if absent."""
    if not d.is_dir():
        return None
    h = hashlib.sha256()
    for f in sorted(p for p in d.rglob("*") if p.is_file()):
        h.update(str(f.relative_to(d)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def link_status(link: Path, target: Path) -> tuple[bool, str]:
    """Does `link` resolve to `target`?"""
    if not link.exists() and not link.is_symlink():
        return False, "absent"
    if link.is_symlink():
        try:
            resolved = link.resolve(strict=True)
        except (OSError, RuntimeError):
            return False, "broken-symlink"
        return (resolved == target.resolve(), f"symlink -> {resolved}")
    return False, "exists-but-not-a-symlink (real directory in the way)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually write (default is dry run)")
    ap.add_argument("--approve-overwrite", action="store_true",
                    help="permit replacing a non-identical existing skill directory")
    ap.add_argument("--verify", action="store_true", help="report installed state only, write nothing")
    ap.add_argument("--shared-root", default=None, help="override shared root (used by the mutation fixture)")
    ap.add_argument("--runtime-links", default=None, help="comma-separated override (used by the mutation fixture)")
    args = ap.parse_args()

    m = load_manifest()
    shared_root = expand(args.shared_root or m["install"]["shared_root"])
    runtime_links = ([expand(x) for x in args.runtime_links.split(",")] if args.runtime_links
                     else [expand(x) for x in m["install"]["runtime_links"]])
    backup_root = expand(m["safety"]["backup_dir"])

    mode = "VERIFY" if args.verify else ("APPLY" if args.apply else "DRY RUN")
    print(f"skills_sync — mode: {mode}")
    print(f"  manifest      : {MANIFEST}")
    print(f"  shared root   : {shared_root}")
    print(f"  runtime links : {', '.join(str(p) for p in runtime_links)}")
    print(f"  allowlisted   : {len(m['skills'])} skills\n")

    results, exit_code = [], 0
    for entry in m["skills"]:
        sid, src = entry["id"], REPO / entry["source"]
        dst = shared_root / sid
        r = {"id": sid, "source": str(src), "dest": str(dst)}

        if not (src / "SKILL.md").is_file():
            r["action"], r["status"] = "none", "SOURCE-MISSING"
            results.append(r); exit_code = 1
            print(f"  ✗ {sid}: source has no SKILL.md at {src}")
            continue

        src_h, dst_h = dir_hash(src), dir_hash(dst)
        r["source_hash"], r["dest_hash_before"] = src_h, dst_h

        if dst_h is None:
            r["action"] = "install"
        elif dst_h == src_h:
            r["action"] = "already-identical"
        else:
            r["action"] = "conflict-non-identical"

        if args.verify:
            r["status"] = "reported"
        elif r["action"] == "already-identical":
            r["status"] = "skipped (identical)"
        elif r["action"] == "conflict-non-identical" and not args.approve_overwrite:
            r["status"] = "BLOCKED — existing copy differs; not overwritten"
            exit_code = 2
        elif not args.apply:
            r["status"] = "would-write (dry run)"
        else:
            if dst_h is not None:  # back up before replacing
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                bdir = backup_root / f"{sid}-{stamp}"
                bdir.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(dst, bdir)
                shutil.rmtree(dst)
                r["backup"] = str(bdir)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)
            after = dir_hash(dst)
            r["dest_hash_after"] = after
            if after != src_h:
                r["status"] = "FAILED — post-write hash mismatch"; exit_code = 1
            else:
                r["status"] = "installed + hash-verified"

        # runtime links
        r["links"] = {}
        for link_root in runtime_links:
            link = link_root / sid
            ok, detail = link_status(link, dst)
            if not ok and args.apply and not args.verify and dst.is_dir():
                if link.is_symlink() or link.exists():
                    if link.is_symlink():
                        link.unlink()
                    else:
                        r["links"][str(link)] = f"REFUSED — {detail}"
                        exit_code = 2
                        continue
                link_root.mkdir(parents=True, exist_ok=True)
                link.symlink_to(dst)
                ok, detail = link_status(link, dst)
            r["links"][str(link)] = ("OK " if ok else "NOT-RESOLVING ") + detail
            if not ok and args.apply:
                exit_code = 2

        results.append(r)
        mark = {"installed + hash-verified": "✓", "skipped (identical)": "=", "reported": "·"}.get(r["status"], "!")
        print(f"  {mark} {sid}: {r['action']} -> {r['status']}")
        for k, v in r["links"].items():
            print(f"      link {k}: {v}")

    print("\nsummary:", json.dumps({r["id"]: r["status"] for r in results}, indent=2))
    if exit_code:
        print(f"\nexit {exit_code}: at least one skill was blocked or failed verification.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
