# -*- coding: utf-8 -*-
"""
GIF Maker GUI主窗口模�?这个模块实现了GIF制作工具的图形用户界面，包括图片选择、参数设置、预览和GIF生成功能�?"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入业务逻辑模块
from function.image_utils import load_image, crop_image, get_image_info, resize_image, create_photo_image, calculate_scale_to_fit, calculate_scale_to_fill
from function.history_manager import HistoryManager
from function.file_manager import get_image_files, validate_image_path, get_file_size_kb
from function.gif_operations import create_gif
from function.file_manager import calculate_total_time, validate_gif_params, estimate_gif_size


class GifMakerGUI:
    def __init__(self, root):
        """
        初始化GIF Maker GUI主窗�?
        Args:
            root: Tkinter根窗口对�?        """
        self.root = root
        self.root.title("GIF Maker")
        self.root.geometry("800x600")

        # 先隐藏窗口，防止闪烁
        self.root.withdraw()

        # 设置窗口最小和最大尺�?        self.root.minsize(1366, 768)
        self.root.maxsize(1920, 1080)

        # 设置窗口图标
        self.set_window_icon()

        # 定义实例变量
        self.image_paths = []  # 存储选中的图片路径列�?        self.output_path = tk.StringVar()  # 输出文件路径
        self.duration = tk.IntVar(value=100)  # GIF每帧持续时间，默�?00毫秒
        self.loop = tk.IntVar(value=0)  # 循环次数�?表示无限循环
        self.optimize = tk.BooleanVar(value=True)  # 是否优化GIF
        self.resize_width = tk.StringVar()  # 调整尺寸的宽�?        self.resize_height = tk.StringVar()  # 调整尺寸的高�?        self.current_photo = None  # 保存当前预览图片的PhotoImage对象，防止被垃圾回收
        self.preview_scale = 1.0  # 预览缩放比例
        self.preview_photos = []  # 保存网格预览的所有PhotoImage对象
        self.image_rects = []  # 保存网格预览中每张图片的位置信息
        self.selected_image_index = -1  # 当前选中的图片索�?        self.selected_image_indices = set()  # 多选的图片索引集合
        self.last_selected_index = -1  # 上次选中的图片索引（用于Shift多选）
        self.clipboard_images = []  # 剪贴板中的图片索引列�?        self.clipboard_action = None  # 剪贴板操作类型：'copy' �?'cut'

        # 撤销/重做相关
        self.history_manager = HistoryManager(max_history=50)  # 历史管理�?
        # 待保存的裁剪图片
        self.pending_crops = {}  # 字典：{图片路径: 裁剪后的PIL.Image对象}
        self.pending_crop_coords = {}  # 字典：{图片路径: 裁剪坐标 (x1, y1, x2, y2)}

        # 设置用户界面和菜�?        self.setup_ui()
        self.setup_menu()

        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_resize)

        # 绑定窗口关闭事件
        self.root.protocol('WM_DELETE_WINDOW', self.on_window_close)

        # 居中显示窗口（在UI初始化后�?        self.center_window()

    def save_pending_crops(self):
        """保存所有待保存的裁剪图�?""
        if not self.pending_crops:
            messagebox.showinfo("提示", "没有待保存的裁剪图片")
            return

        # 委托给业务逻辑模块执行批量保存
        from function.file_manager import batch_save_cropped_images
        saved_count, failed_count = batch_save_cropped_images(self.pending_crops)

        if saved_count > 0:
            self.pending_crops.clear()
            self.pending_crop_coords.clear()
            self.display_grid_preview()

            if failed_count > 0:
                messagebox.showwarning("保存完成", f"成功保存 {saved_count} 张图片，失败 {failed_count} 张图�?)
            else:
                messagebox.showinfo("保存完成", f"成功保存 {saved_count} 张裁剪图�?)
        else:
            messagebox.showerror("错误", "保存图片失败")

    def on_window_close(self):
        """窗口关闭事件处理"""
        # 检查是否有待保存的裁剪图片
        if self.pending_crops:
            result = messagebox.askyesnocancel(
                "保存更改",
                f"�?{len(self.pending_crops)} 张图片已裁剪但未保存。\n\n是否保存这些更改�?,
                icon=messagebox.WARNING
            )

            if result is True:  # 用户点击"�?
                # 保存所有待保存的裁剪图�?                for img_path, cropped_img in self.pending_crops.items():
                    try:
                        cropped_img.save(img_path)
                        print(f"已保存裁剪图�? {img_path}")
                    except Exception as e:
                        messagebox.showerror("错误", f"保存图片失败 {img_path}: {str(e)}")
                self.pending_crops.clear()
                self.root.destroy()
            elif result is False:  # 用户点击"�?
                # 不保存，直接关闭
                self.pending_crops.clear()
                self.root.destroy()
            # 如果 result is None，用户点击了"取消"，不关闭窗口
        else:
            # 没有待保存的更改，直接关�?            self.root.destroy()

    def set_window_icon(self):
        """
        设置窗口图标
        从项目icons目录中加载gif.png作为窗口图标
        """
        try:
            # 构建图标文件路径
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'gif.png')
            if os.path.exists(icon_path):
                # 设置窗口图标
                self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception:
            pass  # 如果图标设置失败，忽略错�?
    def on_window_resize(self, event):
        """
        窗口大小变化时的回调函数
        当窗口大小改变时，重新调整预览区域的布局
        """
        # 只处理窗口大小变化事件，忽略其他配置事件
        if event.widget == self.root and (event.width != getattr(self, '_last_width', 0) or event.height != getattr(self, '_last_height', 0)):
            # 记录当前窗口尺寸
            self._last_width = event.width
            self._last_height = event.height

            # 延迟执行，避免频繁调�?            if not hasattr(self, '_resize_timer'):
                self._resize_timer = None
            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(100, self.refresh_preview)

    def center_window(self):
        """
        将窗口居中显�?        计算屏幕中心坐标并将窗口移动到该位置
        """
        # 更新窗口信息
        self.root.update_idletasks()

        # 获取窗口当前尺寸
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # 计算居中位置
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)

        # 设置窗口位置
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # 显示窗口
        self.root.deiconify()
        self.root.update_idletasks()
    
    def setup_menu(self):
        """
        设置菜单�?        创建文件菜单和帮助菜单，并绑定相应的功能
        """
        # 创建菜单�?        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        from function.file_manager import select_images, select_directory
        file_menu.add_command(label="选择图片", command=lambda: select_images(self))
        file_menu.add_command(label="选择目录", command=lambda: select_directory(self))
        file_menu.add_separator()
        file_menu.add_command(label="设置输出文件...", command=self.browse_output, accelerator="Alt+O")
        file_menu.add_separator()
        file_menu.add_command(label="退�?, command=self.root.quit)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

        # 绑定快捷�?        from function.ui_operations import browse_output
        self.root.bind('<Alt-o>', lambda e: browse_output(self))

    def show_about(self):
        """
        显示关于对话�?        显示应用程序的基本信息和功能说明
        """
        messagebox.showinfo("关于", "GIF制作工具 v1.0\n\n将多张图片转换为GIF动画\n支持自定义持续时间、循环次数、尺寸调整等功能")

    def setup_ui(self):
        """
        设置用户界面
        创建并布局所有GUI组件，包括工具栏、参数设置区、预览区和状态栏
        """
        # 配置主窗口的行列权重，使其可以响应大小变�?        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 主框�?        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置主框架的权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)  # 让预览区域可扩展

        # 图片选择工具�?        image_frame = ttk.Frame(main_frame, padding="5")
        image_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # 创建工具提示函数
        btn_select_files = ttk.Button(image_frame, text="📁", command=lambda: select_images(self), width=5)
        btn_select_files.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_select_files, "选择图片文件")

        btn_select_dir = ttk.Button(image_frame, text="📂", command=lambda: select_directory(self), width=5)
        btn_select_dir.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_select_dir, "选择图片目录")

        # 文件下拉列表
        self.file_list_var = tk.StringVar()
        self.file_combobox = ttk.Combobox(
            image_frame,
            textvariable=self.file_list_var,
            state='readonly',
            width=20
        )
        self.file_combobox.pack(side=tk.LEFT, padx=(0, 5))
        from function.ui_operations import on_file_selected
        self.file_combobox.bind('<<ComboboxSelected>>', lambda e: on_file_selected(self, e))

        from function.history_manager import clear_images
        btn_clear_list = ttk.Button(image_frame, text="🗑�?, command=lambda: clear_images(self), width=5)
        btn_clear_list.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_clear_list, "清空列表")

        # 分隔�?        ttk.Separator(image_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 撤销/重做按钮
        btn_undo = ttk.Button(image_frame, text="↩️", command=self.undo, width=5)
        btn_undo.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_undo, "撤销 (Ctrl+Z)")

        btn_redo = ttk.Button(image_frame, text="↪️", command=self.redo, width=5)
        btn_redo.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_redo, "重做 (Ctrl+Y)")

        btn_save = ttk.Button(image_frame, text="💾", command=self.save_pending_crops, width=5)
        btn_save.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_save, "保存裁剪 (Ctrl+S)")

        # 分隔�?        ttk.Separator(image_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 控制按钮和缩放按�?        control_frame = ttk.Frame(image_frame)
        control_frame.pack(side=tk.LEFT, padx=(0, 0))

        btn_preview_gif = ttk.Button(control_frame, text="🎬", command=self.preview_gif, width=5)
        btn_preview_gif.pack(side=tk.LEFT, padx=(0, 3))
        self.create_tooltip(btn_preview_gif, "预览GIF")

        from function.gif_operations import create_gif_from_gui
        btn_create_gif = ttk.Button(control_frame, text="�?, command=lambda: create_gif_from_gui(self), width=5)
        btn_create_gif.pack(side=tk.LEFT, padx=(0, 3))
        self.create_tooltip(btn_create_gif, "生成GIF")

        # 分隔�?        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 预览缩放按钮
        from function.preview import zoom_in_preview, zoom_out_preview, reset_preview_zoom, fit_preview_to_window
        btn_zoom_out = ttk.Button(control_frame, text="🔍-", command=lambda: zoom_out_preview(self), width=5)
        btn_zoom_out.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_out, "缩小预览")

        btn_zoom_in = ttk.Button(control_frame, text="🔍+", command=lambda: zoom_in_preview(self), width=5)
        btn_zoom_in.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_in, "放大预览")


        btn_reset_zoom = ttk.Button(control_frame, text="🔄", command=lambda: reset_preview_zoom(self), width=5)
        btn_reset_zoom.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_reset_zoom, "重置缩放")

        btn_fit_window = ttk.Button(control_frame, text="�?, command=lambda: fit_preview_to_window(self), width=5)
        btn_fit_window.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_fit_window, "适应窗口")

        # 缩放倍数输入�?        self.zoom_entry = ttk.Entry(control_frame, width=4)
        self.zoom_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.zoom_entry.insert(0, "100")  # 默认值为100%
        from function.preview import apply_manual_zoom
        self.zoom_entry.bind('<Return>', lambda e: apply_manual_zoom(self, e))
        self.create_tooltip(self.zoom_entry, "输入缩放百分比，按回车确�?)

        # 添加%标签
        ttk.Label(control_frame, text="%").pack(side=tk.LEFT, padx=(0, 5))

        # GIF参数工具�?        param_frame = ttk.Frame(main_frame, padding="5")
        param_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # 持续时间
        ttk.Label(param_frame, text="每帧时间(ms):").pack(side=tk.LEFT, padx=(0, 5))
        duration_spin = ttk.Spinbox(param_frame, from_=100, to=10000, increment=100, textvariable=self.duration, width=5)
        duration_spin.pack(side=tk.LEFT, padx=(0, 10))

        # 循环次数
        ttk.Label(param_frame, text="循环次数(0=无限):").pack(side=tk.LEFT, padx=(0, 5))
        loop_spin = ttk.Spinbox(param_frame, from_=0, to=999, textvariable=self.loop, width=5)
        loop_spin.pack(side=tk.LEFT, padx=(0, 10))

        # 尺寸调整
        ttk.Label(param_frame, text="调整尺寸:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(param_frame, textvariable=self.resize_width, width=5).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Label(param_frame, text="x").pack(side=tk.LEFT, padx=(0, 3))
        ttk.Entry(param_frame, textvariable=self.resize_height, width=5).pack(side=tk.LEFT, padx=(3, 10))

        # 优化选项
        ttk.Checkbutton(param_frame, text="优化GIF", variable=self.optimize).pack(side=tk.LEFT)

        # 预览区域框架
        preview_outer_frame = ttk.LabelFrame(main_frame, text="图片预览", padding="1")
        preview_outer_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(1, 0))
        preview_outer_frame.columnconfigure(0, weight=1)
        preview_outer_frame.rowconfigure(0, weight=1)

        # 预览区域 - 使用Canvas和滚动条
        self.preview_frame = ttk.Frame(preview_outer_frame)
        self.preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)

        # 创建Canvas和滚动条
        self.preview_canvas = tk.Canvas(self.preview_frame, bg='white', highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.preview_canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.preview_canvas.xview)
        self.preview_canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # 布局Canvas和滚动条 - 使用Grid管理�?        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 直接在Canvas上显示图片，不使用额外的Frame容器
        self.preview_image_id = self.preview_canvas.create_image(0, 0, anchor=tk.CENTER, image=None)

        # 绑定事件以更新滚动区�?        from function.preview import on_preview_canvas_configure, on_preview_mousewheel
        self.preview_canvas.bind("<Configure>", lambda e: on_preview_canvas_configure(self, e))
        self.preview_canvas.bind("<MouseWheel>", lambda e: on_preview_mousewheel(self, e))  # Windows
        self.preview_canvas.bind("<Button-4>", lambda e: on_preview_mousewheel(self, e))   # Linux
        self.preview_canvas.bind("<Button-5>", lambda e: on_preview_mousewheel(self, e))   # Linux
        self.preview_canvas.bind("<Button-3>", self.on_preview_right_click)  # 右键点击
        self.root.bind("<Control-a>", self.select_all_images)  # Ctrl+A 全�?        from function.history_manager import undo, redo
        self.root.bind("<Control-z>", lambda e: undo(self))  # Ctrl+Z 撤销
        self.root.bind("<Control-y>", lambda e: redo(self))  # Ctrl+Y 重做
        self.root.bind("<Control-s>", lambda e: self.save_pending_crops())  # Ctrl+S 保存裁剪

        # 拖拽图片移动位置相关事件
        self.dragging_image_index = -1
        self.drag_source_index = -1
        self.drag_start_pos = None
        self.drag_preview_image = None
        self.drag_preview_photo = None  # 半透明预览图片
        self.insert_cursor = None  # 插入光标
        self.insert_index = -1  # 当前插入位置
        self.preview_canvas.bind("<ButtonPress-1>", self.on_preview_left_click)  # 左键点击
        self.preview_canvas.bind("<B1-Motion>", self.on_preview_drag)  # 左键拖拽
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_preview_release)  # 左键释放

        # 状态栏
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(1, 0))
        self.status_frame.columnconfigure(1, weight=1)

        # 总时间标�?        self.total_time_label = ttk.Label(self.status_frame, text="总时�? --", anchor=tk.W)
        self.total_time_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        # GIF总大小标�?        self.gif_size_label = ttk.Label(self.status_frame, text="GIF大小: --", anchor=tk.W)
        self.gif_size_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))

        # 当前图片大小标签
        self.current_img_size_label = ttk.Label(self.status_frame, text="当前图片: --", anchor=tk.W)
        self.current_img_size_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        # 缩放倍数标签
        self.zoom_label = ttk.Label(self.status_frame, text="缩放: 100%", anchor=tk.E)
        self.zoom_label.grid(row=0, column=3, sticky=tk.E, padx=(0, 5))

    def zoom_in_preview(self):
        """
        放大预览 - 对所有图片生�?        将预览图片的缩放比例增加25%
        """
        if self.preview_scale < 5.0:
            self.preview_scale *= 1.25
            self.display_grid_preview()

    def zoom_out_preview(self):
        """
        缩小预览 - 对所有图片生�?        将预览图片的缩放比例减少20%
        """
        if self.preview_scale > 0.1:
            self.preview_scale /= 1.25
            self.display_grid_preview()

    def reset_preview_zoom(self):
        """
        重置预览缩放 - 让每张图片按原图大小显示
        将预览缩放比例设置为1.0，所有图片按原始尺寸显示
        """
        if not self.image_paths:
            return

        # 设置缩放比例�?.0，按原图大小显示
        self.preview_scale = 1.0

        # 重新显示网格预览
        self.display_grid_preview()

    def fit_preview_to_window(self):
        """
        让预览图片适应窗口 - 对所有图片生�?        自动调整缩放比例，使所有图片完整显示在预览区域�?        """
        if not self.image_paths:
            return

        # 重置缩放比例�?.0，让网格预览自动计算合适的布局
        self.preview_scale = 1.0
        self.display_grid_preview()

    def apply_manual_zoom(self, event):
        """
        应用手动输入的缩放�?        从输入框获取缩放百分比并应用到预览图�?
        Args:
            event: 键盘事件对象
        """
        try:
            zoom_value = float(self.zoom_entry.get())
            if zoom_value <= 0:
                messagebox.showwarning("警告", "缩放值必须大�?")
                return

            # 将百分比转换为小�?            self.preview_scale = zoom_value / 100.0

            # 限制缩放范围
            if self.preview_scale < 0.1:  # 10%
                self.preview_scale = 0.1
                self.zoom_entry.delete(0, tk.END)
                self.zoom_entry.insert(0, "10")
            elif self.preview_scale > 5.0:  # 500%
                self.preview_scale = 5.0
                self.zoom_entry.delete(0, tk.END)
                self.zoom_entry.insert(0, "500")

            from function.preview import refresh_preview
            refresh_preview(self)
            from function.ui_operations import update_status_info
            update_status_info(self)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            # 恢复显示当前缩放�?            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, str(int(self.preview_scale * 100)))


    def on_preview_canvas_configure(self, event):
        """
        当预览canvas大小改变时更新窗口大�?        此方法用于处理Canvas尺寸变化事件

        Args:
            event: Canvas配置事件对象
        """
        # 仅当canvas大小改变时更新滚动区�?        pass  # 滚动区域由display_frame方法管理

    def on_preview_mousewheel(self, event):
        """
        处理预览区域的鼠标滚轮事�?        支持 Ctrl+滚轮缩放功能
        """
        # 检查是否按下了 Ctrl �?        ctrl_pressed = event.state & 0x4  # Ctrl 键的位掩�?
        if ctrl_pressed:
            # Ctrl+滚轮：缩放图�?            from function.preview import zoom_in_preview, zoom_out_preview
            if event.delta > 0 or event.num == 4:
                # 向上滚动：放�?                zoom_in_preview(self)
            elif event.delta < 0 or event.num == 5:
                # 向下滚动：缩�?                zoom_out_preview(self)
        else:
            # 普通滚轮：滚动查看
            # 检查滚动区域是否大于Canvas可视区域
            scrollregion = self.preview_canvas.cget("scrollregion")
            if scrollregion:
                parts = scrollregion.split()
                if len(parts) == 4:
                    scroll_width = float(parts[2])
                    scroll_height = float(parts[3])
                    canvas_width = self.preview_canvas.winfo_width()
                    canvas_height = self.preview_canvas.winfo_height()

                    # 如果图片的宽度或高度大于Canvas的可视区域，则允许滚�?                    if scroll_width > canvas_width or scroll_height > canvas_height:
                        # 检查操作系统类型来确定滚动方向
                        if event.num == 4 or event.delta > 0:
                            # 向上滚动
                            self.preview_canvas.yview_scroll(-1, "units")
                        elif event.num == 5 or event.delta < 0:
                            # 向下滚动
                            self.preview_canvas.yview_scroll(1, "units")

    def create_tooltip(self, widget, text):
        """
        创建鼠标悬浮提示
        为指定控件添加工具提示功�?
        Args:
            widget: 需要添加提示的控件对象
            text: 提示文本内容
        """
        def enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes("-topmost", True)  # 确保提示框在最顶层
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid",
                            borderwidth=1, font=("tahoma", "8", "normal"))
            label.pack()

            # 获取鼠标位置并显示提�?            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")

            # 将tooltip存储在widget属性中，以便后续清�?            widget._tooltip = tooltip

        def leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def preview_first_image(self):
        """
        预览第一张选中的图�?        显示图片列表中的第一张图片到预览区域
        """
        if not self.image_paths:
            messagebox.showwarning("提示", "请先选择图片")
            return

        from function.preview import refresh_preview
        refresh_preview(self)
        from function.ui_operations import update_status_info
        update_status_info(self)

    def preview_specific_image(self, index):
        """
        预览指定索引的图�?        显示图片列表中指定索引位置的图片到预览区�?
        Args:
            index: 图片在列表中的索�?        """
        if not self.image_paths or index < 0 or index >= len(self.image_paths):
            return

        try:
            # 打开指定图片
            img_path = self.image_paths[index]
            img = Image.open(img_path)

            # 获取图片原始尺寸
            orig_width, orig_height = img.size

            # 获取预览Canvas的实际尺�?            self.preview_canvas.update_idletasks()
            preview_width = self.preview_canvas.winfo_width() - 20
            preview_height = self.preview_canvas.winfo_height() - 20

            # 确保预览区域有合理的尺寸
            if preview_width < 50:
                preview_width = orig_width
            if preview_height < 50:
                preview_height = orig_height

            # 计算基础缩放比例，使图片适应预览区域（保持宽高比�?            base_scale = min(preview_width / orig_width, preview_height / orig_height)

            # 应用缩放比例：当preview_scale�?.0时，始终使用原始尺寸显示
            # 这样可以保证100%缩放时显示原始尺寸，即使图片大于窗口
            if self.preview_scale == 1.0:
                scale = 1.0  # 始终显示原始尺寸
            else:
                # 用户手动缩放时，基于原始尺寸进行缩放
                scale = self.preview_scale

            # 计算实际显示尺寸
            scaled_width = int(orig_width * scale)
            scaled_height = int(orig_height * scale)

            # 调整图片大小，根据缩放方向选择合适的插值算�?            if scale >= 1.0:
                resampling = Image.Resampling.LANCZOS
            else:
                resampling = Image.Resampling.BILINEAR
            img_resized = img.resize((scaled_width, scaled_height), resampling)

            # 将图片转换为Tkinter可用的PhotoImage对象
            self.current_photo = ImageTk.PhotoImage(img_resized)  # 保存引用

            # 先更新Canvas上的图片
            self.preview_canvas.itemconfig(self.preview_image_id, image=self.current_photo)

            # 更新Canvas上的图片位置和锚�?            # 当图片大于窗口时，将图片放置在左上角(0, 0)，方便滚动查�?            # 当图片小于窗口时，将图片居中显示
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            if scaled_width > canvas_width or scaled_height > canvas_height:
                # 图片大于窗口，放置在左上角（使用NW锚点�?                self.preview_canvas.itemconfig(self.preview_image_id, anchor=tk.NW)
                self.preview_canvas.coords(self.preview_image_id, 0, 0)
            else:
                # 图片小于窗口，居中显示（使用CENTER锚点�?                self.preview_canvas.itemconfig(self.preview_image_id, anchor=tk.CENTER)
                center_x = canvas_width // 2
                center_y = canvas_height // 2
                self.preview_canvas.coords(self.preview_image_id, center_x, center_y)

            # 更新滚动区域 - 确保滚动区域包含整个图片
            # 使用after确保在图片完全加载后更新滚动区域
            self.preview_canvas.after(10, lambda: self.preview_canvas.configure(scrollregion=(0, 0, scaled_width, scaled_height)))

        except Exception as e:
            messagebox.showerror("错误", f"无法预览图片: {str(e)}")

    def display_grid_preview(self):
        """
        以网格方式显示所有图�?        从上到下，从左到右排列，根据图片尺寸调节每列的图片数
        """
        if not self.image_paths:
            return

        # 委托给业务逻辑模块计算预览布局
        from function.image_utils import calculate_grid_layout
        layout_data = calculate_grid_layout(
            self.image_paths,
            self.pending_crops,
            self.preview_scale
        )

        if not layout_data:
            return

        # 清空预览区域
        self.preview_canvas.delete("all")
        self.image_rects.clear()  # 清空位置信息
        self.preview_photos.clear()  # 清空PhotoImage引用

        # 使用计算好的布局数据显示图片
        for item in layout_data:
            img_path = item['path']
            x, y = item['position']
            size = item['size']

            # 加载并缩放图�?            if img_path in self.pending_crops:
                img = self.pending_crops[img_path]
            else:
                img = load_image(img_path)

            if img:
                # 调整图片大小
                img_resized = resize_image(img, size[0], size[1])
                photo = create_photo_image(img_resized)
                self.preview_photos.append(photo)

                # 在Canvas上绘制图�?                self.preview_canvas.create_image(x, y, image=photo, anchor=tk.NW, tags=f"image_{item['index']}")

                # 记录图片位置信息
                rect = {
                    'index': item['index'],
                    'x1': x,
                    'y1': y,
                    'x2': x + size[0],
                    'y2': y + size[1],
                    'path': img_path
                }
                self.image_rects.append(rect)

                # 添加序号标签
                self.preview_canvas.create_text(
                    x + 5, y + 5,
                    text=f"#{item['index'] + 1}",
                    fill="white",
                    font=("Arial", 10, "bold"),
                    anchor=tk.NW,
                    tags=f"label_{item['index']}"
                )

                # 添加文件名标签（不带后缀�?                filename = os.path.splitext(os.path.basename(img_path))[0]
                max_filename_length = max(5, size[0] // 8)  # 每个字符�?像素
                if len(filename) > max_filename_length:
                    filename = filename[:max_filename_length - 3] + "..."

                font_size = max(7, min(10, size[1] // 15))

                self.preview_canvas.create_text(
                    x + size[0] - 5, y + 5,
                    text=filename,
                    fill="white",
                    font=("Arial", font_size),
                    anchor=tk.NE,
                    tags=f"filename_{item['index']}"
                )

        # 更新滚动区域
        if self.image_rects:
            max_x = max(r['x2'] for r in self.image_rects)
            max_y = max(r['y2'] for r in self.image_rects)
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            scroll_width = max(canvas_width, max_x + 10)
            scroll_height = max(max_y + 10, canvas_height)
            self.preview_canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))

    def draw_selection_box(self, index):
        """绘制选中框（单选）"""
        self.selected_image_indices = {index}
        self.draw_selection_boxes()

    def draw_selection_boxes(self):
        """处理预览区域点击事件"""
        # 检查点击了哪张图片
        click_x = self.preview_canvas.canvasx(event.x)
        click_y = self.preview_canvas.canvasy(event.y)

        for i, rect in enumerate(self.image_rects):
            if rect['x1'] <= click_x <= rect['x2'] and rect['y1'] <= click_y <= rect['y2']:
                # 检查是否按下了 Shift �?                shift_pressed = event.state & 0x1  # Shift 键的位掩�?                
                if shift_pressed and self.last_selected_index >= 0:
                    # Shift 多选：选中从上次选中到当前点击之间的所有图�?                    start = min(self.last_selected_index, i)
                    end = max(self.last_selected_index, i)
                    
                    # 如果 Ctrl 也按下了，则切换选择状�?                    ctrl_pressed = event.state & 0x4
                    if ctrl_pressed:
                        for idx in range(start, end + 1):
                            if idx in self.selected_image_indices:
                                self.selected_image_indices.remove(idx)
                            else:
                                self.selected_image_indices.add(idx)
                    else:
                        # 只有 Shift：替换为范围选择
                        self.selected_image_indices = set(range(start, end + 1))
                    
                    self.last_selected_index = i
                else:
                    # 普通点击：单�?                    ctrl_pressed = event.state & 0x4  # Ctrl 键的位掩�?                    if ctrl_pressed:
                        # Ctrl+点击：切换选择状�?                        if i in self.selected_image_indices:
                            self.selected_image_indices.remove(i)
                        else:
                            self.selected_image_indices.add(i)
                        self.last_selected_index = i
                    else:
                        # 普通点击：清除多选，只选中当前图片
                        self.selected_image_indices = {i}
                        self.last_selected_index = i
                
                self.selected_image_index = i
                self.file_combobox.current(i)
                self.draw_selection_boxes()
                from function.ui_operations import update_status_info
                update_status_info(self)
                break

    def on_preview_left_click(self, event):
        """处理预览区域左键点击事件，用于选择和拖拽图�?""
        # 检查点击了哪张图片
        click_x = self.preview_canvas.canvasx(event.x)
        click_y = self.preview_canvas.canvasy(event.y)

        for i, rect in enumerate(self.image_rects):
            if rect['x1'] <= click_x <= rect['x2'] and rect['y1'] <= click_y <= rect['y2']:
                # 检查是否按下了 Shift 键（用于多选）
                shift_pressed = event.state & 0x1  # Shift 键的位掩�?                ctrl_pressed = event.state & 0x4  # Ctrl 键的位掩�?
                if shift_pressed and self.last_selected_index >= 0:
                    # Shift 多选：选中从上次选中到当前点击之间的所有图�?                    start = min(self.last_selected_index, i)
                    end = max(self.last_selected_index, i)

                    if ctrl_pressed:
                        # Ctrl+Shift：切换选择状�?                        for idx in range(start, end + 1):
                            if idx in self.selected_image_indices:
                                self.selected_image_indices.remove(idx)
                            else:
                                self.selected_image_indices.add(idx)
                    else:
                        # 只有 Shift：替换为范围选择
                        self.selected_image_indices = set(range(start, end + 1))

                    self.last_selected_index = i
                elif ctrl_pressed:
                    # Ctrl+点击：切换选择状�?                    if i in self.selected_image_indices:
                        self.selected_image_indices.remove(i)
                    else:
                        self.selected_image_indices.add(i)
                    self.last_selected_index = i
                else:
                    # 普通点击：清除多选，只选中当前图片
                    self.selected_image_indices = {i}
                    self.last_selected_index = i

                self.selected_image_index = i
                self.file_combobox.current(i)

                # 开始拖拽（记录拖拽状态，但不立即创建预览�?                self.dragging_image_index = i
                self.drag_source_index = i
                self.drag_start_pos = (click_x, click_y)

                # 绘制选框
                self.draw_selection_boxes()
                from function.ui_operations import update_status_info
                update_status_info(self)

                return

        # 点击空白处，取消选择
        self.dragging_image_index = -1
        self.drag_source_index = -1
        self.selected_image_index = -1
        self.selected_image_indices = set()
        self.draw_selection_boxes()

    def create_drag_preview(self, x, y, image_index):
        """创建文件图标拖拽预览"""
        try:
            if image_index >= len(self.image_paths):
                return

            # 获取文件�?            filename = os.path.basename(self.image_paths[image_index])

            # 创建文件图标（使用文本模拟）
            icon_size = 40
            font_size = 10

            # 创建文件图标背景
            self.preview_canvas.create_rectangle(
                x - icon_size // 2, y - icon_size // 2,
                x + icon_size // 2, y + icon_size // 2,
                fill="#E0E0E0",
                outline="#666666",
                width=2,
                tags="drag_preview"
            )

            # 添加文件扩展名图�?            ext = os.path.splitext(filename)[1].upper()
            if ext in ['.JPG', '.JPEG', '.PNG', '.GIF', '.BMP']:
                icon_text = "🖼�?
            else:
                icon_text = "📄"

            self.preview_canvas.create_text(
                x, y - 5,
                text=icon_text,
                font=("Arial", 16),
                tags="drag_preview"
            )

            # 添加文件名（截断过长的文件名�?            max_name_length = 10
            display_name = filename
            if len(display_name) > max_name_length:
                display_name = display_name[:max_name_length - 3] + "..."

            self.preview_canvas.create_text(
                x, y + 15,
                text=display_name,
                font=("Arial", font_size),
                fill="#333333",
                tags="drag_preview"
            )

            # 置顶显示
            self.preview_canvas.tag_raise("drag_preview")

        except Exception as e:
            print(f"创建拖拽预览失败: {e}")

    def on_preview_drag(self, event):
        """处理预览区域拖拽事件"""
        if self.dragging_image_index < 0:
            return

        try:
            # 移动拖拽��览图�?            drag_x = self.preview_canvas.canvasx(event.x)
            drag_y = self.preview_canvas.canvasy(event.y)

            # 如果还没有创建拖拽预览，则创�?            if not self.preview_canvas.find_withtag("drag_preview"):
                self.create_drag_preview(drag_x, drag_y, self.dragging_image_index)
            else:
                # 移动文件图标预览
                items = self.preview_canvas.find_withtag("drag_preview")
                for item in items:
                    # 计算偏移�?                    coords = self.preview_canvas.coords(item)
                    if len(coords) == 4:  # 矩形
                        dx = drag_x - (coords[0] + coords[2]) / 2
                        dy = drag_y - (coords[1] + coords[2]) / 2
                        self.preview_canvas.move(item, dx, dy)
                    elif len(coords) == 2:  # ���?                        dx = drag_x - coords[0]
                        dy = drag_y - coords[1]
                        self.preview_canvas.move(item, dx, dy)

                self.preview_canvas.tag_raise("drag_preview")

            # 计算并显示插入光�?            self.update_insert_cursor(drag_x, drag_y)

        except Exception as e:
            print(f"拖拽失败: {e}")

    def update_insert_cursor(self, x, y):
        """更新插入光标位置（只显示垂直方向，确保两个文件之间只显示一个，光标在间隙正中心�?""
        try:
            # 删除旧的插入光标
            self.preview_canvas.delete("insert_cursor")

            # 计算插入位置
            insert_index = -1
            cursor_x1, cursor_y1, cursor_x2, cursor_y2 = 0, 0, 0, 0

            # 检查是否在某个图片�?            for i, rect in enumerate(self.image_rects):
                if i != self.dragging_image_index and rect['x1'] <= x <= rect['x2'] and rect['y1'] <= y <= rect['y2']:
                    # 在图片上，判断是插入到前面还���后�?                    center_x = (rect['x1'] + rect['x2']) / 2

                    if x < center_x:
                        insert_index = i
                        # 在图片左侧显示��直光标（在间隙正中心）
                        if i > 0:
                            # 计算与前一个文件的间隙中心
                            prev_rect = self.image_rects[i - 1]
                            gap_center = (prev_rect['x2'] + rect['x1']) / 2
                            cursor_x1 = gap_center - 2
                            cursor_x2 = gap_center + 2
                        else:
                            # 第一个文件，显示在左侧边�?                            cursor_x1 = rect['x1'] - 2
                            cursor_x2 = rect['x1'] + 2
                        cursor_y1 = rect['y1']
                        cursor_y2 = rect['y2']
                    else:
                        insert_index = i + 1
                        # 在图片右侧显示垂直光标（在间隙正中心�?                        if i < len(self.image_rects) - 1:
                            # 计算与后一个文件的间隙中心
                            next_rect = self.image_rects[i + 1]
                            gap_center = (rect['x2'] + next_rect['x1']) / 2
                            cursor_x1 = gap_center - 2
                            cursor_x2 = gap_center + 2
                        else:
                            # 最后一个文件，显示在右侧边�?                            cursor_x1 = rect['x2'] - 2
                            cursor_x2 = rect['x2'] + 2
                        cursor_y1 = rect['y1']
                        cursor_y2 = rect['y2']
                    break

            # 如果不在任何图片上，检查是否在两个图片之间
            if insert_index == -1:
                min_distance = float('inf')
                closest_index = -1
                closest_side = None  # 'left' �?'right'

                for i, rect in enumerate(self.image_rects):
                    # 检查是否在图片的左侧或右侧（只考虑水平方向�?                    if y >= rect['y1'] and y <= rect['y2']:
                        # 计算到图片左侧的距离
                        if x < rect['x1']:
                            distance = rect['x1'] - x
                            if distance < min_distance:
                                min_distance = distance
                                closest_index = i
                                closest_side = 'left'
                        # 计算到图片右侧的距离
                        elif x > rect['x2']:
                            distance = x - rect['x2']
                            if distance < min_distance:
                                min_distance = distance
                                closest_index = i + 1
                                closest_side = 'right'

                # 只在两个文件之间显示插入光标，光标在间隙正中�?                if closest_index >= 0 and closest_side == 'right':
                    # 如果在右侧，确保下一个位置有文件
                    if closest_index < len(self.image_rects):
                        insert_index = closest_index
                        # 计算间隙中心
                        current_rect = self.image_rects[closest_index - 1]
                        next_rect = self.image_rects[closest_index]
                        gap_center = (current_rect['x2'] + next_rect['x1']) / 2
                        cursor_x1 = gap_center - 2
                        cursor_x2 = gap_center + 2
                        cursor_y1 = current_rect['y1']
                        cursor_y2 = current_rect['y2']
                elif closest_index >= 0 and closest_side == 'left':
                    # 如果在左侧，确保不是第一个位�?                    if closest_index > 0:
                        insert_index = closest_index
                        # 计算间隙中心
                        prev_rect = self.image_rects[closest_index - 1]
                        current_rect = self.image_rects[closest_index]
                        gap_center = (prev_rect['x2'] + current_rect['x1']) / 2
                        cursor_x1 = gap_center - 2
                        cursor_x2 = gap_center + 2
                        cursor_y1 = current_rect['y1']
                        cursor_y2 = current_rect['y2']

            # 如果找到了插入位置，显示插入光标
            if insert_index >= 0:
                self.insert_index = insert_index
                # Word 样式的插入光标：实心竖线
                cursor_x = (cursor_x1 + cursor_x2) / 2
                self.preview_canvas.create_line(
                    cursor_x, cursor_y1, cursor_x, cursor_y2,
                    fill="#FF0000",
                    width=2,
                    tags="insert_cursor"
                )
                self.preview_canvas.tag_raise("insert_cursor")
            else:
                self.insert_index = -1

        except Exception as e:
            print(f"更新插入光标失败: {e}")

    def on_preview_release(self, event):
        """处理预览区域释放事件"""
        if self.dragging_image_index < 0:
            return

        try:
            # 使用计算好的插入位置
            if self.insert_index >= 0 and self.insert_index != self.drag_source_index:
                # 保存当前状�?                from function.history_manager import save_state
                save_state(self)

                # 调整插入索引（考虑源图片在目标位置之前或之后）
                if self.insert_index > self.drag_source_index:
                    adjusted_insert_index = self.insert_index - 1
                else:
                    adjusted_insert_index = self.insert_index

                # 移动图片到新位置
                source_path = self.image_paths.pop(self.drag_source_index)
                self.image_paths.insert(adjusted_insert_index, source_path)

                # 更新界面
                from function.ui_operations import update_image_list
                update_image_list(self)

        except Exception as e:
            print(f"释放失败: {e}")
        finally:
            # 清除拖拽预览和插入光�?            self.preview_canvas.delete("drag_preview")
            self.preview_canvas.delete("insert_cursor")

            # 重置拖拽状�?            self.dragging_image_index = -1
            self.drag_source_index = -1
            self.drag_start_pos = None
            self.drag_preview_image = None
            self.drag_preview_photo = None
            self.insert_index = -1

    def on_preview_right_click(self, event):
        """处理预览区域右键点击事件"""
        # 检查点击了哪张图片
        click_x = self.preview_canvas.canvasx(event.x)
        click_y = self.preview_canvas.canvasy(event.y)

        clicked_index = -1
        for i, rect in enumerate(self.image_rects):
            if rect['x1'] <= click_x <= rect['x2'] and rect['y1'] <= click_y <= rect['y2']:
                clicked_index = i
                break

        if clicked_index >= 0:
            # 如果点击的图片不在已选中的列表中，则更新当前选中索引
            if clicked_index not in self.selected_image_indices:
                self.selected_image_index = clicked_index
                self.file_combobox.current(clicked_index)
                self.draw_selection_boxes()
                from function.ui_operations import update_status_info
                update_status_info(self)

            # 显示右键菜单
            self.show_context_menu(event, clicked_index)

    def show_context_menu(self, event, index):
        """显示右键菜单"""
        if index < 0 or index >= len(self.image_paths):
            return

        context_menu = tk.Menu(self.root, tearoff=0)
        from function.ui_operations import enter_crop_mode
        from function.list_operations import show_image_properties, open_image_location, open_with_default_viewer, copy_images, cut_images, paste_images, delete_images
        context_menu.add_command(label="进入裁剪模���", command=lambda: enter_crop_mode(self))
        context_menu.add_separator()
        context_menu.add_command(label="复制", command=lambda: copy_images(self, index))
        context_menu.add_command(label="剪切", command=lambda: cut_images(self, index))
        context_menu.add_command(label="粘贴", command=lambda: paste_images(self, index))
        context_menu.add_separator()
        context_menu.add_command(label="删除", command=lambda: delete_images(self, index))
        context_menu.add_separator()
        context_menu.add_command(label="查看属�?, command=lambda: show_image_properties(self, index))
        context_menu.add_command(label="打开位置", command=lambda: open_image_location(self, index))
        context_menu.add_command(label="用默认浏览器打开", command=lambda: open_with_default_viewer(self, index))

        # 在鼠标位置显示菜�?        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def select_all_images(self, event=None):
        """全选所有图�?""
        from function.list_operations import select_all_images as ops_select_all_images
        ops_select_all_images(self, event)

    def draw_selection_boxes(self):
        """绘制选中框（支持多选）"""
        # 删除所有旧的选中�?        self.preview_canvas.delete("selection_box")
        
        # 为所有选中的图片绘制选中�?        for index in self.selected_image_indices:
            if 0 <= index < len(self.image_rects):
                rect = self.image_rects[index]
                self.preview_canvas.create_rectangle(
                    rect['x1'], rect['y1'], rect['x2'], rect['y2'],
                    outline="#0066FF",
                    width=5,
                    tags="selection_box"
                )

    


def run():
    """
    启动GIF Maker GUI应用
    创建主窗口并启动事件循环
    """
    root = tk.Tk()
    app = GifMakerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    run()
