"""
预览功能模块
处理GIF预览和刷新预览功�?"""

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
        messagebox.showwarning("提示", "请先选择至少一张图�?)
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
            messagebox.showerror("错误", "尺寸参数必须是数�?)
            return

    try:
        # 加载所有图片并处理
        frames = []
        duration = main_window_instance.duration.get()

        for img_path in main_window_instance.image_paths:
            try:
                img = Image.open(img_path)

                # 如果需要调整尺�?                if resize:
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

        # 导入预览窗口�?        from gui.preview_gui import GifPreviewWindow

        # 创建预览窗口
        preview_window = GifPreviewWindow(main_window_instance.root, frames, duration, main_window_instance.output_path.get())

    except Exception as e:
        messagebox.showerror("错误", f"预览GIF失败:\n{str(e)}")


def zoom_in_preview(main_window_instance):
    """
    放大预览 - 对所有图片生�?    将预览图片的缩放比例增加25%
    """
    if main_window_instance.preview_scale < 5.0:
        main_window_instance.preview_scale *= 1.25
        main_window_instance.display_grid_preview()


def zoom_out_preview(main_window_instance):
    """
    缩小预览 - 对所有图片生�?    将预览图片的缩放比例减少20%
    """
    if main_window_instance.preview_scale > 0.1:
        main_window_instance.preview_scale /= 1.25
        main_window_instance.display_grid_preview()


def reset_preview_zoom(main_window_instance):
    """
    重置预览缩放 - 让每张图片按原图大小显示
    将预览缩放比例设置为1.0，所有图片按原始尺寸显示
    """
    if not main_window_instance.image_paths:
        return

    # 设置缩放比例�?.0，按原图大小显示
    main_window_instance.preview_scale = 1.0

    # 重新显示网格预览
    main_window_instance.display_grid_preview()


def fit_preview_to_window(main_window_instance):
    """
    让预览图片适应窗口 - 对所有图片生�?    自动调整缩放比例，使所有图片完整显示在预览区域�?    """
    if not main_window_instance.image_paths:
        return

    # 重置缩放比例�?.0，让网格预览自动计算合适的布局
    main_window_instance.preview_scale = 1.0
    main_window_instance.display_grid_preview()


def apply_manual_zoom(main_window_instance, event):
    """
    应用手动输入的缩放�?    从输入框获取缩放百分比并应用到预览图�?
    Args:
        event: 键盘事件对象
    """
    try:
        zoom_value = float(main_window_instance.zoom_entry.get())
        if zoom_value <= 0:
            messagebox.showwarning("警告", "缩放值必须大�?")
            return

        # 将百分比转换为小�?        main_window_instance.preview_scale = zoom_value / 100.0

        # 限制缩放范围
        if main_window_instance.preview_scale < 0.1:  # 10%
            main_window_instance.preview_scale = 0.1
            main_window_instance.zoom_entry.delete(0, 'end')
            main_window_instance.zoom_entry.insert(0, "10")
        elif main_window_instance.preview_scale > 5.0:  # 500%
            main_window_instance.preview_scale = 5.0
            main_window_instance.zoom_entry.delete(0, 'end')
            main_window_instance.zoom_entry.insert(0, "500")

        refresh_preview(main_window_instance)
        from function.ui_operations import update_status_info
        update_status_info(main_window_instance)
    except ValueError:
        messagebox.showerror("错误", "请输入有效的数字")
        # 恢复显示当前缩放�?        main_window_instance.zoom_entry.delete(0, 'end')
        main_window_instance.zoom_entry.insert(0, str(int(main_window_instance.preview_scale * 100)))


def on_preview_canvas_configure(main_window_instance, event):
    """
    当预览canvas大小改变时更新窗口大�?    此方法用于处理Canvas尺寸变化事件

    Args:
        event: Canvas配置事件对象
    """
    # 仅当canvas大小改变时更新滚动区�?    pass  # 滚动区域由display_frame方法管理


def on_preview_mousewheel(main_window_instance, event):
    """
    处理预览区域的鼠标滚轮事�?    支持 Ctrl+滚轮缩放功能
    """
    # 检查是否按下了 Ctrl �?    ctrl_pressed = event.state & 0x4  # Ctrl 键的位掩�?
    if ctrl_pressed:
        # Ctrl+滚轮：缩放图�?        if event.delta > 0 or event.num == 4:
            # 向上滚动：放�?            zoom_in_preview(main_window_instance)
        elif event.delta < 0 or event.num == 5:
            # 向下滚动：缩�?            zoom_out_preview(main_window_instance)
    else:
        # 普通滚轮：滚动查看
        # 检查滚动区域是否大于Canvas可视区域
        scrollregion = main_window_instance.preview_canvas.cget("scrollregion")
        if scrollregion:
            parts = scrollregion.split()
            if len(parts) == 4:
                scroll_width = float(parts[2])
                scroll_height = float(parts[3])
                canvas_width = main_window_instance.preview_canvas.winfo_width()
                canvas_height = main_window_instance.preview_canvas.winfo_height()

                # 如果图片的宽度或高度大于Canvas的可视区域，则允许滚�?                if scroll_width > canvas_width or scroll_height > canvas_height:
                    # 检查操作系统类型来确定滚动方向
                    if event.num == 4 or event.delta > 0:
                        # 向上滚动
                        main_window_instance.preview_canvas.yview_scroll(-1, "units")
                    elif event.num == 5 or event.delta < 0:
                                                # 向下滚动
                                                main_window_instance.preview_canvas.yview_scroll(1, "units")
                    
                    
                    def scroll_to_image(main_window_instance, index):
                        """滚动到指定图片位�?""
                        if index < 0 or index >= len(main_window_instance.image_rects):
                            return
                    
                        rect = main_window_instance.image_rects[index]
                        canvas_width = main_window_instance.preview_canvas.winfo_width()
                        canvas_height = main_window_instance.preview_canvas.winfo_height()
                    
                        # 计算滚动位置，使图片居中显示
                        scroll_x = (rect['x1'] + rect['x2']) / 2 - canvas_width / 2
                        scroll_y = (rect['y1'] + rect['y2']) / 2 - canvas_height / 2
                    
                        # 获取滚动区域
                        scrollregion = main_window_instance.preview_canvas.cget("scrollregion")
                        if scrollregion:
                            parts = scrollregion.split()
                            if len(parts) == 4:
                                max_x = float(parts[2]) - canvas_width
                                max_y = float(parts[3]) - canvas_height
                    
                                # 限制滚动范围
                                scroll_x = max(0, min(scroll_x, max_x))
                                scroll_y = max(0, min(scroll_y, max_y))
                    
                                # 计算滚动比例
                                scrollregion_width = float(parts[2])
                                scrollregion_height = float(parts[3])
                                x_ratio = scroll_x / scrollregion_width if scrollregion_width > 0 else 0
                                y_ratio = scroll_y / scrollregion_height if scrollregion_height > 0 else 0
                    
                                # 执行滚动
                                main_window_instance.preview_canvas.xview_moveto(x_ratio)
                                main_window_instance.preview_canvas.yview_moveto(y_ratio)
