"""
童趣装饰元素组件 - 完全Canvas重写版本
特色：小星星、小云朵、小糖果、小爱心
"""
import tkinter as tk
import random
import math


class CandyDecorations(tk.Canvas):
    """童趣装饰元素 - 星星、云朵、糖果"""
    
    DECORATIONS = {
        'star': '✨',
        'cloud': '☁️',
        'candy': '🍬',
        'heart': '💖',
        'gift': '🎁',
        'star2': '⭐',
        'heart2': '❤️',
        'cloud2': '🌸',
    }
    
    def __init__(self, parent, width=800, height=600, **kwargs):
        parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else '#FFFFFF'
        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, bg=parent_bg,
                        **kwargs)
        
        self.width = width
        self.height = height
        self.decorations = []
        self.animation_ids = []
        self.frame = 0
        
        self._create_decorations()
        self._start_animation()
        
        self.bind('<Configure>', self._on_resize)
    
    def _create_decorations(self):
        """创建装饰元素"""
        self.delete('all')
        
        positions = [
            (50, 50), (150, 80), (700, 40),
            (30, 200), (750, 180), (100, 350),
            (720, 320), (60, 500), (740, 480),
        ]
        
        dec_types = list(self.DECORATIONS.keys())
        
        for i, pos in enumerate(positions):
            dec_type = dec_types[i % len(dec_types)]
            size = random.randint(16, 28)
            self.decorations.append({
                'x': pos[0],
                'y': pos[1],
                'type': dec_type,
                'size': size,
                'phase': random.random() * math.pi * 2,
                'speed': random.uniform(0.02, 0.05)
            })
        
        self._draw_decorations()
    
    def _draw_decorations(self):
        """绘制所有装饰"""
        self.delete('decoration')
        
        for dec in self.decorations:
            offset_y = math.sin(self.frame * dec['speed'] + dec['phase']) * 3
            
            self.create_text(
                dec['x'], dec['y'] + offset_y,
                text=self.DECORATIONS[dec['type']],
                font=('Arial', dec['size']),
                tags='decoration'
            )
    
    def _start_animation(self):
        """开始动画"""
        self.frame += 1
        self._draw_decorations()
        self.animation_id = self.after(50, self._start_animation)
    
    def _on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self._create_decorations()
    
    def stop(self):
        """停止动画"""
        if hasattr(self, 'animation_id') and self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None


class RoundedCard(tk.Canvas):
    """圆角卡片容器"""
    
    COLORS = {
        'bg': '#FFFFFF',
        'border': '#FFDDD8',
        'shadow': '#FFCDD8',
    }
    
    def __init__(self, parent, width=400, height=300, corner_radius=20,
                 bg_color='#FFFFFF', border_color='#FFDDD8', **kwargs):
        parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else '#FFFFFF'
        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, bg=parent_bg,
                        **kwargs)
        
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.bg_color = bg_color
        self.border_color = border_color
        
        self._draw()
        
        self.bind('<Configure>', self._on_resize)
    
    def _draw(self):
        """绘制圆角卡片"""
        self.delete('all')
        
        r = self.corner_radius
        
        self._create_rounded_rect(
            4, 4, self.width - 4, self.height - 4,
            r, fill=self.COLORS['shadow'], outline=''
        )
        
        self._create_rounded_rect(
            0, 0, self.width - 8, self.height - 8,
            r, fill=self.bg_color, outline=''
        )
        
        self._draw_dashed_border(0, 0, self.width - 8, self.height - 8, r)
    
    def _draw_dashed_border(self, x1, y1, x2, y2, r):
        """绘制虚线边框"""
        dash_len = 6
        gap_len = 3
        
        self.create_line(x1 + r, y1, x2 - r, y1,
                        fill=self.border_color, width=2,
                        dash=(dash_len, gap_len))
        self.create_line(x1 + r, y2, x2 - r, y2,
                        fill=self.border_color, width=2,
                        dash=(dash_len, gap_len))
        self.create_line(x1, y1 + r, x1, y2 - r,
                        fill=self.border_color, width=2,
                        dash=(dash_len, gap_len))
        self.create_line(x2, y1 + r, x2, y2 - r,
                        fill=self.border_color, width=2,
                        dash=(dash_len, gap_len))
    
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


