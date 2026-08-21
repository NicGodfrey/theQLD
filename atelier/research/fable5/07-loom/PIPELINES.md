# Loom — Atelier Media Generation Pipelines

*Fable5#7 of 10 · module codename "loom" · BYOK, official APIs only, stdlib only.*

Loom is a single-file Python module (`loom.py`) plus a kit builder
(`demo_assets.py`) that gives Atelier four media pipelines — **images**,
**design briefs**, **speech**, and **video** — with two properties:

1. **BYOK against official endpoints only.** OpenAI (`api.openai.com`) and
   the Gemini API (`generativelanguage.googleapis.com`). No aggregators, no
   resellers, no scraping, no third-party SDKs.
2. **A keyless demo mode for every pipeline.** With no keys configured, every
   call still produces a real file (SVG/PNG/WAV/animated SVG) rendered with
   the Python standard library, so the Atelier UI can be built, demoed, and
   snapshot-tested with zero spend.

Everything is stdlib: HTTP via `urllib`, PNG via `zlib`+`struct`, WAV via
`wave`, SVG via string templates. There is no `requirements.txt` because
there are no requirements. Python ≥ 3.9.

```
                       ┌──────────────────────────────┐
  prompt ─────────────►│  Loom facade (provider router)│
                       └──────┬───────────┬───────────┘
                              │           │
             keys present     │           │   no keys
        ┌─────────────────────┤           └────────────────┐
        ▼                     ▼                            ▼
  OpenAI adapters       Gemini adapters              Demo renderers
  images/generations    :generateContent             PNG (zlib+struct)
  chat/completions      :predict (legacy)            SVG (+SMIL video)
  audio/speech          :predictLongRunning          WAV (wave module)
  /videos (deprecated)                               deterministic brief
        └─────────────────────┴───────────────────────────┘
                              ▼
              Asset record + JSON sidecar on disk
```

## Files

| File | Purpose |
|---|---|
| `loom.py` | All pipelines, provider adapters, demo renderers, CLI. |
| `demo_assets.py` | Builds a complete keyless asset kit (`manifest.json` + images/palette/avatars/audio/video). |
| `PIPELINES.md` | This document. |

## Configuration

| Variable | Meaning |
|---|---|
| `OPENAI_API_KEY` | Key for api.openai.com. |
| `GEMINI_API_KEY` | Key for the Gemini API (`GOOGLE_API_KEY` accepted as fallback). |
| `OPENAI_BASE_URL` | Override, default `https://api.openai.com/v1`. Works with Azure-style gateways that mirror the OpenAI surface. |
| `GEMINI_BASE_URL` | Override, default `https://generativelanguage.googleapis.com/v1beta`. |
| `LOOM_PROVIDER` | Default routing: `openai`, `gemini`, or `demo`. |
| `LOOM_TIMEOUT` | HTTP timeout in seconds (default 120). |
| `LOOM_OUT` | Default output directory for CLI commands (default `./loom-out`). |

**Provider routing** (images, briefs, speech): explicit `--provider` argument
→ `LOOM_PROVIDER` → first configured key (OpenAI, then Gemini) → `demo`.

