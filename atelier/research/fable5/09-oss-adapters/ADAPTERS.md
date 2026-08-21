# ADAPTERS.md — How Atelier integrates OSS without vendoring monorepos

Atelier is an AI design-agent canvas (Lovart-style): a chat-driven planner that manipulates
a layered 2D scene, backed by pluggable image/LLM providers. This document defines, per
upstream project, **what pattern we take**, **what we explicitly do not vendor**, and the
**license situation** that dictates the integration boundary.

License facts below were verified August 2026. Re-verify before any release; several of
these projects have changed licenses before and may again.

---

## Cross-cutting rules

1. **Patterns over packages, packages over vendoring, vendoring never for monorepos.**
   We adopt architectures and data-model ideas freely (ideas are not copyrightable);
   we take permissively licensed libraries as pinned dependencies (pip) when they pull
   their weight; we never copy source trees into our repo.
2. **Process boundary for copyleft.** GPL projects (ComfyUI) are integrated only as
   separate processes spoken to over HTTP. No linking, no imports, no code copying.
   Their workflow/config JSON is data, not code, and does not propagate the license.
3. **Ideas only for non-OSI licenses.** tldraw (tldraw license, production license key
   required) and Open WebUI (BSD-3 + branding clause) contribute *design ideas and UX
   patterns only*. Zero lines of their code, assets, or branding enter Atelier.
4. **Zero-npm MVP.** The MVP frontend is plain ES modules served statically — no
   `package.json`, no bundler, no `node_modules`. All canvas-library value (tldraw,
   excalidraw, fabric, konva) is captured as re-implemented patterns in ~500 lines of
   vanilla JS (see `stubs/js/`). If we ever outgrow that, the permissive escape hatch
   is a single vendored UMD build of konva or fabric (both MIT) — still zero-npm.
5. **The OpenAI chat-completions schema is the lingua franca.** Every LLM/image
   provider is reached through an adapter that speaks it; this is the single most
   valuable LiteLLM lesson and lets us defer the LiteLLM dependency itself.

## Summary table

| Project | License (verified 2026) | What we take | Integration form | MVP? |
|---|---|---|---|---|
| LiteLLM | MIT (core; `enterprise/` dir is commercial) | Router/fallback/cost patterns; OpenAI schema as interface | Pattern now; optional pip dep later | Pattern: yes |
| tldraw | **tldraw license** (source-available, license key in prod, watermark) | Record store, tools-as-state-machines, sync ideas | **Ideas only, never code** | Ideas: yes |
| excalidraw | MIT | Scene JSON schema, element versioning, fractional-index z-order | Pattern (re-implemented) | Yes |
| ComfyUI | GPL-3.0 | Node-graph workflow execution for local image gen | **Out-of-process worker over HTTP** | No (optional) |
| fabric.js | MIT | Object model, serialization shape | Pattern (re-implemented) | Yes |
| konva | MIT | Multi-canvas layers, color-buffer hit testing, batched draw | Pattern (re-implemented) | Yes |
| Open WebUI | BSD-3-Clause-OpenWebUI variant (branding clause ≥ v0.6.6) | Key UX flows (model selector, keys admin, artifacts) | **UX patterns only, no code/assets** | Yes |
| Instructor | MIT | Pydantic-schema extraction + validation-feedback retry loop | Pattern now; optional pip dep later | Pattern: yes |
| Outlines | Apache-2.0 | Constrained decoding for guaranteed-valid plan JSON | Optional pip dep, self-hosted models only | No (future) |

---

## 1. LiteLLM — provider gateway patterns

**What we take (pattern).**

- **One call signature, many providers.** A single `complete(model, messages, ...)`
  entry point; the model string (`"anthropic/claude-…"`, `"openai/gpt-…"`) selects the
  provider adapter. Callers never import provider SDKs.
- **Router with fallback chains.** Ordered fallback lists per logical model alias
  (`"planner" -> [primary, fallback1, fallback2]`), retry with exponential backoff on
  429/5xx, cooldown for failing deployments.
- **Cost/usage accounting at the gateway.** Token counts and per-model unit prices are
  recorded at the single choke point, not scattered through the app.
