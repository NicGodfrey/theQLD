# Opus 5 MCP 完整安装（Windows 从零开始）
# 用法: 右键「使用 PowerShell 运行」，或在 PowerShell 中:
#   powershell -ExecutionPolicy Bypass -File bootstrap-windows.ps1

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/NicGodfrey/theQLD.git"
$Branch = "cursor/opus5-mcp-setup-e208"
$InstallDir = Join-Path $env:USERPROFILE "theQLD"

function Write-Title($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }
function Write-Ok($text) { Write-Host "✓ $text" -ForegroundColor Green }
function Write-Err($text) { Write-Host "✗ $text" -ForegroundColor Red }

Write-Title "Opus 5 MCP 完整安装 (Windows)"

# 检查 Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Err "未安装 Git。请先安装: https://git-scm.com/download/win"
    Read-Host "按 Enter 退出"
    exit 1
}

# 检查 Node
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Err "未安装 Node.js。请先安装 20+: https://nodejs.org"
    Read-Host "按 Enter 退出"
    exit 1
}

# 克隆或更新仓库
if (-not (Test-Path $InstallDir)) {
    Write-Title "克隆仓库到 $InstallDir"
    git clone $RepoUrl $InstallDir
} else {
    Write-Title "更新已有仓库 $InstallDir"
    Push-Location $InstallDir
    git fetch origin
    Pop-Location
}

Push-Location $InstallDir
git checkout $Branch 2>$null
if ($LASTEXITCODE -ne 0) {
    git checkout -b $Branch "origin/$Branch" 2>$null
    if ($LASTEXITCODE -ne 0) {
        git pull origin $Branch
    }
}
Pop-Location

Write-Ok "仓库就绪: $InstallDir"

# 运行项目内安装脚本
$InstallScript = Join-Path $InstallDir "deploy\install.ps1"
if (-not (Test-Path $InstallScript)) {
    Write-Err "未找到 $InstallScript"
    Read-Host "按 Enter 退出"
    exit 1
}

Write-Title "运行安装脚本"
powershell -NoProfile -ExecutionPolicy Bypass -File $InstallScript

Write-Host ""
Write-Ok "全部完成！"
Write-Host "项目目录: $InstallDir"
Read-Host "`n按 Enter 退出"
