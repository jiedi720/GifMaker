"""
固定比例裁剪工具
支持多种预设比例（自由、1:1、4:3、16:9、2:3）的图像裁剪

依赖库：
    pip install Pillow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from gui.crop_gui import GUIBuilder


class PhotoCropper:
    """固定比例裁剪工具主类"""
    
    def __init__(self, root):
        """初始化主窗口和组件"""
        self.root = root
        self.root.title("固定比例裁剪工具")
        self.root.geometry("1280x720")
        self.root.minsize(800, 600)
        
        # 窗口居中
        self.center_window()
        
        # 图像相关变量
        self.original_image = None      # 原始图像对象
        self.display_image = None       # 显示的图像对象
        self.photo_image = None         # Tkinter 图像对象
        self.scale_factor = 1.0         # 缩放系数（显示尺寸/原始尺寸）
        self.image_offset_x = 0         # 图像在画布上的X偏移
        self.image_offset_y = 0         # 图像在画布上的Y偏移
        
        # 裁剪框相关变量
        self.start_x = 0                # 起始X坐标
        self.start_y = 0                # 起始Y坐标
        self.current_rect = None        # 当前绘制的矩形对象
        self.selection_coords = None    # 选择框坐标 (x1, y1, x2, y2)
        self.is_dragging = False        # 是否正在拖动裁剪框
        self.drag_offset_x = 0          # 拖动时的X偏移量
        self.drag_offset_y = 0          # 拖动时的Y偏移量
        self.is_moving_rect = False     # 是否正在移动现有裁剪框
        
        # 控制点相关变量
        self.handles = {}               # 控制点字典
        self.dragging_handle = None     # 当前拖拽的控制点
        self.drag_start_pos = None      # 拖拽起始位置
        self.drag_start_coords = None   # 拖拽起始坐标
        self.handle_size = 8            # 控制点大小
        
        # 设置固定比例字典（宽:高）
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
        self.current_ratio = None       # 当前选择的比例
        self.locked_ratio = None        # 锁定的比例值
        self.original_ratio = None      # 原始图片比例
        
        # 创建GUI界面
        self.setup_gui()
        
        # 禁用裁剪和保存按钮（直到加载图片）
        self.gui.get_widget('crop_btn').config(state=tk.DISABLED)
        self.gui.get_widget('save_btn').config(state=tk.DISABLED)
    
    def setup_gui(self):
        """设置GUI界面"""
        # 定义回调函数
        callbacks = {
            'open_image': self.open_image,
            'on_ratio_change': self.on_ratio_change_wrapper,
            'confirm_crop': self.confirm_crop,
            'save_cropped_image': self.save_cropped_image,
            'on_mouse_down': self.on_mouse_down,
            'on_mouse_drag': self.on_mouse_drag,
            'on_mouse_up': self.on_mouse_up,
            'on_mouse_move': self.on_mouse_move,
            'fit_to_window': self.fit_to_window,
            'original_size': self.original_size
        }
        
        # 创建GUI构建器
        self.gui = GUIBuilder(self.root, callbacks)
    
    def center_window(self):
        """将窗口居中显示"""
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 使用设置的默认尺寸
        width = 1280
        height = 720
        
        # 计算居中位置
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # 在窗口显示前就设置好位置
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def on_ratio_change_wrapper(self, value):
        """比例选择改变的包装函数"""
        if value == "lock":
            # 锁定当前裁剪框的比例
            if self.selection_coords:
                x1, y1, x2, y2 = self.selection_coords
                width = abs(x2 - x1)
                height = abs(y2 - y1)
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
            # 使用原始图片的比例
            if self.original_image:
                img_width, img_height = self.original_image.size
                self.original_ratio = img_width / img_height
                self.current_ratio = self.original_ratio
            else:
                self.original_ratio = None
                self.current_ratio = None
        else:
            # 使用预设比例
            self.current_ratio = self.aspect_ratios.get(value)
        
        # 更新比例显示
        self.update_ratio_display()
        
        # 如果有选择框，清除它
        if self.current_rect:
            self.clear_selection()
    
    def fit_to_window(self):
        """适应窗口 - 缩放图片以适应当前窗口大小"""
        if not self.original_image:
            return
        
        # 重置缩放比例为自动计算
        self.scale_factor = None
        self.calculate_scale_and_display()
    
    def original_size(self):
        """原始大小 - 以1:1比例显示图片"""
        if not self.original_image:
            return
        
        canvas = self.gui.get_widget('canvas')
        
        # 获取画布尺寸
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600
        
        # 获取原始图像尺寸
        img_width, img_height = self.original_image.size
        
        # 设置缩放比例为1.0（原始大小）
        self.scale_factor = 1.0
        
        # 计算显示尺寸（原始大小）
        display_width = img_width
        display_height = img_height
        
        # 不需要缩放，直接使用原始图像
        self.display_image = self.original_image
        
        # 转换为 Tkinter 图像对象
        self.photo_image = ImageTk.PhotoImage(self.display_image)
        
        # 计算偏移量（从0开始，使用滚动条查看）
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        # 设置滚动区域为原始图像大小（加上边框）
        border_padding = 1
        canvas.configure(scrollregion=(0, 0, display_width + border_padding * 2, display_height + border_padding * 2))
        
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
        
        try:
            # 加载原始图像
            self.original_image = Image.open(file_path)
            
            # 计算缩放比例以适应画布
            self.calculate_scale_and_display()
            
            # 启用裁剪和保存按钮
            self.gui.get_widget('crop_btn').config(state=tk.NORMAL)
            self.gui.get_widget('save_btn').config(state=tk.DISABLED)
            
            # 清除之前的选择框
            self.clear_selection()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片：{str(e)}")
    
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
        
        # 设置滚动区域（使用画布尺寸作为滚动区域）
        canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # 在画布上显示图像（居中显示）
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
            else:
                ratio_text = f"1:{1/current_ratio:.2f}"
        else:
            ratio_text = "N/A"
        
        # 更新比例标签
        ratio_label = self.gui.get_widget('ratio_label')
        if ratio_label:
            ratio_label.config(text=ratio_text)
    
    def on_mouse_down(self, event):
        """鼠标按下事件：记录起始点或选中裁剪框"""
        if not self.original_image:
            return
        
        # 检查是否点击在控制点上
        handle = self.get_handle_at_position(event.x, event.y)
        if handle:
            # 进入控制点拖拽模式
            self.dragging_handle = handle
            self.drag_start_pos = (event.x, event.y)
            self.drag_start_coords = self.selection_coords
            return
        
        # 检查是否点击在现有裁剪框内
        if self.selection_coords and self.is_point_in_rect(event.x, event.y, self.selection_coords):
            # 进入移动模式
            self.is_moving_rect = True
            self.drag_offset_x = event.x
            self.drag_offset_y = event.y
            return
        
        # 新建模式：记录起始坐标
        self.start_x = event.x
        self.start_y = event.y
        self.is_moving_rect = False
        
        # 清除之前的选择框
        self.clear_selection()
    
    def on_mouse_drag(self, event):
        """鼠标拖动事件：实时绘制选择框或移动现有裁剪框"""
        if not self.original_image:
            return
        
        if self.dragging_handle:
            # 拖拽控制点
            self.handle_drag(event)
        elif self.is_moving_rect and self.selection_coords:
            # 移动现有裁剪框
            self.move_selection_box(event.x, event.y)
        else:
            # 新建裁剪框
            self.create_selection_box(event.x, event.y)
    
    def adjust_to_aspect_ratio(self, width, height):
        """根据固定比例调整宽度和高度"""
        if self.current_ratio is None or self.current_ratio == 0:
            return width, height
        
        # 处理宽度或高度为0的情况
        if abs(width) < 1:
            width = 1
        if abs(height) < 1:
            height = 1
        
        # 根据比例计算，始终调整以保持比例
        if abs(width) >= abs(height):
            # 以宽度为基准
            adjusted_height = width / self.current_ratio
            return width, adjusted_height
        else:
            # 以高度为基准
            adjusted_width = height * self.current_ratio
            return adjusted_width, height
    
    def on_mouse_up(self, event):
        """鼠标释放事件：完成选择或移动"""
        if not self.original_image or not self.selection_coords:
            return
        
        # 重置移动状态
        self.is_moving_rect = False
        self.dragging_handle = None
        self.drag_start_pos = None
        self.drag_start_coords = None
        
        # 启用裁剪按钮
        self.gui.get_widget('crop_btn').config(state=tk.NORMAL)
    
    def create_selection_box(self, current_x, current_y):
        """创建新的裁剪框"""
        canvas = self.gui.get_widget('canvas')
        
        # 计算矩形框的宽度和高度
        width = current_x - self.start_x
        height = current_y - self.start_y
        
        # 根据比例约束调整矩形框
        if self.current_ratio is not None:
            width, height = self.adjust_to_aspect_ratio(width, height)
        
        # 计算矩形框的四个顶点坐标
        x1 = self.start_x
        y1 = self.start_y
        x2 = self.start_x + width
        y2 = self.start_y + height
        
        # 删除旧的矩形框和控制点
        if self.current_rect:
            canvas.delete(self.current_rect)
        self.clear_handles()
        
        # 绘制新的矩形框（虚线）
        self.current_rect = canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red",
            width=2,
            dash=(5, 5),
            tags="selection"
        )
        
        # 保存当前选择框坐标（相对于画布）
        self.selection_coords = (x1, y1, x2, y2)
        
        # 绘制控制点
        self.draw_handles(x1, y1, x2, y2)
        
        # 更新尺寸标签
        self.update_size_label()
    
    def move_selection_box(self, current_x, current_y):
        """移动现有的裁剪框，保持固定比例"""
        canvas = self.gui.get_widget('canvas')
        
        if not self.selection_coords:
            return
        
        # 计算移动距离
        dx = current_x - self.drag_offset_x
        dy = current_y - self.drag_offset_y
        
        # 获取当前坐标
        x1, y1, x2, y2 = self.selection_coords
        
        # 确保坐标顺序正确
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        # 计算新坐标
        new_x1 = x1 + dx
        new_y1 = y1 + dy
        new_x2 = x2 + dx
        new_y2 = y2 + dy
        
        # 边界检测：确保裁剪框不超出图像显示范围
        new_x1, new_y1, new_x2, new_y2 = self.clamp_to_image_bounds(
            new_x1, new_y1, new_x2, new_y2
        )
        
        # 计算实际移动的距离（可能因为边界限制而改变）
        actual_dx = (new_x1 - x1)
        actual_dy = (new_y1 - y1)
        
        # 删除旧的矩形框和控制点
        if self.current_rect:
            canvas.delete(self.current_rect)
        self.clear_handles()
        
        # 绘制新的矩形框
        self.current_rect = canvas.create_rectangle(
            new_x1, new_y1, new_x2, new_y2,
            outline="red",
            width=2,
            dash=(5, 5),
            tags="selection"
        )
        
        # 更新选择框坐标
        self.selection_coords = (new_x1, new_y1, new_x2, new_y2)
        
        # 重新绘制控制点
        self.draw_handles(new_x1, new_y1, new_x2, new_y2)
        
        # 更新拖动偏移量（使用实际移动距离，确保连续拖动）
        self.drag_offset_x = self.drag_offset_x + actual_dx
        self.drag_offset_y = self.drag_offset_y + actual_dy
        
        # 更新尺寸标签
        self.update_size_label()
    
    def clamp_to_image_bounds(self, x1, y1, x2, y2):
        """限制裁剪框在图像显示范围内，保持固定比例"""
        if not self.display_image:
            return x1, y1, x2, y2
        
        # 获取图像显示区域的边界
        img_left = self.image_offset_x
        img_top = self.image_offset_y
        img_right = self.image_offset_x + self.display_image.width
        img_bottom = self.image_offset_y + self.display_image.height
        
        # 确保坐标顺序正确（x1 < x2, y1 < y2）
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        # 计算裁剪框的宽度和高度
        rect_width = x2 - x1
        rect_height = y2 - y1
        
        # 如果是固定比例模式，使用滑动边界检测
        if self.current_ratio is not None:
            return self.clamp_with_aspect_ratio(x1, y1, rect_width, rect_height, 
                                               img_left, img_top, img_right, img_bottom)
        else:
            # 自由比例模式：简单限制在边界内
            new_x1 = max(img_left, min(x1, img_right - rect_width))
            new_y1 = max(img_top, min(y1, img_bottom - rect_height))
            new_x2 = new_x1 + rect_width
            new_y2 = new_y1 + rect_height
            return new_x1, new_y1, new_x2, new_y2
    
    def clamp_with_aspect_ratio(self, x1, y1, width, height, img_left, img_top, img_right, img_bottom):
        """固定比例下的滑动边界检测，确保比例不被压缩"""
        # 初始化x2和y2
        x2 = x1 + width
        y2 = y1 + height
        
        # 检查左边界
        if x1 < img_left:
            x1 = img_left
            x2 = x1 + width
        
        # 检查右边界
        if x2 > img_right:
            x2 = img_right
            x1 = x2 - width
        
        # 检查上边界
        if y1 < img_top:
            y1 = img_top
            y2 = y1 + height
        
        # 检查下边界
        if y2 > img_bottom:
            y2 = img_bottom
            y1 = y2 - height
        
        # 如果裁剪框仍然超出边界，说明图像太小无法容纳该比例的裁剪框
        # 此时需要限制裁剪框的最大尺寸，但保持比例
        max_width = img_right - img_left
        max_height = img_bottom - img_top
        
        # 根据比例计算最大可能的尺寸
        if max_width / max_height > self.current_ratio:
            # 图像比裁剪框更宽，以高度为基准
            limited_height = max_height
            limited_width = limited_height * self.current_ratio
        else:
            # 图像比裁剪框更高，以宽度为基准
            limited_width = max_width
            limited_height = limited_width / self.current_ratio
        
        # 如果当前裁剪框超过最大尺寸，则缩小到最大尺寸
        if width > limited_width or height > limited_height:
            width = limited_width
            height = limited_height
            # 重新居中或保持左上角位置
            if x1 + width > img_right:
                x1 = img_right - width
            if y1 + height > img_bottom:
                y1 = img_bottom - height
            x2 = x1 + width
            y2 = y1 + height
        
        return x1, y1, x2, y2
    
    def is_point_in_rect(self, px, py, rect_coords):
        """判断点是否在矩形内"""
        x1, y1, x2, y2 = rect_coords
        # 处理反向坐标的情况
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)
        
        return left <= px <= right and top <= py <= bottom
    
    def on_mouse_move(self, event):
        """鼠标移动事件：更新光标样式"""
        if not self.original_image:
            return
        
        canvas = self.gui.get_widget('canvas')
        
        # 检查鼠标是否在控制点上
        handle = self.get_handle_at_position(event.x, event.y)
        if handle:
            # 根据控制点位置设置光标（使用双向箭头）
            cursor_map = {
                'nw': 'size_nw_se',      # 左上-右下对角线
                'n': 'sb_v_double_arrow',     # 垂直双向
                'ne': 'size_ne_sw',      # 右上-左下对角线
                'e': 'sb_h_double_arrow',     # 水平双向
                'se': 'size_nw_se',      # 右下-左上对角线
                's': 'sb_v_double_arrow',     # 垂直双向
                'sw': 'size_ne_sw',      # 左下-右上对角线
                'w': 'sb_h_double_arrow'      # 水平双向
            }
            canvas.config(cursor=cursor_map.get(handle, 'cross'))
        # 检查鼠标是否在裁剪框内
        elif self.selection_coords and self.is_point_in_rect(event.x, event.y, self.selection_coords):
            canvas.config(cursor="fleur")  # 移动光标
        else:
            canvas.config(cursor="cross")  # 十字光标
    
    def handle_drag(self, event):
        """控制点拖拽事件"""
        if not self.dragging_handle or not self.drag_start_coords:
            return
        
        canvas = self.gui.get_widget('canvas')
        
        # 计算鼠标移动距离
        dx = event.x - self.drag_start_pos[0]
        dy = event.y - self.drag_start_pos[1]
        
        # 获取起始坐标
        x1, y1, x2, y2 = self.drag_start_coords
        
        # 确保坐标顺序正确
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        # 根据拖拽的控制点调整坐标
        if self.dragging_handle == 'nw':  # 左上角
            x1 = x1 + dx
            y1 = y1 + dy
        elif self.dragging_handle == 'n':  # 上边中点
            y1 = y1 + dy
        elif self.dragging_handle == 'ne':  # 右上角
            x2 = x2 + dx
            y1 = y1 + dy
        elif self.dragging_handle == 'e':  # 右边中点
            x2 = x2 + dx
        elif self.dragging_handle == 'se':  # 右下角
            x2 = x2 + dx
            y2 = y2 + dy
        elif self.dragging_handle == 's':  # 下边中点
            y2 = y2 + dy
        elif self.dragging_handle == 'sw':  # 左下角
            x1 = x1 + dx
            y2 = y2 + dy
        elif self.dragging_handle == 'w':  # 左边中点
            x1 = x1 + dx
        
        # 如果启用了固定比例，应用比例约束
        if self.current_ratio is not None:
            x1, y1, x2, y2 = self.adjust_coords_with_ratio(x1, y1, x2, y2, self.dragging_handle)
        
        # 确保坐标在边界内
        x1, y1, x2, y2 = self.clamp_to_image_bounds(x1, y1, x2, y2)
        
        # 确保最小尺寸
        min_size = 10
        if abs(x2 - x1) < min_size or abs(y2 - y1) < min_size:
            return
        
        # 删除旧的矩形框和控制点
        if self.current_rect:
            canvas.delete(self.current_rect)
        self.clear_handles()
        
        # 绘制新的矩形框
        self.current_rect = canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red",
            width=2,
            dash=(5, 5),
            tags="selection"
        )
        
        # 更新选择框坐标
        self.selection_coords = (x1, y1, x2, y2)
        
        # 重新绘制控制点
        self.draw_handles(x1, y1, x2, y2)
        
        # 更新尺寸标签
        self.update_size_label()
    
    def adjust_coords_with_ratio(self, x1, y1, x2, y2, handle):
        """根据固定比例调整坐标"""
        if self.current_ratio is None or self.current_ratio == 0:
            return x1, y1, x2, y2
        
        # 确保坐标顺序正确
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        width = x2 - x1
        height = y2 - y1
        
        # 避免除零错误
        if height <= 0 or width <= 0:
            return x1, y1, x2, y2
        
        # 根据拖拽的控制点调整
        if handle in ['nw', 'ne', 'sw', 'se']:  # 角控制点
            # 计算当前宽高比
            current_ratio = width / height
            
            # 始终调整以保持比例
            if width / height > self.current_ratio:
                # 宽度过大，调整高度
                new_height = width / self.current_ratio
                if handle in ['nw', 'sw']:
                    y2 = y1 + new_height
                else:
                    y1 = y2 - new_height
            else:
                # 高度过大，调整宽度
                new_width = height * self.current_ratio
                if handle in ['nw', 'ne']:
                    x2 = x1 + new_width
                else:
                    x1 = x2 - new_width
        elif handle in ['n', 's']:  # 上下边控制点
            # 调整宽度以保持比例
            new_width = height * self.current_ratio
            if handle == 'n':
                x2 = x1 + new_width
            else:
                x2 = x1 + new_width
        elif handle in ['e', 'w']:  # 左右边控制点
            # 调整高度以保持比例
            new_height = width / self.current_ratio
            if handle == 'w':
                y2 = y1 + new_height
            else:
                y2 = y1 + new_height
        
        return x1, y1, x2, y2
    
    def clear_selection(self):
        """清除选择框"""
        canvas = self.gui.get_widget('canvas')
        if self.current_rect:
            canvas.delete(self.current_rect)
            self.current_rect = None
        self.clear_handles()
        self.selection_coords = None
    
    def draw_handles(self, x1, y1, x2, y2):
        """绘制裁剪框的控制点"""
        canvas = self.gui.get_widget('canvas')
        
        # 确保坐标顺序正确
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        # 计算中心点
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        
        # 定义8个控制点位置
        handle_positions = {
            'nw': (x1, y1),      # 左上角
            'n': (cx, y1),       # 上边中点
            'ne': (x2, y1),      # 右上角
            'e': (x2, cy),       # 右边中点
            'se': (x2, y2),      # 右下角
            's': (cx, y2),       # 下边中点
            'sw': (x1, y2),      # 左下角
            'w': (x1, cy)        # 左边中点
        }
        
        # 绘制控制点
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
        
        for item in items:
            tags = canvas.gettags(item)
            if "handle" in tags:
                for tag in tags:
                    if tag in self.handles:
                        return tag
        return None
    
    def confirm_crop(self):
        """确认裁剪并显示预览"""
        if not self.original_image or not self.selection_coords:
            messagebox.showwarning("警告", "请先在图像上选择裁剪区域")
            return
        
        try:
            # 转换画布坐标到原始图像坐标
            x1, y1, x2, y2 = self.selection_coords
            
            # 转换为相对于图像的坐标
            img_x1 = (x1 - self.image_offset_x) / self.scale_factor
            img_y1 = (y1 - self.image_offset_y) / self.scale_factor
            img_x2 = (x2 - self.image_offset_x) / self.scale_factor
            img_y2 = (y2 - self.image_offset_y) / self.scale_factor
            
            # 处理反向拖动的情况（确保 x1 < x2, y1 < y2）
            img_x1, img_x2 = min(img_x1, img_x2), max(img_x1, img_x2)
            img_y1, img_y2 = min(img_y1, img_y2), max(img_y1, img_y2)
            
            # 限制在图像范围内
            orig_width, orig_height = self.original_image.size
            img_x1 = max(0, min(img_x1, orig_width))
            img_y1 = max(0, min(img_y1, orig_height))
            img_x2 = max(0, min(img_x2, orig_width))
            img_y2 = max(0, min(img_y2, orig_height))
            
            # 执行裁剪
            cropped_image = self.original_image.crop((img_x1, img_y1, img_x2, img_y2))
            
            # 保存裁剪结果
            self.cropped_image = cropped_image
            
            # 显示预览窗口
            self.show_preview(cropped_image)
            
            # 启用保存按钮
            self.gui.get_widget('save_btn').config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("错误", f"裁剪失败：{str(e)}")
    
    def show_preview(self, image):
        """显示裁剪预览窗口"""
        if self.preview_window:
            self.preview_window.destroy()
        
        # 创建预览窗口
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("裁剪预览")
        self.preview_window.geometry("600x500")
        
        # 创建预览画布
        preview_canvas = tk.Canvas(self.preview_window, bg="#f0f0f0")
        preview_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 计算预览缩放比例
        canvas_width = 580
        canvas_height = 480
        img_width, img_height = image.size
        
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y)
        
        # 缩放预览图像
        preview_display = image.resize(
            (int(img_width * scale), int(img_height * scale)),
            Image.Resampling.LANCZOS
        )
        preview_photo = ImageTk.PhotoImage(preview_display)
        
        # 居中显示
        offset_x = (canvas_width - int(img_width * scale)) // 2
        offset_y = (canvas_height - int(img_height * scale)) // 2
        
        preview_canvas.create_image(
            offset_x, offset_y,
            image=preview_photo,
            anchor=tk.NW,
            tags="preview"
        )
        
        # 保存引用以防止被垃圾回收
        preview_canvas.preview_photo = preview_photo
        
        # 显示裁剪尺寸信息
        info_text = f"裁剪尺寸: {img_width} x {img_height} 像素"
        preview_canvas.create_text(
            canvas_width // 2, 20,
            text=info_text,
            fill="black",
            font=("Arial", 10)
        )
    
    def save_cropped_image(self):
        """保存裁剪后的图像"""
        if not hasattr(self, 'cropped_image'):
            messagebox.showwarning("警告", "请先执行裁剪操作")
            return
        
        # 获取原始文件名
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
        
        try:
            # 根据文件扩展名确定格式
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg']:
                # JPEG 不支持透明度，转换为 RGB
                if self.cropped_image.mode == 'RGBA':
                    cropped_rgb = Image.new('RGB', self.cropped_image.size, (255, 255, 255))
                    cropped_rgb.paste(self.cropped_image, mask=self.cropped_image.split()[3])
                    cropped_rgb.save(file_path, 'JPEG', quality=95)
                else:
                    self.cropped_image.save(file_path, 'JPEG', quality=95)
            else:
                # PNG, BMP 等格式
                self.cropped_image.save(file_path)
            
            messagebox.showinfo("成功", f"图像已保存到：\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = PhotoCropper(root)
    root.mainloop()


if __name__ == "__main__":
    main()