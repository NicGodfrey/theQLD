# Atelier — Test Gap Analysis

**Opus#8 of 10 · 2026-08-21 · scope: `atelier/` in `NicGodfrey/theQLD` @ `cursor/atelier-byok-studio-d639`**

No file under `/workspace` was modified. All experiments ran from copies in `/tmp`.

---

## 1. Bottom line

The shipped product has 7 tests. They pass, they run in 31 milliseconds, and they
catch almost nothing. I seeded 12 realistic defects into the live code and the suite
caught **2**. The ten that survived include *"the OpenAI spoke sends your API key to
any host"*, *"`public_status()` returns the raw key"*, and *"`Keyring.put` is a no-op"*.

Meanwhile `research/fable5/` contains **172 tests** across four suites — a genuinely
good body of work with fixtures, network blocking, env scrubbing, and a documented
mutation check. The problem is not that the tests do not exist. **The problem is that
they test a different program.** The research suites were written against a prototype
API (`parse_plan`, `route_plan`, `UsageLedger`, `BudgetGuard`) that the shipped
`atelier/helix/` package does not implement. Point the 58-test eval harness at the
live modules and you get 17 errors and 10 skips, not 58 passes.

So there are two distinct failures to fix, and they need different treatments:

1. **The live suite is too weak to protect the product.** Fix by writing ~24 targeted
   tests against the live API. Most are re-expressions of research assertions, not
   copy-paste ports.
2. **Nothing runs any of it automatically.** There is no `.github/` directory in the
   repo at all — no workflows, no CI, no lint, no packaging file. Every suite here is
   run by hand or not at all.

There is also a third thing worth naming plainly: the eval harness's advertised
"58/58, 0 skips" result is **not reproducible on a clean machine**. It depends on a
scratch directory at `/tmp/atelier-fable/` that happens to still exist on this VM.
Delete it and the same command exits 0 with 27 of 58 tests skipped. A green tick that
silently drops 47% of the suite is worse than a red one.

---

## 2. Inventory

### Live product (what ships)

| Component | Lines | Tests | Statement coverage |
|---|---|---|---|
| `helix/store.py` | 304 | partial | 87.2% |
| `helix/conductor.py` | 276 | partial | 86.3% |
| `helix/usage.py` | 109 | partial | 96.5% |
| `helix/keyring.py` | 101 | 1 (vacuous, see §4.3) | 86.1% |
| `helix/spokes/` (5 files) | 356 | **0** | 21–40% |
| `helix/loom.py`, `catalog.py` | 70 | partial | 100% |
| `server.py` (the whole HTTP API) | 238 | **0** | **0% — never imported** |
| `web/app.js` (the whole UI) | 221 | **0** | **0% — no JS runner exists** |
| **Total** | **1,466 py + 221 js** | **7 tests / 116 lines** | **75.9% of `helix/`, 0% of the surfaces users touch** |

### Research (what was written, and does not run against the product)

| Suite | Tests | Result today | Binds to live code? |
|---|---|---|---|
| `10-eval/test_helix.py` + `--eval` scorecard | 58 | OK (see §3) | **No** — 17 errors when pointed at `helix/` |
| `03-keyring-spokes/tests/` (7 files) | 68 | OK | No — tests `gateway.py` / `spokes_*.py` |
| `05-conductor/tests/test_conductor.py` | 36 | OK | No — tests `parse_plan`/`route_plan` |
| `04-helix-arch/test_store.py` | 10 | OK | No — tests `schema.sql` directly |
| **Total** | **172** | | |

The research suites are the better tests by a wide margin. `03-keyring-spokes` alone
has 68 tests with recorded HTTP fixtures and fake transports. None of it guards a line
of shipped code.

---

## 3. The eval harness does not measure the product

This is the finding that reframes everything else, so it goes first.

`10-eval/test_helix.py` discovers components by path, defaulting to `/tmp/atelier-fable`,
and degrades in two ways when it cannot find them: missing schema/usage/loom **skip**
their test classes, and a missing conductor **falls back to the bundled `helix_ref.py`**
reference implementation. That design is defensible for a research drop shipped mid-fleet.
It is dangerous now, because the fallbacks are silent and the exit code stays 0.

