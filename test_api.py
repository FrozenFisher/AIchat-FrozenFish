#!/usr/bin/env python3
"""
测试API脚本
用于测试服务器端API功能
支持在线和离线两种模式
"""

import requests
import json
import base64
import time
import uuid
import os

# 服务器配置
SERVER_URL = "http://localhost:8000"

def test_server_status():
    """测试服务器状态"""
    print("=== 测试服务器状态 ===")
    try:
        response = requests.get(f"{SERVER_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器运行正常")
            print(f"   版本: {data.get('version')}")
            print(f"   模式: {data.get('mode')}")
            print(f"   框架: {data.get('framework')}")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False

def test_mode_config():
    """测试模式配置"""
    print("\n=== 测试模式配置 ===")
    
    # 获取当前模式
    try:
        response = requests.get(f"{SERVER_URL}/config/mode")
        if response.status_code == 200:
            data = response.json()
            print(f"当前模式: {data.get('mode')} ({data.get('framework')})")
        else:
            print(f"❌ 获取模式配置失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取模式配置异常: {e}")
        return False
    
    # 测试切换模式（如果支持）
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        print("🔍 检测到DeepSeek API密钥，测试在线模式切换")
        try:
            response = requests.post(f"{SERVER_URL}/config/online", json=True)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 切换到在线模式: {data.get('message')}")
            else:
                print(f"❌ 切换到在线模式失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 切换模式异常: {e}")
    
    return True

def test_get_agents():
    """测试获取角色列表"""
    print("=== 测试获取角色列表 ===")
    response = requests.get(f"{SERVER_URL}/agents")
    if response.status_code == 200:
        agents = response.json()
        print(f"✅ 获取角色列表成功: {agents}")
        return agents
    else:
        print(f"❌ 获取角色列表失败: {response.status_code}")
        return []

def test_get_agent_config(agent_name):
    """测试获取角色配置"""
    print(f"\n=== 测试获取角色配置: {agent_name} ===")
    response = requests.get(f"{SERVER_URL}/agent/{agent_name}")
    if response.status_code == 200:
        config = response.json()
        print(f"✅ 获取角色配置成功: {config}")
        return config
    else:
        print(f"❌ 获取角色配置失败: {response.status_code}")
        return None

def test_get_agent_prompt(agent_name):
    """测试获取角色提示词"""
    print(f"\n=== 测试获取角色提示词: {agent_name} ===")
    response = requests.get(f"{SERVER_URL}/agent/{agent_name}/prompt")
    if response.status_code == 200:
        prompt = response.json()
        print(f"✅ 获取角色提示词成功: {prompt}")
        return prompt
    else:
        print(f"❌ 获取角色提示词失败: {response.status_code}")
        return None

