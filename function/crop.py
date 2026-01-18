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
                    # ❌ 不再修改坐标，比例只在拖拽时生效
                    return True, original_ratio, (x1, y1, x2, y2)
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
            # ❌ 不再修改坐标，比例只在拖拽时生效
            return True, 1.0, (x1, y1, x2, y2)
        elif ratio_type == "16:9":
            self.is_ratio_locked = True
            self.ratio_value = 16.0 / 9.0
            # ❌ 不再修改坐标，比例只在拖拽时生效
            return True, 16.0 / 9.0, (x1, y1, x2, y2)
        elif ratio_type == "4:3":
            self.is_ratio_locked = True
            self.ratio_value = 4.0 / 3.0
            # ❌ 不再修改坐标，比例只在拖拽时生效
            return True, 4.0 / 3.0, (x1, y1, x2, y2)
        elif ratio_type == "3:2":
            self.is_ratio_locked = True
            self.ratio_value = 3.0 / 2.0
            # ❌ 不再修改坐标，比例只在拖拽时生效
            return True, 3.0 / 2.0, (x1, y1, x2, y2)
        elif ratio_type == "1.618":
            self.is_ratio_locked = True
            self.ratio_value = 1.618
            # ❌ 不再修改坐标，比例只在拖拽时生效
            return True, 1.618, (x1, y1, x2, y2)

        return False, None, (x1, y1, x2, y2)

    def _apply_ratio_lock(self, x1: int, y1: int, x2: int, y2: int, ratio: float) -> Tuple[int, int, int, int]:
        # ❌ 已废弃：比例由 adjust_coords_by_ratio 统一处理
        return x1, y1, x2, y2

    def adjust_coords_by_ratio(
        self,
        x1: int, y1: int, x2: int, y2: int,
        drag_handle: str = None
    ) -> Tuple[int, int, int, int]:
        """
        严格比例锁定（统一逻辑）
        - 1 套逻辑处理：边缘拖拽 + 角点拖拽
        - 1 个 clamp：保证不超出图片边界
        """

        # 0. 基础校验
        if not self.is_ratio_locked or not self.ratio_value or not drag_handle:
            return x1, y1, x2, y2

        if not self.dialog or not hasattr(self.dialog, "original_image"):
            return x1, y1, x2, y2

        img_w, img_h = self.dialog.original_image.size
        ratio = float(self.ratio_value)

        # 1. 统一坐标方向
        left   = min(x1, x2)
        right  = max(x1, x2)
        top    = min(y1, y2)
        bottom = max(y1, y2)

        # 2. 确定锚点（固定不动）与方向
        if drag_handle == "e":
            ax, ay = left, top
            dx, dy = +1, +1
            drive = "x"
        elif drag_handle == "w":
            ax, ay = right, top
            dx, dy = -1, +1
            drive = "x"
        elif drag_handle == "s":
            ax, ay = left, top
            dx, dy = +1, +1
            drive = "y"
        elif drag_handle == "n":
            ax, ay = left, bottom
            dx, dy = +1, -1
            drive = "y"
        elif drag_handle == "se":
            ax, ay = left, top
            dx, dy = +1, +1
            drive = "corner"
        elif drag_handle == "sw":
            ax, ay = right, top
            dx, dy = -1, +1
            drive = "corner"
        elif drag_handle == "ne":
            ax, ay = left, bottom
            dx, dy = +1, -1
            drive = "corner"
        elif drag_handle == "nw":
            ax, ay = right, bottom
            dx, dy = -1, -1
            drive = "corner"
        else:
            return x1, y1, x2, y2

        # 3. 最大可用空间（以锚点为起点）
        max_w = img_w - ax if dx > 0 else ax
        max_h = img_h - ay if dy > 0 else ay

        # 4. 用户期望尺寸（驱动轴决定）
        raw_w = abs(right - left)
        raw_h = abs(bottom - top)

        if drive == "x":
            desired_w = raw_w
        elif drive == "y":
            desired_w = raw_h * ratio
        else:
            # corner：取变化量最大的轴作为驱动，防止选框缩死
            if raw_w >= raw_h * ratio:
                desired_w = raw_w
            else:
                desired_w = raw_h * ratio

        # 5. clamp（保证不超出图片边界）
        max_legal_w = min(max_w, max_h * ratio)
        final_w = max(1, min(desired_w, max_legal_w))
        final_h = final_w / ratio

        # 6. 从锚点生成新框
        nx1 = ax
        ny1 = ay
        nx2 = ax + dx * final_w
        ny2 = ay + dy * final_h

        # 7. 归一化
        nx1, nx2 = sorted((nx1, nx2))
        ny1, ny2 = sorted((ny1, ny2))

        return int(round(nx1)), int(round(ny1)), int(round(nx2)), int(round(ny2))

    def adjust(self, x1: int, y1: int, x2: int, y2: int, handle="se"):
        """供外部调用，自动判断是否需要锁定"""
        if not self.is_ratio_locked:
            return x1, y1, x2, y2
        return self.adjust_coords_by_ratio(x1, y1, x2, y2, drag_handle=handle)

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

    def apply_ratio_lock(self, *args, **kwargs):
        # ❌ 已废弃，禁止 UI 层修改比例
        return

    def on_ratio_change(self, ratio_var, x1_var, y1_var, x2_var, y2_var, ratio_handler, locked_ratio_label, draw_selection_box_func, update_size_label_func):
        """比例选择变化时的回调"""
        ratio = ratio_var.get()

        try:
            # 获取当前裁剪框的实际坐标
            x1 = int(x1_var.get())
            y1 = int(y1_var.get())
            x2 = int(x2_var.get())
            y2 = int(y2_var.get())

            # 调用 lock_ratio 设置状态
            ratio_handler.lock_ratio(ratio, x1, y1, x2, y2)

            # 更新 UI 显示的比例值
            if locked_ratio_label:
                if ratio_handler.is_ratio_locked and ratio_handler.ratio_value:
                    locked_ratio_label.config(text=f"({ratio_handler.ratio_value:.3f})")
                    locked_ratio_label.update_idletasks()
                else:
                    locked_ratio_label.config(text="")
                    locked_ratio_label.update_idletasks()

            # 如果是预设比例（非 lock_current 和 free），立即调整裁剪框
            if ratio_handler.is_ratio_locked and ratio_handler.ratio_value and ratio not in ["free", "lock_current"]:
                # 获取当前裁剪框的中心点和尺寸
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                current_width = abs(x2 - x1)
                current_height = abs(y2 - y1)
                target_ratio = ratio_handler.ratio_value

                # 根据当前宽度或高度计算新的尺寸（保持较大的那个）
                if current_width >= current_height * target_ratio:
                    # 以宽度为基准
                    new_width = current_width
                    new_height = new_width / target_ratio
                else:
                    # 以高度为基准
                    new_height = current_height
                    new_width = new_height * target_ratio

                # 从中心点计算新的坐标
                new_x1 = max(0, center_x - new_width / 2)
                new_y1 = max(0, center_y - new_height / 2)
                new_x2 = min(ratio_handler.dialog.original_image.width, center_x + new_width / 2)
                new_y2 = min(ratio_handler.dialog.original_image.height, center_y + new_height / 2)

                # 如果边界超出，调整中心点
                if new_x2 > ratio_handler.dialog.original_image.width:
                    new_x2 = ratio_handler.dialog.original_image.width
                    new_x1 = max(0, new_x2 - new_width)
                if new_y2 > ratio_handler.dialog.original_image.height:
                    new_y2 = ratio_handler.dialog.original_image.height
                    new_y1 = max(0, new_y2 - new_height)

                # ⚠️ 修正：必须强制转为整数，并确保 x1 < x2, y1 < y2
                ix1, iy1, ix2, iy2 = int(round(new_x1)), int(round(new_y1)), int(round(new_x2)), int(round(new_y2))

                # 更新变量
                x1_var.set(str(ix1))
                y1_var.set(str(iy1))
                x2_var.set(str(ix2))
                y2_var.set(str(iy2))

                # ⚠️ 关键：强制刷新 UI 变量并重绘
                ratio_handler.dialog.dialog.update_idletasks()  # 确保变量生效
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

    #  （、1）
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


