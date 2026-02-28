"""
语音队列管理器 - 最终简化版
确保语音按顺序依次播放
"""
import os
import hashlib
import threading
import asyncio
import time
from collections import deque
from typing import Optional, Dict
from enum import Enum

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class VoicePriority(Enum):
    HIGH = 1
    NORMAL = 2
    LOW = 3


class VoiceStatus(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    GENERATING = "generating"
    QUEUED = "queued"
    ERROR = "error"


class VoiceQueueManager:
    MAX_QUEUE_SIZE = 50
    MAX_MEMORY_CACHE = 100
    
    def __init__(self, cache_dir: str, voice_name: str = "xiaoxiao"):
        self.cache_dir = cache_dir
        self.voice_name = voice_name
        self.rate = 0
        self.volume = 100
        
        self._queue: deque = deque()
        self._memory_cache: Dict[str, str] = {}
        self._lock = threading.RLock()
        self._current_task = None
        self._is_processing = False
        self._should_stop = False
        
        self._status = VoiceStatus.IDLE
        
        self._stats = {
            'total_queued': 0,
            'total_played': 0,
            'total_errors': 0,
            'total_skipped': 0
        }
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        self._load_existing_cache()
    
    def _load_existing_cache(self):
        try:
            mp3_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.mp3')]
            print(f"[VoiceQueue] 加载缓存: {len(mp3_files)} 个音频文件")
        except Exception as e:
            print(f"[VoiceQueue] 加载缓存失败: {e}")
    
    def _get_cache_key(self, message: str) -> str:
        return hashlib.md5(f"{message}_{self.voice_name}_{self.rate}".encode()).hexdigest()
    
    def _get_cache_path(self, message: str) -> str:
        key = self._get_cache_key(message)
        return os.path.join(self.cache_dir, f"{key}.mp3")
    
    def _get_from_memory_cache(self, message: str) -> Optional[str]:
        key = self._get_cache_key(message)
        path = self._memory_cache.get(key)
        if path and os.path.exists(path):
            return path
        return None
    
    def _add_to_memory_cache(self, message: str, path: str):
        key = self._get_cache_key(message)
        if len(self._memory_cache) >= self.MAX_MEMORY_CACHE:
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
        self._memory_cache[key] = path
    
    def enqueue(self, message: str, priority: VoicePriority = VoicePriority.NORMAL) -> str:
        task_id = hashlib.md5(f"{message}_{time.time()}".encode()).hexdigest()[:8]
        task = {
            'id': task_id,
            'message': message,
            'priority': priority,
            'created_at': time.time()
        }
        
        with self._lock:
            if len(self._queue) >= self.MAX_QUEUE_SIZE:
                print(f"[VoiceQueue] 队列已满，跳过: {message[:20]}...")
                self._stats['total_skipped'] += 1
                return ""
            
            self._queue.append(task)
            self._stats['total_queued'] += 1
            
            queue_position = len(self._queue)
            print(f"[VoiceQueue] 加入队列 #{queue_position}: {message[:30]}... (ID: {task_id})")
        
        return task_id
    
    def dequeue(self) -> Optional[dict]:
        with self._lock:
            if not self._queue:
                return None
            return self._queue.popleft()
    
    def get_queue_size(self) -> int:
        with self._lock:
            return len(self._queue)
    
    def get_status(self) -> Dict[str, any]:
        with self._lock:
            return {
                'status': self._status.value,
                'queue_size': len(self._queue),
                'current_message': self._current_task['message'][:30] if self._current_task else None,
                'is_processing': self._is_processing,
                'stats': self._stats.copy()
            }
    
    def stop(self):
        self._should_stop = True
        skipped = len(self._queue)
        self._queue.clear()
        self._stats['total_skipped'] += skipped
        print(f"[VoiceQueue] 停止处理，跳过 {skipped} 个任务")


class VoiceGeneratorWithQueue:
    AVAILABLE_VOICES = {
        "xiaoxiao": "zh-CN-XiaoxiaoNeural",
        "yunxi": "zh-CN-YunxiNeural",
        "yunyang": "zh-CN-YunyangNeural",
    }
    
    def __init__(self, cache_dir: str):
        self.queue_manager = VoiceQueueManager(cache_dir)
        self._is_playing = False
        self._playback_complete = None
        
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._pygame = pygame
            self._pygame_available = True
        except ImportError:
            self._pygame = None
            self._pygame_available = False
            print("[WARN] pygame 未安装")
        
        try:
            import edge_tts
            self._edge_tts = edge_tts
            self._tts_available = True
        except ImportError:
            self._edge_tts = None
            self._tts_available = False
            print("[WARN] edge-tts 未安装")
    
    def _generate_audio(self, message: str, cache_path: str) -> bool:
        if not self._tts_available:
            return False
        
        try:
            voice_id = self.AVAILABLE_VOICES.get(
                self.queue_manager.voice_name, 
                "zh-CN-XiaoxiaoNeural"
            )
            rate = self.queue_manager.rate
            volume = self.queue_manager.volume
            rate_str = f"+{rate}%" if rate >= 0 else f"{rate}%"
            
            communicate = self._edge_tts.Communicate(
                message, voice_id, rate=rate_str, volume=f"+{volume}%"
            )
            
            asyncio.run(communicate.save(cache_path))
            
            return os.path.exists(cache_path) and os.path.getsize(cache_path) > 0
        except Exception as e:
            print(f"[VoiceQueue] 生成失败: {e}")
            return False
    
    def _play_audio(self, file_path: str) -> bool:
        if not self._pygame_available:
            return False
        
        try:
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                return False
            
            self._pygame.mixer.music.stop()
            self._pygame.mixer.music.unload()
            self._pygame.mixer.music.load(file_path)
            self._pygame.mixer.music.play()
            return True
        except Exception as e:
            print(f"[VoiceQueue] 播放失败: {e}")
            return False
    
    def _wait_playback(self):
        if self._pygame_available:
            while self._pygame.mixer.music.get_busy():
                if self.queue_manager._should_stop:
                    self._pygame.mixer.music.stop()
                    break
                time.sleep(0.05)
    
    def process_queue(self):
        while not self.queue_manager._should_stop:
            task = self.queue_manager.dequeue()
            
            if task is None:
                time.sleep(0.1)
                continue
            
            message = task['message']
            self.queue_manager._current_task = task
            self.queue_manager._status = VoiceStatus.PLAYING
            
            cache_path = self.queue_manager._get_cache_path(message)
            
            memory_path = self.queue_manager._get_from_memory_cache(message)
            if memory_path:
                print(f"[VoiceQueue] 使用内存缓存: {message[:30]}...")
            elif os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
                print(f"[VoiceQueue] 使用文件缓存: {message[:30]}...")
                self.queue_manager._add_to_memory_cache(message, cache_path)
            else:
                print(f"[VoiceQueue] 生成音频: {message[:30]}...")
                self.queue_manager._status = VoiceStatus.GENERATING
                
                if not self._generate_audio(message, cache_path):
                    self.queue_manager._stats['total_errors'] += 1
                    self.queue_manager._status = VoiceStatus.ERROR
                    self.queue_manager._current_message = ""
                    continue
                
                self.queue_manager._add_to_memory_cache(message, cache_path)
            
            if self._play_audio(cache_path):
                self._wait_playback()
                self.queue_manager._stats['total_played'] += 1
            
            else:
                self.queue_manager._stats['total_errors'] += 1
            
            self.queue_manager._current_task = None
            self.queue_manager._status = VoiceStatus.IDLE
            
            time.sleep(0.1)
    
    def speak(self, message: str, priority: VoicePriority = VoicePriority.NORMAL) -> str:
        return self.queue_manager.enqueue(message, priority)
    
    def speak_high_priority(self, message: str) -> str:
        return self.queue_manager.enqueue(message, VoicePriority.HIGH)
    
    def stop_current(self):
        if self._pygame_available:
            self._pygame.mixer.music.stop()
    
    def clear_queue(self):
        self.queue_manager.stop()
    
    def get_queue_status(self) -> dict:
        return self.queue_manager.get_status()
    
    def stop_processing(self):
        self.queue_manager._should_stop = True
    
    @property
    def is_playing(self):
        status = self.queue_manager.get_status()
        return status['status'] in ('playing', 'generating')
