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

    def __init__(self, dialog=None):
        self.is_ratio_locked = False
        self.ratio_value = None
        self.dialog = dialog  # Reference to CropDialog instance

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
        elif ratio_type == "original":
            # 原始比例：使用图片的原始宽高比
            if self.dialog and hasattr(self.dialog, 'original_image'):
                orig_width, orig_height = self.dialog.original_image.size
                if orig_height > 0:
                    original_ratio = orig_width / orig_height
                    self.is_ratio_locked = True
                    self.ratio_value = original_ratio
                    new_coords = self._apply_ratio_lock(x1, y1, x2, y2, original_ratio)
                    return True, original_ratio, new_coords
            return False, None, (x1, y1, x2, y2)
        elif ratio_type == "lock_current":
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

        # 获取图片尺寸（如果有dialog实例）
        img_width, img_height = 0, 0
        if self.dialog and hasattr(self.dialog, 'original_image'):
            img_width, img_height = self.dialog.original_image.size

        # 根据当前选框和比例计算新的尺寸
        if img_width > 0 and img_height > 0:
            # 使用图片尺寸计算最大可能的选框
            if ratio >= 1:
                # 宽大于高，以宽度为基准
                new_width = min(width, img_width)
                new_height = int(new_width / ratio)
                # 如果高度超出，以高度为基准
                if new_height > img_height:
                    new_height = img_height
                    new_width = int(new_height * ratio)
            else:
                # 高大于宽，以高度为基准
                new_height = min(height, img_height)
                new_width = int(new_height * ratio)
                # 如果宽度超出，以宽度为基准
                if new_width > img_width:
                    new_width = img_width
                    new_height = int(new_width / ratio)

            # 保持选框中心点不变
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            new_x1 = max(0, center_x - new_width // 2)
            new_y1 = max(0, center_y - new_height // 2)
            new_x2 = min(img_width, new_x1 + new_width)
            new_y2 = min(img_height, new_y1 + new_height)

            # 如果右边界超出，调整左边界
            if new_x2 > img_width:
                new_x2 = img_width
                new_x1 = max(0, new_x2 - new_width)

            # 如果下边界超出，调整上边界
            if new_y2 > img_height:
                new_y2 = img_height
                new_y1 = max(0, new_y2 - new_height)

            return (new_x1, new_y1, new_x2, new_y2)
        else:
            # 没有图片尺寸信息，简单调整高度
            new_height = int(width / ratio)

            # 调整Y
            if y2 > y1:
                new_y2 = y1 + new_height
            else:
                new_y2 = y1 - new_height

            return (x1, y1, x2, new_y2)

    def adjust_coords_by_ratio(self, x1: int, y1: int, x2: int, y2: int, drag_handle: str = None) -> Tuple[int, int, int, int]:
        """严格比例锁定（闭环逻辑版）"""
        if not self.is_ratio_locked or not self.ratio_value or not drag_handle:
            return x1, y1, x2, y2

        if not self.dialog or not hasattr(self.dialog, "original_image"):
            return x1, y1, x2, y2

        img_w, img_h = self.dialog.original_image.size
        ratio = float(self.ratio_value)

        # 1. 确立唯一锚点 (Anchor)
        # 无论鼠标怎么动，锚点是绝对不动的
        if 'e' in drag_handle: anchor_x = x1
        elif 'w' in drag_handle: anchor_x = x2
        else: anchor_x = x1 # n, s 模式下 x1 不动

        if 's' in drag_handle: anchor_y = y1
        elif 'n' in drag_handle: anchor_y = y2
        else: anchor_y = y1 # e, w 模式下 y1 不动

        # 2. 计算四个方向的物理极限
        dist_to_left = anchor_x
        dist_to_right = img_w - anchor_x
        dist_to_top = anchor_y
        dist_to_bottom = img_h - anchor_y

        # 根据拖拽方向确定可用空间
        can_use_w = dist_to_right if 'e' in drag_handle else dist_to_left if 'w' in drag_handle else img_w
        can_use_h = dist_to_bottom if 's' in drag_handle else dist_to_top if 'n' in drag_handle else img_h

        # 3. 计算在该比例下的"最大可行宽度"
        # 重点：这是此方向下，比例框能达到的绝对物理极限
        max_legal_w = min(can_use_w, can_use_h * ratio)

        # 4. 确定期望宽度 (Desired Width)
        raw_w = abs(x2 - x1)
        raw_h = abs(y2 - y1)

        if drag_handle in ("e", "w"):
            desired_w = raw_w
        elif drag_handle in ("n", "s"):
            desired_w = raw_h * ratio
        else:
            # 角拖拽：选择鼠标移动最远的方向作为驱动轴，增加平滑度
            # 解决"拉不动"或者"比例乱跳"的问题
            if raw_w >= raw_h * ratio:
                desired_w = raw_w
            else:
                desired_w = raw_h * ratio

        # 5. 最终锁定：Clamp
        final_w = min(desired_w, max_legal_w)
        if final_w < 1: final_w = 1 # 最小 1 像素防止消失
        final_h = final_w / ratio

        # 6. 从锚点出发，根据方向生成坐标
        # 水平轴
        if 'e' in drag_handle:
            nx1, nx2 = anchor_x, anchor_x + final_w
        elif 'w' in drag_handle:
            nx1, nx2 = anchor_x - final_w, anchor_x
        else:
            nx1, nx2 = x1, x2

        # 垂直轴
        if 's' in drag_handle:
            ny1, ny2 = anchor_y, anchor_y + final_h
        elif 'n' in drag_handle:
            ny1, ny2 = anchor_y - final_h, anchor_y
        else:
            ny1, ny2 = y1, y2

        # 7. 最后的取整（必须在映射完坐标后统一进行，且不再做二次校验）
        return (int(round(nx1)), int(round(ny1)), int(round(nx2)), int(round(ny2)))

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
        valid_ratios = ["free", "lock_current", "original", "1:1", "16:9", "4:3", "3:2", "1.618"]
        return ratio_type in valid_ratios

    def fit_to_window(self, dialog_instance):
        """适应窗口 - 让图片适应窗口大小"""
        if not hasattr(dialog_instance, 'original_image'):
            messagebox.showinfo("提示", "请先加载图片")
            return

        try:
            #   UI  Canvas 
            dialog_instance.dialog.update_idletasks()
            dialog_instance.canvas.update_idletasks()

            orig_width, orig_height = dialog_instance.original_image.size

            #  Canvas（与display_image保持一致）
            canvas_width = dialog_instance.canvas.winfo_width()
            canvas_height = dialog_instance.canvas.winfo_height()

            #  Canvas
            if canvas_width < 100:
                canvas_width = 800
            if canvas_height < 100:
                canvas_height = 600

            # 直接使用calculate_scale_to_fit，与display_image保持一致
            from .image_utils import calculate_scale_to_fit
            fit_scale = calculate_scale_to_fit(orig_width, orig_height, canvas_width, canvas_height)

            dialog_instance.preview_scale = fit_scale

            # 根据当前显示的图片类型来决定如何重新显示
            if hasattr(dialog_instance, 'current_display_mode') and dialog_instance.current_display_mode != 'original' and dialog_instance.current_reference_path:
                # 如果当前显示的是参考图片，重新显示该参考图片
                self.display_reference_image(dialog_instance, dialog_instance.current_reference_path)
            else:
                # 显示原始图片
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


            new_x1, new_y1, new_x2, new_y2 = apply_aspect_ratio_constraints(
                x1, y1, x2, y2, ratio_handler.ratio_value, "lock_current"
            )

            x1_var.set(str(new_x1))
            y1_var.set(str(new_y1))
            x2_var.set(str(new_x2))
            y2_var.set(str(new_y2))

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

            is_locked, ratio_value, new_coords = ratio_handler.lock_ratio(ratio, x1, y1, x2, y2)

            #  UI
            if locked_ratio_label:
                if ratio_value is not None:
                    locked_ratio_label.config(text=f"({ratio_value:.3f})")
                    locked_ratio_label.update_idletasks()  # 确保立即更新
                else:
                    locked_ratio_label.config(text="")
                    locked_ratio_label.update_idletasks()  # 确保立即更新


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
        #  UI
        from .ui_operations import update_size_label as ops_update_size_label
        ops_update_size_label(x1_var, y1_var, x2_var, y2_var, size_label)

    def display_reference_image(self, dialog_instance, image_path):
        """显示参考图片（上一帧/下一帧/第一帧）"""
        try:
            #   image_utils 
            from .image_utils import load_image, resize_image, create_photo_image
            ref_img = load_image(image_path)
            if not ref_img:
                print(f"无法加载参考图片: {image_path}")
                return

            if ref_img.size != dialog_instance.original_image.size:
                ref_img = resize_image(ref_img, dialog_instance.original_image.width, dialog_instance.original_image.height)

            #  PhotoImage
            scaled_width = int(dialog_instance.original_image.width * dialog_instance.preview_scale)
            scaled_height = int(dialog_instance.original_image.height * dialog_instance.preview_scale)
            ref_resized = resize_image(ref_img, scaled_width, scaled_height)
            ref_photo = create_photo_image(ref_resized)

            #  Canvas
            dialog_instance.canvas.delete("all")
            dialog_instance.canvas.create_image(dialog_instance.image_x, dialog_instance.image_y, image=ref_photo, anchor="center")

            dialog_instance.current_photo = ref_photo

        except Exception as e:
            print(f"无法显示参考图片: {e}")

    def on_mousewheel(self, event, zoom_in_func, zoom_out_func):
        """处理鼠标滚轮事件"""
        #   Ctrl 
        ctrl_pressed = event.state & 0x4  #  Ctrl 
        if ctrl_pressed:
            #  Ctrl+：
            if event.delta > 0 or event.num == 4:

                zoom_in_func()
            elif event.delta < 0 or event.num == 5:

                zoom_out_func()
        else:

            #  Canvas
            scrollregion = event.widget.cget("scrollregion")
            if scrollregion:
                parts = scrollregion.split()
                if len(parts) == 4:
                    scroll_width = float(parts[2])
                    scroll_height = float(parts[3])
                    canvas_width = event.widget.winfo_width()
                    canvas_height = event.widget.winfo_height()

                    #  Canvas，
                    if scroll_width > canvas_width or scroll_height > canvas_height:
                        if event.num == 4 or event.delta > 0:
                            event.widget.yview_scroll(-1, "units")
                        elif event.num == 5 or event.delta < 0:
                            event.widget.yview_scroll(1, "units")


class CropState:
    """裁剪状态管理器"""

    def __init__(self, max_history=100):
        #   {: PIL.Image}
        self.crop_results = {}
        #   {:  (x1, y1, x2, y2)}
        self.crop_coords = {}
        self.history_manager = HistoryManager(max_history=max_history)

    def save_crop_state(self):
        """保存当前裁剪状态到历史记录"""
        state = {
            'crop_results': {},
            'crop_coords': {}
        }

        for img_path, cropped_img in self.crop_results.items():

            if img_path in self.crop_coords:
                state['crop_results'][img_path] = True
                state['crop_coords'][img_path] = self.crop_coords[img_path]

        self.history_manager.save_state(state)

    def undo_crop(self):
        """撤销裁剪操作"""
        if not self.history_manager.can_undo():
            return False

        current_state = {
            'crop_results': {path: True for path in self.crop_results.keys()},
            'crop_coords': self.crop_coords.copy()
        }

        previous_state = self.history_manager.undo(current_state)
        if previous_state:
            self.crop_results.clear()
            self.crop_coords.clear()

            for img_path, coords in previous_state['crop_coords'].items():
                self.crop_coords[img_path] = coords

            return True
        return False

    def redo_crop(self):
        """重做裁剪操作"""
        if not self.history_manager.can_redo():
            return False

        current_state = {
            'crop_results': {path: True for path in self.crop_results.keys()},
            'crop_coords': self.crop_coords.copy()
        }

        next_state = self.history_manager.redo(current_state)
        if next_state:
            self.crop_results.clear()
            self.crop_coords.clear()

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

    scale = calculate_scale_to_fit(orig_width, orig_height, canvas_width - padding, canvas_height - padding)

    scaled_width = int(orig_width * scale)
    scaled_height = int(orig_height * scale)

    return scaled_width, scaled_height, scale


def convert_canvas_to_image_coords(canvas_x, canvas_y, image_x, image_y, preview_scale, image_width, image_height):
    """将画布坐标转换为图片坐标"""
    #  Canvas
    img_left = image_x - image_width // 2
    img_top = image_y - image_height // 2

    orig_x = int((canvas_x - img_left) / preview_scale)
    orig_y = int((canvas_y - img_top) / preview_scale)

    return orig_x, orig_y


def validate_crop_coordinates(x1, y1, x2, y2, img_width, img_height, is_ratio_locked=False):
    """验证裁剪坐标是否有效

    Args:
        is_ratio_locked: 是否启用了比例锁定。启用时不进行强制补位，避免破坏比例
    """
    x1 = max(0, min(x1, img_width))
    y1 = max(0, min(y1, img_height))
    x2 = max(0, min(x2, img_width))
    y2 = max(0, min(y2, img_height))

    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    # 仅在未启用比例锁定时进行最小尺寸补位，避免破坏比例
    if not is_ratio_locked:
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

    if constraint_type in ['nw', 'ne', 'sw', 'se']:

        new_height = int(width / aspect_ratio)
        if constraint_type in ['nw', 'sw']:
            y1 = y2 - new_height
        else:
            y2 = y1 + new_height
    elif constraint_type in ['n', 's']:

        new_width = int(height * aspect_ratio)
        x2 = x1 + new_width
    elif constraint_type in ['e', 'w']:

        new_height = int(width / aspect_ratio)
        y2 = y1 + new_height

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


        if image_paths[current_index] != min_path:
            is_base_image = True
    else:

        current_image_path = image_paths[current_index] if 0 <= current_index < len(image_paths) else image_paths[0] if image_paths else ''

    return is_base_image, current_image_path, current_index


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
    x1 = max(0, min(x1, image.width))
    y1 = max(0, min(y1, image.height))
    x2 = max(x1, min(x2, image.width))
    y2 = max(y1, min(y2, image.height))

    return image.crop((x1, y1, x2, y2))


# 别名，保持向后兼容
CropRatioController = CropRatioHandler


