#!/usr/bin/env python3
"""Fable-05 — Round 9 (Undo) verification.

Covers: store.push_undo via add_node, store.undo LIFO pop,
POST /api/projects/:id/undo, web Undo button wiring, and the
documented holes (no redo, artifacts survive undo).

Runnable directly (no package __init__ needed):
    python3 atelier/tests/evolve/test_fable_05.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.store import Memory


class UndoStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mem = Memory(Path(self.tmp.name) / "t.sqlite")
        self.project = self.mem.create_project("Fable05")
        self.pid = self.project["id"]

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def _undo_rows(self):
        return self.mem.conn.execute(
            "SELECT * FROM undo_log WHERE project_id=? ORDER BY created_at ASC",
            (self.pid,),
        ).fetchall()

    def test_add_node_pushes_undo_entry(self):
        node = self.mem.add_node(project_id=self.pid, type="text", text="hello")
        rows = self._undo_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["action"], "add_node")
        payload = json.loads(rows[0]["payload"])
        self.assertEqual(payload["node_id"], node["id"])

    def test_undo_pops_lifo(self):
        first = self.mem.add_node(project_id=self.pid, type="text", text="first")
        second = self.mem.add_node(project_id=self.pid, type="text", text="second")
        result = self.mem.undo(self.pid)
        self.assertTrue(result["undone"])
        self.assertEqual(result["action"], "add_node")
        self.assertEqual(result["payload"]["node_id"], second["id"])
        ids = {n["id"] for n in self.mem.list_nodes(self.pid)}
        self.assertIn(first["id"], ids)
        self.assertNotIn(second["id"], ids)

    def test_undo_empty_log(self):
        result = self.mem.undo(self.pid)
        self.assertEqual(result, {"undone": False, "reason": "empty"})

    def test_undo_scoped_to_project(self):
        other = self.mem.create_project("Other")
        self.mem.add_node(project_id=other["id"], type="text", text="theirs")
        result = self.mem.undo(self.pid)
        self.assertFalse(result["undone"])
        self.assertEqual(len(self.mem.list_nodes(other["id"])), 1)

    def test_hole_no_redo(self):
        """Undo is destructive: the popped entry is gone and no redo API exists."""
        self.mem.add_node(project_id=self.pid, type="text", text="once")
        self.assertTrue(self.mem.undo(self.pid)["undone"])
        self.assertEqual(self.mem.undo(self.pid), {"undone": False, "reason": "empty"})
        self.assertFalse(hasattr(self.mem, "redo"))

    def test_hole_artifact_survives_undo(self):
        """Undo deletes the node row but leaves the artifact row (and file) behind."""
        art = self.mem.add_artifact(project_id=self.pid, kind="image", path="a.svg")
        node = self.mem.add_node(project_id=self.pid, type="image", artifact_id=art["id"])
        result = self.mem.undo(self.pid)
        self.assertTrue(result["undone"])
        self.assertEqual(result["payload"]["artifact_id"], art["id"])
        self.assertNotIn(node["id"], {n["id"] for n in self.mem.list_nodes(self.pid)})
        self.assertIsNotNone(self.mem.get_artifact(art["id"]))  # orphaned artifact


class UndoHTTP(unittest.TestCase):
    def setUp(self):
        import os

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
            return resp.status, json.loads(resp.read().decode())

    def test_post_undo_endpoint(self):
        mem = self.server_mod.get_app().memory
        pid = mem.list_projects()[0]["id"]
        code, node = self._post(f"/api/projects/{pid}/nodes", {"type": "text", "text": "via http"})
        self.assertEqual(code, 201)
        code, result = self._post(f"/api/projects/{pid}/undo", {})
        self.assertEqual(code, 200)
        self.assertTrue(result["undone"])
        self.assertEqual(result["payload"]["node_id"], node["id"])
        code, result = self._post(f"/api/projects/{pid}/undo", {})
        self.assertEqual(code, 200)
        self.assertEqual(result, {"undone": False, "reason": "empty"})


class UndoWeb(unittest.TestCase):
    def test_button_and_wiring(self):
        html = (ROOT / "atelier" / "web" / "index.html").read_text()
        self.assertIn('id="undoBtn"', html)
        js = (ROOT / "atelier" / "web" / "app.js").read_text()
        self.assertIn('getElementById("undoBtn")', js)
        self.assertIn("/undo", js)
        self.assertIn("refreshBoard", js)


if __name__ == "__main__":
    unittest.main(verbosity=2)
