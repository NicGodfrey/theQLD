# Conductor Protocol — v1

Conductor is Atelier's design-run orchestrator. It takes a raw creative
request and walks it through a fixed pipeline of named stages, delegating
every model call to an injected **Spoke**. This document is the contract for
the three JSON envelopes that cross the wire:

| envelope               | direction        | produced by      |
|------------------------|------------------|------------------|
| `conductor-plan/1`     | planner → weave  | planner spoke    |
| `conductor-critique/1` | critic → mend    | critic spoke     |
| `conductor-manifest/1` | pin → disk       | Conductor itself |

Inspiration credit: the staged, self-reviewing shape is inspired by
multimodal chain-of-thought orchestrators such as Lovart's MCoT. The stage
names, schemas, craft vocabulary, and wording here are original to Atelier.

---

## 1. Modes and stages

```
fast      brief ─► route ─► weave
thinking  brief ─► score ─► route ─► weave ─► critique ─► pin
```

| stage    | LLM calls | what happens |
|----------|-----------|--------------|
| brief    | 0         | Deterministic distillation of the raw request into a `Brief` (goal, deliverables, constraints, tone, references). Pure function, unit-testable. |
| score    | 0         | *(thinking only)* Deterministic `Scorecard`: complexity, ambiguity, flags, and a step budget. Never a model call — thinking mode's extra cost is exactly the critique (plus any mend re-runs). |
| route    | 1         | The planner spoke drafts a `conductor-plan/1` plan (one call, one bounded retry on parse failure), then every step is bound to a concrete spoke by the lane rules in `ROUTING.md`. A plan is not "routed" until every step has a lane. |
| weave    | 1 per step| Steps execute in dependency order. Earlier outputs thread into later instructions through `[[step_id]]` tokens. |
| critique | 1         | *(thinking only)* The critic spoke judges the handoff artifacts against the brief and each step's acceptance criteria, returning `conductor-critique/1`. |
| pin      | 0         | Artifacts and `manifest.json` are written to the run directory. Pin is free — it never calls a model — so fast mode runs it silently as weave's epilogue rather than as a named stage. |

**Mend semantics.** If the critique verdict is `revise`, each step whose
artifact drew a `blocker` note is re-run **once**, with the critic's notes
appended as a revision directive. Downstream steps that consumed the old
artifact are *not* re-run; the manifest records the revision lineage instead.
There is no second critique pass. Conductor is bounded by construction:
worst case is `steps + 4` model calls per run (plan, plan-retry, critique,
critique-retry, plus one mend per flagged step).

---

## 2. The plan envelope — `conductor-plan/1`

The planner must reply with **exactly one JSON object** and nothing else.
Conductor tolerates a markdown fence and leading/trailing prose around the
object (it extracts the first JSON object it finds), but the prompt forbids
them, and anything unparseable triggers the single bounded retry.

### Example

```json
{
  "protocol": "conductor-plan/1",
  "reading": "Solstice Tea wants a compact identity: a one-color logo mark in deep green and a short tagline, both quiet and unfussy.",
  "assumptions": [
    "A symbol-only mark (no wordmark) satisfies 'logo' here.",
    "White is an acceptable background since none was specified."
  ],
  "steps": [
    {
      "id": "s1",
      "title": "Write the tagline",
      "craft": "compose-text",
      "instruction": "Write one tagline for Solstice Tea, a small-batch tea house. Six words or fewer. Tone: minimal, warm. Avoid puns on 'tea time'.",
      "needs": [],
      "emits": { "kind": "text", "name": "tagline" },
      "acceptance": ["six words or fewer", "contains no pun on 'tea time'"]
    },
    {
      "id": "s2",
      "title": "Render the logo mark",
      "craft": "render-image",
      "instruction": "Render a minimal logo mark for Solstice Tea: a single continuous line suggesting steam rising from a cup, using only #2F5D50 on white.",
      "needs": [],
      "emits": { "kind": "image", "name": "logo-mark" },
      "acceptance": ["uses only #2F5D50 on white", "legible at 32 pixels"]
    },
    {
      "id": "s3",
      "title": "Assemble the style note",
      "craft": "synthesize",
      "instruction": "Combine the tagline [[s1]] and the logo (attached, from [[s2]]) into a one-page style note covering usage, clear space, and the palette (#2F5D50 plus neutral grays).",
      "needs": ["s1", "s2"],
      "emits": { "kind": "text", "name": "style-note" },
      "acceptance": ["names the hex value #2F5D50", "under 200 words"]
    }
  ],
  "handoff": ["tagline", "logo-mark", "style-note"]
}
```

### Fields

| field                | type            | rules |
|----------------------|-----------------|-------|
| `protocol`           | string          | Must equal `"conductor-plan/1"`. |
| `reading`            | string          | One paragraph: what the client actually wants, in the planner's own words. Non-empty. |
| `assumptions`        | string[]        | Every decision the planner made where the brief was silent. May be empty. In thinking mode the planner must pin one assumption per scorecard flag. |
| `steps`              | object[]        | Non-empty. Must form a DAG (cycles are a parse error). Must not exceed the step budget given in the prompt. |
| `steps[].id`         | string          | Non-empty, unique within the plan. |
| `steps[].title`      | string          | Non-empty, a few words. |
| `steps[].craft`      | string          | One of the craft vocabulary below. |
| `steps[].instruction`| string          | Self-contained: a maker who has read nothing else must be able to act on it. Constraints must be restated inside every instruction they bind. |
| `steps[].needs`      | string[]        | Ids of earlier steps. Every id must exist and must not be the step itself. |
| `steps[].emits.kind` | string          | `text`, `json`, or `image` — and must be a kind the step's craft can emit (see table). |
| `steps[].emits.name` | string          | Non-empty artifact name, unique across the plan. |
| `steps[].acceptance` | string[]        | At least one criterion. Each must be checkable yes/no by a stranger. |
| `handoff`            | string[]        | At least one entry. Each must match some step's `emits.name`. Only what the client receives — scaffolding stays out. |

