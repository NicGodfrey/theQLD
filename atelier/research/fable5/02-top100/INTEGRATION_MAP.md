# INTEGRATION_MAP — MVP 15 → Helix Modules

How each of the 15 MVP repos from [`TOP100.md`](./TOP100.md) wires into Helix's six modules:

- **keyring** — BYOK credential vault, provider registry, budgets/quota
- **spokes** — pluggable generation/processing services (image, audio, video, brand)
- **conductor** — agent orchestration: plans jobs, calls spokes, requests approval
- **board** — the infinite canvas UI where humans and agents co-work
- **loom** — composition layer: weaves generated assets into deliverables (pipelines, templates, exports)
- **memory** — project/brand context: retrieval over guidelines, history, asset metadata

Cross-cutting: **observability** feeds cost/trace data back into keyring quotas and board UI.

```
        ┌─────────────────────────── board (tldraw + vercel/ai) ───────────────────────────┐
        │   canvas shapes · streaming agent UI · voice input (whisper.cpp, in-browser)     │
        └───────▲──────────────────────────────────────────────────────────▲───────────────┘
                │ interrupts/approvals                            streamed │ tool-calls
        ┌───────┴────────── conductor (langgraph + pydantic-ai) ───────────┴───────────────┐
        │   job graphs · typed artifacts · spoke dispatch · memory reads (llama_index)     │
        └───▲────────────────────────────┬─────────────────────────────────────▲──────────┘
            │ model calls                │ spoke calls (HTTP)                   │ context
   ┌────────┴─────────┐    ┌─────────────┴──────────────────────────┐   ┌──────┴──────────┐
   │ keyring (litellm)│    │ spokes: comfyui · rembg · real-esrgan  │   │ memory          │
   │ BYOK vault+proxy │    │         f5-tts · satori                │   │ (llama_index)   │
   └────────┬─────────┘    └─────────────┬──────────────────────────┘   └─────────────────┘
            │                            │ assets
            │              ┌─────────────▼──────────────────────────┐
            │              │ loom (xyflow editor + remotion render) │
            │              └────────────────────────────────────────┘
            └───────────► observability (langfuse): traces, cost-per-canvas, quota signals
```

---

## keyring

