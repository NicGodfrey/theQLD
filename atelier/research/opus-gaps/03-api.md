# Atelier API contract gaps — three-way diff

**Author:** Opus#3 of 10 · **Scope:** read-only analysis, `/workspace` unmodified.

## The three contracts

| Tag | Contract | Files |
|---|---|---|
| **L** | Live implementation | `atelier/server.py`, `atelier/web/app.js`, `atelier/web/index.html`, `atelier/helix/store.py`, `atelier/helix/keyring.py`, `atelier/helix/conductor.py`, `atelier/helix/usage.py` |
| **B** | Research board UI | `atelier/research/fable5/06-board-ui/app.js`, `.../UI_SPEC.md` (§7 contract table, §7.1 SSE) |
| **O** | Research OpenAPI | `atelier/research/fable5/04-helix-arch/openapi.yaml` (+ `store.py`, `schema.sql`) |

---

## 0. Headline

The three contracts do not overlap enough to ship any one of them against any other. **B and L share exactly one working endpoint: `GET /api/health`.** Every other call B makes against L either 404s, 501s, returns the wrong envelope, or returns HTTP 200 while silently discarding the write. O is a different API altogether — different port, different path prefix, different resource tree, different id format, different time unit, different money unit, and a mandatory bearer token that neither other contract has any concept of.

Counted below: **58 mismatches**, of which **19 are ship-blocking** (marked **BLOCKER**) — meaning a user hits them in a normal first session and the product is visibly broken or silently loses their work.

The seven areas the brief called out are all genuinely missing from the shipping path:

| Feature | L (live) | B (board UI) | O (OpenAPI) | Verdict |
|---|---|---|---|---|
| Streaming | absent at all 3 layers (transport, route, spoke) | required, one-call `POST /api/chat` SSE | two-call `202` + `GET …/events` SSE | 3-way conflict, nothing implemented |
| Upload | no route, no multipart parser | `POST /api/uploads` → `{id,url,kind}` | `POST /projects/{id}/artifacts` multipart → `Artifact` | 3-way conflict, nothing implemented |
| Delete project | none | none | `POST /projects/{id}/archive` (soft) | only O has an answer |
| Delete thread | none | none | `PATCH /threads/{id}` status → archived | only O has an answer |
| Delete node | none (501) | `DELETE /api/nodes/{id}` | `DELETE /nodes/{id}` → 204 | B and O agree, L has nothing |
| Export / download | `GET /api/artifacts/{id}` only, always `.bin` attachment | nothing at all | `GET /projects/{id}/snapshot` + `/artifacts/{id}/content` | only O has an answer |
| Health | `GET /api/health` → `{ok,name,architecture}` | `GET /api/health`, 1.5 s timeout, checks `res.ok` only | **no `/health` path exists** | L↔B agree, O omits it |
| CORS | zero headers, `OPTIONS` → 501 | assumes same-origin `/api` | not addressed | nothing implemented |
| Auth | none | explicitly out of scope (UI_SPEC §10) | `security: [localToken]` bearer, global | 3-way conflict |

**Recommended single source of truth for v1, in one line:** freeze **L's routing and transport** (`/api/*` on the same origin that serves the UI), adopt **B's field names and JSON body shapes** (UI_SPEC §7 — it is the only contract with a consumer that actually renders every field), adopt **O only for the four things L and B both lack** (snapshot export format, soft-delete/archive semantics, artifact content/metadata split, and the security model from `research/fable5/08-security-quota/THREAT_MODEL.md`), and defer O's entire boards/layers/rungs/lineage/loom-runs/provider-registry tree to v2.

---

## 1. Smoke test: what happens today if you serve B from L

This is the fastest proof of how wide the gap is. Serving `06-board-ui/` from `server.py`'s static handler and loading it:

| # | Action | Call | Result |
|---|---|---|---|
| 1 | boot | `GET /api/health` | 200 → pill says "Live /api" ✅ |
| 2 | boot | `GET /api/providers` | 404 → silently falls back to hardcoded `anthropic/claude-sonnet-4.5`, a provider L cannot route |
| 3 | boot | `GET /api/keys` | 200, but L returns `{configured,source,base_url,hint}` and B reads `.set` → **every key row shows "not set" even when keys are configured** |
| 4 | boot | `GET /api/projects` | 200 `{projects:[…]}`; B's `asList()` accepts only a bare array or `{items:[…]}` → sees `[]` → **auto-creates "Untitled project" on every single page load** |
| 5 | open project | `GET /api/projects/{id}/nodes` | 404 → board renders empty even though L has nodes at `/board` |
| 6 | open project | `GET /api/projects/{id}/threads` | 200 wrapped → `[]` → creates a thread with `{title:"General"}`; L reads `body["topic"]` → stores `""` → thread dropdown renders literal `undefined` |
| 7 | open project | `GET /api/projects/{id}/brand-kit` | 404 → falls back to default kit; user's real kit invisible |
| 8 | open thread | `GET /api/threads/{id}/messages` | 200 wrapped → `[]` → **all chat history invisible** |
| 9 | send message | `POST /api/chat` | 404 → toast `POST /chat → 404`. Chat is completely dead. |
| 10 | add note | `POST /api/projects/{id}/nodes` | 404 → node exists in DOM only, gone on reload |
| 11 | drag that note | `PATCH /api/nodes/{id}` | node id is a client UUID absent from the DB → `update_node` → `get_node` → `dict(None)` → **uncaught `TypeError`, connection reset, traceback on stderr** |
| 12 | delete node | `DELETE /api/nodes/{id}` | 501 Unsupported method |
| 13 | upload / drop file | `POST /api/uploads` | 404 (and even if routed, `_read_json` would `json.loads` the multipart body → 400) |
| 14 | save keys | `PUT /api/keys` | 501 |
| 15 | save brand kit | `PUT /api/projects/{id}/brand-kit` | 501 |

