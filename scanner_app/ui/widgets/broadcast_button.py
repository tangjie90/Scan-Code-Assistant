"""
广播按钮组件
"""
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QColor, QCursor


class BroadcastButton(QPushButton):
    """广播按钮 - 童趣糖果风格"""
    
    clicked_with_key = Signal(str)
    
    def __init__(self, key, label, icon, color, parent=None):
        super().__init__(parent)
        
        self.key = key
        self.label = label
        self.icon = icon
        self.base_color = color
        self._is_playing = False
        
        self.setFixedSize(70, 55)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        self._apply_style()
        self._setup_animations()
    
    def _apply_style(self):
        """应用样式"""
        color = self.base_color
        
        self._normal_style = f"""
            QPushButton {{
                background-color: {color};
                border: 3px solid white;
                border-radius: 12px;
                color: #5D4E4E;
                font-size: 11px;
                font-weight: bold;
                font-family: "Microsoft YaHei UI";
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color, 0.15)};
                border: 3px solid {color};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.1)};
            }}
        """
        self.setStyleSheet(self._normal_style)
        self.setText(f"{self.icon}\n{self.label}")
    
    def _lighten_color(self, color, factor):
        """使颜色变亮"""
        c = QColor(color)
        r = min(255, int(c.red() + (255 - c.red()) * factor))
        g = min(255, int(c.green() + (255 - c.green()) * factor))
        b = min(255, int(c.blue() + (255 - c.blue()) * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _darken_color(self, color, factor):
        """使颜色变暗"""
        c = QColor(color)
        r = int(c.red() * (1 - factor))
        g = int(c.green() * (1 - factor))
        b = int(c.blue() * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _setup_animations(self):
        """设置动画"""
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self._flash_animation)
        self.flash_state = False
    
    @property
    def is_playing(self):
        return self._is_playing
    
    @is_playing.setter
    def is_playing(self, value):
        self._is_playing = value
    
    def start_playing(self):
        """开始播放状态"""
        self._is_playing = True
        self.flash_state = False
        self.flash_timer.start(300)
    
    def stop_playing(self):
        """停止播放状态"""
        self.flash_timer.stop()
        self._is_playing = False
        self.setStyleSheet(self._normal_style)
        self.setEnabled(True)
    
    def _flash_animation(self):
        """闪烁动画"""
        if self.flash_state:
            self.setStyleSheet(self._normal_style)
        else:
            flash_style = f"""
                QPushButton {{
                    background-color: {self._lighten_color(self.base_color, 0.3)};
                    border: 3px solid {self.base_color};
                    border-radius: 12px;
                    color: #5D4E4E;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: "Microsoft YaHei UI";
                    padding: 4px;
                }}
            """
            self.setStyleSheet(flash_style)
        self.flash_state = not self.flash_state
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            if not self._is_playing:
                self.clicked_with_key.emit(self.key)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        super().mouseReleaseEvent(event)
