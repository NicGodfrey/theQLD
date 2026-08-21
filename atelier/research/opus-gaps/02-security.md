# Atelier BYOK — Security & Quota Gap Analysis

**Author:** Opus#2 of 10
**Date:** 2026-08-21
**Scope:** live `atelier/helix/keyring.py`, `atelier/helix/usage.py`, `atelier/helix/spokes/*`,
`atelier/server.py` (plus `helix/conductor.py`, `helix/store.py`, `web/app.js`, `web/index.html`
where they carry a security invariant) measured against the research specs in
`atelier/research/fable5/03-keyring-spokes/` and `atelier/research/fable5/08-security-quota/`.

**Question answered:** what must change before a real user pastes a real `sk-…` into this app.

**Method.** Read both trees, then reproduced each claimed defect against a *copy* of the runtime
(`ATELIER_HOME=/tmp/atelier-probe/h2`, `ATELIER_RUNTIME=/tmp/atelier-probe/rt`, port 8791) using a
canary key `sk-canary000000000000000000000000AAAA`. `/workspace` was not modified. Findings marked
**[verified]** were observed, not inferred; reproduction commands are in Appendix A. Findings marked
**[by inspection]** are read from code without a runtime probe.

**Severity scale.**

| | Meaning |
|---|---|
| **S0** | Blocker. Leads to raw-key disclosure or unbounded uncontrolled spend. Do not ship with a real key. |
| **S1** | High. Breaks a hard rule in `CONTRACT.md §1` / `POLICY.md`; exploitable with a modest precondition. |
| **S2** | Medium. Defense-in-depth or accounting-accuracy gap the research specifies and the live code omits. |
| **S3** | Low. Hygiene, naming, or divergence with no direct attack path. |

---

## Headline

The live code has the *shape* of the research design — there is an `assert_official_host`, there is a
`public_status()` that masks, there is an `assert_budget` — but in three places the control is applied
at the wrong layer, and that turns each one into a no-op:

1. **Host pinning is applied to the configured base URL, not to the socket that carries the key.**
   `urllib` follows 302s and replays `Authorization`, so the pin is bypassed by any redirect
   (**G02**), and it is skipped entirely for `openai_compat` (**G04**).
2. **The budget is checked inside `usage.record()`, which the conductor calls *after* the provider
   call has already been billed** — and when the check trips, the row is never written, so the ledger
   permanently under-reports and the guard never converges (**G16**). Six billed image generations in
   a row were all refused by the guard while the ledger stayed at `$0.0000`.
3. **The keyring is a plaintext file, and the HTTP server will serve any file on disk.** One
   unauthenticated `GET` returns the raw key (**G01**).

Nothing here is exotic. All ten blockers are small, local fixes; the largest is ~60 lines.

### Top-10 blockers

Ordered by ship priority (what to fix first, not merely by severity):

| # | ID | Sev | Blocker | Evidence |
|---|---|---|---|---|
| 1 | **G01** | S0 | Path traversal in the static handler returns `keyring.json` — raw `sk-…` over HTTP, unauthenticated | `server.py:104-111,153-156` |
| 2 | **G16** | S0 | Budget checked *after* the billed call, and the refused event is never recorded → unbounded real spend while the UI shows `$0.0000` | `usage.py:98-109` + `conductor.py:107-124,178-185` |
| 3 | **G03** | S0 | No session token, no `Origin`/`Host` validation → any web page can drive paid runs; DNS rebinding reads every endpoint | `server.py:94-223` |
| 4 | **G02** | S0 | Redirects followed with `Authorization` intact → key exfiltrated to any `Location` host | `spokes/openai_spoke.py:36-47` |
| 5 | **G13** | S0 | Attacker/model-controlled SVG served inline, same-origin, no CSP → XSS that reads the key via G01 | `server.py:77-91,153-156`; `web/index.html:79` |
| 6 | **G07** | S1 | `_download()` follows provider-supplied URLs with no scheme/IP allowlist — `file://` and `169.254.169.254` both work | `spokes/openai_spoke.py:79-90` |
| 7 | **G04** | S1 | `openai_compat` has no host pin, no TLS requirement; with no `base_url` it ships the compat key to `api.openai.com` | `spokes/openai_spoke.py:30-34`; `keyring.py:23` |
| 8 | **G09** | S1 | Keyring written `0644` then chmod'd (TOCTOU), non-atomic, follows symlinks, parent dir `0755` | `keyring.py:43,50-55` |
| 9 | **G23** | S1 | `{"error": str(exc)}` returns arbitrary exception text to the browser; no redaction filter anywhere in the tree | `server.py:210-211`; `spokes/openai_spoke.py:47` |
| 10 | **G17** | S1 | Unpriceable models silently guessed instead of refused → budget bypass by model choice | `usage.py:62-66` |

**The 11th item is an architectural decision, not a patch.** `08-security-quota/KEYRING_HARDENING.md`
requires the OS keychain with a fail-closed backend check and *no* plaintext fallback;
`03-keyring-spokes/CONTRACT.md §4` specifies exactly the `0600` JSON file the live code implements.
The two research docs conflict, and the live code follows the weaker one (**G08**). My
recommendation: keep the file for v1 but fix **G01** and **G09** first, then treat the keychain as a
follow-on — a correctly-written `0600` file in a non-synced directory is a defensible answer to
attacker A4, whereas a world-readable window plus an HTTP read primitive is not. Do not ship the
file store without also shipping the "exclude from cloud sync" documentation
`KEYRING_HARDENING.md:82-83` asks for.

---

## 1. Key confidentiality and host pinning

### G01 — Path traversal in the static file handler exposes the raw keyring · **S0** · [verified]

**Evidence:** `atelier/server.py:104-111` and `153-156`.

```153:156:atelier/server.py
        candidate = WEB / path.lstrip("/")
        if candidate.exists():
            _send_file(self, candidate)
            return
```

`BaseHTTPRequestHandler` does not normalize `..`, and `urlparse().path` preserves it, so
`WEB / "../../../../tmp/..."` resolves outside `WEB`. The `/web/` and `/assets/` prefix branches at
`:104-111` have the same defect via `path[len("/web/"):]`.

**Verified:** `GET /../../../../tmp/atelier-probe/h2/keyring.json` returned
`{"providers": {"openai": {"key": "sk-canary000000000000000000000000AAAA", ...}}}` with HTTP 200.
This is the whole T1 threat model in one request: the key is on disk in plaintext
(`keyring.py:50-51`) and the server will read any path. Percent-encoded `%2e%2e` is *not* traversable
(the URL is not unquoted before joining), which is the only reason this isn't trivially reachable
from a plain `<img>` tag.

**Ship fix.** Resolve and confine, and stop deriving filesystem paths from request paths at all:

```python
def _safe_web_path(rel: str) -> Path | None:
    candidate = (WEB / rel.lstrip("/")).resolve()
    web_root = WEB.resolve()
    if candidate == web_root or web_root in candidate.parents:
        return candidate
    return None
```

Use it in all four static branches, and additionally serve only from an explicit allowlist
(`index.html`, `app.js`, `styles.css`) since `WEB` holds exactly three files. Reject any request path
containing `..` before routing. `resolve()` also closes the symlink-escape variant.

**Test to add:** `GET /../../etc/passwd`, `/web/../../../etc/passwd`, `/assets/..%2f..%2fetc/passwd`,
and a traversal aimed at the live keyring path all return 404, asserted against a keyring holding a
canary string that must not appear in any response body.

