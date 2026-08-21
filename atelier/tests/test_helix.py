#!/usr/bin/env python3
"""Helix unit tests — no live provider keys required."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.catalog import public
from atelier.helix.conductor import Conductor, extract_json, fallback_plan
from atelier.helix.keyring import Keyring
from atelier.helix.loom import demo_svg, write_bytes
from atelier.helix.store import Memory
from atelier.helix.usage import BudgetExceeded, estimate_usd, record


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mem = Memory(Path(self.tmp.name) / "t.sqlite")

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def test_project_thread_node(self):
        project = self.mem.create_project("Cloth", {"voice": "quiet"})
        thread = self.mem.create_thread(project["id"], topic="mark", mode="thinking")
        self.mem.add_message(thread["id"], "user", "draw a mark")
        node = self.mem.add_node(project_id=project["id"], type="note", text="hello", x=10, y=20)
        self.assertEqual(project["brand_kit"]["voice"], "quiet")
        self.assertEqual(len(self.mem.list_messages(thread["id"])), 1)
        moved = self.mem.update_node(node["id"], x=33)
        self.assertEqual(moved["x"], 33)


class KeyringTests(unittest.TestCase):
    def test_redacts_and_env(self):
        tmp = tempfile.TemporaryDirectory()
        ring = Keyring(Path(tmp.name) / "keyring.json")
        ring.put("openai", key="sk-test-abcdefghijklmnopqrstuvwxyz")
        status = ring.public_status()
        self.assertTrue(status["openai"]["configured"])
        dumped = json.dumps(status)
        self.assertNotIn("sk-test-abcdefghijklmnopqrstuvwxyz", dumped)
        tmp.cleanup()


class ConductorTests(unittest.TestCase):
    def test_extract_json_fences(self):
        plan = extract_json("```json\n{\"intent\":\"logo\",\"weave\":[]}\n```")
        self.assertEqual(plan["intent"], "logo")

    def test_fallback_and_demo_run(self):
        tmp = tempfile.TemporaryDirectory()
        mem = Memory(Path(tmp.name) / "t.sqlite")
        ring = Keyring(Path(tmp.name) / "keys.json")
        project = mem.create_project("Demo")
        thread = mem.create_thread(project["id"])
        cond = Conductor(mem, ring, Path(tmp.name) / "arts")
        result = cond.run(
            project_id=project["id"],
            thread_id=thread["id"],
            prompt="Queensland legal directory poster, calm navy, 12 categories",
            mode="thinking",
            provider="demo",
        )
        self.assertTrue(result["artifacts"])
        self.assertTrue(result["nodes"])
        self.assertIn("Helix", result["message"])
        self.assertEqual(fallback_plan("x", "fast", "demo", "demo-conductor")["route"]["provider"], "demo")
        mem.close()
        tmp.cleanup()


class LoomUsageCatalogTests(unittest.TestCase):
    def test_demo_svg_and_cost(self):
        svg = demo_svg("legal directory")
        self.assertIn("<svg", svg)
        tmp = tempfile.TemporaryDirectory()
        path = write_bytes(Path(tmp.name), "abc", svg.encode(), "image/svg+xml")
        self.assertTrue(path.exists())
        self.assertGreater(estimate_usd("openai", "dall-e-3", "images", 1), 0)
        self.assertEqual(estimate_usd("ollama", "llama3.2", "tokens_in", 100), 0)
        tmp.cleanup()

    def test_record_usage(self):
        tmp = tempfile.TemporaryDirectory()
        mem = Memory(Path(tmp.name) / "t.sqlite")
        record(mem, provider="demo", model="demo-svg", unit_kind="images", units=1)
        totals = mem.usage_totals()
        self.assertEqual(totals[0]["provider"], "demo")
        self.assertEqual(estimate_usd("openai", "gpt-5.6-luna", "tokens_in", 1_000_000), 0.2)
        mem.add_usage(provider="openai", model="dall-e-3", unit_kind="images", units=1, estimated_usd=3.0, thread_id="t1")
        with self.assertRaises(BudgetExceeded):
            record(mem, provider="openai", model="dall-e-3", unit_kind="images", units=1, thread_id="t1")
        mem.close()
        tmp.cleanup()

    def test_catalog_is_100(self):
        cat = public()
        self.assertEqual(cat["count"], 100)
        repos = [p["repo"] for p in cat["projects"]]
        self.assertEqual(len(repos), len(set(repos)))
        self.assertIn("BerriAI/litellm", cat["mvp_wire"])


if __name__ == "__main__":
    unittest.main()
