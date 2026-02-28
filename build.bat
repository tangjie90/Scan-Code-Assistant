@echo off
chcp 936 >nul
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    ɨ��С���� - �Զ�������� v3.0
echo ============================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [���� 1/6] ������л���
echo --------------------------------------------

python --version >nul 2>&1
if errorlevel 1 (
    echo [����] δ�ҵ� Python�����Ȱ�װ Python 3.8+
    echo ���ص�ַ: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo [OK] Python �汾: %PYTHON_VER%

echo.
echo [���� 2/6] ����Ҫ�ļ�
echo --------------------------------------------

if not exist "ɨ��С����.spec" (
    echo [����] δ�ҵ� ɨ��С����.spec �ļ�
    pause
    exit /b 1
)
if not exist "scanner_app\main.py" (
    echo [����] δ�ҵ� scanner_app\main.py ����ļ�
    pause
    exit /b 1
)
if not exist "config.json" (
    echo [����] δ�ҵ� config.json �����ļ�
    pause
    exit /b 1
)
if not exist "products.csv" (
    echo [����] δ�ҵ� products.csv ��Ʒ�����ļ�
    pause
    exit /b 1
)
echo [OK] ���б�Ҫ�ļ�����

echo.
echo [���� 3/6] ��鲢��װ PyInstaller
echo --------------------------------------------

python -c "import PyInstaller; print(PyInstaller.__version__)" >nul 2>&1
if errorlevel 1 (
    echo [INFO] ���ڰ�װ PyInstaller...
    python -m pip install pyinstaller --upgrade -q
    if errorlevel 1 (
        echo [����] PyInstaller ��װʧ��
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('python -c "import PyInstaller; print(PyInstaller.__version__)"') do set PYINSTALLER_VER=%%i
echo [OK] PyInstaller �汾: %PYINSTALLER_VER%

echo.
echo [���� 4/6] �����ɵĹ����ļ�
echo --------------------------------------------

if exist "dist\ɨ��С����" (
    echo [INFO] ����ɾ���ɵ����Ŀ¼...
    rmdir /s /q "dist\ɨ��С����" 2>nul
)
if exist "build" (
    echo [INFO] ����ɾ����ʱ����Ŀ¼...
    rmdir /s /q "build" 2>nul
)
echo [OK] �������

echo.
echo [���� 5/6] ִ�д��
echo --------------------------------------------
echo [INFO] ���ڴ�������Ժ�...
echo [INFO] ʹ�� spec �����ļ�: ɨ��С����.spec

python -m PyInstaller --clean "ɨ��С����.spec"

if errorlevel 1 (
    echo.
    echo [����] ���ʧ�ܣ�
    echo ���������Ϣ���޸����������
    pause
    exit /b 1
)

echo [OK] ������

echo.
echo [���� 6/6] ������������������ļ�
echo --------------------------------------------

if exist "voice_cache" (
    echo [INFO] ���ڸ�����������...
    xcopy /E /I /Y /Q "voice_cache" "dist\ɨ��С����\voice_cache" >nul
    for /f %%i in ('dir /b "dist\ɨ��С����\voice_cache\*.mp3" 2^>nul ^| find /c /v ""') do set CACHE_COUNT=%%i
    echo [OK] �Ѹ��� !CACHE_COUNT! �����������ļ�
) else (
    echo [WARN] δ�ҵ� voice_cache Ŀ¼������
)

echo [INFO] ���������ļ��� exe ͬ��Ŀ¼�������û��༭��...
if exist "dist\ɨ��С����\_internal\products.csv" (
    copy /Y "dist\ɨ��С����\_internal\products.csv" "dist\ɨ��С����\products.csv" >nul
    echo [OK] �Ѹ��� products.csv
)
if exist "dist\ɨ��С����\_internal\config.json" (
    copy /Y "dist\ɨ��С����\_internal\config.json" "dist\ɨ��С����\config.json" >nul
    echo [OK] �Ѹ��� config.json
)

echo.
echo ============================================
echo           �����ɣ�
echo ============================================
echo.
echo  ���Ŀ¼: %PROJECT_DIR%dist\ɨ��С����\
echo  ������:   ɨ��С����.exe
echo  �����ļ�: config.json (�ɱ༭)
echo  ��Ʒ����: products.csv (����Excel�༭)
echo.
echo  ʹ��˵��:
echo  1. ������ "ɨ��С����" �ļ��и��Ƶ�Ŀ�����
echo  2. ˫�� "ɨ��С����.exe" ���г���
echo  3. �� Excel �༭ products.csv ������Ʒ
echo  4. �޸� config.json ����ϵͳ����
echo.
echo  [ע��] �״�������Ҫ���������������绺�治������
echo.

pause