- **OpenAI-compatible schema as the wire format.** Rather than N SDKs, one HTTP client
  that speaks `/v1/chat/completions` covers OpenAI, Azure, Anthropic (via compat
  endpoints or a proxy), Ollama, vLLM, OpenRouter, and LiteLLM's own proxy.

**What we do NOT vendor.**

- The LiteLLM repo (a large monorepo: proxy server, admin UI, DB migrations,
  enterprise features). We do not copy `litellm/` source. Note the repo's
  `enterprise/` directory is under a **commercial** license — one more reason never
  to vendor from that tree.
- The LiteLLM proxy as a required piece of MVP infrastructure. It remains an
  *optional* deployment: because our adapter speaks OpenAI-compatible HTTP, pointing
  `base_url` at a LiteLLM proxy is a config change, not a code change.

**License.** MIT for the core library (`litellm` on PyPI). The `enterprise/`
subdirectory of the repo is commercially licensed — irrelevant when consuming the PyPI
package, fatal if someone vendored the repo wholesale.

**Seam.** `stubs/python/llm_gateway.py` — `Provider` protocol, stdlib-only
`OpenAICompatProvider`, and `Router` with fallbacks + cost hook. Later, `pip install
litellm` and add a ~10-line `LiteLLMProvider` behind the same protocol.

---

## 2. tldraw — store and interaction architecture (ideas only)

**What we take (pattern).**

- **Everything-is-a-record store.** The entire document (shapes, pages, camera,
  presence) lives in one flat keyed store of typed records; the UI is a pure function
  of the store; changes flow through the store, never around it. This makes
  undo/redo, persistence, and multiplayer all fall out of one mechanism.
- **Change-set subscriptions.** Listeners receive `{added, updated, removed}` diffs
  rather than "something changed", enabling cheap incremental rendering.
- **Tools as explicit state machines.** Select/draw/pan are states with `onPointerDown/
  Move/Up` transitions, not `if`-tangles in one event handler.
- **Undo via inverse patches**, captured at the store boundary (a "mark" API for
  grouping user-level operations).

**What we do NOT vendor.**

- **Any tldraw source code, at any version.** The current SDK is source-available
  under the tldraw license: production use requires a license key, hobby use requires
  a visible "made with tldraw" watermark, and the license prohibits interfering with
  key validation. Copying even fragments would import those obligations and
  contaminate our permissive positioning. (tldraw 1.x is MIT and early 2.x betas were
  Apache-2.0, but cherry-picking from abandoned versions of a React-coupled codebase
  is worthless to a zero-npm vanilla app — we take the architecture, not the code.)
- The React dependency chain that tldraw implies. Incompatible with zero-npm anyway.

**License.** tldraw license — source-available, **not** open source (their own docs say
so). Free in development only; trial/commercial/hobby license keys gate production.
Their examples/starter kits are MIT, but we deliberately take nothing, to keep the
provenance story clean: *ideas from documentation and talks, zero code*.

**Seam.** `stubs/js/store.js` — a ~120-line vanilla-JS record store with change-set
listeners and inverse-patch history.

---

## 3. excalidraw — scene format and sync-friendly elements

**What we take (pattern).**

- **A boring, documented scene JSON format.** Excalidraw's `.excalidraw` file
  (`{type, version, elements[], appState, files}`) proves that a flat element array
  plus a small app-state object is enough for a real editor. Atelier defines its own
  `.atelier.json` with the same shape philosophy: flat, versioned, forward-readable.
- **Per-element `version` + `versionNonce` + `isDeleted`.** Monotonic version counter
  with a random nonce as tiebreaker gives last-writer-wins merging without a CRDT
  library; deletion as tombstone keeps merges convergent. This is the cheapest
  credible path to collaboration later.
- **Fractional-index z-order.** Element order is a string key (`index`) generated
  *between* neighbors, so reordering one element touches one record — critical for
  sync and for undo granularity.
- **Files-by-hash.** Binary images live in a content-addressed `files` map; elements
  reference `fileId`. We use the same split between scene JSON and blob store.

**What we do NOT vendor.**

- The excalidraw app or `@excalidraw/excalidraw` React package (React + npm, conflicts
  with zero-npm). Not the roughjs hand-drawn renderer — Atelier is a design canvas,
  not a whiteboard; the sketchy aesthetic is off-brand for us.
