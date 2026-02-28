"""
扫码器模块 - 处理扫码枪输入
修复：
1. 添加防抖机制防止重复扫描
2. 只处理按键按下事件，避免字符重复
"""
import time
import keyboard
import serial
import threading
from config_loader import SCANNER_CONFIG, SYSTEM_CONFIG


class Scanner:
    def __init__(self):
        self.mode = SCANNER_CONFIG['mode']
        self.serial_port = None
        self.scan_buffer = ""
        self.callback = None
        
        self.last_scan_time = 0
        self.last_scan_code = ""
        self.debounce_interval = 0.5
        self.scan_lock = threading.Lock()
        self.is_scanning = False
        
        if self.mode == 'serial':
            self._init_serial()
    
    def _init_serial(self):
        if SCANNER_CONFIG['port']:
            try:
                self.serial_port = serial.Serial(
                    port=SCANNER_CONFIG['port'],
                    baudrate=SCANNER_CONFIG['baudrate'],
                    timeout=SCANNER_CONFIG['timeout']
                )
                print(f"串口 {SCANNER_CONFIG['port']} 连接成功")
            except serial.SerialException as e:
                print(f"串口连接失败: {e}")
                self.mode = 'keyboard'
                print("已切换到键盘模式")
    
    def set_callback(self, callback):
        self.callback = callback
    
    def _is_duplicate_scan(self, code):
        """检查是否为重复扫描"""
        current_time = time.time()
        
        with self.scan_lock:
            if (code == self.last_scan_code and 
                current_time - self.last_scan_time < self.debounce_interval):
                print(f"[防抖] 忽略重复扫描: {code[:20]}...")
                return True
            
            self.last_scan_time = current_time
            self.last_scan_code = code
            return False
    
    def _trigger_callback(self, code):
        """触发回调（带防抖和锁）"""
        if not code or not self.callback:
            return
        
        if self._is_duplicate_scan(code):
            return
        
        with self.scan_lock:
            if self.is_scanning:
                print(f"[防抖] 正在处理中，忽略: {code[:20]}...")
                return
            self.is_scanning = True
        
        try:
            print(f"[扫描] 条码: {code}")
            self.callback(code)
        finally:
            self.is_scanning = False
    
    def _on_key_press(self, event):
        """键盘事件处理 - 只处理按下事件"""
        if event.event_type != 'down':
            return True
        
        if event.name == SYSTEM_CONFIG['exit_key']:
            return False

        if event.name == 'enter':
            if self.scan_buffer:
                code = self.scan_buffer
                self.scan_buffer = ""
                self._trigger_callback(code)
            return True

        if len(event.name) == 1:
            self.scan_buffer += event.name

        return True
    
    def start(self):
        print(f"扫码器启动，模式: {self.mode}")
        print(f"按 {SYSTEM_CONFIG['exit_key']} 键退出")

        if self.mode == 'serial':
            self._run_serial()
        else:
            self._run_keyboard()
    
    def _run_keyboard(self):
        keyboard.hook(self._on_key_press)
        keyboard.wait(SYSTEM_CONFIG['exit_key'])
    
    def _run_serial(self):
        if not self.serial_port:
            print("串口未初始化，切换到键盘模式")
            self._run_keyboard()
            return

        while True:
            try:
                if keyboard.is_pressed(SYSTEM_CONFIG['exit_key']):
                    break

                if self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8').strip()
                    if data:
                        self._trigger_callback(data)

                time.sleep(0.01)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"串口错误: {e}")
                break
    
    def stop(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        keyboard.unhook_all()
        print("扫码器已停止")
