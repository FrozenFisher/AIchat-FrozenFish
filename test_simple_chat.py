import requests
import time

def test_single_chat():
    """测试单个聊天请求"""
    server_url = "http://127.0.0.1:8000/chat"
    payload = {
        "message": "你好，请介绍一下你自己。",
        "agent": "银狼"
    }
    
    print("🔄 发送聊天请求...")
    start_time = time.time()
    
    try:
        resp = requests.post(server_url, json=payload, timeout=60)
        end_time = time.time()
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ 请求成功 (耗时: {end_time - start_time:.2f}s)")
            print(f"回复: {data['response'][:100]}...")
            
            if data.get("audio_data"):
                print(f"音频数据: {len(data['audio_data'])} 个片段")
                for i, audio in enumerate(data['audio_data']):
                    print(f"  片段 {i+1}: {len(audio)} 字符")
            else:
                print("无音频数据")
        else:
            print(f"❌ 请求失败: {resp.status_code}")
            print(f"错误: {resp.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_single_chat() 