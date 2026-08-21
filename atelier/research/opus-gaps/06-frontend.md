# Frontend Gaps — live `atelier/web/` vs. research `06-board-ui/` and `01-product-spec/UX_FLOWS.md`

Opus#6 of 10. Read-only analysis; `/workspace` unmodified.

**Recommendation up front: promote the research UI.** Replace `atelier/web/` with
`research/fable5/06-board-ui/`, rewrite its ~70-line `RemoteBackend` adapter against the live
Helix API, delete its localStorage demo backend, and add nine server endpoints. Incrementally
upgrading the live UI means rewriting the research app's canvas layer from scratch, worse, for
comparable effort. Detail in §4; the API additions are enumerated in §5.

---

## 1. What each side actually is

| | live `atelier/web/` | research `06-board-ui/` |
|---|---|---|
| Size | 221 JS + 81 HTML + 97 CSS = 399 lines | 1,469 JS + 249 HTML + 878 CSS = 2,596 lines + 290-line spec |
| Backend | hard-wired to the live Helix API | `RemoteBackend` / `LocalBackend` behind one interface, chosen by a `GET /api/health` probe |
| Board | absolutely positioned nodes in a clipped div | camera-transformed world with pan/zoom/fit |
| Chat | blocking POST, full re-render after | SSE token streaming with a thinking channel |
| Wired to live `/api`? | yes | no — `README.md:35` says so explicitly |

The live app is a working thin client for a real backend. The research app is a finished studio UI
in front of a backend that doesn't exist yet. Neither is the product; the product is the research
UI's front half joined to the live app's back half.

---

## 2. Gap-by-gap

Severity: **P0** blocks a documented MVP flow · **P1** breaks a spec invariant or acceptance
criterion · **P2** quality/polish.

### 2.1 Pan / zoom — P0, live has none

Live has no camera at all. `.board` declares `transform-origin: 0 0` (`web/styles.css:74`) but
nothing ever writes a transform, and `.board-wrap` is `overflow: hidden` (`web/styles.css:67`), so
there is no scrolling either. Meanwhile the conductor lays nodes out on a fixed 3-wide grid at
`72 + col*360, 72 + row*280` (`helix/conductor.py:70-73`). Past roughly the tenth node, generated
artifacts land below the fold and become permanently unreachable — the user cannot scroll, zoom, or
pan to them. This is not a missing convenience; it is silent data loss from the user's point of
view, and it contradicts the "infinite spatial canvas" that `FEATURE_MATRIX.md:55` puts in MVP.

Research implements the full model: camera `{x, y, scale}` clamped 0.2–2.5, wheel zoom toward the
cursor with a steeper curve under `ctrl` for pinch, background/middle-mouse/`Space`+drag panning,
fit-to-bounding-box with 80px padding, and a zoom HUD that resets on click
(`06-board-ui/app.js:467-516`, `681-758`). The dot grid's `background-size`/`background-position`
track the camera so the grid pans and zooms with content (`app.js:470-471`).

### 2.2 200 nodes at 60 fps — P1, neither passes; research is an order of magnitude closer

`ACCEPTANCE.md:13` requires ≥200 asset nodes at 60 fps pan/zoom on a mid-range laptop.

Live fails structurally, on four counts:

- `refreshBoard()` does `board.innerHTML = ""` and rebuilds every node (`web/app.js:75-76`), and
  `bootProject()` calls it after every conductor run and every project switch
  (`web/app.js:142-153`, invoked at `206`). Each turn destroys and rebuilds the whole board.
- Every card gets three of its own pointer listeners (`web/app.js:94-114`) — 600 listeners at 200
  nodes, no delegation.
- Dragging writes `style.left`/`style.top` (`web/app.js:106-107`), forcing layout on every
  pointermove instead of staying on the transform path.
- Each image node is an `<img src="/api/artifacts/{id}">` with no `loading="lazy"` and no
  `decoding="async"`, and `_send_file` reads the whole artifact into memory and emits no `ETag`,
  `Last-Modified`, or cache header (`server.py:77-91`). Every rebuild re-downloads all N artifacts.

