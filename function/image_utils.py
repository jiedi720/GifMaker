# -*- coding: utf-8 -*-
"""
图像处理工具模块
提供图像加载、缩放、裁剪等功能
"""

from PIL import Image, ImageTk
import os


def load_image(image_path):
    """
    加载图片
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        PIL.Image对象，如果加载失败返回None
    """
    try:
        if not os.path.exists(image_path):
            return None
        return Image.open(image_path)
    except Exception as e:
        print(f"无法加载图片 {image_path}: {e}")
        return None


def resize_image(image, width, height, resample=None):
    """
    调整图片大小
    
    Args:
        image: PIL.Image对象
        width: 目标宽度
        height: 目标高度
        resample: 重采样方法，默认自动选择
        
    Returns:
        调整大小后的PIL.Image对象
    """
    if resample is None:
        # 根据缩放方向选择合适的插值算�?        scale = (width * height) / (image.width * image.height)
        resample = Image.Resampling.LANCZOS if scale >= 1.0 else Image.Resampling.BILINEAR
    
    return image.resize((width, height), resample)


def create_photo_image(image):
    """
    创建Tkinter可用的PhotoImage对象
    
    Args:
        image: PIL.Image对象
        
    Returns:
        ImageTk.PhotoImage对象
    """
    return ImageTk.PhotoImage(image)


def calculate_scale_to_fit(image_width, image_height, canvas_width, canvas_height):
    """
    计算让图片适应Canvas的缩放比�?    
    Args:
        image_width: 图片原始宽度
        image_height: 图片原始高度
        canvas_width: Canvas宽度
        canvas_height: Canvas高度
        
    Returns:
        缩放比例
    """
    if canvas_width < 100:
        canvas_width = image_width
    if canvas_height < 100:
        canvas_height = image_height
    
    scale_width = canvas_width / image_width
    scale_height = canvas_height / image_height
    
    return min(scale_width, scale_height)


def calculate_scale_to_fill(image_width, image_height, canvas_width, canvas_height):
    """
    计算让图片填满Canvas的缩放比例（不留白）
    
    Args:
        image_width: 图片原始宽度
        image_height: 图片原始高度
        canvas_width: Canvas宽度
        canvas_height: Canvas高度
        
    Returns:
        缩放比例
    """
    if canvas_width < 100:
        canvas_width = image_width
    if canvas_height < 100:
        canvas_height = image_height
    
    scale_width = canvas_width / image_width
    scale_height = canvas_height / image_height
    
    return max(scale_width, scale_height)


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
    # 确保坐标有效
    x1 = max(0, min(x1, image.width))
    y1 = max(0, min(y1, image.height))
    x2 = max(x1, min(x2, image.width))
    y2 = max(y1, min(y2, image.height))
    
    return image.crop((x1, y1, x2, y2))


