"""
扫码小助手 - PySide6版本
童趣糖果风格UI - 完整功能版 - 热更新版
"""
import sys
import os
import re
import random
import threading
import json
import hashlib
import time
import warnings
from datetime import datetime
from collections import OrderedDict

if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

warnings.filterwarnings("ignore", category=RuntimeWarning)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QThread, QTimer, Signal, QObject, Slot

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scanner_app.ui import MainWindow, CandyTheme
from scanner_app.core.scanner import Scanner
from scanner_app.core.voice_queue import VoiceGeneratorWithQueue, VoicePriority, VoiceStatus
from scanner_app.core.product_manager import ProductManager, Product
from scanner_app.core.file_watcher import ProductFileWatcher

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def record(self, name, elapsed_ms):
        if name not in self.metrics:
            self.metrics[name] = {'count': 0, 'total': 0, 'max': 0, 'min': float('inf')}
        self.metrics[name]['count'] += 1
        self.metrics[name]['total'] += elapsed_ms
        self.metrics[name]['max'] = max(self.metrics[name]['max'], elapsed_ms)
        self.metrics[name]['min'] = min(self.metrics[name]['min'], elapsed_ms)
    
    def get_avg(self, name):
        if name in self.metrics and self.metrics[name]['count'] > 0:
            return self.metrics[name]['total'] / self.metrics[name]['count']
        return 0


perf_monitor = PerformanceMonitor()


