from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from transformers import DataCollatorWithPadding
from datasets import Dataset
import torch
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import os
from finetune_data import finetune_examples

def compute_metrics(pred):
    """计算评估指标"""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# 检查并创建输出目录
output_dir = "./results"
saved_model_dir = "./saved_model"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(saved_model_dir, exist_ok=True)

# 设备检查 - 修复MPS问题
print("检查可用设备...")
if torch.cuda.is_available():
    device = "cuda"
    print("使用CUDA设备")
elif torch.backends.mps.is_available():
    # 对于MPS设备，我们强制使用CPU以避免兼容性问题
    device = "cpu"
    print("检测到MPS设备，但使用CPU以避免兼容性问题")
else:
    device = "cpu"
    print("使用CPU设备")

# 数据增强 - 通过重复和变体来增加训练数据
def augment_data(examples):
    """简单的数据增强"""
    augmented_examples = []
    
    for example in examples:
        # 原始样本
        augmented_examples.append(example)
        
        # 变体1：添加标点符号
        text = example["text"]
        if not text.endswith(("！", "？", "。", "~", "...")):
            variant1 = {"text": text + "！", "label": example["label"]}
            augmented_examples.append(variant1)
        
        # 变体2：重复关键词
        if "开心" in text or "高兴" in text or "棒" in text:
            variant2 = {"text": text.replace("！", "！太棒了！"), "label": example["label"]}
            augmented_examples.append(variant2)
        
        # 变体3：添加语气词
        if example["label"] in [0, 8]:  # 高兴、兴奋
            variant3 = {"text": "哇！" + text, "label": example["label"]}
            augmented_examples.append(variant3)
        elif example["label"] in [1, 12]:  # 悲伤、委屈
            variant3 = {"text": "唉，" + text, "label": example["label"]}
            augmented_examples.append(variant3)
    
    return augmented_examples

print("正在进行数据增强...")
augmented_examples = augment_data(finetune_examples)
print(f"数据增强后样本数: {len(augmented_examples)} (原始: {len(finetune_examples)})")

# 准备数据集
texts = [example["text"] for example in augmented_examples]
labels = [example["label"] for example in augmented_examples]

# 分割训练集和验证集
train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, labels, test_size=0.15, random_state=42, stratify=labels
)

# 加载预训练模型
print("正在加载预训练模型...")
tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
model = BertForSequenceClassification.from_pretrained("bert-base-chinese", num_labels=15)

# 对训练集和验证集进行tokenization
print("正在处理训练数据...")
train_tokenized = tokenizer(train_texts, truncation=True, padding=True, max_length=128)  # 减少max_length
val_tokenized = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

# 创建数据集
train_dataset = Dataset.from_dict({
    "input_ids": train_tokenized["input_ids"],
    "attention_mask": train_tokenized["attention_mask"],
    "labels": train_labels
})

val_dataset = Dataset.from_dict({
    "input_ids": val_tokenized["input_ids"],
    "attention_mask": val_tokenized["attention_mask"],
    "labels": val_labels
})

print(f"训练集大小: {len(train_dataset)}")
print(f"验证集大小: {len(val_dataset)}")

# 训练参数 - 优化参数解决欠拟合
training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=15,  # 增加训练轮数
    per_device_train_batch_size=4,  # 减小batch size
    per_device_eval_batch_size=4,
    learning_rate=2e-5,  # 降低学习率
    warmup_steps=100,  # 减少warmup
    weight_decay=0.01,
    logging_dir="./logs",
    eval_strategy="steps",
    eval_steps=100,  # 更频繁的评估
    save_strategy="steps",
    save_steps=100,
    save_total_limit=5,  # 保存更多检查点
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    report_to=None,
    no_cuda=True,  # 强制使用CPU
    dataloader_pin_memory=False,
    gradient_accumulation_steps=2,  # 梯度累积
    fp16=False,  # 禁用混合精度
    remove_unused_columns=False,  # 保留所有列
)

# 创建Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics,
)

# 开始训练
print("开始训练...")
trainer.train()

# 在验证集上评估
print("在验证集上评估模型...")
eval_results = trainer.evaluate()
print(f"验证集结果: {eval_results}")

# 保存模型
print("保存模型...")
model.save_pretrained(saved_model_dir)
tokenizer.save_pretrained(saved_model_dir)
print(f"模型已保存到: {saved_model_dir}")