def auto_crop_image(image, margin=5, threshold=10):
    """
    自动裁剪功能 - 自动检测图片内容并去除空白边缘

    Args:
        image: PIL.Image对象
        margin: 边距大小（像素）
        threshold: 检测非空白区域的阈�?
    Returns:
        元组 (x1, y1, x2, y2) �?None（如果检测失败）
    """
    try:
        import numpy as np

        # 将图片转换为numpy数组
        img_array = np.array(image)

        # 如果是RGBA，转换为RGB
        if img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]

        # 转换为灰度图
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array

        # 设置阈值，检测非空白区域
        mask = gray > threshold

        # 找到非空白区域的边界
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)

        if not np.any(rows) or not np.any(cols):
            return None

        y1, y2 = np.where(rows)[0][[0, -1]]
        x1, x2 = np.where(cols)[0][[0, -1]]

        # 添加边距
        x1 = max(0, x1 - margin)
        y1 = max(0, y1 - margin)
        x2 = min(image.width, x2 + margin)
        y2 = min(image.height, y2 + margin)

        return (x1, y1, x2, y2)

    except ImportError:
        print("自动裁剪功能需�?numpy �?)
        return None
    except Exception as e:
        print(f"自动裁剪失败: {e}")
        return None


def get_image_info(image_path: str) -> dict:
    """获取图片信息"""
    try:
        img = load_image(image_path)
        if img is None:
            return {
                'width': 0,
                'height': 0,
                'size_kb': 0,
                'format': 'Unknown',
                'mode': 'Unknown',
                'error': 'Failed to load image'
            }

        width, height = img.size
        size_kb = os.path.getsize(image_path) / 1024  # 文件大小，KB
        return {
            'width': width,
            'height': height,
            'size_kb': size_kb,
            'format': img.format,
            'mode': img.mode
        }
    except Exception as e:
        return {
            'width': 0,
            'height': 0,
            'size_kb': 0,
            'format': 'Unknown',
            'mode': 'Unknown',
            'error': str(e)
        }


def find_smallest_image_path(target_paths, all_paths):
    """查找目标路径中尺寸最小的图片"""
    min_size = float('inf')
    current_image_path = target_paths[0]
    current_index = 0

    for i, img_path in enumerate(target_paths):
        try:
            img = load_image(img_path)
            if img:
                width, height = img.size
                size = width * height
                if size < min_size:
                    min_size = size
                    current_image_path = img_path
                    # 查找在all_paths中的索引
                    current_index = all_paths.index(img_path)
        except Exception as e:
            print(f"无法读取图片尺寸 {img_path}: {e}")
            continue

    return current_image_path, current_index


def batch_crop_images(target_paths, x1, y1, x2, y2, pending_crops, pending_crop_coords):
    """批量裁剪图片"""
    success_count = 0
    for img_path in target_paths:
        img = load_image(img_path)
        if img:
            print(f"裁剪图片: {os.path.basename(img_path)}")
            print(f"  目标尺寸: {img.width} x {img.height}")
            print(f"  裁剪坐标: ({x1}, {y1}) �?({x2}, {y2})")
            print(f"  裁剪尺寸: {x2-x1} x {y2-y1}")

            # 直接使用绝对像素坐标进行裁剪
            cropped_img = crop_image(img, x1, y1, x2, y2)

            # 将裁剪后的图片保存在内存�?            pending_crops[img_path] = cropped_img
            # 保存裁剪坐标
            pending_crop_coords[img_path] = (x1, y1, x2, y2)
            success_count += 1

    return success_count


def calculate_grid_layout(image_paths, pending_crops, preview_scale):
    """计算网格布局"""
    from PIL import Image
    import tkinter as tk

    if not image_paths:
        return []

    # 加载所有图片并获取尺寸
    images = []
    max_width = 0
    max_height = 0

    for img_path in image_paths:
        try:
            # 检查是否有待保存的裁剪图片
            if img_path in pending_crops:
                img = pending_crops[img_path]
            else:
                img = load_image(img_path)

            if img:
                width, height = img.size
                images.append({
                    'path': img_path,
                    'original': img,
                    'width': width,
                    'height': height
                })
                max_width = max(max_width, width)
                max_height = max(max_height, height)
        except Exception as e:
            print(f"无法加载图片 {img_path}: {e}")
            continue

    if not images:
        return []

    # 计算合适的缩放比例和列�?    # 假设每张图片缩放后高度不超过200像素（考虑全局缩放比例�?    target_height = 200 * preview_scale
    scale = target_height / max_height

    # 缩放后的图片尺寸
    scaled_width = int(max_width * scale)
    scaled_height = int(max_height * scale)

    # 计算每行可以放多少张图片（考虑间距�?    padding = 10
    # 这里我们假设canvas宽度�?00，实际在GUI层会获取真实宽度
    canvas_width = 800
    cols = max(1, (canvas_width - padding) // (scaled_width + padding))

    # 调整缩放比例以更好地适应屏幕
    if cols > 1:
        available_width = canvas_width - (cols + 1) * padding
        scale = available_width / (cols * max_width)
        scaled_width = int(max_width * scale)
        scaled_height = int(max_height * scale)

    # 计算图片位置
    x = padding
    y = padding
    row_height = 0
    layout_data = []

    for i, img_info in enumerate(images):
        # 为每张图片单独计算缩放尺�?        orig_width, orig_height = img_info['width'], img_info['height']

        # 计算缩放后的尺寸
        img_scaled_width = int(orig_width * scale)
        img_scaled_height = int(orig_height * scale)

        # 添加到布局数据
        layout_data.append({
            'index': i,
            'path': img_info['path'],
            'position': (x, y),
            'size': (img_scaled_width, img_scaled_height)
        })

        # 更新位置
        x += img_scaled_width + padding
        row_height = max(row_height, img_scaled_height)

        # 换行
        if (i + 1) % cols == 0:
            x = padding
            y += row_height + padding
            row_height = 0

    return layout_data


def create_grid_preview(canvas, image_paths, pending_crops, preview_scale, image_rects, preview_photos, selected_index):
    """创建网格预览"""
    from PIL import Image, ImageTk
    import tkinter as tk

    try:
        # 先保存当前选中索引
        current_selection = selected_index

        # 清空预览区域
        canvas.delete("all")
        image_rects.clear()  # 清空位置信息
        preview_photos.clear()  # 清空PhotoImage引用

        # 获取预览Canvas的实际尺�?        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width < 100:
            canvas_width = 800
        if canvas_height < 100:
            canvas_height = 600

        # 加载所有图片并获取尺寸
        images = []
        max_width = 0
        max_height = 0

        for img_path in image_paths:
            try:
                # 检查是否有待保存的裁剪图片
                if img_path in pending_crops:
                    img = pending_crops[img_path]
                else:
                    img = load_image(img_path)

                if img:
                    width, height = img.size
                    images.append({
                        'path': img_path,
                        'original': img,
                        'width': width,
                        'height': height
                    })
                    max_width = max(max_width, width)
                    max_height = max(max_height, height)
            except Exception as e:
                print(f"无法加载图片 {img_path}: {e}")
                continue

        if not images:
            return

        # 计算合适的缩放比例和列�?        # 假设每张图片缩放后高度不超过200像素（考虑全局缩放比例�?        target_height = 200 * preview_scale
        scale = target_height / max_height

        # 缩放后的图片尺寸
        scaled_width = int(max_width * scale)
        scaled_height = int(max_height * scale)

        # 计算每行可以放多少张图片（考虑间距�?        padding = 10
        cols = max(1, (canvas_width - padding) // (scaled_width + padding))

        # 调整缩放比例以更好地适应屏幕
        if cols > 1:
            available_width = canvas_width - (cols + 1) * padding
            scale = available_width / (cols * max_width)
            scaled_width = int(max_width * scale)
            scaled_height = int(max_height * scale)

        # 显示图片
        x = padding
        y = padding
        row_height = 0

        # 保存PhotoImage引用
        photos = []
        rects = []

        for i, img_info in enumerate(images):
            try:
                # 为每张图片单独计算缩放尺�?                img = img_info['original']
                orig_width, orig_height = img_info['width'], img_info['height']

                # 计算缩放后的尺寸
                img_scaled_width = int(orig_width * scale)
                img_scaled_height = int(orig_height * scale)

                # 缩放图片
                if scale >= 1.0:
                    resampling = Image.Resampling.LANCZOS
                else:
                    resampling = Image.Resampling.BILINEAR
                img_resized = img.resize((img_scaled_width, img_scaled_height), resampling)

                # 转换为PhotoImage
                photo = ImageTk.PhotoImage(img_resized)
                photos.append(photo)

                # 在Canvas上绘制图�?                canvas.create_image(x, y, image=photo, anchor=tk.NW, tags=f"image_{i}")

                # 记录图片位置信息
                rect = {
                    'index': i,
                    'x1': x,
                    'y1': y,
                    'x2': x + img_scaled_width,
                    'y2': y + img_scaled_height,
                    'path': img_info['path']
                }
                rects.append(rect)

                # 添加序号标签
                canvas.create_text(
                    x + 5, y + 5,
                    text=f"#{i + 1}",
                    fill="white",
                    font=("Arial", 10, "bold"),
                    anchor=tk.NW,
                    tags=f"label_{i}"
                )

                # 添加文件名标签（不带后缀�?                filename = os.path.splitext(os.path.basename(img_info['path']))[0]

                # 根据图片宽度限制文件名长�?                max_filename_length = max(5, img_scaled_width // 8)  # 每个字符�?像素
                if len(filename) > max_filename_length:
                    filename = filename[:max_filename_length - 3] + "..."

                # 根据图片大小调整字体大小
                font_size = max(7, min(10, img_scaled_height // 15))

                canvas.create_text(
                    x + img_scaled_width - 5, y + 5,
                    text=filename,
                    fill="white",
                    font=("Arial", font_size),
                    anchor=tk.NE,
                    tags=f"filename_{i}"
                )

                # 更新位置
                x += img_scaled_width + padding
                row_height = max(row_height, img_scaled_height)

                # 换行
                if (i + 1) % cols == 0:
                    x = padding
                    y += row_height + padding
                    row_height = 0

            except Exception as e:
                print(f"无法显示图片 {img_info['path']}: {e}")
                continue

        # 更新滚动区域
        # 获取最后一行图片的位置
        if rects:
            last_rect = rects[-1]
            scroll_width = max(canvas_width, last_rect['x2'] + padding)
            scroll_height = last_rect['y2'] + padding
        else:
            scroll_width = canvas_width
            scroll_height = canvas_height

        canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))

        # 检查是否需要水平滚动条
        if scroll_width <= canvas_width:
            # 不需要水平滚动，隐藏水平滚动�?            # 注意：这里不能直接操作滚动条，因为它是GUI组件
            # 实际的滚动条显示/隐藏应该在GUI层处�?            pass
        else:
            # 需要水平滚�?            pass

        # 更新传入的列�?        preview_photos.extend(photos)
        image_rects.extend(rects)

        # 绘制选中�?        if current_selection >= 0 and current_selection < len(rects):
            selected_index = current_selection
            # 注意：这里不能直接调用GUI方法，需要返回选中信息供GUI层处�?
    except Exception as e:
        print(f"网格预览失败: {e}")" " " 
 
 e��`QT��rGm�Y3 ao
 
 �o�R�`e��`QT��rGm\��\i�o�R�`T��qXQ
 
 " " " 
 
 
 
 f r o m   t k i n t e r   i m p o r t   m e s s a g e b o x 
 
 f r o m   f u n c t i o n . i m a g e _ u t i l s   i m p o r t   l o a d _ i m a g e   a s   u t i l s _ l o a d _ i m a g e 
 
 
 
 
 
 d e f   l o a d _ i m a g e ( d i a l o g _ i n s t a n c e ,   i m a g e _ p a t h = N o n e ) : 
 
         " " " T��rGme�gR�XR?Oi�YtX/\i? " " 
 
         i f   n o t   i m a g e _ p a t h : 
 
                 r e t u r n 
 
 
 
         #   cm�de  i m a g e _ u t i l s   �Y3 aoT��rGme�gR�X
 
         d i a l o g _ i n s t a n c e . o r i g i n a l _ i m a g e   =   u t i l s _ l o a d _ i m a g e ( i m a g e _ p a t h ) 
 
         i f   d i a l o g _ i n s t a n c e . o r i g i n a l _ i m a g e : 
 
                 #   �[�T�WǓX[�g  U I   `m? �m? C a n v a s   Op�T���YG� 
 
                 d i a l o g _ i n s t a n c e . d i a l o g . u p d a t e _ i d l e t a s k s ( ) 
 
                 d i a l o g _ i n s t a n c e . c a n v a s . u p d a t e _ i d l e t a s k s ( ) 
 
 
 
                 #   �~
Y�}  C a n v a s   9p}\�SZ�SKq��\ �m�oO^Y?h�W�YG� (��Rf5p?                 d i a l o g _ i n s t a n c e . d i a l o g . a f t e r ( 1 0 0 ,   l a m b d a :   _ d e l a y e d _ f i t _ t o _ w i n d o w ( d i a l o g _ i n s t a n c e ) ) 
 
         e l s e : 
 
                 p r i n t ( f " Ó�rvxT��rGme�gR�X:   { i m a g e _ p a t h } " ) 
 
 
 
 
 
 d e f   _ d e l a y e d _ f i t _ t o _ w i n d o w ( d i a l o g _ i n s t a n c e ) : 
 
         " " " �[�`\~��F?��R?�P2|�~@i[_ĉvx��\ �m? C a n v a s   Op�T��[�S�~��W�o*[�[" " " 
 
         #   cm�deU I T�B%�X�Y3 ao�~��Z~�R"kZ�SKq9p~\�W
 
         f r o m   f u n c t i o n . u i _ h e l p e r s   i m p o r t   e n s u r e _ w i d g e t _ r e n d e r e d 
 
         e n s u r e _ w i d g e t _ r e n d e r e d ( d i a l o g _ i n s t a n c e . c a n v a s ,   l a m b d a :   d i a l o g _ i n s t a n c e . f i t _ t o _ w i n d o w ( ) ) 
 
 
