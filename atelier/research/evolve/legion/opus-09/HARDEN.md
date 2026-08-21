# Opus-09 · R18 live contract — verified

Verifier: one live `claude-opus-5-thinking-high-fast` agent, branch
`cursor/atelier-byok-studio-d639`, HEAD at `2e8244d` (Round 18).
Method: an `ast` walk of the three `_do_*` bodies in `atelier/server.py`
reduced to route shapes, set-compared against the markdown table; then real
`ThreadingHTTPServer` binds on ephemeral ports, driven over real sockets with a
throwaway `ATELIER_RUNTIME`, `OPENAI_API_KEY` / `GEMINI_API_KEY` scrubbed from
the environment. Demo lane only — no network, no key read, no paid call. Every
bind is shut down inside the test that opened it.

**Verdict: PASS with fixes.** All five claims held as shipped. `/api/chat` does
not exist in this process under any verb, `app.js` runs threads, and every one
of the 25 rows in the table resolves to a live route — nothing listed is dead.
What did not hold was the surface *around* the rows. The table described a
router narrower than the one that ships: a whole HTTP method (`PATCH`) is
served and never mentioned, the six static routes the studio cannot load
without are absent, three rows answer 200 for an id that does not exist while
the status table promises 404, three live status codes (403, 500, 501) are
missing, and the one behavioural note on `/api/quote` — "`priced: false` for
unknown models" — is not what `priced` means and is the wrong way round for
`demo` and `ollama`.

## Claim by claim

| # | Claim | Verdict |
|---|-------|---------|
| 1 | CONTRACT says live does not use `/api/chat` and must not take `research/fable5/06-board-ui` | PASS, and the warning is still load-bearing |
| 2 | No `/api/chat` handler in `server.py`; `app.js` talks to `/api/threads/:id/run` | PASS, on a stronger reading than the shipped test used |
| 3 | The table lists health, keys, quote, catalog, usage, projects, board, camera, brand, upload, export (fmt/scale), undo, nodes, threads/run, threads/messages, DELETE nodes, artifacts GET+export; 415 for JPEG | PASS for everything listed, with seven omissions closed |
| 4 | Real server + demo provider: health is `architecture: helix`, catalog 200, `/api/chat` 404 | PASS, captured below on all four verbs the handler answers |
| 5 | `Round17to20Meta.test_live_contract_notes_exist` still passes | PASS, untouched, re-run against the rewritten contract |

## Path traced

`GET /api/chat` → `Handler.do_GET` → `_check_host` (Host header vs the
`ATELIER_HOST` bind) → `get_app().lock` → `_do_GET` → `urlparse` → the static
block (`/`, `/index.html`, `/web/`, `/assets/`, `/app.js`, `/styles.css`) →
six flat `path ==` API routes → `parts = [p for p in path.split("/") if p]` →
nine `parts[:2] == [...] and len(parts) == N` shapes → the
`path.startswith("/api/")` guard → **404 `{"error": "unknown GET"}`**. There is
no branch in between; the string `/api/chat` does not occur in `server.py` at
all. The same walk for `do_POST` and `do_DELETE` ends at `unknown POST` /
`unknown DELETE`, and `do_PATCH` is literally `self.do_POST()`, so a PATCH to
an unmatched path is answered `unknown POST`.

The browser side: `app.js` `#send` → `runBody()` → `POST
/api/threads/${state.threadId}/run?stream=0` → `renderMessages` off
`/api/threads/:id/messages`. `stream=1` is a live server capability the shipped
UI never asks for. No `EventSource`, no `/api/chat`.

## Router vs table, as a set comparison

The AST reduction turns each `if` test in `_do_GET` / `_do_POST` /
`_do_DELETE` into a `VERB /api/projects/*/board` shape; the table parse turns
each `| VERB | \`path\` |` row into the same shape with `:id` → `*`. Both
directions are asserted:

```
GET      live 13   doc 13     POST     live 11   doc 11     DELETE  live 1  doc 1
PATCH    live 11   doc  0     -> alias:POST, covered by the prose rule
static   live /  /index.html  /app.js  /styles.css  /web/*  /assets/*
         doc  the same six, plus /* for the fallthrough (not an `if`, so the
              walk cannot see it)
sentinel GET->"unknown GET"  POST->"unknown POST"  DELETE->"unknown DELETE"
         PATCH->"unknown POST"
```

