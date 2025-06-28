#!/usr/bin/env python3
"""
Letta版服务器启动脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_letta_installation():
    """检查Letta是否已安装"""
    try:
        import letta_client
        print("✅ Letta客户端已安装")
        return True
    except ImportError:
        print("❌ Letta客户端未安装")
        print("请运行: pip install letta-client")
        return False

def check_letta_server():
    """检查Letta服务器是否运行"""
    try:
        import requests
        response = requests.get("http://localhost:8283/health", timeout=5)
        if response.status_code == 200:
            print("✅ Letta服务器正在运行")
            return True
        else:
            print("❌ Letta服务器响应异常")
            return False
    except:
        print("❌ Letta服务器未运行")
        print("请先启动Letta服务器:")
        print("  letta server start")
        return False

def check_gpt_sovits():
    """检查GPT-SoVITS服务是否运行"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:9880", timeout=5)
        if response.status_code == 200:
            print("✅ GPT-SoVITS服务正在运行")
            return True
        else:
            print("❌ GPT-SoVITS服务响应异常")
            return False
    except:
        print("❌ GPT-SoVITS服务未运行")
        print("请先启动GPT-SoVITS服务")
        return False

def start_letta_server():
    """启动Letta版服务器"""
    print("🚀 启动Letta版AI聊天服务器...")
    
    # 检查依赖
    if not check_letta_installation():
        return False
    
    if not check_letta_server():
        print("⚠️  建议先启动Letta服务器，但可以继续运行")
    
    if not check_gpt_sovits():
        print("⚠️  建议先启动GPT-SoVITS服务，但可以继续运行")
    
    # 设置环境变量
    os.environ.setdefault("LETTA_BASE_URL", "http://localhost:8283")
    
    # 启动服务器
    server_path = Path(__file__).parent / "letta_server.py"
    
    try:
        print(f"📁 服务器路径: {server_path}")
        print("🌐 服务器将在 http://127.0.0.1:8000 启动")
        print("📖 API文档: http://127.0.0.1:8000/docs")
        print("🔄 按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        # 启动服务器进程
        process = subprocess.Popen([
            sys.executable, str(server_path)
        ])
        
        # 等待进程结束
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        if process:
            process.terminate()
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_letta_server() 