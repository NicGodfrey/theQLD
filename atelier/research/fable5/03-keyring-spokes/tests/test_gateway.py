"""Tests for the Gateway hub: routing, shared ledger, config errors."""
import os
import shutil
import tempfile
import unittest

import fakes
from fakes import FakeTransport

from gateway import Gateway
from keyring import Keyring
from ledger import Ledger
from spokes_base import ChatMessage, SpokeError


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.transport = FakeTransport()
        self.keyring = Keyring(
            path=os.path.join(self.tmp, "keyring.json"),
            env={"OPENAI_API_KEY": "sk-test", "GEMINI_API_KEY": "AIza-test"})
        self.ledger = Ledger(path=os.path.join(self.tmp, "ledger.jsonl"),
                             override_path=os.path.join(self.tmp, "prices.json"))
        self.gateway = Gateway(keyring=self.keyring, ledger=self.ledger,
                               transport=self.transport)

    def test_routes_by_provider_and_shares_one_ledger(self):
        self.transport.enqueue_fixture("openai_chat.json")
        self.transport.enqueue_fixture("gemini_chat.json")
        openai_result = self.gateway.chat("openai", [ChatMessage("user", "hi")])
        gemini_result = self.gateway.chat("gemini", [ChatMessage("user", "hi")])
        self.assertEqual(openai_result.provider, "openai")
        self.assertEqual(gemini_result.provider, "gemini")
        summary = self.gateway.usage_summary()
        self.assertEqual(sorted(summary), ["gemini", "openai"])

    def test_spokes_are_cached(self):
        self.assertIs(self.gateway.spoke("openai"), self.gateway.spoke("openai"))

    def test_unknown_provider_raises(self):
        with self.assertRaises(SpokeError):
            self.gateway.spoke("chatgpt_web_session")   # never a thing

    def test_compat_without_base_url_is_a_config_error(self):
        with self.assertRaises(SpokeError) as ctx:
            self.gateway.spoke("openai_compatible")
        self.assertIn("base_url", str(ctx.exception))

    def test_capabilities_pass_through(self):
        self.assertIn("image", self.gateway.capabilities("openai"))
        self.assertIn("chat_stream", self.gateway.capabilities("gemini"))


if __name__ == "__main__":
    unittest.main()