Three runs, same file, same machine:

```bash
# 1. As documented — only green because /tmp/atelier-fable survived on this VM
$ python3 test_helix.py
Ran 58 tests — OK

# 2. As it would run on any fresh checkout or CI runner
$ ATELIER_ROOT=/tmp/does-not-exist python3 test_helix.py
Ran 58 tests — OK (skipped=27)          # exit code 0

# 3. Pointed at the code that actually ships
$ ATELIER_CONDUCTOR=atelier/helix/conductor.py \
  ATELIER_USAGE=atelier/helix/usage.py \
  ATELIER_LOOM=atelier/helix/loom.py python3 test_helix.py
Ran 58 tests — FAILED (errors=17, skipped=10)
AttributeError: module 'atelier_usage' has no attribute 'UsageLedger'
```

The APIs are disjoint, not merely renamed:

| Research expects | Live provides |
|---|---|
| `conductor.parse_plan`, `parse_critique`, `order_steps`, `route_plan`, `distill_brief`, `Plan`/`Step` dataclasses, `PlanParseError` | `extract_json`, `fallback_plan`, `Conductor.run`, plain dicts, `ValueError` |
| `usage.UsageLedger`, `BudgetGuard`, strict/lenient pricing modes | `usage.record`, `estimate_usd`, `BudgetExceeded` |
| `schema.sql` with invariants I3–I8 and a `v_board_scene` view | `store.py` with ad-hoc SQL, no view, no triggers |
| A `conductor-plan/1` JSON envelope with `steps`/`needs`/`emits`/`acceptance` | A freeform `{intent, score, route, weave}` dict |

`ACCEPTANCE_CHECKLIST.md` §5 and `EVAL.md` §8.2 both flag this honestly as
"**pending integration** — real end-to-end runner". That pending item is the entire
distance between the research and the product. It has not moved.

**Consequence for planning:** treat the research suites as a *specification library*,
not as a test suite to be adopted. The assertions are reusable; the code is not. Every
"port" below is a rewrite against the live API, and I have written out the live-API
assertion for each so nobody discovers this at implementation time.

---

## 4. How weak the live 7 actually are

### 4.1 Mutation results

I copied `atelier/` to `/tmp`, seeded one realistic defect at a time, and ran
`python3 -m unittest atelier.tests.test_helix`. Twelve mutants:

**Caught (2):**

- `usage.record` drops the planner's token events
- `store.add_message` silently discards assistant messages

**Survived (10):**

| Mutant | Severity |
|---|---|
| `openai_spoke._url` skips `assert_official_host` — key goes to any host | **Critical (key exfiltration)** |
| `assert_official_host` returns immediately, never refuses | **Critical (same, at the shared choke point)** |
| `Keyring.public_status` returns the raw secret as `hint` | **Critical (key disclosure over `/api/keys`)** |
| `Keyring.put` is a no-op — pasted keys are never saved | High (silent data loss) |
| `build_spoke` always returns `DemoSpoke` — BYOK never engages | High (product does nothing, silently) |
| `store.update_node` column allowlist removed | High (unvalidated identifiers into SQL) |
| Artifact filesystem path never written back to the DB | High (`/api/artifacts/{id}` breaks) |
| `next_board_offset` returns `(0, 0)` — every pin stacks | Medium (board unusable) |
| Weave cap of 4 items removed | Medium (unbounded spend per turn) |
| Thinking mode never runs the critic | Medium (advertised feature absent) |

**Mutation score: 2/12 ≈ 17%.** The two catches are both in the one code path the
suite genuinely exercises (`Conductor.run` in demo mode). Everything reachable only
via a real provider, the HTTP layer, or the browser is unguarded.

### 4.2 Coverage is misleading here — don't use it as the bar

`helix/` measures **75.9% statement coverage**, which sounds respectable next to a 17%
mutation score. Two reasons for the gap, both worth internalising before anyone sets a
coverage target:

