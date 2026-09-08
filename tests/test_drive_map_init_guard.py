"""Tests for the --init guard in scripts/drive_map_builder.py.

--init creates a brand-new spreadsheet suite unconditionally. Running it when
state already holds IDs orphans the live Drive Maps and splits every link that
points at them. These tests prove it refuses, and that the nightly --scan path
is unaffected by the guard.
"""
import importlib.util
import json
import os
import sys
import types

import pytest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "drive_map_builder.py")


def _load_module():
    """Import drive_map_builder with the google libs stubbed out."""
    for name in ("google", "google.oauth2", "google.oauth2.credentials",
                 "googleapiclient", "googleapiclient.discovery"):
        sys.modules.setdefault(name, types.ModuleType(name))
    sys.modules["google.oauth2.credentials"].Credentials = object
    sys.modules["googleapiclient.discovery"].build = lambda *a, **k: None

    spec = importlib.util.spec_from_file_location("drive_map_builder", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def mod(tmp_path, monkeypatch):
    m = _load_module()
    monkeypatch.setattr(m, "STATE_FILE", str(tmp_path / "drive_map_state.json"))
    monkeypatch.setattr(m, "get_services", lambda: (None, None))

    def _no_create(*a, **k):
        raise AssertionError("create_spreadsheet was called - the guard failed")

    monkeypatch.setattr(m, "create_spreadsheet", _no_create)
    return m


def _write_state(mod, payload):
    with open(mod.STATE_FILE, "w") as f:
        json.dump(payload, f)


def test_init_refuses_when_state_exists(mod, monkeypatch):
    _write_state(mod, {"master": "EXISTING_MASTER",
                       "per_drive": {"0AIPzwsJD_qqzUk9PVA": "EXISTING_MKT"}})
    before = open(mod.STATE_FILE).read()
    monkeypatch.setattr(sys, "argv", ["drive_map_builder", "--init"])

    with pytest.raises(SystemExit) as exc:
        mod.main()

    assert exc.value.code == 1
    assert open(mod.STATE_FILE).read() == before, "state file must not be mutated"


def test_init_refuses_with_only_per_drive_state(mod, monkeypatch):
    _write_state(mod, {"per_drive": {"0AIPzwsJD_qqzUk9PVA": "EXISTING_MKT"}})
    monkeypatch.setattr(sys, "argv", ["drive_map_builder", "--init"])

    with pytest.raises(SystemExit) as exc:
        mod.main()

    assert exc.value.code == 1


def test_init_and_scan_are_mutually_exclusive(mod, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["drive_map_builder", "--init", "--scan"])

    with pytest.raises(SystemExit) as exc:
        mod.main()

    assert exc.value.code == 1


def test_scan_path_is_not_blocked_by_the_guard(mod, monkeypatch):
    """Regression: the guard must not interfere with the nightly scan.

    With no state, --scan must reach its own pre-existing "run --init first"
    exit, not the new guard.
    """
    monkeypatch.setattr(sys, "argv", ["drive_map_builder", "--scan"])

    with pytest.raises(SystemExit) as exc:
        mod.main()

    assert exc.value.code == 1
