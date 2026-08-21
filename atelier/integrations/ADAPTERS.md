# OSS adapters — patterns only

| Source | What we take | What we do not vendor | License note |
|---|---|---|---|
| LiteLLM | Provider table, cost units, OpenAI-schema lingua franca | Proxy server and `enterprise/` | MIT core; do not vendor the monorepo |
| Open WebUI / LibreChat | BYOK settings, model picker | Entire chat stack | Open WebUI is BSD-3 with a branding clause — UX only, no assets |
| Instructor / Outlines | JSON plan extraction | Runtime compilers | MIT / Apache-2.0 |
| LangGraph / CrewAI | Phase + role split | Graph runtime | MIT / CC-BY |
| Excalidraw / tldraw / fabric / konva | Infinite board + drag | Frontend SDKs in MVP (vanilla JS) | tldraw is source-available and needs a production key — ideas only |
| ComfyUI / A1111 / Fooocus / Invoke | Optional local image worker | GPL/AGPL graphs in-process | Keep as out-of-process worker |
| Official OpenAI + Gemini SDKs | Endpoint contracts | SDK dependency (we use stdlib urllib) | Apache-2.0 |
| Ollama | Local chat spoke | Their daemon | MIT |
| Langfuse | Usage event shape | Their cloud | Check license |
| ATV-Design / open-design / nebula-nodes / manudesign | Proof that BYOK design studios exist | Their apps | MIT / Apache / AGPL |

## Hard no

- Unofficial ChatGPT website clients, cookie harvesters, or “free quota” reverse proxies
- Deepfake / non-consensual face-swap tools
- Shipping other people’s AGPL/GPL server inside this process (ComfyUI stays HTTP-out-of-process)
- Remotion in-tree (evaluate-only; 4+ person orgs need a paid license) — prefer a generic render-worker contract
- Full detail: `research/fable5/09-oss-adapters/`
