"""Offline tests for spokes_openai (official OpenAI + Ollama + generic
OpenAI-compatible). No sockets, no real keys."""
import json
import os
import shutil
import tempfile
import unittest

import fakes
from fakes import FakeTransport

from keyring import Keyring
from ledger import Ledger
from spokes_base import (AuthError, ChatMessage, KeyLeakError, NotSupported,
                         Part, RateLimitError)
from spokes_openai import OpenAISpoke, compatible_spoke, ollama_spoke

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class OpenAISpokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.transport = FakeTransport()
        self.ledger = Ledger(path=os.path.join(self.tmp, "ledger.jsonl"),
                             override_path=os.path.join(self.tmp, "prices.json"))

    def make_spoke(self, **kwargs):
        kwargs.setdefault("api_key", "sk-test-not-real")
        return OpenAISpoke(transport=self.transport, ledger=self.ledger,
                           **kwargs)

    # -- chat -------------------------------------------------------------

    def test_chat_round_trip(self):
        self.transport.enqueue_fixture("openai_chat.json")
        spoke = self.make_spoke()
        result = spoke.chat(
            [ChatMessage("system", "you are terse"),
             ChatMessage("user", "palette for a rainy street?")],
            model="gpt-4o-mini", temperature=0.2, max_tokens=64)

        self.assertEqual(result.text, "A muted palette of ochre and slate.")
        self.assertEqual(result.provider, "openai")
        self.assertEqual(result.finish_reason, "stop")
        self.assertEqual(result.usage.input_tokens, 42)
        self.assertEqual(result.usage.output_tokens, 12)

        call = self.transport.calls[0]
        self.assertEqual(call.url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(call.headers["Authorization"], "Bearer sk-test-not-real")
        body = call.body_json()
        self.assertEqual(body["model"], "gpt-4o-mini")
        self.assertEqual(body["max_completion_tokens"], 64)
        self.assertEqual(body["messages"][0],
                         {"role": "system", "content": "you are terse"})

    def test_chat_writes_priced_ledger_row(self):
        self.transport.enqueue_fixture("openai_chat.json")
        result = self.make_spoke().chat([ChatMessage("user", "hi")])
        summary = self.ledger.summary()
        self.assertEqual(summary["openai"]["calls"], 1)
        self.assertEqual(summary["openai"]["input_tokens"], 42)
        expected = 42 / 1e6 * 0.15 + 12 / 1e6 * 0.60   # gpt-4o-mini rates
        self.assertAlmostEqual(summary["openai"]["est_usd"], expected)
        self.assertAlmostEqual(result.usage.est_usd, expected)
        self.assertEqual(summary["openai"]["unpriced_calls"], 0)

    def test_chat_stream(self):
        self.transport.enqueue_fixture("openai_chat_stream.sse")
        chunks = []
        result = self.make_spoke().chat([ChatMessage("user", "hi")],
                                        model="gpt-4o-mini",
                                        stream_cb=chunks.append)
        self.assertEqual(chunks, ["Hello", ", atelier."])
        self.assertEqual(result.text, "Hello, atelier.")
        self.assertEqual(result.finish_reason, "stop")
        self.assertEqual(result.usage.input_tokens, 9)
        self.assertEqual(result.usage.output_tokens, 4)
        body = self.transport.calls[0].body_json()
        self.assertTrue(body["stream"])
        self.assertEqual(body["stream_options"], {"include_usage": True})

    def test_multimodal_message_becomes_data_url(self):
        self.transport.enqueue_fixture("openai_chat.json")
        message = ChatMessage("user", [
            Part("text", text="describe this"),
            Part("image", data=b"\x89PNGfake", mime="image/png")])
        self.make_spoke().chat([message])
        content = self.transport.calls[0].body_json()["messages"][0]["content"]
        self.assertEqual(content[0], {"type": "text", "text": "describe this"})
        self.assertTrue(content[1]["image_url"]["url"]
                        .startswith("data:image/png;base64,"))

    # -- images -----------------------------------------------------------

    def test_generate_image(self):
        self.transport.enqueue_fixture("openai_image.json")
        result = self.make_spoke().generate_image(
            "an atelier at dusk", model="gpt-image-1", quality="medium")
        self.assertEqual(len(result.images), 1)
        self.assertTrue(result.images[0].startswith(PNG_MAGIC))
        self.assertEqual(result.usage.images, 1)
        summary = self.ledger.summary()
        self.assertEqual(summary["openai"]["images"], 1)
        self.assertAlmostEqual(summary["openai"]["est_usd"], 0.042)
        body = self.transport.calls[0].body_json()
        self.assertNotIn("response_format", body)   # rejected by gpt-image-1

    def test_dalle_requests_b64(self):
        self.transport.enqueue_fixture("openai_image.json")
        self.make_spoke().generate_image("x", model="dall-e-3")
        body = self.transport.calls[0].body_json()
        self.assertEqual(body["response_format"], "b64_json")

    # -- errors / retries ---------------------------------------------------

    def test_401_maps_to_auth_error(self):
        self.transport.enqueue_json(
            {"error": {"message": "Incorrect API key", "code": "invalid_api_key"}},
            status=401)
        with self.assertRaises(AuthError) as ctx:
            self.make_spoke().chat([ChatMessage("user", "hi")])
        self.assertEqual(ctx.exception.status, 401)
        self.assertIn("Incorrect API key", str(ctx.exception))

    def test_retries_on_429_then_succeeds(self):
        self.transport.enqueue_json({"error": {"message": "slow down"}},
                                    status=429, headers={"Retry-After": "0"})
        self.transport.enqueue_fixture("openai_chat.json")
        result = self.make_spoke().chat([ChatMessage("user", "hi")])
        self.assertEqual(len(self.transport.calls), 2)
        self.assertTrue(result.text)

    def test_429_exhausted_raises_rate_limit(self):
        for _ in range(3):
            self.transport.enqueue_json({"error": {"message": "nope"}},
                                        status=429,
                                        headers={"Retry-After": "0"})
        with self.assertRaises(RateLimitError):
            self.make_spoke().chat([ChatMessage("user", "hi")])

    # -- key-leak guard -------------------------------------------------------

    def test_openai_base_url_is_pinned(self):
        with self.assertRaises(KeyLeakError):
            self.make_spoke(base_url="https://evil.example/v1")

    def test_compat_refuses_plain_http_off_loopback(self):
        spoke = compatible_spoke("http://models.example.com/v1",
                                 api_key="sk-x", transport=self.transport,
                                 record_usage=False)
        with self.assertRaises(KeyLeakError):
            spoke.chat([ChatMessage("user", "hi")])
        self.assertEqual(self.transport.calls, [])   # nothing left the process

    def test_missing_key_raises_helpful_auth_error(self):
        empty_keyring = Keyring(path=os.path.join(self.tmp, "kr.json"), env={})
        with self.assertRaises(AuthError):
            OpenAISpoke(keyring=empty_keyring, transport=self.transport,
                        record_usage=False)

    # -- ollama / compat family -----------------------------------------------

    def test_ollama_is_keyless_and_local(self):
        self.transport.enqueue_fixture("ollama_chat.json")
        empty_keyring = Keyring(path=os.path.join(self.tmp, "kr.json"), env={})
        spoke = ollama_spoke(transport=self.transport, keyring=empty_keyring,
                             ledger=self.ledger)
        result = spoke.chat([ChatMessage("user", "hi")],
                            model="llama3.1:8b", max_tokens=32)
        call = self.transport.calls[0]
        self.assertEqual(call.url, "http://127.0.0.1:11434/v1/chat/completions")
        self.assertNotIn("Authorization", call.headers)
        self.assertEqual(call.body_json()["max_tokens"], 32)   # legacy name
        self.assertEqual(result.provider, "ollama")
        summary = self.ledger.summary()
        self.assertEqual(summary["ollama"]["est_usd"], 0.0)        # free
        self.assertEqual(summary["ollama"]["unpriced_calls"], 0)   # priced $0

    def test_ollama_image_not_supported(self):
        empty_keyring = Keyring(path=os.path.join(self.tmp, "kr.json"), env={})
        spoke = ollama_spoke(transport=self.transport, keyring=empty_keyring,
                             record_usage=False)
        with self.assertRaises(NotSupported):
            spoke.generate_image("nope")

    def test_video_is_contract_stub(self):
        with self.assertRaises(NotSupported):
            self.make_spoke().generate_video("a slow pan over a canvas")

    def test_compat_base_url_from_keyring(self):
        keyring_path = os.path.join(self.tmp, "kr.json")
        kr = Keyring(path=keyring_path, env={})
        kr.set_key("openai_compatible", "sk-compat",
                   base_url="https://llm.internal.example/v1")
        self.transport.enqueue_fixture("openai_chat.json")
        spoke = compatible_spoke(keyring=kr, transport=self.transport,
                                 ledger=self.ledger)
        spoke.chat([ChatMessage("user", "hi")], model="my-model")
        call = self.transport.calls[0]
        self.assertEqual(call.url,
                         "https://llm.internal.example/v1/chat/completions")
        self.assertEqual(call.headers["Authorization"], "Bearer sk-compat")


if __name__ == "__main__":
    unittest.main()
