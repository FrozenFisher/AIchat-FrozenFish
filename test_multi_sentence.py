import requests
import time

def test_multi_sentence_chat():
    """测试多句音频生成"""
    server_url = "http://127.0.0.1:8000/chat"
    
    # 测试包含多个句子的回复
    test_messages = [
        "你好，请介绍一下你自己。",
        "今天天气怎么样？你能告诉我吗？",
        "讲个笑话吧，我想开心一下。",
        "谢谢你的帮助，再见！"
    ]
    
    for i, message in enumerate(test_messages):
        payload = {
            "message": message,
            "agent": "银狼"
        }
        
        print(f"\n🔄 测试 {i+1}: {message}")
        start_time = time.time()
        
        try:
            resp = requests.post(server_url, json=payload, timeout=120)
            end_time = time.time()
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ 请求成功 (耗时: {end_time - start_time:.2f}s)")
                print(f"回复: {data['response'][:100]}...")
                
                if data.get("audio_data"):
                    print(f"音频片段数量: {len(data['audio_data'])}")
                    for j, audio in enumerate(data['audio_data']):
                        print(f"  片段 {j+1}: {len(audio)} 字符")
                else:
                    print("无音频数据")
            else:
                print(f"❌ 请求失败: {resp.status_code}")
                print(f"错误: {resp.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        # 等待一下再发送下一个请求
        time.sleep(2)

if __name__ == "__main__":
    print("🚀 开始多句音频生成测试")
    print("=" * 50)
    test_multi_sentence_chat()
    print("=" * 50)
    print("🎯 测试完成！") 