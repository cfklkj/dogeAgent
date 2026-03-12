@echo off
echo ========================================
echo 重启 dogeAgent 并测试币圈功能
echo ========================================
echo.

REM 停止现有进程（如果有）
echo [1/3] 停止现有进程...
taskkill /F /IM electron.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

REM 启动应用
echo [2/3] 启动 dogeAgent...
cd /d "%~dp0"
start npm start

echo [3/3] 等待 5 秒启动...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 启动完成！请在聊天框输入测试：
echo   - BTC 什么价格
echo   - 分析 ETH 走势
echo   - DOGE 价格
echo ========================================
