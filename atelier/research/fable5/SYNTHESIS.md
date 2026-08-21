# Fable5 fleet synthesis

Ten extra-high agents designed Atelier/Helix in parallel. Live runtime stays in `atelier/helix/` + `atelier/web/`. This tree is the evidence pack.

## Shared conclusions

1. **Replicate the public product, not Lovart’s stack.** ChatCanvas, thinking/fast, brand kit, project/thread, and Talk/Tab/Tune have Helix names (Board, Conductor, StyleLock, Keyring). No private API, no Lovart credits.
2. **BYOK is an architectural boundary.** Keys exist only in env / `~/.atelier/keyring.json` (0600). Official hosts only (`api.openai.com`, `generativelanguage.googleapis.com`, loopback Ollama). Unofficial ChatGPT-web clients are out of scope.
3. **Board is a projection.** Intent (threads/messages) and Matter (artifacts) are the source of truth; canvas nodes can be deleted without destroying work. Next Memory: rungs + append-only triggers in `04-helix-arch/`.
4. **Conductor is staged, not a single prompt.** Fast = brief → route → weave. Thinking adds score → critique → pin. Lanes: `openai` (JSON/copy), `gemini` (see/hold), `image` (synthesis only).
5. **Media defaults moved in 2026.** OpenAI images → `gpt-image-1`. Gemini images → `gemini-2.5-flash-image`. Gemini Imagen API shut down 2026-08-17. Video stays stub-first (Veo live, Sora flagged). Demo SVG/PNG/WAV must work with zero keys.
6. **Integrate patterns, not monorepos.** LiteLLM routing/cost, Instructor JSON, Excalidraw/fabric board ideas, ComfyUI as an out-of-process worker. tldraw is source-available (production key). Open WebUI branding clause → UX only. Remotion is evaluate-only for 4+ person orgs.
7. **Catalog is live-verified.** `data/top100.live.json` dropped archived Flowise/TensorZero/openai-forward and applied org moves. Helix tests still pin `data/top100.json`.
8. **Spend is gated.** 2026-08-21 official prices, daily $10 / thread $2 defaults, keys never in API responses.

## Wiring still open

- Align live `/api/threads/:id/run` with the richer SSE Board (`06-board-ui`) and OpenAPI hub (`04-helix-arch/openapi.yaml`).
- Optionally promote fixture-tested spokes (`03-keyring-spokes`) over the thinner live adapters.
- Run `10-eval/test_helix.py` against the research fleet; live `atelier.tests.test_helix` remains the ship gate (7 tests, no keys).
