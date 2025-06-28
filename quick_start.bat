@echo off
chcp 65001 >nul
echo 🚀 AI聊天系统快速启动脚本
echo ==========================================

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先运行安装脚本: setup_deepseek.bat 或 setup_ollama.bat
    pause
    exit /b 1
)

:: 检查依赖
echo 🔍 检查依赖包...
python -c "import fastapi, uvicorn, openai, requests, pyyaml" >nul 2>&1
if errorlevel 1 (
    echo ❌ 依赖包未安装
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
)

:: 检查运行模式
echo.
echo 🔍 检测运行模式...
set ONLINE_MODE=false

:: 检查DeepSeek API密钥
python -c "
import os
api_key = os.getenv('DEEPSEEK_API_KEY')
if api_key:
    print('✅ 检测到DeepSeek API密钥')
    exit(0)
else:
    print('⚠️  未检测到DeepSeek API密钥')
    exit(1)
" >nul 2>&1

if not errorlevel 1 (
    set ONLINE_MODE=true
    echo 🌐 将使用在线模式 (DeepSeek API)
) else (
    echo 🏠 将使用离线模式 (Ollama)
    
    :: 检查Ollama服务
    python -c "
import requests
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print('✅ Ollama服务运行正常')
        exit(0)
    else:
        print('❌ Ollama服务响应异常')
        exit(1)
except:
    print('❌ Ollama服务未启动')
    exit(1)
" >nul 2>&1
    
    if errorlevel 1 (
        echo ❌ Ollama服务未启动
        echo 请先启动Ollama服务:
        echo 1. 运行 setup_ollama.bat 安装Ollama
        echo 2. 或手动启动: ollama serve
        pause
        exit /b 1
    )
)

:: 启动服务器
echo.
echo 🎯 启动AI聊天服务器...
echo 模式: %ONLINE_MODE%
echo 地址: http://localhost:8000
echo.
echo 💡 提示:
echo - 按 Ctrl+C 停止服务器
echo - 服务器启动后，运行 python client.py 启动客户端
echo.

if "%ONLINE_MODE%"=="true" (
    python start_server.py --online
) else (
    python start_server.py --offline
)

echo.
echo 👋 服务器已停止
pause 