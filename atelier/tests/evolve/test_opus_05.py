#!/usr/bin/env python3
"""Opus-05 — Round 10 (brand kit) verification.

Demo SVG still tints fills. Paid spokes have no style token, so they must
prefix the image prompt with StyleLock brand + hex palette.
"""

from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.loom import demo_svg, style_lock  # noqa: E402
from atelier.helix.spokes.gemini_spoke import GeminiSpoke  # noqa: E402
from atelier.helix.spokes.openai_spoke import OpenAISpoke  # noqa: E402


class StyleLockText(unittest.TestCase):
    def test_prefix_carries_brand_and_palette(self):
        locked = style_lock("poster", palette=["#112233", "#f5c211"], title="QLD")
        self.assertTrue(locked.startswith("[StyleLock "))
        self.assertIn("brand=QLD", locked)
        self.assertIn("palette=#112233,#f5c211", locked)
        self.assertIn("ground=#112233 ink=#f5c211", locked)
        self.assertTrue(locked.endswith("\nposter"))

    def test_empty_kit_leaves_the_prompt_alone(self):
        self.assertEqual(style_lock("plain"), "plain")
        self.assertEqual(style_lock("plain", palette=[], title=""), "plain")
        self.assertEqual(style_lock("plain", palette=[None, ""], title="  "), "plain")


class DemoTint(unittest.TestCase):
    def test_demo_svg_still_paints_the_hex(self):
        svg = demo_svg("logo", title="Helix", palette=["#112233", "#f5c211"])
        self.assertIn("#112233", svg)
        self.assertIn("#f5c211", svg)
        self.assertNotIn("[StyleLock", svg)


class PaidSpokesLock(unittest.TestCase):
    def test_openai_image_prompt_is_style_locked(self):
        captured = {}

        def fake_post(path, body):
            captured["path"] = path
            captured["body"] = body
            return {"data": [{"b64_json": base64.b64encode(b"PNG").decode()}]}

        spoke = OpenAISpoke(mock.Mock())
        spoke._post = fake_post
        result = spoke.image(
            "navy mark",
            model="gpt-image-1",
            palette=["#112233", "#f5c211"],
            title="QLD",
        )
        self.assertIn("#112233", captured["body"]["prompt"])
        self.assertIn("QLD", captured["body"]["prompt"])
        self.assertIn("[StyleLock", result.prompt)
        self.assertEqual(result.mime, "image/png")

    def test_gemini_image_prompt_is_style_locked(self):
        captured = {}

        def fake_post(path, body):
            captured["path"] = path
            captured["body"] = body
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "inlineData": {
                                        "mimeType": "image/png",
                                        "data": base64.b64encode(b"PNG").decode(),
                                    }
                                }
                            ]
                        }
                    }
                ]
            }

        spoke = GeminiSpoke(mock.Mock())
        spoke._post = fake_post
        result = spoke.image(
            "navy mark",
            model="gemini-2.5-flash-image",
            palette=["#0b1d36"],
            title="Helix",
        )
        text = captured["body"]["contents"][0]["parts"][0]["text"]
        self.assertIn("[StyleLock", text)
        self.assertIn("#0b1d36", text)
        self.assertIn("Helix", result.prompt)


if __name__ == "__main__":
    unittest.main()
