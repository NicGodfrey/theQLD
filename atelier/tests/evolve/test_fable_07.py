#!/usr/bin/env python3
"""Fable-07 — Round 13 (designer export) verification.

The zip is still the archive. This round adds the deliverable: board.svg
(text stays <text>), a stdlib sheet PNG/PDF, per-artifact /export?fmt=,
a scale query, and a rights line. JPEG is refused.
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.exportfmt import (  # noqa: E402
    PNG_MAGIC,
    RIGHTS_TEXT,
    FormatError,
    encode_png,
    export_project_bytes,
    export_scale,
)
from atelier.helix.exportzip import export_project_zip  # noqa: E402
from atelier.helix.loom import demo_svg  # noqa: E402

WEB = ROOT / "atelier" / "web"


class ScaleAndPng(unittest.TestCase):
    def test_scale_snaps_to_1_2_4(self):
        self.assertEqual([export_scale(v) for v in (0, 1, 2, 3, 4, 9, "nope")], [1, 1, 2, 2, 4, 4, 1])

    def test_encode_png_is_a_real_png(self):
        blob = encode_png(2, 2, bytes((255, 0, 0, 0, 255, 0, 0, 0, 255, 10, 10, 10)))
        self.assertTrue(blob.startswith(PNG_MAGIC))
        self.assertGreater(len(blob), 40)


class ExportFormats(unittest.TestCase):
    def setUp(self):
        from atelier.helix.conductor import Conductor
        from atelier.helix.keyring import Keyring
        from atelier.helix.store import Memory

        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.arts = root / "artifacts"
        self.arts.mkdir()
        self.mem = Memory(root / "helix.sqlite3")
        self.project = self.mem.create_project("Export Me")
        self.thread = self.mem.create_thread(self.project["id"])
        self.cond = Conductor(self.mem, Keyring(root / "k.json"), self.arts)
        self.cond.run(
            project_id=self.project["id"],
            thread_id=self.thread["id"],
            prompt="navy mark",
            provider="demo",
        )
        self.mem.add_node(
            project_id=self.project["id"],
            type="text",
            text="Headline",
            x=40,
            y=40,
            meta={"layer": "text", "font_size": 36, "font_family": "Georgia, serif"},
        )

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def test_zip_carries_the_designer_sheet(self):
        blob = export_project_zip(self.mem, self.arts, self.project["id"])
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            names = set(zf.namelist())
            for required in (
                "project.json",
                "board.json",
                "board.svg",
                "sheet.png",
                "sheet.pdf",
                "RIGHTS.txt",
                "threads.json",
                "artifacts.json",
            ):
                self.assertIn(required, names)
            svg = zf.read("board.svg").decode("utf-8")
            self.assertIn("<text", svg)
            self.assertIn("Headline", svg)
            self.assertIn('font-size="36', svg)
            self.assertTrue(zf.read("sheet.png").startswith(PNG_MAGIC))
            self.assertTrue(zf.read("sheet.pdf").startswith(b"%PDF"))
            self.assertIn("does not grant commercial rights", zf.read("RIGHTS.txt").decode())

    def test_text_stays_type_in_board_svg(self):
        data, mime, name = export_project_bytes(self.mem, self.arts, self.project["id"], fmt="svg")
        self.assertEqual(mime, "image/svg+xml")
        self.assertTrue(name.endswith("-board.svg"))
        text = data.decode("utf-8")
        self.assertIn("<text", text)
        self.assertIn("Headline", text)
        self.assertNotIn("<img", text)

    def test_sheet_png_and_pdf(self):
        png, mime, name = export_project_bytes(self.mem, self.arts, self.project["id"], fmt="png", scale=2)
        self.assertEqual(mime, "image/png")
        self.assertTrue(png.startswith(PNG_MAGIC))
        self.assertTrue(name.endswith("-sheet.png"))
        pdf, mime, name = export_project_bytes(self.mem, self.arts, self.project["id"], fmt="pdf")
        self.assertEqual(mime, "application/pdf")
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertIn(b"%%EOF", pdf)

    def test_jpeg_is_refused(self):
        with self.assertRaises(FormatError) as ctx:
            export_project_bytes(self.mem, self.arts, self.project["id"], fmt="jpeg")
        self.assertEqual(ctx.exception.code, "unsupported_fmt")

    def test_missing_project_is_missing(self):
        with self.assertRaises(ValueError):
            export_project_bytes(self.mem, self.arts, "deadbeef", fmt="svg")


class ExportHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls._saved = {k: os.environ.get(k) for k in ("ATELIER_RUNTIME", "ATELIER_HOME")}
        os.environ["ATELIER_RUNTIME"] = str(Path(cls.tmp.name) / "rt")
        os.environ["ATELIER_HOME"] = str(Path(cls.tmp.name) / "home")
        from atelier import server as server_module

        cls.mod = server_module
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
        cls.mod.get_app().memory.close()
        cls.mod.reset_app()
        for key, value in cls._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        cls.tmp.cleanup()

    def _json(self, method, path, body=None):
        req = urllib.request.Request(
            self.base + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def _get(self, path):
        req = urllib.request.Request(self.base + path)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.status, resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), dict(exc.headers)

    def _project(self):
        _, project = self._json("POST", "/api/projects", {"name": "R13"})
        _, threads = self._json("GET", f"/api/projects/{project['id']}/threads")
        tid = threads["threads"][0]["id"]
        _, result = self._json(
            "POST",
            f"/api/threads/{tid}/run",
            {"prompt": "export mark", "provider": "demo"},
        )
        self._json(
            "POST",
            f"/api/projects/{project['id']}/nodes",
            {"type": "text", "text": "Quiet type", "meta": {"layer": "text", "font_size": 40}},
        )
        return project, result["artifacts"][0]

    def test_default_export_is_still_a_zip(self):
        project, _ = self._project()
        status, body, headers = self._get(f"/api/projects/{project['id']}/export")
        self.assertEqual(status, 200)
        self.assertEqual(body[:2], b"PK")
        self.assertEqual(headers.get("Content-Type"), "application/zip")
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("attachment", headers.get("Content-Disposition", ""))

    def test_fmt_svg_keeps_text_and_sandboxes(self):
        project, _ = self._project()
        status, body, headers = self._get(f"/api/projects/{project['id']}/export?fmt=svg&scale=2")
        self.assertEqual(status, 200)
        self.assertIn("image/svg", headers.get("Content-Type", ""))
        self.assertIn("default-src 'none'", headers.get("Content-Security-Policy", ""))
        self.assertIn(b"<text", body)
        self.assertIn(b"Quiet type", body)

    def test_fmt_png_and_pdf(self):
        project, _ = self._project()
        status, body, headers = self._get(f"/api/projects/{project['id']}/export?fmt=png")
        self.assertEqual((status, body[:8]), (200, PNG_MAGIC))
        self.assertEqual(headers.get("Content-Type"), "image/png")
        status, body, headers = self._get(f"/api/projects/{project['id']}/export?fmt=pdf")
        self.assertEqual(status, 200)
        self.assertTrue(body.startswith(b"%PDF"))
        self.assertEqual(headers.get("Content-Type"), "application/pdf")

    def test_jpeg_is_415(self):
        project, _ = self._project()
        status, body, _ = self._get(f"/api/projects/{project['id']}/export?fmt=jpeg")
        self.assertEqual(status, 415)
        self.assertEqual(json.loads(body).get("code"), "unsupported_fmt")

    def test_missing_project_is_404(self):
        status, body, _ = self._get("/api/projects/deadbeef/export?fmt=svg")
        self.assertEqual(status, 404)

    def test_artifact_export_png_and_svg(self):
        _, art = self._project()
        status, body, headers = self._get(f"/api/artifacts/{art['id']}/export?fmt=svg")
        self.assertEqual(status, 200)
        self.assertIn("image/svg", headers.get("Content-Type", ""))
        self.assertTrue(body.lstrip().startswith(b"<svg") or b"<svg" in body[:80])
        status, body, headers = self._get(f"/api/artifacts/{art['id']}/export?fmt=png")
        self.assertEqual((status, body[:8]), (200, PNG_MAGIC))
        status, body, headers = self._get(f"/api/artifacts/{art['id']}/export?fmt=pdf")
        self.assertTrue(body.startswith(b"%PDF"))
        status, body, _ = self._get(f"/api/artifacts/{art['id']}/export?fmt=jpeg")
        self.assertEqual(status, 415)

    def test_missing_artifact_export_is_404(self):
        status, _, _ = self._get("/api/artifacts/deadbeef/export?fmt=png")
        self.assertEqual(status, 404)


class ExportWiring(unittest.TestCase):
    def test_dialog_lists_formats_and_rights(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        css = (WEB / "styles.css").read_text(encoding="utf-8")
        app = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="exportDialog"', html)
        self.assertIn('id="exportRights"', html)
        self.assertIn("Atelier grants none", html)
        self.assertIn("exportFmt", html)
        self.assertIn('id="exportScale"', html)
        self.assertIn("/export?fmt=", app)
        self.assertIn("/api/artifacts/${node.artifact_id}/export?fmt=png", app)
        self.assertIn(".export-dialog", css)
        self.assertIn("does not grant commercial rights", RIGHTS_TEXT)
        self.assertIn("does not grant commercial rights", (ROOT / "atelier" / "OUTPUT_RIGHTS.md").read_text())
        # demo_svg still exists; we did not swap the live weave to PNG
        self.assertIn("<svg", demo_svg("probe"))


if __name__ == "__main__":
    unittest.main()
