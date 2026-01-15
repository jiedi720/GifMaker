# -*- coding: utf-8 -*-
"""
GIF Maker GUI主窗口模块
这个模块实现了GIF制作工具的图形用户界面，包括图片选择、参数设置、预览和GIF生成功能。
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


class GifMakerGUI:
    def __init__(self, root):
        """
        初始化GIF Maker GUI主窗口

        Args:
            root: Tkinter根窗口对象
        """
        self.root = root
        self.root.title("GIF Maker")
        self.root.geometry("800x600")

        # 先隐藏窗口，防止闪烁
        self.root.withdraw()

        # 设置窗口最小和最大尺寸
        self.root.minsize(1366, 768)
        self.root.maxsize(1920, 1080)

        # 设置窗口图标
        self.set_window_icon()

        # 定义实例变量
        self.image_paths = []  # 存储选中的图片路径列表
        self.output_path = tk.StringVar()  # 输出文件路径
        self.duration = tk.IntVar(value=100)  # GIF每帧持续时间，默认100毫秒
        self.loop = tk.IntVar(value=0)  # 循环次数，0表示无限循环
        self.optimize = tk.BooleanVar(value=True)  # 是否优化GIF
        self.resize_width = tk.StringVar()  # 调整尺寸的宽度
        self.resize_height = tk.StringVar()  # 调整尺寸的高度
        self.current_photo = None  # 保存当前预览图片的PhotoImage对象，防止被垃圾回收
        self.preview_scale = 1.0  # 预览缩放比例
        self.preview_photos = []  # 保存网格预览的所有PhotoImage对象
        self.image_rects = []  # 保存网格预览中每张图片的位置信息
        self.selected_image_index = -1  # 当前选中的图片索引
        self.selected_image_indices = set()  # 多选的图片索引集合
        self.last_selected_index = -1  # 上次选中的图片索引（用于Shift多选）
        self.clipboard_images = []  # 剪贴板中的图片索引列表
        self.clipboard_action = None  # 剪贴板操作类型：'copy' 或 'cut'

        # 撤销/重做相关
        self.undo_stack = []  # 撤销栈
        self.redo_stack = []  # 重做栈
        self.max_undo_steps = 50  # 最大撤销步数

        # 设置用户界面和菜单
        self.setup_ui()
        self.setup_menu()

        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_resize)

        # 居中显示窗口（在UI初始化后）
        self.center_window()
    
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
            pass  # 如果图标设置失败，忽略错误

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

            # 延迟执行，避免频繁调用
            if not hasattr(self, '_resize_timer'):
                self._resize_timer = None
            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(100, self.refresh_preview)

    def center_window(self):
        """
        将窗口居中显示
        计算屏幕中心坐标并将窗口移动到该位置
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
        设置菜单栏
        创建文件菜单和帮助菜单，并绑定相应的功能
        """
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="选择图片", command=self.select_images)
        file_menu.add_command(label="选择目录", command=self.select_directory)
        file_menu.add_separator()
        file_menu.add_command(label="设置输出文件...", command=self.browse_output, accelerator="Alt+O")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

        # 绑定快捷键
        self.root.bind('<Alt-o>', lambda e: self.browse_output())

    def show_about(self):
        """
        显示关于对话框
        显示应用程序的基本信息和功能说明
        """
        messagebox.showinfo("关于", "GIF制作工具 v1.0\n\n将多张图片转换为GIF动画\n支持自定义持续时间、循环次数、尺寸调整等功能")

    def setup_ui(self):
        """
        设置用户界面
        创建并布局所有GUI组件，包括工具栏、参数设置区、预览区和状态栏
        """
        # 配置主窗口的行列权重，使其可以响应大小变化
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置主框架的权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)  # 让预览区域可扩展

        # 图片选择工具栏
        image_frame = ttk.Frame(main_frame, padding="5")
        image_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # 创建工具提示函数
        btn_select_files = ttk.Button(image_frame, text="📁", command=self.select_images, width=5)
        btn_select_files.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_select_files, "选择图片文件")

        btn_select_dir = ttk.Button(image_frame, text="📂", command=self.select_directory, width=5)
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
        self.file_combobox.bind('<<ComboboxSelected>>', self.on_file_selected)

        btn_clear_list = ttk.Button(image_frame, text="🗑️", command=self.clear_images, width=5)
        btn_clear_list.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_clear_list, "清空列表")

        # 分隔线
        ttk.Separator(image_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 撤销/重做按钮
        btn_undo = ttk.Button(image_frame, text="↩️", command=self.undo, width=5)
        btn_undo.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_undo, "撤销 (Ctrl+Z)")

        btn_redo = ttk.Button(image_frame, text="↪️", command=self.redo, width=5)
        btn_redo.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_redo, "重做 (Ctrl+Y)")

        # 分隔线
        ttk.Separator(image_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 控制按钮和缩放按钮
        control_frame = ttk.Frame(image_frame)
        control_frame.pack(side=tk.LEFT, padx=(0, 0))

        btn_preview_gif = ttk.Button(control_frame, text="🎬", command=self.preview_gif, width=5)
        btn_preview_gif.pack(side=tk.LEFT, padx=(0, 3))
        self.create_tooltip(btn_preview_gif, "预览GIF")

        btn_create_gif = ttk.Button(control_frame, text="⚡", command=self.create_gif_from_gui, width=5)
        btn_create_gif.pack(side=tk.LEFT, padx=(0, 3))
        self.create_tooltip(btn_create_gif, "生成GIF")

        # 分隔线
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 预览缩放按钮
        btn_zoom_out = ttk.Button(control_frame, text="🔍-", command=self.zoom_out_preview, width=5)
        btn_zoom_out.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_out, "缩小预览")

        btn_zoom_in = ttk.Button(control_frame, text="🔍+", command=self.zoom_in_preview, width=5)
        btn_zoom_in.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_in, "放大预览")


        btn_reset_zoom = ttk.Button(control_frame, text="🔄", command=self.reset_preview_zoom, width=5)
        btn_reset_zoom.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_reset_zoom, "重置缩放")

        btn_fit_window = ttk.Button(control_frame, text="⛶", command=self.fit_preview_to_window, width=5)
        btn_fit_window.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_fit_window, "适应窗口")

        # 缩放倍数输入框
        self.zoom_entry = ttk.Entry(control_frame, width=4)
        self.zoom_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.zoom_entry.insert(0, "100")  # 默认值为100%
        self.zoom_entry.bind('<Return>', self.apply_manual_zoom)
        self.create_tooltip(self.zoom_entry, "输入缩放百分比，按回车确认")

        # 添加%标签
        ttk.Label(control_frame, text="%").pack(side=tk.LEFT, padx=(0, 5))

        # GIF参数工具栏
        param_frame = ttk.Frame(main_frame, padding="5")
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

        # 布局Canvas和滚动条 - 使用Grid管理器
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 直接在Canvas上显示图片，不使用额外的Frame容器
        self.preview_image_id = self.preview_canvas.create_image(0, 0, anchor=tk.CENTER, image=None)

        # 绑定事件以更新滚动区域
        self.preview_canvas.bind("<Configure>", self.on_preview_canvas_configure)
        self.preview_canvas.bind("<MouseWheel>", self.on_preview_mousewheel)  # Windows
        self.preview_canvas.bind("<Button-4>", self.on_preview_mousewheel)   # Linux
        self.preview_canvas.bind("<Button-5>", self.on_preview_mousewheel)   # Linux
        self.preview_canvas.bind("<Button-3>", self.on_preview_right_click)  # 右键点击
        self.root.bind("<Control-a>", self.select_all_images)  # Ctrl+A 全选
        self.root.bind("<Control-z>", lambda e: self.undo())  # Ctrl+Z 撤销
        self.root.bind("<Control-y>", lambda e: self.redo())  # Ctrl+Y 重做

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

        # 总时间标签
        self.total_time_label = ttk.Label(self.status_frame, text="总时间: --", anchor=tk.W)
        self.total_time_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        # GIF总大小标签
        self.gif_size_label = ttk.Label(self.status_frame, text="GIF大小: --", anchor=tk.W)
        self.gif_size_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))

        # 当前图片大小标签
        self.current_img_size_label = ttk.Label(self.status_frame, text="当前图片: --", anchor=tk.W)
        self.current_img_size_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        # 缩放倍数标签
        self.zoom_label = ttk.Label(self.status_frame, text="缩放: 100%", anchor=tk.E)
        self.zoom_label.grid(row=0, column=3, sticky=tk.E, padx=(0, 5))

    def select_images(self):
        """
        选择图片文件
        打开文件选择对话框，让用户选择要制作GIF的图片文件
        """
        # 打开文件选择对话框，支持多种图片格式
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )
        if files:
            # 避免重复添加文件
            for file in files:
                if file not in self.image_paths:
                    self.image_paths.append(file)
            self.update_image_list()

    def select_directory(self):
        """
        选择包含图片的目录
        打开目录选择对话框，自动获取目录中所有图片文件
        """
        # 打开目录选择对话框
        directory = filedialog.askdirectory(title="选择包含图片的目录")
        if directory:
            # 添加项目路径到系统路径，以便导入GifMaker模块
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from GifMaker import get_image_files
            # 获取目录中的所有图片文件
            image_files = get_image_files(directory)
            # 避免重复添加文件
            for file in image_files:
                if file not in self.image_paths:
                    self.image_paths.append(file)
            # 更新图片列表并显示网格预览
            self.update_image_list()

    def clear_images(self):
        """
        清空图片列表
        清除所有已选择的图片路径
        """
        # 保存当前状态
        self.save_state()

        self.image_paths = []
        # 清空多选
        self.selected_image_indices = set()
        self.selected_image_index = -1
        self.last_selected_index = -1
        self.update_image_list()

    def update_image_list(self):
        """
        更新图片列表下拉框
        将当前图片路径列表更新到下拉框中，并显示序号
        同时在预览区域以网格方式显示所有图片
        """
        # 清空多选
        self.selected_image_indices = set()
        self.selected_image_index = -1
        self.last_selected_index = -1
        
        # 更新下拉列表
        file_list = []
        for i, img_path in enumerate(self.image_paths, 1):
            file_list.append(f"#{i}: {os.path.basename(img_path)}")

        self.file_combobox['values'] = file_list
        if file_list:
            self.file_combobox.current(0)
            # 更新状态栏信息
            self.update_status_info()
            # 显示网格预览
            self.display_grid_preview()
        else:
            self.file_list_var.set('')
            # 清空状态栏信息
            self.current_img_size_label.config(text="当前图片: --")
            self.total_time_label.config(text="总时间: --")
            self.gif_size_label.config(text="GIF大小: --")
            # 清空预览区域
            self.preview_canvas.delete("all")

    def update_status_info(self):
        """
        更新状态栏信息，显示当前图片信息
        包括当前图片尺寸、文件大小、总时间估算和GIF大小估算
        """
        if self.image_paths:
            # 获取当前选中的图片路径
            current_selection = self.file_combobox.current()
            if current_selection >= 0 and current_selection < len(self.image_paths):
                img_path = self.image_paths[current_selection]

                try:
                    # 获取图片信息
                    img = Image.open(img_path)
                    width, height = img.size
                    size_kb = os.path.getsize(img_path) / 1024  # 文件大小，KB

                    # 显示当前图片大小
                    current_img_info = f"当前图片: {width}x{height}px | {size_kb:.2f}KB | {img.format}"
                    self.current_img_size_label.config(text=current_img_info)

                    # 计算并显示总时间
                    num_images = len(self.image_paths)
                    duration_ms = self.duration.get()
                    total_time_ms = num_images * duration_ms
                    total_time_s = total_time_ms / 1000
                    self.total_time_label.config(text=f"总时间: {total_time_s:.1f}s ({num_images}张 x {duration_ms}ms)")

                    # 计算并显示预估GIF大小
                    # 简单估算：GIF大小约为所有图片大小之和的一定比例（通常GIF压缩率较高）
                    total_original_size = sum(os.path.getsize(path)/1024 for path in self.image_paths)  # KB
                    estimated_gif_size = total_original_size * 0.3  # 估算为原始大小的30%
                    self.gif_size_label.config(text=f"GIF大小: {estimated_gif_size:.2f}KB")

                except Exception as e:
                    self.current_img_size_label.config(text="当前图片: 无法读取")
                    self.total_time_label.config(text="总时间: --")
                    self.gif_size_label.config(text="GIF大小: --")
            else:
                self.current_img_size_label.config(text="当前图片: --")
                self.total_time_label.config(text="总时间: --")
                self.gif_size_label.config(text="GIF大小: --")
        else:
            self.current_img_size_label.config(text="当前图片: --")
            self.total_time_label.config(text="总时间: --")
            self.gif_size_label.config(text="GIF大小: --")

        # 更新缩放倍数显示
        zoom_percent = int(self.preview_scale * 100)
        self.zoom_label.config(text=f"缩放: {zoom_percent}%")

    def zoom_in_preview(self):
        """
        放大预览 - 对所有图片生效
        将预览图片的缩放比例增加25%
        """
        if self.preview_scale < 5.0:
            # 先保存当前选中索引
            current_selection = self.selected_image_index

            self.preview_scale *= 1.25
            self.display_grid_preview()

            # 恢复选中索引
            self.selected_image_index = current_selection
            if current_selection >= 0 and current_selection < len(self.image_rects):
                self.draw_selection_box(current_selection)

    def zoom_out_preview(self):
        """
        缩小预览 - 对所有图片生效
        将预览图片的缩放比例减少20%
        """
        if self.preview_scale > 0.1:
            # 先保存当前选中索引
            current_selection = self.selected_image_index

            self.preview_scale /= 1.25
            self.display_grid_preview()

            # 恢复选中索引
            self.selected_image_index = current_selection
            if current_selection >= 0 and current_selection < len(self.image_rects):
                self.draw_selection_box(current_selection)

    def reset_preview_zoom(self):
        """
        重置预览缩放 - 让每张图片按原图大小显示
        将预览缩放比例设置为1.0，所有图片按原始尺寸显示
        """
        if not self.image_paths:
            return

        try:
            # 先保存当前选中索引
            current_selection = self.selected_image_index

            # 获取第一张图片的原始尺寸
            first_img = Image.open(self.image_paths[0])
            orig_width, orig_height = first_img.size

            # 设置缩放比例为1.0，按原图大小显示
            self.preview_scale = 1.0

            # 清空预览区域
            self.preview_canvas.delete("all")
            self.image_rects = []
            self.preview_photos = []

            # 获取预览Canvas的实际尺寸
            self.preview_canvas.update_idletasks()
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            # 显示所有图片（按原图大小）
            x = 10
            y = 10
            max_y = 0

            for i, img_path in enumerate(self.image_paths):
                try:
                    img = Image.open(img_path)
                    width, height = img.size

                    # 不缩放，直接使用原图大小
                    photo = ImageTk.PhotoImage(img)
                    self.preview_photos.append(photo)

                    # 在Canvas上绘制图片
                    self.preview_canvas.create_image(x, y, image=photo, anchor=tk.NW)

                    # 记录图片位置信息
                    self.image_rects.append({
                        'index': i,
                        'x1': x,
                        'y1': y,
                        'x2': x + width,
                        'y2': y + height,
                        'path': img_path
                    })

                    # 添加序号标签
                    self.preview_canvas.create_text(
                        x + 5, y + 5,
                        text=f"#{i + 1}",
                        fill="white",
                        font=("Arial", 10, "bold"),
                        anchor=tk.NW,
                        tags=f"label_{i}"
                    )

                    # 添加文件名标签（不带后缀）
                    filename = os.path.splitext(os.path.basename(img_path))[0]

                    # 根据图片宽度限制文件名长度
                    max_filename_length = max(5, width // 8)  # 每个字符约8像素
                    if len(filename) > max_filename_length:
                        filename = filename[:max_filename_length - 3] + "..."

                    # 根据图片大小调整字体大小
                    font_size = max(7, min(10, height // 15))

                    self.preview_canvas.create_text(
                        x + width - 5, y + 5,
                        text=filename,
                        fill="white",
                        font=("Arial", font_size),
                        anchor=tk.NE,
                        tags=f"filename_{i}"
                    )

                    # 更新位置（垂直排列）
                    y += height + 10
                    max_y = max(max_y, y)

                except Exception as e:
                    print(f"无法显示图片 {img_path}: {e}")
                    continue

            # 更新滚动区域
            scroll_width = max(canvas_width, max([r['x2'] for r in self.image_rects], default=0) + 10)
            scroll_height = max_y + 10
            self.preview_canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))

            # 恢复选中索引
            self.selected_image_index = current_selection
            if current_selection >= 0 and current_selection < len(self.image_rects):
                self.draw_selection_boxes()

        except Exception as e:
            messagebox.showerror("错误", f"重置缩放失败: {str(e)}")

    def fit_preview_to_window(self):
        """
        让预览图片适应窗口 - 对所有图片生效
        自动调整缩放比例，使所有图片完整显示在预览区域内
        """
        if not self.image_paths:
            return

        # 先保存当前选中索引
        current_selection = self.selected_image_index

        # 重置缩放比例为1.0，让网格预览自动计算合适的布局
        self.preview_scale = 1.0
        self.display_grid_preview()

        # 恢复选中索引
        self.selected_image_index = current_selection
        if current_selection >= 0 and current_selection < len(self.image_rects):
            self.draw_selection_boxes()

    def apply_manual_zoom(self, event):
        """
        应用手动输入的缩放值
        从输入框获取缩放百分比并应用到预览图片

        Args:
            event: 键盘事件对象
        """
        try:
            zoom_value = float(self.zoom_entry.get())
            if zoom_value <= 0:
                messagebox.showwarning("警告", "缩放值必须大于0")
                return

            # 将百分比转换为小数
            self.preview_scale = zoom_value / 100.0

            # 限制缩放范围
            if self.preview_scale < 0.1:  # 10%
                self.preview_scale = 0.1
                self.zoom_entry.delete(0, tk.END)
                self.zoom_entry.insert(0, "10")
            elif self.preview_scale > 5.0:  # 500%
                self.preview_scale = 5.0
                self.zoom_entry.delete(0, tk.END)
                self.zoom_entry.insert(0, "500")

            self.refresh_preview()
            self.update_status_info()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            # 恢复显示当前缩放值
            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, str(int(self.preview_scale * 100)))


    def on_preview_canvas_configure(self, event):
        """
        当预览canvas大小改变时更新窗口大小
        此方法用于处理Canvas尺寸变化事件

        Args:
            event: Canvas配置事件对象
        """
        # 仅当canvas大小改变时更新滚动区域
        pass  # 滚动区域由display_frame方法管理

    def on_preview_mousewheel(self, event):
        """
        处理预览区域的鼠标滚轮事件
        支持 Ctrl+滚轮缩放功能
        """
        # 检查是否按下了 Ctrl 键
        ctrl_pressed = event.state & 0x4  # Ctrl 键的位掩码

        if ctrl_pressed:
            # Ctrl+滚轮：缩放图片
            if event.delta > 0 or event.num == 4:
                # 向上滚动：放大
                self.zoom_in_preview()
            elif event.delta < 0 or event.num == 5:
                # 向下滚动：缩小
                self.zoom_out_preview()
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

                    # 如果图片的宽度或高度大于Canvas的可视区域，则允许滚动
                    if scroll_width > canvas_width or scroll_height > canvas_height:
                        # 检查操作系统类型来确定滚动方向
                        if event.num == 4 or event.delta > 0:
                            # 向上滚动
                            self.preview_canvas.yview_scroll(-1, "units")
                        elif event.num == 5 or event.delta < 0:
                            # 向下滚动
                            self.preview_canvas.yview_scroll(1, "units")

    def enter_crop_mode(self):
        """
        进入裁剪模式
        打开裁剪对话框，允许用户对当前图片进行裁剪操作
        """
        if not self.image_paths:
            messagebox.showwarning("提示", "请先选择图片")
            return

        try:
            from .crop import show_crop_dialog

            # 获取当前选中的图片路径和索引
            current_selection = self.file_combobox.current()
            if current_selection >= 0 and current_selection < len(self.image_paths):
                current_image_path = self.image_paths[current_selection]
                current_index = current_selection
            else:
                current_image_path = self.image_paths[0]
                current_index = 0

            # 显示裁剪对话框，传递当前图片路径、图片列表和当前索引
            result = show_crop_dialog(self.root, current_image_path, self.image_paths, current_index)

            if result:
                print(f"裁剪设置: {result}")
                # TODO: 根据裁剪设置处理图片
                messagebox.showinfo("裁剪", f"裁剪设置已应用:\nX: {result['start'][0]}, Y: {result['start'][1]}\n宽度: {result['end'][0]}, 高度: {result['end'][1]}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开裁剪对话框: {str(e)}")

    def create_tooltip(self, widget, text):
        """
        创建鼠标悬浮提示
        为指定控件添加工具提示功能

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

            # 获取鼠标位置并显示提示
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")

            # 将tooltip存储在widget属性中，以便后续清理
            widget._tooltip = tooltip

        def leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def on_file_selected(self, event):
        """
        下拉列表选择回调
        当用户在下拉列表中选择一个图片时触发此方法

        Args:
            event: 选择事件对象
        """
        selection = self.file_combobox.current()
        if selection >= 0 and selection < len(self.image_paths):
            # 单选模式：清除多选，只选中当前图片
            self.selected_image_indices = {selection}
            self.selected_image_index = selection
            self.last_selected_index = selection
            self.draw_selection_boxes()
            # 跳转到该图片位置
            self.scroll_to_image(selection)
            # 更新状态栏信息
            self.update_status_info()

    def scroll_to_image(self, index):
        """滚动到指定图片位置"""
        if index < 0 or index >= len(self.image_rects):
            return

        rect = self.image_rects[index]
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        # 计算滚动位置，使图片居中显示
        scroll_x = (rect['x1'] + rect['x2']) / 2 - canvas_width / 2
        scroll_y = (rect['y1'] + rect['y2']) / 2 - canvas_height / 2

        # 获取滚动区域
        scrollregion = self.preview_canvas.cget("scrollregion")
        if scrollregion:
            parts = scrollregion.split()
            if len(parts) == 4:
                max_x = float(parts[2]) - canvas_width
                max_y = float(parts[3]) - canvas_height

                # 限制滚动范围
                scroll_x = max(0, min(scroll_x, max_x))
                scroll_y = max(0, min(scroll_y, max_y))

                # 计算滚动比例
                scrollregion_width = float(parts[2])
                scrollregion_height = float(parts[3])
                x_ratio = scroll_x / scrollregion_width if scrollregion_width > 0 else 0
                y_ratio = scroll_y / scrollregion_height if scrollregion_height > 0 else 0

                # 执行滚动
                self.preview_canvas.xview_moveto(x_ratio)
                self.preview_canvas.yview_moveto(y_ratio)

    def browse_output(self):
        """
        浏览并设置输出文件路径
        打开文件保存对话框，让用户选择GIF输出路径
        """
        filename = filedialog.asksaveasfilename(
            title="保存GIF文件",
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)

    def create_gif_from_gui(self):
        """
        从GUI创建GIF
        根据用户设置的参数生成GIF文件
        """
        if not self.image_paths:
            messagebox.showerror("错误", "请先选择至少一张图片")
            return

        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出文件路径")
            return

        # 处理尺寸调整参数
        resize = None
        if self.resize_width.get() and self.resize_height.get():
            try:
                width = int(self.resize_width.get())
                height = int(self.resize_height.get())
                if width > 0 and height > 0:
                    resize = (width, height)
                else:
                    messagebox.showerror("错误", "尺寸参数必须大于0")
                    return
            except ValueError:
                messagebox.showerror("错误", "尺寸参数必须是数字")
                return

        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from GifMaker import create_gif
            # 创建GIF
            create_gif(
                image_paths=self.image_paths,
                output_path=self.output_path.get(),
                duration=self.duration.get(),
                loop=self.loop.get(),
                resize=resize,
                optimize=self.optimize.get()
            )

            messagebox.showinfo("成功", f"GIF已成功创建:\n{self.output_path.get()}")

        except Exception as e:
            messagebox.showerror("错误", f"创建GIF失败:\n{str(e)}")

    def preview_first_image(self):
        """
        预览第一张选中的图片
        显示图片列表中的第一张图片到预览区域
        """
        if not self.image_paths:
            messagebox.showwarning("提示", "请先选择图片")
            return

        self.refresh_preview()
        self.update_status_info()

    def preview_specific_image(self, index):
        """
        预览指定索引的图片
        显示图片列表中指定索引位置的图片到预览区域

        Args:
            index: 图片在列表中的索引
        """
        if not self.image_paths or index < 0 or index >= len(self.image_paths):
            return

        try:
            # 打开指定图片
            img_path = self.image_paths[index]
            img = Image.open(img_path)

            # 获取图片原始尺寸
            orig_width, orig_height = img.size

            # 获取预览Canvas的实际尺寸
            self.preview_canvas.update_idletasks()
            preview_width = self.preview_canvas.winfo_width() - 20
            preview_height = self.preview_canvas.winfo_height() - 20

            # 确保预览区域有合理的尺寸
            if preview_width < 50:
                preview_width = orig_width
            if preview_height < 50:
                preview_height = orig_height

            # 计算基础缩放比例，使图片适应预览区域（保持宽高比）
            base_scale = min(preview_width / orig_width, preview_height / orig_height)

            # 应用缩放比例：当preview_scale为1.0时，始终使用原始尺寸显示
            # 这样可以保证100%缩放时显示原始尺寸，即使图片大于窗口
            if self.preview_scale == 1.0:
                scale = 1.0  # 始终显示原始尺寸
            else:
                # 用户手动缩放时，基于原始尺寸进行缩放
                scale = self.preview_scale

            # 计算实际显示尺寸
            scaled_width = int(orig_width * scale)
            scaled_height = int(orig_height * scale)

            # 调整图片大小，根据缩放方向选择合适的插值算法
            if scale >= 1.0:
                resampling = Image.Resampling.LANCZOS
            else:
                resampling = Image.Resampling.BILINEAR
            img_resized = img.resize((scaled_width, scaled_height), resampling)

            # 将图片转换为Tkinter可用的PhotoImage对象
            self.current_photo = ImageTk.PhotoImage(img_resized)  # 保存引用

            # 先更新Canvas上的图片
            self.preview_canvas.itemconfig(self.preview_image_id, image=self.current_photo)

            # 更新Canvas上的图片位置和锚点
            # 当图片大于窗口时，将图片放置在左上角(0, 0)，方便滚动查看
            # 当图片小于窗口时，将图片居中显示
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            if scaled_width > canvas_width or scaled_height > canvas_height:
                # 图片大于窗口，放置在左上角（使用NW锚点）
                self.preview_canvas.itemconfig(self.preview_image_id, anchor=tk.NW)
                self.preview_canvas.coords(self.preview_image_id, 0, 0)
            else:
                # 图片小于窗口，居中显示（使用CENTER锚点）
                self.preview_canvas.itemconfig(self.preview_image_id, anchor=tk.CENTER)
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
        以网格方式显示所有图片
        从上到下，从左到右排列，根据图片尺寸调节每列的图片数
        """
        if not self.image_paths:
            return

        try:
            # 先保存当前选中索引
            current_selection = self.selected_image_index

            # 清空预览区域
            self.preview_canvas.delete("all")
            self.image_rects = []  # 清空位置信息
            self.preview_photos = []  # 清空PhotoImage引用

            # 获取预览Canvas的实际尺寸
            self.preview_canvas.update_idletasks()
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            if canvas_width < 100:
                canvas_width = 800
            if canvas_height < 100:
                canvas_height = 600

            # 加载所有图片并获取尺寸
            images = []
            max_width = 0
            max_height = 0

            for img_path in self.image_paths:
                try:
                    img = Image.open(img_path)
                    width, height = img.size
                    images.append({
                        'path': img_path,
                        'original': img,
                        'width': width,
                        'height': height
                    })
                    max_width = max(max_width, width)
                    max_height = max(max_height, height)
                except Exception as e:
                    print(f"无法加载图片 {img_path}: {e}")
                    continue

            if not images:
                return

            # 计算合适的缩放比例和列数
            # 假设每张图片缩放后高度不超过200像素（考虑全局缩放比例）
            target_height = 200 * self.preview_scale
            scale = target_height / max_height

            # 缩放后的图片尺寸
            scaled_width = int(max_width * scale)
            scaled_height = int(max_height * scale)

            # 计算每行可以放多少张图片（考虑间距）
            padding = 10
            cols = max(1, (canvas_width - padding) // (scaled_width + padding))

            # 调整缩放比例以更好地适应屏幕
            if cols > 1:
                available_width = canvas_width - (cols + 1) * padding
                scale = available_width / (cols * max_width)
                scaled_width = int(max_width * scale)
                scaled_height = int(max_height * scale)

            # 显示图片
            x = padding
            y = padding
            row_height = 0

            self.preview_photos = []  # 保存PhotoImage引用
            self.image_rects = []  # 保存位置信息

            for i, img_info in enumerate(images):
                try:
                    # 为每张图片单独计算缩放尺寸
                    img = img_info['original']
                    orig_width, orig_height = img_info['width'], img_info['height']

                    # 计算缩放后的尺寸
                    img_scaled_width = int(orig_width * scale)
                    img_scaled_height = int(orig_height * scale)

                    # 缩放图片
                    if scale >= 1.0:
                        resampling = Image.Resampling.LANCZOS
                    else:
                        resampling = Image.Resampling.BILINEAR
                    img_resized = img.resize((img_scaled_width, img_scaled_height), resampling)

                    # 转换为PhotoImage
                    photo = ImageTk.PhotoImage(img_resized)
                    self.preview_photos.append(photo)

                    # 在Canvas上绘制图片
                    self.preview_canvas.create_image(x, y, image=photo, anchor=tk.NW, tags=f"image_{i}")

                    # 记录图片位置信息
                    self.image_rects.append({
                        'index': i,
                        'x1': x,
                        'y1': y,
                        'x2': x + img_scaled_width,
                        'y2': y + img_scaled_height,
                        'path': img_info['path']
                    })

                    # 添加序号标签
                    self.preview_canvas.create_text(
                        x + 5, y + 5,
                        text=f"#{i + 1}",
                        fill="white",
                        font=("Arial", 10, "bold"),
                        anchor=tk.NW,
                        tags=f"label_{i}"
                    )

                    # 添加文件名标签（不带后缀）
                    filename = os.path.splitext(os.path.basename(img_info['path']))[0]

                    # 根据图片宽度限制文件名长度
                    max_filename_length = max(5, img_scaled_width // 8)  # 每个字符约8像素
                    if len(filename) > max_filename_length:
                        filename = filename[:max_filename_length - 3] + "..."

                    # 根据图片大小调整字体大小
                    font_size = max(7, min(10, img_scaled_height // 15))

                    self.preview_canvas.create_text(
                        x + img_scaled_width - 5, y + 5,
                        text=filename,
                        fill="white",
                        font=("Arial", font_size),
                        anchor=tk.NE,
                        tags=f"filename_{i}"
                    )

                    # 更新位置
                    x += img_scaled_width + padding
                    row_height = max(row_height, img_scaled_height)

                    # 换行
                    if (i + 1) % cols == 0:
                        x = padding
                        y += row_height + padding
                        row_height = 0

                except Exception as e:
                    print(f"无法显示图片 {img_info['path']}: {e}")
                    continue

            # 更新滚动区域
            # 获取最后一行图片的位置
            if self.image_rects:
                last_rect = self.image_rects[-1]
                scroll_width = max(canvas_width, last_rect['x2'] + padding)
                scroll_height = last_rect['y2'] + padding
            else:
                scroll_width = canvas_width
                scroll_height = canvas_height

            self.preview_canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))

            # 检查是否需要水平滚动条
            if scroll_width <= canvas_width:
                # 不需要水平滚动，隐藏水平滚动条
                self.scroll_x.grid_forget()
            else:
                # 需要水平滚动，显示水平滚动条
                self.scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

            # 绘制选中框
            if current_selection >= 0 and current_selection < len(self.image_rects):
                self.selected_image_index = current_selection
                self.draw_selection_boxes()

        except Exception as e:
            print(f"网格预览失败: {e}")

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
                # 检查是否按下了 Shift 键
                shift_pressed = event.state & 0x1  # Shift 键的位掩码
                
                if shift_pressed and self.last_selected_index >= 0:
                    # Shift 多选：选中从上次选中到当前点击之间的所有图片
                    start = min(self.last_selected_index, i)
                    end = max(self.last_selected_index, i)
                    
                    # 如果 Ctrl 也按下了，则切换选择状态
                    ctrl_pressed = event.state & 0x4
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
                    # 普通点击：单选
                    ctrl_pressed = event.state & 0x4  # Ctrl 键的位掩码
                    if ctrl_pressed:
                        # Ctrl+点击：切换选择状态
                        if i in self.selected_image_indices:
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
                self.update_status_info()
                break

    def on_preview_left_click(self, event):
        """处理预览区域左键点击事件，用于选择和拖拽图片"""
        # 检查点击了哪张图片
        click_x = self.preview_canvas.canvasx(event.x)
        click_y = self.preview_canvas.canvasy(event.y)

        for i, rect in enumerate(self.image_rects):
            if rect['x1'] <= click_x <= rect['x2'] and rect['y1'] <= click_y <= rect['y2']:
                # 检查是否按下了 Shift 键（用于多选）
                shift_pressed = event.state & 0x1  # Shift 键的位掩码
                ctrl_pressed = event.state & 0x4  # Ctrl 键的位掩码

                if shift_pressed and self.last_selected_index >= 0:
                    # Shift 多选：选中从上次选中到当前点击之间的所有图片
                    start = min(self.last_selected_index, i)
                    end = max(self.last_selected_index, i)

                    if ctrl_pressed:
                        # Ctrl+Shift：切换选择状态
                        for idx in range(start, end + 1):
                            if idx in self.selected_image_indices:
                                self.selected_image_indices.remove(idx)
                            else:
                                self.selected_image_indices.add(idx)
                    else:
                        # 只有 Shift：替换为范围选择
                        self.selected_image_indices = set(range(start, end + 1))

                    self.last_selected_index = i
                elif ctrl_pressed:
                    # Ctrl+点击：切换选择状态
                    if i in self.selected_image_indices:
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

                # 开始拖拽（记录拖拽状态，但不立即创建预览）
                self.dragging_image_index = i
                self.drag_source_index = i
                self.drag_start_pos = (click_x, click_y)

                # 绘制选框
                self.draw_selection_boxes()
                self.update_status_info()

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

            # 获取文件名
            filename = os.path.basename(self.image_paths[image_index])

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

            # 添加文件扩展名图标
            ext = os.path.splitext(filename)[1].upper()
            if ext in ['.JPG', '.JPEG', '.PNG', '.GIF', '.BMP']:
                icon_text = "🖼️"
            else:
                icon_text = "📄"

            self.preview_canvas.create_text(
                x, y - 5,
                text=icon_text,
                font=("Arial", 16),
                tags="drag_preview"
            )

            # 添加文件名（截断过长的文件名）
            max_name_length = 10
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
            # 移动拖拽预览图片
            drag_x = self.preview_canvas.canvasx(event.x)
            drag_y = self.preview_canvas.canvasy(event.y)

            # 如果还没有创建拖拽预览，则创建
            if not self.preview_canvas.find_withtag("drag_preview"):
                self.create_drag_preview(drag_x, drag_y, self.dragging_image_index)
            else:
                # 移动文件图标预览
                items = self.preview_canvas.find_withtag("drag_preview")
                for item in items:
                    # 计算偏移量
                    coords = self.preview_canvas.coords(item)
                    if len(coords) == 4:  # 矩形
                        dx = drag_x - (coords[0] + coords[2]) / 2
                        dy = drag_y - (coords[1] + coords[2]) / 2
                        self.preview_canvas.move(item, dx, dy)
                    elif len(coords) == 2:  # 文本
                        dx = drag_x - coords[0]
                        dy = drag_y - coords[1]
                        self.preview_canvas.move(item, dx, dy)

                self.preview_canvas.tag_raise("drag_preview")

            # 计算并显示插入光标
            self.update_insert_cursor(drag_x, drag_y)

        except Exception as e:
            print(f"拖拽失败: {e}")

    def update_insert_cursor(self, x, y):
        """更新插入光标位置（只显示垂直方向，确保两个文件之间只显示一个）"""
        try:
            # 删除旧的插入光标
            self.preview_canvas.delete("insert_cursor")

            # 计算插入位置
            insert_index = -1
            cursor_x1, cursor_y1, cursor_x2, cursor_y2 = 0, 0, 0, 0

            # 检查是否在某个图片上
            for i, rect in enumerate(self.image_rects):
                if i != self.dragging_image_index and rect['x1'] <= x <= rect['x2'] and rect['y1'] <= y <= rect['y2']:
                    # 在图片上，判断是插入到前面还是后面
                    center_x = (rect['x1'] + rect['x2']) / 2

                    if x < center_x:
                        insert_index = i
                        # 在图片左侧显示垂直光标
                        cursor_x1 = rect['x1'] - 2
                        cursor_y1 = rect['y1']
                        cursor_x2 = rect['x1'] + 2
                        cursor_y2 = rect['y2']
                    else:
                        insert_index = i + 1
                        # 在图片右侧显示垂直光标
                        cursor_x1 = rect['x2'] - 2
                        cursor_y1 = rect['y1']
                        cursor_x2 = rect['x2'] + 2
                        cursor_y2 = rect['y2']
                    break

            # 如果不在任何图片上，检查是否在两个图片之间
            if insert_index == -1:
                min_distance = float('inf')
                closest_index = -1
                closest_side = None  # 'left' 或 'right'

                for i, rect in enumerate(self.image_rects):
                    # 检查是否在图片的左侧或右侧（只考虑水平方向）
                    if y >= rect['y1'] and y <= rect['y2']:
                        # 计算到图片左侧的距离
                        if x < rect['x1']:
                            distance = rect['x1'] - x
                            if distance < min_distance:
                                min_distance = distance
                                closest_index = i
                                closest_side = 'left'
                                cursor_x1 = rect['x1'] - 2
                                cursor_y1 = rect['y1']
                                cursor_x2 = rect['x1'] + 2
                                cursor_y2 = rect['y2']
                        # 计算到图片右侧的距离
                        elif x > rect['x2']:
                            distance = x - rect['x2']
                            if distance < min_distance:
                                min_distance = distance
                                closest_index = i + 1
                                closest_side = 'right'
                                cursor_x1 = rect['x2'] - 2
                                cursor_y1 = rect['y1']
                                cursor_x2 = rect['x2'] + 2
                                cursor_y2 = rect['y2']

                # 只在两个文件之间显示插入光标
                if closest_index >= 0 and closest_side == 'right':
                    # 如果在右侧，确保下一个位置有文件
                    if closest_index < len(self.image_rects):
                        insert_index = closest_index
                elif closest_index >= 0 and closest_side == 'left':
                    # 如果在左侧，确保不是第一个位置或前一个位置不是被拖拽的文件
                    if closest_index > 0:
                        insert_index = closest_index

            # 如果找到了插入位置，显示插入光标
            if insert_index >= 0:
                self.insert_index = insert_index
                self.preview_canvas.create_rectangle(
                    cursor_x1, cursor_y1, cursor_x2, cursor_y2,
                    outline="#FF0000",
                    width=3,
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
                # 保存当前状态
                self.save_state()

                # 调整插入索引（考虑源图片在目标位置之前或之后）
                if self.insert_index > self.drag_source_index:
                    adjusted_insert_index = self.insert_index - 1
                else:
                    adjusted_insert_index = self.insert_index

                # 移动图片到新位置
                source_path = self.image_paths.pop(self.drag_source_index)
                self.image_paths.insert(adjusted_insert_index, source_path)

                # 更新界面
                self.update_image_list()

        except Exception as e:
            print(f"释放失败: {e}")
        finally:
            # 清除拖拽预览和插入光标
            self.preview_canvas.delete("drag_preview")
            self.preview_canvas.delete("insert_cursor")

            # 重置拖拽状态
            self.dragging_image_index = -1
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
            # 选中该图片
            self.selected_image_index = clicked_index
            self.file_combobox.current(clicked_index)
            self.draw_selection_box(clicked_index)
            self.update_status_info()

            # 显示右键菜单
            self.show_context_menu(event, clicked_index)

    def show_context_menu(self, event, index):
        """显示右键菜单"""
        if index < 0 or index >= len(self.image_paths):
            return

        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="进入裁剪模式", command=lambda: self.enter_crop_mode())
        context_menu.add_separator()
        context_menu.add_command(label="复制", command=lambda: self.copy_images(index))
        context_menu.add_command(label="剪切", command=lambda: self.cut_images(index))
        context_menu.add_command(label="粘贴", command=lambda: self.paste_images(index))
        context_menu.add_separator()
        context_menu.add_command(label="删除", command=lambda: self.delete_images(index))
        context_menu.add_separator()
        context_menu.add_command(label="查看属性", command=lambda: self.show_image_properties(index))
        context_menu.add_command(label="打开位置", command=lambda: self.open_image_location(index))
        context_menu.add_command(label="用默认浏览器打开", command=lambda: self.open_with_default_viewer(index))

        # 在鼠标位置显示菜单
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def select_all_images(self, event=None):
        """全选所有图片"""
        if self.image_paths:
            self.selected_image_indices = set(range(len(self.image_paths)))
            self.last_selected_index = len(self.image_paths) - 1
            self.draw_selection_boxes()
            self.update_status_info()

    def draw_selection_boxes(self):
        """绘制选中框（支持多选）"""
        # 删除所有旧的选中框
        self.preview_canvas.delete("selection_box")
        
        # 为所有选中的图片绘制选中框
        for index in self.selected_image_indices:
            if 0 <= index < len(self.image_rects):
                rect = self.image_rects[index]
                self.preview_canvas.create_rectangle(
                    rect['x1'], rect['y1'], rect['x2'], rect['y2'],
                    outline="#0066FF",
                    width=5,
                    tags="selection_box"
                )

    def show_image_properties(self, index):
        """显示图片属性"""
        if index < 0 or index >= len(self.image_paths):
            return

        try:
            img_path = self.image_paths[index]
            img = Image.open(img_path)
            width, height = img.size
            size_kb = os.path.getsize(img_path) / 1024

            info_text = f"""图片属性:
            
