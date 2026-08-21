#!/usr/bin/env python3
"""Fable-09 — Round 17 (CI) verification.

The workflow must run the release gate and the evolve legion, trigger on
atelier/**, pyproject.toml and itself for both push and pull_request, pin
Python 3.11 on ubuntu-latest in both jobs, and never mention a live
provider key or GitHub secret. Stdlib only — the yaml is walked as
indented text, no PyYAML.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WF = ROOT / ".github" / "workflows" / "atelier.yml"

GATE_CMD = "python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve"
LEGION_CMD = "python3 -m unittest discover -s atelier/tests/evolve"
TRIGGER_PATHS = ("atelier/**", "pyproject.toml", ".github/workflows/atelier.yml")


def block(text: str, *headers: str) -> str:
    """Return the body of a nested mapping key, found by walking indentation.

    Each header names a mapping key (``jobs``, then ``gate``, ...); the body
    is every following line indented deeper than that key. Raises
    AssertionError when a header is missing, so a renamed job or dropped
    trigger fails loudly instead of vacuously passing.
    """
    lines = text.splitlines()
    lo, hi, indent = 0, len(lines), -1
    for header in headers:
        found = None
        for i in range(lo, hi):
            stripped = lines[i].strip()
            cur = len(lines[i]) - len(lines[i].lstrip())
            if stripped == header + ":" and cur > indent:
                found, indent = i, cur
                break
        if found is None:
            raise AssertionError(f"missing key {header!r} (path {headers})")
        lo = found + 1
        for j in range(lo, hi):
            line = lines[j]
            if line.strip() and (len(line) - len(line.lstrip())) <= indent:
                hi = j
                break
    return "\n".join(lines[lo:hi])


def list_items(body: str) -> list[str]:
    """Dash-list entries of a block body, unquoted."""
    out = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            out.append(stripped[2:].strip().strip('"').strip("'"))
    return out


def run_lines(body: str) -> list[str]:
    return [
        line.split("run:", 1)[1].strip()
        for line in body.splitlines()
        if line.strip().startswith("run:")
    ]


class CIWorkflow(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.text = WF.read_text(encoding="utf-8")

    def test_file_is_present_and_named(self):
        self.assertTrue(WF.is_file())
        self.assertEqual(self.text.splitlines()[0], "name: atelier")

    def test_triggers_cover_push_and_pull_request(self):
        for event in ("push", "pull_request"):
            listed = list_items(block(self.text, "on", event, "paths"))
            for want in TRIGGER_PATHS:
                self.assertIn(want, listed, f"{event} paths missing {want}")

    def test_exactly_gate_and_legion_jobs(self):
        jobs = block(self.text, "jobs")
        names = [
            line.strip().rstrip(":")
            for line in jobs.splitlines()
            if line.strip() and len(line) - len(line.lstrip()) == 2
        ]
        self.assertEqual(names, ["gate", "legion"])

    def test_gate_job_runs_release_gate(self):
        gate = block(self.text, "jobs", "gate")
        self.assertIn("runs-on: ubuntu-latest", gate)
        self.assertIn('python-version: "3.11"', gate)
        self.assertEqual(run_lines(gate), [GATE_CMD])

    def test_legion_job_discovers_evolve(self):
        legion = block(self.text, "jobs", "legion")
        self.assertIn("runs-on: ubuntu-latest", legion)
        self.assertIn('python-version: "3.11"', legion)
        self.assertEqual(run_lines(legion), [LEGION_CMD])

    def test_no_live_keys_secrets_or_env(self):
        lowered = self.text.lower()
        for needle in (
            "openai_api_key",
            "gemini_api_key",
            "anthropic_api_key",
            "secrets.",
        ):
            self.assertNotIn(needle, lowered)
        # No env blocks at all — no place to smuggle a key into a runner.
        self.assertNotIn("env:", self.text)

    def test_release_gate_meta_test_pins_this_file(self):
        from atelier.tests.test_evolve import Round17to20Meta

        self.assertTrue(callable(getattr(Round17to20Meta, "test_ci_workflow_exists")))


if __name__ == "__main__":
    unittest.main()
