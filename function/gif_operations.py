# -*- coding: utf-8 -*-
"""
GIF操作模块
处理GIF创建和相关操作的非GUI功能
"""

from PIL import Image


def save_gif(frames, output_path, duration=100):
    """
    保存GIF文件
    
    Args:
        frames: 图像帧列?        output_path: 输出文件路径
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
    创建GIF - 使用原文件中的函?    """
    from GifMaker import create_gif as original_create_gif
    original_create_gif(image_paths, output_path, duration, loop, resize, optimize, progress_callback)


def create_gif_from_gui(main_window_instance):
    """
    从GUI创建GIF
    根据用户设置的参数生成GIF文件
    """
    from tkinter import messagebox
    from function.file_manager import validate_gif_params

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
            # 这种情况不应该发生，因为validate_gif_params已经验证?            pass

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

        messagebox.showinfo("成功", f"GIF已成功创?\n{main_window_instance.output_path.get()}")

    except Exception as e:
        messagebox.showerror("错误", f"创建GIF失败:\n{str(e)}")