文件名: {os.path.basename(img_path)}
路径: {img_path}
尺寸: {width} x {height} 像素
格式: {img.format}
模式: {img.mode}
文件大小: {size_kb:.2f} KB"""

            messagebox.showinfo("图片属性", info_text)
        except Exception as e:
            messagebox.showerror("错误", f"无法读取图片属性: {str(e)}")

    def open_image_location(self, index):
        """打开图片所在位置"""
        if index < 0 or index >= len(self.image_paths):
            return

        try:
            img_path = self.image_paths[index]
            import subprocess
            subprocess.Popen(['explorer', '/select,', os.path.abspath(img_path)])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开位置: {str(e)}")

    def open_with_default_viewer(self, index):
        """用默认图片浏览器打开"""
        if index < 0 or index >= len(self.image_paths):
            return

        try:
            img_path = self.image_paths[index]
            import subprocess
            if os.name == 'nt':  # Windows
                os.startfile(img_path)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.call(['xdg-open', img_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片: {str(e)}")

    def copy_images(self, index):
        """复制选中的图片到剪贴板"""
        if index < 0 or index >= len(self.image_paths):
            return

        # 将当前选中的图片索引添加到剪贴板
        self.clipboard_images = [index]
        self.clipboard_action = 'copy'
        print(f"已复制图片 #{index + 1}")

    def cut_images(self, index):
        """剪切选中的图片到剪贴板"""
        if index < 0 or index >= len(self.image_paths):
            return

        # 将当前选中的图片索引添加到剪贴板
        self.clipboard_images = [index]
        self.clipboard_action = 'cut'
        print(f"已剪切图片 #{index + 1}")

    def paste_images(self, target_index):
        """从剪贴板粘贴图片"""
        if not self.clipboard_images or not self.clipboard_action:
            messagebox.showinfo("提示", "剪贴板为空")
            return

        if target_index < 0 or target_index >= len(self.image_paths):
            return

        try:
            # 保存当前状态
            self.save_state()

            # 获取要粘贴的图片
            paste_indices = self.clipboard_images.copy()

            if self.clipboard_action == 'copy':
                # 复制模式：在目标位置插入图片的副本
                for i, paste_index in enumerate(paste_indices):
                    if paste_index < len(self.image_paths):
                        # 复制文件到临时位置
                        import shutil
                        src_path = self.image_paths[paste_index]
                        filename = os.path.basename(src_path)
                        name, ext = os.path.splitext(filename)
                        dst_path = os.path.join(os.path.dirname(src_path), f"{name}_copy{ext}")
                        shutil.copy2(src_path, dst_path)

                        # 插入到目标位置
                        insert_pos = target_index + i
                        self.image_paths.insert(insert_pos, dst_path)

            elif self.clipboard_action == 'cut':
                # 剪切模式：将图片移动到目标位置
                # 先按索引排序，确保移动顺序正确
                paste_indices.sort(reverse=True)
                for paste_index in paste_indices:
                    if paste_index < len(self.image_paths):
                        # 移除原位置的图片
                        img_path = self.image_paths.pop(paste_index)

                        # 插入到目标位置
                        if paste_index < target_index:
                            self.image_paths.insert(target_index - 1, img_path)
                        else:
                            self.image_paths.insert(target_index, img_path)

                # 清空剪贴板
                self.clipboard_images = []
                self.clipboard_action = None

            # 更新界面
            self.update_image_list()
            print("粘贴成功")

        except Exception as e:
            messagebox.showerror("错误", f"粘贴失败: {str(e)}")

    def delete_images(self, index):
        """删除选中的图片"""
        if index < 0 or index >= len(self.image_paths):
            return

        # 确认删除
        img_path = self.image_paths[index]
        filename = os.path.basename(img_path)
        result = messagebox.askyesno("确认删除", f"确定要删除图片:\n{filename}?")

        if result:
            try:
                # 保存当前状态
                self.save_state()

                # 从列表中删除
                del self.image_paths[index]

                # 更新选中索引
                if self.selected_image_index == index:
                    self.selected_image_index = -1
                elif self.selected_image_index > index:
                    self.selected_image_index -= 1

                # 更新界面
                self.update_image_list()
                print(f"已删除图片 #{index + 1}")

            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")

    def refresh_preview(self):
        """
        刷新预览
        重新显示网格预览，根据当前窗口大小调整布局
        """
        if self.image_paths:
            self.display_grid_preview()

    def preview_gif(self):
        """
        预览GIF动画效果 - 弹出独立窗口
        创建一个独立的窗口来预览GIF动画效果
        """
        if not self.image_paths:
            messagebox.showwarning("提示", "请先选择至少一张图片")
            return

        # 处理尺寸调整参数
        resize = None
        if self.resize_width.get() and self.resize_height.get():
            try:
                width = int(self.resize_width.get())
                height = int(self.resize_height.get())
                if width > 0 and height > 0:
                    resize = (width, height)
                else:
                    messagebox.showerror("错误", "尺寸参数必须大于0")
                    return
            except ValueError:
                messagebox.showerror("错误", "尺寸参数必须是数字")
                return

        try:
            # 加载所有图片并处理
            frames = []
            duration = self.duration.get()

            for img_path in self.image_paths:
                try:
                    img = Image.open(img_path)

                    # 如果需要调整尺寸
                    if resize:
                        img = img.resize(resize, Image.Resampling.LANCZOS)

                    # 确保所有图片使用相同的模式
                    if img.mode != 'P':
                        img = img.convert('P', palette=Image.Palette.ADAPTIVE)

                    frames.append(img)
                except Exception as e:
                    print(f"警告: 无法加载图片 {img_path}: {e}")
                    continue

            if not frames:
                raise ValueError("没有成功加载任何图片")

            # 导入预览窗口类
            from .preview import GifPreviewWindow

            # 创建预览窗口
            preview_window = GifPreviewWindow(self.root, frames, duration, self.output_path.get())

        except Exception as e:
            messagebox.showerror("错误", f"预览GIF失败:\n{str(e)}")

    def save_state(self):
        """保存当前状态到撤销栈"""
        # 保存当前图片列表的深拷贝
        import copy
        current_state = copy.deepcopy(self.image_paths)
        self.undo_stack.append(current_state)

        # 限制撤销栈的大小
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)

        # 清空重做栈
        self.redo_stack.clear()

    def undo(self):
        """撤销操作"""
        if not self.undo_stack:
            messagebox.showinfo("提示", "没有可撤销的操作")
            return

        # 保存当前状态到重做栈
        import copy
        current_state = copy.deepcopy(self.image_paths)
        self.redo_stack.append(current_state)

        # 从撤销栈恢复上一个状态
        previous_state = self.undo_stack.pop()
        self.image_paths = previous_state

        # 更新界面
        self.update_image_list()

    def redo(self):
        """重做操作"""
        if not self.redo_stack:
            messagebox.showinfo("提示", "没有可重做的操作")
            return

        # 保存当前状态到撤销栈
        import copy
        current_state = copy.deepcopy(self.image_paths)
        self.undo_stack.append(current_state)

        # 从重做栈恢复下一个状态
        next_state = self.redo_stack.pop()
        self.image_paths = next_state

        # 更新界面
        self.update_image_list()


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