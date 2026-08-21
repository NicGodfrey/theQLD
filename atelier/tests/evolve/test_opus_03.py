#!/usr/bin/env python3
"""Opus-03 — Round 6 (canvas camera) verification.

Pins the three surfaces the round claims:

* `Memory.set_camera` — coercion, the 0.25–3 zoom clamp, and the non-finite
  guard that keeps `/api/projects` valid JSON.
* `POST|GET /api/projects/:id/camera` and `GET .../board`, over real HTTP
  against a `ThreadingHTTPServer` (demo lane only, no provider keys).
* The live `atelier/web/app.js` itself, executed under node against that same
  server through a small DOM shim, so Home / Fit / the debounce are checked by
  running them rather than by grepping for their names. Those tests skip when
  no node binary is present; the string-level wiring checks below always run.

Tests marked "pins current behaviour" assert what the tree does today, holes
included, so a later round notices when it changes them.
"""

from __future__ import annotations

import io
import json
import math
import os
import shutil
import subprocess
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
APP_JS = WEB / "app.js"
NODE = shutil.which("node")

# A DOM small enough to be honest about: no layout, no CSS, no bubbling. It
# exists so the real app.js can boot, bind its buttons and talk to the real
# server; every camera number the tests assert on is read back over HTTP.
HARNESS_JS = r"""
const APP = process.argv[2];
const BASE = process.argv[3];
const PROJECT = process.argv[4];
const SCENARIO = process.argv[5];

const fetchLog = [];
const realFetch = globalThis.fetch;
globalThis.fetch = (path, opts = {}) => {
  fetchLog.push({ method: (opts.method || "GET").toUpperCase(), path, body: opts.body });
  return realFetch(path.startsWith("http") ? path : BASE + path, opts);
};
const cameraWrites = () => fetchLog.filter((f) => f.method === "POST" && f.path.endsWith("/camera"));
const serverCamera = async (id) => (await (await realFetch(`${BASE}/api/projects/${id}/camera`)).json()).camera;

class Elem {
  constructor(tag, id) {
    this.tagName = tag; this.id = id || ""; this.style = {}; this.children = [];
    this.listeners = {}; this.className = ""; this.textContent = ""; this.value = "";
    this.checked = false; this._innerHTML = ""; this._cw = 1000; this._ch = 800;
    this.classList = {
      add: (c) => { if (!this.className.split(" ").includes(c)) this.className = (this.className + " " + c).trim(); },
      remove: (c) => { this.className = this.className.split(" ").filter((t) => t && t !== c).join(" "); },
    };
  }
  get innerHTML() { return this._innerHTML; }
  set innerHTML(v) { this._innerHTML = v; if (v === "") this.children = []; }
  get clientWidth() { return this._cw; }
  get clientHeight() { return this._ch; }
  get scrollHeight() { return 0; }
  addEventListener(kind, fn) { (this.listeners[kind] = this.listeners[kind] || []).push(fn); }
  dispatch(kind, ev = {}) {
    ev.target = ev.target || this;
    ev.preventDefault = ev.preventDefault || (() => {});
    ev.stopPropagation = ev.stopPropagation || (() => {});
    (this.listeners[kind] || []).forEach((fn) => fn(ev));
    if (typeof this["on" + kind] === "function") this["on" + kind](ev);
  }
  append(...kids) { kids.forEach((k) => { this.children.push(k); k.parent = this; }); }
  setAttribute(k, v) { this[k] = v; }
  setPointerCapture() {}
  releasePointerCapture() {}
  closest(sel) {
    const hit = (node) => sel.split(",").map((s) => s.trim()).some((s) => (
      s.startsWith(".") ? node.className.split(" ").includes(s.slice(1))
        : s.startsWith("#") ? node.id === s.slice(1) : node.tagName === s));
    let cur = this;
    while (cur) { if (hit(cur)) return cur; cur = cur.parent; }
    return null;
  }
}

const byId = {};
[
  "board", "boardWrap", "camReadout", "camHome", "camFit", "projectList", "threadList",
  "messages", "planCard", "brandKit", "keyStatus", "topMeta", "runStatus", "prompt",
  "mode", "provider", "model", "variants", "newProject", "newThread", "saveKey",
  "saveBrand", "quoteBtn", "run", "undoBtn", "textLayer", "exportZip", "openCatalog",
  "uploadBtn", "filePick", "keyProvider", "keyValue", "keyBase",
].forEach((id) => { byId[id] = new Elem("div", id); });
byId.mode.value = "fast";
byId.provider.value = "demo";
byId.board.parent = byId.boardWrap;

const walk = (node, out) => { node.children.forEach((c) => { out.push(c); walk(c, out); }); return out; };
globalThis.document = {
  getElementById: (id) => byId[id] || null,
  createElement: (tag) => new Elem(tag),
  addEventListener: () => {},
  querySelectorAll: (sel) => (sel === "#board .node"
    ? walk(byId.board, []).filter((n) => n.className.split(" ").includes("node"))
    : []),
};
globalThis.window = {
  addEventListener: (kind, fn) => { (globalThis.window._listeners = globalThis.window._listeners || {})[kind] = fn; },
};
globalThis.prompt = () => "x";
globalThis.alert = () => {};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
require(APP);

async function board(report) {
  report.booted_readout = byId.camReadout.textContent;
  report.node_cards = document.querySelectorAll("#board .node").length;
  report.home_bound = typeof byId.camHome.onclick === "function";
  report.fit_bound = typeof byId.camFit.onclick === "function";
  report.readout_bound = typeof byId.camReadout.onclick === "function";
  report.pagehide_bound = !!(globalThis.window._listeners || {}).pagehide;

  let before = cameraWrites().length;
  for (let i = 0; i < 30; i += 1) byId.boardWrap.dispatch("wheel", { deltaY: -1 });
  report.wheel_readout = byId.camReadout.textContent;
  report.wheel_transform = byId.board.style.transform;
  report.wheel_writes_during_burst = cameraWrites().length - before;
  await sleep(400);
  report.wheel_writes_after_debounce = cameraWrites().length - before;
  report.server_after_wheel = await serverCamera(PROJECT);

  before = cameraWrites().length;
  byId.camFit.onclick();
  await sleep(400);
  report.fit_readout = byId.camReadout.textContent;
  report.fit_writes = cameraWrites().length - before;
  report.server_after_fit = await serverCamera(PROJECT);

  byId.camHome.onclick();
  await sleep(400);
  report.home_readout = byId.camReadout.textContent;
  report.server_after_home = await serverCamera(PROJECT);

  byId.boardWrap.dispatch("pointerdown", { clientX: 0, clientY: 0, pointerId: 1 });
  byId.boardWrap.dispatch("pointermove", { clientX: 260, clientY: 130, pointerId: 1 });
  byId.boardWrap.dispatch("pointerup", { pointerId: 1 });
  report.pan_transform = byId.board.style.transform;
  await sleep(400);
  report.server_after_pan = await serverCamera(PROJECT);

  byId.camReadout.onclick();
  await sleep(400);
  report.readout_click_transform = byId.board.style.transform;
  report.server_after_readout_click = await serverCamera(PROJECT);

  // a drag on a card moves it in world units, i.e. divided by zoom
  byId.camFit.onclick();
  await sleep(300);
  const card = document.querySelectorAll("#board .node")[0];
  const zoom = Number((byId.board.style.transform.match(/scale\(([-\d.]+)\)/) || [])[1]);
  const startLeft = parseFloat(card.style.left);
  card.dispatch("pointerdown", { clientX: 0, clientY: 0, pointerId: 2, target: card });
  card.dispatch("pointermove", { clientX: 100, clientY: 0, pointerId: 2 });
  card.dispatch("pointerup", { pointerId: 2 });
  report.drag = { zoom, start_left: startLeft, end_left: parseFloat(card.style.left) };
  await sleep(200);
}

async function switchProjects(report) {
  const rail = () => byId.projectList.children;
  const click = (name) => rail().find((c) => c.textContent === name).dispatch("click");
  report.rail = rail().map((c) => c.textContent);

  click("A");
  await sleep(500);
  report.on_A_transform = byId.board.style.transform;

  // pan A, then switch to B well inside the 180 ms debounce window
  byId.boardWrap.dispatch("pointerdown", { clientX: 0, clientY: 0, pointerId: 1 });
  byId.boardWrap.dispatch("pointermove", { clientX: 300, clientY: 150, pointerId: 1 });
  byId.boardWrap.dispatch("pointerup", { pointerId: 1 });
  report.after_pan_transform = byId.board.style.transform;
  click("B");
  await sleep(800);
  report.on_B_transform = byId.board.style.transform;
  report.camera_writes = cameraWrites().map((w) => ({ path: w.path, body: w.body }));
}

(async () => {
  const report = {};
  await sleep(600);
  if (SCENARIO === "switch") await switchProjects(report);
  else await board(report);
  console.log("REPORT:" + JSON.stringify(report));
})().catch((err) => {
  console.log("REPORT:" + JSON.stringify({ error: String(err && err.stack || err) }));
});
"""


