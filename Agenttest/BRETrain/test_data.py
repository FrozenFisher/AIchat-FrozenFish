# 测试数据集 - 20条不与训练数据重复的样本
test_examples = [
    # 高兴 (label: 0) - 3个样本
    {"text": "终于考完试了，感觉整个人都轻松了！", "label": 0},  # 高兴
    {"text": "收到录取通知书的那一刻，我激动得说不出话！", "label": 0},  # 高兴
    {"text": "看到久违的朋友，心里暖暖的，特别开心！", "label": 0},  # 高兴
    
    # 悲伤 (label: 1) - 3个样本
    {"text": "听到这个消息，我的世界瞬间崩塌了", "label": 1},  # 悲伤
    {"text": "看着空荡荡的房间，心里说不出的难受", "label": 1},  # 悲伤
    {"text": "失去你的那一刻，我才知道什么是真正的痛", "label": 1},  # 悲伤
    
    # 愤怒 (label: 2) - 3个样本
    {"text": "这种不负责任的行为让我火冒三丈！", "label": 2},  # 愤怒
    {"text": "你凭什么这样对我？我受够了！", "label": 2},  # 愤怒
    {"text": "这种欺骗行为简直让人无法容忍！", "label": 2},  # 愤怒
    
    # 惊讶 (label: 3) - 3个样本
    {"text": "什么？你说的是真的吗？我不敢相信！", "label": 3},  # 惊讶
    {"text": "天哪！这个消息太震撼了！", "label": 3},  # 惊讶
    {"text": "哇！这简直太不可思议了！", "label": 3},  # 惊讶
    
    # 恐惧 (label: 4) - 3个样本
    {"text": "黑暗中传来的声音让我毛骨悚然", "label": 4},  # 恐惧
    {"text": "看到那个场景，我吓得浑身发抖", "label": 4},  # 恐惧
    {"text": "这种未知的恐惧让我无法入睡", "label": 4},  # 恐惧
    
    # 厌恶 (label: 5) - 3个样本
    {"text": "这种味道让我想吐，太恶心了", "label": 5},  # 厌恶
    {"text": "看到这种画面，我胃里一阵翻腾", "label": 5},  # 厌恶
    {"text": "这种行为让我感到极度反感", "label": 5},  # 厌恶
    
    # 中性 (label: 6) - 3个样本
    {"text": "请将报告提交到邮箱", "label": 6},  # 中性
    {"text": "明天上午九点开会", "label": 6},  # 中性
    {"text": "请按照流程操作", "label": 6},  # 中性
    
    # 害羞 (label: 7) - 3个样本
    {"text": "被这么多人看着，我有点不好意思", "label": 7},  # 害羞
    {"text": "突然被夸奖，我脸都红了", "label": 7},  # 害羞
    {"text": "在这么多人面前说话，我紧张得手心出汗", "label": 7},  # 害羞
    
    # 兴奋 (label: 8) - 3个样本
    {"text": "听到这个消息，我兴奋得跳了起来！", "label": 8},  # 兴奋
    {"text": "终于等到这一天了，我太激动了！", "label": 8},  # 兴奋
    {"text": "这个结果让我兴奋得睡不着觉！", "label": 8},  # 兴奋
    
    # 舒适 (label: 9) - 3个样本
    {"text": "躺在沙发上，听着轻音乐，感觉特别放松", "label": 9},  # 舒适
    {"text": "泡个热水澡，全身都舒服了", "label": 9},  # 舒适
    {"text": "坐在阳台上晒太阳，感觉特别惬意", "label": 9},  # 舒适
    
    # 紧张 (label: 10) - 3个样本
    {"text": "马上就要上台了，我紧张得手心冒汗", "label": 10},  # 紧张
    {"text": "面对这个挑战，我心里七上八下的", "label": 10},  # 紧张
    {"text": "等待结果的时候，我紧张得坐立不安", "label": 10},  # 紧张
    
    # 爱慕 (label: 11) - 3个样本
    {"text": "每次看到你，我的心都会加速跳动", "label": 11},  # 爱慕
    {"text": "你的笑容让我无法自拔", "label": 11},  # 爱慕
    {"text": "我想和你一起走过人生的每一个阶段", "label": 11},  # 爱慕
    
    # 委屈 (label: 12) - 3个样本
    {"text": "明明我什么都没做错，为什么要这样对我", "label": 12},  # 委屈
    {"text": "我付出了那么多，却得到这样的结果", "label": 12},  # 委屈
    {"text": "为什么总是我承担这些不公平的对待", "label": 12},  # 委屈
    
    # 骄傲 (label: 13) - 3个样本
    {"text": "这个成就让我感到无比自豪", "label": 13},  # 骄傲
    {"text": "我证明了自己的实力，这就是最好的回应", "label": 13},  # 骄傲
    {"text": "我的努力终于得到了回报，我为自己骄傲", "label": 13},  # 骄傲
    
    # 困惑 (label: 14) - 3个样本
    {"text": "这个问题让我百思不得其解", "label": 14},  # 困惑
    {"text": "我不明白为什么会出现这种情况", "label": 14},  # 困惑
    {"text": "这个结果让我感到困惑不解", "label": 14},  # 困惑
]

# 情感标签映射（与训练数据保持一致）
emotion_map = {
    0: "高兴",
    1: "悲伤", 
    2: "愤怒",
    3: "惊讶",
    4: "恐惧",
    5: "厌恶",
    6: "中性",
    7: "害羞",
    8: "兴奋",
    9: "舒适",
    10: "紧张",
    11: "爱慕",
    12: "委屈",
    13: "骄傲",
    14: "困惑"
}

def print_test_data():
    """打印测试数据统计"""
    print("="*50)
    print("测试数据集统计")
    print("="*50)
    
    # 统计每个标签的数量
    label_counts = {}
    for example in test_examples:
        label = example["label"]
        if label not in label_counts:
            label_counts[label] = 0
        label_counts[label] += 1
    
    print(f"总测试样本数: {len(test_examples)}")
    print("\n各情感标签分布:")
    for label in sorted(label_counts.keys()):
        emotion_name = emotion_map.get(label, "未知")
        count = label_counts[label]
        print(f"  {emotion_name} (label {label}): {count} 个样本")
    
    print("\n测试样本列表:")
    for i, example in enumerate(test_examples, 1):
        emotion_name = emotion_map.get(example["label"], "未知")
        print(f"{i:2d}. [{emotion_name}] {example['text']}")

if __name__ == "__main__":
    print_test_data() 