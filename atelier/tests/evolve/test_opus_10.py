#!/usr/bin/env python3
"""Opus-10 — Round 20 (acceptance scorecard) verification.

`SCORECARD.json` is the only artefact of this round, so the only thing worth
testing is whether it tells the truth. A card can be wrong in two directions
and both are checked here:

* **too rosy** — it claims something the tree does not do. Every entry in
  `remaining_product_holes` is therefore *reproduced* against live modules
  (demo lane, tempdirs, no keys, no network). If a hole is quietly fixed the
  matching test fails and the card has to lose the line; if the card drops a
  line while the hole is still live, `HolesAreNamed` fails.
* **stale** — it repeats a sentence a later round disproved. The two
  behavioural notes that carry numbers (`priced`, remote CI) are measured
  rather than read.

Nothing here contacts a provider. The suite runs the demo conductor, which
is hardwired offline.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EVOLVE = ROOT / "atelier" / "research" / "evolve"
CARD = EVOLVE / "SCORECARD.json"
LEGION = EVOLVE / "legion"
APP_JS = ROOT / "atelier" / "web" / "app.js"
SERVER = ROOT / "atelier" / "server.py"

# Every product module the card speaks for. Tests and research are excluded:
# research is a spec tree that still describes features live Helix does not
# have, which is precisely why the card cannot be read off it.
PRODUCT = sorted((ROOT / "atelier" / "helix").rglob("*.py")) + [
    SERVER,
    ROOT / "atelier" / "launch.py",
    APP_JS,
]


def load_card() -> dict:
    return json.loads(CARD.read_text(encoding="utf-8"))


class _Studio:
    """A throwaway Helix on the demo lane: own db, own artifacts dir, no keys."""

    def __init__(self, stack: unittest.TestCase):
        from atelier.helix.conductor import Conductor
        from atelier.helix.keyring import Keyring
        from atelier.helix.store import Memory

        tmp = tempfile.TemporaryDirectory()
        stack.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.artifacts = self.dir / "artifacts"
        self.artifacts.mkdir()
        self.memory = Memory(self.dir / "atelier.db")
        self.keyring = Keyring(self.dir / "keyring.json")
        self.conductor = Conductor(
            memory=self.memory, keyring=self.keyring, artifacts_dir=self.artifacts
        )

    def project(self, name: str = "card", brand: dict | None = None):
        project = self.memory.create_project(name, brand or {})
        if brand:
            self.memory.update_brand_kit(project["id"], brand)
        thread = self.memory.create_thread(project["id"], topic="card")
        return project, thread

    def run(self, prompt: str, project, thread, **kwargs):
        return self.conductor.run(
            project_id=project["id"],
            thread_id=thread["id"],
            prompt=prompt,
            provider="demo",
            mode="fast",
            **kwargs,
        )


class CardShape(unittest.TestCase):
    """The arithmetic, before any of the prose."""

    def setUp(self):
        self.card = load_card()

    def test_gate_and_counts(self):
        self.assertEqual(self.card["rounds_total"], 20)
        self.assertEqual(len(self.card["rounds"]), 20)
        self.assertGreaterEqual(self.card["passed"], self.card["gate"])
        self.assertGreaterEqual(self.card["gate"], 16)
        self.assertLessEqual(self.card["passed"], self.card["rounds_total"])
        self.assertTrue(self.card["gate_met"])
        for name in ("fail_closed", "quote_before_commit", "no_silent_demo", "stdlib_only"):
            self.assertTrue(self.card["gates"][name], name)

    def test_passed_is_the_count_of_passing_rounds(self):
        """`passed` used to be a hand-typed number sitting next to a list."""
        self.assertEqual(self.card["passed"], sum(1 for r in self.card["rounds"] if r.get("pass")))
        self.assertEqual(self.card["technical_passed"], self.card["passed"])

    def test_every_round_is_numbered_and_owned(self):
        self.assertEqual([r["n"] for r in self.card["rounds"]], list(range(1, 21)))
        self.assertTrue(all(r.get("pass") for r in self.card["rounds"]))
        self.assertEqual(len({r["name"] for r in self.card["rounds"]}), 20)
        for r in self.card["rounds"]:
            self.assertIn(r["owner"], {"fable", "opus"})
            self.assertEqual(r["owner"], "fable" if r["n"] % 2 else "opus", r["n"])

    def test_a_note_is_prose_or_absent_never_empty(self):
        for r in self.card["rounds"]:
            if "note" in r:
                self.assertIsInstance(r["note"], str)
                self.assertGreater(len(r["note"].strip()), 12, r["n"])

    def test_every_round_has_a_live_agent_note_on_disk(self):
        """R1–R19 were closed by live verifiers; R20 is this file's own round."""
        for r in self.card["rounds"]:
            folder = ("fable" if r["owner"] == "fable" else "opus") + f"-{(r['n'] + 1) // 2:02d}"
            notes = list((LEGION / folder).glob("*.md"))
            self.assertEqual(len(notes), 1, folder)
            self.assertGreater(len(notes[0].read_text(encoding="utf-8")), 400, folder)

    def test_round_20_says_what_this_file_is(self):
        note = self.card["rounds"][-1]["note"].lower()
        self.assertEqual(self.card["rounds"][-1]["name"], "acceptance-scorecard")
        self.assertIn("this file", note)
        self.assertIn("not lovart-complete", note)


