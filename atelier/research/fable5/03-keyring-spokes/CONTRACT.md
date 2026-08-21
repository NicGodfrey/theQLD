# Atelier BYOK Gateway — Spoke Contract

Atelier never resells inference. Every request is paid for by the **user's
own official API quota** ("bring your own key"). This document is the
binding contract between the Atelier hub and its provider adapters
("spokes"), plus the security invariants any implementation must uphold.

Everything described here is implemented, stdlib-only (`urllib`, `json`,
`os`), Python 3.9+, in the sibling files:

| File | Role |
|---|---|
| `spokes_base.py` | Contract types, error taxonomy, urllib transport, **key-leak guard**, SSE helper |
| `spokes_openai.py` | OpenAI spoke (chat, stream, image). Also powers **Ollama** and **generic OpenAI-compatible** endpoints via factories |
| `spokes_gemini.py` | Google Gemini spoke (chat, stream, image via native output or Imagen `:predict`) |
| `spokes_anthropic.py` | Optional Anthropic spoke (chat, stream) |
| `keyring.py` | Key storage: `~/.atelier/keyring.json`, 0600, env-var override, CLI |
| `ledger.py` | Per-provider usage ledger: tokens, images, estimated USD |
| `gateway.py` | Hub: routes `provider_id` → spoke, shares one Keyring + one Ledger |
| `run_tests.py`, `tests/` | Offline test suite (no sockets, no real keys) — see `TESTS.md` |
| `live_smoke.py` | Optional, explicit, tiny-cost live check (refuses to run without `ATELIER_LIVE=1`) |

The modules are flat files designed to be dropped into one directory (an
`atelier/` package or a script folder) together.

---

## 1. Hard rules (non-negotiable)

1. **Official APIs only.** The OpenAI spoke speaks exclusively to
   `api.openai.com` with an `Authorization: Bearer <API key>` header. There
   is no ChatGPT web-session reuse, no cookie jar, no reverse proxy that
   impersonates `chatgpt.com` — the string `chatgpt.com` does not appear in
   any code path, and the key guard (rule 2) would refuse it anyway.
   Likewise Gemini speaks only to `generativelanguage.googleapis.com`
   (documented `x-goog-api-key` auth) and Anthropic only to
   `api.anthropic.com`.
2. **Keys never leave the local process except toward the provider's
   official host.** Enforced centrally by `assert_key_safe()` in
   `spokes_base.py`, called before *every* credentialed request:
   - the target host must be in the spoke's pinned `allowed_hosts`;
   - the scheme must be `https`, unless the host is loopback
     (`localhost`, `127.0.0.1`, `::1`) — the loopback exemption exists for
     Ollama and local compat servers;
   - the transport **never follows redirects** (`_NoRedirect`), because
     urllib would otherwise replay the `Authorization` header at an
     attacker-chosen `Location`;
   - the `openai` provider id refuses any `base_url` override at
     construction time (`KeyLeakError`). Users who want a different
     endpoint must consciously opt into the separate
     `ollama` / `openai_compatible` provider ids, whose keys are only ever
     sent to the host *they* configured.
3. **Every call lands in the per-provider usage ledger** (tokens, images,
   estimated USD). Spokes call `Spoke._record()` after each successful
   request; disable only by constructing with `record_usage=False`.

---

## 2. The Spoke interface

```python
class Spoke:
    provider_id: str                      # "openai" | "gemini" | "anthropic"
                                          # | "ollama" | "openai_compatible"

    def capabilities(self) -> frozenset:
        """Subset of {"chat", "chat_stream", "image", "video"}."""

    def chat(self, messages: Sequence[ChatMessage], *,
             model: str | None = None,
             temperature: float | None = None,
             max_tokens: int | None = None,
             stream_cb: Callable[[str], None] | None = None,
             **extra) -> ChatResult: ...

    def generate_image(self, prompt: str, *,
                       model: str | None = None,
                       size: str = "1024x1024",       # "WIDTHxHEIGHT"
                       n: int = 1,
                       quality: str | None = None,     # provider-specific
                       **extra) -> ImageResult: ...

    def generate_video(self, prompt: str, *,
                       model: str | None = None,
                       seconds: int = 4,
                       size: str | None = None,
                       **extra) -> VideoResult: ...    # stub — see §6
```

Semantics:

- **`model=None`** uses the spoke's configurable default
  (`default_chat_model` / `default_image_model` constructor args).
- **Streaming**: pass `stream_cb`; it is invoked once per text delta, in
  order, on the caller's thread. The method still returns the complete
  `ChatResult` (full text + usage) when the stream ends. Same method, same
  return type — the hub never branches on streaming.
- **`**extra`** is forwarded into the provider payload verbatim (after the
  normalized fields), so power users can reach provider-specific switches
  (`response_format`, `generationConfig`, `aspect_ratio`, ...) without
  contract churn. Spokes must never *require* extras.
