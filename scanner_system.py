"""
扫码随机播报系统 - 儿童友好版 Pro
设计风格: Playful Toy-like (玩具风格)
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import fnmatch
import re
import sys
import os
from datetime import datetime
from scanner import Scanner
from config_loader import (
    RANDOM_MESSAGES, CUSTOM_MESSAGES, SYSTEM_CONFIG, VOICE_CONFIG, PRODUCTS,
    get_voice_rate, get_scan_delay, get_queue_check_interval, get_product_names
)

from components.sounds import sound_manager
from components.particles import ParticleSystem
from components.mascot import MascotCharacter
from components.lucky import LuckyNumberSystem
from components.rainbow import RainbowProgressBar
from components.candy_cart import CandyCart
from components.candy_button import CandyButton
from components.candy_total import CandyTotal
from components.candy_decorations import CandyDecorations, RoundedCard, BubbleMessage

from ui import PlayfulButton, StatusIndicator
from voice import FastVoiceGenerator
from utils import SystemSleepPreventer, FastRandomGenerator


def get_project_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class ChildrenQRCodeSystem:
    """扫码播报系统 - 童趣糖果风格"""
    
    COLORS = {
        'primary': '#FF9EB5',
        'primary_light': '#FFB8C8',
        'primary_dark': '#FF7A9A',
        'secondary': '#B8E0FF',
        'secondary_light': '#D4EEFF',
        'secondary_dark': '#8ACDFF',
        'accent': '#FFE5A0',
        'accent_light': '#FFF3CC',
        'accent_dark': '#FFD670',
        'pink': '#FFB5C5',
        'pink_light': '#FFD6E0',
        'lavender': '#E6E6FA',
        'mint': '#B5F2D6',
        'coral': '#FFB5A7',
        'success': '#7DD99A',
        'success_light': '#B5F0C0',
        'success_dark': '#5BC47A',
        'warning': '#FFDB7D',
        'warning_light': '#FFEAB8',
        'warning_dark': '#EBC050',
        'error': '#FF9A9A',
        'error_light': '#FFBDBD',
        'error_dark': '#E57070',
        'background': '#FFF8F5',
        'surface': '#FFFFFF',
        'surface_soft': '#FFF5F0',
        'surface_variant': '#FFF0EB',
        'text_primary': '#5D4E4E',
        'text_secondary': '#8B7E7E',
        'text_tertiary': '#B5A8A8',
        'text_light': '#FFFFFF',
        'border': '#FFDDD8',
        'border_light': '#FFF0EC',
        'border_focus': '#FFB5C5',
        'shadow': '#FFCDD8',
        'shadow_soft': '#FFF0F5',
    }
    
    SPACING = {'xxs': 2, 'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32, 'xxl': 48}
    
    AMOUNT_REGEX = re.compile(r'\d+\.?\d*')
    
    CHINESE_NUM_MAP = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '两': 2
    }
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("扫码小助手")
        self.root.geometry("1100x780")
        self.root.configure(bg=self.COLORS['background'])
        self.root.minsize(900, 600)
        
        self._setup_fonts()
        
        self.scanner = Scanner()
        self.random_gen = FastRandomGenerator(RANDOM_MESSAGES)
        self.voice_generator = None
        self.lucky_system = LuckyNumberSystem()
        
        self.sleep_preventer = None
        if SYSTEM_CONFIG.get('prevent_sleep', True):
            self.sleep_preventer = SystemSleepPreventer()
        
        self.cart_items = []
        self.item_counter = 0
        
        self.compiled_patterns = []
        for pattern, message in CUSTOM_MESSAGES.items():
            if pattern.startswith('regex:'):
                try:
                    self.compiled_patterns.append((re.compile(pattern[6:]), message))
                except:
                    pass
        
        self._create_gui()
        
        self.voice_generator = FastVoiceGenerator(self.root)
        self.scanner.set_callback(self.on_scan)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_fonts(self):
        self.font_title = ('Microsoft YaHei UI', 28, 'bold')
        self.font_subtitle = ('Microsoft YaHei UI', 16, 'bold')
        self.font_body = ('Microsoft YaHei UI', 13)
        self.font_body_bold = ('Microsoft YaHei UI', 13, 'bold')
        self.font_large = ('Microsoft YaHei UI', 52, 'bold')
        self.font_button = ('Microsoft YaHei UI', 15, 'bold')
        self.font_small = ('Microsoft YaHei UI', 11)
    
    def _create_gui(self):
        main = tk.Frame(self.root, bg=self.COLORS['background'])
        main.pack(fill=tk.BOTH, expand=True, padx=self.SPACING['lg'], pady=self.SPACING['lg'])
        
        self._create_header(main)
        
        content = tk.Frame(main, bg=self.COLORS['background'])
        content.pack(fill=tk.BOTH, expand=True, pady=(self.SPACING['lg'], 0))
        
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)
        content.grid_rowconfigure(0, weight=1)
        
        self._create_cart_section(content)
        self._create_right_section(content)
    
    def _create_header(self, parent):
        header = tk.Frame(parent, bg=self.COLORS['surface'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_inner = tk.Frame(header, bg=self.COLORS['surface'])
        header_inner.pack(fill=tk.X, padx=self.SPACING['lg'], pady=self.SPACING['md'])
        
        left_section = tk.Frame(header_inner, bg=self.COLORS['surface'])
        left_section.pack(side=tk.LEFT)
        
        mascot_canvas = tk.Canvas(left_section, width=55, height=55,
                                  highlightthickness=0, bg=self.COLORS['surface'])
        mascot_canvas.pack(side=tk.LEFT, padx=(0, self.SPACING['md']))
        self.header_mascot = MascotCharacter(mascot_canvas, 28, 32, size=45)
        self.header_mascot.animate()
        
        title_frame = tk.Frame(left_section, bg=self.COLORS['surface'])
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(title_frame, text="扫码小助手", font=self.font_title,
                bg=self.COLORS['surface'], fg=self.COLORS['primary']
        ).pack(anchor='w')
        
        tk.Label(title_frame, text="让支付更简单", font=self.font_small,
                bg=self.COLORS['surface'], fg=self.COLORS['text_tertiary']
        ).pack(anchor='w')
        
        right_section = tk.Frame(header_inner, bg=self.COLORS['surface'])
        right_section.pack(side=tk.RIGHT)
        
        self.status_indicator = StatusIndicator(right_section, bg=self.COLORS['surface'])
        self.status_indicator.pack()
    
    def _create_cart_section(self, parent):
        cart_container = tk.Frame(parent, bg=self.COLORS['background'])
        cart_container.grid(row=0, column=0, sticky='nsew', padx=(0, self.SPACING['md']))
        
        cart_header = tk.Frame(cart_container, bg=self.COLORS['surface_soft'], height=50)
        cart_header.pack(fill=tk.X)
        cart_header.pack_propagate(False)
        
        header_inner = tk.Frame(cart_header, bg=self.COLORS['surface_soft'])
        header_inner.pack(fill=tk.X, padx=self.SPACING['lg'], pady=self.SPACING['sm'])
        
        tk.Label(header_inner, text="购物清单", font=self.font_subtitle,
                bg=self.COLORS['surface_soft'], fg=self.COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        self.item_count_label = tk.Label(header_inner, text="0 件",
                                         font=self.font_body,
                                         bg=self.COLORS['surface_soft'],
                                         fg=self.COLORS['text_tertiary'])
        self.item_count_label.pack(side=tk.LEFT, padx=(self.SPACING['sm'], 0))
        
        cart_frame = tk.Frame(cart_container, bg=self.COLORS['surface'])
        cart_frame.pack(fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.Treeview',
                       background=self.COLORS['surface'],
                       foreground=self.COLORS['text_primary'],
                       fieldbackground=self.COLORS['surface'],
                       rowheight=48,
                       font=self.font_body,
                       borderwidth=0)
        style.configure('Custom.Treeview.Heading',
                       background=self.COLORS['primary'],
                       foreground='white',
                       font=self.font_body_bold,
                       borderwidth=0)
        style.map('Custom.Treeview',
                 background=[('selected', self.COLORS['primary_light'])],
                 foreground=[('selected', 'white')])
        
        columns = ('num', 'time', 'name', 'amount')
        self.tree = ttk.Treeview(cart_frame, columns=columns, show='headings',
                                style='Custom.Treeview', height=12)
        
        self.tree.heading('num', text='序号')
        self.tree.heading('time', text='时间')
        self.tree.heading('name', text='商品名称')
        self.tree.heading('amount', text='金额')
        
        self.tree.column('num', width=70, anchor='center', minwidth=50)
        self.tree.column('time', width=90, anchor='center', minwidth=70)
        self.tree.column('name', width=200, anchor='w', minwidth=100)
        self.tree.column('amount', width=100, anchor='center', minwidth=80)
        
        scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.tag_configure('odd', background=self.COLORS['surface_soft'])
        self.tree.tag_configure('even', background=self.COLORS['surface'])
    
    def _create_right_section(self, parent):
        right_container = tk.Frame(parent, bg=self.COLORS['background'], width=320)
        right_container.grid(row=0, column=1, sticky='nsew')
        right_container.grid_propagate(False)
        
        total_frame = tk.Frame(right_container, bg=self.COLORS['surface'])
        total_frame.pack(fill=tk.X, pady=(0, self.SPACING['md']))
        
        total_header = tk.Frame(total_frame, bg=self.COLORS['primary'], height=45)
        total_header.pack(fill=tk.X)
        total_header.pack_propagate(False)
        
        tk.Label(total_header, text="合计金额", font=self.font_body_bold,
                bg=self.COLORS['primary'], fg='white'
        ).pack(pady=self.SPACING['sm'])
        
        total_content = tk.Frame(total_frame, bg=self.COLORS['surface'])
        total_content.pack(fill=tk.X, pady=self.SPACING['lg'])
        
        self.rainbow_progress = RainbowProgressBar(
            total_content, width=280, height=40, max_value=50
        )
        self.rainbow_progress.pack()
        
        mascot_frame = tk.Frame(right_container, bg=self.COLORS['surface'])
        mascot_frame.pack(fill=tk.X, pady=self.SPACING['md'])
        
        self.mascot_canvas = tk.Canvas(mascot_frame, width=300, height=100,
                                       highlightthickness=0, bg=self.COLORS['surface'])
        self.mascot_canvas.pack(pady=self.SPACING['sm'])
        
        self.mascot = MascotCharacter(self.mascot_canvas, 150, 55, size=70)
        self.mascot.animate()
        
        self.particle_system = ParticleSystem(self.mascot_canvas)
        
        btn_frame = tk.Frame(right_container, bg=self.COLORS['background'])
        btn_frame.pack(fill=tk.X, pady=self.SPACING['md'])
        
        self.clear_btn = CandyButton(
            btn_frame,
            text="清空购物车",
            command=self._clear_cart,
            width=280,
            height=56,
            bg_color=self.COLORS['error'],
            hover_color=self.COLORS['error_light'],
            press_color=self.COLORS['error_dark'],
            corner_radius=28,
            icon='trash'
        )
        self.clear_btn.pack()
        
        log_frame = tk.Frame(right_container, bg=self.COLORS['surface'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_header = tk.Frame(log_frame, bg=self.COLORS['surface_soft'], height=40)
        log_header.pack(fill=tk.X)
        log_header.pack_propagate(False)
        
        tk.Label(log_header, text="操作记录", font=self.font_body_bold,
                bg=self.COLORS['surface_soft'], fg=self.COLORS['text_secondary']
        ).pack(pady=self.SPACING['sm'], anchor='w', padx=self.SPACING['md'])
        
        self.log_text = tk.Text(
            log_frame,
            height=6,
            font=('Consolas', 10),
            bg=self.COLORS['surface'],
            fg=self.COLORS['text_primary'],
            relief='flat',
            state=tk.DISABLED,
            padx=self.SPACING['md'],
            pady=self.SPACING['sm'],
            wrap=tk.WORD,
            cursor='arrow'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=self.SPACING['sm'], pady=self.SPACING['sm'])
    
    def _add_log(self, message, log_type='info'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.config(state=tk.NORMAL)
        
        prefix = {'info': '+', 'success': '*', 'clear': '-', 'lucky': '★'}.get(log_type, '+')
        
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _animate_success(self):
        self.status_indicator.set_success("扫码成功")
        self.mascot.set_state('happy')
        sound_manager.play('scan')
    
    def _animate_lucky(self, effect_name):
        self.status_indicator.set_status("幸运数字!", self.COLORS['warning'])
        self.mascot.set_state('surprised')
        self.particle_system.emit_effect(effect_name, 150, 60)
        sound_manager.play('lucky')
    
    def _animate_payment(self):
        self.status_indicator.set_status("收款成功!", self.COLORS['success'])
        self.mascot.set_state('celebrate')
        self.particle_system.emit_effect('payment_success', 150, 60)
        sound_manager.play('payment')
        self.root.after(2500, self._reset_status)
    
    def _reset_status(self):
        self.status_indicator.reset()
    
    def _is_payment_code(self, code):
        if not isinstance(code, str):
            return False
        code = code.strip()
        if not code:
            return False
        patterns = SYSTEM_CONFIG.get('payment_code_patterns', [r'^\d{36}$'])
        for pattern in patterns:
            try:
                if re.match(pattern, code):
                    return True
            except:
                pass
        return False
    
    def _get_message(self, code):
        if self._is_payment_code(code):
            total = sum(item['amount'] for item in self.cart_items) if self.cart_items else 0
            prefix = SYSTEM_CONFIG.get('payment_prefix', '臭宝')
            if total == 0:
                return (f"{prefix}，新年快乐", True, None)
            return (f"{prefix}收款{int(total)}元", True, None)
        
        if code in PRODUCTS:
            product = PRODUCTS[code]
            product_name = product.get('name', '')
            price_msg = self.random_gen.get_next()
            lucky_effect = self.lucky_system.get_lucky_effect(price_msg)
            return (f"{product_name} {price_msg}", False, lucky_effect)
        
        if not RANDOM_MESSAGES:
            return ("欢迎使用", False, None)
        
        if code in CUSTOM_MESSAGES:
            return (CUSTOM_MESSAGES[code], False, None)
        
        for pattern, message in CUSTOM_MESSAGES.items():
            if '*' in pattern and not pattern.startswith('regex:'):
                if fnmatch.fnmatch(code, pattern):
                    return (message, False, None)
        
        for compiled, message in self.compiled_patterns:
            if compiled.match(code):
                return (message, False, None)
        
        if SYSTEM_CONFIG.get('random_mode', True):
            price_msg = self.random_gen.get_next()
            lucky_effect = self.lucky_system.get_lucky_effect(price_msg)
            return (price_msg, False, lucky_effect)
        
        return (RANDOM_MESSAGES[0], False, None)
    
    def _parse_amount(self, message):
        match = self.AMOUNT_REGEX.search(message)
        if match:
            try:
                return float(match.group())
            except:
                pass
        
        amount_str = message.replace('元', '').replace('块', '').strip()
        total = 0
        temp = 0
        
        for char in amount_str:
            if char in self.CHINESE_NUM_MAP:
                digit = self.CHINESE_NUM_MAP[char]
                if digit == 10:
                    total = temp * 10 if temp else 10
                    temp = 0
                else:
                    temp = digit
        
        return total + temp
    
    def _update_display(self):
        total = sum(item['amount'] for item in self.cart_items)
        self.rainbow_progress.set_value(total)
        self.item_count_label.config(text=f"{len(self.cart_items)} 件")
    
    def _add_to_cart(self, code, display_name, message, amount):
        self.item_counter += 1
        
        item = {
            'id': self.item_counter,
            'time': datetime.now().strftime('%H:%M:%S'),
            'code': code[:15] + '...' if len(code) > 15 else code,
            'amount': amount,
            'message': message,
            'display_name': display_name
        }
        
        self.cart_items.append(item)
        
        tag = 'odd' if len(self.cart_items) % 2 == 0 else 'even'
        self.tree.insert('', tk.END, values=(
            item['id'], item['time'], display_name, f"{amount:.0f} 元"
        ), tags=(tag,))
        
        children = self.tree.get_children()
        if children:
            self.tree.see(children[-1])
        
        self._update_display()
    
    def _clear_cart(self):
        if not self.cart_items:
            return
        
        self.cart_items.clear()
        self.item_counter = 0
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self._update_display()
        self._add_log("购物车已清空", 'clear')
        sound_manager.play('clear')
    
    def on_scan(self, code):
        if not code or not isinstance(code, str):
            return
        
        code = code.strip()
        if not code:
            return
        
        message, is_payment, lucky_effect = self._get_message(code)
        scan_delay = get_scan_delay()
        
        if is_payment:
            self._add_log(message, 'success')
            if scan_delay > 0:
                self.root.after(int(scan_delay * 1000),
                    lambda: self.voice_generator.speak_with_callback(message, self._clear_cart))
            else:
                self.voice_generator.speak_with_callback(message, self._clear_cart)
            self._animate_payment()
        else:
            amount = self._parse_amount(message)
            if code in PRODUCTS:
                display_name = PRODUCTS[code]['name']
            else:
                display_name = "未知商品"
            self._add_to_cart(code, display_name, message, amount)
            
            if lucky_effect:
                lucky_msg = self.lucky_system.get_lucky_message(message)
                if lucky_msg:
                    self._add_log(f"幸运数字! {lucky_msg}", 'lucky')
                self._animate_lucky(lucky_effect)
            else:
                self._animate_success()
            
            self._add_log(message, 'info')
            
            if scan_delay > 0:
                self.root.after(int(scan_delay * 1000),
                    lambda: self.voice_generator.speak(message))
            else:
                self.voice_generator.speak(message)
    
    def _get_all_messages(self):
        messages = list(RANDOM_MESSAGES)
        for msg in CUSTOM_MESSAGES.values():
            if msg not in messages:
                messages.append(msg)
        prefix = SYSTEM_CONFIG.get('payment_prefix', '臭宝')
        messages.append(f"{prefix}，新年快乐")
        for i in range(1, 100):
            messages.append(f"{prefix}收款{i}元")
        product_names = get_product_names()
        for name in product_names:
            for price in RANDOM_MESSAGES:
                messages.append(f"{name} {price}")
        for lucky_info in self.lucky_system.LUCKY_CONFIG.values():
            messages.append(lucky_info['message'])
        return messages
    
    def start(self):
        if self.sleep_preventer:
            self.sleep_preventer.enable()
        
        self._add_log("系统启动中...", 'info')
        
        all_messages = self._get_all_messages()
        
        def progress_callback(current, total, msg):
            self.root.after(0, lambda: self._add_log(f"加载语音 [{current}/{total}]", 'info'))
        
        self.voice_generator.preload_common_messages(all_messages, progress_callback)
        
        scan_thread = threading.Thread(target=self._run_scanner, daemon=True)
        scan_thread.start()
        self._add_log("扫码器已就绪", 'info')
        
        self.root.after(1000, self._check_cache_status)
        
        self.root.mainloop()
    
    def _check_cache_status(self):
        if self.voice_generator.cache_loaded:
            self._add_log("系统就绪", 'success')
            self.status_indicator.reset()
        else:
            self.root.after(500, self._check_cache_status)
    
    def _run_scanner(self):
        try:
            self.scanner.start()
        except Exception as e:
            self._add_log(f"扫码器错误: {e}", 'info')
    
    def _on_closing(self):
        if self.sleep_preventer:
            self.sleep_preventer.enabled = False
        try:
            self.scanner.stop()
        except:
            pass
        try:
            self.voice_generator.stop()
        except:
            pass
        try:
            self.mascot.stop()
            self.header_mascot.stop()
        except:
            pass
        self.root.destroy()


def main():
    random.seed()
    try:
        system = ChildrenQRCodeSystem()
        system.start()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
