#!/usr/bin/env python3
"""Fable-09 — Round 17 (CI) verification.

The workflow must run the release gate and the evolve legion, trigger on
pyproject.toml, and never mention a live provider key.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WF = ROOT / ".github" / "workflows" / "atelier.yml"


class CIWorkflow(unittest.TestCase):
    def setUp(self):
        self.text = WF.read_text(encoding="utf-8")

    def test_file_is_present(self):
        self.assertTrue(WF.is_file())
        self.assertIn("name: atelier", self.text)
        self.assertIn("python-version: \"3.11\"", self.text)

    def test_gate_and_legion_jobs(self):
        self.assertIn("atelier.tests.test_helix", self.text)
        self.assertIn("atelier.tests.test_evolve", self.text)
        self.assertIn("unittest discover -s atelier/tests/evolve", self.text)
        self.assertGreaterEqual(self.text.count("runs-on: ubuntu-latest"), 2)

    def test_pyproject_is_a_trigger(self):
        self.assertIn("pyproject.toml", self.text)
        self.assertIn("atelier/**", self.text)

    def test_no_live_keys_in_ci(self):
        for needle in ("OPENAI_API_KEY", "GEMINI_API_KEY", "secrets.", "ANTHROPIC_API_KEY"):
            self.assertNotIn(needle, self.text)


if __name__ == "__main__":
    unittest.main()