- `server.py` and `web/app.js` are excluded from the denominator because no test
  imports them. The 75.9% is 75.9% *of the part that has any tests at all*.
- Lines get executed without being asserted on. `test_catalog_is_100` asserts
  `cat["count"] == 100`, and `count` is computed from the payload *before* the
  `projects` list is built — so a mutant returning only 10 projects passes. The line
  is covered. The behaviour is not.

Set the bar on mutation survival and on named behaviours, not on a coverage percentage.

### 4.3 One of the 7 is vacuous whenever a key is in the environment

`KeyringTests.test_redacts_and_env` writes a key with `put()`, then asserts
`status["openai"]["configured"]` is true and the secret is absent from the JSON dump.
But `get_secret()` prefers `os.environ["OPENAI_API_KEY"]` over stored state. With that
variable set — the normal state of a developer's shell, and the state of this VM — both
assertions are satisfied by the environment, and `put()` is never actually tested:

```bash
# Keyring.put mutated to `return self.public_status()` — a total no-op
$ python3 -m unittest atelier.tests.test_helix                 # OPENAI_API_KEY present
Ran 7 tests — OK                                               # mutant survives

$ env -u OPENAI_API_KEY python3 -m unittest atelier.tests.test_helix
Ran 7 tests — FAILED (failures=1)                              # mutant caught
```

The live suite never scrubs provider env vars and never blocks sockets. The research
harness does both (`LIVE_KEY_ENVS` scrubbing, `forbid_network` patching
`socket.socket.connect`). That hygiene is the single highest-value thing to port, and
it is about 15 lines.

---

## 5. Gaps, one by one

### 5.1 CI — nothing exists

`find` across the repo returns no `.github/`, no workflow, no `Makefile`, no
`requirements.txt`, no `pyproject.toml`, no lint config. Nothing has ever run these
tests except a human at a prompt.

The mitigating fact is that this is unusually cheap to fix. The live code imports
`json`, `sqlite3`, `urllib`, `http.server`, `re`, `pathlib` — **standard library only**.
CI needs no install step and no lockfile.

The one repo-specific caution: `theQLD` is a GitHub Pages site (`CNAME` → `theqld.com`)
serving a static Queensland legal directory, with `atelier/` living inside it as a
subdirectory. If Pages is configured as "deploy from a branch" (the default, and what
the `CNAME`-at-root layout implies), adding a workflow is inert with respect to
publishing. Do **not** add a Pages *deploy* workflow as part of this work — that would
switch the source to Actions and put the live site's publishing path in the blast
radius of a test change. Path-filter to `atelier/**` so directory edits never queue a
run.

```yaml
# .github/workflows/atelier-tests.yml
name: atelier
on:
  push:
    paths: ['atelier/**', '.github/workflows/atelier-tests.yml']
  pull_request:
    paths: ['atelier/**', '.github/workflows/atelier-tests.yml']
jobs:
  unit:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '${{ matrix.python }}' }
      - name: Unit suite (keyless, offline, no skips tolerated)
        env:
          ATELIER_STRICT: '1'      # see 5.2 — turns any skip into a failure
          OPENAI_API_KEY: ''       # explicit: CI must never hold a real key
          GEMINI_API_KEY: ''
          ANTHROPIC_API_KEY: ''
        run: python3 -m unittest -v atelier.tests.test_helix
```

Two follow-on jobs once §7 lands: an `api` job that boots `server.py` on an ephemeral
port and runs the contract tests, and a `ui` job running Playwright against the same
server. Neither belongs in the first commit.

### 5.2 Skip/fail policy — currently "skips are free", which is how §3 went unnoticed

There is no stated policy, and the default `unittest` behaviour (skips are green,
exit 0) is exactly what let a 47%-skipped run be reported as passing. Adopt this:

