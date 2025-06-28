#!/usr/bin/env python3
"""
DeepSeek API安装和配置脚本
"""

import subprocess
import sys
import os
import requests
import json
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("   需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("📦 安装Python依赖包...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "openai", "requests", "pyyaml"
        ], check=True)
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def get_api_key():
    """获取API密钥"""
    print("\n🔑 DeepSeek API密钥设置")
    print("=" * 40)
    print("1. 访问 https://platform.deepseek.com/")
    print("2. 注册账号并获取API密钥")
    print("3. 在下方输入API密钥:")
    
    api_key = input("请输入API密钥: ").strip()
    
    if not api_key:
        print("❌ API密钥不能为空")
        return None
    
    return api_key

def set_environment_variable(api_key):
    """设置环境变量"""
    print("\n🔧 设置环境变量...")
    
    # 当前会话设置
    os.environ["DEEPSEEK_API_KEY"] = api_key
    
    # 永久设置（根据操作系统）
    system = os.name
    if system == "nt":  # Windows
        try:
            subprocess.run([
                "setx", "DEEPSEEK_API_KEY", api_key
            ], check=True)
            print("✅ 环境变量设置成功 (Windows)")
        except subprocess.CalledProcessError:
            print("⚠️  环境变量设置失败，请手动设置:")
            print(f"   set DEEPSEEK_API_KEY={api_key}")
    else:  # Unix/Linux/macOS
        try:
            # 添加到shell配置文件
            home = Path.home()
            shell_config = home / ".bashrc"
            if not shell_config.exists():
                shell_config = home / ".zshrc"
            
            if shell_config.exists():
                with open(shell_config, "a") as f:
                    f.write(f'\nexport DEEPSEEK_API_KEY="{api_key}"\n')
                print(f"✅ 环境变量已添加到 {shell_config}")
            else:
                print("⚠️  未找到shell配置文件，请手动设置:")
                print(f"   export DEEPSEEK_API_KEY={api_key}")
        except Exception as e:
            print(f"⚠️  环境变量设置失败: {e}")
            print("请手动设置环境变量")

def check_api_key(api_key: str) -> bool:
    """检查API密钥是否有效"""
    try:
        import openai
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        # 测试API调用
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ API密钥验证成功")
            return True
        else:
            print("❌ API密钥验证失败：返回空内容")
            return False
            
    except Exception as e:
        print(f"❌ API密钥验证失败：{e}")
        return False

def test_api_connection(api_key):
    """测试API连接"""
    print("\n🧪 测试API连接...")
    
    if not check_api_key(api_key):
        print("❌ API连接测试失败")
        print("请检查:")
        print("1. API密钥是否正确")
        print("2. 网络连接是否正常")
        print("3. API密钥余额是否充足")
        return False
    
    return True

def main():
    """主函数"""
    print("🔧 DeepSeek API安装和配置脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装依赖
    if not install_dependencies():
        return False
    
    # 获取API密钥
    api_key = get_api_key()
    if not api_key:
        return False
    
    # 设置环境变量
    set_environment_variable(api_key)
    
    # 测试API连接
    if not test_api_connection(api_key):
        return False
    
    print("\n🎉 DeepSeek API配置完成!")
    print("现在可以运行: python start_server.py --online")
    print("\n💡 提示:")
    print("- 如果遇到环境变量问题，请重启命令行")
    print("- 要检查API余额，请访问DeepSeek控制台")
    print("- 要更换API密钥，请重新运行此脚本")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 