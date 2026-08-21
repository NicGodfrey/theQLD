"""Offline tests for Conductor. No network, no real models — scripted spokes only.

Run:  python3 -m unittest discover -s tests -v   (from 05-conductor/)
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import conductor as c


# ---------------------------------------------------------------------------
# Scripted test doubles
# ---------------------------------------------------------------------------

class ScriptedSpoke:
    """A Spoke that replays canned results and records every task it saw."""

    def __init__(self, name, results):
        self.name = name
        self._results = list(results)
        self.calls = []

    def perform(self, task):
        self.calls.append(task)
        if not self._results:
            raise AssertionError(f"spoke '{self.name}' ran out of scripted results")
        return self._results.pop(0)


def text_result(text):
    return c.SpokeResult(kind="text", text=text)


def json_result(obj):
    return c.SpokeResult(kind="json", text=json.dumps(obj))


def image_result(data=b"\x89PNG-fake-bytes", fmt="png"):
    return c.SpokeResult(kind="image", data=data, meta={"format": fmt})


def make_clock(step=0.001):
    state = {"t": 1000.0}

    def clock():
        state["t"] += step
        return state["t"]

    return clock


BRIEF_TEXT = (
    "Design a logo and a tagline for Solstice Tea. "
    "Must use #2F5D50. Keep it minimal."
)


def plan_dict():
    return {
        "protocol": "conductor-plan/1",
        "reading": "Solstice Tea wants a compact identity: a minimal deep-green logo mark plus a short tagline.",
        "assumptions": ["A symbol-only mark satisfies 'logo'."],
        "steps": [
            {
                "id": "s1", "title": "Write the tagline", "craft": "compose-text",
                "instruction": "Write one tagline under six words for Solstice Tea. Tone: minimal, warm.",
                "needs": [], "emits": {"kind": "text", "name": "tagline"},
                "acceptance": ["six words or fewer", "no pun on 'tea time'"],
            },
            {
                "id": "s2", "title": "Render the logo mark", "craft": "render-image",
                "instruction": "Render a minimal logo mark for Solstice Tea using only #2F5D50 on white.",
                "needs": [], "emits": {"kind": "image", "name": "logo-mark"},
                "acceptance": ["uses only #2F5D50 on white", "legible at 32px"],
            },
            {
                "id": "s3", "title": "Assemble the style note", "craft": "synthesize",
                "instruction": "Combine the tagline [[s1]] and the logo [[s2]] into a one-page style note naming #2F5D50.",
                "needs": ["s1", "s2"], "emits": {"kind": "text", "name": "style-note"},
                "acceptance": ["names the hex value #2F5D50", "under 200 words"],
            },
        ],
        "handoff": ["tagline", "logo-mark", "style-note"],
    }


def critique_dict(verdict="revise"):
    return {
        "protocol": "conductor-critique/1",
        "verdict": verdict,
        "notes": [
            {
                "artifact": "tagline", "severity": "blocker",
                "note": "Seven words; acceptance requires six or fewer.",
                "fix_hint": "Cut to at most six words.",
            },
            {
                "artifact": "style-note", "severity": "advisory",
                "note": "Clear-space rule is vague.", "fix_hint": "",
            },
        ] if verdict == "revise" else [],
    }


def build_spokes(openai_results, gemini_results, image_results):
    return {
        "openai-text": ScriptedSpoke("openai-text", openai_results),
        "gemini-omni": ScriptedSpoke("gemini-omni", gemini_results),
        "image-forge": ScriptedSpoke("image-forge", image_results),
    }


# ---------------------------------------------------------------------------
# brief
# ---------------------------------------------------------------------------

class BriefTests(unittest.TestCase):
    def test_extracts_goal_deliverables_constraints_tone(self):
        brief = c.distill_brief(BRIEF_TEXT)
        self.assertEqual(brief.goal, "Design a logo and a tagline for Solstice Tea.")
        self.assertEqual(brief.deliverables, ("logo", "tagline"))
        self.assertEqual(brief.constraints, ("Must use #2F5D50.",))
        self.assertIn("minimal", brief.tone)

    def test_detects_dimensions_and_formats_as_constraints(self):
        brief = c.distill_brief("Make a banner. Export 1200x628 as png.")
        self.assertEqual(len(brief.constraints), 1)
        self.assertIn("1200x628", brief.constraints[0])

    def test_empty_request_raises(self):
        with self.assertRaises(c.ConductorError):
            c.distill_brief("   ")

    def test_references_are_carried(self):
        brief = c.distill_brief("Make a poster.", references=("shoot/a.jpg",))
        self.assertEqual(brief.references, ("shoot/a.jpg",))


# ---------------------------------------------------------------------------
# score
# ---------------------------------------------------------------------------

class ScoreTests(unittest.TestCase):
    def test_vague_brief_is_flagged(self):
        card = c.score_brief(c.distill_brief("Make something cool for our brand, whatever works."))
        self.assertIn("no-deliverables-named", card.flags)
        self.assertIn("vague-language", card.flags)
        self.assertGreater(card.ambiguity, 0.5)

    def test_mixed_media_raises_budget(self):
        card = c.score_brief(c.distill_brief(BRIEF_TEXT))
        self.assertIn("mixed-media", card.flags)
        self.assertEqual(card.step_budget, 7)  # 2 + 2*2 deliverables + 1 mixed-media

    def test_budget_is_clamped(self):
        many = "logo poster banner icon illustration moodboard cover tagline copy palette"
        card = c.score_brief(c.distill_brief(many))
        self.assertLessEqual(card.step_budget, 9)
        self.assertGreaterEqual(card.step_budget, 3)

    def test_scores_stay_in_unit_range(self):
        card = c.score_brief(c.distill_brief("x" * 10000 + " something cool nice vibe maybe"))
        self.assertLessEqual(card.complexity, 1.0)
        self.assertLessEqual(card.ambiguity, 1.0)
        self.assertIn("long-source", card.flags)


# ---------------------------------------------------------------------------
# plan parsing
# ---------------------------------------------------------------------------

class PlanParseTests(unittest.TestCase):
    def test_happy_path(self):
        plan = c.parse_plan(json.dumps(plan_dict()))
        self.assertEqual(len(plan.steps), 3)
        self.assertEqual(plan.handoff, ("tagline", "logo-mark", "style-note"))

    def test_tolerates_markdown_fence_and_prose(self):
        wrapped = "Here you go:\n```json\n" + json.dumps(plan_dict()) + "\n```\nDone."
        self.assertEqual(len(c.parse_plan(wrapped).steps), 3)

    def _expect_error(self, mutate, fragment):
        d = copy.deepcopy(plan_dict())
        mutate(d)
        with self.assertRaises(c.PlanParseError) as ctx:
            c.parse_plan(json.dumps(d))
        self.assertIn(fragment, str(ctx.exception))

    def test_rejects_wrong_protocol(self):
        self._expect_error(lambda d: d.update(protocol="nope/9"), "protocol")

    def test_rejects_duplicate_step_id(self):
        self._expect_error(lambda d: d["steps"][1].update(id="s1"), "duplicate")

    def test_rejects_unknown_craft(self):
        self._expect_error(lambda d: d["steps"][0].update(craft="daydream"), "unknown craft")

    def test_rejects_craft_kind_mismatch(self):
        self._expect_error(
            lambda d: d["steps"][1]["emits"].update(kind="text"), "emits")

    def test_rejects_dangling_needs(self):
        self._expect_error(lambda d: d["steps"][2].update(needs=["s1", "ghost"]), "unknown step")

    def test_rejects_token_without_dependency(self):
        self._expect_error(lambda d: d["steps"][2].update(needs=["s1"]), "[[s2]]")

    def test_rejects_empty_acceptance(self):
        self._expect_error(lambda d: d["steps"][0].update(acceptance=[]), "acceptance")

    def test_rejects_handoff_of_unknown_artifact(self):
        self._expect_error(lambda d: d.update(handoff=["mystery"]), "unknown artifact")

    def test_rejects_cycle(self):
        def mutate(d):
            d["steps"][0]["needs"] = ["s3"]
            d["steps"][0]["instruction"] = "Use [[s3]] to write the tagline."
        self._expect_error(mutate, "cycle")

    def test_rejects_non_json(self):
        with self.assertRaises(c.PlanParseError):
            c.parse_plan("I would love to help! First we should...")


# ---------------------------------------------------------------------------
# routing
# ---------------------------------------------------------------------------

class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.brief = c.distill_brief(BRIEF_TEXT)
        self.plan = c.parse_plan(json.dumps(plan_dict()))

    def test_lane_rules(self):
        routes = c.route_plan(self.plan, self.brief)
        self.assertEqual(routes["s1"].lane, "openai")     # plain drafting
        self.assertEqual(routes["s2"].lane, "image")      # render-image
        self.assertEqual(routes["s3"].lane, "gemini")     # consumes an image
        self.assertEqual(routes["s3"].spoke, "gemini-omni")
        self.assertIn("multimodal", routes["s3"].reason)

    def test_long_source_pulls_text_to_gemini(self):
        long_brief = c.distill_brief("Write a tagline. " + "x" * 9000)
        d = copy.deepcopy(plan_dict())
        d["steps"] = [d["steps"][0]]
        d["handoff"] = ["tagline"]
        plan = c.parse_plan(json.dumps(d))
        routes = c.route_plan(plan, long_brief)
        self.assertEqual(routes["s1"].lane, "gemini")

    def test_registry_override(self):
        routes = c.route_plan(self.plan, self.brief, {"image": "glyph-forge"})
        self.assertEqual(routes["s2"].spoke, "glyph-forge")
        self.assertEqual(routes["s1"].spoke, "openai-text")

    def test_missing_lane_raises(self):
        with self.assertRaises(c.RoutingError):
            c.route_plan(self.plan, self.brief, {"image": ""})


# ---------------------------------------------------------------------------
# weave
# ---------------------------------------------------------------------------

class WeaveTests(unittest.TestCase):
    def setUp(self):
        self.brief = c.distill_brief(BRIEF_TEXT)
        self.plan = c.parse_plan(json.dumps(plan_dict()))
        self.routes = c.route_plan(self.plan, self.brief)

    def test_tokens_thread_content_and_attach_images(self):
        spokes = build_spokes(
            openai_results=[text_result("Steeped in quiet.")],
            gemini_results=[text_result("Style note: #2F5D50 everywhere.")],
            image_results=[image_result()],
        )
        produced = c.weave(self.plan, self.routes, spokes)
        s3_task = spokes["gemini-omni"].calls[0]
        self.assertIn("Steeped in quiet.", s3_task.prompt)          # [[s1]] inlined
        self.assertIn("see attached image 'logo-mark'", s3_task.prompt)
        self.assertEqual(len(s3_task.attachments), 1)
        self.assertEqual(s3_task.attachments[0].name, "logo-mark")
        self.assertEqual(produced["s3"].kind, "text")

    def test_step_prompt_carries_acceptance(self):
        spokes = build_spokes([text_result("t")], [text_result("s")], [image_result()])
        c.weave(self.plan, self.routes, spokes)
        self.assertIn("six words or fewer", spokes["openai-text"].calls[0].prompt)

    def test_missing_spoke_raises_routing_error(self):
        spokes = build_spokes([text_result("t")], [text_result("s")], [image_result()])
        del spokes["image-forge"]
        with self.assertRaises(c.RoutingError) as ctx:
            c.weave(self.plan, self.routes, spokes)
        self.assertIn("image-forge", str(ctx.exception))

    def test_kind_mismatch_raises_weave_error(self):
        spokes = build_spokes(
            [text_result("t")], [text_result("s")],
            [text_result("i am not an image")],
        )
        with self.assertRaises(c.WeaveError):
            c.weave(self.plan, self.routes, spokes)


# ---------------------------------------------------------------------------
# critique parsing
# ---------------------------------------------------------------------------

class CritiqueParseTests(unittest.TestCase):
    def test_happy_path(self):
        crit = c.parse_critique(json.dumps(critique_dict()))
        self.assertEqual(crit.verdict, "revise")
        self.assertEqual(crit.notes[0].severity, "blocker")

    def test_revise_without_blocker_rejected(self):
        d = critique_dict()
        d["notes"] = [n for n in d["notes"] if n["severity"] != "blocker"]
        with self.assertRaises(c.CritiqueParseError):
            c.parse_critique(json.dumps(d))

    def test_bad_severity_rejected(self):
        d = critique_dict()
        d["notes"][0]["severity"] = "catastrophic"
        with self.assertRaises(c.CritiqueParseError):
            c.parse_critique(json.dumps(d))


# ---------------------------------------------------------------------------
# end-to-end: fast mode
# ---------------------------------------------------------------------------

class FastRunTests(unittest.TestCase):
    def test_fast_run_pins_manifest_without_critique(self):
        spokes = build_spokes(
            openai_results=[json_result(plan_dict()), text_result("Steeped in quiet.")],
            gemini_results=[text_result("Style note naming #2F5D50.")],
            image_results=[image_result()],
        )
        conductor = c.Conductor(spokes, clock=make_clock())
        with tempfile.TemporaryDirectory() as tmp:
            result = conductor.run(BRIEF_TEXT, "fast", out_dir=tmp, run_id="fastrun00001")

            self.assertIsNone(result.scorecard)
            self.assertIsNone(result.critique)
            stages = [t["stage"] for t in result.trace]
            self.assertEqual(stages, ["brief", "route:plan", "route:bind", "weave", "pin"])

            manifest = json.loads(Path(result.manifest_path).read_text())
            self.assertEqual(manifest["manifest"], "conductor-manifest/1")
            self.assertEqual(manifest["mode"], "fast")
            self.assertIsNone(manifest["critique"])
            self.assertEqual(len(manifest["artifacts"]), 3)
            by_name = {a["name"]: a for a in manifest["artifacts"]}
            self.assertEqual(by_name["logo-mark"]["kind"], "image")
            self.assertTrue(by_name["logo-mark"]["file"].endswith(".png"))
            self.assertEqual(len(by_name["tagline"]["sha256"]), 64)
            self.assertTrue(all(a["handoff"] for a in manifest["artifacts"]))
            for entry in manifest["artifacts"]:
                self.assertTrue((Path(tmp) / entry["file"]).is_file())


# ---------------------------------------------------------------------------
# end-to-end: thinking mode
# ---------------------------------------------------------------------------

class ThinkingRunTests(unittest.TestCase):
    def test_thinking_run_mends_blocker_and_records_lineage(self):
        spokes = build_spokes(
            openai_results=[
                json_result(plan_dict()),                # route: plan
                text_result("A seven word tagline that runs long."),  # weave s1
                json_result(critique_dict("revise")),    # critique
                text_result("Steeped in quiet."),        # mend s1
            ],
            gemini_results=[text_result("Style note naming #2F5D50.")],  # weave s3
            image_results=[image_result()],                              # weave s2
        )
        conductor = c.Conductor(spokes, clock=make_clock())
        with tempfile.TemporaryDirectory() as tmp:
            result = conductor.run(BRIEF_TEXT, "thinking", out_dir=tmp, run_id="think0000001")

            stages = [t["stage"] for t in result.trace]
            self.assertEqual(stages, [
                "brief", "score", "route:plan", "route:bind",
                "weave", "critique", "critique:mend", "pin",
            ])
            self.assertEqual(result.critique.verdict, "revise")

            arts = {a.name: a for a in result.artifacts}
            self.assertEqual(arts["tagline"].revision, 1)
            self.assertEqual(arts["tagline"].text, "Steeped in quiet.")
            self.assertEqual(arts["style-note"].revision, 0)  # downstream not re-run

            # The mend call carried the critic's directive.
            mend_task = spokes["openai-text"].calls[-1]
            self.assertIn("Revision directive", mend_task.prompt)
            self.assertIn("Cut to at most six words.", mend_task.prompt)

            # The critic saw the image artifact as an attachment.
            critic_task = spokes["openai-text"].calls[2]
            self.assertEqual([a.name for a in critic_task.attachments], ["logo-mark"])
            self.assertIn("Acceptance criteria:", critic_task.prompt)

            manifest = json.loads(Path(result.manifest_path).read_text())
            self.assertEqual(manifest["critique"]["verdict"], "revise")
            self.assertEqual(manifest["scorecard"]["step_budget"], 7)
            by_name = {a["name"]: a for a in manifest["artifacts"]}
            self.assertEqual(by_name["tagline"]["revision"], 1)

    def test_accept_verdict_skips_mend(self):
        spokes = build_spokes(
            openai_results=[
                json_result(plan_dict()),
                text_result("Steeped in quiet."),
                json_result(critique_dict("accept")),
            ],
            gemini_results=[text_result("Style note naming #2F5D50.")],
            image_results=[image_result()],
        )
        conductor = c.Conductor(spokes, clock=make_clock())
        with tempfile.TemporaryDirectory() as tmp:
            result = conductor.run(BRIEF_TEXT, "thinking", out_dir=tmp)
            self.assertEqual(result.critique.verdict, "accept")
            self.assertNotIn("critique:mend", [t["stage"] for t in result.trace])
            self.assertTrue(all(a.revision == 0 for a in result.artifacts))

    def test_planner_retry_on_malformed_json(self):
        spokes = build_spokes(
            openai_results=[
                text_result("Sure! Here is my thinking about the plan..."),  # invalid
                json_result(plan_dict()),                                    # retry OK
                text_result("Steeped in quiet."),
            ],
            gemini_results=[text_result("Style note naming #2F5D50.")],
            image_results=[image_result()],
        )
        conductor = c.Conductor(spokes, clock=make_clock())
        with tempfile.TemporaryDirectory() as tmp:
            result = conductor.run(BRIEF_TEXT, "fast", out_dir=tmp)
            self.assertEqual(len(result.plan.steps), 3)
            retry_task = spokes["openai-text"].calls[1]
            self.assertIn("Correction required", retry_task.prompt)

    def test_second_parse_failure_aborts(self):
        spokes = build_spokes(
            openai_results=[text_result("nope"), text_result("still nope")],
            gemini_results=[], image_results=[],
        )
        conductor = c.Conductor(spokes, clock=make_clock())
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(c.PlanParseError):
                conductor.run(BRIEF_TEXT, "fast", out_dir=tmp)


if __name__ == "__main__":
    unittest.main()
