import requests
import threading
import time
import base64
import os
from pathlib import Path

def save_base64_audio(audio_base64, filename):
    """保存base64音频为wav文件"""
    audio_bytes = base64.b64decode(audio_base64)
    with open(filename, "wb") as f:
        f.write(audio_bytes)
    print(f"音频已保存: {filename}")

def chat_request(message, agent, session_id, request_id):
    """发送聊天请求"""
    server_url = "http://127.0.0.1:8000/chat"
    payload = {
        "message": message,
        "agent": agent,
        "session_id": session_id
    }
    
    print(f"🔄 请求 {request_id} 开始: {message[:20]}...")
    start_time = time.time()
    
    try:
        resp = requests.post(server_url, json=payload, timeout=60)
        end_time = time.time()
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ 请求 {request_id} 成功 (耗时: {end_time - start_time:.2f}s)")
            print(f"   回复: {data['response'][:50]}...")
            
            # 保存音频文件
            if data.get("audio_data"):
                os.makedirs("temp", exist_ok=True)
                for idx, audio_base64 in enumerate(data["audio_data"]):
                    filename = f"temp/chat_{request_id}_{idx+1}.wav"
                    save_base64_audio(audio_base64, filename)
            else:
                print(f"   无音频数据")
        else:
            print(f"❌ 请求 {request_id} 失败: {resp.status_code}")
            print(f"   错误: {resp.text}")
            
    except Exception as e:
        print(f"❌ 请求 {request_id} 异常: {e}")

def test_concurrent_requests():
    """测试并发请求"""
    print("🚀 开始并发聊天请求测试")
    print("=" * 50)
    
    # 创建多个线程同时发送请求
    threads = []
    messages = [
        "你好，请介绍一下你自己。",
        "今天天气怎么样？",
        "你能做什么？",
        "讲个笑话吧。",
        "谢谢你的帮助。"
    ]
    
    # 启动多个线程
    for i, message in enumerate(messages):
        thread = threading.Thread(
            target=chat_request,
            args=(message, "银狼", f"test_session_{i}", f"req_{i+1}")
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # 稍微错开启动时间
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("=" * 50)
    print("🎯 并发测试完成！")
    print("请检查temp目录下的音频文件，确认是否有参考音频混入问题")

if __name__ == "__main__":
    test_concurrent_requests() 