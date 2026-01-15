# -*- coding: utf-8 -*-
"""
裁剪动画对话框模块 - 高清自适应版
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
from functions.image_utils import (
    load_image,
    resize_image,
    create_photo_image,
    calculate_scale_to_fit,
    calculate_scale_to_fill,
    crop_image,
    auto_crop_image
)

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
        self.dragging_handle = None  # 当前正在拖拽的滑块
        self.drag_start_pos = None  # 拖拽起始位置
        self.drag_start_coords = None  # 拖拽起始时的选框坐标

        # 比例锁定相关
        self.is_ratio_locked = False
        self.ratio_value = None  # 锁定的比例值

        # 选框移动相关
        self.is_moving_selection = False
        self.move_start_pos = None
        self.move_start_coords = None

        # 图片显示位置（用于坐标转换）
        self.image_x = 0
        self.image_y = 0
        self.image_width = 0
        self.image_height = 0
        
        # 创建对话框窗口 - 设置为 1280x720
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Crop Animation - High Definition")
        self.dialog.geometry("1280x720")
        self.dialog.minsize(800, 600)  # 设置最小尺寸防止布局崩溃
        
        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 字体增强
        self.ui_font = ("Microsoft YaHei UI", 10)
        self.header_font = ("Microsoft YaHei UI", 12, "bold")
        
        self.setup_ui()
        self.center_window()

        # 如果提供了图片路径，加载图片
        if self.image_path:
            self.load_image()
        
    def center_window(self):
        """将窗口居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def load_image(self):
        """加载图片到预览区域"""
        if not self.image_path:
            return

        # 使用 image_utils 模块加载图片
        self.original_image = load_image(self.image_path)
        if self.original_image:
            # 先显示图片
            self.display_image()
            # 然后自动适应窗口
            self.fit_to_window()
        else:
            print(f"无法加载图片: {self.image_path}")

    def display_image(self):
        """显示图片"""
        if not hasattr(self, 'original_image'):
            return

        try:
            img = self.original_image
            orig_width, orig_height = img.size

            # 获取预览Canvas的实际尺寸
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width() - 20
            canvas_height = self.canvas.winfo_height() - 20

            # 如果没有设置过缩放比例，则计算适应Canvas的缩放比例
            if not hasattr(self, 'preview_scale') or self.preview_scale == 0:
                self.preview_scale = calculate_scale_to_fit(orig_width, orig_height, canvas_width, canvas_height)
                self.initial_scale = self.preview_scale  # 保存初始缩放比例

            # 计算实际显示尺寸
            scaled_width = int(orig_width * self.preview_scale)
            scaled_height = int(orig_height * self.preview_scale)

            # 使用 image_utils 模块调整图片大小
            img_resized = resize_image(img, scaled_width, scaled_height)

            # 使用 image_utils 模块创建PhotoImage对象
            self.current_photo = create_photo_image(img_resized)
            self.base_photo = self.current_photo  # 保存基础图片

            # 清除Canvas并显示图片
            self.canvas.delete("all")

            # 计算图片在Canvas中的位置
            # 当图片大于Canvas时，使用NW锚点，从(0,0)开始显示
            # 当图片小于Canvas时，居中显示
            if scaled_width > canvas_width or scaled_height > canvas_height:
                # 图片大于窗口，放置在左上角（使用NW锚点）
                self.image_x = 0
                self.image_y = 0
                anchor = tk.NW
            else:
                # 图片小于窗口，居中显示（使用CENTER锚点）
                # 使用Canvas的实际可见区域中心
                actual_canvas_width = self.canvas.winfo_width()
                actual_canvas_height = self.canvas.winfo_height()
                self.image_x = actual_canvas_width // 2
                self.image_y = actual_canvas_height // 2
                anchor = tk.CENTER

            self.image_width = scaled_width
            self.image_height = scaled_height

            self.canvas.create_image(self.image_x, self.image_y, image=self.current_photo, anchor=anchor)

            # 更新滚动区域
            self.canvas.configure(scrollregion=(0, 0, scaled_width, scaled_height))

            # 更新裁剪参数为图片原始尺寸
            self.x1_var.set("0")
            self.y1_var.set("0")
            self.x2_var.set(str(orig_width))
            self.y2_var.set(str(orig_height))

            # 绑定选项变化事件（只绑定一次）
            if not hasattr(self, '_trace_ids'):
                self._trace_ids = []
                self._trace_ids.append(self.show_cropped_var.trace_add('write', self.on_option_change))
                self._trace_ids.append(self.show_prev_var.trace_add('write', self.on_option_change))
                self._trace_ids.append(self.show_next_var.trace_add('write', self.on_option_change))
                self._trace_ids.append(self.show_first_var.trace_add('write', self.on_option_change))

            # 初始显示选框
            self.draw_selection_box()

        except Exception as e:
            print(f"无法显示图片: {e}")
        
    def setup_ui(self):
        """使用 Grid 权重布局实现自适应"""
        # 配置全局行列权重
        self.dialog.columnconfigure(0, weight=3) # 左侧预览区权重
        self.dialog.columnconfigure(1, weight=1) # 右侧控制区权重
        self.dialog.rowconfigure(0, weight=1)    # 主内容区权重
        self.dialog.rowconfigure(1, weight=0)    # 底部按钮区固定

        # --- 1. 左侧预览区域 (Canvas) ---
        self.preview_frame = ttk.LabelFrame(self.dialog, text="预览视图 (Preview)", padding=10)
        self.preview_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

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

        # 绑定鼠标事件用于选框和滑块
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)  # 统一处理左键按下
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)  # 统一处理左键拖拽
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)  # 统一处理左键释放
        self.canvas.bind("<Motion>", self.on_mouse_move)  # 鼠标移动事件，用于改变光标形状

        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mousewheel)   # Linux 上滚
        self.canvas.bind("<Button-5>", self.on_mousewheel)   # Linux 下滚

        # 绘制占位辅助线
        self.canvas.create_text(450, 300, text="图像预览区域\n(Image Preview Area)", fill="white", justify="center")

        # --- 2. 右侧控制面板 ---
        self.right_panel = ttk.Frame(self.dialog, padding=20)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        # 2.1 坐标输入组
        coord_group = ttk.LabelFrame(self.right_panel, text="裁剪坐标设置", padding=15)
        coord_group.pack(fill="x", pady=(0, 20))
        
        # 第一组：起始点 (X, Y)
        ttk.Label(coord_group, text="起始位置 (Top-Left):", font=self.ui_font).grid(row=0, column=0, columnspan=3, sticky="w")
        self.x1_var = tk.StringVar(value="0")
        self.y1_var = tk.StringVar(value="0")
        self.create_spin_row(coord_group, 1, "X:", self.x1_var, "Y:", self.y1_var)
        
        # 第二组：结束点 (X, Y)
        ttk.Label(coord_group, text="结束位置 (Bottom-Right):", font=self.ui_font).grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self.x2_var = tk.StringVar(value="100")
        self.y2_var = tk.StringVar(value="100")
        self.create_spin_row(coord_group, 3, "X:", self.x2_var, "Y:", self.y2_var)

        # 实时尺寸显示
        size_frame = ttk.Frame(coord_group)
        size_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        self.size_label = ttk.Label(size_frame, text="尺寸: 100 x 100 像素", font=("Microsoft YaHei UI", 9))
        self.size_label.pack(anchor="w")

        # 2.2 预设比例组
        ratio_group = ttk.LabelFrame(self.right_panel, text="预设比例", padding=15)
        ratio_group.pack(fill="x", pady=(10, 0))

        # 比例按钮
        ratio_btn_frame = ttk.Frame(ratio_group)
        ratio_btn_frame.pack(fill="x")

        self.ratio_var = tk.StringVar(value="free")
        self.ratio_var.trace_add('write', self.on_ratio_change)

        ratios = [
            ("自由", "free"),
            ("锁定当前比例", "lock_current"),
            ("1:1", "1:1"),
            ("16:9", "16:9"),
            ("4:3", "4:3"),
            ("3:2", "3:2"),
            ("黄金分割", "1.618")
        ]

        for text, value in ratios:
            if value == "lock_current":
                # 为"锁定当前比例"添加比例显示标签
                rb_frame = ttk.Frame(ratio_btn_frame)
                rb_frame.pack(anchor="w", pady=2)
                rb = ttk.Radiobutton(rb_frame, text=text, variable=self.ratio_var, value=value)
                rb.pack(side="left")
                self.locked_ratio_label = ttk.Label(rb_frame, text="", foreground="blue")
                self.locked_ratio_label.pack(side="left", padx=(10, 0))
            else:
                rb = ttk.Radiobutton(ratio_btn_frame, text=text, variable=self.ratio_var, value=value)
                rb.pack(anchor="w", pady=2)

        # 2.3 选项组
        option_group = ttk.LabelFrame(self.right_panel, text="显示选项", padding=15)
        option_group.pack(fill="x")
        
        self.show_cropped_var = tk.BooleanVar()
        self.show_prev_var = tk.BooleanVar()
        self.show_next_var = tk.BooleanVar()
        self.show_first_var = tk.BooleanVar()

        opts = [
            ("显示裁剪后状态 (Show As Cropped)", self.show_cropped_var),
            ("显示上一帧 (Show Previous)", self.show_prev_var),
            ("显示下一帧 (Show Next)", self.show_next_var),
            ("显示第一帧 (Show First)", self.show_first_var)
        ]
        
        for text, var in opts:
            cb = ttk.Checkbutton(option_group, text=text, variable=var)
            cb.pack(anchor="w", pady=5)

        # --- 3. 底部操作按钮区 ---
        self.bottom_bar = ttk.Frame(self.dialog, padding=(20, 10))
        self.bottom_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # 分隔线
        ttk.Separator(self.dialog, orient="horizontal").grid(row=1, column=0, columnspan=2, sticky="new")
        
        # 按钮容器（右对齐）
        btn_container = ttk.Frame(self.bottom_bar)
        btn_container.pack(side="right")

        self.fit_btn = ttk.Button(btn_container, text="⛶", width=5, command=self.fit_to_window)
        self.fit_btn.pack(side="left", padx=5)
        self.create_tooltip(self.fit_btn, "适应窗口 (Fit)")

        self.reset_btn = ttk.Button(btn_container, text="🔄", width=5, command=self.reset_zoom)
        self.reset_btn.pack(side="left", padx=5)
        self.create_tooltip(self.reset_btn, "重置缩放 (100%)")

        self.ok_btn = ttk.Button(btn_container, text="✓", width=5, command=self.ok_clicked)
        self.ok_btn.pack(side="left", padx=5)
        self.create_tooltip(self.ok_btn, "确定 (OK)")

        self.cancel_btn = ttk.Button(btn_container, text="✕", width=5, command=self.cancel_clicked)
        self.cancel_btn.pack(side="left", padx=5)
        self.create_tooltip(self.cancel_btn, "取消 (Cancel)")

    def create_spin_row(self, parent, row, label1, var1, label2, var2):
        """辅助函数：创建一行两个带标签的微调框"""
        ttk.Label(parent, text=label1).grid(row=row, column=0, sticky="w")
        s1 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var1, width=8)
        s1.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        # 绑定回车键更新尺寸显示
        s1.bind('<Return>', lambda e: self.update_size_label())
        s1.bind('<FocusOut>', lambda e: self.update_size_label())

        ttk.Label(parent, text=label2).grid(row=row, column=2, sticky="w")
        s2 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var2, width=8)
        s2.grid(row=row, column=3, sticky="w", padx=5, pady=5)
        # 绑定回车键更新尺寸显示
        s2.bind('<Return>', lambda e: self.update_size_label())
        s2.bind('<FocusOut>', lambda e: self.update_size_label())

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

    def reset_zoom(self):
        """重置缩放 - 按原尺寸大小显示图片"""
        if not hasattr(self, 'original_image'):
            messagebox.showinfo("提示", "请先加载图片")
            return

        try:
            # 设置缩放比例为1.0，即原尺寸显示
            self.preview_scale = 1.0

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
            self.result = {
                'start': (int(self.x1_var.get()), int(self.y1_var.get())),
                'end': (int(self.x2_var.get()), int(self.y2_var.get())),
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

        # 检查是否点击了选框内部（用于移动选框）
        try:
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

            # 转换为原始图片坐标的偏移量
            img_dx = int(dx / self.preview_scale)
            img_dy = int(dy / self.preview_scale)

            x1, y1, x2, y2 = self.move_start_coords

            # 移动选框
            new_x1 = x1 + img_dx
            new_y1 = y1 + img_dy
            new_x2 = x2 + img_dx
            new_y2 = y2 + img_dy

            # 确保选框在图片范围内
            new_x1 = max(0, new_x1)
            new_y1 = max(0, new_y1)
            new_x2 = min(self.original_image.width, new_x2)
            new_y2 = min(self.original_image.height, new_y2)

            # 如果选框被边界限制了，需要保持尺寸
            width = new_x2 - new_x1
            height = new_y2 - new_y1
            orig_width = x2 - x1
            orig_height = y2 - y1

            if width != orig_width:
                if new_x1 == 0:
                    new_x2 = new_x1 + orig_width
                else:
                    new_x1 = new_x2 - orig_width

            if height != orig_height:
                if new_y1 == 0:
                    new_y2 = new_y1 + orig_height
                else:
                    new_y1 = new_y2 - orig_height

            # 更新输入框
            self.x1_var.set(str(new_x1))
            self.y1_var.set(str(new_y1))
            self.x2_var.set(str(new_x2))
            self.y2_var.set(str(new_y2))

            # 重绘选框和滑块
            self.draw_selection_box()
            self.update_size_label()

        except Exception as e:
            print(f"移动选框失败: {e}")

    def handle_drag(self, event):
        """滑块拖拽事件"""
        try:
            # 计算鼠标移动的偏移量
            dx = event.x - self.drag_start_pos[0]
            dy = event.y - self.drag_start_pos[1]

            # 转换为原始图片坐标的偏移量
            img_dx = int(dx / self.preview_scale)
            img_dy = int(dy / self.preview_scale)

            x1, y1, x2, y2 = self.drag_start_coords

            # 根据滑块类型调整选框
            if self.dragging_handle == 'nw':  # 左上角
                x1 = max(0, x1 + img_dx)
                y1 = max(0, y1 + img_dy)
            elif self.dragging_handle == 'n':  # 上边
                y1 = max(0, y1 + img_dy)
            elif self.dragging_handle == 'ne':  # 右上角
                x2 = min(self.original_image.width, x2 + img_dx)
                y1 = max(0, y1 + img_dy)
            elif self.dragging_handle == 'e':  # 右边
                x2 = min(self.original_image.width, x2 + img_dx)
            elif self.dragging_handle == 'se':  # 右下角
                x2 = min(self.original_image.width, x2 + img_dx)
                y2 = min(self.original_image.height, y2 + img_dy)
            elif self.dragging_handle == 's':  # 下边
                y2 = min(self.original_image.height, y2 + img_dy)
            elif self.dragging_handle == 'sw':  # 左下角
                x1 = max(0, x1 + img_dx)
                y2 = min(self.original_image.height, y2 + img_dy)
            elif self.dragging_handle == 'w':  # 左边
                x1 = max(0, x1 + img_dx)

            # 如果锁定了比例，调整尺寸以保持比例
            if self.is_ratio_locked and self.ratio_value:
                width = abs(x2 - x1)
                height = abs(y2 - y1)

                if width == 0 or height == 0:
                    x1, y1, x2, y2 = self.drag_start_coords
                else:
                    # 根据较大的变化方向调整
                    if self.dragging_handle in ['nw', 'ne', 'sw', 'se']:
                        # 角滑块：根据宽度调整高度
                        new_height = int(width / self.ratio_value)
                        if self.dragging_handle in ['nw', 'sw']:
                            y1 = y2 - new_height
                        else:
                            y2 = y1 + new_height
                    elif self.dragging_handle in ['n', 's']:
                        # 上下边滑块：根据高度调整宽度
                        new_width = int(height * self.ratio_value)
                        x2 = x1 + new_width
                    elif self.dragging_handle in ['e', 'w']:
                        # 左右边滑块：根据宽度调整高度
                        new_height = int(width / self.ratio_value)
                        y2 = y1 + new_height

            # 确保选框有效（宽度、高度至少为1）
            if abs(x2 - x1) < 1:
                if self.dragging_handle in ['nw', 'w', 'sw']:
                    x1 = x2 - 1
                else:
                    x2 = x1 + 1
            if abs(y2 - y1) < 1:
                if self.dragging_handle in ['nw', 'n', 'ne']:
                    y1 = y2 - 1
                else:
                    y2 = y1 + 1

            # 更新输入框
            self.x1_var.set(str(x1))
            self.y1_var.set(str(y1))
            self.x2_var.set(str(x2))
            self.y2_var.set(str(y2))

            # 重绘选框和滑块
            self.draw_selection_box()
            self.update_size_label()

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
            self.update_size_label()
            return

        # 如果正在绘制选框
        if not self.is_selecting or not self.selection_start:
            return

        self.is_selecting = False

        # 计算选框在原始图片中的坐标
        if self.selection_rect:
            coords = self.canvas.coords(self.selection_rect)
            if len(coords) == 4:
                x1, y1, x2, y2 = coords

                # 转换为图片坐标
                img_left = self.image_x - self.image_width // 2
                img_top = self.image_y - self.image_height // 2

                # 转换为原始图片坐标
                orig_x1 = int((x1 - img_left) / self.preview_scale)
                orig_y1 = int((y1 - img_top) / self.preview_scale)
                orig_x2 = int((x2 - img_left) / self.preview_scale)
                orig_y2 = int((y2 - img_top) / self.preview_scale)

                # 确保坐标顺序正确
                orig_x1, orig_x2 = min(orig_x1, orig_x2), max(orig_x1, orig_x2)
                orig_y1, orig_y2 = min(orig_y1, orig_y2), max(orig_y1, orig_y2)

                # 更新输入框
                self.x1_var.set(str(orig_x1))
                self.y1_var.set(str(orig_y1))
                self.x2_var.set(str(orig_x2))
                self.y2_var.set(str(orig_y2))

                # 删除临时选框，绘制永久选框
                self.canvas.delete(self.selection_rect)
                self.selection_rect = None

                # 应用显示选项
                self.apply_display_options()

            # 更新尺寸显示
            self.update_size_label()

    def on_mouse_move(self, event):
        """鼠标移动事件，根据位置改变光标形状"""
        # 检查是否在滑块上
        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            if "handle" in tags:
                for tag in tags:
                    if tag in self.handles and self.handles[tag] == item:
                        # 根据滑块类型设置双向箭头光标
                        cursor_map = {
                            'nw': 'size_nw_se',  # 左上-右下斜对角双向箭头
                            'n': 'sb_v_double_arrow',  # 垂直双向箭头
                            'ne': 'size_ne_sw',  # 右上-左下斜对角双向箭头
                            'e': 'sb_h_double_arrow',  # 水平双向箭头
                            'se': 'size_nw_se',  # 左上-右下斜对角双向箭头
                            's': 'sb_v_double_arrow',  # 垂直双向箭头
                            'sw': 'size_ne_sw',  # 右上-左下斜对角双向箭头
                            'w': 'sb_h_double_arrow'  # 水平双向箭头
                        }
                        self.canvas.config(cursor=cursor_map.get(tag, 'arrow'))
                        return

        # 如果不在滑块上，恢复默认光标
        self.canvas.config(cursor='arrow')

    def on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        # 检查是否按下了 Ctrl 键
        ctrl_pressed = event.state & 0x4  # Ctrl 键的位掩码

        if ctrl_pressed:
            # Ctrl+滚轮：缩放图片
            if event.delta > 0 or event.num == 4:
                # 向上滚动：放大
                self.zoom_in()
            elif event.delta < 0 or event.num == 5:
                # 向下滚动：缩小
                self.zoom_out()
        else:
            # 普通滚轮：滚动查看
            # 检查滚动区域是否大于Canvas可视区域
            scrollregion = self.canvas.cget("scrollregion")
            if scrollregion:
                parts = scrollregion.split()
                if len(parts) == 4:
                    scroll_width = float(parts[2])
                    scroll_height = float(parts[3])
                    canvas_width = self.canvas.winfo_width()
                    canvas_height = self.canvas.winfo_height()

                    # 如果图片的宽度或高度大于Canvas的可视区域，则允许滚动
                    if scroll_width > canvas_width or scroll_height > canvas_height:
                        # 检查操作系统类型来确定滚动方向
                        if event.num == 4 or event.delta > 0:
                            # 向上滚动
                            self.canvas.yview_scroll(-1, "units")
                        elif event.num == 5 or event.delta < 0:
                            # 向下滚动
                            self.canvas.yview_scroll(1, "units")

    def on_option_change(self, *args):
        """选项变化时的回调"""
        self.apply_display_options()

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

            # 显示裁剪后的状态
            if self.show_cropped_var.get():
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

            # 显示上一帧
            elif self.show_prev_var.get() and self.image_paths and self.current_index > 0:
                prev_path = self.image_paths[self.current_index - 1]
                self.display_reference_image(prev_path)

            # 显示下一帧
            elif self.show_next_var.get() and self.image_paths and self.current_index < len(self.image_paths) - 1:
                next_path = self.image_paths[self.current_index + 1]
                self.display_reference_image(next_path)

            # 显示第一帧
            elif self.show_first_var.get() and self.image_paths:
                first_path = self.image_paths[0]
                self.display_reference_image(first_path)

            # 始终显示选框
            self.draw_selection_box()

        except Exception as e:
            print(f"应用显示选项失败: {e}")

    def display_reference_image(self, image_path):
        """显示参考图片（上一帧/下一帧/第一帧）"""
        try:
            # 使用 image_utils 模块加载图片
            ref_img = load_image(image_path)
            if not ref_img:
                print(f"无法加载参考图片: {image_path}")
                return

            # 调整参考图片尺寸与当前图片一致
            if ref_img.size != self.original_image.size:
                ref_img = resize_image(ref_img, self.original_image.width, self.original_image.height)

            # 转换为PhotoImage
            scaled_width = int(self.original_image.width * self.preview_scale)
            scaled_height = int(self.original_image.height * self.preview_scale)
            ref_resized = resize_image(ref_img, scaled_width, scaled_height)
            ref_photo = create_photo_image(ref_resized)

            # 清除Canvas并显示参考图片
            self.canvas.delete("all")
            self.canvas.create_image(self.image_x, self.image_y, image=ref_photo, anchor=tk.CENTER)

            # 保存引用防止被垃圾回收
            self.current_photo = ref_photo

        except Exception as e:
            print(f"无法显示参考图片: {e}")

    def draw_selection_box(self):
        """绘制选框和滑块"""
        try:
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

            # 删除旧选框和滑块
            self.canvas.delete("selection_box")
            self.canvas.delete("handle")

            # 绘制新选框（红色虚线）
            self.canvas.create_rectangle(
                scaled_x1, scaled_y1, scaled_x2, scaled_y2,
                outline="red",
                width=3,
                dash=(4, 4),
                tags="selection_box"
            )

            # 绘制8个滑块（4个角 + 4个边中间）
            handle_size = 10
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

    def update_size_label(self):
        """更新实时尺寸显示"""
        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            width = abs(x2 - x1)
            height = abs(y2 - y1)

            # 计算当前比例
            if height > 0:
                current_ratio = width / height
                ratio_text = f"比例: {current_ratio:.3f}"
            else:
                ratio_text = "比例: --"

            self.size_label.config(text=f"尺寸: {width} x {height} 像素 | {ratio_text}")
        except Exception as e:
            print(f"更新尺寸显示失败: {e}")

    def on_ratio_change(self, *args):
        """比例选择变化时的回调"""
        ratio = self.ratio_var.get()

        if ratio == "free":
            self.is_ratio_locked = False
            self.ratio_value = None
            if hasattr(self, 'locked_ratio_label'):
                self.locked_ratio_label.config(text="")
        elif ratio == "lock_current":
            # 锁定当前选框的比例
            try:
                x1 = int(self.x1_var.get())
                y1 = int(self.y1_var.get())
                x2 = int(self.x2_var.get())
                y2 = int(self.y2_var.get())

                width = abs(x2 - x1)
                height = abs(y2 - y1)

                if height > 0:
                    current_ratio = width / height
                    self.is_ratio_locked = True
                    self.ratio_value = current_ratio
                    # 更新标签显示
                    if hasattr(self, 'locked_ratio_label'):
                        self.locked_ratio_label.config(text=f"({current_ratio:.3f})")
                else:
                    messagebox.showwarning("警告", "请先设置有效的选框")
                    self.ratio_var.set("free")
                    if hasattr(self, 'locked_ratio_label'):
                        self.locked_ratio_label.config(text="")
            except Exception as e:
                messagebox.showerror("错误", f"锁定比例失败: {str(e)}")
                self.ratio_var.set("free")
                if hasattr(self, 'locked_ratio_label'):
                    self.locked_ratio_label.config(text="")
        elif ratio == "1:1":
            self.is_ratio_locked = True
            self.ratio_value = 1.0
            if hasattr(self, 'locked_ratio_label'):
                self.locked_ratio_label.config(text="(1.000)")
        elif ratio == "16:9":
            self.is_ratio_locked = True
            self.ratio_value = 16.0 / 9.0
            if hasattr(self, 'locked_ratio_label'):
                self.locked_ratio_label.config(text=f"({16.0/9.0:.3f})")
        elif ratio == "4:3":
            self.is_ratio_locked = True
            self.ratio_value = 4.0 / 3.0
            if hasattr(self, 'locked_ratio_label'):
                self.locked_ratio_label.config(text=f"({4.0/3.0:.3f})")
        elif ratio == "3:2":
            self.is_ratio_locked = True
            self.ratio_value = 3.0 / 2.0
            if hasattr(self, 'locked_ratio_label'):
                self.locked_ratio_label.config(text=f"({3.0/2.0:.3f})")
        elif ratio == "1.618":
            self.is_ratio_locked = True
            self.ratio_value = 1.618
            if hasattr(self, 'locked_ratio_label'):
                self.locked_ratio_label.config(text="(1.618)")

        # 如果锁定了比例，调整当前选框以符合比例
        if self.is_ratio_locked and self.ratio_value and ratio != "lock_current":
            self.apply_ratio_lock()

    def apply_ratio_lock(self):
        """应用比例锁定，调整选框以符合指定比例"""
        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            width = abs(x2 - x1)
            height = abs(y2 - y1)

            if width == 0 or height == 0:
                return

            # 根据宽度计算新的高度
            new_height = int(width / self.ratio_value)

            # 更新Y坐标
            if y2 > y1:
                self.y2_var.set(str(y1 + new_height))
            else:
                self.y2_var.set(str(y1 - new_height))

            # 重绘选框
            self.draw_selection_box()
            self.update_size_label()

        except Exception as e:
            print(f"应用比例锁定失败: {e}")

    def auto_crop(self):
        """自动裁剪功能 - 自动检测图片内容并去除空白边缘"""
        if not hasattr(self, 'original_image'):
            messagebox.showinfo("提示", "请先加载图片")
            return

        # 使用 image_utils 模块进行自动裁剪
        crop_coords = auto_crop_image(self.original_image, margin=5, threshold=10)

        if crop_coords is None:
            messagebox.showerror("错误", "自动裁剪功能需要 numpy 库\n请运行: pip install numpy\n\n或者图片中未检测到有效内容区域")
            return

        try:
            x1, y1, x2, y2 = crop_coords

            # 更新输入框
            self.x1_var.set(str(x1))
            self.y1_var.set(str(y1))
            self.x2_var.set(str(x2))
            self.y2_var.set(str(y2))

            # 重绘选框
            self.draw_selection_box()

            messagebox.showinfo("自动裁剪", f"已自动检测内容区域:\nX: {x1}, Y: {y1}\n宽度: {x2-x1}, 高度: {y2-y1}")

        except Exception as e:
            messagebox.showerror("错误", f"自动裁剪失败: {str(e)}")

    def fit_to_window(self):
        """适应窗口 - 让图片适应窗口大小"""
        if not hasattr(self, 'original_image'):
            messagebox.showinfo("提示", "请先加载图片")
            return

        try:
            # 获取图片的原始尺寸
            orig_width, orig_height = self.original_image.size

            # 获取Canvas的实际尺寸
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width() - 20  # 减去padding
            canvas_height = self.canvas.winfo_height() - 20  # 减去padding

            # 确保Canvas有合理的尺寸
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
            self.display_image()

        except Exception as e:
            messagebox.showerror("错误", f"适应窗口失败: {str(e)}")


def show_crop_dialog(parent, image_path=None, image_paths=None, current_index=0):
    """显示裁剪对话框的便捷函数"""
    dialog = CropDialog(parent, image_path, image_paths, current_index)
    return dialog.show()
