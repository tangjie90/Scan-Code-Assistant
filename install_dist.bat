@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo  扫码随机播报系统 - 安装程序
echo ========================================
echo.
echo 此安装程序将系统文件复制到指定目录。
echo 请确保已使用 build.bat 打包生成 dist 文件夹。
echo.

REM 检查dist文件夹
if not exist "dist\main.exe" (
    echo [错误] 未找到 dist\main.exe
    echo 请先运行 build.bat 打包系统
    pause
    exit /b 1
)

REM 选择安装目录
set "default_dir=%ProgramFiles%\扫码播报系统"
echo 请输入安装目录 (默认: %default_dir%)
set /p install_dir="安装目录: "
if "!install_dir!"=="" set "install_dir=%default_dir%"

REM 创建目录
echo.
echo [INFO] 正在创建目录: !install_dir!
mkdir "!install_dir!" 2>nul
if errorlevel 1 (
    echo [错误] 无法创建目录，请检查权限
    pause
    exit /b 1
)

REM 复制文件
echo [INFO] 正在复制程序文件...
xcopy "dist\*" "!install_dir!\" /E /Y /Q

if errorlevel 1 (
    echo [错误] 文件复制失败
    pause
    exit /b 1
)

echo [OK] 程序文件复制完成

REM 创建桌面快捷方式
echo.
set /p create_shortcut="是否创建桌面快捷方式? (y/n, 默认y): "
if /i "!create_shortcut!"=="y" (
    if "!create_shortcut!"=="" set "create_shortcut=y"
)

if /i "!create_shortcut!"=="y" (
    set "shortcut_path=%USERPROFILE%\Desktop\扫码播报系统.lnk"
    
    REM 使用 PowerShell 创建快捷方式
    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut_path%'); $Shortcut.TargetPath = '!install_dir!\main.exe'; $Shortcut.WorkingDirectory = '!install_dir!'; $Shortcut.Save()"
    
    if errorlevel 1 (
        echo [WARN] 快捷方式创建失败，请手动创建
    ) else (
        echo [OK] 桌面快捷方式已创建
    )
)

REM 创建开始菜单快捷方式
echo.
set /p create_startmenu="是否创建开始菜单快捷方式? (y/n, 默认y): "
if /i "!create_startmenu!"=="y" (
    if "!create_startmenu!"=="" set "create_startmenu=y"
)

if /i "!create_startmenu!"=="y" (
    set "startmenu_dir=%APPDATA%\Microsoft\Windows\Start Menu\Programs\扫码播报系统"
    mkdir "!startmenu_dir!" 2>nul
    
    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('!startmenu_dir!\扫码播报系统.lnk'); $Shortcut.TargetPath = '!install_dir!\main.exe'; $Shortcut.WorkingDirectory = '!install_dir!'; $Shortcut.Save()"
    
    echo [OK] 开始菜单快捷方式已创建
)

echo.
echo ========================================
echo  安装完成
echo ========================================
echo.
echo  安装目录: !install_dir!
echo  主程序: !install_dir!\main.exe
echo  配置文件: !install_dir!\config.json
echo.
echo  启动方式:
echo  1. 双击桌面快捷方式"扫码播报系统"
echo  2. 或直接运行 !install_dir!\main.exe
echo.
echo  配置说明:
echo  如需修改播报内容、语速等设置，请编辑 !install_dir!\config.json
echo.
echo  [注意] 系统需要音频设备和语音合成引擎支持
echo        Windows 系统通常已自带，无需额外安装
echo.

pause