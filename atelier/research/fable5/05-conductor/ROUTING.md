# Routing — choosing a lane for every step

Routing is the second half of Conductor's `route` stage: after the planner
drafts a `conductor-plan/1` plan, every step is bound to exactly one **lane**,
and each lane maps to one concrete injected spoke through the registry. A
plan is not routed until every step has a lane. The rules below are mirrored
one-for-one in `route_plan()` in `conductor.py`; if this document and that
function ever disagree, the function is a bug.

## The three lanes

| lane     | default spoke  | built for |
|----------|----------------|-----------|
| `openai` | `openai-text`  | Tight structured drafting: plans and critiques (strict JSON compliance), copy, naming, specs, acceptance-driven text work. The default when nothing pulls a step elsewhere. |
| `gemini` | `gemini-omni`  | Anything that must *look* at something or *hold* a lot: reading supplied or rendered imagery, writing copy that describes an image it can actually see, digesting long source material. |
| `image`  | `image-forge`  | Making and remaking pictures. Any diffusion or image-generation endpoint slots in here; only this lane ever returns `kind: image`. |

Lane names are deliberately vendor-flavored but not vendor-locked: the
registry is a plain mapping `{lane -> spoke name}`, and spokes are injected
by name. Swapping vendors means swapping the registry entry and the injected
spoke — no routing logic changes.

## Rule order

Rules are evaluated top-down per step; the first match wins. Reasons are
recorded on every `RouteDecision` and land in the manifest, so a routing
choice is always explainable after the fact.

1. **Craft is `render-image` or `refine-image` → `image` lane.**
   Image synthesis runs on the image lane, full stop. No text model ever
   fakes a picture.
2. **Craft is `analyze-visual` → `gemini` lane.**
   Reading visuals — reference boards the client supplied, or images an
   earlier step rendered — needs a multimodal reader.
3. **Step `needs` any image-emitting step → `gemini` lane.**
   Copy or synthesis that consumes a rendered image (its instruction
   carries a `[[step_id]]` token whose artifact is an image) must be
   grounded in what the image actually shows, not in the prompt that
   requested it. This catches the classic failure of a text model
   confidently describing an image it never saw.
4. **Brief source at or above the long-context threshold (8,000 chars) →
   `gemini` lane.** Long transcripts, pasted documents, sprawling
   requirements: route drafting to the long-context lane rather than
   truncating.
5. **Otherwise → `openai` lane.** Structured text drafting rides the
   default lane.

## Signals read from the brief

| signal | where it comes from | effect |
|--------|---------------------|--------|
| Raw length ≥ 8,000 chars | `len(brief.raw)` | Rule 4 pulls text steps to `gemini`; scorecard gains `long-source`. |
| Reference files supplied | `brief.references` | Scorecard gains `has-references`; the planner is told what was supplied and will typically open with an `analyze-visual` step, which rule 2 routes to `gemini`. |
| Image deliverables named | deliverable scan (logo, poster, icon, …) | The planner emits `render-image` steps, which rule 1 routes to `image`. |
| Mixed media (image + text deliverables) | scorecard flag `mixed-media` | No direct routing effect; raises the step budget by one so the weave can afford a synthesis step. |

## Where the planner and critic run

The planner and critic are ordinary spokes selected by name
(`Conductor(planner_spoke=..., critic_spoke=...)`), defaulting to the
`openai` lane's spoke because plan and critique quality lives or dies on
strict JSON envelope compliance. Two situations justify overriding:

- **The critique must see images.** Rendered image artifacts in the handoff
  are attached to the critic's task. If the critic spoke cannot accept image
  attachments, point `critic_spoke` at the `gemini` lane's spoke so verdicts
  on visual work are grounded in pixels, not in step instructions.
- **The brief itself is dominated by imagery or very long source.** If the
  plan cannot be drawn well without actually reading the supplied material,
  point `planner_spoke` at the `gemini` lane's spoke.

Text-in-image legibility (posters with headlines, UI mockups with real
labels) is a spoke-selection concern inside the `image` lane: register an
image spoke that holds glyphs well as `image-forge` for those runs. The lane
logic does not change.

## Failure is loud

- A registry missing any of the three lanes raises `RoutingError` at bind
  time — before any step runs.
- A route naming a spoke that was never injected raises `RoutingError` at
  the step, identifying both the step and the missing spoke.
- There is **no silent substitution**: Conductor never quietly downgrades an
  image step to a text spoke or vice versa. Retry, fallback-vendor, and
  budget policies belong to the layer above Conductor (Atelier's quota and
  scheduling machinery), which can rerun with a different registry.

## Overriding the registry

```python
from conductor import Conductor

conductor = Conductor(
    spokes={
        "openai-text": my_openai_spoke,
        "gemini-omni": my_gemini_spoke,
        "glyph-forge": my_typography_tuned_image_spoke,
    },
    registry={"image": "glyph-forge"},   # openai/gemini keep their defaults
    critic_spoke="gemini-omni",          # critic must see the rendered posters
)
```

## Worked examples

**"Write five tagline options for a bakery. Friendly, no puns."**
One `compose-text` step. No images anywhere, short brief → rule 5, `openai`.

**"Here are 12 photos from our shoot (attached). Pick a direction and make
a poster, 1080x1350."**
`analyze-visual` over the references → rule 2, `gemini`. `render-image` for
the poster → rule 1, `image`. A closing `synthesize` rationale that cites
the chosen photo and the rendered poster needs both image artifacts →
rule 3, `gemini`.

**A 20,000-character product spec pasted into the brief, asking for landing
page copy.**
Every `compose-text` step → rule 4, `gemini`, because the source exceeds
the long-context threshold and truncating a spec is how contradictions
ship.
