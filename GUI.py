import sys
import threading
import queue
from PyQt5 import QtWidgets, QtGui, QtCore
import os

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
        
        #设置背景
        self.settingbg = QtWidgets.QLabel(self)
        settingbg = QtGui.QPixmap(f"{current_path}/lib/settingbg.png").scaled(600, 400, QtCore.Qt.KeepAspectRatio)
        self.settingbg.setPixmap(settingbg)
        self.settingbg.setGeometry(0, 0, 600, 400)
        self.settingbg.setVisible(False)
        
        
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
            
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            if self.wheshowSet == True:
                self.wheshowSet = not self.wheshowSet  
                self.settingbg.setVisible(self.wheshowSet)

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
    
    def showSettings(self, event):
        self.wheshowSet = not self.wheshowSet  
        self.settingbg.setVisible(self.wheshowSet)
        


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
