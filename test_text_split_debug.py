#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def split_text_for_audio(text: str) -> tuple[list[str], list[str]]:
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

def test_text_split():
    """测试文本分割函数"""
    test_text = "银狼: (开心地蹭蹭你的手)呜~好舒服！再多摸摸嘛~"
    
    print("=" * 50)
    print("测试修改后的文本分割函数")
    print("=" * 50)
    print(f"输入文本: {test_text}")
    print()
    
    # 测试分割
    bert_sentences, audio_sentences = split_text_for_audio(test_text)
    
    print("分割结果:")
    print(f"BERT句子数量: {len(bert_sentences)}")
    print(f"音频句子数量: {len(audio_sentences)}")
    print()
    
    for i, (bert_sent, audio_sent) in enumerate(zip(bert_sentences, audio_sentences)):
        print(f"句子 {i+1}:")
        print(f"  BERT输入: '{bert_sent}'")
        print(f"  音频输入: '{audio_sent}'")
        print()
    
    # 分析问题
    print("问题分析:")
    if len(bert_sentences) < 3:
        print(f"❌ 期望至少3句（角色名+2句内容），实际{len(bert_sentences)}句")
    else:
        print("✅ 句子数量正确")
    
    # 过滤掉角色名，只保留有效内容
    valid_bert_sentences = [s for s in bert_sentences if not s.endswith(':')]
    valid_audio_sentences = [s for s in audio_sentences if not s.endswith(':')]
    
    print(f"\n有效内容句子数量: {len(valid_bert_sentences)}")
    for i, (bert_sent, audio_sent) in enumerate(zip(valid_bert_sentences, valid_audio_sentences)):
        print(f"有效句子 {i+1}:")
        print(f"  BERT输入: '{bert_sent}'")
        print(f"  音频输入: '{audio_sent}'")
        print()

if __name__ == "__main__":
    test_text_split() 