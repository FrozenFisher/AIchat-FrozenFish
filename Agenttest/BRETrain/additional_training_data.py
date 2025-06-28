"""
为恐惧、害羞、紧张类别生成额外训练样本

根据训练效果分析，这三个类别表现最差（0%准确率），需要增加训练数据
"""

# 恐惧类别 (label: 4) - 30个样本
fear_samples = [
    {"text": "黑暗中传来的脚步声让我毛骨悚然", "label": 4},
    {"text": "看到那个场景，我吓得浑身发抖", "label": 4},
    {"text": "这种未知的恐惧让我无法入睡", "label": 4},
    {"text": "听到这个消息，我害怕得说不出话", "label": 4},
    {"text": "面对这个挑战，我心里充满了恐惧", "label": 4},
    {"text": "那个声音让我感到极度恐惧", "label": 4},
    {"text": "我害怕失去你", "label": 4},
    {"text": "这种恐惧感让我无法呼吸", "label": 4},
    {"text": "看到那个画面，我吓得魂飞魄散", "label": 4},
    {"text": "我害怕面对这个结果", "label": 4},
    {"text": "这种恐惧让我想要逃跑", "label": 4},
    {"text": "我害怕明天的考试", "label": 4},
    {"text": "那个噩梦让我感到恐惧", "label": 4},
    {"text": "我害怕孤独", "label": 4},
    {"text": "这种恐惧感让我无法集中注意力", "label": 4},
    {"text": "我害怕失败", "label": 4},
    {"text": "那个想法让我感到恐惧", "label": 4},
    {"text": "我害怕改变", "label": 4},
    {"text": "这种恐惧让我想要躲起来", "label": 4},
    {"text": "我害怕未知的未来", "label": 4},
    {"text": "那个声音让我感到恐惧", "label": 4},
    {"text": "我害怕被拒绝", "label": 4},
    {"text": "这种恐惧感让我无法前进", "label": 4},
    {"text": "我害怕失去控制", "label": 4},
    {"text": "那个场景让我感到恐惧", "label": 4},
    {"text": "我害怕承担责任", "label": 4},
    {"text": "这种恐惧让我想要放弃", "label": 4},
    {"text": "我害怕面对现实", "label": 4},
    {"text": "那个想法让我感到恐惧", "label": 4},
    {"text": "我害怕被误解", "label": 4},
]

# 害羞类别 (label: 7) - 30个样本
shy_samples = [
    {"text": "被这么多人看着，我有点不好意思", "label": 7},
    {"text": "突然被夸奖，我脸都红了", "label": 7},
    {"text": "在这么多人面前说话，我紧张得手心出汗", "label": 7},
    {"text": "我不好意思表达自己的想法", "label": 7},
    {"text": "被当众表扬让我感到害羞", "label": 7},
    {"text": "我不好意思主动搭话", "label": 7},
    {"text": "在陌生人面前我总是很害羞", "label": 7},
    {"text": "我不好意思展示自己的作品", "label": 7},
    {"text": "被关注让我感到不自在", "label": 7},
    {"text": "我不好意思说出自己的感受", "label": 7},
    {"text": "在公共场合我总是很害羞", "label": 7},
    {"text": "我不好意思接受别人的好意", "label": 7},
    {"text": "被拍照让我感到害羞", "label": 7},
    {"text": "我不好意思提出要求", "label": 7},
    {"text": "在老师面前我总是很害羞", "label": 7},
    {"text": "我不好意思展示自己的才艺", "label": 7},
    {"text": "被介绍给陌生人让我害羞", "label": 7},
    {"text": "我不好意思表达爱意", "label": 7},
    {"text": "在异性面前我总是很害羞", "label": 7},
    {"text": "我不好意思承认自己的错误", "label": 7},
    {"text": "被当众批评让我感到害羞", "label": 7},
    {"text": "我不好意思寻求帮助", "label": 7},
    {"text": "在长辈面前我总是很害羞", "label": 7},
    {"text": "我不好意思展示自己的优点", "label": 7},
    {"text": "被关注让我想要躲起来", "label": 7},
    {"text": "我不好意思说出自己的梦想", "label": 7},
    {"text": "在重要场合我总是很害羞", "label": 7},
    {"text": "我不好意思表达自己的观点", "label": 7},
    {"text": "被当众点名让我感到害羞", "label": 7},
    {"text": "我不好意思展示自己的努力", "label": 7},
]

# 紧张类别 (label: 10) - 30个样本
nervous_samples = [
    {"text": "马上就要上台了，我紧张得手心冒汗", "label": 10},
    {"text": "面对这个挑战，我心里七上八下的", "label": 10},
    {"text": "等待结果的时候，我紧张得坐立不安", "label": 10},
    {"text": "我紧张得说不出话来", "label": 10},
    {"text": "面对这个决定，我心里很紧张", "label": 10},
    {"text": "我紧张得心跳加速", "label": 10},
    {"text": "面对这个任务，我感到很紧张", "label": 10},
    {"text": "我紧张得手心出汗", "label": 10},
    {"text": "面对这个考试，我很紧张", "label": 10},
    {"text": "我紧张得无法集中注意力", "label": 10},
    {"text": "面对这个面试，我很紧张", "label": 10},
    {"text": "我紧张得想要逃跑", "label": 10},
    {"text": "面对这个演讲，我很紧张", "label": 10},
    {"text": "我紧张得想要放弃", "label": 10},
    {"text": "面对这个比赛，我很紧张", "label": 10},
    {"text": "我紧张得想要躲起来", "label": 10},
    {"text": "面对这个约会，我很紧张", "label": 10},
    {"text": "我紧张得想要推迟", "label": 10},
    {"text": "面对这个会议，我很紧张", "label": 10},
    {"text": "我紧张得想要取消", "label": 10},
    {"text": "面对这个表演，我很紧张", "label": 10},
    {"text": "我紧张得想要退出", "label": 10},
    {"text": "面对这个挑战，我很紧张", "label": 10},
    {"text": "我紧张得想要逃避", "label": 10},
    {"text": "面对这个责任，我很紧张", "label": 10},
    {"text": "我紧张得想要拒绝", "label": 10},
    {"text": "面对这个机会，我很紧张", "label": 10},
    {"text": "我紧张得想要放弃", "label": 10},
    {"text": "面对这个决定，我很紧张", "label": 10},
    {"text": "我紧张得想要拖延", "label": 10},
    {"text": "面对这个变化，我很紧张", "label": 10},
    {"text": "我紧张得想要保持现状", "label": 10},
    {"text": "面对这个未知，我很紧张", "label": 10},
    {"text": "我紧张得想要退缩", "label": 10},
]

def print_samples_for_copy():
    """打印样本供手动复制"""
    print("="*80)
    print("恐惧类别样本 (label: 4) - 30个")
    print("="*80)
    for sample in fear_samples:
        print(f'    {sample},')
    
    print("\n" + "="*80)
    print("害羞类别样本 (label: 7) - 30个")
    print("="*80)
    for sample in shy_samples:
        print(f'    {sample},')
    
    print("\n" + "="*80)
    print("紧张类别样本 (label: 10) - 30个")
    print("="*80)
    for sample in nervous_samples:
        print(f'    {sample},')
    
    print(f"\n总计: {len(fear_samples) + len(shy_samples) + len(nervous_samples)} 个样本")
    print("请将这些样本手动添加到 finetune_data.py 的训练数据中")

if __name__ == "__main__":
    print_samples_for_copy() 