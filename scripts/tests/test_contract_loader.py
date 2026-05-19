"""Tests for STORY-001 route-specific contract loader stub."""

import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "content_creator"))

from contract_loader import load_contract  # noqa: E402


class ContractLoaderTest(unittest.TestCase):
    def test_loads_opc_stub(self):
        self.assertEqual(
            load_contract("opc"),
            {"route": "opc", "version": "0.1.0-stub", "loaded": False},
        )

    def test_loads_news_stub(self):
        self.assertEqual(
            load_contract("news"),
            {"route": "news", "version": "0.1.0-stub", "loaded": False},
        )

    def test_maps_existing_news_route_aliases_to_news_contract(self):
        self.assertEqual(load_contract("brazil")["route"], "news")
        self.assertEqual(load_contract("usa")["route"], "news")

    def test_unrouted_is_kill_gate_placeholder(self):
        with self.assertRaises(ValueError):
            load_contract("unrouted")

    def test_unknown_route_raises(self):
        with self.assertRaises(ValueError):
            load_contract("stocks")


if __name__ == "__main__":
    unittest.main()
