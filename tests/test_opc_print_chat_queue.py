"""Synthetic tests for the temporary pre-merge ChatGPT OPC queue. No network or paid APIs."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

HERE=Path(__file__).resolve().parents[1]/"scripts/factcheck_print"
sys.path.insert(0,str(HERE))

from opc_contract import GateError
from opc_chat_queue import link_request,pending


class QueueStore:
    def __init__(self,items):
        self.items=items
    def list_children(self,parent):
        return list(self.items)


class ChatQueue(unittest.TestCase):
    def test_one_ready_chat_item(self):
        item={"id":"x","name":"READY — OPC CHAT — kitchen","appProperties":{}}
        got=pending(QueueStore([item]),"chat")
        self.assertEqual(got["id"],"x")

    def test_built_item_is_ignored(self):
        done={"id":"old","name":"READY — OPC CHAT — old","appProperties":{"opcChatState":"BUILT_NOT_APPROVED"}}
        ready={"id":"new","name":"READY — OPC CHAT — new","appProperties":{}}
        self.assertEqual(pending(QueueStore([done,ready]),"chat")["id"],"new")

    def test_ambiguous_ready_queue_blocks(self):
        items=[
            {"id":"a","name":"READY — OPC CHAT — one","appProperties":{}},
            {"id":"b","name":"READY — OPC CHAT — two","appProperties":{}},
        ]
        with self.assertRaisesRegex(GateError,"exactly one"):
            pending(QueueStore(items),"chat")

    def test_valid_link_request(self):
        url,notes=link_request({"version":1,"project":"opc","source_url":"https://youtu.be/abcdefghijk","notes":"focus on one claim"})
        self.assertEqual(url,"https://youtu.be/abcdefghijk")
        self.assertEqual(notes,"focus on one claim")

    def test_bad_link_request_blocks(self):
        with self.assertRaises(GateError):
            link_request({"version":1,"project":"opc","source_url":"https://example.com/video"})

    def test_wrong_project_blocks(self):
        with self.assertRaises(GateError):
            link_request({"version":1,"project":"brazil","source_url":"https://youtu.be/abcdefghijk"})


if __name__=="__main__":
    unittest.main()