# 已废弃：apply_aspect_ratio_constraints 函数
# 所有比例逻辑现在统一由 CropRatioHandler.adjust_coords_by_ratio() 处理


def determine_crop_strategy(image_paths: List[str], current_index: int) -> Tuple[bool, str, int]:
    """确定裁剪策略

    Returns:
        tuple: (should_crop_all, strategy_type, target_index)
    """
    if not image_paths:
        return False, "none", 0

    if len(image_paths) == 1:
        return False, "single", 0

    # 检查所有图片尺寸是否一致
    first_img = Image.open(image_paths[0])
    first_size = first_img.size

    all_same_size = True
    for path in image_paths[1:]:
        img = Image.open(path)
        if img.size != first_size:
            all_same_size = False
            break

    if all_same_size:
        return True, "all_same", 0
    else:
        # 找到最小尺寸的图片
        min_path, min_index = find_smallest_image_path(image_paths)
        return True, "use_smallest", min_index


def crop_image(image: Image.Image, x1: int, y1: int, x2: int, y2: int) -> Image.Image:
    """裁剪图片

    Args:
        image: PIL.Image 对象
        x1, y1, x2, y2: 裁剪坐标

    Returns:
        PIL.Image: 裁剪后的图片
    """
    # 确保坐标顺序正确
    x1 = min(x1, x2)
    y1 = min(y1, y2)
    x2 = max(x1, x2)
    y2 = max(y1, y2)

    # 确保坐标在图片范围内
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(image.width, x2)
    y2 = min(image.height, y2)

    return image.crop((x1, y1, x2, y2))


# 别名，保持向后兼容
CropRatioController = CropRatioHandler