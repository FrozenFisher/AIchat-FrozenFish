#!/bin/bash

echo "🚀 AI聊天系统快速启动脚本"
echo "=========================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    echo "请先安装Python3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python@3.9"
    exit 1
fi

# 检查依赖
echo "🔍 检查依赖包..."
python3 -c "import fastapi, uvicorn, openai, requests, pyyaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 依赖包未安装"
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败"
        exit 1
    fi
fi

# 检查运行模式
echo ""
echo "🔍 检测运行模式..."
ONLINE_MODE=false

# 检查DeepSeek API密钥
if [ -n "$DEEPSEEK_API_KEY" ]; then
    echo "✅ 检测到DeepSeek API密钥"
    ONLINE_MODE=true
    echo "🌐 将使用在线模式 (DeepSeek API)"
else
    echo "⚠️  未检测到DeepSeek API密钥"
    echo "🏠 将使用离线模式 (Ollama)"
    
    # 检查Ollama服务
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "✅ Ollama服务运行正常"
    else
        echo "❌ Ollama服务未启动"
        echo "请先启动Ollama服务:"
        echo "1. 运行 python3 setup_ollama.py 安装Ollama"
        echo "2. 或手动启动: ollama serve"
        exit 1
    fi
fi

# 启动服务器
echo ""
echo "🎯 启动AI聊天服务器..."
echo "模式: $ONLINE_MODE"
echo "地址: http://localhost:8000"
echo ""
echo "💡 提示:"
echo "- 按 Ctrl+C 停止服务器"
echo "- 服务器启动后，运行 python3 client.py 启动客户端"
echo ""

if [ "$ONLINE_MODE" = true ]; then
    python3 start_server.py --online
else
    python3 start_server.py --offline
fi

echo ""
echo "👋 服务器已停止" 