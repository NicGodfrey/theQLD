# Fable5 research drops

Isolated reports from the ten Fable 5 extra-high sub-agents. Helix runtime code stays in `atelier/helix/`; these files are evidence, not a second implementation.

Completed and copied:

- `01-product-spec/` — Lovart public feature matrix, UX flows, acceptance
- `02-top100/` — live GitHub GraphQL TOP100, MVP 15, Helix integration map
- `03-keyring-spokes/` — BYOK contract, official-host lock, 68 fixture tests, Anthropic/Ollama/compat spokes
- `04-helix-arch/` — Memory invariants, OpenAPI hub, content-addressed store prototype
- `08-security-quota/` — threat model, keyring notes, 2026-08-21 cost table
- `05-conductor/` — plan/critique/manifest protocol, three-lane routing, 36 offline tests
- `06-board-ui/` — vanilla infinite canvas + demo/live backends (expects SSE `/api/chat`; not swapped over the live Helix `/api/threads/:id/run` UI yet)
- `07-loom/` — official-API media pipelines, demo kit, Veo/Sora stubs (Imagen Gemini API shut down 2026-08-17)
- `09-oss-adapters/` — license-aware pattern map, Comfy/ffmpeg/Remotion future, zero-npm stubs

Other workstreams are still landing under `/tmp/atelier-fable/`.
