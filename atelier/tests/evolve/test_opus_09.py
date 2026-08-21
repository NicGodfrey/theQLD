#!/usr/bin/env python3
"""Opus-09 — Round 18 (live contract) verification.

`CONTRACT.md` has to describe *this* process, not `research/fable5/06-board-ui`.
Two independent measures, because a markdown table can agree with itself:

1. A real `ast` walk of the route tests inside `server.Handler._do_GET` /
   `_do_POST` / `_do_DELETE`, reduced to `VERB /api/projects/*/board` shapes,
   set-compared against the table in both directions. A route added to the
   server without a row — or a row with no route — fails here.
2. Real requests over a real socket to a real `ThreadingHTTPServer` on the demo
   lane, with a throwaway runtime dir. No network, no key read, no paid call;
   every bind takes an ephemeral port and is shut down in the same test.
"""

from __future__ import annotations

import ast
import base64
import json
import os
import re
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

CONTRACT = ROOT / "atelier" / "research" / "evolve" / "CONTRACT.md"
SERVER = ROOT / "atelier" / "server.py"
WEB_JS = ROOT / "atelier" / "web" / "app.js"
BOARD_UI = ROOT / "atelier" / "research" / "fable5" / "06-board-ui"

VERBS = ("GET", "POST", "DELETE", "PATCH", "PUT", "HEAD", "OPTIONS")

# The GET handler's last statement is `_send_web(self, path.lstrip("/"))` —
# a fallthrough, not an `if`, so the AST walk cannot see it. Documented as `/*`.
STATIC_FALLTHROUGH = "/*"


# --------------------------------------------------------------------------
# What the router actually serves, read out of the source
# --------------------------------------------------------------------------


def _handler_class() -> ast.ClassDef:
    tree = ast.parse(SERVER.read_text(encoding="utf-8"))
    return next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "Handler")


def _handler_methods() -> dict[str, str]:
    """`{"GET": "_do_GET", "PATCH": "alias:POST", ...}` for every `do_*`."""
    out: dict[str, str] = {}
    for node in _handler_class().body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("do_"):
            continue
        verb = node.name[len("do_") :]
        # `do_PATCH` is a one-line alias: `self.do_POST()`.
        if len(node.body) == 1 and isinstance(node.body[0], ast.Expr):
            call = node.body[0].value
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr.startswith("do_")
            ):
                out[verb] = f"alias:{call.func.attr[len('do_') :]}"
                continue
        out[verb] = f"_do_{verb}"
    return out


def _conditions(test: ast.expr) -> list[ast.expr]:
    if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And):
        return [c for v in test.values for c in _conditions(v)]
    return [test]


