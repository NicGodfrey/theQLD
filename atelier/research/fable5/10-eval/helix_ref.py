"""Reference implementation of the Conductor protocol + a demo Loom.

This module exists so `test_helix.py` is runnable *today*, before the real
`conductor.py` (Fable5#5) and loom (Fable5#7) land. It implements, offline and
stdlib-only, the contract published in `/tmp/atelier-fable/05-conductor/PROTOCOL.md`:

  * `parse_plan`       — validates a `conductor-plan/1` envelope (all rules in §2)
  * `parse_critique`   — validates a `conductor-critique/1` envelope (§3)
  * `order_steps`      — dependency (topological) ordering, cycles are errors
  * `route_plan`       — binds every step's craft to a lane (text / image)
  * `distill_brief`    — deterministic request → Brief distillation (§1 "brief")
  * `Conductor`        — brief → route → weave → (critique → mend) → pin (§1, §4)
  * `DemoPlannerSpoke`, `DemoMakerSpoke`, `DemoCriticSpoke` — deterministic
    scripted spokes: no API keys, no sockets, byte-reproducible output.

When the real conductor module appears, `test_helix.py` binds to it instead;
this file remains the executable specification the tests were written against.
"""

from __future__ import annotations

import hashlib
import json
import re
import os
import struct
import zlib
from dataclasses import dataclass, field

PLAN_PROTOCOL = "conductor-plan/1"
CRITIQUE_PROTOCOL = "conductor-critique/1"
MANIFEST_PROTOCOL = "conductor-manifest/1"

# Craft vocabulary -> kinds it may emit (PROTOCOL.md §2).
CRAFT_EMITS = {
    "compose-text": {"text", "json"},
    "analyze-visual": {"text", "json"},
    "render-image": {"image"},
    "refine-image": {"image"},
    "synthesize": {"text", "json"},
}

# Lanes and registry, mirroring 05-conductor/ROUTING.md: three lanes, each
# bound to one concrete spoke name. There is deliberately no video/audio/3d
# lane, so a plan can never route a launch brief there.
DEFAULT_REGISTRY = {
    "openai": "openai-text",
    "gemini": "gemini-omni",
    "image": "image-forge",
}
LANES = tuple(DEFAULT_REGISTRY)
LONG_SOURCE_CHARS = 8_000

_TOKEN = re.compile(r"\[\[([^\[\]]+)\]\]")
_HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")
_QUOTED = re.compile(r"'([^']{2,60})'")


class PlanParseError(ValueError):
    """A conductor-plan/1 envelope violated the protocol."""


class CritiqueParseError(ValueError):
    """A conductor-critique/1 envelope violated the protocol."""


class RoutingError(ValueError):
    """A step's craft could not be bound to any configured lane."""


# ---------------------------------------------------------------------------
# Envelope extraction and parsing
# ---------------------------------------------------------------------------

def _first_json_object(text: str) -> dict:
    """Extract the first balanced JSON object from prose/fenced model output."""
    if not isinstance(text, str):
        raise PlanParseError("envelope must be a string of JSON")
    start = text.find("{")
    if start == -1:
        raise PlanParseError("no JSON object found in output")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError as e:
                    raise PlanParseError(f"invalid JSON: {e}") from e
    raise PlanParseError("unterminated JSON object in output")


@dataclass
class Plan:
    reading: str
    assumptions: list
    steps: list
    handoff: list

    def to_dict(self) -> dict:
        return {
            "protocol": PLAN_PROTOCOL,
            "reading": self.reading,
            "assumptions": self.assumptions,
            "steps": self.steps,
            "handoff": self.handoff,
        }


def _fail(reason: str) -> None:
    raise PlanParseError(reason)


