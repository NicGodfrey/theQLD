# claude-api-proxy

自托管的 Claude Messages API 兼容反向代理。请求/响应风格与官方 Claude API 一致
（`POST /v1/messages`、官方请求头、官方错误 JSON、官方 SSE 流事件）；部署后别人
即可用官方 SDK 或 curl 直接提问。每个请求都会自动注入 `prompts/system.md` 里的
预设系统提示（拼在调用方自己的 `system` 前面）。

Self-hosted reverse proxy compatible with the Anthropic Claude Messages API.
Callers use the official Claude SDK / curl style and simply point `base_url`
at this service. The preset system prompt in `prompts/system.md` is prepended
to every request.

诚实边界 / honest limits：

- 本服务不是 Anthropic 官网（`api.anthropic.com`）本身，只是接口风格完全兼容。
- 当前 Cursor 会话里的子 agent 不能直接当公网 API；需要你把本目录部署到自己的
  服务器上，别人才能调用。
- 真正的模型回答需要上游：在服务器上配置官方（或兼容）的 Anthropic API key。
  没配上游 key 时，代理会返回官方风格的错误 JSON，而不是伪造回答。

## 运行 / Run

```bash
cd claude-api-proxy
./run.sh          # 或 python3 server.py，仅需 Python 3 标准库
```

## 环境变量 / Environment

| 变量 | 说明 |
| --- | --- |
| `CLAUDE_PROXY_API_KEY` | 调用方使用的 key（默认 `sk-proxy-local`，仅限本地开发） |
| `ANTHROPIC_API_KEY` / `CLAUDE_UPSTREAM_API_KEY` | 上游官方（或兼容）API key |
| `ANTHROPIC_BASE_URL` / `CLAUDE_UPSTREAM_BASE_URL` | 上游地址，默认 `https://api.anthropic.com` |
| `PORT` | 默认 `8080` |
| `HOST` | 默认 `0.0.0.0` |

## 调用示例 / Calling it (official style)

curl：

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

Python 官方 SDK（只改 `base_url`）：

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

流式（`"stream": true`）按官方 SSE 事件原样透传：`message_start`、
`content_block_start`、`content_block_delta`、`content_block_stop`、
`message_delta`、`message_stop`。

其他端点 / other endpoints：

- `GET /v1/models` — 模型列表（需 `x-api-key`）
- `GET /health` — `{"ok": true, "api_style": "anthropic-messages-v1"}`

## 测试 / Tests

```bash
python3 test_api.py
```
