@echo off
echo 快速安装扫码随机播报系统依赖...
echo.

:: 一键安装所有依赖
python -m pip install --upgrade pip pyaudio pyttsx3 pyserial keyboard

if errorlevel 1 (
    echo.
    echo [错误] 安装失败，请尝试完整安装脚本: install.bat
    pause
    exit /b 1
)

echo.
echo 安装完成！
echo 运行: python main.py
pause
