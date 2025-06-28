"""
训练效果分析脚本

分析BERT情感分类模型的训练效果
统计准确率、置信度分布、混淆矩阵等指标
"""

import numpy as np
from collections import defaultdict, Counter

# 测试数据及其真实标签
test_data = [
    # 高兴 (label: 0)
    ("终于考完试了，感觉整个人都轻松了！", "高兴"),
    ("收到录取通知书的那一刻，我激动得说不出话！", "高兴"),
    ("看到久违的朋友，心里暖暖的，特别开心！", "高兴"),
    
    # 悲伤 (label: 1)
    ("听到这个消息，我的世界瞬间崩塌了", "悲伤"),
    ("看着空荡荡的房间，心里说不出的难受", "悲伤"),
    ("失去你的那一刻，我才知道什么是真正的痛", "悲伤"),
    
    # 愤怒 (label: 2)
    ("这种不负责任的行为让我火冒三丈！", "愤怒"),
    ("你凭什么这样对我？我受够了！", "愤怒"),
    ("这种欺骗行为简直让人无法容忍！", "愤怒"),
    
    # 惊讶 (label: 3)
    ("什么？你说的是真的吗？我不敢相信！", "惊讶"),
    ("天哪！这个消息太震撼了！", "惊讶"),
    ("哇！这简直太不可思议了！", "惊讶"),
    
    # 恐惧 (label: 4)
    ("黑暗中传来的声音让我毛骨悚然", "恐惧"),
    ("看到那个场景，我吓得浑身发抖", "恐惧"),
    ("这种未知的恐惧让我无法入睡", "恐惧"),
    
    # 厌恶 (label: 5)
    ("这种味道让我想吐，太恶心了", "厌恶"),
    ("看到这种画面，我胃里一阵翻腾", "厌恶"),
    ("这种行为让我感到极度反感", "厌恶"),
    
    # 中性 (label: 6)
    ("请将报告提交到邮箱", "中性"),
    ("明天上午九点开会", "中性"),
    ("请按照流程操作", "中性"),
    
    # 害羞 (label: 7)
    ("被这么多人看着，我有点不好意思", "害羞"),
    ("突然被夸奖，我脸都红了", "害羞"),
    ("在这么多人面前说话，我紧张得手心出汗", "害羞"),
    
    # 兴奋 (label: 8)
    ("听到这个消息，我兴奋得跳了起来！", "兴奋"),
    ("终于等到这一天了，我太激动了！", "兴奋"),
    ("这个结果让我兴奋得睡不着觉！", "兴奋"),
    
    # 舒适 (label: 9)
    ("躺在沙发上，听着轻音乐，感觉特别放松", "舒适"),
    ("泡个热水澡，全身都舒服了", "舒适"),
    ("坐在阳台上晒太阳，感觉特别惬意", "舒适"),
    
    # 紧张 (label: 10)
    ("马上就要上台了，我紧张得手心冒汗", "紧张"),
    ("面对这个挑战，我心里七上八下的", "紧张"),
    ("等待结果的时候，我紧张得坐立不安", "紧张"),
    
    # 爱慕 (label: 11)
    ("每次看到你，我的心都会加速跳动", "爱慕"),
    ("你的笑容让我无法自拔", "爱慕"),
    ("我想和你一起走过人生的每一个阶段", "爱慕"),
    
    # 委屈 (label: 12)
    ("明明我什么都没做错，为什么要这样对我", "委屈"),
    ("我付出了那么多，却得到这样的结果", "委屈"),
    ("为什么总是我承担这些不公平的对待", "委屈"),
    
    # 骄傲 (label: 13)
    ("这个成就让我感到无比自豪", "骄傲"),
    ("我证明了自己的实力，这就是最好的回应", "骄傲"),
    ("我的努力终于得到了回报，我为自己骄傲", "骄傲"),
    
    # 困惑 (label: 14)
    ("这个问题让我百思不得其解", "困惑"),
    ("我不明白为什么会出现这种情况", "困惑"),
    ("这个结果让我感到困惑不解", "困惑"),
]

# 实际测试结果（从运行输出中提取）
actual_results = [
    ("高兴", 0.5234), ("高兴", 0.2506), ("高兴", 0.7056),
    ("悲伤", 0.1958), ("厌恶", 0.2056), ("愤怒", 0.1333),
    ("愤怒", 0.2494), ("愤怒", 0.4555), ("愤怒", 0.2627),
    ("惊讶", 0.3690), ("惊讶", 0.3657), ("兴奋", 0.4735),
    ("厌恶", 0.1656), ("厌恶", 0.1833), ("厌恶", 0.2013),
    ("厌恶", 0.6776), ("厌恶", 0.2143), ("厌恶", 0.2137),
    ("中性", 0.8613), ("中性", 0.7583), ("中性", 0.8492),
    ("愤怒", 0.1886), ("兴奋", 0.3192), ("愤怒", 0.1428),
    ("高兴", 0.2750), ("兴奋", 0.6243), ("兴奋", 0.3855),
    ("舒适", 0.1753), ("舒适", 0.3957), ("高兴", 0.1992),
    ("兴奋", 0.4654), ("愤怒", 0.1484), ("兴奋", 0.2272),
    ("高兴", 0.1789), ("悲伤", 0.3487), ("爱慕", 0.2980),
    ("委屈", 0.3594), ("兴奋", 0.2140), ("委屈", 0.2796),
    ("骄傲", 0.2434), ("骄傲", 0.2986), ("骄傲", 0.2674),
    ("困惑", 0.2231), ("中性", 0.1729), ("中性", 0.1636),
]

