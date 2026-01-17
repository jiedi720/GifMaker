# -*- coding: utf-8 -*-
"""
图像操作模块
处理图像列表的各种操作，如删除、复制、粘贴等
"""

from tkinter import messagebox
import os
import shutil


def select_all_images(main_window_instance, event=None):
    """全选所有图片"""
    if main_window_instance.image_paths:
        main_window_instance.selected_image_indices = set(range(len(main_window_instance.image_paths)))
        main_window_instance.last_selected_index = len(main_window_instance.image_paths) - 1
        main_window_instance.draw_selection_boxes()
        main_window_instance.update_status_info()


def show_image_properties(main_window_instance, index):
    """显示图片属性（支持单张和多张图片）"""
    if not main_window_instance.selected_image_indices:
        return

    try:
        from PIL import Image

        selected_indices = sorted(main_window_instance.selected_image_indices)

        if len(selected_indices) == 1:
            # 单张图片：显示详细属性
            idx = selected_indices[0]
            if idx < 0 or idx >= len(main_window_instance.image_paths):
                return

            img_path = main_window_instance.image_paths[idx]
            img = Image.open(img_path)
            width, height = img.size
            size_kb = os.path.getsize(img_path) / 1024

            info_text = f"""图片属性:

文件名: {os.path.basename(img_path)}
路径: {img_path}
尺寸: {width} x {height} 像素
格式: {img.format}
模式: {img.mode}
文件大小: {size_kb:.2f} KB"""

            messagebox.showinfo("图片属性", info_text)
        else:
            # 多张图片：显示汇总信息
            total_size_kb = 0
            min_width = float('inf')
            min_height = float('inf')
            max_width = 0
            max_height = 0
            formats = set()
            modes = set()

            for idx in selected_indices:
                if idx < 0 or idx >= len(main_window_instance.image_paths):
                    continue

                img_path = main_window_instance.image_paths[idx]
                img = Image.open(img_path)
                width, height = img.size
                size_kb = os.path.getsize(img_path) / 1024

                total_size_kb += size_kb
                min_width = min(min_width, width)
                min_height = min(min_height, height)
                max_width = max(max_width, width)
                max_height = max(max_height, height)
                formats.add(img.format)
                modes.add(img.mode)

            info_text = f"""多张图片属性:

选中数量: {len(selected_indices)} 张
总文件大小: {total_size_kb:.2f} KB
平均文件大小: {total_size_kb / len(selected_indices):.2f} KB

尺寸范围:
  最小: {min_width} x {min_height} 像素
  最大: {max_width} x {max_height} 像素

格式: {', '.join(sorted(formats))}
模式: {', '.join(sorted(modes))}"""

            messagebox.showinfo("图片属性", info_text)

    except Exception as e:
        messagebox.showerror("错误", f"无法读取图片属性: {str(e)}")


def open_image_location(main_window_instance, index):
    """打开图片所在位置"""
    if index < 0 or index >= len(main_window_instance.image_paths):
        return

    try:
        img_path = main_window_instance.image_paths[index]
        import subprocess
        subprocess.Popen(['explorer', '/select,', os.path.abspath(img_path)])
    except Exception as e:
        messagebox.showerror("错误", f"无法打开位置: {str(e)}")


def open_with_default_viewer(main_window_instance, index):
    """用默认图片浏览器打开"""
    if index < 0 or index >= len(main_window_instance.image_paths):
        return

    try:
        img_path = main_window_instance.image_paths[index]
        import subprocess
        if os.name == 'nt':  # Windows
            os.startfile(img_path)
        elif os.name == 'posix':  # macOS/Linux
            subprocess.call(['xdg-open', img_path])
    except Exception as e:
        messagebox.showerror("错误", f"无法打开图片: {str(e)}")


def copy_images(main_window_instance, index):
    """复制选中的图片到剪贴板"""
    if index < 0 or index >= len(main_window_instance.image_paths):
        return

    main_window_instance.clipboard_images = [index]
    main_window_instance.clipboard_action = 'copy'
    print(f"已复制图片 # {index + 1}")


def cut_images(main_window_instance, index):
    """剪切选中的图片到剪贴板"""
    if index < 0 or index >= len(main_window_instance.image_paths):
        return

    main_window_instance.clipboard_images = [index]
    main_window_instance.clipboard_action = 'cut'
    print(f"已剪切图片 # {index + 1}")


def paste_images(main_window_instance, target_index):
    """从剪贴板粘贴图片"""
    if not main_window_instance.clipboard_images or not main_window_instance.clipboard_action:
        messagebox.showinfo("提示", "剪贴板为空")
        return

    if target_index < 0 or target_index >= len(main_window_instance.image_paths):
        return

    try:
        from function.history_manager import save_state as save_main_window_state
        save_main_window_state(main_window_instance)

        paste_indices = main_window_instance.clipboard_images.copy()

        if main_window_instance.clipboard_action == 'copy':

            for i, paste_index in enumerate(paste_indices):
                if paste_index < len(main_window_instance.image_paths):
                    src_path = main_window_instance.image_paths[paste_index]
                    filename = os.path.basename(src_path)
                    name, ext = os.path.splitext(filename)
                    dst_path = os.path.join(os.path.dirname(src_path), f"{name}_copy{ext}")
                    shutil.copy2(src_path, dst_path)

                    insert_pos = target_index + i
                    main_window_instance.image_paths.insert(insert_pos, dst_path)

        elif main_window_instance.clipboard_action == 'cut':


            images_to_move = []
            for paste_index in sorted(paste_indices, reverse=True):
                if paste_index < len(main_window_instance.image_paths):
                    img_path = main_window_instance.image_paths.pop(paste_index)
                    images_to_move.insert(0, img_path)

            for i, img_path in enumerate(images_to_move):
                insert_pos = target_index + i
                main_window_instance.image_paths.insert(insert_pos, img_path)

        main_window_instance.clipboard_images = []
        main_window_instance.clipboard_action = None

        # 更新图片列表显示
        main_window_instance.display_grid_preview()
        print(f"已粘贴图片到位置 # {target_index + 1}")

    except Exception as e:
        messagebox.showerror("错误", f"粘贴失败: {str(e)}")


def delete_images(main_window_instance, index):
    """删除选中的图片"""
    if index < 0 or index >= len(main_window_instance.image_paths):
        return

    img_path = main_window_instance.image_paths[index]
    filename = os.path.basename(img_path)
    result = messagebox.askyesno("确认删除", f"确定要删除图片:\n{filename}?")

    if result:
        try:
            from function.history_manager import save_state as save_main_window_state
            save_main_window_state(main_window_instance)

            del main_window_instance.image_paths[index]

            if main_window_instance.selected_image_index == index:
                main_window_instance.selected_image_index = -1
            elif main_window_instance.selected_image_index > index:
                main_window_instance.selected_image_index -= 1

            # 更新图片列表显示
            main_window_instance.display_grid_preview()
            print(f"已删除图片 # {index + 1}")

        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")