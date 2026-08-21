"""Offline tests for spokes_gemini. No sockets, no real keys."""
import os
import shutil
import tempfile
import unittest

import fakes
from fakes import FakeTransport

from keyring import Keyring
from ledger import Ledger
from spokes_base import (AuthError, ChatMessage, KeyLeakError, NotSupported,
                         Part, ProviderError)
from spokes_gemini import GeminiSpoke, _aspect_from_size

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class GeminiSpokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.transport = FakeTransport()
        self.ledger = Ledger(path=os.path.join(self.tmp, "ledger.jsonl"),
                             override_path=os.path.join(self.tmp, "prices.json"))

    def make_spoke(self, **kwargs):
        kwargs.setdefault("api_key", "AIza-test-not-real")
        return GeminiSpoke(transport=self.transport, ledger=self.ledger,
                           **kwargs)

    # -- chat -------------------------------------------------------------

    def test_chat_round_trip(self):
        self.transport.enqueue_fixture("gemini_chat.json")
        result = self.make_spoke().chat(
            [ChatMessage("system", "you are a painter"),
             ChatMessage("user", "describe the light"),
             ChatMessage("assistant", "warm."),
             ChatMessage("user", "more detail")],
            model="gemini-2.5-flash", temperature=0.7, max_tokens=256)

        self.assertEqual(result.text,
                         "Golden-hour glaze over wet cobblestones.")
        self.assertEqual(result.provider, "gemini")
        self.assertEqual(result.finish_reason, "STOP")
        self.assertEqual(result.usage.input_tokens, 21)
        self.assertEqual(result.usage.output_tokens, 9)

        call = self.transport.calls[0]
        self.assertEqual(call.url,
                         "https://generativelanguage.googleapis.com/v1beta/"
                         "models/gemini-2.5-flash:generateContent")
        self.assertEqual(call.headers["x-goog-api-key"], "AIza-test-not-real")
        self.assertNotIn("Authorization", call.headers)
        body = call.body_json()
        self.assertEqual(body["systemInstruction"],
                         {"parts": [{"text": "you are a painter"}]})
        roles = [c["role"] for c in body["contents"]]
        self.assertEqual(roles, ["user", "model", "user"])
        self.assertEqual(body["generationConfig"],
                         {"temperature": 0.7, "maxOutputTokens": 256})

    def test_chat_ledger_pricing(self):
        self.transport.enqueue_fixture("gemini_chat.json")
        self.make_spoke().chat([ChatMessage("user", "hi")])
        summary = self.ledger.summary()
        expected = 21 / 1e6 * 0.30 + 9 / 1e6 * 2.50   # gemini-2.5-flash rates
        self.assertAlmostEqual(summary["gemini"]["est_usd"], expected)
        self.assertEqual(summary["gemini"]["unpriced_calls"], 0)

    def test_chat_stream(self):
        self.transport.enqueue_fixture("gemini_chat_stream.sse")
        chunks = []
        result = self.make_spoke().chat([ChatMessage("user", "hi")],
                                        stream_cb=chunks.append)
        self.assertEqual(chunks, ["Golden-hour ", "glaze."])
        self.assertEqual(result.text, "Golden-hour glaze.")
        self.assertEqual(result.finish_reason, "STOP")
        self.assertEqual(result.usage.input_tokens, 21)
        self.assertEqual(result.usage.output_tokens, 8)
        self.assertTrue(self.transport.calls[0].url.endswith(
            ":streamGenerateContent?alt=sse"))

    def test_image_input_part_becomes_inline_data(self):
        self.transport.enqueue_fixture("gemini_chat.json")
        message = ChatMessage("user", [Part("text", text="what is this?"),
                                       Part("image", data=b"12345",
                                            mime="image/jpeg")])
        self.make_spoke().chat([message])
        parts = self.transport.calls[0].body_json()["contents"][0]["parts"]
        self.assertEqual(parts[0], {"text": "what is this?"})
        self.assertEqual(parts[1]["inlineData"]["mimeType"], "image/jpeg")

    def test_blocked_prompt_raises(self):
        self.transport.enqueue_json(
            {"promptFeedback": {"blockReason": "SAFETY"}, "candidates": []})
        with self.assertRaises(ProviderError) as ctx:
            self.make_spoke().chat([ChatMessage("user", "hi")])
        self.assertIn("SAFETY", str(ctx.exception))

    # -- images -----------------------------------------------------------

    def test_native_image_generation(self):
        self.transport.enqueue_fixture("gemini_image.json")
        result = self.make_spoke().generate_image("a red dot")
        self.assertEqual(len(result.images), 1)
        self.assertTrue(result.images[0].startswith(PNG_MAGIC))
        self.assertEqual(result.mime, "image/png")
        self.assertEqual(result.text, "Here is your image.")
        body = self.transport.calls[0].body_json()
        self.assertEqual(body["generationConfig"]["responseModalities"],
                         ["TEXT", "IMAGE"])
        self.assertEqual(body["generationConfig"]["imageConfig"],
                         {"aspectRatio": "1:1"})
        summary = self.ledger.summary()
        self.assertEqual(summary["gemini"]["images"], 1)
        self.assertAlmostEqual(summary["gemini"]["est_usd"], 0.039)

    def test_native_image_n2_loops_calls(self):
        self.transport.enqueue_fixture("gemini_image.json")
        self.transport.enqueue_fixture("gemini_image.json")
        result = self.make_spoke().generate_image("a red dot", n=2)
        self.assertEqual(len(result.images), 2)
        self.assertEqual(len(self.transport.calls), 2)
        self.assertEqual(self.ledger.summary()["gemini"]["images"], 2)

    def test_imagen_predict(self):
        self.transport.enqueue_fixture("imagen_predict.json")
        result = self.make_spoke().generate_image(
            "a red dot", model="imagen-4.0-generate-001", n=2,
            size="1024x1024")
        self.assertEqual(len(result.images), 2)
        call = self.transport.calls[0]
        self.assertTrue(call.url.endswith(
            "models/imagen-4.0-generate-001:predict"))
        body = call.body_json()
        self.assertEqual(body["instances"], [{"prompt": "a red dot"}])
        self.assertEqual(body["parameters"]["sampleCount"], 2)
        self.assertEqual(body["parameters"]["aspectRatio"], "1:1")
        summary = self.ledger.summary()
        self.assertAlmostEqual(summary["gemini"]["est_usd"], 0.08)  # 2 x $0.04

    def test_non_image_model_without_image_data_raises(self):
        self.transport.enqueue_fixture("gemini_chat.json")   # text-only reply
        with self.assertRaises(ProviderError):
            self.make_spoke().generate_image("a red dot")

    # -- guard rails ----------------------------------------------------------

    def test_missing_key_raises(self):
        empty_keyring = Keyring(path=os.path.join(self.tmp, "kr.json"), env={})
        with self.assertRaises(AuthError):
            GeminiSpoke(keyring=empty_keyring, transport=self.transport,
                        record_usage=False)

    def test_video_is_contract_stub(self):
        with self.assertRaises(NotSupported):
            self.make_spoke().generate_video("pan across the studio")

    def test_key_guard_is_active(self):
        spoke = self.make_spoke()
        with self.assertRaises(KeyLeakError):
            spoke._post("http://generativelanguage.googleapis.com/v1beta/x",
                        {})   # https required off loopback

    def test_aspect_mapping(self):
        self.assertEqual(_aspect_from_size("1024x1024"), "1:1")
        self.assertEqual(_aspect_from_size("1920x1080"), "16:9")
        self.assertEqual(_aspect_from_size("768x1024"), "3:4")
        self.assertIsNone(_aspect_from_size("banana"))


if __name__ == "__main__":
    unittest.main()
