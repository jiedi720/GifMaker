# -*- coding: utf-8 -*-
"""
文件处理和参数验证模块
提供文件验证、路径处理、文件大小获取、参数验证等功能
"""

import os
from tkinter import filedialog


def validate_image_path(image_path: str) -> bool:
    """验证图片路径是否有效"""
    if not image_path or not os.path.exists(image_path):
        return False

    ext = os.path.splitext(image_path)[1].lower()
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    return ext in valid_extensions


def get_file_size_kb(file_path: str) -> float:
    """获取文件大小（KB）"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / 1024
    return 0.0


def get_image_files(directory: str) -> list:
    """获取目录中的所有图片文件"""
    image_files = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in valid_extensions:
                image_files.append(os.path.join(root, file))

    return sorted(image_files)


def remove_duplicates_preserve_order(items):
    """移除列表中的重复项，保持原有顺序"""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def batch_save_cropped_images(pending_crops):
    """批量保存裁剪后的图片"""
    saved_count = 0
    failed_count = 0

    for img_path, cropped_img in pending_crops.items():
        try:
            cropped_img.save(img_path)
            saved_count += 1
            print(f"已保存裁剪图片: {img_path}")
        except Exception as e:
            failed_count += 1
            print(f"保存图片失败 {img_path}: {str(e)}")

    return saved_count, failed_count


def select_images(main_window_instance):
    """
    选择图片文件
    打开文件选择对话框，让用户选择要制作GIF的图片文件
    选择新图片时会清除已有的图片，只保留新选择的图片
    """

    files = filedialog.askopenfilenames(
        title="选择图片文件",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
            ("All files", "*.*")
        ]
    )
    if files:
        # 保存当前状态到历史记录
        from function.history_manager import save_state as save_main_window_state
        save_main_window_state(main_window_instance)

        # 清除已有图片，只保留新选择的图片
        main_window_instance.image_paths = list(files)

        # 重置选择状态
        main_window_instance.selected_image_indices = set()
        main_window_instance.selected_image_index = -1
        main_window_instance.last_selected_index = -1
        main_window_instance.pending_crops = {}
        main_window_instance.pending_crop_coords = {}

        # 使用适应窗口模式
        from function.preview import fit_preview_to_window
        fit_preview_to_window(main_window_instance)


def select_directory(main_window_instance):
    """
    选择包含图片的目录
    打开目录选择对话框，自动获取目录中所有图片文件
    选择新目录时会清除已有的图片，只保留新选择的图片
    """
    directory = filedialog.askdirectory(title="选择包含图片的目录")
    if directory:
        # 获取目录中的图片文件
        image_files = get_image_files(directory)

        if image_files:
            # 保存当前状态到历史记录
            from function.history_manager import save_state as save_main_window_state
            save_main_window_state(main_window_instance)

            # 清除已有图片，只保留新选择的图片
            main_window_instance.image_paths = image_files

            # 重置选择状态
            main_window_instance.selected_image_indices = set()
            main_window_instance.selected_image_index = -1
            main_window_instance.last_selected_index = -1
            main_window_instance.pending_crops = {}
            main_window_instance.pending_crop_coords = {}

            # 使用适应窗口模式
            from function.preview import fit_preview_to_window
            fit_preview_to_window(main_window_instance)

def clear_images(main_window_instance):
    """
    清空图片列表
    清除所有已选择的图片路径
    """
    from function.history_manager import save_state as save_main_window_state
    save_main_window_state(main_window_instance)

    main_window_instance.image_paths = []
    main_window_instance.selected_image_indices = set()
    main_window_instance.selected_image_index = -1
    main_window_instance.last_selected_index = -1
    main_window_instance.pending_crops = {}
    main_window_instance.pending_crop_coords = {}
    main_window_instance.preview_scale = 1.0
    main_window_instance.display_grid_preview()




def calculate_total_time(num_images: int, duration_ms: int) -> tuple:
    """计算GIF总时间"""
    total_time_ms = num_images * duration_ms
    total_time_s = total_time_ms / 1000
    return total_time_s, total_time_ms


def validate_gif_params(image_paths, output_path, resize_width, resize_height):
    """验证GIF参数"""
    if not image_paths:
        return False, "请先选择至少一张图片"

    if not output_path:
        return False, "请选择输出文件路径"

    if resize_width and resize_height:
        try:
            width = int(resize_width)
            height = int(resize_height)
            if width <= 0 or height <= 0:
                return False, "尺寸参数必须大于0"
        except ValueError:
            return False, "尺寸参数必须是数字"

    return True, ""


def estimate_gif_size(image_paths: list) -> float:
    """估算GIF大小"""
    total_original_size = sum(os.path.getsize(path)/1024 for path in image_paths)  # KB
    estimated_gif_size = total_original_size * 0.3  #  30%
    return estimated_gif_size


def is_single_image_mode(image_paths: list) -> bool:
    """判断是否为单张图片模式

    Args:
        image_paths: 图片路径列表

    Returns:
        bool: 是否为单张图片模式
    """
    return len(image_paths) <= 1


def get_target_paths(selected_indices: set, all_paths: list) -> list:
    """获取目标路径列表

    Args:
        selected_indices: 选中的索引集合
        all_paths: 所有路径列表

    Returns:
        list: 目标路径列表
    """
    if selected_indices and len(selected_indices) > 1:
        target_indices = sorted(list(selected_indices))
        return [all_paths[i] for i in target_indices if 0 <= i < len(all_paths)]
    else:
        if selected_indices:
            idx = list(selected_indices)[0]
            if 0 <= idx < len(all_paths):
                return [all_paths[idx]]
        return []