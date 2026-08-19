# Opus 5 远程中转架构

物理电脑 → **你的中转网站** → Cursor Cloud Agents API (Opus 5)

```
┌─────────────────┐     HTTPS + Bearer Token      ┌──────────────────┐
│  物理电脑 B      │  ───────────────────────────► │  opus5-relay     │
│  Claude Code    │                               │  (你的 VPS/云)    │
│  或浏览器        │  ◄───────────────────────────  │  持有 CURSOR_KEY │
└─────────────────┘         JSON / Web UI          └────────┬─────────┘
                                                             │
                                                             ▼
                                                  Cursor Cloud Agents API
                                                  (Claude Opus 5)
```

**安全原则**
- `CURSOR_API_KEY` 只放在中转服务器
- 物理电脑只持有 `RELAY_AUTH_TOKEN`（可轮换、可限流）

---

## 一、在中转服务器部署 relay

### 方式 A：Docker（推荐）

```bash
cd opus5-relay
cp .env.example .env
# 编辑 .env：填入 CURSOR_API_KEY 和 RELAY_AUTH_TOKEN

docker compose up -d --build
```

默认端口 `8787`。前面加 Nginx/Caddy 做 HTTPS。

### 方式 B：裸机 Node

```bash
cd opus5-relay
cp .env.example .env
# 编辑 .env
npm install && npm run build
npm start
```

### .env 必填项

```env
CURSOR_API_KEY=crsr_xxx
RELAY_AUTH_TOKEN=请用 openssl rand -hex 32 生成
PORT=8787
```

---

## 二、HTTPS 反向代理（示例 Caddy）

```
your-relay.example.com {
    reverse_proxy localhost:8787
}
```

---

## 三、物理电脑调用

### 方式 1：浏览器

打开 `https://your-relay.example.com/`，输入 `RELAY_AUTH_TOKEN` 即可对话。

### 方式 2：curl

```bash
curl -X POST https://your-relay.example.com/api/v1/ask \
  -H "Authorization: Bearer 你的RELAY令牌" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"你好，你是谁？\"}"
```

返回：

```json
{
  "session_id": "uuid",
  "reply": "Opus 5 的回复…",
  "agent_id": "bc-...",
  "agent_url": "https://cursor.com/agents/bc-..."
}
```

后续对话带上同一 `session_id` 即可续接。

### 方式 3：Claude Code（推荐）

在物理电脑上：

```bash
cd opus5-mcp-remote
npm install && npm run build
```

`.mcp.json`：

```json
{
  "mcpServers": {
    "opus5-remote": {
      "type": "stdio",
      "command": "node",
      "args": ["C:/path/to/opus5-mcp-remote/dist/index.js"],
      "env": {
        "OPUS5_RELAY_URL": "https://your-relay.example.com",
        "OPUS5_RELAY_TOKEN": "你的RELAY令牌"
      }
    }
  }
}
```

然后 `claude` → `/mcp` 批准 `opus5-remote`。

---

## API 参考

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查（无需鉴权） |
| POST | `/api/v1/ask` | 发送消息 |
| GET | `/api/v1/session/:id` | 查看会话 |
| POST | `/api/v1/reset` | 重置会话 |

`POST /api/v1/ask` body：

```json
{
  "message": "你的问题",
  "session_id": "可选，续接对话",
  "reset": false,
  "repo_url": "可选 GitHub 仓库"
}
```

---

## 与本地直连方案对比

| | 本地 opus5-mcp | 中转 relay |
|--|----------------|------------|
| API Key 位置 | 本机 | 服务器 |
| 多设备共享 | 每台都要 Key | 只发 RELAY 令牌 |
| 延迟 | 较低 | + 中转一跳 |
| 适合 | 单台开发机 | 多台物理机 / 团队 |
