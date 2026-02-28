"""
气泡日志组件
"""
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QScrollArea, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QPainterPath
from ..styles.theme import CandyTheme


class BubbleMessage(QWidget):
    """气泡消息"""
    
    def __init__(self, text, msg_type='info', parent=None):
        super().__init__(parent)
        
        self.msg_type = msg_type
        self._setup_ui(text)
    
    def _setup_ui(self, text):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        bg_color = self._get_bg_color()
        border_color = self._get_border_color()
        icon = self._get_icon()
        
        self.setStyleSheet(f"""
            BubbleMessage {{
                background-color: {bg_color};
                border-radius: 10px;
                border: 1px solid {border_color};
                padding: 8px 12px;
            }}
        """)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont('Arial', 12))
        
        text_label = QLabel(text)
        text_label.setFont(QFont('Microsoft YaHei UI', 10))
        text_label.setStyleSheet(f"color: {CandyTheme.COLORS['text_primary']}")
        
        content_layout = QHBoxLayout()
        content_layout.addWidget(icon_label)
        content_layout.addWidget(text_label, 1)
        content_layout.setSpacing(8)
        
        layout.addLayout(content_layout)
    
    def _get_bg_color(self):
        """获取背景颜色"""
        colors = {
            'info': '#E3F2FD',
            'success': '#E8F5E9',
            'warning': '#FFF8E1',
            'error': '#FFE4EC',
            'lucky': '#F3E5F5',
            'clear': '#FFE4EC'
        }
        return colors.get(self.msg_type, '#E3F2FD')
    
    def _get_border_color(self):
        """获取边框颜色"""
        colors = {
            'info': '#B8E0FF',
            'success': '#B5F2D6',
            'warning': '#FFE5A0',
            'error': '#FFB5C5',
            'lucky': '#D4B5FF',
            'clear': '#FFB5C5'
        }
        return colors.get(self.msg_type, '#B8E0FF')
    
    def _get_icon(self):
        """获取图标"""
        icons = {
            'info': '📝',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'lucky': '🌟',
            'clear': '🗑️'
        }
        return icons.get(self.msg_type, '📝')


class BubbleLog(QWidget):
    """气泡日志组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.max_messages = 50
        self.messages = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        header = QLabel("📋 操作记录")
        header.setFont(QFont('Microsoft YaHei UI', 13, QFont.Bold))
        header.setStyleSheet(f"color: {CandyTheme.COLORS['text_secondary']}")
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(4)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border-radius: 15px;
                border: none;
            }
        """)
        
        self.scroll_area.setWidget(self.list_widget)
        
        layout.addWidget(header)
        layout.addWidget(self.scroll_area)
    
    def add_message(self, text, msg_type='info'):
        """添加消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M')
        
        message_data = {
            'text': text,
            'type': msg_type,
            'timestamp': timestamp
        }
        
        self.messages.append(message_data)
        
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        self._update_display()
    
    def _update_display(self):
        """更新显示"""
        self.list_widget.clear()
        
        for msg in self.messages:
            item = QListWidgetItem()
            
            bubble = BubbleMessage(msg['text'], msg['type'])
            
            item.setSizeHint(bubble.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, bubble)
        
        self.list_widget.scrollToBottom()
    
    def clear(self):
        """清空消息"""
        self.messages.clear()
        self.list_widget.clear()
