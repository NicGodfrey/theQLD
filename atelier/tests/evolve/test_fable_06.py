#!/usr/bin/env python3
"""Fable-06 — Round 11 (spot-edit) verification.

A clicked board card becomes `state.selectedArtifactId` and is sent as
`parent_artifact_id` without requiring magic words.
"""

from __future__ import annotations

import json
import os
import re
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
        self.assertIn("!present.has(state.selectedArtifactId)", app_js)

    def test_run_body_parent_priority_order(self):
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        priority = re.search(
            r"const parent = state\.selectedArtifactId\s*"
            r"\|\|\s*\(spotWords \? state\.lastArtifactId : undefined\)\s*"
            r"\|\|\s*state\.lastUploadId",
            app_js,
        )
        self.assertIsNotNone(priority, "runBody() must prefer selection, then spot-word fallback, then upload")
        spot = re.search(r"const spotWords = /(.+?)/i\.test\(prompt\)", app_js)
        self.assertIsNotNone(spot)
        for word in ("spot", "局部", "edit this", "refine", "larger type", "bigger type"):
            self.assertIn(word, spot.group(1))

    def test_selection_clears_when_the_project_changes(self):
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        resets = app_js.count("state.selectedArtifactId = null")
        self.assertGreaterEqual(
            resets, 2, "project switch and new-project must clear the selected parent"
        )
        for chunk in re.findall(r"state\.projectId = (?:p\.id|project\.id);[^}]+", app_js):
            self.assertIn("state.selectedArtifactId = null", chunk)


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

    def test_unknown_parent_is_ignored_not_fatal(self):
        _, project = self._post("/api/projects", {"name": "R11-ghost"})
        _, thread = self._post(f"/api/projects/{project['id']}/threads", {"topic": "r11"})
        status, result = self._post(
            f"/api/threads/{thread['id']}/run",
            {
                "prompt": "refine the crest",
                "provider": "demo",
                "parent_artifact_id": "art-does-not-exist",
            },
        )
        self.assertEqual(status, 200)
        self.assertIsNone(result["artifacts"][0].get("parent_id"))
        self.assertNotIn("spot_edit", result["plan"])

    def test_spot_artifact_id_alias_still_accepted(self):
        _, project = self._post("/api/projects", {"name": "R11-alias"})
        _, thread = self._post(f"/api/projects/{project['id']}/threads", {"topic": "r11"})
        _, first = self._post(
            f"/api/threads/{thread['id']}/run",
            {"prompt": "base mark", "provider": "demo"},
        )
        parent_id = first["artifacts"][0]["id"]
        status, second = self._post(
            f"/api/threads/{thread['id']}/run",
            {
                "prompt": "bigger type",
                "provider": "demo",
                "spot_artifact_id": parent_id,
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(second["artifacts"][0]["parent_id"], parent_id)
        self.assertEqual(second["plan"]["spot_edit"]["parent_id"], parent_id)

    def test_parent_from_another_project_is_ignored(self):
        _, a = self._post("/api/projects", {"name": "R11-A"})
        _, ta = self._post(f"/api/projects/{a['id']}/threads", {"topic": "a"})
        _, first = self._post(
            f"/api/threads/{ta['id']}/run",
            {"prompt": "base mark", "provider": "demo"},
        )
        foreign = first["artifacts"][0]["id"]
        _, b = self._post("/api/projects", {"name": "R11-B"})
        _, tb = self._post(f"/api/projects/{b['id']}/threads", {"topic": "b"})
        status, result = self._post(
            f"/api/threads/{tb['id']}/run",
            {"prompt": "steal", "provider": "demo", "parent_artifact_id": foreign},
        )
        self.assertEqual(status, 200)
        self.assertIsNone(result["artifacts"][0].get("parent_id"))
        self.assertNotIn("spot_edit", result["plan"])


if __name__ == "__main__":
    unittest.main()
