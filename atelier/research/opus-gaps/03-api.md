# Atelier API contract gaps — three-way diff

**Author:** Opus#3 of 10 · **Scope:** read-only analysis; `/workspace` unmodified by me.

> ### State pinned
> `/workspace` is being edited by other agents while I work. `atelier/server.py` grew from 238 to 415 lines mid-analysis (18:49 → 18:58 UTC) and gained streaming, upload, delete, export, quote, undo and camera routes. **Everything below describes exactly this state:**
>
> | File | md5 |
> |---|---|
> | `atelier/server.py` | `e8f43b5be6299fe224d4aabcb67bb3d7` |
> | `atelier/web/app.js` | `5a55d64c7e1d1fe85d8de28dedc4ad81` |
> | `atelier/research/fable5/06-board-ui/app.js` | `e1262fbbd82d87bf8c84c632dfdc484a` |
> | `atelier/research/fable5/04-helix-arch/openapi.yaml` | `3f9b4b50f18aa2f73eed2069464ec3fe` |
>
> Snapshot taken 2026-08-21T19:01:36Z, working tree on `688305f` with uncommitted changes. Re-verify the live column before acting; the two research contracts have not moved.
>
> **Re-verified at 19:09Z** against `server.py` md5 `380ac6c34e385ffbb11c584a5ee5189c` (457 lines): the route surface is byte-for-byte the same set of endpoints, and every finding below still holds. Still absent at that hash: `do_PUT`/`do_OPTIONS`/`do_HEAD`, `/api/providers`, `/api/chat`, project archive, `Origin` validation, static-path containment, and the `on_event` wiring that would make SSE incremental.

## The three contracts

| Tag | Contract | Files |
|---|---|---|
| **L** | Live implementation | `atelier/server.py`, `atelier/web/app.js`, `atelier/web/index.html`, `atelier/helix/{store,keyring,conductor,usage,quote,exportzip,loom}.py` |
| **B** | Research board UI | `atelier/research/fable5/06-board-ui/app.js`, `.../UI_SPEC.md` (§7 contract table, §7.1 SSE) |
| **O** | Research OpenAPI | `atelier/research/fable5/04-helix-arch/openapi.yaml` (+ its own `store.py`, `schema.sql`) |

---

## 0. Headline

L has moved fast in the last hour and now has *something* for six of the seven areas in the brief. **None of them matches either research contract**, and in three cases the live implementation is a fourth design that neither research document anticipated. The gap did not close; it widened in a new direction.

Concretely: **B and L now share two working endpoints — `GET /api/health` and `DELETE /api/nodes/{id}`.** Everything else 404s, 501s, returns the wrong envelope, or returns 2xx while silently discarding the user's content.

Counted below: **56 mismatches**, of which **18 are ship-blocking** (marked **BLOCKER**) — a user hits them in a normal first session and the product is visibly broken or silently loses work. The blockers are listed in §16.

| Feature | L (live, as pinned) | B (board UI) | O (OpenAPI) | Verdict |
|---|---|---|---|---|
| Streaming | `?stream=1` → SSE, but **all events are buffered and replayed after the run finishes**; no token deltas anywhere; the live UI calls `?stream=0` | one-call `POST /api/chat`, incremental token deltas | two-call `202` + `GET …/events` | shape #4; not actually incremental |
| Upload | `POST /api/projects/{id}/upload`, **base64-in-JSON**, 5 MB, auto-creates a node, → `{artifact,node}` | `POST /api/uploads` multipart → `{id,url,kind}` | `POST /projects/{id}/artifacts` multipart → `Artifact` | 3 different paths, 3 different encodings |
| Delete project | none | none | `POST /projects/{id}/archive` | only O has an answer |
| Delete thread | none | none | `PATCH /threads/{id}` → archived | only O has an answer |
| Delete node | ✅ `DELETE /api/nodes/{id}` → `200 {ok}` | ✅ expects `204`, tolerates `200` | ✅ `204` | **works** |
| Export | ✅ `GET /api/projects/{id}/export` → ZIP — but **omits every thread and message** | nothing | `GET /projects/{id}/snapshot` → `helix-snapshot/1` JSON | ships, loses the conversation |
| Health | ✅ `{ok,name,architecture,evolve_rounds}` | ✅ probes it, checks `res.ok` only | **no `/health` path exists** | L↔B agree, O omits it |
| CORS | zero headers; `OPTIONS` → 501 | assumes same-origin `/api` | not addressed | nothing implemented |
| Auth | none | out of scope (UI_SPEC §10) | `security: [localToken]` bearer, global | 3-way contradiction |

**Recommended single source of truth for v1, in one line:** freeze **L's routing and transport** (`/api/*` on the origin that serves the UI), adopt **B's field names and body shapes** (UI_SPEC §7 — the only contract with a consumer that renders every field), adopt **O only where L and B are both silent or wrong** (archive semantics, snapshot completeness, the artifact metadata/content split, the error envelope, and the security model in `research/fable5/08-security-quota/THREAT_MODEL.md`), and defer O's boards/layers/rungs/lineage/loom/provider-registry tree to v2.

**And one process change that matters more than any single fix:** the live server is now *ahead of both research documents* in several places (quote, undo, camera, variants, spot-edit). Those documents are no longer specifications — they are stale proposals being silently contradicted by code. Pick one document to be normative and make it track the code, or the next agent will re-derive this same list.

---

## 1. Smoke test: what happens today if you serve B from L

The fastest proof of the gap. Serving `06-board-ui/` from `server.py`'s static handler:

| # | Action | Call | Result |
|---|---|---|---|
| 1 | boot | `GET /api/health` | 200 → pill says "Live /api" ✅ |
| 2 | boot | `GET /api/providers` | 404 → silently falls back to hardcoded `anthropic/claude-sonnet-4.5`, which L cannot route |
| 3 | boot | `GET /api/keys` | 200, but L returns `{configured,source,base_url,hint}` and B reads `.set` → **every key row shows "not set" even when keys are configured** |
| 4 | boot | `GET /api/projects` | 200 `{projects:[…]}`; B's `asList()` accepts only a bare array or `{items:[…]}` → sees `[]` → **auto-creates "Untitled project" on every page load, and nothing can ever delete them** |
| 5 | open project | `GET /api/projects/{id}/nodes` | 404 (L serves the board at `/board`) → canvas renders empty despite having nodes |
| 6 | open project | `GET /api/projects/{id}/threads` | 200 wrapped → `[]` → creates a thread with `{title:"General"}`; L reads `body["topic"]` → stores `""` → dropdown renders literal `undefined` |
| 7 | open project | `GET /api/projects/{id}/brand-kit` | 404 → falls back to a default kit; the user's real kit is invisible |
| 8 | open thread | `GET /api/threads/{id}/messages` | 200 wrapped → `[]` → **all chat history invisible** |
| 9 | send message | `POST /api/chat` | 404 → toast `POST /chat → 404`. Chat is dead. |
| 10 | add note | `POST /api/projects/{id}/nodes` | **201** — route now exists, but L reads `text`/`type` and ignores B's nested `data:{text}` → **the note is created empty**, and the typed text is gone on reload |
| 11 | drag a node | `PATCH /api/nodes/{id}` | works for server-issued ids; for an id L never issued, `update_node` → `get_node` → `dict(None)` → **uncaught `TypeError`, connection reset** instead of 404 |
| 12 | delete node | `DELETE /api/nodes/{id}` | **200 `{ok:true}`** ✅ (B tolerates non-204) |
| 13 | upload / drop | `POST /api/uploads` | 404 — L's upload is at `/api/projects/{id}/upload` and takes base64 JSON, not multipart |
| 14 | save keys | `PUT /api/keys` | 501 Unsupported method |
| 15 | save brand kit | `PUT /api/projects/{id}/brand-kit` | 501 Unsupported method |

