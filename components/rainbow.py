"""
彩虹进度条 - 金额显示
"""
import tkinter as tk


class RainbowProgressBar(tk.Canvas):
    """彩虹进度条"""
    
    RAINBOW_COLORS = [
        '#FFB5C5',
        '#FFD6A0',
        '#FFE5A0',
        '#B5F2D6',
        '#B8E0FF',
        '#D4B5FF',
        '#FFB5C5'
    ]
    
    def __init__(self, parent, width=280, height=40, max_value=50, bg=None, **kwargs):
        if bg is None:
            bg = parent.cget('bg')
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=bg, **kwargs)
        
        self.bar_width = width
        self.bar_height = height
        self.max_value = max_value
        self.actual_value = 0
        self.display_value = 0
        self.current_value = 0
        self.animation_id = None
        
        self._draw()
    
    def set_value(self, value, animate=True):
        """设置当前值"""
        self.actual_value = value
        self.display_value = min(value, self.max_value)
        
        if animate:
            self._animate_to_target()
        else:
            self.current_value = self.display_value
            self._draw()
    
    def _animate_to_target(self):
        """动画过渡到目标值"""
        if self.animation_id:
            self.after_cancel(self.animation_id)
        
        if not hasattr(self, 'current_value'):
            self.current_value = 0
        
        diff = self.display_value - self.current_value
        
        if abs(diff) < 0.5:
            self.current_value = self.display_value
            self._draw()
            return
        
        self.current_value += diff * 0.15
        self._draw()
        
        self.animation_id = self.after(16, self._animate_to_target)
    
    def _draw(self):
        """绘制进度条"""
        self.delete('all')
        
        padding = 4
        radius = (self.bar_height - padding * 2) // 2
        
        self._draw_rounded_rect(
            padding, padding,
            self.bar_width - padding, self.bar_height - padding,
            radius, '#E8E8E8'
        )
        
        fill_width = (self.current_value / self.max_value) * (self.bar_width - padding * 2)
        fill_width = min(fill_width, self.bar_width - padding * 2)
        
        if fill_width > 0:
            segment_width = (self.bar_width - padding * 2) / len(self.RAINBOW_COLORS)
            
            for i, color in enumerate(self.RAINBOW_COLORS):
                x1 = padding + i * segment_width
                x2 = padding + (i + 1) * segment_width
                
                if x1 < padding + fill_width:
                    x2 = min(x2, padding + fill_width)
                    self._draw_rounded_rect_segment(
                        x1, padding, x2, self.bar_height - padding,
                        radius, color, i == 0, i >= len(self.RAINBOW_COLORS) - 1 or x2 >= padding + fill_width
                    )
        
        text = f"¥ {self.actual_value:.0f}"
        text_color = 'white' if self.display_value > self.max_value * 0.2 else '#666666'
        self.create_text(
            self.bar_width / 2, self.bar_height / 2,
            text=text, font=('Microsoft YaHei UI', 14, 'bold'),
            fill=text_color, tags='text'
        )
    
    def _draw_rounded_rect(self, x1, y1, x2, y2, radius, color):
        """绘制圆角矩形"""
        self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, 
                       start=90, extent=90, style='pieslice', fill=color, outline='')
        self.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, 
                       start=0, extent=90, style='pieslice', fill=color, outline='')
        self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, 
                       start=180, extent=90, style='pieslice', fill=color, outline='')
        self.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, 
                       start=270, extent=90, style='pieslice', fill=color, outline='')
        
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=color, outline='')
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill=color, outline='')
    
    def _draw_rounded_rect_segment(self, x1, y1, x2, y2, radius, color, is_first, is_last):
        """绘制进度条分段"""
        if is_first and is_last:
            self._draw_rounded_rect(x1, y1, x2, y2, radius, color)
        elif is_first:
            self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, 
                           start=90, extent=90, style='pieslice', fill=color, outline='')
            self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, 
                           start=180, extent=90, style='pieslice', fill=color, outline='')
            self.create_rectangle(x1 + radius, y1, x2, y2, fill=color, outline='')
            self.create_rectangle(x1, y1 + radius, x1 + radius, y2 - radius, fill=color, outline='')
        else:
            self.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