### Craft vocabulary

| craft            | does                                              | may emit     |
|------------------|---------------------------------------------------|--------------|
| `compose-text`   | writes copy, names, specs, structured text        | `text`, `json` |
| `analyze-visual` | reads supplied or rendered imagery and reports    | `text`, `json` |
| `render-image`   | creates a new image from a written direction      | `image`      |
| `refine-image`   | reworks an existing image per a directive         | `image`      |
| `synthesize`     | merges earlier outputs into one deliverable       | `text`, `json` |

### Reference tokens

`[[step_id]]` inside an instruction is the only mechanism that carries
content between steps. At weave time the token is replaced by the referenced
step's text output; if the referenced artifact is an **image**, the artifact
is attached to the spoke task and the token becomes
`(see attached image '<name>')`. Two validation rules follow:

1. Every token's id must appear in that step's `needs` (a token without the
   dependency is a parse error — content cannot cross without an edge).
2. `needs` without a token only fixes execution order; no content crosses.

### Validation and retry

`parse_plan` raises `PlanParseError` with a human-readable reason for any
violation above. Conductor appends that reason to the original prompt under a
`## Correction required` heading and retries **once**. A second failure
aborts the run with the error — Conductor never silently repairs a plan.

---

## 3. The critique envelope — `conductor-critique/1`

### Example

```json
{
  "protocol": "conductor-critique/1",
  "verdict": "revise",
  "notes": [
    {
      "artifact": "tagline",
      "severity": "blocker",
      "note": "Seven words; acceptance requires six or fewer.",
      "fix_hint": "Cut to at most six words while keeping 'small-batch'."
    },
    {
      "artifact": "style-note",
      "severity": "advisory",
      "note": "Clear-space rule is stated in words only.",
      "fix_hint": "Express clear space as a multiple of the mark's height."
    }
  ]
}
```

### Fields

| field              | type     | rules |
|--------------------|----------|-------|
| `protocol`         | string   | Must equal `"conductor-critique/1"`. |
| `verdict`          | string   | `accept` or `revise`. `revise` requires at least one blocker note; `accept` may still carry advisory notes. |
| `notes[].artifact` | string   | The artifact name exactly as given in the review prompt. |
| `notes[].severity` | string   | `blocker` (handing off would break a stated constraint or fail a stated acceptance check) or `advisory` (would improve the work; taste lives here). |
| `notes[].note`     | string   | What is wrong, tied to the brief or a criterion. Non-empty. |
| `notes[].fix_hint` | string   | An instruction the original maker could follow verbatim. Required in spirit for blockers; may be empty for advisories. |

`parse_critique` raises `CritiqueParseError` on violations; the same
single-retry contract as the plan applies.

---

## 4. The manifest — `conductor-manifest/1`

Pin writes each artifact to `<out_dir>/artifacts/<safe-name>.<ext>`
(`.md` for text, `.json` for json, image extension from the artifact's
`format` metadata, defaulting to `.png`) and then writes
`<out_dir>/manifest.json`:

```json
{
  "manifest": "conductor-manifest/1",
  "run_id": "3f9c2ab81d04",
  "mode": "thinking",
  "created_at": 1789000000.0,
  "brief": { "goal": "...", "deliverables": ["logo", "tagline"], "constraints": ["Must use #2F5D50."], "tone": ["minimal"], "references": [] },
  "scorecard": { "complexity": 0.38, "ambiguity": 0.0, "step_budget": 7, "flags": ["mixed-media"] },
  "plan": {
    "reading": "...",
    "assumptions": ["..."],
    "handoff": ["tagline", "logo-mark", "style-note"],
    "steps": [
      { "id": "s1", "title": "Write the tagline", "craft": "compose-text", "lane": "openai", "spoke": "openai-text", "reason": "structured text drafting rides the default lane" }
    ]
  },
  "critique": { "verdict": "revise", "notes": [ { "artifact": "tagline", "severity": "blocker", "note": "...", "fix_hint": "..." } ] },
  "artifacts": [
    {
      "name": "tagline", "kind": "text", "file": "artifacts/tagline.md",
      "sha256": "…64 hex chars…", "bytes": 34,
      "step": "s1", "spoke": "openai-text", "revision": 1, "handoff": true
    }
  ]
}
```

`revision` starts at 0 and increments once per mend re-run. `handoff` marks
whether the artifact is part of the client-facing set. The `artifacts` array
is the canonical artifacts list for the run; everything else in the manifest
is provenance.

---

## 5. Determinism and testability

- Every model call goes through the injected `Spoke` protocol
  (`perform(SpokeTask) -> SpokeResult`). `conductor.py` opens no sockets.
- `distill_brief`, `score_brief`, `parse_plan`, `parse_critique`,
  `order_steps`, `route_plan`, `build_planner_prompt`, `build_critic_prompt`,
  `build_step_prompt`, and `pin` are pure or filesystem-only and run offline.
- The clock is injectable (`Conductor(clock=...)`) and the run id can be
  supplied (`run(..., run_id=...)`), so full runs are reproducible in tests
  with scripted spokes. See `tests/test_conductor.py`.
