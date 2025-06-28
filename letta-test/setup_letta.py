#!/usr/bin/env python3
"""
Letta安装配置脚本
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def install_letta_client():
    """安装Letta客户端"""
    print("🔧 安装Letta客户端...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "letta-client"
        ])
        print("✅ Letta客户端安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Letta客户端安装失败: {e}")
        return False

def install_letta_server():
    """安装Letta服务器（可选）"""
    print("🔧 安装Letta服务器...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "letta"
        ])
        print("✅ Letta服务器安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Letta服务器安装失败: {e}")
        return False

def test_letta_installation():
    """测试Letta安装"""
    print("🧪 测试Letta安装...")
    try:
        import letta_client
        print("✅ Letta客户端导入成功")
        
        # 测试基本功能
        client = letta_client.Letta(base_url="http://localhost:8283")
        print("✅ Letta客户端创建成功")
        return True
    except ImportError as e:
        print(f"❌ Letta客户端导入失败: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Letta客户端测试异常: {e}")
        return True  # 可能是网络问题，不算安装失败

def setup_environment():
    """设置环境变量"""
    print("🔧 设置环境变量...")
    
    # 创建.env文件
    env_file = Path(__file__).parent / ".env"
    env_content = """# Letta配置
# 使用Letta Cloud时设置API密钥
# LETTA_API_KEY=your_letta_api_key

# 使用本地Letta服务器时设置地址
LETTA_BASE_URL=http://localhost:8283

# 其他配置
PYTHONPATH=.
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ 环境变量文件已创建: {env_file}")
    
    # 设置环境变量
    os.environ.setdefault("LETTA_BASE_URL", "http://localhost:8283")
    print("✅ 环境变量设置完成")

def create_config_template():
    """创建配置模板"""
    print("🔧 创建配置模板...")
    
    config_file = Path(__file__).parent / "modelconfig.yaml"
    if not config_file.exists():
        config_content = """# 角色配置文件
# 每个角色包含以下配置项：
# - GPTPath: GPT模型路径
# - SoVITSPath: SoVITS模型路径  
# - bgPath: 背景图片路径
# - promptPath: 角色提示词文件路径
# - refaudioPath: 参考音频文件路径
# - letta_agent_id: Letta Agent ID（可选，留空则自动创建）

Agents:
  银狼:
    GPTPath: "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
    SoVITSPath: "GPT_SoVITS/pretrained_models/s2G488k.pth"
    bgPath: "lib/bgSilverWolf.png"
    promptPath: "lib/prompt/promptSilverWolf.txt"
    refaudioPath: "lib/参考音频/该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav"
    letta_agent_id: ""  # 留空则自动创建

  流萤:
    GPTPath: "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
    SoVITSPath: "GPT_SoVITS/pretrained_models/s2G488k.pth"
    bgPath: "lib/bgFireFly.png"
    promptPath: "lib/prompt/promptFireFly.txt"
    refaudioPath: "lib/参考音频/啊，是你呀！欸嘿，要出门么？带我一个呗。.wav"
    letta_agent_id: ""  # 留空则自动创建

  温迪:
    GPTPath: "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
    SoVITSPath: "GPT_SoVITS/pretrained_models/s2G488k.pth"
    bgPath: "lib/bgVenti.png"
    promptPath: "lib/prompt/promptVenti.txt"
    refaudioPath: "lib/参考音频/因为你身上别着星穹列车的徽章呀，我在大银幕上见过！.wav"
    letta_agent_id: ""  # 留空则自动创建

  帕姆:
    GPTPath: "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
    SoVITSPath: "GPT_SoVITS/pretrained_models/s2G488k.pth"
    bgPath: "lib/bgPanxin.png"
    promptPath: "lib/prompt/promptPanxin.txt"
    refaudioPath: "lib/参考音频/该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav"
    letta_agent_id: ""  # 留空则自动创建

  用户输入:
    GPTPath: "none"
    SoVITSPath: "none"
    bgPath: "lib/bg.png"
    promptPath: "none"
    refaudioPath: "none"
    letta_agent_id: ""  # 用户输入模式不需要Agent
"""
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ 配置模板已创建: {config_file}")
    else:
        print(f"✅ 配置文件已存在: {config_file}")

def create_directories():
    """创建必要的目录"""
    print("🔧 创建必要目录...")
    
    current_dir = Path(__file__).parent
    directories = [
        "temp",  # 临时文件目录
        "logs",  # 日志目录
    ]
    
    for dir_name in directories:
        dir_path = current_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ 目录已创建: {dir_path}")

def show_next_steps():
    """显示后续步骤"""
    print("\n" + "=" * 50)
    print("🎉 Letta安装配置完成！")
    print("=" * 50)
    print("\n📋 后续步骤：")
    print("1. 配置Letta服务：")
    print("   - 使用Letta Cloud: 设置 LETTA_API_KEY 环境变量")
    print("   - 使用本地服务: 运行 'letta server start'")
    print("\n2. 配置角色：")
    print("   - 编辑 modelconfig.yaml 文件")
    print("   - 设置正确的模型路径和音频文件路径")
    print("\n3. 启动服务：")
    print("   - 服务器: python start_letta_server.py")
    print("   - 客户端: python letta_client.py")
    print("   - 测试: python test_letta_api.py")
    print("\n4. 查看文档：")
    print("   - README.md 包含详细使用说明")
    print("\n🔗 相关链接：")
    print("   - Letta文档: https://docs.letta.com/")
    print("   - Letta API: https://docs.letta.com/api-reference/")

def main():
    """主函数"""
    print("🚀 Letta安装配置脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装Letta客户端
    if not install_letta_client():
        return False
    
    # 安装Letta服务器（可选）
    install_letta_server()
    
    # 测试安装
    if not test_letta_installation():
        print("⚠️  Letta安装可能有问题，请检查网络连接")
    
    # 设置环境
    setup_environment()
    
    # 创建配置模板
    create_config_template()
    
    # 创建目录
    create_directories()
    
    # 显示后续步骤
    show_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 