Research is architecturally right — one transform on `#world` for the whole camera, node moves via
`transform: translate()` (`app.js:594`), a single delegated pointer listener set on the viewport
(`app.js:681-752`), debounced persistence (`app.js:628-630`), and a full rebuild only on project
load (`app.js:600-611`). But it still won't hold 200 nodes at 60 fps without three additions it
doesn't have: no viewport culling or `content-visibility` (200 live DOM subtrees, each with
`box-shadow`, always painted), no `will-change` hint on `#world`, and `backdrop-filter: blur()` on
the toolbar and drop overlay (`styles.css:195`, `284`) which forces a full-viewport backdrop
re-composite on every pan frame. Treat the acceptance criterion as unmet by both and budget culling
work regardless of which path is chosen.

### 2.3 Upload / drop — P0, live cannot ingest a file at all

The live UI has no file input, no drag handlers, and no upload endpoint — `index.html` contains no
`<input type="file">`, `app.js` registers no `drop` listener, and `server.py:159-219` has no
`/api/uploads` route. A user cannot bring a reference image into the studio by any means. That
blocks `UX_FLOWS` Flow 2.1 (attach files as per-turn references) and all of Flow 4's reference-led
refinement.

Research has the whole flow: depth-counted `dragenter`/`dragleave` so child elements don't flicker
the overlay, drop-point-to-world-coordinate mapping with a +36px cascade per file, type routing
(image → upload then image node, video → placeholder node, anything else → note recording the
filename), and node sizing from the decoded image's aspect ratio clamped 120–480px
(`app.js:774-820`). It depends entirely on `POST /api/uploads`, which does not exist server-side.

### 2.4 SSE streaming — P1, UI is ready, server and spokes are not

Live is fully blocking. `POST /api/threads/{id}/run` runs the entire conductor turn — planner chat,
up to four weave items each up to two images, plus a critic pass in thinking mode
(`helix/conductor.py:82-239`) — and returns one JSON blob. The UI writes `"Conductor weaving…"` and
awaits it (`web/app.js:191-211`). In thinking mode against a real provider that is a static status
line for tens of seconds with no plan, no partial text, and no progressive board painting.

The server has no chunked path at all: `_json` computes `Content-Length` and writes the body once
(`server.py:57-64`). The spokes cannot stream by construction — `Spoke.chat` returns a complete
`ChatResult` (`helix/spokes/base.py:35`) and the Ollama adapter hard-codes `"stream": False`
(`helix/spokes/ollama_spoke.py:39`).

Research's client half is complete and careful: POST with `Accept: text/event-stream`, a
`ReadableStream` reader parsing `\n\n`-delimited frames with multi-`data:`-line joining (so it works
with plain `fetch`, since `EventSource` cannot POST), `thinking.delta` / `message.delta` / `done` /
`error` handling, `[DONE]` honored as terminal, unparseable payloads treated as raw text deltas,
idempotent close when the server ends without a `done` frame, and a non-streaming fallback that
renders `done.message.content` in one shot if no deltas arrived (`app.js:187-226`, `1164-1215`).
Tokens append to a live text node rather than re-rendering the list, and auto-scroll only engages
while the user is pinned within 48px of the bottom (`app.js:1057-1062`).

Two things are missing on the research side too, and they matter more than they look:

- **The SSE contract has no board events.** `UI_SPEC.md:232-256` defines only text deltas plus
  `done`. But the live conductor's entire output is *board nodes and artifacts*. A streamed turn
  under this contract paints text while the canvas stays frozen until a manual refresh. A
  `node.created` event is required, not optional.
- **The chat contract diverges from live.** Research posts `/api/chat` with
  `{thread_id, project_id, message, mode, provider, model}`; live posts `/api/threads/{id}/run` with
  `{prompt, mode, provider, model}` and returns `{plan, artifacts, nodes, message}`.

