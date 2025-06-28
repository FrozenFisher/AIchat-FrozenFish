"""
测试情感分析和音频生成功能
"""

import requests
import json
import os
from pathlib import Path
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import torch
import yaml

bert_tokenizer = None
bert_model = None
sentiment_analyzer = None
emotion_map = {
    0: "高兴", 1: "悲伤", 2: "愤怒", 3: "惊讶", 4: "恐惧", 
    5: "厌恶", 6: "中性", 7: "害羞", 8: "兴奋", 9: "舒适",
    10: "紧张", 11: "爱慕", 12: "委屈", 13: "骄傲", 14: "困惑"
}

def test_emotion_analysis():
    """测试情感分析功能"""
    print("="*60)
    print("测试情感分析功能")
    print("="*60)
    
    # 测试文本
    test_texts = [
        "终于考完试了，感觉整个人都轻松了！",
        "听到这个消息，我的世界瞬间崩塌了",
        "这种不负责任的行为让我火冒三丈！",
        "什么？你说的是真的吗？我不敢相信！",
        "黑暗中传来的声音让我毛骨悚然",
        "这种味道让我想吐，太恶心了",
        "请将报告提交到邮箱",
        "被这么多人看着，我有点不好意思",
        "听到这个消息，我兴奋得跳了起来！",
        "躺在沙发上，听着轻音乐，感觉特别放松",
        "马上就要上台了，我紧张得手心冒汗",
        "每次看到你，我的心都会加速跳动",
        "明明我什么都没做错，为什么要这样对我",
        "这个成就让我感到无比自豪",
        "这个问题让我百思不得其解"
    ]
    
    for text in test_texts:
        try:
            response = requests.post(
                "http://localhost:8000/emotion/analyze",
                params={"text": text}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"文本: {text[:30]}...")
                print(f"情感: {result['emotion']}")
                print("-" * 40)
            else:
                print(f"请求失败: {response.status_code}")
        except Exception as e:
            print(f"测试失败: {e}")

def test_emotion_status():
    """测试情感分析模型状态"""
    print("\n" + "="*60)
    print("测试情感分析模型状态")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/emotion/status")
        if response.status_code == 200:
            result = response.json()
            print(f"BERT模型已加载: {result['bert_loaded']}")
            print(f"使用设备: {result['device']}")
            print(f"支持的情感: {result['available_emotions']}")
        else:
            print(f"请求失败: {response.status_code}")
    except Exception as e:
        print(f"测试失败: {e}")

def test_chat_with_emotion():
    """测试带情感分析的聊天功能"""
    print("\n" + "="*60)
    print("测试带情感分析的聊天功能")
    print("="*60)
    
    test_messages = [
        "我今天特别开心！",
        "我很难过，想哭",
        "我生气了！",
        "哇，太不可思议了！"
    ]
    print()
    
    for message in test_messages:
        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={
                    "message": message,
                    "agent": "银狼"
                }
            )
            if response.status_code == 200:
                result = response.json()
                print(f"用户: {message}")
                print(f"AI回复: {result['response'][:100]}...")
                print(f"音频片段数: {len(result['audio_data']) if result['audio_data'] else 0}")
                print("-" * 40)
            else:
                print(f"请求失败: {response.status_code}")
        except Exception as e:
            print(f"测试失败: {e}")

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

def test_emotion_audio():
    # 使用BERT模型预测情感
    sentences =[
    "我今天特别开心！",
    "我很难过，想哭",
    "我生气了！",
    "哇，太不可思议了！"
    ]
    config_path = "/Users/ycc/workspace/Chat/collection/modelconfig.yaml"
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    agent_config = config['Agents']['银狼']
    for i,sentence in enumerate(sentences): # enumerate()的核心作用是在遍历可迭代对象时，‌同时获取元素的索引和值‌，避免手动管理计数器。其语法为：enumerate(可迭代对象, start=0)
        emotion = predict_emotion(sentence)
        print(f"句子 {i+1}: '{sentence}' -> 情感: {emotion}")
    
        # 根据情感选择对应的参考音频
        ref_audio_path = agent_config['refaudioPath'].get(emotion)
        if not ref_audio_path:
            print(f"未找到情感 '{emotion}' 的参考音频，使用中性音频")
            ref_audio_path = agent_config['refaudioPath'].get(emotion)
    
        if not ref_audio_path or not os.path.exists(ref_audio_path):
            print(f"参考音频不存在: {ref_audio_path}")
        
        # 获取参考音频的文本（从文件名提取）
        ref_audio_name = Path(ref_audio_path).stem
        print(f"参考音频: {ref_audio_path}")
        print(f"参考音频文本: {ref_audio_name}")
            

if __name__ == "__main__":
    print("开始测试情感分析和音频生成功能...")

    load_bert_model()
    # 测试带情感分析的聊天功能
    # test_chat_with_emotion()
    test_emotion_audio()
    print("\n测试完成！") 