# -*- coding: utf-8 -*-
"""
裁剪逻辑处理模块
处理裁剪过程中的非UI逻辑
"""


def find_smallest_image_path(image_paths):
    """查找图片列表中尺寸最小的图片路径"""
    if not image_paths:
        return None, -1
    
    min_size = float('inf')
    min_path = image_paths[0]
    min_index = 0
    
    for i, path in enumerate(image_paths):
        try:
            from PIL import Image
            img = Image.open(path)
            width, height = img.size
            size = width * height
            if size < min_size:
                min_size = size
                min_path = path
                min_index = i
        except Exception as e:
            print(f"无法读取图片尺寸 {path}: {e}")
            continue
    
    return min_path, min_index


def calculate_scaled_dimensions(orig_width, orig_height, canvas_width, canvas_height, padding=20):
    """计算适应画布的缩放尺寸"""
    from function.image_utils import calculate_scale_to_fit
    
    # 获取适应画布的缩放比例
    scale = calculate_scale_to_fit(orig_width, orig_height, canvas_width - padding, canvas_height - padding)
    
    # 计算缩放后的尺寸
    scaled_width = int(orig_width * scale)
    scaled_height = int(orig_height * scale)
    
    return scaled_width, scaled_height, scale


def convert_canvas_to_image_coords(canvas_x, canvas_y, image_x, image_y, preview_scale, image_width, image_height):
    """将画布坐标转换为图片坐标"""
    # 计算图片在Canvas中的实际位置
    img_left = image_x - image_width // 2
    img_top = image_y - image_height // 2
    
    # 转换为原始图片坐标
    orig_x = int((canvas_x - img_left) / preview_scale)
    orig_y = int((canvas_y - img_top) / preview_scale)
    
    return orig_x, orig_y


def validate_crop_coordinates(x1, y1, x2, y2, img_width, img_height):
    """验证裁剪坐标是否有效"""
    # 确保坐标在图片范围内
    x1 = max(0, min(x1, img_width))
    y1 = max(0, min(y1, img_height))
    x2 = max(0, min(x2, img_width))
    y2 = max(0, min(y2, img_height))
    
    # 确保坐标顺序正确
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    
    # 确保选框有效（宽度、高度至少为1）
    if x2 - x1 < 1:
        x2 = x1 + 1
    if y2 - y1 < 1:
        y2 = y1 + 1
    
    return x1, y1, x2, y2


def calculate_aspect_ratio(width, height):
    """计算宽高比"""
    if height > 0:
        return width / height
    else:
        return 0.0


def apply_aspect_ratio_constraints(x1, y1, x2, y2, aspect_ratio, constraint_type="lock_current"):
    """应用宽高比约束"""
    if constraint_type == "free" or aspect_ratio is None:
        return x1, y1, x2, y2
    
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    
    if width == 0 or height == 0:
        return x1, y1, x2, y2
    
    # 根据宽高比调整尺寸
    if constraint_type in ['nw', 'ne', 'sw', 'se']:
        # 角点：根据宽度调整高度
        new_height = int(width / aspect_ratio)
        if constraint_type in ['nw', 'sw']:
            y1 = y2 - new_height
        else:
            y2 = y1 + new_height
    elif constraint_type in ['n', 's']:
        # 上下边：根据高度调整宽度
        new_width = int(height * aspect_ratio)
        x2 = x1 + new_width
    elif constraint_type in ['e', 'w']:
        # 左右边：根据宽度调整高度
        new_height = int(width / aspect_ratio)
        y2 = y1 + new_height
    
    # 确保选框有效
    if abs(x2 - x1) < 1:
        if constraint_type in ['nw', 'w', 'sw']:
            x1 = x2 - 1
        else:
            x2 = x1 + 1
    if abs(y2 - y1) < 1:
        if constraint_type in ['nw', 'n', 'ne']:
            y1 = y2 - 1
        else:
            y2 = y1 + 1
    
    return x1, y1, x2, y2