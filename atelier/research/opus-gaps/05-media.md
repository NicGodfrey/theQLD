# Media gaps — live `atelier/helix` vs `research/fable5/07-loom`

*Opus#5 of 10 · 2026-08-21 · read-only pass over `/workspace`, all probes under `/tmp/atelier-opus/05-media-gaps/`*

Reviewed at commit `6515594`. Peer agents landed uncommitted, not-yet-wired
helpers in the working tree while this pass ran; Section 7 reconciles them.

## Verdict

The live studio has **one** media pipeline (image), **one** demo renderer (a fixed
1024×1024 SVG), and **no** export path. The research module has four pipelines
(image / brief / speech / video), eight demo renderers, provenance sidecars, a
retrying HTTP layer, and a 25-asset keyless kit — 1,339 lines against the live
45. Nothing from `07-loom` has been wired in.

The most damaging gaps are not the missing modalities. They are three things that
make the *existing* image loop unfit to ship:

1. **No size or aspect control reaches either provider.** `Conductor.run` calls
   `image_spoke.image(prompt, model=...)` and never passes `size`, so OpenAI is
   pinned to `1024x1024` and Gemini gets no `imageConfig` at all. Asking for a
   9:16 story returns a square. Verified end-to-end against a running server.
2. **Provider failures are silently disguised as success.** A 401, a 429, or a
   malformed 200 all fall through to `DemoSpoke`, and the run reports
   `Route: openai / gpt-4o-mini` while the artifact on the board carries
   `provider=demo`. The user is never told their key was rejected.
3. **There is no export.** `GET /api/artifacts/{id}` is the only way a file
   leaves the app, and it always sends `Content-Disposition: attachment;
   filename="<hex>.bin"` — every asset downloads as `.bin`, with no sidecar and
   no embedded provenance.

A fourth, quieter one: `estimate_usd` returns `0.0` for any unit kind that isn't
tokens or images, so the moment video (`seconds`) or TTS (`characters`) is wired
in, real spend meters as **$0.00**.

The minimum set for 成品可用 is therefore **not** "add video and audio". It is
"make the image loop honest, sized, and exportable" — Section 5. Video and TTS
belong in the tier after that (Section 6).

---

## 1. Inventory

| Capability | Live (`atelier/helix`) | Research (`research/fable5/07-loom`) |
|---|---|---|
| Image — OpenAI | `openai_spoke.image`, `/v1/images/generations`, `n=1`, `size` accepted but never passed by the caller | `openai_images()` + `quality`, real `n`, `revised_prompt` captured, url-mode fallback |
| Image — Gemini | `gemini_spoke.image`, `:generateContent`, no `imageConfig` | `gemini_images()` with `size`→`aspectRatio` mapping over 10 ratios |
| Image — Imagen | absent (no guard either) | `gemini_imagen_images()`, labelled shut down 2026-08-17, Vertex note |
| Brief expansion | none (planner JSON only) | `demo_brief` + `openai_brief` + `gemini_brief`, 13-key schema, validated |
| Speech / TTS | **none** — `Spoke` protocol has only `chat` + `image` | `openai_speech` (6 formats), `gemini_speech` (PCM→WAV), `demo_speech` |
| Video | **none** | `VideoPipeline` (submit/poll/download/generate), `VeoVideo`, `SoraVideo`, `DemoVideo` |
| Demo renderers | `demo_svg()` — one fixed 1024×1024 layout | PNG writer (zlib+struct), SVG (+SMIL animated), WAV chime, identicon, swatch strip |
| Provenance | SQLite row only | `Asset.write_sidecar()` on every file |
| Demo kit | none | `demo_assets.build_kit()` → 25 assets, deterministic, `manifest.json` |
| HTTP resilience | none — single attempt, `HTTPError` only | retries 429/500/502/503/504, backoff 2s/4s, `URLError` handled |
| Error taxonomy | `SpokeError` | `LoomError` / `MissingKeyError` / `ProviderHTTPError(status,url,body)` |
| Export | none | none (PNG writer exists; no JPEG/PDF/MP4 encoder) |
| Host lock | `assert_official_host` on every spoke | **none** — `OPENAI_BASE_URL` is free-form by design |
| Usage ledger | tokens + images | none (no ledger integration at all) |

