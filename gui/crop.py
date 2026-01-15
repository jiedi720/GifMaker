# -*- coding: utf-8 -*-
"""
裁剪动画对话框模块
实现类似于Windows对话框的裁剪界面
"""

import tkinter as tk
from tkinter import ttk


class CropDialog:
    """裁剪对话框类"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        # 创建对话框窗口 - 匹配RC规格: 310x222
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Crop Animation")
        self.dialog.geometry("310x222")
        self.dialog.resizable(False, False)
        
        # 居中显示
        self.center_window()
        
        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def center_window(self):
        """将窗口居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧图像预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="5")
        preview_frame.grid(row=0, column=0, rowspan=6, padx=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建一个占位符画布作为预览区域
        self.preview_canvas = tk.Canvas(preview_frame, width=150, height=130, bg="lightgray", relief=tk.SUNKEN, bd=1)
        self.preview_canvas.pack()
        
        # 添加一些示例图形来模拟图像预览
        self.preview_canvas.create_rectangle(20, 20, 130, 110, outline="black", width=1)
        self.preview_canvas.create_line(20, 20, 130, 110, dash=(2, 2), fill="red")
        self.preview_canvas.create_line(130, 20, 20, 110, dash=(2, 2), fill="red")
        
        # 右侧控制区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # X坐标控制
        ttk.Label(control_frame, text="X:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_var = tk.StringVar(value="0")
        x_entry = ttk.Entry(control_frame, textvariable=self.x_var, width=8)
        x_entry.grid(row=0, column=1, padx=(5, 0), pady=2)
        ttk.Button(control_frame, text="▲", width=2, command=lambda: self.adjust_value(self.x_var, 1)).grid(row=0, column=2, padx=(2, 0), pady=2)
        ttk.Button(control_frame, text="▼", width=2, command=lambda: self.adjust_value(self.x_var, -1)).grid(row=0, column=3, padx=(0, 5), pady=2)
        
        # Y坐标控制
        ttk.Label(control_frame, text="Y:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.y_var = tk.StringVar(value="0")
        y_entry = ttk.Entry(control_frame, textvariable=self.y_var, width=8)
        y_entry.grid(row=1, column=1, padx=(5, 0), pady=2)
        ttk.Button(control_frame, text="▲", width=2, command=lambda: self.adjust_value(self.y_var, 1)).grid(row=1, column=2, padx=(2, 0), pady=2)
        ttk.Button(control_frame, text="▼", width=2, command=lambda: self.adjust_value(self.y_var, -1)).grid(row=1, column=3, padx=(0, 5), pady=2)
        
        # 宽度控制
        ttk.Label(control_frame, text="Width:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.width_var = tk.StringVar(value="100")
        width_entry = ttk.Entry(control_frame, textvariable=self.width_var, width=8)
        width_entry.grid(row=2, column=1, padx=(5, 0), pady=2)
        ttk.Button(control_frame, text="▲", width=2, command=lambda: self.adjust_value(self.width_var, 1)).grid(row=2, column=2, padx=(2, 0), pady=2)
        ttk.Button(control_frame, text="▼", width=2, command=lambda: self.adjust_value(self.width_var, -1)).grid(row=2, column=3, padx=(0, 5), pady=2)
        
        # 高度控制
        ttk.Label(control_frame, text="Height:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.height_var = tk.StringVar(value="100")
        height_entry = ttk.Entry(control_frame, textvariable=self.height_var, width=8)
        height_entry.grid(row=3, column=1, padx=(5, 0), pady=2)
        ttk.Button(control_frame, text="▲", width=2, command=lambda: self.adjust_value(self.height_var, 1)).grid(row=3, column=2, padx=(2, 0), pady=2)
        ttk.Button(control_frame, text="▼", width=2, command=lambda: self.adjust_value(self.height_var, -1)).grid(row=3, column=3, padx=(0, 5), pady=2)
        
        # 选项复选框
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.show_prev_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Show Previous", variable=self.show_prev_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.show_next_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Show Next", variable=self.show_next_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.show_first_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Show First", variable=self.show_first_var).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.show_cropped_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Show As Cropped", variable=self.show_cropped_var).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky=(tk.E))
        
        self.auto_btn = ttk.Button(button_frame, text="Auto", width=8, command=self.auto_crop)
        self.auto_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reset_btn = ttk.Button(button_frame, text="Reset", width=8, command=self.reset_values)
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.ok_btn = ttk.Button(button_frame, text="OK", width=8, command=self.ok_clicked)
        self.ok_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", width=8, command=self.cancel_clicked)
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 绑定回车和ESC键
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # 设置焦点到第一个输入框
        x_entry.focus()
        
    def adjust_value(self, var, delta):
        """调整数值"""
        try:
            current_val = int(var.get())
            new_val = max(0, current_val + delta)  # 确保值不小于0
            var.set(str(new_val))
        except ValueError:
            var.set("0")
            
    def auto_crop(self):
        """自动裁剪功能"""
        # 这里可以实现自动检测最佳裁剪区域的逻辑
        print("Auto crop clicked")
        
    def reset_values(self):
        """重置值"""
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set("100")
        self.height_var.set("100")
        self.show_prev_var.set(False)
        self.show_next_var.set(False)
        self.show_first_var.set(False)
        self.show_cropped_var.set(False)
        
    def ok_clicked(self):
        """确定按钮点击"""
        try:
            # 验证输入值
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # 确保值有效
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive")
                
            self.result = {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'show_prev': self.show_prev_var.get(),
                'show_next': self.show_next_var.get(),
                'show_first': self.show_first_var.get(),
                'show_cropped': self.show_cropped_var.get()
            }
            self.dialog.destroy()
        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Invalid Input", f"Please enter valid numbers: {e}")
    
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = None
        self.dialog.destroy()
        
    def show(self):
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result


def show_crop_dialog(parent):
    """显示裁剪对话框的便捷函数"""
    dialog = CropDialog(parent)
    return dialog.show()


if __name__ == "__main__":
    # 测试对话框
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("400x300")
    
    def open_dialog():
        result = show_crop_dialog(root)
        if result:
            print("Crop settings:", result)
        else:
            print("Dialog cancelled")
    
    ttk.Button(root, text="Open Crop Dialog", command=open_dialog).pack(pady=50)
    
    root.mainloop()