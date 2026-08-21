#!/usr/bin/env python3
"""Fable-10 — Round 19 (eval fixtures) verification.

Fixtures load, and a demo weave can be scored for must_mention + palette.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.conductor import Conductor  # noqa: E402
from atelier.helix.evalrun import list_fixtures, load_fixture, run_fixture, score_result  # noqa: E402
from atelier.helix.keyring import Keyring  # noqa: E402
from atelier.helix.store import Memory  # noqa: E402

EVAL = ROOT / "atelier" / "data" / "eval"


class FixturesLoad(unittest.TestCase):
    def test_four_briefs_exist(self):
        names = {p.name for p in list_fixtures(EVAL)}
        self.assertEqual(
            names,
            {
                "brief_logo.json",
                "brief_poster.json",
                "brief_factsheet_legal_directory.json",
                "brief_brand_kit_apply.json",
            },
        )
        for path in list_fixtures(EVAL):
            data = load_fixture(path)
            self.assertIn("request", data)
            self.assertIn("expected", data)
            self.assertTrue(data["expected"].get("must_mention") or data["expected"].get("palette"))


class DemoScore(unittest.TestCase):
    def test_score_result_without_a_server(self):
        fixture = {
            "id": "toy",
            "expected": {"must_mention": ["Helix"], "palette": ["#112233"], "lanes_forbidden": ["video"]},
        }
        result = {
            "message": "Pinned Helix mark",
            "plan": {"intent": "Helix logo"},
            "artifacts": [{"prompt": "Helix", "kind": "image"}],
            "nodes": [{}],
        }
        report = score_result(fixture, result, [b'<svg fill="#112233"></svg>'])
        self.assertTrue(report["ok"])
        miss = score_result(fixture, {"message": "nope", "plan": {}, "artifacts": []}, [b"<svg/>"])
        self.assertFalse(miss["ok"])

    def test_logo_fixture_through_demo_conductor(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        arts = root / "artifacts"
        arts.mkdir()
        mem = Memory(root / "helix.sqlite3")
        cond = Conductor(mem, Keyring(root / "k.json"), arts)
        fixture = load_fixture(EVAL / "brief_logo.json")
        report = run_fixture(fixture, memory=mem, conductor=cond, artifacts_dir=arts)
        self.assertTrue(report["ok"], report)
        self.assertGreaterEqual(report["artifact_count"], 1)
        mem.close()
        tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