def parse_plan(text: str) -> Plan:
    """Validate a conductor-plan/1 envelope. Raises PlanParseError (PROTOCOL §2)."""
    data = _first_json_object(text) if isinstance(text, str) else text
    if not isinstance(data, dict):
        _fail("top level must be a JSON object")
    if data.get("protocol") != PLAN_PROTOCOL:
        _fail(f"protocol must be {PLAN_PROTOCOL!r}, got {data.get('protocol')!r}")
    reading = data.get("reading")
    if not isinstance(reading, str) or not reading.strip():
        _fail("'reading' must be a non-empty string")
    assumptions = data.get("assumptions", [])
    if not isinstance(assumptions, list) or any(not isinstance(a, str) for a in assumptions):
        _fail("'assumptions' must be an array of strings")
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        _fail("'steps' must be a non-empty array")

    ids: set = set()
    names: set = set()
    for i, step in enumerate(steps):
        where = f"steps[{i}]"
        if not isinstance(step, dict):
            _fail(f"{where} must be an object")
        sid = step.get("id")
        if not isinstance(sid, str) or not sid:
            _fail(f"{where}.id must be a non-empty string")
        if sid in ids:
            _fail(f"duplicate step id {sid!r}")
        ids.add(sid)
        if not isinstance(step.get("title"), str) or not step["title"].strip():
            _fail(f"{where}.title must be a non-empty string")
        craft = step.get("craft")
        if craft not in CRAFT_EMITS:
            _fail(f"{where}.craft must be one of {sorted(CRAFT_EMITS)}, got {craft!r}")
        if not isinstance(step.get("instruction"), str) or not step["instruction"].strip():
            _fail(f"{where}.instruction must be a non-empty string")
        emits = step.get("emits")
        if not isinstance(emits, dict):
            _fail(f"{where}.emits must be an object")
        kind = emits.get("kind")
        if kind not in ("text", "json", "image"):
            _fail(f"{where}.emits.kind must be text|json|image, got {kind!r}")
        if kind not in CRAFT_EMITS[craft]:
            _fail(f"{where}: craft {craft!r} cannot emit {kind!r}")
        name = emits.get("name")
        if not isinstance(name, str) or not name:
            _fail(f"{where}.emits.name must be a non-empty string")
        if name in names:
            _fail(f"duplicate artifact name {name!r}")
        names.add(name)
        acceptance = step.get("acceptance")
        if (
            not isinstance(acceptance, list)
            or not acceptance
            or any(not isinstance(a, str) or not a.strip() for a in acceptance)
        ):
            _fail(f"{where}.acceptance must be a non-empty array of criteria")
        needs = step.get("needs")
        if not isinstance(needs, list) or any(not isinstance(n, str) for n in needs):
            _fail(f"{where}.needs must be an array of step ids")

    # Second pass: needs targets, self-needs, token/need consistency.
    for i, step in enumerate(steps):
        where = f"steps[{i}]"
        sid = step["id"]
        for need in step["needs"]:
            if need == sid:
                _fail(f"{where}.needs must not reference the step itself")
            if need not in ids:
                _fail(f"{where}.needs references unknown step {need!r}")
        for token in _TOKEN.findall(step["instruction"]):
            if token not in step["needs"]:
                _fail(
                    f"{where}: token [[{token}]] used without a matching entry in needs"
                )

    order_steps(steps)  # raises on cycles

    handoff = data.get("handoff")
    if not isinstance(handoff, list) or not handoff:
        _fail("'handoff' must be a non-empty array")
    for h in handoff:
        if h not in names:
            _fail(f"handoff entry {h!r} does not match any step's emits.name")

    return Plan(reading=reading, assumptions=list(assumptions), steps=steps, handoff=list(handoff))


def order_steps(steps: list) -> list:
    """Kahn topological order of step ids, stable by plan order. Cycles raise."""
    ids = [s["id"] for s in steps]
    needs = {s["id"]: set(s.get("needs", [])) for s in steps}
    done: list = []
    ready = set()
    while len(done) < len(ids):
        progressed = False
        for sid in ids:
            if sid in ready:
                continue
            if needs[sid] <= ready:
                ready.add(sid)
                done.append(sid)
                progressed = True
        if not progressed:
            stuck = [s for s in ids if s not in ready]
            raise PlanParseError(f"steps form a cycle: {stuck}")
    return done