**Video never auto-routes to a paid backend.** It defaults to `demo` and only
hits Sora/Veo when you name the provider explicitly. Video renders are slow,
expensive, and (in Sora's case) deprecated, so opting in must be deliberate.

Keys are read from the environment at call time, sent only in request
headers, and never written to disk, sidecars, or logs.

## Asset records and sidecars

Every generated file gets a JSON sidecar (`<file>.<ext>.json`) capturing
provenance — kind, provider, model, prompt, timestamps, and provider-specific
metadata (e.g. `revised_prompt` from dall-e-3, aspect ratio mapping for
Gemini). The CLI also prints the same records as JSON to stdout, so a UI or
orchestrator can shell out to `loom.py` and parse the result directly.

---

## Pipeline 1 — Images

### OpenAI Images API

`POST {OPENAI_BASE_URL}/images/generations` with `Authorization: Bearer <key>`.

| Model | Status (checked 2026-08) | Notes |
|---|---|---|
| `gpt-image-1` (default) | Live | Always returns `b64_json`. Sizes `1024x1024`, `1536x1024`, `1024x1536`, `auto`. Quality `low\|medium\|high\|auto`. Supports `n`. `gpt-image-1-mini` also exists for cheaper renders. |
| `dall-e-3` | Live, legacy | Loom forces `response_format: "b64_json"` and `n: 1` (API limit). Sizes `1024x1024`, `1792x1024`, `1024x1792`. Quality `standard\|hd`. Returns `revised_prompt`, captured in the sidecar. |

Request body loom sends (gpt-image-1):

```json
{"model": "gpt-image-1", "prompt": "...", "size": "1024x1024", "n": 1, "quality": "high"}
```

Response handling: each `data[i]` item is decoded from `b64_json`, or — for
legacy URL-mode responses — downloaded from `url`. Files land as PNG with a
sidecar.

Not implemented (documented for future work): `POST /images/edits`
(multipart; inpainting/reference images) and `POST /images/variations`
(dall-e-2 only). Multipart encoding is doable in stdlib but out of scope here.

### Gemini image models

`POST {GEMINI_BASE_URL}/models/{model}:generateContent` with
`x-goog-api-key: <key>`.

| Model | Status (checked 2026-08) | Notes |
|---|---|---|
| `gemini-2.5-flash-image` (default) | GA ("Nano Banana") | Native multimodal image generation via `generateContent`. One image per call → `n>1` loops requests. |
| `gemini-3.1-flash-image-preview`, `gemini-3-pro-image-preview` | Preview | Same request shape; pass via `--model`. Add higher resolutions and more aspect ratios. |
| `imagen-4.0-generate-001` (and `-fast`/`-ultra`) | **Shut down on the Gemini API 2026-08-17** | Used `:predict` with `instances`/`parameters`. Adapter retained in `gemini_imagen_images()` because the identical shape still runs on Vertex AI; calling it against the Gemini API now returns 4xx. |

Request body loom sends (Nano Banana):

```json
{
  "contents": [{"role": "user", "parts": [{"text": "..."}]}],
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": {"aspectRatio": "16:9"}
  }
}
```

Loom maps your `--size WxH` request to the closest supported `aspectRatio`
enum (`1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `5:4`, `4:5`, `16:9`, `9:16`,
`21:9`); the actual pixel size is chosen by the model. Images come back as
base64 `inlineData` parts and are written with their reported MIME type.

Legacy Imagen shape, for reference (now Vertex-only):

```json
{"instances": [{"prompt": "..."}], "parameters": {"sampleCount": 2, "aspectRatio": "1:1"}}
```

### Demo images

`demo_images()` renders deterministic placeholders from a SHA-256 digest of
the prompt: an SVG (gradient + prompt text + label) and/or a PNG (diagonal
two-color gradient with a mirrored 8×8 glyph overlay, encoded by a pure-stdlib
PNG writer). Same prompt → same bytes, forever — good for snapshot tests.

```bash
python loom.py image "poster for a night market" --provider demo --size 1280x720
python loom.py image "poster for a night market"                 # auto: uses a key if present
python loom.py image "..." --provider gemini --model gemini-3-pro-image-preview
python loom.py image "..." --provider openai --model dall-e-3 --quality hd
```

---

## Pipeline 2 — Text → design brief expansion

Turns a one-line idea into a structured brief the other pipelines can
consume. The schema is identical across providers (`BRIEF_KEYS` in
`loom.py`):

```
title, tagline, summary, audience, tone[3],
palette[5]{role,hex}, typography{display,body}, imagery[3],
deliverables[]{name,kind,size}, image_prompts[3],
voice_script, motion_prompt
```

`image_prompts` feed the image pipeline, `voice_script` feeds TTS, and
`motion_prompt` feeds video — so one brief drives a full asset kit.

| Provider | Endpoint | Default model | JSON enforcement |
|---|---|---|---|
| OpenAI | `POST /chat/completions` | `gpt-4o-mini` (override with `--model`) | `response_format: {"type": "json_object"}` |
| Gemini | `POST /models/{m}:generateContent` | `gemini-2.5-flash` | `generationConfig.responseMimeType: "application/json"` |
| Demo | — (offline) | `demo_brief()` | Deterministic template expansion seeded by the prompt digest: palette scheme (analogous/complementary/triadic), curated type pairings, tone words, art direction. |

Responses are validated against the key list; missing keys raise `LoomError`
rather than passing a malformed brief downstream.

```bash
python loom.py brief "a specialty coffee subscription" --provider demo
python loom.py brief "a specialty coffee subscription" --out brief.json   # with keys
```

---

## Pipeline 3 — Speech / TTS

### OpenAI

`POST {OPENAI_BASE_URL}/audio/speech` → raw audio bytes (no JSON envelope).

- Models: `gpt-4o-mini-tts` (default; accepts an `instructions` field for
  delivery style), `tts-1`, `tts-1-hd`.
- Voices: `alloy` (default), `ash`, `ballad`, `coral`, `echo`, `fable`,
  `onyx`, `nova`, `sage`, `shimmer`, `verse`.
- Formats: `mp3` (default), `wav`, `opus`, `aac`, `flac`, `pcm`.

```json
{"model": "gpt-4o-mini-tts", "input": "...", "voice": "alloy", "response_format": "mp3"}
```

### Gemini

`POST {GEMINI_BASE_URL}/models/{model}:generateContent` with
`responseModalities: ["AUDIO"]` and a `speechConfig`:

```json
{
  "contents": [{"role": "user", "parts": [{"text": "..."}]}],
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}
  }
}
```

- Models (checked 2026-08): `gemini-2.5-flash-preview-tts` (default),
  `gemini-2.5-pro-preview-tts`, `gemini-3.1-flash-tts-preview` (adds
  streaming, which loom does not use).
- Voices: `Kore` (default), `Puck`, `Zephyr`, `Charon`, `Fenrir`, `Leda`,
  `Orus`, `Aoede`, and others; multi-speaker is possible via
  `multiSpeakerVoiceConfig` (not wrapped by loom).
- The response is **raw s16le mono PCM at 24 kHz** base64-encoded in an
  `inlineData` part. Loom parses the rate from the returned MIME type
  (`audio/L16;...;rate=24000`) and wraps the PCM in a WAV container with the
  stdlib `wave` module — no ffmpeg needed.

### Demo

`demo_speech()` writes a short seeded pentatonic chime (two-harmonic sine
with exponential decay, 24 kHz mono WAV). It is an audio *placeholder* — it
occupies the audio slot in a UI without pretending to be speech; the sidecar
says so explicitly.

```bash
python loom.py speech "Welcome to Atelier." --provider demo
python loom.py speech "Welcome to Atelier." --voice coral --format wav      # OpenAI
python loom.py speech "Welcome to Atelier." --provider gemini --voice Puck  # Gemini → WAV
```

---

## Pipeline 4 — Video

Video is **stub-first**. The contract is the `VideoPipeline` interface:

```python
class VideoPipeline:
    def submit(self, prompt, **options) -> VideoJob   # start a render job
    def poll(self, job) -> VideoJob                   # refresh status
    def download(self, job, out_dir) -> Asset         # write finished file
    def generate(self, prompt, out_dir, ...) -> Asset # blocking convenience
