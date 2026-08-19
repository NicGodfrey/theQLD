#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/opus5-mcp"

npm install
npm run build

echo ""
echo "Opus 5 MCP 已构建完成。"
echo ""
echo "下一步："
echo "  1. export CURSOR_API_KEY=crsr_你的密钥"
echo "  2. Claude Code: 在项目根目录运行 claude，输入 /mcp 批准 opus5"
echo "  3. OpenCode: 在项目根目录运行 opencode（已读取 opencode.json）"
echo ""
echo "测试 API Key："
echo "  CURSOR_API_KEY=\$CURSOR_API_KEY node opus5-mcp/scripts/test-api.mjs"
