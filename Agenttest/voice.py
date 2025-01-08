
import requests
from pydub import AudioSegment
from io import BytesIO
import simpleaudio as sa

# 定义 API 的基本 URL
base_url = 'http://127.0.0.1:9880'

# 推理 - 使用执行参数指定的参考音频（POST 请求）
post_data = {
    "prompt_text": "该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。",
    "prompt_language": "zh",
    "refer_wav_path": "/Users/ycc/workspace/Chat/参考音频/说话-该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav",
    "text": "你好",
    "text_language": "zh",
    "inp_refs": ["456.wav"]
}
response = requests.post(base_url, json=post_data)
if response.status_code == 200:
    # 处理成功获取的音频流
    print("成功获取音频")
    # 将音频流内容读取到内存中
    audio_data = BytesIO(response.content)
    # 使用 pydub 加载音频
    audio = AudioSegment.from_file(audio_data)
    # 播放音频
    play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels,
                              bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
    play_obj.wait_done()  # 等待音频播放完成
    print("音频播放完成")
else:
    # 处理错误
    print(f"错误: {response.status_code}, {response.text}")