---

### G02 — Redirects replay `Authorization` to an attacker-chosen host · **S0** · [verified]

**Evidence:** `atelier/helix/spokes/openai_spoke.py:36-47` (same pattern in `gemini_spoke.py:34-47`,
`ollama_spoke.py:23-36`).

```36:45:atelier/helix/spokes/openai_spoke.py
    def _post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(
            self._url(path),
            data=json.dumps(body).encode(),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
```

`urllib.request.urlopen` uses the default `HTTPRedirectHandler`, whose `redirect_request` copies all
request headers except `Content-Length`/`Content-Type` onto the new request. `assert_official_host`
runs once, against the *configured* base URL, and never again for the redirect target.

The research calls this out explicitly and solves it centrally
(`03-keyring-spokes/spokes_base.py:240-251`, `CONTRACT.md:44-48`):

```240:244:atelier/research/fable5/03-keyring-spokes/spokes_base.py
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Returning None makes urllib raise the 3xx as an HTTPError instead
        # of replaying our headers (Authorization included) at `newurl`.
        return None
```

**Verified:** a local 302 responder received `POST` with
`Authorization: Bearer sk-canaryREDIRECT0000000000000` and the follow-up `GET /stolen302` arrived at
a *different* origin **carrying the same header**. (307 is raised as `HTTPError` by urllib, so only
301/302/303 replay — which is the majority of redirect responses.)

**Ship fix.** Build one opener in `spokes/base.py` and route every spoke through it:

```python
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

_OPENER = urllib.request.build_opener(_NoRedirect())
```

