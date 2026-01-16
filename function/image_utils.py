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





def get_image_info(image_path):
    """
    获取图片信息

    Args:
        image_path: 图片文件路径

    Returns:
        包含图片信息的字典，格式为:
        {
            'width': 宽度,
            'height': 高度,
            'size_kb': 文件大小(KB),
            'format': 图片格式,
            'mode': 图片模式
        }
        如果加载失败返回None
    """
    try:
        if not os.path.exists(image_path):
            return None

        img = Image.open(image_path)
        file_size = os.path.getsize(image_path) / 1024  # 转换为KB

        return {
            'width': img.width,
            'height': img.height,
            'size_kb': file_size,
            'format': img.format,
            'mode': img.mode
        }
    except Exception as e:
        print(f"无法获取图片信息 {image_path}: {e}")
        return None


def calculate_grid_layout(image_paths, pending_crops, preview_scale=1.0, thumbnail_size=(200, 150), canvas_width=None, canvas_height=None):
    """
    计算网格布局，返回每张图片的位置和大小

    Args:
        image_paths: 图片路径列表
        pending_crops: 待裁剪的图片集合
        preview_scale: 预览缩放比例
        thumbnail_size: 缩略图大小 (width, height)
        canvas_width: Canvas宽度（可选，默认800）
        canvas_height: Canvas高度（可选，默认600）

    Returns:
        包含布局信息的字典列表，每个字典包含:
        {
            'index': 图片索引,
            'path': 图片路径,
            'position': (x, y) 坐标元组,
            'size': (width, height) 尺寸元组,
            'col': 列索引,
            'row': 行索引,
            'is_cropped': 是否已裁剪
        }
    """
    if not image_paths:
        return []

    # 计算可用的缩略图大小
    thumb_width = int(thumbnail_size[0] * preview_scale)
    thumb_height = int(thumbnail_size[1] * preview_scale)

    # 使用传入的Canvas尺寸或默认值
    if canvas_width is None:
        canvas_width = 800
    if canvas_height is None:
        canvas_height = 600

    padding = 10
    cols = max(1, int(canvas_width / (thumb_width + padding)))
    rows = (len(image_paths) + cols - 1) // cols

    layout = []

    for i, img_path in enumerate(image_paths):
        col = i % cols
        row = i // cols

        x = padding + col * (thumb_width + padding)
        y = padding + row * (thumb_height + padding)

        layout.append({
            'index': i,
            'path': img_path,
            'position': (x, y),
            'size': (thumb_width, thumb_height),
            'col': col,
            'row': row,
            'is_cropped': img_path in pending_crops
        })

    return layout


def find_smallest_image_path(image_paths, all_image_paths):
    """
    在给定的图片路径列表中找到最小的图片（按尺寸）

    Args:
        image_paths: 要检查的图片路径列表
        all_image_paths: 所有图片路径列表（用于查找索引）

    Returns:
        (最小图片路径, 在all_image_paths中的索引)
    """
    if not image_paths:
        return None, -1

    min_size = float('inf')
    min_path = None
    min_index = -1

    for img_path in image_paths:
        try:
            img_info = get_image_info(img_path)
            if img_info:
                size = img_info['width'] * img_info['height']
                if size < min_size:
                    min_size = size
                    min_path = img_path
                    if img_path in all_image_paths:
                        min_index = all_image_paths.index(img_path)
        except Exception:
            continue

    return min_path, min_index