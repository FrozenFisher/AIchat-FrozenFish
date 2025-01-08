

#xinference launch -n qwen2-instruct -f mlx -q 4-bit --model-engine mlx -s 7 
'''
更改了/Users/ycc/Library/Python/3.9/lib/python/site-packages/langchain_community/llms/xinference.py中开头
原本为:
if TYPE_CHECKING:
    from xinference.client import RESTfulChatModelHandle, RESTfulGenerateModelHandle
    from xinference.model.llm import LlamaCppGenerateConfig
    
if TYPE_CHECKING:
    from xinference.client.restful.restful_client import RESTfulChatModelHandle, RESTfulGenerateModelHandle
    from xinference.model.llm.ggml.llamacpp import LlamaCppGenerateConfig
    
第98行
        try:
            from xinference.client.restful.restful_client import Client as RESTfulClient
        except ImportError:
            try:
                from xinference_client import RESTfulClient

'''
"""
Launch the model based on the parameters on the server via RESTful APIs.

Parameters
----------
model_name: str
    The name of model.
model_type: str
    type of model.
model_engine: Optional[str]
    Specify the inference engine of the model when launching LLM.
model_uid: str
    UID of model, auto generate a UUID if is None.
model_size_in_billions: Optional[Union[int, str, float]]
    The size (in billions) of the model.
model_format: Optional[str]
    The format of the model.
quantization: Optional[str]
    The quantization of model.
replica: Optional[int]
    The replica of model, default is 1.
n_gpu: Optional[Union[int, str]],
    The number of GPUs used by the model, default is "auto".
    ``n_gpu=None`` means cpu only, ``n_gpu=auto`` lets the system automatically determine the best number of GPUs to use.
peft_model_config: Optional[Dict]
    - "lora_list": A List of PEFT (Parameter-Efficient Fine-Tuning) model and path.
    - "image_lora_load_kwargs": A Dict of lora load parameters for image model
    - "image_lora_fuse_kwargs": A Dict of lora fuse parameters for image model
request_limits: Optional[int]
    The number of request limits for this model, default is None.
    ``request_limits=None`` means no limits for this model.
worker_ip: Optional[str]
    Specify the worker ip where the model is located in a distributed scenario.
gpu_idx: Optional[Union[int, List[int]]]
    Specify the GPU index where the model is located.
**kwargs:
    Any other parameters been specified.

Returns
-------
str
    The unique model_uid for the launched model.

"""
        
from langchain_community.llms import Xinference

llm = Xinference(
    server_url="http://0.0.0.0:9997",
    model_uid = {"qwen2-instruct"} # replace model_uid with the model UID return from launching the model
)

llm(
    prompt="Q: where can we visit in the capital of France? A:",
    generate_config={"max_tokens": 1024, "stream": True},
)

