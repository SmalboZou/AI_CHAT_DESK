@echo off
echo ====================================
echo AI 聊天桌面应用一键启动
echo ====================================
echo.

echo 正在启动应用...
cd frontend
npm run dev

echo.
echo 应用已启动！
echo 如果遇到问题，请检查：
echo 1. Node.js 和 Python 是否正确安装
echo 2. 依赖包是否已安装完成 (npm install)
echo 3. 端口 5173 和 8000 是否被占用
echo.
pause