# 启动后端服务（PowerShell 脚本）
# 用法：在项目根目录执行  powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
# 也可以直接双击 scripts\start_backend.bat

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "项目目录：$root" -ForegroundColor Cyan

$python = "python"
if (Test-Path "$root\.venv\Scripts\python.exe") {
    $python = "$root\.venv\Scripts\python.exe"
}

# 依赖检查（ultralytics 未安装时，backend/config.py 会自动回退到 third_party 内置版本）
& $python -c "import flask, torch, PIL" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "缺少依赖，正在安装 requirements.txt ..." -ForegroundColor Yellow
    & $python -m pip install -r "$root\requirements.txt"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖安装失败，请手动执行：pip install -r requirements.txt" -ForegroundColor Red
        exit 1
    }
}

Write-Host "启动服务：http://127.0.0.1:5000" -ForegroundColor Green
& $python "$root\backend\app.py"
