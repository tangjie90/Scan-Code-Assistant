"""
语音缓存管理模块
"""
import os
import sys
import hashlib
import asyncio
from config_loader import VOICE_CONFIG


def get_project_dir():
    """获取项目根目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


AVAILABLE_VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "yunxi": "zh-CN-YunxiNeural",
    "yunyang": "zh-CN-YunyangNeural",
    "xiaoyi": "zh-CN-XiaoyiNeural",
}


class VoiceCache:
    """语音缓存管理器"""
    
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            project_dir = get_project_dir()
            cache_dir = os.path.join(project_dir, "voice_cache")
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.voice_name = VOICE_CONFIG.get('voice_name', 'xiaoxiao')
        self.rate = VOICE_CONFIG.get('rate', 0)
        self.volume = VOICE_CONFIG.get('volume', 100)
        
    def _get_cache_key(self, text):
        voice_id = AVAILABLE_VOICES.get(self.voice_name, "zh-CN-XiaoxiaoNeural")
        key_str = f"{text}_{voice_id}_{self.rate}_{self.volume}"
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, text):
        return os.path.join(self.cache_dir, f"{self._get_cache_key(text)}.mp3")
    
    def has_cache(self, text):
        return os.path.exists(self._get_cache_path(text))
    
    def get_cache(self, text):
        path = self._get_cache_path(text)
        if os.path.exists(path):
            return path
        return None
    
    async def generate_and_cache(self, text):
        try:
            import edge_tts
        except ImportError:
            raise ImportError("edge_tts is not available")
            
        cache_path = self._get_cache_path(text)
        if os.path.exists(cache_path):
            return cache_path
        voice_id = AVAILABLE_VOICES.get(self.voice_name, "zh-CN-XiaoxiaoNeural")
        rate_str = f"+{self.rate}%" if self.rate >= 0 else f"{self.rate}%"
        volume_int = max(0, min(100, int(self.volume)))
        volume_str = f"+{volume_int}%"
        communicate = edge_tts.Communicate(text, voice_id, rate=rate_str, volume=volume_str)
        await communicate.save(cache_path)
        return cache_path
    
    def preload_messages(self, messages, progress_callback=None):
        results = {}
        total = len(messages)
        async def _preload():
            for i, msg in enumerate(messages):
                try:
                    path = await self.generate_and_cache(msg)
                    results[msg] = path
                    if progress_callback:
                        progress_callback(i + 1, total, msg)
                except Exception as e:
                    print(f"[CACHE] 预加载失败 '{msg}': {e}")
        asyncio.run(_preload())
        return results