def parse_critique(text: str) -> dict:
    """Validate a conductor-critique/1 envelope (PROTOCOL §3)."""
    try:
        data = _first_json_object(text) if isinstance(text, str) else text
    except PlanParseError as e:
        raise CritiqueParseError(str(e)) from e
    if not isinstance(data, dict):
        raise CritiqueParseError("top level must be a JSON object")
    if data.get("protocol") != CRITIQUE_PROTOCOL:
        raise CritiqueParseError(f"protocol must be {CRITIQUE_PROTOCOL!r}")
    verdict = data.get("verdict")
    if verdict not in ("accept", "revise"):
        raise CritiqueParseError(f"verdict must be accept|revise, got {verdict!r}")
    notes = data.get("notes", [])
    if not isinstance(notes, list):
        raise CritiqueParseError("'notes' must be an array")
    for i, note in enumerate(notes):
        where = f"notes[{i}]"
        if not isinstance(note, dict):
            raise CritiqueParseError(f"{where} must be an object")
        if not isinstance(note.get("artifact"), str) or not note["artifact"]:
            raise CritiqueParseError(f"{where}.artifact must be a non-empty string")
        if note.get("severity") not in ("blocker", "advisory"):
            raise CritiqueParseError(f"{where}.severity must be blocker|advisory")
        if not isinstance(note.get("note"), str) or not note["note"].strip():
            raise CritiqueParseError(f"{where}.note must be a non-empty string")
        if not isinstance(note.get("fix_hint", ""), str):
            raise CritiqueParseError(f"{where}.fix_hint must be a string")
    if verdict == "revise" and not any(n.get("severity") == "blocker" for n in notes):
        raise CritiqueParseError("verdict 'revise' requires at least one blocker note")
    return {"verdict": verdict, "notes": notes}


def route_plan(plan, brief, registry: dict | None = None) -> dict:
    """Bind every step to a lane and spoke (ROUTING.md rules 1-5, in order).

    Returns {step_id: {step_id, lane, spoke, reason}}. Pure function of the
    plan, the brief, and the registry — same contract as the real conductor.
    """
    reg = dict(DEFAULT_REGISTRY)
    if registry:
        reg.update(registry)
    missing = [lane for lane in LANES if not reg.get(lane)]
    if missing:
        raise RoutingError(f"registry is missing lanes: {', '.join(missing)}")

    steps = plan.steps if isinstance(plan, Plan) else plan["steps"]
    emits = {s["id"]: s["emits"]["kind"] for s in steps}
    raw = brief.get("raw", "") if isinstance(brief, dict) else getattr(brief, "raw", "")
    long_source = len(raw) >= LONG_SOURCE_CHARS

    decisions = {}
    for step in steps:
        if step["craft"] in ("render-image", "refine-image"):
            lane, why = "image", "image synthesis runs on the image lane"
        elif step["craft"] == "analyze-visual":
            lane, why = "gemini", "reading visuals needs a multimodal reader"
        elif any(emits[n] == "image" for n in step["needs"]):
            lane, why = ("gemini",
                         "step consumes a rendered image, so it needs multimodal grounding")
        elif long_source:
            lane, why = "gemini", "brief source exceeds the long-context threshold"
        else:
            lane, why = "openai", "structured text drafting rides the default lane"
        decisions[step["id"]] = {
            "step_id": step["id"], "lane": lane, "spoke": reg[lane], "reason": why,
        }
    return decisions


# ---------------------------------------------------------------------------
# Brief distillation and scoring (deterministic, model-free)
# ---------------------------------------------------------------------------

_TONE_WORDS = (
    "minimal", "warm", "bold", "quiet", "accessible", "playful",
    "elegant", "unfussy", "geometric", "neon", "dark", "print-friendly",
)
_DELIVERABLE_WORDS = (
    "logo", "poster", "fact sheet", "fact-sheet", "template", "style note",
    "copy block", "change log", "preview", "wordmark", "mark",
)


