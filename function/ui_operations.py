# -*- coding: utf-8 -*-
"""
UI操作模块
处理UI相关的操作，如浏览输出目录、进入裁剪模式等
"""

from tkinter import filedialog, messagebox
import os
import tkinter as tk
from typing import Callable


def delayed_execution(widget: tk.Widget, callback: Callable, delay_ms: int = 100):
    """延迟执行回调函数，确保UI渲染完成后再执行

    Args:
        widget: Tkinter组件对象
        callback: 回调函数
        delay_ms: 延迟时间（毫秒）
    """
    widget.after(delay_ms, callback)


def ensure_widget_rendered(widget: tk.Widget, callback: Callable):
    """确保组件渲染完成后再执行回调

    Args:
        widget: Tkinter组件对象
        callback: 回调函数
    """
    widget.update_idletasks()
    widget.after(10, callback)


def get_actual_dimensions(canvas: tk.Canvas) -> tuple:
    """获取Canvas的实际物理尺寸

    Args:
        canvas: Tkinter Canvas对象

    Returns:
        tuple: (width, height)
    """
    canvas.update_idletasks()
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    if width < 10 or height < 10:
        width = 800
        height = 600

    return width, height


def fit_to_window_strategy(canvas: tk.Canvas, orig_width: int, orig_height: int, padding: int = 20):
    """适应窗口的缩放策略

    Args:
        canvas: Tkinter Canvas对象
        orig_width: 原始图片宽度
        orig_height: 原始图片高度
        padding: 填充大小

    Returns:
        float: 适应窗口的缩放比例
    """
    canvas_width, canvas_height = get_actual_dimensions(canvas)

    scale_width = (canvas_width - padding) / orig_width
    scale_height = (canvas_height - padding) / orig_height
    fit_scale = min(scale_width, scale_height)

    return fit_scale


def on_file_selected(main_window_instance, event):
    """
    处理文件选择变化事件
    当用户从下拉框中选择不同的图片时，更新预览显示

    Args:
        main_window_instance: GifMakerGUI实例
        event: 事件对象
    """
    try:
        current_selection = main_window_instance.file_combobox.current()
        if current_selection >= 0 and current_selection < len(main_window_instance.image_paths):
            # 设置选中的图片索引
            main_window_instance.selected_image_index = current_selection
            main_window_instance.selected_image_indices = {current_selection}
            main_window_instance.last_selected_index = current_selection

            # 只更新选中框，不重新绘制整个网格（避免闪烁）
            main_window_instance.draw_selection_boxes()
            
            # 滚动到选中的图片（已禁用，避免图片移动）
            # main_window_instance.scroll_to_image(current_selection)

            # 更新状态信息
            update_status_info(main_window_instance)
    except Exception as e:
        print(f"文件选择处理失败: {e}")


def browse_output(main_window_instance):
    """浏览输出文件"""
    current_path = main_window_instance.output_path.get()
    current_dir = os.path.dirname(current_path)
    current_filename = os.path.basename(current_path)

    if not current_dir or not os.path.exists(current_dir):
        current_dir = os.getcwd()

    # 生成默认文件名
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"animation_{timestamp}.gif"

    selected_file = filedialog.asksaveasfilename(
        title="选择输出文件",
        initialdir=current_dir,
        initialfile=default_filename,
        defaultextension=".gif",
        filetypes=[
            ("GIF files", "*.gif"),
            ("All files", "*.*")
        ]
    )

    if selected_file:
        main_window_instance.output_path.set(selected_file)


