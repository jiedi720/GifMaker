# -*- coding: utf-8 -*-
"""
裁剪状态管理模块
管理裁剪过程中的状态和坐标转换
"""

import copy
from function.history_manager import HistoryManager


class CropState:
    """裁剪状态管理器"""

    def __init__(self, max_history=100):
        # 保存裁剪结果的字典 {图片路径: 裁剪后的PIL.Image对象}
        self.crop_results = {}
        # 保存裁剪坐标的字典 {图片路径: 裁剪坐标 (x1, y1, x2, y2)}
        self.crop_coords = {}
        # 初始化历史管理器
        self.history_manager = HistoryManager(max_history=max_history)

    def save_crop_state(self):
        """保存当前裁剪状态到历史记录"""
        state = {
            'crop_results': {},
            'crop_coords': {}
        }

        # 保存裁剪结果
        for img_path, cropped_img in self.crop_results.items():
            # 只保存坐标信息，不保存图片对象（避免内存问题）
            if img_path in self.crop_coords:
                state['crop_results'][img_path] = True  # 标记为已裁剪
                state['crop_coords'][img_path] = self.crop_coords[img_path]

        self.history_manager.save_state(state)

    def undo_crop(self):
        """撤销裁剪操作"""
        if not self.history_manager.can_undo():
            return False

        # 获取当前状态
        current_state = {
            'crop_results': {path: True for path in self.crop_results.keys()},
            'crop_coords': self.crop_coords.copy()
        }

        # 执行撤销
        previous_state = self.history_manager.undo(current_state)
        if previous_state:
            # 恢复到上一个状态
            self.crop_results.clear()
            self.crop_coords.clear()

            # 恢复裁剪结果
            for img_path, coords in previous_state['crop_coords'].items():
                self.crop_coords[img_path] = coords

            return True
        return False

    def redo_crop(self):
        """重做裁剪操作"""
        if not self.history_manager.can_redo():
            return False

        # 获取当前状态
        current_state = {
            'crop_results': {path: True for path in self.crop_results.keys()},
            'crop_coords': self.crop_coords.copy()
        }

        # 执行重做
        next_state = self.history_manager.redo(current_state)
        if next_state:
            # 恢复到下一个状态
            self.crop_results.clear()
            self.crop_coords.clear()

            # 恢复裁剪结果
            for img_path, coords in next_state['crop_coords'].items():
                self.crop_coords[img_path] = coords

            return True
        return False

    def get_crop_coords(self, image_path):
        """获取指定图片的裁剪坐标"""
        return self.crop_coords.get(image_path, None)

    def set_crop_coords(self, image_path, coords):
        """设置指定图片的裁剪坐标"""
        self.crop_coords[image_path] = coords

    def get_crop_result(self, image_path):
        """获取指定图片的裁剪结果"""
        return self.crop_results.get(image_path, None)

    def set_crop_result(self, image_path, result):
        """设置指定图片的裁剪结果"""
        self.crop_results[image_path] = result