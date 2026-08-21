"""Offline tests for the optional Anthropic spoke."""
import os
import shutil
import tempfile
import unittest

import fakes
from fakes import FakeTransport

from keyring import Keyring
from ledger import Ledger
from spokes_anthropic import AnthropicSpoke
from spokes_base import AuthError, ChatMessage, NotSupported


class AnthropicSpokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.transport = FakeTransport()
        self.ledger = Ledger(path=os.path.join(self.tmp, "ledger.jsonl"),
                             override_path=os.path.join(self.tmp, "prices.json"))

    def make_spoke(self, **kwargs):
        kwargs.setdefault("api_key", "sk-ant-test-not-real")
        return AnthropicSpoke(transport=self.transport, ledger=self.ledger,
                              **kwargs)

    def test_chat_round_trip(self):
        self.transport.enqueue_fixture("anthropic_chat.json")
        result = self.make_spoke().chat(
            [ChatMessage("system", "you are an art historian"),
             ChatMessage("user", "define chiaroscuro")],
            model="claude-sonnet-4-20250514", max_tokens=200)

        self.assertEqual(result.text,
                         "Chiaroscuro: dramatic light-dark contrast.")
        self.assertEqual(result.finish_reason, "end_turn")
        self.assertEqual(result.usage.input_tokens, 18)
        self.assertEqual(result.usage.output_tokens, 11)

        call = self.transport.calls[0]
        self.assertEqual(call.url, "https://api.anthropic.com/v1/messages")
        self.assertEqual(call.headers["x-api-key"], "sk-ant-test-not-real")
        self.assertEqual(call.headers["anthropic-version"], "2023-06-01")
        body = call.body_json()
        self.assertEqual(body["system"], "you are an art historian")
        self.assertEqual(body["max_tokens"], 200)
        self.assertEqual(body["messages"][0]["role"], "user")

    def test_chat_ledger_pricing(self):
        self.transport.enqueue_fixture("anthropic_chat.json")
        self.make_spoke().chat([ChatMessage("user", "hi")])
        summary = self.ledger.summary()
        expected = 18 / 1e6 * 3.0 + 11 / 1e6 * 15.0   # claude-sonnet-4 rates
        self.assertAlmostEqual(summary["anthropic"]["est_usd"], expected)

    def test_chat_stream(self):
        self.transport.enqueue_fixture("anthropic_chat_stream.sse")
        chunks = []
        result = self.make_spoke().chat([ChatMessage("user", "salut")],
                                        stream_cb=chunks.append)
        self.assertEqual(chunks, ["Bonjour", " atelier"])
        self.assertEqual(result.text, "Bonjour atelier")
        self.assertEqual(result.finish_reason, "end_turn")
        self.assertEqual(result.usage.input_tokens, 10)
        self.assertEqual(result.usage.output_tokens, 5)
        self.assertTrue(self.transport.calls[0].body_json()["stream"])

    def test_max_tokens_defaults_when_omitted(self):
        self.transport.enqueue_fixture("anthropic_chat.json")
        self.make_spoke().chat([ChatMessage("user", "hi")])
        self.assertEqual(self.transport.calls[0].body_json()["max_tokens"], 1024)

    def test_image_generation_not_supported(self):
        with self.assertRaises(NotSupported):
            self.make_spoke().generate_image("nope")

    def test_missing_key_raises(self):
        empty_keyring = Keyring(path=os.path.join(self.tmp, "kr.json"), env={})
        with self.assertRaises(AuthError):
            AnthropicSpoke(keyring=empty_keyring, transport=self.transport,
                           record_usage=False)


if __name__ == "__main__":
    unittest.main()
