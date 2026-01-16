# -*- coding: utf-8 -*-
"""
预览功能模块
处理GIF预览和刷新预览功能
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image


def zoom_in_preview(main_window_instance):
    """
    放大预览，对所有图片生效
    将预览图片的缩放比例增加25%
    Args:
        main_window_instance: 主窗口实例
    """
    if main_window_instance.preview_scale < 5.0:
        main_window_instance.preview_scale *= 1.25
        main_window_instance.display_grid_preview()


def zoom_out_preview(main_window_instance):
    """
    缩小预览，对所有图片生效
    将预览图片的缩放比例减少20%
    Args:
        main_window_instance: 主窗口实例
    """
    if main_window_instance.preview_scale > 0.1:
        main_window_instance.preview_scale /= 1.25
        main_window_instance.display_grid_preview()


def reset_preview_zoom(main_window_instance):
    """
    重置预览缩放，让每张图片按原图大小显示
    将预览缩放比例设置为1.0，所有图片按原始尺寸显示
    Args:
        main_window_instance: 主窗口实例
    """
    if not main_window_instance.image_paths:
        return

    main_window_instance.preview_scale = 1.0
    main_window_instance.display_grid_preview()


def fit_preview_to_window(main_window_instance):
    """
    让预览图片适应窗口，对所有图片生效
    自动调整缩放比例，使所有图片完整显示在预览区域
    Args:
        main_window_instance: 主窗口实例
    """
    if not main_window_instance.image_paths:
        return

    main_window_instance.preview_scale = 1.0
    main_window_instance.display_grid_preview()


def apply_manual_zoom(main_window_instance, event):
    """
    应用手动输入的缩放值
    从输入框获取缩放百分比并应用到预览图
    Args:
        main_window_instance: 主窗口实例
        event: 键盘事件对象
    """
    try:
        zoom_value = float(main_window_instance.zoom_entry.get())
        if zoom_value <= 0:
            messagebox.showwarning("警告", "缩放值必须大于0")
            return

        # 将百分比转换为缩放比例
        main_window_instance.preview_scale = zoom_value / 100.0

        # 限制缩放范围在10%-500%之间
        if main_window_instance.preview_scale < 0.1:
            main_window_instance.preview_scale = 0.1
            main_window_instance.zoom_entry.delete(0, tk.END)
            main_window_instance.zoom_entry.insert(0, "10")
        elif main_window_instance.preview_scale > 5.0:
            main_window_instance.preview_scale = 5.0
            main_window_instance.zoom_entry.delete(0, tk.END)
            main_window_instance.zoom_entry.insert(0, "500")

        # 刷新预览和状态信息
        refresh_preview(main_window_instance)
        from function.ui_operations import update_status_info
        update_status_info(main_window_instance)
    except ValueError:
        messagebox.showerror("错误", "请输入有效的数字")
        # 恢复为当前缩放比例
        main_window_instance.zoom_entry.insert(0, str(int(main_window_instance.preview_scale * 100)))


def on_preview_canvas_configure(main_window_instance, event):
    """
    当预览Canvas大小改变时更新窗口大小
    此方法用于处理Canvas尺寸变化事件
    Args:
        main_window_instance: 主窗口实例
        event: Canvas配置事件对象
    """
    pass


def on_preview_mousewheel(main_window_instance, event):
    """
    处理预览区域的鼠标滚轮事件
    支持 Ctrl+滚轮缩放功能，普通滚轮用于滚动
    Args:
        main_window_instance: 主窗口实例
        event: 鼠标滚轮事件对象
    """
    # 检查是否按下了Ctrl键
    ctrl_pressed = event.state & 0x4
    if ctrl_pressed:
        # Ctrl+滚轮：缩放图片
        if event.delta > 0 or event.num == 4:
            zoom_in_preview(main_window_instance)
        elif event.delta < 0 or event.num == 5:
            zoom_out_preview(main_window_instance)
    else:
        # 普通滚轮：滚动Canvas
        scrollregion = main_window_instance.preview_canvas.cget("scrollregion")
        if scrollregion:
            parts = scrollregion.split()
            if len(parts) == 4:
                scroll_width = float(parts[2])
                scroll_height = float(parts[3])
                canvas_width = main_window_instance.preview_canvas.winfo_width()
                canvas_height = main_window_instance.preview_canvas.winfo_height()

                # 只有当图片尺寸大于Canvas可视区域时才允许滚动
                if scroll_width > canvas_width or scroll_height > canvas_height:
                    if event.num == 4 or event.delta > 0:
                        main_window_instance.preview_canvas.yview_scroll(-1, "units")
                    elif event.num == 5 or event.delta < 0:
                        main_window_instance.preview_canvas.yview_scroll(1, "units")


def refresh_preview(main_window_instance):
    """
    刷新预览
    重新显示网格预览，根据当前窗口大小调整布局
    Args:
        main_window_instance: 主窗口实例
    """
    if main_window_instance.image_paths:
        main_window_instance.display_grid_preview()


def preview_gif(main_window_instance):
    """
    预览GIF动画效果，弹出独立窗口
    创建一个独立的窗口来预览GIF动画效果
    Args:
        main_window_instance: 主窗口实例
    """
    if not main_window_instance.image_paths:
        messagebox.showwarning("提示", "请先选择至少一张图片")
        return

    # 检查是否需要调整尺寸
    resize = None
    if main_window_instance.resize_width.get() and main_window_instance.resize_height.get():
        try:
            width = int(main_window_instance.resize_width.get())
            height = int(main_window_instance.resize_height.get())
            if width > 0 and height > 0:
                resize = (width, height)
            else:
                messagebox.showerror("错误", "尺寸参数必须大于0")
                return
        except ValueError:
            messagebox.showerror("错误", "尺寸参数必须是数字")
            return

    try:
        # 加载并处理所有图片帧
        frames = []
        duration = main_window_instance.duration.get()

        for img_path in main_window_instance.image_paths:
            try:
                img = Image.open(img_path)

                # 如果设置了尺寸，则调整图片大小
                if resize:
                    img = img.resize(resize, Image.Resampling.LANCZOS)

                # 转换为调色板模式以优化GIF
                if img.mode != 'P':
                    img = img.convert('P', palette=Image.Palette.ADAPTIVE)

                frames.append(img)
            except Exception as e:
                print(f"警告: 无法加载图片 {img_path}: {e}")
                continue

        if not frames:
            raise ValueError("没有成功加载任何图片")

        # 创建预览窗口
        from gui.preview_gui import GifPreviewWindow
        preview_window = GifPreviewWindow(main_window_instance.root, frames, duration, main_window_instance.output_path.get())

    except Exception as e:
        messagebox.showerror("错误", f"预览GIF失败:\n{str(e)}")
