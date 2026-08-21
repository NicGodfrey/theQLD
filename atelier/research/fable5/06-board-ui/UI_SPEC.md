# Atelier Board UI — Specification

Deliverable of Fable5#6 (board UI). Companion files: `index.html`, `app.js`, `styles.css`.

Atelier is an AI design studio (Lovart-class). This deliverable is the **board surface**: an
infinite canvas where project assets live as draggable nodes, plus a docked chat for talking
to **Helix**, the orchestration engine. Zero build step — three static files, vanilla JS,
served by any static file server.

---

## 1. Constraints & goals

| Constraint | Decision |
|---|---|
| No React / no build step | Single `app.js` IIFE, plain DOM APIs, CSS custom properties. No dependencies, no CDN fetches (works offline). |
| Talks to REST `/api/*` | All calls use relative paths so the UI works behind any reverse proxy that mounts the Helix API at `/api`. |
| Must work from `python3 -m http.server` | On boot the app pings `GET /api/health` (1.5 s timeout). If unreachable, it switches to a **localStorage demo backend** with seeded content and simulated token streaming. Every feature stays exercisable. |
| Aesthetic | Dark professional studio: near-black charcoal surfaces, warm brass accent (“studio lamp”), dot-grid canvas, hairline borders, restrained motion. |

Run it:

```bash
cd 06-board-ui
python3 -m http.server 8000
# open http://localhost:8000  → demo mode
# or mount behind the Helix server so /api resolves → live mode
```

---

## 2. Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ TOP BAR   ⟁ Atelier │ [Project ▾]        ● Live/api  Brand kit  ⚙  💬 │ 52px
├──────────────────────────────────────────────────────┬───────────────┤
│                                                      │ CHAT DOCK     │
│  ┌───────┐          INFINITE CANVAS                  │ [Thread ▾] [+]│
│  │TOOLBAR│   dot grid · pan · zoom · nodes           │ ┌───────────┐ │
│  │ note  │                                           │ │ messages  │ │
│  │ upload│      ┌────────┐   ┌──────────┐            │ │ (stream)  │ │
│  │ video │      │ note   │   │ image    │            │ └───────────┘ │
│  │ ───── │      └────────┘   └──────────┘            │ Fast|Thinking │
│  │ + − ⛶ │             ┌──────────────┐              │ [prov][model] │
│  └───────┘             │ video (16:9) │              │ [textarea] ➤  │
│  100% ◎                └──────────────┘              │               │
└──────────────────────────────────────────────────────┴───────────────┘
   zoom HUD                                              380px, collapsible
```

Slide-over panels (Settings, Brand kit) open from the right above everything, with a scrim.
The project switcher is an anchored popover under the project button.

---

## 3. Visual design tokens

Defined once in `:root` of `styles.css`:

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0b0c10` | app + canvas background |
| `--panel` / `--panel-2` / `--panel-3` | `#14161d` / `#191c24` / `#1f232d` | dock, cards, inputs |
| `--border` / `--border-soft` | `#262a35` / `#1e222c` | hairlines |
| `--text` / `--text-2` / `--text-3` | `#e9ebf1` / `#9aa2b4` / `#626b7f` | text hierarchy |
| `--accent` | `#e0a94e` (warm brass) | primary actions, selection rings, streaming cursor |
| `--grid-dot` | `#1b1e26` | canvas dot grid (24 px pitch, scales with zoom) |
| Radii | 12 px panels, 8 px controls | |
| Fonts | system UI stack; `ui-monospace` for metadata/hex/zoom | no webfont download |

Depth comes from a canvas vignette (two faint radial gradients) and soft shadows, not from
bright surfaces. Accent usage is deliberately scarce (≤ 10% of any view) to keep the studio feel.

---

## 4. Components

### 4.1 Top bar
- **Logo** (easel glyph) + **project switcher**: button showing the current project name;
  opens a popover listing all projects (checkmark on current) plus an inline
  “New project name… [Create]” row. Selecting a project reloads board, threads, and brand kit.
