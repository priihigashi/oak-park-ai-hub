"""Tests for SH-149 PR B — motion/static gate integration into carousel_reviewer.

Verifies the additive hook in ``carousel_reviewer.check_built_post`` /
``_run_motion_static_gate_check``:
- ``STORY_PIPELINE_V2_ENABLED=0`` (default) -> no motion-static-gate issues appended
- ``STORY_PIPELINE_V2_ENABLED=1`` -> violations appended as
  ``[motion-static-gate] kind: reason`` strings
- Drive-only review (no local png/motion folders) -> empty, skip silently
- unknown/empty niche -> silent skip, never raises
- missing/unavailable gate module -> empty list (no crash)
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

try:
    import carousel_reviewer as _reviewer  # noqa: E402
    _REVIEWER_IMPORT_ERROR = None
except Exception as _e:
    _reviewer = None
    _REVIEWER_IMPORT_ERROR = _e


_SKIP_REASON = (
    f"carousel_reviewer unavailable in this env: {_REVIEWER_IMPORT_ERROR!r}. "
    "Tests will run in CI where production deps are installed."
)


def _build_work_dir(tmp: Path, post_id: str, static: list[str], motion: list[str]):
    """Materialize the canonical <work_dir>/<post_id>/{png,motion}/<files> layout."""
    base = tmp / post_id
    if static:
        png = base / "png"
        png.mkdir(parents=True, exist_ok=True)
        for name in static:
            (png / name).write_bytes(b"x")
    if motion:
        motion_dir = base / "motion"
        motion_dir.mkdir(parents=True, exist_ok=True)
        for name in motion:
            (motion_dir / name).write_bytes(b"x")
    return base


@unittest.skipIf(_reviewer is None, _SKIP_REASON)
class MotionStaticGateReviewerIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.reviewer = _reviewer
        self.tmp = Path(tempfile.mkdtemp(prefix="sh149-reviewer-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- flag OFF (default) ------------------------------------------------

    def test_flag_off_returns_empty_even_with_missing_motion(self):
        _build_work_dir(self.tmp, "post-flagoff", static=["slide1.png"], motion=[])
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "0"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                {}, "opc", "post-flagoff", str(self.tmp)
            )
        self.assertEqual(issues, [])

    def test_flag_default_env_returns_empty(self):
        _build_work_dir(self.tmp, "post-default", static=[], motion=[])
        env = {k: v for k, v in os.environ.items() if k != "STORY_PIPELINE_V2_ENABLED"}
        env["WORK_DIR"] = str(self.tmp)
        with patch.dict(os.environ, env, clear=True):
            issues = self.reviewer._run_motion_static_gate_check(
                {}, "opc", "post-default", str(self.tmp)
            )
        self.assertEqual(issues, [])

    # --- flag ON — happy path ---------------------------------------------

    def test_full_build_passes(self):
        _build_work_dir(
            self.tmp,
            "post-full",
            static=["slide1.png", "slide2.png"],
            motion=["carousel.mp4", "carousel.gif", "cover_preview.png", "slide2_motion.png"],
        )
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                {}, "opc", "post-full", str(self.tmp)
            )
        self.assertEqual(issues, [])

    # --- flag ON — violation paths ----------------------------------------

    def test_empty_motion_folder_violation(self):
        _build_work_dir(self.tmp, "post-empty-motion", static=["s.png"], motion=[])
        # Need motion dir to exist (even if empty) so the helper doesn't bail early
        (self.tmp / "post-empty-motion" / "motion").mkdir(parents=True, exist_ok=True)
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                {}, "opc", "post-empty-motion", str(self.tmp)
            )
        kinds = [s for s in issues if "empty_motion" in s]
        self.assertEqual(len(kinds), 1)
        self.assertTrue(issues[0].startswith("[motion-static-gate]"))

    def test_missing_mp4_violation(self):
        _build_work_dir(
            self.tmp, "post-no-mp4",
            static=["s.png"],
            motion=["c.gif", "cover_preview.png"],
        )
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                {}, "opc", "post-no-mp4", str(self.tmp)
            )
        self.assertTrue(any("missing_mp4" in s for s in issues))
        self.assertFalse(any("missing_gif" in s for s in issues))

    def test_missing_static_violation(self):
        _build_work_dir(
            self.tmp, "post-no-static",
            static=[],
            motion=["c.mp4", "c.gif", "preview.png"],
        )
        # Need png dir to exist so the helper doesn't bail early
        (self.tmp / "post-no-static" / "png").mkdir(parents=True, exist_ok=True)
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                {}, "opc", "post-no-static", str(self.tmp)
            )
        self.assertTrue(any("missing_static" in s for s in issues))

    # --- flag ON — static_only override ----------------------------------

    def test_static_only_override_skips_motion_checks(self):
        _build_work_dir(self.tmp, "post-static-only", static=["s.png"], motion=[])
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                {"static_only": True}, "opc", "post-static-only", str(self.tmp)
            )
        self.assertEqual(issues, [])

    # --- niche filtering / safety -----------------------------------------

    def test_flag_on_truthy_values_all_enable(self):
        _build_work_dir(self.tmp, "post-truthy", static=["s.png"], motion=[])
        (self.tmp / "post-truthy" / "motion").mkdir(parents=True, exist_ok=True)
        for val in ("1", "true", "TRUE", "yes", "on"):
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": val}, clear=False):
                issues = self.reviewer._run_motion_static_gate_check(
                    {}, "opc", "post-truthy", str(self.tmp)
                )
            self.assertTrue(len(issues) >= 1, f"value {val!r} should enable gate")

    def test_unknown_niche_silently_skipped(self):
        _build_work_dir(self.tmp, "post-bad-niche", static=[], motion=[])
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                {}, "stocks", "post-bad-niche", str(self.tmp)
            )
        self.assertEqual(issues, [])

    def test_empty_post_id_silently_skipped(self):
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                {}, "opc", "", str(self.tmp)
            )
        self.assertEqual(issues, [])

    def test_drive_only_review_path_silently_skipped(self):
        """If neither png/ nor motion/ exists on disk, the helper bails early
        (Drive-only review path — file walker can't run, but reviewer must not crash)."""
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                {}, "opc", "post-drive-only", str(self.tmp)
            )
        self.assertEqual(issues, [])

    def test_none_content_does_not_crash(self):
        _build_work_dir(self.tmp, "post-none-content", static=["s.png"], motion=[])
        (self.tmp / "post-none-content" / "motion").mkdir(parents=True, exist_ok=True)
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
            issues = self.reviewer._run_motion_static_gate_check(
                None, "opc", "post-none-content", str(self.tmp)
            )
        self.assertIsInstance(issues, list)

    def test_gate_module_unavailable_returns_empty(self):
        _build_work_dir(self.tmp, "post-mod-missing", static=[], motion=[])
        with patch.object(self.reviewer, "check_motion_static_siblings", None):
            with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1"}, clear=False):
                issues = self.reviewer._run_motion_static_gate_check(
                    {}, "opc", "post-mod-missing", str(self.tmp)
                )
            self.assertEqual(issues, [])

    # --- integration via check_built_post ----------------------------------

    def test_check_built_post_flag_off_no_motion_static_issues(self):
        _build_work_dir(self.tmp, "cbp-flagoff", static=["s.png"], motion=[])
        (self.tmp / "cbp-flagoff" / "motion").mkdir(parents=True, exist_ok=True)
        result = {
            "post_id": "cbp-flagoff",
            "topic": "Test topic",
            "niche": "opc",
            "content": {},
        }
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "0", "WORK_DIR": str(self.tmp)}, clear=False):
            out = self.reviewer.check_built_post(result)
        ms_issues = [i for i in out["issues"] if "[motion-static-gate]" in i]
        self.assertEqual(ms_issues, [])

    def test_check_built_post_flag_on_appends_motion_static_issues(self):
        # Build with png/ populated but motion/ empty -> empty_motion violation
        _build_work_dir(self.tmp, "cbp-flagon", static=["slide1.png"], motion=[])
        (self.tmp / "cbp-flagon" / "motion").mkdir(parents=True, exist_ok=True)
        result = {
            "post_id": "cbp-flagon",
            "topic": "Test topic",
            "niche": "brazil",
            "content": {},
        }
        with patch.dict(os.environ, {"STORY_PIPELINE_V2_ENABLED": "1", "WORK_DIR": str(self.tmp)}, clear=False):
            out = self.reviewer.check_built_post(result)
        ms_issues = [i for i in out["issues"] if "[motion-static-gate]" in i]
        self.assertGreaterEqual(len(ms_issues), 1)
        self.assertTrue(any("empty_motion" in i for i in ms_issues))


if __name__ == "__main__":
    unittest.main()
