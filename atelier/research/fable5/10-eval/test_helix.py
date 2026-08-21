#!/usr/bin/env python3
"""Atelier Helix — test and evaluation harness (Fable5#10).

Covers, offline and with no live API keys:

  * store          — the Helix memory schema (04-helix-arch/schema.sql):
                     invariants I3/I4/I5/I6/I8, board/canvas pinning,
                     v_board_scene projection.
  * conductor parse— the conductor-plan/1 and conductor-critique/1 envelopes
                     (05-conductor/PROTOCOL.md §2–§3): the worked example must
                     parse; every protocol violation must raise.
  * usage ledger   — 08-security-quota/usage.py: cost math, persistence,
                     secret scrubbing, budget guards.
  * demo loom      — a full brief → route → weave → critique → pin run with
                     deterministic scripted spokes (helix_ref.py), network
                     access hard-blocked, provider keys scrubbed from the env.
  * canvas pin     — manifest artifacts registered in the store and pinned to
                     a board; verified through v_board_scene.

Component discovery (override via environment):

  ATELIER_ROOT       fleet output root      (default /tmp/atelier-fable)
  ATELIER_SCHEMA     path to schema.sql     (default $ROOT/04-helix-arch/schema.sql)
  ATELIER_USAGE      path to usage.py       (default $ROOT/08-security-quota/usage.py)
  ATELIER_CONDUCTOR  path to conductor.py   (default $ROOT/05-conductor/conductor.py)

If the real conductor module is absent (or fails to import), the bundled
reference implementation `helix_ref.py` is used; it is the executable
specification these tests were written against. Missing schema/usage
components skip their test classes with an explanatory message rather than
failing, so the harness gives signal at any stage of fleet integration.

Usage:
  python3 test_helix.py -v         # run the unit suite
  python3 test_helix.py --eval     # print the qualitative eval scorecard (see EVAL.md)
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import socket
import sqlite3
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("ATELIER_ROOT", "/tmp/atelier-fable")
SCHEMA_PATH = os.environ.get("ATELIER_SCHEMA", os.path.join(ROOT, "04-helix-arch", "schema.sql"))
USAGE_PATH = os.environ.get("ATELIER_USAGE", os.path.join(ROOT, "08-security-quota", "usage.py"))
CONDUCTOR_PATH = os.environ.get(
    "ATELIER_CONDUCTOR", os.path.join(ROOT, "05-conductor", "conductor.py")
)
LOOM_PATH = os.environ.get("ATELIER_LOOM", os.path.join(ROOT, "07-loom", "loom.py"))
FIXTURE_DIR = os.path.join(HERE, "fixtures")

sys.path.insert(0, HERE)
import helix_ref  # bundled reference implementation / executable spec


def _import_file(name: str, path: str):
    if not os.path.isfile(path):
        return None
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod  # dataclasses resolve annotations via sys.modules
        spec.loader.exec_module(mod)
        return mod
    except Exception as exc:  # a half-written sibling module must not kill the harness
        sys.modules.pop(name, None)
        sys.stderr.write(f"[harness] could not import {path}: {exc}\n")
        return None


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


usage = _import_file("atelier_usage", USAGE_PATH)
HAVE_USAGE = usage is not None

loom = _import_file("atelier_loom", LOOM_PATH)
HAVE_LOOM = loom is not None

HAVE_SCHEMA = os.path.isfile(SCHEMA_PATH)
SCHEMA_SQL = _read_text(SCHEMA_PATH) if HAVE_SCHEMA else ""

_real_conductor = _import_file("atelier_conductor", CONDUCTOR_PATH)
if _real_conductor is not None and hasattr(_real_conductor, "parse_plan") and hasattr(
    _real_conductor, "PlanParseError"
):
    CP = _real_conductor
    CP_SOURCE = CONDUCTOR_PATH
else:
    CP = helix_ref
    CP_SOURCE = "helix_ref.py (bundled reference)"

PlanParseError = CP.PlanParseError
CritiqueParseError = getattr(CP, "CritiqueParseError", PlanParseError)

# The worked example from 05-conductor/PROTOCOL.md §2, verbatim. If this ever
# fails to parse, either the protocol or the parser has drifted.
VALID_PLAN = {
    "protocol": "conductor-plan/1",
    "reading": "Solstice Tea wants a compact identity: a one-color logo mark in deep green and a short tagline, both quiet and unfussy.",
    "assumptions": [
        "A symbol-only mark (no wordmark) satisfies 'logo' here.",
        "White is an acceptable background since none was specified.",
    ],
    "steps": [
        {
            "id": "s1",
            "title": "Write the tagline",
            "craft": "compose-text",
            "instruction": "Write one tagline for Solstice Tea, a small-batch tea house. Six words or fewer. Tone: minimal, warm. Avoid puns on 'tea time'.",
            "needs": [],
            "emits": {"kind": "text", "name": "tagline"},
            "acceptance": ["six words or fewer", "contains no pun on 'tea time'"],
        },
        {
            "id": "s2",
            "title": "Render the logo mark",
            "craft": "render-image",
            "instruction": "Render a minimal logo mark for Solstice Tea: a single continuous line suggesting steam rising from a cup, using only #2F5D50 on white.",
            "needs": [],
            "emits": {"kind": "image", "name": "logo-mark"},
            "acceptance": ["uses only #2F5D50 on white", "legible at 32 pixels"],
        },
        {
            "id": "s3",
            "title": "Assemble the style note",
            "craft": "synthesize",
            "instruction": "Combine the tagline [[s1]] and the logo (attached, from [[s2]]) into a one-page style note covering usage, clear space, and the palette (#2F5D50 plus neutral grays).",
            "needs": ["s1", "s2"],
            "emits": {"kind": "text", "name": "style-note"},
            "acceptance": ["names the hex value #2F5D50", "under 200 words"],
        },
    ],
    "handoff": ["tagline", "logo-mark", "style-note"],
}

LIVE_KEY_ENVS = [
    "LOVART_ACCESS_KEY", "LOVART_SECRET_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY", "GOOGLE_API_KEY", "STABILITY_API_KEY", "REPLICATE_API_TOKEN",
]


# ---------------------------------------------------------------------------
# Shape-agnostic accessors: real modules may return dataclasses, not dicts.
# ---------------------------------------------------------------------------

def _pget(plan, key, default=None):
    if isinstance(plan, dict):
        return plan.get(key, default)
    return getattr(plan, key, default)


def _sget(step, key, default=None):
    if isinstance(step, dict):
        return step.get(key, default)
    return getattr(step, key, default)


def _emits(step):
    if isinstance(step, dict):
        e = step.get("emits", {})
        return e.get("kind"), e.get("name")
    if hasattr(step, "emits_kind"):
        return step.emits_kind, step.emits_name
    e = getattr(step, "emits", None)
    return getattr(e, "kind", None), getattr(e, "name", None)


def _route_decisions(plan, request: str, registry=None) -> dict:
    """Route a plan with the bound conductor; normalize to {step_id: lane}."""
    brief = CP.distill_brief(request)
    if registry is None:
        decisions = CP.route_plan(plan, brief)
    else:
        decisions = CP.route_plan(plan, brief, registry)
    return {sid: _sget(d, "lane") for sid, d in dict(decisions).items()}


def load_fixtures() -> dict:
    fixtures = {}
    for fn in sorted(os.listdir(FIXTURE_DIR)):
        if fn.endswith(".json"):
            with open(os.path.join(FIXTURE_DIR, fn), encoding="utf-8") as f:
                fx = json.load(f)
            fixtures[fx["id"]] = fx
    return fixtures


def plan_text_for(fx: dict) -> str:
    """Deterministic planner output for a fixture brief (demo planner spoke)."""
    task = helix_ref.SpokeTask(
        kind="plan",
        name="plan",
        instruction=json.dumps({"request": fx["request"], "data": fx.get("data")}),
    )
    return helix_ref.DemoPlannerSpoke().perform(task).text


class forbid_network:
    """Hard-fails the test if anything under it opens a socket connection."""

    def __enter__(self):
        self._connect = socket.socket.connect
        self._create = socket.create_connection

        def _blocked(*a, **k):
            raise AssertionError("network access attempted during an offline demo run")

        socket.socket.connect = _blocked
        socket.create_connection = _blocked
        return self

    def __exit__(self, *exc):
        socket.socket.connect = self._connect
        socket.create_connection = self._create
        return False


# ---------------------------------------------------------------------------
# 1. Store — the Helix memory schema
# ---------------------------------------------------------------------------

NOW_MS = 1_789_000_000_000
SHA64 = "ab" * 32


@unittest.skipUnless(HAVE_SCHEMA, f"schema not found at {SCHEMA_PATH}")
class StoreSchemaTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.executescript(SCHEMA_SQL)

    def tearDown(self):
        self.con.close()

    # -- fixtures ------------------------------------------------------------
    def _project(self, pid="prj_1", slug="alpha"):
        self.con.execute(
            "INSERT INTO projects (id, name, slug, created_at, updated_at) VALUES (?,?,?,?,?)",
            (pid, "Alpha", slug, NOW_MS, NOW_MS),
        )

    def _thread(self, tid="thr_1", pid="prj_1"):
        self.con.execute(
            "INSERT INTO threads (id, project_id, created_at, updated_at) VALUES (?,?,?,?)",
            (tid, pid, NOW_MS, NOW_MS),
        )

    def _message(self, mid="msg_1", tid="thr_1", seq=0):
        self.con.execute(
            "INSERT INTO messages (id, thread_id, seq, role, content, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (mid, tid, seq, "user", "make me a logo", NOW_MS),
        )

    def _artifact(self, aid="art_1", pid="prj_1", sha=SHA64):
        self.con.execute(
            "INSERT INTO artifacts (id, project_id, kind, mime, storage, uri, sha256,"
            " byte_size, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (aid, pid, "image", "image/png", "blob", f"{sha[:2]}/{sha}", sha, 128, NOW_MS),
        )

    def _board(self, bid="brd_1", pid="prj_1", lid="lyr_1"):
        self.con.execute(
            "INSERT INTO boards (id, project_id, created_at, updated_at) VALUES (?,?,?,?)",
            (bid, pid, NOW_MS, NOW_MS),
        )
        self.con.execute(
            "INSERT INTO board_layers (id, board_id, created_at, updated_at) VALUES (?,?,?,?)",
            (lid, bid, NOW_MS, NOW_MS),
        )

    def _pin(self, nid, aid, x=0.0, y=0.0, bid="brd_1", lid="lyr_1"):
        self.con.execute(
            "INSERT INTO board_nodes (id, board_id, layer_id, kind, artifact_id, x, y,"
            " w, h, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (nid, bid, lid, "artifact", aid, x, y, 320.0, 240.0, NOW_MS, NOW_MS),
        )

    # -- tests ---------------------------------------------------------------
    def test_schema_loads_idempotently(self):
        self.con.executescript(SCHEMA_SQL)  # every statement is IF NOT EXISTS

    def test_project_slug_is_validated(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._project(pid="prj_bad", slug="Bad Slug!")

    def test_messages_are_append_only_i3(self):
        self._project(); self._thread(); self._message()
        with self.assertRaisesRegex(sqlite3.DatabaseError, "I3"):
            self.con.execute("UPDATE messages SET content = 'rewritten' WHERE id = 'msg_1'")
        with self.assertRaisesRegex(sqlite3.DatabaseError, "I3"):
            self.con.execute("DELETE FROM messages WHERE id = 'msg_1'")

    def test_artifact_provenance_is_frozen_i4(self):
        self._project(); self._artifact()
        with self.assertRaisesRegex(sqlite3.DatabaseError, "I4"):
            self.con.execute("UPDATE artifacts SET uri = 'zz/tampered' WHERE id = 'art_1'")
        # Annotations stay editable.
        self.con.execute("UPDATE artifacts SET title = 'Logo mark v1' WHERE id = 'art_1'")

    def test_canvas_pin_requires_artifact_i5(self):
        self._project(); self._board()
        with self.assertRaises(sqlite3.IntegrityError):
            self._pin("nod_bad", None)

    def test_canvas_pin_appears_in_board_scene(self):
        self._project(); self._artifact(); self._board()
        self._pin("nod_1", "art_1", x=40.0, y=40.0)
        rows = self.con.execute(
            "SELECT node_id, artifact_id, artifact_mime, x, y FROM v_board_scene"
        ).fetchall()
        self.assertEqual(rows, [("nod_1", "art_1", "image/png", 40.0, 40.0)])
        # Pins are mutable projections: moving a pin is allowed...
        self.con.execute("UPDATE board_nodes SET x = 400.0 WHERE id = 'nod_1'")
        # ...and unpinning never deletes the artifact behind it.
        self.con.execute("DELETE FROM board_nodes WHERE id = 'nod_1'")
        (n,) = self.con.execute("SELECT COUNT(*) FROM artifacts").fetchone()
        self.assertEqual(n, 1)

    def test_single_active_brand_kit_i6(self):
        self._project()
        self.con.execute(
            "INSERT INTO brand_kits (id, project_id, name, is_active, created_at, updated_at)"
            " VALUES ('kit_1', 'prj_1', 'Helix', 1, ?, ?)", (NOW_MS, NOW_MS),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute(
                "INSERT INTO brand_kits (id, project_id, name, is_active, created_at, updated_at)"
                " VALUES ('kit_2', 'prj_1', 'Helix2', 1, ?, ?)", (NOW_MS, NOW_MS),
            )
        # A second *inactive* kit and an active kit on another project are fine.
        self.con.execute(
            "INSERT INTO brand_kits (id, project_id, name, is_active, created_at, updated_at)"
            " VALUES ('kit_3', 'prj_1', 'Helix3', 0, ?, ?)", (NOW_MS, NOW_MS),
        )

    def test_usage_events_are_append_only_i8(self):
        self._project()
        self.con.execute(
            "INSERT INTO usage_events (id, created_at, project_id, spoke, operation,"
            " cost_micros) VALUES ('use_1', ?, 'prj_1', 'openai', 'image.generate', 42)",
            (NOW_MS,),
        )
        with self.assertRaisesRegex(sqlite3.DatabaseError, "I8"):
            self.con.execute("UPDATE usage_events SET cost_micros = 0 WHERE id = 'use_1'")
        with self.assertRaisesRegex(sqlite3.DatabaseError, "I8"):
            self.con.execute("DELETE FROM usage_events WHERE id = 'use_1'")

    def test_usage_cost_cannot_be_negative(self):
        self._project()
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute(
                "INSERT INTO usage_events (id, created_at, project_id, spoke, operation,"
                " cost_micros) VALUES ('use_neg', ?, 'prj_1', 'openai', 'x', -1)",
                (NOW_MS,),
            )


# ---------------------------------------------------------------------------
# 2. Conductor parse — conductor-plan/1 and conductor-critique/1
# ---------------------------------------------------------------------------

class ConductorParseTests(unittest.TestCase):
    def _plan_text(self, mutate=None) -> str:
        plan = copy.deepcopy(VALID_PLAN)
        if mutate:
            mutate(plan)
        return json.dumps(plan)

    def _assert_rejects(self, mutate, why=""):
        with self.assertRaises(PlanParseError, msg=why):
            CP.parse_plan(self._plan_text(mutate))

    def test_protocol_worked_example_parses(self):
        plan = CP.parse_plan(self._plan_text())
        steps = _pget(plan, "steps")
        self.assertEqual(len(steps), 3)
        self.assertEqual(list(_pget(plan, "handoff")), ["tagline", "logo-mark", "style-note"])

    def test_tolerates_fence_and_prose(self):
        text = "Sure, here is the plan:\n```json\n" + self._plan_text() + "\n```\nHope it helps!"
        plan = CP.parse_plan(text)
        self.assertEqual(len(_pget(plan, "steps")), 3)

    def test_rejects_unparseable_text(self):
        with self.assertRaises(PlanParseError):
            CP.parse_plan("I would suggest a nice green logo.")

    def test_rejects_wrong_protocol(self):
        self._assert_rejects(lambda p: p.update(protocol="conductor-plan/2"))

    def test_rejects_empty_reading(self):
        self._assert_rejects(lambda p: p.update(reading="  "))

    def test_rejects_empty_steps(self):
        self._assert_rejects(lambda p: p.update(steps=[]))

    def test_rejects_duplicate_step_ids(self):
        def m(p):
            p["steps"][1]["id"] = "s1"
        self._assert_rejects(m)

    def test_rejects_unknown_craft(self):
        def m(p):
            p["steps"][0]["craft"] = "paint-mural"
        self._assert_rejects(m)

    def test_rejects_craft_kind_mismatch(self):
        def m(p):  # render-image may only emit image
            p["steps"][1]["emits"]["kind"] = "text"
        self._assert_rejects(m)

    def test_rejects_duplicate_artifact_names(self):
        def m(p):
            p["steps"][1]["emits"]["name"] = "tagline"
        self._assert_rejects(m)

    def test_rejects_empty_acceptance(self):
        def m(p):
            p["steps"][0]["acceptance"] = []
        self._assert_rejects(m)

    def test_rejects_unknown_need(self):
        def m(p):
            p["steps"][2]["needs"] = ["s1", "s2", "s9"]
        self._assert_rejects(m)

    def test_rejects_self_need(self):
        def m(p):
            p["steps"][0]["needs"] = ["s1"]
        self._assert_rejects(m)

    def test_rejects_token_without_need(self):
        def m(p):  # [[s2]] token survives but the s2 edge is removed
            p["steps"][2]["needs"] = ["s1"]
        self._assert_rejects(m)

    def test_rejects_dependency_cycle(self):
        def m(p):
            p["steps"][0]["needs"] = ["s3"]  # s3 already needs s1 -> cycle
        self._assert_rejects(m)

    def test_rejects_handoff_of_unknown_artifact(self):
        self._assert_rejects(lambda p: p.update(handoff=["tagline", "nope"]))

    def test_rejects_empty_handoff(self):
        self._assert_rejects(lambda p: p.update(handoff=[]))

    def test_order_steps_is_topological(self):
        if not hasattr(CP, "order_steps"):
            self.skipTest("bound conductor exposes no order_steps")
        shuffled = copy.deepcopy(VALID_PLAN)
        shuffled["steps"] = shuffled["steps"][::-1]  # s3 listed before its needs
        plan = CP.parse_plan(json.dumps(shuffled))
        ordered = CP.order_steps(_pget(plan, "steps"))
        ids = [x if isinstance(x, str) else _sget(x, "id") for x in ordered]
        self.assertEqual(set(ids), {"s1", "s2", "s3"})
        self.assertEqual(ids[-1], "s3", "s3 needs s1 and s2, so it must run last")

    # -- critique envelope ----------------------------------------------------
    def test_critique_accept_with_advisory_parses(self):
        if not hasattr(CP, "parse_critique"):
            self.skipTest("bound conductor exposes no parse_critique")
        env = {
            "protocol": "conductor-critique/1",
            "verdict": "accept",
            "notes": [{"artifact": "tagline", "severity": "advisory",
                       "note": "Could be warmer.", "fix_hint": ""}],
        }
        out = CP.parse_critique(json.dumps(env))
        self.assertEqual(_pget(out, "verdict"), "accept")

    def test_critique_revise_requires_a_blocker(self):
        if not hasattr(CP, "parse_critique"):
            self.skipTest("bound conductor exposes no parse_critique")
        env = {
            "protocol": "conductor-critique/1",
            "verdict": "revise",
            "notes": [{"artifact": "tagline", "severity": "advisory",
                       "note": "Meh.", "fix_hint": ""}],
        }
        with self.assertRaises(CritiqueParseError):
            CP.parse_critique(json.dumps(env))

    def test_critique_rejects_bad_verdict_and_severity(self):
        if not hasattr(CP, "parse_critique"):
            self.skipTest("bound conductor exposes no parse_critique")
        with self.assertRaises(CritiqueParseError):
            CP.parse_critique(json.dumps({"protocol": "conductor-critique/1",
                                          "verdict": "maybe", "notes": []}))
        with self.assertRaises(CritiqueParseError):
            CP.parse_critique(json.dumps({
                "protocol": "conductor-critique/1", "verdict": "accept",
                "notes": [{"artifact": "x", "severity": "fatal", "note": "n", "fix_hint": ""}],
            }))


# ---------------------------------------------------------------------------
# 3. Routing correctness (ROUTING.md: three lanes, five rules, first match wins)
# ---------------------------------------------------------------------------

SOLSTICE_REQUEST = (
    "Design a logo and tagline for 'Solstice Tea', a small-batch tea house. "
    "One-colour mark in deep green #2F5D50 on white, quiet and unfussy, plus "
    "a one-page style note."
)


class RoutingTests(unittest.TestCase):
    def test_worked_example_follows_the_rule_order(self):
        plan = CP.parse_plan(json.dumps(VALID_PLAN))
        lanes = _route_decisions(plan, SOLSTICE_REQUEST)
        self.assertEqual(lanes["s1"], "openai")  # rule 5: structured drafting
        self.assertEqual(lanes["s2"], "image")   # rule 1: render-image
        self.assertEqual(lanes["s3"], "gemini")  # rule 3: consumes s2's image

    def test_every_fixture_plan_routes_cleanly(self):
        for fid, fx in load_fixtures().items():
            with self.subTest(fixture=fid):
                plan = CP.parse_plan(plan_text_for(fx))
                lanes = _route_decisions(plan, fx["request"])
                steps = _pget(plan, "steps")
                self.assertEqual(len(lanes), len(steps), f"{fid}: unrouted steps")
                used = set(lanes.values())
                self.assertNotIn(None, used, f"{fid}: some step has no lane")
                exp = fx["expected"]
                for lane in exp["lanes_required"]:
                    self.assertIn(lane, used, f"{fid}: lane {lane!r} missing")
                self.assertFalse(
                    used & set(exp["lanes_forbidden"]),
                    f"{fid}: forbidden lane used: {used & set(exp['lanes_forbidden'])}",
                )

    def test_lane_rules_hold_for_every_fixture_step(self):
        for fid, fx in load_fixtures().items():
            with self.subTest(fixture=fid):
                plan = CP.parse_plan(plan_text_for(fx))
                lanes = _route_decisions(plan, fx["request"])
                steps = {_sget(s, "id"): s for s in _pget(plan, "steps")}
                for sid, step in steps.items():
                    craft = _sget(step, "craft")
                    kind, _ = _emits(step)
                    if craft in ("render-image", "refine-image"):
                        self.assertEqual(lanes[sid], "image", f"{fid}/{sid}: rule 1")
                    elif craft == "analyze-visual":
                        self.assertEqual(lanes[sid], "gemini", f"{fid}/{sid}: rule 2")
                    # Only the image lane may return kind image, and vice versa.
                    self.assertEqual(kind == "image", lanes[sid] == "image",
                                     f"{fid}/{sid}: image emission and lane must agree")

    def test_registry_missing_a_lane_fails_before_any_step_runs(self):
        RoutingError = getattr(CP, "RoutingError", Exception)
        plan = CP.parse_plan(json.dumps(VALID_PLAN))
        with self.assertRaises(RoutingError):
            _route_decisions(plan, SOLSTICE_REQUEST, registry={"image": ""})


# ---------------------------------------------------------------------------
# 4. Usage ledger — 08-security-quota/usage.py
# ---------------------------------------------------------------------------

@unittest.skipUnless(HAVE_USAGE, f"usage module not importable from {USAGE_PATH}")
class UsageLedgerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="helix-ledger-")
        self.addCleanup(self._tmp.cleanup)
        self.db = os.path.join(self._tmp.name, "usage.sqlite3")
        self.ledger = usage.UsageLedger(self.db)

    def test_token_cost_math(self):
        got = usage.estimate_cost(
            "openai", "gpt-5.6-luna", {"input_tokens": 100_000, "output_tokens": 10_000}
        )
        self.assertAlmostEqual(got, 0.032, places=6)  # 100k*0.20/M + 10k*1.20/M

    def test_unknown_model_lenient_none_strict_raises(self):
        self.assertIsNone(usage.estimate_cost("openai", "mystery-9000", {"input_tokens": 5}))
        with self.assertRaises(usage.UnknownPriceError):
            usage.estimate_cost("openai", "mystery-9000", {"input_tokens": 5}, strict=True)

    def test_negative_quantities_rejected(self):
        with self.assertRaises(ValueError):
            usage.estimate_cost("openai", "gpt-5.6-luna", {"input_tokens": -1})

    def test_empty_units_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.record("openai", "gpt-5.6-luna", {}, thread_id="t1")

    def test_record_persists_across_reopen(self):
        self.ledger.record("openai", "gpt-5.6-luna",
                           {"input_tokens": 1000, "output_tokens": 100}, thread_id="t1")
        self.ledger.record("gemini", "imagen-4.0-generate-001", {"images": 2}, thread_id="t2")
        reopened = usage.UsageLedger(self.db)
        events = list(reopened.events())
        self.assertEqual(len(events), 2)
        self.assertAlmostEqual(reopened.spend_usd(thread_id="t2"), 0.08, places=6)
        self.assertEqual(reopened.unpriced_count(), 0)

    def test_thread_and_provider_filters(self):
        self.ledger.record("openai", "gpt-5.6-luna", {"input_tokens": 1000}, thread_id="a")
        self.ledger.record("gemini", "imagen-4.0-fast-generate-001", {"images": 1}, thread_id="b")
        self.assertEqual(len(list(self.ledger.events(thread_id="a"))), 1)
        self.assertAlmostEqual(self.ledger.spend_usd(provider="gemini"), 0.02, places=6)

    def test_metadata_secrets_are_scrubbed(self):
        ev = self.ledger.record(
            "openai", "gpt-5.6-luna", {"input_tokens": 10}, thread_id="t1",
            metadata={"note": "used sk-" + "a" * 24 + " and AIza" + "B" * 35},
        )
        blob = json.dumps(ev.metadata)
        self.assertNotIn("sk-" + "a" * 24, blob)
        self.assertNotIn("AIza" + "B" * 35, blob)
        self.assertIn("[REDACTED]", blob)

    def test_budget_guard_daily_cap(self):
        self.ledger.record("openai", "gpt-image-2", {"image_output_tokens": 1},
                           thread_id="t1", estimated_cost_usd=0.04)
        guard = usage.BudgetGuard(self.ledger, daily_usd=0.05, per_thread_usd=None)
        guard.check("t1", 0.005)  # within cap
        with self.assertRaises(usage.QuotaExceeded):
            guard.check("t1", 0.02)

    def test_budget_guard_per_thread_cap(self):
        self.ledger.record("openai", "gpt-image-2", {"image_output_tokens": 1},
                           thread_id="hot", estimated_cost_usd=0.008)
        guard = usage.BudgetGuard(self.ledger, daily_usd=None, per_thread_usd=0.01)
        guard.check("cold", 0.009)  # other threads unaffected
        with self.assertRaises(usage.QuotaExceeded):
            guard.check("hot", 0.005)

    def test_budget_guard_rejects_negative_projection(self):
        guard = usage.BudgetGuard(self.ledger, daily_usd=1.0, per_thread_usd=1.0)
        with self.assertRaises(ValueError):
            guard.check("t1", -0.01)

    def test_demo_events_cost_zero_and_are_priced(self):
        self.ledger.record("demo", "demo-image", {"requests": 1},
                           thread_id="run1", estimated_cost_usd=0.0)
        self.assertEqual(self.ledger.spend_usd(), 0.0)
        self.assertEqual(self.ledger.unpriced_count(), 0)


# ---------------------------------------------------------------------------
# 5. Demo loom — offline brief → plan → weave → pin, no keys, no network
# ---------------------------------------------------------------------------

class DemoLoomTests(unittest.TestCase):
    def setUp(self):
        self._saved_env = {}
        for key in LIVE_KEY_ENVS:
            self._saved_env[key] = os.environ.pop(key, None)
        self._tmp = tempfile.TemporaryDirectory(prefix="helix-loom-")
        self.addCleanup(self._tmp.cleanup)
        self.fixtures = load_fixtures()

    def tearDown(self):
        for key, val in self._saved_env.items():
            if val is not None:
                os.environ[key] = val

    def _run(self, fx, **kw):
        out_dir = os.path.join(self._tmp.name, kw.pop("subdir", fx["id"]))
        return helix_ref.demo_run(
            fx["request"], out_dir=out_dir, data=fx.get("data"), **kw
        )

    def test_all_fixtures_run_offline_without_keys(self):
        for key in LIVE_KEY_ENVS:
            self.assertNotIn(key, os.environ)
        for fid, fx in self.fixtures.items():
            with self.subTest(fixture=fid), forbid_network():
                result = self._run(fx)
                manifest = result["manifest"]
                self.assertTrue(os.path.isfile(result["manifest_path"]))
                exp = fx["expected"]
                self.assertGreaterEqual(len(manifest["artifacts"]), exp["min_steps"])
                kinds = {a["kind"] for a in manifest["artifacts"]}
                for kind in exp["deliverable_kinds"]:
                    self.assertIn(kind, kinds, f"{fid}: no {kind} artifact produced")
                handoff = [a for a in manifest["artifacts"] if a["handoff"]]
                self.assertGreaterEqual(len(handoff), exp["handoff_min"])

    def test_manifest_matches_protocol_and_disk(self):
        result = self._run(self.fixtures["logo"])
        m = result["manifest"]
        for field in ("manifest", "run_id", "mode", "created_at", "brief", "plan", "artifacts"):
            self.assertIn(field, m)
        self.assertEqual(m["manifest"], "conductor-manifest/1")
        for entry in m["artifacts"]:
            for field in ("name", "kind", "file", "sha256", "bytes", "step",
                          "spoke", "revision", "handoff"):
                self.assertIn(field, entry)
            path = os.path.join(result["out_dir"], entry["file"])
            self.assertTrue(os.path.isfile(path), entry["file"])
            payload = _read_bytes(path)
            self.assertEqual(len(payload), entry["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), entry["sha256"])
            if entry["kind"] == "image":
                self.assertTrue(payload.startswith(b"\x89PNG"), "image artifact is not a PNG")
        # Every routed step names its lane and spoke (M-3: engine always named).
        for step in m["plan"]["steps"]:
            self.assertIn(step["lane"], ("openai", "gemini", "image"))
            self.assertTrue(step["spoke"])
            self.assertTrue(step["reason"])

    def test_factsheet_content_flows_through_tokens(self):
        fx = self.fixtures["factsheet"]
        result = self._run(fx)
        texts = []
        for entry in result["manifest"]["artifacts"]:
            if entry["kind"] in ("text", "json"):
                texts.append(_read_text(os.path.join(result["out_dir"], entry["file"])))
        combined = "\n".join(texts)
        for term in fx["expected"]["content_terms"]:
            self.assertIn(term, combined, f"source data {term!r} did not reach the artifacts")

    def test_reruns_are_byte_identical(self):
        fx = self.fixtures["logo"]
        clock = lambda: 1_789_000_000.0
        a = self._run(fx, subdir="det-a", run_id="fixedrun", clock=clock)
        b = self._run(fx, subdir="det-b", run_id="fixedrun", clock=clock)
        self.assertEqual(_read_bytes(a["manifest_path"]), _read_bytes(b["manifest_path"]))
        for ea, eb in zip(a["manifest"]["artifacts"], b["manifest"]["artifacts"]):
            pa = _read_bytes(os.path.join(a["out_dir"], ea["file"]))
            pb = _read_bytes(os.path.join(b["out_dir"], eb["file"]))
            self.assertEqual(pa, pb, f"{ea['name']} differs between identical runs")

    @unittest.skipUnless(HAVE_USAGE, f"usage module not importable from {USAGE_PATH}")
    def test_every_spoke_call_lands_in_the_ledger(self):
        db = os.path.join(self._tmp.name, "loom-usage.sqlite3")
        ledger = usage.UsageLedger(db)

        def hook(provider, model, units, meta):
            ledger.record(provider, model, units, thread_id=meta["run_id"],
                          metadata=meta, estimated_cost_usd=0.0)

        result = self._run(self.fixtures["logo"], usage_hook=hook)
        events = list(ledger.events(limit=100))
        # fast mode: 1 planner call + 3 woven steps
        self.assertEqual(len(events), 4)
        self.assertTrue(all(e.provider == "demo" for e in events))
        self.assertTrue(all(e.thread_id == result["run_id"] for e in events))
        self.assertEqual(ledger.spend_usd(), 0.0)
        self.assertEqual(ledger.unpriced_count(), 0)

    def test_thinking_mode_critiques_and_accepts(self):
        result = self._run(self.fixtures["poster"], mode="thinking")
        m = result["manifest"]
        self.assertEqual(m["critique"]["verdict"], "accept")
        self.assertIsNotNone(m["scorecard"])
        self.assertIn("step_budget", m["scorecard"])
        self.assertTrue(all(a["revision"] == 0 for a in m["artifacts"]))

    def test_thinking_mode_mends_blockers_exactly_once(self):
        critic = helix_ref.ScriptedCriticSpoke({
            "protocol": "conductor-critique/1",
            "verdict": "revise",
            "notes": [{
                "artifact": "logo-mark", "severity": "blocker",
                "note": "Strokes too thin to read at 32 pixels.",
                "fix_hint": "Thicken every stroke by 40 percent.",
            }],
        })
        result = self._run(self.fixtures["logo"], mode="thinking", critic=critic)
        m = result["manifest"]
        self.assertEqual(m["critique"]["verdict"], "revise")
        revisions = {a["name"]: a["revision"] for a in m["artifacts"]}
        self.assertEqual(revisions["logo-mark"], 1, "flagged artifact must be re-run once")
        self.assertEqual(revisions["direction"], 0)
        self.assertEqual(revisions["style-note"], 0)


# ---------------------------------------------------------------------------
# 6. Real loom (07-loom/loom.py) — demo mode must be keyless and offline
# ---------------------------------------------------------------------------

@unittest.skipUnless(HAVE_LOOM, f"loom module not importable from {LOOM_PATH}")
class LoomDemoModeTests(unittest.TestCase):
    def setUp(self):
        self._saved_env = {}
        for key in LIVE_KEY_ENVS + ["LOOM_PROVIDER"]:
            self._saved_env[key] = os.environ.pop(key, None)
        self._tmp = tempfile.TemporaryDirectory(prefix="helix-realloom-")
        self.addCleanup(self._tmp.cleanup)
        self.lm = loom.Loom(loom.Config())  # no keys configured

    def tearDown(self):
        for key, val in self._saved_env.items():
            if val is not None:
                os.environ[key] = val

    def test_provider_resolution_defaults_to_demo_without_keys(self):
        self.assertEqual(self.lm.resolve(), "demo")

    def test_demo_images_render_offline_with_provenance_sidecars(self):
        fx = load_fixtures()["poster"]
        with forbid_network():
            assets = self.lm.image(fx["request"], self._tmp.name, provider="demo", n=1)
        self.assertGreaterEqual(len(assets), 1)
        for asset in assets:
            self.assertTrue(os.path.isfile(asset.path), asset.path)
            self.assertEqual(asset.provider, "demo")
            sidecar = asset.path + ".json"
            self.assertTrue(os.path.isfile(sidecar), "missing provenance sidecar")
            with open(sidecar, encoding="utf-8") as f:
                side = json.load(f)
            self.assertEqual(side["provider"], "demo")
            self.assertEqual(side["prompt"], fx["request"])
            if asset.mime == "image/png":
                self.assertTrue(_read_bytes(asset.path).startswith(b"\x89PNG"))

    def test_demo_brief_is_deterministic_and_complete(self):
        fx = load_fixtures()["logo"]
        with forbid_network():
            b1 = self.lm.brief(fx["request"], provider="demo")
            b2 = self.lm.brief(fx["request"], provider="demo")
        self.assertEqual(b1, b2, "demo brief expansion must be deterministic")
        for key in ("title", "palette", "deliverables", "image_prompts", "tone"):
            self.assertIn(key, b1)
        self.assertEqual(b1["_provenance"]["provider"], "demo")

    def test_live_provider_without_key_fails_loud_before_network(self):
        with forbid_network():
            with self.assertRaises(loom.MissingKeyError):
                self.lm.image("a poster", self._tmp.name, provider="openai")
            with self.assertRaises(loom.MissingKeyError):
                self.lm.brief("a poster", provider="gemini")

    def test_video_never_auto_routes_to_a_paid_backend(self):
        with forbid_network():
            asset = self.lm.video("slow orbit around a helix", self._tmp.name)
        self.assertEqual(asset.provider, "demo")
        self.assertTrue(os.path.isfile(asset.path))


# ---------------------------------------------------------------------------
# 7. Canvas pin integration — manifest artifacts pinned onto a board
# ---------------------------------------------------------------------------

@unittest.skipUnless(HAVE_SCHEMA, f"schema not found at {SCHEMA_PATH}")
class CanvasPinIntegrationTests(unittest.TestCase):
    KIND_MAP = {"image": "image", "text": "text", "json": "text"}

    def test_demo_run_artifacts_pin_to_the_board(self):
        with tempfile.TemporaryDirectory(prefix="helix-pin-") as tmp:
            fx = load_fixtures()["logo"]
            result = helix_ref.demo_run(fx["request"], out_dir=os.path.join(tmp, "run"),
                                        data=fx.get("data"))
            con = sqlite3.connect(":memory:")
            con.execute("PRAGMA foreign_keys = ON")
            con.executescript(SCHEMA_SQL)
            con.execute(
                "INSERT INTO projects (id, name, slug, created_at, updated_at)"
                " VALUES ('prj_1', 'Logo run', 'logo-run', ?, ?)", (NOW_MS, NOW_MS))
            con.execute(
                "INSERT INTO boards (id, project_id, created_at, updated_at)"
                " VALUES ('brd_1', 'prj_1', ?, ?)", (NOW_MS, NOW_MS))
            con.execute(
                "INSERT INTO board_layers (id, board_id, created_at, updated_at)"
                " VALUES ('lyr_1', 'brd_1', ?, ?)", (NOW_MS, NOW_MS))

            artifacts = result["manifest"]["artifacts"]
            for i, entry in enumerate(artifacts):
                aid = f"art_{i}"
                con.execute(
                    "INSERT INTO artifacts (id, project_id, kind, mime, storage, uri,"
                    " sha256, byte_size, title, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (aid, "prj_1", self.KIND_MAP[entry["kind"]],
                     "image/png" if entry["kind"] == "image" else "text/markdown",
                     "blob", f"{entry['sha256'][:2]}/{entry['sha256']}",
                     entry["sha256"], entry["bytes"], entry["name"], NOW_MS),
                )
                con.execute(
                    "INSERT INTO board_nodes (id, board_id, layer_id, kind, artifact_id,"
                    " x, y, w, h, created_at, updated_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (f"nod_{i}", "brd_1", "lyr_1", "artifact", aid,
                     40.0 + i * 360.0, 40.0, 320.0, 240.0, NOW_MS, NOW_MS),
                )

            rows = con.execute(
                "SELECT node_id, artifact_id, artifact_kind, x FROM v_board_scene ORDER BY x"
            ).fetchall()
            self.assertEqual(len(rows), len(artifacts))
            self.assertEqual({r[1] for r in rows}, {f"art_{i}" for i in range(len(artifacts))})
            # Pinned nodes carry real geometry, spaced on the grid we asked for.
            self.assertEqual([r[3] for r in rows], [40.0 + i * 360.0 for i in range(len(rows))])
            con.close()


# ---------------------------------------------------------------------------
# Qualitative eval scorecard (python3 test_helix.py --eval); see EVAL.md
# ---------------------------------------------------------------------------

def _score_fixture(fx: dict, tmp: str):
    exp = fx["expected"]
    notes = []
    try:
        plan = CP.parse_plan(plan_text_for(fx))
    except Exception as exc:
        return [0, 0, 0, 0, 0], [f"plan failed to parse: {exc}"]
    steps = _pget(plan, "steps")
    instructions = " ".join(_sget(s, "instruction", "") for s in steps)
    reading = _pget(plan, "reading", "") or ""

    # D1 task-type fidelity: the crafts the task demands are present.
    crafts = {_sget(s, "craft") for s in steps}
    req_ok = all(c in crafts for c in exp["crafts_required"])
    any_ok = not exp["crafts_any_of"] or any(c in crafts for c in exp["crafts_any_of"])
    d1 = 2 if (req_ok and any_ok) else (1 if (req_ok or any_ok) else 0)
    if d1 < 2:
        notes.append(f"crafts seen {sorted(crafts)}, required {exp['crafts_required']}")

    # D2 constraint capture: palette + names restated inside instructions/reading.
    wanted = list(exp.get("palette", [])) + list(exp.get("must_mention", []))
    hits = sum(1 for w in wanted if w in instructions or w in reading)
    frac = hits / len(wanted) if wanted else 1.0
    d2 = 2 if frac == 1.0 else (1 if frac >= 0.5 else 0)
    if d2 < 2:
        missing = [w for w in wanted if w not in instructions and w not in reading]
        notes.append(f"constraints not restated: {missing}")

    # D3 routing correctness.
    try:
        lanes = _route_decisions(plan, fx["request"])
        used = set(lanes.values())
        if used & set(exp["lanes_forbidden"]) or None in used or len(lanes) != len(steps):
            d3 = 0
            notes.append(f"forbidden/unbound lanes: {sorted(used)}")
        elif all(l in used for l in exp["lanes_required"]):
            d3 = 2
        else:
            d3 = 1
            notes.append(f"lanes used {sorted(used)}, required {exp['lanes_required']}")
    except Exception as exc:
        d3 = 0
        notes.append(f"routing failed: {exc}")

    # D4 plan hygiene: size, handoff, self-contained acceptance criteria.
    handoff = _pget(plan, "handoff", [])
    d4 = 2
    if len(steps) < exp["min_steps"] or len(handoff) < exp["handoff_min"]:
        d4 = 1
        notes.append(f"{len(steps)} steps / {len(handoff)} handoff, "
                     f"wanted >= {exp['min_steps']} / {exp['handoff_min']}")
    if not _pget(plan, "assumptions"):
        d4 = min(d4, 1)
        notes.append("no assumptions recorded for an underspecified brief")

    # D5 pin & canvas: run the demo loom, verify manifest + board pinning.
    d5 = 0
    try:
        result = helix_ref.demo_run(fx["request"], out_dir=os.path.join(tmp, fx["id"]),
                                    data=fx.get("data"))
        m = result["manifest"]
        files_ok = all(
            hashlib.sha256(_read_bytes(os.path.join(result["out_dir"], a["file"])))
            .hexdigest() == a["sha256"]
            for a in m["artifacts"]
        )
        handoff_ok = sum(a["handoff"] for a in m["artifacts"]) >= exp["handoff_min"]
        if files_ok and handoff_ok:
            d5 = 1
            if HAVE_SCHEMA:
                con = sqlite3.connect(":memory:")
                con.executescript(SCHEMA_SQL)
                con.execute("INSERT INTO projects (id,name,slug,created_at,updated_at)"
                            " VALUES ('p','p','p',0,0)")
                con.execute("INSERT INTO boards (id,project_id,created_at,updated_at)"
                            " VALUES ('b','p',0,0)")
                con.execute("INSERT INTO board_layers (id,board_id,created_at,updated_at)"
                            " VALUES ('l','b',0,0)")
                for i, a in enumerate(m["artifacts"]):
                    con.execute(
                        "INSERT INTO artifacts (id,project_id,kind,mime,storage,uri,sha256,"
                        "created_at) VALUES (?,?,?,?,?,?,?,0)",
                        (f"a{i}", "p", "image" if a["kind"] == "image" else "text",
                         "application/octet-stream", "blob",
                         f"{a['sha256'][:2]}/{a['sha256']}", a["sha256"]))
                    con.execute(
                        "INSERT INTO board_nodes (id,board_id,layer_id,kind,artifact_id,"
                        "x,y,created_at,updated_at) VALUES (?,?,?,?,?,?,?,0,0)",
                        (f"n{i}", "b", "l", "artifact", f"a{i}", i * 360.0, 0.0))
                (pinned,) = con.execute("SELECT COUNT(*) FROM v_board_scene").fetchone()
                con.close()
                if pinned == len(m["artifacts"]):
                    d5 = 2
                else:
                    notes.append(f"only {pinned}/{len(m['artifacts'])} artifacts pinned")
            else:
                notes.append("schema unavailable; board-pin half of D5 not scored")
        else:
            notes.append("manifest artifacts missing on disk or handoff too small")
        terms = exp.get("content_terms", [])
        if terms:
            texts = "".join(
                _read_text(os.path.join(result["out_dir"], a["file"]))
                for a in m["artifacts"] if a["kind"] in ("text", "json"))
            missed = [t for t in terms if t not in texts]
            notes.append("content flow: OK — all source terms reached the artifacts"
                         if not missed else f"content flow: MISSING {missed}")
    except Exception as exc:
        notes.append(f"demo run failed: {exc}")

    return [d1, d2, d3, d4, d5], notes


def run_eval() -> int:
    print("# Atelier Helix — qualitative eval scorecard\n")
    print(f"- conductor parse/routing  : {CP_SOURCE}")
    print(f"- store schema             : {SCHEMA_PATH if HAVE_SCHEMA else 'NOT FOUND'}")
    print(f"- usage ledger             : {USAGE_PATH if HAVE_USAGE else 'NOT FOUND'}")
    print(f"- media loom (demo mode)   : {LOOM_PATH if HAVE_LOOM else 'NOT FOUND'}")
    print(f"- pipeline demo runs       : helix_ref.py (deterministic scripted spokes)\n")
    header = ("| fixture | D1 task-type | D2 constraints | D3 routing "
              "| D4 hygiene | D5 pin+canvas | total /10 |")
    print(header)
    print("|" + "---|" * 7)
    totals = []
    all_notes = []
    with tempfile.TemporaryDirectory(prefix="helix-eval-") as tmp:
        for fid, fx in load_fixtures().items():
            scores, notes = _score_fixture(fx, tmp)
            totals.append(sum(scores))
            print(f"| {fid} | " + " | ".join(str(s) for s in scores)
                  + f" | **{sum(scores)}** |")
            all_notes.extend(f"- `{fid}`: {n}" for n in notes)
    print(f"\n**Overall: {sum(totals)}/{10 * len(totals)}**\n")
    if all_notes:
        print("Notes:")
        print("\n".join(all_notes))
    return 0


if __name__ == "__main__":
    if "--eval" in sys.argv:
        sys.argv.remove("--eval")
        sys.exit(run_eval())
    unittest.main()
