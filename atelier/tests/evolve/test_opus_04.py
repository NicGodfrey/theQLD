#!/usr/bin/env python3
"""Opus-04 — Round 8 (4-up variants) verification.

Read-only over the live tree: exercises `_wants_variants`, the 2x2 board
offsets, the demo end-to-end 4-artifact weave, and the wiring from the web
checkbox through `POST /api/threads/:id/run`. Also pins the known holes so a
later fix has to change a test on purpose.
"""

from __future__ import annotations

import json
import re
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

from atelier.helix.conductor import (  # noqa: E402
    Conductor,
    ConductorError,
    _wants_variants,
    next_board_offset,
)
from atelier.helix.keyring import Keyring  # noqa: E402
from atelier.helix.spokes.base import DemoSpoke, SpokeError  # noqa: E402
from atelier.helix.store import Memory  # noqa: E402

WEB = ROOT / "atelier" / "web"
SERVER_PY = ROOT / "atelier" / "server.py"


class FlakyImageSpoke:
    """Paid lane that only succeeds on the variants listed in `ok_variants`."""

    def __init__(self, ok_variants=(1, 3)):
        self.ok_variants = set(ok_variants)

    def chat(self, messages, model="", **kwargs):
        return DemoSpoke().chat(messages, model=model or "demo-conductor", **kwargs)

    def image(self, prompt, model="", **kwargs):
        match = re.search(r"variant (\d+)", prompt or "")
        index = int(match.group(1)) if match else 1
        if index not in self.ok_variants:
            raise SpokeError(f"quota exceeded on {model or 'gpt-image-1'}")
        return DemoSpoke().image(prompt, model=model, **kwargs)


class VariantsIntent(unittest.TestCase):
    """`_wants_variants` — the single gate for the whole round."""

    def test_explicit_count_clamped_to_two_through_four(self):
        self.assertEqual(_wants_variants("mark", 4), 4)
        self.assertEqual(_wants_variants("mark", 2), 2)
        self.assertEqual(_wants_variants("mark", 3), 3)
        self.assertEqual(_wants_variants("mark", 9), 4)
        self.assertEqual(_wants_variants("mark", 1), 0)
        self.assertEqual(_wants_variants("mark", 0), 0)

    def test_prompt_phrases_imply_four(self):
        for prompt in (
            "give me a 4-up board",
            "four variants of a navy mark",
            "4 variants please",
            "四宫格 logo",
            "四个变体",
            "variants of the poster",
        ):
            self.assertEqual(_wants_variants(prompt, 0), 4, prompt)

    def test_plain_prompt_stays_single(self):
        self.assertEqual(_wants_variants("a calm navy poster", 0), 0)

    def test_known_hole_negated_prompt_still_fans_out(self):
        # "variants" is matched as a bare substring, so a refusal reads as a request.
        self.assertEqual(_wants_variants("no variants please, just one", 0), 4)


class BoardOffsets(unittest.TestCase):
    def test_grid_two_lays_out_a_2x2_block(self):
        coords = [next_board_offset(i, grid=2) for i in range(4)]
        self.assertEqual(coords, [(72, 72), (432, 72), (72, 352), (432, 352)])
        self.assertEqual(len(set(coords)), 4)

    def test_grid_argument_coerces_to_two_or_three(self):
        self.assertEqual(next_board_offset(2, grid=5), next_board_offset(2, grid=3))
        self.assertEqual(next_board_offset(2, grid=0), next_board_offset(2, grid=3))