def enter_crop_mode(main_window_instance):
    """
    进入裁剪模式
    打开裁剪对话框，允许用户对当前图片进行裁剪操作
    """
    if not main_window_instance.image_paths:
        messagebox.showwarning("提示", "请先选择图片")
        return

    try:
        from gui.crop_gui import show_crop_dialog

        if main_window_instance.selected_image_indices and len(main_window_instance.selected_image_indices) > 1:

            target_indices = sorted(main_window_instance.selected_image_indices)
            target_paths = [main_window_instance.image_paths[i] for i in target_indices]

            from function.image_utils import find_smallest_image_path
            current_image_path, current_index = find_smallest_image_path(target_paths, main_window_instance.image_paths)
        else:

            current_selection = main_window_instance.file_combobox.current()
            if current_selection >= 0 and current_selection < len(main_window_instance.image_paths):
                current_image_path = main_window_instance.image_paths[current_selection]
                # 选择单个文件时，只传递当前图片，禁用导航功能
                target_paths = [current_image_path]
                current_index = 0  # 只有一张图片，索引必须是 0
            else:
                current_image_path = main_window_instance.image_paths[0]
                # 选择单个文件时，只传递当前图片，禁用导航功能
                target_paths = [current_image_path]
                current_index = 0  # 只有一张图片，索引必须是 0

        result = show_crop_dialog(
            main_window_instance.root,
            image_path=current_image_path,
            image_paths=target_paths,
            current_index=current_index
        )

        if result:
            # 在应用裁剪之前先保存状态
            from function.history_manager import save_state
            save_state(main_window_instance)

            from function.image_utils import load_image
            from function.crop_backup import crop_image

            if result.get('is_base_image', False):
                # 如果是基础图片模式，使用返回的裁剪坐标
                crop_coords = result.get('crop_coords', {})

                # 保存裁剪坐标和裁剪后的图片
                for img_path, coords in crop_coords.items():
                    if img_path in main_window_instance.image_paths:
                        main_window_instance.pending_crop_coords[img_path] = coords
                        # 加载图片并应用裁剪
                        img = load_image(img_path)
                        if img:
                            x1, y1, x2, y2 = coords
                            cropped_img = crop_image(img, x1, y1, x2, y2)
                            main_window_instance.pending_crops[img_path] = cropped_img
            else:
                # 如果是单个裁剪结果，需要确定应用到哪些图片
                start_pos = result['start']
                end_pos = result['end']

                # 如果用户选择了多个图片，则将相同的裁剪区域应用到所有选中的图片
                if main_window_instance.selected_image_indices and len(main_window_instance.selected_image_indices) > 1:
                    # 获取所有选中的图片路径
                    target_indices = sorted(main_window_instance.selected_image_indices)
                    target_paths = [main_window_instance.image_paths[i] for i in target_indices]

                    # 将相同的裁剪区域应用到所有选中的图片
                    for img_path in target_paths:
                        main_window_instance.pending_crop_coords[img_path] = (
                            start_pos[0], start_pos[1], end_pos[0], end_pos[1]
                        )
                        # 加载图片并应用裁剪
                        img = load_image(img_path)
                        if img:
                            x1, y1, x2, y2 = start_pos[0], start_pos[1], end_pos[0], end_pos[1]
                            cropped_img = crop_image(img, x1, y1, x2, y2)
                            main_window_instance.pending_crops[img_path] = cropped_img
                else:
                    # 单个图片的情况，只应用到当前图片
                    current_img_path = current_image_path
                    main_window_instance.pending_crop_coords[current_img_path] = (
                        start_pos[0], start_pos[1], end_pos[0], end_pos[1]
                    )
                    # 加载图片并应用裁剪
                    img = load_image(current_img_path)
                    if img:
                        x1, y1, x2, y2 = start_pos[0], start_pos[1], end_pos[0], end_pos[1]
                        cropped_img = crop_image(img, x1, y1, x2, y2)
                        main_window_instance.pending_crops[current_img_path] = cropped_img

            # 更新图片列表
            main_window_instance.display_grid_preview()
            print("裁剪设置已保存")

    except Exception as e:
        messagebox.showerror("错误", f"进入裁剪模式失败:\n{str(e)}")


def update_status_info(main_window_instance):
    """
    更新状态栏信息，显示当前图片信息
    包括当前图片尺寸、文件大小、总时间估算和GIF大小估算
    """
    if main_window_instance.image_paths:
        current_selection = main_window_instance.file_combobox.current()
        if current_selection >= 0 and current_selection < len(main_window_instance.image_paths):
            img_path = main_window_instance.image_paths[current_selection]

            try:

                from function.image_utils import get_image_info
                img_info = get_image_info(img_path)

                current_img_info = f"当前图片: {img_info['width']}x{img_info['height']}px | {img_info['size_kb']:.2f}KB | {img_info['format']}"
                main_window_instance.current_img_size_label.config(text=current_img_info)

                # 计算总时间 - 从file_manager导入
                from function.file_manager import calculate_total_time
                num_images = len(main_window_instance.image_paths)
                duration_ms = main_window_instance.duration.get()
                total_time_s, total_time_ms = calculate_total_time(num_images, duration_ms)
                main_window_instance.total_time_label.config(text=f"总时间: {total_time_s:.1f}s ({num_images}张 x {duration_ms}ms)")

                # 估算GIF大小 - 从file_manager导入
                from function.file_manager import estimate_gif_size
                estimated_gif_size = estimate_gif_size(main_window_instance.image_paths)
                main_window_instance.gif_size_label.config(text=f"GIF大小: {estimated_gif_size:.2f}KB")

            except Exception as e:
                main_window_instance.current_img_size_label.config(text="当前图片: 无法读取")
                main_window_instance.total_time_label.config(text="总时间: --")
                main_window_instance.gif_size_label.config(text="GIF大小: --")
        else:
            main_window_instance.current_img_size_label.config(text="当前图片: --")
            main_window_instance.total_time_label.config(text="总时间: --")
            main_window_instance.gif_size_label.config(text="GIF大小: --")
    else:
        main_window_instance.current_img_size_label.config(text="当前图片: --")
        main_window_instance.total_time_label.config(text="总时间: --")
        main_window_instance.gif_size_label.config(text="GIF大小: --")

    zoom_percent = int(main_window_instance.preview_scale * 100)
    main_window_instance.zoom_label.config(text=f"缩放: {zoom_percent}%")


def update_size_label(x1_var, y1_var, x2_var, y2_var, size_label):
    """
    更新实时尺寸显示
    
    Args:
        x1_var: 起始X坐标变量
        y1_var: 起始Y坐标变量
        x2_var: 结束X坐标变量
        y2_var: 结束Y坐标变量
        size_label: 显示尺寸的Label控件
    """
    try:
        x1 = int(x1_var.get())
        y1 = int(y1_var.get())
        x2 = int(x2_var.get())
        y2 = int(y2_var.get())
        
        # 确保坐标顺序正确
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        width = x2 - x1
        height = y2 - y1
        
        if width > 0 and height > 0:
            size_label.config(text=f"尺寸: {width} x {height}")
        else:
            size_label.config(text="尺寸: --")
    except (ValueError, AttributeError):
        size_label.config(text="尺寸: --")