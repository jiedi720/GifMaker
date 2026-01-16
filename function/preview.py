"""
预览功能模块
处理GIF预览和刷新预览功能
"""

from tkinter import messagebox
from PIL import Image


def refresh_preview(main_window_instance):
    """
    刷新预览
    重新显示网格预览，根据当前窗口大小调整布局
    """
    if main_window_instance.image_paths:
        main_window_instance.display_grid_preview()


def preview_gif(main_window_instance):
    """
    预览GIF动画效果 - 弹出独立窗口
    创建一个独立的窗口来预览GIF动画效果
    """
    if not main_window_instance.image_paths:
        messagebox.showwarning("提示", "请先选择至少一张图片")
        return

    # 处理尺寸调整参数
    resize = None
    if main_window_instance.resize_width.get() and main_window_instance.resize_height.get():
        try:
            width = int(main_window_instance.resize_width.get())
            height = int(main_window_instance.resize_height.get())
            if width > 0 and height > 0:
                resize = (width, height)
            else:
                messagebox.showerror("错误", "尺寸参数必须大于0")
                return
        except ValueError:
            messagebox.showerror("错误", "尺寸参数必须是数字")
            return

    try:
        # 加载所有图片并处理
        frames = []
        duration = main_window_instance.duration.get()

        for img_path in main_window_instance.image_paths:
            try:
                img = Image.open(img_path)

                # 如果需要调整尺寸
                if resize:
                    img = img.resize(resize, Image.Resampling.LANCZOS)

                # 确保所有图片使用相同的模式
                if img.mode != 'P':
                    img = img.convert('P', palette=Image.Palette.ADAPTIVE)

                frames.append(img)
            except Exception as e:
                print(f"警告: 无法加载图片 {img_path}: {e}")
                continue

        if not frames:
            raise ValueError("没有成功加载任何图片")

        # 导入预览窗口类
        from gui.preview_gui import GifPreviewWindow

        # 创建预览窗口
        preview_window = GifPreviewWindow(main_window_instance.root, frames, duration, main_window_instance.output_path.get())

    except Exception as e:
        messagebox.showerror("错误", f"预览GIF失败:\n{str(e)}")