The streaming spokes already exist in research — `03-keyring-spokes/spokes_{openai,gemini,anthropic}.py`
all handle streams and ship `.sse` fixtures — they simply were never ported into `helix/spokes/`.

### 2.5 Settings eye-toggle — P2 on the toggle, P1 on what surrounds it

Live has one password field in the rail with no reveal control (`web/index.html:34-43`). Three
things around it are worse than the missing toggle:

- Key status renders through `innerHTML` with interpolated server values
  (`web/app.js:130-133`) — the only place the live app puts data into `innerHTML`. Currently safe
  because the keys come from a fixed `ENV_MAP`, but it is a latent injection path.
- The keyring already computes a masked hint, `sk-…abcd` (`helix/keyring.py:99`), and the UI never
  shows it. It renders `provider:source`, so the user cannot tell which key is stored.
- `Keyring.delete()` exists (`helix/keyring.py:82`) but no route exposes it. There is no way to
  remove a key from the UI.

Research gives each provider a row with a reveal button that flips `input.type` and tints the icon
(`app.js:1285-1292`), a `saved …abcd` / `not set` status chip, placeholder text that changes to
"Enter new key to replace" when one is stored, save-only-non-empty semantics, and inputs cleared
after save (`app.js:1259-1312`). Two mismatches against live: research sends `PUT /api/keys` as a
`{provider: rawKey}` map where live takes `POST` one provider at a time with `{provider, key,
base_url}`; and research's provider list (openai/anthropic/google/fal/replicate) doesn't match
live's (`ENV_MAP`: openai/gemini/anthropic/ollama/openai_compat) and drops the `base_url` field that
Ollama and openai-compat hosts require (`web/index.html:38-41`).

### 2.6 StyleLock UI — P1

Live is a raw JSON textarea (`web/index.html:44-48`). `JSON.parse` on save has no `try`/`catch`
(`web/app.js:187`), so malformed JSON throws an unhandled rejection and the save silently does
nothing — no toast, no inline error, no indication the kit wasn't stored.

Research ships the structured editor `UX_FLOWS` Flow 6 describes: palette rows with a native color
input, editable role name, hex readout and remove button; heading/body font fields; a click-or-drop
logo zone routed through the same upload endpoint; a voice textarea; and footer copy stating the kit
is injected into every generation and enforced by the critic (`app.js:1333-1414`,
`index.html:206-238`). That copy is already true of live — the conductor injects the kit into the
planner system prompt (`helix/conductor.py:101`, `260-263`) — so a structured editor is immediately
meaningful rather than aspirational.

Schema and route both diverge: live stores `{name, palette: [hex], voice}` (`server.py:44-49`) at
`POST /api/projects/{id}/brand`; research expects `{colors: [{name, value}], fonts: {heading, body},
logo_url, voice}` at `PUT /api/projects/{id}/brand-kit`. A read-side normalizer is needed.

Still missing on both sides vs. spec: cross-project kit CRUD (`UX_FLOWS` Flow 6 "Workspace → Kits"),
the canvas upper-left kit selector, and per-turn `@`-mention override.

### 2.7 Undo — P1, absent from both, and research is actively worse

`ACCEPTANCE.md:36` requires node-scoped undo of ≥50 steps plus a project snapshot on every agent
turn, restorable in ≤5s. `UX_FLOWS:91` makes "nothing destructive" a cross-flow invariant.

Live has no history — drag commits straight to the server on pointerup (`web/app.js:109-113`) — but
it also has no delete, so nothing can be destroyed.

Research introduces destruction without recovery: `removeNode` drops the node from state, removes
the element, and issues `DELETE` with no tombstone (`app.js:665-672`), reachable from a bare
`Delete`/`Backspace` keystroke with no confirmation (`app.js:858-861`). One mis-keystroke with a
node selected permanently destroys a generated artifact's placement. That is a direct violation of
the invariant and must be fixed before promotion, not after.

