@echo off
chcp 65001 >nul
echo ====================================
echo   扫码随机播报系统 - 依赖安装
echo ====================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.x
    pause
    exit /b 1
)

echo [1/6] 检查 pip 版本...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [错误] pip 未安装，正在安装...
    python -m ensurepip --upgrade
) else (
    python -m pip install --upgrade pip
)
if errorlevel 1 (
    echo [错误] pip 升级失败
    pause
    exit /b 1
)
echo [成功] pip 已就绪
echo.

echo [2/6] 安装 PyAudio (音频处理)...
echo [提示] PyAudio 需要 PortAudio，如果安装失败请尝试：
echo        Windows: 从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio 下载 .whl 文件
echo        或运行: pip install pipwin ^&^& pipwin install pyaudio
python -m pip install pyaudio
if errorlevel 1 (
    echo [警告] PyAudio 安装失败，语音功能可能不可用
    echo         尝试安装替代方案: pip install pipwin ^&^& pipwin install pyaudio
) else (
    echo [成功] PyAudio 已安装
)
echo.

echo [3/6] 安装 pyttsx3 (文字转语音)...
python -m pip install pyttsx3
if errorlevel 1 (
    echo [错误] pyttsx3 安装失败
    pause
    exit /b 1
)
echo [成功] pyttsx3 已安装
echo.

echo [4/6] 安装 pywin32 (Windows COM 高性能语音)...
python -m pip install pywin32
if errorlevel 1 (
    echo [警告] pywin32 安装失败，将使用 pyttsx3 回退模式
) else (
    echo [成功] pywin32 已安装
)
echo.

echo [5/6] 安装 pyserial (串口通信)...
python -m pip install pyserial
if errorlevel 1 (
    echo [错误] pyserial 安装失败
    pause
    exit /b 1
)
echo [成功] pyserial 已安装
echo.

echo [6/6] 安装 keyboard (键盘输入捕获)...
python -m pip install keyboard
if errorlevel 1 (
    echo [错误] keyboard 安装失败
    pause
    exit /b 1
)
echo [成功] keyboard 已安装
echo.

echo ====================================
echo   验证安装...
echo ====================================
python -c "import pyaudio; import pyttsx3; import serial; import keyboard; import win32com.client" >nul 2>&1
if errorlevel 1 (
    echo [警告] 部分依赖包无法导入，尝试无 pywin32 验证...
    python -c "import pyaudio; import pyttsx3; import serial; import keyboard" >nul 2>&1
    if errorlevel 1 (
        echo [错误] 部分依赖包无法导入，请检查安装
        pause
        exit /b 1
    )
    echo [成功] 核心依赖包验证通过！（高性能语音模式不可用）
) else (
    echo [成功] 所有依赖包验证通过！
)
echo.

echo ====================================
echo   安装完成！
echo ====================================
echo.
echo 运行系统: run.bat
echo.
pause
