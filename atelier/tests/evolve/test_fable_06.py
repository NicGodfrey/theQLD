#!/usr/bin/env python3
"""Fable-06 — Round 11 (spot-edit) verification.

A clicked board card becomes `state.selectedArtifactId` and is sent as
`parent_artifact_id` without requiring magic words.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WEB = ROOT / "atelier" / "web"


class SpotWiring(unittest.TestCase):
    def test_selection_is_the_parent_without_magic_words(self):
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        css = (WEB / "styles.css").read_text(encoding="utf-8")
        self.assertIn("selectedArtifactId", app_js)
        self.assertIn("Use as reference", app_js)
        self.assertIn("state.selectedArtifactId", app_js)
        self.assertIn(".node.selected", css)
        self.assertIn("larger type", app_js)
        self.assertIn("parent_artifact_id: parent", app_js)


class SpotRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls._saved_env = {k: os.environ.get(k) for k in ("ATELIER_RUNTIME", "ATELIER_HOME")}
        os.environ["ATELIER_RUNTIME"] = str(Path(cls.tmp.name) / "rt")
        os.environ["ATELIER_HOME"] = str(Path(cls.tmp.name) / "home")
        from atelier import server as server_module

        cls.server = server_module
        server_module.reset_app()
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server_module.Handler)
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.thread.join(timeout=5)
        cls.httpd.server_close()
        cls.server.get_app().memory.close()
        cls.server.reset_app()
        for key, value in cls._saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        cls.tmp.cleanup()

    def _post(self, path, body):
        req = urllib.request.Request(
            self.base + path,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_selected_parent_does_not_need_spot_words(self):
        _, project = self._post("/api/projects", {"name": "R11"})
        _, thread = self._post(f"/api/projects/{project['id']}/threads", {"topic": "r11"})
        _, first = self._post(
            f"/api/threads/{thread['id']}/run",
            {"prompt": "base mark", "provider": "demo"},
        )
        parent_id = first["artifacts"][0]["id"]
        status, second = self._post(
            f"/api/threads/{thread['id']}/run",
            {
                "prompt": "make the type larger",
                "provider": "demo",
                "parent_artifact_id": parent_id,
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(second["artifacts"][0]["parent_id"], parent_id)
        self.assertEqual(second["plan"]["spot_edit"]["parent_id"], parent_id)


if __name__ == "__main__":
    unittest.main()
