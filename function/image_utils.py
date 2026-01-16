# -*- coding: utf-8 -*-
"""
图像处理工具模块
提供图像加载、缩放、裁剪等功能
"""

from PIL import Image, ImageTk
import os


def load_image(image_path):
    """
    加载图片

    Args:
        image_path: 图片文件路径

    Returns:
        PIL.Image对象，如果加载失败返回None
    """
    try:
        if not os.path.exists(image_path):
            return None
        return Image.open(image_path)
    except Exception as e:
        print(f"无法加载图片 {image_path}: {e}")
        return None


def resize_image(image, width, height, resample=None):
    """
    调整图片大小

    Args:
        image: PIL.Image对象
        width: 目标宽度
        height: 目标高度
        resample: 重采样方法，默认自动选择

    Returns:
        调整大小后的PIL.Image对象
    """
    if resample is None:
        # 根据缩放方向选择合适的插值算法
        scale = (width * height) / (image.width * image.height)
        resample = Image.Resampling.LANCZOS if scale >= 1.0 else Image.Resampling.BILINEAR

    return image.resize((width, height), resample)


def create_photo_image(image):
    """
    创建Tkinter可用的PhotoImage对象

    Args:
        image: PIL.Image对象

    Returns:
        ImageTk.PhotoImage对象
    """
    return ImageTk.PhotoImage(image)


def calculate_scale_to_fit(image_width, image_height, canvas_width, canvas_height):
    """
    计算让图片适应Canvas的缩放比例

    Args:
        image_width: 图片原始宽度
        image_height: 图片原始高度
        canvas_width: Canvas宽度
        canvas_height: Canvas高度

    Returns:
        缩放比例
    """
    if canvas_width < 100:
        canvas_width = image_width
    if canvas_height < 100:
        canvas_height = image_height

    scale_width = canvas_width / image_width
    scale_height = canvas_height / image_height

    return min(scale_width, scale_height)


def calculate_scale_to_fill(image_width, image_height, canvas_width, canvas_height):
    """
    计算让图片填满Canvas的缩放比例（不留白）

    Args:
        image_width: 图片原始宽度
        image_height: 图片原始高度
        canvas_width: Canvas宽度
        canvas_height: Canvas高度

    Returns:
        缩放比例
    """
    if canvas_width < 100:
        canvas_width = image_width
    if canvas_height < 100:
        canvas_height = image_height

    scale_width = canvas_width / image_width
    scale_height = canvas_height / image_height

    return max(scale_width, scale_height)


def crop_image(image, x1, y1, x2, y2):
    """
    裁剪图片

    Args:
        image: PIL.Image对象
        x1: 左上角x坐标
        y1: 左上角y坐标
        x2: 右下角x坐标
        y2: 右下角y坐标

    Returns:
        裁剪后的PIL.Image对象
    """
    # 确保坐标有效
    x1 = max(0, min(x1, image.width))
    y1 = max(0, min(y1, image.height))
    x2 = max(x1, min(x2, image.width))
    y2 = max(y1, min(y2, image.height))

    return image.crop((x1, y1, x2, y2))