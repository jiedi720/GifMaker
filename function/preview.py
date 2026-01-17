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
    重置缩放为原始尺寸（Natural Size）

    功能说明：
    - 取消一切动态缩放计算
    - 将图片的显示尺寸直接设置为其物理原始尺寸（Natural Size/Dimensions）
    - 基于图片自身的 naturalWidth 和 naturalHeight
    - 缩放比例设置为 1.0，表示 1:1 像素映射

    明确定义：
    - "重置"是指回归图片自身的原始宽度和高度数值
    - 而非简单的 1:1 视口填充

    适用场景：
    - 图片原始尺寸小于窗口：图片按原始尺寸显示，周围留白
    - 图片原始尺寸大于窗口：图片按原始尺寸显示，超出部分可通过滚动查看

    Args:
        main_window_instance: 主窗口实例
    """
    if not main_window_instance.image_paths:
        return

    # 设置缩放比例为 1.0，表示 1:1 像素映射（图片原始尺寸）
    main_window_instance.preview_scale = 1.0

    # 刷新预览显示（始终使用网格预览模式）
    main_window_instance.display_grid_preview()


def update_single_preview(main_window_instance):
    """
    更新单张图片预览，用于显示当前选中的图片
    Args:
        main_window_instance: 主窗口实例
    """
    if not main_window_instance.image_paths or main_window_instance.selected_image_index < 0:
        return
    
    main_window_instance.preview_specific_image(main_window_instance.selected_image_index)


def fit_preview_to_window(main_window_instance):
    """
    适应窗口 - 确保所有图片都可见

    功能说明：
    - 计算合适的缩放比例，使所有图片都完整显示在预览窗口内
    - 核心约束：必须保证所有图片在窗口内完整显示，不得有任何部分超出视口
    - 必须保持原始纵横比，严禁拉伸变形
    - 这是典型的 Object-fit: contain 逻辑，但应用于整个图片集合

    计算逻辑：
    - 使用当前缩放比例计算所有图片的布局
    - 检查布局的总尺寸（最大 x 和最大 y）
    - 如果布局超出窗口，调整缩放比例
    - 重复计算直到所有图片都能完整显示

    适用场景：
    - 多张图片：确保所有图片都能完整显示在窗口内
    - 单张图片：让图片充满窗口的一个维度

    交互关联：
    - 当窗口尺寸发生变化（Resize）时，需重新计算缩放比例

    Args:
        main_window_instance: 主窗口实例
    """
    if not main_window_instance.image_paths:
        return

    # 获取Canvas的实际尺寸（视口尺寸）
    main_window_instance.preview_canvas.update_idletasks()
    canvas_width = main_window_instance.preview_canvas.winfo_width()
    canvas_height = main_window_instance.preview_canvas.winfo_height()

    if canvas_width <= 0 or canvas_height <= 0:
        return

    # 导入布局计算函数
    from function.image_utils import calculate_grid_layout

    # 二分查找法找到合适的缩放比例
    min_scale = 0.01
    max_scale = 5.0
    best_scale = 1.0
    tolerance = 0.001

    for _ in range(20):  # 最多迭代20次
        test_scale = (min_scale + max_scale) / 2

        # 使用测试缩放比例计算布局
        layout = calculate_grid_layout(
            main_window_instance.image_paths,
            main_window_instance.pending_crops,
            test_scale,
            canvas_width=canvas_width,
            canvas_height=canvas_height
        )

        if not layout:
            break

        # 计算布局的总尺寸
        max_x = max(item['position'][0] + item['size'][0] for item in layout)
        max_y = max(item['position'][1] + item['size'][1] for item in layout)

        # 检查布局是否能完整显示在Canvas中（考虑padding）
        padding = 10
        if max_x <= canvas_width - padding and max_y <= canvas_height - padding:
            # 布局可以完整显示，尝试更大的缩放比例
            best_scale = test_scale
            min_scale = test_scale
        else:
            # 布局超出窗口，尝试更小的缩放比例
            max_scale = test_scale

        # 如果缩放范围已经很小，停止迭代
        if max_scale - min_scale < tolerance:
            break

    # 应用最佳缩放比例
    main_window_instance.preview_scale = best_scale

    # 刷新预览显示（始终使用网格预览模式）
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

    try:
        # 加载并处理所有图片帧
        frames = []
        duration = main_window_instance.duration.get()
        loop = main_window_instance.loop.get()

        for img_path in main_window_instance.image_paths:
            try:
                img = Image.open(img_path)

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
        from gui.gifpreview_gui import GifPreviewWindow
        preview_window = GifPreviewWindow(main_window_instance.root, frames, duration, main_window_instance.output_path.get(), loop)

    except Exception as e:
        messagebox.showerror("错误", f"预览GIF失败:\n{str(e)}")
