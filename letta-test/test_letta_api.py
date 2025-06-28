#!/usr/bin/env python3
"""
Letta版API测试脚本
"""

import requests
import json
import time
from typing import Dict, Any

# 服务器配置
SERVER_URL = "http://127.0.0.1:8000"

def test_server_health():
    """测试服务器健康状态"""
    print("🔍 测试服务器健康状态...")
    try:
        response = requests.get(f"{SERVER_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器运行正常")
            print(f"   版本: {data.get('version', 'N/A')}")
            print(f"   框架: {data.get('framework', 'N/A')}")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False

def test_letta_health():
    """测试Letta服务状态"""
    print("\n🔍 测试Letta服务状态...")
    try:
        response = requests.get(f"{SERVER_URL}/letta/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Letta服务状态: {data.get('status', 'unknown')}")
            if data.get('health'):
                print(f"   健康信息: {data['health']}")
            return True
        else:
            print(f"❌ Letta服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法获取Letta服务状态: {e}")
        return False

def test_get_agents():
    """测试获取角色列表"""
    print("\n🔍 测试获取角色列表...")
    try:
        response = requests.get(f"{SERVER_URL}/agents")
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", [])
            print(f"✅ 获取到 {len(agents)} 个角色:")
            for agent in agents:
                print(f"   - {agent}")
            return agents
        else:
            print(f"❌ 获取角色列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取角色列表异常: {e}")
        return []

def test_get_agent_config(agent_name: str):
    """测试获取角色配置"""
    print(f"\n🔍 测试获取角色配置: {agent_name}")
    try:
        response = requests.get(f"{SERVER_URL}/agent/{agent_name}")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ 角色配置获取成功:")
            print(f"   GPT路径: {config.get('gpt_path', 'N/A')}")
            print(f"   SoVITS路径: {config.get('sovits_path', 'N/A')}")
            print(f"   背景路径: {config.get('bg_path', 'N/A')}")
            print(f"   Letta Agent ID: {config.get('letta_agent_id', 'N/A')}")
            return config
        else:
            print(f"❌ 获取角色配置失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取角色配置异常: {e}")
        return None

def test_get_agent_prompt(agent_name: str):
    """测试获取角色提示词"""
    print(f"\n🔍 测试获取角色提示词: {agent_name}")
    try:
        response = requests.get(f"{SERVER_URL}/agent/{agent_name}/prompt")
        if response.status_code == 200:
            data = response.json()
            prompt = data.get("prompt", "")
            message = data.get("message", "")
            print(f"✅ 提示词获取成功: {message}")
            if prompt:
                print(f"   提示词长度: {len(prompt)} 字符")
                print(f"   提示词预览: {prompt[:100]}...")
            else:
                print("   提示词为空")
            return data
        else:
            print(f"❌ 获取角色提示词失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取角色提示词异常: {e}")
        return None