Working: health, project creation, thread creation (untitled). Everything else is broken, and four of the failures (#3, #4, #6, #8) are *silent* — the UI reports success or emptiness rather than an error, which is the worst failure class for a shipping product.

An O-generated client against L fails even earlier: wrong port (8787 vs 8765), wrong prefix (`/v1` vs `/api`), and a mandatory `Authorization: Bearer` that L never reads.

---

## 2. Transport, framing, and identity

### T1 — Base URL and path prefix disagree three ways · **BLOCKER**
- **L:** `/api/*`, `ThreadingHTTPServer` on `ATELIER_HOST=127.0.0.1:ATELIER_PORT=8765`, same origin as the UI (`server.py:225-234`).
- **B:** `const API = "/api"` — relative, same-origin by design (`06-board-ui/app.js:63`; UI_SPEC §7 "all calls use relative paths").
- **O:** `servers: http://127.0.0.1:8787/v1` (`openapi.yaml:24-26`).
- **Who breaks:** anyone generating a client from O, any reverse-proxy or Electron shell author, and every future integrator who reads the spec instead of the code. Also breaks docs: the spec's own `events_url` examples are `/v1/conductor/turns/…`.
- **SSOT for v1:** **L.** Keep `/api` on the UI's own origin. Delete the `:8787/v1` server block from O or re-point it at `http://127.0.0.1:8765/api`. Same-origin is what makes the "no CORS, no auth" posture even arguable; giving the API its own port throws that away for nothing.

### T2 — List responses: wrapped object vs bare array · **BLOCKER**
- **L:** `{"projects":[…]}`, `{"threads":[…]}`, `{"messages":[…]}`, `{"nodes":[…]}` (`server.py:120,134,138,141`).
- **B:** `asList()` unwraps a bare array or `{items:[…]}` — and nothing else (`06-board-ui/app.js:143`).
- **O:** bare arrays for every list (`openapi.yaml:72-74, 182-185, 256-260`).
- **Who breaks:** every list in B renders empty against L; worse, the empty project list triggers auto-creation of a junk project per reload (smoke test #4), and the empty message list looks like history loss.
- **SSOT for v1:** **O + B — bare arrays.** Two of three contracts already agree, B's unwrapper is one line, and L's wrapper buys nothing. Change `server.py` to return arrays; update `web/app.js`'s five `data.x || []` call sites. If you want a growth path for pagination, standardize on `{items, next}` and teach B's `asList` nothing new — it already handles it.

### T3 — Id format
- **L:** `uuid.uuid4().hex` — 32 unprefixed hex chars (`helix/store.py:78-79`).
- **B:** `crypto.randomUUID()` client-side, expects the server may reissue (`app.js:21-22, 656-660`).
- **O:** prefixed ULIDs, `prj_`/`thr_`/`msg_`/`art_`/`nod_`… documented as a convention (`openapi.yaml:18-19`).
- **Who breaks:** anything that routes or validates on the prefix (log filters, snapshot import validation, error messages that say which kind of id was bad); and support, which cannot tell a thread id from an artifact id in a bug report.
- **SSOT for v1:** **O's prefix convention, L's generator.** Keep uuid4 (ULID needs a dependency or 40 lines), but prefix it: `prj_<hex>`. Cheap, reversible, and it makes every other gap on this list easier to debug.

### T4 — Timestamp unit: float seconds vs integer milliseconds
- **L:** `created_at REAL` = `time.time()` float seconds (`helix/store.py:52-53, 74-76`).
- **B:** `Date.now()` milliseconds in its demo store; does not currently render `created_at` at all, so this is latent on the UI side (`app.js:25, 247`).
- **O:** "timestamps are unix epoch **milliseconds**", `format: int64` on every `created_at` (`openapi.yaml:20, 1265-1266`).
- **Who breaks:** the moment anyone adds a timestamp to the chat bubble or the node card, L's seconds render as January 1970. Also breaks snapshot round-tripping and any `since=` query filter O defines (`/usage/events?since`).
- **SSOT for v1:** **O — integer epoch milliseconds everywhere.** Convert at the store boundary now, while there is one writer, rather than after two clients have baked in seconds.

### T5 — Money unit: float USD vs integer micro-USD
- **L:** `estimated_usd REAL`, dollars, `round(…, 6)` (`helix/usage.py:55-66`; `helix/store.py:67`), summed in the UI with `toFixed(4)` (`web/app.js:150-152`).
- **B:** does not display spend at all.
- **O:** `cost_micros` integer micro-USD (`openapi.yaml:21, 1470`).
- **Who breaks:** accounting. Float dollars accumulate representation error across thousands of rows, and the two schemas do not convert losslessly in either direction. Also: B ships with **no spend meter at all**, which for a BYOK product means the user watches their own money disappear with no in-product signal.
- **SSOT for v1:** **O — integer `cost_micros`.** And port L's spend pill (`web/app.js:149-152`) into B before ship; this is a product requirement, not a nicety.

### T6 — HTTP methods: `PUT`, `DELETE`, `OPTIONS`, `HEAD` are unimplemented · **BLOCKER**
- **L:** only `do_GET`, `do_POST`, `do_PATCH` (and `do_PATCH` just calls `do_POST`) — `server.py:98, 159, 221-222`. `BaseHTTPRequestHandler` answers everything else with **501 Unsupported method**.
- **B:** uses `PUT /api/keys`, `PUT /api/projects/{id}/brand-kit`, `DELETE /api/nodes/{id}` (`app.js:162, 167, 171`).
- **O:** uses `PUT /keyring/{keyRef}`, `DELETE /keyring/{keyRef}`, `DELETE /nodes/{id}`, `DELETE /layers/{id}`.
- **Who breaks:** three of B's write paths return 501 (smoke test #12, #14, #15). Preflight `OPTIONS` also 501s, which forecloses any cross-origin story (see X2).
- **SSOT for v1:** **B + O — implement `do_PUT`, `do_DELETE`, `do_OPTIONS`, `do_HEAD`.** This is ~20 lines in `server.py` and unblocks delete, key save, and brand-kit save at once.

### T7 — `do_PATCH` aliases `do_POST`, so PATCH routing is accidental
- **L:** `def do_PATCH(self): self.do_POST()` (`server.py:221-222`). `PATCH /api/nodes/{id}` works only because a POST route with the same shape exists; `PATCH /api/projects/{id}` (O's `updateProject`) falls through to `{"error":"unknown POST"}` 404.
- **B:** `PATCH /api/nodes/{id}` (`app.js:160-161`).
- **O:** PATCH on projects, threads, artifacts, boards, layers, nodes, providers.
- **Who breaks:** anyone who assumes verb-correct routing; renaming a project is impossible today.
- **SSOT for v1:** **L's paths, real verb dispatch.** Route on `(method, path)` explicitly. Keep only the PATCHes v1 needs: node, project (rename), thread (rename/archive).

### T8 — Error body shape
- **L:** `{"error": "<string>"}` (`server.py:79, 151, 165, 199, 211, 219`).
- **B:** reads only `res.status`; surfaces `METHOD path → status` in a toast (`app.js:138`).
- **O:** `Error {error, detail}` with `error` as a stable machine code (`not_found`) and `detail` as prose (`openapi.yaml:1221-1228`).
- **Who breaks:** B cannot distinguish "budget exceeded" from "provider down" from "bad JSON" — all render as a bare status. Which matters most for the one error users will actually hit (see C4, budget → 500).
- **SSOT for v1:** **O.** `{error: <stable_code>, detail: <prose>}`, and teach B's `apiFetch` to read the body on `!res.ok`. Small change, large support-cost reduction.

### T9 — HTTP/1.0, `Content-Length` on every response
- **L:** `protocol_version` is never set, so responses are HTTP/1.0 with no keep-alive; `_json` always sets `Content-Length` (`server.py:57-64`).
- **B:** requires a readable `res.body` stream for SSE (`app.js:195-224`).
- **O:** `text/event-stream` on two endpoints.
- **Who breaks:** this is the transport-level reason streaming cannot be bolted on without touching `server.py`'s response helpers — see S1.
- **SSOT for v1:** **B/O.** Set `protocol_version = "HTTP/1.1"`, add an SSE writer that omits `Content-Length` and flushes per frame.

---

## 3. Streaming

### S1 — No streaming exists anywhere in L, at any of three layers · **BLOCKER**
- **L:** no SSE route; no chunked writer (T9); and the spokes have no streaming method at all — `helix/spokes/ollama_spoke.py:39` hardcodes `"stream": False`, and `openai_spoke`/`gemini_spoke` expose only `chat()`/`image()`. `POST /api/threads/{id}/run` (`server.py:196-214`) runs planner chat → up to 8 image generations → critic chat **synchronously**, then returns one JSON blob.
- **B:** `POST /api/chat` with `Accept: text/event-stream`, reads `res.body.getReader()`, parses `\n\n` frames (`app.js:187-226`); the entire chat dock is built around incremental token append with a blinking cursor and a live "Reasoning" `<details>` block (UI_SPEC §4.5).
- **O:** `POST /conductor/turns` → `202 {turn_id, events_url}` then `GET /conductor/turns/{turnId}/events` SSE (`openapi.yaml:1105-1162`), plus `GET /loom/runs/{runId}/events`.
- **Research prior art that L ignores:** `research/fable5/03-keyring-spokes/spokes_openai.py:186` `_chat_stream`, `spokes_anthropic.py:131`, `spokes_gemini.py:183`, with recorded SSE fixtures in `03-keyring-spokes/tests/fixtures/*.sse`.
- **Who breaks:** every user. A thinking-mode run with four weave items is tens of seconds of a frozen button with no progress and no cancel. B's chat is unusable against L (smoke test #9). And "thinking vs fast", the product's headline differentiator, is invisible without streaming — the critique L generates is buried in a summary string.
- **SSOT for v1:** **B — one-call `POST /api/chat` returning SSE.** Rationale: O's two-call `202` + `GET events` shape needs a turn registry, an event bus, and reconnect/replay semantics (what happens if the client fetches `events_url` after the turn finished?) — real infrastructure for a single-user local app. B's shape is one request, no server-side turn state, and it is already implemented on the client including the non-streaming degradation path (UI_SPEC §7.1: "if `done` carries full `content` and no deltas were received, the full text is rendered at once"). That last property means **you can ship the SSE route wrapping the existing synchronous conductor on day one** — emit `plan`, then `done` — and add real token deltas after, with no client change.

### S2 — SSE event vocabularies are disjoint
- **B:** `thinking.delta {delta}` / `message.delta {delta}` / `done {message}` / `error {message}`; default event type is `message.delta`; bare `data: [DONE]` honored (UI_SPEC §7.1; `app.js:199-206`).
- **O:** `plan`, `message.appended`, `artifact.created`, `node.placed`, `usage`, `error`, `done` (`openapi.yaml:1157-1159`); Loom adds `run.status`, `step.status`, `step.output`.
- **L:** n/a.
- **Who breaks:** the board needs `artifact.created`/`node.placed` to place a generated image without a full refetch — B's vocabulary has no way to express "a node appeared", so B would have to poll or refetch the whole board after every turn (which is exactly what L's `web/app.js:206` `bootProject()` does today).
- **SSOT for v1:** **B's frame grammar, extended with two events from O.** Ship `thinking.delta`, `message.delta`, `node.placed`, `usage`, `error`, `done`. Drop `plan`, `message.appended`, `artifact.created` (fold artifact info into `node.placed`). This is the one place where B is under-specified and O's vocabulary is right.

### S3 — Turn request field name differs three ways
- **L:** `{prompt, mode, provider, model}` at `POST /api/threads/{id}/run` (`server.py:196-209`).
- **B:** `{thread_id, project_id, message, mode, provider, model}` at `POST /api/chat` (`app.js:1164-1173`).
- **O:** `{thread_id, instruction, board_id, constraints}` at `POST /conductor/turns` (`openapi.yaml:1114-1131`).
- **Who breaks:** `prompt` vs `message` vs `instruction` for the same string. Any adapter has to translate, and the translation is invisible in logs.
- **SSOT for v1:** **B.** `POST /api/chat {thread_id, project_id, message, mode, provider, model}`. `project_id` is redundant with `thread_id` but harmless and lets the server skip a lookup.

### S4 — No cancel / abort path
- **L:** synchronous request; no cancel route; a slow provider call holds the connection with no way to stop it.
- **B:** disables Send for the duration of the stream (`app.js:1129`); there is no stop button in the markup or the keymap.
- **O:** `POST /loom/runs/{runId}/cancel` with a `409` for terminal runs (`openapi.yaml:1067-1084`) — but nothing equivalent for conductor turns.
- **Who breaks:** a user who typos a prompt and watches their own API budget burn through 8 image generations with no way out. For a BYOK product this is a money bug, not a UX bug.
- **SSOT for v1:** **new, minimal.** Client aborts the `fetch` (`AbortController`, which B already imports for the health probe at `app.js:430`); server checks `wfile` write failure between weave items and stops. No cancel endpoint, no run registry. Add a visible Stop button to the composer.

### S5 — Streamed output has nowhere to live in the message schema
- **L:** `messages` table is `{id, thread_id, role, content, plan_json, created_at}` (`helix/store.py:27-35`). Thinking output is squeezed into the summary string by `_summarize` (`helix/conductor.py:266-276`).
- **B:** renders `m.thinking` in a collapsible Reasoning block and `m.mode/provider/model` in the metadata line (UI_SPEC §4.5, §6).
- **O:** generic `payload: object` plus `seq` (`openapi.yaml:1278-1287`).
- **Who breaks:** thinking mode. The reasoning stream arrives, renders live, and then vanishes on reload because there is no column for it.
- **SSOT for v1:** **B's field names, stored in O's generic slot.** Add `thinking TEXT`, `mode`, `provider`, `model` as real columns (B renders them by name, so a generic `payload` blob would force client-side unpacking for the one thing that must render on every message). Keep `plan_json` as the generic payload.

---

## 4. Upload

### U1 — No upload route and no multipart parser in L · **BLOCKER**
- **L:** no `/api/uploads`, no `/artifacts` POST, and `_read_json` unconditionally `json.loads` the body (`server.py:67-74`) — so a multipart POST would 400 `invalid json` even if routed. No `cgi`/`email.parser`/multipart handling anywhere in the tree. The only way an artifact comes into existence is `Conductor.run` (`helix/conductor.py:165-177`).
- **B:** `POST /api/uploads` multipart `file` → `{id, url, kind}`; drives canvas drop, toolbar Upload / `U` key, and the brand-kit logo picker (`app.js:173-179, 799-820`; UI_SPEC §4.4, §4.7).
- **O:** `POST /projects/{projectId}/artifacts`, multipart with **required** `kind`, `mime`, `file`, → full `Artifact` with sha256 content-addressing and dedupe; plus an `application/json` variant to register an external URL (`openapi.yaml:342-384`).
- **Who breaks:** every user with a reference image, a client logo, or a moodboard — which is the entire target audience of a design studio. Drag-and-drop is B's most prominent canvas affordance and it fails silently into a toast.
- **SSOT for v1:** **B's route and response, O's storage semantics.** Ship `POST /api/uploads` returning `{id, url, kind}` (B's shape, so no client change), but implement it over O's model underneath: content-address by sha256, dedupe, write into the same artifacts table/dir the conductor uses, and return `url = /api/artifacts/{id}/content`. Rejecting O's `POST /projects/{id}/artifacts` path for v1 is deliberate — B already codes against `/uploads`, and O's required `kind`+`mime` form fields duplicate what the server can sniff.

### U2 — Upload response shape: `{id,url,kind}` vs `Artifact`
- **B:** `{id, url, kind}` where `kind` is the raw MIME type (`app.js:178, 380`) and `url` goes straight into `node.data.src` / `<img src>`.
- **O:** `Artifact {id, project_id, kind (enum image|video|audio|…), mime, storage, uri, sha256, byte_size, width, height, …}` — note `kind` is an *enum category* in O and a *MIME string* in B. Same field name, different meaning.
- **L:** n/a.
- **Who breaks:** anyone writing the server against O and the client against B — `kind: "image/png"` vs `kind: "image"` is exactly the kind of collision that passes review and fails at runtime.
- **SSOT for v1:** **O's vocabulary, B's envelope.** Return `{id, url, kind, mime}` where `kind` is O's enum and `mime` is the raw type. B's `placeFile` only branches on the `File` object's own `type`, so adding `mime` is free.

### U3 — Where uploaded bytes are served from: three spellings
- **L:** `GET /api/artifacts/{id}` returns bytes directly (`server.py:143-149`).
- **B:** stores whatever absolute-or-relative `url` the upload returned into `node.data.src`.
- **O:** metadata at `GET /artifacts/{id}`, bytes at `GET /artifacts/{id}/content`, with `409` if the artifact is external (`openapi.yaml:386-441`).
- **Who breaks:** node rows persist a URL, so this choice is baked into the database. Changing it later means a migration over every node's `data.src`.
- **SSOT for v1:** **O.** Split metadata from content — `GET /api/artifacts/{id}` → JSON, `GET /api/artifacts/{id}/content` → bytes. Persist artifact **ids** on nodes (L already does, via `nodes.artifact_id`) and let the client build the URL, so the path stays changeable.

### U4 — `Content-Disposition: attachment` on the only byte route, always `.bin`
- **L:** `_send_file(..., download_name=f"{art['id']}.bin")` (`server.py:148`) — every artifact downloads as `<32-hex>.bin` regardless of its real type, and the same route is used as an `<img src>` by the live UI (`web/app.js:84`). One route serving both "render inline" and "save to disk" is the root cause.
- **B:** expects a plain inline URL.
- **O:** `Content-Type` = the artifact's mime, no forced disposition (`openapi.yaml:431-435`).
- **Who breaks:** anyone who clicks Download and gets an unopenable `.bin`; and it is the sole "export" path in the product today (see E1).
- **SSOT for v1:** **O.** Serve inline with the correct `Content-Type` by default; add `?download=1` to opt into `Content-Disposition: attachment` with a real filename (`<title or id>.<ext from mime>`).

### U5 — No size limit, no MIME allowlist, and SVG is served same-origin
- **L:** `_send_file` force-sets `image/svg+xml` for `.svg` (`server.py:83-84`) and there is no upload path to validate in the first place. The demo weave produces SVG (`helix/loom.py:10-28`).
- **B:** no client-side size or type gate; anything not `image/*` or `video/*` becomes a note (`app.js:799-805`).
- **O:** silent on limits. `research/fable5/08-security-quota/THREAT_MODEL.md:115, 127` requires CSP and SVG sanitization/rasterization.
- **Who breaks:** ship U1 without this and you have created stored XSS *on the same origin that holds the BYOK key API* — an uploaded SVG with a script tag, rendered from `/api/artifacts/…`, can read `GET /api/keys` (which leaks partial secrets, see A4) and drive `POST /api/chat` on the user's dime.
- **SSOT for v1:** **THREAT_MODEL.md.** Enforce a size cap, a MIME allowlist, `Content-Security-Policy` on all responses, and either rasterize uploaded SVG or serve artifacts with `Content-Disposition: attachment` + `Content-Security-Policy: sandbox`. This is a prerequisite for U1, not a follow-up.

---

## 5. Delete

### D1 — Cannot delete or archive a project · **BLOCKER**
- **L:** no route, and `helix/store.py` has no `delete_project`/`archive_project` and no `archived_at` column (`store.py:13-18`).
- **B:** the project switcher creates and selects; there is no remove affordance anywhere (`app.js:900-935`).
- **O:** `POST /projects/{projectId}/archive` — "Archive (never hard-delete)" — plus `archived_at` and an `include_archived` list filter (`openapi.yaml:134-147, 63-66, 1264`).
- **Who breaks:** every user, permanently and cumulatively. Compounded by T2: B creates a junk "Untitled project" on every reload, and none of them can ever be removed. Within a day of use the switcher is unusable.
- **SSOT for v1:** **O — soft archive.** `POST /api/projects/{id}/archive` + `?include_archived`. Soft over hard is right here: the data is the user's design history and there is no undo elsewhere in the product. Add an Archive item to B's project popover.

### D2 — Cannot delete or archive a thread
- **L:** nothing.
- **B:** nothing — new-thread button only (`app.js:995-1005`).
- **O:** `PATCH /threads/{threadId}` with `status: archived` (`openapi.yaml:218-236`, `ThreadStatus` enum `open|pinned|resolved|archived` at 1230-1232).
- **Who breaks:** the thread `<select>` grows without bound; combined with K1 (every thread from B is untitled) the dropdown becomes a list of identical `undefined` entries.
- **SSOT for v1:** **O.** `PATCH /api/threads/{id} {status}`, and reuse the same PATCH for rename. One route covers both.

### D3 — Cannot delete a node · **BLOCKER**
- **L:** `DELETE` → 501 (T6); `Memory` has no `delete_node` (`store.py:213-266` has add/get/list/update only).
- **B:** `DELETE /api/nodes/{id}`, wired to the per-node hover `×`, and to `Delete`/`Backspace` (`app.js:162, 665-672`; UI_SPEC §4.3, keymap §5).
- **O:** `DELETE /nodes/{id}` → `204`, "the artifact behind it is untouched" (`openapi.yaml:676-682`).
- **Who breaks:** every user, on their first bad generation. The live UI has no delete affordance at all, so a misfired weave pins up to 8 permanent images.
- **SSOT for v1:** **B + O (they agree).** `DELETE /api/nodes/{id}` → `204`, artifact survives.

### D4 — Cascade and artifact garbage collection are undefined
- **L:** the `nodes` table has **no foreign key at all** (`store.py:48-60`); `threads`/`messages` have FKs but SQLite doesn't enforce them without `PRAGMA foreign_keys=ON`, which is never set. Artifact files under `.runtime/artifacts/` are never removed.
- **B:** assumes the server sorts it out.
- **O:** explicit — deleting a layer cascades to its nodes, artifacts survive (`openapi.yaml:600-606`); archiving a project cascades to nothing.
- **Who breaks:** whoever implements D1/D3 without deciding this, and later every user's disk. Orphaned artifact blobs accumulate with no reachable reference.
- **SSOT for v1:** **O's rule (artifacts survive node/project deletion) + a new explicit GC.** Enable `PRAGMA foreign_keys=ON`, add `ON DELETE CASCADE` for archive-then-purge, and ship a "purge archived" action that deletes rows *and* their unreferenced blobs. Do not silently GC — surface it.

### D5 — Cannot remove a stored key
- **L:** `Keyring.delete()` exists and is correct (`helix/keyring.py:82-86`) — **but is not routed**. No `DELETE /api/keys`.
- **B:** no remove-key affordance; a saved key can only be overwritten (`app.js:1282` placeholder "Enter new key to replace").
- **O:** `DELETE /keyring/{keyRef}` → `204` (`openapi.yaml:945-951`).
- **Who breaks:** a user who pastes a key into the wrong provider row, or who wants to revoke local storage of a credential before handing over the laptop. Today `public_status` will keep reporting `configured: true` forever.
- **SSOT for v1:** **O.** Route the method that already exists; add a small × per key row in B's settings panel. Roughly a ten-line change with an outsized trust payoff for a BYOK product.

---

## 6. Export and download

### E1 — No project export anywhere in the shipping path · **BLOCKER**
- **L:** nothing. No snapshot route, no export function in `helix/store.py`.
- **B:** nothing — a full-text search for `export`/`download` across `06-board-ui/` returns only a CSS font comment and the keymap's `Delete`. There is no export button in the markup.
- **O:** `GET /projects/{projectId}/snapshot` → `ProjectSnapshot` with `format: helix-snapshot/1`, threads-with-messages, artifacts, boards-with-layers-and-nodes, brand kits, runs, and a usage summary (`openapi.yaml:149-162, 1548-1588`).
- **Who breaks:** every user, at the moment they want their work out — and the product's whole BYOK, local-first, your-data-is-yours pitch dies with it. Also blocks backup, support ("send me your project"), and migration between machines.
- **SSOT for v1:** **O — `helix-snapshot/1`, trimmed.** Ship `GET /api/projects/{id}/snapshot` emitting exactly the tables that exist live (project, threads, messages, artifacts, nodes, brand kit, usage) under O's envelope and version string. Trimming is fine — the `format` field is there precisely so a v2 can add boards/layers/runs. What must not happen is inventing a second, incompatible export format later.

### E2 — Product-required asset export formats have no route at all
- **Spec:** `research/fable5/01-product-spec/ACCEPTANCE.md:44-47` (M-6) requires PNG (incl. transparent), JPEG, SVG for vector-text nodes, PDF-RGB, MP4 — plus watermarking by tier.
- **L:** the only byte-serving route is one artifact at a time (`server.py:143-149`), in whatever format the provider returned. Demo weaves are SVG (`helix/loom.py`), so a "download my poster" today yields an SVG named `.bin`.
- **B:** no export UI.
- **O:** no format-conversion endpoint either — `/artifacts/{id}/content` serves stored bytes only.
- **Who breaks:** the acceptance criteria, directly. And any user who needs a print-ready or platform-ready file, which is the actual job to be done.
- **SSOT for v1:** **new, and explicitly scoped down.** For v1 ship exactly two things: per-artifact download in its native format (U4), and the JSON snapshot (E1). Put PNG/PDF/SVG conversion and board-level composite export in v2 with a real route (`POST /api/projects/{id}/exports {format, node_ids}` → job → artifact). **Do not** let "export" ship as the `.bin` link and call M-6 satisfied.

### E3 — No batch or board-level export
- **L / B / O:** all three serve one artifact per request; nothing zips a board or a selection.
- **Who breaks:** the 7-platform fanout flow in `ACCEPTANCE.md:73` and any real handoff, where the deliverable is a folder, not a file.
- **SSOT for v1:** **defer explicitly.** The snapshot (E1) is the v1 answer to "get my stuff out"; note the limitation in the UI copy rather than shipping a half-batch.

---

## 7. Health

### H1 — O has no health endpoint, so B's live-detection fails against a spec-conformant server · **BLOCKER for the O path**
- **L:** `GET /api/health` → `200 {"ok":true,"name":"atelier","architecture":"helix"}` (`server.py:113-115`).
- **B:** `GET /api/health` with a 1.5 s `AbortController` timeout; **success is `res.ok` alone**, body ignored; on failure it silently switches to the localStorage demo backend (`app.js:428-437`).
- **O:** no `/health` path exists in the document.
- **Who breaks:** anyone who deploys a gateway that exposes only documented paths — B's probe 404s, the pill says "Demo mode", and the user is shown **seeded fake data** ("Neon Botanica — Campaign", two invented chat messages) that looks exactly like their real project list was wiped. This is the single most alarming failure mode in the entire diff.
- **SSOT for v1:** **L + B (they already agree).** Add `/health` to O. Also make the demo-mode banner unmistakable — the current amber pill is not enough to distinguish "seed data" from "your data".

### H2 — Health reports nothing actionable
- **L:** a static literal — it cannot fail. It does not check the SQLite connection, the keyring file, the artifacts directory, or report a version.
- **B:** shows "Live /api" on a bare 200.
- **O:** n/a.
- **Who breaks:** support, and any future updater. A corrupted DB or an unwritable runtime dir still reports healthy, and there is no way to ask a user "what version are you on".
- **SSOT for v1:** **new, minimal.** `{ok, name, version, architecture, db: ok|error, runtime_dir_writable: bool}`. Keep it cheap enough for a 1.5 s probe.

---

## 8. CORS and origin policy

### X1 — Zero CORS headers and `OPTIONS` → 501
- **L:** no `Access-Control-*` header anywhere; no `do_OPTIONS`, so preflight gets 501 (`server.py`, T6).
- **B:** assumes same-origin `/api`, so it needs no CORS — *if* it is served by the same server.
- **O:** does not address CORS; asserts loopback-only.
- **Who breaks:** the research team's own documented workflow. `UI_SPEC.md:23-28` tells you to run the board UI under `python3 -m http.server 8000`; the live API is on `:8765`; that is cross-origin, there is no CORS and no dev proxy config in the repo, so **the documented dev loop cannot be pointed at the real backend at all.** It can only ever run in demo mode. That is very likely why B has never been exercised against L, and why the mismatches in §1 went unnoticed.
- **SSOT for v1:** **B's same-origin assumption — serve the UI from the API server (which `server.py:101-112` already does).** Do not add permissive CORS; it is the wrong tool and it widens X2. Instead add a documented dev proxy (a ten-line `http.server` subclass, or `--proxy` support in the static server) so the research dev loop works.

### X2 — No `Origin`/`Host` validation: any web page can drive the local API · **BLOCKER**
- **L:** no origin check, no CSRF token, no `Host` validation. Every state-changing route is a simple `POST` with a JSON body — reachable cross-origin from any page the user visits, since simple requests are not preflighted for `Content-Type: text/plain` and the server never checks. That includes `POST /api/keys` and `POST /api/threads/{id}/run` (spends the user's provider budget).
- **B:** sends no CSRF token and has no place to hold one.
- **O:** `security: [localToken]` bearer (`openapi.yaml:28-29, 1167-1173`).
- **Threat model that already documented this:** `research/fable5/08-security-quota/THREAT_MODEL.md:110, 122-125` — "DNS rebinding / CSRF from A2 against 127.0.0.1"; mitigation is a per-session bearer token minted at startup **plus** `Host`/`Origin` validation **plus** loopback binding.
- **Who breaks:** the user, financially and confidentially, on any drive-by page. This is not theoretical — it is the exact scenario the project's own threat model calls out, and none of the three mitigations exist in code.
- **SSOT for v1:** **THREAT_MODEL.md §A2 + O's `localToken`.** Validate `Origin`/`Host` against `127.0.0.1`/`localhost` on every mutating request, and require the bearer token (see A1). Both are small; shipping without them is not defensible for software that holds API keys.

### X3 — No CSP, and the UI is served by the same origin as the key API
- **L:** `index.html` loads `/app.js` with no CSP header on any response; `_json` sets only `Cache-Control: no-store` (`server.py:62`); static and artifact responses set no cache or security headers.
- **B:** carefully avoids `innerHTML` with user data (UI_SPEC §9) — good, but that is a client-side mitigation with no server-side backstop.
- **O:** silent. THREAT_MODEL.md:115 specifies `default-src 'self'; base-uri 'none'; connect-src 'self'`, no inline script.
- **Who breaks:** compounds U5 into a key-exfiltration path.
- **SSOT for v1:** **THREAT_MODEL.md.** Add the CSP header to every response from `server.py`.

### X4 — Path traversal in static file serving (adjacent, but ship-blocking)
- **L:** `_send_file(self, WEB / path[len("/web/"):])` and `WEB / path.lstrip("/")` with no normalization or containment check (`server.py:104-109, 153-155`). A client that does not normalize (`curl --path-as-is 'http://127.0.0.1:8765/web/../../../../etc/passwd'`) reads arbitrary files — including `~/.atelier/keyring.json`.
- **B / O:** n/a (neither specifies static serving).
- **Who breaks:** combined with X2, a malicious local process or a rebinding attack reads the plaintext keyring off disk.
- **SSOT for v1:** **new.** Resolve and assert the path is inside `WEB` before reading. Three lines. Not optional.

---

## 9. Auth

### A1 — Three incompatible positions: required / absent / someone else's problem · **BLOCKER**
- **L:** no authentication on any route. `ATELIER_HOST` is env-overridable with no warning (`server.py:226`), so `ATELIER_HOST=0.0.0.0` publishes an unauthenticated, key-spending, key-hint-leaking API to the LAN.
- **B:** sends no `Authorization` header anywhere; `UI_SPEC.md:290` lists auth under **Out of scope** — "assumed session handled upstream of `/api`".
- **O:** global `security: [localToken]`, HTTP bearer, "per-install token generated at first launch and stored in the Keyring; defends the loopback port against other local processes" (`openapi.yaml:28-29, 1167-1173`).
- **Who breaks:** implement O as written and **100% of B's requests 401**, with no UI anywhere to enter or receive a token. Implement B as written and X2 stands. The two research deliverables directly contradict each other, and the live code sides with neither.
- **SSOT for v1:** **O's `localToken`, delivered the way B can actually consume it.** Mint a per-install token at first launch; have `server.py` inject it into `index.html` at serve time (or set a `SameSite=Strict` cookie plus an `Origin` check) so B never needs a token entry field; require it as a bearer header or cookie on every `/api/*` request. This keeps O's security property and B's zero-friction UX. Resolve the UI_SPEC §10 "out of scope" line explicitly — it is the single sentence that let this gap exist.

### A2 — Binding: env override with no guardrail
- **L:** `ATELIER_HOST` honored blindly (`server.py:226-228`).
- **O:** "loopback only; never bound to a public interface" (`openapi.yaml:25-26`).
- **Who breaks:** anyone who sets it to run the studio from another room, unaware there is no auth.
- **SSOT for v1:** **O.** Refuse a non-loopback bind unless a token is configured, and print a loud warning.

### A3 — Key write shape differs three ways
- **L:** `POST /api/keys {provider, key, base_url}` — one provider per call, returns the **full** status map (`server.py:169-179`).
- **B:** `PUT /api/keys {provider: rawKey, …}` — a map of all non-empty inputs at once, returns the masked map (`app.js:167, 1300-1312`).
- **O:** `PUT /keyring/{keyRef} {secret}` — one write-only secret per ref, `204` with no body; provider configs reference it by `key_ref` and raw secrets in a provider config are `422`-rejected before touching disk (`openapi.yaml:919-951, 804-840`).
- **Who breaks:** B's save button 501s today (T6); and the `key_ref` indirection in O has no counterpart in L at all, so O's whole provider-config model is unimplementable against the current keyring.
- **SSOT for v1:** **B's route and batch shape, O's write-only semantics.** `PUT /api/keys` accepting a map, returning masked status, never echoing a secret. Defer `key_ref` indirection to v2 — it only pays off with multiple configs per provider, which v1 does not have.

### A4 — Key masking: L leaks the first three characters of the live secret
- **L:** `hint = secret[:3] + "…" + secret[-4:]` (`helix/keyring.py:99`) — returned by an **unauthenticated** `GET /api/keys`.
- **B:** expects `{set, hint}` and renders `saved …abcd` — last-4 only (`app.js:1272-1273`).
- **O:** the keyring returns names and creation times **only**; "Secret values are never returned by any endpoint" (`openapi.yaml:901-917`).
- **Who breaks:** combined with X2, any web page the user visits can read a partial key plus its provider and base URL. Prefix+suffix is materially more disclosure than suffix alone.
- **SSOT for v1:** **B's shape, O's discipline.** Return `{set: bool, hint: "…" + last4}` and nothing else. Also fixes the field-name break in smoke test #3 (`configured` vs `set`), which today makes B report "not set" for keys that are configured.

### A5 — No secret scrubbing on the error path
- **L:** `except Exception as exc: _json(self, 500, {"error": str(exc)})` (`server.py:210-211`) — provider errors sometimes echo request headers or bodies. There is no scrubber in `helix/`.
- **B:** displays the error string in a toast / message bubble.
- **O / research:** `research/fable5/08-security-quota/POLICY.md:13` specifies `usage.scrub_secrets()` for `sk-…`, `AIza…`, `Bearer …`.
- **Who breaks:** a key ends up in a screenshot, a bug report, or a log.
- **SSOT for v1:** **POLICY.md.** Port `scrub_secrets()` into `helix/` and run every error string through it before it reaches a response or a log line.

---

## 10. Providers and model catalog

### P1 — `GET /api/providers` does not exist in L · **BLOCKER**
- **L:** no such route. `GET /api/catalog` exists but returns the TOP100 **GitHub repo list** (`server.py:122-124`, `helix/catalog.py`) — a completely unrelated payload that happens to sit at a plausible-looking path.
- **B:** `GET /api/providers` → `[{id, name, models}]` drives both selects; on failure it silently keeps a hardcoded catalog (`app.js:164, 1431`).
- **O:** `GET /providers` returns `ProviderConfig` rows — a spoke *registry* with `label`, `key_ref`, `capabilities`, `defaults`, `enabled` — structurally different from B's `{id, name, models}` (`openapi.yaml:784-803, 1435-1450`), and with no model list anywhere in the document.
- **Who breaks:** B falls back silently, so the user is offered Anthropic and fal.ai models that the live server cannot route (smoke test #2).
- **SSOT for v1:** **B's shape.** `GET /api/providers` → `[{id, name, models: [...], configured: bool}]`, generated from the live spoke registry + keyring status. O's `ProviderConfig` registry is a v2 feature (multiple labeled configs per provider); shipping it in v1 would require the `key_ref` indirection from A3 for no user-visible gain. Add `configured` so the picker can grey out providers with no key — the failure the current UI hides.

### P2 — Provider id sets barely intersect · **BLOCKER**
- **L:** spokes are `demo | openai | gemini | ollama` (`helix/conductor.py:242-257`, `helix/spokes/`); keyring `ENV_MAP` is `openai | gemini | anthropic | ollama | openai_compat` (`helix/keyring.py:10-16`) — note the keyring knows `anthropic` but there is **no anthropic spoke**.
- **B:** chat providers `openai | anthropic | google | fal`; key rows `openai | anthropic | google | fal | replicate` (`app.js:65-78`).
- **O:** free-form lowercase family string, examples `openai, anthropic, replicate, fal, local`.
- **Who breaks:** `google` (B) vs `gemini` (L) is the same vendor under two ids, so a Gemini key saved through B lands under a provider L never reads. `demo` — L's no-key fallback and the only thing that works out of the box — does not exist in B at all. B's default `anthropic/claude-sonnet-4.5` is unroutable on L, so the conductor silently degrades to a demo SVG and the user thinks Claude drew it.
- **SSOT for v1:** **L's ids** (they are what the code can actually call), with B's list trimmed to `demo | openai | gemini | ollama` and `google → gemini` renamed. Ship `anthropic` only if the spoke ships; keyring entries for providers with no spoke are a trap.

### P3 — Model lists have no source
- **L:** hardcoded per provider in the conductor (`_default_model`, `_image_model` — `helix/conductor.py:242-257`); the live UI is a free-text input (`web/index.html:62`).
- **B:** needs `models[]` per provider for its second `<select>`.
- **O:** no model-listing endpoint at all; `/providers/{id}/verify` returns a prose `detail` like "42 models visible" but no list.
- **Who breaks:** the model picker is either stale or wrong, forever.
- **SSOT for v1:** **B's shape, served from a static table.** Return a curated model list per provider from the server (one dict, versioned with the app) rather than live-querying provider APIs. Revisit in v2 with `/providers/{id}/models`.

---

## 11. Board and node model

### N1 — Three different canvas data models · **BLOCKER**
- **L:** flat per-project node list. `GET /api/projects/{id}/board` → `{nodes:[…]}` (`server.py:136-139`). No boards, no layers — the `nodes` table has `project_id` and nothing above it (`helix/store.py:48-60`).
- **B:** flat per-project node list at a **different path** — `GET /api/projects/{id}/nodes` → bare array (`app.js:157`), with a client-side monotonic `z` for bring-to-front.
- **O:** `Project → Board → Layer → Node`, with `GET /boards/{id}/scene` returning denormalized `SceneNode` render rows in paint order, plus layer visibility/lock and fractional node `z` (`openapi.yaml:469-682, 1370-1393`).
- **Who breaks:** B's board is empty against L purely because of the path (smoke test #5) — the two are one rename apart. O's model is a different schema entirely and would require new tables.
- **SSOT for v1:** **B's path over L's flat model.** Rename to `GET /api/projects/{id}/nodes` returning a bare array. **Explicitly defer O's board/layer tree to v2** — it is well-designed and it is the right destination, but it is a schema migration plus a renderer rewrite, and no v1 requirement needs layers. Record the deferral so the next reader does not re-litigate it.

### N2 — No node-create route in L · **BLOCKER**
- **L:** nodes exist only as conductor output (`helix/conductor.py:145-197`); `Memory.add_node` is never reachable over HTTP.
- **B:** `POST /api/projects/{id}/nodes` with a client-generated id, server may reissue (`app.js:158-159, 632-663`).
- **O:** `POST /boards/{boardId}/nodes` requiring `layer_id` + `kind` (`openapi.yaml:608-643`).
- **Who breaks:** every manual canvas action — double-click-to-add-note, `N`, `V` (video placeholder), and every uploaded image. All of B's toolbar fails (smoke test #10). The canvas is read-only-except-by-AI, which is not a design tool.
- **SSOT for v1:** **B.** `POST /api/projects/{id}/nodes` accepting the full node, echoing the server's canonical row. Accept the client id or reissue — B already handles both (`app.js:657-660`).

### N3 — Node field shapes disagree three ways
- **L:** columns `type`(`image|note`), `x,y,w,h,z(INTEGER)`, `artifact_id`, `text`, `meta{}` (`store.py:48-60`).
- **B:** `{type: note|image|video, x,y,w,h,z, data:{text? src? title? sub?}}` (UI_SPEC §6).
- **O:** `{kind: artifact|text|shape|frame|sticky|connector, layer_id, artifact_id, x,y,w,h, rotation, opacity, z(number, fractional), props{}}`.
- **Specific collisions:** `type` vs `kind`; `text` (column) vs `data.text` (nested) vs `props`; image source as `artifact_id` (L, O) vs `data.src` URL (B); `video` type exists only in B; `rotation`/`opacity` exist only in O; `z` integer (L) vs fractional (O).
- **Who breaks:** any node written by one contract and read by another loses fields silently — see N4 for the live instance of this.
- **SSOT for v1:** **B's wire shape, L's storage.** Keep `text` and `meta` as columns; serialize to B's `{type, data:{...}}` at the API boundary. Add `video` to the type enum (it is a placeholder node, no backend work). Skip `rotation`/`opacity` for v1; add `layer_id` never — see N1.

### N4 — `update_node` silently drops the field B sends most · **BLOCKER**
- **L:** `update_node` filters to `{"x","y","w","h","z","text","meta"}` and ignores everything else, then returns **200 with the unchanged row** (`helix/store.py:251-266`).
- **B:** note autosave sends `{data: {text}}` (nested, debounced 500 ms — UI_SPEC §4.3); geometry sends `{x,y,w,h,z}` (fine).
- **O:** PATCH accepts `props` (its equivalent of `data`).
- **Who breaks:** **every note the user types is lost on reload, with a success response and no error.** This is the single most damaging mismatch in the diff: it is silent, it destroys user-authored content (not regenerable AI output), and nothing in the UI hints at it.
- **SSOT for v1:** **B.** Accept `data` on PATCH, map it onto `meta`/`text`, and — regardless of shape — **reject unknown fields with `422` instead of ignoring them.** Silent field-dropping is how this class of bug survives review.

### N5 — `update_node` on an unknown id crashes the connection
- **L:** `APP.memory.update_node(parts[2], **{k: body[k] for k in body})` (`server.py:216`) → `UPDATE` matches zero rows → `get_node` does `dict(fetchone())` on `None` → uncaught `TypeError` (only `json.JSONDecodeError` is caught in `do_POST`) → traceback and a broken connection rather than a 404. A body containing a `node_id` key raises `TypeError: got multiple values` the same way.
- **B:** hits this on the first drag of any client-created node (smoke test #11).
- **O:** `404` for a missing node.
- **Who breaks:** the user sees a network error with no explanation; the operator sees a stack trace per drag.
- **SSOT for v1:** **O.** Return `404` for unknown ids, `422` for unknown fields, and add a catch-all handler that converts an unexpected exception into a scrubbed `500` JSON body (A5) instead of a dropped connection.

### N6 — PATCH response body: `204` vs `200 Node`
- **L:** always `200` with the node. **B:** accepts either (`app.js:139`). **O:** `200 Node` for PATCH, `204` only for DELETE.
- **Who breaks:** nobody today; it is a latent inconsistency worth pinning while the contract is being written.
- **SSOT for v1:** **O.** `200` + entity for PATCH, `204` for DELETE.

---

## 12. Threads and messages

### K1 — `topic` vs `title` · **BLOCKER**
- **L:** `threads.topic` + `threads.mode` (`store.py:19-26`); `POST` reads `body.get("topic")` (`server.py:185-192`); the live UI renders `t.topic` (`web/app.js:62`).
- **B:** sends and renders `title` (`app.js:153, 987`).
- **O:** `title` + `status` (`openapi.yaml:1268-1276`).
- **Who breaks:** every thread B creates is stored untitled, and the dropdown renders literal `undefined` (smoke test #6). Two of three contracts say `title`.
- **SSOT for v1:** **B + O — `title`.** Rename the column; update the live UI's one reference.

### K2 — Where `mode` lives is undecided
- **L:** a column on `threads` (`store.py:23`), also accepted per-run (`server.py:206`).
- **B:** client-side per-message, persisted in `localStorage` prefs, sent on every chat call (UI_SPEC §4.5).
- **O:** does not model mode at all — it is a Conductor `constraints` concern.
- **Who breaks:** ambiguity about whether switching Fast/Thinking mid-thread rewrites the thread's mode or applies per-turn. All three answer differently; the behavior a user sees depends on which contract you implement.
- **SSOT for v1:** **B — per-message.** Store `mode` on the message row (it is already needed for the metadata line, S5), and drop it from `threads`. A thread-level mode cannot express the common case of one thinking turn inside a fast conversation.

### K3 — Message role enum: `assistant` is not legal in O
- **L:** writes `"user"` / `"assistant"` (`helix/conductor.py:96, 226`). **B:** expects `user|assistant`. **O:** `user|conductor|spoke|system|note` — **no `assistant`** (`openapi.yaml:1234-1236`).
- **Who breaks:** a snapshot exported from L and validated against O rejects every assistant message. Any strict client generated from O rejects the live stream.
- **SSOT for v1:** **L + B — `user|assistant`,** with `system` and `note` added from O. `conductor`/`spoke` are a provenance distinction that the rungs model needs and v1 does not have.

### K4 — Message ordering: float `created_at` vs gap-free `seq`
- **L:** ordered by `created_at` float seconds (`store.py:174-180`) — two messages written inside the same conductor run can tie, and the ordering is then arbitrary.
- **B:** renders in received order.
- **O:** per-thread, gap-free `seq` starting at 0, with an `after_seq` query for incremental fetch (`openapi.yaml:246-252, 1283`).
- **Who breaks:** a user whose turn and the assistant reply occasionally render in the wrong order; and any future incremental-load or resume-stream feature, which needs a cursor.
- **SSOT for v1:** **O — add `seq`.** It is one column and it is a precondition for reconnect-after-stream-drop, which SSE will need.

### K5 — No direct message-append route
- **L:** none — messages appear only as a side effect of `/run`. **B:** never needs one (chat does it server-side). **O:** `POST /threads/{id}/messages` (`openapi.yaml:261-284`).
- **Who breaks:** nobody in v1. Worth noting so the O route is not mistaken for implemented.
- **SSOT for v1:** **skip.** Document as v2.

---

## 13. Brand kit

### B1 — Three different resource models · **BLOCKER**
- **L:** an opaque JSON blob column on `projects`; read via `GET /api/projects/{id}` (`brand_kit` field), written via `POST /api/projects/{id}/brand {brand_kit}` (`server.py:193-195`, `store.py:124-130`). The live UI edits it as **raw JSON in a textarea** (`web/index.html:46`).
- **B:** a singleton sub-resource — `GET`/`PUT /api/projects/{id}/brand-kit` — with a structured editor: palette rows, fonts, logo, voice (`app.js:169-171`; UI_SPEC §4.7).
- **O:** a versioned collection — `GET`/`POST /projects/{id}/brand-kits`, `POST /brand-kits/{id}/activate` with an at-most-one-active invariant (I6), and `POST /brand-kits/{id}/assets` (`openapi.yaml:687-779`).
- **Who breaks:** B's brand-kit panel 404s on read and 501s on save (smoke test #7, #15). The live raw-JSON textarea lets a user save a kit that B cannot render.
- **SSOT for v1:** **B — singleton `GET`/`PUT /api/projects/{id}/brand-kit`,** stored in L's existing blob column. O's multi-kit/activate model is a real feature (A/B-ing brand systems) and a real cost (new table, activation invariant, asset join); defer it. Retire the raw-JSON textarea — an unvalidated free-text schema editor in the shipping UI guarantees B2.

### B2 — Field shapes are mutually unreadable
- **L (seed):** `{name, palette: ["#0c0d10", …], voice: "quiet, precise, editorial"}` — palette is a flat string list (`server.py:44-49`).
- **B:** `{colors: [{name, value}], fonts: {heading, body}, logo_url, voice}` — palette is `colors`, entries are objects with `value`.
- **O:** `{name, palette: [{name, hex}], typography: {}, voice: {} }` — palette entries use `hex`, and **`voice` is an object**, not a string.
- **Who breaks:** `palette` vs `colors`; `value` vs `hex`; `voice` string vs object. The live seed kit renders as an empty palette in B. And the conductor just JSON-dumps whatever it finds into the prompt (`helix/conductor.py:260-263`), so a malformed kit degrades generation quality invisibly rather than erroring.
- **SSOT for v1:** **B.** `{colors:[{name,value}], fonts:{heading,body}, logo_url, voice: string}` — it is the only shape with a real editor behind it. Migrate the seed kit. Validate on write so the conductor never receives a shape it will silently ignore.

### B3 — Logo upload depends on the missing upload route
- **B:** the logo drop zone posts to `/api/uploads` (UI_SPEC §4.7). **L:** U1. **O:** `POST /brand-kits/{id}/assets` referencing an existing artifact.
- **SSOT for v1:** **B**, unblocked by U1; store `logo_url` as an artifact id rendered through `/api/artifacts/{id}/content`.

---

## 14. Usage, budget, and the conductor run

### C1 — Usage ledger schemas do not convert
- **L:** `{provider, model, unit_kind: tokens_in|tokens_out|images, units, estimated_usd, thread_id, created_at}` (`store.py:61-70`); exposed as `GET /api/usage` → `{events, totals}`.
- **B:** does not read usage at all.
- **O:** `/usage/events` + `/usage/summary` with `spoke`, `operation`, `unit_type: tokens|pixels|seconds|characters|requests`, `cost_micros`, `project_id`, `run_id`, `status`, `latency_ms` (`openapi.yaml:956-1015, 1452-1493`).
- **Who breaks:** `provider` vs `spoke`; `unit_kind` values that do not exist in O's enum; **no `project_id` on live rows**, so per-project spend — the number a user actually wants — is unanswerable today.
- **SSOT for v1:** **O's field names and units, L's endpoint.** Keep `GET /api/usage`, adopt `cost_micros`, `unit_type`, `project_id`, `status`, `latency_ms`. Adding `project_id` now is far cheaper than backfilling it.

### C2 — Budget enforcement exists in L but is invisible and un-negotiated
- **L:** real and working — `ATELIER_DAILY_BUDGET` (default $10) and `ATELIER_THREAD_BUDGET` (default $2), checked in `usage.record` via `assert_budget` (`helix/usage.py:15-16, 87-101`).
- **B:** no concept of a budget; no spend display; no place to show a cap.
- **O:** per-turn `constraints: {max_cost_micros}` on the conductor turn (`openapi.yaml:1128-1131`) — a different mechanism (per-request ceiling vs rolling window).
- **Who breaks:** the user, who hits an invisible cap they never set and cannot see. There is no `GET /api/budget`, so no client can display remaining spend.
- **SSOT for v1:** **L's rolling-window mechanism, exposed.** Add budget state to `GET /api/usage` (`{daily_limit, daily_spent, thread_limit, thread_spent}`) and render it in B next to the spend meter from T5. Add O's per-turn ceiling in v2.

### C3 — Budget enforcement is post-hoc
- **L:** `assert_budget` runs inside `record`, i.e. **after** the provider call has already been made and paid for (`helix/usage.py:98-109`). The cap stops the *next* call, not the one that crossed the line.
- **Who breaks:** a single expensive turn can overshoot the daily cap arbitrarily — for image generation with `count: 2` across 4 weave items, by up to 8 images.
- **SSOT for v1:** **new.** Pre-flight an estimate before each spoke call and refuse if the projected total exceeds the cap. The estimator already exists (`estimate_usd`).

### C4 — Budget rejection surfaces as HTTP 500 · **BLOCKER**
- **L:** `BudgetExceeded(RuntimeError)` is not in the conductor's `except (SpokeError, ValueError, JSONDecodeError)` list (`helix/conductor.py:127`), so it propagates to `server.py:210-211` → `500 {"error":"daily budget $10.00 exceeded ($10.4021)"}`.
- **B:** renders it as a generic failed toast; SSE has an `error` frame that would be the right channel, but there is no route to emit it from.
- **O:** would express this as a `422`/`409` with a stable code.
- **Who breaks:** the most likely real-world error in a BYOK product reads as a server crash. Users will file it as a bug.
- **SSOT for v1:** **O's error contract (T8).** `402`/`409` with `{error: "budget_exceeded", detail: …}`, and a matching SSE `error` frame.

### C5 — Weave fan-out has no user confirmation
- **L:** up to 4 weave items × `count` 2 = **8 image generations per turn**, decided by the planner LLM with no preview and no confirmation (`helix/conductor.py:140-143`).
- **B / O:** neither models a confirmation step; O's `plan` SSE event would be the natural place.
- **Who breaks:** a user's wallet, on a single ambiguous prompt.
- **SSOT for v1:** **S2's `plan` event, used as a gate.** Emit the plan first, show the intended asset count, and either require confirmation above a threshold or show a running cost during the stream.

### C6 — Run result is computed and discarded
- **L:** `/run` returns `{plan, artifacts, nodes, message}` (`server.py:213`) and the live UI throws it away, calling `bootProject()` to refetch everything (`web/app.js:206`).
- **B:** expects the terminal `done` frame to carry the persisted assistant message.
- **O:** the `202` carries nothing; the client follows SSE.
- **SSOT for v1:** **B.** `done {message}` plus `node.placed` events (S2), so the board updates incrementally with no full refetch.

---

## 15. Endpoint-by-endpoint index

Legend: ✅ present and compatible · ⚠️ present but shape/name differs · ❌ absent

| Capability | L | B | O | v1 SSOT |
|---|---|---|---|---|
| health | ✅ `GET /api/health` | ✅ same | ❌ | L/B |
| list projects | ⚠️ wrapped | ⚠️ bare array | ⚠️ bare array | bare array |
| create project | ✅ | ✅ | ✅ | L |
| get project | ✅ | ❌ | ✅ | L |
| rename project | ❌ | ❌ | ✅ PATCH | O |
| archive project | ❌ | ❌ | ✅ | O |
| export project | ❌ | ❌ | ✅ snapshot | O |
| list threads | ⚠️ wrapped, `topic` | ⚠️ `title` | ⚠️ `title` | B/O `title` |
| create thread | ⚠️ `topic` | ⚠️ `title` | ⚠️ `title` | B/O |
| rename/archive thread | ❌ | ❌ | ✅ PATCH | O |
| list messages | ⚠️ wrapped | ⚠️ bare | ⚠️ bare + `seq` | O |
| append message | ❌ | ❌ | ✅ | defer |
| chat / turn | ⚠️ sync `/run`, `prompt` | ⚠️ SSE `/chat`, `message` | ⚠️ 202 + SSE, `instruction` | **B** |
| cancel turn | ❌ | ❌ | ⚠️ loom only | new (abort) |
| list nodes | ⚠️ `/board`, wrapped | ⚠️ `/nodes`, bare | ⚠️ `/boards/{id}/scene` | **B** |
| create node | ❌ | ✅ | ✅ (board-scoped) | B |
| update node | ⚠️ drops `data` | ✅ | ✅ | B + 422 |
| delete node | ❌ 501 | ✅ | ✅ | B/O |
| boards / layers | ❌ | ❌ | ✅ | defer to v2 |
| upload | ❌ | ✅ `/uploads` | ⚠️ `/artifacts` | **B** route, O storage |
| artifact metadata | ❌ | ❌ | ✅ | O |
| artifact bytes | ⚠️ forced `.bin` attach | (via url) | ✅ `/content` | O |
| artifact lineage | ❌ | ❌ | ✅ | defer |
| brand kit | ⚠️ blob on project | ⚠️ singleton PUT | ⚠️ collection + activate | **B** |
| providers | ❌ (catalog ≠ providers) | ✅ | ⚠️ registry rows | **B** |
| verify provider | ❌ | ❌ | ✅ | nice-to-have |
| get keys | ⚠️ `configured`, 3-char hint | ⚠️ `set`, last-4 | ⚠️ names only | B shape, O discipline |
| save keys | ⚠️ POST, single | ⚠️ PUT, map | ⚠️ PUT per ref | B |
| delete key | ⚠️ code exists, unrouted | ❌ | ✅ | O |
| usage events / summary | ⚠️ `/api/usage`, USD float | ❌ | ✅ micros | O fields, L route |
| budget visibility | ❌ (enforced, unexposed) | ❌ | ⚠️ per-turn constraint | new |
| loom runs | ❌ | ❌ | ✅ | defer to v2 |
| rungs / provenance | ❌ | ❌ | ✅ | defer to v2 |
| auth | ❌ | ❌ (out of scope) | ✅ bearer | **O** |
| CORS / origin check | ❌ | same-origin | ❌ | same-origin + origin check |

---

## 16. Minimum cut to ship v1

Ordered by dependency, not by size. Each line resolves the mismatches in brackets.

**Security — do first; the rest is unshippable without it**
1. Origin/Host validation + per-install token injected into `index.html` [X2, A1, A2]
2. CSP header on every response; path-traversal containment in `_send_file` [X3, X4]
3. Key hint → last-4 only; `scrub_secrets()` on every error and log path [A4, A5]

**Transport — one pass over `server.py`**
4. Real verb dispatch: `PUT`, `DELETE`, `OPTIONS`, `HEAD`; `HTTP/1.1`; SSE writer [T6, T7, T9]
5. Bare-array list responses; `{error, detail}` bodies; `404` on unknown id; `422` on unknown field; catch-all → scrubbed JSON [T2, T8, N5, N4]
6. Id prefixes; epoch-ms timestamps; `cost_micros` [T3, T4, T5]

**The seven named gaps**
7. `POST /api/chat` SSE wrapping the existing conductor — `thinking.delta`, `message.delta`, `node.placed`, `usage`, `error`, `done`; client-side abort + Stop button [S1–S5]
8. `POST /api/uploads` with a size cap, MIME allowlist, sha256 dedupe, and SVG neutralization; split `/api/artifacts/{id}` (JSON) from `/api/artifacts/{id}/content` (bytes, inline by default, `?download=1` for attachment) [U1–U5]
9. `DELETE /api/nodes/{id}`; `POST /api/projects/{id}/archive`; `PATCH /api/threads/{id}`; route the existing `Keyring.delete` [D1, D2, D3, D5]
10. `GET /api/projects/{id}/snapshot` → `helix-snapshot/1` [E1]
11. Health with version + db/runtime status; add `/health` to the OpenAPI doc [H1, H2]

**Contract alignment so B works against L**
12. `topic` → `title`; `mode` moves to the message; add `seq`, `thinking`, `provider`, `model` columns [K1, K2, K4, S5]
13. `/board` → `/nodes` (bare array); `POST /api/projects/{id}/nodes`; accept `data` on PATCH [N1, N2, N3, N4]
14. `GET`/`PUT /api/projects/{id}/brand-kit` with B's field shape; retire the raw-JSON textarea [B1, B2]
15. `GET /api/providers` with `configured` flags; align ids on `demo|openai|gemini|ollama`; batch `PUT /api/keys` [P1, P2, P3, A3]
16. Usage: add `project_id`, `cost_micros`, `unit_type`; expose budget state; pre-flight the cap; `budget_exceeded` as a real error code [C1–C4]

**Explicitly deferred to v2 — write this down so it is not re-litigated**
Boards and layers (N1) · rungs and lineage · Loom runs and the run SSE · brand-kit versioning and activation · the `ProviderConfig`/`key_ref` registry · direct message append · format-converting export, PNG/PDF/SVG/MP4 and batch (E2, E3).

---

## 17. Where the process failed

Worth recording, because the same failure will otherwise recur:

- **B and L were never run against each other.** The board UI's own quickstart (`UI_SPEC.md:23-28`) can only produce demo mode, because there is no CORS and no dev proxy (X1). A UI that transparently falls back to seeded fake data is very good UX and very effective at hiding the fact that the backend contract does not match — the pill turns amber and everything still works.
- **The OpenAPI was written against a different store.** `04-helix-arch/store.py` (1,201 lines, boards/layers/rungs/loom) is not `helix/store.py` (304 lines). `atelier/ARCHITECTURE.md:48-50` is honest about this — "the live `helix/store.py` stays the small runtime" — but the OpenAPI document does not say so anywhere in its own text, so a reader takes it for the API of the thing that is running.
- **Auth was declared out of scope by one deliverable and mandatory by another**, and neither noticed (A1). `UI_SPEC.md:290` and `openapi.yaml:28` are direct contradictions, and the threat model that would have settled it (`08-security-quota/THREAT_MODEL.md:122-125`) is a third deliverable neither one cites.

The concrete fix: pick the v1 SSOT per §16, write it into a single document that both the server and the board UI cite by name, and add a smoke test that runs B's `RemoteBackend` calls against a live `server.py` in CI. Every one of the 19 blockers above would have been caught by that one test.
