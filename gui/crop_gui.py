# -*- coding: utf-8 -*-
"""
裁剪窗口 GUI 模块 - 高清自适应裁剪窗口，只包含裁剪窗口的 GUI 设定相关代码
支持 1280x720 布局，并能随窗口缩放自动调整控件位置
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from function.image_utils import (
    load_image,
    resize_image,
    create_photo_image,
    calculate_scale_to_fit,
    calculate_scale_to_fill
)
from function.crop import CropState, CropRatioHandler, find_smallest_image_path, calculate_scaled_dimensions, convert_canvas_to_image_coords, validate_crop_coordinates, calculate_aspect_ratio, apply_aspect_ratio_constraints, determine_crop_strategy, crop_image
from function.ui_operations import ensure_widget_rendered

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
        self.base_photo = None
        self.preview_scale = 0.0  # 初始值为0，表示需要计算适应窗口的缩放比例
        self.initial_scale = 1.0

        self.selection_start = None
        self.selection_rect = None
        self.is_selecting = False

        self.handles = {}
        self.dragging_handle = None
        self.drag_start_pos = None
        self.drag_start_coords = None

        self.ratio_handler = CropRatioHandler()
        self.ratio_handler.dialog = self

        self.is_moving_selection = False
        self.move_start_pos = None
        self.move_start_coords = None

        # 跟踪当前显示的图片类型：'original', 'prev', 'next', 'first'
        self.current_display_mode = 'original'
        self.current_reference_path = None  # 当前显示的参考图片路径


        self.image_x = 0
        self.image_y = 0
        self.image_width = 0
        self.image_height = 0

        self.crop_state = CropState(max_history=100)

        self.is_base_image, self.min_image_path, min_idx = determine_crop_strategy(self.image_paths, current_index)
        self.min_image_size = min_idx
        #   - 1280x720
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Crop Animation - High Definition")
        self.dialog.geometry("1280x720")
        self.dialog.minsize(800, 600)

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.ui_font = ("Microsoft YaHei UI", 10)
        self.header_font = ("Microsoft YaHei UI", 12, "bold")

        self.setup_ui()
        self.center_window()

        if self.image_path:
            from function.image_utils import load_image
            # 正确加载图片：只传递图片路径，不传递self
            self.original_image = load_image(self.image_path)
            if self.original_image:
                # 延迟显示图片，确保Canvas完全渲染
                self.dialog.after(100, self.display_image)

    def center_window(self):
        """将窗口居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        
        # 如果窗口还没有显示，使用设置的默认尺寸
        if width <= 1 or height <= 1:
            width = 1280
            height = 720
        
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def display_image(self):
        """显示图片"""
        if not hasattr(self, 'original_image'):
            return

        try:
            # 重置为显示原始图片
            self.current_display_mode = 'original'
            self.current_reference_path = None

            img = self.original_image
            orig_width, orig_height = img.size

            # 强制更新Canvas尺寸
            self.dialog.update_idletasks()
            self.canvas.update_idletasks()
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # 确保Canvas有合理的尺寸
            if canvas_width < 100:
                canvas_width = 800
            if canvas_height < 100:
                canvas_height = 600

            # 计算适应窗口的缩放比例
            if not hasattr(self, 'preview_scale') or self.preview_scale == 0:
                self.preview_scale = calculate_scale_to_fit(orig_width, orig_height, canvas_width, canvas_height)
                self.initial_scale = self.preview_scale

            # 计算缩放后的尺寸
            scaled_width = int(orig_width * self.preview_scale)
            scaled_height = int(orig_height * self.preview_scale)

            #   image_utils 
            img_resized = resize_image(img, scaled_width, scaled_height)

            #   image_utils PhotoImage
            self.current_photo = create_photo_image(img_resized)
            self.base_photo = self.current_photo

            #  Canvas
            self.canvas.delete("all")

            #  Canvas
            #  Canvas
            actual_canvas_width = self.canvas.winfo_width()
            actual_canvas_height = self.canvas.winfo_height()

            #   Canvas
            if scaled_width > actual_canvas_width or scaled_height > actual_canvas_height:
                #   Canvas，NW(0,0) ，
                self.image_x = 0
                self.image_y = 0
                anchor = tk.NW
                self.canvas.configure(scrollregion=(0, 0, scaled_width, scaled_height))
            else:
                #  Canvas，，
                self.image_x = actual_canvas_width // 2
                self.image_y = actual_canvas_height // 2
                anchor = tk.CENTER
                #  Canvas，设置为Canvas尺寸，确保滚动条始终可见
                self.canvas.configure(scrollregion=(0, 0, actual_canvas_width, actual_canvas_height))

            self.image_width = scaled_width
            self.image_height = scaled_height

            # 绘制图片
            self.canvas.create_image(self.image_x, self.image_y, image=self.current_photo, anchor=anchor)

            # 绘制图片边框
            if anchor == tk.NW:
                # 左上角对齐
                border_x1 = self.image_x - 1
                border_y1 = self.image_y - 1
                border_x2 = self.image_x + scaled_width + 1
                border_y2 = self.image_y + scaled_height + 1
            else:
                # 居中对齐
                border_x1 = self.image_x - scaled_width // 2 - 1
                border_y1 = self.image_y - scaled_height // 2 - 1
                border_x2 = self.image_x + scaled_width // 2 + 1
                border_y2 = self.image_y + scaled_height // 2 + 1

            self.canvas.create_rectangle(
                border_x1, border_y1, border_x2, border_y2,
                outline="#CCCCCC",
                width=2,
                tags="image_border"
            )

            self.x1_var.set("0")
            self.y1_var.set("0")
            self.x2_var.set(str(orig_width))
            self.y2_var.set(str(orig_height))

            self.draw_selection_box()

        except Exception as e:
            print(f"无法显示图片: {e}")
        
    def setup_ui(self):
        """使用 Grid 权重布局实现自适应"""
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.columnconfigure(1, weight=0)
        self.dialog.rowconfigure(0, weight=1)

        #  --- 1.  (Canvas) ---
        self.preview_frame = ttk.LabelFrame(self.dialog, text="预览视图 (Preview)", padding=10)
        self.preview_frame.grid(row=0, column=0, padx=(20, 0), pady=20, sticky="nsew")

        #   Canvas 
        self.canvas = tk.Canvas(self.preview_frame, bg="#313337", highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        #   Canvas 
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)
        self.preview_frame.rowconfigure(1, weight=0)  # 确保水平滚动条行不拉伸

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<MouseWheel>", lambda e: self.ratio_handler.on_mousewheel(e, self.zoom_in, self.zoom_out))  # Windows
        self.canvas.bind("<Button-4>", lambda e: self.ratio_handler.on_mousewheel(e, self.zoom_in, self.zoom_out))   #  Linux 
        self.canvas.bind("<Button-5>", lambda e: self.ratio_handler.on_mousewheel(e, self.zoom_in, self.zoom_out))   #  Linux 

        self.canvas.create_text(450, 300, text="图像预览区域\n(Image Preview Area)", fill="white", justify="center")

        #  --- 2.  ---
        self.right_panel = ttk.Frame(self.dialog, padding=20)
        self.right_panel.grid(row=0, column=1, sticky="n", padx=0)  #   50 
        
        self.right_panel.columnconfigure(0, weight=0)
        self.modules_container = ttk.Frame(self.right_panel, width=320)
        self.modules_container.grid(row=0, column=0, sticky="n")
        
        # 2.1 坐标设置
        coord_title = "坐标设置" + ("（基准图）" if self.is_base_image else "")
        coord_group = ttk.LabelFrame(self.modules_container, text=coord_title, padding=5)
        coord_group.pack(fill="x", pady=(0, 15), ipadx=10)
        

        coord_group.columnconfigure(0, weight=0)
        coord_group.columnconfigure(1, weight=0)
        coord_group.columnconfigure(2, weight=0)
        coord_group.columnconfigure(3, weight=0)
        ttk.Label(coord_group, text="起始位置 (Top-Left):", font=self.ui_font).grid(row=0, column=0, columnspan=4, sticky="w", padx=5)
        self.x1_var = tk.StringVar(value="0")
        self.y1_var = tk.StringVar(value="0")
        self.create_spin_row(coord_group, 1, "X:", self.x1_var, "Y:", self.y1_var)
        ttk.Label(coord_group, text="结束位置 (Bottom-Right):", font=self.ui_font).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0), padx=5)
        self.x2_var = tk.StringVar(value="100")
        self.y2_var = tk.StringVar(value="100")
        self.create_spin_row(coord_group, 3, "X:", self.x2_var, "Y:", self.y2_var)

        size_frame = ttk.Frame(coord_group)
        size_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 0), padx=5)
        self.size_label = ttk.Label(size_frame, text="尺寸: 100 x 100 像素", font=("Microsoft YaHei UI", 9))
        self.size_label.pack(side="left", anchor="w")
        self.locked_ratio_label = ttk.Label(size_frame, text="", foreground="blue", font=("Microsoft YaHei UI", 9))
        self.locked_ratio_label.pack(side="left", padx=(10, 0))

        # 2.2 比例设置
        ratio_group = ttk.LabelFrame(self.modules_container, text="比例设置", padding=5)
        ratio_group.pack(fill="x", pady=(0, 15), ipadx=10)
        

        ratio_group.columnconfigure(0, weight=0)
        ratio_group.columnconfigure(1, weight=0)

        self.ratio_var = tk.StringVar(value="free")
        self.ratio_var.trace_add('write', lambda *args: self.ratio_handler.on_ratio_change(
            self.ratio_var,
            self.x1_var,
            self.y1_var,
            self.x2_var,
            self.y2_var,
            self.ratio_handler,
            self.locked_ratio_label,
            self.draw_selection_box,
            lambda: self.ratio_handler.update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)
        ))

        ratios = [
            ("自由", "free"),
            ("锁定比例", "lock_current"),
            ("原始比例", "original"),
            ("黄金分割", "1.618"),
            ("1:1", "1:1"),
            ("16:9", "16:9"),
            ("4:3", "4:3"),
            ("3:2", "3:2")
        ]

        #   grid ，
        for i, (text, value) in enumerate(ratios):
            row = i // 2
            col = i % 2
            rb = ttk.Radiobutton(ratio_group, text=text, variable=self.ratio_var, value=value)
            rb.grid(row=row, column=col, sticky="w", padx=5, pady=2)

        # 2.3 选项设置
        option_group = ttk.LabelFrame(self.modules_container, text="选项", padding=5)
        option_group.pack(fill="x", pady=(0, 15), ipadx=10)
        
        option_group.columnconfigure(0, weight=0)
        
        # "显示裁剪后"是独立的选项
        self.show_cropped_var = tk.BooleanVar()
        cb_cropped = ttk.Checkbutton(option_group, text="显示裁剪后", variable=self.show_cropped_var,
                                   command=self.apply_display_options)
        cb_cropped.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        ttk.Separator(option_group, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=(5, 5))
        
        # 其他选项是互斥的
        self.display_option_var = tk.StringVar(value="none")
        
        opts = [
            ("显示上一帧", "prev"),
            ("显示下一帧", "next"),
            ("显示第一帧", "first")
        ]
        
        for i, (text, value) in enumerate(opts):
            rb = ttk.Radiobutton(option_group, text=text, variable=self.display_option_var, value=value,
                                command=self.apply_display_options)
            rb.grid(row=i + 2, column=0, sticky="w", padx=5, pady=5)

        # 分隔线
        ttk.Separator(self.modules_container, orient="horizontal").pack(fill="x", pady=(10, 10))
        
        btn_row1 = ttk.Frame(self.modules_container)
        btn_row1.pack(fill="x", pady=(0, 5))

        self.fit_btn = ttk.Button(btn_row1, text="⬜", width=5, command=lambda: self.ratio_handler.fit_to_window(self))
        self.fit_btn.pack(side="left", padx=5)
        self.create_tooltip(self.fit_btn, "适应窗口")

        self.reset_btn = ttk.Button(btn_row1, text="🔄", width=5, command=self.reset_zoom)
        self.reset_btn.pack(side="left", padx=5)
        self.create_tooltip(self.reset_btn, "原始大小")

        btn_row2 = ttk.Frame(self.modules_container)
        btn_row2.pack(fill="x", pady=(0, 10))

        self.ok_btn = ttk.Button(btn_row2, text="✅", width=15, command=self.ok_clicked)
        self.ok_btn.pack(side="left", padx=5)
        self.create_tooltip(self.ok_btn, "确定 (OK)")

        self.cancel_btn = ttk.Button(btn_row2, text="❌", width=15, command=self.cancel_clicked)
        self.cancel_btn.pack(side="left", padx=5)
        self.create_tooltip(self.cancel_btn, "取消 (Cancel)")

    def create_spin_row(self, parent, row, label1, var1, label2, var2):
        """辅助函数：创建一行两个带标签的微调框"""
        ttk.Label(parent, text=label1).grid(row=row, column=0, sticky="w", padx=5)
        s1 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var1, width=6)
        s1.grid(row=row, column=1, sticky="w", padx=(2, 5), pady=5)
        #          from function.ui_operations import update_size_label
        s1.bind('<Return>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))
        s1.bind('<FocusOut>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))

        ttk.Label(parent, text=label2).grid(row=row, column=2, sticky="w", padx=5)
        s2 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var2, width=6)
        s2.grid(row=row, column=3, sticky="w", padx=(2, 5), pady=5)
        s2.bind('<Return>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))
        s2.bind('<FocusOut>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))

    def create_tooltip(self, widget, text):
        """创建鼠标悬浮提示"""
        def enter(event):
            # 如果已经存在tooltip，先销毁
            if hasattr(widget, '_tooltip'):
                try:
                    widget._tooltip.destroy()
                except:
                    pass
                del widget._tooltip
            
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes("-topmost", True)
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid",
                            borderwidth=1, font=("tahoma", "8", "normal"))
            label.pack()

            # 计算提示框位置
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")

            # 保存tooltip引用，避免被垃圾回收
            widget._tooltip = tooltip

        def leave(event):
            if hasattr(widget, '_tooltip'):
                try:
                    widget._tooltip.destroy()
                except:
                    pass
                del widget._tooltip

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def reset_zoom(self):
        """原始大小 - 按图片原始尺寸显示图片"""
        if not hasattr(self, 'original_image'):
            messagebox.showinfo("提示", "请先加载图片")
            return

        try:
            # 重置缩放比例为1.0（原始尺寸）
            self.preview_scale = 1.0

            # 根据当前显示的图片类型来决定如何重新显示
            if self.current_display_mode != 'original' and self.current_reference_path:
                # 重新应用显示选项
                self.apply_display_options()
            else:
                # 显示原始图片
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

                # 根据当前显示的图片类型来决定如何重新显示
                if self.current_display_mode != 'original' and self.current_reference_path:
                    # 如果当前显示的是参考图片，重新显示该参考图片
                    self.ratio_handler.display_reference_image(self, self.current_reference_path)
                else:
                    # 显示原始图片
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

                # 根据当前显示的图片类型来决定如何重新显示
                if self.current_display_mode != 'original' and self.current_reference_path:
                    # 如果当前显示的是参考图片，重新显示该参考图片
                    self.ratio_handler.display_reference_image(self, self.current_reference_path)
                else:
                    # 显示原始图片
                    self.display_image()
        except Exception as e:
            print(f"缩小失败: {e}")

    def ok_clicked(self):
        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            from function.history_manager import save_crop_state
            save_crop_state(self.crop_state)


            if len(self.image_paths) > 1 and self.is_base_image:
                # 获取基准图片宽度
                base_width = self.original_image.width
                base_height = self.original_image.height

                confirm = messagebox.askyesno(
                    "确认裁剪",
                    f"将使用相同的像素坐标裁剪选中的所有 {len(self.image_paths)} 张图片\n\n"
                    f"基准图片尺寸: {base_width} x {base_height}\n"
                    f"裁剪区域: ({x1}, {y1}) 到 ({x2}, {y2})\n"
                    f"裁剪尺寸: {x2-x1} x {y2-y1}\n\n"
                    f"所有图片将使用相同的像素坐标进行裁剪\n"
                    f"最终生成的裁剪图片分辨率将完全相同\n\n"
                    f"此操作可撤销/重做\n"
                    f"是否继续？"
                )

                if not confirm:

                    self.crop_state.history_manager.undo({
                        'crop_results': {},
                        'crop_coords': {}
                    })
                    return

                for img_path in self.image_paths:
                    self.crop_state.set_crop_coords(img_path, (x1, y1, x2, y2))

                self.result = {
                    'start': (x1, y1),
                    'end': (x2, y2),
                    'is_base_image': True,
                    'crop_coords': {path: self.crop_state.get_crop_coords(path) for path in self.image_paths},
                    'options': {
                        'show_cropped': self.show_cropped_var.get(),
                        'display_option': self.display_option_var.get()
                    }
                }
            else:

                self.crop_state.set_crop_coords(self.image_path, (x1, y1, x2, y2))

                self.result = {
                    'start': (x1, y1),
                    'end': (x2, y2),
                    'crop_coords': {self.image_path: (x1, y1, x2, y2)},
                    'options': {
                        'show_cropped': self.show_cropped_var.get(),
                        'display_option': self.display_option_var.get()
                    }
                }

            # 清理所有tooltip
            self._cleanup_all_tooltips()
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字坐标")
    
    def cancel_clicked(self):
        self.result = None
        # 清理所有tooltip
        self._cleanup_all_tooltips()
        self.dialog.destroy()
    
    def _cleanup_all_tooltips(self):
        """清理所有tooltip"""
        # 遍历所有子控件，清理tooltip
        for widget in self.dialog.winfo_children():
            if hasattr(widget, '_tooltip'):
                try:
                    widget._tooltip.destroy()
                except:
                    pass
                del widget._tooltip
            # 递归清理子控件的tooltip
            for child in widget.winfo_children():
                if hasattr(child, '_tooltip'):
                    try:
                        child._tooltip.destroy()
                    except:
                        pass
                    del child._tooltip

        # 清理所有 Toplevel 窗口（除了对话框本身）
        try:
            all_windows = self.dialog.winfo_children()
            for window in all_windows:
                if isinstance(window, tk.Toplevel) and window != self.dialog:
                    try:
                        window.destroy()
                    except:
                        pass
        except:
            pass
        
    def show(self):
        self.dialog.wait_window()
        return self.result

    def on_canvas_press(self, event):
        """统一处理Canvas上的鼠标按下事件"""
        if not hasattr(self, 'original_image'):
            return

        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            if "handle" in tags:
                for tag in tags:
                    if tag in self.handles and self.handles[tag] == item:
                        self.dragging_handle = tag
                        self.drag_start_pos = (event.x, event.y)
                        self.drag_start_coords = (
                            int(self.x1_var.get()),
                            int(self.y1_var.get()),
                            int(self.x2_var.get()),
                            int(self.y2_var.get())
                        )
                        return


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

            if (scaled_x1 < event.x < scaled_x2 and
                scaled_y1 < event.y < scaled_y2):
                self.is_moving_selection = True
                self.move_start_pos = (event.x, event.y)
                self.move_start_coords = (x1, y1, x2, y2)
                return
        except:
            pass


        img_left = self.image_x - self.image_width // 2
        img_top = self.image_y - self.image_height // 2
        img_right = self.image_x + self.image_width // 2
        img_bottom = self.image_y + self.image_height // 2

        if img_left <= event.x <= img_right and img_top <= event.y <= img_bottom:
            self.is_selecting = True
            self.selection_start = (event.x, event.y)

    def on_canvas_drag(self, event):
        """统一处理Canvas上的鼠标拖拽事件"""
        if self.dragging_handle:
            self.handle_drag(event)
            return

        if self.is_moving_selection:
            self.move_selection(event)
            return

        if not self.is_selecting or not self.selection_start:
            return

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        x1, y1 = self.selection_start
        x2, y2 = event.x, event.y

        img_left = self.image_x - self.image_width // 2
        img_top = self.image_y - self.image_height // 2
        img_right = self.image_x + self.image_width // 2
        img_bottom = self.image_y + self.image_height // 2

        x1 = max(img_left, min(x1, img_right))
        y1 = max(img_top, min(y1, img_bottom))
        x2 = max(img_left, min(x2, img_right))
        y2 = max(img_top, min(y2, img_bottom))


        self.selection_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red",
            width=2,
            dash=(4, 4)
        )

    def move_selection(self, event):
        """移动选框"""
        try:
            dx = event.x - self.move_start_pos[0]
            dy = event.y - self.move_start_pos[1]

            # 计算图片坐标的移动距离
            img_dx = int(dx / self.preview_scale)
            img_dy = int(dy / self.preview_scale)

            x1, y1, x2, y2 = self.move_start_coords

            new_x1 = x1 + img_dx
            new_y1 = y1 + img_dy
            new_x2 = x2 + img_dx
            new_y2 = y2 + img_dy


            from function.crop import validate_crop_coordinates
            new_x1, new_y1, new_x2, new_y2 = validate_crop_coordinates(
                new_x1, new_y1, new_x2, new_y2, self.original_image.width, self.original_image.height
            )

            self.x1_var.set(str(new_x1))
            self.y1_var.set(str(new_y1))
            self.x2_var.set(str(new_x2))
            self.y2_var.set(str(new_y2))

            self.draw_selection_box()
            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)

        except Exception as e:
            print(f"移动选框失败: {e}")

    def handle_drag(self, event):
        """滑块拖拽事件"""
        try:
            dx = event.x - self.drag_start_pos[0]
            dy = event.y - self.drag_start_pos[1]

            # 计算图片坐标的移动距离
            img_dx = int(dx / self.preview_scale)
            img_dy = int(dy / self.preview_scale)

            x1, y1, x2, y2 = self.drag_start_coords

            # 保存原始坐标用于比例锁定
            orig_x1, orig_y1, orig_x2, orig_y2 = x1, y1, x2, y2

            if self.dragging_handle == 'nw':  # 左上角
                x1 = x1 + img_dx
                y1 = y1 + img_dy
            elif self.dragging_handle == 'n':
                y1 = y1 + img_dy
            elif self.dragging_handle == 'ne':  # 右上角
                x2 = x2 + img_dx
                y1 = y1 + img_dy
            elif self.dragging_handle == 'e':
                x2 = x2 + img_dx
            elif self.dragging_handle == 'se':  # 右下角
                x2 = x2 + img_dx
                y2 = y2 + img_dy
            elif self.dragging_handle == 's':
                y2 = y2 + img_dy
            elif self.dragging_handle == 'sw':  # 左下角
                x1 = x1 + img_dx
                y2 = y2 + img_dy
            elif self.dragging_handle == 'w':
                x1 = x1 + img_dx

            # 如果启用了比例锁定，先应用比例约束
            if self.ratio_handler.is_ratio_locked and self.ratio_handler.ratio_value:
                x1, y1, x2, y2 = self.ratio_handler.adjust_coords_by_ratio(x1, y1, x2, y2, self.dragging_handle)
            else:
                # 如果没有启用比例锁定，确保坐标在边界内
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(self.original_image.width, x2)
                y2 = min(self.original_image.height, y2)

            # 验证坐标（确保最小尺寸和正确顺序）
            from function.crop import validate_crop_coordinates
            x1, y1, x2, y2 = validate_crop_coordinates(
                x1, y1, x2, y2, self.original_image.width, self.original_image.height
            )

            # 如果启用了比例锁定，再次应用比例约束以确保比例不被破坏
            if self.ratio_handler.is_ratio_locked and self.ratio_handler.ratio_value:
                x1, y1, x2, y2 = self.ratio_handler.adjust_coords_by_ratio(x1, y1, x2, y2, self.dragging_handle)

            self.x1_var.set(str(x1))
            self.y1_var.set(str(y1))
            self.x2_var.set(str(x2))
            self.y2_var.set(str(y2))

            # 如果勾选了显示裁剪后，需要更新预览
            show_cropped = self.show_cropped_var.get()
            display_option = self.display_option_var.get()
            if show_cropped or display_option != "none":
                # 添加调试信息
                print(f"显示裁剪后: {show_cropped}, 显示选项: {display_option}")
                self.apply_display_options()
            else:
                self.draw_selection_box()

            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)

        except Exception as e:
            print(f"滑块拖拽失败: {e}")

    def on_canvas_release(self, event):
        """统一处理Canvas上的鼠标释放事件"""
        if self.dragging_handle:
            self.dragging_handle = None
            self.drag_start_pos = None
            self.drag_start_coords = None
            return

        if self.is_moving_selection:
            self.is_moving_selection = False
            self.move_start_pos = None
            self.move_start_coords = None
            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)
            return

        if not self.is_selecting or not self.selection_start:
            return

        self.is_selecting = False

        if self.selection_rect:
            coords = self.canvas.coords(self.selection_rect)
            if len(coords) == 4:
                x1, y1, x2, y2 = coords


                orig_x1, orig_y1 = convert_canvas_to_image_coords(
                    x1, y1, self.image_x, self.image_y, self.preview_scale, self.image_width, self.image_height
                )
                orig_x2, orig_y2 = convert_canvas_to_image_coords(
                    x2, y2, self.image_x, self.image_y, self.preview_scale, self.image_width, self.image_height
                )


                from function.crop import validate_crop_coordinates
                orig_x1, orig_y1, orig_x2, orig_y2 = validate_crop_coordinates(
                    orig_x1, orig_y1, orig_x2, orig_y2, self.original_image.width, self.original_image.height
                )

                self.x1_var.set(str(orig_x1))
                self.y1_var.set(str(orig_y1))
                self.x2_var.set(str(orig_x2))
                self.y2_var.set(str(orig_y2))


                self.canvas.delete(self.selection_rect)
                self.selection_rect = None

                self.apply_display_options()

            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)

    def on_mouse_move(self, event):
        """鼠标移动事件，根据位置改变光标形状"""
        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            if "handle" in tags:
                for tag in tags:
                    if tag in self.handles and self.handles[tag] == item:
                        cursor_map = {
                            'nw': 'size_nw_se',  # 左上角
                            'n': 'sb_v_double_arrow',  # 上边
                            'ne': 'size_ne_sw',  # 右上角
                            'e': 'sb_h_double_arrow',  # 右边
                            'se': 'size_nw_se',  # 右下角
                            's': 'sb_v_double_arrow',  # 下边
                            'sw': 'size_ne_sw',  # 左下角
                            'w': 'sb_h_double_arrow'  # 左边
                        }
                        self.canvas.config(cursor=cursor_map.get(tag, 'arrow'))
                        return


        self.canvas.config(cursor='arrow')

    def apply_display_options(self):
        """应用显示选项"""
        if not hasattr(self, 'original_image'):
            return

        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            orig_width, orig_height = self.original_image.size

            self.canvas.delete("all")
            if self.base_photo:
                self.canvas.create_image(self.image_x, self.image_y, image=self.base_photo, anchor=tk.CENTER)

            # 获取当前选择的显示选项
            display_option = self.display_option_var.get()
            show_cropped = self.show_cropped_var.get()

            # 添加调试信息
            print(f"apply_display_options - show_cropped: {show_cropped}, display_option: {display_option}")
            print(f"裁剪坐标: ({x1}, {y1}, {x2}, {y2})")

            self.current_display_mode = 'original'  # 重置为原始图片
            self.current_reference_path = None

            # 确定要显示的图片
            if display_option == "prev" and self.image_paths and len(self.image_paths) > 1 and self.current_index > 0:
                # 显示上一帧
                prev_path = self.image_paths[self.current_index - 1]
                self.current_display_mode = 'prev'
                self.current_reference_path = prev_path
                display_image_path = prev_path
            elif display_option == "next" and self.image_paths and len(self.image_paths) > 1 and self.current_index < len(self.image_paths) - 1:
                # 显示下一帧
                next_path = self.image_paths[self.current_index + 1]
                self.current_display_mode = 'next'
                self.current_reference_path = next_path
                display_image_path = next_path
            elif display_option == "first" and self.image_paths and len(self.image_paths) > 1:
                # 显示第一帧
                first_path = self.image_paths[0]
                self.current_display_mode = 'first'
                self.current_reference_path = first_path
                display_image_path = first_path
            else:
                # 显示原始图片
                self.current_display_mode = 'original'
                self.current_reference_path = None
                display_image_path = None

            # 加载要显示的图片
            from function.image_utils import load_image, resize_image, create_photo_image

            if display_image_path:
                display_img = load_image(display_image_path)
                if not display_img:
                    print(f"无法加载图片: {display_image_path}")
                    return

                # 调整图片尺寸以匹配原始图片
                if display_img.size != (orig_width, orig_height):
                    display_img = resize_image(display_img, orig_width, orig_height)
            else:
                display_img = self.original_image

            # 如果需要显示裁剪效果
            if show_cropped:
                # 添加调试信息
                print(f"开始显示裁剪效果...")
                print(f"原始图片尺寸: {orig_width}x{orig_height}")
                print(f"显示图片尺寸: {display_img.size}")

                # 应用裁剪
                cropped_img = crop_image(display_img, x1, y1, x2, y2)
                print(f"裁剪后图片尺寸: {cropped_img.size}")

                # 创建一个半透明的黑色遮罩
                mask = Image.new('RGBA', (orig_width, orig_height), (0, 0, 0, 180))
                # 将裁剪后的图片粘贴到遮罩上
                cropped_rgba = cropped_img.convert('RGBA')
                mask.paste(cropped_rgba, (x1, y1))
                # 转换为 RGB 以便显示
                mask = mask.convert('RGB')

                # 创建PhotoImage
                scaled_width = int(orig_width * self.preview_scale)
                scaled_height = int(orig_height * self.preview_scale)
                mask_resized = resize_image(mask, scaled_width, scaled_height)
                self.current_photo = create_photo_image(mask_resized)
                self.canvas.delete("all")
                self.canvas.create_image(self.image_x, self.image_y, image=self.current_photo, anchor=tk.CENTER)
                # 绘制图片边框
                border_x1 = self.image_x - scaled_width // 2 - 1
                border_y1 = self.image_y - scaled_height // 2 - 1
                border_x2 = self.image_x + scaled_width // 2 + 1
                border_y2 = self.image_y + scaled_height // 2 + 1
                self.canvas.create_rectangle(
                    border_x1, border_y1, border_x2, border_y2,
                    outline="#CCCCCC",
                    width=2,
                    tags="image_border"
                )
                print(f"裁剪效果显示完成")
            else:
                # 不显示裁剪效果，直接显示图片
                scaled_width = int(orig_width * self.preview_scale)
                scaled_height = int(orig_height * self.preview_scale)
                img_resized = resize_image(display_img, scaled_width, scaled_height)
                self.current_photo = create_photo_image(img_resized)
                self.canvas.delete("all")
                self.canvas.create_image(self.image_x, self.image_y, image=self.current_photo, anchor=tk.CENTER)
                # 绘制图片边框
                border_x1 = self.image_x - scaled_width // 2 - 1
                border_y1 = self.image_y - scaled_height // 2 - 1
                border_x2 = self.image_x + scaled_width // 2 + 1
                border_y2 = self.image_y + scaled_height // 2 + 1
                self.canvas.create_rectangle(
                    border_x1, border_y1, border_x2, border_y2,
                    outline="#CCCCCC",
                    width=2,
                    tags="image_border"
                )

            self.draw_selection_box()

        except Exception as e:
            print(f"应用显示选项失败: {e}")

    def draw_selection_box(self):
        """绘制选框和滑块"""
        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            #   image_x  image_y  0，（CENTER ）
            #   image_x  image_y  0，（NW ）
            if self.image_x > 0 and self.image_y > 0:

                img_left = self.image_x - self.image_width // 2
                img_top = self.image_y - self.image_height // 2
            else:
                img_left = self.image_x
                img_top = self.image_y

            scaled_x1 = img_left + x1 * self.preview_scale
            scaled_y1 = img_top + y1 * self.preview_scale
            scaled_x2 = img_left + x2 * self.preview_scale
            scaled_y2 = img_top + y2 * self.preview_scale

            self.canvas.delete("selection_box")
            self.canvas.delete("handle")

            # 确保图片边框在选框下方
            self.canvas.tag_lower("image_border")


            self.canvas.create_rectangle(
                scaled_x1, scaled_y1, scaled_x2, scaled_y2,
                outline="red",
                width=3,
                dash=(4, 4),
                tags="selection_box"
            )

            # 绘制8个控制点（4个角点 + 4个中点）
            handle_size = 10
            handle_offset = handle_size // 2

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
