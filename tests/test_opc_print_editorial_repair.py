"""Repair and checkpoint tests use synthetic data, never paid API requests."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/factcheck_print'))
from opc_contract import GateError
from opc_editorial import accepted, copy_checks, repair_after_review, review_or_repair
from opc_resume_editorial import verify_checkpoint


def draft():
    return {'caption':'Test the color in your room.','slides':[
      {'id':i,'layout':'point','headline':'Check your own sample','body':'View it in your room.'}
      for i in range(1,6)]}


def fake_model(responses, calls=0):
    model=Mock();model.calls=calls;model.max_calls=7;model.engine='claude';model.model='synthetic'
    def ask(*args,**kwargs):
        model.calls+=1
        return responses.pop(0)
    model.ask.side_effect=ask
    return model


class Repair(unittest.TestCase):
    def test_truthy_not_boolean_rejected(self):
        self.assertFalse(accepted({'passed':'true','english':True,'issues':[]}))
    def test_issues_block_pass(self):
        self.assertFalse(accepted({'passed':True,'english':True,'issues':['unsupported claim']}))
    def test_sponsor_not_invented(self):
        x=draft();x['caption']+=' #ad'
        self.assertIn('Unverified sponsorship in caption',copy_checks(x))
    def test_pass_does_not_rewrite(self):
        m=fake_model([{'passed':True,'english':True,'issues':[]}])
        with tempfile.TemporaryDirectory() as d:
            x,cert=review_or_repair(m,draft(),[],[],Path(d))
        self.assertEqual(m.calls,1);self.assertFalse(cert['repaired'])
    def test_saved_failure_uses_only_two_remaining_calls(self):
        m=fake_model([draft(),{'passed':True,'english':True,'issues':[]}],calls=5)
        with tempfile.TemporaryDirectory() as d:
            x,cert=repair_after_review(m,draft(),[],[],Path(d),{'passed':False,'issues':['fix']})
            self.assertTrue((Path(d)/'feed-before-editorial-repair.json').exists())
        self.assertEqual(m.calls,7);self.assertTrue(cert['repaired'])
    def test_failed_revision_not_force_approved(self):
        m=fake_model([draft(),{'passed':False,'english':True,'issues':['still unsupported']}],calls=5)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(GateError):
            repair_after_review(m,draft(),[],[],Path(d),{'passed':False,'issues':['fix']})
        self.assertEqual(m.calls,7)
    def test_budget_guard_before_paid_request(self):
        m=fake_model([],calls=6)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(GateError):
            repair_after_review(m,draft(),[],[],Path(d),{'passed':False,'issues':['fix']})
        m.ask.assert_not_called()


class Checkpoint(unittest.TestCase):
    def sample(self,root):
        p=root/'resources';p.mkdir()
        files={'run.json':{'run_key':'same'},'failure.json':{'message':'Editorial/source review failed; no ready status was written'},
          'text-usage.json':{'entries':[{'engine':'claude','status':'measured_response','estimated_usd':1}]},
          'usage-summary.json':{'image_requests':0},'model-result-01.json':{'passed':False,'issues':['fix']}}
        for name,value in files.items():(p/name).write_text(json.dumps(value))
    def test_keep_usage_history(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.sample(p);u,fail,n=verify_checkpoint(p,'same')
            self.assertEqual(u['entries'][0]['estimated_usd'],1);self.assertEqual(n,1)
    def test_wrong_run_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.sample(p)
            with self.assertRaises(GateError):verify_checkpoint(p,'different')
    def test_prior_images_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.sample(p);(p/'resources/usage-summary.json').write_text('{"image_requests":1}')
            with self.assertRaises(GateError):verify_checkpoint(p,'same')
    def test_uncertain_usage_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.sample(p);(p/'resources/text-usage.json').write_text('{"entries":[{"engine":"claude","status":"request_failed_or_unknown"}]}')
            with self.assertRaises(GateError):verify_checkpoint(p,'same')

if __name__=='__main__':unittest.main()
