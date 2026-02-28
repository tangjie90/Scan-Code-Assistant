"""
童趣卡通金额显示组件 - 完全Canvas重写版本
特色：渐变蓝紫顶部栏、金额放大2倍、卡通金币装饰
"""
import tkinter as tk
import math


class CandyTotal(tk.Canvas):
    """卡通风格金额显示 - 童趣糖果风格"""
    
    COLORS = {
        'bg': '#FFFFFF',
        'header_purple': '#D4B5FF',
        'header_blue': '#B8E0FF',
        'header_pink': '#FF9EB5',
        'border': '#FFDDD8',
        'text': '#5D4E4E',
        'text_light': '#8B7E7E',
        'money': '#FFD700',
        'money_dark': '#FFA500',
        'money_shadow': '#FFE4B5',
        'shadow': '#FFCDD8',
        'progress_bg': '#F5F5F5',
    }
    
    RAINBOW_COLORS = [
        '#FFB5C5',
        '#FFD6A0',
        '#FFE5A0',
        '#B5F2D6',
        '#B8E0FF',
        '#D4B5FF',
        '#FFB5C5'
    ]
    
    def __init__(self, parent, width=280, height=220, max_value=50, **kwargs):
        parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else '#FFFFFF'
        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, bg=parent_bg,
                        **kwargs)
        
        self.width = width
        self.height = height
        self.corner_radius = 20
        self.max_value = max_value
        self.current_value = 0
        self.display_value = 0
        self.animation_id = None
        self.coin_angle = 0
        
        self._draw()
        
        self.bind('<Configure>', self._on_resize)
    
    def _draw(self):
        self.delete('all')
        
        self._draw_shadow()
        self._draw_background()
        self._draw_header()
        self._draw_amount()
        self._draw_progress()
        self._draw_coins()
    
    def _draw_shadow(self):
        """绘制阴影"""
        r = self.corner_radius
        w = self.width
        h = self.height
        
        self._create_rounded_rect(
            6, 6, w - 2, h - 2,
            r, fill=self.COLORS['shadow'], outline=''
        )
    
    def _draw_background(self):
        """绘制背景"""
        r = self.corner_radius
        w = self.width
        h = self.height
        
        self._create_rounded_rect(
            0, 0, w - 8, h - 8,
            r, fill=self.COLORS['bg'], outline=''
        )
    
    def _draw_header(self):
        """绘制渐变蓝紫顶部栏"""
        header_height = 48
        r = self.corner_radius
        w = self.width - 8
        
        colors = [
            self.COLORS['header_purple'],
            self.COLORS['header_blue'],
            self.COLORS['header_pink']
        ]
        
        section_width = w / 3
        
        for i, color in enumerate(colors):
            x1 = i * section_width
            x2 = (i + 1) * section_width
            if i == 2:
                x2 = w
            
            self.create_rectangle(
                x1, 0, x2, header_height,
                fill=color, outline=''
            )
        
        self.create_arc(
            0, 0, 2 * r, 2 * r,
            start=180, extent=90,
            fill=colors[0], outline=''
        )
        self.create_arc(
            w - 2 * r, 0, w, 2 * r,
            start=270, extent=90,
            fill=colors[-1], outline=''
        )
        
        self.create_rectangle(
            r, 0, w - r, r,
            fill=colors[0], outline=''
        )
        
        self.create_text(
            w // 2, header_height // 2,
            text='💰 合计金额',
            fill=self.COLORS['text'],
            font=('Microsoft YaHei UI', 15, 'bold')
        )
    
    def _draw_amount(self):
        """绘制金额 - 放大2倍"""
        header_height = 48
        amount_y = header_height + 55
        
        self.create_text(
            self.width // 2 - 70, amount_y,
            text='¥',
            fill=self.COLORS['money_dark'],
            font=('Arial', 32, 'bold'),
            anchor='e'
        )
        
        amount_str = f'{self.display_value:.0f}'
        self.create_text(
            self.width // 2 + 10, amount_y,
            text=amount_str,
            fill=self.COLORS['text'],
            font=('Arial', 56, 'bold'),
            anchor='center'
        )
        
        self.create_text(
            self.width // 2 + 70, amount_y + 15,
            text='元',
            fill=self.COLORS['text_light'],
            font=('Microsoft YaHei UI', 16),
            anchor='w'
        )
    
    def _draw_progress(self):
        """绘制彩虹进度条"""
        progress_y = self.height - 55
        progress_height = 28
        progress_width = self.width - 60
        r = 14
        
        self._create_rounded_rect(
            26, progress_y, 26 + progress_width, progress_y + progress_height,
            r, fill=self.COLORS['progress_bg'], outline=''
        )
        
        if self.max_value > 0 and self.display_value > 0:
            fill_ratio = min(self.display_value / self.max_value, 1.0)
            fill_width = fill_ratio * progress_width
            
            segment_width = progress_width / len(self.RAINBOW_COLORS)
            
            for i, color in enumerate(self.RAINBOW_COLORS):
                x1 = 26 + i * segment_width
                x2 = 26 + (i + 1) * segment_width
                
                if x1 < 26 + fill_width:
                    x2 = min(x2, 26 + fill_width)
                    
                    is_first = (i == 0)
                    is_last = (x2 >= 26 + fill_width)
                    
                    self._draw_progress_segment(
                        x1, progress_y, x2, progress_y + progress_height,
                        r, color, is_first, is_last
                    )
        
        self.create_text(
            self.width // 2, progress_y + progress_height // 2,
            text=f'目标: {self.max_value:.0f}元',
            fill='#888888' if self.display_value < self.max_value * 0.3 else 'white',
            font=('Microsoft YaHei UI', 11),
        )
    
    def _draw_progress_segment(self, x1, y1, x2, y2, r, color, is_first, is_last):
        """绘制进度条分段"""
        if is_first and is_last:
            self._create_rounded_rect(x1, y1, x2, y2, r, fill=color, outline='')
        elif is_first:
            self.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r,
                           start=90, extent=90, style='pieslice', fill=color, outline='')
            self.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2,
                           start=180, extent=90, style='pieslice', fill=color, outline='')
            self.create_rectangle(x1 + r, y1, x2, y2, fill=color, outline='')
            self.create_rectangle(x1, y1 + r, x1 + r, y2 - r, fill=color, outline='')
        else:
            self.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
    
    def _draw_coins(self):
        """绘制卡通金币装饰"""
        self.coin_angle += 0.1
        
        self._draw_coin(25, self.height - 20, 14, 0.9 + 0.1 * math.sin(self.coin_angle))
        self._draw_coin(self.width - 35, self.height - 20, 14, 0.9 + 0.1 * math.sin(self.coin_angle + 1))
    
    def _draw_coin(self, x, y, size, scale=1.0):
        """绘制单个卡通金币"""
        size = size * scale
        
        self.create_oval(
            x - size - 2, y - size + 2,
            x + size - 2, y + size + 2,
            fill=self.COLORS['money_shadow'], outline=''
        )
        
        self.create_oval(
            x - size, y - size,
            x + size, y + size,
            fill=self.COLORS['money'], outline=self.COLORS['money_dark'], width=2
        )
        
        inner_size = size * 0.75
        self.create_oval(
            x - inner_size, y - inner_size,
            x + inner_size, y + inner_size,
            fill='', outline=self.COLORS['money_dark'], width=1
        )
        
        self.create_text(
            x, y,
            text='¥',
            fill=self.COLORS['money_dark'],
            font=('Arial', int(size * 0.9), 'bold')
        )
    
    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """创建圆角矩形"""
        self.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r,
                       start=90, extent=90, style='pieslice', **kwargs)
        self.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r,
                       start=0, extent=90, style='pieslice', **kwargs)
        self.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2,
                       start=180, extent=90, style='pieslice', **kwargs)
        self.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2,
                       start=270, extent=90, style='pieslice', **kwargs)
        
        self.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)
        self.create_rectangle(x1, y1 + r, x2, y2 - r, **kwargs)
    
    def _on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self._draw()
    
    def set_value(self, value, animate=True):
        """设置金额"""
        self.current_value = value
        if animate:
            self._animate_to_target()
        else:
            self.display_value = min(value, self.max_value)
            self._draw()
    
    def _animate_to_target(self):
        """动画过渡到目标值"""
        if self.animation_id:
            self.after_cancel(self.animation_id)
        
        target = min(self.current_value, self.max_value)
        diff = target - self.display_value
        
        if abs(diff) < 0.5:
            self.display_value = target
            self._draw()
            return
        
        self.display_value += diff * 0.15
        self._draw()
        
        self.animation_id = self.after(16, self._animate_to_target)
    
    def set_max(self, max_value):
        """设置最大值"""
        self.max_value = max_value
        self._draw()
    
    def get_value(self):
        """获取当前值"""
        return self.current_value
