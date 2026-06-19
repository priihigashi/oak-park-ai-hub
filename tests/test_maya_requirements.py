"""Requirement -> test traceability: every RM/RE is mapped and unit refs exist."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from maya import requirements as req

HERE = os.path.dirname(__file__)
MAYA_DIR = os.path.join(HERE, "..", "scripts", "maya")


def test_no_requirement_is_missing():
    assert req.missing_ids() == []


def test_every_requirement_has_desc_and_type():
    for rid, meta in req.REQUIREMENTS.items():
        assert meta.get("desc"), rid
        assert meta.get("type") in {"unit", "spec", "ops"}, rid
        assert meta.get("ref"), rid


def test_unit_refs_point_at_existing_test_files():
    for rid, meta in req.REQUIREMENTS.items():
        if meta["type"] == "unit":
            path = os.path.join(HERE, meta["ref"])
            assert os.path.exists(path), f"{rid} -> missing test file {meta['ref']}"


def test_spec_refs_point_at_existing_artifacts():
    for rid, meta in req.REQUIREMENTS.items():
        if meta["type"] == "spec":
            path = os.path.join(MAYA_DIR, meta["ref"])
            assert os.path.exists(path), f"{rid} -> missing spec artifact {meta['ref']}"