class NotLovartComplete(unittest.TestCase):
    """The four booleans the whole card hangs on."""

    def setUp(self):
        self.card = load_card()
        self.holes = " ".join(self.card["remaining_product_holes"]).lower()

    def test_does_not_claim_lovart_or_paid(self):
        self.assertFalse(self.card["lovart_complete"])
        self.assertFalse(self.card["paid_loop_proven"])
        self.assertTrue(self.card["demo_loop"])
        self.assertTrue(self.card["honest"])

    def test_holes_name_the_six_that_must_never_go_quiet(self):
        for needle in (
            "contact sheet",
            "stylelock",
            "stream=0",
            "redo",
            "echo",
            "paid",
        ):
            self.assertIn(needle, self.holes, needle)

    def test_no_hole_is_a_placeholder(self):
        holes = self.card["remaining_product_holes"]
        self.assertGreaterEqual(len(holes), 8)
        self.assertEqual(len(set(holes)), len(holes))
        for hole in holes:
            self.assertGreater(len(hole.strip()), 30, hole)

    def test_the_paid_loop_cannot_be_claimed_from_this_environment(self):
        keys = [k for k in ("OPENAI_API_KEY", "GEMINI_API_KEY") if os.environ.get(k)]
        self.assertFalse(self.card["paid_loop_proven"], f"no run recorded; keys present: {keys}")
        self.assertIn("api_key", self.holes)


