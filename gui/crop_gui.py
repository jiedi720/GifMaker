"""
GUI界面构建器模块
负责创建和管理固定比例裁剪工具的所有界面组件
采用深色主题、Grid布局、滚动条等现代化设计
"""

import tkinter as tk
from tkinter import ttk


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
        
        # 1. 文件操作
        self.create_file_operations()
        
        # 2. 坐标设置
        self.create_coordinate_settings()
        
        # 3. 比例设置
        self.create_ratio_settings()
        
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
            text="⬜ 适应窗口", 
            command=self.callbacks['fit_to_window']
        )
        self.widgets['fit_btn'].pack(side="left", padx=5, fill="x", expand=True)
        
        # 原始大小按钮
        self.widgets['original_btn'] = ttk.Button(
            zoom_row, 
            text="🔄 原始大小", 
            command=self.callbacks['original_size']
        )
        self.widgets['original_btn'].pack(side="left", padx=5, fill="x", expand=True)
        
        # 操作按钮行
        btn_row = ttk.Frame(self.widgets['modules_container'])
        btn_row.pack(fill="x", pady=(0, 10))
        
        # 确认裁剪按钮
        self.widgets['crop_btn'] = ttk.Button(
            btn_row, 
            text="✅ 确认裁剪", 
            command=self.callbacks['confirm_crop']
        )
        self.widgets['crop_btn'].pack(side="left", padx=5, fill="x", expand=True)
        
        # 保存按钮
        self.widgets['save_btn'] = ttk.Button(
            btn_row, 
            text="💾 保存结果", 
            command=self.callbacks['save_cropped_image']
        )
        self.widgets['save_btn'].pack(side="left", padx=5, fill="x", expand=True)
    
    
    
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