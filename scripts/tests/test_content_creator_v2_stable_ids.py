"""Deterministic identity and rerun tests for Content Creator V2.

Run:
  python3 -m unittest scripts/tests/test_content_creator_v2_stable_ids.py
"""

from __future__ import annotations

import inspect
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from scripts.content_creator_v2 import ffprobe, scene_extractor  # noqa: E402
from scripts.content_creator_v2.catalog import Catalog  # noqa: E402
from scripts.content_creator_v2.contracts import MediaAsset  # noqa: E402
from scripts.content_creator_v2.stable_ids import (  # noqa: E402
    asset_id,
    keyframe_name,
    scene_id,
)


def _asset(*, checksum: str = "checksum-v1") -> MediaAsset:
    return MediaAsset(
        asset_id=asset_id("photos:ABC-123"),
        path="/tmp/example.mov",
        source="personal",
        owner="mike",
        captured_at=None,
        duration=5.0,
        width=1920,
        height=1080,
        orientation="landscape",
        checksum=checksum,
    )


class StableIdUnitTests(unittest.TestCase):
    def test_asset_id_is_stable_and_source_specific(self):
        self.assertEqual(asset_id("photos:1"), asset_id("photos:1"))
        self.assertNotEqual(asset_id("photos:1"), asset_id("photos:2"))

    def test_scene_id_canonicalises_float_noise(self):
        parent = asset_id("photos:1")
        self.assertEqual(
            scene_id(parent, 0.1 + 0.2, 3.0, media_version="v1"),
            scene_id(parent, 0.3, 3.0, media_version="v1"),
        )

    def test_scene_id_changes_for_media_version_or_boundaries(self):
        parent = asset_id("photos:1")
        base = scene_id(parent, 0.0, 3.0, media_version="v1")
        self.assertNotEqual(base, scene_id(parent, 0.0, 3.0, media_version="v2"))
        self.assertNotEqual(base, scene_id(parent, 0.0, 4.0, media_version="v1"))

    def test_invalid_identity_inputs_fail_loudly(self):
        with self.assertRaises(ValueError):
            asset_id("")
        with self.assertRaises(ValueError):
            scene_id("asset", 2.0, 2.0, media_version="v1")
        with self.assertRaises(ValueError):
            scene_id("asset", 0.0, 2.0, media_version="")

    def test_keyframe_name_is_stable_and_safe(self):
        sid = scene_id(asset_id("photos:1"), 0.0, 3.0, media_version="v1")
        name = keyframe_name(sid, 0.6)
        self.assertEqual(name, keyframe_name(sid, 0.6))
        self.assertTrue(name.endswith(".png"))
        for unsafe in ("/", "\\", ":", " ", "\x00"):
            self.assertNotIn(unsafe, name)


class FfprobeIdentityTests(unittest.TestCase):
    def test_repeated_extract_uses_same_asset_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clip.mov"
            path.write_bytes(b"test")
            probe = {
                "format": {"duration": "2", "tags": {}},
                "streams": [{"codec_type": "video", "width": 10, "height": 20}],
            }
            with patch.object(ffprobe, "_run_ffprobe", return_value=probe):
                first = ffprobe.extract(path)
                second = ffprobe.extract(path)
        self.assertEqual(first.asset_id, second.asset_id)

    def test_caller_supplied_source_id_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clip.mov"
            path.write_bytes(b"test")
            probe = {"format": {"tags": {}}, "streams": []}
            with patch.object(ffprobe, "_run_ffprobe", return_value=probe):
                result = ffprobe.extract(path, asset_id="photos-stable-id")
        self.assertEqual(result.asset_id, "photos-stable-id")


class SceneExtractionRerunTests(unittest.TestCase):
    def _run(self, asset: MediaAsset, output_dir: Path):
        def fake_keyframe(_path, _timestamp, directory, *, filename=None):
            return str(directory / filename)

        with (
            patch.object(scene_extractor, "detect_scenes", return_value=[(0.0, 2.0), (2.0, 5.0)]),
            patch.object(scene_extractor, "extract_keyframe", side_effect=fake_keyframe),
            patch.object(scene_extractor, "_quality_signals", return_value={}),
        ):
            return scene_extractor.extract_scenes(asset, output_dir)

    def test_two_runs_produce_identical_scene_ids_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self._run(_asset(), Path(tmp))
            second = self._run(_asset(), Path(tmp))
        self.assertEqual([s.scene_id for s in first], [s.scene_id for s in second])
        self.assertEqual(
            [s.keyframe_paths for s in first],
            [s.keyframe_paths for s in second],
        )

    def test_changed_media_version_changes_scene_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self._run(_asset(checksum="v1"), Path(tmp))
            second = self._run(_asset(checksum="v2"), Path(tmp))
        self.assertNotEqual([s.scene_id for s in first], [s.scene_id for s in second])

    def test_rerun_upserts_instead_of_duplicating_scenes(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset = _asset()
            scenes = self._run(asset, Path(tmp))
            with Catalog(Path(tmp) / "catalog.db") as catalog:
                catalog.upsert_asset(asset)
                for scene in scenes:
                    catalog.upsert_scene(scene)
                for scene in self._run(asset, Path(tmp)):
                    catalog.upsert_scene(scene)
                self.assertEqual(catalog.stats(), {"assets": 1, "scenes": 2})


class RandomIdentityRegressionTest(unittest.TestCase):
    def test_identity_paths_no_longer_call_uuid4(self):
        """CATCHES: random IDs reintroduced into asset or scene creation."""
        self.assertNotIn("uuid.uuid4", inspect.getsource(ffprobe))
        self.assertNotIn("uuid.uuid4", inspect.getsource(scene_extractor))


if __name__ == "__main__":
    unittest.main()
