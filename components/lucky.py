"""
幸运数字系统 - 特殊播报和效果
"""


class LuckyNumberSystem:
    """幸运数字系统"""
    
    LUCKY_CONFIG = {
        '6': {'message': '六六大顺！', 'effect': 'gold_stars'},
        '8': {'message': '发财啦！', 'effect': 'coin_rain'},
        '9': {'message': '长长久久！', 'effect': 'hearts'},
        '10': {'message': '十全十美！', 'effect': 'rainbow'}
    }
    
    PRICE_MAP = {
        "一元": 1, "二元": 2, "三元": 3, "四元": 4, "五元": 5,
        "六元": 6, "七元": 7, "八元": 8, "九元": 9, "十元": 10
    }
    
    def __init__(self):
        self.enabled = True
    
    def check_lucky(self, price_text):
        """检查是否为幸运数字"""
        if not self.enabled:
            return None
        
        price_num = self.PRICE_MAP.get(price_text, 0)
        
        if str(price_num) in self.LUCKY_CONFIG:
            return self.LUCKY_CONFIG[str(price_num)]
        
        return None
    
    def get_lucky_message(self, price_text):
        """获取幸运消息"""
        lucky_info = self.check_lucky(price_text)
        if lucky_info:
            return lucky_info.get('message', '幸运！')
        return None
    
    def get_lucky_effect(self, price_text):
        """获取幸运效果名称"""
        lucky_info = self.check_lucky(price_text)
        if lucky_info:
            return lucky_info.get('effect', 'gold_stars')
        return None
    
    def set_enabled(self, enabled):
        """启用/禁用幸运数字"""
        self.enabled = enabled
