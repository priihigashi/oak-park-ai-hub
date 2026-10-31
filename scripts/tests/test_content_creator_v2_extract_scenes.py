"""
Content Creator V2 — unit tests for scene_extractor.py (Sprint 2-C).

Run:
  python3 -m pytest scripts/tests/test_content_creator_v2_extract_scenes.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from scripts.content_creator_v2 import scene_extractor  # noqa: E402
from scripts.content_creator_v2.contracts import MediaAsset  # noqa: E402
from scripts.content_creator_v2.stable_ids import asset_id  # noqa: E402


def _asset(duration: float = 10.0) -> MediaAsset:
    return MediaAsset(
        asset_id=asset_id("test:scene-extractor-v2"),
        path="/tmp/test_video.mp4",
        source="personal",
        owner="priscila",
        captured_at=None,
        duration=duration,
        width=1920,
        height=1080,
        orientation="landscape",
        checksum="abc123checksum",
    )


def _fake_stderr(timestamps: list[float]) -> str:
    return "\n".join(
        f"[Parsed_showinfo_1 @ 0x0] pts_time:{ts}" for ts in timestamps
    )


class TestDetectScenes(unittest.TestCase):
    """Unit tests for detect_scenes() with subprocess.run mocked."""

    def _run(self, stderr: str, duration: float = 10.0) -> list[tuple[float, float]]:
        fake = MagicMock()
        fake.stderr = stderr
        asset = _asset(duration=duration)
        with patch("subprocess.run", return_value=fake):
            return scene_extractor.detect_scenes(asset)

    def test_two_cuts_produce_three_scenes(self):
        pairs = self._run(_fake_stderr([3.0, 7.0]), duration=10.0)
        self.assertEqual(len(pairs), 3)
        self.assertEqual(pairs[0], (0.0, 3.0))
        self.assertEqual(pairs[1], (3.0, 7.0))
        self.assertEqual(pairs[2], (7.0, 10.0))

    def test_no_cuts_returns_whole_video_as_one_scene(self):
        pairs = self._run("", duration=8.0)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0], (0.0, 8.0))

    def test_zero_duration_returns_empty(self):
        self.assertEqual(scene_extractor.detect_scenes(_asset(duration=0.0)), [])

    def test_negative_duration_returns_empty(self):
        self.assertEqual(scene_extractor.detect_scenes(_asset(duration=-1.0)), [])

    def test_cut_too_close_to_previous_is_filtered(self):
        # Cut at 0.5s is only 0.5s from the start (0.0) — below MIN_SCENE_SECONDS (1.5)
        # It should be dropped, leaving just the full 10s video as one scene.
        pairs = self._run(_fake_stderr([0.5]), duration=10.0)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0], (0.0, 10.0))

    def test_max_scenes_cap_respected(self):
        # 249 cuts 2.0s apart in a 600s video — all exceed MIN_SCENE_SECONDS, cap at _MAX_SCENES
        timestamps = [i * 2.0 for i in range(1, 250)]
        pairs = self._run(_fake_stderr(timestamps), duration=600.0)
        self.assertLessEqual(len(pairs), scene_extractor._MAX_SCENES)

    def test_last_scene_end_equals_asset_duration(self):
        pairs = self._run(_fake_stderr([4.0]), duration=9.5)
        self.assertEqual(pairs[-1][1], 9.5)

    def test_single_cut_produces_two_scenes(self):
        pairs = self._run(_fake_stderr([5.0]), duration=10.0)
        self.assertEqual(len(pairs), 2)
        self.assertEqual(pairs[0][0], 0.0)
        self.assertEqual(pairs[1][1], 10.0)


class TestExtractScenes(unittest.TestCase):
    """Tests for extract_scenes() with all I/O helpers mocked."""

    def _run(
        self,
        asset: MediaAsset,
        keyframe_dir: Path,
        *,
        transcribe: bool = False,
        detect_return: list = None,
    ) -> list:
        if detect_return is None:
            detect_return = [(0.0, 4.0), (4.0, 8.0)]

        def fake_kf(video_path, timestamp, directory, *, filename=None):
            return str(directory / (filename or "kf.png"))

        with (
            patch.object(scene_extractor, "detect_scenes", return_value=detect_return),
            patch.object(scene_extractor, "extract_keyframe", side_effect=fake_kf),
            patch.object(
                scene_extractor, "_quality_signals",
                return_value={"blur_score": 800.0, "brightness": 0.6},
            ),
        ):
            return scene_extractor.extract_scenes(
                asset, keyframe_dir, transcribe=transcribe
            )

    def test_scene_count_matches_detected_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            scenes = self._run(_asset(), Path(tmp))
        self.assertEqual(len(scenes), 2)

    def test_scene_fields_are_populated(self):
        with tempfile.TemporaryDirectory() as tmp:
            scenes = self._run(_asset(), Path(tmp))
        s = scenes[0]
        self.assertIsNotNone(s.scene_id)
        self.assertEqual(s.start_time, 0.0)
        self.assertEqual(s.end_time, 4.0)
        self.assertEqual(len(s.keyframe_paths), 1)
        self.assertIn("blur_score", s.quality_signals)

    def test_asset_id_propagated_to_each_scene(self):
        asset = _asset()
        with tempfile.TemporaryDirectory() as tmp:
            scenes = self._run(asset, Path(tmp))
        for s in scenes:
            self.assertEqual(s.asset_id, asset.asset_id)

    def test_no_transcribe_leaves_transcript_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            scenes = self._run(_asset(), Path(tmp), transcribe=False)
        for s in scenes:
            self.assertIsNone(s.transcript)

    def test_keyframe_failure_handled_gracefully(self):
        asset = _asset()
        with tempfile.TemporaryDirectory() as tmp:
            with (
                patch.object(scene_extractor, "detect_scenes", return_value=[(0.0, 5.0)]),
                patch.object(
                    scene_extractor, "extract_keyframe",
                    side_effect=RuntimeError("ffmpeg not found"),
                ),
                patch.object(scene_extractor, "_quality_signals", return_value={}),
            ):
                scenes = scene_extractor.extract_scenes(asset, Path(tmp))
        self.assertEqual(len(scenes), 1)
        self.assertEqual(scenes[0].keyframe_paths, [])
        self.assertEqual(scenes[0].quality_signals, {})

    def test_scene_ids_stable_across_reruns(self):
        asset = _asset()
        with tempfile.TemporaryDirectory() as tmp:
            first = self._run(asset, Path(tmp))
            second = self._run(asset, Path(tmp))
        self.assertEqual(
            [s.scene_id for s in first],
            [s.scene_id for s in second],
        )

    def test_empty_detect_returns_empty_scenes(self):
        with tempfile.TemporaryDirectory() as tmp:
            scenes = self._run(_asset(), Path(tmp), detect_return=[])
        self.assertEqual(scenes, [])


class TestQualitySignals(unittest.TestCase):
    def test_returns_empty_dict_on_missing_file(self):
        result = scene_extractor._quality_signals("/nonexistent/does_not_exist.png")
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    def test_returns_dict_type_always(self):
        result = scene_extractor._quality_signals("/tmp/not_a_real_image.png")
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
