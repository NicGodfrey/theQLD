# Conductor Gaps — live `helix/conductor.py` vs `research/fable5/05-conductor/`

Opus#4 of 10 · 2026-08-21 · read-only audit, no files in `/workspace` touched.

Scope: what stands between the shipped Conductor and a design agent a stranger
could use for an hour without concluding it ignores them. Both sides were run:
`research/fable5/05-conductor` → **36 tests, all pass**;
`atelier/tests/test_helix.py` → **7 tests, all pass**. The research module is
not aspirational vapor — it is working, offline-testable code that the live
product does not import.

---

## 0. The shape of the difference

| | live `atelier/helix/conductor.py` | research `05-conductor/conductor.py` |
|---|---|---|
| lines | 277 | 1,075 (+ PROTOCOL.md, ROUTING.md, 2 prompt files) |
| plan representation | one untyped `dict`; `weave: [{kind, prompt, count}]` | `Plan`/`Step` frozen dataclasses with `needs`, `emits`, `acceptance` |
| plan validation | none — `extract_json` regex-greps `{.*}` and `plan.update(parsed)` merges whatever arrived (`conductor.py:42-50`, `:126`) | 22 `raise PlanParseError` sites in `parse_plan`, 9 in `parse_critique` |
| malformed planner reply | swallowed to a local single-image fallback with no user signal (`:127-130`) | one bounded retry carrying the parse reason back, then abort (`_ask_for_json`, `:976-1004`) |
| step ordering | list order, `weave_items[:4]`, `count` clamped to 2 (`:140-143`) | topological `order_steps` with cycle detection (`:534-552`) |
| inter-step content | none — every item prompt is standalone | `[[step_id]]` tokens inline text, attach images (`build_step_prompt`, `:689-722`) |
| routing | one provider for the whole run; `_image_model(provider)` (`:158`, `:252-257`) | 5 ordered lane rules → `RouteDecision(lane, spoke, reason)` (`route_plan`, `:559-594`) |
| provider failure | silent downgrade to demo SVG, still pinned as a real artifact (`:162-164`) | `RoutingError`, loud, before any step runs; ROUTING.md §"Failure is loud" |
| critique | prose blob, thinking mode only, appended to the chat summary (`:199-223`) | `conductor-critique/1` with per-artifact `severity`/`fix_hint` + bounded `_mend` re-run (`:1040-1074`) |
| record of the run | `messages.plan_json` + board nodes | `conductor-manifest/1`: sha256, revision lineage, per-step lane + reason (`pin`, `:785-878`) |
| brand kit | project kit JSON truncated to 1,200 chars into the planner system prompt only (`:260-263`) | absent entirely (research never modelled brand) |
| variants | `count` clamp duplicates the *same* prompt, no rationale, no choice | absent entirely |

Two different absences are in play and they need different fixes:

- **Regression** — the research module has the machinery, the live product does
  not import it (validation, retry, lanes, tokens, mend, manifest). This is a
  transplant, and the 36 tests come with it.
- **Never built** — neither side has it (visible plan card, step reorder,
  4-variant pick grid, referring expressions, brand-kit enforcement). These are
  in `01-product-spec/ACCEPTANCE.md` as MVP must-haves and exist only as prose.

There is also a **protocol mismatch** that gates several items: research spokes
are `perform(SpokeTask) -> SpokeResult` with `attachments` and an `expect` kind
(`:166-186`); live spokes are `chat(messages, model)` / `image(prompt, model)`
with **no attachment path at all** (`helix/spokes/base.py:34-41`). Live
`gemini_spoke.chat` builds text-only `parts` (`gemini_spoke.py:49-66`);
`openai_spoke.chat` posts a bare `messages` array (`openai_spoke.py:49-55`).
So today a synthesis step *cannot* see the image it is describing, and the
critic cannot see the poster it is judging. Any lane rule about multimodal
grounding is decorative until that is fixed.

---

## 1. Gaps ranked by user-visible impact

Ranked by "how fast does a first-time user notice, and does it read as the
product being broken or merely thin?" Severity: **S1** = the product looks
broken or dishonest; **S2** = a promised interaction is missing; **S3** =
quality degrades without an obvious cause.