def test_init_agent_session(agent_name):
    """测试初始化角色会话"""
    print(f"\n=== 测试初始化角色会话: {agent_name} ===")
    data = {
        "message": "初始化",
        "agent": agent_name,
        "session_id": None
    }
    response = requests.post(f"{SERVER_URL}/agent/{agent_name}/init", json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 初始化角色会话成功")
        print(f"回复: {result['response']}")
        
        # 检查音频数据
        audio_data = result.get('audio_data', [])
        if audio_data:
            print(f"✅ 收到音频数据: {len(audio_data)} 个片段")
            for i, audio_base64 in enumerate(audio_data):
                if audio_base64:
                    # 解码base64数据查看大小
                    audio_bytes = base64.b64decode(audio_base64)
                    print(f"  片段 {i+1}: {len(audio_bytes)} 字节")
                else:
                    print(f"  片段 {i+1}: 空数据")
        else:
            print("❌ 没有收到音频数据")
        
        return result
    else:
        print(f"❌ 初始化角色会话失败: {response.status_code}")
        return None

def test_chat(agent_name, message):
    """测试聊天功能"""
    print(f"\n=== 测试聊天功能: {agent_name} ===")
    data = {
        "message": message,
        "agent": agent_name,
        "session_id": None
    }
    response = requests.post(f"{SERVER_URL}/chat", json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 聊天成功")
        print(f"回复: {result['response']}")
        
        # 检查音频数据
        audio_data = result.get('audio_data', [])
        if audio_data:
            print(f"✅ 收到音频数据: {len(audio_data)} 个片段")
            for i, audio_base64 in enumerate(audio_data):
                if audio_base64:
                    # 解码base64数据查看大小
                    audio_bytes = base64.b64decode(audio_base64)
                    print(f"  片段 {i+1}: {len(audio_bytes)} 字节")
                else:
                    print(f"  片段 {i+1}: 空数据")
        else:
            print("❌ 没有收到音频数据")
        
        return result
    else:
        print(f"❌ 聊天失败: {response.status_code}")
        return None

def test_get_audio(filename):
    """测试获取音频文件 - 已废弃"""
    print(f"\n=== 测试获取音频文件 ({filename}) - 已废弃 ===")
    try:
        response = requests.get(f"{SERVER_URL}/audio/{filename}")
        if response.status_code == 410:
            print(f"✅ 正确返回废弃状态: {response.json()}")
            return None
        else:
            print(f"❌ 意外状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取音频文件异常: {e}")
        return None

def test_switch_agent(agent_name):
    """测试切换角色"""
    print(f"\n=== 测试切换角色: {agent_name} ===")
    response = requests.post(f"{SERVER_URL}/switch_agent/{agent_name}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 切换角色成功: {result}")
        return result
    else:
        print(f"❌ 切换角色失败: {response.status_code}")
        return None

def test_get_models():
    """测试获取模型列表"""
    print("\n=== 测试获取模型列表 ===")
    try:
        response = requests.get(f"{SERVER_URL}/models")
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            print(f"✅ 获取模型列表成功")
            print(f"   可用模型: {models}")
            return models
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取模型列表异常: {e}")
        return []

def test_switch_model(model_name):
    """测试切换模型"""
    print(f"\n=== 测试切换模型 ({model_name}) ===")
    try:
        response = requests.post(f"{SERVER_URL}/models/{model_name}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 切换模型成功: {data.get('message')}")
            return True
        else:
            print(f"❌ 切换模型失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 切换模型异常: {e}")
        return False

def test_think_tag_filtering():
    """测试think标签过滤功能"""
    print(f"\n=== 测试think标签过滤功能 ===")
    try:
        # 发送包含think标签的消息
        data = {
            "message": "请思考一下这个问题：什么是人工智能？",
            "agent": "银狼",
            "session_id": "test_think_session"
        }
        response = requests.post(f"{SERVER_URL}/chat", json=data)
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '')
            print(f"✅ 包含think标签的回复:")
            print(f"   原始回复: {ai_response}")
            
            # 检查是否包含think标签
            if '<think>' in ai_response and '</think>' in ai_response:
                print(f"   ✅ 检测到think标签")
            else:
                print(f"   ⚠️ 未检测到think标签")
            
            audio_files = result.get("audio_files", [])
            print(f"   音频文件数量: {len(audio_files)}")
            return result
        else:
            print(f"❌ think标签测试失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ think标签测试异常: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 开始API测试")
    
    # 测试服务器状态
    if not test_server_status():
        print("❌ 服务器状态测试失败，测试终止")
        return
    
    # 测试模式配置
    if not test_mode_config():
        print("❌ 模式配置测试失败，测试终止")
        return
    
    # 测试获取角色列表
    agents = test_get_agents()
    if not agents:
        print("❌ 无法获取角色列表，测试终止")
        return
    
    # 选择第一个角色进行测试
    test_agent = agents[0]
    print(f"\n🎯 选择测试角色: {test_agent}")
    
    # 测试获取角色配置
    test_get_agent_config(test_agent)
    
    # 测试获取角色提示词
    test_get_agent_prompt(test_agent)
    
    # 测试初始化角色会话
    init_result = test_init_agent_session(test_agent)
    if not init_result:
        print("❌ 角色初始化失败，跳过后续测试")
        return
    
    # 测试聊天功能
    test_chat(test_agent, "你好，请介绍一下你自己")
    
    # 测试切换角色（如果有多个角色）
    if len(agents) > 1:
        test_switch_agent(agents[1])
    
    # 测试模型管理
    models = test_get_models()
    if models and len(models) > 1:
        test_switch_model(models[1])
    
    # 测试think标签过滤功能
    test_think_tag_filtering()
    
    print("\n✅ API测试完成")

if __name__ == "__main__":
    main() 