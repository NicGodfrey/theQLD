#!/usr/bin/env python3
"""Opus-10 — Round 20 (scorecard) verification.

The card must stay above the 16/20 gate without claiming Lovart-complete
or a proven paid loop.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CARD = ROOT / "atelier" / "research" / "evolve" / "SCORECARD.json"


class HonestScorecard(unittest.TestCase):
    def setUp(self):
        self.card = json.loads(CARD.read_text(encoding="utf-8"))

    def test_gate_and_counts(self):
        self.assertEqual(self.card["rounds_total"], 20)
        self.assertEqual(len(self.card["rounds"]), 20)
        self.assertGreaterEqual(self.card["passed"], self.card["gate"])
        self.assertGreaterEqual(self.card["gate"], 16)
        self.assertTrue(self.card["gates"]["fail_closed"])
        self.assertTrue(self.card["gates"]["stdlib_only"])

    def test_does_not_claim_lovart_or_paid(self):
        self.assertFalse(self.card["lovart_complete"])
        self.assertFalse(self.card["paid_loop_proven"])
        self.assertTrue(self.card["demo_loop"])
        self.assertTrue(self.card["honest"])
        holes = " ".join(self.card["remaining_product_holes"]).lower()
        self.assertIn("paid", holes)
        self.assertIn("stylelock", holes)
        self.assertIn("contact sheet", holes)

    def test_every_round_is_numbered(self):
        nums = [r["n"] for r in self.card["rounds"]]
        self.assertEqual(nums, list(range(1, 21)))
        self.assertTrue(all(r.get("pass") for r in self.card["rounds"]))
        self.assertTrue(self.card["rounds"][-1].get("note"))


if __name__ == "__main__":
    unittest.main()
