"""Cached transcripts are source-bound, never invented video evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

BASE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(BASE/'scripts/factcheck_print'),str(BASE/'scripts')]
import opc_capture_cache as cache
import opc_media as media
from opc_contract import GateError

URL='https://www.youtube.com/watch?v=abcdefghijk'

class CaptureCache(unittest.TestCase):
    def test_exact_source_transcript_retains_warning(self):
        store=MagicMock()
        store.list_children.side_effect=[[{'id':'folder','name':'YT-abcdefghijk','mimeType':'application/vnd.google-apps.folder'}],[{'id':'text','name':'transcript.txt'}]]
        text='SOURCE: '+URL+'\n'+'Original transcribed words. '*20
        with tempfile.TemporaryDirectory() as d,patch.object(cache,'read_text',return_value=text):
            root=Path(d);(root/'resources').mkdir()
            result=cache.cached_capture(URL,root,store)
            self.assertFalse(result['video_available']);self.assertIsNone(result['full_file'])
            self.assertIn('no playable',result['reference_warning'])
            self.assertEqual((root/result['transcript_file']).read_text(),text)
    def test_wrong_video_is_not_reused(self):
        store=MagicMock();store.list_children.side_effect=[[{'id':'folder','name':'YT-abcdefghijk','mimeType':'application/vnd.google-apps.folder'}],[{'id':'text','name':'transcript.txt'}]]
        with tempfile.TemporaryDirectory() as d,patch.object(cache,'read_text',return_value='SOURCE: https://youtu.be/otherid1234\n'+'wrong text '*40):
            with self.assertRaises(GateError):cache.cached_capture(URL,Path(d),store)
    def test_placeholder_rejected(self):
        store=MagicMock();store.list_children.side_effect=[[{'id':'folder','name':'YT-abcdefghijk','mimeType':'application/vnd.google-apps.folder'}],[{'id':'text','name':'transcript.txt'}]]
        text='SOURCE: '+URL+'\n[MEDIA RETRIEVAL BLOCKED]\n'+'not a transcript '*30
        with tempfile.TemporaryDirectory() as d,patch.object(cache,'read_text',return_value=text):
            with self.assertRaises(GateError):cache.cached_capture(URL,Path(d),store)
    def test_missing_video_never_becomes_fake_cut(self):
        with patch.object(media,'probe') as probe:
            self.assertIsNone(cache.cut_video({'video_available':False},[],Path('/tmp')))
            probe.assert_not_called()
    def setup_zero(self,counts):
        store=MagicMock();store.list_children.side_effect=[
            [{'id':'f','appProperties':{'opcPrintRun':'key','state':'BLOCKED_NOT_APPROVED'}}],
            [{'id':'r','name':'resources'}],
            [{'id':'u','name':'usage-summary.json'},{'id':'e','name':'failure.json'}]]
        read=patch.object(cache,'read_text',side_effect=[json.dumps(counts),json.dumps({'message':'Source video could not be retrieved by routes'})])
        return store,read
    def test_generation_free_failure_can_resume(self):
        store,read=self.setup_zero({'text_responses':0,'image_requests':0})
        with read:cache.verify_zero_generation(store,'key')
    def test_prior_text_generation_blocks_resume(self):
        store,read=self.setup_zero({'text_responses':1,'image_requests':0})
        with read,self.assertRaises(GateError):cache.verify_zero_generation(store,'key')
    def test_prior_image_generation_blocks_resume(self):
        store,read=self.setup_zero({'text_responses':0,'image_requests':1})
        with read,self.assertRaises(GateError):cache.verify_zero_generation(store,'key')
    def test_missing_usage_not_zero(self):
        store,read=self.setup_zero({})
        with read,self.assertRaises(GateError):cache.verify_zero_generation(store,'key')

if __name__=='__main__':unittest.main()
