# Fable-08 · R15 host-pin — verified

Verifier: one live `claude-fable-5-thinking-high` agent, branch
`cursor/atelier-byok-studio-d639`, HEAD at `26f8194` (Round 15).
Method: read the live tree, exercise `Keyring`, `assert_official_host`,
`urlopen_no_redirect` and `_download` with real imports; drive a real
`ThreadingHTTPServer` on loopback for the redirect claim; mock the opener
only where a fetch would otherwise leave the machine. No external network,
no key read, no paid call.

**Verdict: PASS with fixes.** All five claims held as shipped. What did not
hold was the *belt* under the image-fetch allow-list: `is_blocked_fetch_host`
only knew dotted-quad IPv4 and the literal `::1`, so IPv6 mapped/unique-local/
link-local addresses and legacy IPv4 spellings sailed past it. Nothing was
exploitable through `_download` today — the CDN suffix allow-list rejects
those hosts anyway — but the function's docstring promises "never fetch here",
and a belt that misses `::ffff:127.0.0.1` is a hole waiting for the next
caller. Hardened with stdlib `ipaddress`.

## Claim by claim

| # | Claim | Verdict |
|---|-------|---------|
| 1 | `Keyring.put("openai"\|"gemini", base_url=unofficial)` → `ValueError`; `http://api.openai.com` rejected; Ollama may stay `http://127.0.0.1`; `openai_compat` free-form | PASS |
| 2 | `OpenAISpoke._url` / `GeminiSpoke._url` call `assert_official_host(..., require_https=True)`; empty host / suffix mismatch raise `SpokeError` | PASS |
| 3 | Credentialed POSTs go through `urlopen_no_redirect`; `NoRedirectHandler` returns None; mocked 302 → `SpokeError` naming the redirect | PASS (also proven live on loopback) |
| 4 | `_download` refuses `file:`, `http:`, loopback, RFC1918, link-local, unknown https hosts; the four CDN suffixes are the allow-list | PASS, belt hardened |
| 5 | `http.py` has no top-level spokes import; `http` → `openai_spoke` import order succeeds | PASS |

## Path traced

Settings → `Keyring.put(provider, key, base_url)` lowercases the provider
and, for any provider in `ALLOWED_HOST_SUFFIXES` (openai, gemini, anthropic,
ollama), runs the candidate `base_url` through
`assert_official_host(url, suffixes, require_https=provider != "ollama")`
before a byte is written — `SpokeError` is re-raised as `ValueError`.
`openai_compat` is not in `ALLOWED_HOST_SUFFIXES`, so a user-set vLLM /
LM-Studio host stays free-form by design.

At call time the pin is re-checked: `OpenAISpoke._url` asserts
`("api.openai.com",)` with `require_https=True` whenever `self.name ==
"openai"` (the compat alias skips it), `GeminiSpoke._url` asserts
`("generativelanguage.googleapis.com",)`, `OllamaSpoke._url` asserts
`("127.0.0.1", "localhost")` without the https requirement. This is defense
in depth — a `base_url` written straight into `keyring.json` behind `put`'s
back is still refused before any request object is built (verified by
tampering the file; both spokes raised `SpokeError`).

Every `_post` in all three spokes builds a `urllib.request.Request` and opens
it with `urlopen_no_redirect` — a grep of `atelier/helix` finds no bare
`urlopen` anywhere. The opener is `build_opener(NoRedirectHandler)`, whose
`redirect_request` returns None, making urllib raise `HTTPError` on any 3xx
instead of replaying Authorization at the Location. `urlopen_no_redirect`
catches 3xx `HTTPError` and raises
`SpokeError("Refusing HTTP redirect 302 to https://evil.example/steal")`;
the `SpokeError` import lives *inside* that except branch, which is what
keeps `http.py` free of a top-level spokes import (claim 5 — a fresh
interpreter importing `atelier.helix.http` then
`atelier.helix.spokes.openai_spoke` exits 0).

OpenAI images may come back as a URL instead of `b64_json`. `_download`
requires `https`, runs the hostname through `is_blocked_fetch_host`, then
requires a label-boundary match against `IMAGE_FETCH_SUFFIXES =
("api.openai.com", "openai.com", "oaiusercontent.com",
"blob.core.windows.net")`, and only then opens — via `urlopen_no_redirect`,
so the CDN cannot 302 the fetch somewhere else either. Gemini's image path
has no URL fetch at all: `inlineData` base64 or `SpokeError`.

## Evidence

Claim 1 — live `Keyring` on a temp file:

```
put openai  https://chatgpt.com            ValueError: Refusing unofficial host chatgpt.com
put openai  http://api.openai.com          ValueError: Refusing non-https official host (http)
put gemini  https://evil.example           ValueError: Refusing unofficial host evil.example
put openai  https://api.openai.com@evil.example/  ValueError: Refusing unofficial host evil.example
put openai  https://notapi.openai.com      ValueError: Refusing unofficial host notapi.openai.com
put ollama  http://evil.example:11434      ValueError: Refusing unofficial host evil.example
put openai  https://api.openai.com         ok    put ollama http://127.0.0.1:11434  ok
put openai_compat https://my-vllm.example/v1  ok  (free-form, by design)
```

Claim 2 — `keyring.json` edited on disk behind `put`'s back:

