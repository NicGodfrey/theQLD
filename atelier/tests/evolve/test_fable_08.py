#!/usr/bin/env python3
"""Fable-08 — Round 15 (host-pin) verification.

Official providers only talk to official hosts. Credentialed POSTs never
follow redirects. Unauthenticated OpenAI image GETs are still host-pinned
and refuse loopback / RFC1918 / non-global IPs in any spelling.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.http import NoRedirectHandler, urlopen_no_redirect  # noqa: E402
from atelier.helix.keyring import Keyring  # noqa: E402
from atelier.helix.spokes.base import SpokeError, assert_official_host, is_blocked_fetch_host  # noqa: E402
from atelier.helix.spokes.gemini_spoke import GeminiSpoke  # noqa: E402
from atelier.helix.spokes.openai_spoke import IMAGE_FETCH_SUFFIXES, OpenAISpoke, _download  # noqa: E402


class HostPinUnit(unittest.TestCase):
    def test_official_host_suffix_and_https(self):
        assert_official_host("https://api.openai.com", ("api.openai.com",), require_https=True)
        assert_official_host("https://us.api.openai.com", ("api.openai.com",), require_https=True)
        with self.assertRaises(SpokeError):
            assert_official_host("https://chatgpt.com", ("api.openai.com",), require_https=True)
        with self.assertRaises(SpokeError):
            assert_official_host("http://api.openai.com", ("api.openai.com",), require_https=True)
        with self.assertRaises(SpokeError):
            assert_official_host("https://evil.example", ("generativelanguage.googleapis.com",))

    def test_official_host_rejects_lookalikes_and_tricks(self):
        # suffix must match on a label boundary
        with self.assertRaises(SpokeError):
            assert_official_host("https://notapi.openai.com", ("api.openai.com",), require_https=True)
        # userinfo trick: the real host is after the @
        with self.assertRaises(SpokeError):
            assert_official_host(
                "https://api.openai.com@evil.example/", ("api.openai.com",), require_https=True
            )
        # empty host
        with self.assertRaises(SpokeError):
            assert_official_host("https://", ("api.openai.com",), require_https=True)

    def test_blocked_fetch_hosts(self):
        blocked = (
            "127.0.0.1",
            "localhost",
            "10.0.0.5",
            "192.168.1.8",
            "169.254.169.254",
            "172.16.0.1",
            "0.0.0.0",
            "::1",
            # IPv6 mapped / unique-local / link-local
            "::ffff:127.0.0.1",
            "fd00::1",
            "fe80::1",
            # legacy IPv4 spellings the socket connector accepts
            "2130706433",
            "127.1",
            "0x7f.0.0.1",
        )
        for host in blocked:
            self.assertTrue(is_blocked_fetch_host(host), host)
        for host in (
            "oaidalleapiprodscus.blob.core.windows.net",
            "files.oaiusercontent.com",
            "8.8.8.8",
            "2606:4700::1111",
        ):
            self.assertFalse(is_blocked_fetch_host(host), host)


class KeyringPin(unittest.TestCase):
    def test_put_rejects_unofficial_and_http(self):
        tmp = tempfile.TemporaryDirectory()
        ring = Keyring(Path(tmp.name) / "k.json")
        with self.assertRaises(ValueError):
            ring.put("openai", key="sk-testkey-abcdefghijk", base_url="https://chatgpt.com")
        with self.assertRaises(ValueError):
            ring.put("openai", key="sk-testkey-abcdefghijk", base_url="http://api.openai.com")
        with self.assertRaises(ValueError):
            ring.put("gemini", key="AIza-test", base_url="https://evil.example")
        with self.assertRaises(ValueError):
            ring.put("ollama", base_url="http://evil.example:11434")
        ring.put("openai", key="sk-testkey-abcdefghijk", base_url="https://api.openai.com")
        ring.put("ollama", key="", base_url="http://127.0.0.1:11434")
        # openai_compat stays free-form by design (user-set host)
        ring.put("openai_compat", key="sk-x", base_url="https://example.com/v1")
        tmp.cleanup()

    def test_spoke_url_rechecks_a_tampered_keyring_file(self):
        """Even a base_url written straight into keyring.json is caught at _url."""
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / "k.json"
        ring = Keyring(path)
        ring.put("openai", key="sk-testkey-abcdefghijk")
        data = json.loads(path.read_text())
        data["providers"]["openai"]["base_url"] = "https://evil.example"
        data["providers"]["gemini"] = {
            "key": "k",
            "base_url": "http://generativelanguage.googleapis.com",
        }
        path.write_text(json.dumps(data))
        with self.assertRaises(SpokeError):
            OpenAISpoke(ring)._url("/v1/chat/completions")
        with self.assertRaises(SpokeError):
            GeminiSpoke(ring)._url("/v1beta/x")
        tmp.cleanup()


class RedirectPin(unittest.TestCase):
    def test_handler_returns_none(self):
        handler = NoRedirectHandler()
        self.assertIsNone(
            handler.redirect_request(None, None, 302, "Found", {}, "https://evil.example/steal")
        )

    def test_urlopen_maps_3xx_to_spoke_error(self):
        import io
        import urllib.error
        import urllib.request

        class FakeOpener:
            def open(self, req, timeout=120):
                raise urllib.error.HTTPError(
                    "https://api.openai.com/v1/x",
                    302,
                    "Found",
                    {"Location": "https://evil.example/steal"},
                    io.BytesIO(b""),
                )

        with mock.patch("atelier.helix.http.opener", return_value=FakeOpener()):
            with self.assertRaises(SpokeError) as ctx:
                urlopen_no_redirect(urllib.request.Request("https://api.openai.com/v1/x"))
        self.assertIn("redirect", str(ctx.exception).lower())
        self.assertIn("evil.example", str(ctx.exception))

    def test_live_302_is_refused_through_the_real_opener(self):
        """A real loopback server answers 302; the real handler chain must not follow."""
        import urllib.request

        class Redirector(BaseHTTPRequestHandler):
            hits = []

            def do_POST(self):
                Redirector.hits.append(self.path)
                self.send_response(302)
                self.send_header("Location", "https://evil.example/steal")
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *args):
                pass

        srv = ThreadingHTTPServer(("127.0.0.1", 0), Redirector)
        thread = threading.Thread(target=srv.serve_forever, daemon=True)
        thread.start()
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{srv.server_address[1]}/v1/chat/completions",
                data=b"{}",
                headers={"Authorization": "Bearer sk-test"},
                method="POST",
            )
            with self.assertRaises(SpokeError) as ctx:
                urlopen_no_redirect(req, timeout=5)
            self.assertIn("302", str(ctx.exception))
            self.assertIn("evil.example", str(ctx.exception))
            # exactly one request hit the server — nothing was replayed anywhere
            self.assertEqual(Redirector.hits, ["/v1/chat/completions"])
        finally:
            srv.shutdown()


class ImageFetchPin(unittest.TestCase):
    def test_download_refuses_private_and_foreign(self):
        for url in (
            "file:///etc/passwd",
            "http://example.com/x.png",
            "http://oaiusercontent.com/x.png",  # right host, wrong scheme
            "https://127.0.0.1/x.png",
            "https://10.0.0.5/x.png",
            "https://[::ffff:127.0.0.1]/x.png",
            "https://169.254.169.254/latest/meta-data",
            "https://evil.example/x.png",
            "https://evilopenai.com/x.png",  # suffix without a label boundary
            "https://openai.com.evil.example/x.png",  # official name as a prefix
        ):
            with self.assertRaises(SpokeError, msg=url):
                _download(url)

    def test_permitted_url_reaches_the_no_redirect_opener(self):
        """A CDN URL passes the pin and is fetched via urlopen_no_redirect (mocked)."""

        class FakeResp:
            class _Headers(dict):
                pass

            headers = _Headers({"Content-Type": "image/png; charset=binary"})

            def read(self):
                return b"\x89PNGfake"

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        seen = []

        def fake_open(req, timeout=120):
            seen.append(req.full_url)
            return FakeResp()

        url = "https://oaidalleapiprodscus.blob.core.windows.net/private/img.png?sig=x"
        # _download imports urlopen_no_redirect from atelier.helix.http at call time
        with mock.patch("atelier.helix.http.urlopen_no_redirect", side_effect=fake_open):
            data, mime = _download(url)
        self.assertEqual(seen, [url])
        self.assertEqual(data, b"\x89PNGfake")
        self.assertEqual(mime, "image/png")

    def test_openai_spoke_pins_before_post(self):
        tmp = tempfile.TemporaryDirectory()
        ring = Keyring(Path(tmp.name) / "k.json")
        os.environ.pop("OPENAI_API_KEY", None)
        ring.put("openai", key="sk-testkey-abcdefghijk", base_url="https://api.openai.com")
        spoke = OpenAISpoke(ring)
        with mock.patch.object(spoke, "_post", side_effect=AssertionError("must not post")):
            # host check happens in _url, before _post is reached from chat
            url = spoke._url("/v1/chat/completions")
            self.assertTrue(url.startswith("https://api.openai.com/"))
        gem = GeminiSpoke(ring)
        self.assertIn("generativelanguage.googleapis.com", gem._url("/v1beta/x"))
        tmp.cleanup()

    def test_image_cdn_suffixes_are_named(self):
        self.assertIn("blob.core.windows.net", IMAGE_FETCH_SUFFIXES)
        self.assertIn("oaiusercontent.com", IMAGE_FETCH_SUFFIXES)
        self.assertIn("api.openai.com", IMAGE_FETCH_SUFFIXES)
        self.assertIn("openai.com", IMAGE_FETCH_SUFFIXES)


class ImportOrder(unittest.TestCase):
    def test_http_before_spokes_in_a_fresh_interpreter(self):
        """http.py must not import spokes at module top level (circular import)."""
        code = (
            "import atelier.helix.http\n"
            "import atelier.helix.spokes.openai_spoke\n"
            "print('ok')\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "ok")


if __name__ == "__main__":
    unittest.main()