Drift is caught both ways. Adding `if path == "/api/chat"` to `_do_GET`:
4 failures, including `test_every_live_route_has_a_row`. Adding a
`| POST | /api/chat |` row with no route behind it: 1 failure,
`test_every_row_is_a_live_route`.

## HTTP evidence (claim 4)

Every line below came off a real socket against a real `ThreadingHTTPServer`
on an ephemeral port, demo provider, empty runtime dir.

```
GET    /api/health   -> 200 {"ok": true, "name": "atelier",
                             "architecture": "helix", "evolve_rounds": 20}
GET    /api/catalog  -> 200 {"title": "Atelier Helix TOP100", "architecture": "Helix", ...}

GET    /api/chat     -> 404 {"error": "unknown GET"}
POST   /api/chat     -> 404 {"error": "unknown POST"}
DELETE /api/chat     -> 404 {"error": "unknown DELETE"}
PATCH  /api/chat     -> 404 {"error": "unknown POST"}      # do_PATCH is do_POST
```

The conductor, run for real on the demo lane:

```
POST /api/threads/:id/run          -> 200 ok=true  artifact provider=demo mime=image/svg+xml
     events: brief quote score route weave pin pin done
POST /api/threads/:id/run?stream=1 -> 200 text/event-stream
     event: phase quote phase phase phase pin phase phase result
GET  /api/threads/:id/messages     -> 200 assistant message carries plan.route
```

Exports, both routes, with the content type and the attachment name the client
actually receives:

```
GET /api/projects/:id/export             -> 200 application/zip  atelier-atelier-studio.zip
                             ?fmt=svg    -> 200 image/svg+xml    …-board.svg      1 917 B
                             ?fmt=png    -> 200 image/png        …-sheet.png      4 040 B
                    ?fmt=png&scale=2     -> 200 image/png                         8 917 B
                    ?fmt=png&scale=4     -> 200 image/png                        24 319 B
                             ?fmt=pdf    -> 200 application/pdf  …-sheet.pdf
                          ?format=svg    -> 200 image/svg+xml    (undocumented alias)
                    ?fmt=jpeg | ?fmt=jpg -> 415 {"code": "unsupported_fmt"}
GET /api/artifacts/:id/export            -> 200 image/svg+xml    a-quiet-poster.svg
                        ?fmt=png|pdf     -> 200 image/png | application/pdf
                        ?fmt=jpeg        -> 415 {"code": "unsupported_fmt"}
GET /api/artifacts/:id                   -> 200 image/svg+xml, no Content-Disposition
GET /api/artifacts/:id?download=1        -> 200 attachment; filename="a-quiet-poster.svg"
```

Every status code in the table, produced rather than asserted from a string:

