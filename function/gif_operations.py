# -*- coding: utf-8 -*-
"""
GIF操作模块
处理GIF创建和相关操作的非GUI功能
"""

from PIL import Image
import os


def save_gif(frames, output_path, duration=100):
    """
    保存GIF文件

    Args:
        frames: 图像帧列表
        output_path: 输出文件路径
        duration: 每帧持续时间（毫秒）
    """
    if not output_path:
        raise ValueError("请先设置输出文件路径")

    try:
        # 直接保存frames为GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            optimize=True
        )
        return True
    except Exception as e:
        raise e


def create_gif(image_paths, output_path, duration=100, loop=0, resize=None, optimize=True, progress_callback=None):
    """
    创建GIF - 使用原文件中的函数
    """
    from .image_utils import load_image, resize_image

    if not image_paths:
        raise ValueError("图片路径列表不能为空")

    if not output_path:
        raise ValueError("输出路径不能为空")

    # 加载所有图片
    frames = []
    for img_path in image_paths:
        img = load_image(img_path)
        if img is None:
            print(f"警告: 无法加载图片 {img_path}")
            continue

        # 如果需要调整尺寸
        if resize:
            img = resize_image(img, resize[0], resize[1])

        # 确保所有图片使用相同的模式
        if img.mode != 'P':
            img = img.convert('P')

        frames.append(img)

    if not frames:
        raise ValueError("没有成功加载任何图片")

    # 保存GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
        optimize=optimize
    )

    # 调用进度回调（如果提供）
    if progress_callback:
        progress_callback(100)  # 完成100%

    return True


def create_gif_from_gui(main_window_instance):
    """
    从GUI创建GIF
    根据用户设置的参数生成GIF文件
    """
    from tkinter import messagebox
    from .file_manager import validate_gif_params

    # 委托给业务逻辑模块验证参数
    is_valid, error_msg = validate_gif_params(
        main_window_instance.image_paths,
        main_window_instance.output_path.get(),
        main_window_instance.resize_width.get(),
        main_window_instance.resize_height.get()
    )
    if not is_valid:
        messagebox.showerror("错误", error_msg)
        return

    # 处理尺寸调整参数
    resize = None
    if main_window_instance.resize_width.get() and main_window_instance.resize_height.get():
        try:
            width = int(main_window_instance.resize_width.get())
            height = int(main_window_instance.resize_height.get())
            resize = (width, height)
        except ValueError:
            # 这种情况不应该发生，因为validate_gif_params已经验证
            pass

    # 委托给业务逻辑模块创建GIF
    try:
        create_gif(
            image_paths=main_window_instance.image_paths,
            output_path=main_window_instance.output_path.get(),
            duration=main_window_instance.duration.get(),
            loop=main_window_instance.loop.get(),
            resize=resize,
            optimize=main_window_instance.optimize.get()
        )

        messagebox.showinfo("成功", f"GIF已成功创建\n{main_window_instance.output_path.get()}")

    except Exception as e:
        messagebox.showerror("错误", f"创建GIF失败:\n{str(e)}")