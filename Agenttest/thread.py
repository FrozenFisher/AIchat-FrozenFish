
import threading
import re
import os
import queue
import requests
from pydub import AudioSegment
import simpleaudio as sa


text = "该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。"
textlist = re.findall(r'[^,.!?;:，。！？：；]*[,.!?;:，。！？：；]*', text)
textlist = [part for part in textlist if part.strip()]

# 创建一个共享的队列
shared_queue = queue.Queue()

def textToVoiceProducer(textlist, shared_queue):
    for i in range(0, len(textlist)):
        base_url = 'http://127.0.0.1:9880'

        # 推理 - 使用执行参数指定的参考音频（POST 请求）
        post_data = {
            "prompt_text": "该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。",
            "prompt_language": "zh",
            "refer_wav_path": "/Users/ycc/workspace/Chat/参考音频/说话-该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav",
            "text": textlist[i],
            "text_language": "zh",
            "inp_refs": [str(i)+".wav"]
        }
        response = requests.post(base_url, json=post_data)
        if response.status_code == 200:
            print("produced " + textlist[i])
            # 生成文件名
            filename = f"{i}.wav"
            file_path = os.path.join("/Users/ycc/workspace/Chat/collection/temp/", filename)
            with open(file_path, 'wb') as audio_file:
                audio_file.write(response.content)
            # 将文件名放入队列
            shared_queue.put(filename)
        else:
            # 处理错误
            print(f"错误: {response.status_code}, {response.text}")
    # 标记生产者线程结束
    shared_queue.put(None)

def Voice(shared_queue):
    while True:
        # 从队列中获取文件名
        filename = shared_queue.get()
        if filename is None:
            # 如果接收到 None，表示生产者线程已经结束
            break
        file_path = os.path.join("/Users/ycc/workspace/Chat/collection/temp/", filename)
        audio = AudioSegment.from_file(file_path)
        play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
        play_obj.wait_done()
        os.remove(file_path)

# 启动生产者线程
producer_thread = threading.Thread(target=textToVoiceProducer, args=(textlist, shared_queue))
producer_thread.start()

# 启动消费者线程
consumer_thread = threading.Thread(target=Voice, args=(shared_queue,))
consumer_thread.start()

# 等待生产者线程结束
producer_thread.join()
# 等待消费者线程结束
consumer_thread.join()