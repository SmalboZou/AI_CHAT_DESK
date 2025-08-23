#!/usr/bin/env powershell

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "AI 聊天桌面应用一键启动" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "正在启动应用..." -ForegroundColor Green

try {
    Set-Location frontend
    npm run dev
} catch {
    Write-Host "启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "请检查以下问题:" -ForegroundColor Yellow
    Write-Host "1. Node.js 和 Python 是否正确安装" -ForegroundColor White
    Write-Host "2. 依赖包是否已安装完成 (npm install)" -ForegroundColor White
    Write-Host "3. 端口 5173 和 8000 是否被占用" -ForegroundColor White
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
Read-Host