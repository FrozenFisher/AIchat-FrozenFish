@echo off
chcp 65001 >nul
echo 🔧 DeepSeek API 配置脚本 (Windows)
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

:: 安装依赖
echo 📦 安装Python依赖包...
pip install openai requests pyyaml

:: 检查API密钥
echo.
echo 🔑 请设置DeepSeek API密钥:
echo 1. 访问 https://platform.deepseek.com/
echo 2. 注册账号并获取API密钥
echo 3. 在下方输入API密钥:
set /p api_key="请输入API密钥: "

if "%api_key%"=="" (
    echo ❌ API密钥不能为空
    pause
    exit /b 1
)

:: 设置环境变量
echo.
echo 🔧 设置环境变量...
setx DEEPSEEK_API_KEY "%api_key%"
if errorlevel 1 (
    echo ⚠️  环境变量设置失败，请手动设置:
    echo set DEEPSEEK_API_KEY=%api_key%
) else (
    echo ✅ 环境变量设置成功
)

:: 测试API连接
echo.
echo 🧪 测试API连接...
python -c "
import os
import openai
import sys

api_key = '%api_key%'
if not api_key:
    print('❌ API密钥未设置')
    sys.exit(1)

try:
    client = openai.OpenAI(
        api_key=api_key,
        base_url='https://api.deepseek.com/v1'
    )
    
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=10
    )
    
    if response.choices[0].message.content:
        print('✅ API连接测试成功')
    else:
        print('❌ API连接测试失败')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ API连接测试失败: {e}')
    sys.exit(1)
"

if errorlevel 1 (
    echo ❌ API测试失败，请检查网络连接和API密钥
    pause
    exit /b 1
)

echo.
echo 🎉 DeepSeek API配置完成!
echo 现在可以运行: python start_server.py --online
echo.
pause 