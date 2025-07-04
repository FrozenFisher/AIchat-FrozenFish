'''
作者:Mcqueen_yang(FrozenFisher)
特别鸣谢：
llm:Qwen2-Alibaba
框架:Xinference
实时语音:GPT-Sovits(bilibili@花儿不哭https://space.bilibili.com/5760446/)
由PyQt5提供GUI支持
语音模型作者与GSV api作者:bilibili@白菜工厂1145号员工https://space.bilibili.com/518098961
语音模型数据集来源:红血球AE3803
一些程序由ChatGPT-3.5生成

v1-大模型对话与语音
v2-增加了图形化界面
v2.1-优化图形界面
v3.0-加入设置界面
v3.1-加入模型切换功能（使用GPT-SoVITS apiv2）
v3.2-丰富模型
v3.2.1-qf-修复问题
计划：
vonline0.1-重构，接入DeepSeek
'''

import re
import yaml
import os
import queue
import threading
import sys
import requests
from typing import List, Any, Callable, Dict, ForwardRef, Iterable, List, Optional, Union
from typing_extensions import Literal, NotRequired, TypedDict
from xinference.client import Client
from pydub import AudioSegment
import openai
import tiktoken

import simpleaudio as sa
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QColor

'''
启动:
conda activate xinference
xinference-local --host 0.0.0.0 --port 9997
/Users/ycc/workspace/Chat/GPT-SoVITS/go-apiv2.command ; exit;
/usr/bin/python3 /Users/ycc/workspace/Chat/collection/main-v3.py

/Users/ycc/workspace/Chat/GPT-SoVITS/go-webui.command ; exit;
'''

input_queue = queue.Queue()
output_queue = queue.Queue()

current_path = os.path.abspath(os.path.dirname(__file__))
print(f"正在{current_path}运行")

with open(f'{current_path}/modelconfig.yaml', 'r') as file:
    config = yaml.safe_load(file)
Agentlist = list(config['Agents'].keys())
Agentlist.append("userinput")

Agent = "银狼"
GPTPath = f"{os.path.dirname(current_path)}/GPT-SoVITS/GPT_weights_v2/银狼-e10.ckpt"
SoVITSPath = f"{os.path.dirname(current_path)}/GPT-SoVITS/SoVITS_weights_v2/银狼_e15_s480.pth"
bgPath = f"{current_path}/lib/bg/bgSilverWolf.png"
promptPath = f"{current_path}/lib/prompt/promptSilverWolf.txt"
refaudioPath = f"{current_path}/lib/参考音频/该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav"
GPTPathin = f"GPT_weights_v2/银狼-e10.ckpt"
SoVITSPathin = f"SoVITS_weights_v2/银狼_e15_s480.pth"
bgPathin = f"lib/bg/bgSilverWolf.png"
promptPathin = f"lib/prompt/promptSilverWolf.txt"
refaudioPathin = f"lib/参考音频/该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav"


class ChatCompletionMessage(TypedDict):
    role: str
    content: Optional[str]
    user: NotRequired[str]
    tool_calls: NotRequired[List]