Undo cannot be closed client-side alone. The `nodes` table has no version or history columns and
`artifacts` has no parent/variant link (`helix/store.py:36-60`), and `Memory` has no delete method at
all. A client-local command stack covers `x/y/w/h/text` cheaply; anything touching artifacts, plus
turn-level snapshots, needs schema work.

### 2.8 Variant grid — P0 for the flow, absent from both

`UX_FLOWS` Flow 3.3 specifies a Pick grid: variants side by side, each with a one-line rationale,
`Tab`/arrows to cycle, `Enter` to keep, `K` to keep-and-continue, non-kept variants collapsing into
a recoverable variant stack. `FEATURE_MATRIX.md:105` sets the default at 4 in Plan mode, 1 in
Direct, user-adjustable 1–8.

Neither UI has any of it. Research lists it under out-of-scope (`UI_SPEC.md:288-290`). Live's
conductor already generates multiple artifacts per turn — up to 4 weave items × up to 2 each
(`helix/conductor.py:140-143`) — but pins them all onto the board as independent, ungrouped nodes
(`conductor.py:186-197`), and the planner JSON schema has no per-item `rationale` field
(`conductor.py:24-32`). There is no grouping, no rationale, no pick step, no stack.

This is the largest net-new item and it is not a UI-only change: it needs a planner schema field, an
artifact `variant_group`/`parent_id`, a keep/discard endpoint, and only then the grid. Sequence it
last.

### 2.9 Cost before commit — P0 invariant, and live is *ahead* of research

`UX_FLOWS:90` makes it invariant #1: no action consumes credits without the cost having been on
screen. `FEATURE_MATRIX.md:115` puts "credits with pre-generation cost preview" in MVP.

Live shows *cumulative* spend after the fact in the top bar (`web/app.js:149-152`); the Weave button
fires with no estimate. Budget enforcement exists but is the wrong shape for the invariant:
`usage.assert_budget` raises *during* the turn, after the planner call has already spent
(`helix/usage.py:87-95`, called from `usage.record` at `98-109`), and the failure surfaces as a
generic HTTP 500 carrying `str(exc)` (`server.py:210-211`) that the UI drops into a status line
(`web/app.js:209`). There is no machine-readable budget error the UI can render as a limit or
top-up affordance.

Research has *no* cost surface whatsoever — no estimate, no ledger, no budget, no spend meter. On
this gap the live UI is the better starting point and its spend meter must be carried forward.

The building blocks are in place: `usage.estimate_usd` is a pure function over
`(provider, model, unit_kind, units)` (`helix/usage.py:55-66`), and `_default_model`/`_image_model`
(`conductor.py:242-257`) fix the route. The honest complication: true turn cost depends on how many
weave items the *planner* returns, which isn't known until after the planner call. So a faithful
implementation quotes in two stages — quote and confirm the (cheap) planner call, then surface the
returned plan with the (expensive) weave quote and require an explicit **Run plan**. That happens to
match `UX_FLOWS` Flow 2.2c exactly, so the constraint and the spec agree.

### 2.10 Empty states — P1

Live has none. An empty board is a blank dark rectangle; an empty message list is blank; an empty
project list is blank. Nothing tells a first-time user what to do. `UX_FLOWS` Flow 1.3 asks for
three one-click example-brief chips (poster / social pack / product shot) in the empty prompt box.

Research has a board empty-hint with keyboard affordances (`index.html:79-82`), a chat empty state
with a suggested prompt (`index.html:138-141`), bottom-center toasts for every save/failure
(`app.js:32-39`), and seeded demo content so the first paint exercises every node type
(`app.js:244-284`). Remaining vs. spec: the chat suggestion is static text, not clickable chips;
there is no "no projects yet" state because it silently auto-creates one (`app.js:1443-1446`); and
there is no "no keys configured" state, which is the single most likely first-run condition.

### 2.11 Mobile — P2, recommend declaring out of scope

Live has zero media queries (none in `web/styles.css`) against a fixed
`grid-template-columns: 280px 1fr 360px` (`web/styles.css:23`). At a 390px viewport the canvas
column collapses to nothing and the layout overflows horizontally; rail and dock are both unusable.

