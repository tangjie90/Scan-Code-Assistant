"""
小兔子吉祥物组件
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush
import math


class RabbitMascot(QWidget):
    """小兔子吉祥物"""
    
    state_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 100)
        
        self.state = 'idle'
        self.frame = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        
        self._setup_animations()
        self.animation_timer.start(50)
    
    def _setup_animations(self):
        """设置动画参数"""
        self.bounce_offset = 0
        self.bounce_dir = 1
        self.blink_timer = 0
        self.is_blinking = False
    
    def set_state(self, state):
        """设置状态"""
        self.state = state
        self.frame = 0
        self.state_changed.emit(state)
    
    def _animate(self):
        """动画循环"""
        self.frame += 1
        
        if self.state == 'idle':
            self._animate_idle()
        elif self.state == 'happy':
            self._animate_happy()
        elif self.state == 'surprised':
            self._animate_surprised()
        elif self.state == 'celebrate':
            self._animate_celebrate()
        
        self.update()
    
    def _animate_idle(self):
        """待机动画"""
        self.bounce_offset += 0.15 * self.bounce_dir
        if abs(self.bounce_offset) > 2:
            self.bounce_dir *= -1
        
        self.blink_timer += 1
        if self.blink_timer > 80:
            self.is_blinking = True
            if self.blink_timer > 85:
                self.is_blinking = False
                self.blink_timer = 0
    
    def _animate_happy(self):
        """开心动画"""
        jump = abs(math.sin(self.frame * 0.15)) * 8
        self.bounce_offset = -jump
        
        if self.frame > 40:
            self.state = 'idle'
            self.frame = 0
    
    def _animate_surprised(self):
        """惊喜动画"""
        self.bounce_offset = 0
        
        if self.frame > 30:
            self.state = 'idle'
            self.frame = 0
    
    def _animate_celebrate(self):
        """庆祝动画"""
        jump = abs(math.sin(self.frame * 0.15)) * 6
        self.bounce_offset = -jump
        
        if self.frame > 60:
            self.state = 'idle'
            self.frame = 0
    
    def paintEvent(self, event):
        """绘制小兔子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = 150
        center_y = 50 + self.bounce_offset
        
        self._draw_body(painter, center_x, center_y)
        self._draw_ears(painter, center_x, center_y)
        self._draw_face(painter, center_x, center_y)
        
        painter.end()
    
    def _draw_body(self, painter, x, y):
        """绘制身体"""
        body_color = QColor('#FFB5C5')
        belly_color = QColor('#FFE4EC')
        
        painter.setPen(QPen(QColor('#E5A0A0'), 2))
        painter.setBrush(QBrush(body_color))
        
        painter.drawEllipse(int(x - 35), int(y - 20), 70, 50)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(belly_color))
        painter.drawEllipse(int(x - 25), int(y), 50, 35)
    
    def _draw_ears(self, painter, x, y):
        """绘制耳朵"""
        ear_color = QColor('#FFB5C5')
        inner_color = QColor('#FFE4EC')
        
        painter.setPen(QPen(QColor('#E5A0A0'), 2))
        painter.setBrush(QBrush(ear_color))
        
        painter.drawEllipse(int(x - 30), int(y - 55), 18, 35)
        painter.drawEllipse(int(x + 12), int(y - 55), 18, 35)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(inner_color))
        painter.drawEllipse(int(x - 26), int(y - 48), 10, 20)
        painter.drawEllipse(int(x + 16), int(y - 48), 10, 20)
    
    def _draw_face(self, painter, x, y):
        """绘制脸部"""
        eye_y = y - 5
        
        if self.is_blinking:
            painter.setPen(QPen(QColor('#2D3436'), 2))
            painter.drawLine(int(x - 15), int(eye_y), int(x - 5), int(eye_y))
            painter.drawLine(int(x + 5), int(eye_y), int(x + 15), int(eye_y))
        else:
            eye_color = QColor('#FFFFFF')
            pupil_color = QColor('#2D3436')
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(eye_color))
            painter.drawEllipse(int(x - 15), int(eye_y - 6), 12, 12)
            painter.drawEllipse(int(x + 3), int(eye_y - 6), 12, 12)
            
            painter.setBrush(QBrush(pupil_color))
            painter.drawEllipse(int(x - 12), int(eye_y - 3), 6, 6)
            painter.drawEllipse(int(x + 6), int(eye_y - 3), 6, 6)
        
        nose_color = QColor('#FFB5C5')
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(nose_color))
        painter.drawEllipse(int(x - 4), int(y + 2), 8, 6)
        
        painter.setPen(QPen(QColor('#2D3436'), 2))
        painter.drawArc(int(x - 8), int(y + 8), 16, 12, 200 * 16, 140 * 16)
        
        cheek_color = QColor('#FFD6E0')
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(cheek_color))
        painter.drawEllipse(int(x - 30), int(y - 2), 10, 10)
        painter.drawEllipse(int(x + 20), int(y - 2), 10, 10)
    
    def stop(self):
        """停止动画"""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
