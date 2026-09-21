"""Assisted acceptance must never masquerade as an autonomous pass."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/factcheck_print'))
from opc_assisted_acceptance import verify_pack
from opc_contract import GateError

class Assisted(unittest.TestCase):
    def test_mode_and_evidence_are_bound(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'resources').mkdir();(root/'resources/evidence.json').write_text('{}')
            pack={'mode':'assisted_acceptance','original_run_key':'same','approved':False,'published':False,
                  'editorial_review':{'provider':'ChatGPT-assisted','automated_review_passed':False},
                  'evidence_sha256':hashlib.sha256(b'{}').hexdigest()}
            verify_pack(pack,root,'same')
            pack['editorial_review']['automated_review_passed']=True
            with self.assertRaises(GateError):verify_pack(pack,root,'same')
    def test_cannot_approve_or_swap_sources(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'resources').mkdir();(root/'resources/evidence.json').write_text('{}')
            pack={'mode':'assisted_acceptance','original_run_key':'same','approved':False,'published':False,
                  'editorial_review':{'provider':'ChatGPT-assisted','automated_review_passed':False},'evidence_sha256':'wrong'}
            with self.assertRaises(GateError):verify_pack(pack,root,'same')
            pack['approved']=True
            with self.assertRaises(GateError):verify_pack(pack,root,'same')
if __name__=='__main__':unittest.main()
