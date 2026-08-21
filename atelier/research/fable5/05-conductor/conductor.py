"""Conductor — Atelier's design-run orchestrator.

Conductor turns a raw creative request into pinned artifacts by walking a
fixed pipeline of named stages:

    fast      brief -> route -> weave
    thinking  brief -> score -> route -> weave -> critique -> pin

(`pin` — writing the artifact manifest — always happens; in fast mode it is
weave's silent epilogue rather than a named stage.)

Every model call goes through an injected ``Spoke``. Nothing in this module
opens a socket: the planner and the critic are ordinary spokes looked up by
name, so all parsing, scoring, routing, ordering, and prompt-building logic
is unit-testable offline. See PROTOCOL.md for the wire envelopes and
ROUTING.md for the lane rules mirrored in :func:`route_plan`.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

__all__ = [
    "Mode", "Brief", "Scorecard", "Step", "Plan", "RouteDecision",
    "Spoke", "SpokeTask", "SpokeResult", "Artifact",
    "CritiqueNote", "Critique", "RunResult", "Conductor",
    "ConductorError", "PlanParseError", "CritiqueParseError",
    "RoutingError", "WeaveError",
    "distill_brief", "score_brief", "parse_plan", "parse_critique",
    "order_steps", "route_plan", "build_planner_prompt",
    "build_critic_prompt", "build_step_prompt", "weave", "run_step",
    "pin", "load_prompt",
    "PLAN_PROTOCOL", "CRITIQUE_PROTOCOL", "CRAFTS", "DEFAULT_REGISTRY",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLAN_PROTOCOL = "conductor-plan/1"
CRITIQUE_PROTOCOL = "conductor-critique/1"
MANIFEST_PROTOCOL = "conductor-manifest/1"

CRAFTS = ("compose-text", "analyze-visual", "render-image", "refine-image", "synthesize")
ARTIFACT_KINDS = ("text", "json", "image")

# Which artifact kinds each craft may emit.
CRAFT_OUTPUT: Mapping[str, tuple[str, ...]] = {
    "compose-text": ("text", "json"),
    "analyze-visual": ("text", "json"),
    "render-image": ("image",),
    "refine-image": ("image",),
    "synthesize": ("text", "json"),
}

# Lane keys -> default spoke names. Callers override via the registry.
DEFAULT_REGISTRY: Mapping[str, str] = {
    "openai": "openai-text",
    "gemini": "gemini-omni",
    "image": "image-forge",
}
LANES = tuple(DEFAULT_REGISTRY)

LONG_SOURCE_CHARS = 8_000     # raw briefs at/above this ride the long-context lane
TEXT_DIGEST_CHARS = 2_000     # how much of a text artifact the critic sees
FAST_STEP_BUDGET = 5          # step budget when no scorecard is computed

TOKEN_RE = re.compile(r"\[\[([A-Za-z0-9_-]+)\]\]")

WEAVER_SYSTEM = (
    "You are a working spoke of Atelier's Conductor. You receive exactly one "
    "step of a larger weave. Execute that step and nothing else: no "
    "commentary, no questions, no preamble — only the artifact itself."
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ConductorError(Exception):
    """Base class for every failure Conductor raises on purpose."""


class PlanParseError(ConductorError):
    """The planner's reply violated the conductor-plan/1 contract."""


class CritiqueParseError(ConductorError):
    """The critic's reply violated the conductor-critique/1 contract."""


class RoutingError(ConductorError):
    """A step could not be bound to an injected spoke."""


class WeaveError(ConductorError):
    """A step failed at execution time."""


# ---------------------------------------------------------------------------
# Core data types
# ---------------------------------------------------------------------------

class Mode(str, Enum):
    FAST = "fast"
    THINKING = "thinking"


@dataclass(frozen=True)
class Brief:
    raw: str
    goal: str
    deliverables: tuple[str, ...]
    constraints: tuple[str, ...]
    tone: tuple[str, ...]
    references: tuple[str, ...] = ()


@dataclass(frozen=True)
class Scorecard:
    complexity: float          # 0.0 .. 1.0
    ambiguity: float           # 0.0 .. 1.0
    step_budget: int
    flags: tuple[str, ...]


@dataclass(frozen=True)
class Step:
    id: str
    title: str
    craft: str
    instruction: str
    needs: tuple[str, ...]
    emits_kind: str
    emits_name: str
    acceptance: tuple[str, ...]


@dataclass(frozen=True)
class Plan:
    protocol: str
    reading: str
    assumptions: tuple[str, ...]
    steps: tuple[Step, ...]
    handoff: tuple[str, ...]


