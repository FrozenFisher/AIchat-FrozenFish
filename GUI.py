import sys
import threading
import queue
from PyQt5 import QtWidgets, QtGui, QtCore
import os
import yaml
import requests

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
refaudioPath = f"{current_path}/lib/参考音频/说话-该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav"
GPTPathin = f"GPT_weights_v2/银狼-e10.ckpt"
SoVITSPathin = f"SoVITS_weights_v2/银狼_e15_s480.pth"
bgPathin = f"lib/bg/bgSilverWolf.png"
promptPathin = f"lib/prompt/promptSilverWolf.txt"
refaudioPathin = f"lib/参考音频/说话-该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav"

class FloatingWindow(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("对话")
        self.setFixedSize(600, 400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_AlwaysStackOnTop, True)
        # 主布局
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        #创建一个容器来放置图片和输入框
        self.container = QtWidgets.QWidget(self)
        self.container.setGeometry(0, 0, 600, 400)
        self.container.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #图片
        self.imageLabel = QtWidgets.QLabel(self.container)
        pixmap = QtGui.QPixmap(f"{current_path}/lib/bg.png").scaled(600, 400, QtCore.Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setGeometry(0, 0, 600, 400)

        #文本显示、输入框和按钮垂直布局
        inputLayout = QtWidgets.QVBoxLayout(self.container)
        inputLayout.setContentsMargins(300, 49, 30, 20)
        #文本显示
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
        #输入框
        self.input_box = QtWidgets.QLineEdit(self.container)
        self.input_box.returnPressed.connect(self.send_message)
        sendlayout.addWidget(self.input_box)
        #发送按钮
        self.send_button = QtWidgets.QPushButton("发送", self.container)
        self.send_button.clicked.connect(self.send_message)
        sendlayout.addWidget(self.send_button)
        inputLayout.addLayout(sendlayout)
        
        
        
        #1级按钮布局
        firstButtonLayout = QtWidgets.QHBoxLayout(self.container)
        #切换按钮
        self.setButton = QtWidgets.QLabel(self.container)
        self.setButton.setStyleSheet("color: #FFFFFF; font-family: Unifont; font-size: 16pt;")
        self.setButton.setText("设置")
        self.setButton.setGeometry(310, 25, 50, 24)
        firstButtonLayout.addWidget(self.setButton)
        self.setButton.raise_()
        
        #事件
        self.input_box.setDisabled(False)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_text_area)
        self.timer.start(100)

        self.is_dragging = False
        self.wheshowSet = False
        
        self.setButton.mousePressEvent = lambda event: self.showSettings(event)

    #移动浮窗
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
            input_queue.put(message)

    def update_text_area(self):
        try:
            while True:
                result = output_queue.get_nowait()
                self.textArea.append(result)
                self.input_box.setDisabled(False)
        except queue.Empty:
            pass
    
    def showSettings(self, event):
        self.wheshowSet = True
        # 创建设置窗口
        self.setting_window = SettingWindow(self)
        self.setting_window.show()
    
class SettingWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)
        self.setFixedSize(600, 400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 设置背景
        self.settingbg = QtWidgets.QLabel(self)
        settingbg = QtGui.QPixmap(f"{current_path}/lib/settingbg.png").scaled(600, 400, QtCore.Qt.KeepAspectRatio)
        self.settingbg.setPixmap(settingbg)
        self.settingbg.setGeometry(0, 0, 600, 400)

        # 添加设置窗口内容
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.top_layout = QtWidgets.QHBoxLayout()
        self.top_layout.setContentsMargins(0, 20, 20, 0)
        self.top_layout.addStretch()
        self.label = QtWidgets.QLabel("设置-切换模型")
        self.label.setStyleSheet("color: #FFFFFF; font-family: Unifont; font-size: 15pt;")
        self.top_layout.addWidget(self.label)
        self.layout.addLayout(self.top_layout)

        self.agent_combo = QtWidgets.QComboBox()
        self.agent_combo.addItems(Agentlist)
        self.agent_combo.currentTextChanged.connect(self.freshPath)
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setContentsMargins(40, 0, 40, 0)
        self.left_layout.addWidget(self.agent_combo)
        
        self.gpt_path_title = QtWidgets.QLabel()
        self.gpt_path_title.setStyleSheet("color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
        self.gpt_path_title.setText("GPT模型路径")
        self.left_layout.addWidget(self.gpt_path_title)
        self.gpt_path_edit = QtWidgets.QLineEdit()
        self.gpt_path_edit.setReadOnly(True)
        self.gpt_path_edit.setText(GPTPath)
        self.left_layout.addWidget(self.gpt_path_edit)

        self.sovits_path_title = QtWidgets.QLabel()
        self.sovits_path_title.setStyleSheet("color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
        self.sovits_path_title.setText("SoVITS模型路径")
        self.left_layout.addWidget(self.sovits_path_title)
        self.sovits_path_edit = QtWidgets.QLineEdit()
        self.sovits_path_edit.setReadOnly(True)
        self.sovits_path_edit.setText(SoVITSPath)
        self.left_layout.addWidget(self.sovits_path_edit)

        self.bg_path_title = QtWidgets.QLabel()
        self.bg_path_title.setStyleSheet("color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
        self.bg_path_title.setText("背景路径")
        self.left_layout.addWidget(self.bg_path_title)
        self.bg_path_edit = QtWidgets.QLineEdit()
        self.bg_path_edit.setReadOnly(True)
        self.bg_path_edit.setText(bgPath) 
        self.left_layout.addWidget(self.bg_path_edit)

        self.prompt_path_title = QtWidgets.QLabel()
        self.prompt_path_title.setStyleSheet("color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
        self.prompt_path_title.setText("prompt路径")
        self.left_layout.addWidget(self.prompt_path_title)
        self.prompt_path_edit = QtWidgets.QLineEdit()
        self.prompt_path_edit.setReadOnly(True)
        self.prompt_path_edit.setText(promptPath) 
        self.left_layout.addWidget(self.prompt_path_edit)
        
        self.refaudioPath_title = QtWidgets.QLabel()
        self.refaudioPath_title.setStyleSheet("color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
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

    def freshPath(self, userinput):
        global Agent, GPTPath, SoVITSPath, bgPath, promptPath
        global GPTPathin, SoVITSPathin, bgPathin, promptPathin
        Agent = userinput
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
            
            self.gpt_path_edit.setText(GPTPath)
            self.sovits_path_edit.setText(SoVITSPath)
            self.bg_path_edit.setText(bgPath)
            self.prompt_path_edit.setText(promptPath)
            self.refaudioPath_edit.setText(refaudioPath)


    def close(self):
        self.parent().wheshowSet = False
        self.deleteLater()

    def apply(self):
        self.parent().imageLabel.setPixmap(QtGui.QPixmap(bgPath).scaled(600, 400, QtCore.Qt.KeepAspectRatio))
        print("调用get请求")
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
            return False
        
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
            return False
        print(f"当前GPT路径{GPTPath},Soviets路径{SoVITSPath},背景路径{bgPath},prompt路径{promptPath},参考音频路径{refaudioPath}")


                
        


def model_thread_function():
    while True:
        user_input = input_queue.get()
        if user_input is None:
            break
        model_response = f"Processed: {user_input}"
        output_queue.put(model_response)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = FloatingWindow()
    window.show()

    model_thread = threading.Thread(target=model_thread_function)
    model_thread.daemon = True
    model_thread.start()

    sys.exit(app.exec_())
