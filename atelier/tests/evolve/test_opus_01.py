#!/usr/bin/env python3
"""Opus-01 · Round 2 audit — quote-before-commit honesty probes.

Read-only verification of the live quote path. Nothing here edits or imports
fixtures from the release-gate modules; run it with:

    python3 -m unittest atelier.tests.evolve.test_opus_01
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix import usage
from atelier.helix.conductor import Conductor, _image_model
from atelier.helix.keyring import Keyring
from atelier.helix.quote import image_model_for, quote_run
from atelier.helix.spokes.base import DemoSpoke
from atelier.helix.store import Memory


def _workspace(tmp: Path):
    mem = Memory(tmp / "opus01.sqlite")
    ring = Keyring(tmp / "opus01-keys.json")
    arts = tmp / "arts"
    arts.mkdir(exist_ok=True)
    return mem, ring, arts


class UnknownIsNeverFree(unittest.TestCase):
    """Claim 1: an unpriced model must quote a real hold, not $0."""

    def test_unknown_openai_model_holds_money(self):
        q = quote_run(provider="openai", model="brand-new-model-2027", prompt="logo")
        self.assertFalse(q["priced"])
        self.assertGreater(q["conservative_usd"], 0)
        self.assertEqual(q["estimated_usd"], q["conservative_usd"])
        chat_rows = [b for b in q["breakdown"] if b["model"] == "brand-new-model-2027"]
        self.assertTrue(chat_rows and not any(b["priced"] for b in chat_rows))

    def test_unknown_provider_holds_money(self):
        q = quote_run(provider="anthropic", model="claude-x", prompt="logo", count=3)
        self.assertFalse(q["priced"])
        self.assertGreater(q["estimated_usd"], 0)

    def test_hold_scales_with_variant_count(self):
        one = quote_run(provider="openai", model="unknown-a", prompt="p", count=1)
        four = quote_run(provider="openai", model="unknown-a", prompt="p", count=4)
        self.assertGreater(four["estimated_usd"], one["estimated_usd"])

    def test_is_priced_never_guesses(self):
        self.assertTrue(usage.is_priced("openai", "gpt-4o-mini", "tokens_in"))
        self.assertFalse(usage.is_priced("openai", "gpt-4o-mini-2099", "tokens_in"))
        self.assertTrue(usage.is_priced("gemini", "gemini-2.5-flash-image", "images"))
        self.assertFalse(usage.is_priced("nobody", "nothing", "images"))

    def test_gemini_default_image_model_is_priced(self):
        q = quote_run(provider="gemini", model="gemini-2.0-flash", prompt="poster", count=4)
        self.assertEqual(q["image_model"], "gemini-2.5-flash-image")
        self.assertTrue(q["priced"])
        self.assertGreaterEqual(q["estimated_usd"], usage.estimate_usd("gemini", "gemini-2.5-flash-image", "images", 4))


class LocalLanesAreFree(unittest.TestCase):
    """Claim 2: demo and ollama quote exactly $0 and stay marked priced."""

    def test_demo_and_ollama_are_zero(self):
        for provider in ("demo", "ollama", "DEMO", "Ollama"):
            q = quote_run(provider=provider, model="", prompt="x" * 900, count=4)
            self.assertEqual(q["estimated_usd"], 0.0, provider)
            self.assertEqual(q["conservative_usd"], 0.0, provider)
            self.assertTrue(q["priced"], provider)
            self.assertFalse(q["would_exceed"], provider)

    def test_local_lanes_skip_the_budget_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            mem, _, _ = _workspace(Path(tmp))
            thread = mem.create_thread(mem.create_project("Free")["id"])
            mem.add_usage(
                provider="openai",
                model="gpt-image-1",
                unit_kind="images",
                units=1,
                estimated_usd=999.0,
                thread_id=thread["id"],
            )
            for provider in ("demo", "ollama"):
                q = quote_run(
                    provider=provider,
                    prompt="x",
                    memory=mem,
                    thread_id=thread["id"],
                )
                self.assertFalse(q["would_exceed"], provider)
                self.assertEqual(q["estimated_usd"], 0.0, provider)
            mem.close()

    @unittest.expectedFailure
    def test_gap_ollama_breakdown_row_contradicts_total(self):
        """Ollama images fall through to the $0.04 guess inside `breakdown`.

        The headline total is forced to $0, so the UI looks right, but any
        surface that renders `breakdown` shows a phantom image charge. Delete
        this expectedFailure once `("ollama", "*", "images"): 0.0` lands.
        """
        q = quote_run(provider="ollama", prompt="x", count=2)
        self.assertAlmostEqual(
            sum(row["usd"] for row in q["breakdown"]), q["estimated_usd"], places=6
        )


class QuoteRidesWithThePlan(unittest.TestCase):
    """Claim 3: the quote is emitted, attached to the plan, and persisted."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mem, self.ring, self.arts = _workspace(Path(self.tmp.name))
        self.project = self.mem.create_project("Quote")
        self.thread = self.mem.create_thread(self.project["id"])
        self.cond = Conductor(self.mem, self.ring, self.arts)

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def test_quote_event_plan_field_and_persisted_message(self):
        result = self.cond.run(
            project_id=self.project["id"],
            thread_id=self.thread["id"],
            prompt="calm poster",
            provider="demo",
        )
        quote_events = [e for e in result["events"] if e["kind"] == "quote"]
        self.assertEqual(len(quote_events), 1)
        self.assertIn("estimated_usd", quote_events[0]["quote"])

        plan_quote = result["plan"]["quote"]
        for key in ("estimated_usd", "priced", "provider", "image_model", "count"):
            self.assertIn(key, plan_quote)

        stored = [m for m in self.mem.list_messages(self.thread["id"]) if m["role"] == "assistant"]
        self.assertTrue(stored)
        self.assertEqual(stored[-1]["plan"]["quote"], plan_quote)
        self.assertIn("Quote:", stored[-1]["content"])

    def test_quoted_count_matches_planner_multi_item_weave(self):
        planner_plan = {
            "intent": "campaign",
            "mode": "fast",
            "route": {"provider": "demo", "model": "demo-conductor"},
            "weave": [{"kind": "image", "prompt": f"panel {i}", "count": 2} for i in range(4)],
        }

        class PlannerSpoke(DemoSpoke):
            def chat(self, messages, model="", **kwargs):
                reply = super().chat(messages, model=model or "demo-conductor", **kwargs)
                reply.text = json.dumps(planner_plan)
                return reply

        with mock.patch(
            "atelier.helix.conductor.build_spoke", side_effect=lambda provider, keyring: PlannerSpoke()
        ):
            result = self.cond.run(
                project_id=self.project["id"],
                thread_id=self.thread["id"],
                prompt="campaign board",
                provider="demo",
            )
        self.assertEqual(result["plan"]["quote"]["count"], 8)
        self.assertEqual(len(result["artifacts"]), 8)

    def test_quote_and_conductor_disagree_on_the_ollama_image_model(self):
        """Two copies of the same table; ollama already drifted."""
        for provider in ("openai", "gemini", "demo"):
            self.assertEqual(image_model_for(provider), _image_model(provider), provider)
        self.assertNotEqual(image_model_for("ollama"), _image_model("ollama"))


