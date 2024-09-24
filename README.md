#### collection
### 0.对于0起步的用户（确保你的环境中有pip和conda）


### 1.安装Xinference环境
    ```bash
    conda create -n xinference
    conda activate xinference
    ```
    推荐:
    ```bash
    pip install xinference[all]
    pip install xinference
    ```
    如果需要节省空间：
        如果为Mac平台，推荐(或许M芯也仅有):
            ```bash
            pip install xinference[mlx]
            pip install xinference
            ```
    
    
### 2.安装对应环境的Qwen2-instruct-7B
    mac:
    ```bash
    XINFERENCE_MODEL_SRC=modelscope xinference-local --host 0.0.0.0 --port 9997
    ```
    打开http://0.0.0.0:9997，在LANGUAGE MODELS栏"Search for model name and description"输入"Qwen2-instruct"
    点击下方Qwen2-instruct的卡片，ModelEngine选择MLX，ModelFromat是mlx，model Size选7，Quantization选4-bit，N-GPU确定为auto，其他不要动
    点下方的小火箭，返回命令行查看下载进度，等下载完成，不要刷新网页

### 3.安装GPT-Sovits RVC api

### 4.安装语音包
### 5.启动
5.conda activate xinference
xinference-local --host 0.0.0.0 --port 9997
/Users/ycc/workspace/Chat/GPT-SoVITS/go-api.command ; exit;
/usr/bin/python3 /Users/ycc/workspace/Chat/collection/main-v1.py 

改变模型:config.py和Chat/GPT-SoVITS/GPT_SoVITS/configs/tts_infer.yaml
/Users/ycc/workspace/Chat/GPT-SoVITS/go-webui.command ; exit;
