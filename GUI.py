import sys
import threading
import queue
from PyQt5 import QtWidgets, QtGui, QtCore

input_queue = queue.Queue()
output_queue = queue.Queue()

class FloatingWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("浮窗示例")
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
        pixmap = QtGui.QPixmap("/Users/ycc/workspace/Chat/collection/lib/SilverWolfpng.png").scaled(600, 400, QtCore.Qt.KeepAspectRatio)
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
            input_queue.put(message)

    def update_text_area(self):
        try:
            while True:
                result = output_queue.get_nowait()
                self.text_area.append("Model: " + result)
        except queue.Empty:
            pass

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