class HolesAreNamed(unittest.TestCase):
    """Each hole below is reproduced against the live tree. The pairing is the
    point: the test says what the code does, the assertion says the card has to
    admit it."""

    def setUp(self):
        self.card = load_card()
        self.holes = self.card["remaining_product_holes"]

    def assertHole(self, *needles: str):
        joined = " ".join(self.holes).lower()
        for needle in needles:
            self.assertIn(needle.lower(), joined, f"live hole is not on the card: {needle}")

    # -- 1. the raster ----------------------------------------------------

    def test_png_export_never_rasterises_the_artwork(self):
        from atelier.helix.exportfmt import export_artifact_bytes, export_project_bytes, png_dimensions

        studio = _Studio(self)
        project, thread = studio.project()
        result = studio.run("a quiet poster", project, thread)
        art = studio.memory.get_artifact(result["artifacts"][0]["id"])
        svg_bytes = (studio.artifacts / f"{art['id']}.svg").read_bytes()
        self.assertIn(b"<svg", svg_bytes)

        board, mime, _ = export_project_bytes(
            studio.memory, studio.artifacts, project["id"], fmt="svg"
        )
        self.assertEqual(mime, "image/svg+xml")
        self.assertIn(b"<circle", board)  # the artwork is inlined, vector intact

        sheet, mime, name = export_project_bytes(
            studio.memory, studio.artifacts, project["id"], fmt="png"
        )
        self.assertEqual(mime, "image/png")
        self.assertIn("sheet.png", name)
        self.assertNotIn(b"<circle", sheet)  # …and nowhere in the raster
        # 640 wide whatever the board holds: the sheet is a fixed canvas the
        # exporter paints node boxes onto, not a view of the 1024² artwork
        self.assertEqual((png_dimensions(sheet) or (0, 0))[0], 640)
        self.assertNotEqual(png_dimensions(sheet), (1024, 1024))

        card, mime, _ = export_artifact_bytes(art, studio.artifacts, fmt="png")
        self.assertEqual(mime, "image/png")
        self.assertNotIn(b"<circle", card)
        self.assertHole("contact sheet", "labeled card")

    # -- 2. StyleLock -----------------------------------------------------

    def test_stylelock_is_prompt_text_and_nothing_measures_the_result(self):
        from atelier.helix.loom import style_lock

        locked = style_lock("a poster", palette=["#0B3954", "#E0A458"], title="QLD")
        self.assertTrue(locked.startswith("[StyleLock "))
        self.assertIn("palette=#0B3954,#E0A458", locked)
        self.assertIn("a poster", locked)
        for path in PRODUCT:
            body = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("delta_e", body, path.name)
            self.assertNotIn("deltae", body, path.name)
        self.assertHole("StyleLock", "ΔE")

    # -- 3. the dock does not stream --------------------------------------

    def test_the_ui_asks_for_stream_0_and_owns_no_eventsource(self):
        app = APP_JS.read_text(encoding="utf-8")
        server = SERVER.read_text(encoding="utf-8")
        self.assertIn("/run?stream=0", app)
        self.assertNotIn("stream=1", app)
        self.assertNotIn("EventSource", app)
        self.assertIn("text/event-stream", server)  # live, and unused by the client
        self.assertHole("stream=0", "EventSource")

    # -- 4. undo ----------------------------------------------------------

    def test_undo_drops_the_node_and_leaves_the_file(self):
        studio = _Studio(self)
        project, thread = studio.project()
        result = studio.run("a quiet poster", project, thread)
        art_id = result["artifacts"][0]["id"]
        before = sorted(p.name for p in studio.artifacts.iterdir())

        self.assertTrue(studio.memory.undo(project["id"])["undone"])
        self.assertEqual(len(studio.memory.list_nodes(project["id"])), 0)
        self.assertIsNotNone(studio.memory.get_artifact(art_id))  # row survives
        self.assertEqual(sorted(p.name for p in studio.artifacts.iterdir()), before)  # file too

        for path in PRODUCT:
            self.assertNotIn("redo", path.read_text(encoding="utf-8").lower(), path.name)
        self.assertHole("no redo", "on disk")

    # -- 5. no caret ------------------------------------------------------

    def test_text_edit_is_a_window_prompt(self):
        app = APP_JS.read_text(encoding="utf-8")
        self.assertIn("prompt(TEXT_SPEC_LABEL", app)
        self.assertNotIn("contentEditable", app)
        self.assertNotIn("caret", app.lower())
        self.assertHole("window.prompt", "caret")

    # -- 6. the reference never leaves the machine ------------------------

    def test_a_reference_upload_is_a_text_mention_not_pixels(self):
        studio = _Studio(self)
        project, thread = studio.project()
        upload = studio.memory.add_artifact(
            project_id=project["id"],
            thread_id=None,
            kind="upload",
            mime="image/png",
            prompt="client-logo.png",
            provider="upload",
            model="upload",
        )
        result = studio.run(
            "restyle this in navy", project, thread, parent_artifact_id=upload["id"]
        )
        woven = result["artifacts"][0]["prompt"]
        self.assertIn("Spot-edit of previous artifact", woven)
        self.assertIn("Original brief: client-logo.png", woven)  # the filename, not the file
        openai = (ROOT / "atelier" / "helix" / "spokes" / "openai_spoke.py").read_text("utf-8")
        self.assertIn("/v1/images/generations", openai)  # text-to-image only
        self.assertNotIn("/v1/images/edits", openai)
        self.assertHole("pixels never leave", "text-only")

    # -- 7. a 4-up is four strangers --------------------------------------

    def test_variants_share_no_identity_and_cannot_be_promoted(self):
        studio = _Studio(self)
        project, thread = studio.project()
        result = studio.run("four variants of a quiet poster", project, thread, variants=4)
        self.assertEqual(len(result["artifacts"]), 4)
        for art in result["artifacts"]:
            self.assertIsNone(studio.memory.get_artifact(art["id"])["parent_id"])
        for node in studio.memory.list_nodes(project["id"]):
            self.assertEqual(node["meta"], {})
        server = SERVER.read_text(encoding="utf-8")
        for route in ("/pick", "/promote", "/winner"):
            self.assertNotIn(route, server)
        self.assertHole("pick-winner", "variant")

    # -- 8/9. the eval scorer ---------------------------------------------

    def _score(self, fixture: dict) -> dict:
        from atelier.helix import evalrun

        studio = _Studio(self)
        return evalrun.run_fixture(
            fixture,
            memory=studio.memory,
            conductor=studio.conductor,
            artifacts_dir=studio.artifacts,
        )

    def test_the_factsheet_fixture_fails_and_the_others_can_pass_on_an_echo(self):
        from atelier.helix import evalrun
        from atelier.helix.loom import demo_svg

        by_name = {p.name: p for p in evalrun.list_fixtures()}
        factsheet = evalrun.load_fixture(by_name["brief_factsheet_legal_directory.json"])
        self.assertNotIn("brand", factsheet)  # no kit, so nothing tints the SVG
        scored = self._score(factsheet)
        self.assertFalse(scored["ok"])
        self.assertTrue(all(m["hit"] for m in scored["must_mention"]))
        self.assertFalse(any(p["hit"] for p in scored["palette"]))
        # …because the caption echo stops at 180 characters and the hexes are past it
        self.assertNotIn("#0B3954", demo_svg(factsheet["request"]))
        self.assertGreater(factsheet["request"].index("#0B3954"), 180)

        brand_apply = evalrun.load_fixture(by_name["brief_brand_kit_apply.json"])
        self.assertTrue(self._score(brand_apply)["ok"])
        no_kit = json.loads(json.dumps(brand_apply))
        no_kit.pop("brand")
        echo = self._score(no_kit)
        self.assertTrue(echo["ok"])  # passes with no kit at all: caption echo only
        self.assertTrue(all(p["hit"] for p in echo["palette"]))

        scrubbed = json.loads(json.dumps(brand_apply))
        scrubbed["request"] = scrubbed["request"].replace(
            "set headings in Archivo and body copy in Inter", "set headings and body copy in the kit fonts"
        )
        self.assertFalse(self._score(scrubbed)["ok"])  # the kit alone cannot carry the mention
        self.assertHole("caption echo", "brief echo")

    # -- 10. the kit forgets its type -------------------------------------

    def test_a_brand_kit_drops_its_fonts(self):
        studio = _Studio(self)
        project, _ = studio.project(
            brand={"name": "Atelier Helix", "palette": ["#1A5FB4"], "fonts": {"heading": "Archivo"}}
        )
        stored = studio.memory.get_project(project["id"])["brand_kit"]
        self.assertEqual(set(stored), {"name", "palette", "voice"})
        self.assertNotIn("fonts", stored)
        self.assertHole("fonts")

    # -- 11. non-Latin briefs ---------------------------------------------

    def test_a_non_latin_brief_downloads_as_its_hex_id(self):
        from atelier.helix.loom import download_filename

        art = {"prompt": "静かなポスター", "mime": "image/svg+xml", "id": "deadbeefcafe0123"}
        self.assertEqual(download_filename(art), "deadbeefcafe.svg")
        self.assertEqual(download_filename({**art, "prompt": "Кириллица"}), "deadbeefcafe.svg")
        self.assertEqual(download_filename({**art, "prompt": "a quiet poster"}), "a-quiet-poster.svg")
        self.assertHole("hex id")

    # -- 12. openai_compat ------------------------------------------------

    def test_openai_compat_accepts_any_host(self):
        from atelier.helix.keyring import ALLOWED_HOST_SUFFIXES, ENV_MAP, Keyring

        self.assertIn("openai_compat", ENV_MAP)
        self.assertNotIn("openai_compat", ALLOWED_HOST_SUFFIXES)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        ring = Keyring(Path(tmp.name) / "keyring.json")
        with self.assertRaises(ValueError):
            ring.put("openai", key="sk-x", base_url="https://evil.example")
        ring.put("openai_compat", key="sk-x", base_url="http://evil.example/v1")
        self.assertEqual(ring.get_base_url("openai_compat"), "http://evil.example/v1")
        self.assertTrue(ring.public_status()["openai_compat"]["configured"])
        self.assertHole("openai_compat")