Both probes reproduce cleanly: `loom.py selftest` → 11 files; `loom.py demo-kit`
→ 25 assets, zero network, ~1.2 s.

---

## 2. Gap detail

### 2.1 Video — absent from live, job-shaped in research

Live has no video anywhere: no spoke method, no `weave` kind (`PLANNER_SYSTEM`
advertises only `image` and `note`, and `Conductor.run` handles only those two),
no node type in `web/app.js` (anything not `type=="image"` renders as a text
card), no `seconds`/`duration` column, no job table. The single vestige is
`write_bytes`'s `"video/mp4": ".mp4"` entry, which nothing can reach.

Research supplies the right shape: `VideoJob` is a plain serializable record and
`VideoPipeline` is `submit`/`poll`/`download` with a blocking `generate()`
wrapper, because both official backends are asynchronous and take minutes.
`VeoVideo` is live (`:predictLongRunning` → operation polling → `uri` or inline
base64, both shapes handled). `SoraVideo` is deprecated 2026-03-24 with removal
2026-09-24, warns on submit, and should not be ported as a default.

Two porting constraints the research module does not solve:

- **The live HTTP surface is synchronous and single-shot.** `POST
  /api/threads/{id}/run` blocks; a 900-second Veo poll inside it will time out
  any browser. Video needs a jobs table plus `GET /api/jobs/{id}`, which is a
  server + store + UI change, not a loom change.
- **`DemoVideo` emits an animated SVG with mime `image/svg+xml`.** It is a fine
  canvas placeholder and it can never satisfy an MP4 export. Keyless mode cannot
  produce MP4 without an encoder; say so in the UI rather than implying it.

### 2.2 Audio / TTS — absent from live

The `Spoke` protocol itself blocks this: `base.py` declares `chat` and `image`
only, so there is nowhere for `speech()` to live without widening the protocol.
No audio node type, no `<audio>` element in the board renderer, no
`characters` unit in the cost table.

Research has both official paths done properly, including the part that is easy
to get wrong: Gemini TTS returns **raw s16le mono PCM at 24 kHz**, base64 in an
`inlineData` part, and `pcm_to_wav()` wraps it with the stdlib `wave` module —
no ffmpeg. OpenAI's `/v1/audio/speech` returns bytes with no JSON envelope,
which the live `_post()` (which always `json.loads` the body) cannot handle at
all; TTS needs a raw-bytes sibling to `_post`.

TTS is the cheapest real modality to add (one endpoint, no polling, no job
table) and it is what makes storyboard/teaser work meaningful later. It is still
not part of the 成品可用 floor — see Section 5.

### 2.3 Provenance sidecar — DB-only, and the file carries nothing

Live provenance is a SQLite row (`kind, path, mime, prompt, provider, model,
created_at`). Verified against a live server: the artifacts directory contains
exactly `<id>.svg` and nothing else. So:

- an exported file, once out of the app, has **no** record of engine, prompt, or
  time — the opposite of the spec's "engine name visible in export metadata"
  (`ACCEPTANCE.md` M-3, `UX_FLOWS.md` §5.4 asks for XMP embedded in the artifact);
- there is no `sha256` and no `byte_size`, so nothing detects a truncated or
  swapped file (the research schema at `04-helix-arch/schema.sql:172` has both,
  with a hex-format check and an I4 freeze trigger);
- there is no `params`/`meta` JSON, so `revised_prompt`, resolved aspect ratio,
  quality, seed, and voice have nowhere to go even when a provider returns them;
- there is no `parent_id`/`revision`, so edit lineage (Section 2.8) is
  unrepresentable.

Research writes `<file>.<ext>.json` beside every asset via
`Asset.write_sidecar()`, with the provider-specific `meta` populated. Porting is
small; the store migration is the real work. Note that neither side embeds XMP —
that stays a net-new item.

### 2.4 Demo kit — the live keyless mode is one square SVG

