"""No paid APIs: adversarial inputs, provenance, media and failure behavior."""
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

HERE=Path(__file__).resolve().parents[1]/'scripts/factcheck_print'
sys.path.insert(0,str(HERE))
import opc_contract as c
import opc_llm as llm
import opc_network as net
import opc_media as media
import opc_usage
import resolve_inputs as inputs
from opc_store import Store, quote_tab


class Inputs(unittest.TestCase):
    def test_opc_issue_routes_opc(self):
        x=inputs.resolve({'EVT':'issues','ISSUE_AUTHOR':'priihigashi','ISSUE_TITLE':'opc-print: quartz versus granite'})
        self.assertEqual((x['project'],x['mode']),('opc','idea'))
    def test_opc_link(self):
        x=inputs.resolve({'EVT':'issues','ISSUE_AUTHOR':'priihigashi','ISSUE_TITLE':'opc-print: https://youtu.be/abcdefghijk'})
        self.assertEqual((x['project'],x['mode']),('opc','link'))
    def test_opc_private_chat_spec(self):
        spec='1UJJPeilZ5deMFn4eca2J1KX4RhP3Sbdy'
        x=inputs.resolve({'EVT':'issues','ISSUE_AUTHOR':'priihigashi','ISSUE_TITLE':'opc-chat: '+spec})
        self.assertEqual((x['project'],x['mode'],x['chat_spec_id']),('opc','chat_spec',spec))
    def test_invalid_chat_spec_blocked(self):
        with self.assertRaises(ValueError):
            inputs.resolve({'EVT':'issues','ISSUE_AUTHOR':'priihigashi','ISSUE_TITLE':'opc-chat: ../../secret'})
    def test_legacy_news_unchanged(self):
        x=inputs.resolve({'EVT':'issues','ISSUE_AUTHOR':'priihigashi','ISSUE_TITLE':'factcheck: https://youtu.be/abcdefghijk'})
        self.assertEqual(x['project'],'brazil')
    def test_foreign_issue_cannot_spend(self):
        with self.assertRaises(ValueError): inputs.resolve({'EVT':'issues','ISSUE_AUTHOR':'other','ISSUE_TITLE':'opc-print: kitchen'})
    def test_find_idea(self):
        x=inputs.resolve({'EVT':'issues','ISSUE_AUTHOR':'priihigashi','ISSUE_TITLE':'opc-print: procure uma ideia'})
        self.assertEqual(x['mode'],'discover')
    def test_multiline_url(self):
        self.assertFalse(inputs.video_url('https://youtu.be/abcdefghijk\nFC_PROJECT=opc'))
    def test_hostname_suffix_attack(self):
        self.assertFalse(inputs.video_url('https://youtube.com.evil.example/watch?v=abcdefghijk'))
    def test_userinfo(self):
        self.assertFalse(inputs.video_url('https://name:secret@youtube.com/watch?v=abcdefghijk'))
    def test_model_whitelist(self):
        with self.assertRaises(ValueError): inputs.resolve({'IN_PROJECT':'opc','IN_IDEA':'kitchen','IN_IMAGE_MODEL':'wrong/model'})
    def test_missing_input(self):
        with self.assertRaises(ValueError): inputs.resolve({'IN_PROJECT':'opc'})
    def test_invalid_rebuild(self):
        with self.assertRaises(ValueError): inputs.resolve({'IN_PROJECT':'opc','IN_IDEA':'kitchen','IN_REBUILD_ROW':'-1'})
    def test_notes_are_data(self):
        x=inputs.resolve({'IN_PROJECT':'opc','IN_IDEA':'kitchen','IN_NOTES':'$(echo never-run)\nGITHUB_TOKEN=not-a-command'})
        self.assertIn('$(echo',x['notes'])


class Models(unittest.TestCase):
    def test_prose_url_does_not_count(self):
        self.assertEqual(llm.observed_urls('openai',{'output':[{'type':'message','content':[{'type':'output_text','text':'https://example.org'}]}]}),set())
    def test_openai_structured_sources(self):
        raw={'output':[{'type':'web_search_call','action':{'sources':[{'url':'https://example.org/fact#one'}]}}]}
        self.assertEqual(llm.observed_urls('openai',raw),{'https://example.org/fact'})
    def test_anthropic_structured_sources(self):
        raw={'content':[{'type':'web_search_tool_result','content':[{'type':'web_search_result','url':'https://example.org/fact'}]}]}
        self.assertEqual(llm.observed_urls('claude',raw),{'https://example.org/fact'})
    def test_search_error_not_evidence(self):
        raw={'content':[{'type':'web_search_tool_result','content':{'type':'web_search_tool_result_error','error_code':'max_uses_exceeded'}}]}
        self.assertEqual(llm.observed_urls('claude',raw),set())
    def test_openai_does_not_need_claude_key(self):
        fake=MagicMock()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-only'},clear=True),patch.dict(sys.modules,{'openai':fake}):
            m=llm.Model('openai',Path('not-written.json'))
            self.assertEqual(m.engine,'openai');fake.OpenAI.assert_called_once()
    def test_legacy_key_not_used_for_opc(self):
        obj=llm.Model.__new__(llm.Model);obj.engine='claude'
        fake=MagicMock()
        with patch.dict(os.environ,{'CLAUDE_KEY_4_CONTENT':'test-only'},clear=True),patch.dict(sys.modules,{'anthropic':fake}):
            with self.assertRaises(c.GateError):obj._client()
            fake.Anthropic.assert_not_called()
    def test_openai_cache_not_double_counted(self):
        e=llm.usage_entry('openai','gpt-5',{'usage':{'input_tokens':1000,'output_tokens':100,'input_tokens_details':{'cached_tokens':300}},'output':[{'type':'web_search_call'}]})
        self.assertEqual(e['input_tokens'],700);self.assertEqual(e['cache_read_tokens'],300);self.assertEqual(e['web_searches'],1)
    def test_unknown_model_cost_not_invented(self):
        e=llm.usage_entry('openai','future-unknown',{'usage':{'input_tokens':1000}})
        self.assertIsNone(e['estimated_usd'])
    def test_json_object_ignores_fences(self):
        self.assertEqual(llm.json_object('prefix ```json\n{"title":"sample"}\n```'),{'title':'sample'})
    def test_no_paid_retries(self):
        m=llm.Model.__new__(llm.Model);m.calls=1;m.max_calls=1
        with self.assertRaises(c.GateError):m.ask('anything',{})


