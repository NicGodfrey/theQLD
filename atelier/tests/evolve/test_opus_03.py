#!/usr/bin/env python3
"""Opus-03 — Round 6 (canvas camera) verification.

Pins server-side camera persist + zoom clamp, and the Home / Fit / readout
reset wiring in the live board.
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


class CameraWiring(unittest.TestCase):
    def test_home_fit_and_readout_reset_exist(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="camHome"', html)
        self.assertIn('id="camFit"', html)
        self.assertIn("function resetCamera()", app_js)
        self.assertIn("function fitCamera()", app_js)
        self.assertIn("persistCameraTimer", app_js)
        self.assertIn('document.getElementById("camHome").onclick = resetCamera', app_js)
        self.assertIn('document.getElementById("camFit").onclick = fitCamera', app_js)
        self.assertIn('document.getElementById("camReadout").onclick = resetCamera', app_js)

    def test_wheel_and_pan_still_drive_the_camera(self):
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('wrap.addEventListener("wheel"', app_js)
        self.assertIn("persistCamera()", app_js)
        self.assertIn("clampCamera", app_js)


class CameraRoute(unittest.TestCase):
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

    def _json(self, method, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(
            self.base + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_camera_round_trips_on_the_board(self):
        _, project = self._json("POST", "/api/projects", {"name": "R6"})
        status, saved = self._json(
            "POST",
            f"/api/projects/{project['id']}/camera",
            {"camera": {"x": 40, "y": -12, "zoom": 1.5}},
        )
        self.assertEqual(status, 200)
        self.assertEqual(saved["camera"], {"x": 40.0, "y": -12.0, "zoom": 1.5})
        status, got = self._json("GET", f"/api/projects/{project['id']}/camera")
        self.assertEqual(status, 200)
        self.assertEqual(got["camera"]["zoom"], 1.5)
        _, board = self._json("GET", f"/api/projects/{project['id']}/board")
        self.assertEqual(board["camera"]["x"], 40.0)

    def test_zoom_is_clamped(self):
        _, project = self._json("POST", "/api/projects", {"name": "R6-clamp"})
        _, hi = self._json(
            "POST",
            f"/api/projects/{project['id']}/camera",
            {"camera": {"zoom": 99}},
        )
        self.assertEqual(hi["camera"]["zoom"], 3.0)
        _, lo = self._json(
            "POST",
            f"/api/projects/{project['id']}/camera",
            {"camera": {"zoom": 0.01}},
        )
        self.assertEqual(lo["camera"]["zoom"], 0.25)
        _, zero = self._json(
            "POST",
            f"/api/projects/{project['id']}/camera",
            {"camera": {"zoom": 0}},
        )
        self.assertEqual(zero["camera"]["zoom"], 1.0)

    def test_missing_project_is_404(self):
        status, body = self._json("POST", "/api/projects/deadbeef/camera", {"camera": {"zoom": 1}})
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "missing project")


if __name__ == "__main__":
    unittest.main()