`demo_svg()` produces a single fixed 1024×1024 layout: two circles, a title, and
the prompt truncated at 180 characters on one unwrapped line. There is no size
argument, no PNG, no palette, no avatar, no audio, no animation, and no manifest.

Consequences beyond aesthetics:

- **keyless mode cannot produce a raster at all** — a user without keys can only
  ever get SVG, which most social and print targets reject;
- **no snapshot-test corpus.** The research kit is byte-deterministic for a given
  prompt (verified by `diff -r` per `PIPELINES.md`), which is exactly what UI
  snapshot tests need; the live suite tests only that `demo_svg` contains
  `"<svg"`;
- **no demo for anything but images**, so a video or audio node cannot be
  designed in the UI before the paid path exists.

Porting `render_placeholder_png` (pure `zlib`+`struct`), `render_swatch_png`,
`render_identicon_png`, `render_chime_wav`, and the animated-SVG flag brings the
live demo mode to parity for roughly 250 lines of stdlib, with no dependencies.

### 2.5 `gpt-image-1` vs `dall-e-3` — one body for two different APIs

Live sends `{model, prompt, n:1, size}` and adds `response_format: "b64_json"`
when the model starts with `dall-e`. That is the only branch. Missing:

| Concern | Live | Consequence |
|---|---|---|
| `quality` | not sent | `gpt-image-1` (`low\|medium\|high\|auto`) and `dall-e-3` (`standard\|hd`) both stuck on default |
| Size legality | none | the two models take **disjoint** non-square sizes (`1536x1024`/`1024x1536` vs `1792x1024`/`1024x1792`); any non-square request will 400 on one of them |
| `n` | hardcoded 1 | `Conductor` loops `count` as separate API calls; for `gpt-image-1` one call with `n=2` is the cheaper shape |
| `revised_prompt` | dropped | `dall-e-3` rewrites prompts; the user never sees what was actually rendered (research keeps it in the sidecar) |
| `gpt-image-1-mini` | unreachable | priced in `usage.py` at $0.020 but `_image_model()` hardcodes `gpt-image-1`; the cheap tier cannot be selected |
| `background: "transparent"` | not sent | **blocks M-6's "PNG (incl. transparent)"** — `gpt-image-1` supports this natively at generation time |
| `output_format` | not sent | `gpt-image-1` can emit `jpeg`/`webp` directly; this is the only realistic JPEG source without adding an encoder |

Research fixes the first four. `background` and `output_format` are gaps on
**both** sides and are the cheapest wins in the whole report — two request fields
that convert directly into two spec line items.

### 2.6 Gemini image path and the Imagen shutdown

Live `gemini_spoke.image` sends `responseModalities: ["IMAGE","TEXT"]` and no
`imageConfig`, so **aspect ratio cannot be requested at all** — every Gemini
image is the model default. Research maps `WxH` to the nearest of ten supported
ratios (`_closest_aspect`). This is the single highest-value line to port.

Two more:

- **Key in the query string.** Live builds `?key=<secret>` (`gemini_spoke.py:36`);
  research uses the `x-goog-api-key` header. Query strings land in proxy and
  access logs, which is a poor fit for a product whose pitch is "keys stay on
  this machine".
- **No Imagen guard.** Imagen on the Gemini API shut down 2026-08-17. Live has
  no adapter (correct) but also no rejection: typing `imagen-4.0-generate-001`
  into the model box POSTs `:generateContent` — the wrong verb for a `:predict`
  model, against a dead endpoint — and the resulting 4xx is swallowed into a
  demo SVG (Section 2.9). Meanwhile `usage.py` still prices
  `imagen-3.0-generate-002` and `imagen-4.0-generate`, advertising models that
  cannot be called. Delete those rows and reject `imagen-*` on the Gemini
  provider with a message naming the shutdown and pointing at Vertex.

### 2.7 Export formats — PNG / JPEG / SVG / PDF / MP4

There is no export code on either side. Live reality:

- demo path produces **SVG only**; keyed path produces PNG (OpenAI) or whatever
  MIME Gemini returns;