Research has one query at 860px that only hides top-bar button labels (`styles.css:873-878`).
`--dock-w` drops to 320px, still leaving a phone almost no canvas. There is no touch pinch-zoom —
zoom is wheel-only (`app.js:754-758`); trackpad pinch works because it arrives as `ctrl`+wheel, but
a two-finger pinch on a touchscreen does not, there is no multi-touch pointer handling, and no
`touch-action` declaration anywhere.

Both are desktop-only. Rather than half-supporting phones, declare mobile out of MVP scope
explicitly and ship a small-screen interstitial. `UX_FLOWS` Flow 6 only references mobile in the
context of Lovart's session caps, which Atelier already defers.

### 2.12 Accessibility — P1

**Live.** The one concrete bug worth fixing immediately: the document declares `lang="zh-CN"`
(`web/index.html:2`) while every string in the UI is English, so a screen reader attempts to
pronounce the entire interface in Mandarin. Beyond that: no `aria-live` on the message list, so
streamed or refreshed assistant turns are never announced; board nodes are non-focusable `div`s with
pointer-only drag (`web/app.js:94-114`), making the canvas entirely unreachable by keyboard; native
`alert()` and `prompt()` for the catalog and project naming (`web/app.js:156`, `216`); and no
`:focus` styling defined anywhere in `web/styles.css`. Landmarks are the one bright spot — real
`header`/`aside`/`main`/`section` elements (`index.html:11`, `15`, `50`, `53`).

**Research** is substantially better: `aria-live="polite"` on the message list and toasts
(`index.html:137`, `241`), `role="radiogroup"` with `aria-checked` on the mode toggle
(`index.html:146-151`), `aria-expanded` on the project popover (`index.html:26`, `app.js:885`),
`aria-hidden` tracked on panels, `aria-label` on canvas/dock/panels, `aria-hidden="true"` on
decorative SVGs, `tabindex="0"` on the viewport, and `Escape` closing panels from anywhere
including inside inputs (`app.js:840-848`).

What research still misses, all of which should be fixed as part of promotion:

- Nodes remain keyboard-unreachable. Selection happens only via `pointerdown`
  (`app.js:681-711`); `Delete` acts on the selection, but the selection can never be made without a
  mouse. Needs roving `tabindex` over nodes and arrow-key nudge.
- Closed panels stay in the tab order — they're hidden by class/transform only (`app.js:1242-1245`).
  Needs `inert`.
- Panels neither trap focus while open nor restore focus to the invoking button on close.
- `prompt()` still used for new thread titles (`app.js:996`).
- No `prefers-reduced-motion` block despite transform transitions (`styles.css:703`).
- `--text-3: #626b7f` on `--panel: #14161d` is roughly **3.5:1** — below the 4.5:1 minimum, and it's
  the token used for the mono metadata lines. (`--text-2` at ~7.2:1 is fine.)
- The drop overlay and zoom HUD change state without any announcement.

### 2.13 First run without Python knowledge — P0 for adoption, unaddressed by both

`README.md:5-8` says `python3 -m atelier`. That silently assumes Python 3 installed and on `PATH`,
the repo cloned, the working directory set to the repo's *parent* so `atelier` resolves as a module,
and the user knowing what a module is. There is no `pyproject.toml` and no `setup.py` anywhere in
the tree, so there is no `pip install`, no console-script entry point, and no packaged artifact.
`__main__.py` is a two-line shim to `server.main`. The server binds `127.0.0.1:8765` and prints a
URL (`server.py:225-234`) but never opens a browser.

Research's answer to first-run is its demo backend — but that is *also* a Python instruction
(`UI_SPEC.md:23-28` tells the user to run `python3 -m http.server 8000`), and it stores API keys
base64-obfuscated in localStorage (`app.js:358`), which the spec itself flags as never-for-production
(`UI_SPEC.md:144-146`).