- excalidraw.com collab server code.

**License.** MIT. We *could* copy code legally (with attribution); we still choose
patterns-only because their code is React-shaped and ours is not.

**Seam.** `stubs/js/scene.js` — element schema, `indexBetween()` fractional indexing,
and a `mergeElement()` LWW reconciler.

---

## 4. ComfyUI — optional local image-generation worker

**What we take (pattern).**

- **The workflow-graph-as-JSON execution model.** A generation job is a declarative
  node graph; Atelier stores its own workflow JSON templates (API format) and fills
  in parameters (prompt, seed, size, input image) at dispatch time.
- **The HTTP job API as the integration contract**: `POST /prompt` to queue, `GET
  /history/{prompt_id}` to poll status/outputs, `GET /view` to fetch result images,
  `POST /upload/image` for inputs, WebSocket `/ws` for progress events (optional —
  polling suffices).

**What we do NOT vendor.**

- **Any ComfyUI Python code.** ComfyUI is GPL-3.0. Importing it, copying from it, or
  shipping it inside Atelier's process would obligate Atelier to GPL-3.0. Instead
  ComfyUI runs as a **separate, user-installed process** (or container) that Atelier
  talks to over localhost HTTP. Communication over a network API between separate
  programs does not create a derivative work; Atelier's license is unaffected.
- Custom-node packs, model weights, or the ComfyUI frontend. Users bring their own
  ComfyUI install; Atelier only needs its URL.

**License.** GPL-3.0. Our workflow JSON files are our own authored data (the API
format is an interface, node names are facts); they carry our license, not GPL.

**Seam.** `stubs/python/comfy_client.py` — stdlib-only client implementing
queue/poll/fetch against a user-provided base URL. Registered as one implementation
of Atelier's generic `ImageProvider` interface, alongside hosted APIs (fal, Replicate,
OpenAI Images). **Not in MVP** — MVP uses hosted APIs; see FUTURE.md for the worker
architecture.

---

## 5. fabric.js / konva — canvas layer and object model

**What we take (pattern).**

- From **konva**: the **multi-canvas layer model** — each logical layer
  (background / artwork / overlay-selection) is its own stacked `<canvas>` element, so
  redrawing selection handles never re-rasterizes the artwork. Also:
  **`batchDraw` / dirty-flag rendering** coalesced into one `requestAnimationFrame`,
  and **color-buffer hit testing** (draw each node in a unique flat color to an
  offscreen canvas; hit test = one `getImageData` pixel read) which gives exact
  hit-testing for rotated/complex shapes at O(1) per pointer event.
- From **fabric.js**: the **object model** — every canvas item is an object with
  `left/top/width/height/angle/scaleX/scaleY`, a `render(ctx)` method, and
  `toObject()/fromObject()` symmetric serialization; groups are objects containing
  objects; interactive transform controls (handles, rotation) operate on the object's
  transform matrix, not on pixels.

**What we do NOT vendor.**

- Neither library's source tree or npm package in MVP (zero-npm). Their capability
  surface (filters, animation tweens, framework bindings, SVG parsing) is far beyond
  MVP needs; the ~15% we need is re-implemented in `stubs/js/`.
- **Escape hatch, explicitly permitted:** if custom canvas code becomes the
  bottleneck, vendor *one file* — the prebuilt `konva.min.js` or `fabric.min.js` UMD
  bundle with its MIT header retained — served statically. That is a single-file
  vendored artifact of an MIT library, not a monorepo, and preserves zero-npm.

**License.** Both MIT.

**Seam.** `stubs/js/renderer.js` — `Layer` (one canvas each), `Renderer`
(dirty/batchDraw), and `HitCanvas` (color-picking).

---

## 6. Open WebUI — key UX patterns (patterns only, no code)

**What we take (pattern).** The UX decisions that made Open WebUI the default
self-hosted AI frontend:

- **Model selector in the composer, not in settings.** Switching model/provider is a
  one-click dropdown at the point of typing, with per-conversation override.
- **Bring-your-own-key onboarding.** First-run screen asks only for a base URL + API
  key, validates with a live test call, stores server-side; multiple named provider
  connections can coexist and be toggled.
