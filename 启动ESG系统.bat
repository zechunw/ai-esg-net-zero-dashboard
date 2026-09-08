@echo off
chcp 65001 >nul
title ESG 净零契合度评估系统
color 0A

echo ==========================================
echo    ESG 净零契合度评估系统
echo    正在启动...
echo ==========================================
echo.

REM 进入项目目录
cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Python版本:
python --version
echo.

REM 检查并安装依赖
echo [2/3] 检查依赖...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖，请稍候...
    python -m pip install flask flask-cors requests beautifulsoup4 lxml pandas numpy python-dotenv python-dateutil reportlab openpyxl -q
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo 依赖安装完成！
) else (
    echo 依赖已安装，跳过
)
echo.

REM 创建必要目录
echo [3/3] 检查目录结构...
if not exist "reports" mkdir reports
if not exist "data" mkdir data
echo 目录检查完成！
echo.

echo ==========================================
echo    启动成功！
echo    请在浏览器中访问:
echo    http://localhost:5000
echo ==========================================
echo.
echo 按 Ctrl+C 停止服务器
echo.

REM 启动Flask应用
python app.py

pause
