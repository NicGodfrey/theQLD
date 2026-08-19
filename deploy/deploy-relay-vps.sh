#!/usr/bin/env bash
# 在 Linux VPS 上部署 opus5-relay
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/opus5-relay"

if [ ! -f .env ]; then
  cp .env.example .env
  TOKEN="$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p)"
  echo ""
  echo "已创建 .env，请编辑填入 CURSOR_API_KEY"
  echo "建议 RELAY_AUTH_TOKEN=$TOKEN"
  echo ""
  read -r -p "按 Enter 继续编辑 .env …"
  ${EDITOR:-nano} .env
fi

if command -v docker >/dev/null 2>&1; then
  docker compose up -d --build
  echo "✓ relay 已启动: http://$(hostname -I | awk '{print $1}'):8787"
else
  npm install && npm run build
  nohup npm start > relay.log 2>&1 &
  echo "✓ relay 已后台启动，日志 relay.log"
fi
