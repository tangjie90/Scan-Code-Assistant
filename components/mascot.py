"""
吉祥物角色 - 可爱小狐狸
"""
import math


class MascotCharacter:
    """吉祥物角色 - 小狐狸"""
    
    COLORS = {
        'body': '#FF6B35',
        'body_dark': '#E85D04',
        'belly': '#FFEAA7',
        'cheek': '#FF9F43',
        'nose': '#2D3436',
        'eye': '#2D3436',
        'eye_white': '#FFFFFF'
    }
    
    def __init__(self, canvas, x, y, size=80):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.state = 'idle'
        self.frame = 0
        self.animation_id = None
        
        self.bounce_offset = 0
        self.bounce_dir = 1
        self.blink_timer = 0
        self.is_blinking = False
        self.tail_angle = 0
    
    def set_state(self, state):
        """设置角色状态"""
        self.state = state
        self.frame = 0
    
    def draw(self):
        """绘制角色"""
        self.canvas.delete('mascot')
        
        if self.state == 'idle':
            self._draw_idle()
        elif self.state == 'happy':
            self._draw_happy()
        elif self.state == 'surprised':
            self._draw_surprised()
        elif self.state == 'celebrate':
            self._draw_celebrate()
    
    def _draw_idle(self):
        """待机动画"""
        self.bounce_offset += 0.2 * self.bounce_dir
        if abs(self.bounce_offset) > 2:
            self.bounce_dir *= -1
        
        self.blink_timer += 1
        if self.blink_timer > 80:
            self.is_blinking = True
            if self.blink_timer > 85:
                self.is_blinking = False
                self.blink_timer = 0
        
        self.tail_angle = math.sin(self.frame * 0.1) * 10
        
        y = self.y + self.bounce_offset
        self._draw_body(y)
        self._draw_face(y)
        self._draw_tail(y)
        
        self.frame += 1
    
    def _draw_happy(self):
        """开心动画"""
        jump = abs(math.sin(self.frame * 0.15)) * 12
        y = self.y - jump
        
        self.tail_angle = math.sin(self.frame * 0.3) * 20
        
        self._draw_body(y)
        self._draw_happy_face(y)
        self._draw_tail(y)
        
        self.frame += 1
        if self.frame > 40:
            self.state = 'idle'
            self.frame = 0
    
    def _draw_surprised(self):
        """惊喜动画"""
        scale = 1 + math.sin(self.frame * 0.2) * 0.05
        y = self.y
        
        self._draw_body(y, scale)
        self._draw_surprised_face(y)
        
        self.frame += 1
        if self.frame > 30:
            self.state = 'idle'
            self.frame = 0
    
    def _draw_celebrate(self):
        """庆祝动画"""
        swing = math.sin(self.frame * 0.2) * 8
        jump = abs(math.sin(self.frame * 0.15)) * 8
        
        x = self.x + swing
        y = self.y - jump
        
        self.tail_angle = math.sin(self.frame * 0.4) * 25
        
        self._draw_body(y, x_offset=swing)
        self._draw_happy_face(y)
        self._draw_tail(y, x_offset=swing)
        
        self.frame += 1
        if self.frame > 60:
            self.state = 'idle'
            self.frame = 0
    
    def _draw_body(self, y, scale=1, x_offset=0):
        """绘制身体"""
        x = self.x + x_offset
        s = self.size * scale
        
        self.canvas.create_oval(
            x - s * 0.5, y - s * 0.4,
            x + s * 0.5, y + s * 0.5,
            fill=self.COLORS['body'], outline=self.COLORS['body_dark'], width=2, tags='mascot'
        )
        
        self.canvas.create_oval(
            x - s * 0.35, y - s * 0.1,
            x + s * 0.35, y + s * 0.4,
            fill=self.COLORS['belly'], outline='', tags='mascot'
        )
        
        ear_size = s * 0.25
        self.canvas.create_polygon(
            x - s * 0.35, y - s * 0.35,
            x - s * 0.5, y - s * 0.7,
            x - s * 0.15, y - s * 0.35,
            fill=self.COLORS['body'], outline=self.COLORS['body_dark'], width=2, tags='mascot'
        )
        self.canvas.create_polygon(
            x + s * 0.35, y - s * 0.35,
            x + s * 0.5, y - s * 0.7,
            x + s * 0.15, y - s * 0.35,
            fill=self.COLORS['body'], outline=self.COLORS['body_dark'], width=2, tags='mascot'
        )
        
        self.canvas.create_oval(
            x - s * 0.28, y - s * 0.55,
            x - s * 0.12, y - s * 0.4,
            fill=self.COLORS['belly'], outline='', tags='mascot'
        )
        self.canvas.create_oval(
            x + s * 0.12, y - s * 0.55,
            x + s * 0.28, y - s * 0.4,
            fill=self.COLORS['belly'], outline='', tags='mascot'
        )
    
    def _draw_face(self, y):
        """绘制脸部"""
        x = self.x
        s = self.size
        
        eye_y = y - s * 0.15
        eye_size = s * 0.12
        
        if self.is_blinking:
            self.canvas.create_line(
                x - s * 0.2, eye_y,
                x - s * 0.08, eye_y,
                fill=self.COLORS['eye'], width=2, tags='mascot'
            )
            self.canvas.create_line(
                x + s * 0.08, eye_y,
                x + s * 0.2, eye_y,
                fill=self.COLORS['eye'], width=2, tags='mascot'
            )
        else:
            self.canvas.create_oval(
                x - s * 0.2 - eye_size, eye_y - eye_size,
                x - s * 0.2 + eye_size, eye_y + eye_size,
                fill=self.COLORS['eye_white'], outline=self.COLORS['eye'], width=1, tags='mascot'
            )
            self.canvas.create_oval(
                x + s * 0.2 - eye_size, eye_y - eye_size,
                x + s * 0.2 + eye_size, eye_y + eye_size,
                fill=self.COLORS['eye_white'], outline=self.COLORS['eye'], width=1, tags='mascot'
            )
            
            pupil_size = eye_size * 0.5
            self.canvas.create_oval(
                x - s * 0.2 - pupil_size, eye_y - pupil_size,
                x - s * 0.2 + pupil_size, eye_y + pupil_size,
                fill=self.COLORS['eye'], outline='', tags='mascot'
            )
            self.canvas.create_oval(
                x + s * 0.2 - pupil_size, eye_y - pupil_size,
                x + s * 0.2 + pupil_size, eye_y + pupil_size,
                fill=self.COLORS['eye'], outline='', tags='mascot'
            )
        
        nose_size = s * 0.06
        self.canvas.create_oval(
            x - nose_size, y - nose_size,
            x + nose_size, y + nose_size,
            fill=self.COLORS['nose'], outline='', tags='mascot'
        )
        
        self.canvas.create_arc(
            x - s * 0.12, y,
            x + s * 0.12, y + s * 0.15,
            start=200, extent=140, style='arc',
            outline=self.COLORS['nose'], width=2, tags='mascot'
        )
        
        cheek_size = s * 0.08
        self.canvas.create_oval(
            x - s * 0.35, y - s * 0.05,
            x - s * 0.35 + cheek_size * 2, y - s * 0.05 + cheek_size * 2,
            fill=self.COLORS['cheek'], outline='', tags='mascot'
        )
        self.canvas.create_oval(
            x + s * 0.35 - cheek_size * 2, y - s * 0.05,
            x + s * 0.35, y - s * 0.05 + cheek_size * 2,
            fill=self.COLORS['cheek'], outline='', tags='mascot'
        )
    
    def _draw_happy_face(self, y):
        """绘制开心的脸"""
        x = self.x
        s = self.size
        
        eye_y = y - s * 0.15
        
        self.canvas.create_arc(
            x - s * 0.22, eye_y - s * 0.08,
            x - s * 0.08, eye_y + s * 0.08,
            start=0, extent=180, style='arc',
            outline=self.COLORS['eye'], width=2, tags='mascot'
        )
        self.canvas.create_arc(
            x + s * 0.08, eye_y - s * 0.08,
            x + s * 0.22, eye_y + s * 0.08,
            start=0, extent=180, style='arc',
            outline=self.COLORS['eye'], width=2, tags='mascot'
        )
        
        nose_size = s * 0.06
        self.canvas.create_oval(
            x - nose_size, y - nose_size,
            x + nose_size, y + nose_size,
            fill=self.COLORS['nose'], outline='', tags='mascot'
        )
        
        self.canvas.create_arc(
            x - s * 0.15, y - s * 0.05,
            x + s * 0.15, y + s * 0.2,
            start=200, extent=140, style='chord',
            fill='#FF6B6B', outline=self.COLORS['nose'], width=2, tags='mascot'
        )
        
        cheek_size = s * 0.1
        self.canvas.create_oval(
            x - s * 0.38, y - s * 0.08,
            x - s * 0.38 + cheek_size * 2, y - s * 0.08 + cheek_size * 2,
            fill=self.COLORS['cheek'], outline='', tags='mascot'
        )
        self.canvas.create_oval(
            x + s * 0.38 - cheek_size * 2, y - s * 0.08,
            x + s * 0.38, y - s * 0.08 + cheek_size * 2,
            fill=self.COLORS['cheek'], outline='', tags='mascot'
        )
    
    def _draw_surprised_face(self, y):
        """绘制惊喜的脸"""
        x = self.x
        s = self.size
        
        eye_y = y - s * 0.15
        eye_size = s * 0.18
        
        self.canvas.create_oval(
            x - s * 0.22 - eye_size, eye_y - eye_size,
            x - s * 0.22 + eye_size, eye_y + eye_size,
            fill=self.COLORS['eye_white'], outline=self.COLORS['eye'], width=2, tags='mascot'
        )
        self.canvas.create_oval(
            x + s * 0.22 - eye_size, eye_y - eye_size,
            x + s * 0.22 + eye_size, eye_y + eye_size,
            fill=self.COLORS['eye_white'], outline=self.COLORS['eye'], width=2, tags='mascot'
        )
        
        pupil_size = eye_size * 0.4
        self.canvas.create_oval(
            x - s * 0.22 - pupil_size, eye_y - pupil_size,
            x - s * 0.22 + pupil_size, eye_y + pupil_size,
            fill=self.COLORS['eye'], outline='', tags='mascot'
        )
        self.canvas.create_oval(
            x + s * 0.22 - pupil_size, eye_y - pupil_size,
            x + s * 0.22 + pupil_size, eye_y + pupil_size,
            fill=self.COLORS['eye'], outline='', tags='mascot'
        )
        
        nose_size = s * 0.06
        self.canvas.create_oval(
            x - nose_size, y - nose_size,
            x + nose_size, y + nose_size,
            fill=self.COLORS['nose'], outline='', tags='mascot'
        )
        
        mouth_size = s * 0.1
        self.canvas.create_oval(
            x - mouth_size, y + s * 0.05,
            x + mouth_size, y + s * 0.05 + mouth_size * 1.5,
            fill='#FF6B6B', outline=self.COLORS['nose'], width=2, tags='mascot'
        )
    
    def _draw_tail(self, y, x_offset=0):
        """绘制尾巴"""
        x = self.x + x_offset
        s = self.size
        
        tail_x = x + s * 0.45
        tail_y = y + s * 0.1
        
        angle = math.radians(self.tail_angle)
        
        points = [
            tail_x, tail_y,
            tail_x + s * 0.3 * math.cos(angle + 0.3), tail_y - s * 0.2 + s * 0.3 * math.sin(angle),
            tail_x + s * 0.4 * math.cos(angle), tail_y - s * 0.3 + s * 0.4 * math.sin(angle),
            tail_x + s * 0.3 * math.cos(angle - 0.3), tail_y - s * 0.1 + s * 0.3 * math.sin(angle),
        ]
        
        self.canvas.create_polygon(points, fill=self.COLORS['body'], 
                                   outline=self.COLORS['body_dark'], width=2, tags='mascot')
    
    def animate(self):
        """动画循环"""
        self.draw()
        self.animation_id = self.canvas.after(50, self.animate)
    
    def stop(self):
        """停止动画"""
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)
            self.animation_id = None