class FourUpWeave(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.mem = Memory(root / "t.sqlite")
        self.ring = Keyring(root / "keys.json")
        self.arts = root / "arts"
        self.arts.mkdir()
        self.project = self.mem.create_project("Round8")
        self.thread = self.mem.create_thread(self.project["id"])
        self.cond = Conductor(self.mem, self.ring, self.arts)

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def _run(self, prompt="navy wordmark", **kwargs):
        return self.cond.run(
            project_id=self.project["id"],
            thread_id=self.thread["id"],
            prompt=prompt,
            provider=kwargs.pop("provider", "demo"),
            **kwargs,
        )

    def test_four_artifacts_land_on_disk_and_on_the_board(self):
        result = self._run(variants=4)
        self.assertEqual(len(result["artifacts"]), 4)
        self.assertEqual(result["plan"]["variants"], 4)
        for art in result["artifacts"]:
            blob = Path(art["path"])
            self.assertTrue(blob.exists(), art["path"])
            self.assertGreater(blob.stat().st_size, 0)
        nodes = self.mem.list_nodes(self.project["id"])
        self.assertEqual(len(nodes), 4)
        self.assertEqual(
            sorted((n["x"], n["y"]) for n in nodes),
            [(72, 72), (72, 352), (432, 72), (432, 352)],
        )
        self.assertEqual(len({n["artifact_id"] for n in nodes}), 4)

    def test_each_variant_gets_its_own_prompt_suffix(self):
        result = self._run(variants=4)
        suffixes = sorted(a["prompt"][-len("variant 1"):] for a in result["artifacts"])
        self.assertEqual(suffixes, ["variant 1", "variant 2", "variant 3", "variant 4"])

    def test_quote_prices_all_four_images_before_the_weave(self):
        result = self._run(variants=4)
        quote_events = [e for e in result["events"] if e["kind"] == "quote"]
        self.assertEqual(len(quote_events), 1)
        self.assertEqual(quote_events[0]["quote"]["count"], 4)
        self.assertEqual(result["plan"]["quote"]["count"], 4)

    def test_prompt_alone_triggers_the_fan_out(self):
        result = self._run(prompt="four variants of a navy mark")
        self.assertEqual(len(result["artifacts"]), 4)
        self.assertEqual(result["plan"]["variants"], 4)

    def test_request_for_nine_is_capped_at_four(self):
        result = self._run(variants=9)
        self.assertEqual(len(result["artifacts"]), 4)
        self.assertEqual(len(self.mem.list_nodes(self.project["id"])), 4)

    def test_summary_names_the_variant_count(self):
        result = self._run(variants=4)
        self.assertIn("Variants: 4", result["message"])
        self.assertIn("Pinned 4 artifact(s)", result["message"])

    def test_paid_lane_failure_mints_nothing(self):
        def factory(provider, keyring):
            return DemoSpoke() if provider == "demo" else FlakyImageSpoke(ok_variants=())

        with mock.patch("atelier.helix.conductor.build_spoke", side_effect=factory):
            with self.assertRaises(ConductorError):
                self._run(provider="openai", variants=4)
        rows = self.mem.conn.execute("SELECT id FROM artifacts").fetchall()
        self.assertEqual(len(rows), 0)

    def test_known_hole_partial_failure_collapses_the_grid(self):
        # Two of four succeed: the plan still claims 4, and the survivors
        # compact onto row 0 instead of leaving holes in the 2x2.
        def factory(provider, keyring):
            return DemoSpoke() if provider == "demo" else FlakyImageSpoke(ok_variants=(1, 3))

        with mock.patch("atelier.helix.conductor.build_spoke", side_effect=factory):
            result = self._run(provider="openai", variants=4)
        self.assertEqual(len(result["artifacts"]), 2)
        self.assertEqual(result["plan"]["variants"], 4)
        self.assertIn("Pinned 2 artifact(s)", result["message"])
        nodes = self.mem.list_nodes(self.project["id"])
        self.assertEqual(sorted((n["x"], n["y"]) for n in nodes), [(72, 72), (432, 72)])

    def test_known_hole_second_four_up_is_not_a_2x2_block(self):
        # Offsets continue from the board's node count, so a 4-up on a board
        # holding an odd number of nodes straddles three rows.
        self.mem.add_node(project_id=self.project["id"], type="text", text="brief")
        result = self._run(variants=4)
        self.assertEqual(len(result["artifacts"]), 4)
        fresh = [n for n in self.mem.list_nodes(self.project["id"]) if n["type"] == "image"]
        rows = {n["y"] for n in fresh}
        self.assertEqual(len(rows), 3)

    def test_known_hole_no_pick_winner_linkage(self):
        result = self._run(variants=4)
        for art in result["artifacts"]:
            self.assertIsNone(art["parent_id"])
        for node in self.mem.list_nodes(self.project["id"]):
            self.assertEqual(node["meta"], {})
        self.assertNotIn("winner", result["plan"])


class WebAndServerWiring(unittest.TestCase):
    def test_checkbox_exists_and_posts_four(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        self.assertRegex(html, r'<input type="checkbox" id="variants">\s*4-up variants')
        app_js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('variants: document.getElementById("variants").checked ? 4 : 0', app_js)

    def test_run_and_quote_routes_read_the_field(self):
        server = SERVER_PY.read_text(encoding="utf-8")
        self.assertIn("as_int(body.get(\"variants\")", server)
        self.assertIn("as_int(body.get(\"count\")", server)

    def test_known_hole_no_pick_winner_endpoint(self):
        server = SERVER_PY.read_text(encoding="utf-8")
        for token in ("winner", "/pick", "promote"):
            self.assertNotIn(token, server, f"unexpected {token} route — update HARDEN.md")


class LiveRunRoute(unittest.TestCase):
    """`POST /api/threads/:id/run` with the checkbox on."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        with mock.patch.dict("os.environ", {"ATELIER_RUNTIME": cls.tmp.name}):
            from atelier import server as server_module

            cls.server_module = server_module
            server_module.reset_app()
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server_module.Handler)
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.thread.join(timeout=5)
        cls.server_module.APP.memory.close()
        cls.tmp.cleanup()

    def _post(self, path, body):
        req = urllib.request.Request(
            self.base + path,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def _get(self, path):
        with urllib.request.urlopen(self.base + path) as resp:
            return resp.status, json.loads(resp.read())

    def _thread(self):
        _, project = self._post("/api/projects", {"name": "R8 live"})
        _, thread = self._post(f"/api/projects/{project['id']}/threads", {"topic": "4up"})
        return project, thread

    def test_checkbox_payload_pins_four_and_quotes_four(self):
        project, thread = self._thread()
        status, quote = self._post(
            "/api/quote", {"provider": "demo", "prompt": "navy mark", "variants": 4}
        )
        self.assertEqual(status, 200)
        self.assertEqual(quote["count"], 4)
        status, result = self._post(
            f"/api/threads/{thread['id']}/run",
            {"prompt": "navy mark", "provider": "demo", "model": "", "variants": 4},
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(result["artifacts"]), 4)
        _, board = self._get(f"/api/projects/{project['id']}/board")
        self.assertEqual(
            sorted((n["x"], n["y"]) for n in board["nodes"]),
            [(72, 72), (72, 352), (432, 72), (432, 352)],
        )
        for art in result["artifacts"]:
            with urllib.request.urlopen(f"{self.base}/api/artifacts/{art['id']}") as resp:
                self.assertEqual(resp.status, 200)
                self.assertGreater(len(resp.read()), 0)

    def test_unchecked_box_stays_single(self):
        _, thread = self._thread()
        status, result = self._post(
            f"/api/threads/{thread['id']}/run",
            {"prompt": "navy mark", "provider": "demo", "variants": 0},
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(result["artifacts"]), 1)
        self.assertNotIn("variants", result["plan"])

    def test_non_numeric_variants_is_ignored_not_500(self):
        _, thread = self._thread()
        status, body = self._post(
            f"/api/threads/{thread['id']}/run",
            {"prompt": "navy mark", "provider": "demo", "variants": "four"},
        )
        self.assertEqual(status, 200)
        self.assertTrue(body.get("ok"))
        self.assertEqual(len(body["artifacts"]), 1)


if __name__ == "__main__":
    unittest.main()
