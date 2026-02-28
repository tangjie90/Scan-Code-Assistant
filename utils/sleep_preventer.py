"""
系统休眠阻止工具
"""
import sys
import ctypes


class SystemSleepPreventer:
    """系统休眠阻止器"""
    
    def __init__(self):
        self.original_state = None
        self.enabled = False
        
    def enable(self):
        if sys.platform == 'win32':
            try:
                ES_CONTINUOUS = 0x80000000
                ES_SYSTEM_REQUIRED = 0x00000001
                ES_DISPLAY_REQUIRED = 0x00000002
                self.original_state = ctypes.windll.kernel32.SetThreadExecutionState(
                    ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
                )
                self.enabled = True
            except:
                pass
