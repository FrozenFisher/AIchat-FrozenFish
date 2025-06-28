import re

def split_text_for_audio(text: str) -> tuple[list[str], list[str]]:
    """将文本分割为适合音频生成的句子
    返回: (bert_sentences, audio_sentences)
    bert_sentences: 包含圆括号内容的句子，用于BERT情感预测
    audio_sentences: 去除圆括号内容的句子，用于音频生成
    """
    # 过滤掉<think></think>标签及其内容
    text_without_think = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # 按标点符号分割，保留圆括号内容
    bert_sentences = re.findall(r'[^.!?;:。！？：；]*[.!?;:。！？：；]*', text_without_think)
    bert_sentences = [s.strip() for s in bert_sentences if s.strip()]
    
    # 去除圆括号中的内容，用于音频生成
    text_clean = re.sub(r'（.*?）|\(.*?\)', '', text_without_think)
    audio_sentences = re.findall(r'[^.!?;:。！？：；]*[.!?;:。！？：；]*', text_clean)
    audio_sentences = [s.strip() for s in audio_sentences if s.strip()]
    
    return bert_sentences, audio_sentences

# 测试可能导致长度不匹配的用例
test_cases = [
    "（叹气）。今天天气真好。",
    "（开心地笑）（挥手）。你好。",
    "（皱眉）（叹气）。这个任务很难。",
    "（高兴）你好（挥手）。我是小明（开心）。",
    # 添加更多极端情况
    "（叹气）（皱眉）（摇头）。",
    "（开心）（兴奋）（激动）！",
    "（叹气）。。（开心）。",
    "（叹气）（叹气）（叹气）。",
    "（叹气）。（叹气）。（叹气）。",
    "（叹气）（叹气）（叹气）。（开心）。",
]

print("测试可能导致长度不匹配的用例:")
for i, test_case in enumerate(test_cases):
    print(f"\n测试用例 {i+1}: '{test_case}'")
    bert_sentences, audio_sentences = split_text_for_audio(test_case)
    print(f"BERT句子 ({len(bert_sentences)}): {bert_sentences}")
    print(f"音频句子 ({len(audio_sentences)}): {audio_sentences}")
    if len(bert_sentences) != len(audio_sentences):
        print("❌ 长度不匹配！")
    else:
        print("✅ 长度匹配") 