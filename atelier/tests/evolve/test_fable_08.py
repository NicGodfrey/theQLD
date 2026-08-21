#!/usr/bin/env python3
"""Fable-08 — Round 15 (host-pin) verification.

Official providers only talk to official hosts. Credentialed POSTs never
follow redirects. Unauthenticated OpenAI image GETs are still host-pinned
and refuse loopback / RFC1918.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
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

    def test_blocked_fetch_hosts(self):
        for host in ("127.0.0.1", "localhost", "10.0.0.5", "192.168.1.8", "169.254.169.254", "172.16.0.1"):
            self.assertTrue(is_blocked_fetch_host(host), host)
        self.assertFalse(is_blocked_fetch_host("oaidalleapiprodscus.blob.core.windows.net"))
        self.assertFalse(is_blocked_fetch_host("files.oaiusercontent.com"))


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
        ring.put("openai", key="sk-testkey-abcdefghijk", base_url="https://api.openai.com")
        ring.put("ollama", key="", base_url="http://127.0.0.1:11434")
        ring.put("openai_compat", key="sk-x", base_url="https://example.com/v1")
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


class ImageFetchPin(unittest.TestCase):
    def test_download_refuses_private_and_foreign(self):
        for url in (
            "file:///etc/passwd",
            "http://example.com/x.png",
            "https://127.0.0.1/x.png",
            "https://169.254.169.254/latest/meta-data",
            "https://evil.example/x.png",
        ):
            with self.assertRaises(SpokeError, msg=url):
                _download(url)

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


if __name__ == "__main__":
    unittest.main()
