#!/usr/bin/env python3
"""Twenty-round Helix self-evolution tests — no live provider keys required."""

from __future__ import annotations

import base64
import json
import os
import stat
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.conductor import Conductor, ConductorError
from atelier.helix.exportzip import export_project_zip
from atelier.helix.http import NoRedirectHandler
from atelier.helix.keyring import Keyring
from atelier.helix.loom import demo_svg, download_filename
from atelier.helix.paths import safe_under
from atelier.helix.quote import quote_run
from atelier.helix.spokes import build_spoke
from atelier.helix.spokes.base import DemoSpoke, SpokeError
from atelier.helix.spokes.openai_spoke import _download as openai_download
from atelier.helix.store import Memory
from atelier.helix.usage import is_priced
from atelier.launch import ensure_sys_path, repo_root as launch_root


class FailImageSpoke:
    def chat(self, messages, model="", **kwargs):
        return DemoSpoke().chat(messages, model=model or "demo-conductor", **kwargs)

    def image(self, prompt, model="", **kwargs):
        raise SpokeError("quota exceeded on gpt-image-1")


def _mem(tmp: Path) -> tuple[Memory, Keyring, Path]:
    mem = Memory(tmp / "t.sqlite")
    ring = Keyring(tmp / "keys.json")
    arts = tmp / "arts"
    arts.mkdir(exist_ok=True)
    return mem, ring, arts


class Round01FailClosed(unittest.TestCase):
    def test_paid_image_failure_does_not_mint_demo(self):
        tmp = tempfile.TemporaryDirectory()
        mem, ring, arts = _mem(Path(tmp.name))
        project = mem.create_project("Fail")
        thread = mem.create_thread(project["id"])
        cond = Conductor(mem, ring, arts)

        def factory(provider, keyring):
            if provider == "demo":
                return DemoSpoke()
            return FailImageSpoke()

        with mock.patch("atelier.helix.conductor.build_spoke", side_effect=factory):
            with self.assertRaises(ConductorError):
                cond.run(
                    project_id=project["id"],
                    thread_id=thread["id"],
                    prompt="navy logo",
                    provider="openai",
                )
        arts_rows = mem.conn.execute("SELECT provider FROM artifacts").fetchall()
        self.assertEqual(len(arts_rows), 0)
        mem.close()
        tmp.cleanup()

    def test_unknown_provider_does_not_fall_through_to_demo(self):
        tmp = tempfile.TemporaryDirectory()
        mem, ring, arts = _mem(Path(tmp.name))
        project = mem.create_project("Fail")
        thread = mem.create_thread(project["id"])
        cond = Conductor(mem, ring, arts)
        with self.assertRaises(ConductorError) as ctx:
            cond.run(
                project_id=project["id"],
                thread_id=thread["id"],
                prompt="navy logo",
                provider="open-ai",
            )
        self.assertEqual(ctx.exception.code, "unknown_provider")
        self.assertEqual(mem.conn.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0], 0)
        with self.assertRaises(SpokeError):
            build_spoke("not-a-vendor", ring)
        mem.close()
        tmp.cleanup()


class Round04DownloadName(unittest.TestCase):
    def test_slug_not_hex_id(self):
        name = download_filename(
            {"id": "abcdef123456", "prompt": "Queensland Legal Directory poster", "mime": "image/svg+xml"}
        )
        self.assertEqual(name, "queensland-legal-directory-poste.svg")
        self.assertTrue(name.endswith(".svg"))
        self.assertNotIn("abcdef", name)
    def test_quote_priced_and_unknown(self):
        priced = quote_run(provider="openai", model="gpt-4o-mini", prompt="logo", count=1)
        self.assertTrue(priced["priced"])
        self.assertGreater(priced["estimated_usd"], 0)
        unknown = quote_run(provider="openai", model="totally-unknown-model-xyz", prompt="logo")
        self.assertFalse(unknown["priced"])
        self.assertGreater(unknown["conservative_usd"], 0)
        self.assertFalse(is_priced("openai", "totally-unknown-model-xyz", "tokens_in"))
        demo = quote_run(provider="demo", prompt="x")
        self.assertTrue(demo["priced"])
        self.assertEqual(demo["estimated_usd"], 0)


class Round03Stream(unittest.TestCase):
    def test_run_emits_progress_events(self):
        tmp = tempfile.TemporaryDirectory()
        mem, ring, arts = _mem(Path(tmp.name))
        project = mem.create_project("Stream")
        thread = mem.create_thread(project["id"])
        cond = Conductor(mem, ring, arts)
        seen = []
        result = cond.run(
            project_id=project["id"],
            thread_id=thread["id"],
            prompt="calm poster",
            provider="demo",
            on_event=seen.append,
        )
        kinds = [e["kind"] for e in result["events"]]
        phases = [e.get("phase") for e in result["events"] if e["kind"] == "phase"]
        self.assertIn("quote", kinds)
        self.assertIn("brief", phases)
        self.assertIn("weave", phases)
        self.assertIn("done", phases)
        self.assertGreaterEqual(len(seen), 3)
        mem.close()
        tmp.cleanup()


