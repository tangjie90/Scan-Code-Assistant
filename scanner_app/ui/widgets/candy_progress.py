"""
彩虹进度条组件 - 修复版
"""
from PySide6.QtWidgets import QProgressBar, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, Signal, Qt
from PySide6.QtGui import QFont


class CandyProgressBar(QWidget):
    """童趣彩虹进度条 - 修复清空问题"""
    
    value_changed = Signal(float)
    
    def __init__(self, max_value=1000, parent=None):
        super().__init__(parent)
        
        self.max_value = max_value
        self._current_value = 0
        self._display_value = 0
        self._is_cleared = False
        
        self._setup_ui()
        self._setup_animations()
    
    def get_value(self):
        return self._display_value
    
    def set_value_property(self, value):
        if self._is_cleared and value > 0:
            return
        self._display_value = value
        self._update_display()
    
    value = Property(float, get_value, set_value_property)
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self.title_label = QLabel("💰 合计金额")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont('Microsoft YaHei UI', 15, QFont.Bold))
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #D4B5FF, stop:0.5 #B8E0FF, stop:1 #FF9EB5);
                color: white;
                padding: 12px;
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        self.amount_label = QLabel("¥ 0")
        self.amount_label.setAlignment(Qt.AlignCenter)
        self.amount_label.setFont(QFont('Arial', 48, QFont.Bold))
        self.amount_label.setStyleSheet("color: #5D4E4E; padding: 10px;")
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(28)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #F5F5F5;
                border-radius: 14px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #FFB5C5, stop:0.2 #FFD6A0, stop:0.4 #FFE5A0,
                            stop:0.6 #B5F2D6, stop:0.8 #B8E0FF, stop:1 #D4B5FF);
                border-radius: 14px;
            }
        """)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.amount_label)
        layout.addWidget(self.progress)
    
    def _setup_animations(self):
        """设置动画"""
        self.value_anim = QPropertyAnimation(self, b"value")
        self.value_anim.setDuration(300)
        self.value_anim.setEasingCurve(QEasingCurve.OutBack)
    
    def set_value(self, value, animate=True):
        """设置进度值"""
        self._is_cleared = False
        self._current_value = value
        
        if self.value_anim.state() == QPropertyAnimation.Running:
            self.value_anim.stop()
        
        if animate and value > 0:
            self.value_anim.setStartValue(self._display_value)
            self.value_anim.setEndValue(value)
            self.value_anim.start()
        else:
            self._display_value = value
            self._update_display()
    
    def _update_display(self):
        """更新显示"""
        if self._is_cleared:
            return
            
        if self._current_value > 0:
            if self._current_value <= 100:
                progress_percent = self._current_value
            elif self._current_value <= 500:
                progress_percent = 50 + (self._current_value - 100) * 0.1
            elif self._current_value <= 1000:
                progress_percent = 80 + (self._current_value - 500) * 0.04
            else:
                progress_percent = min(100, 90 + (self._current_value - 1000) * 0.01)
        else:
            progress_percent = 0
        
        self.progress.setValue(int(progress_percent))
        self.amount_label.setText(f"¥ {int(self._display_value)}")
        self.value_changed.emit(self._display_value)
    
    def clear(self):
        """彻底清空 - 停止所有动画"""
        self._is_cleared = True
        
        if self.value_anim.state() == QPropertyAnimation.Running:
            self.value_anim.stop()
        
        self._current_value = 0
        self._display_value = 0
        self.progress.setValue(0)
        self.amount_label.setText("¥ 0")
        self.value_changed.emit(0)