```
200 GET  /api/health
201 POST /api/projects
400 POST /api/keys  base_url=https://evil.example  {"code": "unofficial_host"}
    POST /api/keys  base_url=http://127.0.0.1:1/v1 {"error": "Refusing non-https official host (http)"}
    POST /api/quote  body `{not json`               {"error": "invalid json"}
402 POST /api/threads/:id/run  provider=openai, DAILY_BUDGET_USD=0
      {"error": "daily budget $0.00 exceeded ($0.0403)", "code": "budget_exceeded", "ok": false}
403 GET  /api/health  Host: attacker.example        {"code": "bad_host"}
404 GET  /api/chat
413 POST /api/projects/:id/upload  6 800 001 base64 chars  {"error": "upload too large"}
415 GET  /api/projects/:id/export?fmt=jpeg
422 POST /api/threads/:id/run  provider=openai, no key
      {"code": "auth", "ok": false}  — fail-closed, no demo SVG substituted
    POST /api/threads/:id/run  provider=not-a-provider  {"code": "unknown_provider"}
500 POST /api/threads/:id/run  with conductor.run raising  {"ok": false}
501 PUT | OPTIONS | HEAD | TRACE  /api/health       HTML from BaseHTTPRequestHandler
```

Static surface, which the table did not mention at all:

```
GET /              -> 200 text/html        5 157 B
GET /index.html    -> 200 text/html        5 157 B
GET /app.js        -> 200 text/javascript 22 139 B   (contains /api/threads/, not /api/chat)
GET /styles.css    -> 200 text/css         6 024 B
GET /web/index.html   -> 200   GET /assets/app.js -> 200
GET /web/../../helix/keyring.py -> 404      # safe_under holds
```

## Holes found and closed

All seven are documentation holes. R18 is a documentation round and the live
code is not touched here.

1. **A whole HTTP method was undocumented.** `do_PATCH` is `self.do_POST()`,
   so all eleven POST rows also answer PATCH — `PATCH /api/nodes/:id` with
   `{"text": "after"}` returns 200 and the node really changes. The table
   listed `POST` only. Now stated as a rule rather than 11 duplicated rows,
   with the wart that an unmatched PATCH is answered `{"error": "unknown POST"}`.
   Pinned by an AST assertion that `do_PATCH` is an alias *and* a live PATCH.
2. **`PUT` / `OPTIONS` / `HEAD` / `TRACE` are 501 HTML, not JSON.** Every other
   error on this surface is a JSON body; these four fall through to
   `BaseHTTPRequestHandler` and come back as an HTML error page. A client that
   assumes JSON everywhere breaks on them. Now a row in the status table.
3. **The static surface was missing.** Six live GET routes — `/`,
   `/index.html`, `/app.js`, `/styles.css`, `/web/*`, `/assets/*` — plus a
   fallthrough that resolves any other non-API path under `atelier/web/`.
   The studio does not load without them, so they belong in the contract.
   Added as their own table, with the `safe_under` traversal guard noted and
   exercised.
4. **"404 — missing project/thread/artifact/node" was an overclaim on three
   rows.** `GET /api/projects/nope/threads` is `200 {"threads": []}`,
   `GET /api/threads/nope/messages` is `200 {"messages": []}`, and
   `POST /api/projects/nope/undo` is `200 {"undone": false, "reason": "empty"}`.
   Neither `list_threads` nor `list_messages` nor `undo` checks that the parent
   exists — they are plain `WHERE` queries that return nothing. A client
   following the old contract would treat a typo'd project id as an empty
   project instead of a missing one. Each row now says so in bold, and the 404
   line is qualified. Pinned by three exact `(code, body)` assertions.
5. **403 and 500 were absent from the status table.** 403 `bad_host` is the
   guard the whole loopback threat model rests on (R14's hole 2), and 500 is
   the bare `except Exception` around `conductor.run`. Both are now listed and
   both are produced live by the suite.
6. **`priced: false for unknown models` is not what `priced` means.** It is not
   a model lookup: `priced` is `chat_priced and image_priced`, and both are
   short-circuited to true for `demo` and `ollama`. Measured:

   ```
   openai / gpt-4o-mini    image -> priced=True   0.0403
   openai / no-such-model  chat  -> priced=False  0.0500
   openai / gpt-image-1    image -> priced=False  0.0500   # image model in the chat slot
   gemini / made-up-9000   chat  -> priced=False  0.0500
   ollama / made-up-9000   image -> priced=True   0.0000   # unknown model, priced anyway
   demo   / made-up-9000   image -> priced=True   0.0000
   ```

   So the shipped sentence is exactly backwards for the two free lanes, and it
   also mislabels a *known* model (`gpt-image-1`) passed in the `model` field,
   because `chat_model_for` puts it in the chat slot where it has no token row.
   Replaced with the real rule plus this matrix, and the note that unpriced
   falls back to `0.04 × count + 0.01` — the number 402 is computed against.
7. **`?format=` is a live alias for `?fmt=`** on both export routes
   (`query.get("fmt") or query.get("format")`). Undocumented; now a line under
   Methods and exercised in the export test.

### Checked and *not* a hole

- **Nothing in the table is dead.** All 25 rows resolve to a live route; the
  set difference `doc − live` is empty for GET, POST and DELETE. Nothing had
  to be removed or marked.
- **`/api/chat` is genuinely absent**, not merely unrouted. The shipped test
  checked `path == "/api/chat"`; the string does not occur in `server.py`,
  `app.js`, or anywhere under `atelier/web/`. The research spec under
  `research/fable5/06-board-ui` *does* still speak it, which is asserted here
  so the warning cannot go stale silently.
- **Fail-closed survives.** `provider=openai` with no key is 422 `auth` with no
  artifact, not a demo SVG wearing an OpenAI label. `demo` is never budgeted,
  so a zero daily budget does not brick the offline lane.
- **`/api/quote` spends nothing.** `/api/usage` is byte-identical before and
  after a paid-provider quote.
- **The SSE the contract documents is real.** `?stream=1` emits
  `text/event-stream` with the phase events and `event: result` last, even
  though the shipped UI always sends `stream=0`.
- **Traversal on the static surface holds.** `/web/../../helix/keyring.py` is
  404, not the keyring source.

## Known live behaviour left alone

`POST /api/keys {"provider": "nope", "key": "x"}` returns 200. `Keyring.put`
only host-checks providers in `ALLOWED_HOST_SUFFIXES`, so an unknown provider
skips validation entirely, is written to `keyring.json`, and is then invisible
in `public_status()` (which iterates `ENV_MAP`). It stores a secret nothing can
read back or delete through the UI. That is a keyring defect, not a contract
defect, and fixing it is a code change this round does not own. Recorded in the
table as "an unknown provider is a silent 200 no-op" so the contract is at
least honest about it, and left for a later round.

## Evidence that the tests bite

Against the shipped `2e8244d` `CONTRACT.md`, with the product code untouched:
**8 of 32 fail** — `test_every_live_route_has_a_row` (PATCH),
`test_static_surface_is_documented`, `test_patch_is_documented_as_an_alias_of_post`,
`test_every_verb_the_handler_answers_is_named`,
`test_unmatched_api_paths_are_documented_as_404`,
`test_the_three_rows_that_answer_200_for_a_missing_id`,
`test_every_documented_code_is_produced_live` (403/500/501 observed live and
absent from the table), `test_quote_priced_is_not_unknown_model`.

Against a `server.py` that grows an undocumented `/api/chat` handler: **4 fail**.
Against a `CONTRACT.md` that grows a dead `POST /api/chat` row: **1 fails**.

## Tests

`atelier/tests/evolve/test_opus_09.py` — was 5 tests in one class, all of them
substring greps over the markdown plus five greps over `server.py` source
(`assertIn('path == "/api/catalog"', self.server)`); now **32 across six
classes**. What changed in kind: the route claim is a two-way set comparison
between an AST reduction of the router and a parse of the table, so it fails on
drift in either direction instead of confirming five hand-picked strings; the
status table is *produced* by a live walk and compared as a set, so a code that
appears in the router without a row fails; and every behavioural claim
(415, scale, download filename, SSE, `data` alias, DELETE twice, fail-closed
422, budget 402, bad-host 403) is a real request over a real socket rather than
a string in a document.

```
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve \
    atelier.tests.evolve.test_opus_09
Ran 68 tests — OK
```

Full tree (`unittest discover -s atelier/tests`): 350 tests, OK
(1 expected failure, pre-existing).

## Remaining holes

- The two-way set comparison is between the table and an **AST reduction**, not
  the running router. It reads the `if` tests, so a route added by some other
  shape — a dict dispatch, a decorator, a regex — would be invisible to it.
  The live walk covers today's routes by hand; there is no proof that the two
  lists are the same list.
- The `/*` static fallthrough is documented but excluded from the set
  comparison, because it is a trailing statement rather than an `if`. A change
  to what it serves would not fail anything here.
- **The unknown-provider keyring write above is still live.** It is out of R18
  scope and now documented rather than fixed.
- 402 was produced by patching `usage.DAILY_BUDGET_USD` in-process, because the
  module reads `ATELIER_DAILY_BUDGET` once at import. A subprocess with the env
  set was used to confirm the same 402 end to end, but the suite does not spawn
  one; that is the cost of keeping the gate under 15 s.
- No paid provider was contacted, by design, so 422's *other* lane — a real
  spoke that fails mid-weave — is inferred from the demo lane and from R01's
  fail-closed tests, not observed here.
- `?stream=1` is contract-documented and server-live but no shipped client uses
  it, so the SSE framing has one consumer: this test file.
- The contract still describes one process on one machine. Nothing here checks
  what the surface looks like behind a reverse proxy, which is where the
  `Host`-header guard and the static fallthrough would both need rereading.

## Not started

Round 19 (`atelier/data/eval/*.json`). `SCORECARD.json` untouched. No research
Board UI swapped onto the live process.
