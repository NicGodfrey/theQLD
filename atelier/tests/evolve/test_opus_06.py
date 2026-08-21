#!/usr/bin/env python3
"""Opus-06 — Round 12 (text layer) verification.

The round's promise is that type is *type*: a text layer is a node with
`type="text"`, its size lives in `meta`, and nothing about it is ever baked
into a raster. Four surfaces carry that promise, and each is pinned by
exercising it rather than by grepping for it:

* `loom.text_meta` — the clamp that used to live only in the browser.
* `Memory.add_node` / `update_node` — the `data` alias, coordinate coercion,
  and the meta write path that a text layer is the only UI writer of.
* `POST /api/projects/:id/nodes`, `POST /api/nodes/:id` and
  `GET /api/projects/:id/board`, over real HTTP against a
  `ThreadingHTTPServer` (demo lane only, no keys, no paid call).
* The live `atelier/web/app.js`, executed under node against that same server
  through a DOM shim, so "the board applies font_size as CSS on a .text-body
  div" is checked by reading the div. Those tests skip when no node binary is
  present; the string-level wiring checks always run.

Tests marked "pins current behaviour" assert what the tree does today, holes
included, so a later round notices when it changes them.
"""

from __future__ import annotations

import json
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
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WEB = ROOT / "atelier" / "web"
APP_JS = WEB / "app.js"
NODE = shutil.which("node")

