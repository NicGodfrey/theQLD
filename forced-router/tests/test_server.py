from __future__ import annotations

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

from forced_router.config import load_config
from forced_router.server import handle_request, make_handler

ROOT = Path(__file__).resolve().parents[2]


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cfg = load_config(ROOT)

    def test_health(self) -> None:
        status, data, _ = handle_request("GET", "/health", None, self.cfg)
        self.assertEqual(status, 200)
        body = json.loads(data)
        self.assertTrue(body["ok"])
        self.assertEqual(body["forced_model"], "claude-fable-5-thinking-xhigh")

    def test_rewrite_endpoint(self) -> None:
        status, data, _ = handle_request(
            "POST", "/v1/rewrite", {"model": "auto", "messages": []}, self.cfg
        )
        self.assertEqual(status, 200)
        body = json.loads(data)
        self.assertEqual(body["original_model"], "auto")
        self.assertEqual(body["model"], "claude-fable-5-thinking-xhigh")

    def test_chat_completions_force(self) -> None:
        status, data, _ = handle_request(
            "POST",
            "/v1/chat/completions",
            {"model": "default", "messages": [{"role": "user", "content": "hi"}]},
            self.cfg,
        )
        self.assertEqual(status, 200)
        body = json.loads(data)
        self.assertTrue(body["rewritten"])
        self.assertEqual(body["model"], "claude-fable-5-thinking-xhigh")

    def test_cloud_agents_create(self) -> None:
        status, data, _ = handle_request(
            "POST", "/v1/agents", {"prompt": {"text": "hi"}}, self.cfg
        )
        body = json.loads(data)
        self.assertEqual(status, 200)
        self.assertEqual(body["model"]["id"], "claude-fable-5")

    def test_http_roundtrip(self) -> None:
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.cfg, None))
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            port = httpd.server_address[1]
            req = Request(
                f"http://127.0.0.1:{port}/v1/chat/completions",
                data=json.dumps({"model": "auto"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(body["model"], "claude-fable-5-thinking-xhigh")
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main()
