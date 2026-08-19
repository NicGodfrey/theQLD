#!/usr/bin/env bash
# 一键部署 Opus 5 MCP 到本机（Claude Code + OpenCode）
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_ENTRY="$ROOT_DIR/opus5-mcp/dist/index.js"
ENV_FILE="$ROOT_DIR/.env.local"

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
red() { printf '\033[31m%s\033[0m\n' "$*"; }

bold "==> Opus 5 MCP 一键部署"

if ! command -v node >/dev/null 2>&1; then
  red "未找到 node。请先安装 Node.js 20+：https://nodejs.org"
  exit 1
fi

NODE_MAJOR="$(node -p "process.versions.node.split('.')[0]")"
if [ "$NODE_MAJOR" -lt 20 ]; then
  red "需要 Node.js 20+，当前: $(node -v)"
  exit 1
fi

bold "==> 构建 MCP 服务"
(cd "$ROOT_DIR/opus5-mcp" && npm install && npm run build)

if [ ! -f "$MCP_ENTRY" ]; then
  red "构建失败：未找到 $MCP_ENTRY"
  exit 1
fi

green "✓ 构建完成"

# 加载或创建 .env.local
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [ -z "${CURSOR_API_KEY:-}" ]; then
  yellow "未检测到 CURSOR_API_KEY"
  echo ""
  echo "请从 https://cursor.com/dashboard/api 创建 API Key"
  read -r -p "粘贴你的 CURSOR_API_KEY (crsr_...): " CURSOR_API_KEY_INPUT
  if [ -z "$CURSOR_API_KEY_INPUT" ]; then
    red "未提供 API Key，退出"
    exit 1
  fi
  cat > "$ENV_FILE" <<EOF
# Opus 5 MCP — 勿提交到 git
CURSOR_API_KEY=$CURSOR_API_KEY_INPUT
CURSOR_OPUS5_REPO_URL=https://github.com/NicGodfrey/theQLD
CURSOR_OPUS5_STARTING_REF=main
EOF
  chmod 600 "$ENV_FILE"
  export CURSOR_API_KEY="$CURSOR_API_KEY_INPUT"
  green "✓ 已写入 $ENV_FILE"
else
  green "✓ 已加载 CURSOR_API_KEY"
fi

bold "==> 验证 Cursor API"
if node "$ROOT_DIR/opus5-mcp/scripts/test-api.mjs" >/tmp/opus5-test.json 2>/tmp/opus5-test.err; then
  green "✓ API Key 有效"
  OPUS_MODEL="$(node -p "JSON.parse(require('fs').readFileSync('/tmp/opus5-test.json','utf8')).resolved.id" 2>/dev/null || echo unknown)"
  echo "  解析到的 Opus 模型: $OPUS_MODEL"
else
  yellow "⚠ API 验证失败（可稍后重试）:"
  cat /tmp/opus5-test.err
fi

bold "==> 注册 Claude Code MCP"
if command -v claude >/dev/null 2>&1; then
  MCP_JSON=$(cat <<EOF
{
  "type": "stdio",
  "command": "node",
  "args": ["$MCP_ENTRY"],
  "env": {
    "CURSOR_API_KEY": "\${CURSOR_API_KEY}",
    "CURSOR_OPUS5_REPO_URL": "https://github.com/NicGodfrey/theQLD",
    "CURSOR_OPUS5_STARTING_REF": "main"
  }
}
EOF
)
  if claude mcp add-json opus5 --scope project "$MCP_JSON" 2>/dev/null; then
    green "✓ 已注册 Claude Code MCP (project scope)"
  else
    yellow "⚠ claude mcp add-json 失败，项目根 .mcp.json 仍可用"
  fi
  echo "  启动 Claude Code 后输入 /mcp 批准 opus5"
else
  yellow "未找到 claude CLI，跳过。可手动使用项目根 .mcp.json"
fi

bold "==> OpenCode"
if [ -f "$ROOT_DIR/opencode.json" ]; then
  green "✓ opencode.json 已就绪"
  echo "  在项目根运行: export CURSOR_API_KEY=... && opencode"
else
  yellow "未找到 opencode.json"
fi

bold "==> Shell 自动加载（可选）"
SHELL_RC=""
case "${SHELL:-}" in
  */zsh) SHELL_RC="$HOME/.zshrc" ;;
  */bash) SHELL_RC="$HOME/.bashrc" ;;
esac

if [ -n "$SHELL_RC" ]; then
  MARKER="# opus5-mcp env"
  if ! grep -q "$MARKER" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" <<EOF

$MARKER
[ -f "$ENV_FILE" ] && set -a && . "$ENV_FILE" && set +a
EOF
    green "✓ 已追加到 $SHELL_RC（新开终端自动加载 API Key）"
  else
    echo "  $SHELL_RC 已包含 opus5 配置，跳过"
  fi
fi

echo ""
bold "部署完成 🎉"
echo ""
echo "Claude Code:"
echo "  cd $ROOT_DIR"
echo "  claude"
echo "  # 会话内输入 /mcp 批准 opus5，然后直接对话即可"
echo ""
echo "OpenCode:"
echo "  cd $ROOT_DIR && opencode"
echo ""
echo "测试:"
echo "  source $ENV_FILE && node $ROOT_DIR/opus5-mcp/scripts/test-api.mjs"
