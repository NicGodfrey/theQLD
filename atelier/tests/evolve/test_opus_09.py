#!/usr/bin/env python3
"""Opus-09 — Round 18 (live contract) verification.

CONTRACT.md must list the live Helix surface and must not describe the
research `/api/chat` SSE board as live.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONTRACT = ROOT / "atelier" / "research" / "evolve" / "CONTRACT.md"
SERVER = ROOT / "atelier" / "server.py"
WEB_JS = ROOT / "atelier" / "web" / "app.js"


class LiveContract(unittest.TestCase):
    def setUp(self):
        self.contract = CONTRACT.read_text(encoding="utf-8")
        self.server = SERVER.read_text(encoding="utf-8")
        self.app = WEB_JS.read_text(encoding="utf-8")

    def test_contract_file_exists(self):
        self.assertTrue(CONTRACT.is_file())
        self.assertIn("Live Helix HTTP contract", self.contract)

    def test_live_is_not_research_chat(self):
        self.assertIn("does not use `/api/chat`", self.contract)
        self.assertNotIn('path == "/api/chat"', self.server)
        self.assertNotIn("/api/chat", self.app)
        self.assertIn("/api/threads/", self.app)
        self.assertIn("/api/quote", self.contract)

    def test_missing_routes_are_now_listed(self):
        for needle in (
            "DELETE | `/api/nodes/:id`",
            "POST | `/api/projects/:id/brand`",
            "GET | `/api/catalog`",
            "GET | `/api/health`",
            "GET | `/api/artifacts/:id/export`",
        ):
            self.assertIn(needle, self.contract)

    def test_server_actually_has_those_routes(self):
        self.assertIn('path == "/api/catalog"', self.server)
        self.assertIn('path == "/api/health"', self.server)
        self.assertIn('parts[3] == "brand"', self.server)
        self.assertIn("def do_DELETE", self.server)
        self.assertIn('parts[3] == "export"', self.server)

    def test_415_is_documented(self):
        self.assertIn("415", self.contract)
        self.assertIn("JPEG", self.contract)


if __name__ == "__main__":
    unittest.main()
