# Live Helix HTTP contract (2026-08-21)

Research Board UI (`research/fable5/06-board-ui`) speaks SSE `/api/chat`.
**Live Atelier does not use `/api/chat`.** Do not swap that UI onto this process.
Every row below was walked against a real `ThreadingHTTPServer` on the demo
lane; see `legion/opus-09/HARDEN.md` for the captured responses.

## Live API surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/health` | `{ok, name, architecture: helix, evolve_rounds: 20}` |
| GET | `/api/keys` | Redacted status for every known provider. Never 400 |
| POST | `/api/keys` | Store key/base_url. Unofficial or non-https host → 400 `unofficial_host`. An unknown provider is a silent 200 no-op |
| GET | `/api/catalog` | TOP100 public listing |
| GET | `/api/usage` | `{events, totals}` |
| POST | `/api/quote` | Quote-before-commit; spends nothing. `would_exceed` mirrors the 402 a run would give |
| GET | `/api/projects` | `{projects}` |
| POST | `/api/projects` | 201, and mints a first thread |
| GET | `/api/projects/:id` | One project; 404 if missing |
| GET | `/api/projects/:id/threads` | `{threads}`. Unknown project → **200 `[]`**, not 404 |
| POST | `/api/projects/:id/threads` | 201; 404 if project missing |
| GET | `/api/projects/:id/board` | `{nodes, camera}`; 404 if project missing |
| GET | `/api/projects/:id/camera` | `{camera}`; 404 if project missing |
| POST | `/api/projects/:id/camera` | Persist pan/zoom, returns the project; 404 if missing |
| POST | `/api/projects/:id/brand` | Brand kit, returns the project; 404 if project missing |
| POST | `/api/projects/:id/upload` | JSON `{filename, mime, data}` base64 → 201 `{artifact, node}`; 404 if project missing |
| GET | `/api/projects/:id/export` | `?fmt=zip\|svg\|png\|pdf&scale=1\|2\|4`. Default zip. JPEG → 415. 404 if project missing |
| POST | `/api/projects/:id/undo` | Pop last `add_node`. Nothing to pop — or an unknown project — is **200 `{undone: false, reason: "empty"}`**, not 404 |
| POST | `/api/projects/:id/nodes` | Text layer (`type=text`) → 201; 404 if project missing |
| GET | `/api/threads/:id/messages` | `{messages}`, includes stored `plan`. Unknown thread → **200 `[]`**, not 404 |
| POST | `/api/threads/:id/run` | Conductor. `?stream=1` → SSE of `events` then `result`. 404 if thread missing |
| POST | `/api/nodes/:id` | Patch node (`data` aliases `text`); 404 if node missing |
| DELETE | `/api/nodes/:id` | 200 `{ok: true}`; already gone → 404 `{ok: false}` |
| GET | `/api/artifacts/:id` | `?download=1` → attachment; filename slug + ext from the stored mime |
| GET | `/api/artifacts/:id/export` | `?fmt=native\|svg\|png\|pdf&scale=`. JPEG → 415. 404 if artifact missing |

Unmatched `/api/*` is 404 JSON (`unknown GET` / `unknown POST` / `unknown DELETE`).

## Static surface

Served out of `atelier/web/`, guarded by `safe_under` — the same process, and
part of the contract because the studio will not load without it.

| Method | Path | Notes |
|---|---|---|
| GET | `/`, `/index.html` | `web/index.html` |
| GET | `/app.js`, `/styles.css` | Served from the package, not from `/web/` |
| GET | `/web/*`, `/assets/*` | Same directory; traversal (`/web/../../helix/keyring.py`) → 404 |
| GET | `/*` | Any other non-API path resolves under `web/`, else 404 JSON. This is the fallthrough, not a route test |

## Methods

- `do_PATCH` is `do_POST`. **Every POST row above also answers PATCH**, and an
  unmatched PATCH comes back as 404 `{"error": "unknown POST"}`.
- Any other verb (`PUT`, `OPTIONS`, `HEAD`, `TRACE`) has no `do_*` and falls to
  `BaseHTTPRequestHandler` → **501, HTML not JSON**.
- Both export routes accept `?format=` as an alias for `?fmt=`.

## Status codes

| Code | When |
|---|---|
| 200 | Success (`ok: true` on run) |
| 201 | Project, thread, node, upload created |
| 400 | Invalid JSON / unofficial or non-https key host |
| 402 | Daily or thread budget would be exceeded (`code: budget_exceeded`) |
| 403 | Non-local `Host` header while bound to loopback (`code: bad_host`) |
| 404 | Missing project / thread / artifact / node **on the rows that check** — see the three 200-instead-of-404 rows above — plus every unmatched `/api/*` |
| 413 | Upload > 5 MB, or a JSON body > 8 MB |
| 415 | Unsupported export format (JPEG, on both export routes) |
| 422 | Paid weave failed, unknown provider, or key missing (fail-closed; no demo SVG) |
| 500 | Anything else out of `conductor.run` |
| 501 | HTTP verb with no `do_*` handler |

## Quote pricing

`priced` is not "is this model known". It is true when the cost table has a row
for **both** the resolved chat model and the resolved image model, with `demo`
and `ollama` short-circuited to true because they are free by definition:

| provider / model sent | capability | `priced` | `estimated_usd` |
|---|---|---|---|
| `openai` / `gpt-4o-mini` | image | true | 0.0403 |
| `openai` / `no-such-model` | chat | false | 0.0500 (conservative hold) |
| `openai` / `gpt-image-1` | image | **false** — an image model in the chat slot has no token row | 0.0500 |
| `gemini` / `made-up-9000` | chat | false | 0.0500 |
| `ollama` / `made-up-9000` | image | **true** | 0.0000 |
| `demo` / `made-up-9000` | image | **true** | 0.0000 |

Unpriced never means free: it falls back to `0.04 × count + 0.01` for budget
math, which is what 402 is computed against.

## Non-goals on this contract

- Research-only `/api/chat` SSE board
- Lovart credits, video, 3D, PSD, teams
- Following HTTP redirects on credentialed spoke calls