The live app already has the better story for the no-key case and should keep it: the demo *spoke*
weaves real SVG artifacts through the real conductor pipeline at zero quota
(`conductor.py:162-164`, `README.md:20`), so the studio is honest without keys instead of faking a
backend. The gap is packaging and onboarding only: no zero-argument launcher, no browser auto-open,
no in-app "you have no keys, here's what that costs you" state, and no explanation that demo mode is
real.

---

## 3. Summary table

| # | Gap | Live | Research | Spec ref | Sev |
|---|---|---|---|---|---|
| 1 | Pan / zoom | none; content past ~10 nodes unreachable | complete camera | FEATURE_MATRIX:55 | P0 |
| 2 | 200 nodes @ 60fps | fails structurally (full rebuild, per-node listeners, `left/top`) | right architecture, no culling | ACCEPTANCE:13 | P1 |
| 3 | Upload / drop | no input, no handler, no endpoint | complete, needs `/api/uploads` | UX_FLOWS 2.1, 4 | P0 |
| 4 | SSE streaming | blocking; no chunked path; spokes can't stream | client complete; contract lacks board events | UX_FLOWS 2.2c, 3.2 | P1 |
| 5 | Settings eye-toggle | none; hint unused; `innerHTML`; no delete | complete; wrong provider list, no `base_url` | UX_FLOWS 6 | P2 |
| 6 | StyleLock UI | JSON textarea, silent parse failure | structured editor; schema diverges | UX_FLOWS 6 | P1 |
| 7 | Undo | none (but nothing destructive either) | **destructive delete, no recovery** | ACCEPTANCE:36, invariant 2 | P1 |
| 8 | Variant grid | none; conductor pins all variants flat | none (declared out of scope) | UX_FLOWS 3.3 | P0 |
| 9 | Cost before commit | cumulative only; budget raises mid-turn as 500 | **none at all** | UX_FLOWS:90 | P0 |
| 10 | Empty states | none | good; no chips, no no-keys state | UX_FLOWS 1.2–1.3 | P1 |
| 11 | Mobile | zero media queries | one label-hiding query; no touch pinch | — | P2 |
| 12 | A11y | `lang="zh-CN"`, no live region, no keyboard canvas | good ARIA; no keyboard nodes, no `inert`, 3.5:1 text | — | P1 |
| 13 | First run | no packaging, no launcher, no browser open | demo mode is also a Python instruction | UX_FLOWS 1 (≤2 min) | P0 |

Research wins outright on 1, 3, 5, 6, 10, 12 and on the client half of 4. Live wins on 9 and on the
honesty of 13. Both fail 2, 7, 8, 11.

---

## 4. Decision: promote, don't upgrade

**Promote the research UI to `atelier/web/`, rewrite its backend adapter, delete its demo backend.**

### Why not incremental

The two hardest live gaps are architectural, not additive. Closing pan/zoom and 200-node
performance in the live app requires replacing absolute `left`/`top` positioning with a world
transform, replacing per-node listeners with delegation, and replacing full-rebuild refresh with
incremental patching. That is precisely the research app's canvas layer — rebuilt from scratch, by
someone who doesn't have the 290-line spec in their head, at comparable cost and worse quality.
Everything else on the list (drop overlay, slide-over panels, key rows, palette editor, empty
states, ARIA, toasts) would likewise be reimplemented rather than reused. Incremental only wins if
the live UI contains something worth preserving; it contains exactly two such things — the
cumulative-spend meter (`web/app.js:149-152`) and the `base_url` field for Ollama and
openai-compatible hosts (`web/index.html:38-41`) — and both are roughly twenty lines to port
forward.

### Why not promote as-is

Dropping the research app in front of the live server unmodified produces something *worse* than
today's UI. `detectBackend()` probes `GET /api/health`, which the live server answers
(`server.py:113-115`), so the app flips to live mode — and then every subsequent call 404s. Because
`openProject` catches each failure and substitutes an empty array (`app.js:953-957`), the result is
a UI that confidently displays "Live /api" next to a permanently empty board with no error. A
confidently-wrong client is a worse failure mode than a limited one.