- **Connection pill**: green “Live /api” or amber “Demo mode”; clicking retries detection and,
  on success, reloads data from the live backend.
- **Brand kit**, **Settings**, **Chat** toggles.

### 4.2 Infinite canvas
- `#viewport` (fixed, overflow hidden) contains `#world`, translated/scaled via CSS transform
  with `transform-origin: 0 0`. The dot grid is the viewport background; `background-size`
  and `background-position` are kept in sync with the camera so the grid pans/zooms with content.
- Camera: `{x, y, scale}`, scale clamped **0.2–2.5**.
- **Zoom**: wheel zooms toward the cursor (`exp(-deltaY·k)`, higher k for ctrl/pinch);
  toolbar `+ / −`; `0` resets; `F` / fit button fits the bounding box of all nodes with 80 px padding.
- **Pan**: drag empty canvas, middle-mouse drag anywhere, or hold `Space` + drag.
- Zoom HUD (bottom-left) shows the current % and resets on click.

### 4.3 Canvas nodes
Common: absolutely positioned card with a 28 px header (kind label + delete-on-hover ×),
body, and a SE resize handle. Click selects (brass ring + bring-to-front), drag header/body
moves (3 px threshold distinguishes click from drag; pointer deltas divided by camera scale).
`Delete`/`Backspace` removes the selection. All geometry changes are persisted with a
debounced `PATCH /api/nodes/{id}`.

| Type | Body | Notes |
|---|---|---|
| `note` | `contenteditable` plain text, autosaved (500 ms debounce) | marked `data-nodrag` so text editing never fights dragging; drag via header. Double-click empty canvas creates a note and focuses it. |
| `image` | `<img object-fit:cover>` + filename caption gradient | created from uploads/drops; node sized to the image aspect ratio (width 320, height clamped 120–480). |
| `video` | placeholder: play ring, filename, “Video placeholder” sub-label over a subtle diagonal-stripe slate | stands in for renders that Loom/pipeline agents will produce; no `<video>` element yet. |

