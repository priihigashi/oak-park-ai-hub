"""Regression for the reproduced null-citation crash. No paid API calls."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/factcheck_print'))
from opc_llm import observed_urls, Model

class OptionalCitations(unittest.TestCase):
    def test_claude_null_citations(self):
        raw={'content':[{'type':'text','text':'{}','citations':None}]}
        self.assertEqual(observed_urls('claude',raw),set())
    def test_null_content(self):
        self.assertEqual(observed_urls('claude',{'content':None}),set())
    def test_null_annotations(self):
        raw={'output':[{'type':'message','content':[{'type':'output_text','annotations':None}]}]}
        self.assertEqual(observed_urls('openai',raw),set())
    def test_real_search_survives_optional_citations(self):
        raw={'content':[{'type':'text','citations':None},{'type':'web_search_tool_result','content':[{'url':'https://example.org/evidence'}]}]}
        self.assertEqual(observed_urls('claude',raw),{'https://example.org/evidence'})
    def test_usage_saved_before_parsing_error(self):
        with tempfile.TemporaryDirectory() as d:
            m=Model.__new__(Model);m.engine='claude';m.model='claude-sonnet-4-6'
            m.entries=[];m.search_urls=set();m.ledger_path=Path(d)/'usage.json'
            with patch('opc_llm.observed_urls',side_effect=ValueError('test')):
                with self.assertRaises(ValueError):m._record({'usage':{'input_tokens':10}})
            self.assertTrue(m.ledger_path.exists())

if __name__=='__main__':unittest.main()
