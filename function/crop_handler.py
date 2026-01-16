# -*- coding: utf-8 -*-
"""
比例锁定处理器模块
处理裁剪过程中根据预设比例实时计算并修正坐标的逻辑
"""

from typing import Tuple, Optional, Any
from tkinter import messagebox
from PIL import Image
from .image_utils import auto_crop_image


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
        if original_image is None:
            messagebox.showinfo("提示", "请先加载图片")
            return

        # 使用 image_utils 模块进行自动裁剪
        crop_coords = auto_crop_image(original_image, margin=5, threshold=10)

        if crop_coords is None:
            messagebox.showerror("错误", "自动裁剪功能需要 numpy 库\n请运行: pip install numpy\n\n或者图片中未检测到有效内容区域")
            return

        try:
            x1, y1, x2, y2 = crop_coords

            # 更新输入框
            x1_var.set(str(x1))
            y1_var.set(str(y1))
            x2_var.set(str(x2))
            y2_var.set(str(y2))

            # 重绘选框
            draw_selection_box_func()

            messagebox.showinfo("自动裁剪", f"已自动检测内容区域:\nX: {x1}, Y: {y1}\n宽度: {x2-x1}, 高度: {y2-y1}")

        except Exception as e:
            messagebox.showerror("错误", f"自动裁剪失败: {str(e)}")

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
            from .crop_logic import calculate_scaled_dimensions
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
            from .crop_logic import apply_aspect_ratio_constraints
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