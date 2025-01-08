import pynini
from nltk.tokenize import sent_tokenize

# 假设我们有一段文本
text = """自然语言处理是人工智能领域的重要组成部分。它涉及计算机与人类语言之间的互动。"""
sentences = sent_tokenize(text)

# 简单选择前两句话作为摘录
summary_sentences = sentences[:2]

# 创建FST以确保输出格式一致
fst = pynini.string_map([("自然语言处理", "NLP"), ("人工智能", "AI")])

# 应用FST对每个选定句子进行格式化，并提取结果字符串
formatted_summary = [str(fst @ sentence) for sentence in summary_sentences]

# 输出最终总结
final_summary = ' '.join(formatted_summary)
print(final_summary)
