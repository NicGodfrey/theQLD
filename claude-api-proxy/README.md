# claude-api-proxy

把**当前这个 Cursor Cloud Agent** 用官方 Claude Messages API 的外形反代出去。

远程调用方用官方 SDK / curl 打 `POST /v1/messages`。本服务把它转成对
`CURSOR_AGENT_ID` 的 follow-up run（`POST https://api.cursor.com/v1/agents/{id}/runs`），
再把 Agent 的回复包装成官方 Claude 响应。默认打到本会话的 Cloud Agent
`bc-f222349c-ced0-4c32-9a8e-c15d699654d3`，并要求它按 Fable 5 thinking xhigh /
Claude Code 子 agent 来答。

This is not `api.anthropic.com`. Callers point `base_url` here. Completions come
from the Cursor Cloud Agent, not from a generic Anthropic key (unless you
explicitly set `ANTHROPIC_API_KEY` as a fallback backend).

## 运行 / Run

```bash
export CURSOR_API_KEY="key_from_cursor_dashboard"
export CURSOR_AGENT_ID="bc-f222349c-ced0-4c32-9a8e-c15d699654d3"  # optional, this is the default
cd claude-api-proxy
./run.sh
```

## 环境变量 / Environment

| 变量 | 说明 |
| --- | --- |
| `CURSOR_API_KEY` | Cursor Dashboard → API Keys。用来远程驱动**这个** Cloud Agent |
| `CURSOR_AGENT_ID` | 默认 `bc-f222349c-ced0-4c32-9a8e-c15d699654d3`（当前 agent） |
| `CURSOR_API_BASE` | 默认 `https://api.cursor.com` |
| `CLAUDE_PROXY_API_KEY` | 调用方放在 `x-api-key` 里的 key（默认 `sk-proxy-local`，仅限本地） |
| `ANTHROPIC_API_KEY` | 可选回退：没有 Cursor key 时才走普通 Anthropic 反代 |
| `PORT` / `HOST` | 默认 `8080` / `0.0.0.0` |

## 别人怎么调 / Official Claude style

```bash
curl https://YOUR_HOST/v1/messages \
  -H "x-api-key: $CLAUDE_PROXY_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-fable-5",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "你好，你是什么模型"}]
  }'
```

```python
from anthropic import Anthropic

client = Anthropic(api_key="YOUR_PROXY_KEY", base_url="https://YOUR_HOST")
msg = client.messages.create(
    model="claude-fable-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(msg.content[0].text)
```

同一时间一个 Agent 只能跑一个 run。代理会排队重试 `409 agent_busy`。

## 持久化部署 / Persistent deploy

Fly.io 常驻（`auto_stop_machines = "off"`，`min_machines_running = 1`）。
公网地址形如 `https://theqld-claude-api-proxy.fly.dev`。

Fly 机器只做 HTTP 门面；真正答题的是 Cursor 上的这个 Cloud Agent，不依赖本仓库所在的临时 VM。

需要的密钥：

- `CURSOR_API_KEY` — https://cursor.com/dashboard/api
- `FLY_API_TOKEN` — https://fly.io/user/personal_access_tokens
- `CLAUDE_PROXY_API_KEY` — 给远程调用方（可选，不填则部署时生成）

```bash
cd claude-api-proxy
flyctl apps create theqld-claude-api-proxy
flyctl secrets set CURSOR_API_KEY="..." CLAUDE_PROXY_API_KEY="..." CURSOR_AGENT_ID="bc-f222349c-ced0-4c32-9a8e-c15d699654d3"
flyctl deploy
```

## 测试 / Tests

```bash
python3 test_api.py
```
