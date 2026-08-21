#!/usr/bin/env python3
"""Fable-02 — Round 3 verification: progress events + ?stream=1 SSE.

Verifies, without touching live code:
  * conductor.run emits phase events brief → score → route → weave → pin → done
    (critique inserted before pin in thinking mode) plus a quote event, and
    forwards every event to on_event in the same order as result["events"].
  * POST /api/threads/:id/run?stream=1 answers text/event-stream whose frames
    replay the run events and end with a final `event: result` frame.
  * Documents the post-hoc flush: the server never passes on_event, so SSE
    bytes are written only after the sync run finishes (not mid-weave).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.conductor import Conductor
from atelier.helix.keyring import Keyring
from atelier.helix.store import Memory


def _mem(tmp: Path):
    mem = Memory(tmp / "t.sqlite")
    ring = Keyring(tmp / "keys.json")
    arts = tmp / "arts"
    arts.mkdir(exist_ok=True)
    return mem, ring, arts


def _parse_sse(raw: str) -> list[tuple[str, dict]]:
    frames = []
    for block in raw.split("\n\n"):
        if not block.strip():
            continue
        event, data = "message", ""
        for line in block.splitlines():
            if line.startswith("event: "):
                event = line[len("event: "):]
            elif line.startswith("data: "):
                data = line[len("data: "):]
        frames.append((event, json.loads(data)))
    return frames


class ConductorPhases(unittest.TestCase):
    def _run(self, prompt: str, mode: str = "fast"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        mem, ring, arts = _mem(Path(tmp.name))
        self.addCleanup(mem.close)
        project = mem.create_project("R3")
        thread = mem.create_thread(project["id"])
        seen: list[dict] = []
        result = Conductor(mem, ring, arts).run(
            project_id=project["id"],
            thread_id=thread["id"],
            prompt=prompt,
            provider="demo",
            mode=mode,
            on_event=seen.append,
        )
        return result, seen

    def test_fast_run_walks_all_round3_phases_in_order(self):
        result, seen = self._run("calm poster")
        phases = [e["phase"] for e in result["events"] if e["kind"] == "phase"]
        for phase in ("brief", "score", "route", "weave", "pin", "done"):
            self.assertIn(phase, phases)
        # brief first, done last, pin just before done
        self.assertEqual(phases[0], "brief")
        self.assertEqual(phases[-2:], ["pin", "done"])
        self.assertLess(phases.index("score"), phases.index("route"))
        self.assertLess(phases.index("route"), phases.index("weave"))
        # on_event received the exact same event stream, in order
        self.assertEqual(seen, result["events"])

    def test_quote_event_precedes_score_and_carries_estimate(self):
        result, _ = self._run("navy logo")
        kinds = [e["kind"] for e in result["events"]]
        self.assertIn("quote", kinds)
        quote_ev = next(e for e in result["events"] if e["kind"] == "quote")
        self.assertIn("estimated_usd", quote_ev["quote"])
        score_idx = next(
            i for i, e in enumerate(result["events"])
            if e["kind"] == "phase" and e["phase"] == "score"
        )
        self.assertLess(kinds.index("quote"), score_idx)

    def test_thinking_mode_adds_critique_phase_before_pin(self):
        result, _ = self._run("poster with rationale", mode="thinking")
        phases = [e["phase"] for e in result["events"] if e["kind"] == "phase"]
        self.assertIn("critique", phases)
        self.assertLess(phases.index("critique"), phases.index("pin"))

    def test_pin_events_reference_created_nodes(self):
        result, _ = self._run("single mark")
        pins = [e for e in result["events"] if e["kind"] == "pin"]
        self.assertGreaterEqual(len(pins), 1)
        node_ids = {n["id"] for n in result["nodes"]}
        for pin in pins:
            self.assertIn(pin["node_id"], node_ids)


class StreamEndpoint(unittest.TestCase):
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

    def _post(self, path: str, body: dict):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(body).encode(),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode(), dict(resp.headers)

    def _tid(self):
        with urllib.request.urlopen(
            f"http://127.0.0.1:{self.port}/api/projects", timeout=10
        ) as resp:
            pid = json.loads(resp.read())["projects"][0]["id"]
        with urllib.request.urlopen(
            f"http://127.0.0.1:{self.port}/api/projects/{pid}/threads", timeout=10
        ) as resp:
            return json.loads(resp.read())["threads"][0]["id"]

    def test_stream_1_replays_phases_then_result_frame(self):
        tid = self._tid()
        status, raw, headers = self._post(
            f"/api/threads/{tid}/run?stream=1", {"prompt": "sse mark", "provider": "demo"}
        )
        self.assertEqual(status, 200)
        self.assertIn("text/event-stream", headers.get("Content-Type", ""))
        frames = _parse_sse(raw)
        names = [name for name, _ in frames]
        self.assertIn("quote", names)
        phases = [data["phase"] for name, data in frames if name == "phase"]
        for phase in ("brief", "score", "route", "weave", "pin", "done"):
            self.assertIn(phase, phases)
        # the terminal frame is the full run result
        self.assertEqual(names[-1], "result")
        self.assertTrue(frames[-1][1].get("ok"))
        self.assertEqual(len(frames[-1][1]["events"]), len(frames) - 1)

    def test_stream_accepts_true_and_yes_spellings(self):
        tid = self._tid()
        for spelling in ("true", "yes"):
            _, raw, headers = self._post(
                f"/api/threads/{tid}/run?stream={spelling}",
                {"prompt": "alias", "provider": "demo"},
            )
            self.assertIn("text/event-stream", headers.get("Content-Type", ""))
            self.assertEqual(_parse_sse(raw)[-1][0], "result")

    def test_stream_0_returns_plain_json_with_events(self):
        tid = self._tid()
        status, raw, headers = self._post(
            f"/api/threads/{tid}/run?stream=0", {"prompt": "json mark", "provider": "demo"}
        )
        self.assertEqual(status, 200)
        self.assertIn("application/json", headers.get("Content-Type", ""))
        result = json.loads(raw)
        self.assertTrue(any(e["kind"] == "phase" for e in result["events"]))

    def test_documented_gap_server_flushes_events_after_sync_run(self):
        """The handler never wires on_event, so SSE frames are written only
        after conductor.run returns — a mid-weave observer sees nothing."""
        tid = self._tid()
        app = self.server_mod.get_app()
        real_run = app.conductor.run
        captured: dict = {}

        def spy(**kwargs):
            captured.update(kwargs)
            return real_run(**kwargs)

        with mock.patch.object(app.conductor, "run", side_effect=spy):
            self._post(
                f"/api/threads/{tid}/run?stream=1",
                {"prompt": "spy", "provider": "demo"},
            )
        self.assertIn("prompt", captured)
        self.assertIsNone(captured.get("on_event"))


if __name__ == "__main__":
    unittest.main()
