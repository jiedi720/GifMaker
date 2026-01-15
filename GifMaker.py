#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIF Maker - 将多张图片转换为GIF动画
支持自定义持续时间、循环次数、尺寸调整等功能
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image


def create_gif(image_paths, output_path, duration=100, loop=0, resize=None, optimize=True, progress_callback=None):
    """
    将多张图片创建为GIF动画

    Args:
        image_paths: 图片路径列表
        output_path: 输出GIF文件路径
        duration: 每帧持续时间（毫秒）
        loop: 循环次数（0表示无限循环）
        resize: 调整尺寸，格式为 (width, height) 或 None
        optimize: 是否优化GIF
        progress_callback: 进度回调函数，接受当前进度百分比作为参数
    """
    if not image_paths:
        raise ValueError("至少需要一张图片")

    # 确保输出目录存在
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 加载所有图片
    images = []
    total_images = len(image_paths)
    
    for i, img_path in enumerate(image_paths):
        try:
            img = Image.open(img_path)
            if resize:
                img = img.resize(resize, Image.Resampling.LANCZOS)
            # 确保所有图片使用相同的模式
            if img.mode != 'P':
                img = img.convert('P', palette=Image.Palette.ADAPTIVE)
            images.append(img)
            
            # 更新进度
            if progress_callback:
                progress = int((i + 1) / total_images * 80)  # 使用80%的时间加载图片
                progress_callback(progress)
                
        except Exception as e:
            print(f"警告: 无法加载图片 {img_path}: {e}")
            if progress_callback:
                progress = int((i + 1) / total_images * 80)
                progress_callback(progress)
            continue

    if not images:
        raise ValueError("没有成功加载任何图片")

    # 保存为GIF
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop,
        optimize=optimize
    )
    
    # 完成保存步骤
    if progress_callback:
        progress_callback(100)
        
    print(f"GIF已成功创建: {output_path}")


def get_image_files(directory, pattern="*"):
    """
    获取目录中的所有图片文件

    Args:
        directory: 目录路径
        pattern: 文件名模式（如 "*.png"）

    Returns:
        图片文件路径列表
    """
    extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    dir_path = Path(directory)

    if not dir_path.exists():
        raise ValueError(f"目录不存在: {directory}")

    image_files = []
    for file in sorted(dir_path.glob(pattern)):
        if file.suffix.lower() in extensions:
            image_files.append(str(file))

    return image_files


def main():
    parser = argparse.ArgumentParser(
        description='GIF Maker - 将多张图片转换为GIF动画',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 将指定图片转换为GIF
  python GifMaker.py -i img1.png img2.png img3.png -o output.gif

  # 从目录中读取所有图片
  python GifMaker.py -d ./images -o output.gif

  # 设置每帧持续时间为200毫秒
  python GifMaker.py -i *.png -o output.gif -d 200

  # 调整GIF尺寸为800x600
  python GifMaker.py -i *.png -o output.gif -r 800x600

  # 设置循环次数（0表示无限循环）
  python GifMaker.py -i *.png -o output.gif -l 3
        """
    )

    # 输入选项
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-i', '--images', nargs='+', help='输入图片文件路径（支持多个）')
    input_group.add_argument('-d', '--directory', help='包含图片的目录路径')

    # 输出选项
    parser.add_argument('-o', '--output', required=True, help='输出GIF文件路径')

    # GIF参数
    parser.add_argument('--duration', type=int, default=100,
                        help='每帧持续时间（毫秒），默认: 100')
    parser.add_argument('--loop', type=int, default=0,
                        help='循环次数，0表示无限循环，默认: 0')
    parser.add_argument('--resize', help='调整尺寸，格式: WIDTHxHEIGHT (如 800x600)')
    parser.add_argument('--no-optimize', action='store_true',
                        help='不优化GIF文件')
    parser.add_argument('--pattern', default='*',
                        help='目录模式匹配（当使用 -d 时），默认: *')

    args = parser.parse_args()

    # 处理输入图片
    if args.images:
        image_paths = [str(Path(img).resolve()) for img in args.images]
    else:
        image_paths = get_image_files(args.directory, args.pattern)

    if not image_paths:
        print("错误: 未找到任何图片文件")
        sys.exit(1)

    print(f"找到 {len(image_paths)} 张图片:")
    for img in image_paths:
        print(f"  - {img}")

    # 处理resize参数
    resize = None
    if args.resize:
        try:
            width, height = map(int, args.resize.lower().split('x'))
            resize = (width, height)
        except ValueError:
            print("错误: 尺寸格式不正确，应为 WIDTHxHEIGHT (如 800x600)")
            sys.exit(1)

    # 创建GIF
    try:
        create_gif(
            image_paths=image_paths,
            output_path=args.output,
            duration=args.duration,
            loop=args.loop,
            resize=resize,
            optimize=not args.no_optimize
        )
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # 如果有命令行参数，使用命令行模式；否则启动GUI
    if len(sys.argv) > 1:
        main()
    else:
        # 启动GUI界面
        from gui.main_window import run
        run()