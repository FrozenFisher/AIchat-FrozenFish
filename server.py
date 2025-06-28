"""
AI聊天服务器 - 负责所有计算任务
提供LLM推理、音频生成、模型管理等功能
支持本地Ollama和在线DeepSeek API两种模式
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
from queue import Queue
import time

import requests
import tiktoken
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import simpleaudio as sa

# BERT情感分析相关导入
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import torch

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
    ref_audio_path: Dict[str, str]  # 修改为字典格式，支持多种情感

class ModelConfig(BaseModel):
    gpt_weights: str
    sovits_weights: str

# 全局变量
app = FastAPI(title="AI聊天服务器", version="1.0.0")
ollama_client = None
deepseek_client = None
model_name = "qwen3:8b"  # 默认使用qwen3:8b模型
online_mode = False  # 在线模式标志
deepseek_api_key = None  # DeepSeek API密钥
chat_sessions: Dict[str, List[ChatMessage]] = {}
current_agent = "银狼"
agent_configs: Dict[str, AgentConfig] = {}

# 音频生成队列和锁（解决GPT-SoVITS并发问题）
audio_generation_lock = threading.Lock()
audio_generation_queue = Queue()

# BERT情感分析相关全局变量
bert_tokenizer = None
bert_model = None
sentiment_analyzer = None
emotion_map = {
    0: "高兴", 1: "悲伤", 2: "愤怒", 3: "惊讶", 4: "恐惧", 
    5: "厌恶", 6: "中性", 7: "害羞", 8: "兴奋", 9: "舒适",
    10: "紧张", 11: "爱慕", 12: "委屈", 13: "骄傲", 14: "困惑"
}

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_bert_model():
    """加载BERT情感分析模型"""
    global bert_tokenizer, bert_model, sentiment_analyzer
    
    try:
        model_path = "./lib/retrainedBERT"
        if not os.path.exists(model_path):
            print(f"❌ BERT模型路径不存在: {model_path}")
            return False
        
        print(f"正在加载BERT模型: {model_path}")
        bert_tokenizer = BertTokenizer.from_pretrained(model_path)
        bert_model = BertForSequenceClassification.from_pretrained(model_path)
        
        # 创建情感分析pipeline
        sentiment_analyzer = pipeline(
            "text-classification",
            model=bert_model,
            tokenizer=bert_tokenizer,
            framework="pt",
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        
        print(f"✅ BERT模型加载成功，使用设备: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
        return True
        
    except Exception as e:
        print(f"❌ BERT模型加载失败: {e}")
        return False

def predict_emotion(text: str) -> str:
    """预测文本情感，返回情感标签"""
    global sentiment_analyzer, emotion_map
    
    if sentiment_analyzer is None:
        print("BERT模型未加载，使用默认中性情感")
        return "中性"
    
    try:
        if not text.strip():
            return "中性"
        
        result = sentiment_analyzer(text)
        label = int(result[0]['label'].split('_')[-1])
        emotion = emotion_map.get(label, "中性")
        
        print(f"情感分析: '{text[:50]}...' -> {emotion} (置信度: {result[0]['score']:.4f})")
        return emotion
        
    except Exception as e:
        print(f"情感分析失败: {e}")
        return "中性"

def load_config():
    """加载配置文件"""
    global agent_configs
    current_path = Path(__file__).parent
    config_path = current_path / "modelconfig.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    for agent_name, agent_data in config['Agents'].items():
        agent_configs[agent_name] = AgentConfig(
            name=agent_name,
            gpt_path=str(current_path.parent / "GPT-SoVITS" / agent_data["GPTPath"]),
            sovits_path=str(current_path.parent / "GPT-SoVITS" / agent_data["SoVITSPath"]),
            bg_path=str(current_path / agent_data["bgPath"]),
            prompt_path=str(current_path / agent_data["promptPath"]),
            ref_audio_path=agent_data["refaudioPath"]  # 现在是字典格式
        )

def init_ollama():
    """初始化Ollama客户端"""
    global ollama_client
    
    # 检查Ollama服务是否可用
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✅ Ollama服务连接成功")
            ollama_client = True
        else:
            print("❌ Ollama服务响应异常")
            ollama_client = False
    except Exception as e:
        print(f"❌ 无法连接到Ollama服务: {e}")
        ollama_client = False

def init_deepseek():
    """初始化DeepSeek客户端"""
    global deepseek_client, deepseek_api_key
    
    # 从环境变量获取API密钥
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        print("❌ 未设置DEEPSEEK_API_KEY环境变量")
        deepseek_client = None
        return
    
    try:
        # 创建DeepSeek客户端
        deepseek_client = openai.OpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        # 测试连接
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ DeepSeek API连接成功")
        
    except Exception as e:
        print(f"❌ DeepSeek API连接失败: {e}")
        deepseek_client = None

def get_ollama_client():
    """获取Ollama客户端配置"""
    return {
        "base_url": "http://localhost:11434",
        "model": model_name
    }

def split_text_for_audio(text: str) -> tuple[List[str], List[str]]:
    """将文本分割为适合音频生成的句子
    返回: (bert_sentences, audio_sentences)
    bert_sentences: 包含圆括号内容的句子，用于BERT情感预测
    audio_sentences: 去除圆括号内容的句子，用于音频生成
    """
    # 过滤掉<think></think>标签及其内容
    text_without_think = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # 先按标点分句，保留括号内容（添加~作为句子结束符）
    bert_sentences = re.findall(r'[^.!?;:。！？：；~]*[.!?;:。！？：；~]+', text_without_think)
    bert_sentences = [s.strip() for s in bert_sentences if s.strip()]
    # 对每个句子分别去除括号内容
    audio_sentences = [re.sub(r'（.*?）|\(.*?\)', '', s).strip() for s in bert_sentences]
    return bert_sentences, audio_sentences

async def generate_audio_segments(text: str, agent: str) -> List[str]:
    """生成音频片段，返回base64编码的音频数据列表"""
    agent_config = agent_configs.get(agent)
    if not agent_config or not agent_config.ref_audio_path:
        return []
    
    bert_sentences, audio_sentences = split_text_for_audio(text)
    audio_data_list = []
    
    # 确保两个列表长度一致
    if len(bert_sentences) != len(audio_sentences):
        print(f"警告：BERT句子数量({len(bert_sentences)})与音频句子数量({len(audio_sentences)})不匹配")
        return []
    
    for i, (bert_sentence, audio_sentence) in enumerate(zip(bert_sentences, audio_sentences)):
        try:
            # 使用BERT模型预测情感（使用包含圆括号内容的句子）
            emotion = predict_emotion(bert_sentence)
            print(f"句子 {i+1}: BERT输入 '{bert_sentence}' -> 情感: {emotion}")
            print(f"句子 {i+1}: 音频输入 '{audio_sentence}'")
            
            # 根据情感选择对应的参考音频
            ref_audio_path = agent_config.ref_audio_path.get(emotion)
            if not ref_audio_path:
                print(f"未找到情感 '{emotion}' 的参考音频，使用中性音频")
                ref_audio_path = agent_config.ref_audio_path.get("中性")
            
            if not ref_audio_path or not os.path.exists(ref_audio_path):
                print(f"参考音频不存在: {ref_audio_path}")
                continue
            
            # 获取参考音频的文本（从文件名提取）
            ref_audio_name = Path(ref_audio_path).stem
            current_path = Path(__file__).parent
            
            # 使用锁确保GPT-SoVITS API调用是串行的
            try:
                with audio_generation_lock:
                    print(f"🔒 获取音频生成锁，开始生成第 {i+1} 个音频...")
                    
                    # 调用GPT-SoVITS API（使用去除圆括号内容的句子）
                    tts_url = "http://127.0.0.1:9880/tts"
                    post_data = {
                        "prompt_text": ref_audio_name,
                        "prompt_lang": "zh",
                        "ref_audio_path": str(current_path / ref_audio_path),
                        "text": audio_sentence,
                        "text_lang": "zh",
                        "parallel_infer": True,  # 启用并行推理
                    }
                    
                    response = requests.post(tts_url, json=post_data)
                    if response.status_code == 200:
                        # 将音频数据编码为base64字符串
                        audio_base64 = base64.b64encode(response.content).decode('utf-8')
                        audio_data_list.append(audio_base64)
                        print(f"✅ 生成音频: {audio_sentence} (情感: {emotion})")
                    else:
                        print(f"❌ 音频生成失败: {response.status_code}")
                        print(f"   错误信息: {response.text}")
                    
                    print(f"🔓 释放音频生成锁，第 {i+1} 个音频生成完成")
            except Exception as lock_error:
                print(f"❌ 音频生成锁错误: {lock_error}")
                # 确保锁被释放
                if audio_generation_lock.locked():
                    audio_generation_lock.release()
                    print("🔓 强制释放音频生成锁")
                
        except Exception as e:
            print(f"❌ 音频生成错误: {e}")
    
    return audio_data_list

async def call_llm_api(messages: List[Dict]) -> str:
    """调用LLM API（支持Ollama和DeepSeek）"""
    global online_mode
    
    if online_mode and deepseek_client is not None:
        # 在线模式：使用DeepSeek API
        try:
            # 确保消息格式正确
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",  # 使用DeepSeek-V3模型
                messages=formatted_messages,
                temperature=0.8,
                max_tokens=1024
            )
            content = response.choices[0].message.content
            if content is None:
                raise Exception("DeepSeek API返回空内容")
            return content
            
        except Exception as e:
            print(f"DeepSeek API错误: {e}")
            raise
    else:
        # 离线模式：使用Ollama API
        if not ollama_client:
            raise Exception("Ollama服务不可用")
            
        try:
            # 构建Ollama API请求
            ollama_data = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "num_predict": 1024
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/chat",
                json=ollama_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"]
            else:
                raise Exception(f"Ollama API调用失败: {response.status_code}")
                
        except Exception as e:
            print(f"Ollama API错误: {e}")
            raise

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    global online_mode
    
    load_config()
    init_ollama()
    init_deepseek()
    
    # 加载BERT情感分析模型
    bert_loaded = load_bert_model()
    if bert_loaded:
        print("✅ BERT情感分析模型加载成功")
    else:
        print("⚠️ BERT情感分析模型加载失败，将使用默认中性情感")
    
    # 根据环境变量设置在线模式
    online_mode = os.getenv("ONLINE_MODE", "false").lower() == "true"
    
    if online_mode:
        if deepseek_client is not None:
            print("✅ 服务器启动完成 - 在线模式 (DeepSeek API)")
        else:
            print("❌ 在线模式配置失败，切换到离线模式")
            online_mode = False
    else:
        if ollama_client:
            print("✅ 服务器启动完成 - 离线模式 (Ollama)")
        else:
            print("❌ 离线模式配置失败，请检查Ollama服务")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    print("服务器关闭")

@app.get("/")
async def root():
    """根路径"""
    mode = "在线模式 (DeepSeek API)" if online_mode else "离线模式 (Ollama)"
    return {
        "message": "AI聊天服务器运行中", 
        "version": "1.0.0", 
        "mode": mode,
        "framework": "DeepSeek API" if online_mode else "Ollama"
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

@app.get("/models")
async def get_models():
    """获取可用的Ollama模型"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            return {"models": [model["name"] for model in models["models"]]}
        else:
            return {"models": []}
    except Exception as e:
        print(f"获取模型列表失败: {e}")
        return {"models": []}