class LiveServer:
    """A real ThreadingHTTPServer on a throwaway runtime."""

    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self._saved_env = {k: os.environ.get(k) for k in ("ATELIER_RUNTIME", "ATELIER_HOME")}
        os.environ["ATELIER_RUNTIME"] = str(Path(self.tmp.name) / "rt")
        os.environ["ATELIER_HOME"] = str(Path(self.tmp.name) / "home")
        from atelier import server as server_module

        self.server = server_module
        server_module.reset_app()
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server_module.Handler)
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    @property
    def memory(self):
        return self.server.get_app().memory

    def stop(self) -> None:
        self.httpd.shutdown()
        self.thread.join(timeout=5)
        self.httpd.server_close()
        self.memory.close()
        self.server.reset_app()
        for key, value in self._saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def raw(self, method: str, path: str, body: bytes | None = None) -> tuple[int, str]:
        req = urllib.request.Request(
            self.base + path,
            data=body,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def json(self, method: str, path: str, body=None) -> tuple[int, dict]:
        data = None if body is None else json.dumps(body).encode()
        status, text = self.raw(method, path, data)
        return status, json.loads(text)


def _strict_json(text: str) -> bool:
    """True when text is JSON a browser would accept — no NaN / Infinity."""

    def reject(token):
        raise ValueError(token)

    try:
        json.loads(text, parse_constant=reject)
        return True
    except ValueError:
        return False


class CameraStore(unittest.TestCase):
    """Memory.set_camera — coercion, clamp, and the non-finite guard."""

    def setUp(self):
        from atelier.helix.store import Memory

        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "helix.sqlite3"
        self.mem = Memory(self.db)
        self.project = self.mem.create_project("Camera")

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def set(self, camera):
        return self.mem.set_camera(self.project["id"], camera)["camera"]

    def test_default_camera_is_home(self):
        self.assertEqual(self.project["camera"], {"x": 0, "y": 0, "zoom": 1})

    def test_zoom_clamped_to_the_quarter_to_triple_band(self):
        self.assertEqual(self.set({"zoom": 99})["zoom"], 3.0)
        self.assertEqual(self.set({"zoom": 3.0})["zoom"], 3.0)
        self.assertEqual(self.set({"zoom": 0.01})["zoom"], 0.25)
        self.assertEqual(self.set({"zoom": 0.25})["zoom"], 0.25)
        self.assertEqual(self.set({"zoom": 1.75})["zoom"], 1.75)

    def test_non_positive_zoom_becomes_one_then_stays_in_band(self):
        for bad in (0, -1, -0.0, -1e9):
            self.assertEqual(self.set({"zoom": bad})["zoom"], 1.0)

    def test_garbage_falls_back_instead_of_raising(self):
        for bad in (None, "", "abc", [1, 2], {"a": 1}, object()):
            self.assertEqual(self.set({"x": bad, "y": bad, "zoom": bad}), {"x": 0.0, "y": 0.0, "zoom": 1.0})

    def test_numeric_strings_are_accepted(self):
        self.assertEqual(self.set({"x": "40", "y": "-12", "zoom": "2.5"}), {"x": 40.0, "y": -12.0, "zoom": 2.5})

    def test_non_finite_never_reaches_the_row(self):
        # NaN / Infinity survive json.loads but json.dumps writes them as bare
        # tokens, which is not JSON — one write used to break every later read.
        for bad in (float("nan"), float("inf"), float("-inf"), "1e999", "nan", "Infinity"):
            camera = self.set({"x": bad, "y": bad, "zoom": bad})
            for axis in ("x", "y", "zoom"):
                self.assertTrue(math.isfinite(camera[axis]), f"{axis} non-finite for {bad!r}")
            self.assertEqual((camera["x"], camera["y"]), (0.0, 0.0))
            self.assertEqual(camera["zoom"], 1.0)
        stored = self.mem.conn.execute(
            "SELECT camera FROM projects WHERE id=?", (self.project["id"],)
        ).fetchone()[0]
        self.assertTrue(_strict_json(stored), stored)

    def test_camera_is_not_a_dict_at_all(self):
        for bad in (None, "nope", 7, [1, 2, 3]):
            self.assertEqual(self.mem.set_camera(self.project["id"], bad)["camera"],
                             {"x": 0.0, "y": 0.0, "zoom": 1.0})

    def test_missing_project_returns_none(self):
        self.assertIsNone(self.mem.set_camera("deadbeef", {"zoom": 2}))

    def test_camera_survives_a_reopen(self):
        from atelier.helix.store import Memory

        self.set({"x": 11, "y": 22, "zoom": 2})
        self.mem.close()
        again = Memory(self.db)
        try:
            self.assertEqual(again.get_project(self.project["id"])["camera"],
                             {"x": 11.0, "y": 22.0, "zoom": 2.0})
        finally:
            again.close()
            self.mem = Memory(self.db)  # tearDown closes this one


class CameraWiring(unittest.TestCase):
    """Cheap string gate — the node tests below prove the behaviour, but these
    still run on a machine with no JS runtime."""

    def setUp(self):
        self.longMessage = False  # these haystacks are whole files
        self.html = (WEB / "index.html").read_text(encoding="utf-8")
        self.app_js = APP_JS.read_text(encoding="utf-8")

    def in_js(self, needle):
        self.assertIn(needle, self.app_js, f"app.js no longer contains: {needle}")

    def in_html(self, needle):
        self.assertIn(needle, self.html, f"index.html no longer contains: {needle}")

    def test_home_fit_and_readout_reset_exist(self):
        self.in_html('id="camHome"')
        self.in_html('id="camFit"')
        self.in_js("function resetCamera()")
        self.in_js("function fitCamera()")
        self.in_js("persistCameraTimer")
        self.in_js('document.getElementById("camHome").onclick = resetCamera')
        self.in_js('document.getElementById("camFit").onclick = fitCamera')
        self.in_js('document.getElementById("camReadout").onclick = resetCamera')

    def test_wheel_and_pan_still_drive_the_camera(self):
        self.in_js('wrap.addEventListener("wheel"')
        self.in_js("persistCamera()")
        self.in_js("clampCamera")

    def test_debounced_write_captures_its_project(self):
        self.in_js("pendingCamera = { projectId: state.projectId")
        self.in_js("pending.projectId")

    def test_pending_write_is_flushed_on_pagehide_and_project_switch(self):
        self.in_js('window.addEventListener("pagehide", flushCamera)')
        self.in_js("await flushCamera();")

    def test_camera_buttons_sit_outside_the_pan_surface(self):
        # board-tools is excluded from the pan handler, so Home / Fit / the
        # readout are clickable instead of starting a drag.
        self.in_js('e.target.closest(".board-tools")')
        self.in_html('class="board-tools"')


class CameraRoute(unittest.TestCase):
    """POST|GET /api/projects/:id/camera and GET .../board over real HTTP."""

    @classmethod
    def setUpClass(cls):
        cls.live = LiveServer()

    @classmethod
    def tearDownClass(cls):
        cls.live.stop()

    def _json(self, method, path, body=None):
        return self.live.json(method, path, body)

    def _project(self, name="R6"):
        return self._json("POST", "/api/projects", {"name": name})[1]

    def test_camera_round_trips_on_the_board(self):
        project = self._project()
        status, saved = self._json(
            "POST",
            f"/api/projects/{project['id']}/camera",
            {"camera": {"x": 40, "y": -12, "zoom": 1.5}},
        )
        self.assertEqual(status, 200)
        self.assertEqual(saved["camera"], {"x": 40.0, "y": -12.0, "zoom": 1.5})
        status, got = self._json("GET", f"/api/projects/{project['id']}/camera")
        self.assertEqual(status, 200)
        self.assertEqual(got["camera"]["zoom"], 1.5)
        _, board = self._json("GET", f"/api/projects/{project['id']}/board")
        self.assertEqual(board["camera"]["x"], 40.0)
        _, listed = self._json("GET", "/api/projects")
        mine = [p for p in listed["projects"] if p["id"] == project["id"]][0]
        self.assertEqual(mine["camera"]["y"], -12.0)

    def test_zoom_is_clamped(self):
        project = self._project("R6-clamp")
        _, hi = self._json("POST", f"/api/projects/{project['id']}/camera", {"camera": {"zoom": 99}})
        self.assertEqual(hi["camera"]["zoom"], 3.0)
        _, lo = self._json("POST", f"/api/projects/{project['id']}/camera", {"camera": {"zoom": 0.01}})
        self.assertEqual(lo["camera"]["zoom"], 0.25)
        _, zero = self._json("POST", f"/api/projects/{project['id']}/camera", {"camera": {"zoom": 0}})
        self.assertEqual(zero["camera"]["zoom"], 1.0)

    def test_missing_project_is_404(self):
        status, body = self._json("POST", "/api/projects/deadbeef/camera", {"camera": {"zoom": 1}})
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "missing project")
        status, body = self._json("GET", "/api/projects/deadbeef/camera")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "missing project")

    def test_flat_body_without_a_camera_key_still_works(self):
        # pins current behaviour: the route falls back to `body` itself.
        project = self._project("R6-flat")
        _, saved = self._json("POST", f"/api/projects/{project['id']}/camera", {"x": 5, "y": 6, "zoom": 2})
        self.assertEqual(saved["camera"], {"x": 5.0, "y": 6.0, "zoom": 2.0})

    def test_empty_and_malformed_bodies_land_on_home(self):
        project = self._project("R6-empty")
        self._json("POST", f"/api/projects/{project['id']}/camera", {"camera": {"x": 9, "y": 9, "zoom": 2}})
        for body in ({"camera": {}}, {"camera": "nope"}, {"camera": [1, 2]}, {}):
            _, saved = self._json("POST", f"/api/projects/{project['id']}/camera", body)
            self.assertEqual(saved["camera"], {"x": 0.0, "y": 0.0, "zoom": 1.0}, body)
        status, text = self.live.raw("POST", f"/api/projects/{project['id']}/camera")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(text)["camera"], {"x": 0.0, "y": 0.0, "zoom": 1.0})
        status, _ = self.live.raw("POST", f"/api/projects/{project['id']}/camera", b"{not json")
        self.assertEqual(status, 400)

    def test_non_finite_write_cannot_poison_later_reads(self):
        # Regression: `{"x": 1e999}` used to store bare `Infinity`, which made
        # /api/projects unparseable for every project, not just this one.
        project = self._project("R6-nan")
        other = self._project("R6-bystander")
        for literal in (
            b'{"camera": {"x": NaN, "y": 0, "zoom": 2}}',
            b'{"camera": {"x": Infinity, "y": -Infinity, "zoom": 2}}',
            b'{"camera": {"x": 0, "y": 0, "zoom": Infinity}}',
            b'{"camera": {"x": "1e999", "y": 0, "zoom": 2}}',
            b'{"camera": {"x": 0, "y": 0, "zoom": NaN}}',
        ):
            status, text = self.live.raw("POST", f"/api/projects/{project['id']}/camera", literal)
            self.assertEqual(status, 200, literal)
            self.assertTrue(_strict_json(text), f"{literal!r} -> {text}")
            for path in (
                f"/api/projects/{project['id']}",
                f"/api/projects/{project['id']}/camera",
                f"/api/projects/{project['id']}/board",
                f"/api/projects/{other['id']}/board",
                "/api/projects",
            ):
                _, body = self.live.raw("GET", path)
                self.assertTrue(_strict_json(body), f"{literal!r} poisoned {path}")

    def test_board_of_a_missing_project_is_200_with_a_home_camera(self):
        # pins current behaviour — GET .../camera 404s but GET .../board does
        # not, it answers 200 with an empty board. Listed as a remaining hole.
        status, body = self._json("GET", "/api/projects/deadbeef/board")
        self.assertEqual(status, 200)
        self.assertEqual(body["nodes"], [])
        self.assertEqual(body["camera"], {"x": 0, "y": 0, "zoom": 1})

    def test_pan_offsets_are_unbounded(self):
        # pins current behaviour: only zoom is clamped, x/y take any finite
        # value, so a fast pan can park content off-screen until Home / Fit.
        project = self._project("R6-pan")
        _, saved = self._json(
            "POST", f"/api/projects/{project['id']}/camera", {"camera": {"x": 1e9, "y": -1e9, "zoom": 1}}
        )
        self.assertEqual(saved["camera"]["x"], 1e9)

    def test_camera_body_never_reaches_the_log(self):
        project = self._project("R6-log")
        buf = io.StringIO()
        stderr, sys.stderr = sys.stderr, buf
        try:
            # send_response logs the request line before the body is written,
            # so the line is already in the buffer once we have the response.
            _, saved = self._json(
                "POST",
                f"/api/projects/{project['id']}/camera",
                {"camera": {"x": 31337, "y": 4242, "zoom": 2.75}},
            )
        finally:
            sys.stderr = stderr
        log = buf.getvalue()
        self.assertEqual(saved["camera"]["x"], 31337.0)
        self.assertIn("/camera", log)
        for secret in ("31337", "4242", "2.75"):
            self.assertNotIn(secret, log, log)