class BubbleMessage(tk.Canvas):
    """气泡消息组件 - 童趣风格"""
    
    COLORS = {
        'pink': '#FFE4EC',
        'pink_border': '#FFB5C5',
        'blue': '#E3F2FD',
        'blue_border': '#B8E0FF',
        'yellow': '#FFF8E1',
        'yellow_border': '#FFE5A0',
        'green': '#E8F5E9',
        'green_border': '#B5F2D6',
        'purple': '#F3E5F5',
        'purple_border': '#D4B5FF',
    }
    
    TYPE_COLORS = {
        'info': ('blue', 'blue_border'),
        'success': ('green', 'green_border'),
        'warning': ('yellow', 'yellow_border'),
        'error': ('pink', 'pink_border'),
        'lucky': ('purple', 'purple_border'),
        'clear': ('pink', 'pink_border'),
    }
    
    def __init__(self, parent, width=300, height=150, corner_radius=15, **kwargs):
        parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else '#FFFFFF'
        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, bg=parent_bg,
                        **kwargs)
        
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.messages = []
        self.max_messages = 8
        
        self._draw()
        
        self.bind('<Configure>', self._on_resize)
    
    def add_message(self, text, msg_type='info'):
        """添加消息"""
        colors = self.TYPE_COLORS.get(msg_type, self.TYPE_COLORS['info'])
        self.messages.append({
            'text': text,
            'bg_color': self.COLORS[colors[0]],
            'border_color': self.COLORS[colors[1]],
            'type': msg_type
        })
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        self._draw()
    
    def _draw(self):
        """绘制消息"""
        self.delete('all')
        
        if not self.messages:
            return
        
        msg_height = min(32, self.height // min(len(self.messages), 5))
        visible_count = min(len(self.messages), 5)
        
        for i, msg in enumerate(self.messages[-visible_count:]):
            y = i * msg_height + msg_height // 2
            
            self._draw_bubble(
                8, y - msg_height // 2 + 4,
                self.width - 8, y + msg_height // 2 - 4,
                msg['bg_color'], msg['border_color']
            )
            
            icon = self._get_type_icon(msg['type'])
            display_text = f"{icon} {msg['text']}" if icon else msg['text']
            
            if len(display_text) > 30:
                display_text = display_text[:27] + '...'
            
            self.create_text(
                16, y,
                text=display_text,
                fill='#5D4E4E',
                font=('Microsoft YaHei UI', 10),
                anchor='w'
            )
    
    def _draw_bubble(self, x1, y1, x2, y2, bg_color, border_color):
        """绘制气泡"""
        r = 10
        
        self.create_rectangle(x1 + r, y1, x2 - r, y2, fill=bg_color, outline='')
        self.create_rectangle(x1, y1 + r, x2, y2 - r, fill=bg_color, outline='')
        self.create_oval(x1, y1, x1 + 2 * r, y1 + 2 * r, fill=bg_color, outline='')
        self.create_oval(x2 - 2 * r, y1, x2, y1 + 2 * r, fill=bg_color, outline='')
        self.create_oval(x1, y2 - 2 * r, x1 + 2 * r, y2, fill=bg_color, outline='')
        self.create_oval(x2 - 2 * r, y2 - 2 * r, x2, y2, fill=bg_color, outline='')
        
        self.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r,
                       start=90, extent=90, style='arc', outline=border_color, width=1)
        self.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r,
                       start=0, extent=90, style='arc', outline=border_color, width=1)
        self.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2,
                       start=180, extent=90, style='arc', outline=border_color, width=1)
        self.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2,
                       start=270, extent=90, style='arc', outline=border_color, width=1)
        
        self.create_line(x1 + r, y1, x2 - r, y1, fill=border_color, width=1)
        self.create_line(x1 + r, y2, x2 - r, y2, fill=border_color, width=1)
        self.create_line(x1, y1 + r, x1, y2 - r, fill=border_color, width=1)
        self.create_line(x2, y1 + r, x2, y2 - r, fill=border_color, width=1)
    
    def _get_type_icon(self, msg_type):
        """获取消息类型图标"""
        icons = {
            'info': '📝',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'lucky': '🌟',
            'clear': '🗑️',
        }
        return icons.get(msg_type, '')
    
    def _on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self._draw()
    
    def clear(self):
        """清空消息"""
        self.messages = []
        self._draw()
    
    def get_message_count(self):
        """获取消息数量"""
        return len(self.messages)
