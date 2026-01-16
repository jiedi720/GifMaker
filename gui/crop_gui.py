# -*- coding: utf-8 -*-
"""
裁剪窗口 GUI 模块 - 高清自适应�?只包含裁剪窗口的 GUI 设定相关代码
支持 1280x720 布局，并能随窗口缩放自动调整控件位置
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import os

# 导入图像处理工具模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from function.image_utils import (
    load_image,
    resize_image,
    create_photo_image,
    calculate_scale_to_fit,
    calculate_scale_to_fill,
    crop_image,
    auto_crop_image
)
from function.crop_state import CropState
from function.crop_handler import CropRatioHandler
from function.crop_logic import (
    find_smallest_image_path,
    calculate_scaled_dimensions,
    convert_canvas_to_image_coords,
    validate_crop_coordinates,
    calculate_aspect_ratio,
    apply_aspect_ratio_constraints
)
from function.crop_strategy import determine_crop_strategy
from function.widget_utils import ensure_widget_rendered

class CropDialog:
    """裁剪对话框类"""

    def __init__(self, parent, image_path=None, image_paths=None, current_index=0):
        self.parent = parent
        self.result = None
        self.image_path = image_path
        self.image_paths = image_paths or []
        self.current_index = current_index
        self.current_photo = None
        self.original_image = None
        self.base_photo = None  # 保存基础图片用于恢复
        self.preview_scale = 1.0
        self.initial_scale = 1.0  # 保存加载时的初始缩放比例

        # 鼠标选框相关变量
        self.selection_start = None
        self.selection_rect = None
        self.is_selecting = False

        # 滑块相关变量
        self.handles = {}  # 存储滑块对象
        self.dragging_handle = None  # 当前正在拖拽的滑�?        self.drag_start_pos = None  # 拖拽起始位置
        self.drag_start_coords = None  # 拖拽起始时的选框坐标

        # 比例锁定相关
        self.ratio_handler = CropRatioHandler()

        # 选框移动相关
        self.is_moving_selection = False
        self.move_start_pos = None
        self.move_start_coords = None

        # 图片显示位置（用于坐标转换）
        self.image_x = 0
        self.image_y = 0
        self.image_width = 0
        self.image_height = 0

        # 初始化裁剪状态管理器
        self.crop_state = CropState(max_history=100)

        # 初始化筛选逻辑：使用策略模块确定裁剪策�?        from function.crop_strategy import determine_crop_strategy
        self.is_base_image, self.min_image_path, min_idx = determine_crop_strategy(self.image_paths, current_index)
        self.min_image_size = min_idx  # 存储索引而不是尺�?
        # 创建对话框窗�?- 设置�?1280x720
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Crop Animation - High Definition")
        self.dialog.geometry("1280x720")
        self.dialog.minsize(800, 600)  # 设置最小尺寸防止布局崩溃

        # 设置模�?        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 字体增强
        self.ui_font = ("Microsoft YaHei UI", 10)
        self.header_font = ("Microsoft YaHei UI", 12, "bold")

        self.setup_ui()
        self.center_window()

        # 绑定键盘快捷�?        from function.history_manager import undo_crop, redo_crop
        self.dialog.bind('<Control-z>', lambda e: undo_crop(self.crop_state))
        self.dialog.bind('<Control-y>', lambda e: redo_crop(self.crop_state))

        # 如果提供了图片路径，加载图片
        if self.image_path:
            from function.image_utils import load_image
            load_image(self, self.image_path)
        
    def center_window(self):
        """将窗口居中显�?""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def display_image(self):
        """显示图片"""
        if not hasattr(self, 'original_image'):
            return

        try:
            img = self.original_image
            orig_width, orig_height = img.size

            # 获取预览Canvas的实际尺�?            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width() - 20
            canvas_height = self.canvas.winfo_height() - 20

            # 如果没有设置过缩放比例，则计算适应Canvas的缩放比�?            if not hasattr(self, 'preview_scale') or self.preview_scale == 0:
                self.preview_scale = calculate_scale_to_fit(orig_width, orig_height, canvas_width, canvas_height)
                self.initial_scale = self.preview_scale  # 保存初始缩放比例

            # 计算实际显示尺寸 - 委托给业务逻辑模块
            from function.crop_logic import calculate_scaled_dimensions
            scaled_width, scaled_height, scale = calculate_scaled_dimensions(
                orig_width, orig_height, canvas_width, canvas_height
            )
            if scale:  # 如果业务逻辑模块返回了scale�?                self.preview_scale = scale

            # 使用 image_utils 模块调整图片大小
            img_resized = resize_image(img, scaled_width, scaled_height)

            # 使用 image_utils 模块创建PhotoImage对象
            self.current_photo = create_photo_image(img_resized)
            self.base_photo = self.current_photo  # 保存基础图片

            # 清除Canvas并显示图�?            self.canvas.delete("all")

            # 计算图片在Canvas中的位置
            # 使用Canvas的实际可见区域中�?            actual_canvas_width = self.canvas.winfo_width()
            actual_canvas_height = self.canvas.winfo_height()

            # 判断图片是否大于 Canvas
            if scaled_width > actual_canvas_width or scaled_height > actual_canvas_height:
                # 图片大于 Canvas，使�?NW 锚点�?(0,0) 开始显示，启用滚动
                self.image_x = 0
                self.image_y = 0
                anchor = tk.NW
                # 更新滚动区域为实际图片尺�?                self.canvas.configure(scrollregion=(0, 0, scaled_width, scaled_height))
            else:
                # 图片小于或等�?Canvas，居中显示，禁用滚动
                self.image_x = actual_canvas_width // 2
                self.image_y = actual_canvas_height // 2
                anchor = tk.CENTER
                # 设置滚动区域�?Canvas 大小，禁用滚�?                self.canvas.configure(scrollregion=(0, 0, actual_canvas_width, actual_canvas_height))

            self.image_width = scaled_width
            self.image_height = scaled_height

            self.canvas.create_image(self.image_x, self.image_y, image=self.current_photo, anchor=anchor)

            # 更新裁剪参数为图片原始尺�?            self.x1_var.set("0")
            self.y1_var.set("0")
            self.x2_var.set(str(orig_width))
            self.y2_var.set(str(orig_height))

            # 绑定选项变化事件（只绑定一次）
            if not hasattr(self, '_trace_ids'):
                self._trace_ids = []
                self._trace_ids.append(self.show_cropped_var.trace_add('write', lambda *args: self.apply_display_options()))
                self._trace_ids.append(self.show_prev_var.trace_add('write', lambda *args: self.apply_display_options()))
                self._trace_ids.append(self.show_next_var.trace_add('write', lambda *args: self.apply_display_options()))
                self._trace_ids.append(self.show_first_var.trace_add('write', lambda *args: self.apply_display_options()))

            # 初始显示选框
            self.draw_selection_box()

        except Exception as e:
            print(f"无法显示图片: {e}")
        
    def setup_ui(self):
        """使用 Grid 权重布局实现自适应"""
        # 配置全局行列权重
        self.dialog.columnconfigure(0, weight=1) # 左侧预览区权重（可伸缩）
        self.dialog.columnconfigure(1, weight=0) # 右侧控制区权重（固定宽度�?        self.dialog.rowconfigure(0, weight=1)    # 主内容区权重

        # --- 1. 左侧预览区域 (Canvas) ---
        self.preview_frame = ttk.LabelFrame(self.dialog, text="预览视图 (Preview)", padding=10)
        self.preview_frame.grid(row=0, column=0, padx=(20, 0), pady=20, sticky="nsew")

        # 创建 Canvas 和滚动条
        self.canvas = tk.Canvas(self.preview_frame, bg="#333333", highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # 布局 Canvas 和滚动条
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        # 配置权重
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)

        # 绑定鼠标事件用于选框和滑�?        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)  # 统一处理左键按下
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)  # 统一处理左键拖拽
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)  # 统一处理左键释放
        self.canvas.bind("<Motion>", self.on_mouse_move)  # 鼠标移动事件，用于改变光标形�?
        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", lambda e: self.ratio_handler.on_mousewheel(e, self.zoom_in, self.zoom_out))  # Windows
        self.canvas.bind("<Button-4>", lambda e: self.ratio_handler.on_mousewheel(e, self.zoom_in, self.zoom_out))   # Linux 上滚
        self.canvas.bind("<Button-5>", lambda e: self.ratio_handler.on_mousewheel(e, self.zoom_in, self.zoom_out))   # Linux 下滚

        # 绘制占位辅助�?        self.canvas.create_text(450, 300, text="图像预览区域\n(Image Preview Area)", fill="white", justify="center")

        # --- 2. 右侧控制面板 ---
        self.right_panel = ttk.Frame(self.dialog, padding=20)
        self.right_panel.grid(row=0, column=1, sticky="n", padx=0)  # 强制左右各留 50 像素
        
        # 配置右侧面板的列权重
        self.right_panel.columnconfigure(0, weight=0)  # 组件区（固定宽度�?        
        # 创建一个容器来包裹三个模块
        self.modules_container = ttk.Frame(self.right_panel, width=320)  # 设置固定宽度
        self.modules_container.grid(row=0, column=0, sticky="n")  # 去掉 e/w，不左右拉伸
        
        # 2.1 坐标输入�?        coord_title = "裁剪坐标设置" + ("（基准图片）" if self.is_base_image else "")
        coord_group = ttk.LabelFrame(self.modules_container, text=coord_title, padding=5)
        coord_group.pack(fill="x", pady=(0, 15), ipadx=10)
        
        # 配置列权重，禁用所有列的拉伸，确保固定宽度
        coord_group.columnconfigure(0, weight=0)  # 标签�?        coord_group.columnconfigure(1, weight=0)  # 输入�?列（固定宽度�?        coord_group.columnconfigure(2, weight=0)  # 中间标签�?        coord_group.columnconfigure(3, weight=0)  # 输入�?列（固定宽度�?
        # 第一组：起始�?(X, Y)
        ttk.Label(coord_group, text="起始位置 (Top-Left):", font=self.ui_font).grid(row=0, column=0, columnspan=4, sticky="w", padx=5)
        self.x1_var = tk.StringVar(value="0")
        self.y1_var = tk.StringVar(value="0")
        self.create_spin_row(coord_group, 1, "X:", self.x1_var, "Y:", self.y1_var)

        # 第二组：结束�?(X, Y)
        ttk.Label(coord_group, text="结束位置 (Bottom-Right):", font=self.ui_font).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0), padx=5)
        self.x2_var = tk.StringVar(value="100")
        self.y2_var = tk.StringVar(value="100")
        self.create_spin_row(coord_group, 3, "X:", self.x2_var, "Y:", self.y2_var)

        # 实时尺寸显示
        size_frame = ttk.Frame(coord_group)
        size_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 0), padx=5)
        self.size_label = ttk.Label(size_frame, text="尺寸: 100 x 100 像素", font=("Microsoft YaHei UI", 9))
        self.size_label.pack(anchor="w")

        # 2.2 预设比例�?        ratio_group = ttk.LabelFrame(self.modules_container, text="预设比例", padding=5)
        ratio_group.pack(fill="x", pady=(0, 15), ipadx=10)
        
        # 配置列权重，禁用所有列的拉伸，确保固定宽度
        ratio_group.columnconfigure(0, weight=0)  # 左列按钮
        ratio_group.columnconfigure(1, weight=0)  # 右列按钮

        self.ratio_var = tk.StringVar(value="free")
        from function.ui_operations import on_ratio_change
        self.ratio_var.trace_add('write', lambda *args: on_ratio_change(
            self.ratio_var,
            self.x1_var,
            self.y1_var,
            self.x2_var,
            self.y2_var,
            self.ratio_handler,
            getattr(self, 'locked_ratio_label', None),
            self.draw_selection_box,
            lambda: self.ratio_handler.update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)
        ))

        ratios = [
            ("自由", "free"),
            ("锁定比例", "lock_current"),
            ("1:1", "1:1"),
            ("16:9", "16:9"),
            ("4:3", "4:3"),
            ("3:2", "3:2"),
            ("黄金分割", "1.618")
        ]

        # 使用 grid 布局实现双列，左对齐
        for i, (text, value) in enumerate(ratios):
            row = i // 2
            col = i % 2
            
            if value == "lock_current":
                # �?锁定当前比例"添加比例显示标签
                rb_frame = ttk.Frame(ratio_group)
                rb_frame.grid(row=row, column=col, sticky="w", padx=5, pady=2)
                rb = ttk.Radiobutton(rb_frame, text=text, variable=self.ratio_var, value=value)
                rb.pack(side="left")
                self.locked_ratio_label = ttk.Label(rb_frame, text="", foreground="blue")
                self.locked_ratio_label.pack(side="left", padx=(10, 0))
            else:
                rb = ttk.Radiobutton(ratio_group, text=text, variable=self.ratio_var, value=value)
                rb.grid(row=row, column=col, sticky="w", padx=5, pady=2)

        # 2.3 选项�?        option_group = ttk.LabelFrame(self.modules_container, text="显示选项", padding=5)
        option_group.pack(fill="x", pady=(0, 15), ipadx=10)
        
        # 配置列权重，禁用拉伸，确保固定宽�?        option_group.columnconfigure(0, weight=0)  # 复选框�?        
        self.show_cropped_var = tk.BooleanVar()
        self.show_prev_var = tk.BooleanVar()
        self.show_next_var = tk.BooleanVar()
        self.show_first_var = tk.BooleanVar()

        opts = [
            ("显示裁剪后状�?(Show As Cropped)", self.show_cropped_var),
            ("显示上一�?(Show Previous)", self.show_prev_var),
            ("显示下一�?(Show Next)", self.show_next_var),
            ("显示第一�?(Show First)", self.show_first_var)
        ]
        
        for i, (text, var) in enumerate(opts):
            cb = ttk.Checkbutton(option_group, text=text, variable=var)
            cb.grid(row=i, column=0, sticky="w", padx=5, pady=5)

        # --- 操作按钮区（紧跟在显示选项下方�?--
        # 添加分隔�?        ttk.Separator(self.modules_container, orient="horizontal").pack(fill="x", pady=(10, 10))
        
        # 第一行按钮容�?        btn_row1 = ttk.Frame(self.modules_container)
        btn_row1.pack(fill="x", pady=(0, 5))

        self.fit_btn = ttk.Button(btn_row1, text="�?, width=5, command=lambda: self.ratio_handler.fit_to_window(self))
        self.fit_btn.pack(side="left", padx=5)
        self.create_tooltip(self.fit_btn, "适应窗口 (Fit)")

        self.reset_btn = ttk.Button(btn_row1, text="🔄", width=5, command=self.reset_zoom)
        self.reset_btn.pack(side="left", padx=5)
        self.create_tooltip(self.reset_btn, "重置缩放 (100%)")
        
        # 第二行按钮容�?        btn_row2 = ttk.Frame(self.modules_container)
        btn_row2.pack(fill="x", pady=(0, 10))

        from function.history_manager import undo_crop, redo_crop
        self.undo_btn = ttk.Button(btn_row2, text="↩️", width=10, command=lambda: undo_crop(self.crop_state))
        self.undo_btn.pack(side="left", padx=5)
        self.create_tooltip(self.undo_btn, "撤销 (Ctrl+Z)")

        self.redo_btn = ttk.Button(btn_row2, text="↪️", width=10, command=lambda: redo_crop(self.crop_state))
        self.redo_btn.pack(side="left", padx=5)
        self.create_tooltip(self.redo_btn, "重做 (Ctrl+Y)")

        # 分隔�?        ttk.Separator(btn_row2, orient="vertical").pack(side="left", fill=tk.Y, padx=5)

        self.ok_btn = ttk.Button(btn_row2, text="�?, width=15, command=self.ok_clicked)
        self.ok_btn.pack(side="left", padx=5)
        self.create_tooltip(self.ok_btn, "确定 (OK)")

        self.cancel_btn = ttk.Button(btn_row2, text="�?, width=15, command=self.cancel_clicked)
        self.cancel_btn.pack(side="left", padx=5)
        self.create_tooltip(self.cancel_btn, "取消 (Cancel)")

    def create_spin_row(self, parent, row, label1, var1, label2, var2):
        """辅助函数：创建一行两个带标签的微调框"""
        ttk.Label(parent, text=label1).grid(row=row, column=0, sticky="w", padx=5)
        s1 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var1, width=6)
        s1.grid(row=row, column=1, sticky="w", padx=(2, 5), pady=5)
        # 绑定回车键更新尺寸显�?        from function.ui_operations import update_size_label
        s1.bind('<Return>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))
        s1.bind('<FocusOut>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))

        ttk.Label(parent, text=label2).grid(row=row, column=2, sticky="w", padx=5)
        s2 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var2, width=6)
        s2.grid(row=row, column=3, sticky="w", padx=(2, 5), pady=5)
        # 绑定回车键更新尺寸显�?        s2.bind('<Return>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))
        s2.bind('<FocusOut>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))

    def create_tooltip(self, widget, text):
        """创建鼠标悬浮提示"""
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

    def reset_zoom(self):
        """重置缩放 - 按原尺寸大小显示图片"""
        if not hasattr(self, 'original_image'):
            messagebox.showinfo("提示", "请先加载图片")
            return

        try:
            # 设置缩放比例�?.0，即原尺寸显�?            self.preview_scale = 1.0

            # 重新显示图片
            self.display_image()

        except Exception as e:
            messagebox.showerror("错误", f"重置缩放失败: {str(e)}")

    def zoom_in(self):
        """放大图片"""
        if not hasattr(self, 'original_image'):
            return

        try:
            if self.preview_scale < 5.0:
                self.preview_scale *= 1.25
                self.display_image()
        except Exception as e:
            print(f"放大失败: {e}")

    def zoom_out(self):
        """缩小图片"""
        if not hasattr(self, 'original_image'):
            return

        try:
            if self.preview_scale > 0.1:
                self.preview_scale /= 1.25
                self.display_image()
        except Exception as e:
            print(f"缩小失败: {e}")

    def ok_clicked(self):
        try:
            # 获取裁剪坐标
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            # 保存当前裁剪状态到历史记录
            from function.history_manager import save_crop_state
            save_crop_state(self.crop_state)

            # 如果是多张图片且是基准图片，直接使用绝对像素坐标
            if len(self.image_paths) > 1 and self.is_base_image:
                # 获取基准图片的尺�?                base_width = self.original_image.width
                base_height = self.original_image.height

                # 添加确认提示
                confirm = messagebox.askyesno(
                    "确认裁剪",
                    f"将使用相同的像素坐标裁剪选中的所�?{len(self.image_paths)} 张图片\n\n"
                    f"基准图片尺寸: {base_width} x {base_height}\n"
                    f"裁剪区域: ({x1}, {y1}) �?({x2}, {y2})\n"
                    f"裁剪尺寸: {x2-x1} x {y2-y1}\n\n"
                    f"所有图片将使用相同的像素坐标进行裁剪\n"
                    f"最终生成的裁剪图片分辨率将完全相同\n\n"
                    f"此操作可撤销/重做\n"
                    f"是否继续�?
                )

                if not confirm:
                    # 如果用户取消，撤销刚才保存的状�?                    self.crop_state.history_manager.undo({
                        'crop_results': {},
                        'crop_coords': {}
                    })
                    return

                # 保存裁剪坐标
                for img_path in self.image_paths:
                    self.crop_state.set_crop_coords(img_path, (x1, y1, x2, y2))

                # 保存绝对像素坐标到结果中
                self.result = {
                    'start': (x1, y1),
                    'end': (x2, y2),
                    'is_base_image': True,
                    'crop_coords': {path: self.crop_state.get_crop_coords(path) for path in self.image_paths},
                    'options': {
                        'cropped': self.show_cropped_var.get(),
                        'prev': self.show_prev_var.get(),
                        'next': self.show_next_var.get(),
                        'first': self.show_first_var.get()
                    }
                }
            else:
                # 单张图片或非基准图片，直接使用像素坐�?                # 保存裁剪坐标
                self.crop_state.set_crop_coords(self.image_path, (x1, y1, x2, y2))

                self.result = {
                    'start': (x1, y1),
                    'end': (x2, y2),
                    'crop_coords': {self.image_path: (x1, y1, x2, y2)},
                    'options': {
                        'cropped': self.show_cropped_var.get(),
                        'prev': self.show_prev_var.get(),
                        'next': self.show_next_var.get(),
                        'first': self.show_first_var.get()
                    }
                }

            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字坐标")
    
    def cancel_clicked(self):
        self.result = None
        self.dialog.destroy()
        
    def show(self):
        self.dialog.wait_window()
        return self.result

    def on_canvas_press(self, event):
        """统一处理Canvas上的鼠标按下事件"""
        if not hasattr(self, 'original_image'):
            return

        # 首先检查是否点击了滑块
        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            if "handle" in tags:
                for tag in tags:
                    if tag in self.handles and self.handles[tag] == item:
                        self.dragging_handle = tag
                        self.drag_start_pos = (event.x, event.y)
                        # 保存当前选框坐标
                        self.drag_start_coords = (
                            int(self.x1_var.get()),
                            int(self.y1_var.get()),
                            int(self.x2_var.get()),
                            int(self.y2_var.get())
                        )
                        return

        # 检查是否点击了选框内部（用于移动选框�?        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            img_left = self.image_x - self.image_width // 2
            img_top = self.image_y - self.image_height // 2

            scaled_x1 = img_left + x1 * self.preview_scale
            scaled_y1 = img_top + y1 * self.preview_scale
            scaled_x2 = img_left + x2 * self.preview_scale
            scaled_y2 = img_top + y2 * self.preview_scale

            # 检查点击是否在选框内部
            if (scaled_x1 < event.x < scaled_x2 and
                scaled_y1 < event.y < scaled_y2):
                self.is_moving_selection = True
                self.move_start_pos = (event.x, event.y)
                self.move_start_coords = (x1, y1, x2, y2)
                return
        except:
            pass

        # 如果没有点击滑块或选框内部，则检查是否在图片范围内进行选框绘制
        img_left = self.image_x - self.image_width // 2
        img_top = self.image_y - self.image_height // 2
        img_right = self.image_x + self.image_width // 2
        img_bottom = self.image_y + self.image_height // 2

        if img_left <= event.x <= img_right and img_top <= event.y <= img_bottom:
            self.is_selecting = True
            self.selection_start = (event.x, event.y)

    def on_canvas_drag(self, event):
        """统一处理Canvas上的鼠标拖拽事件"""
        # 如果正在拖拽滑块
        if self.dragging_handle:
            self.handle_drag(event)
            return

        # 如果正在移动选框
        if self.is_moving_selection:
            self.move_selection(event)
            return

        # 如果正在绘制选框
        if not self.is_selecting or not self.selection_start:
            return

        # 删除之前的选框
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        # 绘制新的选框
        x1, y1 = self.selection_start
        x2, y2 = event.x, event.y

        # 限制选框在图片范围内
        img_left = self.image_x - self.image_width // 2
        img_top = self.image_y - self.image_height // 2
        img_right = self.image_x + self.image_width // 2
        img_bottom = self.image_y + self.image_height // 2

        x1 = max(img_left, min(x1, img_right))
        y1 = max(img_top, min(y1, img_bottom))
        x2 = max(img_left, min(x2, img_right))
        y2 = max(img_top, min(y2, img_bottom))

        # 绘制选框（红色虚线）
        self.selection_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red",
            width=2,
            dash=(4, 4)
        )

    def move_selection(self, event):
        """移动选框"""
        try:
            # 计算鼠标移动的偏移量
            dx = event.x - self.move_start_pos[0]
            dy = event.y - self.move_start_pos[1]

            # 转换为原始图片坐标的偏移�?            img_dx = int(dx / self.preview_scale)
            img_dy = int(dy / self.preview_scale)

            x1, y1, x2, y2 = self.move_start_coords

            # 移动选框
            new_x1 = x1 + img_dx
            new_y1 = y1 + img_dy
            new_x2 = x2 + img_dx
            new_y2 = y2 + img_dy

            # 确保选框在图片范围内 - 委托给业务逻辑模块
            from function.crop_logic import validate_crop_coordinates
            new_x1, new_y1, new_x2, new_y2 = validate_crop_coordinates(
                new_x1, new_y1, new_x2, new_y2, self.original_image.width, self.original_image.height
            )

            # 更新输入�?            self.x1_var.set(str(new_x1))
            self.y1_var.set(str(new_y1))
            self.x2_var.set(str(new_x2))
            self.y2_var.set(str(new_y2))

            # 重绘选框和滑�?            self.draw_selection_box()
            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)

        except Exception as e:
            print(f"移动选框失败: {e}")

    def handle_drag(self, event):
        """滑块拖拽事件"""
        try:
            # 计算鼠标移动的偏移量
            dx = event.x - self.drag_start_pos[0]
            dy = event.y - self.drag_start_pos[1]

            # 转换为原始图片坐标的偏移�?            img_dx = int(dx / self.preview_scale)
            img_dy = int(dy / self.preview_scale)

            x1, y1, x2, y2 = self.drag_start_coords

            # 根据滑块类型调整选框
            if self.dragging_handle == 'nw':  # 左上�?                x1 = max(0, x1 + img_dx)
                y1 = max(0, y1 + img_dy)
            elif self.dragging_handle == 'n':  # 上边
                y1 = max(0, y1 + img_dy)
            elif self.dragging_handle == 'ne':  # 右上�?                x2 = min(self.original_image.width, x2 + img_dx)
                y1 = max(0, y1 + img_dy)
            elif self.dragging_handle == 'e':  # 右边
                x2 = min(self.original_image.width, x2 + img_dx)
            elif self.dragging_handle == 'se':  # 右下�?                x2 = min(self.original_image.width, x2 + img_dx)
                y2 = min(self.original_image.height, y2 + img_dy)
            elif self.dragging_handle == 's':  # 下边
                y2 = min(self.original_image.height, y2 + img_dy)
            elif self.dragging_handle == 'sw':  # 左下�?                x1 = max(0, x1 + img_dx)
                y2 = min(self.original_image.height, y2 + img_dy)
            elif self.dragging_handle == 'w':  # 左边
                x1 = max(0, x1 + img_dx)

            # 如果锁定了比例，调整尺寸以保持比�?            if self.ratio_handler.is_ratio_locked and self.ratio_handler.ratio_value:
                # 使用比例处理器调整坐�?- 委托给业务逻辑模块
                x1, y1, x2, y2 = self.ratio_handler.adjust_coords_by_ratio(x1, y1, x2, y2, self.dragging_handle)

            # 确保选框有效（宽度、高度至少为1�? 委托给业务逻辑模块
            from function.crop_logic import validate_crop_coordinates
            x1, y1, x2, y2 = validate_crop_coordinates(
                x1, y1, x2, y2, self.original_image.width, self.original_image.height
            )

            # 更新输入�?            self.x1_var.set(str(x1))
            self.y1_var.set(str(y1))
            self.x2_var.set(str(x2))
            self.y2_var.set(str(y2))

            # 重绘选框和滑�?            self.draw_selection_box()
            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)

        except Exception as e:
            print(f"滑块拖拽失败: {e}")

    def on_canvas_release(self, event):
        """统一处理Canvas上的鼠标释放事件"""
        # 如果正在拖拽滑块
        if self.dragging_handle:
            self.dragging_handle = None
            self.drag_start_pos = None
            self.drag_start_coords = None
            return

        # 如果正在移动选框
        if self.is_moving_selection:
            self.is_moving_selection = False
            self.move_start_pos = None
            self.move_start_coords = None
            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)
            return

        # 如果正在绘制选框
        if not self.is_selecting or not self.selection_start:
            return

        self.is_selecting = False

        # 计算选框在原始图片中的坐�?        if self.selection_rect:
            coords = self.canvas.coords(self.selection_rect)
            if len(coords) == 4:
                x1, y1, x2, y2 = coords

                # 转换为原始图片坐�?- 委托给业务逻辑模块
                orig_x1, orig_y1 = convert_canvas_to_image_coords(
                    x1, y1, self.image_x, self.image_y, self.preview_scale, self.image_width, self.image_height
                )
                orig_x2, orig_y2 = convert_canvas_to_image_coords(
                    x2, y2, self.image_x, self.image_y, self.preview_scale, self.image_width, self.image_height
                )

                # 确保坐标顺序正确 - 委托给业务逻辑模块
                from function.crop_logic import validate_crop_coordinates
                orig_x1, orig_y1, orig_x2, orig_y2 = validate_crop_coordinates(
                    orig_x1, orig_y1, orig_x2, orig_y2, self.original_image.width, self.original_image.height
                )

                # 更新输入�?                self.x1_var.set(str(orig_x1))
                self.y1_var.set(str(orig_y1))
                self.x2_var.set(str(orig_x2))
                self.y2_var.set(str(orig_y2))

                # 删除临时选框，绘制永久选框
                self.canvas.delete(self.selection_rect)
                self.selection_rect = None

                # 应用显示选项
                self.apply_display_options()

            # 更新尺寸显示
            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)

    def on_mouse_move(self, event):
        """鼠标移动事件，根据位置改变光标形�?""
        # 检查是否在滑块�?        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            if "handle" in tags:
                for tag in tags:
                    if tag in self.handles and self.handles[tag] == item:
                        # 根据滑块类型设置双向箭头光标
                        cursor_map = {
                            'nw': 'size_nw_se',  # 左上-右下斜对角双向箭�?                            'n': 'sb_v_double_arrow',  # 垂直双向箭头
                            'ne': 'size_ne_sw',  # 右上-左下斜对角双向箭�?                            'e': 'sb_h_double_arrow',  # 水平双向箭头
                            'se': 'size_nw_se',  # 左上-右下斜对角双向箭�?                            's': 'sb_v_double_arrow',  # 垂直双向箭头
                            'sw': 'size_ne_sw',  # 右上-左下斜对角双向箭�?                            'w': 'sb_h_double_arrow'  # 水平双向箭头
                        }
                        self.canvas.config(cursor=cursor_map.get(tag, 'arrow'))
                        return

        # 如果不在滑块上，恢复默认光标
        self.canvas.config(cursor='arrow')

    def apply_display_options(self):
        """应用显示选项"""
        if not hasattr(self, 'original_image'):
            return

        try:
            # 获取裁剪区域
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            orig_width, orig_height = self.original_image.size

            # 恢复基础图片
            self.canvas.delete("all")
            if self.base_photo:
                self.canvas.create_image(self.image_x, self.image_y, image=self.base_photo, anchor=tk.CENTER)

            # 显示裁剪后的状�?            if self.show_cropped_var.get():
                # 使用 image_utils 模块裁剪图片
                cropped_img = crop_image(self.original_image, x1, y1, x2, y2)
                # 创建半透明遮罩效果
                mask = Image.new('RGBA', (orig_width, orig_height), (0, 0, 0, 180))
                mask.paste(cropped_img, (x1, y1))
                mask = mask.convert('RGB')

                # 转换为PhotoImage显示
                scaled_width = int(orig_width * self.preview_scale)
                scaled_height = int(orig_height * self.preview_scale)
                mask_resized = resize_image(mask, scaled_width, scaled_height)
                self.current_photo = create_photo_image(mask_resized)
                self.canvas.delete("all")
                self.canvas.create_image(self.image_x, self.image_y, image=self.current_photo, anchor=tk.CENTER)

            # 显示上一�?            elif self.show_prev_var.get() and self.image_paths and self.current_index > 0:
                prev_path = self.image_paths[self.current_index - 1]
                self.ratio_handler.display_reference_image(self, prev_path)

            # 显示下一�?            elif self.show_next_var.get() and self.image_paths and self.current_index < len(self.image_paths) - 1:
                next_path = self.image_paths[self.current_index + 1]
                self.ratio_handler.display_reference_image(self, next_path)

            # 显示第一�?            elif self.show_first_var.get() and self.image_paths:
                first_path = self.image_paths[0]
                self.ratio_handler.display_reference_image(self, first_path)

            # 始终显示选框
            self.draw_selection_box()

        except Exception as e:
            print(f"应用显示选项失败: {e}")

    def draw_selection_box(self):
        """绘制选框和滑�?""
        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            # 根据图片的显示位置计算图片左上角坐标
            # 如果 image_x �?image_y 都大�?0，说明图片是居中显示（CENTER 锚点�?            # 如果 image_x �?image_y 都为 0，说明图片是从左上角开始显示（NW 锚点�?            if self.image_x > 0 and self.image_y > 0:
                # 居中显示，计算图片左上角坐标
                img_left = self.image_x - self.image_width // 2
                img_top = self.image_y - self.image_height // 2
            else:
                # 从左上角开始显�?                img_left = self.image_x
                img_top = self.image_y

            scaled_x1 = img_left + x1 * self.preview_scale
            scaled_y1 = img_top + y1 * self.preview_scale
            scaled_x2 = img_left + x2 * self.preview_scale
            scaled_y2 = img_top + y2 * self.preview_scale

            # 删除旧选框和滑�?            self.canvas.delete("selection_box")
            self.canvas.delete("handle")

            # 绘制新选框（红色虚线）
            self.canvas.create_rectangle(
                scaled_x1, scaled_y1, scaled_x2, scaled_y2,
                outline="red",
                width=3,
                dash=(4, 4),
                tags="selection_box"
            )

            # 绘制8个滑块（4个角 + 4个边中间�?            handle_size = 10
            handle_offset = handle_size // 2

            # 滑块位置
            handles = {
                'nw': (scaled_x1 - handle_offset, scaled_y1 - handle_offset, scaled_x1 + handle_offset, scaled_y1 + handle_offset),
                'n':  (scaled_x1 + (scaled_x2 - scaled_x1) // 2 - handle_offset, scaled_y1 - handle_offset,
                       scaled_x1 + (scaled_x2 - scaled_x1) // 2 + handle_offset, scaled_y1 + handle_offset),
                'ne': (scaled_x2 - handle_offset, scaled_y1 - handle_offset, scaled_x2 + handle_offset, scaled_y1 + handle_offset),
                'e':  (scaled_x2 - handle_offset, scaled_y1 + (scaled_y2 - scaled_y1) // 2 - handle_offset,
                       scaled_x2 + handle_offset, scaled_y1 + (scaled_y2 - scaled_y1) // 2 + handle_offset),
                'se': (scaled_x2 - handle_offset, scaled_y2 - handle_offset, scaled_x2 + handle_offset, scaled_y2 + handle_offset),
                's':  (scaled_x1 + (scaled_x2 - scaled_x1) // 2 - handle_offset, scaled_y2 - handle_offset,
                       scaled_x1 + (scaled_x2 - scaled_x1) // 2 + handle_offset, scaled_y2 + handle_offset),
                'sw': (scaled_x1 - handle_offset, scaled_y2 - handle_offset, scaled_x1 + handle_offset, scaled_y2 + handle_offset),
                'w':  (scaled_x1 - handle_offset, scaled_y1 + (scaled_y2 - scaled_y1) // 2 - handle_offset,
                       scaled_x1 + handle_offset, scaled_y1 + (scaled_y2 - scaled_y1) // 2 + handle_offset)
            }

            # 绘制滑块
            for handle_name, coords in handles.items():
                handle_id = self.canvas.create_rectangle(
                    coords[0], coords[1], coords[2], coords[3],
                    fill="yellow",
                    outline="red",
                    width=2,
                    tags=("handle", handle_name)
                )
                self.handles[handle_name] = handle_id

        except Exception as e:
            print(f"绘制选框失败: {e}")

    def show_crop_dialog(parent, image_path=None, image_paths=None, current_index=0):
    """显示裁剪对话框的便捷函数"""
    dialog = CropDialog(parent, image_path, image_paths, current_index)
    return dialog.show()
