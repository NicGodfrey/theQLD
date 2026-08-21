# FUTURE.md — post-MVP integrations: ComfyUI worker, ffmpeg, Remotion

These are deliberately **not** in the MVP. Each is designed as an out-of-process
worker behind an interface that already exists in MVP code, so adding them later is
additive: no MVP code changes shape, only new implementations get registered.

---

## 1. ComfyUI as an optional local generation worker

**Why.** Hosted image APIs (MVP) cost per call and cap control. ComfyUI gives users
with a GPU free local generation, LoRAs, ControlNet, inpainting — the power-user tier
that differentiates an open design agent.

**License constraint (drives the whole design).** ComfyUI is GPL-3.0. It must run as
a **separate process the user installs**, spoken to only over HTTP/WebSocket. Atelier
never imports, subclasses, or bundles ComfyUI code. Atelier ships only: (a) its own
workflow-template JSON files (our data, our license), and (b) a stdlib HTTP client
(`stubs/python/comfy_client.py`).

**Architecture.**

```
Atelier backend ──► JobQueue ──► ImageProvider interface
                                   ├── HostedProvider (MVP: fal/Replicate/OpenAI)
                                   └── ComfyProvider (future)
                                         │  POST /prompt          (queue graph)
                                         │  GET  /history/{id}    (poll status)
                                         │  GET  /view            (fetch PNG)
                                         │  POST /upload/image    (img2img input)
                                         ▼
                                  ComfyUI process (user-installed, GPL,
                                  localhost:8188 or LAN/container URL)
```

- **Workflow templates.** Atelier ships named templates in ComfyUI *API format*
  (`txt2img.json`, `img2img.json`, `inpaint.json`, `upscale.json`) with `{placeholder}`
  slots for prompt/seed/dimensions/model-name/input-image. Advanced users can drop
  their own exported API-format workflows into a templates directory; Atelier
  introspects placeholder slots and exposes them as generation parameters.
- **Capability probe.** On connect, hit `GET /object_info` to discover available
  checkpoints/samplers/LoRAs and surface them in the UI; degrade gracefully by hiding
  templates whose nodes are missing.
- **Progress.** MVP of the worker uses polling (`/history/{id}` every 500 ms with
  backoff). Optional upgrade: WebSocket `/ws?clientId=…` for step-level progress and
  live preview frames — needs a websocket client dependency, so it stays optional.
- **Deployment recipes** (docs, not code): bare `pip`-installed ComfyUI on the user's
  machine; or the community Docker images with `--listen`; queue length 1 per GPU,
  Atelier-side timeout + cancel via `POST /interrupt`.
- **Failure semantics.** Worker unreachable → provider reports unavailable, UI falls
  back to hosted providers with a notice. Never let a dead local worker block the
  agent loop.

**Effort shape.** New module (`ComfyProvider` ~200 lines + templates + probe), one
settings screen (worker URL + test button), no changes to planner/executor.

---

## 2. ffmpeg — export, video assembly, and media utility belt

**Why.** The moment Atelier does more than static images — animated exports, slideshow
renders from a canvas sequence, video ingestion for reference frames, GIF export —
ffmpeg is the only serious answer.

**License constraint.** ffmpeg is LGPL-2.1+ at its core, **GPL when built with
`--enable-gpl`** (which includes libx264/x265 — i.e., most practical H.264 builds).
Same playbook as ComfyUI: **subprocess boundary, never linking**.

- Invoke the **system `ffmpeg` binary** via `subprocess`. Calling a program over
  argv/pipes does not make Atelier a derivative work, even of a GPL build.
- Do **not** vendor ffmpeg binaries into Atelier releases initially (redistribution
  of a GPL build imposes source-offer obligations for that binary; patent questions
  around H.264/HEVC are the user's distro's problem, not ours). Discover the binary
  on PATH or via an `ATELIER_FFMPEG` setting; if absent, video features hide.
- Python bindings like `ffmpeg-python` (Apache-2.0) are just argv builders — fine but
  unnecessary; a small internal command builder keeps us dependency-free.

**Planned uses, in order.**

1. **Canvas → video/GIF**: render N frames server-side (or receive PNG frames from the
   client), pipe to `ffmpeg -f image2pipe -framerate … -i - -c:v libx264 …` (or
   `libvpx-vp9`/GIF palette pipeline for patent-clean outputs).
2. **Ingest**: extract frames/thumbnails/duration from user-dropped videos
   (`-vf select=`, `ffprobe -print_format json` for metadata).
3. **Audio**: mux background audio onto exports; loudness-normalize (`loudnorm`).

**Seam.** A `MediaToolbox` interface with `assemble_video(frames, fps, codec)`,
`probe(path)`, `extract_frames(path, times)` — implemented by an
`FfmpegSubprocessToolbox`. Executor plan steps gain a `render_video` op only when the
toolbox reports available.

---

## 3. Remotion — programmatic motion graphics (evaluate-only)

**What it would buy us.** React-defined, data-driven video: animated brand kits,
templated social clips, text animations — "design agent outputs a *motion* deliverable".
Remotion is the strongest tool in that niche, and its player/embedding story is mature.

**Why it is future-tier and possibly never.**

1. **License is not open source.** Remotion uses its own license: free only for
   individuals, non-profits, and for-profit orgs of ≤3 people. Any 4+-person company
   *using* Atelier-with-Remotion in their org — and Atelier's own maintainers/company
   once ≥4 people — needs a paid Company License ("Automators" tier for automated
   pipelines: $0.01/render, $100/month minimum; Enterprise from $500/month). Shipping
   Remotion inside Atelier would silently impose that obligation on our users. If we
   ever integrate, it must be an **explicit opt-in plugin** where the user supplies
   their own Remotion project and accepts Remotion's terms — mirroring the
   bring-your-own-ComfyUI stance, but for licensing rather than GPL reasons.
2. **It breaks zero-npm hard.** Remotion is a Node/React toolchain with a headless-
   Chromium renderer. It can only ever live in a **separate render-worker container**
   (Node + Chromium) with a tiny HTTP contract: `POST /render {composition, props} →
   mp4`. That container is user-supplied or a separately-published optional image,
   never part of the core install.
3. **Cheaper paths cover 80% of the need.** Frame-by-frame canvas rendering (we already
   own a renderer) piped into ffmpeg gives templated animations with zero new licenses.
   If a real motion-graphics DSL is wanted, **Motion Canvas (MIT)** is the
   permissively-licensed alternative to evaluate first.

**Decision.** Do not integrate Remotion now. Reassess only when (a) users demand
React-templated video specifically, and (b) canvas+ffmpeg demonstrably falls short.
Record this in the plugin roadmap as: `render-worker` HTTP contract first (works for
canvas+ffmpeg, Motion Canvas, or Remotion equally), Remotion adapter last.

---

## Sequencing

1. **Now (MVP):** hosted image providers; static exports; zero-npm canvas.
2. **Next:** ffmpeg `MediaToolbox` (subprocess; smallest lift, unlocks GIF/video export).
3. **Then:** ComfyUI `ComfyProvider` (local power-user tier; template system).
4. **Later, behind a generic render-worker contract:** Motion Canvas evaluation;
   Remotion only as user-opt-in plugin with a licensing warning in the UI.
