#!/usr/bin/env python3
"""Fable-04 — Round 7 (visible plan) verification.

Pins the dock plan card, clickable weave steps, a separate critic card, and
the assistant-message `plan` blob over real HTTP.
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


class PlanWiring(unittest.TestCase):
    def test_plan_card_has_clickable_steps_and_a_critic(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        css = (WEB / "styles.css").read_text(encoding="utf-8")
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="planCard"', html)
        self.assertIn("function renderPlan(plan)", app_js)
        self.assertIn("class: \"plan-step\"", app_js)
        self.assertIn("classList.toggle(\"done\")", app_js)
        self.assertIn("class: \"plan-critic\"", app_js)
        self.assertIn(".plan-step.done", css)
        self.assertIn(".plan-critic", css)
        # the card must render on both entry points: right after a run and on
        # every message refresh (rehydrated from the stored assistant plan)
        self.assertIn("renderPlan(result.plan)", app_js)
        self.assertIn("renderPlan(lastPlan)", app_js)
        self.assertIn("if (m.plan) lastPlan = m.plan;", app_js)
        # dock card caps at four weave steps
        self.assertIn("weave.slice(0, 4)", app_js)
        # step click loads the step prompt into the composer, never innerHTML
        self.assertIn('document.getElementById("prompt")', app_js)
        self.assertIn("box.value = w.prompt || \"\";", app_js)


class PlanRoute(unittest.TestCase):
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
        with urllib.request.urlopen(self.base + path, timeout=15) as resp:
            return resp.status, json.loads(resp.read())

    def test_thinking_run_stores_plan_and_critique_on_the_message(self):
        _, project = self._post("/api/projects", {"name": "R7"})
        _, thread = self._post(f"/api/projects/{project['id']}/threads", {"topic": "r7"})
        status, result = self._post(
            f"/api/threads/{thread['id']}/run",
            {"prompt": "directory poster", "provider": "demo", "mode": "thinking"},
        )
        self.assertEqual(status, 200)
        self.assertIn("intent", result["plan"])
        self.assertTrue(result["plan"].get("weave"))
        self.assertTrue((result["plan"].get("critique") or "").strip())
        _, payload = self._get(f"/api/threads/{thread['id']}/messages")
        assistant = [m for m in payload["messages"] if m["role"] == "assistant"][-1]
        self.assertTrue(assistant.get("plan"))
        self.assertEqual(assistant["plan"].get("intent"), result["plan"].get("intent"))
        # the critique must survive the round-trip so a page refresh still
        # shows the .plan-critic card, not just the immediate run response
        self.assertEqual(assistant["plan"].get("critique"), result["plan"].get("critique"))
        route = assistant["plan"].get("route") or {}
        self.assertEqual(route.get("provider"), "demo")
        self.assertTrue(assistant["plan"].get("weave"))

    def test_fast_run_stores_plan_without_forcing_a_critique(self):
        _, project = self._post("/api/projects", {"name": "R7-fast"})
        _, thread = self._post(f"/api/projects/{project['id']}/threads", {"topic": "r7f"})
        status, result = self._post(
            f"/api/threads/{thread['id']}/run",
            {"prompt": "fast logo pass", "provider": "demo", "mode": "fast"},
        )
        self.assertEqual(status, 200)
        self.assertIn("intent", result["plan"])
        self.assertTrue(result["plan"].get("weave"))
        _, payload = self._get(f"/api/threads/{thread['id']}/messages")
        assistant = [m for m in payload["messages"] if m["role"] == "assistant"][-1]
        self.assertTrue(assistant.get("plan"))
        self.assertEqual(assistant["plan"].get("mode"), "fast")
        # fast mode skips the critic phase; the dock must not fake one
        self.assertFalse((assistant["plan"].get("critique") or "").strip())


if __name__ == "__main__":
    unittest.main()
