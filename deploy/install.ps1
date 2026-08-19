# Opus 5 MCP 一键部署（Windows PowerShell）
# 用法: powershell -ExecutionPolicy Bypass -File deploy\install.ps1

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$McpEntry = Join-Path $RootDir "opus5-mcp\dist\index.js"
$EnvFile = Join-Path $RootDir ".env.local"

function Write-Title($text) { Write-Host "==> $text" -ForegroundColor Cyan }
function Write-Ok($text) { Write-Host "✓ $text" -ForegroundColor Green }
function Write-Warn($text) { Write-Host "⚠ $text" -ForegroundColor Yellow }
function Write-Err($text) { Write-Host "✗ $text" -ForegroundColor Red }

Write-Title "Opus 5 MCP 一键部署 (Windows)"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Err "未找到 node。请先安装 Node.js 20+: https://nodejs.org"
    exit 1
}

$nodeMajor = [int](node -p "process.versions.node.split('.')[0]")
if ($nodeMajor -lt 20) {
    Write-Err "需要 Node.js 20+，当前: $(node -v)"
    exit 1
}

Write-Title "构建 MCP 服务"
Push-Location (Join-Path $RootDir "opus5-mcp")
npm install
npm run build
Pop-Location

if (-not (Test-Path $McpEntry)) {
    Write-Err "构建失败：未找到 $McpEntry"
    exit 1
}
Write-Ok "构建完成"

# 加载 .env.local
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

if (-not $env:CURSOR_API_KEY) {
    Write-Warn "未检测到 CURSOR_API_KEY"
    Write-Host ""
    Write-Host "请从 https://cursor.com/dashboard/api 创建 API Key"
    $key = Read-Host "粘贴你的 CURSOR_API_KEY (crsr_...)"
    if (-not $key) {
        Write-Err "未提供 API Key，退出"
        exit 1
    }
    @"
# Opus 5 MCP — 勿提交到 git
CURSOR_API_KEY=$key
CURSOR_OPUS5_REPO_URL=https://github.com/NicGodfrey/theQLD
CURSOR_OPUS5_STARTING_REF=main
"@ | Set-Content -Path $EnvFile -Encoding UTF8
    $env:CURSOR_API_KEY = $key
    Write-Ok "已写入 $EnvFile"
} else {
    Write-Ok "已加载 CURSOR_API_KEY"
}

Write-Title "验证 Cursor API"
$testScript = Join-Path $RootDir "opus5-mcp\scripts\test-api.mjs"
try {
    $testOut = node $testScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "API Key 有效"
        Write-Host $testOut
    } else {
        Write-Warn "API 验证失败: $testOut"
    }
} catch {
    Write-Warn "API 验证跳过: $_"
}

Write-Title "Claude Code MCP 配置"
$claudeJson = @{
    mcpServers = @{
        opus5 = @{
            type = "stdio"
            command = "node"
            args = @($McpEntry)
            env = @{
                CURSOR_API_KEY = '${CURSOR_API_KEY}'
                CURSOR_OPUS5_REPO_URL = "https://github.com/NicGodfrey/theQLD"
                CURSOR_OPUS5_STARTING_REF = "main"
            }
        }
    }
} | ConvertTo-Json -Depth 6

$mcpJsonPath = Join-Path $RootDir ".mcp.json"
$claudeJson | Set-Content -Path $mcpJsonPath -Encoding UTF8
Write-Ok "已更新 $mcpJsonPath"

if (Get-Command claude -ErrorAction SilentlyContinue) {
    $serverJson = @{
        type = "stdio"
        command = "node"
        args = @($McpEntry)
        env = @{
            CURSOR_API_KEY = '${CURSOR_API_KEY}'
            CURSOR_OPUS5_REPO_URL = "https://github.com/NicGodfrey/theQLD"
            CURSOR_OPUS5_STARTING_REF = "main"
        }
    } | ConvertTo-Json -Depth 6 -Compress

    try {
        claude mcp add-json opus5 --scope project $serverJson 2>$null
        Write-Ok "已注册 Claude Code MCP (project scope)"
    } catch {
        Write-Warn "claude mcp add-json 失败，请手动使用 .mcp.json"
    }
    Write-Host "  启动 Claude Code 后输入 /mcp 批准 opus5"
} else {
    Write-Warn "未找到 claude CLI。安装 Claude Code 后，在项目根运行 claude"
}

Write-Title "设置用户环境变量（当前用户）"
[Environment]::SetEnvironmentVariable("CURSOR_API_KEY", $env:CURSOR_API_KEY, "User")
Write-Ok "已设置用户环境变量 CURSOR_API_KEY（新开的终端生效）"

Write-Host ""
Write-Title "部署完成"
Write-Host ""
Write-Host "下一步:"
Write-Host "  cd $RootDir"
Write-Host "  claude"
Write-Host "  # 会话内输入 /mcp 批准 opus5"
Write-Host ""
Write-Host "OpenCode:"
Write-Host "  cd $RootDir"
Write-Host "  opencode"