Working: health, project create, thread create (untitled), node delete, node create (blank). Everything else broken — and five failures (#3, #4, #6, #8, #10) are *silent*: the UI reports success or emptiness rather than an error. #10 is new and is the worst of them, because the route landing made the failure quieter, not louder.

An O-generated client fails earlier still: wrong port (8787 vs 8765), wrong prefix (`/v1` vs `/api`), and a mandatory `Authorization: Bearer` that L never reads.

---

## 2. Transport, framing, identity

### T1 — Base URL and path prefix disagree three ways · **BLOCKER (O path)**
- **L:** `/api/*` on `127.0.0.1:8765`, same origin as the UI (`server.py:402-406`).
- **B:** `const API = "/api"`, relative by design (`06-board-ui/app.js:63`; UI_SPEC §7).
- **O:** `servers: http://127.0.0.1:8787/v1` (`openapi.yaml:24-26`).
- **Who breaks:** anyone generating a client from O; any proxy or desktop-shell author; the spec's own `events_url` examples (`/v1/conductor/turns/…`).
- **SSOT for v1:** **L.** Keep `/api` same-origin — it is what makes the "no CORS" posture arguable at all. Delete or re-point O's server block.

### T2 — List responses: wrapped object vs bare array · **BLOCKER**
- **L:** `{"projects":[…]}`, `{"threads":[…]}`, `{"messages":[…]}`, `{"nodes":…}` (`server.py:179, 193, 198, 216`).
- **B:** `asList()` unwraps a bare array or `{items:[…]}`, nothing else (`06-board-ui/app.js:143`).
- **O:** bare arrays everywhere.
- **Who breaks:** every list in B renders empty; the empty project list triggers junk-project creation on every reload (#4); the empty message list looks like history loss (#8).
- **SSOT for v1:** **O + B — bare arrays.** Two of three already agree and B's unwrapper is one line. Change `server.py`; update the five `data.x || []` sites in `web/app.js`.

### T3 — Id format
- **L:** `uuid4().hex`, unprefixed (`helix/store.py:78-79`). **B:** `crypto.randomUUID()`, expects reissue. **O:** prefixed ULIDs, `prj_`/`thr_`/`art_`/`nod_` (`openapi.yaml:18-19`).
- **Who breaks:** anything routing or validating on prefix; support staff reading a bug report cannot tell a thread id from an artifact id.
- **SSOT for v1:** **O's prefix convention, L's generator.** `prj_<hex>`. Cheap, reversible, pays for itself in debugging.

### T4 — Timestamps: float seconds vs integer milliseconds
- **L:** `created_at REAL` = `time.time()` (`store.py:52-53, 74-76`). **B:** ms; does not currently render them. **O:** "unix epoch **milliseconds**", `int64` (`openapi.yaml:20`).
- **Who breaks:** latent until someone puts a time on a chat bubble, then everything is 1970. Also breaks the export manifest and any `since=` filter.
- **SSOT for v1:** **O — integer ms.** Convert at the store boundary now, while there is one writer.

### T5 — Money: float USD vs integer micro-USD
- **L:** `estimated_usd REAL`, `round(…,6)` (`helix/usage.py:55-66`), summed with `toFixed(4)` (`web/app.js:257`). **B:** no spend display at all. **O:** `cost_micros` integer (`openapi.yaml:21, 1470`).
- **Who breaks:** float dollars accumulate error across thousands of rows and do not convert losslessly. Separately: **B ships with no spend meter**, which for BYOK means the user watches their own money go without an in-product signal.
- **SSOT for v1:** **O — `cost_micros`.** And port L's spend pill and quote readout into B before ship; that is a product requirement, not polish.

### T6 — `PUT`, `OPTIONS`, `HEAD` still unimplemented · **BLOCKER**
- **L:** `do_GET`, `do_POST`, `do_PATCH` (aliased to POST), `do_DELETE` (`server.py:146, 236, 389, 398`). `BaseHTTPRequestHandler` answers `PUT`/`OPTIONS`/`HEAD` with **501**.
- **B:** `PUT /api/keys`, `PUT /api/projects/{id}/brand-kit` (`app.js:167, 171`).
- **O:** `PUT /keyring/{keyRef}`, plus `DELETE` on keyring and layers.
- **Who breaks:** B's key save and brand-kit save (#14, #15). `OPTIONS` → 501 also forecloses any cross-origin story (X1).
- **SSOT for v1:** **B + O.** Add `do_PUT`, `do_OPTIONS`, `do_HEAD`. ~15 lines; unblocks two of B's three remaining write paths.

### T7 — `do_PATCH` aliases `do_POST`, so PATCH routing is accidental
- **L:** `def do_PATCH(self): self.do_POST()` (`server.py:398-399`). `PATCH /api/nodes/{id}` works only because an identically-shaped POST route exists; `PATCH /api/projects/{id}` (O's rename) falls through to `unknown POST` 404.
- **Who breaks:** renaming a project is impossible today.
- **SSOT for v1:** **L's paths with real `(method, path)` dispatch.** Keep only the PATCHes v1 needs: node, project rename, thread rename/archive.

### T8 — Error envelope: `{error, code}` vs `{error, detail}`
- **L:** improved — `{"error": str, "code": "budget_exceeded"|"unofficial_host"|<ConductorError.code>, "ok": false}` on the run and keys paths (`server.py:260, 370, 373, 376`), but bare `{"error": …}` everywhere else (`104, 190, 211, 221, 228, 244, 387, 396`).
- **B:** reads only `res.status`, surfacing `METHOD path → status` (`06-board-ui/app.js:138`). The **live** UI does read `data.code` (`web/app.js:22`), so the two clients disagree about the envelope too.
- **O:** `Error {error, detail}` — `error` a stable code, `detail` prose (`openapi.yaml:1221-1228`).
- **Who breaks:** L's `error` holds prose while O's holds the machine code, and L puts the machine code in a third field. Any client written against O misreads every live error.
- **SSOT for v1:** **O's field names with L's discipline.** `{error: <stable_code>, detail: <prose>}` on **every** path, and teach B's `apiFetch` to read the body on `!res.ok`. L is already 70% there — it just named the fields differently.

### T9 — HTTP/1.0 with `Content-Length` on every JSON response
- **L:** `protocol_version` is never set, so responses are HTTP/1.0, no keep-alive; `_json` always sets `Content-Length` (`server.py:83-90`). `_sse_result` correctly omits it (`129-139`) but inherits HTTP/1.0, so the stream is close-delimited with no chunked encoding.
- **Who breaks:** this is the transport reason real streaming still cannot work — see S1.
- **SSOT for v1:** **B/O.** Set `protocol_version = "HTTP/1.1"` and flush per frame.

---

## 3. Streaming

### S1 — SSE exists but is a post-hoc replay, not a stream · **BLOCKER**
- **L:** `POST /api/threads/{id}/run?stream=1` → `_sse_result` (`server.py:357, 378-380`). But look at the order: `app.conductor.run(...)` is called **without** the `on_event` callback it accepts (`helix/conductor.py:114`), runs to completion — planner chat, up to 8 image generations, critic pass — and only then does `_sse_result` iterate `result["events"]` and write them all at once (`server.py:134-139`). The user waits the full duration, then receives the entire history in one burst. It is SSE-shaped, not SSE-behaved.
- **Also:** no spoke can stream. `ollama_spoke.py:41` still hardcodes `"stream": False`; `openai_spoke`/`gemini_spoke` expose only `chat()`/`image()`. So there are no token deltas to emit even if the plumbing were live. Research already solved this — `03-keyring-spokes/spokes_openai.py:186` `_chat_stream`, `spokes_anthropic.py:131`, `spokes_gemini.py:183`, with recorded `.sse` fixtures.
- **And:** the live UI explicitly requests `?stream=0` (`web/app.js:332`), so the SSE route has **zero consumers**.
- **B:** `POST /api/chat`, `Accept: text/event-stream`, `res.body.getReader()`, `\n\n` frames; the whole chat dock is built on incremental append with a blinking cursor and a live Reasoning block (`06-board-ui/app.js:187-226`; UI_SPEC §4.5).
- **O:** `POST /conductor/turns` → `202 {turn_id, events_url}` then `GET …/events` (`openapi.yaml:1105-1162`).
- **Who breaks:** every user. A thinking-mode run with four variants is tens of seconds of frozen button. "Thinking vs fast" is the product's headline differentiator and it is invisible.
- **SSOT for v1:** **B — one-call `POST /api/chat` returning SSE.** O's two-call shape needs a turn registry, an event bus, and reconnect/replay semantics — real infrastructure for a single-user local app. B's shape needs no server-side turn state and already handles the non-streaming degradation (UI_SPEC §7.1: if `done` carries full `content` and no deltas arrived, render at once).
- **The fix is unusually cheap and it is worth saying precisely:** `conductor.run` already accepts `on_event`. Pass a callback that writes an SSE frame and flushes, set `protocol_version = "HTTP/1.1"`, and phase/quote events become genuinely live with **no client change**. Token deltas then follow from porting `_chat_stream` off the research spokes. Two independent steps, first one is a few lines.

### S2 — Four disjoint event vocabularies
- **L:** `phase` (`phase=brief|score|route|weave|critique|pin|done`), `quote`, and a terminal `result` frame carrying the whole run dict (`conductor.py:130, 141, 331, 341`; `server.py:137`).
- **B:** `thinking.delta {delta}`, `message.delta {delta}`, `done {message}`, `error {message}`; default event is `message.delta`; bare `data: [DONE]` honored (UI_SPEC §7.1).
- **O:** `plan`, `message.appended`, `artifact.created`, `node.placed`, `usage`, `error`, `done`; Loom adds `run.status`, `step.status`, `step.output`.
- **Who breaks:** B ignores every live frame — `phase` is not in its dispatch table, so it falls through to the `message.delta` default and appends `undefined` to the bubble. And the board needs "a node appeared" to place a generated image without a full refetch; B's vocabulary cannot express it, so it must refetch (which is exactly what `web/app.js:343` `bootProject()` does).
- **SSOT for v1:** **B's grammar plus two events from O.** Ship `thinking.delta`, `message.delta`, `node.placed`, `usage`, `error`, `done`. Keep L's `phase` as an optional extra (it is genuinely useful progress UI and costs nothing). Drop `plan`, `message.appended`, `artifact.created`, and the `result` mega-frame.

### S3 — Turn request field name differs three ways
- **L:** `{prompt, mode, provider, model, variants, parent_artifact_id}` at `POST /api/threads/{id}/run` (`server.py:359-368`).
- **B:** `{thread_id, project_id, message, mode, provider, model}` at `POST /api/chat`.
- **O:** `{thread_id, instruction, board_id, constraints}` at `POST /conductor/turns`.
- **Who breaks:** `prompt` vs `message` vs `instruction` for the same string; any adapter translates invisibly.
- **SSOT for v1:** **B's envelope, extended with L's two real features.** `POST /api/chat {thread_id, project_id, message, mode, provider, model, variants, parent_artifact_id}`. `variants` and `parent_artifact_id` (spot edit) are live capabilities that neither research doc knows about and both should.

### S4 — No cancel or abort
- **L:** synchronous; no cancel route; a slow provider call holds the connection.
- **B:** disables Send for the stream's duration (`app.js:1129`); no stop button anywhere in the markup or keymap.
- **O:** `POST /loom/runs/{id}/cancel` with `409` for terminal runs — nothing equivalent for conductor turns.
- **Who breaks:** a user who typos a prompt and watches 8 image generations bill against their own key. For BYOK this is a money bug, not a UX bug.
- **SSOT for v1:** **new, minimal.** Client aborts the `fetch` (B already uses `AbortController` for the health probe, `app.js:430`); server checks for a broken `wfile` between weave items and stops. No cancel endpoint, no run registry. Add a visible Stop button.

### S5 — Streamed reasoning has nowhere to live
- **L:** `messages` is `{id, thread_id, role, content, plan_json, created_at}` (`store.py`); the critique is flattened into the summary string by `_summarize`.
- **B:** renders `m.thinking` in a collapsible Reasoning block and `m.mode/provider/model` in the metadata line (UI_SPEC §4.5, §6).
- **O:** generic `payload` object plus `seq`.
- **Who breaks:** thinking mode — reasoning streams, renders, then vanishes on reload.
- **SSOT for v1:** **B's names in real columns.** Add `thinking`, `mode`, `provider`, `model`; keep `plan_json` as the generic payload. B renders these by name, so a generic blob would force client-side unpacking for the one thing that must appear on every message.

---

## 4. Upload

### U1 — Three different upload contracts; B's is the only one with a UI · **BLOCKER**
- **L:** `POST /api/projects/{id}/upload` with **base64 in a JSON body** — `{filename, mime, data}` → 5 MB cap on the decoded blob → creates the artifact **and a board node** → returns `{artifact, node}` (`server.py:313-351`).
- **B:** `POST /api/uploads`, `multipart/form-data`, field `file` → `{id, url, kind}`, and **B creates the node itself** from the returned url (`06-board-ui/app.js:173-179, 799-820`; UI_SPEC §4.4, §4.7).
- **O:** `POST /projects/{projectId}/artifacts`, multipart, **required** `kind`+`mime`+`file` → full `Artifact` with sha256 dedupe, plus a JSON variant registering an external URL (`openapi.yaml:342-384`).
- **Who breaks:** B's uploads 404 (#13). Worse, if you naively point B at L's path, **you get two nodes per file** — L auto-creates one, B creates another from the response. The auto-create is a reasonable choice for L's own UI and an actively wrong one for any client that manages its own canvas.
- **SSOT for v1:** **B's route and response, O's storage semantics, and L's node auto-creation made opt-in.** Ship `POST /api/uploads` → `{id, url, kind, mime}` with `?place=1` to also pin a node. Content-address by sha256 and dedupe (O). Keeping L's implicit node creation as the only behavior locks out every non-live client.

### U2 — base64-in-JSON is the wrong encoding, and the client-side encoder will hang the tab
- **L:** base64 inflates the payload ~33%, is buffered entirely in memory server-side, and `_read_json` `json.loads` the whole thing. The live client encodes with a per-byte string concatenation — `bytes.forEach((b) => { bin += String.fromCharCode(b); })` (`web/app.js:206-211`) — which for a 5 MB file is five million string concatenations on the main thread. It will visibly freeze the browser.
- **B / O:** both multipart, both streamable.
- **Who breaks:** anyone dropping a real photograph. The 5 MB cap is checked *after* `b64decode`, so a ~6.7 MB request body is fully read and decoded before rejection.
- **SSOT for v1:** **B + O — multipart.** Parse it server-side (stdlib `email.parser` or a ~60-line reader), stream to disk, cap on `Content-Length` before reading. If base64 must stay as a fallback, use `FileReader.readAsDataURL` client-side rather than the concat loop.

### U3 — `kind` means two different things
- **B:** `kind` is the raw MIME type (`app.js:178, 380`). **O:** `kind` is an enum category — `image|video|audio|vector|text|font|model3d|archive|other` — with `mime` separate. **L:** hardcodes `kind="upload"` and stores the real type in `mime` (`server.py:331-332`) — a third meaning, and one that no consumer expects.
- **Who breaks:** exactly the kind of same-name/different-meaning collision that passes review and fails at runtime. L's `"upload"` also makes artifacts unfilterable by media type.
- **SSOT for v1:** **O.** `kind` = enum category, `mime` = raw type; return both.

### U4 — Artifact serving: metadata and bytes on one route
- **L:** improved — `GET /api/artifacts/{id}` serves inline by default with a correct extension from `ext_for_mime`, and `?download=1` forces the attachment (`server.py:218-226`; used at `web/app.js:133, 135`). The `.bin` bug is fixed.
- **B:** stores whatever url the upload returned into `node.data.src`.
- **O:** metadata at `GET /artifacts/{id}` (JSON), bytes at `GET /artifacts/{id}/content`, `409` if external (`openapi.yaml:386-441`).
- **Remaining gap:** there is still no way to fetch artifact *metadata* — the route always returns bytes, so a client cannot ask "what is this, how big, when made" without downloading it.
- **SSOT for v1:** **O.** Split them: `GET /api/artifacts/{id}` → JSON, `GET /api/artifacts/{id}/content` → bytes (keep `?download=1`). Persist artifact **ids** on nodes, not URLs, so the path stays changeable.

### U5 — No MIME allowlist, and SVG is served same-origin · **security**
- **L:** the upload accepts **any** mime the client declares (`server.py:327`) with no allowlist and no sniffing; `_send_file` force-sets `image/svg+xml` for `.svg` (`server.py:109-110`); the demo weave produces SVG (`helix/loom.py`).
- **B:** no client-side type gate; anything not `image/*`/`video/*` becomes a note.
- **O:** silent. `08-security-quota/THREAT_MODEL.md:115, 127` requires CSP plus SVG sanitization or rasterization.
- **Who breaks:** this is live **today**, not hypothetical. Upload an SVG containing a script, and it is served from `/api/artifacts/{id}` on the same origin as the key API — which leaks partial secrets (A4) and can drive `POST /api/threads/{id}/run` on the user's dime, with no auth anywhere (A1). Stored XSS with a credential-shaped payoff.
- **SSOT for v1:** **THREAT_MODEL.md.** MIME allowlist plus content sniffing, size cap enforced pre-read, CSP on every response, and either rasterize SVG or serve artifacts with `Content-Disposition: attachment` and a sandbox CSP. This is a prerequisite for shipping the route that already exists.

---

## 5. Delete

### D1 — Cannot delete or archive a project · **BLOCKER**
- **L:** no route; `helix/store.py` has no `delete_project`/`archive_project` and no `archived_at`.
- **B:** the switcher creates and selects only (`app.js:900-935`).
- **O:** `POST /projects/{projectId}/archive` — "Archive (never hard-delete)" — plus `archived_at` and `include_archived` (`openapi.yaml:134-147, 63-66`).
- **Who breaks:** every user, permanently and cumulatively. Compounded by T2: B creates a junk project on every reload and none can ever be removed. Within a day the switcher is unusable.
- **SSOT for v1:** **O — soft archive.** `POST /api/projects/{id}/archive` + `?include_archived`. Soft is right: this is the user's design history and there is no undo worth the name (D6).

### D2 — Cannot delete or archive a thread
- **L / B:** nothing. **O:** `PATCH /threads/{threadId} {status}`, `ThreadStatus = open|pinned|resolved|archived` (`openapi.yaml:218-236, 1230-1232`).
- **Who breaks:** the thread list grows unbounded; combined with K1 (every B-created thread is untitled) it becomes a column of identical `undefined`s.
- **SSOT for v1:** **O.** One `PATCH /api/threads/{id}` covers both rename and archive.

### D3 — Delete node · **resolved**
- **L:** `DELETE /api/nodes/{id}` → `200 {ok: bool}`, `404` when absent (`server.py:389-396`; `store.py:313-316`). **B:** expects `204`, tolerates any 2xx. **O:** `204`.
- **Remaining nit:** `200 {ok}` vs `204`. Harmless, but align on `204` for consistency with T8/N6.
- **SSOT for v1:** **B/O — `204`.**

### D4 — Cascade and artifact GC still undefined
- **L:** `nodes` has **no foreign key** (`store.py` schema); `PRAGMA foreign_keys` is never enabled, so the FKs that do exist are unenforced. `delete_node` removes the row and leaves the artifact row and its bytes on disk forever (`store.py:313-316`).
- **O:** explicit — layer delete cascades to nodes, artifacts survive (`openapi.yaml:600-606`).
- **Who breaks:** whoever implements D1 without deciding this, and eventually every user's disk. Orphan blobs accumulate unreachably.
- **SSOT for v1:** **O's rule (artifacts survive) plus an explicit purge.** Enable `PRAGMA foreign_keys=ON`, add cascades for archive-then-purge, ship a visible "purge archived" that deletes rows *and* unreferenced blobs. Never GC silently.

### D5 — Cannot remove a stored key
- **L:** `Keyring.delete()` exists and is correct (`helix/keyring.py:90-94`) — **still not routed.** No `DELETE /api/keys`.
- **B:** no remove affordance; a key can only be overwritten (`app.js:1282`).
- **O:** `DELETE /keyring/{keyRef}` → `204`.
- **Who breaks:** a user who pastes a key into the wrong provider row, or wants to revoke local storage before handing over the laptop. `public_status` reports `configured: true` forever.
- **SSOT for v1:** **O.** Route the method that already exists; add a per-row `×` in B's settings. Ten lines, outsized trust payoff for a BYOK product.

### D6 — Undo is one step, add-only, and does not cover delete
- **L:** new `undo_log` and `POST /api/projects/{id}/undo` (`server.py:297-299`; `store.py:318-339`). But `push_undo` is called **only** from `add_node` (`store.py:273`), `undo()` handles **only** `action == "add_node"`, and it pops exactly one entry. `delete_node` pushes nothing — **a deleted node is unrecoverable.**
- **B / O:** neither models undo.
- **Spec:** `01-product-spec/ACCEPTANCE.md:36` requires "node-scoped undo ≥ 50 steps; project snapshot on every agent turn".
- **Who breaks:** a user who deletes the wrong node, and the acceptance criteria as written.
- **SSOT for v1:** **ACCEPTANCE.md.** Push undo entries from delete and update too, and keep a bounded stack rather than a single row. Shipping a one-step add-only undo behind a button labelled "Undo" is worse than no button.

---

## 6. Export and download

### E1 — Export exists and silently omits every thread and message · **BLOCKER**
- **L:** `GET /api/projects/{id}/export` → ZIP containing `project.json`, `board.json` (nodes + camera), `artifacts.json` manifest, and the artifact bytes (`server.py:207-214`; `helix/exportzip.py:11-45`). Read the code: it never touches the `threads` or `messages` tables. **The entire conversation history — the intent strand, the thing that makes this a design *studio* rather than an image folder — is not in the export.** Usage is absent too. There is no `format`/version field.
- **B:** no export UI at all (a full-text search of `06-board-ui/` for `export`/`download` finds only a CSS comment and the keymap's `Delete`).
- **O:** `GET /projects/{projectId}/snapshot` → `ProjectSnapshot` with `format: helix-snapshot/1`, threads **with their messages**, artifacts, boards with layers and nodes, brand kits, runs, usage summary (`openapi.yaml:149-162, 1548-1588`).
- **Who breaks:** every user who exports believing they have their work, and discovers on import that the brief, the iterations, and the critiques are gone. A lossy export that reports success is worse than no export, because the user deletes the original.
- **SSOT for v1:** **O's `ProjectSnapshot` content, L's ZIP transport.** Keep the zip (bytes need somewhere to go) but put an O-shaped `snapshot.json` inside it — threads with messages, usage, brand kit — and stamp `format: "helix-snapshot/1"`. The version string is the whole point: it lets v2 add boards and layers without breaking readers.

### E2 — Product-required asset formats have no route
- **Spec:** `ACCEPTANCE.md:44-47` (M-6) requires PNG incl. transparent, JPEG, SVG for vector-text nodes, PDF-RGB, MP4, plus watermarking by tier.
- **L:** serves stored bytes only, in whatever the provider returned; demo weaves are SVG, so "download my poster" yields an SVG.
- **B / O:** no conversion endpoint either.
- **Who breaks:** the acceptance criteria directly, and any user needing a print- or platform-ready file.
- **SSOT for v1:** **new, explicitly scoped down.** v1 ships exactly two things: per-artifact download in its native format (U4, done) and the complete snapshot zip (E1). Put format conversion and board-level composites in v2 behind a real route (`POST /api/projects/{id}/exports {format, node_ids}`). Do **not** let the current zip be recorded as satisfying M-6.

### E3 — No board-level or selection export
- All three serve one artifact per request; the zip is all-or-nothing at project scope. Nothing exports a selection or a composed board.
- **Who breaks:** the 7-platform fanout in `ACCEPTANCE.md:73`, and any real handoff where the deliverable is a folder.
- **SSOT for v1:** **defer, and say so in the UI copy.**

---

## 7. Health

### H1 — O has no health endpoint · **BLOCKER (O path)**
- **L:** `GET /api/health` → `{ok, name, architecture, evolve_rounds: 20}` (`server.py:163-174`).
- **B:** probes it with a 1.5 s `AbortController`; **success is `res.ok` alone**, body ignored; on failure it silently switches to the localStorage demo backend (`06-board-ui/app.js:428-437`).
- **O:** no `/health` path exists.
- **Who breaks:** deploy any gateway that exposes only documented paths and B's probe 404s, the pill reads "Demo mode", and the user is shown **seeded fake data** — "Neon Botanica — Campaign" and two invented chat messages — that looks exactly like their real work was wiped. The most alarming failure mode in the diff, and it is one missing line of YAML.
- **SSOT for v1:** **L + B (already agree).** Add `/health` to O. Separately, make the demo-mode banner unmistakable; an amber pill does not distinguish "seed data" from "your data".

### H2 — Health reports nothing actionable
- **L:** a static literal that cannot fail — no DB check, no keyring check, no runtime-dir writability, no version. `evolve_rounds: 20` is internal process metadata, not health.
- **Who breaks:** support and any future updater. A corrupted DB still reports healthy, and there is no way to ask a user what version they are on.
- **SSOT for v1:** **new, minimal.** `{ok, name, version, architecture, db: ok|error, runtime_writable: bool}`, cheap enough for a 1.5 s probe.

---

## 8. CORS and origin policy

### X1 — Zero CORS headers; `OPTIONS` → 501
- **L:** no `Access-Control-*` anywhere, no `do_OPTIONS`. **B:** assumes same-origin `/api` — fine *if* served by the same server. **O:** silent; asserts loopback-only.
- **Who breaks:** the research team's own documented workflow. `UI_SPEC.md:23-28` says to run the board UI under `python3 -m http.server 8000`; the API is on `:8765`; that is cross-origin, there is no CORS and no dev proxy in the repo, so **the documented dev loop can only ever reach demo mode.** That is almost certainly why B has never been run against L, and why §1's failures went unnoticed.
- **SSOT for v1:** **B's same-origin assumption — serve the UI from the API server, which `server.py:151-162` already does.** Do not add permissive CORS; it is the wrong tool and it widens X2. Add a documented dev proxy instead.

### X2 — No `Origin`/`Host` validation: any web page can drive the local API · **BLOCKER**
- **L:** no origin check, no CSRF token, no `Host` validation. Every mutating route is a plain `POST` with a JSON body, reachable cross-origin from any page the user visits, because the server never checks. That includes `POST /api/keys` and `POST /api/threads/{id}/run` (spends the user's provider budget) and now `POST /api/projects/{id}/upload` (writes attacker-chosen bytes into the artifact store, see U5).
- **B:** sends no CSRF token and has nowhere to hold one.
- **O:** `security: [localToken]` bearer.
- **Already documented by the project itself:** `08-security-quota/THREAT_MODEL.md:110, 122-125` — "DNS rebinding / CSRF from A2 against `127.0.0.1`"; mitigation is a per-session bearer token **plus** `Host`/`Origin` validation **plus** loopback binding. None of the three exists in code.
- **Who breaks:** the user, financially and confidentially, from any drive-by page. This is the exact scenario the project's own threat model calls out.
- **SSOT for v1:** **THREAT_MODEL.md + O's `localToken`.** Validate `Origin`/`Host` on every mutating request and require the token. Both small; shipping without them is not defensible for software holding API keys.

### X3 — No CSP, and the UI shares an origin with the key API
- **L:** no CSP on any response; `_json` sets only `Cache-Control: no-store`; static and artifact responses set no security headers. `web/app.js:33` now supports an `html` attribute that assigns `innerHTML`, and `refreshKeys` builds markup by string concatenation (`web/app.js:236-240`).
- **B:** deliberately avoids `innerHTML` with user data (UI_SPEC §9) — a client-side mitigation with no server-side backstop.
- **O:** silent. THREAT_MODEL.md:115 specifies `default-src 'self'; base-uri 'none'; connect-src 'self'`.
- **Who breaks:** compounds U5 into a key-exfiltration path.
- **SSOT for v1:** **THREAT_MODEL.md.** Add the CSP header to every response.

### X4 — Path traversal in static serving · **BLOCKER**
- **L:** `_send_file(self, WEB / path[len("/web/"):])` and `WEB / path.lstrip("/")` with no normalization or containment check (`server.py:154-161, 230-232`). A client that does not normalize — `curl --path-as-is 'http://127.0.0.1:8765/web/../../../../etc/passwd'` — reads arbitrary files, including `~/.atelier/keyring.json`, which holds the plaintext keys.
- **Who breaks:** combined with X2, a rebinding attack or any hostile local process reads the keyring off disk.
- **SSOT for v1:** **new.** Resolve the path and assert containment inside `WEB` before reading. Three lines. Not optional. (Note the team already applied exactly this kind of hardening outbound — `helix/http.py` refuses credentialed redirects — so the reflex exists; it just has not been pointed at the inbound path.)

---

## 9. Auth

### A1 — Required / absent / someone else's problem · **BLOCKER**
- **L:** no authentication on any route. `ATELIER_HOST` is env-overridable with no warning (`server.py:403`), so `ATELIER_HOST=0.0.0.0` publishes an unauthenticated, key-spending, key-hint-leaking, arbitrary-file-reading API to the LAN.
- **B:** sends no `Authorization` header; `UI_SPEC.md:290` lists auth under **Out of scope** — "assumed session handled upstream of `/api`".
- **O:** global `security: [localToken]`; "per-install token generated at first launch and stored in the Keyring; defends the loopback port against other local processes" (`openapi.yaml:28-29, 1167-1173`).
- **Who breaks:** implement O as written and **100% of B's requests 401**, with no UI to enter a token. Implement B as written and X2 stands. Two research deliverables directly contradict each other and the live code sides with neither.
- **SSOT for v1:** **O's `localToken`, delivered the way B can consume it.** Mint a per-install token at first launch; have `server.py` inject it into `index.html` at serve time (or set a `SameSite=Strict` cookie plus an Origin check) so no client ever needs a token field; require it on every `/api/*` request. Keeps O's security property and B's zero-friction UX. Resolve the UI_SPEC §10 line explicitly — that one sentence is what let this gap exist.

### A2 — Bind: env override with no guardrail
- **L:** `ATELIER_HOST` honored blindly. **O:** "loopback only; never bound to a public interface."
- **SSOT for v1:** **O.** Refuse a non-loopback bind unless a token is configured; print a loud warning.

### A3 — Key write shape differs three ways
- **L:** `POST /api/keys {provider, key, base_url}` — one provider per call, returns the **full** status map; now validates `base_url` against the official-host allowlist and returns `400 {error, code:"unofficial_host"}` (`server.py:248-261`; `keyring.py:68-76`) — a genuine improvement.
- **B:** `PUT /api/keys {provider: rawKey, …}` — a map of all non-empty inputs, returns the masked map.
- **O:** `PUT /keyring/{keyRef} {secret}` — one write-only secret, `204`, no body; provider configs reference it by `key_ref`, and raw secrets in a config are `422`-rejected before touching disk.
- **Who breaks:** B's save 501s (#14); O's `key_ref` indirection has no live counterpart, making its whole provider-config model unimplementable as written.
- **SSOT for v1:** **B's route and batch shape, L's host validation, O's write-only semantics.** `PUT /api/keys` taking a map, returning masked status, never echoing a secret. Defer `key_ref` to v2 — it only pays off with multiple configs per provider.

### A4 — Key masking: L leaks the first three characters
- **L:** `hint = secret[:3] + "…" + secret[-4:]` (`keyring.py:107`), returned by an **unauthenticated** `GET /api/keys`.
- **B:** expects `{set, hint}`, renders `saved …abcd` — last 4 only.
- **O:** names and creation times only; "Secret values are never returned by any endpoint."
- **Who breaks:** with X2, any page the user visits reads a partial key plus its provider and base URL. Prefix+suffix is materially more disclosure than suffix alone, and for `sk-`-style keys the prefix confirms the vendor and key class.
- **SSOT for v1:** **B's shape, O's discipline.** `{set: bool, hint: "…"+last4}` and nothing else. Also fixes the `configured` vs `set` field-name break (#3), which today makes B report "not set" for configured keys.

### A5 — No secret scrubbing on the error path
- **L:** `except Exception as exc: _json(self, 500, {"error": str(exc), "ok": False})` (`server.py:375-377`) — provider errors sometimes echo request headers or bodies. No scrubber exists in `helix/`.
- **Research:** `08-security-quota/POLICY.md:13` specifies `usage.scrub_secrets()` for `sk-…`, `AIza…`, `Bearer …`.
- **Who breaks:** a key lands in a screenshot, a bug report, or a log line.
- **SSOT for v1:** **POLICY.md.** Port `scrub_secrets()` and run every error string through it before it reaches a response or a log.

---

## 10. Providers and model catalog

### P1 — `GET /api/providers` does not exist · **BLOCKER**
- **L:** no such route. `GET /api/catalog` exists but returns the TOP100 **GitHub repo list** (`server.py:181-183`) — unrelated data at a plausible-looking path.
- **B:** `GET /api/providers` → `[{id, name, models}]` drives both selects; on failure it silently keeps a hardcoded catalog (`app.js:164, 1431`).
- **O:** `GET /providers` returns `ProviderConfig` registry rows — `label`, `key_ref`, `capabilities`, `defaults`, `enabled` — structurally different from B's shape, and **O has no model list anywhere**.
- **Who breaks:** B falls back silently, offering Anthropic and fal.ai models L cannot route (#2).
- **SSOT for v1:** **B's shape.** `GET /api/providers` → `[{id, name, models:[…], configured: bool}]`, generated from the live spoke registry plus keyring status. O's registry is a v2 feature and would drag in the `key_ref` indirection for no user-visible gain. Add `configured` so the picker can grey out keyless providers — the exact failure the current UI hides.

### P2 — Provider id sets barely intersect · **BLOCKER**
- **L:** spokes are `demo | openai | gemini | ollama`; keyring `ENV_MAP` is `openai | gemini | anthropic | ollama | openai_compat` — note it knows `anthropic` while **no anthropic spoke exists**.
- **B:** chat providers `openai | anthropic | google | fal`; key rows add `replicate`.
- **O:** free-form lowercase family.
- **Who breaks:** `google` (B) and `gemini` (L) are the same vendor under two ids, so a Gemini key saved through B lands where L never reads it. `demo` — L's no-key fallback and the only thing that works out of the box — does not exist in B. B's default `anthropic/claude-sonnet-4.5` is unroutable, so the conductor degrades to a demo SVG and the user believes Claude drew it.
- **SSOT for v1:** **L's ids** (they are what the code can call), with B trimmed to `demo | openai | gemini | ollama` and `google → gemini`. Ship `anthropic` only when the spoke ships; a keyring slot with no spoke behind it is a trap.

### P3 — Model lists have no source
- **L:** hardcoded per provider in two places that can drift — `conductor._default_model`/`_image_model` and `quote.chat_model_for`/`image_model_for` (`helix/quote.py:10-31`) — plus a free-text input in the live UI.
- **B:** needs `models[]` per provider. **O:** no model-listing endpoint; `/providers/{id}/verify` returns prose.
- **Who breaks:** the picker is stale or wrong forever, and the quote can price a different model than the run uses.
- **SSOT for v1:** **B's shape from one static table.** Serve a curated per-provider model list from a single dict that both the conductor and the quote import. Revisit with `/providers/{id}/models` in v2.

---

## 11. Board and node model

### N1 — Board list path and shape · **BLOCKER**
- **L:** `GET /api/projects/{id}/board` → `{nodes: […], camera: {x,y,zoom}}` (`server.py:195-199`).
- **B:** `GET /api/projects/{id}/nodes` → bare array (`app.js:157`); camera is client-only, persisted to `localStorage` prefs.
- **O:** `Project → Board → Layer → Node`, with `GET /boards/{id}/scene` returning denormalized paint-ordered `SceneNode` rows, layer visibility/lock, fractional `z`, and a `viewport` on the board (`openapi.yaml:469-682`).
- **Who breaks:** B's canvas is empty against L purely because of the path (#5) — one rename apart. Camera is a genuine three-way split: server-persisted (L), client-persisted (B), board-attached (O).
- **SSOT for v1:** **B's path, L's flat model, L's server-side camera.** Rename to `GET /api/projects/{id}/nodes` returning a bare array, and keep camera on its own route (`GET/POST /api/projects/{id}/camera`, already built at `server.py:200-206, 293-296`) — server-side camera is the better call because it survives a browser change, and O agrees it belongs server-side. **Defer O's board/layer tree to v2** and write the deferral down: it is the right destination, it is a schema migration plus a renderer rewrite, and no v1 requirement needs layers.

### N2 — Node create exists but drops the node's content · **BLOCKER**
- **L:** `POST /api/projects/{id}/nodes` reads `type`, `text`, `x`, `y`, `w`, `h`, `meta` (`server.py:300-312`). It ignores the client's `id`, ignores `z`, and — critically — ignores `data`.
- **B:** posts the whole node including `data: {text}` for notes and `data: {src, title}` for images (`app.js:638-648`).
- **O:** `POST /boards/{boardId}/nodes` requiring `layer_id` + `kind`, with `props` as the free-form slot.
- **Who breaks:** B creates a note, types into it, and the note is stored **blank** (#10). The route landing made this failure quieter, not louder — before, the 404 at least produced a toast.
- **SSOT for v1:** **B's wire shape.** Accept `data`, map it to `text`/`meta`, echo the canonical row. Accept the client id or reissue — B handles both (`app.js:657-660`).

### N3 — Node field shapes disagree three ways
- **L:** columns `type` (`image|note|text`), `x,y,w,h,z(INTEGER)`, `artifact_id`, `text`, `meta{}`; new `text` layer type with `meta.layer`.
- **B:** `{type: note|image|video, x,y,w,h,z, data:{text? src? title? sub?}}`.
- **O:** `{kind: artifact|text|shape|frame|sticky|connector, layer_id, artifact_id, x,y,w,h, rotation, opacity, z(fractional), props{}}`.
- **Collisions:** `type` vs `kind`; `text` column vs `data.text` vs `props`; image source as `artifact_id` (L, O) vs `data.src` URL (B); `video` exists only in B; `text` (as a distinct layer type) only in L; `rotation`/`opacity` only in O; `z` integer vs fractional.
- **SSOT for v1:** **B's wire shape over L's storage.** Keep `text`/`meta` columns, serialize to `{type, data:{…}}` at the boundary. Add `video` (a placeholder node, no backend work) and keep L's `text` type. Skip `rotation`/`opacity`; never add `layer_id` (N1).

### N4 — `update_node` silently drops the field B sends most · **BLOCKER**
- **L:** `update_node` filters to `{"x","y","w","h","z","text","meta"}`, ignores everything else, and returns **200 with the unchanged row** (`store.py:296-311`).
- **B:** note autosave sends `{data: {text}}`, debounced 500 ms (UI_SPEC §4.3). Geometry sends `{x,y,w,h,z}` and works.
- **O:** PATCH accepts `props`.
- **Who breaks:** **every note the user types is lost on reload, with a success response and no error.** The most damaging mismatch here: silent, and it destroys user-authored content rather than regenerable AI output. Note this is the same root cause as N2 — `data` is invisible to both the create and the update path.
- **SSOT for v1:** **B.** Accept `data`, map onto `text`/`meta`, and — whatever shape you choose — **reject unknown fields with `422` instead of ignoring them.** Silent field-dropping is how this class of bug survives review.

### N5 — `update_node` on an unknown id crashes the connection
- **L:** `update_node(parts[2], **{k: body[k] for k in body})` (`server.py:384`) → zero-row `UPDATE` → `get_node` does `dict(fetchone())` on `None` → uncaught `TypeError` (only `json.JSONDecodeError` is caught in `do_POST`) → traceback and a dropped connection instead of a 404. A body containing `node_id` triggers `TypeError: multiple values` the same way. Note `do_DELETE` on the same resource handles the missing case correctly (`server.py:393-394`) — the two paths disagree.
- **O:** `404`.
- **SSOT for v1:** **O.** `404` unknown id, `422` unknown field, plus a catch-all converting unexpected exceptions into a scrubbed `500` JSON body (A5) rather than a reset.

### N6 — PATCH/DELETE response bodies
- **L:** `200` + node for PATCH, `200 {ok}` for DELETE. **B:** accepts either. **O:** `200` + entity for PATCH, `204` for DELETE.
- **SSOT for v1:** **O.**

---

## 12. Threads and messages

### K1 — `topic` vs `title` · **BLOCKER**
- **L:** `threads.topic` + `threads.mode`; `POST` reads `body.get("topic")` (`server.py:282-288`); the live UI renders `t.topic` (`web/app.js:88`).
- **B:** sends and renders `title` (`app.js:153, 987`).
- **O:** `title` + `status`.
- **Who breaks:** every thread B creates is stored untitled and renders as `undefined` (#6). Two of three say `title`.
- **SSOT for v1:** **B + O — `title`.** Rename the column; update the live UI's one reference.

### K2 — Where `mode` lives is undecided
- **L:** a column on `threads`, also accepted per-run, and **silently overwritten** by the conductor on the first turn (`conductor.py:334-339` rewrites `topic` and `mode` together).
- **B:** per-message, persisted in prefs, sent on every call.
- **O:** not modelled — a Conductor `constraints` concern.
- **Who breaks:** switching Fast/Thinking mid-thread means different things in each contract, and L's silent rewrite means the thread's stored mode is not what the user last chose.
- **SSOT for v1:** **B — per-message.** Store `mode` on the message row (already needed for S5) and drop it from `threads`. A thread-level mode cannot express one thinking turn inside a fast conversation.

### K3 — Message role enum: `assistant` is illegal in O
- **L:** writes `user`/`assistant`. **B:** expects `user|assistant`. **O:** `user|conductor|spoke|system|note` — no `assistant` (`openapi.yaml:1234-1236`).
- **Who breaks:** a snapshot exported from L and validated against O rejects every assistant message; a strict O client rejects the live stream.
- **SSOT for v1:** **L + B — `user|assistant`,** plus `system` and `note` from O. `conductor`/`spoke` is a provenance distinction the rungs model needs and v1 does not have.

### K4 — Ordering: float `created_at` vs gap-free `seq`
- **L:** ordered by float seconds; two messages written inside one conductor run can tie, and the order is then arbitrary — and the conductor writes exactly that pattern (user message at the start, assistant at the end of the same run).
- **O:** per-thread gap-free `seq` from 0, plus an `after_seq` cursor (`openapi.yaml:246-252, 1283`).
- **Who breaks:** occasional out-of-order rendering, and any future incremental-load or resume-after-drop, which needs a cursor.
- **SSOT for v1:** **O — add `seq`.** One column, and a precondition for SSE reconnect.

### K5 — No direct message-append route
- **L / B:** none needed. **O:** `POST /threads/{id}/messages`.
- **SSOT for v1:** **skip**; document as v2 so the O route is not mistaken for implemented.

---

## 13. Brand kit

### B1 — Three different resource models · **BLOCKER**
- **L:** an opaque JSON blob column on `projects`; read via `GET /api/projects/{id}`, written via `POST /api/projects/{id}/brand {brand_kit}` (`server.py:290-292`). The live UI edits it as **raw JSON in a textarea** (`web/index.html`).
- **B:** a singleton sub-resource — `GET`/`PUT /api/projects/{id}/brand-kit` — with a structured editor (palette rows, fonts, logo, voice) (UI_SPEC §4.7).
- **O:** a versioned collection — `/projects/{id}/brand-kits`, `/brand-kits/{id}/activate` with an at-most-one-active invariant, `/brand-kits/{id}/assets`.
- **Who breaks:** B's panel 404s on read and 501s on save (#7, #15).
- **SSOT for v1:** **B — singleton `GET`/`PUT /api/projects/{id}/brand-kit`,** stored in L's existing blob column. O's multi-kit model is a real feature and a real cost (new table, activation invariant, asset join); defer it. Retire the raw-JSON textarea — an unvalidated schema editor in the shipping UI guarantees B2.

### B2 — Field shapes are mutually unreadable
- **L (seed):** `{name, palette: ["#0c0d10", …], voice: "quiet, precise, editorial"}` — palette is a flat string list (`server.py:50-54`).
- **B:** `{colors: [{name, value}], fonts: {heading, body}, logo_url, voice}`.
- **O:** `{name, palette: [{name, hex}], typography: {}, voice: {} }` — **`voice` is an object**.
- **Collisions:** `palette` vs `colors`; `value` vs `hex`; voice string vs object. L's own seed kit renders as an empty palette in B. The conductor JSON-dumps whatever it finds into the prompt (`conductor.py:_brand_block`) and now also reads `brand.get("palette")` directly (`conductor.py:120`), so B's `colors` shape would silently disable palette enforcement rather than error.
- **SSOT for v1:** **B.** `{colors:[{name,value}], fonts:{heading,body}, logo_url, voice: string}` — the only shape with a real editor behind it. Migrate the seed. Validate on write so the conductor never silently ignores a kit.

### B3 — Logo upload rides on the upload mismatch
- **B:** the logo drop zone posts to `/api/uploads` (UI_SPEC §4.7) — see U1. **O:** `POST /brand-kits/{id}/assets` referencing an existing artifact.
- **SSOT for v1:** **B**, unblocked by U1; store `logo_url` as an artifact id rendered through `/api/artifacts/{id}/content`.

---

## 14. Usage, budget, conductor

### C1 — Usage ledger schemas do not convert
- **L:** `{provider, model, unit_kind: tokens_in|tokens_out|images, units, estimated_usd, thread_id, created_at}`; exposed as `GET /api/usage` → `{events, totals}`.
- **B:** does not read usage at all.
- **O:** `/usage/events` + `/usage/summary` with `spoke`, `operation`, `unit_type: tokens|pixels|seconds|characters|requests`, `cost_micros`, `project_id`, `run_id`, `status`, `latency_ms`.
- **Who breaks:** `provider` vs `spoke`; `unit_kind` values absent from O's enum; and **no `project_id` on live rows**, so per-project spend — the number a user actually wants — is unanswerable.
- **SSOT for v1:** **O's field names and units on L's endpoint.** Adding `project_id` now is far cheaper than backfilling.

### C2 — Budget is enforced but not visible
- **L:** real — `ATELIER_DAILY_BUDGET` ($10) and `ATELIER_THREAD_BUDGET` ($2), checked in `usage.assert_budget`. The limits are returned inside the `/api/quote` response (`quote.py:94-95`) but there is no route that answers "how much have I spent today", and B has no spend UI at all.
- **O:** per-turn `constraints.max_cost_micros` — a different mechanism (per-request ceiling vs rolling window).
- **Who breaks:** a user hits an invisible cap they never set and cannot inspect.
- **SSOT for v1:** **L's rolling window, exposed.** Add `{daily_limit, daily_spent, thread_limit, thread_spent}` to `GET /api/usage` and render it next to the spend meter from T5. O's per-turn ceiling is v2.

### C3 — Pre-flight budget check · **largely resolved**
- **L:** `conductor.run` now calls `quote_run` **before** spending and raises `BudgetExceeded` up front (`conductor.py:133-143`), and `POST /api/quote` lets the UI price a run before committing (`server.py:262-276`; `web/app.js:315-325`). This is a genuinely good design that neither research contract proposed.
- **Remaining gaps:** the quote prices only the *first* weave item's model, so a plan that routes to a different provider than requested is mispriced; unpriced models fall back to a flat `0.04 * count + 0.01` (`quote.py:71`); and neither B nor O has any concept of a quote, so the feature is undocumented in both specs.
- **SSOT for v1:** **L.** Promote `POST /api/quote` into whichever document becomes normative, and add it to B's composer — "this will cost about $X" before the click is exactly what a BYOK user needs.

### C4 — Budget rejection status · **resolved**
- **L:** `402 {error, code: "budget_exceeded", ok: false}` (`server.py:369-371`), and `ConductorError` → `422 {error, code}` (`372-374`). The live UI reads `err.code`.
- **Remaining:** B has no handler for either, and SSE has no `error` frame to carry them (S2). Field names still differ from O (T8).
- **SSOT for v1:** **L's codes in O's envelope,** plus a matching SSE `error` frame.

### C5 — Weave fan-out has no confirmation gate
- **L:** up to 4 weave items × count 2, plus a `variants` path that forces 2–4 (`conductor.py:86-92, 191-202`), decided by the planner LLM. `/api/quote` exists but calling it is optional and the live UI's Quote button is separate from Run — nothing forces the estimate before the spend.
- **B / O:** neither models a confirmation step.
- **Who breaks:** a user's wallet on one ambiguous prompt.
- **SSOT for v1:** **wire the quote into the run.** Emit the quote as the first SSE frame (L already emits a `quote` event — `conductor.py:141`) and require confirmation above a threshold. The pieces exist; they are just not connected.

### C6 — Run result: computed, returned, discarded
- **L:** returns `{ok, plan, artifacts, nodes, message, events, errors}` (`conductor.py:342-350`); the live UI reads `plan` and `events` for a phase string, then calls `bootProject()` and refetches everything anyway (`web/app.js:338-343`).
- **B:** expects the terminal `done` frame to carry the persisted assistant message.
- **SSOT for v1:** **B** — `done {message}` plus `node.placed` events so the board updates incrementally instead of refetching.

---

## 15. Live-only features that neither research contract knows about

A fourth divergence direction, and the reason the research docs can no longer be treated as specifications. Each of these is in shipping code with no counterpart in B or O:

| Feature | Live route | Status |
|---|---|---|
| Quote-before-commit | `POST /api/quote` (`server.py:262`) | good design; undocumented in both specs (C3) |
| Undo | `POST /api/projects/{id}/undo` (`server.py:297`) | one step, add-only, no delete coverage (D6) |
| Server-side camera | `GET`/`POST /api/projects/{id}/camera` (`server.py:200, 293`) | better than B's client-only camera; adopt it (N1) |
| Variants (4-up) | `variants` on run, prompt-sniffed incl. Chinese tokens (`conductor.py:86-92`) | real feature; belongs in the chat contract (S3) |
| Spot edit | `parent_artifact_id` on run (`server.py:367`) | real feature; belongs in the chat contract (S3) |
| Official-host enforcement on key save | `keyring.put` → `400 unofficial_host` (`keyring.py:68-76`) | good; O's `422` secret-leak rejection is the complementary half |
| No-redirect HTTP for credentialed calls | `helix/http.py` | good; the inbound equivalent (X4) is still missing |

**Recommendation:** whichever document becomes normative must absorb these. Right now a reader of `openapi.yaml` would conclude that quote, undo, camera, variants and spot-edit do not exist, and a reader of `UI_SPEC.md` would conclude the same. Both would then design around their absence.

---

## 16. Blocker list and minimum cut to ship

**The 18 blockers**, by area: T1 (O base URL), T2 (list envelope), T6 (`PUT`/`OPTIONS` → 501), S1 (streaming is a replay), U1 (three upload contracts), D1 (no project delete), E1 (export drops threads and messages), H1 (O has no health), X2 (no origin check), X4 (path traversal), A1 (auth contradiction), P1 (no `/api/providers`), P2 (provider id sets), N1 (board path), N2 (node create drops `data`), N4 (node update drops `data`), K1 (`topic` vs `title`), B1 (brand-kit resource model).

Ordered by dependency, not size. Each line resolves the bracketed items.

**Security — first; the rest is unshippable without it**
1. Origin/Host validation + per-install token injected into `index.html` [X2, A1, A2]
2. Path-traversal containment in `_send_file`; CSP header on every response [X4, X3]
3. Upload MIME allowlist + sniffing + pre-read size cap; SVG rasterized or sandboxed [U5]
4. Key hint → last-4 only; `scrub_secrets()` on every error and log path [A4, A5]

**Transport — one pass over `server.py`**
5. `do_PUT`, `do_OPTIONS`, `do_HEAD`; `protocol_version = "HTTP/1.1"` [T6, T9]
6. Bare-array lists; `{error, detail}` on every path; `404` unknown id; `422` unknown field; catch-all → scrubbed JSON [T2, T8, N5, N6]
7. Id prefixes; epoch-ms timestamps; `cost_micros` [T3, T4, T5]

**The seven named gaps**
8. Pass `on_event` into `conductor.run` so SSE is actually incremental; port `_chat_stream` from the research spokes for token deltas; expose it as `POST /api/chat` with B's frame grammar + `node.placed`; client abort + Stop button [S1–S5]
9. `POST /api/uploads` multipart → `{id, url, kind, mime}`, sha256 dedupe, `?place=1` for node auto-creation; split `/api/artifacts/{id}` (JSON) from `/api/artifacts/{id}/content` (bytes) [U1–U4]
10. `POST /api/projects/{id}/archive`; `PATCH /api/threads/{id}`; route the existing `Keyring.delete`; `204` on delete; undo covers delete with a bounded stack [D1, D2, D5, D6, N6]
11. Put an O-shaped `snapshot.json` — **threads with messages**, usage, brand kit — inside the export zip, stamped `helix-snapshot/1` [E1]
12. Health reports version + db + runtime writability; add `/health` to the OpenAPI doc [H1, H2]

**Contract alignment so B works against L**
13. `topic` → `title`; `mode` moves to the message; add `seq`, `thinking`, `provider`, `model` columns [K1, K2, K4, S5]
14. `/board` → `/nodes` (bare array, camera stays on its own route); accept `data` on node create **and** update [N1, N2, N3, N4]
15. `GET`/`PUT /api/projects/{id}/brand-kit` with B's field shape; retire the raw-JSON textarea [B1, B2]
16. `GET /api/providers` with `configured` flags; align ids on `demo|openai|gemini|ollama`; batch `PUT /api/keys` [P1, P2, P3, A3]
17. Usage gains `project_id`/`cost_micros`/`unit_type`; expose budget state; wire the quote into the run as a gate [C1, C2, C5]

**Explicitly deferred to v2 — write it down so it is not re-litigated**
Boards and layers (N1) · rungs and lineage · Loom runs and run SSE · brand-kit versioning and activation · the `ProviderConfig`/`key_ref` registry · direct message append · format-converting export (PNG/PDF/SVG/MP4) and batch export (E2, E3).

---

## 17. Where the process failed

Worth recording, because the same failure is still happening:

- **B and L have never been run against each other.** The board UI's own quickstart (`UI_SPEC.md:23-28`) can only produce demo mode, because there is no CORS and no dev proxy (X1). A UI that transparently falls back to seeded fake data is excellent UX and extremely effective at hiding a broken backend contract — the pill turns amber and everything still appears to work.
- **The OpenAPI was written against a different store.** `04-helix-arch/store.py` (1,201 lines: boards, layers, rungs, loom) is not `helix/store.py` (~380 lines). `atelier/ARCHITECTURE.md` is honest about this — "the live `helix/store.py` stays the small runtime" — but `openapi.yaml` says so nowhere in its own text, so a reader takes it for the API of the running system.
- **Auth was declared out of scope by one deliverable and mandatory by another**, and neither noticed (A1). `UI_SPEC.md:290` and `openapi.yaml:28` are direct contradictions, and the threat model that would settle it (`08-security-quota/THREAT_MODEL.md:122-125`) is a third deliverable neither cites.
- **New, and the reason this document needed rewriting mid-flight:** the live server gained six routes in the nine minutes between my first and second read, and every one of them chose a shape that matches neither research contract — base64 upload instead of multipart, a buffered replay instead of SSE, a zip instead of a snapshot. Implementation is now outrunning the specs in a third direction (§15). Speed is not the problem; the absence of a normative document is.

**The concrete fix:** pick the v1 SSOT per §16, write it into one document that both `server.py` and the board UI cite by name, and add a CI smoke test that drives B's `RemoteBackend` methods against a live `server.py`. Every one of the 18 blockers above would have been caught by that single test — including the three that landed in the last ten minutes.
