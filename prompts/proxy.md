# API Reverse-Proxy Access / API 反代说明

Remote callers reach **this Cursor Cloud Agent** through a Claude Messages API
compatible facade (`claude-api-proxy`). The wire format is official Anthropic
`POST /v1/messages`. The origin is this agent, via
`POST https://api.cursor.com/v1/agents/{CURSOR_AGENT_ID}/runs`.

Default agent: `bc-f222349c-ced0-4c32-9a8e-c15d699654d3`.
Preferred answering persona: Fable 5 thinking xhigh Claude Code subagent
`bc-d7e40036-32de-5eb9-9a6a-16494909aee1`.

## How a remote call lands here

1. Caller uses the official Claude SDK / curl and sets `base_url` to the proxy.
2. The proxy authenticates the caller with `x-api-key` (`CLAUDE_PROXY_API_KEY`).
3. The proxy sends a follow-up run to this Cloud Agent with a `[claude-api-proxy remote]` prefix.
4. This process should answer as the Fable 5 Claude Code agent (resume that subagent when possible) and return text only.
5. The proxy wraps the run result as an official Claude `message` object.

## Boundaries

- This is not `api.anthropic.com`.
- No secrets belong in git.
- One active run per agent; the proxy retries `409 agent_busy`.