| Suite | Policy |
|---|---|
| `atelier/tests/` (live) | **Zero skips permitted.** A skip is a failure. If a test cannot run in the target environment, it does not belong in this suite. |
| Research suites, if run in CI at all | `ATELIER_STRICT=1` converts skip → failure. Without it they are archival and must not gate anything. |
| Live-key smoke | Must **refuse to run** unless `ATELIER_LIVE=1`. Never invoked by CI. Exit 2 with a message otherwise. |
| Network | Blocked by default in every unit test. A test that wants a socket opts in explicitly. |
| Provider env vars | Scrubbed in `setUpModule`. No test may read a real key. |

Enforce the first row with a meta-test rather than a wrapper script, so it holds
regardless of how the suite is invoked:

```python
class SuiteHygiene(unittest.TestCase):
    def test_no_test_is_skipped(self):
        """A skip means the suite is lying about its coverage. Fail loudly."""
        result = unittest.TextTestRunner(stream=io.StringIO()).run(
            unittest.defaultTestLoader.loadTestsFromName("atelier.tests.test_helix")
        )
        self.assertEqual(result.skipped, [], f"skipped tests are not permitted: {result.skipped}")
```

(Guard it against self-recursion by loading only the non-meta classes.)

### 5.3 API contract tests — 238 lines, zero tests, and it already diverges from itself

`server.py` has never been imported by a test. It is testable — `ATELIER_RUNTIME` and
`ATELIER_HOME` redirect all state to a temp dir, and I booted it cleanly on a spare
port — but one wrinkle needs handling first: `APP = App()` executes at **module import
time**, creating a SQLite file and seeding a project. A test must set the env vars
before importing, or the module needs a `get_app()` accessor. Prefer the env-var
approach initially; it requires no production change.

I probed the running server. Real findings, all currently unguarded:

- **`brand_kit` changes type between two endpoints.** `GET /api/projects` returns it as
  a JSON **string**; `GET /api/projects/{id}` returns it as an **object**. Confirmed at
  the store layer too: `create_project()` → `dict`, `get_project()` → `dict`,
  `list_projects()` → `str`. The UI dodges this only because `loadProject()` happens to
  call the detail endpoint. The one live store test asserts on `create_project`'s return
  value, so it cannot see this.
- **`PATCH /api/projects` creates a project and returns 201.** `do_PATCH` is
  `return self.do_POST()`, so every POST route is silently also a PATCH route. Whatever
  the intent, it should be pinned by a test.
- **`POST /api/keys` accepts any `base_url`** — `{"base_url": "https://evil.example.com"}`
  is stored and echoed back by `GET /api/keys`. Egress is refused later, at the spoke,
  by `assert_official_host`. That layering is *correct* (the choke point is at the socket,
  not the form), but nothing tests it, and §4.1 shows removing the check is invisible.
- **A failed live provider returns HTTP 200 and silently downgrades to demo output.**
  This is the most consequential untested behaviour in the product. With
  `provider: "openai"`, a bogus key and an unofficial host:

  ```
  HTTP 200
  plan.route          = {'provider': 'openai', 'model': 'gpt-4o-mini', ...}
  artifacts providers = ['demo']
  message             = "Helix fast · a calm navy poster
                         Route: openai / gpt-4o-mini          <-- not true
                         Pinned 1 artifact(s) onto the board.
                         local fallback plan"
  ```

  Artifact provenance correctly records `demo`, so the audit trail is intact. But the
  API returns success and the chat message tells the user their work came from
  `openai / gpt-4o-mini`. For a BYOK product whose entire proposition is "this spends
  *your* OpenAI quota", a silent downgrade that still claims the provider is a trust
  bug, not a polish item. `EVAL.md` §7 records the research pipeline getting this right
  — "live providers without keys fail loudly (`MissingKeyError`) *before* any network
  attempt". The shipped conductor swallows `SpokeError` in two places and carries on.

- Correct behaviours that are simply unpinned: unknown routes → 404, malformed JSON
  body → 400, run against a missing thread → 404, `/web/../../etc/passwd` → 404 (both
  raw and percent-encoded).

### 5.4 UI tests — no runner, no harness, no assertions

`web/app.js` is 221 lines driving the entire product surface: board rendering, node
drag, thread switching, the settings rail, the brand-kit editor, the run dock, the
catalog panel. There is no JS test runner in the repo and no browser automation.
Coverage is zero and cannot currently be non-zero.