### G1 — The plan is computed, stored, and never shown · S1
Plan mode has no visible artifact. `Conductor.run` builds a plan and persists it
(`store.py:152-166` writes `plan_json`), `list_messages` deserializes it into
`row["plan"]` (`store.py:174-184`), and then `web/app.js:116-125` renders
`m.content` as a text div and throws the plan away. The user sees three summary
lines from `_summarize` (`conductor.py:266-276`) and images appearing. There is
no step list, no per-step progress, no lane, no engine name on any node — the
board caption is the raw prompt (`app.js:85`).
ACCEPTANCE M-2 line 18 and M-3 line 27 both fail.
**Why it ranks first:** every other agent affordance (reorder, run-remaining,
per-step retry, progress, provenance) hangs off this one surface. Without it the
product is a prompt box that emits pictures, which is the thing the whole
Conductor design exists to not be.

### G2 — No step reorder / delete / run-remaining · S2
There is no plan-edit path anywhere: `server.py` exposes exactly one agent
endpoint, `POST /api/threads/{id}/run` (`:196-214`), which plans and executes in
one blocking call. There is no plan id, no `plans` table (`store.py` SCHEMA
`:12-71` has projects/threads/messages/artifacts/nodes/usage_events), nothing to
edit between drafting and weaving. Research `order_steps` is a topological
sorter, not a user-order validator — it will happily re-derive an order the user
never asked for. This is `FEATURE_MATRIX.md:130`'s stated differentiator over
Lovart's read-only task chain, and it does not exist on either side.

### G3 — Failures are silent, and silence reads as incompetence · S1
Three swallow points, all user-visible as "the agent ignored my brief":
1. Planner returns prose or broken JSON → `except (SpokeError, ValueError,
   JSONDecodeError): pass` (`:127-130`) → the run proceeds on `fallback_plan`,
   a single image of the raw prompt (`:53-67`). No retry, no message, no
   distinction from a successful plan.
2. Planner returns *valid JSON of the wrong shape* → `plan.update(parsed)`
   (`:126`) merges it unvalidated; a missing `weave` silently becomes one
   image (`:135`), a bogus `route.provider` is `setdefault`-patched (`:133-134`).
3. Image spoke raises → `build_spoke("demo")` substitutes a hash-colored
   gradient SVG (`loom.py:10-28`) and pins it as a real artifact with
   `provider="demo"` (`conductor.py:162-164`). The board shows a deliverable
   that is not one.
