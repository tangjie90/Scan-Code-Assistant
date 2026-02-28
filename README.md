# 🍬 扫码小助手

> 一款童趣糖果风格的智能扫码收银系统，支持语音播报、商品管理、热更新等功能。

## ✨ 功能特性

### 核心功能
- 🎯 **智能扫码** - 支持键盘扫码枪，自动识别商品和付款码
- 🛒 **购物车管理** - 实时计算金额，支持商品累加
- 🔊 **语音播报** - TTS语音合成，支持多种语音风格
- 📦 **商品管理** - CSV文件存储，支持热更新

### 技术亮点
- 🎨 **童趣UI** - 糖果风格界面设计，可爱吉祥物
- ⚡ **语音队列** - FIFO排队机制，确保语音顺序播放
- 💾 **智能缓存** - 多级缓存架构，快速响应
- 🔄 **热更新** - 商品数据实时更新，无需重启

## 📋 系统要求

- Python 3.8+
- Windows / macOS / Linux

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python scanner_app/main.py
```

### 打包发布

```bash
pyinstaller scanner_app.spec
```

## 📁 项目结构

```
scanner_app/
├── main.py                 # 主程序入口
├── core/                   # 核心模块
│   ├── scanner.py          # 扫码器
│   ├── voice_queue.py      # 语音队列管理
│   ├── product_manager.py  # 商品管理器
│   ├── file_watcher.py     # 文件监控器
│   └── cache_manager.py    # 缓存管理器
├── ui/                     # 界面模块
│   ├── main_window.py      # 主窗口
│   ├── styles/             # 样式主题
│   └── widgets/            # UI组件
│       ├── candy_table.py  # 糖果表格
│       ├── candy_progress.py # 进度条
│       └── mascot.py       # 吉祥物
└── resources/              # 资源文件
    └── images/             # 图片资源

voice_cache/                # 语音缓存目录
products.csv                # 商品数据文件
config.json                 # 配置文件
```

## ⚙️ 配置说明

### config.json 配置项

```json
{
    "SYSTEM_CONFIG": {
        "payment_prefix": "臭宝",
        "payment_code_patterns": []
    },
    "RANDOM_MESSAGES": ["一元", "二元", "三元", "五元", "十元"],
    "BROADCAST_MESSAGES": {
        "welcome": {
            "text": "欢迎光临！",
            "key": "F1"
        }
    },
    "CUSTOM_MESSAGES": {
        "付款码": "自定义播报内容"
    },
    "VOICE_CONFIG": {
        "voice_name": "xiaoxiao",
        "rate": 0,
        "volume": 100
    }
}
```

### 商品数据文件 (products.csv)

```csv
条码,名称,价格,分类
6901234567890,可口可乐,2,饮料
6934472804733,烤馍片,3,零食
```

**支持热更新**：修改 `products.csv` 后自动生效，无需重启程序！

## 🎤 语音功能

### 可用语音

| 名称 | 标识 | 风格 |
|------|------|------|
| 晓晓 | xiaoxiao | 甜美女声 |
| 云希 | yunxi | 阳光男声 |
| 云扬 | yunyang | 沉稳男声 |

### 语音缓存

- 缓存位置：`voice_cache/` 目录
- 缓存格式：MP3 文件
- 自动管理：LRU淘汰策略

## 🔧 高级功能

### 付款码识别

支持多种付款码格式：
- 16-24位纯数字（银行卡）
- 28-36位纯数字（付款码）
- 微信支付链接
- 支付宝链接

### 语音队列机制

```
加入队列 → 检查缓存 → 生成音频 → 播放 → 执行回调 → 处理下一个
```

特性：
- FIFO顺序播放
- 优先级支持
- 防跳过机制
- 线程安全

### 商品热更新

```
文件变更 → watchdog检测 → 防抖处理 → 重新加载 → UI通知
```

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 缓存命中响应 | < 10ms |
| 语音生成时间 | 1.5-2.5s |
| 内存缓存上限 | 100条 / 50MB |
| 文件缓存上限 | 500MB |

## 🐛 故障排除

### 语音无法播放

```bash
pip install pygame edge-tts
```

### 扫码枪无法识别

确保扫码枪配置为键盘输入模式。

### 商品数据不更新

检查 `products.csv` 文件编码（推荐 UTF-8）。

## 📝 更新日志

### v2.0.0
- ✨ 新增商品热更新功能
- ✨ 新增语音队列机制
- 🎨 优化童趣UI界面
- 🐛 修复购物车金额计算问题
- 🐛 修复进度条动画问题

### v1.0.0
- 🎉 初始版本发布

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