The research drop has the same hole and says so: `ACCEPTANCE_CHECKLIST.md` §7 lists
Board UI verification as "**manual check** — open `06-board-ui/index.html`, confirm
pinned artifacts appear and drag updates x/y only", and `EVAL.md` §8.5 repeats it.
Note that `06-board-ui/` is a *second, richer* UI that is not wired to `/api` at all
(the Atelier README confirms this). Do not test it — test `atelier/web/`, which is
what ships.

Adding Playwright means adding the repo's first `package.json` and its first
non-stdlib dependency. That is a real cost against a currently dependency-free
project, and it is why UI tests sit at P2 in §7 rather than P0. The exception is the
drag-persistence path, which is the one place where a UI bug corrupts stored state
rather than just looking wrong — and that can be covered without a browser by
asserting the `POST /api/nodes/{id}` contract directly.

### 5.5 Live-key smoke — the research pattern is right; adopt it verbatim

`03-keyring-spokes/live_smoke.py` is the one artefact here I would port with almost no
changes. It is well-judged: refuses to run without `ATELIER_LIVE=1`, picks the cheapest
model per provider, documents the cost per invocation (~$0.0001 chat, ~$0.01–0.04
image), prints the resulting ledger rows, and is explicitly excluded from the unit
suite so it "can never fire from CI by accident."

What it needs is retargeting from `gateway.Gateway` to `helix.spokes.build_spoke` and
one addition: a **negative smoke** that runs against each configured provider with the
base URL pointed somewhere unofficial and asserts `SpokeError` before any socket opens.
That is the check that would have caught mutants 1 and 2 from §4.1, and it costs
nothing to run.

Keep it optional and keep it out of CI. This is a BYOK product; CI must never hold a
key, and a scheduled job that spends the maintainer's quota to prove the network still
works is not worth the failure mode where a rotated key turns the dashboard red.

### 5.6 Research spoke tests — 68 tests of genuinely reusable design

`03-keyring-spokes/tests/` is the strongest asset in the repo: `test_openai_spoke.py`
(209 lines), `test_gemini_spoke.py` (175), `test_keyring.py` (145), `test_ledger.py`
(122), `test_anthropic_spoke.py` (87), `test_gateway.py` (57), plus `fakes.py` and a
`make_fixtures.py` that records real provider responses to disk.

The **fake-transport pattern** is what to take: recorded response fixtures plus an
injected transport, so request shaping, response parsing, token accounting and error
mapping are all testable with no network. The live spokes call
`urllib.request.urlopen` directly inside `_post`, so they need a seam — either accept
an `opener` argument or patch `urllib.request.urlopen` per test. Patching is fine to
start and requires no production change.

Note the live product has **no Anthropic spoke** (`ENV_MAP` lists `anthropic` and
`public_status()` reports on it, but `build_spoke` has no branch for it — asking for
`anthropic` silently returns `DemoSpoke`). So `test_anthropic_spoke.py` has nothing to
port to. Either wire the spoke or drop `anthropic` from `ENV_MAP`, because right now
the settings rail offers a provider that cannot work.

---

## 6. The minimum bar to call the product usable

Not "well tested" — *usable*, meaning a stranger can be handed the URL and the
maintainer can sleep. Six gates. Every one is a behaviour, not a number.

**G1 — CI exists and is required.** `.github/workflows/atelier-tests.yml` runs the unit
suite on push and PR touching `atelier/**`, on 3.11 and 3.12, green, with the branch
protection rule set. *Nothing else on this list means anything until this is true.*

**G2 — No test can spend money or reach the network.** Provider env vars scrubbed in
`setUpModule`; `socket.socket.connect` and `socket.create_connection` patched to raise
in every unit test. The suite passes identically with and without `OPENAI_API_KEY` set
— which today it does not (§4.3).

**G3 — Zero skips, and the suite proves it.** The meta-test from §5.2 is present and
green. No skip, no `expectedFailure`, no conditional class registration in
`atelier/tests/`.