class FloatingWindow(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("对话")
        self.setFixedSize(600, 400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_AlwaysStackOnTop, True)
        # 主布局
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # 创建一个容器来放置图片和输入框
        self.container = QtWidgets.QWidget(self)
        self.container.setGeometry(0, 0, 600, 400)
        self.container.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # 图片
        self.imageLabel = QtWidgets.QLabel(self.container)
        pixmap = QtGui.QPixmap(
            f"{current_path}/lib/bg.png").scaled(600, 400, QtCore.Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setGeometry(0, 0, 600, 400)

        # 文本显示、输入框和按钮垂直布局
        inputLayout = QtWidgets.QVBoxLayout(self.container)
        inputLayout.setContentsMargins(300, 49, 30, 20)
        # 文本显示
        font = QtGui.QFont()
        font.setFamily("Unifont")
        font.setPointSize(13)
        self.textArea = QtWidgets.QTextEdit(self.container)
        self.textArea.setReadOnly(True)
        self.textArea.setStyleSheet("background: rgba(255, 255, 255, 150);")
        self.textArea.setGeometry(0, 0, 600, 350)
        self.textArea.setFont(font)
        inputLayout.addWidget(self.textArea)
        sendlayout = QtWidgets.QHBoxLayout()
        sendlayout.setContentsMargins(0, 0, 0, 0)
        # 输入框
        self.input_box = QtWidgets.QLineEdit(self.container)
        self.input_box.returnPressed.connect(self.send_message)
        sendlayout.addWidget(self.input_box)
        # 发送按钮
        self.send_button = QtWidgets.QPushButton("发送", self.container)
        self.send_button.clicked.connect(self.send_message)
        sendlayout.addWidget(self.send_button)
        inputLayout.addLayout(sendlayout)

        # 1级按钮布局
        firstButtonLayout = QtWidgets.QHBoxLayout(self.container)
        # 切换按钮
        self.setButton = QtWidgets.QLabel(self.container)
        self.setButton.setStyleSheet(
            "color: black; font-family: Unifont; font-size: 16pt;")
        self.setButton.setText("设置")
        self.setButton.setGeometry(310, 25, 50, 24)
        firstButtonLayout.addWidget(self.setButton)
        self.setButton.raise_()

        # 事件
        self.input_box.setDisabled(True)
        self.setButton.setDisabled(True)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_text_area)
        self.timer.start(100)

        self.is_dragging = False
        self.wheshowSet = False

        self.setButton.mousePressEvent = lambda event: self.showSettings(event)

        self.update_button_color()

    # 移动浮窗
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
            self.textArea.append("You: " + message)
            self.input_box.clear()
            self.input_box.setDisabled(True)
            self.setButton.setDisabled(True)
            input_queue.put(message)

    def update_text_area(self):
        try:
            while True:
                result = output_queue.get_nowait()
                self.textArea.append(result)
                self.input_box.setDisabled(False)
                self.setButton.setDisabled(False)
        except queue.Empty:
            pass

    def showSettings(self, event):
        self.wheshowSet = True
        # 创建设置窗口
        self.setting_window = SettingWindow(self)
        self.setting_window.show()

    def update_button_color(self):
        # 加载背景图像并计算平均颜色
        pixmap = QtGui.QPixmap(f"{bgPath}")
        # 获取图像的宽高
        widthin = 310
        widthout = 360
        heightin = 25
        heightout = 49
        # 将图像转换为 QImage，以便访问像素数据
        image = pixmap.toImage()
        r_total = g_total = b_total = 0
        for x in range(widthin, widthout):
            for y in range(heightin, heightout):
                color = QColor(image.pixel(x, y))
                r_total += color.red()
                g_total += color.green()
                b_total += color.blue()
        pixel_count = (widthout - widthin) * (heightout - heightin)
        # 计算平均 RGB 值
        avg_r = r_total // pixel_count
        avg_g = g_total // pixel_count
        avg_b = b_total // pixel_count
        # 根据平均亮度判断字体颜色
        brightness = (avg_r * 299 + avg_g * 587 + avg_b * 114) // 1000
        if brightness > 128:  # 如果较暗，使用白色字体
            self.setButton.setStyleSheet(
                "color: white; font-family: Unifont; font-size: 16pt; ")
            print("当前模式：暗")

        else:  # 如果较亮，使用黑色字体
            self.setButton.setStyleSheet(
                "color: black; font-family: Unifont; font-size: 16pt; ")
            print("当前模式：亮")


class SettingWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)
        self.setFixedSize(600, 400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 设置背景
        self.settingbg = QtWidgets.QLabel(self)
        settingbg = QtGui.QPixmap(
            f"{current_path}/lib/settingbg.png").scaled(600, 400, QtCore.Qt.KeepAspectRatio)
        self.settingbg.setPixmap(settingbg)
        self.settingbg.setGeometry(0, 0, 600, 400)

        # 添加设置窗口内容
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.top_layout = QtWidgets.QHBoxLayout()
        self.top_layout.setContentsMargins(0, 20, 20, 0)
        self.top_layout.addStretch()
        self.label = QtWidgets.QLabel("设置-切换模型")
        self.label.setStyleSheet(
            "color: black; font-family: Unifont; font-size: 15pt;")
        self.top_layout.addWidget(self.label)
        self.layout.addLayout(self.top_layout)

        self.agent_combo = QtWidgets.QComboBox()
        self.agent_combo.addItems(Agentlist)
        self.agent_combo.currentTextChanged.connect(lambda userinput: self.freshPathWindow(userinput))
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setContentsMargins(40, 0, 40, 0)
        self.left_layout.addWidget(self.agent_combo)

        self.gpt_path_title = QtWidgets.QLabel()
        self.gpt_path_title.setStyleSheet(
            "color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
        self.gpt_path_title.setText("GPT模型路径")
        self.left_layout.addWidget(self.gpt_path_title)
        self.gpt_path_edit = QtWidgets.QLineEdit()
        self.gpt_path_edit.setReadOnly(True)
        self.gpt_path_edit.setText(GPTPath)
        self.left_layout.addWidget(self.gpt_path_edit)

        self.sovits_path_title = QtWidgets.QLabel()
        self.sovits_path_title.setStyleSheet(
            "color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
        self.sovits_path_title.setText("SoVITS模型路径")
        self.left_layout.addWidget(self.sovits_path_title)
        self.sovits_path_edit = QtWidgets.QLineEdit()
        self.sovits_path_edit.setReadOnly(True)
        self.sovits_path_edit.setText(SoVITSPath)
        self.left_layout.addWidget(self.sovits_path_edit)

        self.bg_path_title = QtWidgets.QLabel()
        self.bg_path_title.setStyleSheet(
            "color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
        self.bg_path_title.setText("背景路径")
        self.left_layout.addWidget(self.bg_path_title)
        self.bg_path_edit = QtWidgets.QLineEdit()
        self.bg_path_edit.setReadOnly(True)
        self.bg_path_edit.setText(bgPath)
        self.left_layout.addWidget(self.bg_path_edit)

        self.prompt_path_title = QtWidgets.QLabel()
        self.prompt_path_title.setStyleSheet(
            "color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
        self.prompt_path_title.setText("prompt路径")
        self.left_layout.addWidget(self.prompt_path_title)
        self.prompt_path_edit = QtWidgets.QLineEdit()
        self.prompt_path_edit.setReadOnly(True)
        self.prompt_path_edit.setText(promptPath)
        self.left_layout.addWidget(self.prompt_path_edit)

        self.refaudioPath_title = QtWidgets.QLabel()
        self.refaudioPath_title.setStyleSheet(
            "color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
        self.refaudioPath_title.setText("参考音频路径")
        self.left_layout.addWidget(self.refaudioPath_title)
        self.refaudioPath_edit = QtWidgets.QLineEdit()
        self.refaudioPath_edit.setReadOnly(True)
        self.refaudioPath_edit.setText(refaudioPath)
        self.left_layout.addWidget(self.refaudioPath_edit)

        self.layout.addLayout(self.left_layout)

        self.layout.addStretch()

        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.bottom_layout.setContentsMargins(0, 0, 20, 20)
        self.bottom_layout.addStretch()
        self.apply_button = QtWidgets.QPushButton("应用")
        self.apply_button.clicked.connect(self.apply)
        self.bottom_layout.addWidget(self.apply_button)
        self.clobutton = QtWidgets.QPushButton("关闭")
        self.clobutton.clicked.connect(self.close)
        self.bottom_layout.addWidget(self.clobutton)
        self.layout.addLayout(self.bottom_layout)

        self.layout.addLayout(self.left_layout)

    def freshPath(self):
        global Agent, GPTPath, SoVITSPath, bgPath, promptPath, refaudioPath
        global GPTPathin, SoVITSPathin, bgPathin, promptPathin, refaudioPathin
        if Agent == "userinput":
            pass
        else:
            with open(f'{current_path}/modelconfig.yaml', 'r') as file:
                config = yaml.safe_load(file)
            GPTPathin = config['Agents'].get(Agent)["GPTPath"]
            GPTPath = f"{os.path.dirname(current_path)}/GPT-SoVITS/{GPTPathin}"
            SoVITSPathin = config['Agents'].get(Agent)["SoVITSPath"]
            SoVITSPath = f"{os.path.dirname(current_path)}/GPT-SoVITS/{SoVITSPathin}"
            bgPathin = config['Agents'].get(Agent)["bgPath"]
            bgPath = f"{current_path}/{bgPathin}"
            promptPathin = config['Agents'].get(Agent)["promptPath"]
            promptPath = f"{current_path}/{promptPathin}"
            refaudioPathin = config['Agents'].get(Agent)["refaudioPath"]
            refaudioPath = f"{current_path}/{refaudioPathin}"

    def freshPathWindow(self, userinput):
        global Agent, GPTPath, SoVITSPath, bgPath, promptPath, refaudioPath
        global GPTPathin, SoVITSPathin, bgPathin, promptPathin, refaudioPathin
        Agent = userinput
        self.freshPath()
        if Agent == "userinput":
            self.gpt_path_edit.setText("")
            self.sovits_path_edit.setText("")
            self.bg_path_edit.setText("")
            self.prompt_path_edit.setText("")
            self.refaudioPath_edit.setText("")
            self.gpt_path_edit.setReadOnly(False)
            self.sovits_path_edit.setReadOnly(False)
            self.bg_path_edit.setReadOnly(False)
            self.prompt_path_edit.setReadOnly(False)
            self.refaudioPath_edit.setReadOnly(False)
        else:
            self.gpt_path_edit.setReadOnly(True)
            self.sovits_path_edit.setReadOnly(True)
            self.bg_path_edit.setReadOnly(True)
            self.prompt_path_edit.setReadOnly(True)

            self.gpt_path_edit.setText(GPTPath)
            self.sovits_path_edit.setText(SoVITSPath)
            self.bg_path_edit.setText(bgPath)
            self.prompt_path_edit.setText(promptPath)
            self.refaudioPath_edit.setText(refaudioPath)

    def close(self):
        self.parent().wheshowSet = False
        self.deleteLater()

    def changeModel(self):
        print("尝试调用api更改")
        try:
            url = "http://127.0.0.1:9880/set_gpt_weights"
            params = {"weights_path": GPTPathin}
            response = requests.get(url, params=params)
            if response.status_code == 200:
                print(f"设置 GPT 权重成功：{GPTPathin}")
            else:
                try:
                    error_info = response.json()
                    print(f"设置 GPT 权重失败：{error_info}")
                except Exception as e:
                    print(f"设置 GPT 权重失败：{response.text}")

            url = "http://127.0.0.1:9880/set_sovits_weights"
            params = {"weights_path": SoVITSPathin}
            response = requests.get(url, params=params)
            if response.status_code == 200:
                print(f"设置 SoVITS 权重成功：{GPTPathin}")
            else:
                try:
                    error_info = response.json()
                    print(f"设置 SoVITS 权重失败：{error_info}")
                except Exception as e:
                    print(f"设置 SoVITS 权重失败：{response.text}")
        except:
            print("调用api更改失败")

        print(
            f"当前GPT路径{GPTPath},Soviets路径{SoVITSPath},背景路径{bgPath},prompt路径{promptPath},参考音频路径{refaudioPath}")

    def apply(self):
        with open(f"{promptPath}", 'r') as file:
            chindexprompt = file.read()
        input_queue.put(chindexprompt)
        self.parent().input_box.setDisabled(True)
        self.parent().imageLabel.setPixmap(QtGui.QPixmap(
            bgPath).scaled(600, 400, QtCore.Qt.KeepAspectRatio))
        self.parent().textArea.clear()
        self.parent().update_button_color()
        self.changeModel()
        self.close()


def model_thread_function():
    global model_uid, client

    SettingWindow.freshPath(self=SettingWindow)
    SettingWindow.changeModel(self=SettingWindow)
    # 模型设定
    endpoint = "http://127.0.0.1:9997"
    model_name = "qwen2-instruct"
    model_size_in_billions = "7"
    model_format = "mlx"
    model_engine = "MLX"
    quantization = "4bit"

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
    # 启动大模型,endl

    # 处理输入对话历史，确保不会超出令牌限制
    encoding = tiktoken.get_encoding("cl100k_base")
    TOKEN_LIMIT = 32768

    def count_tokens(messages):  # 计算文本的令牌数
        token_count = 0
        for message in messages:
            token_count += len(encoding.encode(message["content"]))
        return token_count

    def trim_history(messages):
        while count_tokens(messages) > TOKEN_LIMIT:
            messages.pop(0)  # 删除最早的消息，直到令牌数在限制内
        return messages

    chat_history: List["ChatCompletionMessage"] = []  # chathistory设定
    # 默认prompt设定
    with open(f"{current_path}/lib/prompt.txt", 'r') as file:
        indexprompt = file.read()
    prompt = indexprompt
    chat_history.append(ChatCompletionMessage(role="user", content=prompt))

    messages = [{"role": message["role"], "content": message["content"]} for message in chat_history]  # 构建消息列表
    messages = trim_history(messages)  # 调整对话历史，确保不会超过令牌限制
    print(messages)

    client = openai.Client(api_key="hahanothing", base_url="http://127.0.0.1:9997/v1")

    completion = client.chat.completions.create(
        model=model_uid,
        messages=messages,
        max_tokens=32768
    )
    content = completion.choices[0].message.content
    print(f"{model_name}: {content}")
    output_queue.put(f"{content}")
    chat_history.append(ChatCompletionMessage(role="assistant", content=content))
    # 默认prompt设定,endl
    print(f"对话历史：{chat_history}")

    while True:
        prompt = input_queue.get()
        chat_history.append(ChatCompletionMessage(role="user", content=prompt))
        messages = [{"role": message["role"], "content": message["content"]} for message in chat_history]  # 构建消息列表
        messages = trim_history(messages)  # 调整对话历史，确保不会超过令牌限制

        completion = client.chat.completions.create(
            model=model_uid,
            messages=messages,
            max_tokens=32768
        )
        content = completion.choices[0].message.content
        print(f"对话历史：{chat_history}")
        print(f"{model_name}: {content}")
        output_queue.put(f"{Agent}: {content}")
        chat_history.append(ChatCompletionMessage(role="assistant", content=content))

        print("尝试生成音频")
        try:
            text = content
            textlist = re.findall(r'[^,.!?;:，。！？：；]*[,.!?;:，。！？：；]*', text)
            textlist = [part for part in textlist if part.strip()]
            # 创建一个共享的队列
            shared_queue = queue.Queue()

            def textToVoiceProducer(textlist, shared_queue):
                basename = os.path.basename(refaudioPath)
                reftext, extension = os.path.splitext(basename)
                print(f"参考音频文本:{reftext}")
                for i in range(0, len(textlist)):
                    base_url = 'http://127.0.0.1:9880/tts'
                    # 推理 - 使用执行参数指定的参考音频（POST 请求）
                    post_data = {
                        "prompt_text": reftext,
                        "prompt_lang": "zh",
                        "ref_audio_path": refaudioPath,
                        "text": textlist[i],
                        "text_lang": "zh",
                    }

                    response = requests.post(base_url, json=post_data)
                    if response.status_code == 200:
                        print("produced " + textlist[i])
                        # 生成文件名
                        filename = f"{i}.wav"
                        file_path = os.path.join(
                            f"{current_path}/temp/", filename)
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
                    play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels,
                                              bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
                    play_obj.wait_done()
                    os.remove(file_path)

            # 启动生产线程
            producer_thread = threading.Thread(
                target=textToVoiceProducer, args=(textlist, shared_queue))
            producer_thread.start()

            # 启动消费线程
            consumer_thread = threading.Thread(
                target=Voice, args=(shared_queue,))
            consumer_thread.start()

            # 等待生产线程结束
            producer_thread.join()
            # 等待消费线程结束
            consumer_thread.join()
        except:
            print("音频生成失败，当前仅能进行对话")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = FloatingWindow()
    window.show()

    model_thread = threading.Thread(target=model_thread_function)
    model_thread.daemon = True
    model_thread.start()

    app.aboutToQuit.connect(lambda: Client.terminate_model(model_uid))
    sys.exit(app.exec_())
