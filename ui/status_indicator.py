"""
状态指示器组件 - 气泡风格
"""
import tkinter as tk


class StatusIndicator(tk.Frame):
    """状态指示器 - 气泡风格"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.canvas = tk.Canvas(self, width=12, height=12, 
                               highlightthickness=0, bg=self.cget('bg'))
        self.canvas.pack(side=tk.LEFT, padx=(0, 8))
        
        self.dot = self.canvas.create_oval(2, 2, 10, 10, fill='#5FD068', outline='')
        
        self.label = tk.Label(self, text="准备就绪", 
                             font=('Microsoft YaHei UI', 13),
                             bg=self.cget('bg'), fg='#636E72')
        self.label.pack(side=tk.LEFT)
        
        self._pulse_animation()
    
    def _pulse_animation(self):
        self.after(1500, self._pulse_animation)
    
    def set_status(self, text, color='#5FD068'):
        self.label.config(text=text, fg=color)
        self.canvas.itemconfig(self.dot, fill=color)
    
    def set_success(self, text="操作成功"):
        self.set_status(text, '#5FD068')
        self.after(2000, self.reset)
    
    def set_warning(self, text="处理中..."):
        self.set_status(text, '#FECA57')
    
    def reset(self):
        self.set_status("准备就绪", '#636E72')