@dataclass(frozen=True)
class RouteDecision:
    step_id: str
    lane: str       # "openai" | "gemini" | "image"
    spoke: str      # concrete spoke name from the registry
    reason: str


@dataclass(frozen=True)
class SpokeTask:
    system: str
    prompt: str
    expect: str                              # "text" | "json" | "image"
    attachments: tuple["Artifact", ...] = ()


@dataclass(frozen=True)
class SpokeResult:
    kind: str                                # "text" | "json" | "image"
    text: str = ""
    data: bytes = b""
    meta: Mapping[str, Any] = field(default_factory=dict)


class Spoke(Protocol):
    """Anything that can perform one task. Injected; never constructed here."""

    name: str

    def perform(self, task: SpokeTask) -> SpokeResult: ...


@dataclass(frozen=True)
class Artifact:
    name: str
    kind: str
    step_id: str
    spoke: str
    text: str = ""
    data: bytes = b""
    revision: int = 0
    meta: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CritiqueNote:
    artifact: str
    severity: str    # "blocker" | "advisory"
    note: str
    fix_hint: str = ""


@dataclass(frozen=True)
class Critique:
    verdict: str     # "accept" | "revise"
    notes: tuple[CritiqueNote, ...]


@dataclass(frozen=True)
class RunResult:
    run_id: str
    mode: Mode
    brief: Brief
    scorecard: Scorecard | None
    plan: Plan
    routes: Mapping[str, RouteDecision]
    artifacts: tuple[Artifact, ...]
    critique: Critique | None
    manifest_path: Path
    trace: tuple[Mapping[str, Any], ...]


# ---------------------------------------------------------------------------
# Stage: brief (deterministic)
# ---------------------------------------------------------------------------

DELIVERABLE_WORDS = (
    "logo", "wordmark", "poster", "banner", "icon", "illustration",
    "moodboard", "storyboard", "thumbnail", "cover", "social post",
    "landing page", "style guide", "palette", "tagline", "slogan", "copy",
)
IMAGE_DELIVERABLES = frozenset({
    "logo", "wordmark", "poster", "banner", "icon", "illustration",
    "moodboard", "storyboard", "thumbnail", "cover", "social post",
})
TEXT_DELIVERABLES = frozenset({
    "landing page", "style guide", "palette", "tagline", "slogan", "copy",
})
TONE_WORDS = (
    "playful", "minimal", "bold", "elegant", "retro", "futuristic", "warm",
    "luxurious", "friendly", "serious", "hand-drawn", "corporate",
    "brutalist", "pastel", "vibrant", "muted", "quiet", "loud",
)
VAGUE_WORDS = (
    "something", "cool", "nice", "vibe", "vibes", "whatever", "maybe",
    "some kind", "etc", "pop",
)
CONSTRAINT_RE = re.compile(
    r"#[0-9a-fA-F]{6}\b"                                # hex color
    r"|\b\d+\s*[x×]\s*\d+\b"                            # dimensions
    r"|\b\d+\s*px\b"                                    # pixel sizes
    r"|\b\d+:\d+\b"                                     # aspect ratios
    r"|\b(must|only|avoid|never|exactly|no more than|at least|at most)\b"
    r"|\b(svg|png|webp|pdf|jpe?g|gif|mp4)\b",
    re.IGNORECASE,
)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def distill_brief(raw: str, references: Sequence[str] = ()) -> Brief:
    """Deterministically distill a raw request into a structured Brief.

    Pure text heuristics — no model call — so the planner always receives the
    same skeleton for the same request.
    """
    if not isinstance(raw, str) or not raw.strip():
        raise ConductorError("cannot distill an empty request")
    text = raw.strip()
    lower = text.lower()

    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    goal = sentences[0] if sentences else text

    hits = [(lower.find(w), w) for w in DELIVERABLE_WORDS if w in lower]
    deliverables = tuple(w for _, w in sorted(hits))

    constraints = tuple(dict.fromkeys(
        s for s in sentences if CONSTRAINT_RE.search(s)
    ))

    tone = tuple(w for w in TONE_WORDS if re.search(rf"\b{re.escape(w)}\b", lower))

    return Brief(
        raw=text,
        goal=goal,
        deliverables=deliverables,
        constraints=constraints,
        tone=tone,
        references=tuple(references),
    )


# ---------------------------------------------------------------------------
# Stage: score (deterministic, thinking mode only)
# ---------------------------------------------------------------------------