- no conversion, no scale (`1x/2x/4x`), no transparent-background option, no
  contact sheet, no zip, no fanout;
- **every download is named `<id>.bin`** — verified: `Content-Type: image/svg+xml`
  with `Content-Disposition: attachment; filename="...bin"`. The Content-Type is
  right and the filename is wrong for every format;
- `Content-Disposition: attachment` is sent unconditionally, including for the
  `<img src>` the board uses to render nodes.

Against `ACCEPTANCE.md` M-6 (PNG incl. transparent, JPEG, SVG, PDF-RGB, MP4/H.264):

| Format | Reachable stdlib-only | Route |
|---|---|---|
| SVG | yes | already the demo output; needs the right filename |
| PNG | yes | provider bytes; `write_png()` from research for demo mode |
| PNG transparent | yes, keyed only | `background: "transparent"` on `gpt-image-1` |
| JPEG | keyed only | `output_format: "jpeg"` on `gpt-image-1`; no stdlib encoder for the demo path |
| PDF-RGB | yes | hand-built PDF embedding the PNG as a Flate image XObject (~120 lines, no deps) |
| MP4 | keyed only | passthrough download from Veo; never from an animated SVG |

So the honest stdlib-only export set is **SVG + PNG + PDF everywhere, JPEG and
transparency when a key is present, MP4 only from Veo**. Closing the remaining
holes (SVG→raster, JPEG from demo assets, 2x/4x resampling) requires exactly one
dependency decision: Pillow, plus a renderer such as resvg/cairosvg for SVG
rasterization. That is the fork in the road — either take the dependency and
match the spec, or ship the reduced matrix and label it in the export dialog. Do
not ship the current state, where the format question never gets asked.

### 2.8 Background removal, spot-edit, and masks — blocked by a deeper gap

Both are MVP items (`ACCEPTANCE.md` M-4) and neither side implements them.
Research is explicit that `/images/edits` and `/images/variations` are out of
scope. But the blocker is one level down: **no spoke accepts an input image.**
`Spoke.image(prompt, model, **kwargs)` takes text only, and `ImageResult` is
output-only. That single limitation rules out image-to-image, reference/logo
conditioning, image-to-video, inpainting, outpainting, and background removal
simultaneously.

Unblocking it needs, in order:

1. a `multipart/form-data` encoder (stdlib-doable, ~40 lines) for
   `POST /v1/images/edits` (`image[]` + `mask`, where the mask's **transparent**
   pixels mark the region to regenerate), and inline `inlineData` input parts for
   Gemini, which edits natively via `generateContent`;
2. `artifacts.parent_id` + `revision` + a mask artifact kind, so an edit is a
   child of its source rather than an unrelated row;
3. a canvas mask tool (brush minimum; auto-mask needs a segmentation model that
   neither official API exposes as a primitive);
4. an acceptance harness for "pixels outside the mask byte-identical" — worth
   noting that generative edits do **not** guarantee this, so honest delivery is
   client-side compositing of the model's output through the mask, not a promise
   that the provider preserved the surround.

For background removal specifically, the reachable approximations are
`background: "transparent"` at generation time (good, but only for new assets)
and an edits call instructed to cut the subject out (quality not guaranteed). A
one-click canvas verb with reliable alpha needs a matting model — a third engine,
not a prompt.

### 2.9 Error handling when keys fail mid-weave — verified failure modes

Probed with `urlopen` patched at five failure points
(`probe/probe_live.py`, output reproduced below).

| Scenario | Observed | Assessment |
|---|---|---|
| **401** bad key | run returns HTTP 200, `artifacts=1`, artifact `provider=demo model=demo-svg`, message says `Route: openai / gpt-4o-mini` | silent substitution; the user believes they got an OpenAI image |
| **429** rate limited | identical to 401 — and **no retry attempted** | research retries 429/5xx with 2s/4s backoff; live burns the turn on a transient error |
| **200 with no image** | identical | malformed provider output is indistinguishable from a bad key |
| **`URLError`** (network drop / DNS / TLS) | **`urllib.error.URLError` escapes**: 0 artifacts, 0 files, messages `['user']` only | neither spoke catches `URLError`, so it slips past `except SpokeError`, becomes a 500, and leaves a user message with no reply — the whole turn is lost, board unchanged |
| **`BudgetExceeded`** mid-weave | **raises after the paid call**: 1 artifact row + 1 file on disk, **no node**, no assistant message | orphaned artifact; and because `usage.record` runs *after* generation, the guard cannot prevent spend — it only aborts the bookkeeping. Directly contradicts M-3 ("cost displayed before every generation; generation cannot fire without it") |

