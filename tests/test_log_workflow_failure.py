"""Tests for the four hardening fixes on log_workflow_failure.py (2026-08-11).

The original fix (5398be3) made content_creator.yml log its failures at all,
which was the real bug. Codex's round-3 audit then found four ways the logger
could still lie:

  1. EXPECTED_HEADER was declared and never checked -- column drift would write
     every field into the wrong place, which looks logged but is not.
  2. No read-back -- the append receipt was trusted as proof (KRM #15).
  3. Retries reuse GITHUB_RUN_ID, so a flapping workflow duplicates itself.
  4. When logging failed, nothing said so -- the exact false all-clear this
     script exists to end.

Each test below asserts the FAILURE case, so it goes red if the hardening is
removed (KRM #16).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import log_workflow_failure as lwf  # noqa: E402

GOOD_HEADER = [["TIMESTAMP_UTC", "WORKFLOW", "RUN_ID", "STAGE",
                "ERROR", "RUN_URL", "RESOLVED", "NOTE"]]


class TestHeaderValidation(unittest.TestCase):
    def test_correct_header_passes(self):
        with mock.patch.object(lwf, "_read_range", return_value=GOOD_HEADER):
            self.assertTrue(lwf._header_ok("tok"))

    def test_reordered_columns_are_refused(self):
        drifted = [["WORKFLOW", "TIMESTAMP_UTC", "RUN_ID", "STAGE",
                    "ERROR", "RUN_URL", "RESOLVED", "NOTE"]]
        with mock.patch.object(lwf, "_read_range", return_value=drifted):
            self.assertFalse(lwf._header_ok("tok"))

    def test_renamed_column_is_refused(self):
        drifted = [["TIMESTAMP_UTC", "WORKFLOW", "RUN", "STAGE",
                    "ERROR", "RUN_URL", "RESOLVED", "NOTE"]]
        with mock.patch.object(lwf, "_read_range", return_value=drifted):
            self.assertFalse(lwf._header_ok("tok"))

    def test_empty_tab_is_refused_not_assumed_ok(self):
        with mock.patch.object(lwf, "_read_range", return_value=[]):
            self.assertFalse(lwf._header_ok("tok"))


class TestIdempotency(unittest.TestCase):
    ROWS = [["111", "create-content"], ["222", "render"]]

    def test_same_run_and_stage_is_detected_as_duplicate(self):
        with mock.patch.object(lwf, "_read_range", return_value=self.ROWS):
            self.assertTrue(lwf._already_logged("tok", "111", "create-content"))

    def test_same_run_different_stage_is_not_a_duplicate(self):
        with mock.patch.object(lwf, "_read_range", return_value=self.ROWS):
            self.assertFalse(lwf._already_logged("tok", "111", "upload"))

    def test_new_run_is_not_a_duplicate(self):
        with mock.patch.object(lwf, "_read_range", return_value=self.ROWS):
            self.assertFalse(lwf._already_logged("tok", "999", "create-content"))

    def test_missing_run_id_never_claims_duplicate(self):
        with mock.patch.object(lwf, "_read_range", return_value=self.ROWS):
            self.assertFalse(lwf._already_logged("tok", "", "create-content"))


class TestReadback(unittest.TestCase):
    def test_row_present_passes(self):
        rows = [["2026-08-11T00:00:00Z", "content_creator.yml", "555", "stage"]]
        with mock.patch.object(lwf, "_read_range", return_value=rows):
            self.assertTrue(lwf._readback_matches("tok", "'x'!A9:H9", "555"))

    def test_row_absent_fails_even_though_append_reported_success(self):
        """The whole point: a receipt is not evidence."""
        with mock.patch.object(lwf, "_read_range", return_value=[]):
            self.assertFalse(lwf._readback_matches("tok", "'x'!A9:H9", "555"))

    def test_wrong_run_id_in_the_row_fails(self):
        rows = [["ts", "wf", "OTHER", "stage"]]
        with mock.patch.object(lwf, "_read_range", return_value=rows):
            self.assertFalse(lwf._readback_matches("tok", "'x'!A9:H9", "555"))

    def test_no_updated_range_fails(self):
        self.assertFalse(lwf._readback_matches("tok", "", "555"))


class TestAppendRefusesOnDrift(unittest.TestCase):
    def test_header_drift_blocks_the_write_entirely(self):
        with mock.patch.object(lwf, "_access_token", return_value="tok"), \
             mock.patch.object(lwf, "_header_ok", return_value=False), \
             mock.patch.object(lwf.urllib.request, "urlopen") as opened:
            self.assertFalse(lwf.append_failure("wf.yml", "stage", "boom"))
        opened.assert_not_called()

    def test_duplicate_short_circuits_without_writing(self):
        with mock.patch.object(lwf, "_access_token", return_value="tok"), \
             mock.patch.object(lwf, "_header_ok", return_value=True), \
             mock.patch.object(lwf, "_already_logged", return_value=True), \
             mock.patch.object(lwf.urllib.request, "urlopen") as opened:
            self.assertTrue(lwf.append_failure("wf.yml", "stage", "boom"))
        opened.assert_not_called()


class TestUnloggedFailureIsVisible(unittest.TestCase):
    def test_marker_is_emitted_when_logging_fails(self):
        argv = ["prog", "--workflow", "content_creator.yml", "--stage", "create"]
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.object(lwf, "append_failure", return_value=False), \
             mock.patch("sys.stderr") as err:
            self.assertEqual(lwf.main(), 0)
        written = "".join(str(c.args[0]) for c in err.write.call_args_list if c.args)
        self.assertIn("LOG_FAILURE_UNLOGGED", written)

    def test_no_marker_when_logging_succeeded(self):
        argv = ["prog", "--workflow", "content_creator.yml", "--stage", "create"]
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.object(lwf, "append_failure", return_value=True), \
             mock.patch("sys.stderr") as err:
            self.assertEqual(lwf.main(), 0)
        written = "".join(str(c.args[0]) for c in err.write.call_args_list if c.args)
        self.assertNotIn("LOG_FAILURE_UNLOGGED", written)

    def test_exit_code_stays_zero_so_the_real_failure_is_not_masked(self):
        argv = ["prog", "--workflow", "wf.yml", "--stage", "s"]
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.object(lwf, "append_failure", side_effect=RuntimeError("net")):
            self.assertEqual(lwf.main(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