**G4 — The three key-safety behaviours are pinned.** (a) `assert_official_host` refuses
an unofficial host for openai, gemini and ollama, and the refusal happens before any
socket call; (b) `public_status()` never emits a full secret for any input length,
including short and empty keys; (c) a stored key round-trips through `put`/`get_secret`
with the env var absent. Removing any host check must turn the suite red.

**G5 — The HTTP contract is pinned, and provider failure is honest.** Every route in
`server.py` has at least one happy-path and one error-path test; response field *types*
are asserted, not just presence; and a run with an unreachable provider either fails
loudly or returns a result whose message and `plan.route` say `demo`. The current
behaviour — 200 OK with a demo SVG under a message reading "Route: openai /
gpt-4o-mini" — is the specific thing this gate forbids. **This gate requires a product
decision, not just a test.** My recommendation: return 200 with an explicit
`"downgraded": {"from": "openai", "reason": "..."}` field, surface it in the message,
and record it on the artifact. Fail-loud is defensible too. Silent-and-mislabelled is not.

**G6 — Mutation score ≥ 70% on the §4.1 battery, with all four Critical/High
key-safety mutants killed.** This replaces a coverage target. The mutation script is
~60 lines; check it into `atelier/tests/tools/` and run it before releases, not on
every push.

**Explicitly not in the bar:** browser tests, the eval scorecard, ΔE brand compliance,
the 172 research tests, load testing, and anything from `01-product-spec/ACCEPTANCE.md`
(which describes a product with video engines, spot edit, PSD export and a credit
ledger — a different and much larger thing than what ships today).

---

## 7. Exact tests to port first

Ordered. Every entry names the research source, the live target, and the assertion
**against the live API**, because as established in §3 essentially none of these can be
lifted verbatim. Target file for all P0/P1 items is `atelier/tests/`.

### P0 — required for G2/G3/G4 (do these first; ~1 file of work, no production changes)

| # | Test | Source | Live-API assertion |
|---|---|---|---|
| 1 | `setUpModule` scrubs provider env + blocks sockets | `10-eval` `LIVE_KEY_ENVS` + `forbid_network` (lines 153–156, 215–232) | Port near-verbatim. Delete the 8 key vars from `os.environ`; patch `socket.socket.connect` and `socket.create_connection` to raise. Restore in `tearDownModule`. |
| 2 | `test_no_test_is_skipped` | new (policy §5.2) | `result.skipped == []`. |
| 3 | `test_put_persists_without_env` | `03-keyring-spokes/tests/test_keyring.py` | With env scrubbed: `Keyring(tmp).put("openai", key="sk-…")` then a **fresh** `Keyring(tmp).get_secret("openai")` returns it. Kills the "`put` is a no-op" mutant that §4.3 shows survives today. |
| 4 | `test_public_status_never_leaks` | `test_keyring.py` redaction cases | For key lengths 0, 1, 8, 9, 64: the full secret does not appear in `json.dumps(public_status())`. Currently `hint` is `secret[:3]+"…"+secret[-4:]`, so a 9-char key exposes 7 of 9 characters — assert a max exposed-character count, not just non-equality. |
| 5 | `test_env_beats_keyring_and_is_labelled` | `test_keyring.py` | With `OPENAI_API_KEY` set, `get_secret` returns the env value and `source == "env"`; with it unset and a stored key, `source == "keyring"`; with neither, `source == "none"` and `configured is False`. |
| 6 | `test_official_host_enforced_per_provider` | `test_openai_spoke.py` / `test_gemini_spoke.py` host cases | `assert_official_host` accepts `api.openai.com` and `sub.api.openai.com`, raises `SpokeError` for `evil.example.com`, `api.openai.com.evil.com`, and the empty host. **Kills the two Critical mutants.** |
| 7 | `test_spoke_refuses_unofficial_base_url_before_network` | `10-eval` `test_live_provider_without_key_fails_loud_before_network` | Keyring holds `base_url=https://evil.example.com` and a key; `OpenAISpoke(...).chat(...)` raises `SpokeError` **inside `forbid_network`** — proving refusal precedes the socket. Same for `GeminiSpoke` and `OllamaSpoke`. |
| 8 | `test_missing_key_raises_not_falls_back` | `test_openai_spoke.py` | With no key configured, each live spoke raises `SpokeError` whose message names the env var and does not contain any key material. |
| 9 | `test_build_spoke_maps_every_provider` | `03-keyring-spokes/tests/test_gateway.py` | `build_spoke` returns `OpenAISpoke`/`GeminiSpoke`/`OllamaSpoke`/`DemoSpoke` for the documented names. Kills the "always DemoSpoke" mutant. Also asserts the current `anthropic` → `DemoSpoke` behaviour so §5.6 becomes a visible decision. |

