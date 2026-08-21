#!/usr/bin/env python3
"""Opus-06 — Round 12 (text layer) verification.

Text nodes stay off the raster: type=text, no artifact_id, optional
font_size / font_family / letter_spacing in meta.
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


class TextWiring(unittest.TestCase):
    def test_text_layer_is_not_an_image(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        css = (WEB / "styles.css").read_text(encoding="utf-8")
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="textLayer"', html)
        self.assertIn(".text-layer", css)
        self.assertIn('type: "text"', app_js)
        self.assertIn("meta.font_size", app_js)
        self.assertIn("letter_spacing", app_js)


class TextRoute(unittest.TestCase):
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

    def test_text_node_has_type_and_type_meta(self):
        _, project = self._post("/api/projects", {"name": "R12"})
        status, node = self._post(
            f"/api/projects/{project['id']}/nodes",
            {"type": "text", "text": "Headline", "meta": {"layer": "text", "font_size": 36}},
        )
        self.assertEqual(status, 201)
        self.assertEqual(node["type"], "text")
        self.assertIsNone(node.get("artifact_id"))
        self.assertEqual(node["meta"]["layer"], "text")
        self.assertEqual(node["meta"]["font_size"], 36)


if __name__ == "__main__":
    unittest.main()
