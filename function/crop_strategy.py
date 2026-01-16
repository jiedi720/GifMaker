"""
策略模块
定义裁剪策略，判断当前操作对象是单张基础图像还是作为序列同步的参考基�?
"""

from typing import List, Tuple, Optional


def determine_crop_strategy(image_paths: List[str], current_index: int) -> Tuple[bool, str, int]:
    """确定裁剪策略
    
    Args:
        image_paths: 图片路径列表
        current_index: 当前图片索引
        
    Returns:
        tuple: (is_base_image, current_image_path, current_index)
    """
    if not image_paths:
        return False, '', -1
    
    is_base_image = False
    current_image_path = ''
    
    if len(image_paths) > 1:
        # 多张图片的情况，需要找到尺寸最小的作为基准
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
        
        current_image_path = min_path
        current_index = min_index
        
        # 如果传入的当前图片路径不是最小尺寸的图片，则使用最小尺寸的图片作为基准
        if image_paths[current_index] != min_path:
            is_base_image = True
    else:
        # 只有一张图片，直接使用
        current_image_path = image_paths[current_index] if 0 <= current_index < len(image_paths) else image_paths[0] if image_paths else ''
        
    return is_base_image, current_image_path, current_index


def find_smallest_image_path(image_paths: List[str]) -> Tuple[Optional[str], int]:
    """查找图片列表中尺寸最小的图片路径
    
    Args:
        image_paths: 图片路径列表
        
    Returns:
        tuple: (最小图片路�? 索引)
    """
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


def is_single_image_mode(image_paths: List[str]) -> bool:
    """判断是否为单张图片模�?
    
    Args:
        image_paths: 图片路径列表
        
    Returns:
        bool: 是否为单张图片模�?
    """
    return len(image_paths) <= 1


def get_target_paths(selected_indices: set, all_paths: List[str]) -> List[str]:
    """获取目标路径列表
    
    Args:
        selected_indices: 选中的索引集�?
        all_paths: 所有路径列�?
        
    Returns:
        List[str]: 目标路径列表
    """
    if selected_indices and len(selected_indices) > 1:
        # 多选模�?
        target_indices = sorted(list(selected_indices))
        return [all_paths[i] for i in target_indices if 0 <= i < len(all_paths)]
    else:
        # 单选模�?
        if selected_indices:
            idx = list(selected_indices)[0]
            if 0 <= idx < len(all_paths):
                return [all_paths[idx]]
        return []
