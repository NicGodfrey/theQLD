#!/usr/bin/env python3
"""Fable-01 — Round 1 (fail-closed) verification.

Read-only over the live tree. Extends `Round01FailClosed` in three directions
the shared suite does not cover:

  1. The gemini lane fails closed too, not just openai.
  2. A planner that tries to downgrade `route.provider` to "demo" is repinned
     to the user-selected paid lane, so image failure still raises instead of
     minting demo SVG.
  3. The demo lane still works end-to-end and is allowed to mint SVG.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.conductor import Conductor, ConductorError  # noqa: E402
from atelier.helix.keyring import Keyring  # noqa: E402
from atelier.helix.spokes.base import ChatResult, DemoSpoke, SpokeError  # noqa: E402
from atelier.helix.store import Memory  # noqa: E402


class FailImageSpoke:
    """Paid lane whose planner works but whose image endpoint always fails."""

    def chat(self, messages, model="", **kwargs):
        return DemoSpoke().chat(messages, model=model or "demo-conductor", **kwargs)

    def image(self, prompt, model="", **kwargs):
        raise SpokeError("simulated paid image failure")


class DowngradingPlannerSpoke(FailImageSpoke):
    """Planner that maliciously routes the run to the demo lane."""

    def chat(self, messages, model="", **kwargs):
        plan = (
            '{"mode": "fast", "intent": "downgrade attempt",'
            ' "score": {"audience": "", "format": "", "constraints": []},'
            ' "route": {"provider": "demo", "model": "demo-svg", "capability": "image"},'
            ' "weave": [{"kind": "image", "prompt": "navy logo", "count": 1}],'
            ' "notes": ""}'
        )
        return ChatResult(text=plan, provider="openai", model=model or "gpt-4o-mini")


class Fable01FailClosed(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.mem = Memory(base / "t.sqlite")
        self.ring = Keyring(base / "keys.json")
        self.arts = base / "arts"
        self.arts.mkdir(exist_ok=True)
        self.project = self.mem.create_project("Fable01")
        self.thread = self.mem.create_thread(self.project["id"])
        self.cond = Conductor(self.mem, self.ring, self.arts)

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def _run(self, provider):
        return self.cond.run(
            project_id=self.project["id"],
            thread_id=self.thread["id"],
            prompt="navy logo",
            provider=provider,
        )

    def _artifact_providers(self):
        return [r[0] for r in self.mem.conn.execute("SELECT provider FROM artifacts").fetchall()]

    def test_gemini_image_failure_never_mints_demo(self):
        def factory(provider, keyring):
            return DemoSpoke() if provider == "demo" else FailImageSpoke()

        with mock.patch("atelier.helix.conductor.build_spoke", side_effect=factory):
            with self.assertRaises(ConductorError):
                self._run("gemini")
        self.assertEqual(self._artifact_providers(), [])

    def test_planner_cannot_downgrade_route_to_demo(self):
        built = []

        def factory(provider, keyring):
            built.append(provider)
            return DemoSpoke() if provider == "demo" else DowngradingPlannerSpoke()

        with mock.patch("atelier.helix.conductor.build_spoke", side_effect=factory):
            with self.assertRaises(ConductorError):
                self._run("openai")
        # The image weave must have been routed back to the paid lane,
        # never to the demo spoke.
        self.assertNotIn("demo", built)
        self.assertEqual(self._artifact_providers(), [])

    def test_demo_lane_still_mints_svg(self):
        result = self._run("demo")
        self.assertTrue(result["ok"])
        self.assertEqual(result["errors"], [])
        self.assertGreaterEqual(len(result["artifacts"]), 1)
        self.assertEqual(set(self._artifact_providers()), {"demo"})


if __name__ == "__main__":
    unittest.main()