@app.post("/models/{new_model_name}")
async def switch_model(new_model_name: str):
    """切换Ollama模型"""
    global model_name
    try:
        # 检查模型是否存在
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            available_models = [model["name"] for model in models["models"]]
            if new_model_name in available_models:
                model_name = new_model_name
                return {"message": f"成功切换到模型: {model_name}"}
            else:
                raise HTTPException(status_code=404, detail="模型不存在")
        else:
            raise HTTPException(status_code=500, detail="无法获取模型列表")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换模型失败: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """处理聊天请求"""
    global current_agent
    
    # 检查Ollama服务状态
    if not ollama_client:
        raise HTTPException(status_code=503, detail="Ollama服务不可用")
    
    # 更新当前角色
    if request.agent != current_agent:
        current_agent = request.agent
        await switch_agent(request.agent)
    
    # 获取或创建会话
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    # 添加用户消息
    chat_sessions[session_id].append(
        ChatMessage(role="user", content=request.message)
    )
    
    # 构建消息列表
    messages = [{"role": msg.role, "content": msg.content} 
               for msg in chat_sessions[session_id]]
    
    try:
        # 调用Ollama API
        response_content = await call_llm_api(messages)
        
        # 添加助手回复到会话历史
        chat_sessions[session_id].append(
            ChatMessage(role="assistant", content=response_content)
        )
        
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
        raise HTTPException(status_code=500, detail=f"LLM调用失败: {str(e)}")

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

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """获取音频文件 - 已废弃，现在直接返回音频数据"""
    raise HTTPException(status_code=410, detail="此API已废弃，音频数据现在直接包含在聊天响应中")

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"message": "会话已删除"}
    else:
        raise HTTPException(status_code=404, detail="会话不存在")