The research side solves 1 and 2 (`_ask_for_json` retry + 22 validation rules)
and explicitly forbids 3 (ROUTING.md: "no silent substitution... Conductor never
quietly downgrades an image step to a text spoke"). The fix is a transplant plus
deleting two `except` bodies — cheapest high-severity win in the list.

### G4 — No referring expressions, so there is no second turn · S1
`Conductor.run` takes `prompt` and nothing else (`:82-91`): no selection, no
node id, no entity ledger. Every turn appends fresh nodes at
`next_board_offset(existing)` (`:70-73`), a global 3-column stack. "Make the logo
darker" produces an unrelated fourth image next to the logo. The board has no
notion of a node being *the* logo: `nodes.meta` exists (`store.py:59`) and is
never written with anything, `update_node` accepts `meta` (`store.py:252`) and
nothing calls it. `refine-image` is in the research craft vocabulary
(`CRAFTS`, research `:52`) and has no live counterpart.
ACCEPTANCE M-2 line 23 (20 scripted follow-ups, ≥90% resolution, target shown
before the edit applies) has no code to run against.
**Why S1:** conversational refinement is the product. One-shot generation is a
worse Midjourney.

### G5 — Thinking mode costs double and changes nothing on the board · S1
Live thinking mode adds one prose critic call (`:199-223`) whose output is
concatenated into the chat summary (`_summarize`, `:274`). It names no artifact,
carries no severity, triggers no re-render. Nothing on the canvas differs
between `fast` and `thinking` except the bill — `usage.record` charges the extra
tokens (`:213-220`). The research side has the whole loop: structured
`CritiqueNote(artifact, severity, fix_hint)`, `verdict == "revise"` requiring at
least one blocker (`:528-529`), and `_mend` re-running exactly the flagged steps
once with the directive appended and `revision + 1` (`:1040-1074`). The mend
machinery is *written and tested* (`test_thinking_run_mends_blocker_and_records_lineage`)
and unreachable from the product.

### G6 — Brand kit is a suggestion, not a constraint · S2
`_brand_block` JSON-dumps the kit, truncates at 1,200 chars mid-token, and
appends it to the *planner* system prompt only (`:260-263`). Per-item image
prompts are `item.get("prompt")` verbatim (`:142`, `:161`) — the palette never
reaches the image model. Nothing checks the result. The default studio kit
(`server.py:45-49`) ships four hex values that no generated pixel is obliged to
respect. ACCEPTANCE M-5 line 41 asks for ΔE ≤ 10 on 90% of a 50-generation
benchmark; there is no measurement function anywhere in the repo. Research does
not model brand at all, but its `Step.acceptance` + critic loop is the natural
carrier: brand rules should be *acceptance criteria*, checkable, not vibes in a
system prompt.

### G7 — One provider for everything; no lanes, no reasons, no grounding · S3
`plan["route"]["provider"]` is a single value for the whole run
(`:133-134`, `:158-160`), defaulted from the UI dropdown (`app.js:201`,
`index.html:56-61`). `_default_model` / `_image_model` are two-line switches
(`:242-257`). None of ROUTING.md's five rules exist: no craft→lane mapping, no
`analyze-visual` lane, no image-consumer grounding rule, no 8,000-char
long-source rule, no `RouteDecision.reason` recorded anywhere. Consequence users
feel: pick `openai` and every step goes to `gpt-4o-mini`, including one asked to
write copy about a poster it never saw — the exact failure ROUTING.md rule 3 was
written to prevent. Blocked behind the spoke-attachment gap above, which is why
this is S3 and not S1: the damage is quality-shaped, not visibly-broken-shaped.

### G8 — No token weaving, so multi-asset briefs don't compose · S3
Live weave items are independent prompts in a `for` loop (`:140-197`). Ask for
"a logo, then a poster using that logo, then a style note citing both" and you
get three unrelated images. Research does this correctly and cheaply:
`build_step_prompt` substitutes `TOKEN_RE` matches with the referenced
artifact's text, or attaches the image and leaves
`(see attached image '<name>')` in its place (`:689-722`), with parse-time
enforcement that a token without a `needs` edge is an error (`:461-467`). This
arrives free with the transplant — it is the same code path as G3's validation.

### G9 — No 4-variant pick grid; `count` produces duplicates, not choices · S2
`count = max(1, min(int(item.get("count") or 1), 2))` (`:143`) re-runs the
**identical prompt** up to twice. No variant directions, no rationale, no
grid, no keyboard cycling, no keep, no variant stack. `nodes.meta` is the
obvious home for a variant stack and is unused. ACCEPTANCE M-3 line 29 (4
variants, one-line rationale each, Tab/arrow cycling, Enter to keep, discarded
variants recoverable) and `FEATURE_MATRIX.md:104-105` ("Say / Pick / Polish" —
Pick is the whole middle third of the product grammar) have no implementation on
either side.
**Ranked below G4/G5 deliberately:** a user who cannot refine or trust the
output will not stay long enough to miss the grid. But this is the single most
*legible* feature gap versus Lovart, so it belongs in the first shipped cut.

### Enablers, not user-visible on their own
- **E1 Spoke attachment protocol.** `Spoke.chat` has no attachment parameter
  (`spokes/base.py:37`); OpenAI needs `image_url` content parts, Gemini needs
  `inlineData` parts. Gates G5 (critic sees pixels), G7 (rule 3), G4 (refine
  from a source image). ~40 lines across two files; fixtures already exist at
  `research/fable5/03-keyring-spokes/tests/fixtures/{openai,gemini}_chat.json`.
- **E2 No manifest / provenance.** `pin` (research `:785-878`) writes sha256,
  revision lineage, and per-step lane + reason. Live writes board nodes and a
  chat row. Blocks export metadata (M-6), the credit ledger's per-turn detail
  (M-6 line 48), and any "why did it pick that engine" answer.
- **E3 No structured JSON request.** Neither spoke sets
  `response_format={"type":"json_object"}` (OpenAI) or `responseMimeType`
  (Gemini), so the retry path in `_ask_for_json` will fire more than it needs to.

---

## 2. One-week close: make the transplant visible

Goal for the week: **plan mode you can see and edit, four variants you can pick
from, and failures that announce themselves.** That is G1, G2, G3, G9, plus G8
and G6 arriving nearly free. G4, G5, G7 are explicitly deferred — they need a
ledger, attachments, and per-lane keys respectively, and half-shipping them is
worse than not.

### W1 — Transplant the engine, keep the adapter (unblocks G3, G8)
- Copy `research/fable5/05-conductor/conductor.py` → **`atelier/helix/weave.py`**
  unchanged except imports; copy `prompts/planner.md`, `prompts/critic.md` →
  **`atelier/helix/prompts/`** (research `load_prompt` already resolves
  `Path(__file__).parent / "prompts"`, research `:601-606`, so the layout is
  preserved).
- Reduce **`atelier/helix/conductor.py`** to the impure adapter it should be:
  keep `class Conductor(memory, keyring, artifacts_dir)` and its `run()`
  signature so `server.py:202-209` is untouched, and have it delegate to
  `weave.Conductor`. New private methods: `_build_spokes()`, `_pin_to_board()`,
  `_record_usage()`.
- **Delete** `extract_json`, `fallback_plan`, `PLANNER_SYSTEM`, `CRITIC_SYSTEM`,
  `_default_model`, `_image_model`, `_summarize`, `next_board_offset`. Update
  `tests/test_helix.py:57-78` which imports `extract_json` and `fallback_plan`.
- New **`atelier/helix/spokes/adapter.py`**:
  `class SpokeAdapter` implementing `perform(SpokeTask) -> SpokeResult` by
  dispatching `expect in {"text","json"}` → `Spoke.chat`, `expect == "image"` →
  `Spoke.image`, and translating `SpokeError` → `weave.WeaveError` so failures
  surface instead of being downgraded.
- New **`atelier/helix/lanes.py`**:
  `build_registry(keyring, prefs) -> tuple[dict[str, Spoke], dict[str, str]]`
  returning injected adapters plus the lane→spoke-name registry
  `route_plan` expects. When a lane has no key, register the demo adapter under
  a **distinct name** (`"demo-stand-in"`) so `RouteDecision.spoke` and the node
  provenance chip both say `demo` — substitution stays visible.
- Make the offline demo path go through the same validator: rewrite
  `DemoSpoke.chat` (`spokes/base.py:55-83`) to emit a conformant
  `conductor-plan/1` object. If the demo plan cannot pass `parse_plan`, the
  validator is wrong or the demo is lying; either is worth knowing.
- Port the 36 tests → **`atelier/tests/test_weave.py`** (swap
  `import conductor as c` for `from atelier.helix import weave as c`; drop the
  `sys.path` shim at research `tests/test_conductor.py:15`). Add
  `test_adapter_maps_expect_to_chat_and_image` and
  `test_missing_lane_key_registers_named_stand_in`.

### W2 — Plan/run split and the `plans` table (unblocks G1, G2)
- **`helix/store.py`**: add to SCHEMA a `plans` table
  `(id, thread_id, protocol, reading, assumptions_json, steps_json,
  handoff_json, scorecard_json, routes_json, status, created_at)` and a
  `plan_steps` table `(plan_id, step_id, ord, status, artifact_id, error)` —
  `plan_steps.ord` is what a reorder writes and `status` is what the plan card
  polls. New methods: `save_plan`, `get_plan`, `update_plan_steps`,
  `set_step_status`, `list_plan_steps`.
- **`helix/weave.py`**: two new pure functions beside `order_steps`:
  - `validate_order(steps, order) -> tuple[Step, ...]` — accepts a user order,
    raises `PlanParseError` if it violates a `needs` edge. (`order_steps`
    *derives* an order; this one *checks* one. Different job, same contract.)
  - `drop_steps(plan, ids) -> Plan` — removes steps, then re-runs `parse_plan`'s
    token/needs/handoff checks so dropping a step still referenced by a
    `[[token]]` or by `handoff` is rejected with the reason, not silently
    repaired.
- **`server.py`**: split the single endpoint into
  `POST /api/threads/{id}/plan` → `{plan_id, plan, scorecard, routes,
  cost_estimate}` (calls `distill_brief`, `score_brief`, `_draft_plan`,
  `route_plan`, then `save_plan`);
  `PATCH /api/plans/{plan_id}` → `{order: [...], drop: [...]}` via
  `validate_order` + `drop_steps`;
  `POST /api/plans/{plan_id}/run` → weave + pin, writing `set_step_status` as it
  goes;
  `GET /api/plans/{plan_id}` → the card's poll target.
  Keep `POST /api/threads/{id}/run` as plan-then-run for Direct mode.
- **`helix/usage.py`**: `estimate_plan_cost(plan, routes) -> float` summing
  per-lane token and image estimates through the existing `estimate_usd`
  (`usage.py:55-66`). This is what makes ACCEPTANCE's "cost before commit"
  invariant (`UX_FLOWS.md:90`) enforceable rather than aspirational.
- **`web/plan.js`** (new, loaded from `index.html`):
  `renderPlanCard(plan)` — numbered steps, craft badge, lane badge with
  `RouteDecision.reason` as the title attribute, drag handle reusing the
  pointer-capture pattern from `app.js:94-114`, per-step delete, `Run plan`
  button, cost line, per-step status pill fed by polling `GET /api/plans/{id}`.
  `web/app.js:116-125` starts rendering `m.plan` instead of discarding it.

### W3 — Pick grid (G9)
- **Protocol bump to `conductor-plan/2`**, additive and backward-compatible:
  optional `steps[].variants = {"count": 1..8, "directions":
  [{"label", "rationale"}]}`. `parse_plan` accepts both protocol strings
  (`PLAN_PROTOCOLS` tuple replacing the single `PLAN_PROTOCOL` check at
  research `:381`) and validates `len(directions) == count`. The planner writes
  the rationales in the **same call** that drafts the plan, so the "one-line
  rationale per variant" in `FEATURE_MATRIX.md:69` costs nothing extra; add the
  block to `prompts/planner.md` under "Laws of the plan".
- **`helix/weave.py`**: `fan_out(step) -> tuple[Step, ...]` expanding a variant
  step into `s2#v1..v4` with each direction's label appended to the instruction;
  `run_variants(step, routes, spokes, produced) -> tuple[Artifact, ...]`.
  `weave()` calls `fan_out` and keeps only the *kept* artifact in `produced` —
  downstream `[[s2]]` tokens must resolve to one artifact, so an unresolved pick
  blocks its dependents, which is the correct semantics and needs a
  `WeaveError("step 's3' needs a pick on 's2'")`.
- **`helix/store.py`**: `artifacts` gains `variant_of`, `variant_label`,
  `rationale`; `nodes.meta` carries `{"variants": [ids], "kept": id}`; new
  `keep_variant(node_id, artifact_id)` swapping `nodes.artifact_id` and pushing
  the rest onto the stack — never deleting (`UX_FLOWS.md:91`).
- **`helix/layout.py`** (new): `place(existing, kind, count)` replacing the
  global 3-column `next_board_offset`, laying a 2×2 pick cluster adjacent to its
  source node. Without this the grid scatters across the board.
- **`server.py`**: `POST /api/nodes/{id}/keep {"artifact_id"}`.
- **`web/pick.js`**: `renderPickGrid(node)` 2×2 with rationale captions,
  `Tab`/arrows cycling focus, `Enter` keeps, `K` keep-and-continue (posts a new
  plan whose first step is a `refine-image` needing the kept artifact),
  `variant stack` disclosure on the kept node.
- Tests: `test_fan_out_expands_and_labels`, `test_pick_blocks_dependents`,
  `test_keep_variant_never_deletes`, `test_plan_v1_still_parses`.

### W4 — Brand kit as acceptance criteria (G6)
- **`helix/brand.py`** (new): `compile_brand(kit) -> tuple[str, ...]` turning
  the project kit into imperative constraint strings ("use only #0c0d10,
  #f4f1ea, #d4a373, #7c9a92", "voice: quiet, precise, editorial") and
  `brand_acceptance(kit) -> tuple[str, ...]` turning the same kit into
  checkable acceptance lines.
- Adapter merges those into `Brief.constraints` before `_draft_plan`, so
  `format_brief_block` (research `:609-623`) carries them into the planner
  prompt *and* `build_step_prompt` restates them per step (research `:712-721`)
  — which is the whole point: `prompts/planner.md` law 3 already requires every
  instruction to restate the constraints it binds, so the palette reaches the
  image model instead of dying in a system prompt.
- Delete `_brand_block` and its 1,200-char truncation.
- Test: `test_brand_palette_reaches_every_image_step_prompt`.

**End-of-week state.** Plan card visible, steps reorderable and droppable with
validation, four variants with rationales and a keep action, malformed planner
replies retried once and then loudly failed, provider outages named on the node
instead of disguised as art, brand palette present in every step prompt,
multi-asset briefs composing through tokens. Tests: 36 ported + ~14 new.
Still missing and *known* missing: refine-by-reference, mend-on-board,
real lanes.

---

## 3. One-month close: the conversational loop and the honest lanes

Month scope is G4, G5, G7 plus the enablers and the eval harness that makes the
ACCEPTANCE numbers assertable instead of decorative. Ordered by dependency.

### M1 — Spoke attachments (E1, E3) — gates M2 and M3
- **`spokes/base.py`**: `@dataclass Attachment(mime, data)`; extend
  `Spoke.chat(messages, model, *, attachments=(), expect="text")`.
- **`openai_spoke.py:49-55`**: build multi-part content with
  `{"type":"image_url","image_url":{"url":"data:<mime>;base64,<...>"}}`; set
  `response_format={"type":"json_object"}` when `expect == "json"`.
- **`gemini_spoke.py:49-66`**: append `inlineData` parts to the last user
  content; set `generationConfig.responseMimeType = "application/json"` for
  json.
- Fixture tests reusing `research/fable5/03-keyring-spokes/tests/fixtures/` —
  assert the request body shape, not the network.

### M2 — Context ledger and referring expressions (G4)
- **`helix/ledger.py`** (new). Schema: `entities(id, project_id, node_id, name,
  aliases_json, kind, last_turn)`. `register_entity(node, name, kind)` called
  from `_pin_to_board` — the planner's `emits.name` ("logo-mark", "hero-poster")
  is already a human-usable entity name, which is the quiet payoff of the
  research envelope.
- `resolve(phrase, project_id, selection) -> Resolution(node_id, confidence,
  why, candidates)`, deterministic layers first so it is unit-testable offline:
  1. explicit selection wins (`UX_FLOWS.md:93`, "selection is the context");
  2. exact/alias name match;
  3. `parse_ordinal(phrase)` + deliverable-word scan reusing
     `DELIVERABLE_WORDS` (research `:233-244`) → "the second poster";
  4. recency tiebreak within matching kind;
  5. ambiguity → return top-3 `candidates`, no edit fires.
  Only if all five fail, one `openai`-lane call over a ledger digest.
- **`server.py`**: `POST /api/threads/{id}/run` accepts `selection: [node_id]`
  and returns `resolution` **before** executing, so `web/app.js` draws the
  "→ Logo v3" chip on the user's own message — the spec requires the target
  visible before the edit lands (`UX_FLOWS.md:39`), which means the resolve step
  must be its own round trip: `POST /api/threads/{id}/resolve` →
  `{resolution, pending_edit_id}` → `POST /api/edits/{id}/confirm`.
- Edits compile to a `refine-image` step whose `needs` carries the resolved
  artifact, so `route_plan` rule 1 sends it to the `image` lane with the source
  attached, and the result lands as a revision in the node's variant stack
  (`store.py::push_revision`) rather than as a new node.
- **`tests/test_referring.py`**: the 20 scripted follow-ups from ACCEPTANCE M-2
  line 23, asserting ≥18/20 correct resolution and that every `Resolution`
  carries a non-empty `why`.

### M3 — Critic mend reaching the board (G5)
- Adapter `_pin_to_board` branches on `Artifact.revision > 0` →
  `push_revision(node_id, artifact_id)` instead of a fresh node, so a mend
  visibly replaces the flagged asset and the old one stays in the stack.
- **`helix/checks.py`** (new): deterministic pre-critic checks whose results are
  injected as machine-verified notes, so colour verdicts are facts not taste —
  `palette_delta_e(image_bytes, palette) -> float` (closes ACCEPTANCE M-5's
  ΔE ≤ 10 benchmark), `contrast_ratio`, `dimensions_match`.
- **`web/critique.js`**: `renderCritique(notes)` with blocker/advisory badges
  bound to the node they name, and a per-note `Mend` button posting
  `POST /api/plans/{id}/mend {"notes": [...]}` — user-triggered mend, in
  addition to the automatic pass, because the research contract deliberately
  allows only one automatic mend (PROTOCOL.md §"Mend semantics").
- Point `critic_spoke` at the `gemini` lane when the handoff contains images
  (ROUTING.md §"Where the planner and critic run") — one line in `lanes.py`
  once M1 lands.

### M4 — Real three-lane routing (G7)
- `keyring.py` and `lanes.py` grow per-lane provider preference so a run can
  hold OpenAI for text, Gemini for reading, and a third for images
  simultaneously — today `server.py:207` passes one `provider` string for the
  whole run and `index.html:56-61` offers one dropdown.
- Pre-flight row in the UI (`UX_FLOWS.md:43`): auto-picked lane per step with
  the `RouteDecision.reason` visible and an override dropdown, plus
  `estimate_plan_cost` from W2. Nothing fires until the cost is on screen.
- `LONG_SOURCE_CHARS` (research `:72`) and `FAST_STEP_BUDGET` become settings,
  not constants, once real briefs start hitting them.

### M5 — Manifest, provenance, export (E2)
- Wire research `pin` (`:785-878`) to write `manifest.json` per run beside the
  existing artifact files (`loom.py:31-44`), and surface it at
  `GET /api/runs/{id}/manifest`.
- Engine + revision chip on every node from `manifest.plan.steps[].spoke`
  (closes M-3 line 26); XMP-embedded provenance on export (M-6 line 70) reads
  the same manifest.
- `usage.py`: per-turn ledger view joining `usage_events.thread_id` to the run,
  closing M-6's "engine, action, cost" per-turn history.

### M6 — Documentation truth-up
- PROTOCOL.md gains a `conductor-plan/2` section (variants) and a mend-trigger
  note for user-initiated mends. ROUTING.md gains the per-lane-key story.
- `atelier/ARCHITECTURE.md:42` currently advertises "an explicit JSON plan
  schema, a hard weave cap (4), and demo fallback so a missing key never blanks
  the board." After this work two of those three claims change meaning: the
  schema becomes enforced, and the demo fallback becomes a *named stand-in*
  rather than an invisible one. The line should say so.

---

## 4. What I would not do

- **Do not evolve the live flat plan dict toward the research schema
  incrementally.** The research module is 1,075 lines of already-passing code;
  incremental convergence means maintaining two schemas and re-deriving 22
  validation rules by hand. Transplant, adapt, delete.
- **Do not keep the silent demo-SVG fallback.** It is the single most corrosive
  behavior in the live code: it makes a quota failure indistinguishable from a
  design decision. A named stand-in node with a "no key for this lane" caption
  costs nothing and is honest.
- **Do not ship the pick grid before the plan card.** The grid is the more
  demoable feature and the less load-bearing one; a grid with no visible plan is
  a variant picker, not an agent.
- **Do not implement referring expressions LLM-first.** Four of the five
  resolution layers are deterministic and therefore testable against
  ACCEPTANCE's 20-case set. A model-first resolver cannot be held to a ≥90% bar
  offline, and that bar is the only reason the feature is trustworthy enough to
  auto-apply.
