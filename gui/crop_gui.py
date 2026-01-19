"""
GUI界面构建器模块
负责创建和管理固定比例裁剪工具的所有界面组件
采用深色主题、Grid布局、滚动条等现代化设计
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os


class GUIBuilder:
    """GUI界面构建器类，负责创建和管理所有界面组件"""
    
    def __init__(self, root, callbacks):
        """
        初始化GUI构建器
        
        Args:
            root: Tkinter根窗口
            callbacks: 回调函数字典，包含各按钮的回调函数
        """
        self.root = root
        self.callbacks = callbacks
        self.widgets = {}  # 存储所有创建的组件
        
        # 字体设置
        self.ui_font = ("Microsoft YaHei UI", 10)
        self.header_font = ("Microsoft YaHei UI", 12, "bold")
        
        # 创建主界面
        self.create_main_window()
    
    def create_main_window(self):
        """创建主窗口布局 - 使用Grid权重布局实现自适应"""
        # 主窗口布局配置
        self.root.columnconfigure(0, weight=1)  # 左侧画布区域可伸缩
        self.root.columnconfigure(1, weight=0)  # 右侧控制面板固定宽度
        self.root.rowconfigure(0, weight=1)     # 垂直方向可伸缩
        
        # --- 1. 左侧画布区域 ---
        self.create_canvas_area()
        
        # --- 2. 右侧控制面板 ---
        self.create_control_panel()
    
    def create_canvas_area(self):
        """创建左侧画布区域 - 带滚动条的深色主题画布"""
        # 预览框架
        self.widgets['preview_frame'] = ttk.LabelFrame(
            self.root, 
            text="预览视图 (Preview)", 
            padding=10
        )
        self.widgets['preview_frame'].grid(
            row=0, column=0, 
            padx=(20, 0), pady=20, 
            sticky="nsew"
        )
        
        # 配置预览框架的Grid权重
        self.widgets['preview_frame'].columnconfigure(0, weight=1)
        self.widgets['preview_frame'].rowconfigure(0, weight=1)
        self.widgets['preview_frame'].rowconfigure(1, weight=0)
        
        # 创建画布 - 深色背景
        self.widgets['canvas'] = tk.Canvas(
            self.widgets['preview_frame'], 
            bg="#313337", 
            highlightthickness=0
        )
        
        # 创建滚动条
        self.widgets['scroll_y'] = ttk.Scrollbar(
            self.widgets['preview_frame'], 
            orient="vertical", 
            command=self.widgets['canvas'].yview
        )
        self.widgets['scroll_x'] = ttk.Scrollbar(
            self.widgets['preview_frame'], 
            orient="horizontal", 
            command=self.widgets['canvas'].xview
        )
        
        # 配置画布滚动
        self.widgets['canvas'].configure(
            yscrollcommand=self.widgets['scroll_y'].set,
            xscrollcommand=self.widgets['scroll_x'].set
        )
        
        # 使用Grid布局放置画布和滚动条
        self.widgets['canvas'].grid(row=0, column=0, sticky="nsew")
        self.widgets['scroll_y'].grid(row=0, column=1, sticky="ns")
        self.widgets['scroll_x'].grid(row=1, column=0, sticky="ew")
        
        # 绑定鼠标事件
        self.widgets['canvas'].bind("<ButtonPress-1>", self.callbacks['on_mouse_down'])
        self.widgets['canvas'].bind("<B1-Motion>", self.callbacks['on_mouse_drag'])
        self.widgets['canvas'].bind("<ButtonRelease-1>", self.callbacks['on_mouse_up'])
        self.widgets['canvas'].bind("<Motion>", self.callbacks['on_mouse_move'])
    
    def create_control_panel(self):
        """创建右侧控制面板"""
        # 右侧面板容器
        self.widgets['right_panel'] = ttk.Frame(self.root, padding=20)
        self.widgets['right_panel'].grid(row=0, column=1, sticky="n", padx=0)
        
        # 模块容器
        self.widgets['modules_container'] = ttk.Frame(self.widgets['right_panel'], width=320)
        self.widgets['modules_container'].grid(row=0, column=0, sticky="n")
        
        # 1. 坐标设置
        self.create_coordinate_settings()
        
        # 2. 比例设置
        self.create_ratio_settings()
        
        # 3. 预览控制
        self.create_preview_controls()
        
        # 4. 操作按钮
        self.create_action_buttons()
    
    def create_file_operations(self):
        """创建文件操作区域"""
        file_group = ttk.LabelFrame(
            self.widgets['modules_container'], 
            text="文件操作", 
            padding=5
        )
        file_group.pack(fill="x", pady=(0, 15), ipadx=10)
        
        # 打开图片按钮
        self.widgets['open_btn'] = ttk.Button(
            file_group, 
            text="📂 打开图片", 
            command=self.callbacks['open_image']
        )
        self.widgets['open_btn'].pack(fill="x", pady=5)
    
    def create_coordinate_settings(self):
        """创建坐标设置区域"""
        coord_group = ttk.LabelFrame(
            self.widgets['modules_container'], 
            text="坐标设置", 
            padding=5
        )
        coord_group.pack(fill="x", pady=(0, 15), ipadx=10)
        
        # 配置Grid列，固定列宽
        coord_group.columnconfigure(0, weight=0, minsize=30)
        coord_group.columnconfigure(1, weight=0, minsize=60)
        coord_group.columnconfigure(2, weight=0, minsize=30)
        coord_group.columnconfigure(3, weight=0, minsize=60)
        
        # 起始位置
        ttk.Label(
            coord_group, 
            text="起始位置 (Top-Left):", 
            font=self.ui_font
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=5)
        
        self.widgets['x1_var'] = tk.StringVar(value="0")
        self.widgets['y1_var'] = tk.StringVar(value="0")
        self.create_spin_row(coord_group, 1, "X:", self.widgets['x1_var'], "Y:", self.widgets['y1_var'])
        
        # 结束位置
        ttk.Label(
            coord_group, 
            text="结束位置 (Bottom-Right):", 
            font=self.ui_font
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0), padx=5)
        
        self.widgets['x2_var'] = tk.StringVar(value="100")
        self.widgets['y2_var'] = tk.StringVar(value="100")
        self.create_spin_row(coord_group, 3, "X:", self.widgets['x2_var'], "Y:", self.widgets['y2_var'])
        
        # 尺寸和比例显示
        size_frame = ttk.Frame(coord_group)
        size_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 0), padx=5)
        self.widgets['size_label'] = ttk.Label(
            size_frame, 
            text="尺寸: 100 x 100 像素", 
            font=("Microsoft YaHei UI", 9)
        )
        self.widgets['size_label'].pack(side="left", anchor="w")
        
        # 比例显示标签
        self.widgets['ratio_label'] = ttk.Label(
            size_frame, 
            text="N/A", 
            foreground="blue", 
            font=("Microsoft YaHei UI", 9)
        )
        self.widgets['ratio_label'].pack(side="left", padx=(10, 0))
    
    def create_ratio_settings(self):
        """创建比例设置区域"""
        ratio_group = ttk.LabelFrame(
            self.widgets['modules_container'], 
            text="比例设置", 
            padding=5
        )
        ratio_group.pack(fill="x", pady=(0, 15), ipadx=10)
        
        # 配置Grid列，固定列宽
        ratio_group.columnconfigure(0, weight=0, minsize=100)
        ratio_group.columnconfigure(1, weight=0, minsize=100)
        
        # 比例选项
        self.widgets['ratio_var'] = tk.StringVar(value="free")
        
        ratios = [
            ("自由", "free"),
            ("锁定", "lock"),
            ("原始", "original"),
            ("1:1", "1:1"),
            ("16:9", "16:9"),
            ("4:3", "4:3"),
            ("3:2", "3:2"),
            ("2:3", "2:3")
        ]
        
        # 使用Grid布局创建单选按钮
        for i, (text, value) in enumerate(ratios):
            row = i // 2
            col = i % 2
            rb = ttk.Radiobutton(
                ratio_group, 
                text=text, 
                variable=self.widgets['ratio_var'], 
                value=value,
                command=lambda v=value: self.callbacks['on_ratio_change'](v)
            )
            rb.grid(row=row, column=col, sticky="w", padx=5, pady=2)
    
    def create_preview_controls(self):
        """创建预览控制区域"""
        preview_group = ttk.LabelFrame(
            self.widgets['modules_container'], 
            text="预览控制", 
            padding=5
        )
        preview_group.pack(fill="x", pady=(0, 15), ipadx=10)
        
        # 创建导航按钮容器（垂直排列）
        nav_container = ttk.Frame(preview_group)
        nav_container.pack(fill="x", pady=5)
        
        # --- 第一行：预览按钮 (独占一行，fill="x" 确保与下面对齐) ---
        preview_row = ttk.Frame(nav_container)
        preview_row.pack(fill="x")
        
        self.widgets['preview_crop_btn'] = ttk.Button(
            preview_row, 
            text="裁剪预览", 
            command=self.callbacks['preview_crop']
        )
        # expand=True 让它占据整行剩余空间，fill="x" 让它拉伸到满
        self.widgets['preview_crop_btn'].pack(side="left", padx=5, pady=2, fill="x", expand=True)
        self.create_tooltip(self.widgets['preview_crop_btn'], "裁剪预览")
        
        # --- 第二行：四个导航按钮 (四人平分一行) ---
        nav_row = ttk.Frame(nav_container)
        nav_row.pack(fill="x")
        
        nav_configs = [
            ('first_btn', "⏮", 'first', "第一张"),
            ('prev_btn', "⏴", 'prev', "上一张"),
            ('next_btn', "⏵", 'next', "下一张"),
            ('last_btn', "⏭", 'last', "最后一张")
        ]
        
        for key, icon, action, tip in nav_configs:
            self.widgets[key] = ttk.Button(
                nav_row, 
                text=icon, 
                width=2, # 限制字符宽度
                command=lambda a=action: self.callbacks['navigate_image'](a)
            )
            # 关键点：所有按钮都设 expand=True，它们会平分父容器宽度
            # padx=5 保持与上方预览按钮及其他功能按钮一致的间距
            self.widgets[key].pack(side="left", padx=5, pady=2, fill="x", expand=True)
            self.create_tooltip(self.widgets[key], tip)
        
        # 当前图片显示标签
        self.widgets['current_img_label'] = ttk.Label(
            preview_group, 
            text="1 / 1", 
            font=("Microsoft YaHei UI", 9)
        )
        self.widgets['current_img_label'].pack(pady=(5, 0))
    
    def create_action_buttons(self):
        """创建操作按钮区域"""
        # 分隔线
        ttk.Separator(
            self.widgets['modules_container'], 
            orient="horizontal"
        ).pack(fill="x", pady=(10, 10))
        
        # 缩放控制按钮行
        zoom_row = ttk.Frame(self.widgets['modules_container'])
        zoom_row.pack(fill="x", pady=(0, 10))
        
        # 适应窗口按钮
        self.widgets['fit_btn'] = ttk.Button(
            zoom_row, 
            text="⬜", 
            command=self.callbacks['fit_to_window']
        )
        self.widgets['fit_btn'].pack(side="left", padx=5, fill="x", expand=True)
        # 添加鼠标悬浮提示
        self.create_tooltip(self.widgets['fit_btn'], "适应窗口")
        
        # 原始大小按钮
        self.widgets['original_btn'] = ttk.Button(
            zoom_row, 
            text="🔄", 
            command=self.callbacks['original_size']
        )
        self.widgets['original_btn'].pack(side="left", padx=5, fill="x", expand=True)
        # 添加鼠标悬浮提示
        self.create_tooltip(self.widgets['original_btn'], "原始大小")
        
        # 操作按钮行
        btn_row = ttk.Frame(self.widgets['modules_container'])
        btn_row.pack(fill="x", pady=(0, 10))

        # 确认裁剪按钮
        self.widgets['crop_btn'] = ttk.Button(
            btn_row,
            text="✅",
            command=self.callbacks['confirm_crop']
        )
        self.widgets['crop_btn'].pack(side="left", padx=5, fill="x", expand=True)
        # 添加鼠标悬浮提示
        self.create_tooltip(self.widgets['crop_btn'], "确认裁剪")

        # 添加鼠标悬浮提示
        self.create_tooltip(self.widgets['crop_btn'], "确认裁剪")
    
    
    
    def create_spin_row(self, parent, row, label1, var1, label2, var2):
        """辅助函数：创建一行两个带标签的微调框"""
        ttk.Label(parent, text=label1).grid(row=row, column=0, sticky="w", padx=5)
        s1 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var1, width=6)
        s1.grid(row=row, column=1, sticky="w", padx=(2, 5), pady=5)
        
        ttk.Label(parent, text=label2).grid(row=row, column=2, sticky="w", padx=5)
        s2 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var2, width=6)
        s2.grid(row=row, column=3, sticky="w", padx=(2, 5), pady=5)
    
    def get_widget(self, name):
        """
        获取指定的组件
        
        Args:
            name: 组件名称
            
        Returns:
            Tkinter组件对象，如果不存在则返回None
        """
        return self.widgets.get(name)
    
    def create_tooltip(self, widget, text):
        """
        为组件创建鼠标悬浮提示
        
        Args:
            widget: Tkinter组件
            text: 提示文本
        """
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+0+0")
        tooltip.withdraw()
        
        label = tk.Label(
            tooltip,
            text=text,
            background="#FFFFE0",
            relief="solid",
            borderwidth=1,
            font=("Microsoft YaHei UI", 9)
        )
        label.pack()
        
        def show_tooltip(event):
            x = widget.winfo_rootx() + event.x + 10
            y = widget.winfo_rooty() + event.y + 10
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def hide_tooltip(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)


class CropDialog:
    """裁剪对话框类，用于在主窗口中显示裁剪界面"""
    
    def __init__(self, root, image_path, image_paths, current_index):
        """
        初始化裁剪对话框
        
        Args:
            root: 父窗口
            image_path: 当前图片路径
            image_paths: 所有图片路径列表
            current_index: 当前图片索引
        """
        self.root = root
        self.image_path = image_path
        self.image_paths = image_paths
        self.current_index = current_index
        self.result = None  # 存储裁剪结果
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(root)
        self.dialog.title("图片裁剪")
        self.dialog.geometry("1280x720")
        self.dialog.minsize(800, 600)
        
        # 先隐藏窗口，等待所有组件初始化完成后再显示
        self.dialog.withdraw()
        
        # 设置窗口居中
        self.center_window()
        
        # 模态对话框
        self.dialog.transient(root)
        self.dialog.grab_set()
        
        # 图像相关变量
        self.original_image = None
        self.display_image = None
        self.photo_image = None
        self.scale_factor = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        # 裁剪框相关变量
        self.start_x = 0
        self.start_y = 0
        self.current_rect = None
        self.selection_coords = None
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_moving_rect = False
        
        # 控制点相关变量
        self.handles = {}
        self.dragging_handle = None
        self.drag_start_pos = None
        self.drag_start_coords = None
        self.handle_size = 8
        
        # 设置固定比例字典
        self.aspect_ratios = {
            "free": None,
            "lock": None,
            "original": None,
            "1:1": 1.0,
            "16:9": 16/9,
            "4:3": 4/3,
            "3:2": 3/2,
            "2:3": 2/3
        }
        self.current_ratio = None
        self.locked_ratio = None
        self.original_ratio = None
        
        # 图片导航相关变量
        self.current_image_index = current_index  # 当前图片索引
        self.image_paths = image_paths  # 所有图片路径
        
        # 预览模式相关变量
        self.is_preview_mode = False  # 是否处于预览模式
        self.preview_bind_id = None  # 预览点击事件绑定ID
        self.is_during_drag_operation = False  # 是否在拖动操作期间
        
        # 创建GUI界面
        self.setup_gui()
        
        # 显示窗口（所有组件初始化完成后）
        self.dialog.deiconify()
        self.dialog.update_idletasks()
        
        # 加载图片（在窗口显示后，确保画布尺寸正确）
        self.load_image(image_path)

        # 初始化预览按钮状态
        self.update_preview_button_state()

        # 更新导航按钮状态
        self.update_navigation_buttons()

        # 等待对话框关闭
        self.dialog.wait_window()
    
    def center_window(self):
        """将窗口居中显示"""
        # 获取屏幕尺寸
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # 使用设置的默认尺寸
        width = 1280
        height = 720
        
        # 计算居中位置
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # 在窗口显示前就设置好位置
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_gui(self):
        """设置GUI界面"""
        # 定义回调函数
        callbacks = {
            'on_ratio_change': self.on_ratio_change_wrapper,
            'confirm_crop': self.confirm_crop,
            'save_cropped_image': self.save_cropped_image,
            'on_mouse_down': self.on_mouse_down,
            'on_mouse_drag': self.on_mouse_drag,
            'on_mouse_up': self.on_mouse_up,
            'on_mouse_move': self.on_mouse_move,
            'fit_to_window': self.fit_to_window,
            'original_size': self.original_size,
            'preview_crop': self.preview_crop,
            'navigate_image': self.navigate_image
        }

        # 创建GUI构建器
        self.gui = GUIBuilder(self.dialog, callbacks)

        # 配置按钮样式
        self.style = ttk.Style()
        self.style.configure('Active.TButton', background='#cccccc', foreground='black')
    
    def load_image(self, image_path):
        """加载图片文件"""
        try:
            # 加载原始图像
            self.original_image = Image.open(image_path)
            
            # 延迟加载图片，确保画布尺寸正确
            self.dialog.after(50, self._load_image_delayed)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片：{str(e)}")
    
    def _load_image_delayed(self):
        """延迟加载图片的内部方法"""
        # 计算缩放比例以适应画布
        self.calculate_scale_and_display()

        # 启用裁剪按钮
        self.gui.get_widget('crop_btn').config(state=tk.NORMAL)

        # 禁用保存按钮（直到用户确认裁剪）
        save_btn = self.gui.get_widget('save_btn')
        if save_btn:
            save_btn.config(state=tk.DISABLED)

        # 检查是否正在进行导航操作，如果是，则保留选择框
        if hasattr(self, '_saved_selection_for_navigation'):
            # 这是导航操作，保留选择框
            saved_data = self._saved_selection_for_navigation
            was_in_preview = saved_data['was_in_preview']
            saved_coords = saved_data.get('coords')

            # 删除临时存储的数据
            del self._saved_selection_for_navigation

            # 如果之前有预览模式，现在恢复它
            if was_in_preview and saved_coords:
                # 重新创建选择框（使用相对坐标）
                self._restore_selection_from_saved(saved_coords)

                # 延迟进入预览模式，确保图片和选择框都已加载完成
                self.dialog.after(100, self.enter_preview_mode)
        else:
            # 非导航操作，清除之前的选择框
            self.clear_selection()

        # 更新当前图片显示
        self.update_current_image_label()

        # 更新导航按钮状态
        self.update_navigation_buttons()
    
    def _restore_selection_from_saved(self, saved_coords):
        """从保存的坐标恢复选择框"""
        if not saved_coords or not self.original_image:
            return

        # 计算原始图片的尺寸
        orig_img_width, orig_img_height = self.original_image.size

        # 如果之前的选择框坐标是基于原始图片的，我们需要计算相对位置
        # 但首先需要确定保存的坐标是哪种类型
        # 如果是基于显示图片的坐标，需要先转换为原始图片坐标
        if self.display_image:
            x1_orig, y1_orig, x2_orig, y2_orig = saved_coords

            # 将显示坐标转换为原始图片坐标
            orig_x1 = int(x1_orig / self.scale_factor) if self.scale_factor > 0 else 0
            orig_y1 = int(y1_orig / self.scale_factor) if self.scale_factor > 0 else 0
            orig_x2 = int(x2_orig / self.scale_factor) if self.scale_factor > 0 else 0
            orig_y2 = int(y2_orig / self.scale_factor) if self.scale_factor > 0 else 0

            # 限制在原始图片范围内
            orig_x1 = max(0, min(orig_x1, orig_img_width))
            orig_y1 = max(0, min(orig_y1, orig_img_height))
            orig_x2 = max(0, min(orig_x2, orig_img_width))
            orig_y2 = max(0, min(orig_y2, orig_img_height))

            # 计算相对位置（百分比）
            rel_x1 = orig_x1 / orig_img_width if orig_img_width > 0 else 0
            rel_y1 = orig_y1 / orig_img_height if orig_img_height > 0 else 0
            rel_x2 = orig_x2 / orig_img_width if orig_img_width > 0 else 0
            rel_y2 = orig_y2 / orig_img_height if orig_img_height > 0 else 0
        else:
            # 如果没有显示图片，使用默认值
            rel_x1, rel_y1, rel_x2, rel_y2 = 0.25, 0.25, 0.75, 0.75  # 默认中间区域

        # 根据新图片的尺寸计算新坐标
        new_x1 = int(rel_x1 * orig_img_width)
        new_y1 = int(rel_y1 * orig_img_height)
        new_x2 = int(rel_x2 * orig_img_width)
        new_y2 = int(rel_y2 * orig_img_height)

        # 限制坐标在图片范围内
        new_x1 = max(0, min(new_x1, orig_img_width))
        new_y1 = max(0, min(new_y1, orig_img_height))
        new_x2 = max(0, min(new_x2, orig_img_width))
        new_y2 = max(0, min(new_y2, orig_img_height))

        # 计算在当前显示比例下的坐标
        new_scaled_x1 = int(new_x1 * self.scale_factor)
        new_scaled_y1 = int(new_y1 * self.scale_factor)
        new_scaled_x2 = int(new_x2 * self.scale_factor)
        new_scaled_y2 = int(new_y2 * self.scale_factor)

        # 创建新选择框
        canvas = self.gui.get_widget('canvas')
        if self.current_rect:
            canvas.delete(self.current_rect)
        self.clear_handles()

        self.current_rect = canvas.create_rectangle(
            new_scaled_x1, new_scaled_y1, new_scaled_x2, new_scaled_y2,
            outline="red",
            width=2,
            dash=(5, 5),
            tags="selection"
        )

        # 保存新选择框坐标
        self.selection_coords = (new_scaled_x1, new_scaled_y1, new_scaled_x2, new_scaled_y2)
        self.draw_handles(new_scaled_x1, new_scaled_y1, new_scaled_x2, new_scaled_y2)
        self.update_size_label()

    def update_current_image_label(self):
        """更新当前图片显示标签"""
        label = self.gui.get_widget('current_img_label')
        if label:
            label.config(text=f"{self.current_image_index + 1} / {len(self.image_paths)}")
    
    def update_navigation_buttons(self):
        """更新导航按钮的状态"""
        if hasattr(self, 'gui'):
            nav_buttons = ['first_btn', 'prev_btn', 'next_btn', 'last_btn']
            # 根据图片数量启用或禁用导航按钮
            enable_nav = len(self.image_paths) > 1

            for btn_name in nav_buttons:
                btn = self.gui.get_widget(btn_name)
                if btn:
                    if enable_nav:
                        btn.config(state=tk.NORMAL)
                    else:
                        btn.config(state=tk.DISABLED)

    def navigate_image(self, direction):
            """导航到其他图片"""
            if not self.image_paths or len(self.image_paths) <= 1:
                return
            
            # 保存当前的预览模式状态
            was_in_preview_mode = self.is_preview_mode
            
            old_index = self.current_image_index
    
            if direction == 'first':
                self.current_image_index = 0
            elif direction == 'prev':
                self.current_image_index = max(0, self.current_image_index - 1)
            elif direction == 'next':
                self.current_image_index = min(len(self.image_paths) - 1, self.current_image_index + 1)
            elif direction == 'last':
                self.current_image_index = len(self.image_paths) - 1
    
            # 如果索引改变了，加载新图片
            if old_index != self.current_image_index:
                # 立即更新当前图片标签显示
                self.update_current_image_label()

                # 在加载新图片前，保存当前的选择框信息
                self._saved_selection_for_navigation = {
                    'coords': self.selection_coords,
                    'was_in_preview': was_in_preview_mode
                }

                self.load_image(self.image_paths[self.current_image_index])

    def toggle_preview_crop(self):
        """切换预览裁剪模式 - 进入/退出裁剪预览"""
        if not self.original_image or not self.selection_coords:
            messagebox.showwarning("警告", "请先在图像上选择裁剪区域")
            return

        # 如果当前处于预览模式，则退出预览模式
        if self.is_preview_mode:
            self.close_preview()
        else:
            # 进入预览模式
            try:
                x1, y1, x2, y2 = self.selection_coords

                img_x1 = (x1 - self.image_offset_x) / self.scale_factor
                img_y1 = (y1 - self.image_offset_y) / self.scale_factor
                img_x2 = (x2 - self.image_offset_x) / self.scale_factor
                img_y2 = (y2 - self.image_offset_y) / self.scale_factor

                img_x1, img_x2 = min(img_x1, img_x2), max(img_x1, img_x2)
                img_y1, img_y2 = min(img_y1, img_y2), max(img_y1, img_y2)

                cropped_image = self.original_image.crop((img_x1, img_y1, img_x2, img_y2))

                # 设置预览模式标志
                self.is_preview_mode = True

                # 在原图上显示裁剪预览
                self.show_crop_on_canvas(cropped_image, x1, y1, x2, y2)

                # 更新按钮文本
                self.update_preview_button_state()

            except Exception as e:
                messagebox.showerror("错误", f"预览失败：{str(e)}")

    def enter_preview_mode(self):
        """进入裁剪预览模式"""
        if not self.original_image or not self.selection_coords:
            return

        try:
            # 如果当前已经是预览模式，先关闭当前预览
            if self.is_preview_mode:
                # 临时保存预览模式状态
                was_in_preview = self.is_preview_mode
                # 关闭当前预览
                self.close_preview()
                # 恢复预览状态标记
                self.is_preview_mode = was_in_preview

            x1, y1, x2, y2 = self.selection_coords

            img_x1 = (x1 - self.image_offset_x) / self.scale_factor
            img_y1 = (y1 - self.image_offset_y) / self.scale_factor
            img_x2 = (x2 - self.image_offset_x) / self.scale_factor
            img_y2 = (y2 - self.image_offset_y) / self.scale_factor

            img_x1, img_x2 = min(img_x1, img_x2), max(img_x1, img_x2)
            img_y1, img_y2 = min(img_y1, img_y2), max(img_y1, img_y2)

            cropped_image = self.original_image.crop((img_x1, img_y1, img_x2, img_y2))

            # 设置预览模式标志
            self.is_preview_mode = True

            # 在原图上显示裁剪预览
            self.show_crop_on_canvas(cropped_image, x1, y1, x2, y2)

            # 更新按钮文本
            self.update_preview_button_state()

        except Exception as e:
            pass  # 静默处理错误，避免在切换图片时弹出错误窗口

    def update_preview_button_state(self):
        """更新预览按钮的状态显示"""
        if hasattr(self, 'gui'):
            button = self.gui.get_widget('preview_crop_btn')
            if button:
                if self.is_preview_mode:
                    button.config(text="退出预览")
                    # 更改按钮的样式以表示激活状态
                    button.config(style='Active.TButton')
                else:
                    button.config(text="裁剪预览")
                    button.config(style='TButton')

    def preview_crop(self):
        """预览裁剪结果 - 在原图上显示（保持原有方法兼容性）"""
        self.toggle_preview_crop()
    
    def show_crop_on_canvas(self, cropped_image, x1, y1, x2, y2):
        """在画布上显示裁剪预览"""
        canvas = self.gui.get_widget('canvas')

        # 确保坐标顺序正确
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # 计算裁剪区域的大小
        crop_width = x2 - x1
        crop_height = y2 - y1

        # 先删除旧的预览图层
        canvas.delete("preview_mask")
        canvas.delete("preview_area")
        canvas.delete("preview_image")
        canvas.delete("preview_text")

        # 在画布上创建一个半透明的遮罩层
        # 先创建一个覆盖整个画布的半透明黑色矩形
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # 创建半透明遮罩（使用 stipple 模拟透明效果）
        canvas.create_rectangle(
            0, 0, canvas_width, canvas_height,
            fill="black",
            stipple="gray50",
            tags=("preview_mask", "preview_region")
        )

        # 清除裁剪区域的遮罩，让裁剪区域清晰显示
        # 在裁剪区域绘制一个白色矩形作为背景
        canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="white",
            outline="yellow",
            width=3,
            tags=("preview_area", "preview_region")
        )

        # 在裁剪区域显示裁剪后的图片
        # 计算缩放比例以适应裁剪区域
        img_width, img_height = cropped_image.size
        scale_x = crop_width / img_width
        scale_y = crop_height / img_height

        # 如果裁剪区域比原图小，需要缩放
        if scale_x < 1 or scale_y < 1:
            scale = min(scale_x, scale_y)
            display_width = int(img_width * scale)
            display_height = int(img_height * scale)
            cropped_display = cropped_image.resize(
                (display_width, display_height),
                Image.Resampling.LANCZOS
            )
        else:
            cropped_display = cropped_image
            display_width = crop_width
            display_height = crop_height

        # 转换为 Tkinter 图像对象
        preview_photo = ImageTk.PhotoImage(cropped_display)

        # 居中显示在裁剪区域内
        offset_x = x1 + (crop_width - display_width) // 2
        offset_y = y1 + (crop_height - display_height) // 2

        # 在裁剪区域显示预览图片
        canvas.create_image(
            offset_x, offset_y,
            image=preview_photo,
            anchor=tk.NW,
            tags=("preview_image", "preview_region")
        )

        # 保存引用以防止被垃圾回收
        canvas.preview_photo = preview_photo

        # 显示裁剪尺寸信息
        info_text = f"裁剪尺寸: {img_width} x {img_height} 像素"
        canvas.create_text(
            x1 + crop_width // 2, y1 - 15,
            text=info_text,
            fill="yellow",
            font=("Arial", 10, "bold"),
            tags=("preview_text", "preview_region")
        )

        # 移除"点击外部区域关闭预览"的提示，因为现在只通过按钮控制

        # 不再绑定点击事件来关闭预览，只通过按钮控制
        # self.preview_bind_id = canvas.bind("<Button-1>", self.close_preview, add="+")
    
    def close_preview(self, event=None):
        """关闭预览"""
        # 如果正在拖动操作中，不执行关闭操作
        if self.is_during_drag_operation:
            return

        canvas = self.gui.get_widget('canvas')
        canvas.delete("preview_mask")
        canvas.delete("preview_area")
        canvas.delete("preview_image")
        canvas.delete("preview_text")

        # 清除预览模式标志
        self.is_preview_mode = False

        # 更新按钮状态
        self.update_preview_button_state()
    
    def update_preview(self):
        """更新预览 - 在移动或调整裁剪框时实时更新预览"""
        if not self.original_image or not self.selection_coords:
            return

        try:
            x1, y1, x2, y2 = self.selection_coords

            img_x1 = (x1 - self.image_offset_x) / self.scale_factor
            img_y1 = (y1 - self.image_offset_y) / self.scale_factor
            img_x2 = (x2 - self.image_offset_x) / self.scale_factor
            img_y2 = (y2 - self.image_offset_y) / self.scale_factor

            img_x1, img_x2 = min(img_x1, img_x2), max(img_x1, img_x2)
            img_y1, img_y2 = min(img_y1, img_y2), max(img_y1, img_y2)

            cropped_image = self.original_image.crop((img_x1, img_y1, img_x2, img_y2))

            # 更新预览显示
            self.show_crop_on_canvas(cropped_image, x1, y1, x2, y2)

            # 将裁剪框和控制点提升到最上层，确保可以交互
            canvas = self.gui.get_widget('canvas')
            if self.current_rect:
                canvas.tag_raise(self.current_rect)
            for handle in self.handles.values():
                canvas.tag_raise(handle)

            # 保持预览模式状态
            self.is_preview_mode = True

        except Exception as e:
            pass  # 静默处理错误，避免在拖动时弹出错误窗口
    
    def calculate_scale_and_display(self):
        """计算缩放比例并在画布上显示图像"""
        if not self.original_image:
            return
        
        # 获取画布
        canvas = self.gui.get_widget('canvas')
        
        # 获取画布尺寸
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        # 如果画布还未显示，使用默认值
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600
        
        # 获取原始图像尺寸
        img_width, img_height = self.original_image.size
        
        # 计算缩放比例（保持宽高比）
        scale_x = (canvas_width - 40) / img_width
        scale_y = (canvas_height - 40) / img_height
        self.scale_factor = min(scale_x, scale_y)
        
        # 计算显示尺寸
        display_width = int(img_width * self.scale_factor)
        display_height = int(img_height * self.scale_factor)
        
        # 缩放图像
        self.display_image = self.original_image.resize(
            (display_width, display_height),
            Image.Resampling.LANCZOS
        )
        
        # 转换为 Tkinter 图像对象
        self.photo_image = ImageTk.PhotoImage(self.display_image)
        
        # 计算居中位置
        self.image_offset_x = (canvas_width - display_width) // 2
        self.image_offset_y = (canvas_height - display_height) // 2
        
        # 设置滚动区域
        canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # 在画布上显示图像
        canvas.delete("all")
        canvas.create_image(
            self.image_offset_x, 
            self.image_offset_y,
            image=self.photo_image, 
            anchor=tk.NW,
            tags="image"
        )
        
        # 绘制图片边框
        border_padding = 1
        canvas.create_rectangle(
            self.image_offset_x - border_padding, 
            self.image_offset_y - border_padding,
            self.image_offset_x + display_width + border_padding, 
            self.image_offset_y + display_height + border_padding,
            outline="#CCCCCC",
            width=2,
            tags="image_border"
        )
        
        # 更新坐标显示
        self.update_coordinate_display(img_width, img_height)
    
    def update_coordinate_display(self, img_width, img_height):
        """更新坐标显示"""
        x1_var = self.gui.get_widget('x1_var')
        y1_var = self.gui.get_widget('y1_var')
        x2_var = self.gui.get_widget('x2_var')
        y2_var = self.gui.get_widget('y2_var')
        
        if x1_var:
            x1_var.set("0")
            y1_var.set("0")
            x2_var.set(str(img_width))
            y2_var.set(str(img_height))
        
        self.update_size_label()
    
    def update_size_label(self):
        """更新尺寸标签显示"""
        if not self.selection_coords:
            return

        x1, y1, x2, y2 = self.selection_coords

        # 确保坐标顺序正确
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        # 转换为图像坐标
        img_x1 = int((x1 - self.image_offset_x) / self.scale_factor)
        img_y1 = int((y1 - self.image_offset_y) / self.scale_factor)
        img_x2 = int((x2 - self.image_offset_x) / self.scale_factor)
        img_y2 = int((y2 - self.image_offset_y) / self.scale_factor)

        width = img_x2 - img_x1
        height = img_y2 - img_y1

        # 更新尺寸标签
        size_label = self.gui.get_widget('size_label')
        if size_label:
            size_label.config(text=f"尺寸: {width} x {height} 像素")

        # 更新比例显示
        self.update_ratio_display()

        # 更新坐标输入框
        x1_var = self.gui.get_widget('x1_var')
        y1_var = self.gui.get_widget('y1_var')
        x2_var = self.gui.get_widget('x2_var')
        y2_var = self.gui.get_widget('y2_var')

        if x1_var and y1_var and x2_var and y2_var:
            x1_var.set(str(max(0, img_x1)))
            y1_var.set(str(max(0, img_y1)))
            x2_var.set(str(max(0, img_x2)))
            y2_var.set(str(max(0, img_y2)))

        # 启用保存按钮，因为现在有了选择区域
        save_btn = self.gui.get_widget('save_btn')
        if save_btn:
            save_btn.config(state=tk.NORMAL)
    
    def update_ratio_display(self):
        """更新当前比例显示"""
        if not self.selection_coords:
            return
        
        x1, y1, x2, y2 = self.selection_coords
        
        # 确保坐标顺序正确
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        # 转换为图像坐标
        img_x1 = int((x1 - self.image_offset_x) / self.scale_factor)
        img_y1 = int((y1 - self.image_offset_y) / self.scale_factor)
        img_x2 = int((x2 - self.image_offset_x) / self.scale_factor)
        img_y2 = int((y2 - self.image_offset_y) / self.scale_factor)
        
        width = img_x2 - img_x1
        height = img_y2 - img_y1
        
        # 计算当前比例
        if height > 0:
            current_ratio = width / height
            # 格式化比例显示
            if current_ratio >= 1:
                ratio_text = f"{current_ratio:.2f}:1"
            elif current_ratio > 0:
                ratio_text = f"1:{1/current_ratio:.2f}"
            else:
                ratio_text = "N/A"
        else:
            ratio_text = "N/A"
        
        # 更新比例标签
        ratio_label = self.gui.get_widget('ratio_label')
        if ratio_label:
            ratio_label.config(text=ratio_text)
    
    def open_image(self):
        """打开图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        self.load_image(file_path)
    
    def on_ratio_change_wrapper(self, value):
        """比例选择改变的包装函数"""
        if value == "lock":
            if self.selection_coords:
                x1, y1, x2, y2 = self.selection_coords
                # 转换为原始图像坐标
                img_x1 = (x1 - self.image_offset_x) / self.scale_factor
                img_y1 = (y1 - self.image_offset_y) / self.scale_factor
                img_x2 = (x2 - self.image_offset_x) / self.scale_factor
                img_y2 = (y2 - self.image_offset_y) / self.scale_factor
                
                width = abs(img_x2 - img_x1)
                height = abs(img_y2 - img_y1)
                if height > 0:
                    self.locked_ratio = width / height
                    self.current_ratio = self.locked_ratio
                else:
                    self.locked_ratio = None
                    self.current_ratio = None
            else:
                self.locked_ratio = None
                self.current_ratio = None
        elif value == "original":
            if self.original_image:
                img_width, img_height = self.original_image.size
                self.original_ratio = img_width / img_height
                self.current_ratio = self.original_ratio
            else:
                self.original_ratio = None
                self.current_ratio = None
        else:
            # 切换到预设比例时，清除现有裁剪框
            self.current_ratio = self.aspect_ratios.get(value)
        
        self.update_ratio_display()
        
        # 只在选择预设比例（非锁定、非原始）时清除裁剪框
        if self.current_rect and value not in ["lock", "original"]:
            self.clear_selection()
    
    def fit_to_window(self):
        """适应窗口"""
        if not self.original_image:
            return
        self.scale_factor = None
        self.calculate_scale_and_display()
    
    def original_size(self):
        """原始大小"""
        if not self.original_image:
            return
        
        canvas = self.gui.get_widget('canvas')
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600
        
        img_width, img_height = self.original_image.size
        self.scale_factor = 1.0
        
        display_width = img_width
        display_height = img_height
        
        self.display_image = self.original_image
        self.photo_image = ImageTk.PhotoImage(self.display_image)
        
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        border_padding = 1
        canvas.configure(scrollregion=(0, 0, display_width + border_padding * 2, display_height + border_padding * 2))
        
        canvas.delete("all")
        canvas.create_image(
            self.image_offset_x, 
            self.image_offset_y,
            image=self.photo_image, 
            anchor=tk.NW,
            tags="image"
        )
        
        canvas.create_rectangle(
            self.image_offset_x - border_padding, 
            self.image_offset_y - border_padding,
            self.image_offset_x + display_width + border_padding, 
            self.image_offset_y + display_height + border_padding,
            outline="#CCCCCC",
            width=2,
            tags="image_border"
        )
        
        self.update_coordinate_display(img_width, img_height)
    
    def on_mouse_down(self, event):
        """鼠标按下事件"""
        if not self.original_image:
            return

        # 如果处于预览模式，检查点击位置
        if self.is_preview_mode:
            # 检查是否点击了控制点
            handle = self.get_handle_at_position(event.x, event.y)
            if handle:
                # 点击控制点，保持预览模式并开始拖动
                self.dragging_handle = handle
                self.drag_start_pos = (event.x, event.y)
                self.drag_start_coords = self.selection_coords
                # 标记正在进行拖动操作
                self.is_during_drag_operation = True
                return

            # 检查是否点击了裁剪框内部
            if self.selection_coords and self.is_point_in_rect(event.x, event.y, self.selection_coords):
                # 点击裁剪框内部，保持预览模式并开始移动
                self.is_moving_rect = True
                self.drag_offset_x = event.x
                self.drag_offset_y = event.y
                # 标记正在进行拖动操作
                self.is_during_drag_operation = True
                return

            # 在预览模式下，点击外部区域不再关闭预览
            # 只有通过按钮才能退出预览模式
            return

        # 非预览模式的正常处理
        handle = self.get_handle_at_position(event.x, event.y)
        if handle:
            self.dragging_handle = handle
            self.drag_start_pos = (event.x, event.y)
            self.drag_start_coords = self.selection_coords
            return

        if self.selection_coords and self.is_point_in_rect(event.x, event.y, self.selection_coords):
            self.is_moving_rect = True
            self.drag_offset_x = event.x
            self.drag_offset_y = event.y
            return

        self.start_x = event.x
        self.start_y = event.y
        self.is_moving_rect = False
        self.clear_selection()
    
    def on_mouse_drag(self, event):
        """鼠标拖动事件"""
        if not self.original_image:
            return
        
        if self.dragging_handle:
            self.handle_drag(event)
        elif self.is_moving_rect and self.selection_coords:
            self.move_selection_box(event.x, event.y)
        else:
            self.create_selection_box(event.x, event.y)
    
    def _unbind_preview_click(self):
        """临时解除预览的点击事件绑定（不再需要，保留以兼容）"""
        pass

    def _rebind_preview_click(self):
        """重新绑定预览的点击事件（不再需要，保留以兼容）"""
        pass

    def on_mouse_up(self, event):
        """鼠标释放事件"""
        if not self.original_image or not self.selection_coords:
            return

        self.is_moving_rect = False
        self.dragging_handle = None
        self.drag_start_pos = None
        self.drag_start_coords = None
        # 重置拖动操作标志
        self.is_during_drag_operation = False

        # 保持预览模式状态
        if self.is_preview_mode:
            # 在预览模式下，裁剪按钮应该保持可用状态
            self.gui.get_widget('crop_btn').config(state=tk.NORMAL)
            # 更新预览显示
            self.update_preview()
        else:
            # 非预览模式下，裁剪按钮也应该是可用的
            self.gui.get_widget('crop_btn').config(state=tk.NORMAL)

        # 如果有选择区域，启用保存按钮
        if self.selection_coords:
            save_btn = self.gui.get_widget('save_btn')
            if save_btn:
                save_btn.config(state=tk.NORMAL)
    
    def on_mouse_move(self, event):
        """鼠标移动事件"""
        if not self.original_image:
            return
        
        canvas = self.gui.get_widget('canvas')
        
        handle = self.get_handle_at_position(event.x, event.y)
        if handle:
            cursor_map = {
                'nw': 'size_nw_se',
                'n': 'sb_v_double_arrow',
                'ne': 'size_ne_sw',
                'e': 'sb_h_double_arrow',
                'se': 'size_nw_se',
                's': 'sb_v_double_arrow',
                'sw': 'size_ne_sw',
                'w': 'sb_h_double_arrow'
            }
            canvas.config(cursor=cursor_map.get(handle, 'cross'))
        elif self.selection_coords and self.is_point_in_rect(event.x, event.y, self.selection_coords):
            canvas.config(cursor="fleur")
        else:
            canvas.config(cursor="cross")
    
    def create_selection_box(self, current_x, current_y):
        """创建新的裁剪框"""
        canvas = self.gui.get_widget('canvas')

        width = current_x - self.start_x
        height = current_y - self.start_y

        if self.current_ratio is not None:
            width, height = self.adjust_to_aspect_ratio(width, height)

        x1 = self.start_x
        y1 = self.start_y
        x2 = self.start_x + width
        y2 = self.start_y + height

        # 确保裁剪框不超出图片边界
        x1, y1, x2, y2 = self.clamp_to_image_bounds(x1, y1, x2, y2)

        if self.current_rect:
            canvas.delete(self.current_rect)
        self.clear_handles()

        self.current_rect = canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red",
            width=2,
            dash=(5, 5),
            tags="selection"
        )

        self.selection_coords = (x1, y1, x2, y2)
        self.draw_handles(x1, y1, x2, y2)
        self.update_size_label()

        # 如果处于预览模式，更新预览
        if self.is_preview_mode:
            self.update_preview()
    
    def move_selection_box(self, current_x, current_y):
        """移动现有的裁剪框"""
        canvas = self.gui.get_widget('canvas')

        if not self.selection_coords:
            return

        dx = current_x - self.drag_offset_x
        dy = current_y - self.drag_offset_y

        x1, y1, x2, y2 = self.selection_coords

        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        new_x1 = x1 + dx
        new_y1 = y1 + dy
        new_x2 = x2 + dx
        new_y2 = y2 + dy

        new_x1, new_y1, new_x2, new_y2 = self.clamp_to_image_bounds(
            new_x1, new_y1, new_x2, new_y2
        )

        actual_dx = (new_x1 - x1)
        actual_dy = (new_y1 - y1)

        if self.current_rect:
            canvas.delete(self.current_rect)
        self.clear_handles()

        self.current_rect = canvas.create_rectangle(
            new_x1, new_y1, new_x2, new_y2,
            outline="red",
            width=2,
            dash=(5, 5),
            tags="selection"
        )

        self.selection_coords = (new_x1, new_y1, new_x2, new_y2)
        self.draw_handles(new_x1, new_y1, new_x2, new_y2)

        self.drag_offset_x = self.drag_offset_x + actual_dx
        self.drag_offset_y = self.drag_offset_y + actual_dy

        self.update_size_label()

        # 如果处于预览模式，更新预览
        if self.is_preview_mode:
            self.update_preview()
    
    def adjust_to_aspect_ratio(self, width, height):
        """根据固定比例调整宽度和高度"""
        if self.current_ratio is None or self.current_ratio == 0:
            return width, height
        
        if abs(width) < 1:
            width = 1
        if abs(height) < 1:
            height = 1
        
        if abs(width) >= abs(height):
            adjusted_height = width / self.current_ratio
            return width, adjusted_height
        else:
            adjusted_width = height * self.current_ratio
            return adjusted_width, height
    
    def clamp_to_image_bounds(self, x1, y1, x2, y2):
        """限制裁剪框在图像显示范围内"""
        if not self.display_image:
            return x1, y1, x2, y2
        
        img_left = self.image_offset_x
        img_top = self.image_offset_y
        img_right = self.image_offset_x + self.display_image.width
        img_bottom = self.image_offset_y + self.display_image.height
        
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        rect_width = x2 - x1
        rect_height = y2 - y1
        
        if self.current_ratio is not None:
            return self.clamp_with_aspect_ratio(x1, y1, rect_width, rect_height, 
                                               img_left, img_top, img_right, img_bottom)
        else:
            new_x1 = max(img_left, min(x1, img_right - rect_width))
            new_y1 = max(img_top, min(y1, img_bottom - rect_height))
            new_x2 = new_x1 + rect_width
            new_y2 = new_y1 + rect_height
            return new_x1, new_y1, new_x2, new_y2
    
    def clamp_with_aspect_ratio(self, x1, y1, width, height, img_left, img_top, img_right, img_bottom):
        """固定比例下的滑动边界检测"""
        x2 = x1 + width
        y2 = y1 + height
        
        if x1 < img_left:
            x1 = img_left
            x2 = x1 + width
        
        if x2 > img_right:
            x2 = img_right
            x1 = x2 - width
        
        if y1 < img_top:
            y1 = img_top
            y2 = y1 + height
        
        if y2 > img_bottom:
            y2 = img_bottom
            y1 = y2 - height
        
        max_width = img_right - img_left
        max_height = img_bottom - img_top
        
        if max_width / max_height > self.current_ratio:
            limited_height = max_height
            limited_width = limited_height * self.current_ratio
        else:
            limited_width = max_width
            limited_height = limited_width / self.current_ratio
        
        if width > limited_width or height > limited_height:
            width = limited_width
            height = limited_height
            # 确保调整后的尺寸不会超出边界
            x1 = max(img_left, min(x1, img_right - width))
            y1 = max(img_top, min(y1, img_bottom - height))
            x2 = x1 + width
            y2 = y1 + height
        
        return x1, y1, x2, y2
    
    def is_point_in_rect(self, px, py, rect_coords):
        """判断点是否在矩形内"""
        x1, y1, x2, y2 = rect_coords
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)
        
        return left <= px <= right and top <= py <= bottom
    
    def handle_drag(self, event):
        """控制点拖拽事件"""
        if not self.dragging_handle or not self.drag_start_coords:
            return

        canvas = self.gui.get_widget('canvas')

        dx = event.x - self.drag_start_pos[0]
        dy = event.y - self.drag_start_pos[1]

        x1, y1, x2, y2 = self.drag_start_coords

        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        if self.dragging_handle == 'nw':
            x1 = x1 + dx
            y1 = y1 + dy
        elif self.dragging_handle == 'n':
            y1 = y1 + dy
        elif self.dragging_handle == 'ne':
            x2 = x2 + dx
            y1 = y1 + dy
        elif self.dragging_handle == 'e':
            x2 = x2 + dx
        elif self.dragging_handle == 'se':
            x2 = x2 + dx
            y2 = y2 + dy
        elif self.dragging_handle == 's':
            y2 = y2 + dy
        elif self.dragging_handle == 'sw':
            x1 = x1 + dx
            y2 = y2 + dy
        elif self.dragging_handle == 'w':
            x1 = x1 + dx

        if self.current_ratio is not None:
            x1, y1, x2, y2 = self.adjust_coords_with_ratio(x1, y1, x2, y2, self.dragging_handle)

        x1, y1, x2, y2 = self.clamp_to_image_bounds(x1, y1, x2, y2)

        min_size = 10
        if abs(x2 - x1) < min_size or abs(y2 - y1) < min_size:
            return

        if self.current_rect:
            canvas.delete(self.current_rect)
        self.clear_handles()

        self.current_rect = canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red",
            width=2,
            dash=(5, 5),
            tags="selection"
        )

        self.selection_coords = (x1, y1, x2, y2)
        self.draw_handles(x1, y1, x2, y2)
        self.update_size_label()

        # 如果处于预览模式，更新预览
        if self.is_preview_mode:
            self.update_preview()
    
    def adjust_coords_with_ratio(self, x1, y1, x2, y2, handle):
        """根据固定比例调整坐标"""
        if self.current_ratio is None or self.current_ratio == 0:
            return x1, y1, x2, y2
        
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        width = x2 - x1
        height = y2 - y1
        
        if height <= 0 or width <= 0:
            return x1, y1, x2, y2
        
        if handle in ['nw', 'ne', 'sw', 'se']:
            current_ratio = width / height
            
            if width / height > self.current_ratio:
                new_height = width / self.current_ratio
                if handle in ['nw', 'sw']:
                    y2 = y1 + new_height
                else:
                    y1 = y2 - new_height
            else:
                new_width = height * self.current_ratio
                if handle in ['nw', 'ne']:
                    x2 = x1 + new_width
                else:
                    x1 = x2 - new_width
        elif handle in ['n', 's']:
            new_width = height * self.current_ratio
            # 根据新的高度和固定比例计算新的宽度
            # 保持中心点不变来调整x坐标
            center_x = (x1 + x2) / 2
            half_width = new_width / 2
            x1 = center_x - half_width
            x2 = center_x + half_width
        elif handle in ['e', 'w']:
            new_height = width / self.current_ratio
            # 根据新的宽度和固定比例计算新的高度
            # 保持中心点不变来调整y坐标
            center_y = (y1 + y2) / 2
            half_height = new_height / 2
            y1 = center_y - half_height
            y2 = center_y + half_height
        
        return x1, y1, x2, y2
    
    def clear_selection(self):
        """清除选择框"""
        canvas = self.gui.get_widget('canvas')
        if self.current_rect:
            canvas.delete(self.current_rect)
            self.current_rect = None
        self.clear_handles()
        self.selection_coords = None

        # 禁用保存按钮，因为没有选择区域
        save_btn = self.gui.get_widget('save_btn')
        if save_btn:
            save_btn.config(state=tk.DISABLED)
    
    def draw_handles(self, x1, y1, x2, y2):
        """绘制裁剪框的控制点"""
        canvas = self.gui.get_widget('canvas')
        
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        
        handle_positions = {
            'nw': (x1, y1),
            'n': (cx, y1),
            'ne': (x2, y1),
            'e': (x2, cy),
            'se': (x2, y2),
            's': (cx, y2),
            'sw': (x1, y2),
            'w': (x1, cy)
        }
        
        for handle_name, (hx, hy) in handle_positions.items():
            half_size = self.handle_size / 2
            handle = canvas.create_rectangle(
                hx - half_size, hy - half_size,
                hx + half_size, hy + half_size,
                fill="white",
                outline="red",
                width=2,
                tags=("handle", handle_name)
            )
            self.handles[handle_name] = handle
    
    def clear_handles(self):
        """清除所有控制点"""
        canvas = self.gui.get_widget('canvas')
        for handle in self.handles.values():
            canvas.delete(handle)
        self.handles.clear()
    
    def get_handle_at_position(self, x, y):
        """检查指定位置是否有控制点"""
        canvas = self.gui.get_widget('canvas')
        items = canvas.find_overlapping(
            x - self.handle_size, y - self.handle_size,
            x + self.handle_size, y + self.handle_size
        )

        # 按照图层顺序倒序遍历，优先检测最上层的元素
        for item in reversed(items):
            tags = canvas.gettags(item)
            # 在预览模式下，忽略预览图层
            if self.is_preview_mode:
                if any(tag in ["preview_mask", "preview_area", "preview_image", "preview_text"] for tag in tags):
                    continue
            if "handle" in tags:
                for tag in tags:
                    if tag in self.handles:
                        return tag
        return None
    
    def confirm_crop(self):
        """确认裁剪"""
        if not self.original_image or not self.selection_coords:
            messagebox.showwarning("警告", "请先在图像上选择裁剪区域")
            return
        
        try:
            x1, y1, x2, y2 = self.selection_coords
            
            img_x1 = (x1 - self.image_offset_x) / self.scale_factor
            img_y1 = (y1 - self.image_offset_y) / self.scale_factor
            img_x2 = (x2 - self.image_offset_x) / self.scale_factor
            img_y2 = (y2 - self.image_offset_y) / self.scale_factor
            
            img_x1, img_x2 = min(img_x1, img_x2), max(img_x1, img_x2)
            img_y1, img_y2 = min(img_y1, img_y2), max(img_y1, img_y2)
            
            orig_width, orig_height = self.original_image.size
            img_x1 = max(0, min(img_x1, orig_width))
            img_y1 = max(0, min(img_y1, orig_height))
            img_x2 = max(0, min(img_x2, orig_width))
            img_y2 = max(0, min(img_y2, orig_height))
            
            # 保存裁剪结果
            self.result = {
                'start': (int(img_x1), int(img_y1)),
                'end': (int(img_x2), int(img_y2)),
                'is_base_image': False
            }
            
            # 关闭对话框
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"裁剪失败：{str(e)}")
    
    def save_cropped_image(self):
        """保存裁剪后的图像"""
        if not self.original_image or not self.selection_coords:
            messagebox.showwarning("警告", "请先执行裁剪操作")
            return
        
        try:
            x1, y1, x2, y2 = self.selection_coords
            
            img_x1 = (x1 - self.image_offset_x) / self.scale_factor
            img_y1 = (y1 - self.image_offset_y) / self.scale_factor
            img_x2 = (x2 - self.image_offset_x) / self.scale_factor
            img_y2 = (y2 - self.image_offset_y) / self.scale_factor
            
            img_x1, img_x2 = min(img_x1, img_x2), max(img_x1, img_x2)
            img_y1, img_y2 = min(img_y1, img_y2), max(img_y1, img_y2)
            
            cropped_image = self.original_image.crop((img_x1, img_y1, img_x2, img_y2))
            
            file_path = filedialog.asksaveasfilename(
                title="保存裁剪图像",
                defaultextension=".png",
                filetypes=[
                    ("PNG 图片", "*.png"),
                    ("JPEG 图片", "*.jpg"),
                    ("BMP 图片", "*.bmp"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg']:
                if cropped_image.mode == 'RGBA':
                    cropped_rgb = Image.new('RGB', cropped_image.size, (255, 255, 255))
                    cropped_rgb.paste(cropped_image, mask=cropped_image.split()[3])
                    cropped_rgb.save(file_path, 'JPEG', quality=95)
                else:
                    cropped_image.save(file_path, 'JPEG', quality=95)
            else:
                cropped_image.save(file_path)
            
            messagebox.showinfo("成功", f"图像已保存到：\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")


def show_crop_dialog(root, image_path, image_paths, current_index):
    """
    显示裁剪对话框
    
    Args:
        root: 父窗口
        image_path: 当前图片路径
        image_paths: 所有图片路径列表
        current_index: 当前图片索引
    
    Returns:
        裁剪结果字典，包含裁剪坐标信息；如果用户取消则返��None
    """
    dialog = CropDialog(root, image_path, image_paths, current_index)
    return dialog.result