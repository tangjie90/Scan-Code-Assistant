"""
配置加载模块 - 支持外部配置文件
优先加载 exe 目录下的配置文件（便于用户编辑）
如果不存在则加载 _internal 目录下的配置文件
"""
import json
import os
import sys
from product_manager import load_products as _load_products, get_all_product_names, get_config_path

# 语音速度预设映射（pyttsx3 rate 值）
VOICE_SPEED_PRESETS = {
    "slow": 150,      # 慢速：适合老人/听力障碍
    "normal": 260,    # 正常：默认速度
    "fast": 350,      # 快速：高效播报
    "very_fast": 450  # 极快：最快速
}

# 默认配置
DEFAULT_CONFIG = {
    "SCANNER_CONFIG": {
        "port": None,
        "baudrate": 9600,
        "mode": "keyboard",
        "timeout": 1
    },
    "VOICE_CONFIG": {
        "use_edge_tts": True,
        "voice_name": "xiaoxiao",
        "rate": 0,
        "volume": 100,
        "voice_index": 0
    },
    "TIMING_CONFIG": {
        "scan_delay_ms": 0,           # 扫码后延迟播报时间（毫秒）
        "queue_check_interval_ms": 10  # 队列检查间隔（毫秒）
    },
    "RANDOM_MESSAGES": [
        "一元", "二元", "三元", "四元", "五元",
        "六元", "七元", "八元", "九元", "十元"
    ],
    "CUSTOM_MESSAGES": {},
    "PAYMENT_SUCCESS_MESSAGE": "付款成功",
    "SYSTEM_CONFIG": {
        "random_mode": True,
        "repeat_message": False,
        "exit_key": "esc",
        "prevent_sleep": True,
        "enable_accumulation": True,
        "payment_prefix": "臭宝",
        "payment_code_length": 36,
        "payment_code_patterns": ["^\\d{16,24}$", "^\\d{36}$"]
    }
}

def load_config():
    """加载配置文件"""
    config_file = get_config_path()
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"[OK] 已加载配置文件: {config_file}")
                return config
        except Exception as e:
            print(f"[WARN] 配置文件加载失败: {e}，使用默认配置")
    else:
        print(f"[INFO] 配置文件不存在: {config_file}，使用默认配置")
    
    return DEFAULT_CONFIG.copy()

# 加载配置
CONFIG = load_config()

# 导出配置变量
SCANNER_CONFIG = CONFIG.get("SCANNER_CONFIG", DEFAULT_CONFIG["SCANNER_CONFIG"])
VOICE_CONFIG = CONFIG.get("VOICE_CONFIG", DEFAULT_CONFIG["VOICE_CONFIG"])
TIMING_CONFIG = CONFIG.get("TIMING_CONFIG", DEFAULT_CONFIG["TIMING_CONFIG"])
RANDOM_MESSAGES = CONFIG.get("RANDOM_MESSAGES", DEFAULT_CONFIG["RANDOM_MESSAGES"])
CUSTOM_MESSAGES = CONFIG.get("CUSTOM_MESSAGES", DEFAULT_CONFIG["CUSTOM_MESSAGES"])
PAYMENT_SUCCESS_MESSAGE = CONFIG.get("PAYMENT_SUCCESS_MESSAGE", DEFAULT_CONFIG["PAYMENT_SUCCESS_MESSAGE"])
SYSTEM_CONFIG = CONFIG.get("SYSTEM_CONFIG", DEFAULT_CONFIG["SYSTEM_CONFIG"])

# 商品配置（从 products.csv 加载）
PRODUCTS = _load_products()

def get_voice_rate():
    """获取实际语速值（edge-tts 使用百分比）"""
    return VOICE_CONFIG.get("rate", 0)

def get_scan_delay():
    """获取扫码延迟时间（秒）"""
    return TIMING_CONFIG.get("scan_delay_ms", 0) / 1000.0

def get_queue_check_interval():
    """获取队列检查间隔（毫秒）"""
    return TIMING_CONFIG.get("queue_check_interval_ms", 10)

def get_product_names():
    """获取所有商品名称（用于语音缓存）"""
    return get_all_product_names(PRODUCTS)

if __name__ == "__main__":
    print("=" * 50)
    print("当前配置摘要:")
    print(f"  扫码器模式: {SCANNER_CONFIG['mode']}")
    print(f"  语音引擎: {'edge-tts' if VOICE_CONFIG.get('use_edge_tts', True) else 'pyttsx3'}")
    print(f"  语音名称: {VOICE_CONFIG.get('voice_name', 'xiaoxiao')}")
    print(f"  语速调整: {VOICE_CONFIG.get('rate', 0)}%")
    print(f"  扫码延迟: {get_scan_delay()*1000:.0f}ms")
    print(f"  随机消息数量: {len(RANDOM_MESSAGES)}")
    print(f"  付款前缀: {SYSTEM_CONFIG.get('payment_prefix', '臭宝')}")
    print("=" * 50)