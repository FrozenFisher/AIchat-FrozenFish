#!/usr/bin/env python3
"""
Ollama安装和配置脚本
"""

import subprocess
import sys
import platform
import requests
import json
from pathlib import Path

def check_ollama_installed():
    """检查Ollama是否已安装"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama已安装: {result.stdout.strip()}")
            return True
        else:
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_ollama():
    """安装Ollama"""
    system = platform.system().lower()
    
    print(f"🔧 检测到系统: {system}")
    
    if system == "darwin":  # macOS
        print("📦 在macOS上安装Ollama...")
        try:
            subprocess.run([
                "curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"
            ], shell=True, check=True)
            print("✅ Ollama安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ollama安装失败: {e}")
            return False
    
    elif system == "linux":
        print("📦 在Linux上安装Ollama...")
        try:
            subprocess.run([
                "curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"
            ], shell=True, check=True)
            print("✅ Ollama安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ollama安装失败: {e}")
            return False
    
    elif system == "windows":
        print("📦 在Windows上安装Ollama...")
        print("请访问 https://ollama.ai/download 下载Windows版本")
        return False
    
    else:
        print(f"❌ 不支持的操作系统: {system}")
        return False

def start_ollama_service():
    """启动Ollama服务"""
    print("🚀 启动Ollama服务...")
    try:
        # 检查服务是否已在运行
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务已在运行")
            return True
    except requests.exceptions.RequestException:
        pass
    
    try:
        # 启动Ollama服务
        process = subprocess.Popen(['ollama', 'serve'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待服务启动
        import time
        for i in range(30):  # 最多等待30秒
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    print("✅ Ollama服务启动成功")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print(f"⏳ 等待Ollama服务启动... ({i+1}/30)")
            time.sleep(1)
        
        print("❌ Ollama服务启动超时")
        return False
        
    except Exception as e:
        print(f"❌ 启动Ollama服务失败: {e}")
        return False

def download_model(model_name="qwen3:8b"):
    """下载Ollama模型"""
    print(f"📥 下载模型: {model_name}")
    try:
        # 检查模型是否已存在
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            existing_models = [model["name"] for model in models["models"]]
            if model_name in existing_models:
                print(f"✅ 模型 {model_name} 已存在")
                return True
        
        # 下载模型
        print(f"⏳ 开始下载模型 {model_name}...")
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 模型 {model_name} 下载完成")
            return True
        else:
            print(f"❌ 模型下载失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 下载模型失败: {e}")
        return False

def list_models():
    """列出可用模型"""
    print("📋 列出可用模型...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            if "models" in models and models["models"]:
                print("✅ 可用模型:")
                for model in models["models"]:
                    print(f"   - {model['name']} ({model.get('size', 'N/A')})")
                return models["models"]
            else:
                print("⚠️  没有找到可用模型")
                return []
        else:
            print("❌ 无法获取模型列表")
            return []
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        return []

def test_model(model_name="qwen3:8b"):
    """测试模型"""
    print(f"🧪 测试模型: {model_name}")
    try:
        test_data = {
            "model": model_name,
            "messages": [{"role": "user", "content": "你好"}],
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 模型测试成功")
            print(f"   回复: {result['message']['content'][:100]}...")
            return True
        else:
            print(f"❌ 模型测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Ollama安装和配置脚本")
    print("=" * 50)
    
    # 检查是否已安装
    if not check_ollama_installed():
        print("📦 Ollama未安装，开始安装...")
        if not install_ollama():
            print("❌ 安装失败，请手动安装Ollama")
            return False
    
    # 启动服务
    if not start_ollama_service():
        print("❌ 无法启动Ollama服务")
        return False
    
    # 下载默认模型
    if not download_model("qwen3:8b"):
        print("❌ 无法下载默认模型")
        return False
    
    # 列出模型
    models = list_models()
    
    # 测试模型
    if not test_model("qwen3:8b"):
        print("❌ 模型测试失败")
        return False
    
    print("\n🎉 Ollama配置完成!")
    print("现在可以运行: python start_server.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 