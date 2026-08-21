# Key Handling Policy

Binding rules for all Atelier code that can touch a provider API key. "Key" means
any BYOK credential (OpenAI `sk-…`, Google `AIza…`, OAuth/bearer tokens) and any
string derived from one except its fingerprint.

## 1. Never log raw keys

- **No raw key may ever be written to any log, at any level, in any build.** This
  includes debug logs, tracebacks, HTTP wire logs, and "temporary" prints.
- Structured logging only, through the shared logger, which installs a **redaction
  filter** as the last formatting step. The filter applies the same patterns as
  `usage.scrub_secrets()` (OpenAI-style `sk-…`, Google `AIza…`, `Bearer …`) to the
  final rendered message and all attached fields, replacing matches with
  `[REDACTED]`. The filter is a backstop, not a license: code that *relies* on the
  filter to strip a key it deliberately logged fails review.
- Never log: request/response header dicts, full request objects, provider client
  configs, or environment snapshots. Log the derived facts instead (status code,
  model, token counts, request id).
- Exception paths are log paths: provider-client exceptions are wrapped before
  logging so their messages/`repr` cannot embed auth headers. The `Secret` wrapper
  type (see `KEYRING_HARDENING.md`) makes `repr()` return the fingerprint only.
- Verification: CI runs the full E2E suite with a canary key
  (`sk-canary000...`), then greps every produced artifact (logs, ledger DB dump,
  crash reports, screenshots of terminal output) for the canary and the key
  regexes. Any hit fails the build.

## 2. Redact in API responses

The local backend's HTTP API (consumed by the canvas UI) **never returns a raw
key**, including on the settings screens that manage keys:

- `GET /api/keys` returns only: provider, key **fingerprint** (first 8 hex of
  SHA-256), a masked display form (`sk-…abcd`, last 4 characters only), created-at,
  and last-verified-at. There is no endpoint that returns a stored key. "Reveal
  key" is not a feature; users who lose a key re-paste it from the provider console.
- `POST /api/keys` accepts a key once, stores it (keyring), and responds with the
  fingerprint record above — the response body must not echo the submitted key,
  and the request body is exempted from any request-logging middleware.
- Error responses are built from our own error types, never by string-formatting a
  provider exception into the body. A global response middleware applies the
  redaction patterns to every outgoing JSON/text body as a final backstop, and
  increments a `redaction_backstop_hits` counter — any nonzero value is a bug to
  investigate, since the primary controls should make the backstop unreachable.
- Masked display form rules: show at most the last 4 characters; never show
  prefix + suffix combinations long enough to aid brute force; fingerprints are
  safe to log and display freely.

## 3. Where keys may exist (exhaustive)

1. OS keychain, under service `atelier` (`KEYRING_HARDENING.md`).
2. Backend process memory, inside the key-broker module's `Secret` wrapper.
3. The `Authorization`/`x-goog-api-key` header of an outbound HTTPS request to
   the provider.

Anything else — browser storage, ledger rows, project files, exports, subprocess
argv/env, clipboard writes, telemetry — is a policy violation. The usage ledger
(`usage.py`) additionally scrubs key-shaped strings from metadata on write, so a
violation upstream does not become a persistent one.

## 4. Spend accountability

- Every provider call is recorded in the usage ledger with provider, model, units,
  estimated cost, and thread id — no exceptions, including failed calls where the
  provider billed us (record what was sent).
- Budget checks (`BudgetGuard.check`) run **before** the call, using a strict cost
  estimate; unpriceable calls (unknown model/unit) are refused rather than allowed
  to bypass the budget. The `unpriced_count()` metric must remain zero.
- The user can always see: today's spend, per-thread spend, and the price-table
  date (`PRICES_AS_OF`). If the price table is older than 30 days, the UI shows a
  staleness notice on cost figures.

## 5. Incident response (suspected key exposure)

1. Treat any confirmed appearance of a raw key outside the three locations in §3
   as an incident, even with no evidence of exfiltration.
2. Tell the user immediately in-app: which provider key, where it leaked, and a
   one-click link to the provider's key-revocation console
   (OpenAI: platform API-keys page; Google: Cloud Console credentials page).
3. The app offers to delete the stored key and re-run setup with a fresh one.
4. Fix the leak path, add a regression test that greps for the canary key in that
   artifact class, then ship.

## 6. Enforcement

- Code review checklist item for any PR touching logging, HTTP handlers, provider
  clients, or the key broker.
- Pre-commit + CI secret scanning (gitleaks or equivalent) on the repo itself, so
  developer/test keys never land in git.
- The canary E2E grep (§1) and the `redaction_backstop_hits` counter (§2) are the
  runtime tripwires; both are release blockers when nonzero.
