"""
快速随机消息生成器
"""
import random


class FastRandomGenerator:
    """快速随机消息生成器"""
    
    def __init__(self, messages):
        self.messages = messages if messages else ["欢迎使用"]
        self.indices = list(range(len(self.messages)))
        random.shuffle(self.indices)
        self.current_idx = 0
    
    def get_next(self):
        if self.current_idx >= len(self.indices):
            random.shuffle(self.indices)
            self.current_idx = 0
        idx = self.indices[self.current_idx]
        self.current_idx += 1
        return self.messages[idx]
