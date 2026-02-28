"""
音效管理器 - 互动反馈音效
"""
import os
import sys

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("[WARN] pygame 未安装，音效功能不可用")


def get_sounds_dir():
    """获取音效目录路径"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        internal_dir = os.path.join(base_dir, '_internal', 'sounds')
        if os.path.exists(internal_dir):
            return internal_dir
        return os.path.join(base_dir, 'sounds')
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sounds')


class SoundManager:
    """音效管理器"""
    
    SOUND_FILES = {
        'scan': 'scan.mp3',
        'lucky': 'lucky.mp3',
        'clear': 'clear.mp3',
        'payment': 'payment.mp3',
        'click': 'click.mp3'
    }
    
    def __init__(self):
        self.enabled = PYGAME_AVAILABLE
        self.volume = 0.7
        self.sounds = {}
        self.sounds_dir = get_sounds_dir()
        
        if self.enabled:
            self._load_sounds()
    
    def _load_sounds(self):
        """预加载所有音效"""
        for name, filename in self.SOUND_FILES.items():
            path = os.path.join(self.sounds_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.volume)
                except Exception as e:
                    print(f"[WARN] 无法加载音效 {filename}: {e}")
    
    def play(self, sound_name):
        """播放音效"""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            self.sounds[sound_name].play()
        except Exception as e:
            print(f"[WARN] 播放音效失败: {e}")
    
    def set_volume(self, volume):
        """设置音量 (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def set_enabled(self, enabled):
        """启用/禁用音效"""
        self.enabled = enabled if PYGAME_AVAILABLE else False


sound_manager = SoundManager()
