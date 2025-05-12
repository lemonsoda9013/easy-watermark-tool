import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, ttk
from PIL import Image
import os
import json
import sys
import math
import platform
import threading
import numpy as np
import datetime

# 默认配置
DEFAULT_CONFIG = {
    "watermark_path": "",
    "output_dir": "output",
    "output_format": "JPG",
    "overlay_strength": 255,
    "language": "zh_CN"
}

# 翻译
TRANSLATIONS = {
    "zh_CN": {
        # General
        "title": "水印叠加工具",
        "error": "错误",
        "info": "提示",

        # Language Selection Messages
        "language_selection_info": "切换语言需要重启程序才能生效。\n是否立即保存配置并重启程序？",
        "language_selection_warning": "不能在处理过程中切换语言。",

        # Load Configuration Messages
        "cfg_load_failed": "配置加载失败：",
        "cfg_load_failed_no_permission": "配置加载失败：无读取权限",
        "cfg_load_failed_format_error": "配置加载失败：格式错误",

        # Clear Configuration Messages
        "cfg_clear_success": "配置清除成功：已恢复默认设置",
        "cfg_clear_failed": "配置清除失败：",

        # Save Configuration Messages
        "cfg_save_success": "配置保存成功：已保存到overlay_config.json",
        "cfg_save_failed": "配置保存失败：",
        "cfg_save_failed_no_permission": "配置保存失败：无写入权限",
        "cfg_save_failed_invalid_path": "配置保存失败：路径名包含不支持字符",

        # Start Processing Messages
        "no_watermark": "请选择PNG格式的水印",
        "no_selected_files": "请选择待处理文件",
        "no_output_dir": "请选择合适的输出目录",

        # Image Processing Messages
        "bad_output_dir": "无法创建输出目录",
        "process_failed": "处理失败：",
        "process_stopped": "处理已停止",
        "process_completed": "处理完成",

        # Image Parameter Adjustment Messages
        "invalid_strength_range": "强度必须在0-255之间",
        "invalid_strength_format": "请输入有效的数字",

        # Button Names
        "start_process_btn": "开始处理",
        "stop_process_btn": "停止处理",
        "save_config_btn": "保存配置",
        "clear_config_btn": "清除配置",
        "select_watermark_btn": "打开",
        "select_output_dir_btn": "打开",
        "select_files_btn": "打开文件",
        "select_all_btn": "全选",
        "invert_select_btn": "反选",
        "deselect_all_btn": "取消选择",
        "remove_selected_btn": "关闭文件",
        "output_dir_frame": "选择输出目录",
        "watermark_dir_frame": "选择水印图片",
        "copy_file_path": "复制文件地址",

        # Panel Names
        "control_frame": "操作面板",
        "settings_frame": "设置面板",
        "strength_frame": "强度",
        "format_frame": "格式",
        "file_frame": "图像输入",
        "result_frame": "图像输出"
    },
    "en_US": {
        # General
        "title": "Watermark Overlay Tool",
        "error": "Error",
        "info": "Info",

        # Language Selection Messages
        "language_selection_info": "Changing the language requires a restart. Save settings and restart now?",
        "language_selection_warning": "Cannot switch language during processing.",

        # Load Configuration Messages
        "cfg_load_failed": "Load failed",
        "cfg_load_failed_no_permission": "Load failed: No read permission",
        "cfg_load_failed_format_error": "Load failed: Format error",

        # Clear Configuration Messages
        "cfg_clear_success": "Clear successful: Default settings restored",
        "cfg_clear_failed": "Clear failed",

        # Save Configuration Messages
        "cfg_save_success": "Save successful: Saved to overlay_config.json",
        "cfg_save_failed": "Save failed",
        "cfg_save_failed_no_permission": "Save failed: No write permission",
        "cfg_save_failed_invalid_path": "Save failed: Path contains unsupported characters",

        # Start Processing Messages
        "no_watermark": "Please select a PNG format watermark",
        "no_selected_files": "Please select files to process",
        "no_output_dir": "Please select an output directory",

        # Image Processing Messages
        "bad_output_dir": "Cannot create output directory",
        "process_failed": "Process failed",
        "process_stopped": "Process stopped",
        "process_completed": "Process completed",

        # Image Parameter Adjustment Messages
        "invalid_strength_range": "Strength must be between 0-255",
        "invalid_strength_format": "Please enter a valid number",

        # Button Names
        "start_process_btn": "Start",
        "stop_process_btn": "Stop",
        "save_config_btn": "Save Conf",
        "clear_config_btn": "Clear Conf",
        "select_watermark_btn": "Open",
        "select_output_dir_btn": "Open",
        "select_files_btn": "Open",
        "select_all_btn": "Select All",
        "invert_select_btn": "Inv Selection",
        "deselect_all_btn": "Deselect All",
        "remove_selected_btn": "Close",
        "output_dir_frame": "Output Dir",
        "watermark_dir_frame": "Watermark",
        "copy_file_path": "Copy Path",

        # Panel Names
        "control_frame": "Control",
        "settings_frame": "Settings",
        "strength_frame": "Strength",
        "format_frame": "Format",
        "file_frame": "Image Input",
        "result_frame": "Image Output"
    }
}

