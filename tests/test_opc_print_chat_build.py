"""Synthetic contract tests for the private chat OPC builder. No network or paid APIs."""
from pathlib import Path
import copy
import sys
import unittest

HERE=Path(__file__).resolve().parents[1]/"scripts/factcheck_print"
sys.path.insert(0,str(HERE))

from opc_contract import GateError
from opc_chat_build import audit_payload


def payload():
    return {
        "version":1,
        "project":"opc",
        "kind":"education",
        "title":"Why White Paint Changes",
        "caption":"Check light, undertone, nearby finishes, and samples in your own room before you choose.",
        "hashtags":"#PaintingTips #HomeRenovation",
        "keywords":["white","paint","undertone"],
        "audit":{
            "sources_checked":True,
            "copy_checked":True,
            "visual_jobs_checked":True,
            "no_repetition_checked":True,
            "notes":["synthetic fixture"],
        },
        "sources":[
            {"id":"S1","name":"Official source one","url":"https://example.org/source-one"},
            {"id":"S2","name":"Official source two","url":"https://example.com/source-two"},
        ],
        "slides":[
            {"id":1,"layout":"cover","headline":"White is not just white.","body":"Undertones and room conditions can change how a white feels.","source_ids":[],"visual_key":"A1"},
            {"id":2,"layout":"compare","headline":"Light pulls undertones forward.","body":"Natural and artificial light can make the same white read warmer or cooler.","source_ids":["S1"],"visual_key":"A2"},
            {"id":3,"layout":"point","headline":"Nearby finishes matter too.","body":"Floors, cabinets, fabrics, and nearby colors can change how the white reads.","source_ids":["S2"],"visual_key":"A3"},
            {"id":4,"layout":"point","headline":"Compare samples at home.","body":"Place samples beside your real finishes and check them through the day.","source_ids":["S1","S2"],"visual_key":"A4"},
            {"id":5,"layout":"close","headline":"Choose it in the room.","body":"Judge the sample with your light and surrounding materials before you commit.","source_ids":["S1","S2"],"visual_key":"A5"},
        ],
        "visuals":[
            {"key":"A1","subject":"Distinct room hero"},
            {"key":"A2","subject":"Controlled lighting comparison"},
            {"key":"A3","subject":"Materials context comparison"},
            {"key":"A4","subject":"Sampling process"},
            {"key":"A5","subject":"Distinct overhead close"},
        ],
    }


class ChatBuildContract(unittest.TestCase):
    def test_valid_payload_passes(self):
        audit_payload(payload())

    def test_visual_jobs_must_be_unique_and_sequential(self):
        p=payload()
        p["slides"][4]["visual_key"]="A4"
        with self.assertRaisesRegex(GateError,"sequential visual job"):
            audit_payload(p)

    def test_middle_slide_requires_source(self):
        p=payload()
        p["slides"][2]["source_ids"]=[]
        with self.assertRaisesRegex(GateError,"factual source required"):
            audit_payload(p)

    def test_unknown_source_is_blocked(self):
        p=payload()
        p["slides"][1]["source_ids"]=["S99"]
        with self.assertRaisesRegex(GateError,"unknown source id"):
            audit_payload(p)

    def test_brand_shade_code_is_blocked(self):
        p=payload()
        p["slides"][1]["body"]="Use SW 7005 to make this exact look."
        with self.assertRaisesRegex(GateError,"shade code"):
            audit_payload(p)

    def test_missing_audit_attestation_is_blocked(self):
        p=payload()
        p["audit"]["no_repetition_checked"]=False
        with self.assertRaisesRegex(GateError,"audit attestations"):
            audit_payload(p)

    def test_duplicate_keywords_are_blocked(self):
        p=payload()
        p["keywords"]=["white","white","paint"]
        with self.assertRaisesRegex(GateError,"three distinct"):
            audit_payload(p)


if __name__=="__main__":
    unittest.main()