- A spoke raises `NotSupported` for any capability it does not advertise.
- Constructors resolve credentials at build time and raise `AuthError`
  immediately when a required key is missing (fail fast, with the exact
  env var / CLI command to fix it).

### Data types (all in `spokes_base.py`)

```python
Part(kind="text"|"image", text="", data=b"", mime="image/png")
ChatMessage(role="system"|"user"|"assistant", content=str | [Part, ...])

Usage(input_tokens=0, output_tokens=0, images=0, est_usd=None)
    # est_usd is filled by the ledger when priced; None means "unknown",
    # never a silent 0.

ChatResult(text, model, provider, usage, finish_reason="", raw=None)
ImageResult(images=[bytes, ...], mime, model, provider, usage, text="", raw=None)
VideoResult(video=bytes, mime, model, provider, usage, raw=None)
```

`raw` always carries the provider's decoded response for debugging; the
hub must not depend on its shape.

### Error taxonomy

```
SpokeError                  base; fields: provider, status, code, retryable
├── AuthError               401/403, or missing key at construction
├── RateLimitError          429 (retryable=True)
├── ProviderError           other 4xx/5xx, network errors, malformed bodies
├── NotSupported            capability absent (e.g. video today)
└── KeyLeakError            WE refused to send a credential somewhere unsafe
                            (config bug on our side; raised before any I/O)
```

Retry policy (in `http_call()`): up to 2 retries on 429/500/502/503/504,
honoring `Retry-After` when present, else exponential backoff capped at 8s.
Only after exhaustion is the mapped error raised.

---

## 3. Provider matrix

| provider_id | Host (pinned) | Auth header | chat | stream | image | video |
|---|---|---|---|---|---|---|
| `openai` | `api.openai.com` | `Authorization: Bearer` | `/v1/chat/completions` | SSE + `stream_options.include_usage` | `/v1/images/generations` (`gpt-image-1`, `dall-e-3`) | stub |
| `gemini` | `generativelanguage.googleapis.com` | `x-goog-api-key` | `:generateContent` | `:streamGenerateContent?alt=sse` | native image output (`gemini-2.5-flash-image`) or `imagen-*` via `:predict` | stub |
| `anthropic` (optional) | `api.anthropic.com` | `x-api-key` + `anthropic-version` | `/v1/messages` | SSE event stream | — | stub |
| `ollama` | user's host, default `127.0.0.1:11434` | none (optional bearer) | `/v1/chat/completions` | SSE | — | stub |
| `openai_compatible` | **user-configured** `base_url` | optional bearer | `/v1/chat/completions` | SSE | opt-in via `capabilities=` | stub |

Wire-mapping notes the hub should not need to know but reviewers might:

- **OpenAI**: `max_tokens` is sent as `max_completion_tokens` to the
  official host (current parameter, required by o-series/gpt-5) and as
  legacy `max_tokens` to compat/Ollama endpoints. Image parts become
  `data:` URLs. `dall-e-*` gets `response_format="b64_json"` injected
  (gpt-image-1 always returns b64 and rejects that parameter).
- **Gemini**: `system` messages merge into one `systemInstruction`;
  `assistant` → role `model`; image parts become `inlineData`. Usage comes
  from `usageMetadata` (`thoughtsTokenCount` counted as output). Native
  image generation returns one image per call, so `n>1` loops; `size` is
  best-effort mapped to `aspectRatio` (`1024x1024` → `1:1`, etc.).
  Blocked prompts (empty `candidates`) raise `ProviderError` with the
  `blockReason`.
- **Anthropic**: Messages API requires `max_tokens`; the spoke defaults it
  to 1024 when the caller omits it. Streaming reads
  `message_start` / `content_block_delta` / `message_delta` events.
- **Ollama / compat are the same class** as the OpenAI spoke
  (`ollama_spoke()`, `compatible_spoke()` factories) because they speak the
  same protocol. They differ only in: pinned host (the user's configured
  one), optional key, legacy `max_tokens`, and default capabilities
  (chat+stream only; a compat server known to implement
  `/images/generations` can opt in via `capabilities=("chat",
  "chat_stream", "image")`).

---

## 4. Key management (`keyring.py`)

Resolution order for a provider's key — first hit wins:

1. **Explicit constructor argument** (`OpenAISpoke(api_key=...)`) — used by
   tests and embedders; skips all disk/env access.
2. **Environment variables**, Atelier-scoped name first:
   | provider | variables (in order) |
   |---|---|
   | openai | `ATELIER_OPENAI_API_KEY`, `OPENAI_API_KEY` |
   | gemini | `ATELIER_GEMINI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY` |
   | anthropic | `ATELIER_ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY` |
   | ollama | `ATELIER_OLLAMA_API_KEY` (rarely needed) |
   | openai_compatible | `ATELIER_COMPAT_API_KEY` |
3. **`~/.atelier/keyring.json`** (path overridable via `$ATELIER_KEYRING`).

`base_url` for `ollama` / `openai_compatible` resolves the same way
(explicit > `ATELIER_OLLAMA_BASE_URL` / `ATELIER_COMPAT_BASE_URL` > file >
built-in localhost default for Ollama).

