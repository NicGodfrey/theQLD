#!/usr/bin/env python3
"""Fable-03 — Round 5 (reference upload) verification.

Pins the live JSON upload route, the hidden `#filePick` click binding, and
the next-weave `parent_artifact_id` from `state.lastUploadId`.
"""

from __future__ import annotations

import base64
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


class UploadWiring(unittest.TestCase):
    def test_file_pick_is_bound_to_a_visible_control(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="filePick"', html)
        self.assertIn('id="uploadBtn"', html)
        self.assertIn('document.getElementById("filePick").click()', app_js)
        self.assertIn('document.getElementById("uploadBtn")', app_js)
        self.assertIn('filePick").addEventListener("change"', app_js)
        self.assertIn("lastUploadId", app_js)
        self.assertIn("state.lastUploadId", app_js)
        self.assertIn("parent_artifact_id", app_js)

    def test_drop_and_keyboard_u_also_upload(self):
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('wrap.addEventListener("drop"', app_js)
        self.assertIn("await uploadFile(file)", app_js)
        self.assertIn('e.key === "u"', app_js)


class UploadRoute(unittest.TestCase):
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

    def test_json_upload_pins_a_board_node(self):
        _, project = self._post("/api/projects", {"name": "R5"})
        payload = base64.b64encode(b"<svg xmlns='http://www.w3.org/2000/svg'></svg>").decode()
        status, uploaded = self._post(
            f"/api/projects/{project['id']}/upload",
            {"filename": "ref.svg", "mime": "image/svg+xml", "data": payload},
        )
        self.assertEqual(status, 201)
        self.assertEqual(uploaded["artifact"]["kind"], "upload")
        self.assertEqual(uploaded["node"]["artifact_id"], uploaded["artifact"]["id"])
        self.assertEqual(uploaded["node"]["type"], "image")

    def test_oversized_upload_is_413(self):
        _, project = self._post("/api/projects", {"name": "R5-big"})
        blob = b"x" * 5_000_001
        status, body = self._post(
            f"/api/projects/{project['id']}/upload",
            {
                "filename": "big.bin",
                "mime": "application/octet-stream",
                "data": base64.b64encode(blob).decode(),
            },
        )
        self.assertEqual(status, 413)
        self.assertIn("too large", body["error"])

    def test_uploaded_reference_is_the_next_weave_parent(self):
        _, project = self._post("/api/projects", {"name": "R5-parent"})
        _, thread = self._post(f"/api/projects/{project['id']}/threads", {"topic": "r5"})
        payload = base64.b64encode(b"<svg xmlns='http://www.w3.org/2000/svg'></svg>").decode()
        _, uploaded = self._post(
            f"/api/projects/{project['id']}/upload",
            {"filename": "ref.svg", "mime": "image/svg+xml", "data": payload},
        )
        parent_id = uploaded["artifact"]["id"]
        status, result = self._post(
            f"/api/threads/{thread['id']}/run",
            {"prompt": "match this reference", "provider": "demo", "parent_artifact_id": parent_id},
        )
        self.assertEqual(status, 200)
        self.assertEqual(result["artifacts"][0]["parent_id"], parent_id)
        self.assertEqual(result["plan"]["spot_edit"]["parent_id"], parent_id)


if __name__ == "__main__":
    unittest.main()
