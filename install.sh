#!/bin/bash

echo "正在安装扫码随机播报系统的依赖..."
echo ""

echo "1. 升级 pip..."
python3 -m pip install --upgrade pip

echo ""
echo "2. 安装 PyAudio (音频处理)..."
echo "注意: PyAudio 在 Linux 上可能需要先安装 portaudio 开发库"
echo "Ubuntu/Debian: sudo apt-get install python3-pyaudio portaudio19-dev"
pip install pyaudio

echo ""
echo "3. 安装 pyttsx3 (文字转语音)..."
pip install pyttsx3

echo ""
echo "4. 安装 pyserial (串口通信)..."
pip install pyserial

echo ""
echo "5. 安装 keyboard (键盘输入捕获)..."
echo "注意: 在 Linux 上可能需要 root 权限或 sudo 运行"
pip install keyboard

echo ""
echo "===================================="
echo "所有依赖安装完成！"
echo "===================================="
echo ""
echo "运行系统: python3 main.py"
echo ""
