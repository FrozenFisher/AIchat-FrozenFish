
from langchain_community.llms import Xinference
from xinference.client import Client
import openai
"""
endpoint = "http://127.0.0.1:9997"
model_name = "qwen2-instruct"
model_size_in_billions = "7"
model_format = "pytorch"
model_engine = "Transformers"
quantization = "none"

print(f"Xinference endpoint: {endpoint}")
print(f"Model Name: {model_name}")
print(f"Model Size (in billions): {model_size_in_billions}")
print(f"Model Format: {model_format}")
print(f"Quantization: {quantization}")
# 启动大模型
client = Client(endpoint)
model_uid = client.launch_model(
    model_name=model_name,
    model_engine=model_engine,
    model_size_in_billions=model_size_in_billions,
    model_format=model_format,
    quantization=quantization,
)
model = client.get_model(model_uid)


llm = Xinference(
    server_url="http://0.0.0.0:9997/v1",
    model_uid = {"qwen2-instruct"} # replace model_uid with the model UID return from launching the model
)

llm(
    prompt="Q: where can we visit in the capital of France? A:",
    generate_config={"max_tokens": 1024, "stream": False},
)
print(llm.)

client = openai.Client(api_key="hahanothing", base_url="http://127.0.0.1:9997/v1")

completion = client.chat.completions.create(
    model="qwen2-instruct",
    messages= [
        {
            "role": "user",
            "content": "Hello"
                }
            ],
    max_tokens=8192,
)
content = completion.choices[0].message.content
print(f"{content}")
"""

from xinference.client import Client
client = Client("http://127.0.0.1:9997")
model = client.get_model("qwen2-instruct")
completion = model.chat(
    prompt="Hello",
    generate_config={"max_tokens": 1024},
)
content = completion["choices"][0]["message"]["content"]
print(f"{content}")
