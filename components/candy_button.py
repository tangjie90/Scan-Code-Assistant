"""
童趣卡通按钮组件 - 完全Canvas重写版本
特色：柔雾红撞色、悬浮立体效果、超大圆角28px
"""
import tkinter as tk


class CandyButton(tk.Canvas):
    """卡通风格按钮 - 童趣糖果风格"""
    
    COLORS = {
        'normal_bg': '#FF9A9A',
        'normal_light': '#FFBDBD',
        'normal_dark': '#E57070',
        'hover_bg': '#FFB5B5',
        'hover_light': '#FFD0D0',
        'hover_dark': '#FF8080',
        'press_bg': '#E57070',
        'press_light': '#FF9A9A',
        'press_dark': '#CC5050',
        'shadow': '#FFCDD8',
        'shadow_dark': '#E5A0A0',
        'text': '#FFFFFF',
        'text_shadow': '#CC5050',
    }
    
    def __init__(self, parent, text, command=None, width=260, height=56,
                 bg_color='#FF9A9A', hover_color='#FFB5B5', press_color='#E57070',
                 text_color='white', corner_radius=28, icon=None):
        parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else '#FFFFFF'
        super().__init__(parent, width=width, height=height + 12,
                        highlightthickness=0, bg=parent_bg)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.press_color = press_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.width = width
        self.height = height
        self.text = text
        self.icon = icon
        self.is_hovered = False
        self.is_pressed = False
        self.shadow_offset = 6
        
        self._draw_button('normal')
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
    
    def _draw_button(self, state='normal'):
        self.delete('all')
        
        w = self.width
        h = self.height
        r = self.corner_radius
        
        if state == 'pressed':
            shadow_offset = 2
            main_color = self.press_color
            shadow_color = self.COLORS['shadow_dark']
            highlight_opacity = 0.3
        elif state == 'hovered':
            shadow_offset = 8
            main_color = self.hover_color
            shadow_color = self.COLORS['shadow']
            highlight_opacity = 0.5
        else:
            shadow_offset = 6
            main_color = self.bg_color
            shadow_color = self.COLORS['shadow']
            highlight_opacity = 0.4
        
        self._create_rounded_rect(
            4, shadow_offset + 2, w - 4, h + shadow_offset - 2,
            r, fill=shadow_color, outline=''
        )
        
        self._create_rounded_rect(
            0, 0, w, h,
            r, fill=main_color, outline=''
        )
        
        if state != 'pressed':
            lighter_color = self._lighten_color(main_color, 0.3)
            self._create_rounded_rect(
                4, 4, w - 4, h // 2 + 4,
                r - 2, fill=lighter_color, outline='', stipple='gray50'
            )
        
        self._create_rounded_rect(
            6, 6, w - 6, h // 3,
            r - 3, fill='white', outline='', stipple='gray25'
        )
        
        icon_text = self._get_icon_text()
        if icon_text:
            self.create_text(
                35, h // 2 + 1,
                text=icon_text,
                fill='#CC5050',
                font=('Arial', 20),
                anchor='w'
            )
            self.create_text(
                34, h // 2,
                text=icon_text,
                fill='white',
                font=('Arial', 20),
                anchor='w'
            )
            text_x = 70
        else:
            text_x = w // 2
        
        self.create_text(
            text_x, h // 2 + 2,
            text=self.text,
            fill='#CC5050',
            font=('Microsoft YaHei UI', 17, 'bold'),
            anchor='center' if not icon_text else 'w'
        )
        
        self.create_text(
            text_x, h // 2,
            text=self.text,
            fill=self.text_color,
            font=('Microsoft YaHei UI', 17, 'bold'),
            anchor='center' if not icon_text else 'w'
        )
        
        self._draw_decorations(w, h, r)
    
    def _draw_decorations(self, w, h, r):
        """绘制装饰元素"""
        self.create_oval(
            12, 8, 22, 18,
            fill='white', outline='', stipple='gray25'
        )
        
        self.create_oval(
            w - 22, 8, w - 12, 18,
            fill='white', outline='', stipple='gray25'
        )
    
    def _lighten_color(self, color, factor):
        """使颜色变亮"""
        color = color.lstrip('#')
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """创建圆角矩形"""
        stipple = kwargs.pop('stipple', None)
        
        self.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r,
                       start=90, extent=90, style='pieslice', stipple=stipple, **kwargs)
        self.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r,
                       start=0, extent=90, style='pieslice', stipple=stipple, **kwargs)
        self.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2,
                       start=180, extent=90, style='pieslice', stipple=stipple, **kwargs)
        self.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2,
                       start=270, extent=90, style='pieslice', stipple=stipple, **kwargs)
        
        self.create_rectangle(x1 + r, y1, x2 - r, y2, stipple=stipple, **kwargs)
        self.create_rectangle(x1, y1 + r, x2, y2 - r, stipple=stipple, **kwargs)
    
    def _get_icon_text(self):
        """获取图标文本"""
        icons = {
            'clear': '🗑️',
            'trash': '🗑️',
            'coin': '💰',
            'money': '💰',
            'star': '⭐',
            'heart': '💖',
            'cloud': '☁️',
            'gift': '🎁',
            'cart': '🛒',
        }
        return icons.get(self.icon, '')
    
    def _on_enter(self, event):
        self.is_hovered = True
        self._draw_button('hovered')
        self.config(cursor='hand2')
    
    def _on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self._draw_button('normal')
        self.config(cursor='')
    
    def _on_press(self, event):
        self.is_pressed = True
        self._draw_button('pressed')
    
    def _on_release(self, event):
        was_pressed = self.is_pressed
        self.is_pressed = False
        self._draw_button('hovered' if self.is_hovered else 'normal')
        if was_pressed and self.command:
            self.command()
    
    def configure(self, **kwargs):
        """配置按钮"""
        if 'text' in kwargs:
            self.text = kwargs.pop('text')
        if 'command' in kwargs:
            self.command = kwargs.pop('command')
        if 'bg_color' in kwargs:
            self.bg_color = kwargs.pop('bg_color')
        if 'hover_color' in kwargs:
            self.hover_color = kwargs.pop('hover_color')
        if 'icon' in kwargs:
            self.icon = kwargs.pop('icon')
        self._draw_button('normal')
    
    def set_enabled(self, enabled):
        """设置启用状态"""
        if enabled:
            self.bind('<Enter>', self._on_enter)
            self.bind('<Leave>', self._on_leave)
            self.bind('<Button-1>', self._on_press)
            self.bind('<ButtonRelease-1>', self._on_release)
            self._draw_button('normal')
        else:
            self.unbind('<Enter>')
            self.unbind('<Leave>')
            self.unbind('<Button-1>')
            self.unbind('<ButtonRelease-1>')
            self._draw_button('disabled')
