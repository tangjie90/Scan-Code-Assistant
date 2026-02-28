@echo off
chcp 936 >nul
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    扫码小助手 - 自动打包工具 v3.0
echo ============================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [步骤 1/6] 检查运行环境
echo --------------------------------------------

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo [OK] Python 版本: %PYTHON_VER%

echo.
echo [步骤 2/6] 检查必要文件
echo --------------------------------------------

if not exist "扫码小助手.spec" (
    echo [错误] 未找到 扫码小助手.spec 文件
    pause
    exit /b 1
)
if not exist "scanner_app\main.py" (
    echo [错误] 未找到 scanner_app\main.py 入口文件
    pause
    exit /b 1
)
if not exist "config.json" (
    echo [错误] 未找到 config.json 配置文件
    pause
    exit /b 1
)
if not exist "products.csv" (
    echo [错误] 未找到 products.csv 商品数据文件
    pause
    exit /b 1
)
echo [OK] 所有必要文件存在

echo.
echo [步骤 3/6] 检查并安装 PyInstaller
echo --------------------------------------------

python -c "import PyInstaller; print(PyInstaller.__version__)" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 正在安装 PyInstaller...
    python -m pip install pyinstaller --upgrade -q
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('python -c "import PyInstaller; print(PyInstaller.__version__)"') do set PYINSTALLER_VER=%%i
echo [OK] PyInstaller 版本: %PYINSTALLER_VER%

echo.
echo [步骤 4/6] 清理旧的构建文件
echo --------------------------------------------

if exist "dist\扫码小助手" (
    echo [INFO] 正在删除旧的输出目录...
    rmdir /s /q "dist\扫码小助手" 2>nul
)
if exist "build" (
    echo [INFO] 正在删除临时构建目录...
    rmdir /s /q "build" 2>nul
)
echo [OK] 清理完成

echo.
echo [步骤 5/6] 执行打包
echo --------------------------------------------
echo [INFO] 正在打包，请稍候...
echo [INFO] 使用 spec 配置文件: 扫码小助手.spec

python -m PyInstaller --clean "扫码小助手.spec"

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    echo 请检查错误信息并修复问题后重试
    pause
    exit /b 1
)

echo [OK] 打包完成

echo.
echo [步骤 6/6] 复制语音缓存和配置文件
echo --------------------------------------------

if exist "voice_cache" (
    echo [INFO] 正在复制语音缓存...
    xcopy /E /I /Y /Q "voice_cache" "dist\扫码小助手\voice_cache" >nul
    for /f %%i in ('dir /b "dist\扫码小助手\voice_cache\*.mp3" 2^>nul ^| find /c /v ""') do set CACHE_COUNT=%%i
    echo [OK] 已复制 !CACHE_COUNT! 个语音缓存文件
) else (
    echo [WARN] 未找到 voice_cache 目录，跳过
)

echo [INFO] 复制配置文件到 exe 同级目录（便于用户编辑）...
if exist "dist\扫码小助手\_internal\products.csv" (
    copy /Y "dist\扫码小助手\_internal\products.csv" "dist\扫码小助手\products.csv" >nul
    echo [OK] 已复制 products.csv
)
if exist "dist\扫码小助手\_internal\config.json" (
    copy /Y "dist\扫码小助手\_internal\config.json" "dist\扫码小助手\config.json" >nul
    echo [OK] 已复制 config.json
)

echo.
echo ============================================
echo           打包完成！
echo ============================================
echo.
echo  输出目录: %PROJECT_DIR%dist\扫码小助手\
echo  主程序:   扫码小助手.exe
echo  配置文件: config.json (可编辑)
echo  商品配置: products.csv (可用Excel编辑)
echo.
echo  使用说明:
echo  1. 将整个 "扫码小助手" 文件夹复制到目标电脑
echo  2. 双击 "扫码小助手.exe" 运行程序
echo  3. 用 Excel 编辑 products.csv 添加商品
echo  4. 修改 config.json 调整系统配置
echo.
echo  [注意] 首次运行需要联网下载语音（如缓存不完整）
echo.

pause
