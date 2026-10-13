"""Synthetic checks for curated OPC post specs. No network or paid APIs."""
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parents[1]/"scripts/factcheck_print"
sys.path.insert(0,str(HERE))
import opc_curated_batch as b

class CuratedSpecs(unittest.TestCase):
    def test_two_posts_five_unique_visual_jobs(self):
        posts=b.load_posts()
        self.assertEqual(len(posts),2)
        for post in posts:
            self.assertEqual(len(post["slides"]),5)
            self.assertEqual([s["visual_key"] for s in post["slides"]],[f"A{i}" for i in range(1,6)])
            self.assertEqual([v["key"] for v in post["visuals"]],[f"A{i}" for i in range(1,6)])

    def test_text_audit_passes_curated_specs(self):
        for post in b.load_posts():
            sources=[{"id":s["id"]} for s in post["sources"]]
            report=b.text_audit(post,sources)
            self.assertTrue(report["passed"])

    def test_no_text_model_credentials_or_calls(self):
        source=(HERE/"opc_curated_batch.py").read_text(encoding="utf-8")
        self.assertNotIn("CLAUDE_KEY",source)
        self.assertNotIn("OPENAI_API_KEY",source)
        self.assertNotIn("Model(",source)

if __name__=="__main__":
    unittest.main()
