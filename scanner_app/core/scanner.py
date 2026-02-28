"""
扫码器模块 - 适配PySide6重构
保持原有功能，添加接口封装
"""
import time
import keyboard
import serial
import threading
from PySide6.QtCore import QObject, Signal


class Scanner(QObject):
    """扫码器类 - 支持键盘和串口模式"""
    
    scan_received = Signal(str)  # 扫码信号
    
    def __init__(self, mode='keyboard', port=None, baudrate=9600, timeout=1):
        super().__init__()
        self.mode = mode
        self.serial_port = None
        self.scan_buffer = ""
        
        self.last_scan_time = 0
        self.last_scan_code = ""
        self.debounce_interval = 0.5
        self.scan_lock = threading.Lock()
        self.is_scanning = False
        self.exit_key = 'esc'
        
        if mode == 'serial' and port:
            self._init_serial(port, baudrate, timeout)
    
    def _init_serial(self, port, baudrate, timeout):
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
            )
            print(f"[Scanner] Serial port {port} connected")
        except serial.SerialException as e:
            print(f"[Scanner] Serial connection failed: {e}")
            self.mode = 'keyboard'
            print("[Scanner] Switched to keyboard mode")
    
    def _is_duplicate_scan(self, code):
        current_time = time.time()
        
        with self.scan_lock:
            if (code == self.last_scan_code and 
                current_time - self.last_scan_time < self.debounce_interval):
                print(f"[Scanner] Debounce: {code[:20]}...")
                return True
            
            self.last_scan_time = current_time
            self.last_scan_code = code
            return False
    
    def _trigger_callback(self, code):
        if not code:
            return
        
        if self._is_duplicate_scan(code):
            return
        
        with self.scan_lock:
            if self.is_scanning:
                print(f"[Scanner] Processing: {code[:20]}...")
                return
            self.is_scanning = True
        
        try:
            print(f"[Scanner] Code: {code}")
            self.scan_received.emit(code)
        finally:
            self.is_scanning = False
    
    def _on_key_press(self, event):
        if event.event_type != 'down':
            return True
        
        if event.name == self.exit_key:
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
        print(f"[Scanner] Starting, mode: {self.mode}")
        print(f"[Scanner] Press {self.exit_key} to exit")
        
        if self.mode == 'serial':
            self._run_serial()
        else:
            self._run_keyboard()
    
    def _run_keyboard(self):
        keyboard.hook(self._on_key_press)
        keyboard.wait(self.exit_key)
    
    def _run_serial(self):
        if not self.serial_port:
            print("[Scanner] Serial not initialized, switching to keyboard")
            self._run_keyboard()
            return
        
        while True:
            try:
                if keyboard.is_pressed(self.exit_key):
                    break
                
                if self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8').strip()
                    if data:
                        self._trigger_callback(data)
                
                time.sleep(0.01)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[Scanner] Serial error: {e}")
                break
    
    def stop(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        keyboard.unhook_all()
        print("[Scanner] Stopped")