class VoiceGenerator(QObject):
    """语音生成器 - 队列版"""
    
    play_finished = Signal()
    _callback_signal = Signal(object)
    
    def __init__(self):
        super().__init__()
        
        cache_dir = os.path.join(PROJECT_ROOT, "voice_cache")
        self._voice_queue = VoiceGeneratorWithQueue(cache_dir)
        
        self._process_thread = None
        self._pending_callbacks = {}
        
        self._callback_signal.connect(self._execute_callback)
        
        self._start_processing()
        self._log_cache_status()
    
    def _log_cache_status(self):
        try:
            cache_dir = self._voice_queue.queue_manager.cache_dir
            mp3_count = len([f for f in os.listdir(cache_dir) if f.endswith('.mp3')])
            total_size = sum(
                os.path.getsize(os.path.join(cache_dir, f)) 
                for f in os.listdir(cache_dir) 
                if f.endswith('.mp3')
            )
            print(f"[VoiceGenerator] 缓存状态:")
            print(f"  - MP3文件: {mp3_count}个")
            print(f"  - 总大小: {total_size / (1024*1024):.2f}MB")
        except Exception as e:
            print(f"[VoiceGenerator] 缓存统计失败: {e}")
    
    def _start_processing(self):
        if self._process_thread is None or not self._process_thread.is_alive():
            self._process_thread = threading.Thread(
                target=self._process_queue_with_callbacks,
                daemon=True
            )
            self._process_thread.start()
            print("[VoiceGenerator] 队列处理线程已启动")
    
    def _process_queue_with_callbacks(self):
        while not self._voice_queue.queue_manager._should_stop:
            task = self._voice_queue.queue_manager.dequeue()
            
            if task is None:
                time.sleep(0.1)
                continue
            
            message = task['message']
            callback_id = task.get('callback_id')
            
            self._voice_queue.queue_manager._current_task = task
            self._voice_queue.queue_manager._status = VoiceStatus.PLAYING
            
            cache_path = self._voice_queue.queue_manager._get_cache_path(message)
            
            memory_path = self._voice_queue.queue_manager._get_from_memory_cache(message)
            if memory_path:
                print(f"[VoiceQueue] 使用内存缓存: {message[:30]}...")
            elif os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
                print(f"[VoiceQueue] 使用文件缓存: {message[:30]}...")
                self._voice_queue.queue_manager._add_to_memory_cache(message, cache_path)
            else:
                print(f"[VoiceQueue] 生成音频: {message[:30]}...")
                self._voice_queue.queue_manager._status = VoiceStatus.GENERATING
                
                if not self._voice_queue._generate_audio(message, cache_path):
                    self._voice_queue.queue_manager._stats['total_errors'] += 1
                    self._voice_queue.queue_manager._status = VoiceStatus.ERROR
                    continue
                
                self._voice_queue.queue_manager._add_to_memory_cache(message, cache_path)
            
            if self._voice_queue._play_audio(cache_path):
                self._voice_queue._wait_playback()
                self._voice_queue.queue_manager._stats['total_played'] += 1
                
                if callback_id and callback_id in self._pending_callbacks:
                    callback = self._pending_callbacks.pop(callback_id)
                    self._callback_signal.emit(callback)
            else:
                self._voice_queue.queue_manager._stats['total_errors'] += 1
            
            self._voice_queue.queue_manager._current_task = None
            self._voice_queue.queue_manager._status = VoiceStatus.IDLE
            
            time.sleep(0.1)
    
    def _execute_callback(self, callback):
        if callback:
            try:
                callback()
            except Exception as e:
                print(f"[VoiceGenerator] 回调执行失败: {e}")
    
    @property
    def is_playing(self):
        status = self._voice_queue.get_queue_status()
        return status['status'] in ('playing', 'generating')
    
    def speak(self, message: str, callback=None):
        start_time = time.perf_counter()
        
        callback_id = None
        if callback:
            callback_id = hashlib.md5(f"{message}_{time.time()}".encode()).hexdigest()[:8]
            self._pending_callbacks[callback_id] = callback
        
        task = {
            'id': callback_id or hashlib.md5(f"{message}_{time.time()}".encode()).hexdigest()[:8],
            'message': message,
            'priority': VoicePriority.NORMAL,
            'created_at': time.time(),
            'callback_id': callback_id
        }
        
        with self._voice_queue.queue_manager._lock:
            self._voice_queue.queue_manager._queue.append(task)
            self._voice_queue.queue_manager._stats['total_queued'] += 1
        
        elapsed = (time.perf_counter() - start_time) * 1000
        perf_monitor.record('enqueue', elapsed)
        
        queue_size = self._voice_queue.queue_manager.get_queue_size()
        print(f"[语音] 加入队列: {message[:30]}... (队列: {queue_size})")
        
        return task['id']
    
    def speak_priority(self, message: str, priority: VoicePriority = VoicePriority.NORMAL, callback=None):
        callback_id = None
        if callback:
            callback_id = hashlib.md5(f"{message}_{time.time()}".encode()).hexdigest()[:8]
            self._pending_callbacks[callback_id] = callback
        
        task = {
            'id': callback_id or hashlib.md5(f"{message}_{time.time()}".encode()).hexdigest()[:8],
            'message': message,
            'priority': priority,
            'created_at': time.time(),
            'callback_id': callback_id
        }
        
        with self._voice_queue.queue_manager._lock:
            self._voice_queue.queue_manager._queue.append(task)
            self._voice_queue.queue_manager._stats['total_queued'] += 1
        
        return task['id']
    
    def get_queue_status(self) -> dict:
        return self._voice_queue.get_queue_status()
    
    def clear_queue(self):
        self._voice_queue.clear_queue()
        self._pending_callbacks.clear()
        print("[语音] 队列已清空")
    
    def stop_current(self):
        self._voice_queue.stop_current()
    
    def get_cache_info(self) -> dict:
        try:
            cache_dir = self._voice_queue.queue_manager.cache_dir
            mp3_count = len([f for f in os.listdir(cache_dir) if f.endswith('.mp3')])
            total_size = sum(
                os.path.getsize(os.path.join(cache_dir, f)) 
                for f in os.listdir(cache_dir) 
                if f.endswith('.mp3')
            )
            return {
                'count': mp3_count,
                'total_size_mb': total_size / (1024 * 1024),
                'cache_dir': cache_dir
            }
        except:
            return {'count': 0, 'total_size_mb': 0, 'cache_dir': ''}