def score_brief(brief: Brief) -> Scorecard:
    """Deterministic pre-read of the brief. Never a model call."""
    lower = brief.raw.lower()
    vague_hits = [w for w in VAGUE_WORDS if re.search(rf"\b{re.escape(w)}\b", lower)]

    wants_image = any(d in IMAGE_DELIVERABLES for d in brief.deliverables)
    wants_text = any(d in TEXT_DELIVERABLES for d in brief.deliverables)

    flags: list[str] = []
    if not brief.deliverables:
        flags.append("no-deliverables-named")
    if vague_hits:
        flags.append("vague-language")
    if wants_image and wants_text:
        flags.append("mixed-media")
    if wants_image and not brief.constraints:
        flags.append("unconstrained-visuals")
    if len(brief.raw) >= LONG_SOURCE_CHARS:
        flags.append("long-source")
    if brief.references:
        flags.append("has-references")

    complexity = min(1.0, (
        0.15 * len(brief.deliverables)
        + 0.04 * len(brief.constraints)
        + (0.2 if "mixed-media" in flags else 0.0)
        + (0.1 if brief.references else 0.0)
        + (0.1 if "long-source" in flags else 0.0)
    ))
    ambiguity = min(1.0, (
        (0.3 if not brief.deliverables else 0.0)
        + 0.15 * len(vague_hits)
        + (0.2 if "unconstrained-visuals" in flags else 0.0)
    ))
    budget = 2 + 2 * max(1, len(brief.deliverables))
    if "mixed-media" in flags:
        budget += 1
    budget = max(3, min(9, budget))

    return Scorecard(
        complexity=round(complexity, 2),
        ambiguity=round(ambiguity, 2),
        step_budget=budget,
        flags=tuple(flags),
    )


# ---------------------------------------------------------------------------
# Envelope parsing
# ---------------------------------------------------------------------------

