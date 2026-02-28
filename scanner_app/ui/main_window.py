"""
主窗口模块
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QSplitter, QStatusBar
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor

from .styles.theme import CandyTheme
from .widgets import CandyButton, CandyTable, CandyProgressBar, RabbitMascot, BubbleLog, BroadcastPanel


class HeaderWidget(QFrame):
    """头部组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFixedHeight(70)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CandyTheme.COLORS['surface']};
                border-bottom-left-radius: 20px;
                border-bottom-right-radius: 20px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(16)
        
        self.mascot = RabbitMascot()
        self.mascot.setFixedSize(55, 55)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title = QLabel("扫码小助手")
        title.setFont(QFont('Microsoft YaHei UI', 28, QFont.Bold))
        title.setStyleSheet(f"color: {CandyTheme.COLORS['primary']};")
        
        subtitle = QLabel("让支付更简单 ✨")
        subtitle.setFont(QFont('Microsoft YaHei UI', 11))
        subtitle.setStyleSheet(f"color: {CandyTheme.COLORS['text_tertiary']};")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(self.mascot)
        layout.addLayout(title_layout)
        layout.addStretch()
        
        self.status_label = QLabel("就绪")
        self.status_label.setFont(QFont('Microsoft YaHei UI', 12))
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {CandyTheme.COLORS['success']};
                color: white;
                padding: 8px 16px;
                border-radius: 12px;
            }}
        """)
        layout.addWidget(self.status_label)
    
    def set_status(self, text, color=None):
        if color is None:
            color = CandyTheme.COLORS['success']
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 8px 16px;
                border-radius: 12px;
            }}
        """)
    
    def set_success(self, text):
        self.set_status(text, CandyTheme.COLORS['success'])
    
    def set_warning(self, text):
        self.set_status(text, CandyTheme.COLORS['warning'])
    
    def set_error(self, text):
        self.set_status(text, CandyTheme.COLORS['error'])
    
    def reset(self):
        self.set_status("就绪", CandyTheme.COLORS['success'])


class CartSection(QFrame):
    """购物清单区域"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CandyTheme.COLORS['background']};
                border: none;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        header = QLabel("🛒 购物清单")
        header.setFont(QFont('Microsoft YaHei UI', 16, QFont.Bold))
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {CandyTheme.COLORS['surface_soft']};
                color: {CandyTheme.COLORS['text_primary']};
                padding: 12px 16px;
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
            }}
        """)
        
        self.count_label = QLabel("0 件")
        self.count_label.setFont(QFont('Microsoft YaHei UI', 13))
        self.count_label.setStyleSheet(f"color: {CandyTheme.COLORS['text_tertiary']};")
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(self.count_label)
        
        self.table = CandyTable()
        
        layout.addLayout(header_layout)
        layout.addWidget(self.table)
    
    def add_item(self, item):
        self.table.add_item(item)
        self._update_count()
    
    def clear(self):
        self.table.clear()
        self._update_count()
    
    def _update_count(self):
        count = len(self.table.get_data())
        self.count_label.setText(f"{count} 件")


class RightPanel(QFrame):
    """右侧面板"""
    
    clear_clicked = Signal()
    broadcast_triggered = Signal(str, str)
    broadcast_finished = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFixedWidth(320)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CandyTheme.COLORS['background']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        self.progress = CandyProgressBar()
        layout.addWidget(self.progress)
        
        broadcast_container = QFrame()
        broadcast_container.setStyleSheet(f"""
            QFrame {{
                background-color: {CandyTheme.COLORS['surface']};
                border-radius: 16px;
            }}
        """)
        broadcast_layout = QVBoxLayout(broadcast_container)
        broadcast_layout.setContentsMargins(12, 8, 12, 8)
        
        broadcast_title = QLabel("📢 快捷广播")
        broadcast_title.setFont(QFont('Microsoft YaHei UI', 12, QFont.Bold))
        broadcast_title.setStyleSheet(f"color: {CandyTheme.COLORS['text_primary']};")
        broadcast_layout.addWidget(broadcast_title)
        
        self.broadcast_panel = BroadcastPanel()
        self.broadcast_panel.broadcast_triggered.connect(self._on_broadcast_triggered)
        broadcast_layout.addWidget(self.broadcast_panel)
        
        layout.addWidget(broadcast_container)
        
        mascot_container = QFrame()
        mascot_container.setStyleSheet(f"""
            QFrame {{
                background-color: {CandyTheme.COLORS['surface']};
                border-radius: 20px;
            }}
        """)
        mascot_layout = QVBoxLayout(mascot_container)
        mascot_layout.setContentsMargins(8, 8, 8, 8)
        
        self.mascot = RabbitMascot()
        mascot_layout.addWidget(self.mascot)
        
        layout.addWidget(mascot_container)
        
        self.clear_btn = CandyButton("🗑️ 清空购物车")
        self.clear_btn.clicked.connect(self.clear_clicked.emit)
        layout.addWidget(self.clear_btn)
        
        self.log = BubbleLog()
        layout.addWidget(self.log, 1)
    
    def _on_broadcast_triggered(self, key, text):
        print(f"[RightPanel] 广播触发: {key}")
        self.broadcast_triggered.emit(key, text)
    
    def on_broadcast_finished(self, key=None):
        print(f"[RightPanel] 广播完成: {key}")
        self.broadcast_panel.on_broadcast_finished(key)
    
    def add_log(self, text, log_type='info'):
        self.log.add_message(text, log_type)
    
    def clear_log(self):
        self.log.clear()
    
    def set_total(self, value):
        self.progress.set_value(value)
    
    def clear_all(self):
        self.progress.clear()
        self.log.clear()
    
    def stop_broadcast(self):
        self.broadcast_panel.stop_all()


class MainWindow(QMainWindow):
    """主窗口"""
    
    scan_received = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("扫码小助手")
        self.setGeometry(100, 100, 1100, 780)
        self.setMinimumSize(900, 600)
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        self.header = HeaderWidget()
        layout.addWidget(self.header)
        
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        
        self.cart_section = CartSection()
        content_layout.addWidget(self.cart_section, 1)
        
        self.right_panel = RightPanel()
        self.right_panel.clear_clicked.connect(self._on_clear_clicked)
        content_layout.addWidget(self.right_panel)
        
        layout.addWidget(content, 1)
    
    def _apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {CandyTheme.COLORS['background']};
            }}
        """)
    
    def _on_clear_clicked(self):
        self.cart_section.clear()
        self.right_panel.clear_all()
        self.right_panel.add_log("购物车已清空", 'clear')
    
    def add_cart_item(self, item):
        self.cart_section.add_item(item)
    
    def clear_cart(self):
        self.cart_section.clear()
        self.right_panel.clear_all()
    
    def set_total(self, value):
        self.right_panel.set_total(value)
    
    def add_log(self, text, log_type='info'):
        self.right_panel.add_log(text, log_type)
    
    def set_status(self, text, color=None):
        if color:
            self.header.set_status(text, color)
        else:
            self.header.set_status(text)
    
    def set_success(self, text):
        self.header.set_success(text)
    
    def set_warning(self, text):
        self.header.set_warning(text)
    
    def set_error(self, text):
        self.header.set_error(text)
    
    def reset_status(self):
        self.header.reset()
    
    def set_mascot_state(self, state):
        self.right_panel.mascot.set_state(state)
    
    def on_broadcast_finished(self, key=None):
        print(f"[MainWindow] 广播完成回调: {key}")
        self.right_panel.on_broadcast_finished(key)