### P1 — required for G5 (needs a server fixture; one may need a product decision)

| # | Test | Source | Live-API assertion |
|---|---|---|---|
| 10 | `ServerTestCase` fixture | new | `ATELIER_RUNTIME`/`ATELIER_HOME` → temp dirs **before** importing `atelier.server` (module-level `APP = App()`); `ThreadingHTTPServer` on port 0; tear down and delete temp dirs. Everything below builds on this. |
| 11 | `test_health_contract` | new | `GET /api/health` → 200, `{"ok": True, "name": "atelier", "architecture": "helix"}`, `Content-Type: application/json; charset=utf-8`, `Cache-Control: no-store`. |
| 12 | `test_brand_kit_type_is_consistent` | `04-helix-arch/test_store.py` snapshot tests | `type(GET /api/projects → projects[0]["brand_kit"]) == type(GET /api/projects/{id} → ["brand_kit"]) == dict`. **Fails today** (§5.3) — fix `list_projects` to `json.loads` the column. |
| 13 | `test_keys_endpoint_never_returns_secrets` | `test_keyring.py` | `POST /api/keys` with a key, then `GET /api/keys`: the raw key is absent from the response body. The HTTP-level twin of #4. |
| 14 | `test_provider_failure_is_not_silently_relabelled` | `10-eval` `test_live_provider_without_key_fails_loud_before_network`; `EVAL.md` §7 | `POST /api/threads/{id}/run` with `provider=openai` and no key: **G5's gate.** Assert the chosen contract — my recommendation, `plan.route.provider == "demo"` and the message names the downgrade. Write the test to the decision, then make it pass. |
| 15 | `test_run_records_usage_and_pins_nodes` | `10-eval` `test_every_spoke_call_lands_in_the_ledger` | After a demo run: `GET /api/usage` totals include the run's events; `GET /api/projects/{id}/board` contains a node per artifact; every image node has a non-null `artifact_id`. |
| 16 | `test_artifact_download_round_trip` | `10-eval` `test_manifest_matches_protocol_and_disk` | `GET /api/artifacts/{id}` returns 200, `image/svg+xml`, bytes matching the file on disk. Kills the "path never persisted" mutant. |
| 17 | `test_board_pins_do_not_stack` | `10-eval` `test_canvas_pin_appears_in_board_scene` | After a 3-artifact run, the `(x, y)` pairs are distinct. Kills the `(0,0)` mutant. |
| 18 | `test_node_update_allowlist` | `04-helix-arch` I5/geometry tests | `POST /api/nodes/{id}` with `{"x": 10, "artifact_id": "hijacked", "id": "evil"}` moves `x` and leaves `artifact_id`/`id` untouched. Kills the allowlist mutant. |
| 19 | `test_error_paths` | new | Unknown GET/POST → 404 `{"error": …}`; malformed JSON body → 400; run against a missing thread → 404; `/web/../../etc/passwd` and its percent-encoded form → 404. (All correct today — pin them.) |
| 20 | `test_patch_is_post` | new | `PATCH /api/projects` → 201. Pins the `do_PATCH = do_POST` aliasing so a future refactor is a deliberate change, not an accident. |
| 21 | `test_weave_is_capped` | `05-conductor` fixture-routing tests | A plan with 9 weave items produces ≤ 4 artifacts. Kills the uncapped-spend mutant. |
| 22 | `test_thinking_mode_produces_a_critique` | `10-eval` `test_thinking_mode_critiques_and_accepts` | `mode="thinking"` → `plan["critique"]` non-empty and the message contains `"Critique:"`; `mode="fast"` → neither. Kills the "never critiques" mutant. |
| 23 | `test_catalog_payload_is_whole` | live `test_catalog_is_100`, strengthened | `len(cat["projects"]) == cat["count"] == 100` **and** repos unique **and** `mvp_wire ⊆ repos`. The current test passes against a 10-project payload (§4.2). |