def distill_brief(request: str, data: dict | None = None) -> dict:
    """Deterministic request -> Brief (goal, deliverables, constraints, tone)."""
    if not isinstance(request, str) or not request.strip():
        raise PlanParseError("request must be a non-empty string")
    text = request.strip()
    lower = text.lower()
    goal = re.split(r"(?<=[.!?])\s+", text)[0][:200]
    deliverables = [w for w in _DELIVERABLE_WORDS if w in lower]
    constraints = [f"Must use {h}." for h in dict.fromkeys(_HEX.findall(text))]
    for m in re.findall(r"\b(A[0-7])\b", text):
        constraints.append(f"Format {m}.")
    for f in re.findall(r"\b(Archivo|Inter)\b", text):
        constraints.append(f"Font {f}.")
    tone = [w for w in _TONE_WORDS if w in lower]
    return {
        "raw": text,
        "goal": goal,
        "deliverables": deliverables,
        "constraints": constraints,
        "tone": tone,
        "references": [data["source"]] if data and data.get("source") else [],
    }


def score_brief(brief: dict) -> dict:
    complexity = min(1.0, 0.15 * len(brief["deliverables"]) + 0.08 * len(brief["constraints"]))
    ambiguity = 0.0 if brief["constraints"] else 0.5
    flags = []
    if any(w in ("logo", "poster", "preview", "mark") for w in brief["deliverables"]) and any(
        w in ("style note", "copy block", "change log", "template", "fact sheet", "fact-sheet")
        for w in brief["deliverables"]
    ):
        flags.append("mixed-media")
    return {
        "complexity": round(complexity, 2),
        "ambiguity": ambiguity,
        "step_budget": 7,
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Spokes (PROTOCOL §5: every model call goes through the Spoke protocol)
# ---------------------------------------------------------------------------

@dataclass
class SpokeTask:
    kind: str                 # "plan" | "critique" | "text" | "json" | "image"
    instruction: str
    name: str = ""
    attachments: list = field(default_factory=list)


@dataclass
class SpokeResult:
    kind: str
    text: str = ""
    data: bytes = b""
    format: str = ""


def _digest(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _demo_png(seed: str, size: int = 8) -> bytes:
    """A tiny valid PNG whose pixels derive from the seed. Fully deterministic."""
    raw = hashlib.sha256(seed.encode("utf-8")).digest() * ((size * size * 3) // 32 + 2)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + tag
            + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        )

    rows = b""
    k = 0
    for _y in range(size):
        rows += b"\x00"
        for _x in range(size):
            rows += raw[k : k + 3]
            k += 3
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def _brand_name(request: str) -> str:
    m = _QUOTED.search(request)
    return m.group(1) if m else "the client"


def _canned_plan(request: str, data: dict | None) -> dict:
    """Deterministic planner: keyword-routed canned plans, constraints restated."""
    lower = request.lower()
    name = _brand_name(request)
    palette = list(dict.fromkeys(_HEX.findall(request)))
    p0 = palette[0] if palette else "#000000"
    p1 = palette[1] if len(palette) > 1 else p0
    pal = ", ".join(palette) if palette else "the stated palette"

    if "brand kit" in lower and any(w in lower for w in ("apply", "restyle", "recolour", "recolor")):
        fonts = re.findall(r"\b(Archivo|Inter)\b", request)
        font_note = (
            f"headings in {fonts[0]}, body copy in {fonts[1]}" if len(fonts) >= 2 else "the kit fonts"
        )
        return {
            "protocol": PLAN_PROTOCOL,
            "reading": f"{name} wants the existing launch poster restyled to the brand kit — palette {pal}, {font_note} — with the composition untouched, plus a change log.",
            "assumptions": ["The attached poster is the only asset in scope."],
            "steps": [
                {
                    "id": "s1",
                    "title": "Audit the poster against the kit",
                    "craft": "analyze-visual",
                    "instruction": f"Audit the attached launch poster against the {name} brand kit. List every element whose colour is outside the kit palette ({pal}) or whose type is not set with {font_note}. Report as JSON.",
                    "needs": [],
                    "emits": {"kind": "json", "name": "brand-audit"},
                    "acceptance": ["valid JSON", f"references the kit palette {pal}"],
                },
                {
                    "id": "s2",
                    "title": "Restyle the poster to the kit",
                    "craft": "refine-image",
                    "instruction": f"Restyle the attached launch poster per the audit [[s1]]. Recolour to the kit palette ({pal}), swap the placeholder mark for the {name} logo, set {font_note}. Keep the composition unchanged — restyle only.",
                    "needs": ["s1"],
                    "emits": {"kind": "image", "name": "restyled-poster"},
                    "acceptance": [f"uses only the kit palette ({pal})", "composition matches the original"],
                },
                {
                    "id": "s3",
                    "title": "Write the change log",
                    "craft": "synthesize",
                    "instruction": f"From the audit [[s1]] and the restyled poster (attached, from [[s2]]), write a change log for {name}: every element touched, its old and new treatment. Under 200 words.",
                    "needs": ["s1", "s2"],
                    "emits": {"kind": "text", "name": "change-log"},
                    "acceptance": ["lists every touched element", "under 200 words"],
                },
            ],
            "handoff": ["restyled-poster", "change-log"],
        }

    if "fact sheet" in lower or "fact-sheet" in lower:
        entries = (data or {}).get("entries", [])
        entry_lines = "; ".join(
            f"{e['name']} ({', '.join(e['categories'])}) phone {e['phone']}, {e['email']}, {e['website']} — {e['how_they_help']}"
            for e in entries
        )
        return {
            "protocol": PLAN_PROTOCOL,
            "reading": f"The client wants a one-page fact-sheet template for {name if name != 'the client' else 'The Queensland Legal Directory'} plus a rendered preview built from the supplied entries, accessible and print-friendly in {pal}.",
            "assumptions": ["A4 portrait is acceptable since no page size was stated."],
            "steps": [
                {
                    "id": "s1",
                    "title": "Normalise the directory entries",
                    "craft": "compose-text",
                    "instruction": f"Normalise these directory entries into one JSON object per organisation with fields name, categories, phone, email, website, how_they_help: {entry_lines}",
                    "needs": [],
                    "emits": {"kind": "json", "name": "content-model"},
                    "acceptance": ["valid JSON", "one object per organisation"],
                },
                {
                    "id": "s2",
                    "title": "Write the template spec",
                    "craft": "synthesize",
                    "instruction": f"From the content model [[s1]], write the one-page fact-sheet template spec for The Queensland Legal Directory: name, service categories, phone, email, website, 'how they help'. Restate constraints: palette {p0} on #FEFFFE with {p1 if len(palette) > 1 else p0} highlights, generous line spacing, no decorative imagery over text.",
                    "needs": ["s1"],
                    "emits": {"kind": "text", "name": "template-spec"},
                    "acceptance": [f"names the hex value {p0}", "covers all six fields"],
                },
                {
                    "id": "s3",
                    "title": "Render the preview page",
                    "craft": "render-image",
                    "instruction": f"Render one preview fact-sheet page following the template spec [[s2]]. Palette {pal}; generous line spacing; no decorative imagery over text.",
                    "needs": ["s2"],
                    "emits": {"kind": "image", "name": "factsheet-preview"},
                    "acceptance": ["follows the template spec", "text unobstructed"],
                },
            ],
            "handoff": ["content-model", "template-spec", "factsheet-preview"],
        }

    if "logo" in lower:
        return {
            "protocol": PLAN_PROTOCOL,
            "reading": f"{name} wants a geometric double-helix monogram logo: flat vector, one-colour mark in {p0} with {p1} reserved for the wordmark, plus a short style note.",
            "assumptions": ["White is an acceptable background since none was specified."],
            "steps": [
                {
                    "id": "s1",
                    "title": "Write the design direction",
                    "craft": "compose-text",
                    "instruction": f"Write a short design direction for the {name} logo. Restate constraints: geometric double-helix monogram, flat vector style, one-colour mark in {p0}, accent {p1} reserved for the wordmark, must read at small sizes. Three directions to compare.",
                    "needs": [],
                    "emits": {"kind": "text", "name": "direction"},
                    "acceptance": ["offers three directions", f"names the hex value {p0}"],
                },
                {
                    "id": "s2",
                    "title": "Render the logo mark",
                    "craft": "render-image",
                    "instruction": f"Render the {name} logo mark following the direction [[s1]]: geometric double-helix monogram, flat vector style, using only {p0} on white. Must be legible at 32 pixels.",
                    "needs": ["s1"],
                    "emits": {"kind": "image", "name": "logo-mark"},
                    "acceptance": [f"uses only {p0} on white", "legible at 32 pixels"],
                },
                {
                    "id": "s3",
                    "title": "Assemble the style note",
                    "craft": "synthesize",
                    "instruction": f"Combine the direction [[s1]] and the logo mark (attached, from [[s2]]) into a one-page style note for {name} covering usage, clear space, and the palette ({pal}).",
                    "needs": ["s1", "s2"],
                    "emits": {"kind": "text", "name": "style-note"},
                    "acceptance": [f"names the hex value {p0}", "under 200 words"],
                },
            ],
            "handoff": ["logo-mark", "style-note"],
        }

    if "poster" in lower:
        venue = "Brisbane Powerhouse" if "brisbane powerhouse" in lower else "the venue"
        return {
            "protocol": PLAN_PROTOCOL,
            "reading": f"{name} wants an A3 exhibition poster at {venue}: dark ground {p0} with neon accents, bold typographic hierarchy, legible from three metres, plus the final copy block.",
            "assumptions": ["Portrait A3 unless told otherwise."],
            "steps": [
                {
                    "id": "s1",
                    "title": "Write the copy block",
                    "craft": "compose-text",
                    "instruction": f"Write the poster copy block for {name} at {venue}: title, dates 12-14 September, venue line, one-line blurb. Tone: bold, dark, neon.",
                    "needs": [],
                    "emits": {"kind": "text", "name": "poster-copy"},
                    "acceptance": ["contains title, dates, venue, blurb", "blurb is one line"],
                },
                {
                    "id": "s2",
                    "title": "Render the poster",
                    "craft": "render-image",
                    "instruction": f"Render the A3 poster for {name} using the copy [[s1]]. Restate constraints: dark ground {p0}, neon accents {', '.join(palette[1:]) or p1}, bold typographic hierarchy, legible from three metres.",
                    "needs": ["s1"],
                    "emits": {"kind": "image", "name": "poster-hero"},
                    "acceptance": [f"dark ground is {p0}", "title legible from three metres"],
                },
                {
                    "id": "s3",
                    "title": "Legibility read",
                    "craft": "analyze-visual",
                    "instruction": "Review the rendered poster (attached, from [[s2]]) and report whether the title, dates and venue are legible from three metres.",
                    "needs": ["s2"],
                    "emits": {"kind": "text", "name": "legibility-report"},
                    "acceptance": ["states a legibility verdict for the title"],
                },
            ],
            "handoff": ["poster-hero", "poster-copy"],
        }

    # Generic fallback: one compose-text step.
    return {
        "protocol": PLAN_PROTOCOL,
        "reading": f"The client asked: {request[:160]}",
        "assumptions": [],
        "steps": [
            {
                "id": "s1",
                "title": "Draft the deliverable",
                "craft": "compose-text",
                "instruction": f"Draft the deliverable described by this request: {request}",
                "needs": [],
                "emits": {"kind": "text", "name": "draft"},
                "acceptance": ["addresses the request directly"],
            }
        ],
        "handoff": ["draft"],
    }


class DemoPlannerSpoke:
    """Planner spoke: emits a canned, protocol-valid plan for the request."""

    def perform(self, task: SpokeTask) -> SpokeResult:
        payload = json.loads(task.instruction) if task.kind == "plan" else {}
        plan = _canned_plan(payload.get("request", task.instruction), payload.get("data"))
        return SpokeResult(kind="text", text=json.dumps(plan, indent=2))


class DemoMakerSpoke:
    """Maker spoke for one lane. Deterministic; echoes its instruction so
    downstream content checks can prove data flowed through [[tokens]]."""

    def __init__(self, lane: str):
        self.lane = lane

    def perform(self, task: SpokeTask) -> SpokeResult:
        h = _digest(self.lane, task.name, task.instruction)
        if task.kind == "image":
            return SpokeResult(kind="image", data=_demo_png(h), format="png")
        if task.kind == "json":
            body = json.dumps(
                {"artifact": task.name, "demo": h[:12], "instruction": task.instruction},
                indent=2,
                sort_keys=True,
            )
            return SpokeResult(kind="json", text=body)
        return SpokeResult(
            kind="text",
            text=f"[demo:{self.lane}] {task.name} {h[:12]}\n\n{task.instruction}",
        )


class DemoCriticSpoke:
    """Critic spoke: accepts, with one advisory note on the first artifact."""

    def perform(self, task: SpokeTask) -> SpokeResult:
        names = re.findall(r"artifact '([^']+)'", task.instruction)
        note = (
            [
                {
                    "artifact": names[0],
                    "severity": "advisory",
                    "note": "Consider a tighter crop.",
                    "fix_hint": "",
                }
            ]
            if names
            else []
        )
        return SpokeResult(
            kind="text",
            text=json.dumps({"protocol": CRITIQUE_PROTOCOL, "verdict": "accept", "notes": note}),
        )


class ScriptedCriticSpoke:
    """Test helper: returns a fixed critique envelope (e.g. revise + blocker)."""

    def __init__(self, envelope: dict):
        self.envelope = envelope

    def perform(self, task: SpokeTask) -> SpokeResult:
        return SpokeResult(kind="text", text=json.dumps(self.envelope))


# ---------------------------------------------------------------------------
# Conductor: brief -> route -> weave -> (critique -> mend) -> pin
# ---------------------------------------------------------------------------

def _safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "artifact"


_EXT = {"text": "md", "json": "json"}


class Conductor:
    """Offline reference conductor. Opens no sockets; the clock is injectable
    and the run id can be supplied, so runs are byte-reproducible (PROTOCOL §5)."""

    def __init__(
        self,
        planner=None,
        makers: dict | None = None,
        critic=None,
        clock=None,
        usage_hook=None,
        registry: dict | None = None,
    ):
        self.planner = planner or DemoPlannerSpoke()
        self.makers = makers or {lane: DemoMakerSpoke(lane) for lane in LANES}
        self.critic = critic or DemoCriticSpoke()
        self.clock = clock or (lambda: 0.0)
        self.usage_hook = usage_hook
        self.registry = registry or dict(DEFAULT_REGISTRY)

    def _meter(self, model: str, step: str, run_id: str) -> None:
        if self.usage_hook:
            self.usage_hook(
                provider="demo",
                model=model,
                units={"requests": 1},
                meta={"step": step, "run_id": run_id},
            )

    def run(
        self,
        request: str,
        *,
        mode: str = "fast",
        out_dir: str,
        run_id: str | None = None,
        data: dict | None = None,
    ) -> dict:
        if mode not in ("fast", "thinking"):
            raise ValueError(f"mode must be fast|thinking, got {mode!r}")
        run_id = run_id or _digest(request, mode)[:12]
        brief = distill_brief(request, data)
        scorecard = score_brief(brief) if mode == "thinking" else None

        planner_task = SpokeTask(
            kind="plan",
            name="plan",
            instruction=json.dumps({"request": request, "data": data}),
        )
        plan = parse_plan(self.planner.perform(planner_task).text)
        self._meter("demo-planner", "route", run_id)
        decisions = route_plan(plan, brief, self.registry)
        order = order_steps(plan.steps)
        by_id = {s["id"]: s for s in plan.steps}

        # Weave: [[token]] substitution carries content between steps.
        results: dict = {}   # step id -> (name, kind, SpokeResult)
        revisions: dict = {}
        for sid in order:
            step = by_id[sid]
            results[sid] = (step["emits"]["name"], step["emits"]["kind"],
                            self._perform_step(step, decisions[sid], results, run_id))
            revisions[sid] = 0

        critique = None
        if mode == "thinking":
            artifact_list = ", ".join(
                f"artifact '{by_id[sid]['emits']['name']}'" for sid in order
            )
            critic_task = SpokeTask(
                kind="critique",
                name="critique",
                instruction=f"Judge these against the brief: {artifact_list}. Brief: {json.dumps(brief)}",
            )
            critique = parse_critique(self.critic.perform(critic_task).text)
            self._meter("demo-critic", "critique", run_id)
            # Mend: each blocker-flagged step re-runs once with the fix hint.
            blockers = {
                n["artifact"]: n for n in critique["notes"] if n["severity"] == "blocker"
            }
            if critique["verdict"] == "revise":
                for sid in order:
                    step = by_id[sid]
                    note = blockers.get(step["emits"]["name"])
                    if note is None:
                        continue
                    directive = f"\n\n## Revision directive\n{note.get('fix_hint') or note['note']}"
                    mended = dict(step)
                    mended["instruction"] = step["instruction"] + directive
                    results[sid] = (step["emits"]["name"], step["emits"]["kind"],
                                    self._perform_step(mended, decisions[sid], results, run_id))
                    revisions[sid] = 1

        return self._pin(
            out_dir, run_id, mode, brief, scorecard, plan, decisions, order,
            results, revisions, critique,
        )

    def _perform_step(self, step: dict, decision: dict, results: dict, run_id: str):
        instruction = step["instruction"]
        attachments = []
        for token in _TOKEN.findall(instruction):
            name, kind, res = results[token]
            if kind == "image":
                instruction = instruction.replace(
                    f"[[{token}]]", f"(see attached image '{name}')"
                )
                attachments.append(name)
            else:
                instruction = instruction.replace(f"[[{token}]]", res.text)
        task = SpokeTask(
            kind=step["emits"]["kind"],
            name=step["emits"]["name"],
            instruction=instruction,
            attachments=attachments,
        )
        out = self.makers[decision["lane"]].perform(task)
        self._meter(decision["spoke"], step["id"], run_id)
        return out

    def _pin(
        self, out_dir, run_id, mode, brief, scorecard, plan, decisions, order,
        results, revisions, critique,
    ) -> dict:
        art_dir = os.path.join(out_dir, "artifacts")
        os.makedirs(art_dir, exist_ok=True)
        artifacts = []
        for sid in order:
            name, kind, res = results[sid]
            ext = _EXT.get(kind, res.format or "png")
            rel = os.path.join("artifacts", f"{_safe_name(name)}.{ext}")
            payload = res.data if kind == "image" else res.text.encode("utf-8")
            with open(os.path.join(out_dir, rel), "wb") as f:
                f.write(payload)
            artifacts.append(
                {
                    "name": name,
                    "kind": kind,
                    "file": rel,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "bytes": len(payload),
                    "step": sid,
                    "spoke": decisions[sid]["spoke"],
                    "revision": revisions[sid],
                    "handoff": name in plan.handoff,
                }
            )
        manifest = {
            "manifest": MANIFEST_PROTOCOL,
            "run_id": run_id,
            "mode": mode,
            "created_at": float(self.clock()),
            "brief": brief,
            "scorecard": scorecard,
            "plan": {
                "reading": plan.reading,
                "assumptions": plan.assumptions,
                "handoff": plan.handoff,
                "steps": [
                    {
                        "id": s["id"],
                        "title": s["title"],
                        "craft": s["craft"],
                        "lane": decisions[s["id"]]["lane"],
                        "spoke": decisions[s["id"]]["spoke"],
                        "reason": decisions[s["id"]]["reason"],
                    }
                    for s in plan.steps
                ],
            },
            "critique": critique,
            "artifacts": artifacts,
        }
        path = os.path.join(out_dir, "manifest.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        return {"run_id": run_id, "mode": mode, "out_dir": out_dir,
                "manifest_path": path, "manifest": manifest}


def demo_run(
    request: str,
    *,
    out_dir: str,
    mode: str = "fast",
    data: dict | None = None,
    run_id: str | None = None,
    usage_hook=None,
    critic=None,
    clock=None,
) -> dict:
    """Convenience wrapper: a fully wired demo loom run. No keys, no network."""
    conductor = Conductor(critic=critic, clock=clock, usage_hook=usage_hook)
    return conductor.run(request, mode=mode, out_dir=out_dir, run_id=run_id, data=data)