```
openai base_url → https://evil.example      OpenAISpoke._url  SpokeError: Refusing unofficial host evil.example
gemini base_url → http://generativelang…    GeminiSpoke._url  SpokeError: Refusing non-https official host (http)
assert_official_host("https://", …)                           SpokeError: Refusing empty host for https://
```

Claim 3 — a real `ThreadingHTTPServer` on `127.0.0.1:<ephemeral>` answering
302 with `Location: https://evil.example/steal`, POSTed with an
Authorization header through the *real* opener chain:

```
urlopen_no_redirect(POST /v1/chat/completions)  SpokeError: Refusing HTTP redirect 302 to https://evil.example/steal
server saw exactly one request; nothing was replayed anywhere
NoRedirectHandler().redirect_request(...302...)  → None
```

Claim 4 — `_download` refusals, then a permitted URL with the opener mocked:

```
file:///etc/passwd                       Refusing non-https image URL (file)
http://oaiusercontent.com/x.png          Refusing non-https image URL (http)   (right host, wrong scheme)
https://127.0.0.1/x.png                  Refusing private image host 127.0.0.1
https://10.0.0.5/x.png                   Refusing private image host 10.0.0.5
https://169.254.169.254/latest/meta-data Refusing private image host 169.254.169.254
https://evil.example/x.png               Refusing unofficial image host evil.example
https://evilopenai.com/x.png             Refusing unofficial image host evilopenai.com
https://openai.com.evil.example/x.png    Refusing unofficial image host openai.com.evil.example
https://oaidalleapiprodscus.blob.core.windows.net/private/img.png?sig=x
    → reached mocked urlopen_no_redirect exactly once; mime parsed image/png
```

Claim 5:

```
python3 -c "import atelier.helix.http; import atelier.helix.spokes.openai_spoke; print('ok')"  → ok
top-level imports in http.py: __future__, urllib.error, urllib.request  (spokes.base only inside the except)
```

## Hole found and closed

**`is_blocked_fetch_host` missed every non-dotted-quad spelling of a private
address.** Shipped code checked a literal set plus a hand-rolled dotted-quad
parse, so all of these returned False: `::ffff:127.0.0.1` (IPv4-mapped
loopback), `fd00::1` (unique-local), `fe80::1` (link-local), `2130706433`
(decimal 127.0.0.1), `127.1` and `0x7f.0.0.1` (legacy inet_aton forms the
socket connector happily resolves). Not exploitable through `_download`
today — the suffix allow-list is the real gate and rejected them all — but
the belt now parses with `ipaddress.ip_address`, falls back to
`socket.inet_aton` for legacy IPv4 spellings, unmaps `::ffff:` addresses,
and blocks anything not `is_global` (which also picks up shared address
space `100.64/10`, multicast, reserved and unspecified). Public IPs and CDN
hostnames still pass. Against shipped `26f8194` the tightened test fails at
`::ffff:127.0.0.1`; with the fix all pass.

### Checked and *not* a hole

- **Suffix matching is label-anchored.** `host == s or
  host.endswith("." + s)` — `evilopenai.com`, `notapi.openai.com` and
  `openai.com.evil.example` are all refused; `us.api.openai.com` (a real
  OpenAI subdomain) passes.
- **Userinfo tricks don't parse as the pinned host.**
  `https://api.openai.com@evil.example/` — `urlparse().hostname` is
  `evil.example`, refused.
- **Gemini has no image URL fetch** — `inlineData` or `SpokeError`, so there
  is no Gemini analog of `_download` to pin.
- **The key never rides a redirect even off-host.** Gemini's key travels as
  a query parameter, OpenAI's as a Bearer header; both requests go through
  the same no-redirect opener, and the live-302 test shows one request,
  no replay.

## Tests

`atelier/tests/evolve/test_fable_08.py` — was 7 tests; now 13. New:
lookalike/userinfo/empty-host refusals; IPv6-and-legacy-spelling block list
(bites on shipped code); tampered-keyring-file re-check at `_url`; a real
loopback 302 through the real opener chain (one request, no replay); a
permitted CDN URL proven to reach `urlopen_no_redirect` by mock; the
`http` → `openai_spoke` import order in a fresh interpreter.
`Round15HostPin` and `SecurityHarden` in `atelier/tests/test_evolve.py`
pass untouched.

```
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve \
    atelier.tests.evolve.test_fable_08
Ran 49 tests — OK
```

Full tree (`unittest discover -s atelier/tests`): 311 tests, OK
(1 expected failure, pre-existing).

## Remaining holes (none blocking)

- **DNS rebinding.** We pin the *name*, not the resolution: a pinned host
  that resolves to a private IP at connect time is not caught (we parse the
  hostname, we never resolve it). Real fix is resolve-then-connect-by-IP
  with the Host header pinned; out of the stdlib-slice budget here.
- **`openai_compat` is free-form by design** — a user who points it at a
  hostile host has configured that host on purpose; the key sent there is
  the compat key, never the official OpenAI one, and redirects are still
  refused.
- **Anthropic is in `DEFAULT_HOSTS` / `ALLOWED_HOST_SUFFIXES` but has no
  spoke** (`build_spoke` raises on it). Dead config today; the pin is
  already in place for whenever the spoke lands.
- **No TLS certificate pinning** — we trust the system CA store, same as
  every other stdlib HTTPS client.