### P2 — after the bar (each carries a real cost; sequence deliberately)

| # | Test | Cost / note |
|---|---|---|
| 24 | Fake-transport spoke tests: request shape, response parse, token accounting, HTTP-error mapping for OpenAI and Gemini | Port `test_openai_spoke.py` / `test_gemini_spoke.py` + `fakes.py` + recorded fixtures. Needs a seam in `_post` (patch `urlopen`, or accept an `opener`). ~50 tests. The largest single coverage win available — spokes are at 21–40%. |
| 25 | `live_smoke.py` retargeted to `build_spoke`, plus the negative host-refusal smoke | Port `03-keyring-spokes/live_smoke.py`; keep `ATELIER_LIVE=1`; never in CI (§5.5). |
| 26 | Playwright: load board, run a demo brief, drag a node, assert `x`/`y` persist across reload | First `package.json` and first dependency in the repo. The state-corrupting half is coverable without a browser via #18. |
| 27 | Determinism / byte-identical reruns | `10-eval` `test_reruns_are_byte_identical` needs an injected clock and fixed run id; live `Conductor` has neither. Product change first. |
| 28 | Plan-envelope validation | The 14 `ConductorParseTests.test_rejects_*` cases are the best-designed tests in the repo, but they validate `conductor-plan/1`, which the live conductor does not implement (§3). Adopt only if the protocol is adopted. |

**Do not port:** `04-helix-arch/test_store.py` (tests a `schema.sql` the product does not
use), `05-conductor/tests/test_conductor.py` (tests `parse_plan`/`route_plan`, which do
not exist live), `test_anthropic_spoke.py` (no Anthropic spoke ships), and the `--eval`
scorecard (a qualitative research instrument, not a gate — `EVAL.md` §8.3 itself notes
the scores reflect a deterministic planner and will degrade with a real one).

---

## 8. Reproducing everything above

```bash
# live suite
cd /workspace && python3 -m unittest atelier.tests.test_helix -v            # 7 tests, OK

# research suites
cd atelier/research/fable5/10-eval          && python3 test_helix.py         # 58, OK*
cd ../03-keyring-spokes                     && python3 run_tests.py          # 68, OK
cd ../04-helix-arch                         && python3 test_store.py         # 10, OK
cd ../05-conductor                          && python3 tests/test_conductor.py  # 36, OK

# *the asterisk — 58/58 depends on a scratch dir that will not exist on a clean machine
cd ../10-eval && ATELIER_ROOT=/tmp/nope python3 test_helix.py               # OK (skipped=27), exit 0

# eval harness vs. the code that actually ships
ATELIER_ROOT=/tmp/nope \
ATELIER_CONDUCTOR=/workspace/atelier/helix/conductor.py \
ATELIER_USAGE=/workspace/atelier/helix/usage.py \
ATELIER_LOOM=/workspace/atelier/helix/loom.py python3 test_helix.py         # FAILED (errors=17, skipped=10)

# the vacuous-test proof (§4.3), against a mutated copy in /tmp
env -u OPENAI_API_KEY python3 -m unittest atelier.tests.test_helix

# coverage (stdlib, no dependencies)
python3 -m trace --count --missing --coverdir=/tmp/cov runtests.py          # helix 75.9%, server.py absent
```

Mutation battery: `/tmp/mutate.py` (12 seeded defects, 2 caught). Worth checking into
`atelier/tests/tools/` as part of G6.
