"""
S1-C + S1-D: Incremental SQLite catalog sync.
Scans --media-dir, hashes each file, skips unchanged, re-indexes modified, flags missing.
Usage: python sync_catalog.py --media-dir /path/to/media [--db data/media_catalog.db]
"""

import argparse
import sqlite3
import os
import json
import sys
from datetime import datetime, timezone
from extract_metadata import extract, sha256


DEFAULT_DB = os.path.join(os.path.dirname(__file__), "../../../data/media_catalog.db")

DDL = """
CREATE TABLE IF NOT EXISTS media_files (
    file_hash       TEXT PRIMARY KEY,
    file_path       TEXT NOT NULL,
    duration_sec    REAL,
    width           INTEGER,
    height          INTEGER,
    aspect_ratio    TEXT,
    fps             REAL,
    has_audio       INTEGER,
    codec_video     TEXT,
    codec_audio     TEXT,
    size_bytes      INTEGER,
    last_modified   TEXT,
    indexed_at      TEXT,
    missing_since   TEXT
);

CREATE TABLE IF NOT EXISTS scenes (
    scene_id        TEXT PRIMARY KEY,
    file_hash       TEXT REFERENCES media_files(file_hash),
    start_sec       REAL,
    end_sec         REAL,
    description     TEXT,
    created_at      TEXT
);

CREATE TABLE IF NOT EXISTS embeddings_meta (
    file_hash       TEXT REFERENCES media_files(file_hash),
    model           TEXT,
    embedding_path  TEXT,
    created_at      TEXT,
    PRIMARY KEY (file_hash, model)
);
"""

MEDIA_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".jpg", ".jpeg", ".png"}


def connect(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(DDL)
    conn.commit()
    return conn


def sync(media_dir: str, db_path: str):
    conn = connect(db_path)
    now = datetime.now(tz=timezone.utc).isoformat()

    # Mark all existing rows as potentially missing; clear for files we find
    conn.execute("UPDATE media_files SET missing_since = ? WHERE missing_since IS NULL", (now,))

    found_hashes = set()
    stats = {"new": 0, "updated": 0, "skipped": 0, "errors": 0}

    for root, _, files in os.walk(media_dir):
        for fname in files:
            if os.path.splitext(fname)[1].lower() not in MEDIA_EXTENSIONS:
                continue
            path = os.path.join(root, fname)
            try:
                current_hash = sha256(path)
                found_hashes.add(current_hash)

                row = conn.execute(
                    "SELECT file_hash, last_modified FROM media_files WHERE file_path = ?",
                    (path,)
                ).fetchone()

                if row and row[0] == current_hash:
                    conn.execute(
                        "UPDATE media_files SET missing_since = NULL WHERE file_hash = ?",
                        (current_hash,)
                    )
                    stats["skipped"] += 1
                    continue

                meta = extract(path)
                conn.execute("""
                    INSERT OR REPLACE INTO media_files
                    (file_hash, file_path, duration_sec, width, height, aspect_ratio,
                     fps, has_audio, codec_video, codec_audio, size_bytes,
                     last_modified, indexed_at, missing_since)
                    VALUES (:file_hash, :file_path, :duration_sec, :width, :height,
                            :aspect_ratio, :fps, :has_audio, :codec_video, :codec_audio,
                            :size_bytes, :last_modified, :indexed_at, NULL)
                """, meta)

                if row:
                    stats["updated"] += 1
                else:
                    stats["new"] += 1

            except Exception as e:
                print(f"  ERROR {path}: {e}", file=sys.stderr)
                stats["errors"] += 1

    conn.commit()
    conn.close()
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-dir", required=True)
    parser.add_argument("--db", default=DEFAULT_DB)
    args = parser.parse_args()

    print(f"Syncing {args.media_dir} → {args.db}")
    stats = sync(args.media_dir, args.db)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
