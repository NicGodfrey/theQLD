# OSS adapters — patterns only

| Source | What we take | What we do not vendor | License note |
|---|---|---|---|
| LiteLLM | Provider table, cost units | Proxy server | Check their license before copying code |
| Open WebUI / LibreChat | BYOK settings, model picker | Entire chat stack | Various |
| Instructor / Outlines | JSON plan extraction | Runtime compilers | MIT / Apache-2.0 |
| LangGraph / CrewAI | Phase + role split | Graph runtime | MIT / CC-BY |
| Excalidraw / tldraw / fabric / konva | Infinite board + drag | Frontend SDKs in MVP (vanilla JS) | Mixed; tldraw is source-available |
| ComfyUI / A1111 / Fooocus / Invoke | Optional local image worker | GPL/AGPL graphs in-process | Keep as out-of-process worker |
| Official OpenAI + Gemini SDKs | Endpoint contracts | SDK dependency (we use stdlib urllib) | Apache-2.0 |
| Ollama | Local chat spoke | Their daemon | MIT |
| Langfuse | Usage event shape | Their cloud | Check license |
| ATV-Design / open-design / nebula-nodes / manudesign | Proof that BYOK design studios exist | Their apps | MIT / Apache / AGPL |

## Hard no

- Unofficial ChatGPT website clients, cookie harvesters, or “free quota” reverse proxies
- Deepfake / non-consensual face-swap tools
- Shipping other people’s AGPL server inside this process
