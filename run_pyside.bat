@echo off
title QR Scanner - PySide6 Edition
color 0A

cd /d "%~dp0"

echo ==========================================
echo     QR Scanner - Playful Edition
echo     PySide6 Version
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

if not exist "scanner_app\main.py" (
    echo [ERROR] scanner_app\main.py not found
    echo.
    pause
    exit /b 1
)

echo [START] Launching PySide6 application...
python scanner_app\main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Program exited with error
    echo.
    pause
)
