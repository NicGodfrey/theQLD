#!/usr/bin/env python3
"""Opus-02 — Round 4 (artifact download) verification.

Read-only over the live tree: pins the inline-vs-attachment split on
`GET /api/artifacts/:id`, the brief-derived filename from
`atelier.helix.loom.download_filename`, the `nosniff` header on `_send_file`,
and the `safe_under(app.artifacts, ...)` containment. Also pins the known
holes so a later fix has to change a test on purpose.
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

from atelier.helix.loom import download_filename, ext_for_mime  # noqa: E402
from atelier.helix.paths import safe_under  # noqa: E402

WEB = ROOT / "atelier" / "web"
SERVER_PY = ROOT / "atelier" / "server.py"


class DownloadFilename(unittest.TestCase):
    """`download_filename` — the brief slug, never the hex id."""

    def test_brief_slug_wins_over_the_hex_id(self):
        name = download_filename(
            {"id": "9f3c1b2a4d5e", "prompt": "Navy Wordmark for Bell & Co.", "mime": "image/png"}
        )
        self.assertEqual(name, "navy-wordmark-for-bell-co.png")
        self.assertNotIn("9f3c", name)

    def test_extension_follows_the_stored_mime(self):
        for mime, ext in (
            ("image/svg+xml", ".svg"),
            ("image/png", ".png"),
            ("image/jpeg", ".jpg"),
            ("image/webp", ".webp"),
            ("video/mp4", ".mp4"),
            ("application/zip", ".zip"),
        ):
            self.assertEqual(download_filename({"prompt": "mark", "mime": mime}), f"mark{ext}")
        self.assertEqual(ext_for_mime("image/png; charset=binary"), ".png")

    def test_filename_is_header_safe(self):
        # Only [a-z0-9-] survives the slug, so no quote or CRLF can reach the
        # unescaped `filename="..."` interpolation in `_send_file`.
        hostile = 'poster"; filename="pwned.html\r\nSet-Cookie: a=b'
        name = download_filename({"prompt": hostile, "mime": "image/svg+xml"})
        for bad in ('"', "\r", "\n", ";", "\\"):
            self.assertNotIn(bad, name)
        self.assertRegex(name, r"^[a-z0-9-]+\.svg$")

    def test_slug_is_capped_at_thirty_two_characters(self):
        name = download_filename({"prompt": "z" * 80, "mime": "image/png"})
        self.assertEqual(name, "z" * 32 + ".png")

    def test_known_hole_non_ascii_brief_falls_back_to_the_hex_id(self):
        # A Chinese-only brief slugifies to nothing, so the round's own promise
        # ("slug, not hex") does not hold for CJK users.
        name = download_filename({"id": "abcdef012345ff", "prompt": "四宫格 海报", "mime": "image/svg+xml"})
        self.assertEqual(name, "abcdef012345.svg")
        name = download_filename({"id": "abcdef012345ff", "prompt": "   ", "mime": "image/png"})
        self.assertEqual(name, "abcdef012345.png")

    def test_truncation_does_not_leave_a_trailing_hyphen(self):
        name = download_filename({"prompt": "y" * 31 + " tail", "mime": "image/png"})
        self.assertEqual(name, "y" * 31 + ".png")
        self.assertFalse(Path(name).stem.endswith("-"))

    def test_known_hole_unknown_mime_yields_bin(self):
        self.assertEqual(download_filename({"prompt": "poster", "mime": "image/avif"}), "poster.bin")
        self.assertEqual(download_filename({"prompt": "poster", "mime": ""}), "poster.bin")

    def test_upload_filename_does_not_double_its_extension(self):
        self.assertEqual(
            download_filename({"prompt": "ref.svg", "mime": "image/svg+xml"}), "ref.svg"
        )

    def test_known_hole_same_brief_collides(self):
        a = download_filename({"id": "aaaa1111", "prompt": "navy mark", "mime": "image/png"})
        b = download_filename({"id": "bbbb2222", "prompt": "navy mark", "mime": "image/png"})
        self.assertEqual(a, b)


class PathConfinement(unittest.TestCase):
    """`safe_under` — the guard the artifact route leans on."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "arts"
        self.root.mkdir()
        (self.root / "ok.svg").write_text("<svg/>")

    def tearDown(self):
        self.tmp.cleanup()

    def test_file_inside_root_resolves(self):
        self.assertEqual(safe_under(self.root, self.root / "ok.svg"), (self.root / "ok.svg").resolve())

    def test_escape_and_absolute_paths_are_refused(self):
        self.assertIsNone(safe_under(self.root, self.root / ".." / "outside.svg"))
        self.assertIsNone(safe_under(self.root, Path("/etc/passwd")))

    def test_symlink_out_of_root_is_refused(self):
        secret = Path(self.tmp.name) / "secret.txt"
        secret.write_text("keys")
        link = self.root / "link.svg"
        link.symlink_to(secret)
        self.assertIsNone(safe_under(self.root, link))

    def test_directory_and_missing_file_are_refused(self):
        self.assertIsNone(safe_under(self.root, self.root))
        self.assertIsNone(safe_under(self.root, self.root / "gone.svg"))