@app.get("/sessions")
async def list_sessions():
    """列出所有会话"""
    return {"sessions": list(chat_sessions.keys())}

@app.delete("/audio/{filename}")
async def delete_audio(filename: str):
    """删除音频文件 - 已废弃，音频数据不再保存为文件"""
    raise HTTPException(status_code=410, detail="此API已废弃，音频数据不再保存为文件")

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
    """初始化角色会话，发送角色提示词"""
    global current_agent
    
    # 检查Ollama服务状态
    if not ollama_client:
        raise HTTPException(status_code=503, detail="Ollama服务不可用")
    
    # 更新当前角色
    if agent_name != current_agent:
        current_agent = agent_name
        await switch_agent(agent_name)
    
    # 获取角色提示词
    if agent_name not in agent_configs:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    agent_config = agent_configs[agent_name]
    if agent_config.prompt_path == "none":
        return ChatResponse(
            response="该角色没有配置提示词，可以直接开始对话。",
            session_id=request.session_id or str(uuid.uuid4()),
            audio_data=[]
        )
    
    try:
        with open(agent_config.prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        # 创建会话并发送系统提示词
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        # 添加系统提示词
        chat_sessions[session_id].append(
            ChatMessage(role="system", content=system_prompt)
        )
        
        # 构建消息列表
        messages = [{"role": msg.role, "content": msg.content} 
                   for msg in chat_sessions[session_id]]
        
        # 调用Ollama API获取角色初始化回复
        response_content = await call_llm_api(messages)
        
        # 添加助手回复到会话历史
        chat_sessions[session_id].append(
            ChatMessage(role="assistant", content=response_content)
        )
        
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

@app.post("/config/online")
async def set_online_mode(online: bool):
    """设置在线模式"""
    global online_mode
    online_mode = online
    
    if online_mode:
        if deepseek_client is not None:
            return {"message": "已切换到在线模式 (DeepSeek API)", "mode": "online"}
        else:
            raise HTTPException(status_code=400, detail="DeepSeek API未配置或连接失败")
    else:
        if ollama_client:
            return {"message": "已切换到离线模式 (Ollama)", "mode": "offline"}
        else:
            raise HTTPException(status_code=400, detail="Ollama服务不可用")

@app.get("/config/mode")
async def get_mode():
    """获取当前模式"""
    mode = "online" if online_mode else "offline"
    framework = "DeepSeek API" if online_mode else "Ollama"
    return {"mode": mode, "framework": framework}

@app.post("/emotion/analyze")
async def analyze_emotion(text: str):
    """分析文本情感"""
    try:
        emotion = predict_emotion(text)
        return {
            "text": text,
            "emotion": emotion,
            "message": "情感分析完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情感分析失败: {str(e)}")

@app.get("/emotion/status")
async def get_emotion_status():
    """获取情感分析模型状态"""
    return {
        "bert_loaded": sentiment_analyzer is not None,
        "device": "CUDA" if torch.cuda.is_available() else "CPU",
        "available_emotions": list(emotion_map.values())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)