Four more from reading the same path:

- **No error isolation across weave items.** A hard failure on item 2 of 4 kills
  the remaining items; the successful ones stay on the board with no explanation.
- **The weave cap is 8, not 4.** `ARCHITECTURE.md` claims "a hard weave cap (4)",
  but the loop is `weave_items[:4]` × `count ≤ 2` — up to eight paid image calls
  from one prompt, with the budget guard firing only after each one.
- **Planner failure is swallowed with `pass`** (`conductor.py:127-130`), so a
  provider outage silently downgrades to `fallback_plan` with no note.
- **`_download()` fetches provider-returned URLs with no host check and no size
  cap**, unlike every other request in the codebase, which goes through
  `assert_official_host`.

The fix set is small and mostly not in loom: catch `URLError` in both spokes and
wrap it as `SpokeError`; port the retry helper; check the budget *before* the
call using a priced estimate; make the demo fallback set a visible
`degraded: {provider, status, detail}` on the node and a chat line; and make the
artifact write transactional with the node insert.

### 2.10 Porting hazards (do not copy `loom.py` in as-is)

`07-loom` was written as a standalone CLI and violates three live invariants:

1. **Host lock.** `Config.from_env` accepts any `OPENAI_BASE_URL`, and
   `PIPELINES.md` advertises "works with Azure-style gateways". Live
   `assert_official_host` exists precisely to reject that. Media adapters must
   take keys from `Keyring` and URLs through the host assertion.
2. **Usage ledger.** Loom records nothing. Ported media calls must emit
   `usage.record` rows, which means new unit kinds (`seconds`, `characters`,
   `audio_seconds`) and cost-table entries — otherwise `estimate_usd`'s fallback
   silently prices them at **$0.00**.
3. **Its own HTTP stack.** Keep one. The right direction is to lift loom's
   retrying `_http`/`_http_json` into the spoke base and delete loom's copy,
   rather than running two HTTP layers with different retry semantics.

---

## 3. Store and API changes implied

Media work is mostly *not* in `loom.py`. Minimum schema additions to
`helix/store.py`:

```
artifacts:  sha256, byte_size, width, height, duration_ms,
            params_json (quality/aspect/voice/seed/revised_prompt),
            parent_id, revision, degraded_json
jobs:       id, project_id, thread_id, provider, model, kind,
            job_id, status, submitted_at, polled_at, error_json
usage:      unit kinds 'seconds' | 'characters' + cost rows for
            veo-3.0-generate-001 and gpt-4o-mini-tts
```

New endpoints: `GET /api/artifacts/{id}/export?format=&scale=&background=`,
`GET /api/artifacts/{id}/sidecar`, `POST /api/jobs` + `GET /api/jobs/{id}`,
`POST /api/projects/{id}/export` (board contact sheet / zip). And a one-line fix
to the existing handler: send the real extension in `Content-Disposition`, and
only send it when a download is actually requested.

---

## 4. Ordered port plan

Grouped by what changes, not by calendar.

**A. Make the image loop honest** — `spokes/*`, `conductor.py`
`URLError`→`SpokeError`; retry 429/5xx; pass `size` through `Conductor` to both
spokes; Gemini `imageConfig.aspectRatio` via `_closest_aspect`; OpenAI `quality`
+ per-model size validation + `revised_prompt`; move the budget check before the
call; surface `degraded` on the node and in chat; reject `imagen-*`; move the
Gemini key to the `x-goog-api-key` header.

