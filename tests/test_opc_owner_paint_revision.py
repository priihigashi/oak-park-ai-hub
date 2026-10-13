"""Owner paint revision tests. No network or paid API calls."""
import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1] / "scripts/factcheck_print"
spec = importlib.util.spec_from_file_location("opc_owner_paint_revision", HERE / "opc_owner_paint_revision.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class OwnerRevision(unittest.TestCase):
    def test_five_distinct_visual_jobs(self):
        d = m.draft()
        self.assertEqual(len(d["slides"]), 5)
        self.assertEqual([x["visual_key"] for x in d["slides"]], ["A1","A2","A3","A4","A5"])
    def test_only_four_new_images(self):
        self.assertEqual(m.NEW_IMAGE_KEYS, ("A1","A2","A4","A5"))
    def test_no_public_ai_boilerplate(self):
        self.assertNotIn("AI illustration", m.draft()["caption"])
    def test_sampling_copy_is_process_not_exact_color(self):
        card = m.draft()["slides"][3]
        self.assertIn("foam board", card["body"].lower())
        self.assertNotIn("exact color", card["body"].lower())

if __name__ == "__main__":
    unittest.main()