Replace all three `urllib.request.urlopen(req, ...)` call sites with `_OPENER.open(req, ...)`, and
map the resulting 3xx `HTTPError` to a distinct error ("provider redirected a credentialed request;
refusing to follow") so it is diagnosable rather than looking like a provider outage.

**Test to add:** a scripted transport/local server that 302s; assert the spoke raises and assert the
redirect target never observes an `Authorization` header. This is the "one key-guard assertion" the
research checklist requires of every spoke (`CONTRACT.md:296-309`).

---

### G03 — No session token, no `Origin`/`Host` validation: CSRF and DNS rebinding · **S0** · [verified]

**Evidence:** `atelier/server.py:94-223`. `rg` for `Content-Security|Origin|Host|token|nosniff`
across the live tree returns nothing but unrelated hits in `data/top100.json`. Every endpoint —
including `POST /api/keys` (`:169-179`) and the spend-capable `POST /api/threads/<id>/run`
(`:196-214`) — is unauthenticated and unvalidated.

`THREAT_MODEL.md:120-124` requires: a per-session bearer token minted at startup and passed
out-of-band, `Host`/`Origin` validated against `127.0.0.1`/`localhost`, loopback binding.
Only the last of the three is present (`server.py:226`).

**Verified, two ways:**

- **CSRF.** `_read_json` (`server.py:67-74`) ignores `Content-Type` and just `json.loads` the body.
  A cross-origin `POST` with `Content-Type: text/plain` is a CORS *simple request* — no preflight, so
  the absent `do_OPTIONS` handler doesn't save us. `POST /api/threads/<id>/run` with
  `Origin: https://evil.example` and `Content-Type: text/plain` executed a full run and wrote usage
  rows. With `"provider":"openai"` that is the victim's metered quota, driven from any tab.
- **DNS rebinding.** `GET /api/keys` with `Host: evil.example` returned 200 and the full key status
  (sources, base URLs, hints). No `Host` check means an attacker domain that rebinds to `127.0.0.1`
  becomes same-origin and can read *every* response, including G01's raw key.

**Ship fix.** Three changes in `server.py`, all small:

1. Mint `TOKEN = secrets.token_urlsafe(32)` at startup. Print the UI URL as
   `http://127.0.0.1:8765/?t=<TOKEN>`; `app.js` reads it once from `location.search`, stores it in a
   module variable (not `localStorage`), strips it from the URL via `history.replaceState`, and sends
   it as `Authorization: Bearer <token>` on every `api()` call. Require it on every `/api/*` route
   with `hmac.compare_digest`; return 401 otherwise.
2. Reject any request whose `Host` header is not `127.0.0.1[:port]` / `localhost[:port]`, and any
   request carrying an `Origin` other than the server's own — before routing.
3. Require `Content-Type: application/json` in `_read_json`, which removes the simple-request path
   even if 1 and 2 regress.

**Test to add:** unauthenticated `/api/*` → 401; `Host: evil.example` → 403; cross-`Origin` POST →
403; `Content-Type: text/plain` POST → 415; and a positive test that the tokened UI still works.

---

### G04 — `openai_compat` is completely unpinned, and misconfiguration ships its key to OpenAI · **S1** · [verified]

**Evidence:** `atelier/helix/spokes/openai_spoke.py:30-34`.

```30:34:atelier/helix/spokes/openai_spoke.py
    def _url(self, path: str) -> str:
        base = self.keyring.get_base_url(self.name) or "https://api.openai.com"
        if self.name == "openai":
            assert_official_host(base, ("api.openai.com",))
        return f"{base}{path}"
```

For `openai_compat` there is no host check, no scheme check, and no loopback rule — the key from
`OPENAI_COMPAT_API_KEY` / the keyring goes wherever `base_url` points, over cleartext if asked.
`keyring.py:23` sets `DEFAULT_HOSTS["openai_compat"] = ""` and there is no entry in
`ALLOWED_HOST_SUFFIXES` (`keyring.py:26-31`), so nothing constrains it.

The research permits a user-configured compat host but still runs the same guard on it, requiring
`https` unless the host is loopback (`spokes_base.py:297-315`, `CONTRACT.md:44-52`).

**Verified:** with `base_url=http://evil.tld:8080`, `_url()` returned
`http://evil.tld:8080/v1/chat/completions` — plaintext, arbitrary host, key attached. Separately,
with **no** `base_url` configured, `_url()` returned `https://api.openai.com/v1/chat/completions`:
the *compat* credential (potentially a corporate gateway token) is sent to OpenAI's official host.

Note this composes with **G03**: a CSRF `POST /api/keys` can set the compat `base_url` to an
attacker host, then a CSRF run exfiltrates the compat key. The `openai` provider is *not* vulnerable
to that chain — `_url` re-pins it — which is the design working correctly for one of two paths.

**Ship fix.** Port `assert_key_safe()` semantics into `spokes/base.py` and call it for **every**
provider, with the allowlist coming from the provider's own configured host:

```python
_LOOPBACK = {"localhost", "127.0.0.1", "::1"}

def assert_key_safe(url: str, allowed_hosts: tuple[str, ...], provider: str) -> None:
    parts = urlparse(url)
    host = (parts.hostname or "").lower()
    if host not in {h.lower() for h in allowed_hosts}:
        raise SpokeError(f"{provider}: refusing to send credentials to {host!r}")
    if parts.scheme != "https" and host not in _LOOPBACK:
        raise SpokeError(f"{provider}: refusing credentials over {parts.scheme!r} to {host!r}")
```

For `openai_compat`, `allowed_hosts` is the single host parsed from the stored `base_url` (so the
pin is "the host the user consciously chose, and only that host"), and a missing `base_url` must
raise rather than fall back to `api.openai.com`. Validate the URL at `Keyring.put()` time too, so the
settings panel rejects it immediately instead of at first call.

---

### G05 — `assert_official_host` allows cleartext HTTP and wildcards `.localhost` · **S1** · [verified]

**Evidence:** `atelier/helix/spokes/base.py:44-49`.

```44:49:atelier/helix/spokes/base.py
def assert_official_host(url: str, allowed_suffixes: tuple[str, ...]) -> None:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        raise SpokeError(f"Refusing empty host for {url}")
    if not any(host == s or host.endswith("." + s) for s in allowed_suffixes):
        raise SpokeError(f"Refusing unofficial host {host}")
```

Two problems. The function never looks at `parts.scheme`, so `http://api.openai.com` passes and the
bearer token crosses the network in cleartext — the research guard rejects exactly this
(`spokes_base.py:311-315`). And suffix matching is used where equality is meant: for the Ollama
allowlist `("127.0.0.1", "localhost")`, any `*.localhost` name is accepted.

**Verified:** `http://api.openai.com` → **ALLOW**. `http://evil.localhost:11434` → **ALLOW**.
The genuinely dangerous confusions are correctly rejected (`api.openai.com.evil.tld`,
`notapi.openai.com`, `127.0.0.1.evil.tld` all deny), so this is a hardening gap rather than an open
door — but `.localhost` is not universally resolved to loopback (resolver search domains and some
corporate DNS will answer it), so the wildcard is a real hole, not a theoretical one.

**Ship fix.** Fold into **G04**'s `assert_key_safe`: exact host-set membership (no suffix matching)
plus the `https`-unless-loopback rule. If subdomain support is ever needed for a provider, list the
subdomain explicitly.

---

### G06 — Gemini key travels in the URL query string · **S1** · [by inspection]

**Evidence:** `atelier/helix/spokes/gemini_spoke.py:34-36`.

```34:36:atelier/helix/spokes/gemini_spoke.py
    def _post(self, path: str, body: dict) -> dict:
        sep = "&" if "?" in path else "?"
        url = f"{self._url(path)}{sep}key={urllib.parse.quote(self._key())}"
```

The research pins Gemini auth to the `x-goog-api-key` **header**
(`CONTRACT.md:148`, provider matrix). A key in a URL is a key in a different risk class: it lands in
proxy and gateway access logs, in `Referer` on any redirect, in exception objects that carry
`full_url`, and in anything that logs a request line. `POLICY.md §3` enumerates the three places a
key may exist and "the query string of an outbound URL" is not one of them.

This is why it is S1 rather than S2 in *this* codebase specifically: it composes with **G23**
(`server.py:210-211` returns `str(exc)` to the browser) and **G02** (a 302 puts the full URL in a
`Referer`). Any future code path that stringifies a request or URL becomes a key-disclosure path.

**Ship fix.** Move to the documented header and drop the query parameter:

```python
headers = {"Content-Type": "application/json", "x-goog-api-key": self._key()}
```

**Test to add:** assert the built request has no `key=` in `full_url` and does carry
`x-goog-api-key`.

---

### G07 — SSRF/LFI: provider-supplied image URL fetched with no allowlist · **S1** · [verified]

**Evidence:** `atelier/helix/spokes/openai_spoke.py:79-90`.

```86:90:atelier/helix/spokes/openai_spoke.py
def _download(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "AtelierHelix/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        mime = resp.headers.get("Content-Type", "image/png").split(";")[0]
        return resp.read(), mime
```

`item["url"]` comes from the provider response and is fetched with no scheme allowlist, no DNS/IP
validation, no redirect control, and no size cap. `urllib` handlers include `FileHandler`, so
`file://` works. The result is written to disk as an artifact (`conductor.py:174`) and served back
over HTTP (`server.py:143-149`) — so the read is not blind, it is a full read primitive with
retrieval.

`THREAT_MODEL.md:193-202` specifies the countermeasure in detail: `https`-only, resolve-then-validate
every address against loopback/RFC1918/link-local (169.254.0.0/16 is called out by name for cloud
metadata), connect to the validated IP, no automatic redirects, size and content-type caps.

**Verified:** `_download("file:///tmp/atelier-probe/secretish.txt")` returned the file contents with
`mime: text/plain`. On a cloud VM or remote GPU box — which `THREAT_MODEL.md:181-182` explicitly
anticipates — `http://169.254.169.254/latest/meta-data/` is equally reachable. The trigger is a
malicious/compromised response body, so `openai_compat` (attacker-chosen endpoint, **G04**) makes it
directly attacker-controlled rather than requiring a compromised official provider.

**Ship fix.** Write the `safe_fetch()` the threat model specifies, once, and route every URL-touching
path through it:

- scheme `https` only;
- `socket.getaddrinfo()` then reject any resolved address where `ipaddress.ip_address(a)` is
  `is_loopback | is_private | is_link_local | is_reserved | is_multicast`, including IPv4-mapped IPv6;
- connect to the validated IP with `Host`/SNI set separately (kills rebinding TOCTOU);
- no automatic redirects (reuse **G02**'s opener); each hop re-validated, max 3;
- `Content-Length`/streamed size cap (25 MB per the spec), content-type allowlist `image/*`, no
  credentials attached.

Prefer `response_format="b64_json"` for **all** OpenAI image models where supported, so the common
path never fetches a URL at all.

---

## 2. Keys at rest

### G08 — Plaintext file store only; no OS keychain, no fail-closed, no opt-in encryption · **S1** · [by inspection]

**Evidence:** `atelier/helix/keyring.py` in whole; the key is written as
`json.dumps(data, indent=2)` at `:51`.

`08-security-quota/KEYRING_HARDENING.md:6-52` requires the `keyring` library with an explicit backend
allowlist and a hard failure when no secure backend exists, and
`THREAT_MODEL.md:74-76` states it as a mitigation: *"Fail closed if no real backend is available —
never fall back to a plaintext file."* `KEYRING_HARDENING.md:71-83` permits a file only as an
explicitly opted-into, passphrase-encrypted (`scrypt` + AES-256-GCM), `0600` store. The live code
ships the unencrypted variant as the *only* option, with no warning.

As noted in the headline, `03-keyring-spokes/CONTRACT.md §4` specifies precisely the plaintext `0600`
file that is implemented, so this is a **conflict between the two research documents**, and the live
code is a faithful implementation of one of them. That is why it is S1, not S0.

**Ship fix (staged).**

1. *Now:* fix **G09** so the file actually achieves `0600`/`0700`/atomic/no-symlink, and fix **G01**
   so it isn't readable over HTTP. Add the "exclude from cloud sync" note
   (`KEYRING_HARDENING.md:82-83`) to the README and surface the storage location plus a one-line
   "stored unencrypted, protected by file permissions" statement in the settings panel — an informed
   user is the difference between an accepted risk and a surprise.
2. *Next:* add a `keyring`-library backend behind `assert_secure_backend()` exactly as
   `KEYRING_HARDENING.md:29-48` writes it, with the file store demoted to an explicit
   `--file-store` opt-in. Do not ship `keyrings.alt`; add the `pipdeptree` CI check
   (`KEYRING_HARDENING.md:105`). Never honor `PYTHON_KEYRING_BACKEND` from the environment.

---

### G09 — Keyring write: `0644` window, non-atomic, follows symlinks, `0755` parent · **S1** · [verified]

**Evidence:** `atelier/helix/keyring.py:43` and `:50-55`.

```50:55:atelier/helix/keyring.py
    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2) + "\n")
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass
```

Four defects against `CONTRACT.md:212-220` and the research implementation
(`03-keyring-spokes/keyring.py:166-208`):

- **Secret bytes hit the disk before the permissions do.** `write_text` creates at
  `0666 & ~umask` = `0644` on a default umask; the `chmod` is a *subsequent* syscall. Any crash,
  `OSError`, or read in between leaves the key world-readable — and because the `chmod` failure is
  swallowed by `except OSError: pass`, a filesystem that rejects it leaves `0644` permanently with no
  diagnostic. Research: `os.fchmod(fd, 0o600)` on a temp fd *before* writing.
- **Not atomic.** No temp-file + `os.replace`, so a concurrent reader can observe a truncated file
  and a crash mid-write loses every stored key. `ThreadingHTTPServer` (`server.py:228`) makes
  concurrent `put()` calls reachable.
- **Symlinks followed.** No `os.path.islink` refusal (research: `keyring.py:167-170`), so a
  pre-planted symlink at `~/.atelier/keyring.json` redirects the write to a location the attacker
  controls.
- **Parent directory `0755`.** `:43` uses a bare `mkdir(parents=True, exist_ok=True)`; research
  requires `mode=0o700` plus an explicit `chmod` (`keyring.py:190-195`). Also missing: the
  tighten-on-read behavior that repairs a loosened file (`keyring.py:174-179`).

**Verified:** with `os.chmod` stubbed out, the file created by `write_text` was `0o644`. The parent
directory was `0o755`. Writing through a symlink to `/tmp/atelier-probe/attacker/loot.json`
succeeded — the canary key landed in the attacker-controlled file.

**Ship fix.** Port `_save`/`_load` from `research/fable5/03-keyring-spokes/keyring.py:166-208`
essentially verbatim: `islink` refusal, tighten-on-read with a stderr warning, `makedirs(mode=0o700)`
+ explicit `chmod`, `mkstemp` + `fchmod(0o600)` + write + `os.replace`, and `unlink` the temp on any
exception. Remove the `except OSError: pass` — a permissions failure on a secret store must be loud.

**Test to add:** the research suite already covers this shape; port the assertions. After `put()`:
file mode is exactly `0600`, dir mode `0700`, no `.keyring-*` temp files remain; a pre-existing
`0644` file is tightened on read; a symlinked path raises; and a stubbed-`chmod` run must *fail*
rather than silently proceed.

---

### G10 — Masked hint exposes prefix *and* suffix · **S2** · [verified]

**Evidence:** `atelier/helix/keyring.py:99`.

```99:99:atelier/helix/keyring.py
                "hint": (secret[:3] + "…" + secret[-4:]) if len(secret) > 8 else ("set" if secret else ""),
```

`POLICY.md:45-47`: *"show at most the last 4 characters; never show prefix + suffix combinations long
enough to aid brute force; fingerprints are safe to log and display freely."* Live discloses 7
characters of every key to an unauthenticated endpoint (`server.py:116-118`).

**Verified:** `GET /api/keys` returned `"hint": "sk-…AAAA"` for the canary. Low absolute value for the
first three characters (`sk-` is a constant prefix), but the policy exists so nobody has to reason
about that per-provider, and `AIza…` keys have 4 informative prefix characters.

**Ship fix.** Return `{"fingerprint": sha256(key).hexdigest()[:8], "masked": "…" + key[-4:]}` per
`POLICY.md:32-35`, and add `created_at`/`last_verified_at` while touching the shape. The fingerprint
is what makes rotation and support diagnosis possible without ever printing key material.

---

### G11 — Bare `str` secrets: no `Secret` wrapper, no core-dump suppression · **S2** · [by inspection]

**Evidence:** `keyring.py:57-62` returns a plain `str`; `openai_spoke.py:18-28` interpolates it into
an f-string header; nothing in the tree calls `resource.setrlimit`.

`KEYRING_HARDENING.md:85-99` requires a `Secret` wrapper whose `__repr__` yields only the
fingerprint, minimized copies, and `RLIMIT_CORE = (0, 0)` on POSIX;
`THREAT_MODEL.md:70-71` lists core dumps as a concrete T1 failure mode. Today any traceback that
renders locals, any debugger session, or any crash dump can surface the key, and `_headers()`
(`openai_spoke.py:24-28`) returns a dict that would print the bearer token if it ever reached a log.

**Ship fix.** A ~15-line `Secret` class (`__repr__`/`__str__` → `Secret(sk-…a1b2c3d4)`, explicit
`.reveal()` used only at the header-construction site), `Keyring.get_secret` returning it, and
`resource.setrlimit(resource.RLIMIT_CORE, (0, 0))` at the top of `server.main()` guarded for
non-POSIX. Pair with **G23**'s redaction filter so the two controls back each other up.

---

### G12 — Env-var mapping: no `ATELIER_*` names, and `ollama` maps a host to a secret · **S3** · [verified]

**Evidence:** `atelier/helix/keyring.py:10-16`.

```10:16:atelier/helix/keyring.py
ENV_MAP = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "ollama": "OLLAMA_HOST",
    "openai_compat": "OPENAI_COMPAT_API_KEY",
}
```

Three divergences from `CONTRACT.md:182-198` / `03-keyring-spokes/keyring.py:39-50`:

- No `ATELIER_`-scoped names, so a user cannot scope a key to Atelier without changing the variable
  their other tooling reads. Research resolution order is `ATELIER_<P>_API_KEY` → conventional name;
  `gemini` also accepts `GOOGLE_API_KEY`.
- **`ollama` maps to `OLLAMA_HOST` — a hostname consumed as a secret.** `get_secret("ollama")`
  returns the host string, so `public_status()` reports Ollama as "configured" from `env` and puts
  the *hostname* in the `hint` field. `OllamaSpoke` never sends a key, so nothing leaks today, but
  the moment Ollama auth is added, a hostname will be sent as a bearer token. **Verified** in the
  probe environment where `OLLAMA_HOST` was set and Ollama reported `source: env`.
- `get_base_url` (`keyring.py:64-66`) reads only the file, never the environment; research has
  `BASE_URL_ENV_VARS` for `ollama`/`openai_compatible` (`keyring.py:47-50`).

**Ship fix.** Adopt the research tuples verbatim (`ENV_VARS` with first-hit-wins ordering plus
`BASE_URL_ENV_VARS`), move `OLLAMA_HOST` out of the secret map into the base-URL map, and report
`source` as `env:<VAR>` so the settings panel can tell the user *which* variable is winning.

---

## 3. XSS and the browser boundary

The key-broker invariant holds: no key is ever sent to the browser (`server.py:116-118` returns only
`public_status()`), and `app.js` renders messages and node text with `textContent`
(`app.js:85,87,122`) and loads artifacts through `<img src>` (`app.js:84`), which does not execute
SVG script. That is the design working. What is missing is every backstop around it.

### G13 — Attacker-controlled SVG served inline, same-origin, with no CSP · **S0** · [verified]

**Evidence:** `atelier/server.py:77-91` and `:153-156`; `web/index.html` has no CSP meta and
`_json`/`_send_file` set no security headers.

The `/api/artifacts/<id>` route passes `download_name` (`server.py:148`), so it emits
`Content-Disposition: attachment` and will not render inline — a genuine, if accidental, mitigation.
But the static fallback branch at `:153-156` serves the *same files* with no such header, and
**G01**'s traversal reaches the artifacts directory.

**Verified:** an SVG containing `onload=` and a `<script>` block placed in the artifacts directory was
served at `GET /../../../../tmp/atelier-probe/rt/artifacts/xss_probe.svg` as
`HTTP 200, Content-Type: image/svg+xml`, **with no `Content-Disposition`**. Navigating a browser
there executes script in the studio's own origin. Contrast the same file via `/api/artifacts/<id>`,
which did carry `Content-Disposition: attachment`.

The chain is complete and needs no user error beyond opening a link: model-generated or
compat-provider-supplied SVG becomes stored same-origin script (T2/T3), which reads `/api/keys` for
hints and then reads the raw key through **G01**, and exfiltrates — there is no CSP `connect-src` to
stop the outbound `fetch`.

`THREAT_MODEL.md:114-125` specifies the full control set; none of it is present.

**Ship fix.**

1. **G01** (confinement) removes the inline-serving path.
2. Send security headers on every response from `_json` and `_send_file`:
   `Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; connect-src 'self'; frame-ancestors 'none'`,
   `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`.
3. Never serve a stored artifact with an active content type. Force
   `Content-Type: application/octet-stream` + `Content-Disposition: attachment` for everything under
   `/api/artifacts/`, or serve SVG only after sanitization (see **G15**). Remove the special-case
   `if path.suffix == ".svg": mime = "image/svg+xml"` at `:83-84` — that line exists only to make
   SVG render, which is exactly what we don't want.
4. Add `sandbox` to any future preview iframe; keep using `<img>` on the board.

**Test to add:** every response carries the CSP and `nosniff` headers; a `.svg` artifact is served as
`application/octet-stream` with `attachment`; the traversal tests from **G01** cover the inline path.

---

### G14 — `innerHTML` on the key-status widget · **S2** · [by inspection]

**Evidence:** `atelier/web/app.js:127-134`.

```129:133:atelier/web/app.js
  const bits = Object.entries(keys).map(([k, v]) => {
    const mark = v.configured ? "ok" : "warn";
    return `<span class="pill ${mark}">${k}:${v.source}</span>`;
  });
  document.getElementById("keyStatus").innerHTML = bits.join(" ");
```

Not exploitable today: `k` iterates the fixed `ENV_MAP` keys and `v.source` is one of three literals
(`keyring.py:88-101`). But it is the one `innerHTML` sink fed by server data in the app, it sits on
the *key* panel, and it will become live the moment `public_status()` grows a
provider-name-or-URL-derived field. `THREAT_MODEL.md:120-121` wants model and imported content
inserted via `textContent` as a rule, not case-by-case.

**Ship fix.** Build the pills with the existing `el()` helper (`app.js:21-31`), which already routes
text through `textContent`. Two lines. While there, keep the fingerprint from **G10** out of
`innerHTML` too.

---

### G15 — No sanitization of model-generated image bytes · **S2** · [by inspection]

**Evidence:** `conductor.py:158-176` writes `woven.data` straight to disk via `write_bytes`
(`loom.py:31-44`), which maps `image/svg+xml` to a `.svg` file. Only the *demo* path escapes its
input (`loom.py:14` uses `html.escape`); real provider output is trusted verbatim.

`THREAT_MODEL.md:116-119` requires: never inline untrusted SVG, sanitize on import with an
element/attribute allowlist, and rasterize uploads. There is also no upload/import path yet — which
is the good news: **fix this before adding one**, because `THREAT_MODEL.md:174-209` (T4: XXE,
zip-slip, decompression bombs) applies the moment users can import a template pack, and none of that
scaffolding exists.

**Ship fix.** Refuse to persist `image/svg+xml` from any non-demo provider (today no configured spoke
returns SVG, so this costs nothing and closes the class). If SVG output is wanted later, parse with
`defusedxml` and an element/attribute allowlist that drops `script`, `foreignObject`, `on*`, and
external `href`/`xlink:href`, then store the sanitized form and rasterize for display.

---

## 4. Budget, quota, and cost accounting

### G16 — The budget is checked *after* the money is spent, and refusals erase the ledger row · **S0** · [verified]

**Evidence:** `atelier/helix/usage.py:98-109` and its call sites in `conductor.py:107-124,178-185`.

```98:109:atelier/helix/usage.py
def record(memory, *, provider: str, model: str, unit_kind: str, units: float, thread_id=None) -> dict:
    cost = estimate_usd(provider, model, unit_kind, units)
    if provider != "demo":
        assert_budget(memory, thread_id=thread_id, extra_usd=cost)
    return memory.add_usage(...)
```

Two compounding defects:

- **Ordering.** The only budget check lives inside `record()`, and `record()` is only ever called
  *after* the provider call has returned — `conductor.py:108` calls `spoke.chat(...)` then
  `usage.record(...)` at `:109`; `conductor.py:161` calls `image_spoke.image(...)` then
  `usage.record(...)` at `:178`. The provider has already billed. `POLICY.md:66-68` and
  `08-security-quota/usage.py:437-459` both specify a **pre-call** `BudgetGuard.check()` with a
  strict estimate; `THREAT_MODEL.md:167-169` names it as the backstop that bounds
  prompt-injection spend loops (T3). Live has no pre-flight at all, so the "hard stop" doesn't exist.
- **The refusal loses the row.** When `assert_budget` raises, `memory.add_usage(...)` never executes.
  The spend that *did* happen is not recorded, so the next call re-evaluates against the same stale
  total and is refused identically — forever, while every attempt bills the user.

**Verified.** With caps set to `$0.01`/`$0.005` and six `gpt-image-1` images recorded in sequence:
all six raised `BudgetExceeded`, and after all six the ledger read **`$0.0000` with 0 rows**. In the
conductor that is six real images generated and billed, zero recorded, and a UI
(`app.js:149-152`) reporting `estimated spend $0.0000`. The guard never converges because the thing
it measures is the thing it refuses to write.

Note `atelier/tests/test_helix.py:102-103` currently *asserts this behavior* (`assertRaises(BudgetExceeded)`
around `record`), so the test must be rewritten alongside the fix — the existing test locks in the bug.

**Ship fix.** Split the one function into the research's two, and put them on either side of the call:

```python
# before the provider call — strict estimate, refuse if unpriceable (see G17)
usage.preflight(memory, provider=p, model=m, units={"tokens_in": est_in, "tokens_out": est_out},
                thread_id=tid)
result = spoke.chat(...)
# after — always record, even on failure; never gated by the budget
usage.commit(memory, provider=p, model=result.model, units=actual, thread_id=tid)
```

`commit()` must never raise `BudgetExceeded` — it is bookkeeping, not enforcement. Enforcement lives
only in `preflight()`. For chat, estimate input tokens as `len(prompt) // 4` (already the demo
spoke's own heuristic, `base.py:68`) and use the model's configured `max_tokens` for the output side,
so the pre-flight is conservative in the right direction. Return the projected cost and the remaining
headroom to the caller so `server.py` can pass them to the UI (**G19**).

**Test to add:** a run that trips the cap makes **zero** provider calls (assert with a spoke double
that counts invocations); a call that succeeds after a cap trip is impossible until the window
resets; and `commit()` after a `BudgetExceeded` still writes the row so the ledger total is monotonic.

---

### G17 — Unpriceable models are silently guessed, so budget caps are bypassable by model name · **S1** · [verified]

**Evidence:** `atelier/helix/usage.py:55-66`.

```62:66:atelier/helix/usage.py
    if unit_kind == "images":
        return round(0.04 * units, 6)
    if unit_kind in {"tokens_in", "tokens_out", "tokens"}:
        return round((0.5 / 1_000_000) * units, 6)
    return 0.0
```

`POLICY.md:66-68` is explicit: *"unpriceable calls (unknown model/unit) are refused rather than
allowed to bypass the budget. The `unpriced_count()` metric must remain zero."* The research
`estimate_cost` has a `strict=True` mode that raises `UnknownPriceError`
(`08-security-quota/usage.py:153-182`) and a ledger that records `estimated_cost_usd = NULL` plus an
`unpriced_count()` query (`:397-406`) so the gap is *visible* rather than papered over. The
`03-keyring-spokes` ledger states the same rule: *"the ledger never invents a price"*
(`CONTRACT.md:246-247`).

**Verified:** `estimate_usd("openai", "gpt-6-ultra-secret", "tokens_out", 1_000_000)` → `$0.50`, and
`estimate_usd("openai", "gpt-image-9-4k", "images", 1)` → `$0.04`. For comparison the research
`COST_TABLE` prices a 4K pro image at `$0.24` and `gpt-5.6-sol` output at `$30/M` — 6× and 60×
the guess. A caller who picks an unlisted model gets a budget ceiling inflated by that factor, and
`server.py:196-214` takes `model` straight from the request body with no allowlist, so via **G03**
this is attacker-selectable.

**Ship fix.** Add `strict: bool = False` to `estimate_usd`, raising `UnknownPriceError` on an unknown
`(provider, model, unit_kind)`. Call it with `strict=True` from `preflight()` (**G16**) and surface
the failure as an actionable message ("no price on file for `<model>`; add it to `COST_TABLE` or pick
a listed model"). In `commit()`, store `NULL` rather than a guess, and add
`Memory.unpriced_count()` exposed via `/api/usage` so a nonzero value is visible. Drop the `return 0.0`
fallthrough entirely.

---

### G18 — No refund or reconciliation for failed generations · **S1** · [by inspection]

**Evidence:** `atelier/helix/conductor.py:160-164` and `:201-222`.

```160:164:atelier/helix/conductor.py
                    image_spoke = build_spoke(plan["route"].get("provider") or provider, self.keyring)
                    woven = image_spoke.image(item_prompt, model=image_model)
                except SpokeError:
                    image_spoke = build_spoke("demo", self.keyring)
                    woven = image_spoke.image(item_prompt, model="demo-svg")
```

The `SpokeError` path silently substitutes the demo spoke and then records usage for **`woven.provider`**
— i.e. `demo`, at `$0` (`:178-185`). A provider call that failed *after* being billed (a 500 after
generation, a timeout on a completed image, a content filter that still charged for input tokens)
records nothing at all. `POLICY.md:63-65` is unambiguous: *"Every provider call is recorded in the
usage ledger… no exceptions, including failed calls where the provider billed us (record what was
sent)."*

The same shape appears in the planner path (`conductor.py:127-130`): `except (SpokeError, ValueError,
JSONDecodeError): pass` — if `spoke.chat` raised *after* the provider billed the input tokens, or if
the call succeeded but `extract_json` failed at `:125`, no usage row is written for tokens the user
paid for. The second case is the more common one: a successful, billed chat whose output didn't parse
is charged to the user and recorded nowhere.

There is also no *refund* direction. Once **G16** introduces a pre-flight reservation, a failed call
must release the reservation, or a flaky provider will exhaust the day's budget without spending a
cent.

**Ship fix.** Reserve/settle, and record failures:

- `preflight()` returns a reservation id; `commit(reservation_id, actual_units)` settles it with real
  numbers; `release(reservation_id)` cancels on a pre-billing failure (connection refused, DNS,
  our own `KeyLeakError`).
- On any error *after* bytes reached the provider (any HTTP status received, including 4xx/5xx),
  call `commit()` with the units we sent and a `status` field in metadata — that is "record what was
  sent."
- Track the reservation in the ledger as a row with a `pending` state rather than in memory, so a
  crash mid-call doesn't lose it.
- Stop attributing the demo fallback's usage to the failed provider's attempt: record both events,
  distinctly.

**Test to add:** a spoke double that raises after a simulated 500 produces a ledger row for the
attempted provider; a spoke double that raises `ConnectionRefused` produces no row *and* releases the
reservation; a chat whose JSON fails to parse still records the tokens.

---

### G19 — No cost-before-commit: no estimate, no headroom, no price-staleness notice · **S2** · [verified]

**Evidence:** `atelier/server.py:125-126` exposes only historical totals; `atelier/web/app.js:149-152`
renders them after the fact.

```149:152:atelier/web/app.js
  const usage = await api("/api/usage");
  const usd = (usage.totals || []).reduce((s, t) => s + (t.estimated_usd || 0), 0);
  document.getElementById("topMeta").textContent =
    `Helix · estimated spend $${usd.toFixed(4)} · keys stay on this machine`;
```

There is no pre-run estimate, no confirmation step, and no headroom display. The research provides
`BudgetGuard.headroom()` returning remaining USD per scope (`08-security-quota/usage.py:461-468`),
and `POLICY.md:70-72` requires the UI to always show today's spend, per-thread spend, **and the
price-table date**, with a staleness notice when `PRICES_AS_OF` is older than 30 days.
`PRICES_AS_OF = "2026-08-21"` exists at `usage.py:14` and is never read by any other module —
**verified** by grepping the live tree: it appears exactly once.

`THREAT_MODEL.md:161-164` additionally requires an explicit user click for "spending above threshold"
as a T3 mitigation, which does not exist: `app.js:191-211` fires the run immediately.

**Ship fix.**

- `GET /api/budget?thread_id=…` → `{daily_limit, daily_spent, daily_headroom, thread_limit,
  thread_spent, thread_headroom, prices_as_of, prices_stale: bool}`.
- `POST /api/estimate` → projected USD for the pending `{provider, model, mode, prompt}` using the
  strict estimator, plus whether it fits the headroom.
- In the dock: show `headroom` next to the Weave button; render the estimate inline as the provider
  and model selects change; require an explicit confirm when the estimate exceeds a configurable
  threshold (default $0.25) or when the model is unpriced.
- Show `prices as of 2026-08-21` beside every cost figure, with a visible staleness warning past 30
  days — cheap to add and it is the difference between "estimate" and "implied promise".

---

### G20 — Rolling 24h window, import-time caps, no per-provider cap · **S2** · [verified]

**Evidence:** `atelier/helix/usage.py:15-16` and `:87-95`.

```87:89:atelier/helix/usage.py
def assert_budget(memory, *, thread_id=None, extra_usd: float = 0.0) -> None:
    day_start = time.time() - 86400
```

Three divergences from `08-security-quota/usage.py:425-459`:

- **Rolling 24h vs. calendar day.** Research uses `_utc_midnight_epoch()`. A rolling window means a
  single burst suppresses spend for a full 24 hours from the burst, which is surprising ("my daily
  budget reset at 3pm?") and cannot be reasoned about against a provider invoice, which is
  calendar-dated. **Verified** by reading the computed `day_start`.
- **Caps fixed at import.** `DAILY_BUDGET_USD`/`THREAD_BUDGET_USD` are read from the environment when
  the module first loads (`:15-16`), so they cannot be changed from the settings panel and a
  long-running server can never have its budget adjusted. Research passes them as `BudgetGuard`
  fields.
- **No per-provider cap** and no way to disable a cap (research allows `None` for "unlimited"; live
  requires a float, so "no limit" is spelled `999999`).

**Ship fix.** Move the caps into a `BudgetGuard`-style object constructed in `App.__init__` from
persisted settings, defaulting from the environment; switch the daily window to UTC midnight; add an
optional per-provider cap; allow `None` to disable. Expose read/write via the `/api/budget` endpoint
from **G19** so the user can raise their own ceiling deliberately rather than by editing an env var
and restarting.

---

### G21 — `BudgetExceeded` mid-weave leaves an orphaned artifact and a 500 · **S2** · [by inspection]

**Evidence:** `atelier/helix/conductor.py:165-197`. The ordering is `add_artifact` → `write_bytes` →
`UPDATE artifacts SET path` → `usage.record` → `add_node`. A `BudgetExceeded` from `:178` (which is
*not* a `SpokeError`, so no handler in `conductor.run` catches it) propagates to `server.py:210-211`
and becomes a bare 500. Left behind: an artifact row and a file on disk, no board node, no usage row,
and — per **G16** — no record of the spend that already happened. The user sees only
`err.message` in the status line (`app.js:208-210`).

**Ship fix.** Once **G16**'s pre-flight lands, this is mostly moot: the budget decision happens
before any bytes are written. Still worth doing: catch `BudgetExceeded` in `conductor.run`,
stop the weave loop cleanly, return the partial result with a
`{"stopped": "budget", "detail": …}` field, and have `server.py` map it to **402 Payment Required**
with a structured body instead of a stringified 500. Add a startup reconciliation that deletes
artifact rows with no node and no file (or vice versa).

---

### G22 — One provider call becomes two ledger rows, and two budget checks · **S3** · [by inspection]

**Evidence:** `atelier/helix/conductor.py:109-124` calls `usage.record` twice per chat — once for
`tokens_in`, once for `tokens_out` — because the live schema stores a single `(unit_kind, units)` pair
per row (`store.py:61-70`). The research schema stores a `units` **JSON map** per call
(`08-security-quota/usage.py:216-230`), so one provider call is one row.

Consequences: `assert_budget` runs twice per call; `/api/usage` event counts are inflated 2×; there is
no `request_id` column to correlate a row with a provider invoice line (research has one, `:224`);
and there is no `metadata` column, which is where the research puts its
`scrub_secrets()` defense in depth (`:226`, `POLICY.md:56-59`).

**Ship fix.** Migrate `usage_events` to `units TEXT` (JSON map) + `request_id` + `metadata`, with
`estimated_usd` nullable for **G17**. One row per call. Route `metadata` through a `scrub_secrets()`
port (**G23**). This is the one schema change in this report, so batch it with **G16**'s pre-flight
work rather than shipping it alone.

---

## 5. Logging and redaction

### G23 — No redaction anywhere; raw exception text is returned to the browser · **S1** · [verified]

**Evidence:** `atelier/server.py:210-211` and `atelier/helix/spokes/openai_spoke.py:47`.

```210:212:atelier/server.py
            except Exception as exc:
                _json(self, 500, {"error": str(exc)})
                return
```

```47:47:atelier/helix/spokes/openai_spoke.py
            raise SpokeError(f"OpenAI HTTP {exc.code}: {exc.read().decode()[:400]}") from exc
```

`POLICY.md:40-44` requires the opposite of both: *"Error responses are built from our own error
types, never by string-formatting a provider exception into the body"*, plus a global response
middleware that applies redaction patterns to every outgoing body as a backstop with a
`redaction_backstop_hits` counter. `POLICY.md:9-26` requires a logger-level redaction filter using
the `scrub_secrets()` patterns.

**Verified:** `rg "scrub|redact|REDACT|mask\("` across the live tree returns zero matches in
`helix/`, `web/`, or `server.py` — the only hits are a doc line in `ARCHITECTURE.md` and a test name.
The research pattern set is sitting ready at `08-security-quota/usage.py:191-209`.

Two live consequences. First, provider error bodies are reflected verbatim into a browser-visible
JSON response — and for `openai_compat` (**G04**) that body is attacker-controlled, giving a
reflection channel into the studio UI. Second, several exception types in this stack carry the
request URL (`urllib`'s `ValueError("unknown url type: %r")` interpolates `full_url`), and per
**G06** the Gemini URL contains the API key — so a malformed-URL path plus this handler is a key
disclosure to the browser. Neither leg is exploitable on its own; the combination is why `POLICY.md`
asks for both a primary control and a backstop.

**Ship fix.**

1. Port `_SECRET_PATTERNS` + `scrub_secrets()` from `08-security-quota/usage.py:191-209` into a new
   `helix/redact.py`.
2. Apply it inside `_json()` to every outgoing body, and increment a
   `redaction_backstop_hits` counter exposed on `/api/health` — nonzero means a primary control
   failed and is a bug to chase, per `POLICY.md:43-44`.
3. Replace `{"error": str(exc)}` with a typed error map: known error classes → a safe message and a
   stable code; everything else → `{"error": "internal error", "code": "<uuid>"}` with the detail
   logged server-side only.
4. Truncate and structure the provider-error passthrough: keep `status` and the provider's `code`,
   drop the free-text body (or scrub it) instead of forwarding 400 raw bytes.

---

### G24 — Request-line logging with no scrubbing · **S2** · [by inspection]

**Evidence:** `atelier/server.py:95-96`.

```95:96:atelier/server.py
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("atelier %s - %s\n" % (self.address_string(), fmt % args))
```

This logs the full request line including the query string, unscrubbed, to stderr — which in a
packaged app lands in a log file, and in a terminal lands in scrollback that
`POLICY.md:23-26` explicitly wants covered by the canary grep. No `/api/*` route currently accepts a
secret in the query string, so there is no leak today; the gap is that nothing *prevents* one. Note
that `POST /api/keys` bodies are **not** logged, which satisfies `POLICY.md:37-39` — that part is
correct today and should be locked in by a test so it stays that way.

**Ship fix.** Route this through the **G23** scrubber, and log only method + path (query string
dropped) + status + duration. Add an explicit `# never log request bodies or headers` comment at the
handler boundary, since that is a constraint the code cannot express.

---

### G25 — No canary-key CI tripwire, no secret scanning · **S3** · [by inspection]

**Evidence:** `atelier/tests/test_helix.py` is the whole suite (117 lines); `KeyringTests` asserts
only that `public_status()` does not echo the key (`:44-53`), which is the weakest of the guarantees
`POLICY.md` asks for.

Missing from `POLICY.md:23-26,88-91` and `KEYRING_HARDENING.md:101-111`: an E2E run with a canary key
followed by a grep of every produced artifact (logs, ledger DB dump, HTTP response bodies,
board exports) for the canary and for `sk-[A-Za-z0-9_-]{20,}` / `AIza[0-9A-Za-z_-]{35}`; and
pre-commit/CI secret scanning on the repo itself.

**Ship fix.** Add a `tests/test_no_secret_leak.py` that runs a demo-provider end-to-end flow with
`OPENAI_API_KEY=sk-canary…`, then asserts the canary appears in **no** HTTP response body, no
sqlite dump, no artifact file, and no captured stderr. Wire `gitleaks` into pre-commit. These two are
what keep the other 24 fixes from silently regressing.

---

## What the live code already gets right

Worth stating explicitly so a reviewer doesn't "fix" it:

- **The key-broker invariant holds.** No endpoint returns a raw key; the browser never receives key
  material (`server.py:116-118`, `keyring.py:88-101`). This is the single most important design
  decision in `THREAT_MODEL.md:48-51` and it is intact.
- **Environment beats file** (`keyring.py:57-62`), matching `CONTRACT.md:182-194` — CI and one-off
  shells never need a key on disk.
- **`chmod 0600` is attempted** on the keyring, and the parent directory is created rather than
  assumed. The intent is right; **G09** is about the mechanism.
- **The `openai` provider id genuinely refuses a `base_url` override** (`openai_spoke.py:32-33`),
  which is `CONTRACT.md:49-52`'s hard rule and defeats the most obvious CSRF-to-exfiltration chain.
- **Loopback binding by default** (`server.py:226`).
- **The demo spoke is a real zero-quota path** and is excluded from budget checks
  (`usage.py:100`), so the app is usable and testable without a key — this is why the whole probe
  suite above could run without touching a provider.
- **`/api/artifacts/` sets `Content-Disposition: attachment`** (`server.py:88-89`), which blocks
  inline SVG execution on that route. **G13** is about the *other* route reaching the same bytes.
- **Board and message rendering uses `textContent`** (`app.js:85-87,122`) and artifacts load through
  `<img>` (`app.js:84`) — the two places `THREAT_MODEL.md:118-121` cares most about.
- **`POST /api/keys` bodies are not logged** (`server.py:95-96` logs only the request line),
  satisfying `POLICY.md:37-39`.
- **No CLI flag accepts a key**, so keys stay out of `ps` and shell history
  (`POLICY.md:82-83`) — though this is by omission rather than by design, since there is no CLI at
  all yet; when one lands, use the research's `getpass`/stdin approach
  (`03-keyring-spokes/keyring.py:215-231`).

## Research-internal conflict to resolve before implementing

`03-keyring-spokes/CONTRACT.md §4` (plaintext `0600` JSON at `~/.atelier/keyring.json`, env override,
CLI) and `08-security-quota/KEYRING_HARDENING.md` (OS keychain, fail closed, *never* plaintext;
encrypted file only as an explicit opt-in) specify different stores. The live code implements the
former. Somebody needs to decide, because the tests differ: the `03` suite asserts file modes and
symlink refusal; the `08` checklist asserts `assert_secure_backend()` raises on a plaintext backend.

My recommendation, stated once more because it drives the ship order: implement `03` **correctly**
(**G09**) as v1, since the live code is already 80% of the way there and the remaining 20% is
mechanical; treat `08`'s keychain as the follow-on, and in the meantime tell the user in the UI
exactly where the file is and that it is unencrypted. A plaintext file the user knows about, at
`0600`, in a directory not reachable from the HTTP server, is a defensible answer to attacker A4. A
plaintext file at `0644` that any local process can read and any browser tab can `GET` is not — and
that, not the choice of store, is what makes the current state unshippable.

## Suggested ship order

Each line is one reviewable PR. Order matters: 1–3 remove the read primitives that make everything
else exploitable, and 4 stops the bleeding of actual money.

1. **G01** path confinement + **G13** security headers and inert artifact serving. (~40 lines,
   `server.py`. Highest ratio of risk removed to code changed in the whole list.)
2. **G03** session token + `Host`/`Origin` validation + `Content-Type` enforcement.
   (~60 lines across `server.py` and `app.js`.)
3. **G02** `_NoRedirect` opener + **G04**/**G05** unified `assert_key_safe` + **G06** Gemini header.
   (~50 lines in `spokes/`, one new helper, three call sites.)
4. **G16** pre-flight/commit split + **G17** strict pricing + **G22** schema migration.
   (The largest change; touches `usage.py`, `store.py`, `conductor.py`, and rewrites
   `tests/test_helix.py:94-105`, which currently asserts the bug.)
5. **G09** atomic/symlink-safe keyring write + **G10** fingerprint masking + **G12** env map.
   (Mostly a port from `03-keyring-spokes/keyring.py`.)
6. **G23**/**G24** redaction module, typed errors, response backstop counter + **G25** canary test.
7. **G07** `safe_fetch()` + **G15** SVG refusal. (Do before adding any import-from-URL or upload
   feature, which is when T4 becomes fully live.)
8. **G18** reserve/settle/release + **G19** cost-before-commit UX + **G20** budget settings +
   **G21** clean budget stop.
9. **G08** OS-keychain backend behind `assert_secure_backend()`; **G11** `Secret` wrapper and
   `RLIMIT_CORE`; **G14** `innerHTML` removal.

---

## Appendix A — Reproduction

All probes ran against a copy: `ATELIER_HOME=/tmp/atelier-probe/h2`,
`ATELIER_RUNTIME=/tmp/atelier-probe/rt`, `ATELIER_PORT=8791`, canary key
`sk-canary000000000000000000000000AAAA`. `/workspace` was not modified.

```bash
# setup
mkdir -p /tmp/atelier-probe/h2
cd /workspace
env -u OPENAI_API_KEY -u GEMINI_API_KEY ATELIER_HOME=/tmp/atelier-probe/h2 \
    ATELIER_RUNTIME=/tmp/atelier-probe/rt ATELIER_PORT=8791 python3 -m atelier.server &

# G01 — raw key over HTTP (returns the keyring JSON, key included)
curl -s --path-as-is \
  "http://127.0.0.1:8791/../../../../tmp/atelier-probe/h2/keyring.json"

# G03 — no Host validation (DNS rebinding), unauthenticated key status
curl -s -H "Host: evil.example" -H "Origin: https://evil.example" \
  http://127.0.0.1:8791/api/keys

# G03 — CSRF: cross-origin text/plain POST is a CORS simple request, runs a paid weave
curl -s -X POST -H "Content-Type: text/plain" -H "Origin: https://evil.example" \
  -d '{"prompt":"csrf spend probe","provider":"demo","mode":"fast"}' \
  "http://127.0.0.1:8791/api/threads/<THREAD_ID>/run"

# G13 — attacker SVG served inline, same-origin, no Content-Disposition, no CSP
printf '%s' '<svg xmlns="http://www.w3.org/2000/svg"><script>fetch("/api/keys")</script></svg>' \
  > /tmp/atelier-probe/rt/artifacts/xss_probe.svg
curl -si --path-as-is \
  "http://127.0.0.1:8791/../../../../tmp/atelier-probe/rt/artifacts/xss_probe.svg"
```

`G02` (redirect replays `Authorization` on 302), `G07` (`_download` reads `file://`),
`G04`/`G05` (host-pin matrix), `G09` (`0644` window, symlink write-through, `0755` parent),
`G10` (`sk-…AAAA` hint) and `G16`/`G17` (6/6 billed calls refused with a `$0.0000` ledger) were
reproduced with four standalone scripts in `/tmp/atelier-probe/`:
`redirect_probe2.py`, `probe3.py`, `probe4.py`, and inline `python3 -c` runs against
`atelier.helix.keyring`. Each prints the observed value next to the expected one.
