"""
Content Creator V2 — SQLite media catalog + incremental indexer (Sprint 1).

Tables: assets, scenes. One DB file per project, default ~/.content_creator_v2/catalog.db.
The indexer is incremental: skips any file whose path + checksum already exists.

Master plan: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Iterator, Optional

from .contracts import MediaAsset, Scene
from .ffprobe import extract as ffprobe_extract

logger = logging.getLogger(__name__)

DEFAULT_DB = Path.home() / ".content_creator_v2" / "catalog.db"

_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".jpg", ".jpeg", ".png", ".heic"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
    asset_id    TEXT PRIMARY KEY,
    path        TEXT NOT NULL UNIQUE,
    source      TEXT NOT NULL,
    owner       TEXT NOT NULL,
    captured_at TEXT,
    duration    REAL,
    width       INTEGER,
    height      INTEGER,
    orientation TEXT,
    checksum    TEXT NOT NULL,
    latitude    REAL,
    longitude   REAL
);

CREATE TABLE IF NOT EXISTS scenes (
    scene_id         TEXT PRIMARY KEY,
    asset_id         TEXT NOT NULL REFERENCES assets(asset_id),
    start_time       REAL NOT NULL,
    end_time         REAL NOT NULL,
    transcript       TEXT,
    keyframe_paths   TEXT NOT NULL DEFAULT '[]',
    visual_embedding TEXT,
    text_embedding   TEXT,
    quality_signals  TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_assets_checksum ON assets(checksum);
CREATE INDEX IF NOT EXISTS idx_scenes_asset   ON scenes(asset_id);
"""


class Catalog:
    def __init__(self, db_path: Path = DEFAULT_DB) -> None:
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()
        logger.info("Catalog opened: %s", db_path)

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Catalog":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    # ── assets ──────────────────────────────────────────────────────────────

    def asset_exists(self, path: str, checksum: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM assets WHERE path = ? AND checksum = ?", (path, checksum)
        ).fetchone()
        return row is not None

    def upsert_asset(self, asset: MediaAsset) -> None:
        self.conn.execute(
            """
            INSERT INTO assets
              (asset_id, path, source, owner, captured_at, duration,
               width, height, orientation, checksum, latitude, longitude)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(path) DO UPDATE SET
              asset_id    = excluded.asset_id,
              source      = excluded.source,
              owner       = excluded.owner,
              captured_at = excluded.captured_at,
              duration    = excluded.duration,
              width       = excluded.width,
              height      = excluded.height,
              orientation = excluded.orientation,
              checksum    = excluded.checksum,
              latitude    = excluded.latitude,
              longitude   = excluded.longitude
            """,
            (
                asset.asset_id, asset.path, asset.source, asset.owner,
                asset.captured_at, asset.duration, asset.width, asset.height,
                asset.orientation, asset.checksum, asset.latitude, asset.longitude,
            ),
        )
        self.conn.commit()

    def get_asset(self, asset_id: str) -> Optional[MediaAsset]:
        row = self.conn.execute(
            "SELECT * FROM assets WHERE asset_id = ?", (asset_id,)
        ).fetchone()
        return _row_to_asset(row) if row else None

    def all_assets(self) -> list[MediaAsset]:
        rows = self.conn.execute("SELECT * FROM assets").fetchall()
        return [_row_to_asset(r) for r in rows]

    # ── scenes ───────────────────────────────────────────────────────────────

    def upsert_scene(self, scene: Scene) -> None:
        self.conn.execute(
            """
            INSERT INTO scenes
              (scene_id, asset_id, start_time, end_time, transcript,
               keyframe_paths, visual_embedding, text_embedding, quality_signals)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(scene_id) DO UPDATE SET
              transcript       = excluded.transcript,
              keyframe_paths   = excluded.keyframe_paths,
              visual_embedding = excluded.visual_embedding,
              text_embedding   = excluded.text_embedding,
              quality_signals  = excluded.quality_signals
            """,
            (
                scene.scene_id, scene.asset_id, scene.start_time, scene.end_time,
                scene.transcript,
                json.dumps(scene.keyframe_paths),
                json.dumps(scene.visual_embedding) if scene.visual_embedding else None,
                json.dumps(scene.text_embedding) if scene.text_embedding else None,
                json.dumps(scene.quality_signals),
            ),
        )
        self.conn.commit()

    def scenes_for_asset(self, asset_id: str) -> list[Scene]:
        rows = self.conn.execute(
            "SELECT * FROM scenes WHERE asset_id = ?", (asset_id,)
        ).fetchall()
        return [_row_to_scene(r) for r in rows]

    # ── indexer ──────────────────────────────────────────────────────────────

    def index_folder(
        self,
        folder: Path,
        *,
        source: str = "personal",
        owner: str = "priscila",
        recursive: bool = True,
    ) -> tuple[int, int]:
        """
        Walk `folder` and add any media file not already indexed.
        Returns (added, skipped) counts.
        """
        folder = Path(folder)
        glob = folder.rglob("*") if recursive else folder.glob("*")
        added = skipped = 0
        for file in _media_files(glob):
            try:
                asset = ffprobe_extract(file, source=source, owner=owner)
                if self.asset_exists(asset.path, asset.checksum):
                    skipped += 1
                    logger.debug("skip (unchanged): %s", file.name)
                    continue
                self.upsert_asset(asset)
                added += 1
                logger.info("indexed: %s", file.name)
            except Exception as exc:
                logger.warning("skipped %s: %s", file.name, exc)
        return added, skipped

    def stats(self) -> dict:
        assets = self.conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        scenes = self.conn.execute("SELECT COUNT(*) FROM scenes").fetchone()[0]
        return {"assets": assets, "scenes": scenes}


# ── helpers ──────────────────────────────────────────────────────────────────

def _media_files(paths: Iterator[Path]) -> Iterator[Path]:
    for p in paths:
        if p.is_file() and p.suffix.lower() in _EXTENSIONS:
            yield p


def _row_to_asset(row: sqlite3.Row) -> MediaAsset:
    return MediaAsset(
        asset_id=row["asset_id"],
        path=row["path"],
        source=row["source"],
        owner=row["owner"],
        captured_at=row["captured_at"],
        duration=row["duration"],
        width=row["width"],
        height=row["height"],
        orientation=row["orientation"],
        checksum=row["checksum"],
        latitude=row["latitude"],
        longitude=row["longitude"],
    )


def _row_to_scene(row: sqlite3.Row) -> Scene:
    return Scene(
        scene_id=row["scene_id"],
        asset_id=row["asset_id"],
        start_time=row["start_time"],
        end_time=row["end_time"],
        transcript=row["transcript"],
        keyframe_paths=json.loads(row["keyframe_paths"]),
        visual_embedding=json.loads(row["visual_embedding"]) if row["visual_embedding"] else None,
        text_embedding=json.loads(row["text_embedding"]) if row["text_embedding"] else None,
        quality_signals=json.loads(row["quality_signals"]),
    )