def _decode_json_payload(text: str, err_cls: type[ConductorError]) -> dict:
    """Pull the first JSON object out of a model reply.

    Tolerates a markdown fence and surrounding prose; rejects everything
    else with a reason precise enough to drive the single bounded retry.
    """
    if not isinstance(text, str) or not text.strip():
        raise err_cls("reply was empty; expected a JSON object")
    body = text
    fence = re.search(r"```(?:json)?\s*(.*?)```", body, re.DOTALL)
    if fence:
        body = fence.group(1)
    start = body.find("{")
    if start == -1:
        raise err_cls("no JSON object found in reply")
    try:
        obj, _ = json.JSONDecoder().raw_decode(body[start:])
    except json.JSONDecodeError as exc:
        raise err_cls(f"reply is not valid JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise err_cls("top-level JSON value must be an object")
    return obj


def parse_plan(text: str) -> Plan:
    """Parse and validate a conductor-plan/1 reply. Raises PlanParseError."""
    obj = _decode_json_payload(text, PlanParseError)
    if obj.get("protocol") != PLAN_PROTOCOL:
        raise PlanParseError(
            f"protocol must be '{PLAN_PROTOCOL}', got {obj.get('protocol')!r}")

    reading = obj.get("reading")
    if not isinstance(reading, str) or not reading.strip():
        raise PlanParseError("'reading' must be a non-empty string")

    assumptions = obj.get("assumptions", [])
    if not isinstance(assumptions, list) or not all(isinstance(a, str) for a in assumptions):
        raise PlanParseError("'assumptions' must be a list of strings")

    raw_steps = obj.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise PlanParseError("'steps' must be a non-empty list")

    all_ids = {s.get("id") for s in raw_steps if isinstance(s, dict)}
    steps: list[Step] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()

    for idx, raw in enumerate(raw_steps):
        where = f"steps[{idx}]"
        if not isinstance(raw, dict):
            raise PlanParseError(f"{where} must be an object")

        sid = raw.get("id")
        if not isinstance(sid, str) or not sid.strip():
            raise PlanParseError(f"{where}: 'id' must be a non-empty string")
        if sid in seen_ids:
            raise PlanParseError(f"duplicate step id '{sid}'")
        seen_ids.add(sid)
        where = f"step '{sid}'"

        title = raw.get("title")
        if not isinstance(title, str) or not title.strip():
            raise PlanParseError(f"{where}: 'title' must be a non-empty string")

        craft = raw.get("craft")
        if craft not in CRAFTS:
            raise PlanParseError(
                f"{where}: unknown craft {craft!r}; allowed: {', '.join(CRAFTS)}")

        instruction = raw.get("instruction")
        if not isinstance(instruction, str) or not instruction.strip():
            raise PlanParseError(f"{where}: 'instruction' must be a non-empty string")

        needs = raw.get("needs", [])
        if not isinstance(needs, list) or not all(isinstance(n, str) for n in needs):
            raise PlanParseError(f"{where}: 'needs' must be a list of step ids")
        for n in needs:
            if n == sid:
                raise PlanParseError(f"{where}: cannot need itself")
            if n not in all_ids:
                raise PlanParseError(f"{where}: needs unknown step '{n}'")

        emits = raw.get("emits")
        if not isinstance(emits, dict):
            raise PlanParseError(f"{where}: 'emits' must be an object with kind and name")
        kind = emits.get("kind")
        if kind not in ARTIFACT_KINDS:
            raise PlanParseError(
                f"{where}: emits.kind must be one of {', '.join(ARTIFACT_KINDS)}")
        if kind not in CRAFT_OUTPUT[craft]:
            raise PlanParseError(
                f"{where}: craft '{craft}' emits "
                f"{' or '.join(CRAFT_OUTPUT[craft])}, not '{kind}'")
        name = emits.get("name")
        if not isinstance(name, str) or not name.strip():
            raise PlanParseError(f"{where}: emits.name must be a non-empty string")
        if name in seen_names:
            raise PlanParseError(f"{where}: artifact name '{name}' already used")
        seen_names.add(name)

        acceptance = raw.get("acceptance")
        if (not isinstance(acceptance, list) or not acceptance
                or not all(isinstance(a, str) and a.strip() for a in acceptance)):
            raise PlanParseError(
                f"{where}: 'acceptance' must be a non-empty list of criteria")

        tokens = set(TOKEN_RE.findall(instruction))
        loose = tokens - set(needs)
        if loose:
            raise PlanParseError(
                f"{where}: instruction references "
                f"{', '.join(f'[[{t}]]' for t in sorted(loose))} "
                f"but 'needs' does not include it")

        steps.append(Step(
            id=sid, title=title.strip(), craft=craft,
            instruction=instruction.strip(), needs=tuple(needs),
            emits_kind=kind, emits_name=name.strip(),
            acceptance=tuple(a.strip() for a in acceptance),
        ))

    handoff = obj.get("handoff")
    if not isinstance(handoff, list) or not handoff:
        raise PlanParseError("'handoff' must be a non-empty list of artifact names")
    for h in handoff:
        if h not in seen_names:
            raise PlanParseError(f"handoff names unknown artifact '{h}'")

    plan = Plan(
        protocol=PLAN_PROTOCOL, reading=reading.strip(),
        assumptions=tuple(assumptions), steps=tuple(steps),
        handoff=tuple(handoff),
    )
    order_steps(plan.steps)  # raises PlanParseError on a dependency cycle
    return plan


def parse_critique(text: str) -> Critique:
    """Parse and validate a conductor-critique/1 reply."""
    obj = _decode_json_payload(text, CritiqueParseError)
    if obj.get("protocol") != CRITIQUE_PROTOCOL:
        raise CritiqueParseError(
            f"protocol must be '{CRITIQUE_PROTOCOL}', got {obj.get('protocol')!r}")

    verdict = obj.get("verdict")
    if verdict not in ("accept", "revise"):
        raise CritiqueParseError("'verdict' must be 'accept' or 'revise'")

    raw_notes = obj.get("notes", [])
    if not isinstance(raw_notes, list):
        raise CritiqueParseError("'notes' must be a list")
    notes: list[CritiqueNote] = []
    for idx, raw in enumerate(raw_notes):
        where = f"notes[{idx}]"
        if not isinstance(raw, dict):
            raise CritiqueParseError(f"{where} must be an object")
        artifact = raw.get("artifact")
        if not isinstance(artifact, str) or not artifact.strip():
            raise CritiqueParseError(f"{where}: 'artifact' must be a non-empty string")
        severity = raw.get("severity")
        if severity not in ("blocker", "advisory"):
            raise CritiqueParseError(f"{where}: severity must be 'blocker' or 'advisory'")
        note = raw.get("note")
        if not isinstance(note, str) or not note.strip():
            raise CritiqueParseError(f"{where}: 'note' must be a non-empty string")
        fix_hint = raw.get("fix_hint", "")
        if not isinstance(fix_hint, str):
            raise CritiqueParseError(f"{where}: 'fix_hint' must be a string")
        notes.append(CritiqueNote(
            artifact=artifact.strip(), severity=severity,
            note=note.strip(), fix_hint=fix_hint.strip(),
        ))

    if verdict == "revise" and not any(n.severity == "blocker" for n in notes):
        raise CritiqueParseError("verdict 'revise' requires at least one blocker note")

    return Critique(verdict=verdict, notes=tuple(notes))


def order_steps(steps: Sequence[Step]) -> tuple[Step, ...]:
    """Topologically order steps, preferring plan order among ready steps."""
    by_id = {s.id: s for s in steps}
    deps = {s.id: set(s.needs) for s in steps}
    done: set[str] = set()
    pending = [s.id for s in steps]
    ordered: list[Step] = []
    while pending:
        progressed = False
        for sid in list(pending):
            if deps[sid] <= done:
                ordered.append(by_id[sid])
                done.add(sid)
                pending.remove(sid)
                progressed = True
        if not progressed:
            raise PlanParseError(
                "dependency cycle among steps: " + ", ".join(sorted(pending)))
    return tuple(ordered)


# ---------------------------------------------------------------------------
# Stage: route (lane rules; mirrors ROUTING.md)
# ---------------------------------------------------------------------------

def route_plan(
    plan: Plan,
    brief: Brief,
    registry: Mapping[str, str] | None = None,
) -> dict[str, RouteDecision]:
    """Bind every step to a lane and a concrete spoke name.

    Pure function of the plan, the brief, and the registry. Rule order is
    the contract — see ROUTING.md.
    """
    reg = dict(DEFAULT_REGISTRY)
    if registry:
        reg.update(registry)
    missing = [lane for lane in LANES if not reg.get(lane)]
    if missing:
        raise RoutingError(f"registry is missing lanes: {', '.join(missing)}")

    emits = {s.id: s.emits_kind for s in plan.steps}
    long_source = len(brief.raw) >= LONG_SOURCE_CHARS

    decisions: dict[str, RouteDecision] = {}
    for step in plan.steps:
        if step.craft in ("render-image", "refine-image"):
            lane, why = "image", "image synthesis runs on the image lane"
        elif step.craft == "analyze-visual":
            lane, why = "gemini", "reading visuals needs a multimodal reader"
        elif any(emits[n] == "image" for n in step.needs):
            lane, why = ("gemini",
                         "step consumes a rendered image, so it needs multimodal grounding")
        elif long_source:
            lane, why = "gemini", "brief source exceeds the long-context threshold"
        else:
            lane, why = "openai", "structured text drafting rides the default lane"
        decisions[step.id] = RouteDecision(
            step_id=step.id, lane=lane, spoke=reg[lane], reason=why)
    return decisions


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def load_prompt(name: str, prompts_dir: Path | str | None = None) -> str:
    base = Path(prompts_dir) if prompts_dir else Path(__file__).resolve().parent / "prompts"
    path = base / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def format_brief_block(brief: Brief) -> str:
    lines = ["## Brief", f"Goal: {brief.goal}"]
    lines.append("Deliverables: " + (
        ", ".join(brief.deliverables) if brief.deliverables
        else "(none named — infer from the goal)"))
    if brief.constraints:
        lines.append("Constraints:")
        lines.extend(f"  - {c}" for c in brief.constraints)
    else:
        lines.append("Constraints: (none stated)")
    lines.append("Tone: " + (", ".join(brief.tone) if brief.tone else "(unstated)"))
    if brief.references:
        lines.append("References supplied: " + ", ".join(brief.references))
    lines += ["", "Raw request:", '"""', brief.raw, '"""']
    return "\n".join(lines)


def build_planner_prompt(
    brief: Brief,
    mode: Mode,
    step_budget: int,
    scorecard: Scorecard | None = None,
    prompts_dir: Path | str | None = None,
) -> tuple[str, str]:
    """Return (system, user) for the planner spoke."""
    system = load_prompt("planner", prompts_dir)
    parts = [
        format_brief_block(brief),
        "",
        "## Planning budget",
        f"Mode: {mode.value}",
        f"Use at most {step_budget} steps.",
    ]
    if scorecard is not None:
        parts += [
            "",
            "## Scorecard (deterministic pre-read)",
            f"complexity: {scorecard.complexity:.2f}   ambiguity: {scorecard.ambiguity:.2f}",
            "flags: " + (", ".join(scorecard.flags) if scorecard.flags else "(none)"),
            "Pin one explicit entry in `assumptions` for every flag above.",
        ]
    parts += ["", f"Return the {PLAN_PROTOCOL} JSON object now. No prose."]
    return system, "\n".join(parts)


def build_critic_prompt(
    brief: Brief,
    plan: Plan,
    artifacts: Sequence[Artifact],
    prompts_dir: Path | str | None = None,
) -> tuple[str, str, tuple[Artifact, ...]]:
    """Return (system, user, image_attachments) for the critic spoke."""
    system = load_prompt("critic", prompts_dir)
    acceptance_by_name = {s.emits_name: s.acceptance for s in plan.steps}
    parts = [format_brief_block(brief), "", "## Planner's reading", plan.reading]
    if plan.assumptions:
        parts.append("Assumptions:")
        parts.extend(f"  - {a}" for a in plan.assumptions)
    parts += ["", "## Artifacts under review"]
    attachments: list[Artifact] = []
    for art in artifacts:
        parts.append(
            f"### {art.name}  (kind: {art.kind}, step: {art.step_id}, "
            f"revision: {art.revision})")
        acc = acceptance_by_name.get(art.name, ())
        if acc:
            parts.append("Acceptance criteria:")
            parts.extend(f"  - {a}" for a in acc)
        if art.kind == "image":
            attachments.append(art)
            parts.append("(image attached)")
        else:
            body = art.text[:TEXT_DIGEST_CHARS]
            suffix = " …(truncated)" if len(art.text) > TEXT_DIGEST_CHARS else ""
            parts += ["Content:", '"""', body + suffix, '"""']
        parts.append("")
    parts.append(f"Return the {CRITIQUE_PROTOCOL} JSON object now. No prose.")
    return system, "\n".join(parts), tuple(attachments)


def build_step_prompt(
    step: Step,
    produced: Mapping[str, Artifact],
) -> tuple[str, tuple[Artifact, ...]]:
    """Render a step's prompt, threading earlier outputs through tokens.

    Text/json artifacts are inlined where their [[step_id]] token sits;
    image artifacts become attachments with an in-text marker.
    """
    attachments: list[Artifact] = []

    def _sub(match: re.Match[str]) -> str:
        sid = match.group(1)
        art = produced.get(sid)
        if art is None:
            raise WeaveError(
                f"step '{step.id}' references [[{sid}]] before it has produced anything")
        if art.kind == "image":
            attachments.append(art)
            return f"(see attached image '{art.name}')"
        return art.text

    body = TOKEN_RE.sub(_sub, step.instruction)
    lines = [
        f"## Step {step.id}: {step.title}",
        f"Craft: {step.craft}",
        "",
        body,
        "",
        "## Acceptance criteria",
    ]
    lines.extend(f"- {a}" for a in step.acceptance)
    lines += ["", "Produce only the artifact itself. No commentary, no preamble."]
    return "\n".join(lines), tuple(attachments)


# ---------------------------------------------------------------------------
# Stage: weave
# ---------------------------------------------------------------------------

def run_step(
    step: Step,
    routes: Mapping[str, RouteDecision],
    spokes: Mapping[str, Spoke],
    produced: Mapping[str, Artifact],
    *,
    extra_directive: str = "",
    revision: int = 0,
) -> Artifact:
    decision = routes.get(step.id)
    if decision is None:
        raise RoutingError(f"no route bound for step '{step.id}'")
    spoke = spokes.get(decision.spoke)
    if spoke is None:
        raise RoutingError(
            f"route for step '{step.id}' names spoke '{decision.spoke}', "
            f"which was not injected")

    prompt, attachments = build_step_prompt(step, produced)
    if extra_directive:
        prompt += "\n\n## Revision directive (from the Critic)\n" + extra_directive

    task = SpokeTask(system=WEAVER_SYSTEM, prompt=prompt,
                     expect=step.emits_kind, attachments=attachments)
    result = spoke.perform(task)
    if result.kind != step.emits_kind:
        raise WeaveError(
            f"step '{step.id}' expected a {step.emits_kind} artifact but "
            f"spoke '{decision.spoke}' returned {result.kind}")

    return Artifact(
        name=step.emits_name, kind=step.emits_kind, step_id=step.id,
        spoke=decision.spoke, text=result.text, data=result.data,
        revision=revision, meta=dict(result.meta),
    )


def weave(
    plan: Plan,
    routes: Mapping[str, RouteDecision],
    spokes: Mapping[str, Spoke],
) -> dict[str, Artifact]:
    """Execute every step in dependency order. Returns step_id -> Artifact."""
    produced: dict[str, Artifact] = {}
    for step in order_steps(plan.steps):
        produced[step.id] = run_step(step, routes, spokes, produced)
    return produced


# ---------------------------------------------------------------------------
# Stage: pin
# ---------------------------------------------------------------------------

_ARTIFACT_EXT = {"text": ".md", "json": ".json"}


def pin(
    out_dir: Path | str,
    *,
    run_id: str,
    mode: Mode,
    brief: Brief,
    plan: Plan,
    routes: Mapping[str, RouteDecision],
    artifacts: Sequence[Artifact],
    scorecard: Scorecard | None = None,
    critique: Critique | None = None,
    created_at: float = 0.0,
) -> Path:
    """Write artifact files plus manifest.json; return the manifest path."""
    out = Path(out_dir)
    art_dir = out / "artifacts"
    art_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []
    for art in artifacts:
        if art.kind == "image":
            ext = "." + str(art.meta.get("format", "png")).lstrip(".")
            payload = art.data
        else:
            ext = _ARTIFACT_EXT[art.kind]
            payload = art.text.encode("utf-8")
        safe = re.sub(r"[^A-Za-z0-9._-]+", "-", art.name).strip("-") or art.step_id
        path = art_dir / f"{safe}{ext}"
        path.write_bytes(payload)
        entries.append({
            "name": art.name,
            "kind": art.kind,
            "file": str(path.relative_to(out)),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "step": art.step_id,
            "spoke": art.spoke,
            "revision": art.revision,
            "handoff": art.name in plan.handoff,
        })

    manifest = {
        "manifest": MANIFEST_PROTOCOL,
        "run_id": run_id,
        "mode": mode.value,
        "created_at": created_at,
        "brief": {
            "goal": brief.goal,
            "deliverables": list(brief.deliverables),
            "constraints": list(brief.constraints),
            "tone": list(brief.tone),
            "references": list(brief.references),
        },
        "scorecard": (
            {
                "complexity": scorecard.complexity,
                "ambiguity": scorecard.ambiguity,
                "step_budget": scorecard.step_budget,
                "flags": list(scorecard.flags),
            } if scorecard else None
        ),
        "plan": {
            "reading": plan.reading,
            "assumptions": list(plan.assumptions),
            "handoff": list(plan.handoff),
            "steps": [
                {
                    "id": s.id,
                    "title": s.title,
                    "craft": s.craft,
                    "lane": routes[s.id].lane,
                    "spoke": routes[s.id].spoke,
                    "reason": routes[s.id].reason,
                } for s in plan.steps
            ],
        },
        "critique": (
            {
                "verdict": critique.verdict,
                "notes": [
                    {
                        "artifact": n.artifact,
                        "severity": n.severity,
                        "note": n.note,
                        "fix_hint": n.fix_hint,
                    } for n in critique.notes
                ],
            } if critique else None
        ),
        "artifacts": entries,
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


# ---------------------------------------------------------------------------
# The Conductor
# ---------------------------------------------------------------------------

class Conductor:
    """Orchestrates one design run end to end.

    All spokes are injected; the planner and critic are just spokes named by
    ``planner_spoke`` / ``critic_spoke``. The clock is injectable so traces
    and manifests are reproducible in tests.
    """

    def __init__(
        self,
        spokes: Mapping[str, Spoke],
        *,
        planner_spoke: str = DEFAULT_REGISTRY["openai"],
        critic_spoke: str | None = None,
        registry: Mapping[str, str] | None = None,
        prompts_dir: Path | str | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._spokes = dict(spokes)
        self._registry = dict(DEFAULT_REGISTRY)
        if registry:
            self._registry.update(registry)
        self._planner = planner_spoke
        self._critic = critic_spoke or planner_spoke
        self._prompts_dir = prompts_dir
        self._clock = clock

    # -- public --------------------------------------------------------

    def run(
        self,
        request: str,
        mode: Mode | str = Mode.FAST,
        *,
        out_dir: Path | str,
        references: Sequence[str] = (),
        run_id: str | None = None,
    ) -> RunResult:
        mode = Mode(mode)
        rid = run_id or uuid.uuid4().hex[:12]
        trace: list[dict[str, Any]] = []
        mark = self._clock()

        def stamp(stage: str) -> None:
            nonlocal mark
            now = self._clock()
            trace.append({"stage": stage, "ms": round((now - mark) * 1000.0, 3)})
            mark = now

        brief = distill_brief(request, references)
        stamp("brief")

        scorecard: Scorecard | None = None
        if mode is Mode.THINKING:
            scorecard = score_brief(brief)
            stamp("score")
        budget = scorecard.step_budget if scorecard else FAST_STEP_BUDGET

        plan = self._draft_plan(brief, mode, budget, scorecard)
        stamp("route:plan")
        routes = route_plan(plan, brief, self._registry)
        stamp("route:bind")

        produced = weave(plan, routes, self._spokes)
        stamp("weave")

        critique: Critique | None = None
        if mode is Mode.THINKING:
            critique = self._run_critique(brief, plan, produced)
            stamp("critique")
            if critique.verdict == "revise":
                produced = self._mend(plan, routes, produced, critique)
                stamp("critique:mend")

        artifacts = tuple(produced[s.id] for s in plan.steps)
        manifest_path = pin(
            out_dir, run_id=rid, mode=mode, brief=brief, plan=plan,
            routes=routes, artifacts=artifacts, scorecard=scorecard,
            critique=critique, created_at=self._clock(),
        )
        stamp("pin")

        return RunResult(
            run_id=rid, mode=mode, brief=brief, scorecard=scorecard,
            plan=plan, routes=routes, artifacts=artifacts,
            critique=critique, manifest_path=manifest_path,
            trace=tuple(trace),
        )

    # -- internals -----------------------------------------------------

    def _ask_for_json(
        self,
        spoke_name: str,
        system: str,
        user: str,
        parser: Callable[[str], Any],
        err_cls: type[ConductorError],
        attachments: Sequence[Artifact] = (),
    ) -> Any:
        """One call plus one bounded retry carrying the parse error back."""
        spoke = self._spokes.get(spoke_name)
        if spoke is None:
            raise RoutingError(f"spoke '{spoke_name}' is not injected")
        first = spoke.perform(SpokeTask(
            system=system, prompt=user, expect="json",
            attachments=tuple(attachments)))
        try:
            return parser(first.text)
        except err_cls as exc:
            retry = (
                user
                + "\n\n## Correction required\n"
                + f"Your previous reply could not be used: {exc}\n"
                + "Return only the corrected JSON object, nothing else."
            )
            second = spoke.perform(SpokeTask(
                system=system, prompt=retry, expect="json",
                attachments=tuple(attachments)))
            return parser(second.text)

    def _draft_plan(
        self,
        brief: Brief,
        mode: Mode,
        budget: int,
        scorecard: Scorecard | None,
    ) -> Plan:
        system, user = build_planner_prompt(
            brief, mode, budget, scorecard, self._prompts_dir)

        def parse_within_budget(text: str) -> Plan:
            plan = parse_plan(text)
            if len(plan.steps) > budget:
                raise PlanParseError(
                    f"plan uses {len(plan.steps)} steps but the budget is {budget}")
            return plan

        return self._ask_for_json(
            self._planner, system, user, parse_within_budget, PlanParseError)

    def _run_critique(
        self,
        brief: Brief,
        plan: Plan,
        produced: Mapping[str, Artifact],
    ) -> Critique:
        by_name = {a.name: a for a in produced.values()}
        reviewed = tuple(by_name[n] for n in plan.handoff if n in by_name)
        system, user, attachments = build_critic_prompt(
            brief, plan, reviewed, self._prompts_dir)
        return self._ask_for_json(
            self._critic, system, user, parse_critique,
            CritiqueParseError, attachments)

    def _mend(
        self,
        plan: Plan,
        routes: Mapping[str, RouteDecision],
        produced: dict[str, Artifact],
        critique: Critique,
    ) -> dict[str, Artifact]:
        """Re-run each blocker-flagged step once with the critic's directive.

        Downstream steps keep their originals; the manifest records the
        revision lineage. This keeps the mend pass bounded by construction.
        """
        step_by_name = {s.emits_name: s for s in plan.steps}
        notes_by_step: dict[str, list[CritiqueNote]] = {}
        for note in critique.notes:
            if note.severity != "blocker":
                continue
            step = step_by_name.get(note.artifact)
            if step is None:
                continue  # critic named something we never made; nothing to mend
            notes_by_step.setdefault(step.id, []).append(note)

        mended = dict(produced)
        for sid, notes in notes_by_step.items():
            step = next(s for s in plan.steps if s.id == sid)
            directive = "\n".join(
                f"- {n.note}" + (f" Fix: {n.fix_hint}" if n.fix_hint else "")
                for n in notes
            )
            mended[sid] = run_step(
                step, routes, self._spokes, mended,
                extra_directive=directive,
                revision=produced[sid].revision + 1,
            )
        return mended
