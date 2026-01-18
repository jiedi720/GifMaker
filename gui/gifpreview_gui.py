# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
GIF预览模块
包含GIF动画预览相关的界面和功能
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class GifPreviewWindow:
    """GIF预览窗口"""

    def __init__(self, parent, frames, duration, output_path, loop=0):
        self.frames = frames
        self.duration = duration
        self.output_path = output_path
        self.loop = loop  # 循环次数，0表示无限循环
        self.current_frame_index = 0
        self.is_playing = False
        self.animation_id = None
        self.zoom_scale = 1.0  # 缩放比例
        self.photo_cache = {}  # 缓存所有帧的PhotoImage对象，防止被垃圾回收
        self.photo = None  # 当前显示的PhotoImage对象

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("GIF Preview")

        # 使用与主界面相同的窗口尺寸
        self.window_width = 1366
        self.window_height = 768

        # 设置窗口大小限制
        self.window.minsize(1366, 768)
        self.window.maxsize(1920, 1080)

        # 直接使用固定尺寸，不根据图片调整
        self.window.geometry(f"{self.window_width}x{self.window_height}")

        # 先隐藏窗口，防止闪烁
        self.window.withdraw()

        # 设置窗口图标
        self.set_window_icon()

        # 创建UI
        self.setup_ui()

        # 显示第一帧
        self.display_frame(0)

        # 默认适应窗口
        self.fit_to_window()

        # 居中显示并恢复窗口显示
        self.center_window()
        self.window.deiconify()

        # 确保窗口显示在最前面
        self.window.lift()
        self.window.focus_force()

        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_window_icon(self):
        """设置窗口图标"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'gif.png')
            if os.path.exists(icon_path):
                self.window.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception:
            pass

    def center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()

        # 如果窗口还没有显示，使用保存的窗口尺寸
        if width <= 1 or height <= 1:
            width = self.window_width
            height = self.window_height

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置主框架的网格权重，让图片显示区域获得大部分垂直空间
        main_frame.rowconfigure(0, weight=1)  # 图片显示区域
        main_frame.rowconfigure(1, weight=0)  # 控制区域1
        main_frame.rowconfigure(2, weight=0)  # 控制区域2
        main_frame.rowconfigure(3, weight=0)  # 持续时间区域
        main_frame.columnconfigure(0, weight=1)

        # 图片显示区域 - 使用Canvas和Scrollbar实现滚动功能
        self.canvas_frame = ttk.Frame(main_frame)
        self.canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)

        # 创建Canvas和滚动条
        self.canvas = tk.Canvas(self.canvas_frame, bg='#313337')
        self.scroll_y = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # 布局Canvas和滚动条 - 使用grid管理器
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 直接在Canvas上显示图片，不使用额外的Frame容器
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.CENTER, image=None)

        # 绑定事件以更新滚动区?        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mousewheel)   # Linux
        self.canvas.bind("<Button-5>", self.on_mousewheel)   # Linux

        # 控制区域 - 第一行：播放控制和进度条
        control_frame1 = ttk.Frame(main_frame)
        control_frame1.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 5))

        # 创建一个居中容器
        center_container1 = ttk.Frame(control_frame1)
        center_container1.pack(expand=True)

        # 播放/停止按钮
        self.play_button = ttk.Button(center_container1, text="▶", command=self.toggle_play, width=5)
        self.play_button.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(self.play_button, "播放")

        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_scale = ttk.Scale(
            center_container1,
            from_=0,
            to=len(self.frames) - 1,
            variable=self.progress_var,
            orient=tk.HORIZONTAL,
            command=self.on_progress_change,
            length=200  # 设置进度条长度，与第二行对齐
        )
        self.progress_scale.pack(side=tk.LEFT, padx=(0, 10))

        # 当前帧显示
        self.frame_label = ttk.Label(center_container1, text="0 / 0", width=10)
        self.frame_label.pack(side=tk.LEFT, padx=(0, 10))

        # 控制区域 - 第二行：帧导航和缩放控制
        control_frame2 = ttk.Frame(main_frame)
        control_frame2.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 5))

        # 创建一个居中容器
        center_container2 = ttk.Frame(control_frame2)
        center_container2.pack(expand=True)

        # 左侧容器：持续时间调节和保存按钮
        left_container = ttk.Frame(center_container2)
        left_container.pack(side=tk.LEFT)

        ttk.Label(left_container, text="每帧时间(ms):").pack(side=tk.LEFT, padx=(0, 5))
        self.duration_var = tk.IntVar(value=self.duration)
        self.duration_spin = ttk.Spinbox(
            left_container,
            from_=50,
            to=2000,
            increment=50,
            textvariable=self.duration_var,
            width=5,
            command=self.on_duration_change
        )
        self.duration_spin.pack(side=tk.LEFT, padx=(0, 10))

        # 循环次数设置
        ttk.Label(left_container, text="循环次数(0=无限):").pack(side=tk.LEFT, padx=(0, 5))
        self.loop_var = tk.IntVar(value=self.loop)
        self.loop_spin = ttk.Spinbox(
            left_container,
            from_=0,
            to=999,
            textvariable=self.loop_var,
            width=5
        )
        self.loop_spin.pack(side=tk.LEFT, padx=(0, 10))

        # 分隔线
        ttk.Separator(left_container, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 保存按钮
        save_button = ttk.Button(left_container, text="💾", command=self.save_gif, width=5)
        save_button.pack(side=tk.LEFT)
        self.create_tooltip(save_button, "保存GIF")

        # 分隔线
        ttk.Separator(center_container2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 中间容器：帧导航按钮（居中）
        middle_container = ttk.Frame(center_container2)
        middle_container.pack(side=tk.LEFT, expand=True)

        btn_first = ttk.Button(middle_container, text="⏮", command=self.first_frame, width=5)
        btn_first.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_first, "第一帧")

        btn_prev = ttk.Button(middle_container, text="◀", command=self.previous_frame, width=5)
        btn_prev.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_prev, "上一帧")

        btn_next = ttk.Button(middle_container, text="▶", command=self.next_frame, width=5)
        btn_next.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_next, "下一帧")

        btn_last = ttk.Button(middle_container, text="⏭", command=self.last_frame, width=5)
        btn_last.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_last, "最后一帧")

        # 分隔线
        ttk.Separator(center_container2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 右侧容器：缩放控制按钮
        right_container = ttk.Frame(center_container2)
        right_container.pack(side=tk.LEFT)

        btn_zoom_in = ttk.Button(right_container, text="🔍+", command=self.zoom_in, width=5)
        btn_zoom_in.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_in, "放大画面")

        btn_zoom_out = ttk.Button(right_container, text="🔍-", command=self.zoom_out, width=5)
        btn_zoom_out.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_out, "缩小画面")

        btn_reset_zoom = ttk.Button(right_container, text="🔄", command=self.reset_zoom, width=5)
        btn_reset_zoom.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_reset_zoom, "原始大小")

        btn_fit_window = ttk.Button(right_container, text="⬜", command=self.fit_to_window, width=5)
        btn_fit_window.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_fit_window, "适应窗口")

        # 更新帧数显示
        self.update_frame_label()

    def on_canvas_configure(self, event):
        """当canvas大小改变时更新滚动区域"""
        pass  # 滚动区域由display_frame方法管理

    def on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        # 检查是否按下了Ctrl键
        ctrl_pressed = event.state & 0x4  # Ctrl键的位掩码
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
            # 检查滚动区域是否大于Canvas可视区域，如果是则允许滚动
            bbox = self.canvas.bbox("all")
            if bbox:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()

                # 如果图片的宽度或高度大于Canvas的可视区域，则允许滚动
                if bbox[2] > canvas_width or bbox[3] > canvas_height:
                    # 检查操作系统类型来确定滚动方向
                    if event.num == 4 or event.delta > 0:
                        # 向上滚动 - 水平滚动向左
                        self.canvas.xview_scroll(-1, "units")
                    elif event.num == 5 or event.delta < 0:
                        # 向下滚动 - 水平滚动向右
                        self.canvas.xview_scroll(1, "units")

    def create_tooltip(self, widget, text):
        """创建鼠标悬浮提示"""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+0+0")
        tooltip_label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("tahoma", "8", "normal"))
        tooltip_label.pack()

        def enter(event):
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + 25
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def display_frame(self, frame_index):
        """显示指定帧"""
        if 0 <= frame_index < len(self.frames):
            frame = self.frames[frame_index]

            # 获取原始图片尺寸
            orig_width, orig_height = frame.size

            # 计算基础缩放比例（使用当前窗口大小，考虑控制栏空间）
            self.canvas_frame.update_idletasks()
            # 获取canvas的实际可用空间
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # 减去滚动条的空间
            scrollbar_width = 15  # 滚动条宽度估计值
            max_width = canvas_width - scrollbar_width - 20 if canvas_width > 0 else orig_width
            max_height = canvas_height - scrollbar_width - 20 if canvas_height > 0 else orig_height

            if max_width < 50:
                max_width = orig_width
            if max_height < 50:
                max_height = orig_height

            # 计算基础缩放比例，保持宽高比（用于初始适应窗口）
            base_scale = min(max_width / orig_width, max_height / orig_height)

            # 应用缩放比例：当zoom_scale为1.0时，始终使用原始尺寸显示
            # 这样可以保证100%缩放时显示原始尺寸，即使图片大于窗口
            if self.zoom_scale == 1.0:
                scale = 1.0  # 始终显示原始尺寸
            else:
                # 用户手动缩放时，基于原始尺寸进行缩放
                scale = self.zoom_scale

            # 计算实际显示尺寸
            display_width = int(orig_width * scale)
            display_height = int(orig_height * scale)

            # 创建缓存键，包含帧索引和显示尺寸（使用整数避免浮点数精度问题）
            cache_key = (frame_index, display_width, display_height)

            # 检查缓存中是否已有该帧的PhotoImage
            if cache_key in self.photo_cache:
                self.photo = self.photo_cache[cache_key]
            else:
                # 调整图片大小，根据缩放方向选择合适的插值算法
                frame_copy = frame.copy()
                if scale >= 1.0:
                    # 放大时使用高质量插值，保持清晰
                    resampling = Image.Resampling.LANCZOS
                else:
                    # 缩小时使用双线性插值，提高性能
                    resampling = Image.Resampling.BILINEAR
                frame_copy = frame_copy.resize((display_width, display_height), resampling)

                # 转换为PhotoImage并缓存
                self.photo = ImageTk.PhotoImage(frame_copy)
                self.photo_cache[cache_key] = self.photo

            # 先更新Canvas上的图片
            self.canvas.itemconfig(self.image_id, image=self.photo)

            # 更新Canvas上的图片位置和锚点
            # 当图片大于窗口时，将图片放置在左上角(0, 0)，方便滚动查看
            # 当图片小于窗口时，将图片居中显示
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if display_width > canvas_width or display_height > canvas_height:
                # 图片大于窗口，放置在左上角（使用NW锚点）
                self.canvas.itemconfig(self.image_id, anchor=tk.NW)
                self.canvas.coords(self.image_id, 0, 0)
            else:
                # 图片小于窗口，居中显示（使用CENTER锚点）
                self.canvas.itemconfig(self.image_id, anchor=tk.CENTER)
                center_x = canvas_width // 2
                center_y = canvas_height // 2
                self.canvas.coords(self.image_id, center_x, center_y)

            # 更新当前帧索引
            self.current_frame_index = frame_index
            self.progress_var.set(frame_index)
            self.update_frame_label()

            # 更新滚动区域 - 确保滚动区域包含整个图片
            # 使用after确保在所有UI更新完成后设置滚动区域
            self.canvas.after(10, lambda: self.canvas.configure(scrollregion=(0, 0, display_width, display_height)))

    def update_frame_label(self):
        """更新帧数显示"""
        self.frame_label.configure(text=f"{self.current_frame_index + 1} / {len(self.frames)}")

    def first_frame(self):
        """跳转到第一帧"""
        self.display_frame(0)

    def previous_frame(self):
        """跳转到上一帧"""
        if self.current_frame_index > 0:
            self.display_frame(self.current_frame_index - 1)

    def next_frame(self):
        """跳转到下一帧"""
        if self.current_frame_index < len(self.frames) - 1:
            self.display_frame(self.current_frame_index + 1)

    def last_frame(self):
        """跳转到最后一帧"""
        self.display_frame(len(self.frames) - 1)

    def zoom_in(self):
        """放大画面"""
        # 检查放大后是否会超出边界
        if self.zoom_scale < 10.0:  # 设置最大缩放倍数
            self.zoom_scale *= 1.25
            # 清除缓存，因为缩放比例改变了
            self.photo_cache.clear()
            self.photo = None  # 清除当前图片引用
            self.display_frame(self.current_frame_index)

    def zoom_out(self):
        """缩小画面"""
        if self.zoom_scale > 0.1:  # 设置最小缩放倍数
            self.zoom_scale /= 1.25
            # 清除缓存，因为缩放比例改变了
            self.photo_cache.clear()
            self.photo = None  # 清除当前图片引用
            self.display_frame(self.current_frame_index)

    def reset_zoom(self):
        """原始大小 - 按图片原始尺寸显示"""
        self.zoom_scale = 1.0
        # 清除缓存，因为缩放比例改变了
        self.photo_cache.clear()
        self.photo = None  # 清除当前图片引用
        self.display_frame(self.current_frame_index)

    def fit_to_window(self):
        """让图片适应窗口大小"""
        if not self.frames:
            return

        # 获取当前帧的原始尺寸
        current_frame = self.frames[self.current_frame_index]
        orig_width, orig_height = current_frame.size

        # 获取Canvas的实际尺寸
        self.canvas_frame.update_idletasks()
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
        self.zoom_scale = fit_scale
        # 清除缓存，因为缩放比例改变了
        self.photo_cache.clear()
        self.photo = None  # 清除当前图片引用
        self.display_frame(self.current_frame_index)

    def on_duration_change(self):
        """持续时间变化回调"""
        try:
            self.duration = self.duration_var.get()
        except ValueError:
            self.duration_var.set(self.duration)

    def toggle_play(self):
        """切换播放/暂停状态"""
        if self.is_playing:
            self.stop()
        else:
            self.play()

    def play(self):
        """开始播放"""
        self.is_playing = True
        self.play_button.configure(text="⏸")
        self.create_tooltip(self.play_button, "暂停")
        self.animate()

    def stop(self):
        """停止播放"""
        self.is_playing = False
        self.play_button.configure(text="▶")
        self.create_tooltip(self.play_button, "播放")
        if self.animation_id:
            self.window.after_cancel(self.animation_id)
            self.animation_id = None

    def animate(self):
        """动画播放"""
        if not self.is_playing:
            return

        # 移动到下一帧
        next_frame = (self.current_frame_index + 1) % len(self.frames)
        self.display_frame(next_frame)

        # 继续播放，使用当前的持续时间
        self.animation_id = self.window.after(self.duration_var.get(), self.animate)

    def on_progress_change(self, value):
        """进度条拖动回调"""
        frame_index = int(float(value))
        if frame_index != self.current_frame_index:
            self.display_frame(frame_index)

    def save_gif(self):
        """保存GIF"""
        # 如果没有设置输出文件路径，或路径不包含目录部分，弹出文件保存对话框
        import os
        if not self.output_path or not os.path.dirname(self.output_path):
            from tkinter import filedialog
            import datetime
            
            # 生成默认文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"animation_{timestamp}.gif"
            
            # 弹出文件保存对话框
            selected_file = filedialog.asksaveasfilename(
                title="选择输出文件",
                initialfile=default_filename,
                defaultextension=".gif",
                filetypes=[
                    ("GIF files", "*.gif"),
                    ("All files", "*.*")
                ]
            )
            
            if not selected_file:
                return  # 用户取消了选择
            
            self.output_path = selected_file

        try:
            from function.gif_operations import save_gif as ops_save_gif
            ops_save_gif(self.frames, self.output_path, self.duration_var.get(), self.loop_var.get())
            messagebox.showinfo("成功", f"GIF已保存到:\n{self.output_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存GIF失败:\n{str(e)}")

    def on_close(self):
        """窗口关闭事件"""
        self.stop()
        self.window.destroy()
