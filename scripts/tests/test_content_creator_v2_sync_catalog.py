"""Sprint 2-C: tests for Catalog.index_folder() — SHA-256 hash dedup + incremental indexing.

All tests use tmp_path to keep SQLite and files fully isolated.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.content_creator_v2.catalog import Catalog


_PROBE = {
    "format": {"duration": "8.0", "tags": {}},
    "streams": [{"codec_type": "video", "width": 1080, "height": 1920}],
}


def _mock_run(**kwargs) -> MagicMock:
    return MagicMock(returncode=0, stdout=json.dumps(_PROBE), stderr="")


def _vid(folder: Path, name: str, content: bytes) -> Path:
    p = folder / name
    p.write_bytes(content)
    return p


class TestCatalogDedup:
    def test_new_file_is_indexed(self, tmp_path):
        folder = tmp_path / "vids"
        folder.mkdir()
        _vid(folder, "clip.mp4", b"\x00" * 1024)

        with patch("subprocess.run", side_effect=_mock_run):
            with Catalog(tmp_path / "db") as cat:
                added, skipped = cat.index_folder(folder)

        assert added == 1
        assert skipped == 0

    def test_unchanged_file_skipped_on_second_index(self, tmp_path):
        folder = tmp_path / "vids"
        folder.mkdir()
        _vid(folder, "clip.mp4", b"\xff" * 1024)

        with patch("subprocess.run", side_effect=_mock_run):
            with Catalog(tmp_path / "db") as cat:
                cat.index_folder(folder)
                added2, skipped2 = cat.index_folder(folder)

        assert added2 == 0
        assert skipped2 == 1

    def test_two_distinct_files_both_indexed(self, tmp_path):
        folder = tmp_path / "vids"
        folder.mkdir()
        _vid(folder, "a.mp4", b"\x01" * 512)
        _vid(folder, "b.mp4", b"\x02" * 512)

        with patch("subprocess.run", side_effect=_mock_run):
            with Catalog(tmp_path / "db") as cat:
                added, skipped = cat.index_folder(folder)

        assert added == 2
        assert skipped == 0

    def test_non_media_files_are_ignored(self, tmp_path):
        folder = tmp_path / "mixed"
        folder.mkdir()
        (folder / "notes.txt").write_text("ignore me")
        (folder / "script.py").write_text("pass")
        _vid(folder, "clip.mp4", b"\xAA" * 256)

        with patch("subprocess.run", side_effect=_mock_run):
            with Catalog(tmp_path / "db") as cat:
                added, _ = cat.index_folder(folder)

        assert added == 1

    def test_multiple_files_stats_correct(self, tmp_path):
        folder = tmp_path / "vids"
        folder.mkdir()
        for i in range(3):
            _vid(folder, f"v{i}.mp4", bytes([i + 1]) * 256)

        with patch("subprocess.run", side_effect=_mock_run):
            with Catalog(tmp_path / "db") as cat:
                cat.index_folder(folder)
                s = cat.stats()

        assert s["assets"] == 3
        assert s["scenes"] == 0


class TestCatalogAssetRetrieval:
    def test_upserted_asset_is_retrievable(self, tmp_path):
        folder = tmp_path / "vids"
        folder.mkdir()
        _vid(folder, "clip.mp4", b"\xBB" * 512)

        with patch("subprocess.run", side_effect=_mock_run):
            with Catalog(tmp_path / "db") as cat:
                cat.index_folder(folder)
                assets = cat.all_assets()

        assert len(assets) == 1
        assert assets[0].owner == "priscila"
        assert assets[0].source == "personal"

    def test_context_manager_closes_without_error(self, tmp_path):
        with Catalog(tmp_path / "db.sqlite") as cat:
            stats = cat.stats()
        assert stats["assets"] == 0

    def test_empty_folder_returns_zero_zero(self, tmp_path):
        folder = tmp_path / "empty"
        folder.mkdir()

        with Catalog(tmp_path / "db") as cat:
            added, skipped = cat.index_folder(folder)

        assert added == 0
        assert skipped == 0