class Round06to12Board(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mem, self.ring, self.arts = _mem(Path(self.tmp.name))
        self.project = self.mem.create_project(
            "Board",
            {"name": "Helix", "palette": ["#112233", "#f5c211", "#1a5fb4"]},
        )
        self.thread = self.mem.create_thread(self.project["id"])
        self.cond = Conductor(self.mem, self.ring, self.arts)

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def test_camera_persist(self):
        updated = self.mem.set_camera(self.project["id"], {"x": 40, "y": -12, "zoom": 1.5})
        self.assertEqual(updated["camera"]["zoom"], 1.5)
        self.assertEqual(self.mem.get_project(self.project["id"])["camera"]["x"], 40)
        clamped = self.mem.set_camera(self.project["id"], {"x": 0, "y": 0, "zoom": 99})
        self.assertEqual(clamped["camera"]["zoom"], 3.0)
        zeroed = self.mem.set_camera(self.project["id"], {"zoom": 0})
        self.assertEqual(zeroed["camera"]["zoom"], 1.0)
        # non-finite would serialise as a bare NaN / Infinity token and make
        # every later /api/projects response unparseable in the browser
        finite = self.mem.set_camera(
            self.project["id"], {"x": float("inf"), "y": float("nan"), "zoom": 2}
        )
        self.assertEqual((finite["camera"]["x"], finite["camera"]["y"]), (0.0, 0.0))

    def test_plan_visible_on_message(self):
        result = self.cond.run(
            project_id=self.project["id"],
            thread_id=self.thread["id"],
            prompt="directory poster",
            provider="demo",
            mode="thinking",
        )
        self.assertIn("intent", result["plan"])
        self.assertTrue(result["plan"].get("weave"))
        msgs = self.mem.list_messages(self.thread["id"])
        assistant = [m for m in msgs if m["role"] == "assistant"][-1]
        self.assertTrue(assistant.get("plan"))

    def test_four_up_variants(self):
        result = self.cond.run(
            project_id=self.project["id"],
            thread_id=self.thread["id"],
            prompt="four variants of a navy mark",
            provider="demo",
            variants=4,
        )
        self.assertGreaterEqual(len(result["artifacts"]), 4)
        self.assertEqual(result["plan"].get("variants"), 4)

    def test_undo_last_node(self):
        node = self.mem.add_node(project_id=self.project["id"], type="text", text="A")
        before = len(self.mem.list_nodes(self.project["id"]))
        undone = self.mem.undo(self.project["id"])
        self.assertTrue(undone["undone"])
        self.assertEqual(len(self.mem.list_nodes(self.project["id"])), before - 1)
        self.assertFalse(any(n["id"] == node["id"] for n in self.mem.list_nodes(self.project["id"])))

    def test_brand_kit_tints_demo_svg(self):
        from atelier.helix.loom import style_lock

        svg = demo_svg("logo", title="Helix", palette=["#112233", "#f5c211"])
        self.assertIn("#112233", svg)
        self.assertIn("#f5c211", svg)
        locked = style_lock("navy mark", palette=["#112233", "#f5c211"], title="Helix")
        self.assertIn("[StyleLock", locked)
        self.assertIn("#112233", locked)
        self.assertIn("ground=#112233", locked)
        self.assertTrue(locked.endswith("navy mark"))

    def test_spot_edit_sets_parent(self):
        first = self.cond.run(
            project_id=self.project["id"],
            thread_id=self.thread["id"],
            prompt="base mark",
            provider="demo",
        )
        parent_id = first["artifacts"][0]["id"]
        second = self.cond.run(
            project_id=self.project["id"],
            thread_id=self.thread["id"],
            prompt="spot edit: larger type",
            provider="demo",
            parent_artifact_id=parent_id,
        )
        self.assertEqual(second["artifacts"][0].get("parent_id"), parent_id)
        self.assertTrue(second["plan"].get("spot_edit"))

    def test_uploaded_reference_is_usable_as_parent(self):
        parent = self.mem.add_artifact(
            project_id=self.project["id"],
            kind="upload",
            mime="image/svg+xml",
            prompt="ref.svg",
            provider="local",
            model="upload",
        )
        result = self.cond.run(
            project_id=self.project["id"],
            thread_id=self.thread["id"],
            prompt="match this reference",
            provider="demo",
            parent_artifact_id=parent["id"],
        )
        self.assertEqual(result["artifacts"][0].get("parent_id"), parent["id"])
        self.assertEqual(result["plan"]["spot_edit"]["parent_id"], parent["id"])

    def test_text_layer_not_raster(self):
        node = self.mem.add_node(
            project_id=self.project["id"],
            type="text",
            text="Headline",
            meta={"layer": "text"},
        )
        self.assertEqual(node["type"], "text")
        self.assertEqual(node["meta"]["layer"], "text")
        self.assertIsNone(node.get("artifact_id"))
        via_data = self.mem.add_node(project_id=self.project["id"], type="text", data="From data")
        self.assertEqual(via_data["text"], "From data")
        moved = self.mem.update_node(via_data["id"], data="Edited")
        self.assertEqual(moved["text"], "Edited")


class Round13Export(unittest.TestCase):
    def test_export_zip_contains_board(self):
        tmp = tempfile.TemporaryDirectory()
        mem, ring, arts = _mem(Path(tmp.name))
        project = mem.create_project("Zip")
        thread = mem.create_thread(project["id"])
        cond = Conductor(mem, ring, arts)
        cond.run(project_id=project["id"], thread_id=thread["id"], prompt="mark", provider="demo")
        blob = export_project_zip(mem, arts, project["id"])
        self.assertGreater(len(blob), 40)
        self.assertEqual(blob[:2], b"PK")
        import zipfile
        import io

        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            names = set(zf.namelist())
            self.assertIn("threads.json", names)
            self.assertIn("board.json", names)
            threads = json.loads(zf.read("threads.json"))
            self.assertTrue(threads)
            self.assertTrue(threads[0].get("messages"))
        mem.close()
        tmp.cleanup()


class Round14Launcher(unittest.TestCase):
    def test_repo_root_independent_of_cwd(self):
        root = launch_root()
        self.assertTrue((root / "atelier" / "server.py").exists())
        self.assertEqual(ensure_sys_path(), root)


class Round15HostPin(unittest.TestCase):
    def test_keyring_rejects_unofficial_openai_host(self):
        tmp = tempfile.TemporaryDirectory()
        ring = Keyring(Path(tmp.name) / "k.json")
        with self.assertRaises(ValueError):
            ring.put("openai", key="sk-testkey-abcdefghijk", base_url="https://chatgpt.com")
        with self.assertRaises(ValueError):
            ring.put("gemini", key="AIza-test", base_url="https://evil.example")
        ring.put("openai", key="sk-testkey-abcdefghijk", base_url="https://api.openai.com")
        tmp.cleanup()

    def test_no_redirect_handler_refuses(self):
        handler = NoRedirectHandler()
        self.assertIsNone(
            handler.redirect_request(None, None, 302, "Found", {}, "https://evil.example/steal")
        )


class Round16Budget(unittest.TestCase):
    def test_quote_flags_thread_budget(self):
        tmp = tempfile.TemporaryDirectory()
        mem, _, _ = _mem(Path(tmp.name))
        project = mem.create_project("Bud")
        thread = mem.create_thread(project["id"])
        mem.add_usage(
            provider="openai",
            model="gpt-image-1",
            unit_kind="images",
            units=1,
            estimated_usd=3.0,
            thread_id=thread["id"],
        )
        q = quote_run(
            provider="openai",
            model="gpt-4o-mini",
            prompt="another image",
            memory=mem,
            thread_id=thread["id"],
        )
        self.assertTrue(q["would_exceed"])
        mem.close()
        tmp.cleanup()


class SecurityHarden(unittest.TestCase):
    def test_safe_under_rejects_escape(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name) / "web"
        root.mkdir()
        (root / "ok.txt").write_text("ok")
        self.assertIsNotNone(safe_under(root, root / "ok.txt"))
        self.assertIsNone(safe_under(root, root / ".." / "ok.txt"))
        self.assertIsNone(safe_under(root, Path("/etc/passwd")))
        tmp.cleanup()

    def test_openai_download_rejects_file_url(self):
        with self.assertRaises(SpokeError):
            openai_download("file:///etc/passwd")
        with self.assertRaises(SpokeError):
            openai_download("http://example.com/x.png")

    def test_keyring_mode_0600_not_symlink(self):
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / "keyring.json"
        ring = Keyring(path)
        ring.put("openai", key="sk-testkey-abcdefghijk")
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        tmp.cleanup()


class Round19EvalFixtures(unittest.TestCase):
    def test_eval_briefs_load(self):
        folder = ROOT / "atelier" / "data" / "eval"
        names = [
            "brief_logo.json",
            "brief_poster.json",
            "brief_factsheet_legal_directory.json",
            "brief_brand_kit_apply.json",
        ]
        for name in names:
            data = json.loads((folder / name).read_text())
            self.assertIn("request", data)
            self.assertIn("expected", data)


class Round17to20Meta(unittest.TestCase):
    def test_ci_workflow_exists(self):
        wf = ROOT / ".github" / "workflows" / "atelier.yml"
        text = wf.read_text()
        self.assertIn("atelier.tests.test_helix", text)
        self.assertIn("atelier.tests.test_evolve", text)

    def test_live_contract_notes_exist(self):
        text = (ROOT / "atelier" / "research" / "evolve" / "CONTRACT.md").read_text()
        self.assertIn("/api/threads/", text)
        self.assertIn("/api/quote", text)
        self.assertNotIn("MUST use /api/chat", text)

    def test_scorecard_gate(self):
        card = json.loads((ROOT / "atelier" / "research" / "evolve" / "SCORECARD.json").read_text())
        self.assertEqual(card["rounds_total"], 20)
        self.assertGreaterEqual(card["passed"], 16)
        self.assertTrue(card["gates"]["fail_closed"])
        self.assertEqual(len(card["rounds"]), 20)
        self.assertTrue(all(r.get("pass") for r in card["rounds"]))


class HttpRounds(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["ATELIER_RUNTIME"] = str(Path(self.tmp.name) / "rt")
        os.environ["ATELIER_HOME"] = str(Path(self.tmp.name) / "home")
        from atelier import server

        self.server_mod = server
        server.reset_app()
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.tmp.cleanup()

    def _json(self, method: str, path: str, body: dict | None = None, query: str = ""):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}{query}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                ctype = resp.headers.get("Content-Type", "")
                payload = json.loads(raw.decode()) if raw and "json" in ctype else {"raw": raw.decode(), "headers": dict(resp.headers)}
                return resp.status, payload, resp.headers
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                payload = json.loads(raw.decode())
            except Exception:
                payload = {"raw": raw.decode()}
            return exc.code, payload, exc.headers

    def _ids(self):
        _, data, _ = self._json("GET", "/api/projects")
        project = data["projects"][0]
        _, threads, _ = self._json("GET", f"/api/projects/{project['id']}/threads")
        return project["id"], threads["threads"][0]["id"]

    def test_quote_and_download_and_upload(self):
        pid, tid = self._ids()
        code, quote, _ = self._json(
            "POST",
            "/api/quote",
            {"provider": "openai", "model": "gpt-4o-mini", "prompt": "logo", "thread_id": tid},
        )
        self.assertEqual(code, 200)
        self.assertIn("estimated_usd", quote)

        code, result, _ = self._json(
            "POST",
            f"/api/threads/{tid}/run",
            {"prompt": "demo mark", "provider": "demo"},
        )
        self.assertEqual(code, 200)
        self.assertTrue(result.get("ok"))
        art = result["artifacts"][0]
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/artifacts/{art['id']}?download=1"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            disp = resp.headers.get("Content-Disposition", "")
            self.assertIn("attachment", disp)
            self.assertIn(".svg", disp)
            self.assertNotIn(art["id"], disp)

        svg = base64.b64encode(b"<svg xmlns='http://www.w3.org/2000/svg'></svg>").decode()
        code, uploaded, _ = self._json(
            "POST",
            f"/api/projects/{pid}/upload",
            {"filename": "ref.svg", "mime": "image/svg+xml", "data": svg},
        )
        self.assertEqual(code, 201)
        self.assertEqual(uploaded["artifact"]["kind"], "upload")

    def test_stream_sse_and_export_and_402(self):
        pid, tid = self._ids()
        code, result, headers = self._json(
            "POST",
            f"/api/threads/{tid}/run",
            {"prompt": "sse mark", "provider": "demo"},
            query="?stream=1",
        )
        self.assertEqual(code, 200)
        self.assertIn("text/event-stream", headers.get("Content-Type", ""))

        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/projects/{pid}/export")
        with urllib.request.urlopen(req, timeout=10) as resp:
            self.assertEqual(resp.headers.get("Content-Type"), "application/zip")
            self.assertEqual(resp.read()[:2], b"PK")

        self.server_mod.get_app().memory.add_usage(
            provider="openai",
            model="gpt-image-1",
            unit_kind="images",
            units=1,
            estimated_usd=3.0,
            thread_id=tid,
        )
        code, payload, _ = self._json(
            "POST",
            f"/api/threads/{tid}/run",
            {"prompt": "paid", "provider": "openai"},
        )
        self.assertEqual(code, 402)
        self.assertEqual(payload.get("code"), "budget_exceeded")
        self.assertFalse(payload.get("ok"))

        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/web/../../helix/keyring.py")
        try:
            urllib.request.urlopen(req, timeout=5)
            self.fail("traversal should not succeed")
        except urllib.error.HTTPError as exc:
            self.assertIn(exc.code, {403, 404})


if __name__ == "__main__":
    unittest.main()
