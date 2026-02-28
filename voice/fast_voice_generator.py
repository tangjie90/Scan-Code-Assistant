"""
快速语音生成模块
"""
import queue
import threading
import time
import asyncio
from config_loader import VOICE_CONFIG, get_scan_delay, get_queue_check_interval
from .voice_cache import VoiceCache


try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("[WARN] edge-tts 未安装")

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("[WARN] pygame 未安装")


class FastVoiceGenerator:
    """快速语音生成器"""
    
    def __init__(self, root):
        self.root = root
        self.message_queue = queue.Queue()
        self.callback_queue = queue.Queue()
        self.is_running = True
        self.voice_name = VOICE_CONFIG.get('voice_name', 'xiaoxiao')
        self.use_edge_tts = EDGE_TTS_AVAILABLE and VOICE_CONFIG.get('use_edge_tts', True)
        self.scan_delay = get_scan_delay()
        self.check_interval = get_queue_check_interval()
        self.cache = VoiceCache()
        self.cache_loaded = False
        self.preloaded_sounds = {}
        self.total_speaks = 0
        self.speaking = False
        self._schedule_check()
    
    def preload_common_messages(self, messages, progress_callback=None):
        if not self.use_edge_tts or not EDGE_TTS_AVAILABLE:
            self.cache_loaded = True
            return
        def _preload_thread():
            try:
                results = self.cache.preload_messages(messages, progress_callback)
                self.preloaded_sounds = results
                self.cache_loaded = True
            except Exception as e:
                self.cache_loaded = True
        threading.Thread(target=_preload_thread, daemon=True).start()
    
    def _schedule_check(self):
        if not self.is_running:
            return
        try:
            message = self.message_queue.get_nowait()
            callback = self.callback_queue.get_nowait()
            self._speak_async(message, callback)
        except queue.Empty:
            pass
        self.root.after(self.check_interval, self._schedule_check)
    
    def _speak_async(self, message, callback):
        if self.speaking:
            self.root.after(50, lambda: self._speak_async(message, callback))
            return
        self.speaking = True
        start_time = time.time()
        def _speak_thread():
            try:
                if self.use_edge_tts and EDGE_TTS_AVAILABLE and PYGAME_AVAILABLE:
                    self._speak_cached(message)
                else:
                    self._speak_fallback(message)
                elapsed = (time.time() - start_time) * 1000
                self.total_speaks += 1
                print(f"[VOICE] #{self.total_speaks} 播报: {message} ({elapsed:.0f}ms)")
                if callback and callable(callback):
                    self.root.after(0, callback)
            except Exception as e:
                print(f"[ERROR] 语音播报失败: {e}")
            finally:
                self.speaking = False
        threading.Thread(target=_speak_thread, daemon=True).start()
    
    def _speak_cached(self, message):
        cache_path = self.cache.get_cache(message)
        if cache_path is None:
            cache_path = asyncio.run(self.cache.generate_and_cache(message))
        if PYGAME_AVAILABLE:
            pygame.mixer.music.load(cache_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.01)
        else:
            import winsound
            winsound.PlaySound(cache_path, winsound.SND_FILENAME)
    
    def _speak_fallback(self, message):
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', VOICE_CONFIG.get('rate', 260))
        engine.setProperty('volume', VOICE_CONFIG.get('volume', 1.0))
        voices = engine.getProperty('voices')
        if voices and len(voices) > VOICE_CONFIG.get('voice_index', 0):
            engine.setProperty('voice', voices[VOICE_CONFIG.get('voice_index', 0)].id)
        engine.say(message)
        engine.runAndWait()
        del engine
    
    def speak(self, message):
        self.message_queue.put(message)
        self.callback_queue.put(None)
    
    def speak_with_callback(self, message, callback):
        self.message_queue.put(message)
        self.callback_queue.put(callback)
    
    def stop(self):
        self.is_running = False
        if PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
