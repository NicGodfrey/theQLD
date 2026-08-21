#!/usr/bin/env python3
"""ROUND 16 verification (opus-08): budget pre-call gate + HTTP 402.

Read-only over the live tree: asserts the shipped behaviour of
`usage.assert_budget`, `quote_run(...)["would_exceed"]`, the conductor
pre-call gate, and the server's 402 `budget_exceeded` mapping.
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
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix import usage
from atelier.helix.conductor import Conductor
from atelier.helix.keyring import Keyring
from atelier.helix.quote import quote_run
from atelier.helix.spokes.base import ChatResult, DemoSpoke, ImageResult
from atelier.helix.store import Memory


def _mem(tmp: Path) -> tuple[Memory, Keyring, Path]:
    mem = Memory(tmp / "t.sqlite")
    ring = Keyring(tmp / "keys.json")
    arts = tmp / "arts"
    arts.mkdir(exist_ok=True)
    return mem, ring, arts


class _MemCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mem, self.ring, self.arts = _mem(Path(self.tmp.name))
        self.project = self.mem.create_project("Budget")
        self.thread = self.mem.create_thread(self.project["id"])

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def _spend(self, usd: float, *, thread: bool = True, unit_kind: str = "images") -> None:
        self.mem.add_usage(
            provider="openai",
            model="gpt-image-1",
            unit_kind=unit_kind,
            units=1,
            estimated_usd=usd,
            thread_id=self.thread["id"] if thread else None,
        )


class AssertBudget(_MemCase):
    def test_daily_and_thread_ceilings_raise(self):
        self._spend(usage.DAILY_BUDGET_USD + 0.01, thread=False)
        with self.assertRaises(usage.BudgetExceeded) as ctx:
            usage.assert_budget(self.mem)
        self.assertIn("daily budget", str(ctx.exception))

        thread_only, _, _ = _mem(Path(self.tmp.name) / "b")
        with self.assertRaises(usage.BudgetExceeded) as ctx:
            usage.assert_budget(
                thread_only,
                thread_id="t",
                extra_usd=usage.THREAD_BUDGET_USD + 0.01,
            )
        self.assertIn("thread budget", str(ctx.exception))
        thread_only.close()

    def test_ceiling_is_strict_greater_than(self):
        """Spending exactly to the ceiling is allowed; one cent past is not."""
        self._spend(usage.DAILY_BUDGET_USD, thread=False)
        usage.assert_budget(self.mem)
        with self.assertRaises(usage.BudgetExceeded):
            usage.assert_budget(self.mem, extra_usd=0.01)

    def test_extra_usd_is_counted_before_the_spend(self):
        self._spend(usage.THREAD_BUDGET_USD - 0.02)
        usage.assert_budget(self.mem, thread_id=self.thread["id"])
        with self.assertRaises(usage.BudgetExceeded):
            usage.assert_budget(self.mem, thread_id=self.thread["id"], extra_usd=0.05)


class QuoteWouldExceed(_MemCase):
    def test_thread_budget_sets_would_exceed_and_reason(self):
        self._spend(usage.THREAD_BUDGET_USD - 0.01)
        q = quote_run(
            provider="openai",
            model="gpt-4o-mini",
            prompt="a navy logo",
            memory=self.mem,
            thread_id=self.thread["id"],
        )
        self.assertTrue(q["would_exceed"])
        self.assertIn("thread budget", q["reason"])
        self.assertEqual(q["thread_budget_usd"], usage.THREAD_BUDGET_USD)

    def test_clean_ledger_does_not_flag(self):
        q = quote_run(
            provider="openai",
            model="gpt-4o-mini",
            prompt="a navy logo",
            memory=self.mem,
            thread_id=self.thread["id"],
        )
        self.assertFalse(q["would_exceed"])
        self.assertEqual(q["reason"], "")
        self.assertGreater(q["estimated_usd"], 0)

    def test_unpriced_model_gates_on_conservative_hold(self):
        """Unknown model → priced False and the gate uses the conservative hold."""
        self._spend(usage.THREAD_BUDGET_USD - 0.02)
        q = quote_run(
            provider="openai",
            model="gpt-mystery-9",
            prompt="x",
            count=1,
            memory=self.mem,
            thread_id=self.thread["id"],
        )
        self.assertFalse(q["priced"])
        self.assertEqual(q["conservative_usd"], round(0.04 * 1 + 0.01, 6))
        self.assertEqual(q["estimated_usd"], q["conservative_usd"])
        self.assertTrue(q["would_exceed"])

    def test_free_lanes_are_never_gated(self):
        self._spend(usage.DAILY_BUDGET_USD * 5, thread=False)
        for provider in ("demo", "ollama"):
            q = quote_run(
                provider=provider,
                prompt="free",
                memory=self.mem,
                thread_id=self.thread["id"],
            )
            self.assertFalse(q["would_exceed"], provider)
            self.assertEqual(q["estimated_usd"], 0.0, provider)

    def test_quote_without_memory_cannot_gate(self):
        """/api/quote must pass memory; a memory-less quote always reads clean."""
        q = quote_run(provider="openai", model="gpt-4o-mini", prompt="x")
        self.assertFalse(q["would_exceed"])


class PreCallGate(_MemCase):
    def _run(self, spy, provider="openai"):
        cond = Conductor(self.mem, self.ring, self.arts)
        with mock.patch("atelier.helix.conductor.build_spoke", side_effect=spy):
            return cond.run(
                project_id=self.project["id"],
                thread_id=self.thread["id"],
                prompt="navy logo",
                provider=provider,
            )

    def test_no_spoke_is_built_when_the_quote_would_exceed(self):
        self._spend(usage.THREAD_BUDGET_USD + 0.5)
        built: list[str] = []

        def spy(provider, keyring):
            built.append(provider)
            return DemoSpoke()

        with self.assertRaises(usage.BudgetExceeded):
            self._run(spy)

        self.assertEqual(built, [], "spoke was constructed after the budget gate")
        rows = self.mem.conn.execute("SELECT COUNT(*) FROM artifacts").fetchone()
        self.assertEqual(rows[0], 0)
        nodes = self.mem.list_nodes(self.project["id"])
        self.assertEqual(nodes, [])

    def test_quote_event_is_emitted_before_the_raise(self):
        self._spend(usage.THREAD_BUDGET_USD + 0.5)
        seen: list[dict] = []
        cond = Conductor(self.mem, self.ring, self.arts)
        with mock.patch("atelier.helix.conductor.build_spoke", return_value=DemoSpoke()):
            with self.assertRaises(usage.BudgetExceeded):
                cond.run(
                    project_id=self.project["id"],
                    thread_id=self.thread["id"],
                    prompt="navy logo",
                    provider="openai",
                    on_event=seen.append,
                )
        quotes = [e for e in seen if e["kind"] == "quote"]
        self.assertEqual(len(quotes), 1)
        self.assertTrue(quotes[0]["quote"]["would_exceed"])

    def test_demo_lane_still_weaves_over_budget(self):
        self._spend(usage.DAILY_BUDGET_USD * 3, thread=False)
        result = self._run(lambda provider, keyring: DemoSpoke(), provider="demo")
        self.assertTrue(result["ok"])
        self.assertTrue(result["artifacts"])

    def test_paid_lane_is_blocked_by_the_shared_daily_ledger(self):
        """Daily spend from any thread blocks a paid run on a clean thread."""
        self._spend(usage.DAILY_BUDGET_USD + 1, thread=False)
        with self.assertRaises(usage.BudgetExceeded) as ctx:
            self._run(lambda provider, keyring: DemoSpoke())
        self.assertIn("daily budget", str(ctx.exception))


class TwoImagePlanSpoke:
    """Planner that asks for two images — the pre-call quote only priced one."""

    def chat(self, messages, model="", **kwargs):
        plan = {
            "mode": "fast",
            "intent": "two marks",
            "route": {"provider": "openai", "model": "gpt-4o-mini", "capability": "image"},
            "weave": [
                {"kind": "image", "prompt": "mark one", "count": 1},
                {"kind": "image", "prompt": "mark two", "count": 1},
            ],
        }
        return ChatResult(
            text=json.dumps(plan), provider="openai", model="gpt-4o-mini", tokens_in=0, tokens_out=0
        )

    def image(self, prompt, model="", **kwargs):
        return ImageResult(
            data=b"<svg xmlns='http://www.w3.org/2000/svg'></svg>",
            mime="image/svg+xml",
            provider="openai",
            model="gpt-image-1",
            prompt=prompt,
        )


class MidRunHole(_MemCase):
    def test_multi_item_plan_is_requoted_before_weave(self):
        """Re-quote after the plan so a 2-image weave cannot sneak past a 1-image hold."""
        self._spend(usage.THREAD_BUDGET_USD - 0.05, unit_kind="tokens_out")
        cond = Conductor(self.mem, self.ring, self.arts)
        with mock.patch(
            "atelier.helix.conductor.build_spoke", return_value=TwoImagePlanSpoke()
        ):
            with self.assertRaises(usage.BudgetExceeded):
                cond.run(
                    project_id=self.project["id"],
                    thread_id=self.thread["id"],
                    prompt="two marks",
                    provider="openai",
                )
        images = self.mem.conn.execute(
            "SELECT COUNT(*) FROM artifacts WHERE kind='image'"
        ).fetchone()[0]
        billed = self.mem.conn.execute(
            "SELECT COUNT(*) FROM usage_events WHERE unit_kind='images'"
        ).fetchone()[0]
        self.assertEqual(images, 0)
        self.assertEqual(billed, 0)


class LedgerHole(_MemCase):
    def test_record_drops_the_row_it_was_asked_to_write(self):
        """Hole: `usage.record` gates *after* the provider call already happened.

        The exception aborts `memory.add_usage`, so real spend that pushed the
        ledger over the ceiling is never written down.
        """
        self._spend(usage.THREAD_BUDGET_USD - 0.001)
        before = self.mem.conn.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
        with self.assertRaises(usage.BudgetExceeded):
            usage.record(
                self.mem,
                provider="openai",
                model="gpt-image-1",
                unit_kind="images",
                units=10,
                thread_id=self.thread["id"],
            )
        after = self.mem.conn.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
        self.assertEqual(before, after)


class Http402(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["ATELIER_RUNTIME"] = str(Path(self.tmp.name) / "rt")
        os.environ["ATELIER_HOME"] = str(Path(self.tmp.name) / "home")
        from atelier import server

        self.server_mod = server
        server.reset_app()
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.tmp.cleanup()

    def _req(self, method: str, path: str, body: dict | None = None, query: str = ""):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}{query}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode()
                ctype = resp.headers.get("Content-Type", "")
                payload = json.loads(raw) if raw and "json" in ctype else {"raw": raw}
                return resp.status, payload, resp.headers
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode()
            try:
                payload = json.loads(raw)
            except Exception:
                payload = {"raw": raw}
            return exc.code, payload, exc.headers

    def _ids(self):
        _, data, _ = self._req("GET", "/api/projects")
        pid = data["projects"][0]["id"]
        _, threads, _ = self._req("GET", f"/api/projects/{pid}/threads")
        return pid, threads["threads"][0]["id"]

    def _burn(self, tid: str, usd: float):
        self.server_mod.get_app().memory.add_usage(
            provider="openai",
            model="gpt-image-1",
            unit_kind="images",
            units=1,
            estimated_usd=usd,
            thread_id=tid,
        )

    def test_run_over_budget_returns_402_budget_exceeded(self):
        pid, tid = self._ids()
        self._burn(tid, usage.THREAD_BUDGET_USD + 1)
        code, payload, _ = self._req(
            "POST", f"/api/threads/{tid}/run", {"prompt": "paid", "provider": "openai"}
        )
        self.assertEqual(code, 402)
        self.assertEqual(payload.get("code"), "budget_exceeded")
        self.assertFalse(payload.get("ok"))
        self.assertIn("budget", payload.get("error", ""))

        _, board, _ = self._req("GET", f"/api/projects/{pid}/board")
        self.assertEqual(board["nodes"], [])

    def test_stream_run_also_402s_instead_of_opening_sse(self):
        _, tid = self._ids()
        self._burn(tid, usage.THREAD_BUDGET_USD + 1)
        code, payload, headers = self._req(
            "POST",
            f"/api/threads/{tid}/run",
            {"prompt": "paid", "provider": "openai"},
            query="?stream=1",
        )
        self.assertEqual(code, 402)
        self.assertEqual(payload.get("code"), "budget_exceeded")
        self.assertNotIn("text/event-stream", headers.get("Content-Type", ""))

    def test_quote_endpoint_reports_the_same_verdict(self):
        _, tid = self._ids()
        self._burn(tid, usage.THREAD_BUDGET_USD + 1)
        code, quote, _ = self._req(
            "POST",
            "/api/quote",
            {"provider": "openai", "model": "gpt-4o-mini", "prompt": "logo", "thread_id": tid},
        )
        self.assertEqual(code, 200)
        self.assertTrue(quote["would_exceed"])

    def test_402_body_carries_no_quote_for_the_client(self):
        """Hole: the 402 payload has no estimate/remaining, only a message."""
        _, tid = self._ids()
        self._burn(tid, usage.THREAD_BUDGET_USD + 1)
        _, payload, _ = self._req(
            "POST", f"/api/threads/{tid}/run", {"prompt": "paid", "provider": "openai"}
        )
        self.assertNotIn("quote", payload)
        self.assertNotIn("estimated_usd", payload)


class UiGate(unittest.TestCase):
    """The Weave button has no client-side `would_exceed` check today."""

    def setUp(self):
        self.app_js = (ROOT / "atelier" / "web" / "app.js").read_text()
        start = self.app_js.index('getElementById("run").onclick')
        end = self.app_js.index('getElementById("undoBtn")')
        self.run_handler = self.app_js[start:end]

    def test_quote_button_surfaces_the_flag(self):
        self.assertIn("would_exceed", self.app_js)
        self.assertIn("would exceed budget", self.app_js)

    def test_weave_is_gated_client_side_or_by_the_server_402(self):
        client_gate = "would_exceed" in self.run_handler
        server_gate = "budget_exceeded" in (ROOT / "atelier" / "server.py").read_text()
        self.assertTrue(
            client_gate or server_gate,
            "neither the Weave button nor the server blocks an over-budget run",
        )

    def test_http_errors_reach_the_status_line(self):
        self.assertIn("err.status = res.status", self.app_js)
        self.assertIn("status.textContent = err.message", self.run_handler)


if __name__ == "__main__":
    unittest.main()