Three things must change before it can be promoted:

1. **Rewrite `RemoteBackend`.** `UI_SPEC.md:206-210` anticipated exactly this: "If the final spec
   diverges, only the `RemoteBackend` object in `app.js` (~70 lines) needs edits." That seam is the
   single most valuable property of the research deliverable — the whole promotion hinges on the
   ~80 lines at `app.js:145-227`.
2. **Delete `LocalBackend` entirely** (`app.js:233-422`, ~190 lines). It base64s API keys into
   localStorage, it duplicates a demo mode the server already does better through the real pipeline,
   and it doubles the maintained surface. The live studio's zero-key story is the demo *spoke*, not
   a client-side fake. Keep the connection pill; make it a genuine error state rather than a
   fallback.
3. **Reconcile the node model server-side, not client-side.** Research uses
   `node.data.{text, src, title}`; live stores flat columns `text`, `artifact_id`, `meta`
   (`helix/store.py:48-60`). Normalize in the server — one place, and the store has to grow for undo
   and variants anyway.

Plus the two pre-promotion correctness fixes: make node deletion recoverable (§2.7) and carry the
spend meter forward (§2.9).

---

## 5. API to add

Live routes today: `GET /api/{health, keys, projects, catalog, usage}`,
`GET /api/projects/{id}[/threads|/board]`, `GET /api/threads/{id}/messages`,
`GET /api/artifacts/{id}`, `POST /api/{keys, projects}`, `POST /api/projects/{id}/{threads,brand}`,
`POST /api/threads/{id}/run`, `POST|PATCH /api/nodes/{id}` (`server.py:98-222`).

### Stage A — parity: make the promoted UI work at all

| Endpoint | Status | Notes |
|---|---|---|
| `GET /api/projects/{id}/nodes` | alias | Same as existing `/board`. Return `{items: [...]}`; the client's `asList` accepts either shape (`app.js:143`). |
| `POST /api/projects/{id}/nodes` | route only | `Memory.add_node` exists (`store.py:213`). Flatten `data.text` → `text`, `data.src` → artifact ref. |
| `PATCH /api/nodes/{id}` | **already works** | `do_PATCH` delegates to `do_POST` (`server.py:221-222`). Extend the `update_node` allowlist (`store.py:252`) to accept `data`. |
| `DELETE /api/nodes/{id}` | new | No `do_DELETE` handler exists and `Memory` has no delete. Implement as **soft delete** (`deleted_at`) — see Stage C undo. |
| `POST /api/uploads` | new | Multipart. No multipart parsing exists anywhere; `cgi` is gone in 3.13, so use `email.parser` or a small boundary splitter. Store as an artifact with `kind="upload"`, return `{id, url: "/api/artifacts/{id}", kind}`. **Also fix `_send_file`**: it forces `Content-Disposition: attachment` and names everything `.bin` (`server.py:148`), so `<img>` tags trigger downloads instead of rendering. Serve artifacts inline with a real filename and cache headers. |
| `GET /api/providers` | new | Trivial: derive from `Keyring.ENV_MAP` plus the model names already hard-coded in `_default_model`/`_image_model` (`conductor.py:242-257`). |
| `PUT /api/keys` | extend | Accept the `{provider: rawKey}` map form alongside today's single-provider `POST`. Keep per-provider `base_url`. Expose `Keyring.delete` (`keyring.py:82`) as `DELETE /api/keys/{provider}`. |
| `GET`/`PUT /api/projects/{id}/brand-kit` | new | Map onto existing brand storage; normalize legacy `{palette: [hex]}` → `{colors: [{name, value}]}` on read. Keep `POST /brand` as an alias. |

Client-side in the same stage: adapt to the live keys shape (`{configured, source, base_url, hint}`
vs. the assumed `{set, hint}`), restore the `base_url` input, and correct the provider list to
openai / gemini / anthropic / ollama / openai_compat.

### Stage B — streaming and cost (the two P0 invariants)

