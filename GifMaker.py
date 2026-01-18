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

# 导入GIF操作函数
from function.gif_operations import create_gif


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
  #  GIF
  python GifMaker.py -i img1.png img2.png img3.png -o output.gif

  python GifMaker.py -d ./images -o output.gif

  #  200
  python GifMaker.py -i *.png -o output.gif -d 200

  #  GIF800x600
  python GifMaker.py -i *.png -o output.gif -r 800x600

  #  （0）
  python GifMaker.py -i *.png -o output.gif -l 3
        """
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-i', '--images', nargs='+', help='输入图片文件路径（支持多个）')
    input_group.add_argument('-d', '--directory', help='包含图片的目录路径')

    parser.add_argument('-o', '--output', required=True, help='输出GIF文件路径')

    #  GIF
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

    #  resize
    resize = None
    if args.resize:
        try:
            width, height = map(int, args.resize.lower().split('x'))
            resize = (width, height)
        except ValueError:
            print("错误: 尺寸格式不正确，应为 WIDTHxHEIGHT (如 800x600)")
            sys.exit(1)

    #  GIF
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
    if len(sys.argv) > 1:
        main()
    else:
        from gui.main_window import run
        run()
        