```

`VideoJob` is a plain serializable record (`provider`, `model`, `prompt`,
`job_id`, `status` ∈ `queued|in_progress|completed|failed`, `meta`). A UI
should persist `job.to_dict()` and poll — both official backends are
asynchronous and can take minutes.

### Backends

| Backend | Status (checked 2026-08) | Endpoints |
|---|---|---|
| `DemoVideo` (default) | Always available | Emits an animated SVG (SMIL `animateTransform` rotation + pulse) that completes instantly. Plays in any browser `<img>`/`<object>` tag; stands in for an MP4 in the UI. |
| `SoraVideo` (`--provider openai` / `sora`) | **Deprecated 2026-03-24; removal scheduled 2026-09-24. No announced replacement.** Loom prints a warning on submit. | `POST /v1/videos` (`model: sora-2\|sora-2-pro`, `size: 720x1280\|1280x720\|1024x1792\|1792x1024`, `seconds: "4"\|"8"\|"12"`) → job `{id, status}`; `GET /v1/videos/{id}` to poll; `GET /v1/videos/{id}/content` → MP4 bytes. |
| `VeoVideo` (`--provider gemini` / `veo`) | Live | `POST /v1beta/models/veo-3.0-generate-001:predictLongRunning` with `{"instances":[{"prompt": "..."}]}` (optional `parameters.aspectRatio`, `parameters.negativePrompt`) → `{"name": "<operation>"}`; `GET /v1beta/<operation>` until `done`; the finished operation's `generateVideoResponse.generatedSamples[0].video` carries a download `uri` (fetched with the API key header) or inline base64 bytes — loom handles both shapes. Veo 3.1 preview models accept the same shape via `--model`. |

```bash
python loom.py video "slow dolly across a moonlit harbor"                    # demo, instant
python loom.py video "..." --provider veo --aspect-ratio 16:9 --timeout 900  # Veo, blocks & polls
python loom.py video "..." --provider sora --seconds 8 --size 1280x720       # legacy Sora window
```

Anything not exposed by the stub (Sora remix, `input_reference`
image-to-video, Veo image conditioning, webhooks/Batch) is intentionally out
of scope; the job interface is the extension point.

---

## Demo mode and the asset kit

`demo_assets.py` composes the demo renderers into one coherent, deterministic
kit driven by a single prompt: the deterministic brief picks the palette,
type pairing, shot prompts, voice script, and motion prompt; every other
asset is seeded from those, so the whole kit shares one visual identity.

```bash
python demo_assets.py --prompt "Atelier — a studio for generative design" --out demo_assets_out
# or: python loom.py demo-kit --out demo_assets_out
```

Output (25 assets, ~180 KiB, < 2 s, zero network):

```
demo_assets_out/
├── manifest.json          # index: path, kind, mime, bytes, meta per asset
├── brief.json             # deterministic design brief
├── images/                # hero_16x9 / hero_1x1 / hero_9x16 + 3 brief shots (SVG+PNG each)
├── palette/               # 5-band strip + one 120x120 chip per role
├── avatars/               # 4 identicon PNGs (5x5 mirrored grid)
├── audio/voiceover.wav    # seeded chime standing in for TTS
└── video/teaser.svg       # animated SVG standing in for MP4
```

Determinism is byte-level: rebuilding the kit with the same prompt produces
identical files (verified by `diff -r`; `manifest.json` differs only in its
`generated_at` timestamp). Point the Atelier UI at `manifest.json`, and when
keys arrive, swap generators without changing the UI contract — real assets
carry the same sidecar/record shape.

## CLI reference

```
python loom.py image  PROMPT [--provider auto|openai|gemini|demo] [--model M]
                      [--size WxH] [--n N] [--quality Q] [--demo-format svg|png|both] [--out DIR]
