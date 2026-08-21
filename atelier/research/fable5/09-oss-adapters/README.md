# 09-oss-adapters — OSS integration strategy for Atelier

Produced by Fable5#9. Contents:

- **[ADAPTERS.md](ADAPTERS.md)** — per upstream project (LiteLLM, tldraw,
  excalidraw, ComfyUI, fabric.js/konva, Open WebUI, Instructor/Outlines): the
  pattern we take, what we explicitly do not vendor, the verified license, and
  the code seam it maps to. Opens with cross-cutting rules (process boundary for
  GPL, ideas-only for non-OSI licenses, zero-npm MVP policy).
- **[FUTURE.md](FUTURE.md)** — post-MVP workers: ComfyUI local generation
  worker, ffmpeg media toolbox, Remotion (evaluate-only, licensing caveats,
  Motion Canvas as the permissive alternative).
- **stubs/python/** — stdlib-only adapter seams:
  - `llm_gateway.py` — Provider protocol + OpenAI-compatible client + Router
    (fallbacks, retries, cooldowns, cost hook). LiteLLM patterns, no dependency.
  - `plan_schema.py` — plan JSON schema, stdlib validator, `extract_plan()`
    fallback ladder with Instructor-style validation-error-feedback retries.
  - `comfy_client.py` — ComfyUI HTTP job client (queue/poll/fetch/interrupt)
    plus workflow-template placeholder filling. GPL-safe: no ComfyUI code.
- **stubs/js/** — zero-npm ES modules (no package.json, no bundler):
  - `store.js` — tldraw-inspired record store: change-set listeners,
    inverse-patch undo/redo, JSON persistence.
  - `scene.js` — excalidraw-inspired element schema: version/versionNonce LWW
    merge, tombstones, fractional-index z-order, scene file format.
  - `renderer.js` — konva/fabric-inspired: multi-canvas layers, batchDraw,
    color-buffer hit testing, drawer dispatch table.

Verification: `python3 stubs/python/plan_schema.py` and
`python3 stubs/python/comfy_client.py` run offline self-tests; JS modules are
syntax-checked with `node --check` (renderer requires a DOM, so it is
parse-checked only).
