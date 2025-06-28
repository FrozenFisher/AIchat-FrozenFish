"""
AI聊天服务器 - 基于Letta重构
负责LLM推理、记忆管理、工具调用，使用GPT-SoVITS进行音频生成
"""

import os
import re
import yaml
import json
import uuid
import asyncio
import threading
import base64
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

import requests
import tiktoken
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from letta_client import Letta

# 数据模型
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    agent: str = "银狼"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    audio_data: Optional[List[str]] = None  # base64编码的音频数据

class AgentConfig(BaseModel):
    name: str
    gpt_path: str
    sovits_path: str
    bg_path: str
    prompt_path: str
    ref_audio_path: str
    letta_agent_id: Optional[str] = None  # Letta Agent ID

class ModelConfig(BaseModel):
    gpt_weights: str
    sovits_weights: str

# 全局变量
app = FastAPI(title="AI聊天服务器 (Letta版)", version="2.0.0")
letta_client = None
model_name = "qwen3:8b"  # 默认使用qwen3:8b模型
chat_sessions: Dict[str, List[ChatMessage]] = {}
current_agent = "银狼"
agent_configs: Dict[str, AgentConfig] = {}
letta_agents: Dict[str, str] = {}  # 角色名 -> Letta Agent ID 映射
config_file_path: Optional[Path] = None  # 配置文件路径

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_config():
    """加载配置文件"""
    global agent_configs, config_file_path
    current_path = Path(__file__).parent
    config_file_path = current_path / "modelconfig.yaml"
    
    with open(config_file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    for agent_name, agent_data in config['Agents'].items():
        agent_configs[agent_name] = AgentConfig(
            name=agent_name,
            gpt_path=str(current_path.parent / "GPT-SoVITS" / agent_data["GPTPath"]),
            sovits_path=str(current_path.parent / "GPT-SoVITS" / agent_data["SoVITSPath"]),
            bg_path=str(current_path / agent_data["bgPath"]),
            prompt_path=str(current_path / agent_data["promptPath"]),
            ref_audio_path=str(current_path / agent_data["refaudioPath"]),
            letta_agent_id=agent_data.get("letta_agent_id")  # 从配置中获取Letta Agent ID
        )

def save_config():
    """保存配置文件"""
    global config_file_path
    if not config_file_path:
        return
    
    try:
        # 重新加载原始配置
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # 更新Agent ID
        for agent_name, agent_config in agent_configs.items():
            if agent_name in config['Agents']:
                config['Agents'][agent_name]['letta_agent_id'] = agent_config.letta_agent_id
        
        # 保存更新后的配置
        with open(config_file_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True, indent=2)
        
        print(f"✅ 配置文件已更新: {config_file_path}")
        
    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")

def init_letta():
    """初始化Letta客户端"""
    global letta_client
    
    # 从环境变量获取Letta配置
    letta_base_url = os.getenv("LETTA_BASE_URL", "http://localhost:8283")
    letta_token = os.getenv("LETTA_API_KEY")
    
    try:
        if letta_token:
            # 连接到Letta Cloud
            letta_client = Letta(token=letta_token)
            print("✅ 连接到Letta Cloud")
        else:
            # 连接到本地Letta服务器
            letta_client = Letta(base_url=letta_base_url)
            print(f"✅ 连接到本地Letta服务器: {letta_base_url}")
        
        # 测试连接
        health_check = letta_client.health.get()
        print("✅ Letta连接测试成功")
        
    except Exception as e:
        print(f"❌ Letta连接失败: {e}")
        letta_client = None

def create_letta_agent(agent_name: str, system_prompt: str) -> Optional[str]:
    """为角色创建Letta Agent"""
    if not letta_client:
        return None
    
    try:
        # 创建Agent
        agent_data = {
            "name": f"{agent_name}_agent",
            "description": f"AI聊天角色: {agent_name}",
            "instructions": system_prompt,
            "model": "gpt-4",  # 可以根据需要调整模型
            "tools": []  # 可以添加工具
        }
        
        response = letta_client.agents.create(**agent_data)
        agent_id = response["id"]
        print(f"✅ 创建Letta Agent: {agent_name} -> {agent_id}")
        
        # 更新内存中的配置
        if agent_name in agent_configs:
            agent_configs[agent_name].letta_agent_id = agent_id
        
        # 保存到配置文件
        save_config()
        
        return agent_id
        
    except Exception as e:
        print(f"❌ 创建Letta Agent失败: {e}")
        return None

def get_or_create_letta_agent(agent_name: str) -> Optional[str]:
    """获取或创建Letta Agent"""
    # 检查是否已有Agent ID
    if agent_name in letta_agents:
        return letta_agents[agent_name]
    
    # 检查配置中是否有Agent ID
    if agent_name in agent_configs and agent_configs[agent_name].letta_agent_id:
        letta_agents[agent_name] = agent_configs[agent_name].letta_agent_id
        print(f"✅ 使用已配置的Letta Agent: {agent_name} -> {letta_agents[agent_name]}")
        return letta_agents[agent_name]
    
    # 创建新的Agent
    if agent_name in agent_configs:
        agent_config = agent_configs[agent_name]
        if agent_config.prompt_path != "none":
            try:
                with open(agent_config.prompt_path, 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
                
                agent_id = create_letta_agent(agent_name, system_prompt)
                if agent_id:
                    letta_agents[agent_name] = agent_id
                    print(f"✅ 新创建并保存Letta Agent: {agent_name} -> {agent_id}")
                    return agent_id
            except Exception as e:
                print(f"❌ 读取角色提示词失败: {e}")
    
    return None

def split_text_for_audio(text: str) -> List[str]:
    """将文本分割为适合音频生成的句子"""
    # 过滤掉<think></think>标签及其内容
    text_clean = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # 去除圆括号中的内容
    text_clean = re.sub(r'（.*?）|\(.*?\)', '', text_clean)
    # 按标点符号分割
    sentences = re.findall(r'[^,.!?;:，。！？：；]*[,.!?;:，。！？：；]*', text_clean)
    return [s.strip() for s in sentences if s.strip()]

async def generate_audio_segments(text: str, agent: str) -> List[str]:
    """生成音频片段，返回base64编码的音频数据列表"""
    agent_config = agent_configs.get(agent)
    if not agent_config or agent_config.ref_audio_path == "none":
        return []
    
    sentences = split_text_for_audio(text)
    audio_data_list = []
    
    # 获取参考音频的文本
    ref_audio_name = Path(agent_config.ref_audio_path).stem
    
    for i, sentence in enumerate(sentences):
        try:
            # 调用GPT-SoVITS API
            tts_url = "http://127.0.0.1:9880/tts"
            post_data = {
                "prompt_text": ref_audio_name,
                "prompt_lang": "zh",
                "ref_audio_path": agent_config.ref_audio_path,
                "text": sentence,
                "text_lang": "zh",
            }
            
            response = requests.post(tts_url, json=post_data)
            if response.status_code == 200:
                # 将音频数据编码为base64字符串
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                audio_data_list.append(audio_base64)
                print(f"生成音频: {sentence}")
            else:
                print(f"音频生成失败: {response.status_code}")
                
        except Exception as e:
            print(f"音频生成错误: {e}")
    
    return audio_data_list

async def call_letta_api(message: str, agent_name: str, session_id: str) -> str:
    """调用Letta API进行对话"""
    if not letta_client:
        raise Exception("Letta客户端未初始化")
    
    # 获取或创建Letta Agent
    agent_id = get_or_create_letta_agent(agent_name)
    if not agent_id:
        raise Exception(f"无法获取Letta Agent: {agent_name}")
    
    try:
        # 使用Letta Agent进行对话
        # 这里使用Letta的对话API，具体实现需要根据Letta API文档调整
        response = letta_client.agents.run(
            agent_id=agent_id,
            messages=[{"role": "user", "content": message}],
            session_id=session_id
        )
        
        # 提取回复内容
        if "content" in response:
            return response["content"]
        elif "message" in response:
            return response["message"]["content"]
        else:
            raise Exception("Letta API返回格式异常")
            
    except Exception as e:
        print(f"Letta API错误: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    load_config()
    init_letta()
    print("✅ Letta版服务器启动完成")
    
    # 显示已配置的Agent信息
    print("\n📋 已配置的Letta Agents:")
    for agent_name, agent_config in agent_configs.items():
        if agent_config.letta_agent_id:
            print(f"   {agent_name}: {agent_config.letta_agent_id}")
        else:
            print(f"   {agent_name}: 未配置 (将在首次使用时创建)")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    print("服务器关闭")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI聊天服务器运行中 (Letta版)", 
        "version": "2.0.0", 
        "framework": "Letta + GPT-SoVITS"
    }

@app.get("/agents")
async def get_agents():
    """获取所有可用角色"""
    return {"agents": list(agent_configs.keys())}

@app.get("/agent/{agent_name}")
async def get_agent_config(agent_name: str):
    """获取指定角色的配置"""
    if agent_name not in agent_configs:
        raise HTTPException(status_code=404, detail="角色不存在")
    return agent_configs[agent_name]

@app.get("/agent/{agent_name}/prompt")
async def get_agent_prompt(agent_name: str):
    """获取指定角色的提示词"""
    if agent_name not in agent_configs:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    agent_config = agent_configs[agent_name]
    if agent_config.prompt_path == "none":
        return {"prompt": "", "message": "该角色没有配置提示词"}
    
    try:
        with open(agent_config.prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        return {"prompt": prompt, "message": "成功获取角色提示词"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取提示词失败: {str(e)}")

@app.post("/agent/{agent_name}/init")
async def init_agent_session(agent_name: str, request: ChatRequest):
    """初始化角色会话"""
    if agent_name not in agent_configs:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 获取或创建Letta Agent
    agent_id = get_or_create_letta_agent(agent_name)
    if not agent_id:
        raise HTTPException(status_code=500, detail="无法创建Letta Agent")
    
    try:
        # 使用Letta Agent进行初始化对话
        session_id = request.session_id or str(uuid.uuid4())
        
        # 发送初始化消息
        init_message = "请介绍一下你自己，并说明你的角色设定。"
        response_content = await call_letta_api(init_message, agent_name, session_id)
        
        # 生成音频文件
        audio_data = []
        if agent_name != "userinput":
            audio_data = await generate_audio_segments(response_content, agent_name)
        
        return ChatResponse(
            response=response_content,
            session_id=session_id,
            audio_data=audio_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"角色初始化失败: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """处理聊天请求"""
    if request.agent not in agent_configs:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    try:
        # 使用Letta Agent进行对话
        session_id = request.session_id or str(uuid.uuid4())
        response_content = await call_letta_api(request.message, request.agent, session_id)
        
        # 生成音频文件
        audio_data = []
        if request.agent != "userinput":
            audio_data = await generate_audio_segments(response_content, request.agent)
        
        return ChatResponse(
            response=response_content,
            session_id=session_id,
            audio_data=audio_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

@app.post("/switch_agent/{agent_name}")
async def switch_agent(agent_name: str):
    """切换角色"""
    global current_agent
    
    if agent_name not in agent_configs:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    agent_config = agent_configs[agent_name]
    
    try:
        # 切换GPT模型
        if agent_config.gpt_path != "none":
            gpt_url = "http://127.0.0.1:9880/set_gpt_weights"
            params = {"weights_path": Path(agent_config.gpt_path).name}
            response = requests.get(gpt_url, params=params)
            if response.status_code != 200:
                print(f"GPT模型切换失败: {response.text}")
        
        # 切换SoVITS模型
        if agent_config.sovits_path != "none":
            sovits_url = "http://127.0.0.1:9880/set_sovits_weights"
            params = {"weights_path": Path(agent_config.sovits_path).name}
            response = requests.get(sovits_url, params=params)
            if response.status_code != 200:
                print(f"SoVITS模型切换失败: {response.text}")
        
        current_agent = agent_name
        return {"message": f"成功切换到角色: {agent_name}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"角色切换失败: {str(e)}")

@app.get("/letta/agents")
async def list_letta_agents():
    """列出所有Letta Agents"""
    if not letta_client:
        raise HTTPException(status_code=503, detail="Letta客户端未初始化")
    
    try:
        agents = letta_client.agents.list()
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Letta Agents失败: {str(e)}")

@app.get("/letta/health")
async def letta_health():
    """检查Letta服务状态"""
    if not letta_client:
        return {"status": "disconnected", "message": "Letta客户端未初始化"}
    
    try:
        health = letta_client.health.get()
        return {"status": "connected", "health": health}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/config/agents")
async def get_agent_configs():
    """获取所有角色的配置信息（包括Letta Agent ID）"""
    configs = {}
    for agent_name, agent_config in agent_configs.items():
        configs[agent_name] = {
            "name": agent_config.name,
            "gpt_path": agent_config.gpt_path,
            "sovits_path": agent_config.sovits_path,
            "bg_path": agent_config.bg_path,
            "prompt_path": agent_config.prompt_path,
            "ref_audio_path": agent_config.ref_audio_path,
            "letta_agent_id": agent_config.letta_agent_id
        }
    return {"agents": configs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 