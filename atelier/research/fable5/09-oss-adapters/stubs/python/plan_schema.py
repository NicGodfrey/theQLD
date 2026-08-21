"""Atelier plan extraction — Instructor/Outlines *patterns*, stdlib only.

The agent loop is: user intent -> LLM -> plan JSON -> executor. This module makes
the "plan JSON" step reliable using the fallback ladder from ADAPTERS.md #7:

  1. provider-native structured outputs (response_format: json_schema)
  2. JSON mode + validate, re-prompting with validation errors (Instructor's trick)
  3. fence extraction + tolerant repair + validate
  4. (not here) Outlines/vLLM constrained decoding for self-hosted models —
     slots in as a Provider whose output is valid by construction, so rungs
     2-3 simply never fire.

Upgrading later: replace `validate_plan` with a Pydantic model + `instructor.patch`;
`extract_plan`'s signature and callers stay identical.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from llm_gateway import Message, Router

# ---------------------------------------------------------------------------
# The plan schema. Kept as a plain dict: it doubles as the provider-native
# json_schema payload (rung 1) and drives the stdlib validator (rungs 2-3).
# ---------------------------------------------------------------------------

PLAN_OPS = ("create_layer", "generate_image", "edit_image", "add_text", "move", "resize", "delete")

PLAN_JSON_SCHEMA: dict = {
    "name": "atelier_plan",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["goal", "steps"],
        "properties": {
            "goal": {"type": "string"},
            "steps": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["op", "target", "args"],
                    "properties": {
                        "op": {"type": "string", "enum": list(PLAN_OPS)},
                        "target": {"type": "string"},  # layer/element id or "new"
                        "args": {"type": "object"},
                    },
                },
            },
        },
    },
    "strict": True,
}


@dataclass
class Plan:
    goal: str
    steps: list[dict]


class PlanValidationError(ValueError):
    """Carries human-readable errors we can feed back to the model."""


def validate_plan(data: object) -> Plan:
    errors: list[str] = []
    if not isinstance(data, dict):
        raise PlanValidationError("top level must be a JSON object")
    if not isinstance(data.get("goal"), str) or not data.get("goal"):
        errors.append("'goal' must be a non-empty string")
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("'steps' must be a non-empty array")
        steps = []
    for i, step in enumerate(steps):
        where = f"steps[{i}]"
        if not isinstance(step, dict):
            errors.append(f"{where} must be an object")
            continue
        if step.get("op") not in PLAN_OPS:
            errors.append(f"{where}.op must be one of {PLAN_OPS}, got {step.get('op')!r}")
        if not isinstance(step.get("target"), str):
            errors.append(f"{where}.target must be a string")
        if not isinstance(step.get("args"), dict):
            errors.append(f"{where}.args must be an object")
    if errors:
        raise PlanValidationError("; ".join(errors))
    return Plan(goal=data["goal"], steps=steps)


# ---------------------------------------------------------------------------
# Tolerant JSON recovery (rung 3).
# ---------------------------------------------------------------------------

_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_TRAILING_COMMA = re.compile(r",(\s*[}\]])")


def loads_lenient(text: str) -> object:
    """Extract the first JSON object from model prose and repair common damage."""
    m = _FENCE.search(text)
    candidate = m.group(1) if m else text
    start, end = candidate.find("{"), candidate.rfind("}")
    if start == -1 or end <= start:
        raise PlanValidationError("no JSON object found in output")
    candidate = candidate[start : end + 1]
    candidate = candidate.replace("\u201c", '"').replace("\u201d", '"')
    candidate = _TRAILING_COMMA.sub(r"\1", candidate)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise PlanValidationError(f"invalid JSON: {e}") from e


# ---------------------------------------------------------------------------
# The extraction loop (rungs 1-3 + Instructor-style error feedback).
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are Atelier's planner. Respond with ONLY a JSON object matching the schema: "
    '{"goal": string, "steps": [{"op": one of %s, "target": string, "args": object}]}. '
    "No prose, no markdown fences." % (list(PLAN_OPS),)
)


def extract_plan(
    router: Router,
    alias: str,
    user_messages: list[Message],
    *,
    max_retries: int = 2,
    native_structured: bool = True,
) -> Plan:
    messages: list[Message] = [{"role": "system", "content": SYSTEM_PROMPT}, *user_messages]

    response_format: dict | None = None
    if native_structured:
        response_format = {"type": "json_schema", "json_schema": PLAN_JSON_SCHEMA}

    last_err: PlanValidationError | None = None
    for _ in range(max_retries + 1):
        try:
            result = router.complete(
                alias, messages, temperature=0.2, response_format=response_format
            )
        except Exception:
            if response_format is not None:
                # Provider rejected json_schema (rung 1 unsupported) -> JSON mode.
                response_format = {"type": "json_object"}
                continue
            raise

        try:
            try:
                data = json.loads(result.text)
            except json.JSONDecodeError:
                data = loads_lenient(result.text)
            return validate_plan(data)
        except PlanValidationError as err:
            last_err = err
            # Instructor's core move: show the model its own output and the
            # validation errors, then ask again.
            messages = messages + [
                {"role": "assistant", "content": result.text},
                {
                    "role": "user",
                    "content": f"Your JSON failed validation: {err}. "
                    "Reply with ONLY the corrected JSON object.",
                },
            ]

    raise PlanValidationError(f"could not obtain a valid plan after retries: {last_err}")


if __name__ == "__main__":
    # Offline self-test of the validator + lenient parser (no network).
    good = {"goal": "poster", "steps": [{"op": "add_text", "target": "new", "args": {"text": "hi"}}]}
    assert validate_plan(good).goal == "poster"
    messy = 'Sure! ```json\n{"goal": "x", "steps": [{"op": "move", "target": "l1", "args": {},}]}\n```'
    assert validate_plan(loads_lenient(messy)).steps[0]["op"] == "move"
    try:
        validate_plan({"goal": "", "steps": [{"op": "explode"}]})
    except PlanValidationError as e:
        print("expected failure:", e)
    print("plan_schema self-test OK")
