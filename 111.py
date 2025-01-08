from xinference.client import Client

# 模型设定
endpoint = "http://127.0.0.1:9997"
model_name = "qwen2-instruct"
model_size_in_billions = "7"
model_format = "mlx"
model_engine = "MLX"
quantization = "4-bit"


client = Client(endpoint)
model_uid = client.launch_model(
    model_name=model_name,
    model_engine=model_engine,
    model_size_in_billions=model_size_in_billions,
    model_format=model_format,
    quantization=quantization,
    n_ctx=2048,
)
model = client.get_model(model_uid)