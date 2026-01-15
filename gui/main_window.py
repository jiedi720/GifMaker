# -*- coding: utf-8 -*-
"""
GIF Maker GUI主窗口模块
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


class GifMakerGUI:
    def __init__(self, root):
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

        # 变量
        self.image_paths = []
        self.output_path = tk.StringVar()
        self.duration = tk.IntVar(value=500)
        self.loop = tk.IntVar(value=0)
        self.optimize = tk.BooleanVar(value=True)
        self.resize_width = tk.StringVar()
        self.resize_height = tk.StringVar()
        self.current_photo = None  # 保存当前预览图片
        self.preview_scale = 1.0  # 预览缩放比例

        self.setup_ui()
        self.setup_menu()

        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_resize)

        # 居中显示窗口（在UI初始化后）
        self.center_window()
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'gif.png')
            if os.path.exists(icon_path):
                self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception:
            pass  # 如果图标设置失败，忽略错误
    
    def on_window_resize(self, event):
        """窗口大小变化时的回调函数"""
        # 只处理窗口大小变化事件，忽略其他配置事件
        if event.widget == self.root and (event.width != getattr(self, '_last_width', 0) or event.height != getattr(self, '_last_height', 0)):
            # 只在预览区域有图片时重新调整
            if self.current_photo and self.image_paths:
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
        """将窗口居中显示"""
        # 更新窗口信息
        self.root.update_idletasks()

        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # 显示窗口
        self.root.deiconify()
        self.root.update_idletasks()
    
    def setup_menu(self):
        """设置菜单栏"""
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
        """显示关于对话框"""
        messagebox.showinfo("关于", "GIF制作工具 v1.0\n\n将多张图片转换为GIF动画\n支持自定义持续时间、循环次数、尺寸调整等功能")

    def setup_ui(self):
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
            width=30
        )
        self.file_combobox.pack(side=tk.LEFT, padx=(0, 5))
        self.file_combobox.bind('<<ComboboxSelected>>', self.on_file_selected)

        btn_clear_list = ttk.Button(image_frame, text="🗑️", command=self.clear_images, width=5)
        btn_clear_list.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_clear_list, "清空列表")

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
        directory = filedialog.askdirectory(title="选择包含图片的目录")
        if directory:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from GifMaker import get_image_files
            image_files = get_image_files(directory)
            # 避免重复添加文件
            for file in image_files:
                if file not in self.image_paths:
                    self.image_paths.append(file)
            self.update_image_list()

            # 自动加载首图到预览区域
            if self.image_paths:
                self.preview_first_image()
                self.update_status_info()

    def clear_images(self):
        self.image_paths = []
        self.update_image_list()

    def update_image_list(self):
        # 更新下拉列表
        file_list = []
        for i, img_path in enumerate(self.image_paths, 1):
            file_list.append(f"#{i}: {os.path.basename(img_path)}")

        self.file_combobox['values'] = file_list
        if file_list:
            self.file_combobox.current(0)
            # 更新状态栏信息
            self.update_status_info()
        else:
            self.file_list_var.set('')
            # 清空状态栏信息
            self.current_img_size_label.config(text="当前图片: --")
            self.total_time_label.config(text="总时间: --")
            self.gif_size_label.config(text="GIF大小: --")

    def update_status_info(self):
        """更新状态栏信息，显示当前图片信息"""
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
        """放大预览"""
        if self.preview_scale < 5.0:
            self.preview_scale *= 1.25
            self.refresh_preview()
            self.update_status_info()
            # 立即更新界面
            self.root.update_idletasks()
            # 更新输入框
            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, str(int(self.preview_scale * 100)))

    def zoom_out_preview(self):
        """缩小预览"""
        if self.preview_scale > 0.1:  # 改为0.1以匹配新的最小值
            self.preview_scale /= 1.25
            self.refresh_preview()
            self.update_status_info()
            # 立即更新界面
            self.root.update_idletasks()
            # 更新输入框
            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, str(int(self.preview_scale * 100)))

    def reset_preview_zoom(self):
        """重置预览缩放"""
        self.preview_scale = 1.0
        self.refresh_preview()
        self.update_status_info()
        # 立即更新界面
        self.root.update_idletasks()

        # 更新输入框
        self.zoom_entry.delete(0, tk.END)
        self.zoom_entry.insert(0, "100")

    def fit_preview_to_window(self):
        """让预览图片适应窗口大小"""
        if not self.image_paths:
            return

        try:
            # 打开第一张图片
            img_path = self.image_paths[0]
            img = Image.open(img_path)

            # 获取图片原始尺寸
            orig_width, orig_height = img.size

            # 获取预览Canvas的实际尺寸
            self.preview_canvas.update_idletasks()
            canvas_width = self.preview_canvas.winfo_width() - 20  # 减去padding
            canvas_height = self.preview_canvas.winfo_height() - 20  # 减去padding

            # 确保预览区域有合理的尺寸
            if canvas_width < 50:
                canvas_width = orig_width
            if canvas_height < 50:
                canvas_height = orig_height

            # 计算适应窗口的缩放比例
            scale_width = canvas_width / orig_width
            scale_height = canvas_height / orig_height
            fit_scale = min(scale_width, scale_height)  # 保持宽高比

            # 更新缩放比例
            self.preview_scale = fit_scale
            self.refresh_preview()
            self.update_status_info()

            # 更新输入框
            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, str(int(self.preview_scale * 100)))

        except Exception as e:
            messagebox.showerror("错误", f"无法适应窗口: {str(e)}")

    def apply_manual_zoom(self, event):
        """应用手动输入的缩放值"""
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
        """当预览canvas大小改变时更新窗口大小"""
        # 仅当canvas大小改变时更新滚动区域
        pass  # 滚动区域由display_frame方法管理

    def on_preview_mousewheel(self, event):
        """处理预览区域的鼠标滚轮事件"""
        # 检查滚动区域是否大于Canvas可视区域，如果是则允许滚动
        bbox = self.preview_canvas.bbox("all")
        if bbox:
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            # 如果图片的宽度或高度大于Canvas的可视区域，则允许滚动
            if bbox[2] > canvas_width or bbox[3] > canvas_height:
                # 检查操作系统类型来确定滚动方向
                if event.num == 4 or event.delta > 0:
                    # 向上滚动 - 垂直滚动向上
                    self.preview_canvas.yview_scroll(-1, "units")
                elif event.num == 5 or event.delta < 0:
                    # 向下滚动 - 垂直滚动向下
                    self.preview_canvas.yview_scroll(1, "units")

    def create_tooltip(self, widget, text):
        """创建鼠标悬浮提示"""
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
        """下拉列表选择回调"""
        selection = self.file_combobox.current()
        if selection >= 0 and selection < len(self.image_paths):
            # 预览选中的图片
            self.preview_specific_image(selection)
            # 更新状态栏信息
            self.update_status_info()

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="保存GIF文件",
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)

    def create_gif_from_gui(self):
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
        """预览第一张选中的图片"""
        if not self.image_paths:
            messagebox.showwarning("提示", "请先选择图片")
            return

        self.refresh_preview()
        self.update_status_info()
    
    def preview_specific_image(self, index):
        """预览指定索引的图片"""
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

    def refresh_preview(self):
        """刷新预览图片"""
        if not self.image_paths:
            return

        try:
            # 打开第一张图片
            img_path = self.image_paths[0]
            img = Image.open(img_path)

            # 获取图片原始尺寸
            orig_width, orig_height = img.size

            # 获取预览Canvas的实际尺寸
            self.preview_canvas.update_idletasks()
            preview_width = self.preview_canvas.winfo_width() - 20  # 减去padding
            preview_height = self.preview_canvas.winfo_height() - 20  # 减去padding

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

    def preview_gif(self):
        """预览GIF动画效果 - 弹出独立窗口"""
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


def run():
    """启动GIF Maker GUI应用"""
    root = tk.Tk()
    app = GifMakerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    run()