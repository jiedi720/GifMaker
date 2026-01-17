# -*- coding: utf-8 -*-
"""
GIF Maker GUI主窗口模块
这个模块实现了GIF制作工具的图形用户界面，包括图片选择、参数设置、预览和GIF生成功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入功能模块
from function.image_utils import load_image, get_image_info, resize_image, create_photo_image, calculate_scale_to_fit, calculate_scale_to_fill
from function.crop import crop_image
from function.history_manager import HistoryManager
from function.file_manager import get_image_files, validate_image_path, get_file_size_kb
from function.gif_operations import create_gif
from function.file_manager import calculate_total_time, validate_gif_params, estimate_gif_size


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

        # 隐藏窗口，等待所有组件初始化完成后再显示
        self.root.withdraw()

        # 设置窗口大小限制
        self.root.minsize(1366, 768)
        self.root.maxsize(1920, 1080)

        # 设置窗口图标
        self.set_window_icon()

        # 初始化变量
        self.image_paths = []  # 存储所有图片路径
        self.output_path = tk.StringVar()  # 输出文件路径
        # 设置默认输出文件名
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"animation_{timestamp}.gif"
        self.output_path.set(default_filename)
        self.duration = tk.IntVar(value=100)  # GIF每帧持续时间，默认100ms
        self.loop = tk.IntVar(value=0)  # 循环次数，0表示无限循环
        self.optimize = tk.BooleanVar(value=True)  # 是否优化GIF
        self.resize_width = tk.StringVar()  # 调整宽度
        self.resize_height = tk.StringVar()  # 调整高度
        self.current_photo = None  # 当前PhotoImage对象
        self.preview_scale = 1.0  # 预览缩放比例
        self.preview_photos = []  # 存储所有PhotoImage对象
        self.image_rects = []  # 存储所有图片的矩形区域信息
        self.selected_image_index = -1  # 当前选中的图片索引
        self.selected_image_indices = set()  # 多选图片索引集合
        self.last_selected_index = -1  # 上一次选中的图片索引（用于Shift多选）
        self.clipboard_images = []  # 剪贴板图片列表
        self.clipboard_action = None  # 剪贴板操作类型：'copy'或'cut'

        # 初始化历史管理器
        self.history_manager = HistoryManager(max_history=50)

        # 待保存的裁剪图片
        self.pending_crops = {}  # 格式：{图片路径: PIL.Image对象}
        self.pending_crop_coords = {}  # 格式：{图片路径: (x1, y1, x2, y2)}

        # 设置UI和菜单
        self.setup_ui()
        self.setup_menu()

        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_resize)

        # 绑定窗口关闭事件
        from function.history_manager import on_window_close
        self.root.protocol('WM_DELETE_WINDOW', lambda: on_window_close(self))

        # 居中显示窗口（UI初始化完成后）
        self.center_window()

    def perform_undo(self):
        """执行撤销操作"""
        try:
            from function.history_manager import undo
            undo(self)
        except Exception as e:
            print(f"撤销失败: {e}")

    def perform_redo(self):
        """执行重做操作"""
        try:
            from function.history_manager import redo
            redo(self)
        except Exception as e:
            print(f"重做失败: {e}")

    def preview_gif(self):
        """预览生成的GIF动画"""
        try:
            from function.preview import preview_gif
            preview_gif(self)
        except Exception as e:
            messagebox.showerror("错误", f"预览GIF失败: {str(e)}")

    def browse_output(self):
        """浏览输出目录"""
        try:
            from function.ui_operations import browse_output
            browse_output(self)
        except Exception as e:
            messagebox.showerror("错误", f"浏览输出目录失败: {str(e)}")

    def refresh_preview(self):
        """刷新预览显示"""
        try:
            self.display_grid_preview()
        except Exception as e:
            print(f"刷新预览失败: {e}")

    def set_window_icon(self):
        """设置窗口图标，从项目icons目录中加载gif.png作为窗口图标"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'gif.png')
            if os.path.exists(icon_path):
                self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception:
            pass

    def on_window_resize(self, event):
        """窗口大小变化时的回调函数，当窗口大小改变时，重新调整预览区域的布局"""
        # 只处理根窗口的大小变化事件
        if event.widget == self.root and (event.width != getattr(self, '_last_width', 0) or event.height != getattr(self, '_last_height', 0)):
            # 记录当前窗口大小
            self._last_width = event.width
            self._last_height = event.height

            # 使用防抖机制，避免频繁刷新
            if not hasattr(self, '_resize_timer'):
                self._resize_timer = None
            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(100, self.refresh_preview)

    def center_window(self):
        """将窗口居中显示，计算屏幕中心坐标并将窗口移动到该位置"""
        # 更新窗口信息
        self.root.update_idletasks()

        # 获取窗口尺寸
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # 计算居中位置
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)

        # 设置窗口位置并显示
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()
        self.root.update_idletasks()

    def setup_menu(self):
        """设置菜单栏，创建文件菜单和帮助菜单，并绑定相应的功能"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
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
        file_menu.add_command(label="退出", command=self.root.quit)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

        # 绑定快捷键
        from function.ui_operations import browse_output
        self.root.bind('<Alt-o>', lambda e: browse_output(self))

    def show_about(self):
        """显示关于对话框，显示应用程序的基本信息和功能说明"""
        messagebox.showinfo("关于", "GIF制作工具 v1.0\n\n将多张图片转换为GIF动画\n支持自定义持续时间、循环次数、尺寸调整等功能")

    def setup_ui(self):
        """设置用户界面，创建并布局所有GUI组件，包括工具栏、参数设置区、预览区和状态栏"""
        # 配置主窗口的行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置主框架的行列权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # 图片操作工具栏
        image_frame = ttk.Frame(main_frame, padding="5")
        image_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # 选择图片文件按钮
        from function.file_manager import select_images
        btn_select_files = ttk.Button(image_frame, text="📁", command=lambda: select_images(self), width=5)
        btn_select_files.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_select_files, "选择图片文件")

        # 选择图片目录按钮
        from function.file_manager import select_directory
        btn_select_dir = ttk.Button(image_frame, text="📂", command=lambda: select_directory(self), width=5)
        btn_select_dir.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_select_dir, "选择图片目录")

        # 文件列表下拉框
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

        # 清空列表按钮
        from function.file_manager import clear_images
        btn_clear_list = ttk.Button(image_frame, text="🗑", command=lambda: clear_images(self), width=5)
        btn_clear_list.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_clear_list, "清空列表")

        # 分隔线
        ttk.Separator(image_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 撤销按钮
        btn_undo = ttk.Button(image_frame, text="↶", command=lambda: self.perform_undo(), width=5)
        btn_undo.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_undo, "撤销 (Ctrl+Z)")

        # 重做按钮
        btn_redo = ttk.Button(image_frame, text="↷", command=lambda: self.perform_redo(), width=5)
        btn_redo.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_redo, "重做 (Ctrl+Y)")

        # 保存裁剪按钮
        from function.history_manager import save_pending_crops
        btn_save = ttk.Button(image_frame, text="💾", command=lambda: save_pending_crops(self), width=5)
        btn_save.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_save, "保存裁剪 (Ctrl+S)")

        # 分隔线
        ttk.Separator(image_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 控制按钮框架
        control_frame = ttk.Frame(image_frame)
        control_frame.pack(side=tk.LEFT, padx=(0, 0))

        # 预览GIF按钮
        btn_preview_gif = ttk.Button(control_frame, text="🎬", command=self.preview_gif, width=5)
        btn_preview_gif.pack(side=tk.LEFT, padx=(0, 3))
        self.create_tooltip(btn_preview_gif, "预览GIF")

        # 分隔线
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 缩放控制按钮
        from function.preview import zoom_in_preview, zoom_out_preview, reset_preview_zoom, fit_preview_to_window
        btn_zoom_out = ttk.Button(control_frame, text="🔍-", command=lambda: zoom_out_preview(self), width=5)
        btn_zoom_out.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_out, "缩小预览")

        btn_zoom_in = ttk.Button(control_frame, text="🔍+", command=lambda: zoom_in_preview(self), width=5)
        btn_zoom_in.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_in, "放大预览")

        btn_reset_zoom = ttk.Button(control_frame, text="🔄", command=lambda: reset_preview_zoom(self), width=5)
        btn_reset_zoom.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_reset_zoom, "原始大小")

        btn_fit_window = ttk.Button(control_frame, text="⬜", command=lambda: fit_preview_to_window(self), width=5)
        btn_fit_window.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_fit_window, "适应窗口")

        # 缩放比例输入框
        self.zoom_entry = ttk.Entry(control_frame, width=4)
        self.zoom_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.zoom_entry.insert(0, "100")  # 默认100%
        from function.preview import apply_manual_zoom
        self.zoom_entry.bind('<Return>', lambda e: apply_manual_zoom(self, e))
        self.create_tooltip(self.zoom_entry, "输入缩放百分比，按回车确认")

        # 百分比标签
        ttk.Label(control_frame, text="%").pack(side=tk.LEFT, padx=(0, 5))

        # 图片预览区域
        preview_outer_frame = ttk.LabelFrame(main_frame, text="图片预览", padding="1")
        preview_outer_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(1, 0))
        preview_outer_frame.columnconfigure(0, weight=1)
        preview_outer_frame.rowconfigure(0, weight=1)

        # 预览框架 - 包含Canvas和滚动条
        self.preview_frame = ttk.Frame(preview_outer_frame)
        self.preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)

        # 创建Canvas和滚动条
        self.preview_canvas = tk.Canvas(self.preview_frame, bg='#313337', highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.preview_canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.preview_canvas.xview)
        self.preview_canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # 启用拖拽功能
        self.preview_canvas.drop_target_register(DND_FILES)
        self.preview_canvas.dnd_bind('<<Drop>>', self.on_drop_files)

        # 布局Canvas和滚动条
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 在Canvas中创建一个图片占位符
        self.preview_image_id = self.preview_canvas.create_image(0, 0, anchor=tk.CENTER, image=None)

        # 绑定Canvas事件
        from function.preview import on_preview_canvas_configure, on_preview_mousewheel
        self.preview_canvas.bind("<Configure>", lambda e: on_preview_canvas_configure(self, e))
        self.preview_canvas.bind("<MouseWheel>", lambda e: on_preview_mousewheel(self, e))  # Windows
        self.preview_canvas.bind("<Button-4>", lambda e: on_preview_mousewheel(self, e))   # Linux
        self.preview_canvas.bind("<Button-5>", lambda e: on_preview_mousewheel(self, e))   # Linux
        self.preview_canvas.bind("<Button-3>", self.on_preview_right_click)

        # 绑定全局快捷键
        self.root.bind("<Control-a>", self.select_all_images)  # Ctrl+A 全选
        from function.history_manager import undo, redo
        self.root.bind("<Control-z>", lambda e: undo(self))  # Ctrl+Z 撤销
        self.root.bind("<Control-y>", lambda e: redo(self))  # Ctrl+Y 重做
        self.root.bind("<Control-s>", lambda e: save_pending_crops(self))  # Ctrl+S 保存

        # 初始化拖拽相关变量
        self.dragging_image_index = -1  # 当前拖拽的图片索引
        self.drag_source_index = -1  # 拖拽源索引
        self.drag_start_pos = None  # 拖拽起始位置
        self.drag_preview_image = None  # 拖拽预览图片
        self.drag_preview_photo = None  # 拖拽预览PhotoImage
        self.insert_cursor = None  # 插入光标
        self.insert_index = -1  # 插入位置索引

        # 绑定鼠标拖拽事件
        self.preview_canvas.bind("<ButtonPress-1>", self.on_preview_left_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_preview_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_preview_release)

        # 状态栏
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(1, 0))
        self.status_frame.columnconfigure(1, weight=1)

        # 总时间标签
        self.total_time_label = ttk.Label(self.status_frame, text="总时间: --", anchor=tk.W)
        self.total_time_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        # GIF大小标签
        self.gif_size_label = ttk.Label(self.status_frame, text="GIF: --", anchor=tk.W)
        self.gif_size_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))

        # 当前图片信息标签
        self.current_img_size_label = ttk.Label(self.status_frame, text="当前图片: --", anchor=tk.W)
        self.current_img_size_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        # 缩放比例标签
        self.zoom_label = ttk.Label(self.status_frame, text="缩放: 100%", anchor=tk.E)
        self.zoom_label.grid(row=0, column=3, sticky=tk.E, padx=(0, 5))

    def create_tooltip(self, widget, text):
        """
        创建鼠标悬浮提示，为指定控件添加工具提示功能
        Args:
            widget: 需要添加提示的控件对象
            text: 提示文本内容
        """
        def enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes("-topmost", True)
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid",
                            borderwidth=1, font=("tahoma", "8", "normal"))
            label.pack()

            # 设置提示框位置
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")

            # 保存tooltip引用，避免被垃圾回收
            widget._tooltip = tooltip

        def leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def preview_first_image(self):
        """预览第一张选中的图片，显示图片列表中的第一张图片到预览区域"""
        if not self.image_paths:
            messagebox.showwarning("提示", "请先选择图片")
            return

        from function.preview import refresh_preview
        refresh_preview(self)
        from function.ui_operations import update_status_info
        update_status_info(self)

    def preview_specific_image(self, index):
        """
        预览指定索引的图片，显示图片列表中指定索引位置的图片到预览区域
        Args:
            index: 图片在列表中的索引
        """
        if not self.image_paths or index < 0 or index >= len(self.image_paths):
            return

        try:
            # 加载图片
            img_path = self.image_paths[index]
            img = Image.open(img_path)

            # 获取原始尺寸
            orig_width, orig_height = img.size

            # 直接使用全局的预览缩放比例
            scale = self.preview_scale

            # 计算缩放后的尺寸
            scaled_width = int(orig_width * scale)
            scaled_height = int(orig_height * scale)

            # 根据缩放方向选择合适的插值算法
            if scale >= 1.0:
                resampling = Image.Resampling.LANCZOS
            else:
                resampling = Image.Resampling.BILINEAR
            img_resized = img.resize((scaled_width, scaled_height), resampling)

            # 转换为Tkinter PhotoImage对象
            self.current_photo = ImageTk.PhotoImage(img_resized)

            # 尝试获取现有图片项的坐标，如果失败则重新创建
            try:
                self.preview_canvas.coords(self.preview_image_id)
            except tk.TclError:
                # 如果图片项不存在，重新创建
                self.preview_image_id = self.preview_canvas.create_image(0, 0, anchor=tk.CENTER, image=None)

            # 更新Canvas中的图片
            self.preview_canvas.itemconfig(self.preview_image_id, image=self.current_photo)

            # 根据图片大小调整位置
            # 如果图片大于Canvas，使用左上角对齐
            # 如果图片小于Canvas，使用居中对齐
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            if scaled_width > canvas_width or scaled_height > canvas_height:
                # 图片较大，使用左上角对齐
                self.preview_canvas.itemconfig(self.preview_image_id, anchor=tk.NW)
                self.preview_canvas.coords(self.preview_image_id, 0, 0)
            else:
                # 图片较小，使用居中对齐
                self.preview_canvas.itemconfig(self.preview_image_id, anchor=tk.CENTER)
                center_x = canvas_width // 2
                center_y = canvas_height // 2
                self.preview_canvas.coords(self.preview_image_id, center_x, center_y)

            # 更新滚动区域 - 使用after确保Canvas已更新
            self.preview_canvas.after(10, lambda: self.preview_canvas.configure(scrollregion=(0, 0, scaled_width, scaled_height)))

        except Exception as e:
            messagebox.showerror("错误", f"无法预览图片: {str(e)}")

    def display_grid_preview(self, update_combobox=True):
        """
        以网格方式显示所有图片，从上到下，从左到右排列，根据图片尺寸调节每列的图片数
        
        Args:
            update_combobox: 是否更新下拉框的值（默认为True）
        """
        # 清空Canvas和缓存
        self.preview_canvas.delete("all")
        self.image_rects.clear()
        self.preview_photos.clear()  # 清空PhotoImage列表

        # 更新文件列表下拉框（仅在需要时更新）
        if update_combobox and self.image_paths:
            file_names = [os.path.basename(p) for p in self.image_paths]
            self.file_combobox['values'] = file_names
            if self.selected_image_index >= 0 and self.selected_image_index < len(file_names):
                self.file_combobox.current(self.selected_image_index)
            elif len(file_names) > 0:
                self.file_combobox.current(0)
        elif update_combobox:
            self.file_combobox['values'] = []
            self.file_combobox.set('')

        if not self.image_paths:
            return

        # 计算网格布局
        from function.image_utils import calculate_grid_layout
        layout_data = calculate_grid_layout(
            self.image_paths,
            self.pending_crops,
            self.preview_scale
        )

        if not layout_data:
            return

        # 获取Canvas实际尺寸
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        # 重新计算布局，使用实际的Canvas尺寸
        layout_data = calculate_grid_layout(
            self.image_paths,
            self.pending_crops,
            self.preview_scale,
            canvas_width=canvas_width,
            canvas_height=canvas_height
        )

        # 遍历布局数据，显示每张图片
        for item in layout_data:
            img_path = item['path']
            x, y = item['position']
            size = item['size']

            # 如果图片已裁剪，使用裁剪后的图片
            if img_path in self.pending_crops:
                img = self.pending_crops[img_path]
            else:
                img = load_image(img_path)

            if img:
                # 调整图片大小
                img_resized = resize_image(img, size[0], size[1])
                photo = create_photo_image(img_resized)
                self.preview_photos.append(photo)

                # 在Canvas上显示图片
                self.preview_canvas.create_image(x, y, image=photo, anchor=tk.NW, tags=f"image_{item['index']}")

                # 为所有图片添加细边框
                self.preview_canvas.create_rectangle(
                    x, y, x + size[0], y + size[1],
                    outline="#CCCCCC",
                    width=1,
                    tags=f"border_{item['index']}"
                )

                # 保存图片矩形区域信息
                rect = {
                    'index': item['index'],
                    'x1': x,
                    'y1': y,
                    'x2': x + size[0],
                    'y2': y + size[1],
                    'path': img_path
                }
                self.image_rects.append(rect)

                # 显示图片序号
                self.preview_canvas.create_text(
                    x + 5, y + 5,
                    text=f"#{item['index'] + 1}",
                    fill="white",
                    font=("Arial", 10, "bold"),
                    anchor=tk.NW,
                    tags=f"label_{item['index']}"
                )

                # 显示文件名（截断过长的文件名）
                filename = os.path.splitext(os.path.basename(img_path))[0]
                max_filename_length = max(5, size[0] // 8)
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

        # 绘制选中框
        if self.selected_image_indices:
            self.draw_selection_boxes()

        # 滚动到选中的图片
        if self.selected_image_index >= 0 and self.selected_image_index < len(self.image_rects):
            self.scroll_to_image(self.selected_image_index)

    def scroll_to_image(self, image_index):
        """
        滚动到指定索引的图片，确保该图片在可视区域内
        Args:
            image_index: 图片索引
        """
        if image_index < 0 or image_index >= len(self.image_rects):
            return

        rect = self.image_rects[image_index]
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        # 获取当前滚动位置
        scroll_x = self.preview_canvas.canvasx(0)
        scroll_y = self.preview_canvas.canvasy(0)

        # 计算图片中心点
        img_center_x = (rect['x1'] + rect['x2']) / 2
        img_center_y = (rect['y1'] + rect['y2']) / 2

        # 计算目标滚动位置（使图片居中）
        target_x = max(0, img_center_x - canvas_width / 2)
        target_y = max(0, img_center_y - canvas_height / 2)

        # 获取滚动区域的总尺寸
        scrollregion = self.preview_canvas.cget("scrollregion")
        if scrollregion:
            parts = scrollregion.split()
            if len(parts) == 4:
                max_scroll_x = float(parts[2])
                max_scroll_y = float(parts[3])

                # 计算滚动比例
                scroll_x_ratio = target_x / max_scroll_x
                scroll_y_ratio = target_y / max_scroll_y

                # 限制滚动比例在 0-1 之间
                scroll_x_ratio = max(0, min(1, scroll_x_ratio))
                scroll_y_ratio = max(0, min(1, scroll_y_ratio))

                # 执行滚动
                self.preview_canvas.xview_moveto(scroll_x_ratio)
                self.preview_canvas.yview_moveto(scroll_y_ratio)

    def draw_selection_box(self, index):
        """绘制选中框（单选）"""
        self.selected_image_indices = {index}
        self.draw_selection_boxes()

    def draw_selection_boxes(self):
        """绘制选中框（支持多选），遍历所有选中的图片索引并绘制蓝色边框"""
        # 清除旧的选中框
        self.preview_canvas.delete("selection_box")

        # 遍历所有选中的图片索引
        for index in self.selected_image_indices:
            if 0 <= index < len(self.image_rects):
                rect = self.image_rects[index]
                self.preview_canvas.create_rectangle(
                    rect['x1'], rect['y1'], rect['x2'], rect['y2'],
                    outline="#0066FF",
                    width=5,
                    tags="selection_box"
                )

        # 确保选中框在最上层
        self.preview_canvas.tag_raise("selection_box")

    def on_preview_left_click(self, event):
        """处理预览区域左键点击事件，用于选择和拖拽图片"""
        # 获取点击位置
        click_x = self.preview_canvas.canvasx(event.x)
        click_y = self.preview_canvas.canvasy(event.y)

        # 检查是否点击了某张图片
        for i, rect in enumerate(self.image_rects):
            if rect['x1'] <= click_x <= rect['x2'] and rect['y1'] <= click_y <= rect['y2']:
                # 检查是否按下了Shift或Ctrl键
                shift_pressed = event.state & 0x1  # Shift键的位掩码
                ctrl_pressed = event.state & 0x4  # Ctrl键的位掩码

                if shift_pressed and self.last_selected_index >= 0:
                    # Shift+点击：范围选择
                    start = min(self.last_selected_index, i)
                    end = max(self.last_selected_index, i)

                    if ctrl_pressed:
                        # Ctrl+Shift：切换范围选择
                        for idx in range(start, end + 1):
                            if idx in self.selected_image_indices:
                                self.selected_image_indices.remove(idx)
                            else:
                                self.selected_image_indices.add(idx)
                    else:
                        # Shift：范围选择
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
                    # 普通点击：检查点击的图片是否已经在选中集合中
                    if i not in self.selected_image_indices:
                        # 如果点击的是未选中的图片，才切换到单选
                        self.selected_image_indices = {i}
                        self.last_selected_index = i
                    # 如果点击的是已选中的图片，则保持当前选择不变（用于拖拽）

                self.selected_image_index = i
                self.file_combobox.current(i)

                # 开始拖拽
                self.dragging_image_index = i
                self.drag_source_index = i
                self.drag_start_pos = (click_x, click_y)

                # 更新选中框显示
                self.draw_selection_boxes()
                from function.ui_operations import update_status_info
                update_status_info(self)

                return

        # 点击空白区域，清除选择
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

            # 根据选中的图片数量选择图标
            if len(self.selected_image_indices) > 1:
                # 多张图片：使用 photos.png
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', 'photos.png')
            else:
                # 单张图片：使用 photo.png
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', 'photo.png')

            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                # 缩放图标
                icon_size = 40
                icon_resized = icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                self.drag_preview_photo = ImageTk.PhotoImage(icon_resized)
                
                # 显示图标
                self.preview_canvas.create_image(
                    x, y,
                    image=self.drag_preview_photo,
                    anchor=tk.CENTER,
                    tags="drag_preview"
                )
            else:
                # 如果图标不存在，使用原来的文字显示
                icon_size = 40
                font_size = 10

                # 创建图标背景
                self.preview_canvas.create_rectangle(
                    x - icon_size // 2, y - icon_size // 2,
                    x + icon_size // 2, y + icon_size // 2,
                    fill="#E0E0E0",
                    outline="#666666",
                    width=2,
                    tags="drag_preview"
                )

                # 显示图标文字
                self.preview_canvas.create_text(
                    x, y - 5,
                    text="IMG",
                    font=("Arial", 16),
                    tags="drag_preview"
                )

                # 显示文件名（截断过长的文件名）
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

            # 将拖拽预览置于顶层
            self.preview_canvas.tag_raise("drag_preview")

        except Exception as e:
            print(f"创建拖拽预览失败: {e}")

    def on_preview_drag(self, event):
        """处理预览区域拖拽事件"""
        if self.dragging_image_index < 0:
            return

        try:
            # 获取拖拽位置
            drag_x = self.preview_canvas.canvasx(event.x)
            drag_y = self.preview_canvas.canvasy(event.y)

            # 如果还没有创建拖拽预览，则创建
            if not self.preview_canvas.find_withtag("drag_preview"):
                self.create_drag_preview(drag_x, drag_y, self.dragging_image_index)
            else:
                # 更新拖拽预览位置
                items = self.preview_canvas.find_withtag("drag_preview")
                for item in items:
                    # 获取当前坐标并更新位置
                    coords = self.preview_canvas.coords(item)
                    if len(coords) == 4:
                        dx = drag_x - (coords[0] + coords[2]) / 2
                        dy = drag_y - (coords[1] + coords[2]) / 2
                        self.preview_canvas.move(item, dx, dy)
                    elif len(coords) == 2:  # 图片中心点
                        dx = drag_x - coords[0]
                        dy = drag_y - coords[1]
                        self.preview_canvas.move(item, dx, dy)

                self.preview_canvas.tag_raise("drag_preview")

            # 更新插入光标位置
            self.update_insert_cursor(drag_x, drag_y)

        except Exception as e:
            print(f"拖拽失败: {e}")

    def update_insert_cursor(self, x, y):
        """更新插入光标位置（只显示垂直方向，确保两个文件之间只显示一个，光标在间隙正中心）"""
        try:
            # 清除旧的插入光标
            self.preview_canvas.delete("insert_cursor")

            # 初始化变量
            insert_index = -1
            cursor_x1, cursor_y1, cursor_x2, cursor_y2 = 0, 0, 0, 0

            # 遍历所有图片矩形
            for i, rect in enumerate(self.image_rects):
                if i != self.dragging_image_index and rect['x1'] <= x <= rect['x2'] and rect['y1'] <= y <= rect['y2']:
                    # 计算图片中心点
                    center_x = (rect['x1'] + rect['x2']) / 2

                    if x < center_x:
                        # 在图片左侧插入
                        insert_index = i
                        if i > 0:
                            # 在前一张图片和当前图片之间
                            prev_rect = self.image_rects[i - 1]
                            gap_center = (prev_rect['x2'] + rect['x1']) / 2
                            cursor_x1 = gap_center - 2
                            cursor_x2 = gap_center + 2
                        else:
                            # 在第一张图片左侧
                            cursor_x1 = rect['x1'] - 2
                            cursor_x2 = rect['x1'] + 2
                        cursor_y1 = rect['y1']
                        cursor_y2 = rect['y2']
                    else:
                        # 在图片右侧插入
                        insert_index = i + 1
                        if i < len(self.image_rects) - 1:
                            # 在当前图片和下一张图片之间
                            next_rect = self.image_rects[i + 1]
                            gap_center = (rect['x2'] + next_rect['x1']) / 2
                            cursor_x1 = gap_center - 2
                            cursor_x2 = gap_center + 2
                        else:
                            # 在最后一张图片右侧
                            cursor_x1 = rect['x2'] - 2
                            cursor_x2 = rect['x2'] + 2
                        cursor_y1 = rect['y1']
                        cursor_y2 = rect['y2']
                    break

            # 如果没有在图片上，查找最近的插入位置
            if insert_index == -1:
                min_distance = float('inf')
                closest_index = -1
                closest_side = None  # 'left'或'right'

                for i, rect in enumerate(self.image_rects):
                    # 只考虑同一行的图片
                    if y >= rect['y1'] and y <= rect['y2']:
                        # 检查左侧
                        if x < rect['x1']:
                            distance = rect['x1'] - x
                            if distance < min_distance:
                                min_distance = distance
                                closest_index = i
                                closest_side = 'left'
                        # 检查右侧
                        elif x > rect['x2']:
                            distance = x - rect['x2']
                            if distance < min_distance:
                                min_distance = distance
                                closest_index = i + 1
                                closest_side = 'right'

                # 只在两个文件之间显示插入光标，光标在间隙正中
                if closest_index >= 0 and closest_side == 'right':
                    # 如果在右侧，确保下一个位置有文件
                    if closest_index < len(self.image_rects):
                        insert_index = closest_index
                        current_rect = self.image_rects[closest_index - 1]
                        next_rect = self.image_rects[closest_index]
                        gap_center = (current_rect['x2'] + next_rect['x1']) / 2
                        cursor_x1 = gap_center - 2
                        cursor_x2 = gap_center + 2
                        cursor_y1 = current_rect['y1']
                        cursor_y2 = current_rect['y2']
                elif closest_index >= 0 and closest_side == 'left':
                    # 如果在左侧，确保前一个位置有文件
                    if closest_index > 0:
                        insert_index = closest_index
                        prev_rect = self.image_rects[closest_index - 1]
                        current_rect = self.image_rects[closest_index]
                        gap_center = (prev_rect['x2'] + current_rect['x1']) / 2
                        cursor_x1 = gap_center - 2
                        cursor_x2 = gap_center + 2
                        cursor_y1 = current_rect['y1']
                        cursor_y2 = current_rect['y2']

            # 绘制插入光标
            if insert_index >= 0:
                self.insert_index = insert_index
                # 绘制类似Word的红色垂直光标
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
            # 如果有有效的插入位置，执行移动操作
            if self.insert_index >= 0 and self.insert_index != self.drag_source_index:
                # 保存当前状态到历史记录
                from function.history_manager import save_state
                save_state(self)

                # 检查是否是多选拖拽
                if len(self.selected_image_indices) > 1:
                    # 多选拖拽：移动所有选中的图片
                    # 1. 获取所有选中的索引，按升序排序
                    sorted_selected_indices = sorted(self.selected_image_indices)
                    
                    # 2. 计算插入位置的调整值
                    # 如果插入位置在源索引之后，需要减去已移除的图片数量
                    remove_count = 0
                    adjusted_insert_index = self.insert_index
                    
                    # 3. 收集所有要移动的图片路径
                    images_to_move = []
                    for idx in sorted_selected_indices:
                        if idx < self.insert_index:
                            remove_count += 1
                        images_to_move.append(self.image_paths[idx])
                    
                    # 4. 从原位置移除图片（从后往前移除，避免索引混乱）
                    for idx in reversed(sorted_selected_indices):
                        self.image_paths.pop(idx)
                    
                    # 5. 调整插入索引
                    if self.insert_index > sorted_selected_indices[-1]:
                        adjusted_insert_index = self.insert_index - len(sorted_selected_indices)
                    elif self.insert_index > sorted_selected_indices[0]:
                        adjusted_insert_index = self.insert_index - sum(1 for idx in sorted_selected_indices if idx < self.insert_index)
                    
                    # 6. 插入图片到新位置
                    for i, img_path in enumerate(images_to_move):
                        self.image_paths.insert(adjusted_insert_index + i, img_path)
                    
                    # 7. 更新选中索引
                    new_selected_indices = set(range(adjusted_insert_index, adjusted_insert_index + len(images_to_move)))
                    self.selected_image_indices = new_selected_indices
                    # 选中第一个移动的图片作为当前选中索引
                    self.selected_image_index = adjusted_insert_index
                else:
                    # 单选拖拽：移动单个图片
                    # 调整插入索引（因为删除源图片后索引会变化）
                    if self.insert_index > self.drag_source_index:
                        adjusted_insert_index = self.insert_index - 1
                    else:
                        adjusted_insert_index = self.insert_index

                    # 执行移动操作
                    source_path = self.image_paths.pop(self.drag_source_index)
                    self.image_paths.insert(adjusted_insert_index, source_path)

                    # 更新选中索引
                    self.selected_image_index = adjusted_insert_index
                    self.selected_image_indices = {adjusted_insert_index}

                # 更新UI（不重新绘制整个网格，只更新必要部分）
                self.update_image_positions()

        except Exception as e:
            print(f"释放失败: {e}")
        finally:
            # 清理拖拽相关资源
            self.preview_canvas.delete("drag_preview")
            self.preview_canvas.delete("insert_cursor")
            self.dragging_image_index = -1
            self.drag_source_index = -1
            self.drag_start_pos = None
            self.drag_preview_image = None
            self.drag_preview_photo = None
            self.insert_index = -1

    def update_image_positions(self):
        """更新图片位置（使用双缓冲技术减少闪烁）"""
        from function.image_utils import calculate_grid_layout
        
        # 获取Canvas实际尺寸
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        # 计算布局，使用实际的Canvas尺寸
        layout_data = calculate_grid_layout(
            self.image_paths,
            self.pending_crops,
            self.preview_scale,
            canvas_width=canvas_width,
            canvas_height=canvas_height
        )

        if not layout_data:
            return

        # 清空缓存
        self.image_rects.clear()
        self.preview_photos.clear()

        # 准备新的图片数据
        new_photos = []
        new_rects = []

        # 遍历布局数据，准备每张图片
        for item in layout_data:
            img_path = item['path']
            x, y = item['position']
            size = item['size']

            # 如果图片已裁剪，使用裁剪后的图片
            if img_path in self.pending_crops:
                img = self.pending_crops[img_path]
            else:
                img = load_image(img_path)

            if img:
                # 调整图片大小
                img_resized = resize_image(img, size[0], size[1])
                photo = create_photo_image(img_resized)
                new_photos.append(photo)
                new_rects.append({
                    'x1': x,
                    'y1': y,
                    'x2': x + size[0],
                    'y2': y + size[1]
                })

        # 一次性更新所有内容（减少闪烁）
        # 1. 清空画布
        self.preview_canvas.delete("all")
        
        # 2. 一次性绘制所有图片
        for i, (photo, item) in enumerate(zip(new_photos, layout_data)):
            x, y = item['position']
            size = item['size']
            img_path = item['path']
            
            # 绘制图片
            self.preview_canvas.create_image(x, y, image=photo, anchor=tk.NW, tags=f"image_{item['index']}")
            
            # 为所有图片添加细边框
            self.preview_canvas.create_rectangle(
                x, y, x + size[0], y + size[1],
                outline="#CCCCCC",
                width=1,
                tags=f"border_{item['index']}"
            )
            
            # 显示图片序号
            self.preview_canvas.create_text(
                x + 5, y + 5,
                text=f"#{item['index'] + 1}",
                fill="white",
                font=("Arial", 10, "bold"),
                anchor=tk.NW,
                tags=f"label_{item['index']}"
            )
            
            # 显示文件名（截断过长的文件名）
            filename = os.path.splitext(os.path.basename(img_path))[0]
            max_filename_length = max(5, size[0] // 8)
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

        # 3. 保存新的缓存数据
        self.preview_photos = new_photos
        self.image_rects = new_rects

        # 4. 重新绘制选中框
        if self.selected_image_indices:
            self.draw_selection_boxes()

        # 5. 更新滚动区域
        max_x = max(rect['x2'] for rect in self.image_rects) if self.image_rects else 0
        max_y = max(rect['y2'] for rect in self.image_rects) if self.image_rects else 0
        self.preview_canvas.configure(scrollregion=(0, 0, max_x + 20, max_y + 20))
        if self.selected_image_index >= 0 and self.selected_image_index < len(self.image_rects):
            self.scroll_to_image(self.selected_image_index)

    def on_preview_right_click(self, event):
        """处理预览区域右键点击事件"""
        # 获取点击位置
        click_x = self.preview_canvas.canvasx(event.x)
        click_y = self.preview_canvas.canvasy(event.y)

        # 查找被点击的图片
        clicked_index = -1
        for i, rect in enumerate(self.image_rects):
            if rect['x1'] <= click_x <= rect['x2'] and rect['y1'] <= click_y <= rect['y2']:
                clicked_index = i
                break

        if clicked_index >= 0:
            # 如果图片未被选中，则选中它
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

        context_menu.add_command(label="进入裁剪模式", command=lambda: enter_crop_mode(self))
        context_menu.add_separator()
        context_menu.add_command(label="复制", command=lambda: copy_images(self, index))
        context_menu.add_command(label="剪切", command=lambda: cut_images(self, index))
        context_menu.add_command(label="粘贴", command=lambda: paste_images(self, index))
        context_menu.add_separator()
        context_menu.add_command(label="删除", command=lambda: delete_images(self, index))
        context_menu.add_separator()
        context_menu.add_command(label="查看属性", command=lambda: show_image_properties(self, index))
        context_menu.add_command(label="打开位置", command=lambda: open_image_location(self, index))
        context_menu.add_command(label="用默认浏览器打开", command=lambda: open_with_default_viewer(self, index))

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def select_all_images(self, event=None):
        """全选所有图片"""
        from function.list_operations import select_all_images as ops_select_all_images
        ops_select_all_images(self, event)

    def on_drop_files(self, event):
        """
        处理拖拽文件到预览窗口的事件
        支持拖拽单个或多个文件、目录
        拖拽时会清除已有图片
        """
        try:
            # 解析拖拽的文件/目录列表
            data = event.data
            if not data:
                return

            # 处理Windows格式的拖拽数据
            # 格式1: {文件1 文件2 文件3} - 所有文件在一个花括号内
            # 格式2: {文件1} {文件2} {文件3} - 每个文件都有自己的花括号
            # 格式3: {"文件 1" "文件 2" "文件 3"} - 带空格的路径用引号包围
            paths = []

            # 先尝试提取所有花括号内的内容
            import re
            bracket_matches = re.findall(r'\{([^}]*)\}', data)

            if bracket_matches:
                # 如果找到花括号，提取其中的内容
                for match in bracket_matches:
                    match = match.strip()
                    if match:
                        # 检查是否包含引号（可能是带空格的路径）
                        if '"' in match or "'" in match:
                            # 使用正则表达式提取引号内的内容
                            quoted_matches = re.findall(r'["\']([^"\']+)["\']', match)
                            if quoted_matches:
                                paths.extend([m.strip() for m in quoted_matches if m.strip()])
                            else:
                                # 如果没有匹配到引号内容，直接添加
                                paths.append(match)
                        elif ' ' in match and not os.path.exists(match):
                            # 如果包含空格且不是有效路径，尝试分割
                            split_paths = match.split()
                            paths.extend([p.strip() for p in split_paths if p.strip()])
                        else:
                            # 否则直接添加
                            paths.append(match)
            else:
                # 如果没有花括号，直接使用原始数据
                paths.append(data.strip())

            # 如果提取到的路径为空，尝试直接分割
            if not paths:
                # 移除外层花括号
                if data.startswith('{') and data.endswith('}'):
                    data = data[1:-1]

                # 分割多个文件/目录
                paths = [p.strip() for p in data.split() if p.strip()]

            if not paths:
                return

            # 收集所有图片文件
            image_paths = []
            from function.file_manager import get_image_files, validate_image_path

            for path in paths:
                # 移除可能的引号
                path = path.strip('"').strip("'")

                if os.path.isdir(path):
                    # 如果是目录，获取目录中的所有图片
                    dir_images = get_image_files(path)
                    if dir_images:
                        image_paths.extend(dir_images)
                elif os.path.isfile(path):
                    # 如果是文件，检查是否是有效的图片文件
                    if validate_image_path(path):
                        image_paths.append(path)

            if image_paths:
                # 清除已有图片，只保留新拖拽的图片
                self.image_paths = image_paths

                # 重置选择状态
                self.selected_image_indices = set()
                self.selected_image_index = -1
                self.last_selected_index = -1
                self.pending_crops = {}
                self.pending_crop_coords = {}

                # 使用适应窗口模式
                from function.preview import fit_preview_to_window
                fit_preview_to_window(self)

        except Exception as e:
            print(f"拖拽文件处理失败: {e}")
            messagebox.showerror("错误", f"拖拽文件处理失败: {str(e)}")


def run():
    """
    启动GIF Maker GUI应用
    创建主窗口并启动事件循环
    """
    root = TkinterDnD.Tk()
    app = GifMakerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    run()