| Endpoint | Notes |
|---|---|
| `POST /api/chat` (SSE) | Needs three things, in order: (1) a chunked-transfer path in `Handler` — `_json` currently sets `Content-Length` and writes once (`server.py:57-64`); (2) streaming spokes — port `03-keyring-spokes/spokes_{openai,gemini,anthropic}.py`, which already stream and ship `.sse` fixtures, into `helix/spokes/`; (3) a generator form of `Conductor.run` that yields events instead of returning a dict. Keep `/threads/{id}/run` as the non-streaming path — the client already falls back correctly when `done` carries full content with no deltas (`app.js:1190-1194`). |
| SSE events beyond `UI_SPEC` §7.1 | `node.created` — **required**, or the canvas stays frozen through a streamed turn (§2.4). `plan` — carries the planner JSON so Plan mode can render the editable plan card (`UX_FLOWS` 2.2a). `usage` — running cost during the turn. |
| `POST /api/estimate` | `{provider, model, mode, weave_count}` → `{items: [{unit_kind, units, usd}], total_usd, budget_remaining_usd}`. Pure wrapper over `usage.estimate_usd` (`usage.py:55`). |
| Budget error shape | `usage.BudgetExceeded` must surface as a distinct code (HTTP 402 or `{error_code: "budget_exceeded", limit_usd, spent_usd}`), not today's generic 500-with-string (`server.py:210-211`), so the UI can render a limit affordance instead of a status line. |

Two-stage confirmation belongs here: quote and run the cheap planner call, surface the returned plan
with the weave quote, require explicit **Run plan** before spending on images. This satisfies
invariant #1 and `UX_FLOWS` Flow 2.2c with the same mechanism.

### Stage C — undo and variants (store changes; sequence last)

| Change | Notes |
|---|---|
| `nodes.deleted_at` | Makes `DELETE` recoverable and satisfies "nothing destructive". Blocks nothing else — do it in Stage A. |
| `snapshots` table | One row per conductor turn; satisfies `ACCEPTANCE.md:36`'s project-level half. Client-local command stack covers the node-scoped half for `x/y/w/h/text`. |
| `artifacts.variant_group` + `parent_id` | `store.py:36-47` has neither. Prerequisite for the Pick grid. |
| `weave[].rationale` in the planner schema | `conductor.py:24-32` has no rationale field; `UX_FLOWS` 3.3 requires a one-line rationale per variant, and `FEATURE_MATRIX.md:69` notes it is free in the same planner call. |
| `POST /api/variants/{group}/keep` | Keep-one / collapse-rest, non-destructive. |

Only after all of that does the Pick grid become a UI task.

---

## 6. Sequencing

1. **Pre-promotion fixes to the research app**, in place: soft-delete + undo for node removal
   (§2.7), `lang` correction, `inert` on closed panels, keyboard-reachable nodes, contrast token
   bump, `prefers-reduced-motion`, replace `prompt()` (§2.12).
2. **Stage A** server work + `RemoteBackend` rewrite + `LocalBackend` deletion + spend-meter and
   `base_url` port-forward. At this point the promoted UI is live-wired and strictly better than
   today's on gaps 1, 3, 5, 6, 10, 12.
3. **Stage B**: streaming spokes, chunked responses, `node.created`, estimate endpoint, two-stage
   confirmation. Closes gaps 4 and 9.
4. **Perf pass**: viewport culling, `content-visibility`, drop `backdrop-filter` from the toolbar,
   lazy/async images, artifact cache headers. Then measure against `ACCEPTANCE.md:13` — gap 2 is not
   closed until it is measured.
5. **Stage C**: store changes, then the variant grid. Closes gaps 7 and 8.
6. **Packaging** (gap 13): `pyproject.toml` with a console-script entry point, `webbrowser.open` on
   boot, and a no-keys empty state that explains demo mode is real rather than a fallback. This is
   independent of everything above and can run in parallel.

Mobile (gap 11) is recommended out of MVP scope with a small-screen interstitial.