class NotesThatCarryNumbers(unittest.TestCase):
    """Two round notes make measurable claims. Both were wrong or stale once."""

    def setUp(self):
        self.card = load_card()
        self.rounds = {r["n"]: r for r in self.card["rounds"]}

    def test_round_2_does_not_repeat_the_priced_sentence_r18_disproved(self):
        from atelier.helix.quote import quote_run
        from atelier.helix.store import Memory

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        memory = Memory(Path(tmp.name) / "q.db")
        project = memory.create_project("q", {})
        thread = memory.create_thread(project["id"])

        def priced(provider: str, model: str) -> bool:
            return quote_run(
                provider=provider,
                model=model,
                prompt="a poster",
                count=1,
                memory=memory,
                thread_id=thread["id"],
            )["priced"]

        self.assertTrue(priced("openai", "gpt-4o-mini"))
        self.assertFalse(priced("openai", "no-such-model-9000"))
        # the free lanes short-circuit, so "unknown models are priced:false" is
        # backwards for exactly half the providers the studio ships
        self.assertTrue(priced("ollama", "no-such-model-9000"))
        self.assertTrue(priced("demo", "no-such-model-9000"))
        note = self.rounds[2]["note"].lower()
        self.assertNotIn("unknown models priced:false", note)
        self.assertIn("402 does not persist the prompt", note)

    def test_round_17_matches_the_recorded_remote_run(self):
        ci = self.card["remote_ci"]
        note = self.rounds[17]["note"].lower()
        if ci.get("proven"):
            self.assertIn("actions/runs/", ci["run"])
            self.assertEqual(ci["python"], "3.11")
            self.assertNotIn("unproven", note)
        else:
            self.assertIn("unproven", note)
        workflow = (ROOT / ".github" / "workflows" / "atelier.yml").read_text(encoding="utf-8")
        self.assertIn(f'python-version: "{ci["python"]}"', workflow)

    def test_the_tree_runs_on_the_python_ci_pins(self):
        """The local gate is 3.12 and could not see a 3.12-only builtin."""
        from atelier.helix.loom import text_meta

        self.assertEqual(text_meta({"font_size": 99999})["font_size"], 96)
        for path in PRODUCT:
            if path.suffix != ".py":
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                code = line.split("#", 1)[0]
                if ".is_integer()" in code:
                    self.assertIn("float(", code.split(".is_integer()")[0], f"{path.name}: {line}")


class MetaGateStillHolds(unittest.TestCase):
    def test_round17to20_meta_scorecard_gate_passes(self):
        from atelier.tests.test_evolve import Round17to20Meta

        suite = unittest.TestLoader().loadTestsFromName(
            "test_scorecard_gate", Round17to20Meta
        )
        with open(os.devnull, "w", encoding="utf-8") as sink:
            result = unittest.TextTestRunner(stream=sink, verbosity=0).run(suite)
        self.assertEqual((result.failures, result.errors), ([], []))


if __name__ == "__main__":
    unittest.main()