### 4.4 Upload drop
Drag files anywhere over the canvas → dashed brass overlay (“Drop to add to the board”,
depth-counted dragenter/leave so child elements don't flicker it). On drop, files are placed
at the drop point in world coordinates, cascading +36 px per file:
- `image/*` → `POST /api/uploads` (multipart), then an image node with the returned URL.
- `video/*` → video placeholder node (upload itself is the render pipeline's job).
- anything else → note node recording the filename.
The toolbar Upload button / `U` opens the same flow via a file picker.

### 4.5 Chat dock
- Header: **thread select** + new-thread button (+), collapse chevron. Collapsed state shows a
  floating bubble at top-right to reopen; state persists in prefs. `C` toggles.
- **Message list** (`aria-live=polite`): user turns right-aligned in brass-tinted cards,
  Helix turns left-aligned on panel cards, each with a mono metadata line
  (`Helix · anthropic/claude-sonnet-4.5 · thinking`). Auto-scroll only while the user is pinned
  within 48 px of the bottom, so scrolling up during a stream is never hijacked.
- **Streaming-ready**: an assistant placeholder message is appended on send with a blinking
  brass cursor (`.pending::after`). Tokens are appended to a live text node — no list re-render
  per token. Thinking-mode messages get a collapsible **Reasoning** `<details>` block that
  auto-opens while thinking tokens stream and collapses when the answer starts.
- **Fast / Thinking toggle**: segmented pill (bolt / bulb). Sent as `mode` on every chat call;
  persisted in prefs. Thinking = Helix plans before answering (per product spec).
- **Provider/model picker**: two compact selects; model list re-populates on provider change;
  populated from `GET /api/providers` with a hardcoded fallback catalog. Persisted in prefs.
- **Composer**: auto-growing textarea (max 160 px), `Enter` sends, `Shift+Enter` newline.
  Send is disabled while a stream is in flight.

### 4.6 Settings panel (BYOK)
Right slide-over. One row per provider (OpenAI, Anthropic, Google AI, fal.ai, Replicate):
- `input[type=password]` (`autocomplete=off`), eye button toggles visibility.
- Status chip per row: `not set` or `saved …abcd` from the server's masked hint.
- **Save keys** sends only non-empty inputs via `PUT /api/keys`; the server never returns raw
  keys, only `{set, hint}`. Inputs are cleared after save.
- Connection section shows the active backend and offers a retry button.
- Demo-mode caveat (documented in-app copy too): keys go to localStorage base64-obfuscated —
  fine for a demo, never for production; live mode always stores server-side.

### 4.7 Brand kit panel (StyleLock)
Right slide-over, per-project:
- **Palette**: rows of color-input swatch + role name + hex readout + remove; “+ Add color”.
- **Typography**: heading font / body font text fields.
- **Logo**: click-or-drop zone; uploads through the same `/api/uploads` endpoint, previews inline.
- **Voice & tone**: textarea.
- **Save brand kit** → `PUT /api/projects/{id}/brand-kit`. Footer copy explains the kit is
  injected into every Helix generation and enforced by the critic pass (per product spec).

### 4.8 Feedback
Bottom-center toasts (info / ok / err) for saves, failures, and backend switches.

---

## 5. Keyboard map

| Key | Action |
|---|---|
| `N` | new note (also dbl-click canvas) |
| `U` | upload picker |
| `V` | video placeholder |
| `F` | fit board |
| `0` / `+` / `−` | reset / zoom in / zoom out |
| `Space`+drag | pan |
| `Delete` / `Backspace` | delete selected node |
| `C` | toggle chat dock |
| `Enter` / `Shift+Enter` | send / newline in composer |
| `Esc` | close panels & popovers, deselect |

Shortcuts are suppressed while typing (inputs, selects, contenteditable).

---

## 6. Data model (client-side)

```js
state = {
  backend, live,                      // RemoteBackend | LocalBackend
  projects: [{id, name, created_at}],
  projectId,
  threads: [{id, project_id, title, created_at}],
  threadId,
  messages: [{id, thread_id, role: 'user'|'assistant', content,
              thinking?, mode, provider, model, created_at, error?}],
  nodes: [{id, project_id, type: 'note'|'image'|'video',
           x, y, w, h, z, data: {text? | src?, title? | title?, sub?}}],
  providers: [{id, name, models: [string | {id, label}]}],
  provider, model, mode: 'fast'|'thinking',
  brandKit: {colors: [{name, value}], fonts: {heading, body}, logo_url, voice},
  camera: {x, y, scale}, selectedNodeId, maxZ, streaming,
}
```

Node coordinates are **world-space** (camera-independent); `z` is a monotonically increasing
bring-to-front counter. UI prefs (`atelier.prefs` in localStorage): last project, provider,
model, mode, chat-open.

---

## 7. Assumed Helix REST contract (`/api`)

The Helix OpenAPI document is owned by another workstream; this UI codes against the surface
below and treats response shapes liberally (accepts either a bare array or `{items: [...]}`).
If the final spec diverges, only the `RemoteBackend` object in `app.js` (~70 lines) needs edits.

| Method & path | Body → Response | Used by |
|---|---|---|
| `GET /api/health` | → `200` | backend detection |
| `GET /api/projects` | → `[Project]` | switcher |
| `POST /api/projects` | `{name}` → `Project` | switcher create |
| `GET /api/projects/{id}/threads` | → `[Thread]` | chat dock |
| `POST /api/projects/{id}/threads` | `{title}` → `Thread` | new thread |
| `GET /api/threads/{id}/messages` | → `[Message]` | history load |
| `POST /api/chat` | `{thread_id, project_id, message, mode, provider, model}` → **SSE stream** | send; server persists both turns |
| `GET /api/projects/{id}/nodes` | → `[Node]` | board load |
| `POST /api/projects/{id}/nodes` | `Node` → `Node` (server may re-issue `id`) | create node |
| `PATCH /api/nodes/{id}` | partial `{x,y,w,h,z,data}` → `204/Node` | move/resize/edit |
| `DELETE /api/nodes/{id}` | → `204` | delete node |
| `POST /api/uploads` | multipart `file` → `{id, url, kind}` | drops, picker, logo |
| `GET /api/providers` | → `[{id, name, models}]` | model picker |
| `GET /api/keys` | → `{provider: {set, hint}}` (masked, never raw) | settings |
| `PUT /api/keys` | `{provider: rawKey, …}` → masked map | BYOK save |
| `GET /api/projects/{id}/brand-kit` | → `BrandKit` | StyleLock |
| `PUT /api/projects/{id}/brand-kit` | `BrandKit` → `BrandKit` | StyleLock save |

### 7.1 Chat streaming protocol (SSE over `POST /api/chat`)

`Accept: text/event-stream`. The client reads `response.body` with a `ReadableStream` reader
and parses `\n\n`-delimited frames (multi-`data:`-line frames are joined), so it works with
plain `fetch` — no `EventSource` (which can't POST).

```
event: thinking.delta        ← only in mode="thinking"
data: {"delta":"Reading project ledger…"}

event: message.delta
data: {"delta":"Direction: macro botanical forms"}

event: done
data: {"message":{"id":"m_9","role":"assistant","content":"…"}}
```

Client behavior:
- default event type is `message.delta`; bare `data: [DONE]` is honored as terminal;
  unparseable `data` payloads are treated as raw text deltas;
- `error` frames (`{"message"}`) mark the bubble as errored without losing partial text;
- a stream that ends without a `done` frame is closed idempotently;
- if `done` carries full `content` and no deltas were received (non-streaming server),
  the full text is rendered at once — the UI supports both modes.

---

## 8. Demo fallback backend

`LocalBackend` mirrors the exact `RemoteBackend` interface:
- Store: `atelier.local.v1` in localStorage; quota overflows degrade to session-only silently.
- Seeded first-run content: project *“Neon Botanica — Campaign”* with a brief note, palette
  note, two SVG-data-URI reference images (no network), a video placeholder, one thread with
  two messages, and a filled brand kit — so the first paint demonstrates every node type.
- `sendChat` simulates the SSE contract: streams a thinking block first when
  `mode="thinking"` (~14 ms/token), then the reply (~22 ms/token), cycling through four
  board-aware canned responses, and persists both turns.
- Uploads ≤ 1.5 MB persist as data URLs; larger files use session-only object URLs.

Mode is decided once at boot (plus manual retry); live and demo data are never mixed.

---

## 9. Accessibility & robustness

- Landmarks/labels: `aria-label` on canvas, dock, panels; message list is `aria-live=polite`;
  mode toggle is a `radiogroup`; panels track `aria-hidden`; popover sets `aria-expanded`.
- Full keyboard path for chat, panels, and node deletion; pointer events use capture so drags
  never strand mid-gesture; `pointercancel` handled.
- No `innerHTML` with user data: user strings go through `textContent` / `.value` everywhere
  (messages, notes, titles, project names), preventing DOM XSS.
- Passwords: `type=password`, `autocomplete=off`, never echoed after save.
- Every backend call is wrapped; failures surface as toasts, never break the board.

## 10. Out of scope / follow-ups

Multi-select and marquee; node rotation; realtime multiplayer (CRDT layer); `@`-mentioning
brand kits and nodes from chat (needs Helix context-ledger endpoints); actual video playback;
plan-graph visualization for Thinking mode; auth (assumed session handled upstream of `/api`).
