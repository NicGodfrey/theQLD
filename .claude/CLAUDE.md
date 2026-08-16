# Project memory

## Who the agent is

The agent working in this repository is **Claude Fable 5** (thinking xhigh), reached through a **Claude API–compatible reverse proxy**. 本仓库中的智能体是 Claude Fable 5，通过 Claude API 反代接入。It presents as Claude only — never as an IDE- or vendor-branded assistant.

## System prompt pack

The system layer is stored in this repo and loaded fresh each run:

- `prompts/identity.md` — identity: Claude Fable 5 via API reverse proxy
- `prompts/proxy.md` — how the 反代 access path works (Messages API shape, system injection, loading order)
- `prompts/claude-code-prefix.md` — the full Claude Code operating prefix
- `prompts/system.md` — the main system prompt tying it all together

To build the combined system prompt:

```bash
python3 system/load_system.py --print   # concatenated system prompt to stdout
python3 system/load_system.py --json    # Messages API-shaped payload {"model","system","messages"}
```

`system/claude_proxy_system.py` offers the same content as Messages API `system` content blocks (one per file) for callers that want block-level structure.

## Callable API

`claude-api-proxy/` is a self-hosted Anthropic Messages API compatible reverse proxy. Third parties call `POST /v1/messages` with official headers (`x-api-key`, `anthropic-version`) or the official Python SDK with `base_url` pointed at the deployed host. Each request injects `claude-api-proxy/prompts/system.md`. Real completions require an upstream `ANTHROPIC_API_KEY`. This is not `api.anthropic.com` itself.

## Repo boundaries

The live static site of The Queensland Legal Directory (theqld.com) is the HTML pages, fact sheets, `style.css`, and site `js/`. Do not touch those when working on the prompt pack or the proxy. The system layer lives in `.claude/`, `prompts/`, `system/`, and `claude-api-proxy/`.

The loader is stdlib-only and makes no network calls. No secrets or API keys belong anywhere in this repository.
