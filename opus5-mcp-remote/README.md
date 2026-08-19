# Opus 5 MCP Remote Client

物理电脑通过**中转站**调用 Opus 5，无需在本机保存 Cursor API Key。

## 配置

```powershell
cd opus5-mcp-remote
npm install
npm run build

$env:OPUS5_RELAY_URL = "https://your-relay.example.com"
$env:OPUS5_RELAY_TOKEN = "你的RELAY令牌"
```

## Claude Code

复制 `.mcp.remote.example.json` 为 `.mcp.json`，修改 URL 和令牌路径，然后：

```powershell
claude
# /mcp 批准 opus5-remote
```

## 测试（不用 Claude Code）

```powershell
$body = @{ message = "你好" } | ConvertTo-Json
Invoke-RestMethod -Uri "$env:OPUS5_RELAY_URL/api/v1/ask" `
  -Method POST `
  -Headers @{ Authorization = "Bearer $env:OPUS5_RELAY_TOKEN" } `
  -ContentType "application/json" `
  -Body $body
```