### BerriAI/litellm — the vault's engine
- **Deployment:** LiteLLM proxy as a sidecar container; Helix keyring UI writes provider configs to its DB. User keys encrypted at rest (envelope encryption, per-user DEK — copy LibreChat's pattern, see TOP100 #38).
- **Provider registry:** `openai/*`, `gemini/*`, `anthropic/*`, `ollama/*` (localhost, key-free), plus any `openai_compatible/*` base-URL the user adds. Each maps to one keyring entry with model allow-lists.
- **Quota:** LiteLLM *virtual keys* per workspace: max budget, TPM/RPM limits, model restrictions. Keyring exposes budget state; board renders remaining spend.
- **Contract upward:** everything above the keyring speaks the OpenAI dialect to `http://keyring:4000/v1`; no other module ever touches a raw user key.

### langfuse/langfuse — the meter on the vault (cross-cutting)
- **Deployment:** self-hosted Langfuse (web + worker + ClickHouse/Postgres).
- **Wiring:** LiteLLM's built-in Langfuse callback (success + failure) tags every call with `workspace_id`, `canvas_id`, `job_id`; LangGraph steps traced via the Langfuse SDK so a design job appears as one nested trace.
- **Quota loop:** nightly (or streaming) rollup of Langfuse cost data feeds keyring budget alerts; board shows per-canvas $ badges from the same source.

## conductor

### langchain-ai/langgraph — the job runtime
- **Shape:** one graph per deliverable type. Example `poster_v1`: `intake_brief → retrieve_brand(memory) → concept_options → [interrupt: human picks] → generate(comfyui) → cutout(rembg) → typography_pass(qwen-image via comfyui) → upscale(real-esrgan) → export(loom)`.
- **Durability:** Postgres checkpointer; every node checkpoint stores the artifact manifest, so jobs resume after crashes and users can rewind to any step from the board.
- **Interrupts:** LangGraph `interrupt()` at taste-gates; the board surfaces these as approval cards pinned to the canvas.
- **Model access:** all LLM nodes call the keyring endpoint; model choice per node comes from a routing table (e.g. concepting → user's best creative model; JSON-emitting nodes → cheapest structured-output model).

### pydantic/pydantic-ai — the type system of creativity
- **Artifacts as schemas:** `DesignBrief`, `BrandKit`, `LayerSpec`, `CompfyWorkflowPatch`, `AssetManifest`, `RenderProps` (the JSON handed to Remotion) are Pydantic models; conductor nodes use pydantic-ai agents to guarantee valid structures regardless of which BYOK model produced them.
- **Retry semantics:** validation failure → automatic reprompt with error feedback, before anything reaches a spoke.

## spokes

Common contract: each spoke is a container exposing `POST /jobs` (async, idempotency-key), `GET /jobs/:id`, artifacts to shared object storage (S3/MinIO), plus a manifest (`spoke.yaml`) declaring capabilities, GPU needs and license class. Conductor discovers spokes from the manifest registry. GPL/AGPL tools stay process-isolated behind HTTP — never linked in.

### Comfy-Org/ComfyUI — generation engine (image now, video next)
- **Integration:** headless `--listen` instance; Helix ships versioned workflow-JSON templates (FLUX for hero images, Qwen-Image for text-heavy posters). Conductor patches template parameters (`CompfyWorkflowPatch`) and submits via `/prompt`, tracking progress over WebSocket; queue events stream to board progress bars.
- **BYOK note:** ComfyUI covers *local/self-hosted GPU* generation; when the user has no GPU, the same conductor node falls back to their image-capable API models through the keyring (e.g. `gpt-image-1`, Gemini image out).
- **License handling:** GPL-3.0 — separate container, HTTP only.

### danielgatis/rembg — cutout service
- `rembg s` Docker service; conductor calls it after any generation that will be layered on the canvas. Output: transparent PNG + alpha-matte layer added to the tldraw shape as separate asset.

### xinntao/Real-ESRGAN — upscale service
- Thin FastAPI wrapper around realesrgan-ncnn (CPU-capable) with 2x/4x models; invoked only at export time (loom stage) so working-canvas assets stay light.

### SWivid/F5-TTS — voice service
- Container exposing `POST /tts {text, ref_audio?, ref_text?}`; brand kits may pin a cloned brand voice (ref sample stored in memory module). Used by loom for video voiceovers and by board for audio-preview nodes.

### vercel/satori — brand-asset renderer
- Node service: `POST /render {template_id, tokens, props}` → SVG (+ sharp → PNG). Templates are JSX files versioned in the workspace; brand tokens come from the memory module's `BrandKit`. This is the deterministic fast path: no diffusion, no GPU, pixel-identical re-renders when copy changes.

## board

### tldraw/tldraw — the canvas
- **Custom shapes:** `AssetShape` (generated image/video/audio with provenance + trace link), `GenNodeShape` (parameterized generator the user can re-run), `ApprovalCard` (LangGraph interrupt surfaced), `BoardFrame` (deliverable-sized artboards).
- **Sync:** tldraw sync server for multiplayer; agent edits arrive as just another presence, so users watch the agent arrange the canvas live.
- **Provenance:** every AssetShape stores `job_id`/`trace_id` → click-through to the Langfuse trace ("why does this cost $0.42?").

### vercel/ai — the board's nervous system
- `streamText`/`streamUI` against the keyring endpoint for the chat/command rail; tool-call streaming renders agent actions as canvas mutations in real time. Provider registry mirrors keyring entries so the model picker is BYOK-aware.

### ggml-org/whisper.cpp — voice input
- WASM build in-browser for short utterances ("make the sky more teal"); server container for long voice-brief transcription. Zero API cost, zero key exposure — pure local-first.

## loom

### xyflow/xyflow — the visible pipeline
- Every conductor graph renders as an editable React Flow graph: nodes = spokes/models, edges = artifact flow. Users rewire (swap FLUX → Qwen-Image, insert an upscale node) and save as workspace templates. Loom compiles the graph back to a LangGraph definition + ComfyUI patches.

### remotion-dev/remotion — the video weaver
- Brand-video templates (intro/outro/lower-thirds/social cuts) as Remotion compositions; conductor's `RenderProps` (validated by pydantic-ai) fully parameterize them. Renders run in a worker (`@remotion/renderer`), pulling F5-TTS voiceover and ComfyUI stills/clips from object storage, emitting MP4/WebM to the canvas.
- **License:** company license required past 3 employees — flag in deploy docs.

### vercel/satori + Real-ESRGAN (shared with spokes)
- Loom's export stage: static deliverables render through satori (vector) or are upscaled via Real-ESRGAN (raster) before packaging (ZIP with structured `AssetManifest`).

## memory

### run-llama/llama_index — the studio's long-term taste
- **Indexes per workspace:** (1) brand corpus — guidelines PDFs, tone-of-voice docs, approved assets with structured `BrandKit` extraction; (2) project history — briefs, chosen concepts, rejection reasons; (3) asset metadata — prompt, seed, model, palette per artifact.
- **Wiring:** conductor's `retrieve_brand` node queries these indexes; embeddings/LLM calls go through the keyring like everything else (user's cheap embedding model). Storage: Postgres + pgvector to keep the stack at one database.
- **Feedback loop:** every human approval/rejection at an interrupt is written back as a preference record — the studio gets more on-brand over time.

---

## Boot order for an MVP build

1. **keyring**: LiteLLM proxy + Langfuse callbacks + key-vault UI (test: OpenAI, Gemini, Ollama keys all serve `/v1/chat/completions`).
2. **board skeleton**: tldraw canvas + vercel/ai chat rail against keyring (no spokes yet — text-only design critique already works).
3. **conductor v0**: one LangGraph (`poster_v1`) + pydantic-ai schemas + one interrupt.
4. **first spokes**: ComfyUI (FLUX template) + rembg; assets land as AssetShapes.
5. **loom v0**: satori brand-card templates + Real-ESRGAN export; xyflow read-only pipeline view.
6. **memory v0**: llama_index brand corpus + retrieve_brand node.
7. **close the loop**: Langfuse cost-per-canvas badges; F5-TTS + Remotion for the first video deliverable; xyflow editing.
