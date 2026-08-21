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
    png_dimensions,
    render_sheet_rgb,
    scale_svg,
    wrap_raster_svg,
)
from atelier.helix.exportzip import export_project_zip  # noqa: E402
from atelier.helix.loom import demo_svg  # noqa: E402

WEB = ROOT / "atelier" / "web"

CSP_SANDBOX = "default-src 'none'; style-src 'unsafe-inline'; sandbox"


def _png_size(blob: bytes) -> tuple[int, int]:
    import struct

    assert blob[:8] == PNG_MAGIC
    return struct.unpack(">II", blob[16:24])


class ScaleAndPng(unittest.TestCase):
    def test_scale_snaps_to_1_2_4(self):
        self.assertEqual([export_scale(v) for v in (0, 1, 2, 3, 4, 9, "nope")], [1, 1, 2, 2, 4, 4, 1])

    def test_encode_png_is_a_real_png(self):
        blob = encode_png(2, 2, bytes((255, 0, 0, 0, 255, 0, 0, 0, 255, 10, 10, 10)))
        self.assertTrue(blob.startswith(PNG_MAGIC))
        self.assertGreater(len(blob), 40)
        self.assertEqual(png_dimensions(blob), (2, 2))


class ClosedHoles(unittest.TestCase):
    """Holes found by the R13 verifier and closed in exportfmt."""

    def test_far_flung_node_does_not_size_the_buffer(self):
        # x/y are only checked for finiteness on write; one node at y=1e12
        # used to make the sheet try a petabyte bytearray on the default zip.
        nodes = [
            {"type": "text", "text": "hi", "x": 40, "y": 40, "w": 320, "h": 120},
            {"type": "text", "text": "far", "x": 40, "y": 1e12, "w": 320, "h": 120},
        ]
        for y in (1e12, 1e308):
            nodes[1]["y"] = y
            w, h, rgb = render_sheet_rgb({"name": "X"}, nodes, 1)
            self.assertLessEqual(h, 640 * 4 + 200)
            self.assertEqual(len(rgb), w * h * 3)

    def test_scale_svg_only_touches_the_root_tag(self):
        # A blind first-two-attributes pass used to bump a nested <rect>
        # when an uploaded root carried no width/height of its own.
        noroot = b'<svg xmlns="x" viewBox="0 0 100 50"><rect width="100" height="50"/></svg>'
        out = scale_svg(noroot, 2)
        self.assertIn(b'width="200"', out)
        self.assertIn(b'height="100"', out)
        self.assertIn(b'<rect width="100" height="50"/>', out)
        rooted = b'<svg xmlns="x" width="10" height="20"><rect width="100"/></svg>'
        out = scale_svg(rooted, 4)
        self.assertIn(b'width="40"', out)
        self.assertIn(b'height="80"', out)
        self.assertIn(b'<rect width="100"/>', out)
        neither = b'<svg xmlns="x"><rect width="100"/></svg>'
        self.assertEqual(scale_svg(neither, 4), neither)
        self.assertEqual(scale_svg(noroot, 1), noroot)

    def test_wrap_raster_svg_keeps_png_dimensions(self):
        tiny = encode_png(3, 2, bytes(range(18)))
        out = wrap_raster_svg(tiny, "image/png", 2).decode()
        self.assertIn('width="6" height="4"', out)
        self.assertIn('viewBox="0 0 3 2"', out)
        self.assertIn("data:image/png;base64,", out)
        # non-PNG bytes still get the 1024 frame, not a crash
        out = wrap_raster_svg(b"not a png", "image/webp", 1).decode()
        self.assertIn('viewBox="0 0 1024 1024"', out)


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

    def test_cjk_name_slug_falls_back_to_id(self):
        # Known R4-era hole, pinned: a name with no ASCII alnum yields the id.
        cjk = self.mem.create_project("\u6f22\u5b57\u306e\u540d\u524d")
        _, _, name = export_project_bytes(self.mem, self.arts, cjk["id"], fmt="svg")
        self.assertEqual(name, f"atelier-{cjk['id'][:12]}-board.svg")


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
        with zipfile.ZipFile(io.BytesIO(body)) as zf:
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
            # artifact bytes ride along, and threads carry their messages
            self.assertTrue(any(n.startswith("artifacts/") for n in names))
            threads = json.loads(zf.read("threads.json"))
            self.assertTrue(threads and threads[0].get("messages"))
            self.assertEqual(zf.read("RIGHTS.txt").decode(), RIGHTS_TEXT)
            svg = zf.read("board.svg").decode("utf-8")
            self.assertIn(">Quiet type</text>", svg)

    def test_fmt_svg_keeps_text_and_sandboxes(self):
        project, art = self._project()
        status, body, headers = self._get(f"/api/projects/{project['id']}/export?fmt=svg&scale=2")
        self.assertEqual(status, 200)
        self.assertIn("image/svg", headers.get("Content-Type", ""))
        self.assertEqual(headers.get("Content-Security-Policy"), CSP_SANDBOX)
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("attachment", headers.get("Content-Disposition", ""))
        self.assertIn(b"<text", body)
        self.assertIn(b"Quiet type", body)
        self.assertIn(b'font-size="40', body)
        # the demo SVG artifact is inlined as vector, not baked to pixels
        self.assertGreaterEqual(body.count(b"<svg"), 2)
        # same sandbox as the artifact view route
        _, _, art_headers = self._get(f"/api/artifacts/{art['id']}")
        self.assertEqual(
            headers.get("Content-Security-Policy"),
            art_headers.get("Content-Security-Policy"),
        )

    def test_fmt_png_and_pdf(self):
        project, _ = self._project()
        status, body, headers = self._get(f"/api/projects/{project['id']}/export?fmt=png")
        self.assertEqual((status, body[:8]), (200, PNG_MAGIC))
        self.assertEqual(headers.get("Content-Type"), "image/png")
        status, body, headers = self._get(f"/api/projects/{project['id']}/export?fmt=pdf")
        self.assertEqual(status, 200)
        self.assertTrue(body.startswith(b"%PDF"))
        self.assertTrue(body.rstrip().endswith(b"%%EOF"))
        self.assertEqual(headers.get("Content-Type"), "application/pdf")

    def test_scale_snaps_over_http(self):
        project, _ = self._project()
        widths = {}
        for scale in ("1", "3", "9"):
            status, body, _ = self._get(
                f"/api/projects/{project['id']}/export?fmt=png&scale={scale}"
            )
            self.assertEqual(status, 200)
            widths[scale] = _png_size(body)[0]
        # 3 snaps down to 2, 9 snaps down to 4
        self.assertEqual(widths["3"], widths["1"] * 2)
        self.assertEqual(widths["9"], widths["1"] * 4)

    def test_jpeg_is_415(self):
        project, _ = self._project()
        status, body, _ = self._get(f"/api/projects/{project['id']}/export?fmt=jpeg")
        self.assertEqual(status, 415)
        self.assertEqual(json.loads(body).get("code"), "unsupported_fmt")

    def test_missing_project_is_404(self):
        for fmt in ("zip", "svg", "png", "pdf"):
            status, body, _ = self._get(f"/api/projects/deadbeef/export?fmt={fmt}")
            self.assertEqual(status, 404)

    def test_artifact_export_png_and_svg(self):
        _, art = self._project()
        status, body, headers = self._get(f"/api/artifacts/{art['id']}/export?fmt=native")
        self.assertEqual(status, 200)
        self.assertIn("image/svg", headers.get("Content-Type", ""))
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("attachment", headers.get("Content-Disposition", ""))
        status, body, headers = self._get(f"/api/artifacts/{art['id']}/export?fmt=svg")
        self.assertEqual(status, 200)
        self.assertIn("image/svg", headers.get("Content-Type", ""))
        self.assertEqual(headers.get("Content-Security-Policy"), CSP_SANDBOX)
        self.assertTrue(body.lstrip().startswith(b"<svg") or b"<svg" in body[:80])
        status, body, headers = self._get(f"/api/artifacts/{art['id']}/export?fmt=png")
        self.assertEqual((status, body[:8]), (200, PNG_MAGIC))
        self.assertEqual(headers.get("Content-Type"), "image/png")
        status, body, headers = self._get(f"/api/artifacts/{art['id']}/export?fmt=pdf")
        self.assertTrue(body.startswith(b"%PDF"))
        self.assertTrue(body.rstrip().endswith(b"%%EOF"))
        status, body, _ = self._get(f"/api/artifacts/{art['id']}/export?fmt=jpeg")
        self.assertEqual(status, 415)
        self.assertEqual(json.loads(body).get("code"), "unsupported_fmt")

    def test_uploaded_png_rides_the_board_svg_as_data_uri(self):
        import base64

        project, _ = self._project()
        tiny = encode_png(2, 2, bytes((255, 0, 0, 0, 255, 0, 0, 0, 255, 9, 9, 9)))
        status, up = self._json(
            "POST",
            f"/api/projects/{project['id']}/upload",
            {"filename": "swatch.png", "mime": "image/png",
             "data": base64.b64encode(tiny).decode()},
        )
        self.assertEqual(status, 201)
        status, body, _ = self._get(f"/api/projects/{project['id']}/export?fmt=svg")
        self.assertEqual(status, 200)
        self.assertIn(b'href="data:image/png;base64,', body)
        # the raster artifact's own fmt=svg keeps its true 2x2 dimensions
        art_id = up["artifact"]["id"]
        status, body, _ = self._get(f"/api/artifacts/{art_id}/export?fmt=svg&scale=2")
        self.assertEqual(status, 200)
        self.assertIn(b'viewBox="0 0 2 2"', body)
        self.assertIn(b'width="4" height="4"', body)

    def test_missing_artifact_export_is_404(self):
        status, _, _ = self._get("/api/artifacts/deadbeef/export?fmt=png")
        self.assertEqual(status, 404)
        # a row whose bytes are gone from disk is also 404, not a 500
        app = self.mod.get_app()
        ghost = app.memory.add_artifact(
            project_id=self._project()[0]["id"],
            kind="image", mime="image/svg+xml",
            prompt="ghost", provider="demo", model="demo",
        )
        status, _, _ = self._get(f"/api/artifacts/{ghost['id']}/export?fmt=native")
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

    def test_dialog_fallback_still_downloads_the_zip(self):
        # No showModal (old engine) -> plain navigation to the default export,
        # which the HTTP suite proves is the zip.
        app = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('typeof dlg.showModal === "function"', app)
        self.assertIn("window.location = `/api/projects/${state.projectId}/export`;", app)


if __name__ == "__main__":
    unittest.main()
