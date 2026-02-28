"""
语音生成模块 - 使用 edge-tts 在线语音（更自然的语音）
"""
import asyncio
import threading
import queue
import tempfile
import os
import platform
from config_loader import VOICE_CONFIG

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("[WARN] edge-tts 未安装，将使用 pyttsx3 离线语音")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("[WARN] pyttsx3 未安装")

AVAILABLE_VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "yunxi": "zh-CN-YunxiNeural",
    "yunyang": "zh-CN-YunyangNeural",
    "xiaoyi": "zh-CN-XiaoyiNeural",
    "yunjian": "zh-CN-YunjianNeural",
    "xiaochen": "zh-CN-XiaochenNeural",
    "xiaohan": "zh-CN-XiaohanNeural",
    "xiaomeng": "zh-CN-XiaomengNeural",
    "xiaomo": "zh-CN-XiaomoNeural",
    "xiaoqiu": "zh-CN-XiaoqiuNeural",
    "xiaorui": "zh-CN-XiaoruiNeural",
    "xiaoshuang": "zh-CN-XiaoshuangNeural",
    "xiaoxuan": "zh-CN-XiaoxuanNeural",
    "xiaoyan": "zh-CN-XiaoyanNeural",
    "xiaoyou": "zh-CN-XiaoyouNeural",
    "yunfeng": "zh-CN-YunfengNeural",
    "yunhao": "zh-CN-YunhaoNeural",
    "yunxia": "zh-CN-YunxiaNeural",
    "yunye": "zh-CN-YunyeNeural",
}


class VoiceGenerator:
    def __init__(self):
        self.voice_queue = queue.Queue()
        self.is_running = False
        self.thread = None
        self.speaking = False
        self.speak_lock = threading.Lock()
        self.callback_queue = queue.Queue()
        
        self.voice_name = VOICE_CONFIG.get('voice_name', 'xiaoxiao')
        self.rate = VOICE_CONFIG.get('rate', 0)
        self.volume = VOICE_CONFIG.get('volume', 100)
        
        self.use_edge_tts = EDGE_TTS_AVAILABLE and VOICE_CONFIG.get('use_edge_tts', True)

    def _play_audio_file(self, file_path):
        """播放音频文件"""
        system = platform.system()
        try:
            if system == "Windows":
                import winsound
                winsound.PlaySound(file_path, winsound.SND_FILENAME)
            elif system == "Darwin":
                os.system(f"afplay {file_path}")
            else:
                os.system(f"mpg123 {file_path} 2>/dev/null || aplay {file_path} 2>/dev/null")
        except Exception as e:
            print(f"音频播放错误: {e}")

    async def _speak_with_edge_tts(self, message):
        """使用 edge-tts 生成并播放语音"""
        voice_id = AVAILABLE_VOICES.get(self.voice_name, "zh-CN-XiaoxiaoNeural")
        
        rate_str = f"+{self.rate}%" if self.rate >= 0 else f"{self.rate}%"
        volume_int = max(0, min(100, int(self.volume)))
        volume_str = f"+{volume_int}%"
        
        communicate = edge_tts.Communicate(
            message,
            voice_id,
            rate=rate_str,
            volume=volume_str
        )
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            await communicate.save(tmp_path)
            self._play_audio_file(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass

    def _create_engine_and_speak_pyttsx3(self, message):
        """使用 pyttsx3 播报（备用方案）"""
        if not PYTTSX3_AVAILABLE:
            print("pyttsx3 不可用，无法播报")
            return
        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', VOICE_CONFIG.get('rate', 260))
            engine.setProperty('volume', VOICE_CONFIG.get('volume', 1.0))
            voices = engine.getProperty('voices')
            if voices and len(voices) > VOICE_CONFIG.get('voice_index', 0):
                engine.setProperty('voice', voices[VOICE_CONFIG.get('voice_index', 0)].id)
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print(f"语音播放错误: {e}")
        finally:
            if engine:
                try:
                    del engine
                except:
                    pass

    def _speak_sync(self, message):
        """同步播报语音"""
        if self.use_edge_tts and EDGE_TTS_AVAILABLE:
            try:
                asyncio.run(self._speak_with_edge_tts(message))
            except Exception as e:
                print(f"edge-tts 播报失败: {e}，尝试使用 pyttsx3")
                self._create_engine_and_speak_pyttsx3(message)
        else:
            self._create_engine_and_speak_pyttsx3(message)

    def _worker(self):
        """语音播放工作线程"""
        while self.is_running:
            try:
                message = self.voice_queue.get(timeout=0.1)
                if message:
                    with self.speak_lock:
                        print(f"正在播报: {message}")
                        self._speak_sync(message)
                    
                    try:
                        callback = self.callback_queue.get_nowait()
                        if callback and callable(callback):
                            try:
                                callback()
                            except Exception as e:
                                print(f"回调执行错误: {e}")
                    except queue.Empty:
                        pass
                    
                    self.voice_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"语音队列错误: {e}")

    def start(self):
        """启动语音引擎"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._worker, daemon=True)
            self.thread.start()
            engine_type = "edge-tts" if self.use_edge_tts else "pyttsx3"
            print(f"语音引擎已启动 ({engine_type} 模式)")

    def speak(self, message):
        """添加语音消息到队列"""
        self.voice_queue.put(message)
        self.callback_queue.put(None)
        print(f"添加语音到队列: {message} (队列大小: {self.voice_queue.qsize()})")
    
    def speak_with_callback(self, message, callback=None):
        """添加语音消息到队列，播报完成后执行回调"""
        self.voice_queue.put(message)
        self.callback_queue.put(callback)
        print(f"添加语音到队列（带回调）: {message} (队列大小: {self.voice_queue.qsize()})")

    def stop(self):
        """停止语音引擎"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=3)
        print("语音引擎已停止")


def list_available_voices():
    """列出所有可用的 edge-tts 中文语音"""
    print("可用的中文语音列表:")
    print("=" * 50)
    for name, voice_id in AVAILABLE_VOICES.items():
        print(f"  {name}: {voice_id}")
    print("=" * 50)
    print("在 config.json 中设置 voice_name 来选择语音")


if __name__ == "__main__":
    list_available_voices()
