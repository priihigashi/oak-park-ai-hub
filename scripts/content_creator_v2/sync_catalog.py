"""
CLI: incrementally index a folder of media files into the SQLite catalog.

Usage:
    python -m scripts.content_creator_v2.sync_catalog <folder> [options]

Options:
    --db        Path to the SQLite database file.
                Default: ~/.content_creator_v2/catalog.db
    --source    personal | approved_collection | licensed | ai_generated (default: personal)
    --owner     priscila | mike | <collection_name> (default: priscila)
    --no-recurse  Do not walk subdirectories (default: recursive).
    --stats     Print catalog stats after sync.

Exit codes:
    0  success
    1  folder not found or not a directory
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .catalog import Catalog, DEFAULT_DB


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sync_catalog",
        description="Incrementally index a media folder into the SQLite catalog.",
    )
    p.add_argument("folder", type=Path, help="Root folder to index.")
    p.add_argument("--db", type=Path, default=DEFAULT_DB,
                   help=f"SQLite DB path (default: {DEFAULT_DB}).")
    p.add_argument("--source", default="personal",
                   choices=["personal", "approved_collection", "licensed", "ai_generated"])
    p.add_argument("--owner", default="priscila")
    p.add_argument("--no-recurse", dest="recurse", action="store_false", default=True)
    p.add_argument("--stats", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"error: not a directory: {folder}", file=sys.stderr)
        return 1

    with Catalog(args.db) as cat:
        added, skipped = cat.index_folder(
            folder,
            source=args.source,
            owner=args.owner,
            recursive=args.recurse,
        )
        print(f"sync complete — added: {added}, skipped (unchanged): {skipped}")
        if args.stats:
            s = cat.stats()
            print(f"catalog totals — assets: {s['assets']}, scenes: {s['scenes']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