File format:

```json
{
  "version": 1,
  "providers": {
    "openai": {"api_key": "sk-...", "updated_at": 1755700000},
    "ollama": {"base_url": "http://127.0.0.1:11434/v1", "updated_at": 1755700000}
  }
}
```

Storage guarantees (all under test):

- file mode **0600**, directory mode **0700**;
- writes are atomic: temp file `fchmod`'d to 0600 *before* any secret byte
  is written, then `os.replace`;
- a keyring file found with group/other bits is tightened to 0600 on read
  (stderr warning); a **symlinked** keyring file is refused outright;
- keys never appear in argv (CLI uses `getpass`/stdin), in `repr()`
  (masked as `sk-a…wxyz`), or in logs.

CLI: `python keyring.py {set,get,list,delete,path}` — e.g.
`python keyring.py set openai` (hidden prompt),
`python keyring.py set ollama --no-key --base-url http://127.0.0.1:11434/v1`,
`python keyring.py list` (masked).

---

## 5. Usage ledger (`ledger.py`)

Append-only JSONL at `~/.atelier/ledger.jsonl` (0600). One row per call:

```json
{"ts": 1755700000.123, "provider": "openai", "model": "gpt-4o-mini-2024-07-18",
 "kind": "chat", "input_tokens": 42, "output_tokens": 12, "images": 0,
 "est_usd": 1.35e-05, "priced": true, "meta": {"stream": false}}
```

- `kind` ∈ `chat | image | video`.
- `est_usd` comes from a built-in price table (per-1M-token chat rates,
  per-image rates keyed `"WIDTHxHEIGHT|quality"` with `"*"` fallback;
  longest `provider:model` prefix wins). **Prices are estimates**,
  snapshotted `2026-08`; users override any entry via
  `~/.atelier/prices.json` or `Ledger(price_overrides=...)`.
- Unknown models are recorded with `priced: false` and `est_usd: 0.0` —
  the ledger never invents a price, and `summary()` reports
  `unpriced_calls` so the gap is visible. Ollama is priced $0 explicitly.
- `Ledger.summary(since=None)` aggregates per provider:
  `{calls, input_tokens, output_tokens, images, est_usd, unpriced_calls}`.
- CLI: `python ledger.py summary [--since-hours 24]`.
- Appends use `O_APPEND` single-`write` calls (line-atomic on POSIX) plus a
  process-local lock, so concurrent spokes don't interleave rows.

Spokes copy the resulting estimate back onto `result.usage.est_usd`
(`None` when unpriced), so the hub can show cost inline without touching
the ledger.

---

## 6. Video (contract stub)

`generate_video()` is **reserved but not implemented**: every current
spoke raises `NotSupported` with a message pointing here. The signature,
`VideoResult`, and the ledger `kind="video"` slot are frozen now so the
hub, board UI, and ledger schema will not change when adapters land.

Stub semantics for future implementers:

- Both official video APIs are **async job APIs** (OpenAI Sora:
  `POST /v1/videos` then poll; Gemini Veo: `:predictLongRunning` then poll
  the operation). The contract hides that: `generate_video()` blocks,
  polling internally with the spoke's transport, and returns finished
  bytes. If we later need progress, we will add an optional
  `progress_cb(fraction)` kwarg — additive, non-breaking.
- Video pricing goes into a `VIDEO_PRICES` table in `ledger.py` (per
  second of output); until then rows record `priced: false`.
- The same host pinning and `assert_key_safe()` rules apply — polling URLs
  must stay on the official host.

---

## 7. The hub (`gateway.py`)

```python
gw = Gateway()                       # shared Keyring + shared Ledger
gw.chat("gemini", [ChatMessage("user", "Suggest a palette")])
gw.generate_image("openai", "an atelier at dusk, gouache", quality="low")
gw.usage_summary()                   # per-provider spend, all spokes
```

The Gateway builds spokes lazily, caches them per provider id, injects the
shared keyring/ledger (and a shared transport for tests), and surfaces
configuration gaps as `SpokeError` with the exact CLI command to fix them
(e.g. `openai_compatible` without a `base_url`).

## 8. Adding a new spoke — checklist

1. One file `spokes_<name>.py`, importing only `spokes_base`.
2. Pin `allowed_hosts` to the provider's official API host; route every
   credentialed request through `assert_key_safe()` + `http_call()`.
3. Resolve keys via the shared `Keyring` (add the provider's env-var names
   to `keyring.ENV_VARS`); raise `AuthError` at construction when missing.
4. Normalize usage into `Usage` and call `self._record(...)` after every
   successful call; add price rows to `ledger.py` (or leave unpriced).
5. Advertise honest `capabilities()`; raise `NotSupported` elsewhere.
6. Add recorded-response fixtures + tests per `TESTS.md` (FakeTransport,
   no sockets). Cover: happy path, streaming, auth error, and one
   key-guard assertion.
7. Register the provider id in `gateway.py`.
