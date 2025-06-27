#!/usr/bin/env python3
"""
启动AI聊天服务器
支持本地Ollama和在线DeepSeek API两种模式
"""

import subprocess
import sys
import time
import requests
import os
import argparse
from pathlib import Path

def check_server_health(url: str, max_retries: int = 30) -> bool:
    """检查服务器健康状态"""
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ 服务器启动成功: {url}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ 等待服务器启动... ({i+1}/{max_retries})")
        time.sleep(2)
    
    print(f"❌ 服务器启动失败: {url}")
    return False

def check_ollama_service() -> bool:
    """检查Ollama服务状态"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务运行正常")
            models = response.json()
            if "models" in models:
                print(f"   可用模型: {[model['name'] for model in models['models']]}")
            return True
        else:
            print(f"❌ Ollama服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到Ollama服务: {e}")
        return False

def check_deepseek_config() -> bool:
    """检查DeepSeek API配置"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 未设置DEEPSEEK_API_KEY环境变量")
        print("   请设置环境变量: export DEEPSEEK_API_KEY='your_api_key'")
        return False
    
    print("✅ DeepSeek API密钥已配置")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="启动AI聊天服务器")
    parser.add_argument("--online", action="store_true", help="启用在线模式 (DeepSeek API)")
    parser.add_argument("--offline", action="store_true", help="启用离线模式 (Ollama)")
    args = parser.parse_args()
    
    print("🚀 启动AI聊天服务器...")
    
    # 确定运行模式
    online_mode = args.online
    if not args.online and not args.offline:
        # 默认检查环境变量
        if os.getenv("DEEPSEEK_API_KEY"):
            online_mode = True
            print("🔍 检测到DeepSeek API密钥，默认使用在线模式")
        else:
            online_mode = False
            print("🔍 未检测到DeepSeek API密钥，默认使用离线模式")
    
    if online_mode:
        print("🌐 在线模式: 使用DeepSeek API")
        if not check_deepseek_config():
            print("❌ DeepSeek API配置失败，无法启动在线模式")
            return False
    else:
        print("🏠 离线模式: 使用Ollama")
        if not check_ollama_service():
            print("❌ Ollama服务未启动，请先启动Ollama:")
            print("   1. 安装Ollama: https://ollama.ai/")
            print("   2. 启动Ollama服务: ollama serve")
            print("   3. 下载模型: ollama pull qwen3:8b")
            return False
    
    # 检查GPT-SoVITS服务（音频生成需要）
    #if not check_server_health("http://127.0.0.1:9880", max_retries=5):
    #    print("❌ GPT-SoVITS服务未启动，请先启动GPT-SoVITS API服务")
    #    return False
    
    # 设置环境变量
    if online_mode:
        os.environ["ONLINE_MODE"] = "true"
        print("✅ 已设置在线模式环境变量")
    else:
        os.environ["ONLINE_MODE"] = "false"
        print("✅ 已设置离线模式环境变量")
    
    # 启动服务器
    print("🎯 启动AI聊天服务器...")
    try:
        # 使用uvicorn启动服务器
        cmd = [sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 