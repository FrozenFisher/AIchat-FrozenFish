"""
BERT情感分析测试脚本

测试中文文本情感分类功能
支持: 高兴/悲伤/愤怒/惊讶/恐惧/厌恶/中性/害羞/兴奋/舒适/紧张/爱慕/委屈/骄傲/困惑
"""

from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import torch

# 初始化模型
model_name = "bert-base-chinese"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=15)

# 创建情感分析pipeline
sentiment_analyzer = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    framework="pt",
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# 测试数据
test_cases = [
    "今天天气真好，阳光明媚！",  # 高兴
    "我很难过，因为失去了重要的人",  # 悲伤
    "这种行为简直不可理喻！",  # 愤怒
    "天啊！我简直不敢相信！",  # 惊讶
    "黑暗的房间里好像有什么东西在动...",  # 恐惧
    "这食物闻起来像腐烂了一样",  # 厌恶
    "会议室在二楼，下午三点开会" , # 中性
    "(耳朵突然竖起，尾巴快速摆动)当然可以啦~不过要轻轻的哦！(害羞地把尾巴往前递了递)",
    "(发出舒服的呼噜声，整个人都软绵绵地靠过来)唔...好舒服...再多摸摸嘛~(眯着眼睛，尾巴愉快地摇晃)",
    "(舒服地眯起眼睛) 呜...好舒服~再、再多摸一会儿嘛...(尾巴不自觉地缠上你的手腕)",
    "（突然被碰到尾巴根部，浑身一颤，耳朵瞬间竖起）呜...！别、别碰那里...（下意识往前躲了躲，尾巴炸毛蓬成一团）那里很敏感的...（声音越来越小，脸红着把尾巴抱到胸前挡住）",
    "（瞳孔猛地收缩，兽耳“噗”地炸出绒毛）呜...！等、你犯规...（被亲得踉跄后退抵到墙角，尾巴却诚实地缠上你的手腕）  ",
    "...法术全崩掉了哦？（呼吸乱糟糟地埋在你肩头，尖牙轻轻磨你衣领）这下...要负责帮我重新施一遍咒才行...  "

]

# 情感标签映射
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

# 运行测试
print("="*50)
print("BERT情感分析测试")
print("="*50)

for text in test_cases:
    result = sentiment_analyzer(text)
    label = int(result[0]['label'].split('_')[-1])
    print(f"文本: {text}")
    print(f"情感分析结果: {emotion_map[label]}")
    print(f"置信度: {result[0]['score']:.4f}")
    print("-"*50)

print("测试完成")