# A DOM small enough to be honest about: no layout, no CSS cascade, no
# bubbling. It exists so the real app.js can boot, bind #textLayer and talk to
# the real server; every value the tests assert on is either read back over
# HTTP or read off the element app.js actually wrote to.
HARNESS_JS = r"""
const APP = process.argv[2];
const BASE = process.argv[3];
const PROJECT_NAME = process.argv[4];
const SCENARIO = process.argv[5];

const fetchLog = [];
const realFetch = globalThis.fetch;
globalThis.fetch = (path, opts = {}) => {
  fetchLog.push({ method: (opts.method || "GET").toUpperCase(), path, body: opts.body });
  return realFetch(path.startsWith("http") ? path : BASE + path, opts);
};
const writes = (frag) => fetchLog.filter((f) => f.method === "POST" && f.path.includes(frag));

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
  getBoundingClientRect() { return { left: 0, top: 0, width: this._cw, height: this._ch }; }
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
globalThis.window = { addEventListener: () => {} };
globalThis.alert = () => {};
let answer = null;
globalThis.prompt = () => answer;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
require(APP);

const cards = () => byId.board.children.filter((c) => c.className.split(" ").includes("node"));
const shot = () => cards().map((card) => {
  const body = card.children.find((k) => k.className === "text-body");
  return {
    class: card.className,
    title: card.title || "",
    left: card.style.left,
    top: card.style.top,
    text: body ? body.textContent : null,
    font_size: body ? body.style.fontSize : null,
    font_family: body ? (body.style.fontFamily || null) : null,
    letter_spacing: body ? (body.style.letterSpacing || null) : null,
    img_children: card.children.filter((k) => k.tagName === "img").length,
  };
});

async function openProject() {
  const button = byId.projectList.children.find((c) => c.textContent === PROJECT_NAME);
  if (!button) throw new Error("project " + PROJECT_NAME + " not in the rail");
  button.dispatch("click");
  await sleep(500);
}

async function make(spec) {
  answer = spec;
  await byId.textLayer.onclick();
}

async function create(report) {
  await openProject();
  await make("Headline · 32");
  report.plain = shot();
  await make("Tiny · 5");
  await make("Huge · 500");
  await make("Junk · not-a-number");
  await make("Tracked · 40 · Georgia, serif · 0.08em");
  report.all = shot();
  report.node_posts = writes("/nodes").map((w) => JSON.parse(w.body));
  report.imgs_on_board = walk(byId.board, []).filter((n) => n.tagName === "img").length;

  // Cancel must not mint a card: prompt() returning null used to fall through
  // to the "Headline · 32" default.
  const before = cards().length;
  answer = null;
  await byId.textLayer.onclick();
  await sleep(200);
  report.cards_after_cancel = cards().length;
  report.cards_before_cancel = before;
}

async function edit(report) {
  await openProject();
  report.before = shot();
  answer = "Edited · 48 · Georgia, serif · 0.02em";
  cards()[0].dispatch("dblclick");
  await sleep(500);
  report.after = shot();
  report.node_patches = writes("/api/nodes/").map((w) => JSON.parse(w.body));

  answer = null;
  cards()[0].dispatch("dblclick");
  await sleep(300);
  report.patches_after_cancel = writes("/api/nodes/").length;
  report.after_cancel = shot();
}

async function reload(report) {
  await openProject();
  report.rendered = shot();
  report.imgs_on_board = walk(byId.board, []).filter((n) => n.tagName === "img").length;
  report.artifact_fetches = fetchLog.filter((f) => f.path.includes("/api/artifacts/")).length;
}

(async () => {
  const report = {};
  await sleep(600);
  if (SCENARIO === "edit") await edit(report);
  else if (SCENARIO === "reload") await reload(report);
  else await create(report);
  console.log("REPORT:" + JSON.stringify(report));
})().catch((err) => {
  console.log("REPORT:" + JSON.stringify({ error: String((err && err.stack) || err) }));
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
    def app(self):
        return self.server.get_app()

    @property
    def memory(self):
        return self.app.memory

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

    def blob(self, path: str) -> tuple[int, bytes]:
        with urllib.request.urlopen(self.base + path, timeout=20) as resp:
            return resp.status, resp.read()


def _strict_json(text: str) -> bool:
    """True when text is JSON a browser would accept — no NaN / Infinity."""

    def reject(token):
        raise ValueError(token)

    try:
        json.loads(text, parse_constant=reject)
        return True
    except ValueError:
        return False


class TextMetaNormaliser(unittest.TestCase):
    """loom.text_meta — the clamp the browser used to own alone."""

    def meta(self, value):
        from atelier.helix.loom import text_meta

        return text_meta(value)

    def test_font_size_is_clamped_to_the_readable_band(self):
        self.assertEqual(self.meta({"font_size": 32})["font_size"], 32)
        self.assertEqual(self.meta({"font_size": 99999})["font_size"], 96)
        self.assertEqual(self.meta({"font_size": 1})["font_size"], 12)
        self.assertEqual(self.meta({"font_size": -40})["font_size"], 12)
        self.assertEqual(self.meta({"font_size": "48"})["font_size"], 48)
        self.assertEqual(self.meta({"font_size": 33.5})["font_size"], 33.5)

    def test_the_clamp_never_calls_a_312_only_builtin(self):
        """Clamping to a bound hands back the int bound, and `int.is_integer()`
        only exists on 3.12+. The local gate runs 3.12 and saw nothing; the
        workflow pins 3.11, where six of these tests died with
        `AttributeError: 'int' object has no attribute 'is_integer'`."""
        from atelier.helix.loom import FONT_SIZE_MAX, FONT_SIZE_MIN

        self.assertIsInstance(min(FONT_SIZE_MAX, max(FONT_SIZE_MIN, 99999.0)), int)
        src = (ROOT / "atelier" / "helix" / "loom.py").read_text(encoding="utf-8")
        for line in src.splitlines():
            code = line.split("#", 1)[0]
            if ".is_integer()" in code:
                receiver = code.split(".is_integer()")[0]
                self.assertTrue(receiver.rstrip().endswith("float(size)"), line.strip())

    def test_a_font_size_that_is_not_a_number_is_dropped(self):
        for bad in ("48px; background: red", "", None, [40], {"px": 40}, True, float("nan"), float("inf")):
            self.assertNotIn("font_size", self.meta({"font_size": bad}), repr(bad))

    def test_font_family_must_look_like_a_family_list(self):
        for good in ("Georgia, serif", '"Helvetica Neue", sans-serif', "ui-sans-serif", "Iowan Old Style"):
            self.assertEqual(self.meta({"font_family": good})["font_family"], good)
        # a ';' '{' '(' or newline would let the value close the declaration
        # it is pasted into — refused rather than mangled into something else
        for bad in (
            "serif; background: url(x)",
            "serif}\n.node{display:none",
            "expression(alert(1))",
            "serif</style><script>",
            "x" * 200,
            42,
            None,
            {"name": "serif"},
        ):
            self.assertNotIn("font_family", self.meta({"font_family": bad}), repr(bad))

    def test_letter_spacing_must_be_a_css_length(self):
        for good in ("0.08em", "-1px", "2rem", "normal", "1.5pt", "0.5ch"):
            self.assertEqual(self.meta({"letter_spacing": good})["letter_spacing"], good)
        # a unitless number is ignored by the browser, so storing it would only
        # pretend the tracking had been applied
        for bad in ("2", 2, "2 px", "2px;color:red", "wide", "", None, "99999999px"):
            self.assertNotIn("letter_spacing", self.meta({"letter_spacing": bad}), repr(bad))

    def test_keys_the_board_does_not_read_pass_through(self):
        out = self.meta({"layer": "text", "font_size": 200, "author": "nic", "n": 3})
        self.assertEqual(out, {"layer": "text", "font_size": 96, "author": "nic", "n": 3})

    def test_meta_that_is_not_a_dict_becomes_an_empty_dict(self):
        for bad in (None, "", "not-a-dict", [1, 2], 7, True):
            self.assertEqual(self.meta(bad), {})

    def test_the_caller_dict_is_not_mutated(self):
        source = {"font_size": 400, "font_family": "serif;"}
        self.meta(source)
        self.assertEqual(source, {"font_size": 400, "font_family": "serif;"})


class TextNodeStore(unittest.TestCase):
    """Memory.add_node / update_node — the alias, the coercion, the meta write."""

    def setUp(self):
        from atelier.helix.store import Memory

        self.tmp = tempfile.TemporaryDirectory()
        self.mem = Memory(Path(self.tmp.name) / "helix.sqlite3")
        self.project = self.mem.create_project("Text")
        self.pid = self.project["id"]

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def add(self, **kwargs):
        return self.mem.add_node(project_id=self.pid, **kwargs)

    def test_a_text_node_never_points_at_an_artifact(self):
        node = self.add(type="text", text="Headline", meta={"layer": "text", "font_size": 32})
        self.assertEqual(node["type"], "text")
        self.assertIsNone(node["artifact_id"])
        self.assertEqual(node["meta"], {"layer": "text", "font_size": 32})

    def test_data_is_an_alias_for_text_on_both_writes(self):
        node = self.add(type="text", data="From data")
        self.assertEqual(node["text"], "From data")
        edited = self.mem.update_node(node["id"], data="Edited")
        self.assertEqual(edited["text"], "Edited")
        # an explicit text wins, and the stray alias is not smuggled into SQL
        both = self.add(type="text", text="real", data="ignored")
        self.assertEqual(both["text"], "real")
        self.assertEqual(self.mem.update_node(both["id"], text="A", data="B")["text"], "A")
        # a non-string alias is serialised rather than dropped
        self.assertEqual(self.add(type="text", data={"a": 1})["text"], '{"a": 1}')

    def test_font_size_is_clamped_on_the_way_in(self):
        node = self.add(type="text", text="Huge", meta={"layer": "text", "font_size": 99999})
        self.assertEqual(node["meta"]["font_size"], 96)
        self.assertEqual(self.mem.get_node(node["id"])["meta"]["font_size"], 96)
        edited = self.mem.update_node(node["id"], meta={"layer": "text", "font_size": 0.5})
        self.assertEqual(edited["meta"]["font_size"], 12)

    def test_a_junk_meta_can_never_brick_the_board(self):
        # Regression: update_node stored a raw string verbatim, so every later
        # list_nodes raised inside json.loads and 500'd the whole board.
        node = self.add(type="text", text="T", meta={"font_size": 20})
        self.assertEqual(self.mem.update_node(node["id"], meta="not json")["meta"], {})
        self.assertEqual(self.mem.list_nodes(self.pid)[0]["meta"], {})
        self.assertEqual(self.mem.update_node(node["id"], meta='{"font_size": 40}')["meta"], {"font_size": 40})
        self.assertEqual(self.mem.update_node(node["id"], meta=[1, 2])["meta"], {})
        for bad in (None, 7, True, "[]"):
            self.assertEqual(self.add(type="text", text="x", meta=bad)["meta"], {}, repr(bad))

    def test_a_row_poisoned_before_the_fix_still_reads(self):
        node = self.add(type="text", text="old", meta={"font_size": 20})
        self.mem.conn.execute("UPDATE nodes SET meta=? WHERE id=?", ("not json", node["id"]))
        self.mem.conn.commit()
        self.assertEqual(self.mem.get_node(node["id"])["meta"], {})
        self.assertEqual(self.mem.list_nodes(self.pid)[0]["meta"], {})

    def test_coordinates_are_always_finite_numbers(self):
        # A null or NaN lands as NULL against a NOT NULL column and raises
        # mid-write; an Infinity survives and then serialises as a bare
        # Infinity token, which no browser will parse.
        for bad in (None, "abc", float("nan"), float("inf"), float("-inf"), [1], {"x": 1}, "1e999"):
            node = self.add(type="text", text="c", x=bad, y=bad, w=bad, h=bad, z=bad)
            self.assertEqual((node["x"], node["y"], node["w"], node["h"], node["z"]),
                             (80.0, 80.0, 320.0, 240.0, 0), repr(bad))
        self.assertTrue(_strict_json(json.dumps(self.mem.list_nodes(self.pid))))
        good = self.add(type="text", text="c", x="120", y=44.5, w=300, h=160, z=2)
        self.assertEqual((good["x"], good["y"], good["w"], good["h"], good["z"]), (120.0, 44.5, 300.0, 160.0, 2))

    def test_a_card_cannot_be_wider_than_the_board_span(self):
        # 1e308 is finite, so the Infinity guard was not enough.
        huge = self.add(type="image", w=1e308, h=1e308)
        self.assertEqual((huge["w"], huge["h"]), (2400.0, 2400.0))
        tiny = self.add(type="image", w=1, h=1)
        self.assertEqual((tiny["w"], tiny["h"]), (40.0, 40.0))
        moved = self.mem.update_node(huge["id"], w=1e308, h=8)
        self.assertEqual((moved["w"], moved["h"]), (2400.0, 40.0))

    def test_a_96px_headline_gets_a_taller_card(self):
        node = self.add(type="text", text="Huge", h=120, meta={"layer": "text", "font_size": 96})
        self.assertGreaterEqual(node["h"], 96 * 1.6 + 24)
        self.assertLessEqual(node["h"], 2400.0)

    def test_a_junk_coordinate_update_is_a_no_op_not_a_jump_home(self):
        node = self.add(type="text", text="c", x=500, y=400)
        moved = self.mem.update_node(node["id"], x="nope", y=float("inf"))
        self.assertEqual((moved["x"], moved["y"]), (500.0, 400.0))
        self.assertEqual(self.mem.update_node(node["id"], x=10)["x"], 10.0)

    def test_update_of_a_missing_node_returns_none(self):
        self.assertIsNone(self.mem.update_node("deadbeef", x=1))
        self.assertIsNone(self.mem.get_node("deadbeef"))

    def test_type_and_artifact_id_are_not_patchable(self):
        # pins current behaviour: update_node's allow-list keeps a text layer
        # from being re-pointed at someone else's artifact.
        node = self.add(type="text", text="T")
        patched = self.mem.update_node(node["id"], type="image", artifact_id="stolen", project_id="other")
        self.assertEqual(patched["type"], "text")
        self.assertIsNone(patched["artifact_id"])
        self.assertEqual(patched["project_id"], self.pid)


class TextNodeRoute(unittest.TestCase):
    """POST /api/projects/:id/nodes, POST /api/nodes/:id, GET .../board."""

    @classmethod
    def setUpClass(cls):
        cls.live = LiveServer()

    @classmethod
    def tearDownClass(cls):
        cls.live.stop()

    def project(self, name="R12"):
        return self.live.json("POST", "/api/projects", {"name": name})[1]

    def test_a_text_node_mints_no_image(self):
        project = self.project("R12-plain")
        before = sorted(p.name for p in self.live.app.artifacts.glob("*"))
        status, node = self.live.json(
            "POST",
            f"/api/projects/{project['id']}/nodes",
            {"type": "text", "text": "Headline", "x": 120, "y": 120,
             "meta": {"layer": "text", "font_size": 32}},
        )
        self.assertEqual(status, 201)
        self.assertEqual(node["type"], "text")
        self.assertIsNone(node["artifact_id"])
        self.assertEqual(node["meta"], {"layer": "text", "font_size": 32})
        self.assertEqual(sorted(p.name for p in self.live.app.artifacts.glob("*")), before)
        rows = self.live.memory.conn.execute(
            "SELECT COUNT(*) FROM artifacts WHERE project_id=?", (project["id"],)
        ).fetchone()[0]
        self.assertEqual(rows, 0)

    def test_a_refresh_rehydrates_type_text_and_size(self):
        project = self.project("R12-refresh")
        _, made = self.live.json(
            "POST",
            f"/api/projects/{project['id']}/nodes",
            {"type": "text", "text": "Quiet, precise",
             "meta": {"layer": "text", "font_size": 44, "font_family": "Georgia, serif",
                      "letter_spacing": "0.08em"}},
        )
        status, board = self.live.json("GET", f"/api/projects/{project['id']}/board")
        self.assertEqual(status, 200)
        node = [n for n in board["nodes"] if n["id"] == made["id"]][0]
        self.assertEqual(node["type"], "text")
        self.assertEqual(node["text"], "Quiet, precise")
        self.assertIsNone(node["artifact_id"])
        self.assertEqual(node["meta"], {"layer": "text", "font_size": 44,
                                        "font_family": "Georgia, serif", "letter_spacing": "0.08em"})
        # and again after the process forgets everything it had in memory
        self.live.server.reset_app()
        _, again = self.live.json("GET", f"/api/projects/{project['id']}/board")
        self.assertEqual([n for n in again["nodes"] if n["id"] == made["id"]][0]["meta"]["font_size"], 44)

    def test_data_is_an_alias_for_text_over_http(self):
        project = self.project("R12-alias")
        _, made = self.live.json(
            "POST", f"/api/projects/{project['id']}/nodes", {"type": "text", "data": "From data"}
        )
        self.assertEqual(made["text"], "From data")
        status, edited = self.live.json("POST", f"/api/nodes/{made['id']}", {"data": "Edited"})
        self.assertEqual(status, 200)
        self.assertEqual(edited["text"], "Edited")
        _, board = self.live.json("GET", f"/api/projects/{project['id']}/board")
        self.assertEqual(board["nodes"][0]["text"], "Edited")

    def test_the_server_clamps_font_size_too(self):
        # The browser clamped 12–96; curl, a bookmarklet and any future client
        # did not, and the stored number is what an export renderer will read.
        project = self.project("R12-clamp")
        for asked, kept in ((99999, 96), (2, 12), (-9, 12), (40, 40)):
            _, node = self.live.json(
                "POST", f"/api/projects/{project['id']}/nodes",
                {"type": "text", "text": "T", "meta": {"layer": "text", "font_size": asked}},
            )
            self.assertEqual(node["meta"]["font_size"], kept, asked)
        _, junk = self.live.json(
            "POST", f"/api/projects/{project['id']}/nodes",
            {"type": "text", "text": "T",
             "meta": {"layer": "text", "font_size": "40px; background: red",
                      "font_family": "serif; position: fixed", "letter_spacing": "9px)"}},
        )
        self.assertEqual(junk["meta"], {"layer": "text"})

    def test_nodes_on_a_missing_project_are_404(self):
        # Regression: this used to answer 201 and write a card onto a board
        # that GET /board then 404s on forever.
        status, body = self.live.json(
            "POST", "/api/projects/deadbeef/nodes", {"type": "text", "text": "orphan"}
        )
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "missing project")
        self.assertEqual(
            self.live.memory.conn.execute(
                "SELECT COUNT(*) FROM nodes WHERE project_id=?", ("deadbeef",)
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            self.live.memory.conn.execute(
                "SELECT COUNT(*) FROM undo_log WHERE project_id=?", ("deadbeef",)
            ).fetchone()[0],
            0,
        )

    def test_threads_on_a_missing_project_are_404(self):
        status, body = self.live.json(
            "POST", "/api/projects/deadbeef/threads", {"topic": "orphan"}
        )
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "missing project")
        self.assertEqual(
            self.live.memory.conn.execute(
                "SELECT COUNT(*) FROM threads WHERE project_id=?", ("deadbeef",)
            ).fetchone()[0],
            0,
        )

    def test_patching_a_missing_node_is_404(self):
        status, body = self.live.json("POST", "/api/nodes/deadbeef", {"text": "x"})
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "missing node")

    def test_no_body_can_make_the_board_unparseable(self):
        project = self.project("R12-poison")
        bystander = self.project("R12-bystander")
        self.live.json("POST", f"/api/projects/{bystander['id']}/nodes", {"type": "text", "text": "ok"})
        _, node = self.live.json("POST", f"/api/projects/{project['id']}/nodes", {"type": "text", "text": "T"})
        for literal in (
            b'{"type": "text", "text": "n", "x": NaN, "y": Infinity}',
            b'{"type": "text", "text": "n", "y": null}',
            b'{"type": "text", "text": "n", "w": "1e999"}',
            b'{"type": "text", "text": "n", "meta": "not-a-dict"}',
        ):
            status, text = self.live.raw("POST", f"/api/projects/{project['id']}/nodes", literal)
            self.assertEqual(status, 201, f"{literal!r} -> {text}")
            self.assertTrue(_strict_json(text), f"{literal!r} -> {text}")
        for literal in (b'{"meta": "not json"}', b'{"x": Infinity}', b'{"text": null}'):
            status, text = self.live.raw("POST", f"/api/nodes/{node['id']}", literal)
            self.assertEqual(status, 200, f"{literal!r} -> {text}")
            self.assertTrue(_strict_json(text), f"{literal!r} -> {text}")
        for path in (f"/api/projects/{project['id']}/board", f"/api/projects/{bystander['id']}/board"):
            status, body = self.live.raw("GET", path)
            self.assertEqual(status, 200, path)
            self.assertTrue(_strict_json(body), body)
        status, zipped = self.live.blob(f"/api/projects/{project['id']}/export")
        self.assertEqual((status, zipped[:2]), (200, b"PK"))

    def test_an_unknown_type_still_lands_as_a_node(self):
        # pins current behaviour: type is a free string. The board renders
        # anything that is not an image-with-artifact through the text branch,
        # and the value is only ever compared, never interpolated into markup.
        project = self.project("R12-type")
        _, node = self.live.json(
            "POST", f"/api/projects/{project['id']}/nodes",
            {"type": "<script>alert(1)</script>", "text": "x"},
        )
        self.assertEqual(node["type"], "<script>alert(1)</script>")
        _, empty = self.live.json("POST", f"/api/projects/{project['id']}/nodes", {"text": "x"})
        self.assertEqual(empty["type"], "text")


class ConductorTextWeave(unittest.TestCase):
    """A weave item of kind=text pins type, not pixels."""

    def setUp(self):
        from atelier.helix.conductor import Conductor
        from atelier.helix.keyring import Keyring
        from atelier.helix.store import Memory

        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.arts = root / "artifacts"
        self.arts.mkdir()
        self.mem = Memory(root / "helix.sqlite3")
        self.project = self.mem.create_project("Weave")
        self.thread = self.mem.create_thread(self.project["id"])
        self.cond = Conductor(self.mem, Keyring(), self.arts)

    def tearDown(self):
        self.mem.close()
        self.tmp.cleanup()

    def weave(self, items):
        from atelier.helix.spokes.base import ChatResult, DemoSpoke

        plan = {
            "mode": "fast",
            "intent": "typography",
            "route": {"provider": "demo", "model": "demo-conductor", "capability": "image"},
            "weave": items,
        }

        class PlanSpoke(DemoSpoke):
            def chat(self, messages, model="demo-conductor", **kwargs):
                return ChatResult(text=json.dumps(plan), provider="demo", model=model)

        with mock.patch("atelier.helix.conductor.build_spoke", side_effect=lambda n, k: PlanSpoke()):
            return self.cond.run(
                project_id=self.project["id"],
                thread_id=self.thread["id"],
                prompt="type only",
                provider="demo",
            )

    def test_kind_text_becomes_a_text_node_and_kind_note_stays_a_note(self):
        result = self.weave([
            {"kind": "text", "prompt": "HELIX", "count": 1},
            {"kind": "note", "prompt": "remember the grid", "count": 1},
        ])
        kinds = [(n["type"], n["text"], n["artifact_id"], n["meta"]) for n in result["nodes"]]
        self.assertEqual(kinds, [
            ("text", "HELIX", None, {"layer": "text"}),
            ("note", "remember the grid", None, {}),
        ])
        self.assertEqual(result["artifacts"], [])
        self.assertEqual(sorted(self.arts.iterdir()), [])
        self.assertEqual(
            self.mem.conn.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0], 0
        )

    def test_a_text_only_plan_is_never_billed_as_an_image(self):
        self.weave([{"kind": "text", "prompt": "HELIX", "count": 1}])
        kinds = {u["unit_kind"] for u in self.mem.list_usage()}
        self.assertNotIn("images", kinds)

    def test_an_image_item_alongside_text_still_rasters(self):
        result = self.weave([
            {"kind": "text", "prompt": "HELIX", "count": 1},
            {"kind": "image", "prompt": "navy poster", "count": 1},
        ])
        by_type = {n["type"]: n for n in result["nodes"]}
        self.assertIsNone(by_type["text"]["artifact_id"])
        self.assertIsNotNone(by_type["image"]["artifact_id"])
        self.assertEqual(len(result["artifacts"]), 1)
        self.assertEqual([p.suffix for p in self.arts.iterdir()], [".svg"])


class TextLayerWiring(unittest.TestCase):
    """Cheap string gate — the node tests below prove the behaviour, but these
    still run on a machine with no JS runtime."""

    def setUp(self):
        self.longMessage = False  # these haystacks are whole files
        self.html = (WEB / "index.html").read_text(encoding="utf-8")
        self.css = (WEB / "styles.css").read_text(encoding="utf-8")
        self.app_js = APP_JS.read_text(encoding="utf-8")

    def in_js(self, needle):
        self.assertIn(needle, self.app_js, f"app.js no longer contains: {needle}")

    def test_the_button_and_its_card_class_exist(self):
        self.assertIn('id="textLayer"', self.html)
        self.assertIn(".text-layer", self.css)
        self.assertIn(".text-body", self.css)
        self.in_js('document.getElementById("textLayer").onclick')
        self.in_js('type: "text"')

    def test_size_is_parsed_off_the_prompt_and_clamped(self):
        self.in_js("function parseTextSpec(raw, current)")
        self.in_js('.split("·")')
        self.in_js("Math.min(96, Math.max(12, size))")
        self.in_js("if (raw === null) return;")

    def test_the_board_renders_type_as_css_not_as_an_image(self):
        self.in_js('class: "text-body"')
        self.in_js("body.style.fontSize = size + \"px\"")
        self.in_js("body.style.fontFamily = String(meta.font_family)")
        self.in_js("body.style.letterSpacing = String(meta.letter_spacing)")
        self.in_js("Math.min(96, Math.max(12, Number(meta.font_size) || 22))")
        # the image branch is the only one that ever asks for an artifact
        # (inline src, download, designer export). Text stays off that path.
        self.assertEqual(self.app_js.count("/api/artifacts/${node.artifact_id}"), 3)
        self.assertIn("/export?fmt=png", self.app_js)

    def test_a_text_card_can_be_edited_after_it_is_placed(self):
        self.in_js("async function editTextNode(node)")
        self.in_js('card.addEventListener("dblclick"')
        self.in_js('api(`/api/nodes/${node.id}`, { method: "POST", body: { text: spec.text, meta: spec.meta } })')


@unittest.skipUnless(NODE, "no node binary — JS behaviour tests skipped")
class TextLayerJs(unittest.TestCase):
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
        _, self.project = self.live.json("POST", "/api/projects", {"name": "R12js"})

    def run_harness(self, scenario: str) -> dict:
        proc = subprocess.run(
            [NODE, str(self.harness), str(APP_JS), self.live.base, "R12js", scenario],
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

    def board(self):
        return self.live.json("GET", f"/api/projects/{self.project['id']}/board")[1]["nodes"]

    def test_the_button_writes_a_text_node_and_the_board_draws_it_as_css(self):
        report = self.run_harness("create")

        self.assertEqual(len(report["plain"]), 1)
        card = report["plain"][0]
        self.assertIn("note", card["class"].split(" "))
        self.assertIn("text-layer", card["class"].split(" "))
        self.assertEqual(card["text"], "Headline")
        self.assertEqual(card["font_size"], "32px")
        self.assertEqual(card["img_children"], 0)
        self.assertEqual(card["left"], "120px")

        # "Headline · 32" is the contract; the tail is optional
        bodies = report["node_posts"]
        self.assertEqual(bodies[0], {
            "type": "text", "text": "Headline", "x": 120, "y": 120,
            "meta": {"layer": "text", "font_size": 32},
        })
        self.assertEqual([b["meta"]["font_size"] for b in bodies], [32, 12, 96, 32, 40])
        self.assertEqual(bodies[3]["text"], "Junk")
        self.assertEqual(bodies[4]["meta"], {
            "layer": "text", "font_size": 40,
            "font_family": "Georgia, serif", "letter_spacing": "0.08em",
        })

        rendered = {c["text"]: c for c in report["all"]}
        self.assertEqual(rendered["Tiny"]["font_size"], "12px")
        self.assertEqual(rendered["Huge"]["font_size"], "96px")
        self.assertEqual(rendered["Junk"]["font_size"], "32px")
        self.assertEqual(rendered["Tracked"]["font_family"], "Georgia, serif")
        self.assertEqual(rendered["Tracked"]["letter_spacing"], "0.08em")
        self.assertIsNone(rendered["Headline"]["font_family"])

        # nothing on this board is a raster
        self.assertEqual(report["imgs_on_board"], 0)
        self.assertTrue(all(n["artifact_id"] is None and n["type"] == "text" for n in self.board()))
        self.assertEqual(sorted(p.name for p in self.live.app.artifacts.glob("*")), [])

        # Cancel used to fall through to the default and mint a card anyway
        self.assertEqual(report["cards_after_cancel"], report["cards_before_cancel"])
        self.assertEqual(len(self.board()), 5)

    def test_a_placed_card_is_editable_in_place(self):
        self.live.json(
            "POST", f"/api/projects/{self.project['id']}/nodes",
            {"type": "text", "text": "Before", "meta": {"layer": "text", "font_size": 22}},
        )
        report = self.run_harness("edit")

        self.assertEqual(report["before"][0]["text"], "Before")
        self.assertEqual(report["before"][0]["title"], "Double-click to edit")
        self.assertEqual(report["after"][0]["text"], "Edited")
        self.assertEqual(report["after"][0]["font_size"], "48px")
        self.assertEqual(report["after"][0]["letter_spacing"], "0.02em")
        self.assertEqual(report["node_patches"], [{
            "text": "Edited",
            "meta": {"layer": "text", "font_size": 48,
                     "font_family": "Georgia, serif", "letter_spacing": "0.02em"},
        }])
        self.assertEqual(report["patches_after_cancel"], 1)
        self.assertEqual(report["after_cancel"][0]["text"], "Edited")

        node = self.board()[0]
        self.assertEqual(node["text"], "Edited")
        self.assertEqual(node["type"], "text")
        self.assertIsNone(node["artifact_id"])
        self.assertEqual(node["meta"]["font_size"], 48)

    def test_a_fresh_page_load_rehydrates_the_type(self):
        for text, size in (("Headline", 64), ("Caption", 14)):
            self.live.json(
                "POST", f"/api/projects/{self.project['id']}/nodes",
                {"type": "text", "text": text,
                 "meta": {"layer": "text", "font_size": size, "letter_spacing": "0.04em"}},
            )
        report = self.run_harness("reload")
        rendered = {c["text"]: c for c in report["rendered"]}
        self.assertEqual(rendered["Headline"]["font_size"], "64px")
        self.assertEqual(rendered["Caption"]["font_size"], "14px")
        self.assertEqual(rendered["Caption"]["letter_spacing"], "0.04em")
        self.assertEqual(report["imgs_on_board"], 0)
        self.assertEqual(report["artifact_fetches"], 0)


if __name__ == "__main__":
    unittest.main()