# 启用高 DPI 感知（Windows）
if platform.system() == "Windows":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # 启用 Per-Monitor DPI 感知
    except Exception:
        pass  # 如果 ctypes 不可用，忽略

# 资源路径处理（支持PyInstaller打包）
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path)).replace('\\', '/')

def work_path(relative_path):
    if os.path.isabs(relative_path): # 如果是绝对路径 不变
        return relative_path.replace('\\', '/')
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path)).replace('\\', '/')


def validate_path_format(path, is_file=True, ends_with=[]):
    # 对路径进行格式检查
    try:
        # 检查路径是否为空
        if not path:
            return False
        # 检查路径是否包含非法字符
        invalid_chars = '<>"|?*'
        if any(char in path for char in invalid_chars):
            return False
        if is_file:
            # 检查文件是否存在且是指定类型文件
            return os.path.isfile(path) and any(path.lower().endswith(ext.lower()) for ext in ends_with)
        return True
    except:
        return False

# 图像叠加函数（包含平铺功能）
def overlay_images(base_path, overlay_path, output_dir, overlay_strength, output_format):
    try:
        base_img = Image.open(base_path).convert("RGBA")
        overlay_img = Image.open(overlay_path).convert("RGBA")
        
        # 检查尺寸是否一致
        if base_img.size != overlay_img.size:
            base_width, base_height = base_img.size
            overlay_width, overlay_height = overlay_img.size
            repeat_x = math.ceil(base_width / overlay_width)
            repeat_y = math.ceil(base_height / overlay_height)
            
            tiled_width = overlay_width * repeat_x
            tiled_height = overlay_height * repeat_y
            tiled_img = Image.new("RGBA", (tiled_width, tiled_height))
            
            for y in range(repeat_y):
                for x in range(repeat_x):
                    tiled_img.paste(overlay_img, (x * overlay_width, y * overlay_height))
            
            overlay_img = tiled_img.crop((0, 0, base_width, base_height))
        else:
            pass # overlay_img = overlay_img.resize(base_img.size, Image.LANCZOS) # 没有缩放的必要

        # 转换为 NumPy 数组进行处理 像素值归一化到[0,1]
        base_array = np.array(base_img) / 255.0
        overlay_array = np.array(overlay_img) / 255.0
        
        # 分离 alpha 通道
        base_rgb = base_array[..., :3]
        base_alpha = base_array[..., 3]
        overlay_rgb = overlay_array[..., :3]
        overlay_alpha = overlay_array[..., 3]
        
        # 计算混合强度
        strength = overlay_strength / 255.0
        alpha = overlay_alpha[..., np.newaxis] * strength
        
        # 应用混合模式
        mask = base_rgb <= 0.5
        result_rgb = np.where(mask,
                            2 * base_rgb * overlay_rgb,
                            1 - 2 * (1 - base_rgb) * (1 - overlay_rgb))
        
        # 应用 alpha 混合
        result_rgb = result_rgb * alpha + base_rgb * (1 - alpha)
        result_rgb = np.clip(result_rgb, 0, 1)
        
        # 重建 RGBA 图像 将像素值还原到[0,255]
        result_array = np.dstack((result_rgb, base_alpha))
        result_array = (result_array * 255).astype(np.uint8)
        result_img = Image.fromarray(result_array)
        
        # 保存结果
        base_name = os.path.splitext(os.path.basename(base_path))[0]
        output_ext = 'jpg' if output_format == 'JPG' else 'png'
        output_path = os.path.join(output_dir, f"{base_name}.{output_ext}")
        
        if output_format == 'JPG':
            result_img = result_img.convert("RGB")
            result_img.save(output_path, quality=95, subsampling=2)
        else:  # PNG
            result_img.save(output_path, format='PNG')
        
        return output_path
        
    except UnicodeEncodeError:
        raise Exception("Unicode Encode Error") # 路径名错误
    except UnicodeDecodeError:
        raise Exception("Unicode Decode Error") # 路径名错误
    except InterruptedError:
        raise InterruptedError("Interrupted Error") # 中断错误
    except Exception as e:
        raise Exception(f"Failed: {str(e)}") # 失败错误

