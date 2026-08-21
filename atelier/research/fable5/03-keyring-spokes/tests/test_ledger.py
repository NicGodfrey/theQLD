"""Tests for ledger.py: recording, aggregation, price estimation."""
import json
import os
import shutil
import stat
import tempfile
import unittest

import fakes  # noqa: F401  (path bootstrap)

from ledger import Ledger


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.path = os.path.join(self.tmp, "ledger.jsonl")
        self.no_overrides = os.path.join(self.tmp, "prices.json")  # absent

    def make(self, **kwargs):
        kwargs.setdefault("override_path", self.no_overrides)
        return Ledger(path=self.path, **kwargs)

    # -- chat pricing -----------------------------------------------------------

    def test_chat_estimate_gpt4o(self):
        led = self.make()
        rec = led.record(provider="openai", model="gpt-4o", kind="chat",
                         input_tokens=1000, output_tokens=500)
        self.assertTrue(rec.priced)
        self.assertAlmostEqual(rec.est_usd, 1000 / 1e6 * 2.5 + 500 / 1e6 * 10)

    def test_longest_prefix_wins(self):
        led = self.make()
        mini = led.record(provider="openai", model="gpt-4o-mini-2024-07-18",
                          kind="chat", input_tokens=1_000_000)
        self.assertAlmostEqual(mini.est_usd, 0.15)   # -mini rate, not gpt-4o

    def test_unknown_model_is_unpriced_not_free(self):
        led = self.make()
        rec = led.record(provider="openai_compatible", model="mystery-9b",
                         kind="chat", input_tokens=1000, output_tokens=1000)
        self.assertFalse(rec.priced)
        self.assertEqual(rec.est_usd, 0.0)
        summary = led.summary()
        self.assertEqual(summary["openai_compatible"]["unpriced_calls"], 1)

    # -- image pricing ------------------------------------------------------------

    def test_image_estimate_by_size_and_quality(self):
        led = self.make()
        rec = led.record(provider="openai", model="gpt-image-1", kind="image",
                         images=2, size="1024x1024", quality="high")
        self.assertAlmostEqual(rec.est_usd, 2 * 0.167)

    def test_image_estimate_fallback_star(self):
        led = self.make()
        rec = led.record(provider="openai", model="gpt-image-1", kind="image",
                         images=1, size="2048x2048")
        self.assertAlmostEqual(rec.est_usd, 0.042)

    def test_gemini_image_flat_price(self):
        led = self.make()
        rec = led.record(provider="gemini", model="gemini-2.5-flash-image",
                         kind="image", images=3)
        self.assertAlmostEqual(rec.est_usd, 3 * 0.039)

    # -- summary --------------------------------------------------------------------

    def test_summary_aggregates_per_provider(self):
        led = self.make()
        led.record(provider="openai", model="gpt-4o", kind="chat",
                   input_tokens=100, output_tokens=10)
        led.record(provider="openai", model="gpt-image-1", kind="image",
                   images=1, size="1024x1024", quality="low")
        led.record(provider="gemini", model="gemini-2.5-flash", kind="chat",
                   input_tokens=50, output_tokens=5)
        summary = led.summary()
        self.assertEqual(summary["openai"]["calls"], 2)
        self.assertEqual(summary["openai"]["images"], 1)
        self.assertEqual(summary["openai"]["input_tokens"], 100)
        self.assertEqual(summary["gemini"]["calls"], 1)

    def test_summary_since_filters(self):
        led = self.make()
        led.record(provider="openai", model="gpt-4o", kind="chat",
                   input_tokens=1)
        far_future = 32503680000.0   # year 3000
        self.assertEqual(led.summary(since=far_future), {})

    def test_ledger_file_is_0600_jsonl(self):
        led = self.make()
        led.record(provider="openai", model="gpt-4o", kind="chat",
                   input_tokens=1)
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o600)
        with open(self.path) as fh:
            row = json.loads(fh.readline())
        self.assertEqual(row["provider"], "openai")
        self.assertIn("ts", row)

    # -- overrides ----------------------------------------------------------------

    def test_price_overrides_argument(self):
        led = self.make(price_overrides={
            "chat": {"openai:custom-model": [1.0, 2.0]}})
        rec = led.record(provider="openai", model="custom-model", kind="chat",
                         input_tokens=1_000_000, output_tokens=1_000_000)
        self.assertAlmostEqual(rec.est_usd, 3.0)

    def test_price_override_file(self):
        override_path = os.path.join(self.tmp, "prices.json")
        with open(override_path, "w") as fh:
            json.dump({"image": {"openai:gpt-image-1": 9.99}}, fh)
        led = Ledger(path=self.path, override_path=override_path)
        rec = led.record(provider="openai", model="gpt-image-1", kind="image",
                         images=1)
        self.assertAlmostEqual(rec.est_usd, 9.99)


if __name__ == "__main__":
    unittest.main()