def analyze_training_effectiveness():
    """分析训练效果"""
    
    # 统计准确率
    correct = 0
    total = len(test_data)
    emotion_accuracy = defaultdict(lambda: {"correct": 0, "total": 0})
    confidence_by_emotion = defaultdict(list)
    
    print("="*80)
    print("BERT情感分析训练效果分析")
    print("="*80)
    
    for i, ((text, true_emotion), (pred_emotion, confidence)) in enumerate(zip(test_data, actual_results)):
        is_correct = true_emotion == pred_emotion
        if is_correct:
            correct += 1
            emotion_accuracy[true_emotion]["correct"] += 1
        emotion_accuracy[true_emotion]["total"] += 1
        confidence_by_emotion[true_emotion].append(confidence)
        
        print(f"测试 {i+1:2d}: {true_emotion:4s} -> {pred_emotion:4s} "
              f"[{'✓' if is_correct else '✗'}] 置信度: {confidence:.4f}")
    
    # 总体准确率
    overall_accuracy = correct / total
    print(f"\n总体准确率: {overall_accuracy:.2%} ({correct}/{total})")
    
    # 各类别准确率
    print("\n各类别准确率:")
    print("-" * 40)
    for emotion in sorted(emotion_accuracy.keys()):
        acc = emotion_accuracy[emotion]["correct"] / emotion_accuracy[emotion]["total"]
        avg_conf = np.mean(confidence_by_emotion[emotion])
        print(f"{emotion:4s}: {acc:.2%} (置信度: {avg_conf:.4f})")
    
    # 置信度分析
    print(f"\n置信度统计:")
    print(f"平均置信度: {np.mean([conf for _, conf in actual_results]):.4f}")
    print(f"最高置信度: {max([conf for _, conf in actual_results]):.4f}")
    print(f"最低置信度: {min([conf for _, conf in actual_results]):.4f}")
    
    # 问题分析
    print(f"\n主要问题分析:")
    print("-" * 40)
    
    # 1. 低置信度问题
    low_confidence = [conf for _, conf in actual_results if conf < 0.3]
    print(f"低置信度样本 (<0.3): {len(low_confidence)}/{total} ({len(low_confidence)/total:.2%})")
    
    # 2. 错误分类分析
    error_cases = []
    for (text, true_emotion), (pred_emotion, confidence) in zip(test_data, actual_results):
        if true_emotion != pred_emotion:
            error_cases.append((true_emotion, pred_emotion, confidence))
    
    print(f"错误分类样本: {len(error_cases)}/{total} ({len(error_cases)/total:.2%})")
    
    # 3. 常见错误模式
    error_patterns = Counter([(true, pred) for true, pred, _ in error_cases])
    print(f"\n常见错误模式:")
    for (true, pred), count in error_patterns.most_common(5):
        print(f"  {true} -> {pred}: {count}次")
    
    # 4. 建议改进方向
    print(f"\n改进建议:")
    print("-" * 40)
    
    if overall_accuracy < 0.7:
        print("1. 模型准确率偏低，建议:")
        print("   - 增加训练数据量")
        print("   - 调整学习率和训练轮数")
        print("   - 使用数据增强技术")
    
    if len(low_confidence) / total > 0.3:
        print("2. 低置信度样本较多，建议:")
        print("   - 增加训练数据的多样性")
        print("   - 调整模型架构或超参数")
        print("   - 使用集成学习方法")
    
    # 找出表现最差的类别
    worst_emotions = sorted(emotion_accuracy.items(), 
                          key=lambda x: x[1]["correct"] / x[1]["total"])[:3]
    print("3. 表现较差的类别:")
    for emotion, stats in worst_emotions:
        acc = stats["correct"] / stats["total"]
        print(f"   {emotion}: {acc:.2%} - 需要更多训练数据")
    
    return {
        "overall_accuracy": overall_accuracy,
        "emotion_accuracy": emotion_accuracy,
        "confidence_stats": {
            "mean": np.mean([conf for _, conf in actual_results]),
            "std": np.std([conf for _, conf in actual_results]),
            "min": min([conf for _, conf in actual_results]),
            "max": max([conf for _, conf in actual_results])
        },
        "error_cases": error_cases
    }

if __name__ == "__main__":
    results = analyze_training_effectiveness() 