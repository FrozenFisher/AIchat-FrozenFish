@echo off
chcp 65001 >nul
echo 🔧 Ollama 安装配置脚本 (Windows)
echo ==========================================

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请访问 https://www.python.org/downloads/ 下载并安装Python
    echo 安装时请勾选"Add Python to PATH"选项
    pause
    exit /b 1
)

echo ✅ Python已安装

:: 检查pip是否可用
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip不可用
    echo 尝试升级pip...
    python -m pip install --upgrade pip
)

:: 安装Python依赖
echo 📦 安装Python依赖包...
pip install requests pyyaml

:: 检查Ollama是否已安装
echo.
echo 🔍 检查Ollama是否已安装...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama未安装
    echo.
    echo 📥 请手动安装Ollama:
    echo 1. 访问 https://ollama.ai/download
    echo 2. 下载Windows版本
    echo 3. 运行安装程序
    echo 4. 安装完成后重新运行此脚本
    echo.
    echo 或者使用以下命令安装:
    echo winget install Ollama.Ollama
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Ollama已安装
)

:: 启动Ollama服务
echo.
echo 🚀 启动Ollama服务...
echo 注意: 如果Ollama服务已在运行，请忽略以下错误信息
start /B ollama serve

:: 等待服务启动
echo ⏳ 等待Ollama服务启动...
timeout /t 5 /nobreak >nul

:: 检查服务状态
echo 🔍 检查Ollama服务状态...
python -c "
import requests
import time
import sys

for i in range(30):
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            print('✅ Ollama服务启动成功')
            sys.exit(0)
    except:
        pass
    
    print(f'⏳ 等待Ollama服务启动... ({i+1}/30)')
    time.sleep(1)

print('❌ Ollama服务启动超时')
sys.exit(1)
"

if errorlevel 1 (
    echo ❌ Ollama服务启动失败
    echo 请检查:
    echo 1. Ollama是否正确安装
    echo 2. 端口11434是否被占用
    echo 3. 防火墙设置
    pause
    exit /b 1
)

:: 检查现有模型
echo.
echo 📋 检查现有模型...
python -c "
import requests
import json

try:
    response = requests.get('http://localhost:11434/api/tags')
    if response.status_code == 200:
        models = response.json()
        if 'models' in models and models['models']:
            print('✅ 现有模型:')
            for model in models['models']:
                print(f'   - {model[\"name\"]}')
        else:
            print('⚠️  没有找到现有模型')
    else:
        print('❌ 无法获取模型列表')
except Exception as e:
    print(f'❌ 获取模型列表失败: {e}')
"

:: 下载默认模型
echo.
echo 📥 下载默认模型 (qwen3:8b)...
echo 这可能需要几分钟时间，请耐心等待...
ollama pull qwen3:8b

if errorlevel 1 (
    echo ❌ 模型下载失败
    echo 请检查网络连接或手动下载:
    echo ollama pull qwen3:8b
    pause
    exit /b 1
)

:: 测试模型
echo.
echo 🧪 测试模型...
python -c "
import requests
import json

try:
    test_data = {
        'model': 'qwen3:8b',
        'messages': [{'role': 'user', 'content': '你好'}],
        'stream': False
    }
    
    response = requests.post(
        'http://localhost:11434/api/chat',
        json=test_data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print('✅ 模型测试成功')
        print(f'   回复: {result[\"message\"][\"content\"][:50]}...')
    else:
        print(f'❌ 模型测试失败: {response.status_code}')
        
except Exception as e:
    print(f'❌ 模型测试失败: {e}')
"

if errorlevel 1 (
    echo ❌ 模型测试失败
    pause
    exit /b 1
)

echo.
echo 🎉 Ollama配置完成!
echo 现在可以运行: python start_server.py --offline
echo.
echo 💡 提示:
echo - 要停止Ollama服务: 在任务管理器中结束ollama.exe进程
echo - 要下载其他模型: ollama pull 模型名称
echo - 要查看可用模型: ollama list
echo.
pause 