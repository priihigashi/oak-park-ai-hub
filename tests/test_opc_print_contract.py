"""Synthetic fixtures test contracts; they are never described as live evidence."""
import copy
import importlib.util
import pathlib
import tempfile
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / 'scripts/factcheck_print/opc_contract.py'
sp = importlib.util.spec_from_file_location('opc_contract', PATH)
m = importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)


def fixture():
    return {'project':'opc','language':'en','status':m.STATUS,'approved':False,'kind':'education',
            'title':'Choosing a countertop','caption':'Save these material tips.',
            'hashtags':'#KitchenRemodel', 'editorial_review':{'passed':True},
            'sources':[{'id':'S1','url':'https://example.org/care','observed_in_search':True,'screenshot':'resources/source.jpg'}],
            'assets':[{'key':'A1','kind':'ai_illustration','model':m.MODELS[0],'path':'resources/material.jpg','sha256':'test'}],
            'slides':[{'id':i,'layout':'cover' if i==1 else 'close' if i==5 else 'point',
                       'headline':'Check the care guide','body':'Match the surface to your daily routine.',
                       'source_ids':[] if i in (1,5) else ['S1'],'visual_key':'A1',
                       'intentional_reuse': True if i>1 else False} for i in range(1,6)]}


class Contracts(unittest.TestCase):
    def test_valid_metadata(self):
        self.assertTrue(m.validate(fixture())['passed'])
    def reject(self, key, value):
        s=fixture();s[key]=value
        with self.assertRaises(m.GateError): m.validate(s)
    def test_english_only(self): self.reject('language','pt')
    def test_project_mandatory(self): self.reject('project','brazil')
    def test_cannot_approve(self): self.reject('approved',True)
    def test_cannot_publish_status(self): self.reject('status','Published')
    def test_missing_editorial_review(self): self.reject('editorial_review',{})
    def test_dense_text_rejected(self):
        s=fixture();s['slides'][1]['body']='word '*50
        with self.assertRaisesRegex(m.GateError,'dense'): m.validate(s)
    def test_long_hook(self):
        s=fixture();s['slides'][0]['headline']='word '*10
        with self.assertRaisesRegex(m.GateError,'headline'): m.validate(s)
    def test_no_assets(self): self.reject('assets',[])
    def test_bad_source(self):
        s=fixture();s['sources'][0]['observed_in_search']=False
        with self.assertRaisesRegex(m.GateError,'researched'): m.validate(s)
    def test_no_screenshot(self):
        s=fixture();s['sources'][0]['screenshot']=''
        with self.assertRaisesRegex(m.GateError,'captured'): m.validate(s)
    def test_quoted_competitor_rejected(self):
        s=fixture();s['slides'][2]['body']='Fictional Counter Co says this.'
        with self.assertRaisesRegex(m.GateError,'competitor'): m.validate(s,aliases=['Fictional Counter Co'])
    def test_false_badge(self):
        s=fixture();s['slides'][1]['badge']='false'
        with self.assertRaisesRegex(m.GateError,'badge'): m.validate(s)
    def test_portuguese_rejected(self):
        s=fixture();s['slides'][1]['body']='Confira os fatos verificados.'
        with self.assertRaises(m.GateError): m.validate(s)
    def test_no_ai_before_after(self): self.reject('kind','project_proof')
    def test_no_silent_alternate_model(self):
        s=fixture();s['assets'][0]['model']='unapproved/model'
        with self.assertRaisesRegex(m.GateError,'model'): m.validate(s)
    def test_public_ai_disclosure_not_required(self):
        s=fixture();s['caption']='Save this.'
        self.assertTrue(m.validate(s)['passed'])
    def test_consecutive_visual_reuse_requires_intent(self):
        s=fixture()
        for i in range(1,len(s['slides'])): s['slides'][i]['intentional_reuse']=False
        with self.assertRaisesRegex(m.GateError,'consecutive visual reuse'): m.validate(s)
        for i in range(1,len(s['slides'])): s['slides'][i]['intentional_reuse']=True
        self.assertTrue(m.validate(s)['passed'])
    def test_raw_model_code(self):
        s=fixture();s['slides'][1]['body']='Care &lt;cite index="1"&gt;guide&lt;/cite&gt;'
        with self.assertRaises(m.GateError): m.validate(s)
    def test_citation_cleaning(self):
        self.assertEqual(m.plain('Care &amp;lt;cite index="1"&amp;gt;guide&amp;lt;/cite&amp;gt;'),'Care guide')
        self.assertEqual(m.plain('<script>alert(1)</script><b>Safe</b>'),'Safe')
    def test_missing_asset_on_disk(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(m.GateError,'asset'): m.validate(fixture(),pathlib.Path(d))
    def test_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(m.GateError): m.safe_relative(pathlib.Path(d),'../secret')
    def test_url_normalization(self):
        self.assertEqual(m.canonical_url('https://youtu.be/abcdefghijk?t=5'),m.canonical_url('https://www.youtube.com/watch?v=abcdefghijk&si=tracking'))
    def test_url_credentials_rejected(self):
        with self.assertRaises(m.GateError): m.canonical_url('https://user:pw@youtube.com/watch?v=abcdefghijk')
    def test_duplicate_url(self):
        rows=[list(m.HEADERS),['','Other title','','','','','','','','','','','https://youtu.be/abcdefghijk']]
        self.assertEqual(m.find_duplicates(rows,'Quartz granite countertop',['quartz','granite','countertop'],'https://www.youtube.com/watch?v=abcdefghijk'),[2])
    def test_duplicate_keywords(self):
        rows=[list(m.HEADERS),['','Granite versus quartz countertop guide']]
        self.assertEqual(m.find_duplicates(rows,'New angle',['quartz','granite','countertop']),[2])
    def test_dedupe_fails_closed_on_schema(self):
        with self.assertRaises(m.GateError): m.find_duplicates([], 'Anything',['one','two','three'])
    def test_headers_order_is_not_assumed(self):
        heads=list(reversed(m.HEADERS));values={'Title':'A countertop','Status':m.STATUS}
        row=m.tracker_row(heads,values)
        self.assertEqual(row[heads.index('Title')],'A countertop')
    def test_new_schema_blocked(self):
        with self.assertRaises(m.GateError): m.tracker_row(list(m.HEADERS)+['new'],{'Status':m.STATUS})
    def test_quarantine_blocks_photo(self):
        p={'Provenance':'REAL OPC','Identity Confidence':'VERIFIED (tracker evidence)','Approval Status':'APPROVED FOR WEBSITE','Selected Copy Drive Location':'https://drive.google.com/file/d/fake/view'}
        self.assertTrue(m.photo_eligible(p));p['Notes']='QUARANTINED'
        self.assertFalse(m.photo_eligible(p))
    def test_unverified_photo(self):
        self.assertFalse(m.photo_eligible({'Provenance':'REAL OPC'}))

if __name__=='__main__': unittest.main()
