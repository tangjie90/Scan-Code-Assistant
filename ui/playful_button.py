"""
Material Design 3 风格按钮组件
"""
import tkinter as tk
from components.sounds import sound_manager


class PlayfulButton(tk.Canvas):
    """Material Design 3 风格按钮"""
    
    def __init__(self, parent, text, command=None, width=220, height=48, 
                 bg_color='#4285F4', hover_color='#3367D6', press_color='#2A5BB8',
                 text_color='white', corner_radius=24):
        super().__init__(parent, width=width, height=height + 4, 
                        highlightthickness=0, bg=parent.cget('bg'))
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.press_color = press_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.width = width
        self.height = height
        self.text = text
        self.is_hovered = False
        self.is_pressed = False
        
        self._draw_button()
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
    
    def _draw_button(self, state='normal'):
        self.delete('all')
        r = self.corner_radius
        w = self.width
        h = self.height
        
        if state == 'pressed':
            shadow_offset = 1
            main_color = self.press_color
            shadow_color = '#000000'
        elif state == 'hovered':
            shadow_offset = 3
            main_color = self.hover_color
            shadow_color = '#333333'
        else:
            shadow_offset = 2
            main_color = self.bg_color
            shadow_color = '#000000'
        
        # Shadow layer
        self.create_rectangle(r + 2, shadow_offset + 2, w - r + 2, h + shadow_offset + 2, 
                            fill=shadow_color, outline='')
        self.create_oval(2, shadow_offset + 2, 2 * r + 2, shadow_offset + 2 + 2 * r, 
                        fill=shadow_color, outline='')
        self.create_oval(w - 2 * r + 2, shadow_offset + 2, w + 2, shadow_offset + 2 + 2 * r, 
                        fill=shadow_color, outline='')
        
        # Main button
        self.create_rectangle(r, 0, w - r, h, fill=main_color, outline='')
        self.create_oval(0, 0, 2 * r, 2 * r, fill=main_color, outline='')
        self.create_oval(w - 2 * r, 0, w, 2 * r, fill=main_color, outline='')
        
        # Icon placeholder (left side)
        icon_x = 16
        icon_y = h // 2
        self.create_oval(icon_x - 6, icon_y - 6, icon_x + 6, icon_y + 6, 
                        fill='white', outline='', stipple='gray50')
        
        # Text
        self.create_text(w // 2 + 8, h // 2, text=self.text, fill=self.text_color,
                        font=('Microsoft YaHei UI', 14, 'bold'))
    
    def _on_enter(self, event):
        self.is_hovered = True
        if not self.is_pressed:
            self._draw_button('hovered')
    
    def _on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self._draw_button('normal')
    
    def _on_press(self, event):
        self.is_pressed = True
        self._draw_button('pressed')
        sound_manager.play('click')
    
    def _on_release(self, event):
        was_pressed = self.is_pressed
        self.is_pressed = False
        self._draw_button('hovered' if self.is_hovered else 'normal')
        if was_pressed and self.command:
            self.command()
