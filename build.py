"""
打包脚本 - 自动复制配置文件
"""
import PyInstaller.__main__
import shutil
import os

print("开始打包...")

# 清理旧文件
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

# 运行打包
PyInstaller.__main__.run([
    "--clean",
    "--distpath", "dist",
    "--workpath", "build",
    "--name", "扫码小助手",
    "--windowed",
    "--add-data", "config.json;.",
    "--add-data", "products.csv;.",
    "--hidden-import", "pyttsx3",
    "--hidden-import", "pyttsx3.drivers",
    "--hidden-import", "pyttsx3.drivers.sapi5",
    "--hidden-import", "edge_tts",
    "--hidden-import", "pygame",
    "--hidden-import", "serial",
    "--hidden-import", "keyboard",
    "--hidden-import", "tkinter",
    "--hidden-import", "tkinter.ttk",
    "--collect-all", "edge_tts",
    "--collect-all", "components",
    "scanner_system.py",
])

# 复制语音缓存
if os.path.exists("voice_cache"):
    print("复制语音缓存...")
    if os.path.exists("dist\\扫码小助手\\voice_cache"):
        shutil.rmtree("dist\\扫码小助手\\voice_cache")
    shutil.copytree("voice_cache", "dist\\扫码小助手\\voice_cache")

# 复制配置文件到 exe 同目录
print("复制配置文件...")
internal_dir = "dist\\扫码小助手\\_internal"
exe_dir = "dist\\扫码小助手"

if os.path.exists(os.path.join(internal_dir, "products.csv")):
    shutil.copy(
        os.path.join(internal_dir, "products.csv"),
        os.path.join(exe_dir, "products.csv")
    )
    print("  - products.csv")

if os.path.exists(os.path.join(internal_dir, "config.json")):
    shutil.copy(
        os.path.join(internal_dir, "config.json"),
        os.path.join(exe_dir, "config.json")
    )
    print("  - config.json")

print("打包完成！")
print(f"输出目录: dist\\扫码小助手")
