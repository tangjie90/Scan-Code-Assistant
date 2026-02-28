"""
广播面板组件
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
import json
import os

from .broadcast_button import BroadcastButton


class BroadcastPanel(QFrame):
    """广播面板 - 包含四个广播按钮"""
    
    broadcast_triggered = Signal(str, str)
    broadcast_finished = Signal(str)
    
    DEFAULT_BROADCASTS = {
        "welcome": {
            "text": "欢迎光临，祝您购物愉快！",
            "icon": "👋",
            "label": "迎宾",
            "color": "#B5F2D6"
        },
        "special": {
            "text": "今日特惠商品，限时折扣，欢迎选购！",
            "icon": "🎉",
            "label": "特惠",
            "color": "#FFE5A0"
        },
        "notice": {
            "text": "温馨提示，请保管好您的随身物品，注意安全！",
            "icon": "💡",
            "label": "提示",
            "color": "#B8E0FF"
        },
        "search": {
            "text": "寻人寻物广播，请到服务台咨询！",
            "icon": "📢",
            "label": "寻人",
            "color": "#D4B5FF"
        }
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.broadcast_messages = self._load_config()
        self.buttons = {}
        self._current_playing = None
        
        self._setup_ui()
    
    @property
    def current_playing(self):
        return self._current_playing
    
    @current_playing.setter
    def current_playing(self, value):
        self._current_playing = value
    
    def _load_config(self):
        """加载配置"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config.json')
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('BROADCAST_MESSAGES', self.DEFAULT_BROADCASTS)
        except Exception as e:
            print(f"加载广播配置失败: {e}")
        
        return self.DEFAULT_BROADCASTS
    
    def _setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)
        
        for key, msg in self.broadcast_messages.items():
            button = BroadcastButton(
                key=key,
                label=msg.get('label', key),
                icon=msg.get('icon', '📢'),
                color=msg.get('color', '#B5F2D6')
            )
            button.clicked_with_key.connect(self._on_button_clicked)
            
            self.buttons[key] = button
            layout.addWidget(button)
        
        layout.addStretch()
    
    def _on_button_clicked(self, key):
        """按钮点击处理"""
        if self._current_playing:
            print(f"[BroadcastPanel] 已有广播正在播放: {self._current_playing}")
            return
        
        msg_data = self.broadcast_messages.get(key, {})
        text = msg_data.get('text', '')
        
        if text:
            self._current_playing = key
            self.buttons[key].start_playing()
            print(f"[BroadcastPanel] 触发广播: {key}")
            self.broadcast_triggered.emit(key, text)
    
    def on_broadcast_finished(self, key=None):
        """广播播放完成"""
        finished_key = key or self._current_playing
        
        if finished_key and finished_key in self.buttons:
            self.buttons[finished_key].stop_playing()
            print(f"[BroadcastPanel] 广播完成: {finished_key}")
        
        self._current_playing = None
        self.broadcast_finished.emit(finished_key)
    
    def get_message(self, key):
        """获取广播消息"""
        msg_data = self.broadcast_messages.get(key, {})
        return msg_data.get('text', '')
    
    def stop_all(self):
        """停止所有按钮动画"""
        for button in self.buttons.values():
            button.stop_playing()
        self._current_playing = None