class WouldExceedReadsTheLedger(unittest.TestCase):
    """Claim 4: would_exceed is computed from usage_events, not a counter."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mem, _, _ = _workspace(Path(self.tmp.name))
        self.project = self.mem.create_project("Ledger")
        self.thread = self.mem.create_thread(self.project["id"])

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def _quote(self):
        return quote_run(
            provider="openai",
            model="gpt-4o-mini",
            prompt="one more",
            memory=self.mem,
            thread_id=self.thread["id"],
        )

    def _spend(self, usd: float, thread_id, age_seconds: float = 0.0):
        row = self.mem.add_usage(
            provider="openai",
            model="gpt-image-1",
            unit_kind="images",
            units=1,
            estimated_usd=usd,
            thread_id=thread_id,
        )
        if age_seconds:
            self.mem.conn.execute(
                "UPDATE usage_events SET created_at=created_at-? WHERE id=?",
                (age_seconds, row["id"]),
            )
            self.mem.conn.commit()
        return row

    def test_clean_ledger_passes_then_spend_flips_it(self):
        self.assertFalse(self._quote()["would_exceed"])
        self._spend(usage.THREAD_BUDGET_USD + 1, self.thread["id"])
        flipped = self._quote()
        self.assertTrue(flipped["would_exceed"])
        self.assertIn("thread budget", flipped["reason"])

    def test_deleting_ledger_rows_clears_the_flag(self):
        row = self._spend(usage.THREAD_BUDGET_USD + 1, self.thread["id"])
        self.assertTrue(self._quote()["would_exceed"])
        self.mem.conn.execute("DELETE FROM usage_events WHERE id=?", (row["id"],))
        self.mem.conn.commit()
        self.assertFalse(self._quote()["would_exceed"])

    def test_other_threads_only_count_against_the_daily_budget(self):
        other = self.mem.create_thread(self.project["id"])
        self._spend(usage.THREAD_BUDGET_USD + 1, other["id"])
        self.assertFalse(self._quote()["would_exceed"])
        self._spend(usage.DAILY_BUDGET_USD, other["id"])
        daily = self._quote()
        self.assertTrue(daily["would_exceed"])
        self.assertIn("daily budget", daily["reason"])

    def test_daily_window_rolls_but_thread_budget_never_resets(self):
        self._spend(usage.DAILY_BUDGET_USD + 5, None, age_seconds=86_400 + 600)
        self.assertFalse(self._quote()["would_exceed"])
        self._spend(usage.THREAD_BUDGET_USD + 1, self.thread["id"], age_seconds=400 * 86_400)
        self.assertTrue(self._quote()["would_exceed"])

    def test_unpriced_hold_is_what_gets_charged_against_the_budget(self):
        self._spend(usage.THREAD_BUDGET_USD - 0.02, self.thread["id"])
        unknown = quote_run(
            provider="openai",
            model="unknown-model-9",
            prompt="one more",
            memory=self.mem,
            thread_id=self.thread["id"],
        )
        self.assertFalse(unknown["priced"])
        self.assertTrue(unknown["would_exceed"])


if __name__ == "__main__":
    unittest.main()
