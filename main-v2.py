

'''
作者:Mcqueen_yang
特别鸣谢：
llm:Qwen2-Alibaba
框架:Xinference
实时语音:GPT-Sovits
银狼语音模型作者与Sovits api作者:白菜工厂1145号员工
银狼语音模型数据集来源:红血球AE3803
一些程序由ChatGPT-3.5生成
v2-增加了图形化界面
计划：
v2.1-优化图形界面
v3-使用LoRA微调
'''


from typing import List
from xinference.client import Client
from xinference.types import ChatCompletionMessage
import requests
from pydub import AudioSegment
import threading
import re
import os
import queue
import simpleaudio as sa
import sys
import threading
import queue
from PyQt5 import QtWidgets, QtGui, QtCore

'''启动:
conda activate xinference
xinference-local --host 0.0.0.0 --port 9997
/Users/ycc/workspace/Chat/GPT-SoVITS/go-api.command ; exit;
/usr/bin/python3 /Users/ycc/workspace/Chat/collection/main-v2.py

改变模型:config.py和Chat/GPT-SoVITS/GPT_SoVITS/configs/tts_infer.yaml
/Users/ycc/workspace/Chat/GPT-SoVITS/go-webui.command ; exit;
'''


input_queue = queue.Queue()
output_queue = queue.Queue()
current_path = os.path.abspath(os.path.dirname(__file__))
print(f"正在{current_path}运行")


class FloatingWindow(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("对话")
        self.setFixedSize(600, 400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_AlwaysStackOnTop, True)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 创建一个容器来放置图片和输入框
        self.container = QtWidgets.QWidget(self)
        self.container.setGeometry(0, 0, 600, 400)
        self.container.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.image_label = QtWidgets.QLabel(self.container)
        pixmap = QtGui.QPixmap(f"{current_path}/lib/SilverWolfpng.png").scaled(600, 400, QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.setGeometry(0, 0, 600, 400)

        # 输入框和按钮布局
        input_layout = QtWidgets.QVBoxLayout(self.container)
        input_layout.setContentsMargins(300, 0, 0, 0)

        self.text_area = QtWidgets.QTextEdit(self.container)
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("background: rgba(255, 255, 255, 150);")
        self.text_area.setGeometry(0, 0, 600, 350)
        input_layout.addWidget(self.text_area)

        sendlayout = QtWidgets.QHBoxLayout()
        sendlayout.setContentsMargins(0, 0, 0, 0)
        
        self.input_box = QtWidgets.QLineEdit(self.container)
        self.input_box.returnPressed.connect(self.send_message)
        sendlayout.addWidget(self.input_box)

        self.send_button = QtWidgets.QPushButton("发送", self.container)
        self.send_button.clicked.connect(self.send_message)
        sendlayout.addWidget(self.send_button)

        input_layout.addLayout(sendlayout)
        
        self.input_box.setDisabled(True)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_text_area)
        self.timer.start(100)

        self.is_dragging = False

            
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False

    def send_message(self):
        message = self.input_box.text()
        if message:
            self.text_area.append("You: " + message)
            self.input_box.clear()
            self.input_box.setDisabled(True)
            input_queue.put(message)

    def update_text_area(self):
        try:
            while True:
                result = output_queue.get_nowait()
                self.text_area.append(result)
                self.input_box.setDisabled(False)
        except queue.Empty:
            pass

def model_thread_function():
    global model_uid,client
    endpoint = "http://127.0.0.1:9997"
    model_name = "qwen2-instruct"
    model_size_in_billions = "7"
    model_format = "mlx"
    model_engine="MLX"
    quantization = "4-bit"
    base_url = 'http://127.0.0.1:9880'
    with open(f"{current_path}/lib/prompt.txt", 'r') as file:
        indexprompt = file.read()

    print(f"Xinference endpoint: {endpoint}")
    print(f"Model Name: {model_name}")
    print(f"Model Size (in billions): {model_size_in_billions}")
    print(f"Model Format: {model_format}")
    print(f"Quantization: {quantization}")

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

    chat_history: List["ChatCompletionMessage"] = []
    prompt = indexprompt
    completion = model.chat(
        prompt=prompt,
        chat_history=chat_history,
        generate_config={"max_tokens": 1024},
    )
    content = completion["choices"][0]["message"]["content"]
    print(f"{model_name}: {content}")
    output_queue.put(f"银狼: {content}")
    chat_history.append(ChatCompletionMessage(role="user", content=prompt))
    chat_history.append(ChatCompletionMessage(role="assistant", content=content))
    while True:
        prompt = input_queue.get()
        completion = model.chat(
            prompt=prompt,
            chat_history=chat_history,
            generate_config={"max_tokens": 1024},
        )
        content = completion["choices"][0]["message"]["content"]
        print(f"{model_name}: {content}")
        output_queue.put(f"银狼: {content}")
        chat_history.append(ChatCompletionMessage(role="user", content=prompt))
        chat_history.append(ChatCompletionMessage(role="assistant", content=content))
        
        print("生成音频中")
        text = content
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
                    "refer_wav_path": f"{current_path}/lib/参考音频/说话-该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav",
                    "text": textlist[i],
                    "text_language": "zh",
                    "inp_refs": [str(i)+".wav"]
                }
                response = requests.post(base_url, json=post_data)
                if response.status_code == 200:
                    print("produced " + textlist[i])
                    # 生成文件名
                    filename = f"{i}.wav"
                    file_path = os.path.join(f"{current_path}/temp/", filename)
                    with open(file_path, 'wb') as audio_file:
                        audio_file.write(response.content)
                    # 将文件名放入队列
                    shared_queue.put(filename)
                else:
                    # 处理错误
                    print(f"错误: {response.status_code}, {response.text}")
            # 标记生产线程结束
            shared_queue.put(None)

        def Voice(shared_queue):
            while True:
                # 从队列中获取文件名
                filename = shared_queue.get()
                if filename is None:
                    # 如果接收到 None，表示生产线程已经结束
                    break
                file_path = os.path.join(f"{current_path}/temp/", filename)
                audio = AudioSegment.from_file(file_path)
                play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
                play_obj.wait_done()
                os.remove(file_path)

        # 启动生产线程
        producer_thread = threading.Thread(target=textToVoiceProducer, args=(textlist, shared_queue))
        producer_thread.start()

        # 启动消费线程
        consumer_thread = threading.Thread(target=Voice, args=(shared_queue,))
        consumer_thread.start()

        # 等待生产线程结束
        producer_thread.join()
        # 等待消费线程结束
        consumer_thread.join()
        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = FloatingWindow()
    window.show()
    
    
    model_thread = threading.Thread(target=model_thread_function)
    model_thread.daemon = True
    model_thread.start()
    
    app.aboutToQuit.connect(lambda: client.terminate_model(model_uid))
    sys.exit(app.exec_())
    

