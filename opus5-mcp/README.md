# Opus 5 MCP

通过 [Cursor Cloud Agents API](https://cursor.com/docs/cloud-agent/api/endpoints) 远程调用 **Claude Opus 5**（主模型人设），可在 **Claude Code** 与 **OpenCode** 中作为 MCP 工具使用。

## 前置条件

1. 在 [Cursor Dashboard → API Keys](https://cursor.com/dashboard/api) 创建 API Key（`crsr_...`）
2. Node.js 20+

## 一键部署（推荐）

在项目根目录运行：

```bash
./deploy/install.sh
```

脚本会自动：构建 MCP、验证 API Key、注册 Claude Code MCP、配置 shell 环境。

## 手动安装

```bash
cd opus5-mcp
npm install
npm run build
```

## 环境变量

复制示例并填入你的 Key：

```bash
cp opus5-mcp/.env.example opus5-mcp/.env
export CURSOR_API_KEY=crsr_xxx
```

| 变量 | 必填 | 说明 |
|------|------|------|
| `CURSOR_API_KEY` | 是 | Cursor API Key |
| `CURSOR_OPUS5_MODEL_ID` | 否 | 手动指定模型 ID |
| `CURSOR_OPUS5_MODEL_PARAMS` | 否 | JSON 数组，如 `[{"id":"reasoning","value":"high"}]` |
| `CURSOR_OPUS5_AGENT_ID` | 否 | 复用已有 agent |
| `CURSOR_OPUS5_REPO_URL` | 否 | 创建 agent 时绑定的 GitHub 仓库 |
| `CURSOR_OPUS5_STARTING_REF` | 否 | 分支或 commit，默认 `main` |

## Claude Code 配置

项目根目录已包含 `.mcp.json`。先设置环境变量，再批准 MCP：

```bash
export CURSOR_API_KEY=crsr_xxx

# 方式 1：使用项目配置（推荐）
cd /path/to/theQLD
claude mcp list

# 方式 2：CLI 手动添加
claude mcp add opus5 --scope project -- node opus5-mcp/dist/index.js
```

在 Claude Code 会话中输入 `/mcp` 批准 `opus5` 服务器。

**使用示例（在 Claude Code 里自然语言即可）：**

> 用 ask_opus5 工具问 Opus 5：帮我审查 legalDirectory.html 的架构

## OpenCode 配置

项目根目录已包含 `opencode.json`：

```bash
export CURSOR_API_KEY=crsr_xxx
opencode
```

或在 OpenCode 中：

```bash
opencode mcp add
# 名称: opus5
# 类型: local
# 命令: node opus5-mcp/dist/index.js
```

## MCP 工具

| 工具 | 说明 |
|------|------|
| `ask_opus5` | 发送消息给 Opus 5 并等待完整回复 |
| `opus5_status` | 查看当前持久化 agent 会话 |
| `opus5_reset` | 清除本地会话 ID，下次创建新 agent |
| `opus5_list_models` | 列出可用模型（排查 model id） |

### ask_opus5 参数

```json
{
  "message": "你好，你是谁？",
  "reset": false,
  "repo_url": "https://github.com/NicGodfrey/theQLD",
  "starting_ref": "main"
}
```

## 本地测试

```bash
export CURSOR_API_KEY=crsr_xxx
npm run build --prefix opus5-mcp
node opus5-mcp/scripts/smoke-test.mjs
```

## 说明

- 这是 **Cursor Cloud Agent** 调用，不是 Anthropic 直连 API
- Opus 5 按 Cursor 用量计费（Other Models 池）
- 会话 ID 保存在 `~/.config/opus5-mcp/state.json`
- 同一 agent 同时只能有一个 run；忙时返回错误，可稍后重试或 `reset: true`
