import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'image_overlay_gui.py',
    '--name=WatermarkTool',
    '--windowed',  # 不显示控制台窗口
    '--onefile',   # 打包成单个文件
    '--icon=icon.ico',  # 设置图标
    '--noupx',  # 缩小文件体积？
    f'--distpath={os.path.join(current_dir, "dist")}',  # 输出目录
    f'--workpath={os.path.join(current_dir, "build")}',  # 工作目录
    '--clean',     # 清理临时文件
    '--add-data=icon.ico:.',  # 添加资源文件
])