**B. Make files leave the app** — `server.py`, new `helix/export.py`
Correct filenames; sidecar writer; `sha256`/`byte_size`; PNG passthrough; PDF
writer; `background`/`output_format` request fields for transparency and JPEG;
export endpoint with scale.

**C. Make keyless mode real** — `helix/loom.py`, `web/app.js`
Port `write_png`, `render_placeholder_png/svg` (with size + animated), swatch,
identicon, chime; add `demo_kit` behind a dev flag; snapshot tests on the
byte-deterministic output.

**D. Add the second and third modality** — `spokes/base.py`, `store.py`, `server.py`
Widen the `Spoke` protocol with `speech()` and the video job triple; raw-bytes
HTTP sibling for `/v1/audio/speech`; PCM→WAV; jobs table + polling endpoint;
`VeoVideo`; audio/video node types with `<audio>`/`<video>`; `seconds` and
`characters` in the cost table. **Do not** port `SoraVideo` as a default.

**E. Editing** — everything above plus a canvas tool
Input-image support on both spokes, multipart encoder, mask artifacts,
`parent_id`/`revision`, brush UI, compositing-based "outside the mask unchanged".

---

## 5. Minimum media set for 成品可用

The bar: *a designer can go from a brief to a file they can hand a client, and
the app never misrepresents what produced it.* Eight items, all reachable with
the two official APIs and the standard library.

1. **Image generation with real aspect control** — 1:1, 16:9, 9:16, 4:5 minimum,
   honored on both OpenAI and Gemini, chosen in the UI and recorded on the
   artifact. *Test:* request each of the four on both providers; the returned
   pixel ratio matches within one aspect bucket.
2. **A raster in keyless mode** — port the stdlib PNG writer so demo mode emits
   PNG + SVG at the requested size. *Test:* demo run at 1080×1920 yields a PNG
   with a valid signature and those dimensions.
3. **Correct file identity on the way out** — real extension, real
   Content-Type, `Content-Disposition` only when downloading. *Test:* download
   each of svg/png/webp/jpeg and get that suffix.
4. **Provenance that survives export** — a `<file>.json` sidecar plus
   `sha256`/`byte_size`/`params` in the DB, and the engine name visible on the
   node. *Test:* sidecar's sha256 matches the bytes on disk; engine name appears
   on the node and in the sidecar.
5. **Export set PNG + SVG + PDF-RGB**, with transparent PNG and JPEG when a key
   is present, and the reduced matrix stated in the dialog rather than implied.
   *Test:* one artifact exports to all three; the PDF opens and embeds the image
   at the right size.
6. **Honest failure** — no silent demo substitution. A degraded weave shows a
   badge on the node and a chat line naming the HTTP status; 429/5xx retried with
   backoff; `URLError` never escapes; a failed turn still records an assistant
   message. *Test:* the five scenarios in §2.9 all end with a user-visible,
   accurate explanation and no orphaned rows.
7. **Spend truth before the call** — budget checked against a priced estimate
   *before* generation; the weave cap in the docs matches the loop; no unit kind
   silently prices at zero. *Test:* a thread at its cap performs zero paid calls;
   `estimate_usd` raises (not returns 0.0) on an unpriced unit kind.
8. **A deterministic demo kit in CI** — the 25-asset kit as the snapshot corpus
   so UI work and regression tests need no keys or spend. *Test:* two builds of
   the same prompt are byte-identical apart from the manifest timestamp.

**Explicitly excluded from the floor, and why:** video (needs a jobs table, an
async API surface, and per-second billing — a whole subsystem for one node
type); TTS (cheap, but nothing in the floor consumes audio); spot-edit and
background removal (need input-image support plus a mask tool, and their
"unchanged outside the mask" promise cannot be kept by prompting alone); JPEG in
demo mode, SVG rasterization, and 2x/4x scaling (all gated on the Pillow
decision); PSD, CMYK, and fanout (P2 in the spec and correctly so).

