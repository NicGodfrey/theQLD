#!/usr/bin/env python3
"""Fable-10 — Round 19 (eval fixtures) verification.

Fixtures load, a demo weave can be scored for must_mention + palette, and the
scorer's honest edges are pinned: the kit palette genuinely lands as SVG fill,
but brief text echoed into the intent / artifact prompt / SVG caption can
satisfy must_mention and palette on its own, and the factsheet fixture does
not pass the demo lane at all.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.helix.conductor import Conductor  # noqa: E402
from atelier.helix.evalrun import list_fixtures, load_fixture, run_fixture, score_result  # noqa: E402
from atelier.helix.keyring import Keyring  # noqa: E402
from atelier.helix.store import Memory  # noqa: E402

EVAL = ROOT / "atelier" / "data" / "eval"


class _DemoRuntime:
    """Throwaway Memory + Conductor + artifacts dir, demo lane only."""

    def __enter__(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.artifacts = root / "artifacts"
        self.artifacts.mkdir()
        self.memory = Memory(root / "helix.sqlite3")
        self.conductor = Conductor(self.memory, Keyring(root / "k.json"), self.artifacts)
        return self

    def __exit__(self, *exc):
        self.memory.close()
        self._tmp.cleanup()
        return False

    def run(self, fixture: dict) -> dict:
        return run_fixture(
            fixture,
            memory=self.memory,
            conductor=self.conductor,
            artifacts_dir=self.artifacts,
        )

    def svg_texts(self) -> list[str]:
        return [p.read_text(encoding="utf-8") for p in sorted(self.artifacts.glob("*.svg"))]


class FixturesLoad(unittest.TestCase):
    def test_four_briefs_exist(self):
        names = {p.name for p in list_fixtures(EVAL)}
        self.assertEqual(
            names,
            {
                "brief_logo.json",
                "brief_poster.json",
                "brief_factsheet_legal_directory.json",
                "brief_brand_kit_apply.json",
            },
        )
        for path in list_fixtures(EVAL):
            data = load_fixture(path)
            self.assertIn("request", data)
            self.assertIn("expected", data)
            self.assertTrue(data.get("id"))
            self.assertTrue(data["expected"].get("must_mention"))
            self.assertTrue(data["expected"].get("palette"))
            # The richer research graph stays documentary on the fixture.
            self.assertIn("crafts_required", data["expected"])
            self.assertIn("lanes_required", data["expected"])

    def test_load_fixture_rejects_missing_keys(self):
        tmp = tempfile.TemporaryDirectory()
        bad = Path(tmp.name) / "brief_bad.json"
        bad.write_text(json.dumps({"request": "no expected"}), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_fixture(bad)
        bad.write_text(json.dumps({"expected": {}}), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_fixture(bad)
        tmp.cleanup()

    def test_list_fixtures_only_matches_brief_prefix(self):
        tmp = tempfile.TemporaryDirectory()
        folder = Path(tmp.name)
        (folder / "brief_a.json").write_text("{}", encoding="utf-8")
        (folder / "notes.json").write_text("{}", encoding="utf-8")
        (folder / "brief_dir.json").mkdir()
        self.assertEqual([p.name for p in list_fixtures(folder)], ["brief_a.json"])
        tmp.cleanup()


class ScorerSemantics(unittest.TestCase):
    def test_score_result_without_a_server(self):
        fixture = {
            "id": "toy",
            "expected": {"must_mention": ["Helix"], "palette": ["#112233"], "lanes_forbidden": ["video"]},
        }
        result = {
            "message": "Pinned Helix mark",
            "plan": {"intent": "Helix logo"},
            "artifacts": [{"prompt": "Helix", "kind": "image"}],
            "nodes": [{}],
        }
        report = score_result(fixture, result, [b'<svg fill="#112233"></svg>'])
        self.assertTrue(report["ok"])
        miss = score_result(fixture, {"message": "nope", "plan": {}, "artifacts": []}, [b"<svg/>"])
        self.assertFalse(miss["ok"])
        self.assertEqual([m["hit"] for m in miss["must_mention"]], [False])

    def test_forbidden_lane_fails(self):
        fixture = {"id": "toy", "expected": {"lanes_forbidden": ["video"]}}
        report = score_result(fixture, {"message": "", "plan": {}, "artifacts": [{"kind": "video"}]}, [])
        self.assertFalse(report["ok"])
        self.assertEqual(report["forbidden_hits"], ["video"])

    def test_crafts_and_steps_are_not_scored(self):
        # crafts_required / lanes_required / min_steps / handoff_min /
        # deliverable_kinds / content_terms describe the research graph.
        # A result that satisfies none of them still scores ok.
        fixture = {
            "id": "graph-only",
            "expected": {
                "crafts_required": ["render-image", "compose-text"],
                "crafts_any_of": ["synthesize"],
                "lanes_required": ["openai", "gemini", "image"],
                "min_steps": 9,
                "handoff_min": 9,
                "deliverable_kinds": ["image", "text"],
                "content_terms": ["never checked"],
            },
        }
        report = score_result(fixture, {"message": "", "plan": {}, "artifacts": [], "nodes": []}, [])
        self.assertTrue(report["ok"])
        self.assertEqual(report["artifact_count"], 0)
        self.assertEqual(report["node_count"], 0)

    def test_palette_gate_skipped_without_blobs(self):
        # Pinned current behaviour: expected palette with no SVG bytes
        # collected does not fail the run — the misses are only reported.
        fixture = {"id": "soft", "expected": {"must_mention": ["hi"], "palette": ["#ABCDEF"]}}
        report = score_result(fixture, {"message": "hi", "plan": {}, "artifacts": []}, [])
        self.assertTrue(report["ok"])
        self.assertEqual([p["hit"] for p in report["palette"]], [False])

    def test_palette_hex_match_is_case_sensitive(self):
        # Pinned current behaviour: #abcdef does not match fill="#ABCDEF".
        fixture = {"id": "case", "expected": {"palette": ["#abcdef"]}}
        report = score_result(fixture, {"message": "", "plan": {}, "artifacts": []}, [b'<rect fill="#ABCDEF"/>'])
        self.assertFalse(report["ok"])

    def test_zero_artifacts_can_still_pass(self):
        # Pinned current behaviour: the scorer never gates on artifact_count.
        fixture = {"id": "empty", "expected": {"must_mention": ["hi"]}}
        report = score_result(fixture, {"message": "hi", "plan": {}, "artifacts": []}, [])
        self.assertTrue(report["ok"])
        self.assertEqual(report["artifact_count"], 0)


class DemoConductorRuns(unittest.TestCase):
    def test_logo_fixture_through_demo_conductor(self):
        fixture = load_fixture(EVAL / "brief_logo.json")
        # The expected hex sits past the 180-char SVG caption echo, so a hit
        # can only come from the brand-kit fill — verify that premise first.
        self.assertNotIn("#1A5FB4", fixture["request"][:180])
        with _DemoRuntime() as rt:
            report = rt.run(fixture)
            svgs = rt.svg_texts()
        self.assertTrue(report["ok"], report)
        self.assertGreaterEqual(report["artifact_count"], 1)
        self.assertTrue(all(p["hit"] for p in report["palette"]), report)
        self.assertTrue(any('fill="#1A5FB4"' in svg for svg in svgs))

    def test_all_four_fixtures_current_demo_truth(self):
        # Pinned current behaviour of the whole set: logo, poster and
        # brand_apply pass the demo lane; factsheet does not — its hexes sit
        # past both the 240-char intent and 180-char caption echoes and it
        # ships no brand kit, so no demo SVG ever carries them.
        verdicts = {}
        for path in list_fixtures(EVAL):
            fixture = load_fixture(path)
            with _DemoRuntime() as rt:
                report = rt.run(fixture)
            verdicts[fixture["id"]] = report["ok"]
            self.assertGreaterEqual(report["artifact_count"], 1, report)
        self.assertEqual(
            verdicts,
            {"logo": True, "poster": True, "brand_apply": True, "factsheet": False},
        )

    def test_brand_apply_mentions_ride_the_brief_not_the_kit(self):
        # Honesty pin: Archivo/Inter hit because the user brief becomes the
        # plan intent (request[:240]) and the artifact prompt — not because
        # fonts were applied. update_brand_kit drops the fonts key entirely.
        fixture = load_fixture(EVAL / "brief_brand_kit_apply.json")
        self.assertLess(fixture["request"].find("Inter") + len("Inter"), 240)
        with _DemoRuntime() as rt:
            project = rt.memory.create_project(fixture["title"], fixture["brand"])
            rt.memory.update_brand_kit(project["id"], fixture["brand"])
            stored = rt.memory.get_project(project["id"])["brand_kit"]
            self.assertNotIn("fonts", stored)
            thread = rt.memory.create_thread(project["id"], topic="probe")
            result = rt.conductor.run(
                project_id=project["id"],
                thread_id=thread["id"],
                prompt=fixture["request"],
                provider="demo",
                mode="fast",
            )
            blobs = [Path(a["path"]).read_bytes() for a in result["artifacts"]]
        message_only = {"message": result["message"], "plan": {}, "artifacts": [], "nodes": []}
        report = score_result(fixture, message_only, blobs)
        self.assertTrue(all(m["hit"] for m in report["must_mention"]), report)

    def test_poster_palette_hits_only_via_prompt_echo(self):
        # Honesty pin: the poster has no brand kit, so its hexes never become
        # fill/stop-color — they pass because the brief text (hexes included,
        # all inside the first 180 chars) is baked into the SVG caption.
        fixture = load_fixture(EVAL / "brief_poster.json")
        for hex_color in fixture["expected"]["palette"]:
            self.assertIn(hex_color, fixture["request"][:180])
        with _DemoRuntime() as rt:
            report = rt.run(fixture)
            svgs = rt.svg_texts()
        self.assertTrue(report["ok"], report)
        for svg in svgs:
            for hex_color in fixture["expected"]["palette"]:
                self.assertIn(hex_color, svg)
                self.assertNotIn(f'fill="{hex_color}"', svg)
                self.assertNotIn(f'stop-color="{hex_color}"', svg)

    def test_kit_palette_lands_as_fill_without_brief_echo(self):
        # A palette hex that never appears in the request text still hits —
        # the kit → demo_svg → fill path is real, not a brief echo.
        fixture = {
            "id": "kitproof",
            "title": "kit proof",
            "request": "Design a calm abstract studio mark.",
            "brand": {"name": "KitProof", "palette": ["#ABCDEF", "#123456"]},
            "expected": {"must_mention": [], "palette": ["#ABCDEF", "#123456"]},
        }
        with _DemoRuntime() as rt:
            report = rt.run(fixture)
            svgs = rt.svg_texts()
        self.assertTrue(report["ok"], report)
        self.assertTrue(any('fill="#ABCDEF"' in svg for svg in svgs))
        # And the same expectation without a kit fails: the gate is live.
        no_kit = {k: v for k, v in fixture.items() if k != "brand"}
        with _DemoRuntime() as rt:
            report = rt.run(no_kit)
        self.assertFalse(report["ok"], report)

    def test_mutated_must_mention_fails_through_a_real_run(self):
        fixture = load_fixture(EVAL / "brief_logo.json")
        mutated = json.loads(json.dumps(fixture))
        mutated["expected"]["must_mention"] = ["Zanzibar Chrome Whale"]
        with _DemoRuntime() as rt:
            report = rt.run(mutated)
        self.assertFalse(report["ok"], report)
        self.assertEqual([m["hit"] for m in report["must_mention"]], [False])


if __name__ == "__main__":
    unittest.main()