class ScannerApp(QObject):
    """扫码应用 - 支持商品热更新"""
    
    _products_updated_signal = Signal(int, int)  # version, count
    _products_update_failed_signal = Signal(str)  # error message
    
    def __init__(self):
        super().__init__()
        
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        
        self.window = MainWindow()
        self.window.show()
        
        self.scanner = Scanner()
        self.scanner.scan_received.connect(self.on_scan)
        
        self.window.right_panel.broadcast_triggered.connect(self.on_broadcast)
        
        self.voice = VoiceGenerator()
        
        self.cart_items = []
        self.item_counter = 0
        
        self._products_updated_signal.connect(self._on_products_updated_ui)
        self._products_update_failed_signal.connect(self._on_products_update_failed_ui)
        
        self._load_config()
        self._setup_regex_patterns()
        self._load_products()
        self._preload_voices()
    
    def on_products_updated(self, products, version: int):
        """商品数据更新回调"""
        self._products_updated_signal.emit(version, len(products))
    
    def on_products_update_failed(self, error: str):
        """商品数据更新失败回调"""
        self._products_update_failed_signal.emit(error)
    
    @Slot(int, int)
    def _on_products_updated_ui(self, version: int, count: int):
        """UI线程处理商品更新"""
        self.window.add_log(f"商品数据已更新: {count}个商品 (v{version})", 'success')
    
    @Slot(str)
    def _on_products_update_failed_ui(self, error: str):
        """UI线程处理商品更新失败"""
        self.window.add_log(f"商品数据更新失败: {error}", 'error')
    
    def _load_config(self):
        config_path = os.path.join(PROJECT_ROOT, 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.config = {}
    
    def _setup_regex_patterns(self):
        self.amount_regex = re.compile(r'\d+\.?\d*')
        
        config_patterns = self.config.get('SYSTEM_CONFIG', {}).get('payment_code_patterns', [])
        self.payment_patterns = []
        for pattern in config_patterns:
            try:
                self.payment_patterns.append(re.compile(pattern))
            except:
                pass
        
        if not self.payment_patterns:
            self.payment_patterns = [
                re.compile(r'^\d{16,24}$'),
                re.compile(r'^\d{28,36}$'),
                re.compile(r'^https?://.*(?:wxpay|alipay|pay).*', re.IGNORECASE),
                re.compile(r'^https?://u\.wechat\.com/.*', re.IGNORECASE),
                re.compile(r'^https?://.*qr.*', re.IGNORECASE),
            ]
        
        self.custom_messages = self.config.get('CUSTOM_MESSAGES', {})
    
    def _load_products(self):
        csv_path = os.path.join(PROJECT_ROOT, 'products.csv')
        self.product_manager = ProductManager(csv_path)
        
        self._file_watcher = ProductFileWatcher(
            csv_path,
            self._on_products_file_changed
        )
        self._file_watcher.start()
        print(f"[ScannerApp] 商品文件监控已启动")
    
    def _on_products_file_changed(self):
        """商品文件变更回调"""
        if self.product_manager.reload():
            self.on_products_updated(
                self.product_manager.products,
                self.product_manager.version
            )
        else:
            self.on_products_update_failed("重新加载商品数据失败")
    
    def _preload_voices(self):
        messages = []
        
        random_msgs = self.config.get('RANDOM_MESSAGES', ["1元", "2元", "3元", "5元", "10元"])
        messages.extend(random_msgs)
        
        for i in range(1, 101):
            messages.append(f"{i}元")
        
        broadcast_msgs = self.config.get('BROADCAST_MESSAGES', {})
        for msg_data in broadcast_msgs.values():
            text = msg_data.get('text', '')
            if text:
                messages.append(text)
        
        prefix = self.config.get('SYSTEM_CONFIG', {}).get('payment_prefix', '臭宝')
        for i in range(0, 501, 1):
            messages.append(f"{prefix}收款{i}元")
        
        messages.append(f"{prefix}，新年快乐")
        
        products = self.product_manager.products
        for product in products.values():
            if product.price > 0:
                messages.append(f"{int(product.price)}元")
        
        unique_messages = list(set(messages))
        self._generate_cache_async(unique_messages)
    
    def _generate_cache_async(self, messages: list):
        def generate():
            cache_dir = self.voice._voice_queue.queue_manager.cache_dir
            voice_name = self.voice._voice_queue.queue_manager.voice_name
            
            count = 0
            for msg in messages:
                if msg:
                    key = hashlib.md5(f"{msg}_{voice_name}_0".encode()).hexdigest()
                    cache_path = os.path.join(cache_dir, f"{key}.mp3")
                    if not os.path.exists(cache_path) or os.path.getsize(cache_path) == 0:
                        count += 1
            
            print(f"[预加载] 需要生成 {count} 个新音频")
            self._cache_check_complete = True
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def _is_payment_code(self, code):
        if code in self.custom_messages:
            return True
        
        for pattern in self.payment_patterns:
            if pattern.match(code):
                return True
        
        if len(code) >= 16 and code.isdigit():
            return True
        
        if code.startswith('http') and ('pay' in code.lower() or 'wx' in code.lower() or 'qr' in code.lower()):
            return True
        
        return False
    
    def _parse_amount(self, message):
        chinese_nums = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, 
                       '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                       '百': 100, '千': 1000, '万': 10000}
        
        for cn, num in chinese_nums.items():
            if cn in message:
                return float(num)
        
        match = self.amount_regex.search(message)
        if match:
            try:
                return float(match.group())
            except:
                pass
        return 0.0
    
    def _get_product_info(self, code):
        product = self.product_manager.get_product(code)
        if product:
            return product.name, product.price
        return None, 0.0
    
    def _get_message(self, code):
        if self._is_payment_code(code):
            if code in self.custom_messages:
                custom_msg = self.custom_messages[code]
                total = sum(item[3] for item in self.cart_items) if self.cart_items else 0
                return custom_msg, True, total
            
            total = sum(item[3] for item in self.cart_items) if self.cart_items else 0
            prefix = self.config.get('SYSTEM_CONFIG', {}).get('payment_prefix', '臭宝')
            if total == 0:
                return f"{prefix}，新年快乐", True, 0
            return f"{prefix}收款{int(total)}元", True, total
        
        product_name, product_price = self._get_product_info(code)
        
        if product_name and product_price > 0:
            return f"{product_name} {int(product_price)}元", False, product_price
        elif product_name:
            price_messages = self.config.get('RANDOM_MESSAGES', ["1元", "2元", "3元", "5元", "10元"])
            price_msg = random.choice(price_messages)
            price = self._parse_amount(price_msg)
            return f"{product_name} {price_msg}", False, price
        
        price_messages = self.config.get('RANDOM_MESSAGES', ["1元", "2元", "3元", "5元", "10元"])
        price_msg = random.choice(price_messages)
        price = self._parse_amount(price_msg)
        return price_msg, False, price
    
    def _add_to_cart(self, code, name, amount):
        self.item_counter += 1
        
        item = [
            str(self.item_counter),
            datetime.now().strftime('%H:%M:%S'),
            name,
            amount
        ]
        
        self.cart_items.append(item)
        self.window.add_cart_item(item)
        
        total = sum(item[3] for item in self.cart_items)
        self.window.set_total(total)
        
        print(f"[购物车] 添加: {name}, 金额: {amount}, 合计: {total}")
    
    def _clear_cart(self):
        self.cart_items = []
        self.item_counter = 0
        
        self.window.clear_cart()
        
        if hasattr(self.window.right_panel, 'progress'):
            self.window.right_panel.progress.clear()
        
        print("[购物车] 已彻底清空，所有数据归零")
    
    def on_scan(self, code):
        start_time = time.perf_counter()
        
        if not code or not isinstance(code, str):
            return
        
        code = code.strip()
        if not code:
            return
        
        message, is_payment, price = self._get_message(code)
        
        elapsed = (time.perf_counter() - start_time) * 1000
        perf_monitor.record('scan_process', elapsed)
        
        if is_payment:
            self.window.add_log(message, 'success')
            self.window.set_success("收款成功!")
            self.window.set_mascot_state('celebrate')
            
            def on_voice_done():
                self._clear_cart()
                self.window.reset_status()
                self.window.set_mascot_state('idle')
            
            self.voice.speak(message, on_voice_done)
        else:
            product_name, product_price = self._get_product_info(code)
            display_name = product_name if product_name else "未知商品"
            
            self._add_to_cart(code, display_name, price)
            
            self.window.add_log(f"{display_name} {int(price)}元", 'info')
            self.window.set_success("扫码成功")
            self.window.set_mascot_state('happy')
            
            def on_voice_done():
                self.window.set_mascot_state('idle')
                self.window.reset_status()
            
            self.voice.speak(message, on_voice_done)
    
    def on_broadcast(self, key, text):
        print(f"[广播] 触发: key={key}")
        
        self.window.add_log(f"广播: {text}", 'lucky')
        self.window.set_mascot_state('happy')
        
        def on_voice_done():
            self.window.on_broadcast_finished(key)
            self.window.reset_status()
            self.window.set_mascot_state('idle')
        
        self.voice.speak_priority(text, VoicePriority.HIGH, on_voice_done)
    
    def start(self):
        self.window.add_log("系统启动中...", 'info')
        
        cache_info = self.voice.get_cache_info()
        product_count = self.product_manager.count
        self.window.add_log(f"缓存: {cache_info['count']}个音频, 商品: {product_count}个", 'info')
        self.window.add_log("商品热更新已启用", 'info')
        
        def run_scanner():
            try:
                self.scanner.start()
            except Exception as e:
                self.window.add_log(f"扫码器错误: {e}", 'error')
        
        scan_thread = threading.Thread(target=run_scanner, daemon=True)
        scan_thread.start()
        
        self.window.add_log("扫码器已就绪", 'info')
        
        if not EDGE_TTS_AVAILABLE:
            self.window.add_log("请安装 edge-tts: pip install edge-tts", 'warning')
        if not PYGAME_AVAILABLE:
            self.window.add_log("请安装 pygame: pip install pygame", 'warning')
        
        sys.exit(self.app.exec())


def main():
    random.seed()
    try:
        app = ScannerApp()
        app.start()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
