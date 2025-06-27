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