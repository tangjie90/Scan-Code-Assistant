"""
童趣糖果按钮组件
"""
from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Signal, QSize, Qt
from PySide6.QtGui import QColor, QCursor
from ..styles.theme import CandyTheme


class CandyButton(QPushButton):
    """童趣糖果按钮"""
    
    clicked_anim = Signal()
    
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        
        self.icon = icon
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setColor(QColor(CandyTheme.COLORS['shadow']))
        self.shadow_effect.setOffset(0, 4)
        
        self.setGraphicsEffect(self.shadow_effect)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedSize(280, 56)
        
        self._apply_style()
        self._setup_animations()
    
    def _apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFBDBD, stop:1 #FF9A9A);
                border-radius: 28px;
                color: white;
                font-size: 17px;
                font-weight: bold;
                font-family: "Microsoft YaHei UI";
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD0D0, stop:1 #FFB5B5);
            }
            QPushButton:pressed {
                background: #E57070;
            }
        """)
    
    def _setup_animations(self):
        """设置动画"""
        self.blur_anim = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.blur_anim.setDuration(200)
        self.blur_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        self.offset_anim = QPropertyAnimation(self.shadow_effect, b"offset")
        self.offset_anim.setDuration(200)
        self.offset_anim.setEasingCurve(QEasingCurve.OutQuad)
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.blur_anim.setStartValue(10)
        self.blur_anim.setEndValue(20)
        self.blur_anim.start()
        
        self.offset_anim.setStartValue(4)
        self.offset_anim.setEndValue(8)
        self.offset_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.blur_anim.setStartValue(20)
        self.blur_anim.setEndValue(10)
        self.blur_anim.start()
        
        self.offset_anim.setStartValue(8)
        self.offset_anim.setEndValue(4)
        self.offset_anim.start()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.blur_anim.setStartValue(20)
        self.blur_anim.setEndValue(2)
        self.blur_anim.start()
        
        self.offset_anim.setStartValue(8)
        self.offset_anim.setEndValue(2)
        self.offset_anim.start()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.blur_anim.setStartValue(2)
        self.blur_anim.setEndValue(10)
        self.blur_anim.start()
        
        self.offset_anim.setStartValue(2)
        self.offset_anim.setEndValue(4)
        self.offset_anim.start()
        
        self.clicked_anim.emit()
        super().mouseReleaseEvent(event)
