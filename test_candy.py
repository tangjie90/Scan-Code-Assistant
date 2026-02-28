"""
测试童趣组件
"""
import tkinter as tk
from components.candy_button import CandyButton
from components.candy_total import CandyTotal
from components.candy_decorations import CandyDecorations

root = tk.Tk()
root.title("童趣组件测试")
root.geometry("800x600")
root.configure(bg='#FFF8F5')

# 测试 CandyButton
btn = CandyButton(
    root,
    text="清空购物车",
    width=260,
    height=56,
    bg_color='#FF9A9A',
    hover_color='#FFB5B5',
    press_color='#E57070',
    corner_radius=28,
    icon='trash'
)
btn.pack(pady=20)

# 测试 CandyTotal
total = CandyTotal(root, width=280, height=200)
total.pack(pady=20)
total.set_value(25.5)

# 测试装饰
deco = CandyDecorations(root, width=800, height=100)
deco.pack(pady=20)

root.mainloop()
