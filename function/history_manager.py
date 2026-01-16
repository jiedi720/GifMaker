# -*- coding: utf-8 -*-
"""
历史管理模块
提供撤销/重做功能，支持无限次操作历史
"""

import copy
from typing import Any, Dict, List, Optional
from tkinter import messagebox


class HistoryManager:
    """历史管理器类，支持撤销和重做操作"""

    def __init__(self, max_history: int = 100):
        """
        初始化历史管理器

        Args:
            max_history: 最大历史记录数量，默认为100
        """
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self.max_history = max_history

    def save_state(self, state: Dict[str, Any]) -> None:
        """
        保存当前状态到撤销栈
        Args:
            state: 要保存的状态字典
        """
        # 深拷贝状态，避免引用问题
        state_copy = copy.deepcopy(state)
        self.undo_stack.append(state_copy)

        # 限制撤销栈的大小
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        # 清空重做栈
        self.redo_stack.clear()

    def undo(self, current_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        执行撤销操作

        Args:
            current_state: 当前状态
        Returns:
            上一个状态，如果没有可撤销的操作则返回None
        """
        if not self.undo_stack:
            return None

        # 保存当前状态到重做栈
        current_copy = copy.deepcopy(current_state)
        self.redo_stack.append(current_copy)

        # 从撤销栈弹出上一个状态
        previous_state = self.undo_stack.pop()
        return previous_state

    def redo(self, current_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        执行重做操作

        Args:
            current_state: 当前状态

        Returns:
            下一个状态，如果没有可重做的操作则返回None
        """
        if not self.redo_stack:
            return None

        # 保存当前状态到撤销栈
        current_copy = copy.deepcopy(current_state)
        self.undo_stack.append(current_copy)

        # 从重做栈弹出下一个状态
        next_state = self.redo_stack.pop()
        return next_state

    def can_undo(self) -> bool:
        """
        检查是否可以撤销

        Returns:
            如果可以撤销返回True，否则返回False
        """
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """
        检查是否可以重做

        Returns:
            如果可以重做返回True，否则返回False
        """
        return len(self.redo_stack) > 0

    def clear(self) -> None:
        """清空所有历史记录"""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def get_undo_count(self) -> int:
        """
        获取可撤销的次数

        Returns:
            可撤销的次数
        """
        return len(self.undo_stack)

    def get_redo_count(self) -> int:
        """
        获取可重做的次数

        Returns:
            可重做的次数
        """
        return len(self.redo_stack)


class UndoRedoManager:
    """撤销/重做管理器"""

    def __init__(self, max_steps: int = 50):
        self.undo_stack = []  # 撪销栈
        self.redo_stack = []  # 重做栈
        self.max_steps = max_steps

    def save_state(self, state):
        self.undo_stack.append(state.copy())
        if len(self.undo_stack) > self.max_steps:
            self.undo_stack.pop(0)  # 移除最早的记录
        # 清空重做栈，因为新的操作使重做历史失效
        self.redo_stack.clear()

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def undo(self, current_state):
        if not self.can_undo():
            return None

        # 将当前状态保存到重做栈
        self.redo_stack.append(current_state.copy())

        # 从撤销栈中取出上一个状态
        return self.undo_stack.pop()

    def redo(self, current_state):
        if not self.can_redo():
            return None

        # 将当前状态保存到撤销栈
        self.undo_stack.append(current_state.copy())

        # 从重做栈中取出下一个状态
        return self.redo_stack.pop()


def save_crop_state(crop_state_obj):
    """保存当前裁剪状态到历史记录"""
    crop_state_obj.save_crop_state()
    print(f"已保存裁剪状态，可撤销次数: {crop_state_obj.history_manager.get_undo_count()}")


def undo_crop(crop_state_obj):
    """撤销裁剪操作"""
    if crop_state_obj.undo_crop():
        print(f"已撤销裁剪操作，可重做次数: {crop_state_obj.history_manager.get_redo_count()}")
        messagebox.showinfo("撤销", "已撤销裁剪操作")
    else:
        messagebox.showinfo("提示", "没有可撤销的操作")


def redo_crop(crop_state_obj):
    """重做裁剪操作"""
    if crop_state_obj.redo_crop():
        print(f"已重做裁剪操作，可撤销次数: {crop_state_obj.history_manager.get_undo_count()}")
        messagebox.showinfo("重做", "已重做裁剪操作")
    else:
        messagebox.showinfo("提示", "没有可重做的操作")


def save_state(main_window_instance, backup_images=False):
    """保存当前状态到历史栈"""
    # 保存当前图片列表的深拷贝
    import copy
    current_state = copy.deepcopy(main_window_instance.image_paths)
    state_data = {
        'image_paths': current_state,
        'pending_crops': {}  # 保存当前的 pending_crops 状态
    }

    # 保存当前的 pending_crops 状态
    if main_window_instance.pending_crops:
        # 保存裁剪坐标信息
        state_data['pending_crops'] = {}
        for img_path in main_window_instance.pending_crops.keys():
            if img_path in main_window_instance.pending_crop_coords:
                state_data['pending_crops'][img_path] = {
                    'coords': main_window_instance.pending_crop_coords[img_path]
                }
            else:
                # 如果没有坐标信息，只保存路径
                state_data['pending_crops'][img_path] = {}

    main_window_instance.history_manager.save_state(state_data)


def undo(main_window_instance):
    """撤销操作"""
    if not main_window_instance.history_manager.can_undo():
        messagebox.showinfo("提示", "没有可撤销的操作")
        return

    # 保存当前状态到重做栈
    import copy
    current_state = copy.deepcopy(main_window_instance.image_paths)
    redo_state = {
        'image_paths': current_state,
        'pending_crops': {}  # 保存当前的 pending_crops 状态
    }

    # 保存当前的 pending_crops 状态
    if main_window_instance.pending_crops:
        # 保存裁剪坐标信息
        redo_state['pending_crops'] = {}
        for img_path in main_window_instance.pending_crops.keys():
            if img_path in main_window_instance.pending_crop_coords:
                redo_state['pending_crops'][img_path] = {
                    'coords': main_window_instance.pending_crop_coords[img_path]
                }
            else:
                # 如果没有坐标信息，只保存路径
                redo_state['pending_crops'][img_path] = {}

    # 使用history_manager执行撤销
    previous_state = main_window_instance.history_manager.undo(redo_state)
    if previous_state:
        # 处理状态数据结构
        if 'image_paths' in previous_state:
            main_window_instance.image_paths = previous_state['image_paths']

            # 恢复 pending_crops 状态
            if 'pending_crops' in previous_state:
                # 清除当前状态中在 previous_state 中存在的 pending_crops
                for img_path in previous_state['pending_crops'].keys():
                    if img_path in main_window_instance.pending_crops:
                        del main_window_instance.pending_crops[img_path]
                        print(f"已清除待保存的裁剪: {img_path}")
                    if img_path in main_window_instance.pending_crop_coords:
                        del main_window_instance.pending_crop_coords[img_path]
        else:
            # 兼容旧的状态格式（直接是列表）
            main_window_instance.image_paths = previous_state
            # 清除所有 pending_crops
            main_window_instance.pending_crops.clear()
            main_window_instance.pending_crop_coords.clear()

        # 更新界面
        main_window_instance.update_image_list()
        print("已撤销操作")


def redo(main_window_instance):
    """重做操作"""
    if not main_window_instance.history_manager.can_redo():
        messagebox.showinfo("提示", "没有可重做的操作")
        return

    # 保存当前状态到撤销栈
    import copy
    import shutil
    current_state = copy.deepcopy(main_window_instance.image_paths)
    undo_state = {
        'image_paths': current_state,
        'backup_files': [],
        'pending_crops': {}  # 保存当前的 pending_crops 状态
    }

    # 保存当前的 pending_crops 状态
    if main_window_instance.pending_crops:
        # 保存裁剪坐标信息
        undo_state['pending_crops'] = {}
        for img_path in main_window_instance.pending_crops.keys():
            if img_path in main_window_instance.pending_crop_coords:
                undo_state['pending_crops'][img_path] = {
                    'coords': main_window_instance.pending_crop_coords[img_path]
                }
            else:
                # 如果没有坐标信息，只保存路径
                undo_state['pending_crops'][img_path] = {}

    # 如果当前状态有备份文件，也需要保存到重做栈
    if hasattr(main_window_instance, 'undo_stack') and main_window_instance.undo_stack and 'backup_files' in main_window_instance.undo_stack[-1]:
        for backup_info in main_window_instance.undo_stack[-1]['backup_files']:
            try:
                # 创建当前文件的备份作为重做时的恢复点
                backup_filename = f"redo_backup_{os.path.basename(backup_info['original'])}"
                temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                backup_path = os.path.join(temp_dir, backup_filename)
                shutil.copy2(backup_info['original'], backup_path)
                undo_state['backup_files'].append({
                    'original': backup_info['original'],
                    'backup': backup_path
                })
            except Exception as e:
                print(f"创建重做备份失败 {backup_info['original']}: {e}")

    # 使用history_manager执行重做
    next_state = main_window_instance.history_manager.redo(undo_state)
    if next_state:
        # 处理状态数据结构
        if 'image_paths' in next_state:
            main_window_instance.image_paths = next_state['image_paths']

            # 恢复 pending_crops 状态
            if 'pending_crops' in next_state:
                print(f"重做: 恢复 pending_crops")
                print(f"  当前 pending_crops: {list(main_window_instance.pending_crops.keys())}")
                print(f"  目标 pending_crops: {list(next_state['pending_crops'].keys())}")

                # 清除当前状态中不在 next_state 中的 pending_crops
                current_pending = set(main_window_instance.pending_crops.keys())
                next_pending = set(next_state['pending_crops'].keys())
                to_remove = current_pending - next_pending
                for img_path in to_remove:
                    if img_path in main_window_instance.pending_crops:
                        del main_window_instance.pending_crops[img_path]
                        print(f"已清除待保存的裁剪: {img_path}")

                # 添加 next_state 中存在但当前状态中不存在的 pending_crops
                to_add = next_pending - current_pending
                print(f"  需要添加的裁剪: {list(to_add)}")
                for img_path in to_add:
                    # 重新加载图片并应用裁剪
                    from .image_utils import load_image, crop_image
                    img = load_image(img_path)
                    if img and img_path in next_state['pending_crops']:
                        crop_data = next_state['pending_crops'][img_path]
                        print(f"  裁剪数据: {crop_data}")
                        # crop_data 应该包含裁剪坐标
                        if isinstance(crop_data, dict) and 'coords' in crop_data:
                            x1, y1, x2, y2 = crop_data['coords']
                            print(f"  应用裁剪坐标: ({x1}, {y1}, {x2}, {y2})")
                            cropped_img = crop_image(img, x1, y1, x2, y2)
                            main_window_instance.pending_crops[img_path] = cropped_img
                            main_window_instance.pending_crop_coords[img_path] = (x1, y1, x2, y2)
                            print(f"已恢复待保存的裁剪: {img_path}")
                        else:
                            print(f"  警告: 裁剪数据格式不正确: {crop_data}")
        else:
            # 兼容旧的状态格式（直接是列表）
            main_window_instance.image_paths = next_state
            # 清除所有 pending_crops
            main_window_instance.pending_crops.clear()

        # 更新界面
        main_window_instance.update_image_list()