- **Admin/user separation for keys**: server-level provider keys set by an admin,
  per-user keys optional — Atelier copies this two-tier key model.
- **Artifacts panel**: generated outputs render in a side panel bound to the chat
  turn that produced them, with version history per artifact — this maps directly to
  Atelier's canvas-generation history rail.
- **Chat-turn affordances**: regenerate, edit-and-resubmit, copy, and per-turn model
  attribution ("which model made this") — essential in a multi-provider app.

**What we do NOT vendor.**

- Any Open WebUI code (Svelte frontend or Python backend), CSS, icons, or branding.
  Since v0.6.6 (April 2025) the license is a BSD-3-Clause variant with a **branding
  protection clause** (SPDX: `BSD-3-Clause-OpenWebUI`): deployments may not remove or
  alter "Open WebUI" branding except under narrow exemptions (≤50 users/30 days,
  written permission, or enterprise license). Reusing their code while presenting an
  "Atelier" brand is exactly the scenario the clause targets. UX *patterns*
  (layouts, flows, interaction ideas) are not copyrightable and are fair game.

**License.** BSD-3-Clause-OpenWebUI variant (v0.6.6+); code up to v0.6.5 remains plain
BSD-3. We take neither — patterns only.

**Seam.** None (product/design guidance, not code). Feeds Atelier's settings and chat
UI specs.

---

## 7. Instructor / Outlines — reliable plan JSON

Atelier's core loop is: user intent → LLM → **plan JSON** (a typed list of canvas
operations) → executor. Malformed plans are the #1 reliability risk.

**What we take (pattern).**

- From **Instructor**: **schema-first extraction with a validation-feedback retry
  loop.** Define the plan as a schema (Pydantic in the full build); on parse/validation
  failure, re-prompt the model *with the validation errors appended*, up to N retries.
  This one trick converts most malformed outputs into valid ones at the cost of one
  extra call. Also: `Maybe`-style graceful degradation (return "couldn't plan" as data,
  not as an exception into the UI).
- From **Outlines**: **constrained decoding** — compile the JSON schema to a
  regex/grammar mask applied at token-sampling time, making invalid JSON *impossible*
  rather than merely retried. Only applicable when we control decoding (self-hosted
  open-weights models via vLLM — which has `guided_json` built in — or
  llama.cpp grammars).

**The fallback ladder Atelier implements** (each rung behind the same seam):

1. Provider-native structured outputs (`response_format: json_schema`, tool calls) —
   OpenAI/Anthropic-class hosted models.
2. JSON mode + Instructor-style validate-and-retry-with-errors.
3. Fence extraction + tolerant repair (trailing commas, smart quotes) + validate.
4. (self-hosted only) Outlines/vLLM constrained decoding — guarantees rung 2/3 never
   trigger.

**What we do NOT vendor.**

- Neither repo's source. Both are clean pip dependencies when wanted. MVP ships with
  **stdlib-only** validation (the plan schema is small enough for a hand-rolled
  validator, see stub) so `pydantic`+`instructor` remain optional. Outlines and its
  heavyweight friends (torch, vLLM) are strictly future/self-hosted-tier deps —
  never imported in the default install.

**License.** Instructor: MIT. Outlines: Apache-2.0 (patent grant included — good).

**Seam.** `stubs/python/plan_schema.py` — plan schema, stdlib validator, and
`extract_plan()` implementing the ladder with error-feedback retries.

---

## Dependency policy summary

- **MVP Python deps:** stdlib + (already-chosen web framework). `litellm`,
  `instructor`, `pydantic` are *upgrades*, adopted only when the stub seams prove
  limiting. `outlines` only in a self-hosted-model extra (`pip install atelier[local]`).
- **MVP JS deps: none.** No npm, no bundler. Vanilla ES modules implementing the
  store/scene/renderer patterns above. Single-file UMD vendoring of konva or fabric
  (MIT) is the sanctioned escape hatch.
- **Never in-process:** ComfyUI (GPL-3.0), Remotion (paid company license — see
  FUTURE.md), anything tldraw-licensed.
- **Attribution file:** ship `THIRD_PARTY_NOTICES.md` listing every adopted pattern's
  inspiration and every actual dependency's license text once dependencies exist.
