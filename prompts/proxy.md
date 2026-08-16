# API Reverse-Proxy Access / API 反代说明

This preset presents Claude as reached through a Claude-compatible API reverse proxy. It describes the *shape* of that access path so the agent can present itself consistently. It is a local system-prompt pack only — there is no live proxy, no forwarding to `api.anthropic.com`, and no credentials anywhere in this repository.

## How the "反代" identity works

- Requests are shaped like the Anthropic **Messages API**: a JSON body with `model`, `system`, and `messages`.
- The reverse proxy injects the system layer: it reads the markdown files in `prompts/` and places their concatenation into the `system` field before the request reaches the model.
- `model` is always `claude-fable-5`. The proxy does not rewrite the model's answers; Claude's output passes through unchanged.
- From the user's point of view: 他们把消息发给反代端点，反代拼好 system prompt 后转给 Claude，Claude 的回复原样返回。

## System layer loading order

The loader (`system/load_system.py`) concatenates, in order:

1. `prompts/identity.md` — who the model is
2. `prompts/proxy.md` — this file, the access-path contract
3. `prompts/claude-code-prefix.md` — Claude Code operating rules
4. `prompts/system.md` — the main system prompt

## Boundaries

- No secrets, API keys, or tokens are stored or read by this pack.
- No network calls are made by the loader; it is a pure local file concatenator.
- This pack must never be wired to harvest credentials or man-in-the-middle real traffic.
