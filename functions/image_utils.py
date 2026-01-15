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


def auto_crop_image(image, margin=5, threshold=10):
    """
    自动裁剪功能 - 自动检测图片内容并去除空白边缘
    
    Args:
        image: PIL.Image对象
        margin: 边距大小（像素）
        threshold: 检测非空白区域的阈值
        
    Returns:
        元组 (x1, y1, x2, y2) 或 None（如果检测失败）
    """
    try:
        import numpy as np
        
        # 将图片转换为numpy数组
        img_array = np.array(image)

        # 如果是RGBA，转换为RGB
        if img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]

        # 转换为灰度图
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array

        # 设置阈值，检测非空白区域
        mask = gray > threshold

        # 找到非空白区域的边界
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)

        if not np.any(rows) or not np.any(cols):
            return None

        y1, y2 = np.where(rows)[0][[0, -1]]
        x1, x2 = np.where(cols)[0][[0, -1]]

        # 添加边距
        x1 = max(0, x1 - margin)
        y1 = max(0, y1 - margin)
        x2 = min(image.width, x2 + margin)
        y2 = min(image.height, y2 + margin)

        return (x1, y1, x2, y2)
        
    except ImportError:
        print("自动裁剪功能需要 numpy 库")
        return None
    except Exception as e:
        print(f"自动裁剪失败: {e}")
        return None