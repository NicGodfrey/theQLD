# Testing the BYOK gateway — no live keys required

The entire suite runs **offline**: no sockets are opened, no API keys are
read from the real environment or home directory, and nothing costs money.
Live verification exists but is a separate, explicitly-armed script (§5).

## 1. Run it

```bash
cd 03-keyring-spokes
python3 run_tests.py                    # 68 tests, < 1s
# or:
python3 -m unittest discover -s tests -v
```

No dependencies beyond the Python 3.9+ standard library.

## 2. How offline testing works

Two seams make the code testable without the network:

1. **Transport injection.** Every spoke takes a `transport=` constructor
   argument (default: the real `UrllibTransport`). Tests pass
   `tests/fakes.FakeTransport`, which:
   - returns scripted responses in FIFO order
     (`enqueue_json(...)`, `enqueue_fixture("openai_chat.json")`,
     status/headers configurable);
   - records every request (`method`, `url`, `headers`, decoded JSON
     body, `stream` flag) so tests assert **exactly what would have gone
     on the wire** — URL pinning, auth headers, payload shape;
   - raises on any unexpected request, so a test fails loudly if a spoke
     makes an extra call.
2. **Hermetic keyring/ledger.** Tests construct
   `Keyring(path=<tmpdir>, env={...})` and
   `Ledger(path=<tmpdir>/ledger.jsonl, override_path=<tmpdir>/prices.json)`,
   so the real `~/.atelier/` and real environment variables are never
   touched (and a developer's real `OPENAI_API_KEY` can never leak into a
   test). Explicit `api_key="sk-test-not-real"` arguments skip all
   disk/env access entirely.

Because streaming responses are read through the same
`HttpResponse.iter_lines()` interface, SSE is tested by enqueuing a
recorded `.sse` byte blob — no threads, no sockets.

## 3. Fixtures

`tests/fixtures/` holds recorded-response fixtures matching each
provider's documented response shapes:

| Fixture | Simulates |
|---|---|
| `openai_chat.json` | `POST /v1/chat/completions` (non-stream, with `usage`) |
| `openai_chat_stream.sse` | SSE chunk stream incl. `stream_options.include_usage` final-usage chunk and `[DONE]` |
| `openai_image.json` | `POST /v1/images/generations` (`gpt-image-1`, `b64_json` + token usage) |
| `ollama_chat.json` | Ollama's OpenAI-compatible chat response |
| `gemini_chat.json` | `:generateContent` with `usageMetadata` |
| `gemini_chat_stream.sse` | `:streamGenerateContent?alt=sse` chunks (cumulative `usageMetadata`) |
| `gemini_image.json` | Native image output (`inlineData` part + text part, 1290-token image) |
| `imagen_predict.json` | `imagen-*:predict` with two `bytesBase64Encoded` predictions |
| `anthropic_chat.json` | `POST /v1/messages` (non-stream) |
| `anthropic_chat_stream.sse` | `message_start` / `content_block_delta` / `message_delta` event stream |

Image fixtures embed a **real 1×1 PNG** (built with zlib in
`tests/make_fixtures.py`), so base64-decode paths and PNG magic-byte
checks are exercised for real. Regenerate everything with:

```bash
python3 tests/make_fixtures.py
```

To add a fixture for a new case: capture the provider's documented example
response (or a sanitized real one — **strip any ids/keys**), add it to
`JSON_FIXTURES`/`SSE_FIXTURES` in `make_fixtures.py`, regenerate, and
enqueue it in a test.

## 4. What is covered where

| File | Coverage |
|---|---|
| `test_openai_spoke.py` | chat round-trip (URL, bearer header, `max_completion_tokens`), streaming + usage chunk, multimodal → `data:` URL, gpt-image-1 vs dall-e-3 payload differences, PNG decode, 401→`AuthError`, 429 retry then success, retry exhaustion→`RateLimitError`, **base_url pinning (`KeyLeakError`)**, **plain-HTTP-off-loopback refusal with zero requests sent**, missing-key fail-fast, Ollama keyless/local/legacy `max_tokens`/$0-priced, compat base_url from keyring, video stub |
| `test_gemini_spoke.py` | chat round-trip (`x-goog-api-key`, role mapping, `systemInstruction`, `generationConfig`), SSE streaming, image input → `inlineData`, blocked-prompt → `ProviderError`, native image gen (modalities, aspect ratio, ledger $0.039), `n=2` loop = 2 calls, Imagen `:predict` (sampleCount, aspectRatio, $0.04/image), text-only model in image call → error, missing key, https guard, aspect-ratio mapping |
| `test_anthropic_spoke.py` | chat (headers incl. `anthropic-version`, `system` promotion, required `max_tokens` defaulting), event-stream parsing with usage reconciliation, image gen `NotSupported`, missing key |
| `test_keyring.py` | 0600/0700 permissions, loose-permission tightening, symlink refusal, corrupt-file error, atomic round-trip, delete, base_url-only entries, key preservation on metadata update, env-over-file precedence, `ATELIER_*`-scoped over conventional vars, `GOOGLE_API_KEY` fallback, base_url env override, masking/no-secret-in-repr |
| `test_ledger.py` | per-1M-token math, longest-prefix model matching, unknown model → `priced:false` (never fake-free), image pricing by size|quality with `*` fallback, per-provider aggregation, `since` filter, 0600 JSONL, override argument + override file |
| `test_gateway.py` | provider routing, spoke caching, shared ledger across providers, unknown provider error, `openai_compatible` without base_url → actionable config error, capability pass-through |

Security-relevant tests to keep green forever: the two `KeyLeakError`
tests (pinning + https), `test_compat_refuses_plain_http_off_loopback`
asserting **zero** requests left the process, and every permissions test.

## 5. Optional: live smoke test (spends pennies, never runs by accident)

```bash
ATELIER_LIVE=1 python3 live_smoke.py openai          # ~$0.0001 (gpt-4o-mini)
ATELIER_LIVE=1 python3 live_smoke.py gemini          # ~$0.0001 (2.5-flash-lite)
ATELIER_LIVE=1 python3 live_smoke.py anthropic       # ~$0.001  (haiku)
ATELIER_LIVE=1 python3 live_smoke.py ollama          # free, local
ATELIER_LIVE=1 python3 live_smoke.py openai --image  # ~$0.01-0.04 (gpt-image-1)
```

The script exits immediately unless `ATELIER_LIVE=1` is set, uses the
cheapest model per provider, sends a fixed one-line prompt, and prints the
result plus the ledger rows it produced — a end-to-end check of key
resolution, host pinning, and accounting against the real APIs.

## 6. CLI smoke (offline, verified)

```bash
export ATELIER_KEYRING=/tmp/demo/keyring.json
printf 'sk-demo\n' | python3 keyring.py set openai --stdin
python3 keyring.py set ollama --no-key --base-url http://127.0.0.1:11434/v1
python3 keyring.py list                       # masked keys, sources
python3 ledger.py summary --path /tmp/demo/ledger.jsonl
```