class ArtifactRoute(unittest.TestCase):
    """`GET /api/artifacts/:id` over real HTTP."""

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

    def _get(self, path):
        try:
            with urllib.request.urlopen(self.base + path, timeout=15) as resp:
                return resp.status, resp.read(), resp.headers
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), exc.headers

    def _artifact(self, prompt="Queensland Legal Directory poster"):
        _, project = self._post("/api/projects", {"name": "R4"})
        _, thread = self._post(f"/api/projects/{project['id']}/threads", {"topic": "r4"})
        status, result = self._post(
            f"/api/threads/{thread['id']}/run", {"prompt": prompt, "provider": "demo"}
        )
        self.assertEqual(status, 200)
        return project, result["artifacts"][0]

    def test_plain_get_renders_inline_for_img_src(self):
        _, art = self._artifact()
        status, body, headers = self._get(f"/api/artifacts/{art['id']}")
        self.assertEqual(status, 200)
        self.assertIsNone(headers.get("Content-Disposition"))
        self.assertEqual(headers.get("Content-Type"), "image/svg+xml")
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(int(headers.get("Content-Length")), len(body))
        self.assertTrue(body.lstrip().startswith(b"<svg"))

    def test_download_flag_sends_the_brief_slug_as_an_attachment(self):
        _, art = self._artifact()
        status, _, headers = self._get(f"/api/artifacts/{art['id']}?download=1")
        self.assertEqual(status, 200)
        disp = headers.get("Content-Disposition", "")
        self.assertEqual(disp, 'attachment; filename="queensland-legal-directory-poste.svg"')
        self.assertNotIn(art["id"], disp)
        self.assertEqual(disp.count('"'), 2)
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        expected = download_filename(self.server.get_app().memory.get_artifact(art["id"]))
        self.assertIn(f'filename="{expected}"', disp)

    def test_truthy_spellings_of_the_download_flag(self):
        _, art = self._artifact()
        for value in ("1", "true", "yes", "on", "True", "YES", "ON"):
            _, _, headers = self._get(f"/api/artifacts/{art['id']}?download={value}")
            self.assertIn("attachment", headers.get("Content-Disposition", ""), value)
        for value in ("0", "false", ""):
            _, _, headers = self._get(f"/api/artifacts/{art['id']}?download={value}")
            self.assertIsNone(headers.get("Content-Disposition"), value)

    def test_missing_artifact_is_a_json_404(self):
        status, body, headers = self._get("/api/artifacts/deadbeef")
        self.assertEqual(status, 404)
        self.assertEqual(json.loads(body)["error"], "missing artifact")

    def test_row_pointing_outside_the_artifacts_root_is_refused(self):
        app = self.server.get_app()
        _, project = self._post("/api/projects", {"name": "escape"})
        art = app.memory.add_artifact(
            project_id=project["id"],
            kind="image",
            path="/etc/passwd",
            mime="image/svg+xml",
            prompt="escape",
        )
        status, body, _ = self._get(f"/api/artifacts/{art['id']}")
        self.assertEqual(status, 404)
        self.assertEqual(json.loads(body)["error"], "not found")
        status, _, _ = self._get(f"/api/artifacts/{art['id']}?download=1")
        self.assertEqual(status, 404)

    def test_symlink_inside_the_root_is_refused(self):
        app = self.server.get_app()
        secret = Path(self.tmp.name) / "keyring-copy.json"
        secret.write_text('{"openai": "sk-live"}')
        link = Path(app.artifacts) / "sneak.svg"
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(secret)
        _, project = self._post("/api/projects", {"name": "symlink"})
        art = app.memory.add_artifact(
            project_id=project["id"],
            kind="image",
            path=str(link),
            mime="image/svg+xml",
            prompt="sneak",
        )
        status, body, _ = self._get(f"/api/artifacts/{art['id']}")
        self.assertEqual(status, 404)
        self.assertNotIn(b"sk-live", body)

    def test_dot_segments_in_the_stored_path_are_refused(self):
        app = self.server.get_app()
        _, project = self._post("/api/projects", {"name": "dots"})
        art = app.memory.add_artifact(
            project_id=project["id"],
            kind="image",
            path=str(Path(app.artifacts) / ".." / ".." / "etc" / "hosts"),
            mime="image/svg+xml",
            prompt="dots",
        )
        status, _, _ = self._get(f"/api/artifacts/{art['id']}")
        self.assertEqual(status, 404)

    def test_known_hole_no_head_no_range_no_cache_validators(self):
        _, art = self._artifact()
        req = urllib.request.Request(f"{self.base}/api/artifacts/{art['id']}", method="HEAD")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, timeout=10)
        self.assertEqual(ctx.exception.code, 501)
        _, _, headers = self._get(f"/api/artifacts/{art['id']}")
        for absent in ("ETag", "Last-Modified", "Cache-Control", "Accept-Ranges"):
            self.assertIsNone(headers.get(absent), absent)

    def test_inline_svg_carries_a_script_blocking_csp(self):
        _, project = self._post("/api/projects", {"name": "svg"})
        payload = base64.b64encode(
            b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>"
        ).decode()
        status, uploaded = self._post(
            f"/api/projects/{project['id']}/upload",
            {"filename": "evil.svg", "mime": "image/svg+xml", "data": payload},
        )
        self.assertEqual(status, 201)
        status, body, headers = self._get(f"/api/artifacts/{uploaded['artifact']['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Content-Type"), "image/svg+xml")
        self.assertIsNone(headers.get("Content-Disposition"))
        self.assertIn("default-src 'none'", headers.get("Content-Security-Policy", ""))
        self.assertIn(b"<script>", body)

    def test_export_zip_sends_nosniff(self):
        project, _ = self._artifact()
        status, body, headers = self._get(f"/api/projects/{project['id']}/export")
        self.assertEqual(status, 200)
        self.assertEqual(body[:2], b"PK")
        self.assertIn("attachment", headers.get("Content-Disposition", ""))
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")


class WebWiring(unittest.TestCase):
    def test_board_uses_inline_src_and_a_separate_download_link(self):
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('src: `/api/artifacts/${node.artifact_id}`', app_js)
        self.assertIn('href: `/api/artifacts/${node.artifact_id}?download=1`', app_js)

    def test_server_sends_nosniff_and_confines_the_artifact_path(self):
        server = SERVER_PY.read_text(encoding="utf-8")
        self.assertIn('handler.send_header("X-Content-Type-Options", "nosniff")', server)
        self.assertIn('safe_under(app.artifacts, Path(art["path"]))', server)
        self.assertIn("download_name=name if force else None", server)


if __name__ == "__main__":
    unittest.main()
