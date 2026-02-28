"""
示例配置 - 如何自定义扫码随机播报系统
"""

# 1. 如果使用串口连接的扫码枪，请修改 config.py 中的 SCANNER_CONFIG
# SCANNER_CONFIG = {
#     'port': 'COM3',  # Windows: COM3, COM4 等；Linux: /dev/ttyUSB0
#     'mode': 'serial',  # 改为 'serial'
# }

# 2. 如果使用USB扫码枪（模拟键盘输入），保持默认配置
SCANNER_CONFIG = {
    'mode': 'keyboard',  # 键盘模式
}

# 3. 自定义播报消息
RANDOM_MESSAGES = [
    "欢迎光临！",
    "祝您今天愉快！",
    # 添加更多消息...
]

# 4. 自定义扫码结果对应消息 - 支持多种匹配模式
CUSTOM_MESSAGES = {
    # 精确匹配：扫描到完全相同的码时播报指定消息
    '123456': '会员码，欢迎会员光临！',
    '789012': '特价商品，快来选购！',
    
    # 通配符匹配：使用*匹配任意字符序列
    'VIP*': '尊贵会员，欢迎您！',           # 匹配VIP001, VIP123等
    'product-*': '商品扫码成功',           # 匹配product-001, product-abc等
    'ORDER-*-*': '订单扫码成功',           # 匹配ORDER-123-456等
    
    # 正则表达式匹配：以regex:开头，使用正则表达式模式
    'regex:^\\d{6}$': '6位数字码',         # 匹配6位纯数字
    'regex:^https?://': '网站链接扫码',     # 匹配http或https开头的URL
    'regex:^[A-Z]{3}-\\d{4}$': '产品编号扫码',  # 匹配ABC-1234格式
    
    # 注意：优先级为 精确匹配 > 通配符 > 正则表达式
}

# 5. 调整语音参数
VOICE_CONFIG = {
    'rate': 150,  # 语速，数值越大越快
    'volume': 1.0,  # 音量 0.0-1.0
    'voice_index': 0,  # 尝试不同的索引选择不同的语音
}
