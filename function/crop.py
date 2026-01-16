# -*- coding: utf-8 -*-
"""
裁剪功能模块
整合了裁剪相关的所有功能，包括比例处理、逻辑计算、状态管理和策略制定
"""

from typing import Tuple, Optional, Any, List
from tkinter import messagebox
from PIL import Image
import copy
from .history_manager import HistoryManager


class CropRatioHandler:
    """裁剪比例处理器"""

    def __init__(self):
        self.is_ratio_locked = False
        self.ratio_value = None
        self.dialog = None  # Reference to CropDialog instance

    def lock_ratio(self, ratio_type: str, x1: int, y1: int, x2: int, y2: int) -> Tuple[bool, float, Tuple[int, int, int, int]]:
        """锁定比例

        Args:
            ratio_type: 比例类型 ('free', 'lock_current', '1:1', '16:9', '4:3', '3:2', '1.618')
            x1, y1, x2, y2: 当前选框坐标

        Returns:
            tuple: (is_locked, ratio_value, new_coords)
        """
        if ratio_type == "free":
            self.is_ratio_locked = False
            self.ratio_value = None
            return False, None, (x1, y1, x2, y2)
        elif ratio_type == "lock_current":
            # 锁定当前选框的比例
            width = abs(x2 - x1)
            height = abs(y2 - y1)

            if height > 0:
                current_ratio = width / height
                self.is_ratio_locked = True
                self.ratio_value = current_ratio
                return True, current_ratio, (x1, y1, x2, y2)
            else:
                return False, None, (x1, y1, x2, y2)
        elif ratio_type == "1:1":
            self.is_ratio_locked = True
            self.ratio_value = 1.0
            new_coords = self._apply_ratio_lock(x1, y1, x2, y2, 1.0)
            return True, 1.0, new_coords
        elif ratio_type == "16:9":
            self.is_ratio_locked = True
            self.ratio_value = 16.0 / 9.0
            new_coords = self._apply_ratio_lock(x1, y1, x2, y2, 16.0 / 9.0)
            return True, 16.0 / 9.0, new_coords
        elif ratio_type == "4:3":
            self.is_ratio_locked = True
            self.ratio_value = 4.0 / 3.0
            new_coords = self._apply_ratio_lock(x1, y1, x2, y2, 4.0 / 3.0)
            return True, 4.0 / 3.0, new_coords
        elif ratio_type == "3:2":
            self.is_ratio_locked = True
            self.ratio_value = 3.0 / 2.0
            new_coords = self._apply_ratio_lock(x1, y1, x2, y2, 3.0 / 2.0)
            return True, 3.0 / 2.0, new_coords
        elif ratio_type == "1.618":
            self.is_ratio_locked = True
            self.ratio_value = 1.618
            new_coords = self._apply_ratio_lock(x1, y1, x2, y2, 1.618)
            return True, 1.618, new_coords

        return False, None, (x1, y1, x2, y2)

    def _apply_ratio_lock(self, x1: int, y1: int, x2: int, y2: int, ratio: float) -> Tuple[int, int, int, int]:
        """应用比例锁定，调整选框以符合指定比例"""
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if width == 0 or height == 0:
            return (x1, y1, x2, y2)

        # 根据宽度计算新的高度
        new_height = int(width / ratio)

        # 更新Y坐标
        if y2 > y1:
            new_y2 = y1 + new_height
        else:
            new_y2 = y1 - new_height

        return (x1, y1, x2, new_y2)

    def adjust_coords_by_ratio(self, x1: int, y1: int, x2: int, y2: int, drag_handle: str = None) -> Tuple[int, int, int, int]:
        """根据锁定的比例调整坐标

        Args:
            x1, y1, x2, y2: 当前坐标
            drag_handle: 拖拽的句柄类型 ('nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w')

        Returns:
            tuple: 调整后的坐标 (x1, y1, x2, y2)
        """
        if not self.is_ratio_locked or not self.ratio_value:
            return (x1, y1, x2, y2)

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if width == 0 or height == 0:
            return (x1, y1, x2, y2)

        # 根据拖拽的句柄类型调整尺寸
        if drag_handle in ['nw', 'ne', 'sw', 'se']:
            # 角句柄：根据宽度调整高度
            new_height = int(width / self.ratio_value)
            if drag_handle in ['nw', 'sw']:
                y1 = y2 - new_height
            else:
                y2 = y1 + new_height
        elif drag_handle in ['n', 's']:
            # 上下边句柄：根据高度调整宽度
            new_width = int(height * self.ratio_value)
            x2 = x1 + new_width
        elif drag_handle in ['e', 'w']:
            # 左右边句柄：根据宽度调整高度
            new_height = int(width / self.ratio_value)
            y2 = y1 + new_height

        # 确保选框有效（宽度、高度至少为1）
        if abs(x2 - x1) < 1:
            if drag_handle in ['nw', 'w', 'sw']:
                x1 = x2 - 1
            else:
                x2 = x1 + 1
        if abs(y2 - y1) < 1:
            if drag_handle in ['nw', 'n', 'ne']:
                y1 = y2 - 1
            else:
                y2 = y1 + 1

        return (x1, y1, x2, y2)

    def get_current_ratio(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """获取当前选框的比例"""
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if height > 0:
            return width / height
        else:
            return 0.0

    def is_valid_ratio(self, ratio_type: str) -> bool:
        """检查比例类型是否有效"""
        valid_ratios = ["free", "lock_current", "1:1", "16:9", "4:3", "3:2", "1.618"]
        return ratio_type in valid_ratios

    def auto_crop(self, original_image, x1_var, y1_var, x2_var, y2_var, draw_selection_box_func):
        """自动裁剪功能 - 自动检测图片内容并去除空白边缘"""
        messagebox.showerror("错误", "自动裁剪功能已被移除")

    def fit_to_window(self, dialog_instance):
        """适应窗口 - 让图片适应窗口大小"""
        if not hasattr(dialog_instance, 'original_image'):
            messagebox.showinfo("提示", "请先加载图片")
            return

        try:
            # 强制更新 UI 以确保 Canvas 尺寸正确
            dialog_instance.dialog.update_idletasks()
            dialog_instance.canvas.update_idletasks()

            # 获取图片的原始尺寸
            orig_width, orig_height = dialog_instance.original_image.size

            # 获取Canvas的实际尺寸
            canvas_width = dialog_instance.canvas.winfo_width() - 20  # 减去padding
            canvas_height = dialog_instance.canvas.winfo_height() - 20  # 减去padding

            # 确保Canvas有合理的尺寸
            if canvas_width < 100:
                canvas_width = orig_width
            if canvas_height < 100:
                canvas_height = orig_height

            # 计算适应窗口的缩放比例 - 委托给业务逻辑模块
            # 使用本地函数
            scaled_width, scaled_height, fit_scale = calculate_scaled_dimensions(
                orig_width, orig_height, canvas_width, canvas_height, padding=20
            )

            # 更新缩放比例
            dialog_instance.preview_scale = fit_scale
            dialog_instance.display_image()

        except Exception as e:
            messagebox.showerror("错误", f"适应窗口失败: {str(e)}")

    def apply_ratio_lock(self, x1_var, y1_var, x2_var, y2_var, ratio_handler, draw_selection_box_func, update_size_label_func):
        """应用比例锁定，调整选框以符合指定比例"""
        try:
            x1 = int(x1_var.get())
            y1 = int(y1_var.get())
            x2 = int(x2_var.get())
            y2 = int(y2_var.get())

            # 使用比例处理器调整坐标 - 委托给业务逻辑模块
            # 使用本地函数
            new_x1, new_y1, new_x2, new_y2 = apply_aspect_ratio_constraints(
                x1, y1, x2, y2, ratio_handler.ratio_value, "lock_current"
            )

            # 更新坐标
            x1_var.set(str(new_x1))
            y1_var.set(str(new_y1))
            x2_var.set(str(new_x2))
            y2_var.set(str(new_y2))

            # 重绘选框
            draw_selection_box_func()
            update_size_label_func()

        except Exception as e:
            print(f"应用比例锁定失败: {e}")

    def on_ratio_change(self, ratio_var, x1_var, y1_var, x2_var, y2_var, ratio_handler, locked_ratio_label, draw_selection_box_func, update_size_label_func):
        """比例选择变化时的回调"""
        ratio = ratio_var.get()

        try:
            x1 = int(x1_var.get())
            y1 = int(y1_var.get())
            x2 = int(x2_var.get())
            y2 = int(y2_var.get())

            # 使用比例处理器处理比例锁定
            is_locked, ratio_value, new_coords = ratio_handler.lock_ratio(ratio, x1, y1, x2, y2)

            # 更新UI显示
            if locked_ratio_label:
                if ratio_value is not None:
                    locked_ratio_label.config(text=f"({ratio_value:.3f})")
                else:
                    locked_ratio_label.config(text="")

            # 如果锁定了比例，调整当前选框以符合比例
            if is_locked and ratio_value and ratio != "lock_current":
                x1, y1, x2, y2 = new_coords
                x1_var.set(str(x1))
                y1_var.set(str(y1))
                x2_var.set(str(x2))
                y2_var.set(str(y2))
                draw_selection_box_func()
                update_size_label_func()

        except Exception as e:
            messagebox.showerror("错误", f"处理比例失败: {str(e)}")
            ratio_var.set("free")
            if locked_ratio_label:
                locked_ratio_label.config(text="")

    def update_size_label(self, x1_var, y1_var, x2_var, y2_var, size_label):
        """更新实时尺寸显示"""
        # 调用UI操作模块中的函数
        from .ui_operations import update_size_label as ops_update_size_label
        ops_update_size_label(x1_var, y1_var, x2_var, y2_var, size_label)

    def display_reference_image(self, dialog_instance, image_path):
        """显示参考图片（上一帧/下一帧/第一帧）"""
        try:
            # 使用 image_utils 模块加载图片
            from .image_utils import load_image, resize_image, create_photo_image
            ref_img = load_image(image_path)
            if not ref_img:
                print(f"无法加载参考图片: {image_path}")
                return

            # 调整参考图片尺寸与当前图片一致
            if ref_img.size != dialog_instance.original_image.size:
                ref_img = resize_image(ref_img, dialog_instance.original_image.width, dialog_instance.original_image.height)

            # 转换为PhotoImage
            scaled_width = int(dialog_instance.original_image.width * dialog_instance.preview_scale)
            scaled_height = int(dialog_instance.original_image.height * dialog_instance.preview_scale)
            ref_resized = resize_image(ref_img, scaled_width, scaled_height)
            ref_photo = create_photo_image(ref_resized)

            # 清除Canvas并显示参考图片
            dialog_instance.canvas.delete("all")
            dialog_instance.canvas.create_image(dialog_instance.image_x, dialog_instance.image_y, image=ref_photo, anchor="center")

            # 保存引用防止被垃圾回收
            dialog_instance.current_photo = ref_photo

        except Exception as e:
            print(f"无法显示参考图片: {e}")

    def on_mousewheel(self, event, zoom_in_func, zoom_out_func):
        """处理鼠标滚轮事件"""
        # 检查是否按下了 Ctrl 键
        ctrl_pressed = event.state & 0x4  # Ctrl 键的位掩码
        if ctrl_pressed:
            # Ctrl+滚轮：缩放图片
            if event.delta > 0 or event.num == 4:
                # 向上滚动：放大
                zoom_in_func()
            elif event.delta < 0 or event.num == 5:
                # 向下滚动：缩小
                zoom_out_func()
        else:
            # 普通滚轮：滚动查看
            # 检查滚动区域是否大于Canvas可视区域
            scrollregion = event.widget.cget("scrollregion")
            if scrollregion:
                parts = scrollregion.split()
                if len(parts) == 4:
                    scroll_width = float(parts[2])
                    scroll_height = float(parts[3])
                    canvas_width = event.widget.winfo_width()
                    canvas_height = event.widget.winfo_height()

                    # 如果图片的宽度或高度大于Canvas的可视区域，则允许滚动
                    if scroll_width > canvas_width or scroll_height > canvas_height:
                        # 检查操作系统类型来确定滚动方向
                        if event.num == 4 or event.delta > 0:
                            # 向上滚动
                            event.widget.yview_scroll(-1, "units")
                        elif event.num == 5 or event.delta < 0:
                            # 向下滚动
                            event.widget.yview_scroll(1, "units")


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
    from .image_utils import calculate_scale_to_fit

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


