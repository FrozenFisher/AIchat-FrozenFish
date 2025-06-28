"""
数据验证脚本
检查 finetune_data.py 中的数据质量和格式
"""

from finetune_data import finetune_examples, emotion_map
from collections import Counter
import re

def validate_data():
    """验证训练数据的质量和格式"""
    print("="*50)
    print("数据验证报告")
    print("="*50)
    
    # 1. 检查数据数量
    print(f"\n1. 数据数量统计:")
    print(f"   总样本数: {len(finetune_examples)}")
    
    # 2. 检查标签分布
    labels = [example["label"] for example in finetune_examples]
    label_counts = Counter(labels)
    
    print(f"\n2. 标签分布:")
    for label in sorted(label_counts.keys()):
        emotion_name = emotion_map.get(label, "未知")
        count = label_counts[label]
        print(f"   {emotion_name} (label {label}): {count} 个样本")
    
    # 3. 检查标签范围
    print(f"\n3. 标签范围检查:")
    min_label = min(labels)
    max_label = max(labels)
    print(f"   最小标签: {min_label}")
    print(f"   最大标签: {max_label}")
    
    if min_label < 0 or max_label > 14:
        print("   ❌ 错误: 标签超出范围 [0, 14]")
    else:
        print("   ✅ 标签范围正确")
    
    # 4. 检查数据格式
    print(f"\n4. 数据格式检查:")
    format_errors = []
    for i, example in enumerate(finetune_examples):
        if not isinstance(example, dict):
            format_errors.append(f"样本 {i}: 不是字典格式")
            continue
            
        if "text" not in example:
            format_errors.append(f"样本 {i}: 缺少 'text' 字段")
        elif not isinstance(example["text"], str):
            format_errors.append(f"样本 {i}: 'text' 不是字符串")
            
        if "label" not in example:
            format_errors.append(f"样本 {i}: 缺少 'label' 字段")
        elif not isinstance(example["label"], int):
            format_errors.append(f"样本 {i}: 'label' 不是整数")
    
    if format_errors:
        print("   ❌ 发现格式错误:")
        for error in format_errors[:5]:  # 只显示前5个错误
            print(f"      {error}")
        if len(format_errors) > 5:
            print(f"      ... 还有 {len(format_errors) - 5} 个错误")
    else:
        print("   ✅ 数据格式正确")
    
    # 5. 检查文本长度
    print(f"\n5. 文本长度统计:")
    text_lengths = [len(example["text"]) for example in finetune_examples]
    print(f"   最短文本: {min(text_lengths)} 字符")
    print(f"   最长文本: {max(text_lengths)} 字符")
    print(f"   平均长度: {sum(text_lengths) / len(text_lengths):.1f} 字符")
    
    # 6. 检查重复文本
    print(f"\n6. 重复文本检查:")
    texts = [example["text"] for example in finetune_examples]
    text_counts = Counter(texts)
    duplicates = [text for text, count in text_counts.items() if count > 1]
    
    if duplicates:
        print(f"   ⚠️  发现 {len(duplicates)} 个重复文本:")
        for text in duplicates[:3]:  # 只显示前3个
            print(f"      '{text[:50]}{'...' if len(text) > 50 else ''}'")
        if len(duplicates) > 3:
            print(f"      ... 还有 {len(duplicates) - 3} 个重复文本")
    else:
        print("   ✅ 没有重复文本")
    
    # 7. 检查特殊字符
    print(f"\n7. 特殊字符检查:")
    special_chars = []
    for example in finetune_examples:
        text = example["text"]
        # 检查是否包含特殊字符
        if re.search(r'[^\u4e00-\u9fff\w\s\(\)（），。！？~…—""''、：；]', text):
            special_chars.append(text)
    
    if special_chars:
        print(f"   ⚠️  发现 {len(special_chars)} 个包含特殊字符的文本")
        for text in special_chars[:3]:
            print(f"      '{text[:50]}{'...' if len(text) > 50 else ''}'")
    else:
        print("   ✅ 没有发现特殊字符")
    
    # 8. 检查数据平衡性
    print(f"\n8. 数据平衡性检查:")
    expected_samples_per_label = 10
    unbalanced_labels = []
    
    for label in range(15):
        count = label_counts.get(label, 0)
        if count != expected_samples_per_label:
            emotion_name = emotion_map.get(label, "未知")
            unbalanced_labels.append(f"{emotion_name} (label {label}): {count} 个样本")
    
    if unbalanced_labels:
        print("   ⚠️  发现不平衡的标签:")
        for label_info in unbalanced_labels:
            print(f"      {label_info}")
    else:
        print("   ✅ 所有标签都有10个样本，数据平衡")
    
    # 9. 总体评估
    print(f"\n9. 总体评估:")
    total_issues = len(format_errors) + len(duplicates) + len(unbalanced_labels)
    
    if total_issues == 0:
        print("   ✅ 数据质量优秀，可以直接用于训练")
    elif total_issues <= 5:
        print("   ⚠️  数据质量良好，有少量问题需要修复")
    else:
        print("   ❌ 数据质量较差，需要修复多个问题")
    
    print(f"\n总共发现 {total_issues} 个问题")

if __name__ == "__main__":
    validate_data() 