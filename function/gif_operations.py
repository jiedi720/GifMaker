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
        #  framesGIF
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
    将多张图片创建为GIF动画

    Args:
        image_paths: 图片路径列表
        output_path: 输出GIF文件路径
        duration: 每帧持续时间（毫秒）
        loop: 循环次数（0表示无限循环）
        resize: 调整尺寸，格式为 (width, height) 或 None
        optimize: 是否优化GIF
        progress_callback: 进度回调函数，接受当前进度百分比作为参数
    """
    if not image_paths:
        raise ValueError("至少需要一张图片")

    # 确保输出目录存在
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 加载和处理所有图片
    images = []
    total_images = len(image_paths)
    
    for i, img_path in enumerate(image_paths):
        try:
            img = Image.open(img_path)
            if resize:
                img = img.resize(resize, Image.Resampling.LANCZOS)
            # 转换为调色板模式以优化GIF
            if img.mode != 'P':
                img = img.convert('P', palette=Image.Palette.ADAPTIVE)
            images.append(img)
            
            # 调用进度回调
            if progress_callback:
                progress = int((i + 1) / total_images * 80)  # 加载图片占80%
                progress_callback(progress)
                
        except Exception as e:
            print(f"警告: 无法加载图片 {img_path}: {e}")
            if progress_callback:
                progress = int((i + 1) / total_images * 80)
                progress_callback(progress)
            continue

    if not images:
        raise ValueError("没有成功加载任何图片")

    # 保存为GIF
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop,
        optimize=optimize
    )
    
    # 完成
    if progress_callback:
        progress_callback(100)
        
    print(f"GIF已成功创建: {output_path}")


def create_gif_from_gui(main_window_instance):
    """
    从GUI创建GIF
    根据用户设置的参数生成GIF文件
    """
    from tkinter import messagebox
    from .file_manager import validate_gif_params

    is_valid, error_msg = validate_gif_params(
        main_window_instance.image_paths,
        main_window_instance.output_path.get(),
        main_window_instance.resize_width.get(),
        main_window_instance.resize_height.get()
    )
    if not is_valid:
        messagebox.showerror("错误", error_msg)
        return

    resize = None
    if main_window_instance.resize_width.get() and main_window_instance.resize_height.get():
        try:
            width = int(main_window_instance.resize_width.get())
            height = int(main_window_instance.resize_height.get())
            resize = (width, height)
        except ValueError:
            pass

    #  GIF
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