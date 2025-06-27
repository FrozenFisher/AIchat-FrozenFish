"""
AI聊天客户端 - 只负责UI交互和音频播放
通过RESTful API与server通信
"""

import os
import sys
import json
import uuid
import requests
import threading
import queue
import re
import base64
from typing import Optional, Dict, Any, List
from pathlib import Path

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QColor
from pydub import AudioSegment
import simpleaudio as sa

# 全局配置
SERVER_URL = "http://127.0.0.1:8000"
current_path = Path(__file__).parent
session_id = str(uuid.uuid4())
current_agent = "银狼"

class ChatClient:
    """聊天客户端API封装"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session_id = str(uuid.uuid4())
    
    def get_agents(self) -> list:
        """获取所有可用角色"""
        try:
            response = requests.get(f"{self.server_url}/agents")
            if response.status_code == 200:
                return response.json()["agents"]
            return []
        except Exception as e:
            print(f"获取角色列表失败: {e}")
            return []
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict]:
        """获取角色配置"""
        try:
            response = requests.get(f"{self.server_url}/agent/{agent_name}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"获取角色配置失败: {e}")
            return None
    
    def get_agent_prompt(self, agent_name: str) -> Optional[Dict]:
        """获取角色提示词"""
        try:
            response = requests.get(f"{self.server_url}/agent/{agent_name}/prompt")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"获取角色提示词失败: {e}")
            return None
    
    def init_agent_session(self, agent_name: str) -> Optional[Dict]:
        """初始化角色会话"""
        try:
            data = {
                "message": "",  # 空消息，用于初始化
                "agent": agent_name,
                "session_id": self.session_id
            }
            response = requests.post(f"{self.server_url}/agent/{agent_name}/init", json=data)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"初始化角色会话失败: {e}")
            return None
    
    def switch_agent(self, agent_name: str) -> bool:
        """切换角色"""
        try:
            response = requests.post(f"{self.server_url}/switch_agent/{agent_name}")
            return response.status_code == 200
        except Exception as e:
            print(f"切换角色失败: {e}")
            return False
    
    def send_message(self, message: str, agent: str) -> Optional[Dict]:
        """发送消息"""
        try:
            data = {
                "message": message,
                "agent": agent,
                "session_id": self.session_id
            }
            response = requests.post(f"{self.server_url}/chat", json=data)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"发送消息失败: {e}")
            return None
    
    def get_audio(self, filename: str) -> Optional[bytes]:
        """获取音频文件 - 已废弃"""
        print("警告: get_audio方法已废弃，音频数据现在直接包含在聊天响应中")
        return None


class FloatingWindow(QtWidgets.QWidget):
    """主聊天窗口"""
    
    def __init__(self):
        super().__init__()
        self.chat_client = ChatClient(SERVER_URL)
        self.current_agent = "银狼"
        self.agent_configs = {}
        self.is_initialized = False
        
        # 先初始化UI组件
        self.init_ui()
        
        # 然后加载角色配置
        self.load_agents()
        
        # 最后更新UI显示
        self.update_background()
        self.update_button_color()
        
        # 初始化当前角色
        self.initialize_current_agent()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("AI聊天")
        self.setFixedSize(600, 400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_AlwaysStackOnTop, True)
        
        # 主布局
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 容器
        self.container = QtWidgets.QWidget(self)
        self.container.setGeometry(0, 0, 600, 400)
        self.container.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # 背景图片
        self.imageLabel = QtWidgets.QLabel(self.container)
        self.update_background()
        self.imageLabel.setGeometry(0, 0, 600, 400)
        
        # 文本显示区域
        inputLayout = QtWidgets.QVBoxLayout(self.container)
        inputLayout.setContentsMargins(300, 49, 30, 20)
        
        font = QtGui.QFont()
        font.setFamily("Unifont")
        font.setPointSize(13)
        
        self.textArea = QtWidgets.QTextEdit(self.container)
        self.textArea.setReadOnly(True)
        self.textArea.setStyleSheet("background: rgba(255, 255, 255, 150);")
        self.textArea.setGeometry(0, 0, 600, 350)
        self.textArea.setFont(font)
        inputLayout.addWidget(self.textArea)
        
        # 输入区域
        sendlayout = QtWidgets.QHBoxLayout()
        sendlayout.setContentsMargins(0, 0, 0, 0)
        
        self.input_box = QtWidgets.QLineEdit(self.container)
        self.input_box.returnPressed.connect(self.send_message)
        sendlayout.addWidget(self.input_box)
        
        self.send_button = QtWidgets.QPushButton("发送", self.container)
        self.send_button.clicked.connect(self.send_message)
        sendlayout.addWidget(self.send_button)
        inputLayout.addLayout(sendlayout)
        
        # 设置按钮
        self.setButton = QtWidgets.QLabel(self.container)
        self.setButton.setStyleSheet("color: black; font-family: Unifont; font-size: 16pt;")
        self.setButton.setText("设置")
        self.setButton.setGeometry(310, 25, 50, 24)
        self.setButton.raise_()
        
        # 事件处理
        self.input_box.setDisabled(True)
        self.setButton.setDisabled(True)
        self.setButton.mousePressEvent = lambda event: self.showSettings(event)
        
        # 拖拽相关
        self.is_dragging = False
        self.wheshowSet = False
        
        self.update_button_color()
    
    def load_agents(self):
        """加载角色列表"""
        print("🔄 开始加载角色配置...")
        agents = self.chat_client.get_agents()
        print(f"📋 获取到角色列表: {agents}")
        
        for agent in agents:
            print(f"🔍 加载角色配置: {agent}")
            config = self.chat_client.get_agent_config(agent)
            if config:
                self.agent_configs[agent] = config
                print(f"✅ 角色 {agent} 配置加载成功")
                print(f"   背景路径: {config.get('bg_path', 'N/A')}")
                print(f"   GPT路径: {config.get('gpt_path', 'N/A')}")
                print(f"   SoVITS路径: {config.get('sovits_path', 'N/A')}")
            else:
                print(f"❌ 角色 {agent} 配置加载失败")
        
        print(f"📊 总共加载了 {len(self.agent_configs)} 个角色配置")
    
    def initialize_current_agent(self):
        """初始化当前角色"""
        if not self.is_initialized:
            self.textArea.append("🔄 正在初始化角色...")
            
            def init_thread():
                try:
                    # 获取角色提示词
                    prompt_info = self.chat_client.get_agent_prompt(self.current_agent)
                    if prompt_info and prompt_info.get("prompt"):
                        self.textArea.append(f"📝 角色提示词: {prompt_info['prompt'][:100]}...")
                    
                    # 初始化角色会话
                    init_result = self.chat_client.init_agent_session(self.current_agent)
                    if init_result:
                        ai_response = init_result["response"]
                        # 不过滤think标签，直接显示完整回复
                        self.textArea.append(f"{self.current_agent}: {ai_response}")
                        
                        # 使用新的音频处理方式
                        audio_data_list = init_result.get("audio_data", [])
                        print(f"收到音频数据片段数量: {len(audio_data_list)}")
                        if audio_data_list:
                            print(f"音频数据大小: {[len(data) for data in audio_data_list]} 字节")
                            self.process_audio_data(audio_data_list)
                        else:
                            print("没有收到音频数据")
                    
                    self.is_initialized = True
                    self.input_box.setDisabled(False)
                    self.setButton.setDisabled(False)
                    
                except Exception as e:
                    print(f"角色初始化失败: {e}")
                    self.textArea.append("❌ 角色初始化失败，请检查服务器连接")
                    self.input_box.setDisabled(False)
                    self.setButton.setDisabled(False)
            
            threading.Thread(target=init_thread, daemon=True).start()
    
    def update_background(self):
        """更新背景图片"""
        if self.current_agent in self.agent_configs:
            bg_path = self.agent_configs[self.current_agent]["bg_path"]
            if os.path.exists(bg_path):
                pixmap = QtGui.QPixmap(bg_path).scaled(600, 400, QtCore.Qt.KeepAspectRatio)
                self.imageLabel.setPixmap(pixmap)
            else:
                # 使用默认背景
                default_bg = current_path / "lib" / "bg.png"
                if default_bg.exists():
                    pixmap = QtGui.QPixmap(str(default_bg)).scaled(600, 400, QtCore.Qt.KeepAspectRatio)
                    self.imageLabel.setPixmap(pixmap)
    
    def update_button_color(self):
        """更新按钮颜色"""
        if self.current_agent in self.agent_configs:
            bg_path = self.agent_configs[self.current_agent]["bg_path"]
            if os.path.exists(bg_path):
                pixmap = QtGui.QPixmap(bg_path)
                image = pixmap.toImage()
                
                # 计算按钮区域的平均颜色
                widthin, widthout = 310, 360
                heightin, heightout = 25, 49
                r_total = g_total = b_total = 0
                
                for x in range(widthin, widthout):
                    for y in range(heightin, heightout):
                        color = QColor(image.pixel(x, y))
                        r_total += color.red()
                        g_total += color.green()
                        b_total += color.blue()
                
                pixel_count = (widthout - widthin) * (heightout - heightin)
                avg_r = r_total // pixel_count
                avg_g = g_total // pixel_count
                avg_b = b_total // pixel_count
                
                brightness = (avg_r * 299 + avg_g * 587 + avg_b * 114) // 1000
                color = "white" if brightness > 128 else "black"
                
                self.setButton.setStyleSheet(
                    f"color: {color}; font-family: Unifont; font-size: 16pt;"
                )
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False
    
    def send_message(self):
        """发送消息"""
        if not self.is_initialized:
            self.textArea.append("⚠️ 请等待角色初始化完成")
            return
            
        message = self.input_box.text()
        if not message:
            return
        
        # 显示用户消息
        self.textArea.append(f"You: {message}")
        self.input_box.clear()
        self.input_box.setDisabled(True)
        self.setButton.setDisabled(True)
        
        # 发送消息到服务器
        def send_message_thread():
            try:
                response = self.chat_client.send_message(message, self.current_agent)
                if response:
                    # 立即显示AI回复（不过滤think标签）
                    ai_response = response["response"]
                    self.textArea.append(f"{self.current_agent}: {ai_response}")
                    
                    # 使用生产者-消费者模式处理音频数据流
                    audio_data_list = response.get("audio_data", [])
                    print(f"收到音频数据片段数量: {len(audio_data_list)}")
                    if audio_data_list:
                        print(f"音频数据大小: {[len(data) for data in audio_data_list]} 字节")
                        self.process_audio_data(audio_data_list)
                    else:
                        print("没有收到音频数据")
                
                # 重新启用输入
                self.input_box.setDisabled(False)
                self.setButton.setDisabled(False)
                
            except Exception as e:
                print(f"发送消息失败: {e}")
                self.textArea.append("错误: 无法连接到服务器")
                self.input_box.setDisabled(False)
                self.setButton.setDisabled(False)
        
        threading.Thread(target=send_message_thread, daemon=True).start()
    
    def process_audio_data(self, audio_data_list: List[str]):
        """使用生产者-消费者模式处理base64编码的音频数据流"""
        if not audio_data_list:
            print("音频数据列表为空")
            return
        
        print(f"开始处理音频数据，共 {len(audio_data_list)} 个片段")
        
        # 创建共享队列
        shared_queue = queue.Queue()
        
        def audio_producer(audio_data_list, shared_queue):
            """音频数据生产者"""
            try:
                for i, audio_base64 in enumerate(audio_data_list):
                    if audio_base64:
                        # 解码base64音频数据
                        audio_data = base64.b64decode(audio_base64)
                        
                        # 生成临时文件路径
                        temp_filename = f"{uuid.uuid4()}_{i}.wav"
                        temp_path = current_path / "temp" / temp_filename
                        
                        # 确保temp目录存在
                        temp_path.parent.mkdir(exist_ok=True)
                        
                        # 保存音频文件
                        with open(temp_path, 'wb') as f:
                            f.write(audio_data)
                        
                        print(f"✅ 保存音频片段 {i+1}/{len(audio_data_list)}: {temp_path} ({len(audio_data)} 字节)")
                        # 将文件路径放入队列
                        shared_queue.put(str(temp_path))
                    else:
                        print(f"❌ 音频数据为空: 片段 {i+1}")
                        shared_queue.put(None)
                        
            except Exception as e:
                print(f"❌ 音频数据处理失败: {e}")
                shared_queue.put(None)
            
            # 标记生产线程结束
            shared_queue.put(None)
            print("🎬 生产者线程结束")
        
        def audio_consumer(shared_queue):
            """音频播放消费者"""
            print("🎵 消费者线程开始")
            while True:
                # 从队列中获取文件路径
                file_path = shared_queue.get()
                if file_path is None:
                    # 如果接收到 None，表示生产线程已经结束
                    print("🎵 消费者线程结束")
                    break
                
                try:
                    print(f"🎵 开始播放: {file_path}")
                    # 播放音频
                    audio = AudioSegment.from_file(file_path)
                    print(f"🎵 音频信息: {audio.channels}声道, {audio.frame_rate}Hz, {audio.sample_width}字节/样本")
                    
                    play_obj = sa.play_buffer(
                        audio.raw_data, 
                        num_channels=audio.channels,
                        bytes_per_sample=audio.sample_width, 
                        sample_rate=audio.frame_rate
                    )
                    print(f"🎵 播放对象创建成功，等待播放完成...")
                    play_obj.wait_done()
                    print(f"🎵 播放完成: {file_path}")
                    
                    # 播放完成后立即删除文件
                    os.remove(file_path)
                    print(f"🗑️ 文件已删除: {file_path}")
                    
                except Exception as e:
                    print(f"❌ 音频播放失败: {e}")
                    # 尝试删除临时文件
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"🗑️ 清理失败文件: {file_path}")
                    except:
                        pass
        
        # 启动生产者线程
        producer_thread = threading.Thread(
            target=audio_producer, 
            args=(audio_data_list, shared_queue),
            daemon=True
        )
        producer_thread.start()
        print("🚀 生产者线程已启动")
        
        # 启动消费者线程
        consumer_thread = threading.Thread(
            target=audio_consumer, 
            args=(shared_queue,),
            daemon=True
        )
        consumer_thread.start()
        print("🚀 消费者线程已启动")
    
    def showSettings(self, event):
        """显示设置窗口"""
        self.wheshowSet = True
        self.setting_window = SettingWindow(self)
        self.setting_window.show()

class SettingWindow(QtWidgets.QWidget):
    """设置窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # 初始化UI
        self.setFixedSize(600, 400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # 背景
        self.settingbg = QtWidgets.QLabel(self)
        settingbg_path = current_path / "lib" / "settingbg.png"
        if settingbg_path.exists():
            settingbg = QtGui.QPixmap(str(settingbg_path)).scaled(600, 400, QtCore.Qt.KeepAspectRatio)
            self.settingbg.setPixmap(settingbg)
        self.settingbg.setGeometry(0, 0, 600, 400)
        
        # 布局
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        self.top_layout = QtWidgets.QHBoxLayout()
        self.top_layout.setContentsMargins(0, 20, 20, 0)
        self.top_layout.addStretch()
        
        self.label = QtWidgets.QLabel("设置-切换模型")
        self.label.setStyleSheet("color: black; font-family: Unifont; font-size: 15pt;")
        self.top_layout.addWidget(self.label)
        self.layout.addLayout(self.top_layout)
        
        # 角色选择
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setContentsMargins(40, 0, 40, 0)
        
        self.agent_combo = QtWidgets.QComboBox()
        self.agent_combo.addItems(list(self.parent_window.agent_configs.keys()))
        self.agent_combo.setCurrentText(self.parent_window.current_agent)
        self.agent_combo.currentTextChanged.connect(self.on_agent_changed)
        self.left_layout.addWidget(self.agent_combo)
        
        # 配置显示
        self.config_labels = {}
        config_fields = [
            ("gpt_path", "GPT模型路径"),
            ("sovits_path", "SoVITS模型路径"),
            ("bg_path", "背景路径"),
            ("prompt_path", "Prompt路径"),
            ("ref_audio_path", "参考音频路径")
        ]
        
        for field, title in config_fields:
            title_label = QtWidgets.QLabel(title)
            title_label.setStyleSheet("color: black; font-family: Unifont; font-size: 15pt; background:rgba(255,255,255,0.5)")
            self.left_layout.addWidget(title_label)
            
            value_edit = QtWidgets.QLineEdit()
            value_edit.setReadOnly(True)
            self.left_layout.addWidget(value_edit)
            self.config_labels[field] = value_edit
        
        self.layout.addLayout(self.left_layout)
        self.layout.addStretch()
        
        # 按钮
        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.bottom_layout.setContentsMargins(0, 0, 20, 20)
        self.bottom_layout.addStretch()
        
        self.apply_button = QtWidgets.QPushButton("应用")
        self.apply_button.clicked.connect(self.apply)
        self.bottom_layout.addWidget(self.apply_button)
        
        self.close_button = QtWidgets.QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        self.bottom_layout.addWidget(self.close_button)
        
        self.layout.addLayout(self.bottom_layout)
        
        # 更新配置显示
        self.update_config_display()
    
    def update_config_display(self):
        """更新配置显示"""
        current_agent = self.agent_combo.currentText()
        print(f"🔍 更新配置显示: {current_agent}")
        
        if current_agent in self.parent_window.agent_configs:
            config = self.parent_window.agent_configs[current_agent]
            print(f"✅ 找到角色配置: {config}")
            
            for field, edit in self.config_labels.items():
                # 从字典中获取值，而不是使用getattr
                value = config.get(field, "")
                display_value = str(value) if value != "none" else ""
                edit.setText(display_value)
                print(f"   {field}: {display_value}")
        else:
            print(f"❌ 未找到角色 {current_agent} 的配置")
            # 清空所有字段
            for edit in self.config_labels.values():
                edit.setText("")
    
    def on_agent_changed(self, agent_name):
        """角色改变事件"""
        self.update_config_display()
    
    def apply(self):
        """应用设置"""
        new_agent = self.agent_combo.currentText()
        
        # 切换角色
        if self.parent_window.chat_client.switch_agent(new_agent):
            self.parent_window.current_agent = new_agent
            self.parent_window.update_background()
            self.parent_window.update_button_color()
            self.parent_window.textArea.clear()
            
            # 重新初始化新角色
            self.parent_window.is_initialized = False
            self.parent_window.initialize_current_agent()
        
        self.close()
    
    def close(self):
        """关闭窗口"""
        self.parent_window.wheshowSet = False
        self.deleteLater()

def main():
    """主函数"""
    app = QtWidgets.QApplication(sys.argv)
    window = FloatingWindow()
    window.show()
    
    # 清理函数
    def cleanup():
        window.audio_player.stop()
    
    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