@unittest.skipUnless(NODE, "no node binary — JS behaviour tests skipped")
class BoardCameraJs(unittest.TestCase):
    """Run the real app.js against the real server through a DOM shim."""

    @classmethod
    def setUpClass(cls):
        cls.harness_dir = tempfile.TemporaryDirectory()
        cls.harness = Path(cls.harness_dir.name) / "harness.js"
        cls.harness.write_text(HARNESS_JS, encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.harness_dir.cleanup()

    def setUp(self):
        self.live = LiveServer()
        self.addCleanup(self.live.stop)

    def run_harness(self, project_id: str, scenario: str) -> dict:
        proc = subprocess.run(
            [NODE, str(self.harness), str(APP_JS), self.live.base, project_id, scenario],
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        line = [ln for ln in proc.stdout.splitlines() if ln.startswith("REPORT:")]
        self.assertTrue(line, f"no report\nstdout={proc.stdout[-2000:]}\nstderr={proc.stderr[-2000:]}")
        report = json.loads(line[-1][len("REPORT:"):])
        self.assertNotIn("error", report, report.get("error"))
        return report

    def test_board_camera_behaviour(self):
        _, project = self.live.json("POST", "/api/projects", {"name": "js"})
        pid = project["id"]
        mem = self.live.memory
        mem.add_node(project_id=pid, type="text", text="a", x=100, y=100, w=300, h=200)
        mem.add_node(project_id=pid, type="text", text="b", x=900, y=600, w=300, h=200)
        report = self.run_harness(pid, "board")

        self.assertEqual(report["node_cards"], 2)
        self.assertTrue(report["home_bound"] and report["fit_bound"] and report["readout_bound"])
        self.assertTrue(report["pagehide_bound"])
        self.assertEqual(report["booted_readout"], "100%")

        # 30 wheel ticks clamp at 300% on screen and collapse to ONE write.
        self.assertEqual(report["wheel_readout"], "300%")
        self.assertIn("scale(3)", report["wheel_transform"])
        self.assertEqual(report["wheel_writes_during_burst"], 0)
        self.assertEqual(report["wheel_writes_after_debounce"], 1)
        self.assertEqual(report["server_after_wheel"], {"x": 0.0, "y": 0.0, "zoom": 3.0})

        # Fit frames both cards: bbox is (100,100)-(1200,800) in a 1000x800
        # viewport with 64 px of padding.
        zoom = min(3, max(0.25, min((1000 - 128) / 1100, (800 - 128) / 700)))
        self.assertAlmostEqual(report["server_after_fit"]["zoom"], zoom, places=6)
        self.assertAlmostEqual(report["server_after_fit"]["x"], (1000 - 1300 * zoom) / 2, places=4)
        self.assertAlmostEqual(report["server_after_fit"]["y"], (800 - 900 * zoom) / 2, places=4)
        self.assertEqual(report["fit_writes"], 1)
        self.assertEqual(report["fit_readout"], "79%")

        self.assertEqual(report["home_readout"], "100%")
        self.assertEqual(report["server_after_home"], {"x": 0.0, "y": 0.0, "zoom": 1.0})

        # pan persists, then a click on the readout homes it again
        self.assertIn("translate(260px, 130px)", report["pan_transform"])
        self.assertEqual(report["server_after_pan"], {"x": 260.0, "y": 130.0, "zoom": 1.0})
        self.assertEqual(report["server_after_readout_click"], {"x": 0.0, "y": 0.0, "zoom": 1.0})

        # dragging a card moves it in world units: 100 screen px at zoom z is
        # 100/z on the board.
        drag = report["drag"]
        self.assertAlmostEqual(drag["end_left"] - drag["start_left"], 100 / drag["zoom"], places=4)

    def test_switching_projects_does_not_lose_or_cross_the_pending_write(self):
        # Regression: the debounced write used to read state.projectId when it
        # fired, so a pan followed by a project switch inside 180 ms silently
        # dropped the pan (and could write it to the other project).
        _, a = self.live.json("POST", "/api/projects", {"name": "A"})
        _, b = self.live.json("POST", "/api/projects", {"name": "B"})
        self.live.json("POST", f"/api/projects/{a['id']}/camera", {"camera": {"x": 10, "y": 20, "zoom": 1}})
        self.live.json("POST", f"/api/projects/{b['id']}/camera", {"camera": {"x": -400, "y": -300, "zoom": 2}})

        report = self.run_harness(a["id"], "switch")
        self.assertEqual(report["after_pan_transform"], "translate(310px, 170px) scale(1)")
        self.assertEqual(report["on_B_transform"], "translate(-400px, -300px) scale(2)")

        _, got_a = self.live.json("GET", f"/api/projects/{a['id']}/camera")
        _, got_b = self.live.json("GET", f"/api/projects/{b['id']}/camera")
        self.assertEqual(got_a["camera"], {"x": 310.0, "y": 170.0, "zoom": 1.0})
        self.assertEqual(got_b["camera"], {"x": -400.0, "y": -300.0, "zoom": 2.0})
        for write in report["camera_writes"]:
            self.assertNotIn(b["id"], write["path"], "B was written while only A moved")


if __name__ == "__main__":
    unittest.main()