def _const_strs(node: ast.expr) -> list[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
        return [e.value for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
    return []


def _is_parts_prefix(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "parts"
        and isinstance(node.slice, ast.Slice)
    )


def _parts_index(node: ast.expr) -> int | None:
    if (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "parts"
        and isinstance(node.slice, ast.Constant)
        and isinstance(node.slice.value, int)
    ):
        return node.slice.value
    return None


def _routes_in(func: ast.FunctionDef) -> tuple[set[str], set[str], str]:
    """Reduce one `_do_*` body to (api shapes, static paths, 404 sentinel text)."""
    api: set[str] = set()
    static: set[str] = set()
    sentinel = ""
    for node in ast.walk(func):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value.startswith("unknown "):
                sentinel = node.value
    for stmt in func.body:
        if not isinstance(stmt, ast.If):
            continue
        prefix: list[str] = []
        length: int | None = None
        seg: dict[int, str] = {}
        literals: list[str] = []
        prefixes: list[str] = []
        for cond in _conditions(stmt.test):
            if isinstance(cond, ast.Compare) and len(cond.ops) == 1:
                left, op, right = cond.left, cond.ops[0], cond.comparators[0]
                if isinstance(left, ast.Name) and left.id == "path":
                    if isinstance(op, (ast.Eq, ast.In)):
                        literals.extend(_const_strs(right))
                elif _is_parts_prefix(left) and isinstance(op, ast.Eq):
                    prefix = _const_strs(right)
                elif isinstance(op, ast.Eq) and _parts_index(left) is not None:
                    values = _const_strs(right)
                    if values:
                        seg[_parts_index(left)] = values[0]
                elif (
                    isinstance(left, ast.Call)
                    and isinstance(left.func, ast.Name)
                    and left.func.id == "len"
                    and isinstance(op, ast.Eq)
                    and isinstance(right, ast.Constant)
                ):
                    length = right.value
            elif (
                isinstance(cond, ast.Call)
                and isinstance(cond.func, ast.Attribute)
                and cond.func.attr == "startswith"
                and isinstance(cond.func.value, ast.Name)
                and cond.func.value.id == "path"
            ):
                prefixes.extend(_const_strs(cond.args[0]) if cond.args else [])

        for raw in literals:
            (api if raw.startswith("/api") else static).add(raw)
        for raw in prefixes:
            if raw != "/api/":  # the /api/ prefix guard is the 404 sentinel
                static.add(raw.rstrip("/") + "/*")
        if prefix[:1] == ["api"] and length:
            shape = "/" + "/".join(prefix)
            for i in range(len(prefix), length):
                shape += "/" + seg.get(i, "*")
            api.add(shape)
    return api, static, sentinel


def live_surface() -> tuple[dict[str, set[str]], set[str], dict[str, str]]:
    """(api routes by verb, static paths, the 404 sentinel each verb returns)."""
    bodies = {n.name: n for n in _handler_class().body if isinstance(n, ast.FunctionDef)}
    methods = _handler_methods()
    api: dict[str, set[str]] = {}
    static: set[str] = set()
    sentinels: dict[str, str] = {}
    for verb, target in methods.items():
        if target.startswith("alias:"):
            continue
        routes, statics, sentinel = _routes_in(bodies[target])
        api[verb] = routes
        static |= statics
        sentinels[verb] = sentinel
    for verb, target in methods.items():
        if target.startswith("alias:"):
            source = target.split(":", 1)[1]
            api[verb] = set(api[source])
            sentinels[verb] = sentinels[source]
    return api, static, sentinels


# --------------------------------------------------------------------------
# What the contract says
# --------------------------------------------------------------------------

_ROW = re.compile(r"^\|(.+)\|$")
_TICKED = re.compile(r"`([^`]+)`")


def contract_rows() -> list[tuple[str, str, str]]:
    """`(verb, path, notes)` for every markdown row whose first cell is a verb."""
    rows = []
    for line in CONTRACT.read_text(encoding="utf-8").splitlines():
        match = _ROW.match(line.strip())
        if not match:
            continue
        cells = [c.strip() for c in match.group(1).split("|")]
        if len(cells) < 2 or cells[0] not in VERBS:
            continue
        for path in _TICKED.findall(cells[1]):
            rows.append((cells[0], path, cells[2] if len(cells) > 2 else ""))
    return rows


def documented_surface() -> tuple[dict[str, set[str]], set[str]]:
    api: dict[str, set[str]] = {}
    static: set[str] = set()
    for verb, path, _ in contract_rows():
        clean = re.sub(r":[a-z_]+", "*", path.split("?")[0])
        if clean.startswith("/api"):
            api.setdefault(verb, set()).add(clean)
        else:
            static.add(clean)
    return api, static


class RouterMatchesTheTable(unittest.TestCase):
    """Claim 3, done as a set comparison rather than five substring greps."""

    @classmethod
    def setUpClass(cls):
        cls.live_api, cls.live_static, cls.sentinels = live_surface()
        cls.doc_api, cls.doc_static = documented_surface()
        cls.own_rows = {v for v, t in _handler_methods().items() if not t.startswith("alias:")}

    def test_the_walk_found_a_real_router(self):
        # Guard the guard: if the AST reduction silently stops matching, the
        # set comparisons below would pass by both sides being empty.
        self.assertGreaterEqual(len(self.live_api.get("GET", ())), 12)
        self.assertGreaterEqual(len(self.live_api.get("POST", ())), 10)
        self.assertIn("/api/health", self.live_api["GET"])
        self.assertIn("/api/projects/*/board", self.live_api["GET"])
        self.assertIn("/api/threads/*/run", self.live_api["POST"])
        self.assertIn("/api/nodes/*", self.live_api["DELETE"])

    def test_every_live_route_has_a_row(self):
        # PATCH has no rows of its own — it is an alias, pinned by the prose
        # rule below rather than by 11 duplicated lines in the table.
        for verb in self.own_rows:
            missing = self.live_api[verb] - self.doc_api.get(verb, set())
            self.assertEqual(missing, set(), f"{verb} routes served but not in CONTRACT.md: {sorted(missing)}")

    def test_every_row_is_a_live_route(self):
        for verb, routes in self.doc_api.items():
            dead = routes - self.live_api.get(verb, set())
            self.assertEqual(dead, set(), f"{verb} rows in CONTRACT.md with no route: {sorted(dead)}")
        self.assertEqual(set(self.doc_api), self.own_rows)

    def test_patch_is_documented_as_an_alias_of_post(self):
        methods = _handler_methods()
        self.assertEqual(methods.get("PATCH"), "alias:POST")
        self.assertEqual(self.live_api["PATCH"], self.live_api["POST"])
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("`do_PATCH` is `do_POST`", text)
        self.assertIn("also answers PATCH", text)

    def test_every_verb_the_handler_answers_is_named(self):
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertEqual(set(_handler_methods()), {"GET", "POST", "DELETE", "PATCH"})
        for verb in _handler_methods():
            self.assertIn(verb, text, f"{verb} is served and never named in CONTRACT.md")
        for verb in ("PUT", "OPTIONS", "HEAD", "TRACE"):
            self.assertNotIn(verb, _handler_methods())
            self.assertIn(verb, text, f"{verb} 501s and CONTRACT.md never says so")
        self.assertIn("501", text)

    def test_static_surface_is_documented(self):
        self.assertIn(STATIC_FALLTHROUGH, self.doc_static)
        self.assertEqual(
            self.doc_static - {STATIC_FALLTHROUGH},
            self.live_static,
            "the static surface in CONTRACT.md is not what _do_GET serves",
        )

    def test_unmatched_api_paths_are_documented_as_404(self):
        self.assertEqual(
            self.sentinels,
            {"GET": "unknown GET", "POST": "unknown POST",
             "DELETE": "unknown DELETE", "PATCH": "unknown POST"},
        )
        text = CONTRACT.read_text(encoding="utf-8")
        for sentinel in set(self.sentinels.values()):
            self.assertIn(sentinel, text)


class ContractIsLiveNotResearch(unittest.TestCase):
    """Claims 1 and 2."""

    def setUp(self):
        self.contract = CONTRACT.read_text(encoding="utf-8")
        self.server = SERVER.read_text(encoding="utf-8")
        self.app = WEB_JS.read_text(encoding="utf-8")

    def test_contract_names_itself_live(self):
        self.assertTrue(CONTRACT.is_file())
        self.assertIn("Live Helix HTTP contract", self.contract)
        self.assertIn("does not use `/api/chat`", self.contract)
        self.assertIn("research/fable5/06-board-ui", self.contract)
        self.assertIn("Do not swap that UI onto this process", self.contract)

    def test_the_word_chat_never_appears_in_the_live_router(self):
        # Stronger than `path == "/api/chat"`: no spelling of the route at all.
        self.assertNotIn("/api/chat", self.server)
        self.assertNotIn("/api/chat", self.app)

    def test_the_browser_runs_threads_not_chat(self):
        self.assertRegex(self.app, r"/api/threads/\$\{[^}]+\}/run")
        self.assertIn("/api/quote", self.app)
        self.assertIn("/api/threads/", self.contract)
        self.assertIn("/api/quote", self.contract)

    def test_the_warning_is_load_bearing(self):
        # If the research board ever stopped speaking /api/chat the warning
        # would be stale; assert the thing it warns about still exists.
        spec = (BOARD_UI / "UI_SPEC.md").read_text(encoding="utf-8")
        research = spec + "".join(
            p.read_text(encoding="utf-8") for p in sorted(BOARD_UI.glob("*.js"))
        )
        self.assertIn("/api/chat", research)

    def test_research_board_is_not_wired_into_the_package(self):
        for path in (ROOT / "atelier" / "web").glob("*"):
            self.assertNotIn("/api/chat", path.read_text(encoding="utf-8", errors="ignore"))


# --------------------------------------------------------------------------
# Real server, demo lane
# --------------------------------------------------------------------------


class LiveServerCase(unittest.TestCase):
    """One real ThreadingHTTPServer per test, ephemeral port, torn down here."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._saved = {
            k: os.environ.get(k)
            for k in ("ATELIER_RUNTIME", "ATELIER_HOME", "ATELIER_HOST", "ATELIER_PORT",
                      "OPENAI_API_KEY", "GEMINI_API_KEY")
        }
        os.environ["ATELIER_RUNTIME"] = str(Path(self._tmp.name) / "rt")
        os.environ["ATELIER_HOME"] = str(Path(self._tmp.name) / "home")
        for key in ("ATELIER_HOST", "ATELIER_PORT", "OPENAI_API_KEY", "GEMINI_API_KEY"):
            os.environ.pop(key, None)
        from atelier import server

        self.srv = server
        server.reset_app()
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.seen: set[int] = set()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=10)
        self.assertFalse(self.thread.is_alive(), "server thread outlived the test")
        self._tmp.cleanup()
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def hit(self, method, path, body=None, host_header=None, raw_body=None):
        data = raw_body if raw_body is not None else (None if body is None else json.dumps(body).encode())
        headers = {"Content-Type": "application/json"}
        if host_header:
            headers["Host"] = host_header
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=data, method=method, headers=headers
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                code, payload, hdrs = resp.status, resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as exc:
            code, payload, hdrs = exc.code, exc.read(), dict(exc.headers)
        self.seen.add(code)
        try:
            parsed = json.loads(payload)
        except Exception:
            parsed = None
        return code, parsed, payload, hdrs

    def first_project(self):
        _, data, _, _ = self.hit("GET", "/api/projects")
        return data["projects"][0]["id"]

    def first_thread(self, pid):
        _, data, _, _ = self.hit("GET", f"/api/projects/{pid}/threads")
        return data["threads"][0]["id"]


class LiveHealthAndChat(LiveServerCase):
    """Claim 4."""

    def test_health_is_the_helix(self):
        code, data, _, _ = self.hit("GET", "/api/health")
        self.assertEqual(code, 200)
        self.assertEqual(data["architecture"], "helix")
        self.assertTrue(data["ok"])
        self.assertEqual(data["name"], "atelier")
        self.assertEqual(data["evolve_rounds"], 20)

    def test_catalog_is_200(self):
        code, data, _, _ = self.hit("GET", "/api/catalog")
        self.assertEqual(code, 200)
        self.assertTrue(data)

    def test_api_chat_is_404_on_every_verb_the_handler_answers(self):
        for method, sentinel in (
            ("GET", "unknown GET"),
            ("POST", "unknown POST"),
            ("DELETE", "unknown DELETE"),
            ("PATCH", "unknown POST"),  # do_PATCH is do_POST
        ):
            code, data, _, _ = self.hit(method, "/api/chat", body={} if method != "GET" else None)
            self.assertEqual(code, 404, f"{method} /api/chat")
            self.assertEqual(data["error"], sentinel)

    def test_unhandled_verbs_are_501(self):
        for method in ("PUT", "OPTIONS", "TRACE"):
            code, _, _, _ = self.hit(method, "/api/health", body={})
            self.assertEqual(code, 501, method)

    def test_static_surface_loads(self):
        for path, needle in (
            ("/", b"<"),
            ("/index.html", b"<"),
            ("/app.js", b"/api/threads/"),
            ("/styles.css", b"{"),
            ("/web/index.html", b"<"),
            ("/assets/app.js", b"/api/threads/"),
        ):
            code, _, payload, _ = self.hit("GET", path)
            self.assertEqual(code, 200, path)
            self.assertIn(needle, payload, path)
        code, data, _, _ = self.hit("GET", "/web/../../helix/keyring.py")
        self.assertEqual(code, 404)


class LiveContractWalk(LiveServerCase):
    """Every row in the table, driven for real on the demo lane."""

    def test_every_documented_route_answers(self):
        pid = self.first_project()
        _, thread, _, _ = self.hit("POST", f"/api/projects/{pid}/threads", {"topic": "walk"})
        tid = thread["id"]
        _, node, _, _ = self.hit("POST", f"/api/projects/{pid}/nodes", {"type": "text", "text": "hi"})
        _, run, _, _ = self.hit("POST", f"/api/threads/{tid}/run", {"prompt": "poster", "provider": "demo"})
        aid = run["artifacts"][0]["id"]
        sample = {
            ("GET", "/api/health"): None,
            ("GET", "/api/keys"): None,
            ("POST", "/api/keys"): {"provider": "openai", "key": "sk-probe"},
            ("GET", "/api/catalog"): None,
            ("GET", "/api/usage"): None,
            ("POST", "/api/quote"): {"provider": "demo", "prompt": "x"},
            ("GET", "/api/projects"): None,
            ("POST", "/api/projects"): {"name": "walk"},
            ("GET", f"/api/projects/{pid}"): None,
            ("GET", f"/api/projects/{pid}/threads"): None,
            ("POST", f"/api/projects/{pid}/threads"): {"topic": "x"},
            ("GET", f"/api/projects/{pid}/board"): None,
            ("GET", f"/api/projects/{pid}/camera"): None,
            ("POST", f"/api/projects/{pid}/camera"): {"camera": {"x": 1, "y": 2, "zoom": 1.5}},
            ("POST", f"/api/projects/{pid}/brand"): {"brand_kit": {"name": "W"}},
            ("POST", f"/api/projects/{pid}/upload"): {
                "filename": "p.png",
                "mime": "image/png",
                "data": base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"0" * 32).decode(),
            },
            ("GET", f"/api/projects/{pid}/export"): None,
            ("POST", f"/api/projects/{pid}/undo"): {},
            ("POST", f"/api/projects/{pid}/nodes"): {"type": "text", "text": "y"},
            ("GET", f"/api/threads/{tid}/messages"): None,
            ("POST", f"/api/threads/{tid}/run"): {"prompt": "again", "provider": "demo"},
            ("POST", f"/api/nodes/{node['id']}"): {"text": "z"},
            ("GET", f"/api/artifacts/{aid}"): None,
            ("GET", f"/api/artifacts/{aid}/export"): None,
            ("DELETE", f"/api/nodes/{node['id']}"): None,
        }
        for (method, path), body in sample.items():
            code, data, _, _ = self.hit(method, path, body)
            self.assertIn(code, (200, 201), f"{method} {path} -> {code} {data}")
            if isinstance(data, dict):
                self.assertNotIn(data.get("error"), {"unknown GET", "unknown POST", "unknown DELETE"})

    def test_the_three_rows_that_answer_200_for_a_missing_id(self):
        # These are live behaviour, not aspiration; the table calls them out
        # so the blanket "404 for a missing id" line cannot be believed.
        code, data, _, _ = self.hit("GET", "/api/projects/nope/threads")
        self.assertEqual((code, data), (200, {"threads": []}))
        code, data, _, _ = self.hit("GET", "/api/threads/nope/messages")
        self.assertEqual((code, data), (200, {"messages": []}))
        code, data, _, _ = self.hit("POST", "/api/projects/nope/undo", {})
        self.assertEqual((code, data), (200, {"undone": False, "reason": "empty"}))
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("**200 `[]`**, not 404", text)
        self.assertIn('**200 `{undone: false, reason: "empty"}`**', text)

    def test_the_rows_that_do_404_really_404(self):
        for method, path in (
            ("GET", "/api/projects/nope"),
            ("GET", "/api/projects/nope/board"),
            ("GET", "/api/projects/nope/camera"),
            ("POST", "/api/projects/nope/camera"),
            ("POST", "/api/projects/nope/threads"),
            ("POST", "/api/projects/nope/brand"),
            ("POST", "/api/projects/nope/nodes"),
            ("POST", "/api/projects/nope/upload"),
            ("GET", "/api/projects/nope/export"),
            ("POST", "/api/threads/nope/run"),
            ("POST", "/api/nodes/nope"),
            ("GET", "/api/artifacts/nope"),
            ("GET", "/api/artifacts/nope/export"),
        ):
            body = {"prompt": "x", "brand_kit": {}, "camera": {}, "data": "aGk=", "mime": "text/plain"}
            code, _, _, _ = self.hit(method, path, None if method == "GET" else body)
            self.assertEqual(code, 404, f"{method} {path}")

    def test_delete_node_then_delete_again(self):
        pid = self.first_project()
        _, node, _, _ = self.hit("POST", f"/api/projects/{pid}/nodes", {"type": "text", "text": "bye"})
        code, data, _, _ = self.hit("DELETE", f"/api/nodes/{node['id']}")
        self.assertEqual((code, data), (200, {"ok": True}))
        code, data, _, _ = self.hit("DELETE", f"/api/nodes/{node['id']}")
        self.assertEqual((code, data), (404, {"ok": False}))

    def test_patch_reaches_the_post_routes(self):
        pid = self.first_project()
        _, node, _, _ = self.hit("POST", f"/api/projects/{pid}/nodes", {"type": "text", "text": "before"})
        code, data, _, _ = self.hit("PATCH", f"/api/nodes/{node['id']}", {"text": "after"})
        self.assertEqual(code, 200)
        self.assertEqual(data["text"], "after")

    def test_data_aliases_text_on_a_node_patch(self):
        pid = self.first_project()
        _, node, _, _ = self.hit("POST", f"/api/projects/{pid}/nodes", {"type": "text", "text": "before"})
        code, data, _, _ = self.hit("POST", f"/api/nodes/{node['id']}", {"data": "via the alias"})
        self.assertEqual(code, 200)
        self.assertEqual(data["text"], "via the alias")

    def test_run_streams_events_then_result(self):
        pid = self.first_project()
        tid = self.first_thread(pid)
        code, _, payload, hdrs = self.hit(
            "POST", f"/api/threads/{tid}/run?stream=1", {"prompt": "sse", "provider": "demo"}
        )
        self.assertEqual(code, 200)
        self.assertTrue(hdrs["Content-Type"].startswith("text/event-stream"))
        events = [line.split(": ", 1)[1] for line in payload.decode().splitlines() if line.startswith("event: ")]
        self.assertEqual(events[-1], "result")
        self.assertIn("phase", events)
        self.assertIn("pin", events)

    def test_messages_carry_the_stored_plan(self):
        pid = self.first_project()
        tid = self.first_thread(pid)
        self.hit("POST", f"/api/threads/{tid}/run", {"prompt": "plan me", "provider": "demo"})
        code, data, _, _ = self.hit("GET", f"/api/threads/{tid}/messages")
        self.assertEqual(code, 200)
        plans = [m for m in data["messages"] if m.get("plan")]
        self.assertTrue(plans, "no message carried a plan")
        self.assertIn("route", plans[-1]["plan"])


class LiveExports(LiveServerCase):
    def setUp(self):
        super().setUp()
        self.pid = self.first_project()
        tid = self.first_thread(self.pid)
        _, run, _, _ = self.hit("POST", f"/api/threads/{tid}/run", {"prompt": "an export", "provider": "demo"})
        self.aid = run["artifacts"][0]["id"]

    def test_project_export_formats_and_scales(self):
        expected = {
            "": "application/zip",
            "?fmt=zip": "application/zip",
            "?fmt=svg": "image/svg+xml",
            "?fmt=png": "image/png",
            "?fmt=pdf": "application/pdf",
            "?format=svg": "image/svg+xml",
        }
        for query, mime in expected.items():
            code, _, payload, hdrs = self.hit("GET", f"/api/projects/{self.pid}/export{query}")
            self.assertEqual(code, 200, query)
            self.assertEqual(hdrs["Content-Type"], mime, query)
            self.assertIn("attachment; filename=", hdrs["Content-Disposition"], query)
            self.assertTrue(payload, query)
        sizes = []
        for scale in (1, 2, 4):
            code, _, payload, _ = self.hit("GET", f"/api/projects/{self.pid}/export?fmt=png&scale={scale}")
            self.assertEqual(code, 200)
            sizes.append(len(payload))
        self.assertEqual(sizes, sorted(sizes), f"scale did not grow the sheet: {sizes}")
        self.assertLess(sizes[0], sizes[-1])

    def test_artifact_export_formats(self):
        for query, mime in (
            ("", "image/svg+xml"),
            ("?fmt=native", "image/svg+xml"),
            ("?fmt=svg", "image/svg+xml"),
            ("?fmt=png", "image/png"),
            ("?fmt=pdf", "application/pdf"),
        ):
            code, _, payload, hdrs = self.hit("GET", f"/api/artifacts/{self.aid}/export{query}")
            self.assertEqual(code, 200, query)
            self.assertEqual(hdrs["Content-Type"], mime, query)
            self.assertTrue(payload, query)

    def test_jpeg_is_415_on_both_export_routes(self):
        for path in (f"/api/projects/{self.pid}/export", f"/api/artifacts/{self.aid}/export"):
            for fmt in ("jpeg", "jpg"):
                code, data, _, _ = self.hit("GET", f"{path}?fmt={fmt}")
                self.assertEqual(code, 415, f"{path}?fmt={fmt}")
                self.assertEqual(data["code"], "unsupported_fmt")
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("415", text)
        self.assertIn("JPEG", text)

    def test_download_filename_uses_the_mime_extension(self):
        code, _, _, hdrs = self.hit("GET", f"/api/artifacts/{self.aid}?download=1")
        self.assertEqual(code, 200)
        self.assertRegex(hdrs["Content-Disposition"], r'attachment; filename="[^"]+\.svg"')
        code, _, _, hdrs = self.hit("GET", f"/api/artifacts/{self.aid}")
        self.assertEqual(code, 200)
        self.assertNotIn("Content-Disposition", hdrs)


class LiveStatusCodes(LiveServerCase):
    """Claim 3's status table, produced rather than asserted from a string."""

    def documented_codes(self):
        codes = set()
        for line in CONTRACT.read_text(encoding="utf-8").splitlines():
            match = _ROW.match(line.strip())
            if not match:
                continue
            head = match.group(1).split("|")[0].strip()
            if re.fullmatch(r"\d{3}", head):
                codes.add(int(head))
        return codes

    def test_every_documented_code_is_produced_live(self):
        pid = self.first_project()
        tid = self.first_thread(pid)
        self.hit("GET", "/api/health")                                        # 200
        self.hit("POST", "/api/projects", {"name": "codes"})                  # 201
        code, data, _, _ = self.hit(
            "POST", "/api/keys", {"provider": "openai", "key": "k", "base_url": "https://evil.example"}
        )
        self.assertEqual((code, data["code"]), (400, "unofficial_host"))      # 400
        code, data, _, _ = self.hit("GET", "/api/health", host_header="attacker.example")
        self.assertEqual((code, data["code"]), (403, "bad_host"))             # 403
        self.hit("GET", "/api/chat")                                          # 404
        code, data, _, _ = self.hit(
            "POST", f"/api/projects/{pid}/upload",
            {"filename": "big", "mime": "application/octet-stream", "data": "A" * 6_800_001},
        )
        self.assertEqual(code, 413)                                           # 413
        self.hit("GET", f"/api/projects/{pid}/export?fmt=jpeg")               # 415
        code, data, _, _ = self.hit("POST", f"/api/threads/{tid}/run", {"prompt": "x", "provider": "openai"})
        self.assertEqual((code, data["code"], data["ok"]), (422, "auth", False))  # 422 fail-closed
        self.hit("PUT", "/api/health", {})                                    # 501

        from atelier.helix import usage

        saved = usage.DAILY_BUDGET_USD
        usage.DAILY_BUDGET_USD = 0.0
        try:
            code, data, _, _ = self.hit(
                "POST", f"/api/threads/{tid}/run",
                {"prompt": "x", "provider": "openai", "model": "gpt-4o-mini"},
            )
            self.assertEqual((code, data["code"]), (402, "budget_exceeded"))  # 402
        finally:
            usage.DAILY_BUDGET_USD = saved

        run = self.srv.APP.conductor.run

        def boom(**kwargs):
            raise RuntimeError("induced")

        self.srv.APP.conductor.run = boom
        try:
            code, data, _, _ = self.hit("POST", f"/api/threads/{tid}/run", {"prompt": "x"})
            self.assertEqual((code, data["ok"]), (500, False))                # 500
        finally:
            self.srv.APP.conductor.run = run

        code, data, _, _ = self.hit("POST", "/api/quote", raw_body=b"{not json")
        self.assertEqual((code, data["error"]), (400, "invalid json"))

        documented = self.documented_codes()
        self.assertEqual(
            documented - self.seen,
            set(),
            f"CONTRACT.md lists codes this walk never produced: {sorted(documented - self.seen)}",
        )
        self.assertEqual(
            self.seen - documented,
            set(),
            f"live codes missing from the CONTRACT.md status table: {sorted(self.seen - documented)}",
        )

    def test_quote_priced_is_not_unknown_model(self):
        # CONTRACT used to say `priced: false` for unknown models. It is not a
        # model lookup: demo and ollama are true for any string at all.
        matrix = {
            ("openai", "gpt-4o-mini", "image"): True,
            ("openai", "no-such-model", "chat"): False,
            ("openai", "gpt-image-1", "image"): False,
            ("gemini", "made-up-9000", "chat"): False,
            ("ollama", "made-up-9000", "image"): True,
            ("demo", "made-up-9000", "image"): True,
        }
        for (provider, model, capability), priced in matrix.items():
            code, data, _, _ = self.hit(
                "POST", "/api/quote",
                {"provider": provider, "model": model, "prompt": "x", "capability": capability},
            )
            self.assertEqual(code, 200)
            self.assertIs(data["priced"], priced, f"{provider}/{model}/{capability}")
            if not priced:
                self.assertGreater(data["estimated_usd"], 0.0, "unpriced must not mean free")
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("`priced` is not \"is this model known\"", text)
        self.assertNotIn("`priced: false` for unknown models", text)

    def test_quote_spends_nothing(self):
        before = self.hit("GET", "/api/usage")[1]
        self.hit("POST", "/api/quote", {"provider": "openai", "model": "gpt-4o-mini", "prompt": "x"})
        after = self.hit("GET", "/api/usage")[1]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
