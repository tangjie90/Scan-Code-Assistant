"""
文件监控器模块 - 基于 watchdog

特性：
- 实时文件变更检测
- 防抖机制
- 跨平台支持
"""
import os
import time
import threading
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("[FileWatcher] watchdog 未安装，使用轮询模式")


class FileWatcherBase:
    """文件监控器基类"""
    
    def __init__(self, file_path: str, callback: Callable[[], None], debounce_ms: int = 500):
        self._path = Path(file_path)
        self._callback = callback
        self._debounce_ms = debounce_ms
        self._last_trigger = 0.0
        self._running = False
        self._lock = threading.Lock()
    
    def start(self):
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError
    
    def _trigger_callback(self):
        """防抖触发回调"""
        now = time.time() * 1000
        with self._lock:
            if now - self._last_trigger < self._debounce_ms:
                return
            self._last_trigger = now
        
        print(f"[FileWatcher] 检测到文件变更: {self._path.name}")
        try:
            self._callback()
        except Exception as e:
            print(f"[FileWatcher] 回调执行失败: {e}")


if WATCHDOG_AVAILABLE:
    class FileEventHandler(FileSystemEventHandler):
        """文件事件处理器"""
        
        def __init__(self, watcher: 'FileWatcherBase'):
            self._watcher = watcher
        
        def on_modified(self, event):
            if not event.is_directory:
                if Path(event.src_path).resolve() == self._watcher._path.resolve():
                    self._watcher._trigger_callback()
        
        def on_created(self, event):
            if not event.is_directory:
                if Path(event.src_path).resolve() == self._watcher._path.resolve():
                    self._watcher._trigger_callback()


class FileWatcher(FileWatcherBase):
    """文件监控器 - watchdog 实现"""
    
    def __init__(self, file_path: str, callback: Callable[[], None], debounce_ms: int = 500):
        super().__init__(file_path, callback, debounce_ms)
        self._observer: Optional[Observer] = None
        self._handler: Optional[FileEventHandler] = None
    
    def start(self):
        if self._running:
            return
        
        if WATCHDOG_AVAILABLE:
            self._handler = FileEventHandler(self)
            self._observer = Observer()
            self._observer.schedule(
                self._handler,
                str(self._path.parent),
                recursive=False
            )
            self._observer.start()
            print(f"[FileWatcher] 已启动监控: {self._path.name}")
        else:
            self._start_polling()
        
        self._running = True
    
    def _start_polling(self):
        """轮询模式（无 watchdog 时使用）"""
        def poll():
            last_mtime = 0
            while self._running:
                try:
                    if self._path.exists():
                        current_mtime = self._path.stat().st_mtime
                        if current_mtime > last_mtime:
                            if last_mtime > 0:
                                self._trigger_callback()
                            last_mtime = current_mtime
                except Exception as e:
                    print(f"[FileWatcher] 轮询错误: {e}")
                time.sleep(1)
        
        self._poll_thread = threading.Thread(target=poll, daemon=True)
        self._poll_thread.start()
        print(f"[FileWatcher] 已启动轮询模式: {self._path.name}")
    
    def stop(self):
        if not self._running:
            return
        
        self._running = False
        
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            print(f"[FileWatcher] 已停止监控: {self._path.name}")


class ProductFileWatcher(FileWatcher):
    """商品文件监控器"""
    
    def __init__(self, csv_path: str, on_change: Callable[[], None]):
        super().__init__(csv_path, on_change, debounce_ms=1000)
    
    def get_status(self) -> dict:
        return {
            'file': str(self._path),
            'running': self._running,
            'last_trigger': datetime.fromtimestamp(self._last_trigger / 1000).isoformat() if self._last_trigger else None,
            'watchdog_available': WATCHDOG_AVAILABLE
        }
