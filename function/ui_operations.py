"""
UI操作模块
处理UI相关的操作，如浏览输出目录、进入裁剪模式等
"""

from tkinter import filedialog, messagebox
import os


def browse_output(main_window_instance):
    """浏览输出目录"""
    # 获取当前输出路径的目录
    current_dir = os.path.dirname(main_window_instance.output_path.get())
    if not current_dir or not os.path.exists(current_dir):
        current_dir = os.getcwd()

    # 弹出目录选择对话框
    selected_dir = filedialog.askdirectory(
        title="选择输出目录",
        initialdir=current_dir
    )

    if selected_dir:
        # 生成默认的GIF文件名
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"animation_{timestamp}.gif"
        default_path = os.path.join(selected_dir, default_filename)

        # 设置输出路径
        main_window_instance.output_path.set(default_path)


def enter_crop_mode(main_window_instance):
    """
    进入裁剪模式
    打开裁剪对话框，允许用户对当前图片进行裁剪操作
    """
    if not main_window_instance.image_paths:
        messagebox.showwarning("提示", "请先选择图片")
        return

    try:
        from gui.crop_gui import show_crop_dialog

        # 确定要裁剪的图片列表
        if main_window_instance.selected_image_indices and len(main_window_instance.selected_image_indices) > 1:
            # 有多个选中的图片，获取所有选中图片的路径
            target_indices = sorted(main_window_instance.selected_image_indices)
            target_paths = [main_window_instance.image_paths[i] for i in target_indices]

            # 委托给业务逻辑模块寻找最小尺寸图片
            from function.image_utils import find_smallest_image_path
            current_image_path, current_index = find_smallest_image_path(target_paths, main_window_instance.image_paths)
        else:
            # 只有一张选中的图片，使用当前图片
            current_selection = main_window_instance.file_combobox.current()
            if current_selection >= 0 and current_selection < len(main_window_instance.image_paths):
                current_image_path = main_window_instance.image_paths[current_selection]
                current_index = current_selection
                target_paths = [current_image_path]
            else:
                current_image_path = main_window_instance.image_paths[0]
                current_index = 0
                target_paths = [current_image_path]

        # 显示裁剪对话框
        result = show_crop_dialog(
            main_window_instance.root,
            image_path=current_image_path,
            image_paths=target_paths,
            current_index=current_index
        )

        if result:
            # 处理裁剪结果
            if result.get('is_base_image', False):
                # 如果是基准图片模式，应用相同的裁剪坐标到所有图片
                crop_coords = result.get('crop_coords', {})
                
                # 保存裁剪坐标到 pending_crop_coords
                for img_path, coords in crop_coords.items():
                    if img_path in main_window_instance.image_paths:
                        main_window_instance.pending_crop_coords[img_path] = coords
                        main_window_instance.pending_crops.add(img_path)
            else:
                # 单张图片模式，只处理当前图片
                start_pos = result['start']
                end_pos = result['end']
                current_img_path = current_image_path
                
                # 保存裁剪坐标
                main_window_instance.pending_crop_coords[current_img_path] = (
                    start_pos[0], start_pos[1], end_pos[0], end_pos[1]
                )
                main_window_instance.pending_crops.add(current_img_path)

            # 更新界面
            main_window_instance.update_image_list()
            print("裁剪设置已保存")

    except Exception as e:
        messagebox.showerror("错误", f"进入裁剪模式失败:\n{str(e)}")


def update_status_info(main_window_instance):
    """
    更新状态栏信息，显示当前图片信息
    包括当前图片尺寸、文件大小、总时间估算和GIF大小估算
    """
    if main_window_instance.image_paths:
        # 获取当前选中的图片路径
        current_selection = main_window_instance.file_combobox.current()
        if current_selection >= 0 and current_selection < len(main_window_instance.image_paths):
            img_path = main_window_instance.image_paths[current_selection]

            try:
                # 获取图片信息 - 委托给业务逻辑模块
                from function.image_utils import get_image_info
                img_info = get_image_info(img_path)

                # 显示当前图片大小
                current_img_info = f"当前图片: {img_info['width']}x{img_info['height']}px | {img_info['size_kb']:.2f}KB | {img_info['format']}"
                main_window_instance.current_img_size_label.config(text=current_img_info)

                # 计算并显示总时间 - 委托给业务逻辑模块
                from function.image_utils import calculate_total_time
                num_images = len(main_window_instance.image_paths)
                duration_ms = main_window_instance.duration.get()
                total_time_s, total_time_ms = calculate_total_time(num_images, duration_ms)
                main_window_instance.total_time_label.config(text=f"总时间: {total_time_s:.1f}s ({num_images}张 x {duration_ms}ms)")

                # 计算并显示预估GIF大小 - 委托给业务逻辑模块
                from function.image_utils import estimate_gif_size
                estimated_gif_size = estimate_gif_size(main_window_instance.image_paths)
                main_window_instance.gif_size_label.config(text=f"GIF大小: {estimated_gif_size:.2f}KB")

            except Exception as e:
                main_window_instance.current_img_size_label.config(text="当前图片: 无法读取")
                main_window_instance.total_time_label.config(text="总时间: --")
                main_window_instance.gif_size_label.config(text="GIF大小: --")
        else:
            main_window_instance.current_img_size_label.config(text="当前图片: --")
            main_window_instance.total_time_label.config(text="总时间: --")
            main_window_instance.gif_size_label.config(text="GIF大小: --")
    else:
        main_window_instance.current_img_size_label.config(text="当前图片: --")
        main_window_instance.total_time_label.config(text="总时间: --")
        main_window_instance.gif_size_label.config(text="GIF大小: --")

    # 更新缩放倍数显示
    zoom_percent = int(main_window_instance.preview_scale * 100)
    main_window_instance.zoom_label.config(text=f"缩放: {zoom_percent}%")