class Media(unittest.TestCase):
    def test_exif_removed(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'in.jpg';b=Path(d)/'out.jpg'
            im=Image.new('RGB',(1600,1000));exif=Image.Exif();exif[270]='private address'
            im.save(a,exif=exif);media.sanitize_photo(a,b)
            got=Image.open(b);self.assertFalse(got.getexif());self.assertLessEqual(got.width,1440)
    def test_tiny_photo_rejected(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a.png';Image.new('RGB',(20,20)).save(a)
            with self.assertRaises(c.GateError):media.sanitize_photo(a,Path(d)/'b.jpg')
    def test_private_network_rejected(self):
        for ip in ('127.0.0.1','10.0.0.1','169.254.169.254','::1'):
            with patch('socket.getaddrinfo',return_value=[(0,0,0,'',(ip,443))]):self.assertFalse(net.public_https('https://example.org/image'))
    def test_invalid_port_rejected(self):self.assertFalse(net.public_https('https://example.org:80/image'))
    def test_certificate_failure_uses_next_real_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'resources').mkdir()
            src=[{'url':'https://first.example/proof','name':'First'},{'url':'https://second.example/proof','name':'Second'}]
            with patch.object(net,'screenshot_source',side_effect=[RuntimeError('certificate'),{'heading':'Genuine headline','excerpt':'Actual source body'}]):
                found,attempts=net.screenshot_candidates(src,{x['url'] for x in src},root,'S1')
            self.assertEqual(found['name'],'Second');self.assertEqual(attempts[0]['status'],'failed')
    def test_unobserved_url_is_never_screenshot(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'resources').mkdir()
            with patch.object(net,'screenshot_source') as shot:
                with self.assertRaises(c.GateError):net.screenshot_candidates([{'url':'https://fabricated.example'}],set(),root,'S1')
                shot.assert_not_called()
    def test_replicate_schema_blocks_hidden_fallback(self):
        m=media.ReplicateImages.__new__(media.ReplicateImages)
        m.schema={'properties':{'prompt':{},'aspect_ratio':{},'allow_fallback_model':{}},'required':['prompt']}
        x=m._input('A real-looking stone sample',None)
        self.assertIs(x['allow_fallback_model'],False);self.assertEqual(x['aspect_ratio'],'16:9')
    def test_replicate_extra_required_input_blocks(self):
        m=media.ReplicateImages.__new__(media.ReplicateImages);m.schema={'properties':{'prompt':{}},'required':['prompt','new_required_field']}
        with self.assertRaises(c.GateError):m._input('sample',None)
    def test_replicate_request_path_cannot_exfiltrate_key(self):
        m=media.ReplicateImages.__new__(media.ReplicateImages)
        with self.assertRaises(c.GateError):m._request('GET','https://evil.example')
    def test_four_image_cap(self):
        m=media.ReplicateImages.__new__(media.ReplicateImages);m.max_images=4;m.records=[{}]*4
        with self.assertRaises(c.GateError):m.generate('A1','sample')


class Filing(unittest.TestCase):
    def test_quoted_tab(self):self.assertEqual(quote_tab("Owner's ideas"),"'Owner''s ideas'")
    def test_duplicate_rebuild_must_match(self):
        store=Store.__new__(Store)
        with patch.object(store,'read_rows',return_value=[list(c.HEADERS)]):
            with self.assertRaises(c.GateError):store.duplicates('Kitchen',['one','two','three'],'',428)
    def test_persistent_run_guard(self):
        store=Store.__new__(Store)
        with patch.object(store,'list_children',return_value=[{'appProperties':{'opcPrintRun':'same-key'},'name':'v500_topic'}]):
            with self.assertRaises(c.GateError):store.start_run('Topic','same-key')
    def test_versions_use_max_not_folder_count(self):
        store=Store.__new__(Store)
        with patch.object(store,'list_children',return_value=[{'name':'v4_old'},{'name':'v10_new'}]),patch.object(store,'folder',return_value={}) as folder:
            store.start_run('Kitchen','unused');self.assertEqual(folder.call_args.args[0],'v11_kitchen_print')
    def test_unknown_image_cost_stays_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'resources').mkdir();(root/'resources/image-usage.json').write_text('[{"status":"succeeded"}]')
            result=opc_usage.summary(root)
            self.assertIsNone(result['image_estimated_usd']);self.assertFalse(result['total_cost_complete'])

if __name__=='__main__':unittest.main()
