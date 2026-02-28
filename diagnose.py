import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print('=== 模块导入测试 ===')

try:
    from scanner_app.ui.styles.theme import CandyTheme
    print('[OK] CandyTheme')
except Exception as e:
    print(f'[FAIL] CandyTheme: {e}')

try:
    from scanner_app.ui.widgets.candy_button import CandyButton
    print('[OK] CandyButton')
except Exception as e:
    print(f'[FAIL] CandyButton: {e}')

try:
    from scanner_app.ui.widgets.candy_table import CandyTable
    print('[OK] CandyTable')
except Exception as e:
    print(f'[FAIL] CandyTable: {e}')

try:
    from scanner_app.ui.widgets.candy_progress import CandyProgressBar
    print('[OK] CandyProgressBar')
except Exception as e:
    print(f'[FAIL] CandyProgressBar: {e}')

try:
    from scanner_app.ui.widgets.mascot_widget import RabbitMascot
    print('[OK] RabbitMascot')
except Exception as e:
    print(f'[FAIL] RabbitMascot: {e}')

try:
    from scanner_app.ui.widgets.bubble_log import BubbleLog
    print('[OK] BubbleLog')
except Exception as e:
    print(f'[FAIL] BubbleLog: {e}')

try:
    from scanner_app.ui.widgets.broadcast_button import BroadcastButton
    print('[OK] BroadcastButton')
except Exception as e:
    print(f'[FAIL] BroadcastButton: {e}')

try:
    from scanner_app.ui.widgets.broadcast_panel import BroadcastPanel
    print('[OK] BroadcastPanel')
except Exception as e:
    print(f'[FAIL] BroadcastPanel: {e}')

try:
    from scanner_app.ui.main_window import MainWindow
    print('[OK] MainWindow')
except Exception as e:
    print(f'[FAIL] MainWindow: {e}')

try:
    from scanner_app.core.scanner import Scanner
    print('[OK] Scanner')
except Exception as e:
    print(f'[FAIL] Scanner: {e}')

try:
    import edge_tts
    print('[OK] edge_tts')
except Exception as e:
    print(f'[FAIL] edge_tts: {e}')

try:
    import pygame
    print('[OK] pygame')
except Exception as e:
    print(f'[FAIL] pygame: {e}')

print('\n=== 配置文件测试 ===')
try:
    import json
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    print('[OK] config.json 加载成功')
    print(f'  - RANDOM_MESSAGES: {len(config.get("RANDOM_MESSAGES", []))} 条')
    print(f'  - BROADCAST_MESSAGES: {len(config.get("BROADCAST_MESSAGES", {}))} 个')
except Exception as e:
    print(f'[FAIL] config.json: {e}')

print('\n=== 诊断完成 ===')