python loom.py brief  PROMPT [--provider ...] [--model M] [--out FILE|-]
python loom.py speech TEXT   [--provider ...] [--model M] [--voice V] [--format F] [--out DIR]
python loom.py video  PROMPT [--provider demo|openai|sora|gemini|veo] [--model M]
                      [--size WxH] [--seconds S] [--aspect-ratio R] [--timeout SEC] [--out DIR]
python loom.py demo-kit [--prompt P] [--out DIR] [--png-size N]
python loom.py selftest [--out DIR]
```

Exit codes: `0` success · `1` pipeline/provider error (`LoomError`) ·
`2` missing API key (`MissingKeyError`).

## Error handling and retries

- All HTTP goes through one helper that retries 429/500/502/503/504 and
  network errors with exponential backoff (2 s, 4 s; 3 attempts total),
  then raises `ProviderHTTPError` carrying status, URL, and the response
  body's first 400 characters — vendor error messages surface verbatim.
- Malformed or unexpectedly-shaped responses raise `LoomError` with a
  truncated dump of what was received.
- Blocking video generation enforces a wall-clock timeout (default 900 s).

## Model lifecycle notes (verified against vendor docs, 2026-08)

| Surface | State |
|---|---|
| OpenAI `gpt-image-1` | Live; default image model. |
| OpenAI `dall-e-3` | Live but legacy; check the deprecations page before new builds. |
| Gemini `gemini-2.5-flash-image` | GA; default Gemini image model. |
| Gemini API Imagen (`imagen-4.0-*` via `:predict`) | Shut down 2026-08-17 (Gemini API); shape lives on in Vertex AI. |
| OpenAI Videos API / `sora-2` | Deprecated 2026-03-24; removal 2026-09-24; no announced replacement. |
| Gemini `veo-3.0-generate-001` | Live; Veo 3.1 in preview. |
| Gemini TTS (`*-preview-tts`) | Live in preview. |

When a default here dies, change the constant at the top of `loom.py`; every
model is also overridable per-call via `--model` without touching code.

## Extending

To add a provider (e.g. a self-hosted image server or a new official API):

1. Write an adapter function/class mirroring an existing one
   (`openai_images`, `VeoVideo`, …) that returns `Asset`s / `VideoJob`s.
2. Register it in the `Loom` facade's routing (`resolve` /
   `video_pipeline`).
3. Document its endpoint and lifecycle status in this file.

The demo renderers (`render_placeholder_png/svg`, `render_chime_wav`,
`render_identicon_png`, `render_swatch_png`) are importable on their own —
`demo_assets.py` is the reference consumer.