The set is deliberately smaller than the spec's MVP. `ACCEPTANCE.md` M-3/M-4
were written for Lovart parity — four variants, a video engine, spot edit,
background removal. 成品可用 is a weaker and more urgent claim: the thing works,
tells the truth, and produces a file. Items 1, 3, 6, and 7 are all *defects* in
shipped behavior, not missing features, and they cost less than any one of the
deferred modalities.

---

## 6. Lovart-class later

**Tier 1 — credible studio** (the spec's real MVP, once the floor holds)
One video engine (Veo via the job interface; MP4 export; ≤10 s; no Sora),
TTS voiceover attachable to a video node, a Pick grid of 4 variants with a
recoverable variant stack, brief expansion wired to the board (the 13-key
research schema already drives images + voice + motion from one prompt), and
`gpt-image-1-mini` selectable so cheap iteration is possible.

**Tier 2 — editing parity** Input-image support across both spokes, spot edit
with brush and mask compositing, one-click background removal (accepting that
reliable alpha means a third engine), text-layer editing, node-scoped undo ≥ 50
steps.

**Tier 3 — scale-out** Fanout to ≥ 7 platform sizes in one job, Sweep strips,
multi-engine router with logged win rates, 4K upscale, layered PSD and CMYK+bleed
PDF — the spec's contested-claim differentiator, and the only place where a
non-stdlib dependency is unavoidable.

The ordering matters more than the contents: every Tier 1+ item multiplies the
cost of the Section 5 defects. Silent demo substitution is a bad bug on an image;
on a $0.40 Veo render metered at $0.00 it is a billing incident.

---

## 7. Concurrent work already in the tree (uncommitted at `6515594`)

Peer agents have written five pieces that overlap this report. All are present
in the working tree and **none are wired into `server.py` or `conductor.py`**, so
every defect verified in §2.9 and §2.7 still reproduces at runtime.

| In flight | Covers | Still needed |
|---|---|---|
| `loom.ext_for_mime()` + `MIME_EXT` | §2.7 filenames | wire into `server.py`'s `_send_file` call; send `Content-Disposition` only on download |
| `usage.is_priced()` | §5 item 7 | make `record()` refuse unpriced units instead of leaving the choice to callers; add `seconds`/`characters` rows |
| `artifacts.parent_id` + `undo_log` | §2.8 lineage, §3 schema | `revision`, `sha256`, `byte_size`, `params_json`, `degraded_json` still absent |
| `helix/http.py` (no-redirect opener) | part of §2.9 | it is a redirect hardening, **not** the retry/`URLError` fix; spokes still use bare `urllib.request.urlopen` |
| `helix/exportzip.py` (board zip) | part of §2.7 | zip is a container, not a format — PNG/JPEG/PDF conversion and the sidecar are still missing |

`demo_svg()` also gained a brand-palette argument, which is a good change and
orthogonal: it still emits one fixed 1024×1024 layout, so §2.4 (no raster, no
size, no kit) is unaffected.

Two notes for whoever merges: `helix/http.py` and the retrying `_http` this
report recommends porting from `07-loom` are the same seam, so they should be
one helper rather than two; and `is_priced()` currently documents the
`estimate_usd` fallback as safe for budget math while leaving the zero-price hole
open for any caller that forgets to ask — the video and TTS paths are exactly the
callers that will forget.

---

## Evidence

- `probe/probe_live.py` — five patched-transport failure scenarios against the
  live `Conductor`; output quoted in §2.9.
- `probe/loom-research/` — copy of `07-loom`; `selftest` → 11 files,
  `demo-kit` → 25 assets (`probe/kit/`, `probe/selftest-out/`).
- Live server on a private runtime (`ATELIER_RUNTIME`/`ATELIER_HOME` under
  `/tmp`): confirmed the `.bin` download name, the absent sidecar, and the
  1024×1024 SVG returned for a 9:16 request.
- No file under `/workspace` was modified; `PYTHONDONTWRITEBYTECODE=1`
  throughout.

One note for whoever reads this next: my first server attempt bound port 8791,
which was already held by a peer agent's Atelier instance, so my `curl` hit
their server and added one demo-mode project weave to it (no spend, no keys).
Subsequent probes used a verified-free port. Worth coordinating ports if several
of these run at once.