# GUI应用程序类
class ImageOverlayApp:
    def __init__(self, root):
        # 从文件加载默认配置
        self.config_file = work_path("overlay_config.json")
        self.load_config()
        self.lang = TRANSLATIONS[self.current_language]
        
        # 初始化GUI
        self.root = root
        self.root.title(self.lang["title"])
        self.root.geometry("1200x600")
        self.root.iconbitmap(resource_path("icon.ico")) # 设置窗口图标
        
        # 启用 Tk 的高 DPI 缩放
        try:
            scaling = self.root.winfo_fpixels('1i') / 72
            self.root.tk.call('tk', 'scaling', scaling)
        except Exception:
            pass
        
        # 设置默认字体
        default_font = ("Microsoft YaHei UI", 10)
        self.root.option_add("*Font", default_font)

        # 停止处理标志 使用列表包装以允许线程修改
        self.stop_processing = [False]
        
        # 创建主布局      
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.minsize(600, 400)
        
        # 创建主框架
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # 创建左栏
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # 创建右栏
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # 更新布局 初始化UI
        self.root.update()
        self.setup_left_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        # 左栏-文件选择区域
        file_frame = tk.LabelFrame(self.left_frame, text=self.lang["file_frame"], padx=10, pady=5)
        file_frame.pack(fill=tk.BOTH, expand=True) # 填充可用空间
        
        # 左栏-文件选择区域-Listbox
        listbox_frame = tk.Frame(file_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5)) # 填充可用空间

        # 左栏-文件选择区域-Listbox-垂直滚动条
        v_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 左栏-文件选择区域-Listbox-水平滚动条
        h_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 左栏-文件选择区域-Listbox-多选列表框
        self.file_listbox = Listbox(
            listbox_frame, 
            selectmode=tk.MULTIPLE,  # 允许多选
            width=50,
            yscrollcommand=v_scrollbar.set,  # 绑定垂直滚动条
            xscrollcommand=h_scrollbar.set,  # 绑定水平滚动条
            exportselection=False  # 添加这个属性，防止选择状态被其他组件影响
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 配置滚动条与列表框的联动
        v_scrollbar.config(command=self.file_listbox.yview)
        h_scrollbar.config(command=self.file_listbox.xview)
        
        # 左栏-文件选择区域-按钮区域
        btn_frame = tk.Frame(file_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # 左栏-文件选择区域-按钮区域-文件操作按钮
        self.select_files_btn = tk.Button(btn_frame, text=self.lang["select_files_btn"], command=self.select_files)
        self.select_files_btn.pack(side=tk.LEFT, padx=5)
        self.select_all_btn = tk.Button(btn_frame, text=self.lang["select_all_btn"], command=self.select_all)
        self.select_all_btn.pack(side=tk.LEFT, padx=5)
        self.invert_select_btn = tk.Button(btn_frame, text=self.lang["invert_select_btn"], command=self.invert_selection)
        self.invert_select_btn.pack(side=tk.LEFT, padx=5)
        self.deselect_all_btn = tk.Button(btn_frame, text=self.lang["deselect_all_btn"], command=self.deselect_all)
        self.deselect_all_btn.pack(side=tk.LEFT, padx=5)
        self.remove_selected_btn = tk.Button(btn_frame, text=self.lang["remove_selected_btn"], command=self.remove_selected)
        self.remove_selected_btn.pack(side=tk.LEFT, padx=5)
    
        # 左栏-设置区域
        settings_frame = tk.LabelFrame(self.left_frame, text=self.lang["settings_frame"], padx=10, pady=5)
        settings_frame.pack(fill=tk.X, pady=(10, 0))
        settings_frame.pack_propagate(False)  # 禁止自动调整大小
        settings_frame.configure(height=120)  # 固定高度
    
        # 左栏-设置区域-选择水印
        watermark_dir_frame = tk.Frame(settings_frame)
        watermark_dir_frame.pack(fill=tk.X, pady=2)
        tk.Label(watermark_dir_frame, text=self.lang["watermark_dir_frame"]).pack(side=tk.LEFT)
        self.watermark_entry = tk.Entry(watermark_dir_frame)  # 水印路径输入框
        self.watermark_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.watermark_entry.insert(0, self.watermark_path)  # 设置默认值
        # self.watermark_entry.bind('<FocusOut>', self.update_watermark_path)  # 失去焦点时验证
        self.watermark_entry.bind('<Return>', self.update_watermark_path)    # 按回车时验证
        self.select_watermark_btn = tk.Button(watermark_dir_frame, text=self.lang["select_watermark_btn"], command=self.select_watermark) # 手动选择按钮
        self.select_watermark_btn.pack(side=tk.LEFT)

        # 左栏-设置区域-选择输出目录
        output_dir_frame = tk.Frame(settings_frame)
        output_dir_frame.pack(fill=tk.X, pady=2)
        tk.Label(output_dir_frame, text=self.lang["output_dir_frame"]).pack(side=tk.LEFT)
        self.output_entry = tk.Entry(output_dir_frame)  # 输出目录路径输入框
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.output_entry.insert(0, self.output_dir)  # 设置默认值
        # self.output_entry.bind('<FocusOut>', self.update_output_path)  # 失去焦点时验证
        self.output_entry.bind('<Return>', self.update_output_path)    # 按回车时验证
        self.select_output_dir_btn = tk.Button(output_dir_frame, text=self.lang["select_output_dir_btn"], command=self.select_output_dir) # 手动选择按钮
        self.select_output_dir_btn.pack(side=tk.LEFT)

    def setup_right_panel(self):
        # 右栏-处理结果区域
        result_frame = tk.LabelFrame(self.right_frame, text=self.lang["result_frame"], padx=10, pady=5)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 右栏-处理结果区域-Listbox
        listbox_frame = tk.Frame(result_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 右栏-处理结果区域-Listbox-垂直滚动条
        v_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右栏-处理结果区域-Listbox-水平滚动条
        h_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 右栏-处理结果区域-Listbox-结果列表框
        self.result_listbox = Listbox(
            listbox_frame, 
            width=50,
            yscrollcommand=v_scrollbar.set,  # 绑定垂直滚动条
            xscrollcommand=h_scrollbar.set   # 绑定水平滚动条
        )
        self.result_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 右栏-处理结果区域-Listbox-右键菜单
        self.result_menu = tk.Menu(self.result_listbox, tearoff=0)
        self.result_menu.add_command(label=self.lang["copy_file_path"], command=self.copy_selected_result(True))
        self.result_listbox.bind("<Button-3>", self.show_result_menu)
        
        # 配置滚动条与列表框的联动
        v_scrollbar.config(command=self.result_listbox.yview)
        h_scrollbar.config(command=self.result_listbox.xview)
        
        # 右栏-处理结果区域-操作行
        control_row = tk.Frame(result_frame)
        control_row.pack(fill=tk.X, pady=5)
        
        # 右栏-处理结果区域-操作行-格式选择
        format_frame = tk.Frame(control_row)
        format_frame.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(format_frame, text=self.lang["format_frame"]).pack(side=tk.LEFT)
        self.output_format_var = tk.StringVar(value=self.output_format)
        self.output_format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.output_format_var,
            values=["JPG", "PNG"],
            state="readonly",
            width=5
        )
        self.output_format_combo.pack(side=tk.LEFT, padx=(5, 0))
        # 绑定选择事件，防止文件栏的选择状态丢失
        # self.output_format_combo.bind('<<ComboboxSelected>>', lambda e: self.root.focus())
        
        # 右栏-处理结果区域-操作行-强度调节
        strength_frame = tk.Frame(control_row)
        strength_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 右栏-处理结果区域-操作行-强度调节-标签
        tk.Label(strength_frame, text=self.lang["strength_frame"]).pack(side=tk.LEFT)

        # 右栏-处理结果区域-操作行-强度调节-滑块
        self.strength_var = tk.DoubleVar(value=self.overlay_strength)
        self.strength_scale = tk.Scale(
            strength_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=self.strength_var,
            length=128,
            showvalue=False
        )
        self.strength_scale.pack(side=tk.LEFT, padx=5)

        # 右栏-处理结果区域-操作行-强度调节-强度数值输入框
        self.strength_entry = tk.Entry(strength_frame, width=5)
        self.strength_entry.pack(side=tk.LEFT)
        self.strength_entry.insert(0, str(int(self.overlay_strength)))  # 设置默认值
        
        # 绑定强度调节事件
        self.strength_scale.bind("<Motion>", self.update_strength_entry)
        self.strength_entry.bind("<Return>", self.update_strength_scale)
        
        # 右栏-操作面板区域
        control_frame = tk.LabelFrame(self.right_frame, text=self.lang["control_frame"], padx=10, pady=5)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        control_frame.pack_propagate(False)  # 禁止自动调整大小
        control_frame.configure(height=120)  # 固定高度
        
        # 右栏-操作面板区域-进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # 右栏-操作面板区域-按钮区域
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        self.start_process_btn = tk.Button(btn_frame, text=self.lang["start_process_btn"], command=self.process_images)
        self.start_process_btn.pack(side=tk.LEFT, padx=5)
        self.stop_process_btn = tk.Button(btn_frame, text=self.lang["stop_process_btn"], command=self.stop_process)
        self.stop_process_btn.pack(side=tk.LEFT, padx=5)
        self.save_config_btn = tk.Button(btn_frame, text=self.lang["save_config_btn"], command=self.save_config)
        self.save_config_btn.pack(side=tk.LEFT, padx=5)
        self.clear_config_btn = tk.Button(btn_frame, text=self.lang["clear_config_btn"], command=self.clear_config)
        self.clear_config_btn.pack(side=tk.LEFT, padx=5)
        # 添加语言选择下拉框
        self.language_var = tk.StringVar(value=self.current_language)
        self.language_combo = ttk.Combobox(
            btn_frame,
            textvariable=self.language_var,
            values=["zh_CN", "en_US"],
            state="readonly",
            width=5
        )
        self.language_combo.pack(side=tk.RIGHT, padx=5)
        self.language_combo.bind('<<ComboboxSelected>>', self.change_language)
        tk.Label(btn_frame, text="🌐").pack(side=tk.RIGHT, padx=(10, 0))

    def update_strength_entry(self, event=None):
        # 右栏操作 拖动滑块时更新强度数值输入框
        self.strength_entry.delete(0, tk.END)
        self.strength_entry.insert(0, str(int(self.strength_var.get())))

    def update_strength_scale(self, event=None):
        # 右栏操作 输入强度数值时更新滑块和输入框
        try:
            value = float(self.strength_entry.get())
            if 0 <= value <= 255:
                value = int(value) # 将value取整
                self.strength_var.set(value)
                self.strength_entry.delete(0, tk.END) # 更新输入框显示为整数
                self.strength_entry.insert(0, str(value))
            else:
                messagebox.showerror(self.lang["error"], self.lang["invalid_strength_range"])
                self.strength_entry.delete(0, tk.END)
                self.strength_entry.insert(0, str(int(self.strength_var.get())))
        except ValueError:
            messagebox.showerror(self.lang["error"], self.lang["invalid_strength_format"])
            self.strength_entry.delete(0, tk.END)
            self.strength_entry.insert(0, str(int(self.strength_var.get())))

    def show_result_menu(self, event):
        # 右栏操作 显示结果列表框的右键菜单
        try:
            # 获取鼠标点击位置对应的项目索引
            index = self.result_listbox.nearest(event.y)
            # 如果点击的位置有项目，则显示菜单
            if index >= 0:
                self.result_listbox.selection_clear(0, tk.END)
                self.result_listbox.selection_set(index)
                self.result_menu.post(event.x_root, event.y_root)
        except:
            pass

    def copy_selected_result(self, remove_timestamp=False):
        def _copy():
            try:
                # 获取选中的项目
                selection = self.result_listbox.get(self.result_listbox.curselection())
                # 如果需要去除时间戳
                if remove_timestamp:
                    selection = selection[11:]  # 跳过前11个字符 "[HH:MM:SS] "
                # 复制到剪贴板
                self.root.clipboard_clear()
                self.root.clipboard_append(selection)
                self.root.update()  # 刷新剪贴板
            except:
                pass
        return _copy

    def select_files(self):
        # 左栏操作 文件操作 打开文件
        files = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        for file in files:
            if file not in self.file_listbox.get(0, tk.END):  # 避免重复添加
                self.file_listbox.insert(tk.END, file)

    def select_all(self):
        # 左栏操作 文件操作 全选
        self.file_listbox.select_set(0, tk.END)

    def invert_selection(self):
        # 左栏操作 文件操作 反选
        for i in range(self.file_listbox.size()):
            if i in self.file_listbox.curselection():
                self.file_listbox.selection_clear(i)
            else:
                self.file_listbox.selection_set(i)

    def deselect_all(self):
        # 左栏操作 文件操作 取消选择
        self.file_listbox.selection_clear(0, tk.END)

    def remove_selected(self):
        # 左栏操作 文件操作 关闭文件
        selected = list(self.file_listbox.curselection())
        selected.reverse()  # 从后往前删除，避免索引变化
        for i in selected:
            self.file_listbox.delete(i)

    def select_watermark(self):
        # 左栏操作 选择水印图片
        file = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file:
            self.watermark_path = file
            self.watermark_entry.delete(0, tk.END)
            self.watermark_entry.insert(0, file)

    def select_output_dir(self):
        # 左栏操作 选择输出目录
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dir_path)

    def update_watermark_path(self, event=None):
        # 验证并更新水印路径
        path = self.watermark_entry.get()
        if validate_path_format(path, is_file=True, ends_with=[".png"]):
            self.watermark_path = work_path(path)
            return True
        else:
            # 恢复原值
            self.watermark_entry.delete(0, tk.END)
            self.watermark_entry.insert(0, self.watermark_path)
            messagebox.showerror(self.lang["error"], self.lang["no_watermark"])
            return False

    def update_output_path(self, event=None):
        # 验证并更新输出目录路径 不检查权限 只检查是否合法
        path = self.output_entry.get()
        if validate_path_format(path, is_file=False):
            self.output_dir = work_path(path) # 改绝对
            print(self.output_dir)
            return True
        else:
            # 恢复原值
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_dir)
            messagebox.showerror(self.lang["error"], self.lang["no_output_dir"])
            return False

    def stop_process(self):
        # 右栏操作 停止处理
        self.stop_processing[0] = True

    def toggle_ui_state(self, enable=True):
        # 切换UI状态 不想被锁定的UI不要加入到列表里
        state = tk.NORMAL if enable else tk.DISABLED
        components = [
            self.select_files_btn,
            self.select_all_btn,
            self.deselect_all_btn,
            self.select_watermark_btn,
            self.select_output_dir_btn,
            self.start_process_btn,
            self.save_config_btn,
            self.clear_config_btn,
            self.output_format_combo,
            self.strength_scale,
            self.strength_entry,
            self.watermark_entry,
            self.output_entry,
            self.file_listbox,
            self.language_combo
        ]
        for component in components:
            component.config(state=state)

    def process_images(self):
        # 右栏操作 开始处理
        if not self.update_output_path():
            return

        if not self.update_watermark_path():
            return

        selected_files = [self.file_listbox.get(i) for i in self.file_listbox.curselection()]
        if not selected_files:
            messagebox.showerror(self.lang["error"], self.lang["no_selected_files"])
            return
        
        output_dir = self.output_dir
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True) # 如果不存在就创建一个
            except Exception as e:
                messagebox.showerror(self.lang["error"], f"{self.lang['bad_output_dir']}\n{e}")
                return

        self.toggle_ui_state(False)
        self.stop_process_btn.config(state=tk.NORMAL)
        
        self.progress_var.set(0)
        # self.result_listbox.delete(0, tk.END) # 删除之前的结果
        self.stop_processing[0] = False
        
        processing_thread = threading.Thread(target=self.process_images_thread, args=(selected_files, output_dir))
        processing_thread.start()

    def process_images_thread(self, selected_files, output_dir):
        # 图像处理线程
        total_files = len(selected_files)
        
        for i, file in enumerate(selected_files):
            try:
                # 在处理文件前检查停止标志
                if self.stop_processing[0]:
                    self.root.after(0, lambda: self.finalize_processing(self.lang["process_stopped"]))
                    return

                # 处理文件
                output_path = overlay_images(
                    file,
                    self.watermark_path,
                    output_dir,
                    self.strength_var.get(),
                    self.output_format_var.get()
                ).replace("\\", "/")
                
                # 更新UI
                self.root.after(0, lambda p=output_path, idx=i: self.update_progress(idx, total_files, p))
                
                # 再次检查停止标志
                if self.stop_processing[0]:
                    self.root.after(0, lambda: self.finalize_processing(self.lang["process_stopped"]))
                    return
                    
            except InterruptedError:
                self.root.after(0, lambda: self.finalize_processing(self.lang["process_stopped"]))
                return
            
            except Exception as e:
                error_msg = f"{self.lang['process_failed']}{str(e)}" # error_msg = f"处理 {file} 失败: {str(e)}"
                self.root.after(0, lambda p=error_msg, idx=i: self.update_progress(idx, total_files, p)) # 更新UI
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(self.lang["error"], msg))
        
        # 处理完成
        if not self.stop_processing[0]:
            self.root.after(0, lambda: self.finalize_processing(self.lang["process_completed"]))

    def update_progress(self, index, total_files, output_path):
        # 处理图片的过程中更新ui

        # 更新进度条
        progress = ((index + 1) / total_files) * 100
        self.progress_var.set(progress)

        # 获取当前时间并格式化
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        # 更新结果列表
        self.result_listbox.insert(tk.END, f"[{current_time}] {output_path}") # 添加已处理项
        self.result_listbox.see(tk.END)  # 滚动到最新项

    def finalize_processing(self, message):
        # 处理已停止或已完成
        self.toggle_ui_state(True)
        self.stop_process_btn.config(state=tk.NORMAL)
        messagebox.showinfo(self.lang["info"], message)

    def save_config(self):
        # 右栏操作 保存配置
        # 获取当前配置
        try:
            strength_value = int(self.strength_entry.get())
            if 0 <= strength_value <= 255:
                self.overlay_strength = strength_value
            else:
                self.overlay_strength = 255
        except ValueError:
            self.overlay_strength = 255
            
        config = {
            "watermark_path": self.watermark_path,
            "output_dir": self.output_dir,
            "output_format": self.output_format_var.get(),
            "overlay_strength": self.overlay_strength,
            "language": self.current_language
        }

        # 写入配置文件
        try:
            # 如果配置文件不存在 会创建一个
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo(self.lang["info"], self.lang["cfg_save_success"])
        except PermissionError:
            messagebox.showerror(self.lang["error"], self.lang["cfg_save_failed_no_permission"])
        except UnicodeEncodeError:
            messagebox.showerror(self.lang["error"], self.lang["cfg_save_failed_invalid_path"])
        except Exception as e:
            messagebox.showerror(self.lang["error"], f"{self.lang['cfg_save_failed']}{str(e)}")

    def clear_config(self):
        # 右栏操作 清除配置
        try:
            # 清空配置文件 如果不存在会创建一个
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
            
            # 将配置恢复到默认 当前语言先不修改
            self.set_config({"language":self.current_language})

            # 将默认配置同步到UI
            self.watermark_entry.delete(0, tk.END)
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_dir)
            self.output_format_var.set(self.output_format)
            self.strength_var.set(self.overlay_strength)
            self.strength_entry.delete(0, tk.END)
            self.strength_entry.insert(0, str(self.overlay_strength))
            messagebox.showinfo(self.lang["info"], self.lang["cfg_clear_success"])
        
        except Exception as e:
            messagebox.showerror(self.lang["error"], f"{self.lang['cfg_clear_failed']}{str(e)}")
    
    def load_config(self):
        # 加载配置 打开程序时自动执行
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.set_config(config)
        except FileNotFoundError:
            self.set_config() # 配置文件不存在则使用默认配置
        except PermissionError:
            messagebox.showerror(self.lang["error"], self.lang["cfg_load_failed_no_permission"])
            self.set_config()    
        except json.JSONDecodeError:
            messagebox.showerror(self.lang["error"], self.lang["cfg_load_failed_format_error"])
            self.set_config()
        except Exception as e:
            messagebox.showerror(self.lang["error"], f"{self.lang['cfg_load_failed']}{str(e)}")
            self.set_config()

    def set_config(self, config=None):
        # 设置配置值,如果没有提供配置则使用默认配置
        if config is None:
            config = DEFAULT_CONFIG
        self.watermark_path = work_path(config.get("watermark_path", DEFAULT_CONFIG["watermark_path"]))
        self.output_dir = work_path(config.get("output_dir", DEFAULT_CONFIG["output_dir"]))
        self.output_format = config.get("output_format", DEFAULT_CONFIG["output_format"])
        self.overlay_strength = config.get("overlay_strength", DEFAULT_CONFIG["overlay_strength"])
        self.current_language = config.get("language", DEFAULT_CONFIG["language"])

    def change_language(self, event=None):
        new_language = self.language_var.get()
        
        # 如果选择的语言与当前语言不同
        if new_language != self.current_language:
            # 创建确认对话框
            result = messagebox.askyesno(
                TRANSLATIONS[new_language]["info"],
                TRANSLATIONS[new_language]["language_selection_info"]
            )
        
            if result:  # 用户点击"是"
                self.current_language = new_language
                if self.stop_processing[0]:
                    messagebox.showerror(TRANSLATIONS[new_language]["error"], TRANSLATIONS[new_language]["language_selection_warning"])
                    return
                self.save_config()  # 保存配置
                self.root.quit()    # 关闭程序
            else:  # 用户点击"否"
                self.language_var.set(self.current_language) # 恢复语言选择框为当前语言


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageOverlayApp(root)
    root.mainloop()