def test_init_agent_session(agent_name: str):
    """测试初始化角色会话"""
    print(f"\n🔍 测试初始化角色会话: {agent_name}")
    try:
        data = {
            "message": "",
            "agent": agent_name,
            "session_id": None
        }
        response = requests.post(f"{SERVER_URL}/agent/{agent_name}/init", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 角色初始化成功:")
            print(f"   会话ID: {result.get('session_id', 'N/A')}")
            print(f"   回复长度: {len(result.get('response', ''))} 字符")
            print(f"   音频片段数: {len(result.get('audio_data', []))}")
            print(f"   回复内容: {result.get('response', '')[:100]}...")
            return result
        else:
            print(f"❌ 角色初始化失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 角色初始化异常: {e}")
        return None

def test_chat(agent_name: str, message: str, session_id: str = None):
    """测试聊天功能"""
    print(f"\n🔍 测试聊天功能: {agent_name}")
    print(f"   消息: {message}")
    try:
        data = {
            "message": message,
            "agent": agent_name,
            "session_id": session_id
        }
        response = requests.post(f"{SERVER_URL}/chat", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 聊天成功:")
            print(f"   会话ID: {result.get('session_id', 'N/A')}")
            print(f"   回复长度: {len(result.get('response', ''))} 字符")
            print(f"   音频片段数: {len(result.get('audio_data', []))}")
            print(f"   回复内容: {result.get('response', '')[:100]}...")
            return result
        else:
            print(f"❌ 聊天失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 聊天异常: {e}")
        return None

def test_switch_agent(agent_name: str):
    """测试切换角色"""
    print(f"\n🔍 测试切换角色: {agent_name}")
    try:
        response = requests.post(f"{SERVER_URL}/switch_agent/{agent_name}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 角色切换成功: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ 角色切换失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 角色切换异常: {e}")
        return False

def test_letta_agents():
    """测试获取Letta Agents列表"""
    print("\n🔍 测试获取Letta Agents列表...")
    try:
        response = requests.get(f"{SERVER_URL}/letta/agents")
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", [])
            print(f"✅ 获取到 {len(agents)} 个Letta Agents:")
            for agent in agents:
                print(f"   - {agent.get('name', 'N/A')} (ID: {agent.get('id', 'N/A')})")
            return agents
        else:
            print(f"❌ 获取Letta Agents失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取Letta Agents异常: {e}")
        return []

def test_get_agent_configs():
    """测试获取所有角色配置信息"""
    print("\n🔍 测试获取所有角色配置信息...")
    try:
        response = requests.get(f"{SERVER_URL}/config/agents")
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", {})
            print(f"✅ 获取到 {len(agents)} 个角色配置:")
            for agent_name, config in agents.items():
                print(f"   {agent_name}:")
                print(f"     Letta Agent ID: {config.get('letta_agent_id', 'N/A')}")
                print(f"     GPT路径: {config.get('gpt_path', 'N/A')}")
                print(f"     SoVITS路径: {config.get('sovits_path', 'N/A')}")
            return agents
        else:
            print(f"❌ 获取角色配置失败: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ 获取角色配置异常: {e}")
        return {}

def test_config_persistence():
    """测试配置持久化功能"""
    print("\n🔍 测试配置持久化功能...")
    
    # 1. 获取初始配置
    initial_configs = test_get_agent_configs()
    if not initial_configs:
        print("❌ 无法获取初始配置")
        return False
    
    # 2. 选择一个没有Agent ID的角色进行初始化
    test_agent = None
    for agent_name, config in initial_configs.items():
        if not config.get('letta_agent_id'):
            test_agent = agent_name
            break
    
    if not test_agent:
        print("⚠️  所有角色都已配置Agent ID，跳过持久化测试")
        return True
    
    print(f"🔧 测试角色: {test_agent}")
    
    # 3. 初始化角色（这会创建新的Agent并保存到配置）
    init_result = test_init_agent_session(test_agent)
    if not init_result:
        print("❌ 角色初始化失败")
        return False
    
    # 4. 等待一下让配置保存
    time.sleep(2)
    
    # 5. 重新获取配置，检查Agent ID是否已保存
    updated_configs = test_get_agent_configs()
    if test_agent in updated_configs:
        new_agent_id = updated_configs[test_agent].get('letta_agent_id')
        if new_agent_id:
            print(f"✅ 配置持久化成功: {test_agent} -> {new_agent_id}")
            return True
        else:
            print(f"❌ Agent ID未保存: {test_agent}")
            return False
    else:
        print(f"❌ 角色配置丢失: {test_agent}")
        return False

def run_full_test():
    """运行完整测试"""
    print("🚀 开始Letta版API完整测试")
    print("=" * 50)
    
    # 1. 测试服务器健康状态
    if not test_server_health():
        print("❌ 服务器不可用，测试终止")
        return
    
    # 2. 测试Letta服务状态
    test_letta_health()
    
    # 3. 测试获取角色列表
    agents = test_get_agents()
    if not agents:
        print("❌ 没有可用角色，测试终止")
        return
    
    # 4. 测试第一个角色的配置和提示词
    test_agent = agents[0]
    test_get_agent_config(test_agent)
    test_get_agent_prompt(test_agent)
    
    # 5. 测试初始化角色会话
    init_result = test_init_agent_session(test_agent)
    if not init_result:
        print("❌ 角色初始化失败，跳过后续测试")
        return
    
    session_id = init_result.get("session_id")
    
    # 6. 测试聊天功能
    test_chat(test_agent, "你好，请介绍一下你自己", session_id)
    
    # 7. 测试角色切换（如果有多个角色）
    if len(agents) > 1:
        test_switch_agent(agents[1])
        test_init_agent_session(agents[1])
        test_chat(agents[1], "你好", session_id)
    
    # 8. 测试获取Letta Agents列表
    test_letta_agents()
    
    # 9. 测试配置持久化功能
    test_config_persistence()
    
    print("\n" + "=" * 50)
    print("✅ Letta版API测试完成")

if __name__ == "__main__":
    run_full_test() 