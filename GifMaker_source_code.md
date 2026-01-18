# GifMaker 源代码整合文档

**生成时间**: 2026-01-18 13:30:57

## 目录

- [build_exe.py](#file-build_exepy)
- [GifMaker.py](#file-gifmakerpy)
- [requirements.txt](#file-requirementstxt)
- [test_adjust_coords.py](#file-test_adjust_coordspy)
- [.trae\documents\Fix _适应窗口_ and _重置缩放_ buttons functionality.md](#file-traedocumentsfix-_适应窗口_-and-_重置缩放_-buttons-functionalitymd)
- [.trae\documents\plan_20260117_032522.md](#file-traedocumentsplan_20260117_032522md)
- [function\crop.py](#file-functioncroppy)
- [function\crop_backup.py](#file-functioncrop_backuppy)
- [function\file_manager.py](#file-functionfile_managerpy)
- [function\history_manager.py](#file-functionhistory_managerpy)
- [function\image_utils.py](#file-functionimage_utilspy)
- [function\list_operations.py](#file-functionlist_operationspy)
- [function\ui_operations.py](#file-functionui_operationspy)
- [function\__init__.py](#file-function__init__py)
- [GitSync\ClearFolder.bat](#file-gitsyncclearfolderbat)
- [GitSync\CloneFromGit.bat](#file-gitsyncclonefromgitbat)
- [GitSync\Update2Git.bat](#file-gitsyncupdate2gitbat)
- [gui\crop_gui.py](#file-guicrop_guipy)
- [gui\gifpreview_gui.py](#file-guigifpreview_guipy)
- [gui\main_window.py](#file-guimain_windowpy)
- [gui\__init__.py](#file-gui__init__py)

---

<a name="file-build_exepy"></a>
## 1. build_exe.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\build_exe.py`

```python
import os
import subprocess
import sys
import shutil
from tqdm import tqdm
import re

def remove_directory(path):
    """彻底删除目录"""
    if os.path.exists(path):
        print(f"[Info] Removing directory: {path}")
        try:
            shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"[Error] Failed to remove {path}: {e}")
            return False
    return True

def move_subfolders(src_dir, dst_dir):
    """将源目录下的所有子文件夹移动到目标目录"""
    if not os.path.exists(src_dir):
        return True
    
    print(f"[Info] Moving subfolders from {src_dir} to {dst_dir}")
    success = True
    
    for item in os.listdir(src_dir):
        item_path = os.path.join(src_dir, item)
        if os.path.isdir(item_path):
            dst_item_path = os.path.join(dst_dir, item)
            
            # 如果目标目录已存在，先删除
            if os.path.exists(dst_item_path):
                if not remove_directory(dst_item_path):
                    success = False
                    continue
            
            try:
                shutil.move(item_path, dst_dir)
                print(f"[Info] Moved: {item} -> {dst_dir}")
            except Exception as e:
                print(f"[Error] Failed to move {item}: {e}")
                success = False
    
    return success

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取当前文件夹名称
    folder_name = os.path.basename(current_dir)
    
    # 构建 spec 文件路径
    spec_file = f"{folder_name}.spec"
    
    print("============================================")
    print(f"  PyInstaller Build Script")
    print("============================================")
    print(f"Current directory: {current_dir}")
    print(f"Folder name: {folder_name}")
    print(f"Spec file: {spec_file}")
    print()
    
    # 检查 spec 文件是否存在
    if not os.path.exists(spec_file):
        print(f"[Error] Spec file '{spec_file}' not found!")
        input("Press Enter to exit...")
        return 1
    
    # 执行打包前的检查
    print("[Info] Pre-build checks...")
    
    # 检查是否同时存在 build 和 dist 文件夹
    build_dir = "build"
    dist_dir = "dist"
    
    if os.path.exists(build_dir) and os.path.exists(dist_dir):
        print(f"[Warning] Found both {build_dir} and {dist_dir} directories!")
        # 1. 彻底删除 build 文件夹
        remove_directory(build_dir)
        # 2. 把 dist 文件夹里的子文件夹移到当前目录
        if move_subfolders(dist_dir, current_dir):
            # 3. 彻底删除 dist 文件夹
            remove_directory(dist_dir)
        print("[Info] Both directories processed. Stopping build.")
        input("Press Enter to exit...")
        return 0
    
    # 检查是否已有 build 文件夹
    if os.path.exists(build_dir):
        print(f"[Warning] Found existing {build_dir} directory!")
        remove_directory(build_dir)
        print("[Info] Build directory removed. Stopping build.")
        input("Press Enter to exit...")
        return 0
    
    # 检查是否已有 dist 文件夹
    if os.path.exists(dist_dir):
        print(f"[Warning] Found existing {dist_dir} directory!")
        # 移动 dist 文件夹里的子文件夹到当前目录
        if move_subfolders(dist_dir, current_dir):
            # 彻底删除 dist 文件夹
            remove_directory(dist_dir)
        print("[Info] Dist directory processed. Stopping build.")
        input("Press Enter to exit...")
        return 0
    
    # 检查 Python 版本
    print("[Info] Checking Python version...")
    python_version = sys.version
    print(f"[Info] Python version: {python_version.strip()}")
    print()
    
    # 检查 requirements.txt 并安装依赖
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        print(f"[Info] Found {requirements_file}, installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
        print()
    else:
        print(f"[Warning] {requirements_file} not found, skipping dependency installation")
        print()
    
    # 执行 PyInstaller 命令
    print(f"[Info] Starting build process with PyInstaller...")
    print(f"[Command] {sys.executable} -m PyInstaller {spec_file}")
    print()
    
    try:
        # 直接执行 PyInstaller 并捕获输出
        cmd_command = [sys.executable, "-m", "PyInstaller", spec_file]
        print(f"[Info] Running: {' '.join(cmd_command)}")
        print("[Info] Showing build progress...")
        print()
        
        # 执行 PyInstaller 并捕获输出
        process = subprocess.Popen(
            cmd_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 进度条配置
        total_steps = 100  # 预估总步骤数
        pbar = tqdm(total=total_steps, desc="Building", unit="steps", ncols=80)
        
        # 读取输出并更新进度条
        step_count = 0
        for line in process.stdout:
            # 显示关键输出信息
            line = line.strip()
            if line:
                # 过滤掉不重要的调试信息
                if any(keyword in line for keyword in ["INFO:", "ERROR:", "WARNING:"]):
                    # 清除进度条，打印信息，然后恢复进度条
                    pbar.clear()
                    print(f"[PyInstaller] {line}")
                    pbar.refresh()
            
            # 更新进度条
            step_count += 1
            pbar.update(1)
            
            # 如果超过预估总步骤，调整进度条
            if step_count > total_steps:
                pbar.total = step_count
                pbar.refresh()
        
        # 等待进程结束
        process.wait()
        pbar.close()
        
        if process.returncode != 0:
            print(f"\n[Error] PyInstaller failed with exit code: {process.returncode}")
            # 清理 __pycache__ 文件夹
            pycache_dir = os.path.join(current_dir, "__pycache__")
            remove_directory(pycache_dir)
            input("Press Enter to exit...")
            return process.returncode
        
        # 打包后的处理
        print("\n[Info] Post-build processing...")
        
        # 1. 彻底删除生成的 build 文件夹
        remove_directory(build_dir)
        
        # 2. 把 dist 文件夹里的子文件夹移到当前目录
        move_subfolders(dist_dir, current_dir)
        
        # 3. 彻底删除 dist 文件夹
        remove_directory(dist_dir)
        
        print("\n[Info] Post-build processing completed!")
        print()
        
        # 显示最终结果
        print("[Info] Build completed successfully!")
        print(f"[Info] Output files are now in the current directory.")
        
        # 移除运行后生成的 __pycache__ 文件夹
        pycache_dir = os.path.join(current_dir, "__pycache__")
        remove_directory(pycache_dir)
        
        return 0
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to start build process: {e}")
        
        # 移除运行后生成的 __pycache__ 文件夹
        pycache_dir = os.path.join(current_dir, "__pycache__")
        remove_directory(pycache_dir)
        
        input("Press Enter to exit...")
        return 1
    except Exception as e:
        print(f"[Error] Unexpected error: {e}")
        
        # 移除运行后生成的 __pycache__ 文件夹
        pycache_dir = os.path.join(current_dir, "__pycache__")
        remove_directory(pycache_dir)
        
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

[回到目录](#目录)

---

<a name="file-gifmakerpy"></a>
## 2. GifMaker.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\GifMaker.py`

```python
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
```

[回到目录](#目录)

---

<a name="file-requirementstxt"></a>
## 3. requirements.txt

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\requirements.txt`

```text
# 图像处理库
Pillow>=10.0.0

# 拖拽功能支持
tkinterdnd2>=0.3.0

# 构建工具依赖
pyinstaller>=6.0.0
```

[回到目录](#目录)

---

<a name="file-test_adjust_coordspy"></a>
## 4. test_adjust_coords.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\test_adjust_coords.py`

```python
# 测试 adjust_coords_by_ratio 函数

from function.crop import CropRatioHandler

# 创建一个测试用的 handler
handler = CropRatioHandler()
handler.is_ratio_locked = True
handler.ratio_value = 16.0 / 9.0  # 16:9 比例

# 测试用例1：拖拽右下角碰到右边界
x1, y1, x2, y2 = 100, 100, 500, 350
print(f"原始坐标: ({x1}, {y1}, {x2}, {y2})")
print(f"原始比例: {(x2 - x1) / (y2 - y1):.2f}")

# 模拟拖拽右下角，x2 超出边界
new_x2 = 800  # 超出边界
new_y2 = 500  # 也会超出边界

result = handler.adjust_coords_by_ratio(x1, y1, new_x2, new_y2, 'se')
print(f"调整后坐标: {result}")
print(f"调整后比例: {(result[2] - result[0]) / (result[3] - result[1]):.2f}")
print()

# 测试用例2：拖拽左边碰到左边界
x1, y1, x2, y2 = 100, 100, 500, 350
print(f"原始坐标: ({x1}, {y1}, {x2}, {y2})")
print(f"原始比例: {(x2 - x1) / (y2 - y1):.2f}")

# 模拟拖拽左边，x1 超出边界
new_x1 = -50  # 超出边界
new_y1 = 50  # 也会超出边界

result = handler.adjust_coords_by_ratio(new_x1, new_y1, x2, y2, 'nw')
print(f"调整后坐标: {result}")
print(f"调整后比例: {(result[2] - result[0]) / (result[3] - result[1]):.2f}")
```

[回到目录](#目录)

---

<a name="file-traedocumentsfix-_适应窗口_-and-_重置缩放_-buttons-functionalitymd"></a>
## 5. .trae\documents\Fix _适应窗口_ and _重置缩放_ buttons functionality.md

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\.trae\documents\Fix _适应窗口_ and _重置缩放_ buttons functionality.md`

```markdown
# 问题分析

1. **"适应窗口"按钮问题**：当前实现基于固定缩略图宽度计算缩放比例，没有考虑图片的实际尺寸，无法确保图片完全显示并充满窗口宽度或高度。

2. **"重置缩放"按钮问题**：尝试调用不存在的`update_single_preview`函数，且未正确处理单张图片预览和网格预览两种模式。

3. **缺少单张图片预览更新函数**：代码中引用了`update_single_preview`，但该函数不存在。

# 修复方案

## 1. 修复`fit_preview_to_window`函数

- 移除基于固定缩略图宽度的计算逻辑
- 针对单张图片预览：计算缩放比例，确保图片完全显示并充满窗口宽度或高度
- 针对网格预览：计算合适的缩放比例，确保图片网格在窗口中合理显示

## 2. 修复`reset_preview_zoom`函数

- 移除对不存在的`update_single_preview`函数的调用
- 针对单张图片预览：调用`preview_specific_image`函数显示原始尺寸
- 针对网格预览：调用`display_grid_preview`函数显示原始尺寸

## 3. 添加缺失的`update_single_preview`函数

- 创建`update_single_preview`函数，用于更新单张图片预览
- 该函数应调用`preview_specific_image`来显示当前选中的图片

# 预期效果

1. **"适应窗口"按钮**：
   - 单张图片：图片将缩放至完全显示，并充满窗口宽度或高度（保持宽高比）
   - 网格预览：图片网格将自适应窗口大小，确保合理显示

2. **"重置缩放"按钮**：
   - 单张图片：显示图片原始尺寸
   - 网格预览：显示图片原始尺寸

3. 所有功能将正确处理单张图片预览和网格预览两种模式

# 修改文件

- `function/preview.py`：修复`fit_preview_to_window`和`reset_preview_zoom`函数，添加`update_single_preview`函数
- 无需修改其他文件

# 实施步骤

1. 修改`function/preview.py`中的`fit_preview_to_window`函数
2. 修改`function/preview.py`中的`reset_preview_zoom`函数
3. 添加`update_single_preview`函数到`function/preview.py`
4. 测试修改后的功能，确保两种模式下都能正常工作
```

[回到目录](#目录)

---

<a name="file-traedocumentsplan_20260117_032522md"></a>
## 6. .trae\documents\plan_20260117_032522.md

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\.trae\documents\plan_20260117_032522.md`

```markdown
# 问题分析

错误信息：`load_image() takes 1 positional argument but 2 were given`

1. **问题根源**：在 `crop_gui.py` 第 87 行，代码错误地调用了 `load_image(self, self.image_path)`，而 `load_image` 函数只接受一个参数 `image_path`

2. **错误原因**：
   - `load_image` 是从 `image_utils` 模块导入的函数，只需要图片路径作为参数
   - 但代码错误地将其当作 `CropDialog` 类的方法调用，传递了 `self` 作为第一个参数

3. **正确逻辑**：
   - `CropDialog` 类需要先加载图片并存储到 `self.original_image` 属性
   - 然后调用 `display_image()` 方法来显示图片

# 修复方案

1. **修复 `CropDialog.__init__` 方法**：
   - 移除错误的 `load_image(self, self.image_path)` 调用
   - 使用正确的方式调用 `load_image` 函数，只传递图片路径
   - 将加载的图片存储到 `self.original_image` 属性
   - 调用 `self.display_image()` 方法显示图片

2. **检查其他相关代码**：确保 `display_image()` 方法能正确处理 `self.original_image` 属性

# 预期效果

1. 修复后，进入裁剪模式时不会再出现 `load_image()` 参数错误
2. 图片会正确加载并显示在裁剪对话框中
3. 裁剪功能可以正常使用

# 修改文件

- `gui/crop_gui.py`：修复 `CropDialog.__init__` 方法中的图片加载逻辑

# 实施步骤

1. 定位到 `crop_gui.py` 第 87 行
2. 移除错误的 `load_image(self, self.image_path)` 调用
3. 添加正确的图片加载代码：
   ```python
   # 正确加载图片
   self.original_image = load_image(self.image_path)
   if self.original_image:
       self.display_image()
   ```
4. 保存修改并测试裁剪功能

# 代码修改预览

**修改前**：
```python
if self.image_path:
    from function.image_utils import load_image
    load_image(self, self.image_path)
```

**修改后**：
```python
if self.image_path:
    from function.image_utils import load_image
    # 正确加载图片
    self.original_image = load_image(self.image_path)
    if self.original_image:
        self.display_image()
```
```

[回到目录](#目录)

---

<a name="file-functioncroppy"></a>
## 7. function\crop.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\function\crop.py`

```python
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
        """锁定比例"""
        if ratio_type == "free":
            self.is_ratio_locked = False
            self.ratio_value = None
            return False, None, (x1, y1, x2, y2)

        # 预设比例映射
        ratios = {
            "original": lambda: self.dialog.original_image.width / self.dialog.original_image.height if self.dialog and hasattr(self.dialog, 'original_image') else None,
            "1:1": lambda: 1.0,
            "16:9": lambda: 16.0 / 9.0,
            "4:3": lambda: 4.0 / 3.0,
            "3:2": lambda: 3.0 / 2.0,
            "1.618": lambda: 1.618,
            "lock_current": lambda: abs(x2 - x1) / abs(y2 - y1) if abs(y2 - y1) > 0 else None
        }

        val_func = ratios.get(ratio_type)
        if val_func:
            val = val_func()
            if val:
                self.is_ratio_locked = True
                self.ratio_value = val
                return True, val, (x1, y1, x2, y2)

        self.is_ratio_locked = False
        return False, None, (x1, y1, x2, y2)

    def _apply_ratio_lock(self, x1: int, y1: int, x2: int, y2: int, ratio: float) -> Tuple[int, int, int, int]:
        # ❌ 已废弃：比例由 adjust_coords_by_ratio 统一处理
        return x1, y1, x2, y2

    def adjust_coords_by_ratio(self, x1, y1, x2, y2, drag_handle) -> Tuple[int, int, int, int]:
        """调整坐标以符合比例锁定"""
        if not drag_handle or not self.ratio_value:
            return x1, y1, x2, y2

        img_w, img_h = self.dialog.original_image.size
        ratio = float(self.ratio_value)

        # 1. 确定锚点 (Anchor)
        # 锚点是拖拽时不动的那一个点
        if drag_handle in ["se", "e", "s"]:
            ax, ay = min(x1, x2), min(y1, y2)
            dx, dy = 1, 1
        elif drag_handle in ["nw", "w", "n"]:
            ax, ay = max(x1, x2), max(y1, y2)
            dx, dy = -1, -1
        elif drag_handle == "ne":
            ax, ay = min(x1, x2), max(y1, y2)
            dx, dy = 1, -1
        elif drag_handle == "sw":
            ax, ay = max(x1, x2), min(y1, y2)
            dx, dy = -1, 1
        else:
            return x1, y1, x2, y2

        # 2. 计算当前拖拽产生的宽高
        cur_w = abs(x2 - x1)
        cur_h = abs(y2 - y1)

        # 3. 核心算法：根据驱动轴计算目标尺寸
        if drag_handle in ["e", "w"]:  # 左右边缘：宽度驱动
            target_w = cur_w
            target_h = target_w / ratio
        elif drag_handle in ["s", "n"]:  # 上下边缘：高度驱动
            target_h = cur_h
            target_w = target_h * ratio
        else:  # 角点：采用"最大覆盖"逻辑，保持平滑拖拽感
            target_w = max(cur_w, cur_h * ratio)
            target_h = target_w / ratio

        # 4. 边界裁剪 (Clamp) - 保证不超出图片
        # 寻找在比例约束下的最大可用宽高
        limit_w = (img_w - ax) if dx > 0 else ax
        limit_h = (img_h - ay) if dy > 0 else ay

        max_possible_w = min(limit_w, limit_h * ratio)

        final_w = min(target_w, max_possible_w)
        final_h = final_w / ratio

        # 5. 生成最终坐标
        nx2 = ax + dx * final_w
        ny2 = ay + dy * final_h

        return int(round(ax)), int(round(ay)), int(round(nx2)), int(round(ny2))

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
                # ⚠️ 修正：调用 adjust 统一逻辑
                # 使用 "se" 作为虚拟 handle，表示从左上角固定往右下角调整
                nx1, ny1, nx2, ny2 = ratio_handler.adjust(x1, y1, x2, y2, handle="se")

                # 更新 UI 变量
                x1_var.set(str(nx1))
                y1_var.set(str(ny1))
                x2_var.set(str(nx2))
                y2_var.set(str(ny2))

                # ⚠️ 必须：先更新标签再重绘
                if locked_ratio_label:
                    locked_ratio_label.config(text=f"({ratio_handler.ratio_value:.3f})" if ratio_handler.is_ratio_locked else "")

                # ⚠️ 关键：触发画布重绘
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
```

[回到目录](#目录)

---

<a name="file-functioncrop_backuppy"></a>
## 8. function\crop_backup.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\function\crop_backup.py`

```python
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



```

[回到目录](#目录)

---

<a name="file-functionfile_managerpy"></a>
## 9. function\file_manager.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\function\file_manager.py`

```python
# -*- coding: utf-8 -*-
"""
文件处理和参数验证模块
提供文件验证、路径处理、文件大小获取、参数验证等功能
"""

import os
from tkinter import filedialog


def validate_image_path(image_path: str) -> bool:
    """验证图片路径是否有效"""
    if not image_path or not os.path.exists(image_path):
        return False

    ext = os.path.splitext(image_path)[1].lower()
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    return ext in valid_extensions


def get_file_size_kb(file_path: str) -> float:
    """获取文件大小（KB）"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / 1024
    return 0.0


def get_image_files(directory: str) -> list:
    """获取目录中的所有图片文件"""
    image_files = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in valid_extensions:
                image_files.append(os.path.join(root, file))

    return sorted(image_files)


def remove_duplicates_preserve_order(items):
    """移除列表中的重复项，保持原有顺序"""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def batch_save_cropped_images(pending_crops):
    """批量保存裁剪后的图片"""
    saved_count = 0
    failed_count = 0

    for img_path, cropped_img in pending_crops.items():
        try:
            cropped_img.save(img_path)
            saved_count += 1
            print(f"已保存裁剪图片: {img_path}")
        except Exception as e:
            failed_count += 1
            print(f"保存图片失败 {img_path}: {str(e)}")

    return saved_count, failed_count


def select_images(main_window_instance):
    """
    选择图片文件
    打开文件选择对话框，让用户选择要制作GIF的图片文件
    选择新图片时会清除已有的图片，只保留新选择的图片
    """

    files = filedialog.askopenfilenames(
        title="选择图片文件",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
            ("All files", "*.*")
        ]
    )
    if files:
        # 清除已有图片，只保留新选择的图片
        main_window_instance.image_paths = list(files)

        # 重置选择状态
        main_window_instance.selected_image_indices = set()
        main_window_instance.selected_image_index = -1
        main_window_instance.last_selected_index = -1
        main_window_instance.pending_crops = {}
        main_window_instance.pending_crop_coords = {}

        # 使用适应窗口模式
        from function.preview import fit_preview_to_window
        fit_preview_to_window(main_window_instance)


def select_directory(main_window_instance):
    """
    选择包含图片的目录
    打开目录选择对话框，自动获取目录中所有图片文件
    选择新目录时会清除已有的图片，只保留新选择的图片
    """
    directory = filedialog.askdirectory(title="选择包含图片的目录")
    if directory:
        # 获取目录中的图片文件
        image_files = get_image_files(directory)

        if image_files:
            # 清除已有图片，只保留新选择的图片
            main_window_instance.image_paths = image_files

            # 重置选择状态
            main_window_instance.selected_image_indices = set()
            main_window_instance.selected_image_index = -1
            main_window_instance.last_selected_index = -1
            main_window_instance.pending_crops = {}
            main_window_instance.pending_crop_coords = {}

            # 使用适应窗口模式
            from function.preview import fit_preview_to_window
            fit_preview_to_window(main_window_instance)

def clear_images(main_window_instance):
    """
    清空图片列表
    清除所有已选择的图片路径
    """
    main_window_instance.image_paths = []
    main_window_instance.selected_image_indices = set()
    main_window_instance.selected_image_index = -1
    main_window_instance.last_selected_index = -1
    main_window_instance.pending_crops = {}
    main_window_instance.pending_crop_coords = {}
    main_window_instance.preview_scale = 1.0
    main_window_instance.display_grid_preview()




def calculate_total_time(num_images: int, duration_ms: int) -> tuple:
    """计算GIF总时间"""
    total_time_ms = num_images * duration_ms
    total_time_s = total_time_ms / 1000
    return total_time_s, total_time_ms


def validate_gif_params(image_paths, output_path, resize_width, resize_height):
    """验证GIF参数"""
    if not image_paths:
        return False, "请先选择至少一张图片"

    if not output_path:
        return False, "请选择输出文件路径"

    if resize_width and resize_height:
        try:
            width = int(resize_width)
            height = int(resize_height)
            if width <= 0 or height <= 0:
                return False, "尺寸参数必须大于0"
        except ValueError:
            return False, "尺寸参数必须是数字"

    return True, ""


def estimate_gif_size(image_paths: list) -> float:
    """估算GIF大小"""
    total_original_size = sum(os.path.getsize(path)/1024 for path in image_paths)  # KB
    estimated_gif_size = total_original_size * 0.3  #  30%
    return estimated_gif_size


def is_single_image_mode(image_paths: list) -> bool:
    """判断是否为单张图片模式

    Args:
        image_paths: 图片路径列表

    Returns:
        bool: 是否为单张图片模式
    """
    return len(image_paths) <= 1


def get_target_paths(selected_indices: set, all_paths: list) -> list:
    """获取目标路径列表

    Args:
        selected_indices: 选中的索引集合
        all_paths: 所有路径列表

    Returns:
        list: 目标路径列表
    """
    if selected_indices and len(selected_indices) > 1:
        target_indices = sorted(list(selected_indices))
        return [all_paths[i] for i in target_indices if 0 <= i < len(all_paths)]
    else:
        if selected_indices:
            idx = list(selected_indices)[0]
            if 0 <= idx < len(all_paths):
                return [all_paths[idx]]
        return []
```

[回到目录](#目录)

---

<a name="file-functionhistory_managerpy"></a>
## 10. function\history_manager.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\function\history_manager.py`

```python
# -*- coding: utf-8 -*-
"""
历史管理模块
提供撤销/重做功能，支持无限次操作历史
"""

import copy
import os
from typing import Any, Dict, List, Optional
from tkinter import messagebox


class HistoryManager:
    """历史管理器类，支持撤销和重做操作"""

    def __init__(self, max_history: int = 100):
        """
        初始化历史管理器
        Args:
            max_history: 最大历史记录数量，默认为100
        """
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self.max_history = max_history

    def save_state(self, state: Dict[str, Any]) -> None:
        """
        保存当前状态到撤销栈
        Args:
            state: 要保存的状态字典
        """
        # 深拷贝状态，避免引用问题
        state_copy = copy.deepcopy(state)
        self.undo_stack.append(state_copy)

        # 如果超过最大历史记录数，移除最早的记录
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        # 清空重做栈，因为新的操作会使重做历史失效
        self.redo_stack.clear()

    def undo(self, current_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        执行撤销操作
        Args:
            current_state: 当前状态
        Returns:
            上一个状态，如果没有可撤销的操作则返回None
        """
        if not self.undo_stack:
            return None

        # 将当前状态保存到重做栈
        current_copy = copy.deepcopy(current_state)
        self.redo_stack.append(current_copy)

        # 从撤销栈中弹出上一个状态
        previous_state = self.undo_stack.pop()
        return previous_state

    def redo(self, current_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        执行重做操作
        Args:
            current_state: 当前状态
        Returns:
            下一个状态，如果没有可重做的操作则返回None
        """
        if not self.redo_stack:
            return None

        # 将当前状态保存到撤销栈
        current_copy = copy.deepcopy(current_state)
        self.undo_stack.append(current_copy)

        # 从重做栈中弹出下一个状态
        next_state = self.redo_stack.pop()
        return next_state

    def can_undo(self) -> bool:
        """
        检查是否可以撤销
        Returns:
            如果可以撤销返回True，否则返回False
        """
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """
        检查是否可以重做
        Returns:
            如果可以重做返回True，否则返回False
        """
        return len(self.redo_stack) > 0

    def clear(self) -> None:
        """清空所有历史记录"""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def get_undo_count(self) -> int:
        """
        获取可撤销的次数
        Returns:
            可撤销的次数
        """
        return len(self.undo_stack)

    def get_redo_count(self) -> int:
        """
        获取可重做的次数
        Returns:
            可重做的次数
        """
        return len(self.redo_stack)


class UndoRedoManager:
    """撤销/重做管理器"""

    def __init__(self, max_steps: int = 50):
        """
        初始化撤销/重做管理器
        Args:
            max_steps: 最大历史记录步数
        """
        self.undo_stack = []  # 撤销栈
        self.redo_stack = []  # 重做栈
        self.max_steps = max_steps

    def save_state(self, state):
        """
        保存当前状态
        Args:
            state: 要保存的状态
        """
        self.undo_stack.append(state.copy())
        if len(self.undo_stack) > self.max_steps:
            self.undo_stack.pop(0)  # 移除最早的记录
        # 新操作会清空重做栈
        self.redo_stack.clear()

    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return len(self.redo_stack) > 0

    def undo(self, current_state):
        """
        执行撤销操作
        Args:
            current_state: 当前状态
        Returns:
            上一个状态，如果没有可撤销的操作则返回None
        """
        if not self.can_undo():
            return None

        # 将当前状态保存到重做栈
        self.redo_stack.append(current_state.copy())

        # 从撤销栈中弹出上一个状态
        return self.undo_stack.pop()

    def redo(self, current_state):
        """
        执行重做操作
        Args:
            current_state: 当前状态
        Returns:
            下一个状态，如果没有可重做的操作则返回None
        """
        if not self.can_redo():
            return None

        # 将当前状态保存到撤销栈
        self.undo_stack.append(current_state.copy())

        # 从重做栈中弹出下一个状态
        return self.redo_stack.pop()


def save_crop_state(crop_state_obj):
    """
    保存当前裁剪状态到历史记录
    Args:
        crop_state_obj: 裁剪状态对象
    """
    crop_state_obj.save_crop_state()
    print(f"已保存裁剪状态，可撤销次数: {crop_state_obj.history_manager.get_undo_count()}")


def undo_crop(crop_state_obj):
    """
    撤销裁剪操作
    Args:
        crop_state_obj: 裁剪状态对象
    """
    if crop_state_obj.undo_crop():
        print(f"已撤销裁剪操作，可重做次数: {crop_state_obj.history_manager.get_redo_count()}")
        messagebox.showinfo("撤销", "已撤销裁剪操作")
    else:
        messagebox.showinfo("提示", "没有可撤销的操作")


def redo_crop(crop_state_obj):
    """
    重做裁剪操作
    Args:
        crop_state_obj: 裁剪状态对象
    """
    if crop_state_obj.redo_crop():
        print(f"已重做裁剪操作，可撤销次数: {crop_state_obj.history_manager.get_undo_count()}")
        messagebox.showinfo("重做", "已重做裁剪操作")
    else:
        messagebox.showinfo("提示", "没有可重做的操作")


def save_state(main_window_instance, backup_images=False):
    """
    保存当前状态到历史栈
    Args:
        main_window_instance: 主窗口实例
        backup_images: 是否备份图片
    """
    # 深拷贝图片路径列表
    current_state = copy.deepcopy(main_window_instance.image_paths)
    state_data = {
        'image_paths': current_state,
        'pending_crops': {}  # 保存待保存的裁剪信息
    }

    # 保存待保存的裁剪信息
    if main_window_instance.pending_crops:
        state_data['pending_crops'] = {}
        for img_path in main_window_instance.pending_crops.keys():
            if img_path in main_window_instance.pending_crop_coords:
                state_data['pending_crops'][img_path] = {
                    'coords': main_window_instance.pending_crop_coords[img_path]
                }
            else:
                # 没有裁剪坐标信息，保存空字典
                state_data['pending_crops'][img_path] = {}

    main_window_instance.history_manager.save_state(state_data)


def undo(main_window_instance):
    """
    撤销操作
    Args:
        main_window_instance: 主窗口实例
    """
    print(f"撤销: 开始撤销操作")
    print(f"  当前 pending_crops 数量: {len(main_window_instance.pending_crops)}")
    print(f"  当前 pending_crop_coords 数量: {len(main_window_instance.pending_crop_coords)}")
    print(f"  当前 image_paths 数量: {len(main_window_instance.image_paths)}")
    print(f"  可以撤销: {main_window_instance.history_manager.can_undo()}")
    print(f"  撤销栈深度: {main_window_instance.history_manager.get_undo_count()}")
    
    if not main_window_instance.history_manager.can_undo():
        messagebox.showinfo("提示", "没有可撤销的操作")
        return

    # 深拷贝当前状态到重做栈
    current_state = copy.deepcopy(main_window_instance.image_paths)
    redo_state = {
        'image_paths': current_state,
        'pending_crops': {}  # 保存待保存的裁剪信息
    }

    # 保存待保存的裁剪信息
    if main_window_instance.pending_crops:
        redo_state['pending_crops'] = {}
        for img_path in main_window_instance.pending_crops.keys():
            if img_path in main_window_instance.pending_crop_coords:
                redo_state['pending_crops'][img_path] = {
                    'coords': main_window_instance.pending_crop_coords[img_path]
                }
            else:
                # 没有裁剪坐标信息，保存空字典
                redo_state['pending_crops'][img_path] = {}

    # 从历史管理器获取上一个状态
    previous_state = main_window_instance.history_manager.undo(redo_state)
    if previous_state:
        # 恢复上一个状态
        if 'image_paths' in previous_state:
            main_window_instance.image_paths = previous_state['image_paths']

            # 恢复待保存的裁剪信息
            if 'pending_crops' in previous_state:
                print(f"撤销: 恢复 pending_crops")
                print(f"  当前 pending_crops: {list(main_window_instance.pending_crops.keys())}")
                print(f"  目标 pending_crops: {list(previous_state['pending_crops'].keys())}")

                # 清除previous_state中不存在的裁剪
                current_pending = set(main_window_instance.pending_crops.keys())
                previous_pending = set(previous_state['pending_crops'].keys())
                to_remove = current_pending - previous_pending
                for img_path in to_remove:
                    if img_path in main_window_instance.pending_crops:
                        del main_window_instance.pending_crops[img_path]
                        print(f"已清除待保存的裁剪: {img_path}")
                    if img_path in main_window_instance.pending_crop_coords:
                        del main_window_instance.pending_crop_coords[img_path]

                # 添加previous_state中存在的裁剪
                to_add = previous_pending - current_pending
                print(f"  需要添加的裁剪: {list(to_add)}")
                for img_path in to_add:
                    # 重新加载图片并应用裁剪
                    from function.image_utils import load_image
                    from function.crop import crop_image
                    img = load_image(img_path)
                    if img and img_path in previous_state['pending_crops']:
                        crop_data = previous_state['pending_crops'][img_path]
                        print(f"  裁剪数据: {crop_data}")
                        # 检查crop_data格式
                        if isinstance(crop_data, dict) and 'coords' in crop_data:
                            x1, y1, x2, y2 = crop_data['coords']
                            print(f"  应用裁剪坐标: ({x1}, {y1}, {x2}, {y2})")
                            cropped_img = crop_image(img, x1, y1, x2, y2)
                            main_window_instance.pending_crops[img_path] = cropped_img
                            main_window_instance.pending_crop_coords[img_path] = (x1, y1, x2, y2)
                            print(f"已恢复待保存的裁剪: {img_path}")
                        else:
                            print(f"  警告: 裁剪数据格式不正确: {crop_data}")
        else:
            # 兼容旧版本（没有pending_crops字段）
            main_window_instance.image_paths = previous_state
            # 清空待保存的裁剪
            main_window_instance.pending_crops.clear()
            main_window_instance.pending_crop_coords.clear()

        # 更新UI（使用update_image_positions避免闪烁）
        main_window_instance.update_image_positions()
        print("已撤销操作")


def save_pending_crops(main_window_instance):
    """
    保存所有待保存的裁剪图片
    Args:
        main_window_instance: 主窗口实例
    """
    if not main_window_instance.pending_crops:
        messagebox.showinfo("提示", "没有待保存的裁剪图片")
        return

    from function.file_manager import batch_save_cropped_images
    saved_count, failed_count = batch_save_cropped_images(main_window_instance.pending_crops)

    if saved_count > 0:
        main_window_instance.pending_crops.clear()
        main_window_instance.pending_crop_coords.clear()
        main_window_instance.display_grid_preview()

        if failed_count > 0:
            messagebox.showwarning("保存完成", f"成功保存 {saved_count} 张图片，失败 {failed_count} 张图片")
        else:
            messagebox.showinfo("保存完成", f"成功保存 {saved_count} 张裁剪图片")
    else:
        messagebox.showerror("错误", "保存图片失败")


def on_window_close(main_window_instance):
    """
    窗口关闭事件处理
    Args:
        main_window_instance: 主窗口实例
    """
    if main_window_instance.pending_crops:
        result = messagebox.askyesnocancel(
            "保存更改",
            f"{len(main_window_instance.pending_crops)} 张图片已裁剪但未保存。\n\n是否保存这些更改？",
            icon=messagebox.WARNING
        )

        if result is True:
            # 保存所有待保存的裁剪图片
            for img_path, cropped_img in main_window_instance.pending_crops.items():
                try:
                    cropped_img.save(img_path)
                    print(f"已保存裁剪图 {img_path}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存图片失败 {img_path}: {str(e)}")
            main_window_instance.pending_crops.clear()
            main_window_instance.root.destroy()
        elif result is False:
            # 不保存，直接关闭
            main_window_instance.pending_crops.clear()
            main_window_instance.root.destroy()
        # result is None，用户点击了"取消"，不关闭窗口
    else:
        # 没有待保存的更改，直接关闭窗口
        main_window_instance.root.destroy()


def redo(main_window_instance):
    """
    重做操作
    Args:
        main_window_instance: 主窗口实例
    """
    if not main_window_instance.history_manager.can_redo():
        messagebox.showinfo("提示", "没有可重做的操作")
        return

    # 深拷贝当前状态到撤销栈
    import shutil
    current_state = copy.deepcopy(main_window_instance.image_paths)
    undo_state = {
        'image_paths': current_state,
        'backup_files': [],
        'pending_crops': {}  # 保存待保存的裁剪信息
    }

    # 保存待保存的裁剪信息
    if main_window_instance.pending_crops:
        undo_state['pending_crops'] = {}
        for img_path in main_window_instance.pending_crops.keys():
            if img_path in main_window_instance.pending_crop_coords:
                undo_state['pending_crops'][img_path] = {
                    'coords': main_window_instance.pending_crop_coords[img_path]
                }
            else:
                # 没有裁剪坐标信息，保存空字典
                undo_state['pending_crops'][img_path] = {}

    # 处理备份文件（如果有）
    if hasattr(main_window_instance, 'undo_stack') and main_window_instance.undo_stack and 'backup_files' in main_window_instance.undo_stack[-1]:
        for backup_info in main_window_instance.undo_stack[-1]['backup_files']:
            try:
                # 创建重做备份
                backup_filename = f"redo_backup_{os.path.basename(backup_info['original'])}"
                temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                backup_path = os.path.join(temp_dir, backup_filename)
                shutil.copy2(backup_info['original'], backup_path)
                undo_state['backup_files'].append({
                    'original': backup_info['original'],
                    'backup': backup_path
                })
            except Exception as e:
                print(f"创建重做备份失败 {backup_info['original']}: {e}")

    # 从历史管理器获取下一个状态
    next_state = main_window_instance.history_manager.redo(undo_state)
    if next_state:
        # 恢复下一个状态
        if 'image_paths' in next_state:
            main_window_instance.image_paths = next_state['image_paths']

            # 恢复待保存的裁剪信息
            if 'pending_crops' in next_state:
                print(f"重做: 恢复 pending_crops")
                print(f"  当前 pending_crops: {list(main_window_instance.pending_crops.keys())}")
                print(f"  目标 pending_crops: {list(next_state['pending_crops'].keys())}")

                # 清除next_state中不存在的裁剪
                current_pending = set(main_window_instance.pending_crops.keys())
                next_pending = set(next_state['pending_crops'].keys())
                to_remove = current_pending - next_pending
                for img_path in to_remove:
                    if img_path in main_window_instance.pending_crops:
                        del main_window_instance.pending_crops[img_path]
                        print(f"已清除待保存的裁剪: {img_path}")

                # 添加next_state中存在的裁剪
                to_add = next_pending - current_pending
                print(f"  需要添加的裁剪: {list(to_add)}")
                for img_path in to_add:
                    # 重新加载图片并应用裁剪
                    from function.image_utils import load_image
                    from function.crop import crop_image
                    img = load_image(img_path)
                    if img and img_path in next_state['pending_crops']:
                        crop_data = next_state['pending_crops'][img_path]
                        print(f"  裁剪数据: {crop_data}")
                        # 检查crop_data格式
                        if isinstance(crop_data, dict) and 'coords' in crop_data:
                            x1, y1, x2, y2 = crop_data['coords']
                            print(f"  应用裁剪坐标: ({x1}, {y1}, {x2}, {y2})")
                            cropped_img = crop_image(img, x1, y1, x2, y2)
                            main_window_instance.pending_crops[img_path] = cropped_img
                            main_window_instance.pending_crop_coords[img_path] = (x1, y1, x2, y2)
                            print(f"已恢复待保存的裁剪: {img_path}")
                        else:
                            print(f"  警告: 裁剪数据格式不正确: {crop_data}")
        else:
            # 兼容旧版本（没有pending_crops字段）
            main_window_instance.image_paths = next_state
            # 清空待保存的裁剪
            main_window_instance.pending_crops.clear()

        # 更新UI（使用update_image_positions避免闪烁）
        main_window_instance.update_image_positions()

```

[回到目录](#目录)

---

<a name="file-functionimage_utilspy"></a>
## 11. function\image_utils.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\function\image_utils.py`

```python
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
        scale = (width * height) / (image.width * image.height)
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
    计算让图片适应Canvas的缩放比例

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





def get_image_info(image_path):
    """
    获取图片信息

    Args:
        image_path: 图片文件路径

    Returns:
        包含图片信息的字典，格式为:
        {
            'width': 宽度,
            'height': 高度,
            'size_kb': 文件大小(KB),
            'format': 图片格式,
            'mode': 图片模式
        }
        如果加载失败返回None
    """
    try:
        if not os.path.exists(image_path):
            return None

        img = Image.open(image_path)
        file_size = os.path.getsize(image_path) / 1024  # 转换为KB

        return {
            'width': img.width,
            'height': img.height,
            'size_kb': file_size,
            'format': img.format,
            'mode': img.mode
        }
    except Exception as e:
        print(f"无法获取图片信息 {image_path}: {e}")
        return None


def calculate_grid_layout(image_paths, pending_crops, preview_scale=1.0, thumbnail_size=(200, 150), canvas_width=None, canvas_height=None):
    """
    计算网格布局，返回每张图片的位置和大小

    Args:
        image_paths: 图片路径列表
        pending_crops: 待裁剪的图片集合
        preview_scale: 预览缩放比例
        thumbnail_size: 缩略图大小 (width, height) - 仅在 preview_scale=1.0 且图片尺寸未知时使用
        canvas_width: Canvas宽度（可选，默认800）
        canvas_height: Canvas高度（可选，默认600）

    Returns:
        包含布局信息的字典列表，每个字典包含:
        {
            'index': 图片索引,
            'path': 图片路径,
            'position': (x, y) 坐标元组,
            'size': (width, height) 尺寸元组,
            'col': 列索引,
            'row': 行索引,
            'is_cropped': 是否已裁剪
        }
    """
    if not image_paths:
        return []

    # 使用传入的Canvas尺寸或默认值
    if canvas_width is None:
        canvas_width = 800
    if canvas_height is None:
        canvas_height = 600

    # 加载所有图片获取实际尺寸
    image_sizes = []
    for img_path in image_paths:
        img = load_image(img_path)
        if img:
            image_sizes.append((img.width, img.height))
        else:
            # 如果加载失败，使用默认尺寸
            image_sizes.append((200, 150))

    # 计算每张图片的显示尺寸
    display_sizes = []
    for i, (img_width, img_height) in enumerate(image_sizes):
        if preview_scale == 1.0:
            # 原始大小模式：使用图片的实际尺寸
            display_sizes.append((img_width, img_height))
        else:
            # 缩放模式：根据图片实际尺寸计算缩放后的尺寸
            display_sizes.append((
                int(img_width * preview_scale),
                int(img_height * preview_scale)
            ))

    padding = 10
    
    # 计算列数：基于所有图片的平均宽度
    if display_sizes:
        avg_width = sum(size[0] for size in display_sizes) / len(display_sizes)
        avg_height = sum(size[1] for size in display_sizes) / len(display_sizes)
    else:
        avg_width = 200
        avg_height = 150
    
    cols = max(1, int(canvas_width / (avg_width + padding)))
    rows = (len(image_paths) + cols - 1) // cols

    # 计算每列的最大宽度和每行的最大高度
    col_widths = [0] * cols
    row_heights = [0] * rows
    
    for i, img_path in enumerate(image_paths):
        col = i % cols
        row = i // cols
        width, height = display_sizes[i]
        col_widths[col] = max(col_widths[col], width)
        row_heights[row] = max(row_heights[row], height)

    # 计算每列和每行的起始位置
    col_positions = [padding]
    for i in range(1, cols):
        col_positions.append(col_positions[-1] + col_widths[i-1] + padding)
    
    row_positions = [padding]
    for i in range(1, rows):
        row_positions.append(row_positions[-1] + row_heights[i-1] + padding)

    layout = []

    for i, img_path in enumerate(image_paths):
        col = i % cols
        row = i // cols

        # 使用该列和该行的起始位置
        x = col_positions[col]
        y = row_positions[row]

        layout.append({
            'index': i,
            'path': img_path,
            'position': (x, y),
            'size': display_sizes[i],
            'col': col,
            'row': row,
            'is_cropped': img_path in pending_crops
        })

    return layout


def find_smallest_image_path(image_paths, all_image_paths):
    """
    在给定的图片路径列表中找到最小的图片（按尺寸）

    Args:
        image_paths: 要检查的图片路径列表
        all_image_paths: 所有图片路径列表（用于查找索引）

    Returns:
        (最小图片路径, 在all_image_paths中的索引)
    """
    if not image_paths:
        return None, -1

    min_size = float('inf')
    min_path = None
    min_index = -1

    for img_path in image_paths:
        try:
            img_info = get_image_info(img_path)
            if img_info:
                size = img_info['width'] * img_info['height']
                if size < min_size:
                    min_size = size
                    min_path = img_path
                    if img_path in all_image_paths:
                        min_index = all_image_paths.index(img_path)
        except Exception:
            continue

    return min_path, min_index
```

[回到目录](#目录)

---

<a name="file-functionlist_operationspy"></a>
## 12. function\list_operations.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\function\list_operations.py`

```python
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

            # 更新图片列表显示（使用update_image_positions避免闪烁）
            main_window_instance.update_image_positions()
            print(f"已删除图片 # {index + 1}")

        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")
```

[回到目录](#目录)

---

<a name="file-functionui_operationspy"></a>
## 13. function\ui_operations.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\function\ui_operations.py`

```python
# -*- coding: utf-8 -*-
"""
UI操作模块
处理UI相关的操作，如浏览输出目录、进入裁剪模式等
"""

from tkinter import filedialog, messagebox
import os
import tkinter as tk
from typing import Callable


def delayed_execution(widget: tk.Widget, callback: Callable, delay_ms: int = 100):
    """延迟执行回调函数，确保UI渲染完成后再执行

    Args:
        widget: Tkinter组件对象
        callback: 回调函数
        delay_ms: 延迟时间（毫秒）
    """
    widget.after(delay_ms, callback)


def ensure_widget_rendered(widget: tk.Widget, callback: Callable):
    """确保组件渲染完成后再执行回调

    Args:
        widget: Tkinter组件对象
        callback: 回调函数
    """
    widget.update_idletasks()
    widget.after(10, callback)


def get_actual_dimensions(canvas: tk.Canvas) -> tuple:
    """获取Canvas的实际物理尺寸

    Args:
        canvas: Tkinter Canvas对象

    Returns:
        tuple: (width, height)
    """
    canvas.update_idletasks()
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    if width < 10 or height < 10:
        width = 800
        height = 600

    return width, height


def fit_to_window_strategy(canvas: tk.Canvas, orig_width: int, orig_height: int, padding: int = 20):
    """适应窗口的缩放策略

    Args:
        canvas: Tkinter Canvas对象
        orig_width: 原始图片宽度
        orig_height: 原始图片高度
        padding: 填充大小

    Returns:
        float: 适应窗口的缩放比例
    """
    canvas_width, canvas_height = get_actual_dimensions(canvas)

    scale_width = (canvas_width - padding) / orig_width
    scale_height = (canvas_height - padding) / orig_height
    fit_scale = min(scale_width, scale_height)

    return fit_scale


def on_file_selected(main_window_instance, event):
    """
    处理文件选择变化事件
    当用户从下拉框中选择不同的图片时，更新预览显示

    Args:
        main_window_instance: GifMakerGUI实例
        event: 事件对象
    """
    try:
        current_selection = main_window_instance.file_combobox.current()
        if current_selection >= 0 and current_selection < len(main_window_instance.image_paths):
            # 设置选中的图片索引
            main_window_instance.selected_image_index = current_selection
            main_window_instance.selected_image_indices = {current_selection}
            main_window_instance.last_selected_index = current_selection

            # 只更新选中框，不重新绘制整个网格（避免闪烁）
            main_window_instance.draw_selection_boxes()
            
            # 滚动到选中的图片
            main_window_instance.scroll_to_image(current_selection)

            # 更新状态信息
            update_status_info(main_window_instance)
    except Exception as e:
        print(f"文件选择处理失败: {e}")


def browse_output(main_window_instance):
    """浏览输出文件"""
    current_path = main_window_instance.output_path.get()
    current_dir = os.path.dirname(current_path)
    current_filename = os.path.basename(current_path)

    if not current_dir or not os.path.exists(current_dir):
        current_dir = os.getcwd()

    # 生成默认文件名
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"animation_{timestamp}.gif"

    selected_file = filedialog.asksaveasfilename(
        title="选择输出文件",
        initialdir=current_dir,
        initialfile=default_filename,
        defaultextension=".gif",
        filetypes=[
            ("GIF files", "*.gif"),
            ("All files", "*.*")
        ]
    )

    if selected_file:
        main_window_instance.output_path.set(selected_file)


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

        if main_window_instance.selected_image_indices and len(main_window_instance.selected_image_indices) > 1:

            target_indices = sorted(main_window_instance.selected_image_indices)
            target_paths = [main_window_instance.image_paths[i] for i in target_indices]

            from function.image_utils import find_smallest_image_path
            current_image_path, current_index = find_smallest_image_path(target_paths, main_window_instance.image_paths)
        else:

            current_selection = main_window_instance.file_combobox.current()
            if current_selection >= 0 and current_selection < len(main_window_instance.image_paths):
                current_image_path = main_window_instance.image_paths[current_selection]
                current_index = current_selection
                target_paths = [current_image_path]
            else:
                current_image_path = main_window_instance.image_paths[0]
                current_index = 0
                target_paths = [current_image_path]

        result = show_crop_dialog(
            main_window_instance.root,
            image_path=current_image_path,
            image_paths=target_paths,
            current_index=current_index
        )

        if result:
            # 在应用裁剪之前先保存状态
            from function.history_manager import save_state
            save_state(main_window_instance)

            from function.image_utils import load_image
            from function.crop import crop_image

            if result.get('is_base_image', False):

                crop_coords = result.get('crop_coords', {})

                # 保存裁剪坐标和裁剪后的图片
                for img_path, coords in crop_coords.items():
                    if img_path in main_window_instance.image_paths:
                        main_window_instance.pending_crop_coords[img_path] = coords
                        # 加载图片并应用裁剪
                        img = load_image(img_path)
                        if img:
                            x1, y1, x2, y2 = coords
                            cropped_img = crop_image(img, x1, y1, x2, y2)
                            main_window_instance.pending_crops[img_path] = cropped_img
            else:

                start_pos = result['start']
                end_pos = result['end']
                current_img_path = current_image_path

                main_window_instance.pending_crop_coords[current_img_path] = (
                    start_pos[0], start_pos[1], end_pos[0], end_pos[1]
                )
                # 加载图片并应用裁剪
                img = load_image(current_img_path)
                if img:
                    x1, y1, x2, y2 = start_pos[0], start_pos[1], end_pos[0], end_pos[1]
                    cropped_img = crop_image(img, x1, y1, x2, y2)
                    main_window_instance.pending_crops[current_img_path] = cropped_img

            # 更新图片列表
            main_window_instance.display_grid_preview()
            print("裁剪设置已保存")

    except Exception as e:
        messagebox.showerror("错误", f"进入裁剪模式失败:\n{str(e)}")


def update_status_info(main_window_instance):
    """
    更新状态栏信息，显示当前图片信息
    包括当前图片尺寸、文件大小、总时间估算和GIF大小估算
    """
    if main_window_instance.image_paths:
        current_selection = main_window_instance.file_combobox.current()
        if current_selection >= 0 and current_selection < len(main_window_instance.image_paths):
            img_path = main_window_instance.image_paths[current_selection]

            try:

                from function.image_utils import get_image_info
                img_info = get_image_info(img_path)

                current_img_info = f"当前图片: {img_info['width']}x{img_info['height']}px | {img_info['size_kb']:.2f}KB | {img_info['format']}"
                main_window_instance.current_img_size_label.config(text=current_img_info)

                # 计算总时间 - 从file_manager导入
                from function.file_manager import calculate_total_time
                num_images = len(main_window_instance.image_paths)
                duration_ms = main_window_instance.duration.get()
                total_time_s, total_time_ms = calculate_total_time(num_images, duration_ms)
                main_window_instance.total_time_label.config(text=f"总时间: {total_time_s:.1f}s ({num_images}张 x {duration_ms}ms)")

                # 估算GIF大小 - 从file_manager导入
                from function.file_manager import estimate_gif_size
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

    zoom_percent = int(main_window_instance.preview_scale * 100)
    main_window_instance.zoom_label.config(text=f"缩放: {zoom_percent}%")


def update_size_label(x1_var, y1_var, x2_var, y2_var, size_label):
    """
    更新实时尺寸显示
    
    Args:
        x1_var: 起始X坐标变量
        y1_var: 起始Y坐标变量
        x2_var: 结束X坐标变量
        y2_var: 结束Y坐标变量
        size_label: 显示尺寸的Label控件
    """
    try:
        x1 = int(x1_var.get())
        y1 = int(y1_var.get())
        x2 = int(x2_var.get())
        y2 = int(y2_var.get())
        
        # 确保坐标顺序正确
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        width = x2 - x1
        height = y2 - y1
        
        if width > 0 and height > 0:
            size_label.config(text=f"尺寸: {width} x {height}")
        else:
            size_label.config(text="尺寸: --")
    except (ValueError, AttributeError):
        size_label.config(text="尺寸: --")
```

[回到目录](#目录)

---

<a name="file-function__init__py"></a>
## 14. function\__init__.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\function\__init__.py`

```python
# -*- coding: utf-8 -*-
"""
功能模块包初始化文件
"""

from .image_utils import (
    load_image,
    resize_image,
    create_photo_image,
    calculate_scale_to_fit,
    calculate_scale_to_fill
)

from .crop import crop_image

__all__ = [
    'load_image',
    'resize_image',
    'create_photo_image',
    'calculate_scale_to_fit',
    'calculate_scale_to_fill',
    'crop_image'
]

```

[回到目录](#目录)

---

<a name="file-gitsyncclearfolderbat"></a>
## 15. GitSync\ClearFolder.bat

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\GitSync\ClearFolder.bat`

```batch
@echo off
chcp 65001 >nul

echo ============================================
echo Clear Parent Folder Script (Move to Recycle Bin)
echo ============================================
echo.
echo This will MOVE all files and folders in the parent directory to Recycle Bin
echo EXCEPT:
echo   - .git folder (Git repository)
echo   - GitSync folder (This script's location)
echo.
echo WARNING: Files will be moved to Recycle Bin, not permanently deleted!
echo.
echo Current parent directory:
set "PARENT_DIR=%~dp0.."
cd /d "%PARENT_DIR%"
cd
echo.
echo Files and folders to be moved to Recycle Bin (excluded: .git, GitSync):
echo.
dir /b /a-d
dir /b /ad | findstr /v /i "^\.git$" | findstr /v /i "^GitSync$"
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause >nul

echo.
echo Starting cleanup...
echo.

REM Change to parent directory
cd /d "%PARENT_DIR%"

REM Delete files and folders using PowerShell
set "PS_SCRIPT=%TEMP%\DeleteWithRecycle_%RANDOM%.ps1"

REM Create PowerShell script
(
echo $ErrorActionPreference = 'SilentlyContinue'
echo Add-Type -AssemblyName Microsoft.VisualBasic
echo.
) > "%PS_SCRIPT%"

REM Delete files directly
for /f "delims=" %%f in ('dir /b /a-d 2^>nul ^| findstr /v /i "^GitSync"') do (
    echo Moving file to Recycle Bin: %%f
    echo $filePath = Join-Path "%PARENT_DIR%" "%%f" >> "%PS_SCRIPT%"
    echo if ^(Test-Path $filePath^) { >> "%PS_SCRIPT%"
    echo     Write-Host "Moving to Recycle Bin: %%f" >> "%PS_SCRIPT%"
    echo     [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile^($filePath, 'OnlyErrorDialogs', 'SendToRecycleBin'^) >> "%PS_SCRIPT%"
    echo } >> "%PS_SCRIPT%"
)

REM Delete folders directly
for /f "delims=" %%d in ('dir /b /ad 2^>nul ^| findstr /v /i "^\.git$" ^| findstr /v /i "^GitSync$"') do (
    echo Moving folder to Recycle Bin: %%d
    echo $folderPath = Join-Path "%PARENT_DIR%" "%%d" >> "%PS_SCRIPT%"
    echo if ^(Test-Path $folderPath^) { >> "%PS_SCRIPT%"
    echo     Write-Host "Moving to Recycle Bin: %%d" >> "%PS_SCRIPT%"
    echo     [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory^($folderPath, 'OnlyErrorDialogs', 'SendToRecycleBin'^) >> "%PS_SCRIPT%"
    echo } >> "%PS_SCRIPT%"
)

REM Execute the PowerShell script
echo [========================      ] 75%% Moving to Recycle Bin...
powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

REM Clean up PowerShell script
if exist "%PS_SCRIPT%" del /f /q "%PS_SCRIPT%"

echo [============================] 100%% Complete!

echo.
echo ============================================
echo Cleanup completed!
echo ============================================
echo.
echo All files and folders have been moved to Recycle Bin.
echo You can restore them from Recycle Bin if needed.
echo.
echo Remaining folders:
dir /b /ad
echo.
echo Remaining files:
dir /b /a-d 2>nul
if errorlevel 1 (
    echo (No files remaining)
)
echo.
pause
```

[回到目录](#目录)

---

<a name="file-gitsyncclonefromgitbat"></a>
## 16. GitSync\CloneFromGit.bat

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\GitSync\CloneFromGit.bat`

```batch

@echo off
chcp 65001 >nul
REM Change to parent directory (GitSync folder's parent)
cd /d "%~dp0.."
REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    pause
    exit /b 1
)
echo Git version check completed
REM Get current folder name as repo name (parent directory)
for %%i in (.) do set REPO_NAME=%%~ni
REM Construct GitHub URL based on folder name
REM Format: https://github.com/USERNAME/REPO_NAME.git
set "REPO_URL=https://github.com/jiedi720/%REPO_NAME%.git"
set "BRANCH=main"
echo ======================================
echo Force overwrite current folder with GitHub repo
echo Repo: %REPO_URL%
echo Branch: %BRANCH%
echo ======================================
echo.
echo WARNING: This will DISCARD all local changes!
echo Press Ctrl+C to cancel, or any key to continue...
pause >nul
REM Initialize if not a git repo or if .git folder is empty/invalid
if not exist ".git" (
    echo Current directory is not a Git repo, initializing...
    git init
    git remote add origin %REPO_URL%
) else (
    REM Check if .git is a valid git repo by checking for HEAD file
    if not exist ".git\HEAD" (
        echo .git folder exists but is not a valid Git repo, reinitializing...
        rmdir /s /q ".git"
        git init
        git remote add origin %REPO_URL%
    )
)
echo Fetching remote repo...
echo [==========                    ] 25%% Fetching...
git fetch origin
if %errorlevel% neq 0 (
    echo ERROR: Failed to fetch from remote repository
    pause
    exit /b 1
)
echo Force overwriting local files...
echo [==================            ] 50%% Resetting...
git reset --hard origin/%BRANCH%
if %errorlevel% neq 0 (
    echo ERROR: Failed to reset to remote branch
    pause
    exit /b 1
)
echo Cleaning untracked files (including GitSync folder)...
echo [========================      ] 75%% Cleaning...
git clean -fd
echo [============================] 100%% Complete!
echo.
echo Overwrite completed successfully
echo Repository: %REPO_NAME%
pause

```

[回到目录](#目录)

---

<a name="file-gitsyncupdate2gitbat"></a>
## 17. GitSync\Update2Git.bat

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\GitSync\Update2Git.bat`

```batch
@echo off
:: Set code page to UTF-8 for proper character display
chcp 65001 >nul

REM Change to parent directory (project root)
cd /d "%~dp0.."

:: Step 1: Clean Python cache
echo [1/5] Cleaning Python cache folders...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

:: Step 2: Clean compiled files
echo [2/5] Cleaning compiled files...
del /s /q *.pyc *.pyo >nul 2>&1

:: Step 3: Gitignore check
echo [3/5] Checking Git ignore configuration...
if not exist ".gitignore" goto :git_ops
findstr /i "GitSync" ".gitignore" >nul
if errorlevel 1 goto :git_ops

echo WARNING: GitSync found in .gitignore, removing entry...
findstr /v /i "GitSync" ".gitignore" > ".gitignore.tmp"
move /y ".gitignore.tmp" ".gitignore" >nul

:git_ops
:: Step 4: Standard Git workflow
echo [4/5] Switching to main branch and adding changes...
git checkout main
git add -A

echo [5/5] Committing and Pushing changes...
set "msg=Daily update"
set /p msg="Enter message (Press Enter for 'Daily update'): "
git commit -m "%msg%"
git push origin main --force

:: Check if the push was successful
if errorlevel 1 goto :push_failed

:push_success
echo.
echo ========================================
echo [SUCCESS] Update completed and pushed!
echo ========================================
echo.
:: Step 6: Display Summary with Full Paths and Extensions
echo  STATUS          FILE NAME
echo --------------------------------------------------------------------------
:: tokens=1,* ensures the second variable %%b captures the FULL path even with spaces
for /f "tokens=1,*" %%a in ('git log -1 --name-status --format^=') do (
    if "%%a"=="M" echo  Modified    :  %%b
    if "%%a"=="A" echo  Added       :  %%b
    if "%%a"=="D" echo  Deleted     :  %%b
    if "%%a"=="R" echo  Renamed     :  %%b
)
echo --------------------------------------------------------------------------
goto :final_end

:push_failed
echo.
echo ========================================
echo [ERROR] Push failed. Check your network.
echo ========================================

:final_end
echo.
pause
exit /b 0
```

[回到目录](#目录)

---

<a name="file-guicrop_guipy"></a>
## 18. gui\crop_gui.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\gui\crop_gui.py`

```python
# -*- coding: utf-8 -*-
"""
裁剪窗口 GUI 模块 - 高清自适应裁剪窗口，只包含裁剪窗口的 GUI 设定相关代码
支持 1280x720 布局，并能随窗口缩放自动调整控件位置
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from function.image_utils import (
    load_image,
    resize_image,
    create_photo_image,
    calculate_scale_to_fit,
    calculate_scale_to_fill
)
from function.crop import CropState, CropRatioController, find_smallest_image_path, calculate_scaled_dimensions, convert_canvas_to_image_coords, validate_crop_coordinates, calculate_aspect_ratio, determine_crop_strategy, crop_image
from function.ui_operations import ensure_widget_rendered

class CropDialog:
    """裁剪对话框类"""

    def __init__(self, parent, image_path=None, image_paths=None, current_index=0):
        self.parent = parent
        self.result = None
        self.image_path = image_path
        self.image_paths = image_paths or []
        self.current_index = current_index
        self.current_photo = None
        self.original_image = None
        self.base_photo = None
        self.preview_scale = 0.0  # 初始值为0，表示需要计算适应窗口的缩放比例
        self.initial_scale = 1.0

        self.selection_start = None
        self.selection_rect = None
        self.is_selecting = False

        self.handles = {}
        self.dragging_handle = None
        self.drag_start_pos = None
        self.drag_start_coords = None

        self.ratio_handler = CropRatioController(self)
        self.ratio_handler.dialog = self

        self.is_moving_selection = False
        self.move_start_pos = None
        self.move_start_coords = None

        # 跟踪当前显示的图片类型：'original', 'prev', 'next', 'first'
        self.current_display_mode = 'original'
        self.current_reference_path = None  # 当前显示的参考图片路径


        self.image_x = 0
        self.image_y = 0
        self.image_width = 0
        self.image_height = 0

        self.crop_state = CropState(max_history=100)

        self.is_base_image, self.min_image_path, min_idx = determine_crop_strategy(self.image_paths, current_index)
        self.min_image_size = min_idx
        #   - 1280x720
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Crop Animation - High Definition")
        self.dialog.geometry("1280x720")
        self.dialog.minsize(800, 600)

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.ui_font = ("Microsoft YaHei UI", 10)
        self.header_font = ("Microsoft YaHei UI", 12, "bold")

        self.setup_ui()
        self.center_window()

        if self.image_path:
            from function.image_utils import load_image
            # 正确加载图片：只传递图片路径，不传递self
            self.original_image = load_image(self.image_path)
            if self.original_image:
                # 延迟显示图片，确保Canvas完全渲染
                self.dialog.after(100, self.display_image)

    def center_window(self):
        """将窗口居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        
        # 如果窗口还没有显示，使用设置的默认尺寸
        if width <= 1 or height <= 1:
            width = 1280
            height = 720
        
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def display_image(self):
        """显示图片"""
        if not hasattr(self, 'original_image'):
            return

        try:
            # 重置为显示原始图片
            self.current_display_mode = 'original'
            self.current_reference_path = None

            img = self.original_image
            orig_width, orig_height = img.size

            # 强制更新Canvas尺寸
            self.dialog.update_idletasks()
            self.canvas.update_idletasks()
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # 确保Canvas有合理的尺寸
            if canvas_width < 100:
                canvas_width = 800
            if canvas_height < 100:
                canvas_height = 600

            # 计算适应窗口的缩放比例
            if not hasattr(self, 'preview_scale') or self.preview_scale == 0:
                self.preview_scale = calculate_scale_to_fit(orig_width, orig_height, canvas_width, canvas_height)
                self.initial_scale = self.preview_scale

            # 计算缩放后的尺寸
            scaled_width = int(orig_width * self.preview_scale)
            scaled_height = int(orig_height * self.preview_scale)

            #   image_utils 
            img_resized = resize_image(img, scaled_width, scaled_height)

            #   image_utils PhotoImage
            self.current_photo = create_photo_image(img_resized)
            self.base_photo = self.current_photo

            #  Canvas
            self.canvas.delete("all")

            #  Canvas
            #  Canvas
            actual_canvas_width = self.canvas.winfo_width()
            actual_canvas_height = self.canvas.winfo_height()

            #   Canvas
            if scaled_width > actual_canvas_width or scaled_height > actual_canvas_height:
                #   Canvas，NW(0,0) ，
                self.image_x = 0
                self.image_y = 0
                anchor = tk.NW
                self.canvas.configure(scrollregion=(0, 0, scaled_width, scaled_height))
            else:
                #  Canvas，，
                self.image_x = actual_canvas_width // 2
                self.image_y = actual_canvas_height // 2
                anchor = tk.CENTER
                #  Canvas，设置为Canvas尺寸，确保滚动条始终可见
                self.canvas.configure(scrollregion=(0, 0, actual_canvas_width, actual_canvas_height))

            self.image_width = scaled_width
            self.image_height = scaled_height

            # 绘制图片
            self.canvas.create_image(self.image_x, self.image_y, image=self.current_photo, anchor=anchor)

            # 绘制图片边框
            if anchor == tk.NW:
                # 左上角对齐
                border_x1 = self.image_x - 1
                border_y1 = self.image_y - 1
                border_x2 = self.image_x + scaled_width + 1
                border_y2 = self.image_y + scaled_height + 1
            else:
                # 居中对齐
                border_x1 = self.image_x - scaled_width // 2 - 1
                border_y1 = self.image_y - scaled_height // 2 - 1
                border_x2 = self.image_x + scaled_width // 2 + 1
                border_y2 = self.image_y + scaled_height // 2 + 1

            self.canvas.create_rectangle(
                border_x1, border_y1, border_x2, border_y2,
                outline="#CCCCCC",
                width=2,
                tags="image_border"
            )

            self.x1_var.set("0")
            self.y1_var.set("0")
            self.x2_var.set(str(orig_width))
            self.y2_var.set(str(orig_height))

            self.draw_selection_box()

        except Exception as e:
            print(f"无法显示图片: {e}")
        
    def setup_ui(self):
        """使用 Grid 权重布局实现自适应"""
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.columnconfigure(1, weight=0)
        self.dialog.rowconfigure(0, weight=1)

        #  --- 1.  (Canvas) ---
        self.preview_frame = ttk.LabelFrame(self.dialog, text="预览视图 (Preview)", padding=10)
        self.preview_frame.grid(row=0, column=0, padx=(20, 0), pady=20, sticky="nsew")

        #   Canvas 
        self.canvas = tk.Canvas(self.preview_frame, bg="#313337", highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        #   Canvas 
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)
        self.preview_frame.rowconfigure(1, weight=0)  # 确保水平滚动条行不拉伸

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<MouseWheel>", lambda e: self.ratio_handler.on_mousewheel(e, self.zoom_in, self.zoom_out))  # Windows
        self.canvas.bind("<Button-4>", lambda e: self.ratio_handler.on_mousewheel(e, self.zoom_in, self.zoom_out))   #  Linux 
        self.canvas.bind("<Button-5>", lambda e: self.ratio_handler.on_mousewheel(e, self.zoom_in, self.zoom_out))   #  Linux 

        self.canvas.create_text(450, 300, text="图像预览区域\n(Image Preview Area)", fill="white", justify="center")

        #  --- 2.  ---
        self.right_panel = ttk.Frame(self.dialog, padding=20)
        self.right_panel.grid(row=0, column=1, sticky="n", padx=0)  #   50 
        
        self.right_panel.columnconfigure(0, weight=0)
        self.modules_container = ttk.Frame(self.right_panel, width=320)
        self.modules_container.grid(row=0, column=0, sticky="n")
        
        # 2.1 坐标设置
        coord_title = "坐标设置" + ("（基准图）" if self.is_base_image else "")
        coord_group = ttk.LabelFrame(self.modules_container, text=coord_title, padding=5)
        coord_group.pack(fill="x", pady=(0, 15), ipadx=10)
        

        coord_group.columnconfigure(0, weight=0)
        coord_group.columnconfigure(1, weight=0)
        coord_group.columnconfigure(2, weight=0)
        coord_group.columnconfigure(3, weight=0)
        ttk.Label(coord_group, text="起始位置 (Top-Left):", font=self.ui_font).grid(row=0, column=0, columnspan=4, sticky="w", padx=5)
        self.x1_var = tk.StringVar(value="0")
        self.y1_var = tk.StringVar(value="0")
        self.create_spin_row(coord_group, 1, "X:", self.x1_var, "Y:", self.y1_var)
        ttk.Label(coord_group, text="结束位置 (Bottom-Right):", font=self.ui_font).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0), padx=5)
        self.x2_var = tk.StringVar(value="100")
        self.y2_var = tk.StringVar(value="100")
        self.create_spin_row(coord_group, 3, "X:", self.x2_var, "Y:", self.y2_var)

        size_frame = ttk.Frame(coord_group)
        size_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 0), padx=5)
        self.size_label = ttk.Label(size_frame, text="尺寸: 100 x 100 像素", font=("Microsoft YaHei UI", 9))
        self.size_label.pack(side="left", anchor="w")
        self.locked_ratio_label = ttk.Label(size_frame, text="", foreground="blue", font=("Microsoft YaHei UI", 9))
        self.locked_ratio_label.pack(side="left", padx=(10, 0))

        # 2.2 比例设置
        ratio_group = ttk.LabelFrame(self.modules_container, text="比例设置", padding=5)
        ratio_group.pack(fill="x", pady=(0, 15), ipadx=10)
        

        ratio_group.columnconfigure(0, weight=0)
        ratio_group.columnconfigure(1, weight=0)

        self.ratio_var = tk.StringVar(value="free")
        self.ratio_var.trace_add('write', lambda *args: self.ratio_handler.on_ratio_change(
            self.ratio_var,
            self.x1_var,
            self.y1_var,
            self.x2_var,
            self.y2_var,
            self.ratio_handler,
            self.locked_ratio_label,
            self.draw_selection_box,
            lambda: self.ratio_handler.update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)
        ))

        ratios = [
            ("自由", "free"),
            ("锁定比例", "lock_current"),
            ("原始比例", "original"),
            ("黄金分割", "1.618"),
            ("1:1", "1:1"),
            ("16:9", "16:9"),
            ("4:3", "4:3"),
            ("3:2", "3:2")
        ]

        #   grid ，
        for i, (text, value) in enumerate(ratios):
            row = i // 2
            col = i % 2
            rb = ttk.Radiobutton(ratio_group, text=text, variable=self.ratio_var, value=value)
            rb.grid(row=row, column=col, sticky="w", padx=5, pady=2)

        # 2.3 选项设置
        option_group = ttk.LabelFrame(self.modules_container, text="选项", padding=5)
        option_group.pack(fill="x", pady=(0, 15), ipadx=10)
        
        option_group.columnconfigure(0, weight=0)
        
        # "显示裁剪后"是独立的选项
        self.show_cropped_var = tk.BooleanVar()
        cb_cropped = ttk.Checkbutton(option_group, text="显示裁剪后", variable=self.show_cropped_var,
                                   command=self.apply_display_options)
        cb_cropped.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        ttk.Separator(option_group, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=(5, 5))
        
        # 其他选项是互斥的
        self.display_option_var = tk.StringVar(value="none")
        
        opts = [
            ("显示上一帧", "prev"),
            ("显示下一帧", "next"),
            ("显示第一帧", "first")
        ]
        
        for i, (text, value) in enumerate(opts):
            rb = ttk.Radiobutton(option_group, text=text, variable=self.display_option_var, value=value,
                                command=self.apply_display_options)
            rb.grid(row=i + 2, column=0, sticky="w", padx=5, pady=5)

        # 分隔线
        ttk.Separator(self.modules_container, orient="horizontal").pack(fill="x", pady=(10, 10))
        
        btn_row1 = ttk.Frame(self.modules_container)
        btn_row1.pack(fill="x", pady=(0, 5))

        self.fit_btn = ttk.Button(btn_row1, text="⬜", width=5, command=lambda: self.ratio_handler.fit_to_window(self))
        self.fit_btn.pack(side="left", padx=5)
        self.create_tooltip(self.fit_btn, "适应窗口")

        self.reset_btn = ttk.Button(btn_row1, text="🔄", width=5, command=self.reset_zoom)
        self.reset_btn.pack(side="left", padx=5)
        self.create_tooltip(self.reset_btn, "原始大小")

        btn_row2 = ttk.Frame(self.modules_container)
        btn_row2.pack(fill="x", pady=(0, 10))

        self.ok_btn = ttk.Button(btn_row2, text="✅", width=15, command=self.ok_clicked)
        self.ok_btn.pack(side="left", padx=5)
        self.create_tooltip(self.ok_btn, "确定 (OK)")

        self.cancel_btn = ttk.Button(btn_row2, text="❌", width=15, command=self.cancel_clicked)
        self.cancel_btn.pack(side="left", padx=5)
        self.create_tooltip(self.cancel_btn, "取消 (Cancel)")

    def create_spin_row(self, parent, row, label1, var1, label2, var2):
        """辅助函数：创建一行两个带标签的微调框"""
        ttk.Label(parent, text=label1).grid(row=row, column=0, sticky="w", padx=5)
        s1 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var1, width=6)
        s1.grid(row=row, column=1, sticky="w", padx=(2, 5), pady=5)
        #          from function.ui_operations import update_size_label
        s1.bind('<Return>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))
        s1.bind('<FocusOut>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))

        ttk.Label(parent, text=label2).grid(row=row, column=2, sticky="w", padx=5)
        s2 = tk.Spinbox(parent, from_=0, to=9999, textvariable=var2, width=6)
        s2.grid(row=row, column=3, sticky="w", padx=(2, 5), pady=5)
        s2.bind('<Return>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))
        s2.bind('<FocusOut>', lambda e: update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label))

    def create_tooltip(self, widget, text):
        """创建鼠标悬浮提示"""
        def enter(event):
            # 如果已经存在tooltip，先销毁
            if hasattr(widget, '_tooltip'):
                try:
                    widget._tooltip.destroy()
                except:
                    pass
                del widget._tooltip
            
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes("-topmost", True)
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid",
                            borderwidth=1, font=("tahoma", "8", "normal"))
            label.pack()

            # 计算提示框位置
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")

            # 保存tooltip引用，避免被垃圾回收
            widget._tooltip = tooltip

        def leave(event):
            if hasattr(widget, '_tooltip'):
                try:
                    widget._tooltip.destroy()
                except:
                    pass
                del widget._tooltip

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def reset_zoom(self):
        """原始大小 - 按图片原始尺寸显示图片"""
        if not hasattr(self, 'original_image'):
            messagebox.showinfo("提示", "请先加载图片")
            return

        try:
            # 重置缩放比例为1.0（原始尺寸）
            self.preview_scale = 1.0

            # 根据当前显示的图片类型来决定如何重新显示
            if self.current_display_mode != 'original' and self.current_reference_path:
                # 重新应用显示选项
                self.apply_display_options()
            else:
                # 显示原始图片
                self.display_image()

        except Exception as e:
            messagebox.showerror("错误", f"重置缩放失败: {str(e)}")

    def zoom_in(self):
        """放大图片"""
        if not hasattr(self, 'original_image'):
            return

        try:
            if self.preview_scale < 5.0:
                self.preview_scale *= 1.25

                # 根据当前显示的图片类型来决定如何重新显示
                if self.current_display_mode != 'original' and self.current_reference_path:
                    # 如果当前显示的是参考图片，重新显示该参考图片
                    self.ratio_handler.display_reference_image(self, self.current_reference_path)
                else:
                    # 显示原始图片
                    self.display_image()
        except Exception as e:
            print(f"放大失败: {e}")

    def zoom_out(self):
        """缩小图片"""
        if not hasattr(self, 'original_image'):
            return

        try:
            if self.preview_scale > 0.1:
                self.preview_scale /= 1.25

                # 根据当前显示的图片类型来决定如何重新显示
                if self.current_display_mode != 'original' and self.current_reference_path:
                    # 如果当前显示的是参考图片，重新显示该参考图片
                    self.ratio_handler.display_reference_image(self, self.current_reference_path)
                else:
                    # 显示原始图片
                    self.display_image()
        except Exception as e:
            print(f"缩小失败: {e}")

    def ok_clicked(self):
        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            if len(self.image_paths) > 1 and self.is_base_image:
                # 获取基准图片宽度
                base_width = self.original_image.width
                base_height = self.original_image.height

                confirm = messagebox.askyesno(
                    "确认裁剪",
                    f"将使用相同的像素坐标裁剪选中的所有 {len(self.image_paths)} 张图片\n\n"
                    f"基准图片尺寸: {base_width} x {base_height}\n"
                    f"裁剪区域: ({x1}, {y1}) 到 ({x2}, {y2})\n"
                    f"裁剪尺寸: {x2-x1} x {y2-y1}\n\n"
                    f"所有图片将使用相同的像素坐标进行裁剪\n"
                    f"最终生成的裁剪图片分辨率将完全相同\n\n"
                    f"此操作可撤销/重做\n"
                    f"是否继续？"
                )

                if not confirm:

                    self.crop_state.history_manager.undo({
                        'crop_results': {},
                        'crop_coords': {}
                    })
                    return

                for img_path in self.image_paths:
                    self.crop_state.set_crop_coords(img_path, (x1, y1, x2, y2))

                self.result = {
                    'start': (x1, y1),
                    'end': (x2, y2),
                    'is_base_image': True,
                    'crop_coords': {path: self.crop_state.get_crop_coords(path) for path in self.image_paths},
                    'options': {
                        'show_cropped': self.show_cropped_var.get(),
                        'display_option': self.display_option_var.get()
                    }
                }
            else:

                self.crop_state.set_crop_coords(self.image_path, (x1, y1, x2, y2))

                self.result = {
                    'start': (x1, y1),
                    'end': (x2, y2),
                    'crop_coords': {self.image_path: (x1, y1, x2, y2)},
                    'options': {
                        'show_cropped': self.show_cropped_var.get(),
                        'display_option': self.display_option_var.get()
                    }
                }

            # 清理所有tooltip
            self._cleanup_all_tooltips()
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字坐标")
    
    def cancel_clicked(self):
        self.result = None
        # 清理所有tooltip
        self._cleanup_all_tooltips()
        self.dialog.destroy()
    
    def _cleanup_all_tooltips(self):
        """清理所有tooltip"""
        def recursive_cleanup(widget):
            """递归清理控件及其所有子控件的tooltip"""
            if hasattr(widget, '_tooltip'):
                try:
                    widget._tooltip.destroy()
                except:
                    pass
                del widget._tooltip
            
            # 递归清理子控件
            for child in widget.winfo_children():
                recursive_cleanup(child)
        
        # 递归清理所有控件的tooltip
        recursive_cleanup(self.dialog)
        
        # 清理所有 Toplevel 窗口（除了对话框本身）
        try:
            all_windows = self.dialog.winfo_toplevel().winfo_children()
            for window in all_windows:
                if isinstance(window, tk.Toplevel) and window != self.dialog:
                    try:
                        window.destroy()
                    except:
                        pass
        except:
            pass
        
        # 强制更新UI，确保tooltip被彻底清理
        self.dialog.update_idletasks()
        
    def show(self):
        self.dialog.wait_window()
        return self.result

    def on_canvas_press(self, event):
        """统一处理Canvas上的鼠标按下事件"""
        if not hasattr(self, 'original_image'):
            return

        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            if "handle" in tags:
                for tag in tags:
                    if tag in self.handles and self.handles[tag] == item:
                        self.dragging_handle = tag
                        self.drag_start_pos = (event.x, event.y)
                        self.drag_start_coords = (
                            int(self.x1_var.get()),
                            int(self.y1_var.get()),
                            int(self.x2_var.get()),
                            int(self.y2_var.get())
                        )
                        return


        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            img_left = self.image_x - self.image_width // 2
            img_top = self.image_y - self.image_height // 2

            scaled_x1 = img_left + x1 * self.preview_scale
            scaled_y1 = img_top + y1 * self.preview_scale
            scaled_x2 = img_left + x2 * self.preview_scale
            scaled_y2 = img_top + y2 * self.preview_scale

            if (scaled_x1 < event.x < scaled_x2 and
                scaled_y1 < event.y < scaled_y2):
                self.is_moving_selection = True
                self.move_start_pos = (event.x, event.y)
                self.move_start_coords = (x1, y1, x2, y2)
                return
        except:
            pass


        img_left = self.image_x - self.image_width // 2
        img_top = self.image_y - self.image_height // 2
        img_right = self.image_x + self.image_width // 2
        img_bottom = self.image_y + self.image_height // 2

        if img_left <= event.x <= img_right and img_top <= event.y <= img_bottom:
            self.is_selecting = True
            self.selection_start = (event.x, event.y)

    def on_canvas_drag(self, event):
        """统一处理Canvas上的鼠标拖拽事件"""
        if self.dragging_handle:
            self.handle_drag(event)
            return

        if self.is_moving_selection:
            self.move_selection(event)
            return

        if not self.is_selecting or not self.selection_start:
            return

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        x1, y1 = self.selection_start
        x2, y2 = event.x, event.y

        img_left = self.image_x - self.image_width // 2
        img_top = self.image_y - self.image_height // 2
        img_right = self.image_x + self.image_width // 2
        img_bottom = self.image_y + self.image_height // 2

        x1 = max(img_left, min(x1, img_right))
        y1 = max(img_top, min(y1, img_bottom))
        x2 = max(img_left, min(x2, img_right))
        y2 = max(img_top, min(y2, img_bottom))


        self.selection_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red",
            width=2,
            dash=(4, 4)
        )

    def move_selection(self, event):
        """移动选框"""
        try:
            dx = event.x - self.move_start_pos[0]
            dy = event.y - self.move_start_pos[1]

            # 计算图片坐标的移动距离
            img_dx = int(dx / self.preview_scale)
            img_dy = int(dy / self.preview_scale)

            x1, y1, x2, y2 = self.move_start_coords

            new_x1 = x1 + img_dx
            new_y1 = y1 + img_dy
            new_x2 = x2 + img_dx
            new_y2 = y2 + img_dy


            from function.crop import validate_crop_coordinates
            is_ratio_locked = self.ratio_handler.is_ratio_locked and self.ratio_handler.ratio_value
            new_x1, new_y1, new_x2, new_y2 = validate_crop_coordinates(
                new_x1, new_y1, new_x2, new_y2, self.original_image.width, self.original_image.height, is_ratio_locked
            )

            self.x1_var.set(str(new_x1))
            self.y1_var.set(str(new_y1))
            self.x2_var.set(str(new_x2))
            self.y2_var.set(str(new_y2))

            self.draw_selection_box()
            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)

        except Exception as e:
            print(f"移动选框失败: {e}")

    def handle_drag(self, event):
        """滑块拖拽事件"""
        try:
            dx = event.x - self.drag_start_pos[0]
            dy = event.y - self.drag_start_pos[1]

            # 计算图片坐标的移动距离
            img_dx = int(dx / self.preview_scale)
            img_dy = int(dy / self.preview_scale)

            x1, y1, x2, y2 = self.drag_start_coords

            # 保存原始坐标用于比例锁定
            orig_x1, orig_y1, orig_x2, orig_y2 = x1, y1, x2, y2

            if self.dragging_handle == 'nw':  # 左上角
                x1 = x1 + img_dx
                y1 = y1 + img_dy
            elif self.dragging_handle == 'n':
                y1 = y1 + img_dy
            elif self.dragging_handle == 'ne':  # 右上角
                x2 = x2 + img_dx
                y1 = y1 + img_dy
            elif self.dragging_handle == 'e':
                x2 = x2 + img_dx
            elif self.dragging_handle == 'se':  # 右下角
                x2 = x2 + img_dx
                y2 = y2 + img_dy
            elif self.dragging_handle == 's':
                y2 = y2 + img_dy
            elif self.dragging_handle == 'sw':  # 左下角
                x1 = x1 + img_dx
                y2 = y2 + img_dy
            elif self.dragging_handle == 'w':
                x1 = x1 + img_dx

            # 如果启用了比例锁定，先应用比例约束
            if self.ratio_handler.is_ratio_locked and self.ratio_handler.ratio_value:
                x1, y1, x2, y2 = self.ratio_handler.adjust(x1, y1, x2, y2, handle=self.dragging_handle)
            else:
                # 如果没有启用比例锁定，确保坐标在边界内
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(self.original_image.width, x2)
                y2 = min(self.original_image.height, y2)

            # 验证坐标（确保最小尺寸和正确顺序）
            # 如果启用了比例锁定，传递 is_ratio_locked=True 避免破坏比例
            from function.crop import validate_crop_coordinates
            is_ratio_locked = self.ratio_handler.is_ratio_locked and self.ratio_handler.ratio_value
            x1, y1, x2, y2 = validate_crop_coordinates(
                x1, y1, x2, y2, self.original_image.width, self.original_image.height, is_ratio_locked
            )

            self.x1_var.set(str(x1))
            self.y1_var.set(str(y1))
            self.x2_var.set(str(x2))
            self.y2_var.set(str(y2))

            # 如果勾选了显示裁剪后，需要更新预览
            show_cropped = self.show_cropped_var.get()
            display_option = self.display_option_var.get()
            if show_cropped or display_option != "none":
                # 添加调试信息
                print(f"显示裁剪后: {show_cropped}, 显示选项: {display_option}")
                self.apply_display_options()
            else:
                self.draw_selection_box()

            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)

        except Exception as e:
            print(f"滑块拖拽失败: {e}")

    def on_canvas_release(self, event):
        """统一处理Canvas上的鼠标释放事件"""
        if self.dragging_handle:
            self.dragging_handle = None
            self.drag_start_pos = None
            self.drag_start_coords = None
            return

        if self.is_moving_selection:
            self.is_moving_selection = False
            self.move_start_pos = None
            self.move_start_coords = None
            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)
            return

        if not self.is_selecting or not self.selection_start:
            return

        self.is_selecting = False

        if self.selection_rect:
            coords = self.canvas.coords(self.selection_rect)
            if len(coords) == 4:
                x1, y1, x2, y2 = coords


                orig_x1, orig_y1 = convert_canvas_to_image_coords(
                    x1, y1, self.image_x, self.image_y, self.preview_scale, self.image_width, self.image_height
                )
                orig_x2, orig_y2 = convert_canvas_to_image_coords(
                    x2, y2, self.image_x, self.image_y, self.preview_scale, self.image_width, self.image_height
                )


                from function.crop import validate_crop_coordinates
                is_ratio_locked = self.ratio_handler.is_ratio_locked and self.ratio_handler.ratio_value
                orig_x1, orig_y1, orig_x2, orig_y2 = validate_crop_coordinates(
                    orig_x1, orig_y1, orig_x2, orig_y2, self.original_image.width, self.original_image.height, is_ratio_locked
                )

                self.x1_var.set(str(orig_x1))
                self.y1_var.set(str(orig_y1))
                self.x2_var.set(str(orig_x2))
                self.y2_var.set(str(orig_y2))


                self.canvas.delete(self.selection_rect)
                self.selection_rect = None

                self.apply_display_options()

            from function.ui_operations import update_size_label
            update_size_label(self.x1_var, self.y1_var, self.x2_var, self.y2_var, self.size_label)

    def on_mouse_move(self, event):
        """鼠标移动事件，根据位置改变光标形状"""
        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            if "handle" in tags:
                for tag in tags:
                    if tag in self.handles and self.handles[tag] == item:
                        cursor_map = {
                            'nw': 'size_nw_se',  # 左上角
                            'n': 'sb_v_double_arrow',  # 上边
                            'ne': 'size_ne_sw',  # 右上角
                            'e': 'sb_h_double_arrow',  # 右边
                            'se': 'size_nw_se',  # 右下角
                            's': 'sb_v_double_arrow',  # 下边
                            'sw': 'size_ne_sw',  # 左下角
                            'w': 'sb_h_double_arrow'  # 左边
                        }
                        self.canvas.config(cursor=cursor_map.get(tag, 'arrow'))
                        return


        self.canvas.config(cursor='arrow')

    def apply_display_options(self):
        """应用显示选项"""
        if not hasattr(self, 'original_image'):
            return

        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            orig_width, orig_height = self.original_image.size

            self.canvas.delete("all")
            if self.base_photo:
                self.canvas.create_image(self.image_x, self.image_y, image=self.base_photo, anchor=tk.CENTER)

            # 获取当前选择的显示选项
            display_option = self.display_option_var.get()
            show_cropped = self.show_cropped_var.get()

            # 添加调试信息
            print(f"apply_display_options - show_cropped: {show_cropped}, display_option: {display_option}")
            print(f"裁剪坐标: ({x1}, {y1}, {x2}, {y2})")

            self.current_display_mode = 'original'  # 重置为原始图片
            self.current_reference_path = None

            # 确定要显示的图片
            if display_option == "prev" and self.image_paths and len(self.image_paths) > 1 and self.current_index > 0:
                # 显示上一帧
                prev_path = self.image_paths[self.current_index - 1]
                self.current_display_mode = 'prev'
                self.current_reference_path = prev_path
                display_image_path = prev_path
            elif display_option == "next" and self.image_paths and len(self.image_paths) > 1 and self.current_index < len(self.image_paths) - 1:
                # 显示下一帧
                next_path = self.image_paths[self.current_index + 1]
                self.current_display_mode = 'next'
                self.current_reference_path = next_path
                display_image_path = next_path
            elif display_option == "first" and self.image_paths and len(self.image_paths) > 1:
                # 显示第一帧
                first_path = self.image_paths[0]
                self.current_display_mode = 'first'
                self.current_reference_path = first_path
                display_image_path = first_path
            else:
                # 显示原始图片
                self.current_display_mode = 'original'
                self.current_reference_path = None
                display_image_path = None

            # 加载要显示的图片
            from function.image_utils import load_image, resize_image, create_photo_image

            if display_image_path:
                display_img = load_image(display_image_path)
                if not display_img:
                    print(f"无法加载图片: {display_image_path}")
                    return

                # 调整图片尺寸以匹配原始图片
                if display_img.size != (orig_width, orig_height):
                    display_img = resize_image(display_img, orig_width, orig_height)
            else:
                display_img = self.original_image

            # 如果需要显示裁剪效果
            if show_cropped:
                # 添加调试信息
                print(f"开始显示裁剪效果...")
                print(f"原始图片尺寸: {orig_width}x{orig_height}")
                print(f"显示图片尺寸: {display_img.size}")

                # 应用裁剪
                cropped_img = crop_image(display_img, x1, y1, x2, y2)
                print(f"裁剪后图片尺寸: {cropped_img.size}")

                # 创建一个半透明的黑色遮罩
                mask = Image.new('RGBA', (orig_width, orig_height), (0, 0, 0, 180))
                # 将裁剪后的图片粘贴到遮罩上
                cropped_rgba = cropped_img.convert('RGBA')
                mask.paste(cropped_rgba, (x1, y1))
                # 转换为 RGB 以便显示
                mask = mask.convert('RGB')

                # 创建PhotoImage
                scaled_width = int(orig_width * self.preview_scale)
                scaled_height = int(orig_height * self.preview_scale)
                mask_resized = resize_image(mask, scaled_width, scaled_height)
                self.current_photo = create_photo_image(mask_resized)
                self.canvas.delete("all")
                self.canvas.create_image(self.image_x, self.image_y, image=self.current_photo, anchor=tk.CENTER)
                # 绘制图片边框
                border_x1 = self.image_x - scaled_width // 2 - 1
                border_y1 = self.image_y - scaled_height // 2 - 1
                border_x2 = self.image_x + scaled_width // 2 + 1
                border_y2 = self.image_y + scaled_height // 2 + 1
                self.canvas.create_rectangle(
                    border_x1, border_y1, border_x2, border_y2,
                    outline="#CCCCCC",
                    width=2,
                    tags="image_border"
                )
                print(f"裁剪效果显示完成")
            else:
                # 不显示裁剪效果，直接显示图片
                scaled_width = int(orig_width * self.preview_scale)
                scaled_height = int(orig_height * self.preview_scale)
                img_resized = resize_image(display_img, scaled_width, scaled_height)
                self.current_photo = create_photo_image(img_resized)
                self.canvas.delete("all")
                self.canvas.create_image(self.image_x, self.image_y, image=self.current_photo, anchor=tk.CENTER)
                # 绘制图片边框
                border_x1 = self.image_x - scaled_width // 2 - 1
                border_y1 = self.image_y - scaled_height // 2 - 1
                border_x2 = self.image_x + scaled_width // 2 + 1
                border_y2 = self.image_y + scaled_height // 2 + 1
                self.canvas.create_rectangle(
                    border_x1, border_y1, border_x2, border_y2,
                    outline="#CCCCCC",
                    width=2,
                    tags="image_border"
                )

            self.draw_selection_box()

        except Exception as e:
            print(f"应用显示选项失败: {e}")

    def draw_selection_box(self):
        """绘制选框和滑块"""
        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            #   image_x  image_y  0，（CENTER ）
            #   image_x  image_y  0，（NW ）
            if self.image_x > 0 and self.image_y > 0:

                img_left = self.image_x - self.image_width // 2
                img_top = self.image_y - self.image_height // 2
            else:
                img_left = self.image_x
                img_top = self.image_y

            scaled_x1 = img_left + x1 * self.preview_scale
            scaled_y1 = img_top + y1 * self.preview_scale
            scaled_x2 = img_left + x2 * self.preview_scale
            scaled_y2 = img_top + y2 * self.preview_scale

            self.canvas.delete("selection_box")
            self.canvas.delete("handle")

            # 确保图片边框在选框下方
            self.canvas.tag_lower("image_border")


            self.canvas.create_rectangle(
                scaled_x1, scaled_y1, scaled_x2, scaled_y2,
                outline="red",
                width=3,
                dash=(4, 4),
                tags="selection_box"
            )

            # 绘制8个控制点（4个角点 + 4个中点）
            handle_size = 10
            handle_offset = handle_size // 2

            handles = {
                'nw': (scaled_x1 - handle_offset, scaled_y1 - handle_offset, scaled_x1 + handle_offset, scaled_y1 + handle_offset),
                'n':  (scaled_x1 + (scaled_x2 - scaled_x1) // 2 - handle_offset, scaled_y1 - handle_offset,
                       scaled_x1 + (scaled_x2 - scaled_x1) // 2 + handle_offset, scaled_y1 + handle_offset),
                'ne': (scaled_x2 - handle_offset, scaled_y1 - handle_offset, scaled_x2 + handle_offset, scaled_y1 + handle_offset),
                'e':  (scaled_x2 - handle_offset, scaled_y1 + (scaled_y2 - scaled_y1) // 2 - handle_offset,
                       scaled_x2 + handle_offset, scaled_y1 + (scaled_y2 - scaled_y1) // 2 + handle_offset),
                'se': (scaled_x2 - handle_offset, scaled_y2 - handle_offset, scaled_x2 + handle_offset, scaled_y2 + handle_offset),
                's':  (scaled_x1 + (scaled_x2 - scaled_x1) // 2 - handle_offset, scaled_y2 - handle_offset,
                       scaled_x1 + (scaled_x2 - scaled_x1) // 2 + handle_offset, scaled_y2 + handle_offset),
                'sw': (scaled_x1 - handle_offset, scaled_y2 - handle_offset, scaled_x1 + handle_offset, scaled_y2 + handle_offset),
                'w':  (scaled_x1 - handle_offset, scaled_y1 + (scaled_y2 - scaled_y1) // 2 - handle_offset,
                       scaled_x1 + handle_offset, scaled_y1 + (scaled_y2 - scaled_y1) // 2 + handle_offset)
            }

            for handle_name, coords in handles.items():
                handle_id = self.canvas.create_rectangle(
                    coords[0], coords[1], coords[2], coords[3],
                    fill="yellow",
                    outline="red",
                    width=2,
                    tags=("handle", handle_name)
                )
                self.handles[handle_name] = handle_id

        except Exception as e:
            print(f"绘制选框失败: {e}")

def show_crop_dialog(parent, image_path=None, image_paths=None, current_index=0):
    """显示裁剪对话框的便捷函数"""
    dialog = CropDialog(parent, image_path, image_paths, current_index)
    return dialog.show()

```

[回到目录](#目录)

---

<a name="file-guigifpreview_guipy"></a>
## 19. gui\gifpreview_gui.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\gui\gifpreview_gui.py`

```python
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
GIF预览模块
包含GIF动画预览相关的界面和功能
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class GifPreviewWindow:
    """GIF预览窗口"""

    def __init__(self, parent, frames, duration, output_path, loop=0):
        self.frames = frames
        self.duration = duration
        self.output_path = output_path
        self.loop = loop  # 循环次数，0表示无限循环
        self.current_frame_index = 0
        self.is_playing = False
        self.animation_id = None
        self.zoom_scale = 1.0  # 缩放比例
        self.photo_cache = {}  # 缓存所有帧的PhotoImage对象，防止被垃圾回收
        self.photo = None  # 当前显示的PhotoImage对象

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("GIF Preview")

        # 使用与主界面相同的窗口尺寸
        self.window_width = 1366
        self.window_height = 768

        # 设置窗口大小限制
        self.window.minsize(1366, 768)
        self.window.maxsize(1920, 1080)

        # 直接使用固定尺寸，不根据图片调整
        self.window.geometry(f"{self.window_width}x{self.window_height}")

        # 先隐藏窗口，防止闪烁
        self.window.withdraw()

        # 设置窗口图标
        self.set_window_icon()

        # 创建UI
        self.setup_ui()

        # 显示第一帧
        self.display_frame(0)

        # 默认适应窗口
        self.fit_to_window()

        # 居中显示并恢复窗口显示
        self.center_window()
        self.window.deiconify()

        # 确保窗口显示在最前面
        self.window.lift()
        self.window.focus_force()

        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_window_icon(self):
        """设置窗口图标"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'gif.png')
            if os.path.exists(icon_path):
                self.window.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception:
            pass

    def center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()

        # 如果窗口还没有显示，使用保存的窗口尺寸
        if width <= 1 or height <= 1:
            width = self.window_width
            height = self.window_height

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置主框架的网格权重，让图片显示区域获得大部分垂直空间
        main_frame.rowconfigure(0, weight=1)  # 图片显示区域
        main_frame.rowconfigure(1, weight=0)  # 控制区域1
        main_frame.rowconfigure(2, weight=0)  # 控制区域2
        main_frame.rowconfigure(3, weight=0)  # 持续时间区域
        main_frame.columnconfigure(0, weight=1)

        # 图片显示区域 - 使用Canvas和Scrollbar实现滚动功能
        self.canvas_frame = ttk.Frame(main_frame)
        self.canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)

        # 创建Canvas和滚动条
        self.canvas = tk.Canvas(self.canvas_frame, bg='#313337')
        self.scroll_y = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # 布局Canvas和滚动条 - 使用grid管理器
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 直接在Canvas上显示图片，不使用额外的Frame容器
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.CENTER, image=None)

        # 绑定事件以更新滚动区?        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mousewheel)   # Linux
        self.canvas.bind("<Button-5>", self.on_mousewheel)   # Linux

        # 控制区域 - 第一行：播放控制和进度条
        control_frame1 = ttk.Frame(main_frame)
        control_frame1.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 5))

        # 创建一个居中容器
        center_container1 = ttk.Frame(control_frame1)
        center_container1.pack(expand=True)

        # 播放/停止按钮
        self.play_button = ttk.Button(center_container1, text="▶", command=self.toggle_play, width=5)
        self.play_button.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(self.play_button, "播放")

        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_scale = ttk.Scale(
            center_container1,
            from_=0,
            to=len(self.frames) - 1,
            variable=self.progress_var,
            orient=tk.HORIZONTAL,
            command=self.on_progress_change,
            length=200  # 设置进度条长度，与第二行对齐
        )
        self.progress_scale.pack(side=tk.LEFT, padx=(0, 10))

        # 当前帧显示
        self.frame_label = ttk.Label(center_container1, text="0 / 0", width=10)
        self.frame_label.pack(side=tk.LEFT, padx=(0, 10))

        # 控制区域 - 第二行：帧导航和缩放控制
        control_frame2 = ttk.Frame(main_frame)
        control_frame2.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 5))

        # 创建一个居中容器
        center_container2 = ttk.Frame(control_frame2)
        center_container2.pack(expand=True)

        # 左侧容器：持续时间调节和保存按钮
        left_container = ttk.Frame(center_container2)
        left_container.pack(side=tk.LEFT)

        ttk.Label(left_container, text="每帧时间(ms):").pack(side=tk.LEFT, padx=(0, 5))
        self.duration_var = tk.IntVar(value=self.duration)
        self.duration_spin = ttk.Spinbox(
            left_container,
            from_=50,
            to=2000,
            increment=50,
            textvariable=self.duration_var,
            width=5,
            command=self.on_duration_change
        )
        self.duration_spin.pack(side=tk.LEFT, padx=(0, 10))

        # 循环次数设置
        ttk.Label(left_container, text="循环次数(0=无限):").pack(side=tk.LEFT, padx=(0, 5))
        self.loop_var = tk.IntVar(value=self.loop)
        self.loop_spin = ttk.Spinbox(
            left_container,
            from_=0,
            to=999,
            textvariable=self.loop_var,
            width=5
        )
        self.loop_spin.pack(side=tk.LEFT, padx=(0, 10))

        # 分隔线
        ttk.Separator(left_container, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 保存按钮
        save_button = ttk.Button(left_container, text="💾", command=self.save_gif, width=5)
        save_button.pack(side=tk.LEFT)
        self.create_tooltip(save_button, "保存GIF")

        # 分隔线
        ttk.Separator(center_container2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 中间容器：帧导航按钮（居中）
        middle_container = ttk.Frame(center_container2)
        middle_container.pack(side=tk.LEFT, expand=True)

        btn_first = ttk.Button(middle_container, text="⏮", command=self.first_frame, width=5)
        btn_first.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_first, "第一帧")

        btn_prev = ttk.Button(middle_container, text="◀", command=self.previous_frame, width=5)
        btn_prev.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_prev, "上一帧")

        btn_next = ttk.Button(middle_container, text="▶", command=self.next_frame, width=5)
        btn_next.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_next, "下一帧")

        btn_last = ttk.Button(middle_container, text="⏭", command=self.last_frame, width=5)
        btn_last.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_last, "最后一帧")

        # 分隔线
        ttk.Separator(center_container2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 右侧容器：缩放控制按钮
        right_container = ttk.Frame(center_container2)
        right_container.pack(side=tk.LEFT)

        btn_zoom_in = ttk.Button(right_container, text="🔍+", command=self.zoom_in, width=5)
        btn_zoom_in.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_in, "放大画面")

        btn_zoom_out = ttk.Button(right_container, text="🔍-", command=self.zoom_out, width=5)
        btn_zoom_out.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_out, "缩小画面")

        btn_reset_zoom = ttk.Button(right_container, text="🔄", command=self.reset_zoom, width=5)
        btn_reset_zoom.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_reset_zoom, "原始大小")

        btn_fit_window = ttk.Button(right_container, text="⬜", command=self.fit_to_window, width=5)
        btn_fit_window.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_fit_window, "适应窗口")

        # 更新帧数显示
        self.update_frame_label()

    def on_canvas_configure(self, event):
        """当canvas大小改变时更新滚动区域"""
        pass  # 滚动区域由display_frame方法管理

    def on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        # 检查是否按下了Ctrl键
        ctrl_pressed = event.state & 0x4  # Ctrl键的位掩码
        if ctrl_pressed:
            # Ctrl+滚轮：缩放图片
            if event.delta > 0 or event.num == 4:
                # 向上滚动：放大
                self.zoom_in()
            elif event.delta < 0 or event.num == 5:
                # 向下滚动：缩小
                self.zoom_out()
        else:
            # 普通滚轮：滚动查看
            # 检查滚动区域是否大于Canvas可视区域，如果是则允许滚动
            bbox = self.canvas.bbox("all")
            if bbox:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()

                # 如果图片的宽度或高度大于Canvas的可视区域，则允许滚动
                if bbox[2] > canvas_width or bbox[3] > canvas_height:
                    # 检查操作系统类型来确定滚动方向
                    if event.num == 4 or event.delta > 0:
                        # 向上滚动 - 水平滚动向左
                        self.canvas.xview_scroll(-1, "units")
                    elif event.num == 5 or event.delta < 0:
                        # 向下滚动 - 水平滚动向右
                        self.canvas.xview_scroll(1, "units")

    def create_tooltip(self, widget, text):
        """创建鼠标悬浮提示"""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+0+0")
        tooltip_label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("tahoma", "8", "normal"))
        tooltip_label.pack()

        def enter(event):
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + 25
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def display_frame(self, frame_index):
        """显示指定帧"""
        if 0 <= frame_index < len(self.frames):
            frame = self.frames[frame_index]

            # 获取原始图片尺寸
            orig_width, orig_height = frame.size

            # 计算基础缩放比例（使用当前窗口大小，考虑控制栏空间）
            self.canvas_frame.update_idletasks()
            # 获取canvas的实际可用空间
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # 减去滚动条的空间
            scrollbar_width = 15  # 滚动条宽度估计值
            max_width = canvas_width - scrollbar_width - 20 if canvas_width > 0 else orig_width
            max_height = canvas_height - scrollbar_width - 20 if canvas_height > 0 else orig_height

            if max_width < 50:
                max_width = orig_width
            if max_height < 50:
                max_height = orig_height

            # 计算基础缩放比例，保持宽高比（用于初始适应窗口）
            base_scale = min(max_width / orig_width, max_height / orig_height)

            # 应用缩放比例：当zoom_scale为1.0时，始终使用原始尺寸显示
            # 这样可以保证100%缩放时显示原始尺寸，即使图片大于窗口
            if self.zoom_scale == 1.0:
                scale = 1.0  # 始终显示原始尺寸
            else:
                # 用户手动缩放时，基于原始尺寸进行缩放
                scale = self.zoom_scale

            # 计算实际显示尺寸
            display_width = int(orig_width * scale)
            display_height = int(orig_height * scale)

            # 创建缓存键，包含帧索引和显示尺寸（使用整数避免浮点数精度问题）
            cache_key = (frame_index, display_width, display_height)

            # 检查缓存中是否已有该帧的PhotoImage
            if cache_key in self.photo_cache:
                self.photo = self.photo_cache[cache_key]
            else:
                # 调整图片大小，根据缩放方向选择合适的插值算法
                frame_copy = frame.copy()
                if scale >= 1.0:
                    # 放大时使用高质量插值，保持清晰
                    resampling = Image.Resampling.LANCZOS
                else:
                    # 缩小时使用双线性插值，提高性能
                    resampling = Image.Resampling.BILINEAR
                frame_copy = frame_copy.resize((display_width, display_height), resampling)

                # 转换为PhotoImage并缓存
                self.photo = ImageTk.PhotoImage(frame_copy)
                self.photo_cache[cache_key] = self.photo

            # 先更新Canvas上的图片
            self.canvas.itemconfig(self.image_id, image=self.photo)

            # 更新Canvas上的图片位置和锚点
            # 当图片大于窗口时，将图片放置在左上角(0, 0)，方便滚动查看
            # 当图片小于窗口时，将图片居中显示
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if display_width > canvas_width or display_height > canvas_height:
                # 图片大于窗口，放置在左上角（使用NW锚点）
                self.canvas.itemconfig(self.image_id, anchor=tk.NW)
                self.canvas.coords(self.image_id, 0, 0)
            else:
                # 图片小于窗口，居中显示（使用CENTER锚点）
                self.canvas.itemconfig(self.image_id, anchor=tk.CENTER)
                center_x = canvas_width // 2
                center_y = canvas_height // 2
                self.canvas.coords(self.image_id, center_x, center_y)

            # 更新当前帧索引
            self.current_frame_index = frame_index
            self.progress_var.set(frame_index)
            self.update_frame_label()

            # 更新滚动区域 - 确保滚动区域包含整个图片
            # 使用after确保在所有UI更新完成后设置滚动区域
            self.canvas.after(10, lambda: self.canvas.configure(scrollregion=(0, 0, display_width, display_height)))

    def update_frame_label(self):
        """更新帧数显示"""
        self.frame_label.configure(text=f"{self.current_frame_index + 1} / {len(self.frames)}")

    def first_frame(self):
        """跳转到第一帧"""
        self.display_frame(0)

    def previous_frame(self):
        """跳转到上一帧"""
        if self.current_frame_index > 0:
            self.display_frame(self.current_frame_index - 1)

    def next_frame(self):
        """跳转到下一帧"""
        if self.current_frame_index < len(self.frames) - 1:
            self.display_frame(self.current_frame_index + 1)

    def last_frame(self):
        """跳转到最后一帧"""
        self.display_frame(len(self.frames) - 1)

    def zoom_in(self):
        """放大画面"""
        # 检查放大后是否会超出边界
        if self.zoom_scale < 10.0:  # 设置最大缩放倍数
            self.zoom_scale *= 1.25
            # 清除缓存，因为缩放比例改变了
            self.photo_cache.clear()
            self.photo = None  # 清除当前图片引用
            self.display_frame(self.current_frame_index)

    def zoom_out(self):
        """缩小画面"""
        if self.zoom_scale > 0.1:  # 设置最小缩放倍数
            self.zoom_scale /= 1.25
            # 清除缓存，因为缩放比例改变了
            self.photo_cache.clear()
            self.photo = None  # 清除当前图片引用
            self.display_frame(self.current_frame_index)

    def reset_zoom(self):
        """原始大小 - 按图片原始尺寸显示"""
        self.zoom_scale = 1.0
        # 清除缓存，因为缩放比例改变了
        self.photo_cache.clear()
        self.photo = None  # 清除当前图片引用
        self.display_frame(self.current_frame_index)

    def fit_to_window(self):
        """让图片适应窗口大小"""
        if not self.frames:
            return

        # 获取当前帧的原始尺寸
        current_frame = self.frames[self.current_frame_index]
        orig_width, orig_height = current_frame.size

        # 获取Canvas的实际尺寸
        self.canvas_frame.update_idletasks()
        canvas_width = self.canvas.winfo_width() - 20  # 减去padding
        canvas_height = self.canvas.winfo_height() - 20  # 减去padding

        # 确保Canvas有合理的尺寸
        if canvas_width < 50:
            canvas_width = orig_width
        if canvas_height < 50:
            canvas_height = orig_height

        # 计算适应窗口的缩放比例
        scale_width = canvas_width / orig_width
        scale_height = canvas_height / orig_height
        fit_scale = min(scale_width, scale_height)  # 保持宽高比
        # 更新缩放比例
        self.zoom_scale = fit_scale
        # 清除缓存，因为缩放比例改变了
        self.photo_cache.clear()
        self.photo = None  # 清除当前图片引用
        self.display_frame(self.current_frame_index)

    def on_duration_change(self):
        """持续时间变化回调"""
        try:
            self.duration = self.duration_var.get()
        except ValueError:
            self.duration_var.set(self.duration)

    def toggle_play(self):
        """切换播放/暂停状态"""
        if self.is_playing:
            self.stop()
        else:
            self.play()

    def play(self):
        """开始播放"""
        self.is_playing = True
        self.play_button.configure(text="⏸")
        self.create_tooltip(self.play_button, "暂停")
        self.animate()

    def stop(self):
        """停止播放"""
        self.is_playing = False
        self.play_button.configure(text="▶")
        self.create_tooltip(self.play_button, "播放")
        if self.animation_id:
            self.window.after_cancel(self.animation_id)
            self.animation_id = None

    def animate(self):
        """动画播放"""
        if not self.is_playing:
            return

        # 移动到下一帧
        next_frame = (self.current_frame_index + 1) % len(self.frames)
        self.display_frame(next_frame)

        # 继续播放，使用当前的持续时间
        self.animation_id = self.window.after(self.duration_var.get(), self.animate)

    def on_progress_change(self, value):
        """进度条拖动回调"""
        frame_index = int(float(value))
        if frame_index != self.current_frame_index:
            self.display_frame(frame_index)

    def save_gif(self):
        """保存GIF"""
        # 如果没有设置输出文件路径，或路径不包含目录部分，弹出文件保存对话框
        import os
        if not self.output_path or not os.path.dirname(self.output_path):
            from tkinter import filedialog
            import datetime
            
            # 生成默认文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"animation_{timestamp}.gif"
            
            # 弹出文件保存对话框
            selected_file = filedialog.asksaveasfilename(
                title="选择输出文件",
                initialfile=default_filename,
                defaultextension=".gif",
                filetypes=[
                    ("GIF files", "*.gif"),
                    ("All files", "*.*")
                ]
            )
            
            if not selected_file:
                return  # 用户取消了选择
            
            self.output_path = selected_file

        try:
            from function.gif_operations import save_gif as ops_save_gif
            ops_save_gif(self.frames, self.output_path, self.duration_var.get(), self.loop_var.get())
            messagebox.showinfo("成功", f"GIF已保存到:\n{self.output_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存GIF失败:\n{str(e)}")

    def on_close(self):
        """窗口关闭事件"""
        self.stop()
        self.window.destroy()

```

[回到目录](#目录)

---

<a name="file-guimain_windowpy"></a>
## 20. gui\main_window.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\gui\main_window.py`

```python
# -*- coding: utf-8 -*-
"""
GIF Maker GUI主窗口模块
这个模块实现了GIF制作工具的图形用户界面，包括图片选择、参数设置、预览和GIF生成功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入功能模块
from function.image_utils import load_image, get_image_info, resize_image, create_photo_image, calculate_scale_to_fit, calculate_scale_to_fill
from function.crop import crop_image
from function.history_manager import HistoryManager
from function.file_manager import get_image_files, validate_image_path, get_file_size_kb
from function.gif_operations import create_gif
from function.file_manager import calculate_total_time, validate_gif_params, estimate_gif_size


class GifMakerGUI:
    def __init__(self, root):
        """
        初始化GIF Maker GUI主窗口
        Args:
            root: Tkinter根窗口对象
        """
        self.root = root
        self.root.title("GIF Maker")
        self.root.geometry("800x600")

        # 隐藏窗口，等待所有组件初始化完成后再显示
        self.root.withdraw()

        # 设置窗口大小限制
        self.root.minsize(1366, 768)
        self.root.maxsize(1920, 1080)

        # 设置窗口图标
        self.set_window_icon()

        # 初始化变量
        self.image_paths = []  # 存储所有图片路径
        self.output_path = tk.StringVar()  # 输出文件路径
        # 设置默认输出文件名
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"animation_{timestamp}.gif"
        self.output_path.set(default_filename)
        self.duration = tk.IntVar(value=100)  # GIF每帧持续时间，默认100ms
        self.loop = tk.IntVar(value=0)  # 循环次数，0表示无限循环
        self.optimize = tk.BooleanVar(value=True)  # 是否优化GIF
        self.resize_width = tk.StringVar()  # 调整宽度
        self.resize_height = tk.StringVar()  # 调整高度
        self.current_photo = None  # 当前PhotoImage对象
        self.preview_scale = 1.0  # 预览缩放比例
        self.preview_photos = []  # 存储所有PhotoImage对象
        self.image_rects = []  # 存储所有图片的矩形区域信息
        self.selected_image_index = -1  # 当前选中的图片索引
        self.selected_image_indices = set()  # 多选图片索引集合
        self.last_selected_index = -1  # 上一次选中的图片索引（用于Shift多选）
        self.clipboard_images = []  # 剪贴板图片列表
        self.clipboard_action = None  # 剪贴板操作类型：'copy'或'cut'

        # 初始化历史管理器
        self.history_manager = HistoryManager(max_history=50)

        # 待保存的裁剪图片
        self.pending_crops = {}  # 格式：{图片路径: PIL.Image对象}
        self.pending_crop_coords = {}  # 格式：{图片路径: (x1, y1, x2, y2)}

        # 设置UI和菜单
        self.setup_ui()
        self.setup_menu()

        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_resize)

        # 绑定窗口关闭事件
        from function.history_manager import on_window_close
        self.root.protocol('WM_DELETE_WINDOW', lambda: on_window_close(self))

        # 居中显示窗口（UI初始化完成后）
        self.center_window()

    def perform_undo(self):
        """执行撤销操作"""
        try:
            from function.history_manager import undo
            undo(self)
        except Exception as e:
            print(f"撤销失败: {e}")

    def perform_redo(self):
        """执行重做操作"""
        try:
            from function.history_manager import redo
            redo(self)
        except Exception as e:
            print(f"重做失败: {e}")

    def preview_gif(self):
        """预览生成的GIF动画"""
        try:
            from function.preview import preview_gif
            preview_gif(self)
        except Exception as e:
            messagebox.showerror("错误", f"预览GIF失败: {str(e)}")

    def browse_output(self):
        """浏览输出目录"""
        try:
            from function.ui_operations import browse_output
            browse_output(self)
        except Exception as e:
            messagebox.showerror("错误", f"浏览输出目录失败: {str(e)}")

    def refresh_preview(self):
        """刷新预览显示"""
        try:
            self.display_grid_preview()
        except Exception as e:
            print(f"刷新预览失败: {e}")

    def set_window_icon(self):
        """设置窗口图标，从项目icons目录中加载gif.png作为窗口图标"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'gif.png')
            if os.path.exists(icon_path):
                self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception:
            pass

    def on_window_resize(self, event):
        """窗口大小变化时的回调函数，当窗口大小改变时，重新调整预览区域的布局"""
        # 只处理根窗口的大小变化事件
        if event.widget == self.root and (event.width != getattr(self, '_last_width', 0) or event.height != getattr(self, '_last_height', 0)):
            # 记录当前窗口大小
            self._last_width = event.width
            self._last_height = event.height

            # 使用防抖机制，避免频繁刷新
            if not hasattr(self, '_resize_timer'):
                self._resize_timer = None
            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(100, self.refresh_preview)

    def center_window(self):
        """将窗口居中显示，计算屏幕中心坐标并将窗口移动到该位置"""
        # 更新窗口信息
        self.root.update_idletasks()

        # 获取窗口尺寸
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # 计算居中位置
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)

        # 设置窗口位置并显示
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()
        self.root.update_idletasks()

    def setup_menu(self):
        """设置菜单栏，创建文件菜单和帮助菜单，并绑定相应的功能"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        from function.file_manager import select_images, select_directory
        file_menu.add_command(label="选择图片", command=lambda: select_images(self))
        file_menu.add_command(label="选择目录", command=lambda: select_directory(self))
        file_menu.add_separator()
        file_menu.add_command(label="设置输出文件...", command=self.browse_output, accelerator="Alt+O")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

        # 绑定快捷键
        from function.ui_operations import browse_output
        self.root.bind('<Alt-o>', lambda e: browse_output(self))

    def show_about(self):
        """显示关于对话框，显示应用程序的基本信息和功能说明"""
        messagebox.showinfo("关于", "GIF制作工具 v1.0\n\n将多张图片转换为GIF动画\n支持自定义持续时间、循环次数、尺寸调整等功能")

    def setup_ui(self):
        """设置用户界面，创建并布局所有GUI组件，包括工具栏、参数设置区、预览区和状态栏"""
        # 配置主窗口的行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置主框架的行列权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # 图片操作工具栏
        image_frame = ttk.Frame(main_frame, padding="5")
        image_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # 选择图片文件按钮
        from function.file_manager import select_images
        btn_select_files = ttk.Button(image_frame, text="📁", command=lambda: select_images(self), width=5)
        btn_select_files.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_select_files, "选择图片文件")

        # 选择图片目录按钮
        from function.file_manager import select_directory
        btn_select_dir = ttk.Button(image_frame, text="📂", command=lambda: select_directory(self), width=5)
        btn_select_dir.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_select_dir, "选择图片目录")

        # 文件列表下拉框
        self.file_list_var = tk.StringVar()
        self.file_combobox = ttk.Combobox(
            image_frame,
            textvariable=self.file_list_var,
            state='readonly',
            width=20
        )
        self.file_combobox.pack(side=tk.LEFT, padx=(0, 5))
        from function.ui_operations import on_file_selected
        self.file_combobox.bind('<<ComboboxSelected>>', lambda e: on_file_selected(self, e))

        # 清空列表按钮
        from function.file_manager import clear_images
        btn_clear_list = ttk.Button(image_frame, text="🗑", command=lambda: clear_images(self), width=5)
        btn_clear_list.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_clear_list, "清空列表")

        # 分隔线
        ttk.Separator(image_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 撤销按钮
        btn_undo = ttk.Button(image_frame, text="↶", command=lambda: self.perform_undo(), width=5)
        btn_undo.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_undo, "撤销 (Ctrl+Z)")

        # 重做按钮
        btn_redo = ttk.Button(image_frame, text="↷", command=lambda: self.perform_redo(), width=5)
        btn_redo.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_redo, "重做 (Ctrl+Y)")

        # 保存裁剪按钮
        from function.history_manager import save_pending_crops
        btn_save = ttk.Button(image_frame, text="💾", command=lambda: save_pending_crops(self), width=5)
        btn_save.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_save, "保存裁剪 (Ctrl+S)")

        # 分隔线
        ttk.Separator(image_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 控制按钮框架
        control_frame = ttk.Frame(image_frame)
        control_frame.pack(side=tk.LEFT, padx=(0, 0))

        # 预览GIF按钮
        btn_preview_gif = ttk.Button(control_frame, text="🎬", command=self.preview_gif, width=5)
        btn_preview_gif.pack(side=tk.LEFT, padx=(0, 3))
        self.create_tooltip(btn_preview_gif, "预览GIF")

        # 分隔线
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 缩放控制按钮
        from function.preview import zoom_in_preview, zoom_out_preview, reset_preview_zoom, fit_preview_to_window
        btn_zoom_out = ttk.Button(control_frame, text="🔍-", command=lambda: zoom_out_preview(self), width=5)
        btn_zoom_out.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_out, "缩小预览")

        btn_zoom_in = ttk.Button(control_frame, text="🔍+", command=lambda: zoom_in_preview(self), width=5)
        btn_zoom_in.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_zoom_in, "放大预览")

        btn_reset_zoom = ttk.Button(control_frame, text="🔄", command=lambda: reset_preview_zoom(self), width=5)
        btn_reset_zoom.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_reset_zoom, "原始大小")

        btn_fit_window = ttk.Button(control_frame, text="⬜", command=lambda: fit_preview_to_window(self), width=5)
        btn_fit_window.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(btn_fit_window, "适应窗口")

        # 缩放比例输入框
        self.zoom_entry = ttk.Entry(control_frame, width=4)
        self.zoom_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.zoom_entry.insert(0, "100")  # 默认100%
        from function.preview import apply_manual_zoom
        self.zoom_entry.bind('<Return>', lambda e: apply_manual_zoom(self, e))
        self.create_tooltip(self.zoom_entry, "输入缩放百分比，按回车确认")

        # 百分比标签
        ttk.Label(control_frame, text="%").pack(side=tk.LEFT, padx=(0, 5))

        # 图片预览区域
        preview_outer_frame = ttk.LabelFrame(main_frame, text="图片预览", padding="1")
        preview_outer_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(1, 0))
        preview_outer_frame.columnconfigure(0, weight=1)
        preview_outer_frame.rowconfigure(0, weight=1)

        # 预览框架 - 包含Canvas和滚动条
        self.preview_frame = ttk.Frame(preview_outer_frame)
        self.preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)

        # 创建Canvas和滚动条
        self.preview_canvas = tk.Canvas(self.preview_frame, bg='#313337', highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.preview_canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.preview_canvas.xview)
        self.preview_canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # 启用拖拽功能
        self.preview_canvas.drop_target_register(DND_FILES)
        self.preview_canvas.dnd_bind('<<Drop>>', self.on_drop_files)

        # 布局Canvas和滚动条
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 在Canvas中创建一个图片占位符
        self.preview_image_id = self.preview_canvas.create_image(0, 0, anchor=tk.CENTER, image=None)

        # 绑定Canvas事件
        from function.preview import on_preview_canvas_configure, on_preview_mousewheel
        self.preview_canvas.bind("<Configure>", lambda e: on_preview_canvas_configure(self, e))
        self.preview_canvas.bind("<MouseWheel>", lambda e: on_preview_mousewheel(self, e))  # Windows
        self.preview_canvas.bind("<Button-4>", lambda e: on_preview_mousewheel(self, e))   # Linux
        self.preview_canvas.bind("<Button-5>", lambda e: on_preview_mousewheel(self, e))   # Linux
        self.preview_canvas.bind("<Button-3>", self.on_preview_right_click)

        # 绑定全局快捷键
        self.root.bind("<Control-a>", self.select_all_images)  # Ctrl+A 全选
        from function.history_manager import undo, redo
        self.root.bind("<Control-z>", lambda e: undo(self))  # Ctrl+Z 撤销
        self.root.bind("<Control-y>", lambda e: redo(self))  # Ctrl+Y 重做
        self.root.bind("<Control-s>", lambda e: save_pending_crops(self))  # Ctrl+S 保存

        # 初始化拖拽相关变量
        self.dragging_image_index = -1  # 当前拖拽的图片索引
        self.drag_source_index = -1  # 拖拽源索引
        self.drag_start_pos = None  # 拖拽起始位置
        self.drag_preview_image = None  # 拖拽预览图片
        self.drag_preview_photo = None  # 拖拽预览PhotoImage
        self.insert_cursor = None  # 插入光标
        self.insert_index = -1  # 插入位置索引

        # 绑定鼠标拖拽事件
        self.preview_canvas.bind("<ButtonPress-1>", self.on_preview_left_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_preview_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_preview_release)

        # 状态栏
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(1, 0))
        self.status_frame.columnconfigure(1, weight=1)

        # 总时间标签
        self.total_time_label = ttk.Label(self.status_frame, text="总时间: --", anchor=tk.W)
        self.total_time_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        # GIF大小标签
        self.gif_size_label = ttk.Label(self.status_frame, text="GIF: --", anchor=tk.W)
        self.gif_size_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))

        # 当前图片信息标签
        self.current_img_size_label = ttk.Label(self.status_frame, text="当前图片: --", anchor=tk.W)
        self.current_img_size_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        # 缩放比例标签
        self.zoom_label = ttk.Label(self.status_frame, text="缩放: 100%", anchor=tk.E)
        self.zoom_label.grid(row=0, column=3, sticky=tk.E, padx=(0, 5))

    def create_tooltip(self, widget, text):
        """
        创建鼠标悬浮提示，为指定控件添加工具提示功能
        Args:
            widget: 需要添加提示的控件对象
            text: 提示文本内容
        """
        def enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes("-topmost", True)
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid",
                            borderwidth=1, font=("tahoma", "8", "normal"))
            label.pack()

            # 设置提示框位置
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")

            # 保存tooltip引用，避免被垃圾回收
            widget._tooltip = tooltip

        def leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def preview_first_image(self):
        """预览第一张选中的图片，显示图片列表中的第一张图片到预览区域"""
        if not self.image_paths:
            messagebox.showwarning("提示", "请先选择图片")
            return

        from function.preview import refresh_preview
        refresh_preview(self)
        from function.ui_operations import update_status_info
        update_status_info(self)

    def preview_specific_image(self, index):
        """
        预览指定索引的图片，显示图片列表中指定索引位置的图片到预览区域
        Args:
            index: 图片在列表中的索引
        """
        if not self.image_paths or index < 0 or index >= len(self.image_paths):
            return

        try:
            # 加载图片
            img_path = self.image_paths[index]
            img = Image.open(img_path)

            # 获取原始尺寸
            orig_width, orig_height = img.size

            # 直接使用全局的预览缩放比例
            scale = self.preview_scale

            # 计算缩放后的尺寸
            scaled_width = int(orig_width * scale)
            scaled_height = int(orig_height * scale)

            # 根据缩放方向选择合适的插值算法
            if scale >= 1.0:
                resampling = Image.Resampling.LANCZOS
            else:
                resampling = Image.Resampling.BILINEAR
            img_resized = img.resize((scaled_width, scaled_height), resampling)

            # 转换为Tkinter PhotoImage对象
            self.current_photo = ImageTk.PhotoImage(img_resized)

            # 尝试获取现有图片项的坐标，如果失败则重新创建
            try:
                self.preview_canvas.coords(self.preview_image_id)
            except tk.TclError:
                # 如果图片项不存在，重新创建
                self.preview_image_id = self.preview_canvas.create_image(0, 0, anchor=tk.CENTER, image=None)

            # 更新Canvas中的图片
            self.preview_canvas.itemconfig(self.preview_image_id, image=self.current_photo)

            # 根据图片大小调整位置
            # 如果图片大于Canvas，使用左上角对齐
            # 如果图片小于Canvas，使用居中对齐
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            if scaled_width > canvas_width or scaled_height > canvas_height:
                # 图片较大，使用左上角对齐
                self.preview_canvas.itemconfig(self.preview_image_id, anchor=tk.NW)
                self.preview_canvas.coords(self.preview_image_id, 0, 0)
            else:
                # 图片较小，使用居中对齐
                self.preview_canvas.itemconfig(self.preview_image_id, anchor=tk.CENTER)
                center_x = canvas_width // 2
                center_y = canvas_height // 2
                self.preview_canvas.coords(self.preview_image_id, center_x, center_y)

            # 更新滚动区域 - 使用after确保Canvas已更新
            self.preview_canvas.after(10, lambda: self.preview_canvas.configure(scrollregion=(0, 0, scaled_width, scaled_height)))

        except Exception as e:
            messagebox.showerror("错误", f"无法预览图片: {str(e)}")

    def display_grid_preview(self, update_combobox=True):
        """
        以网格方式显示所有图片，从上到下，从左到右排列，根据图片尺寸调节每列的图片数
        
        Args:
            update_combobox: 是否更新下拉框的值（默认为True）
        """
        # 清空Canvas和缓存
        self.preview_canvas.delete("all")
        self.image_rects.clear()
        self.preview_photos.clear()  # 清空PhotoImage列表

        # 更新文件列表下拉框（仅在需要时更新）
        if update_combobox and self.image_paths:
            file_names = [os.path.basename(p) for p in self.image_paths]
            self.file_combobox['values'] = file_names
            if self.selected_image_index >= 0 and self.selected_image_index < len(file_names):
                self.file_combobox.current(self.selected_image_index)
            elif len(file_names) > 0:
                self.file_combobox.current(0)
        elif update_combobox:
            self.file_combobox['values'] = []
            self.file_combobox.set('')

        if not self.image_paths:
            return

        # 计算网格布局
        from function.image_utils import calculate_grid_layout
        layout_data = calculate_grid_layout(
            self.image_paths,
            self.pending_crops,
            self.preview_scale
        )

        if not layout_data:
            return

        # 获取Canvas实际尺寸
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        # 重新计算布局，使用实际的Canvas尺寸
        layout_data = calculate_grid_layout(
            self.image_paths,
            self.pending_crops,
            self.preview_scale,
            canvas_width=canvas_width,
            canvas_height=canvas_height
        )

        # 遍历布局数据，显示每张图片
        for item in layout_data:
            img_path = item['path']
            x, y = item['position']
            size = item['size']

            # 如果图片已裁剪，使用裁剪后的图片
            if img_path in self.pending_crops:
                img = self.pending_crops[img_path]
            else:
                img = load_image(img_path)

            if img:
                # 调整图片大小
                img_resized = resize_image(img, size[0], size[1])
                photo = create_photo_image(img_resized)
                self.preview_photos.append(photo)

                # 在Canvas上显示图片
                self.preview_canvas.create_image(x, y, image=photo, anchor=tk.NW, tags=f"image_{item['index']}")

                # 为所有图片添加细边框
                self.preview_canvas.create_rectangle(
                    x, y, x + size[0], y + size[1],
                    outline="#CCCCCC",
                    width=1,
                    tags=f"border_{item['index']}"
                )

                # 保存图片矩形区域信息
                rect = {
                    'index': item['index'],
                    'x1': x,
                    'y1': y,
                    'x2': x + size[0],
                    'y2': y + size[1],
                    'path': img_path
                }
                self.image_rects.append(rect)

                # 显示图片序号
                self.preview_canvas.create_text(
                    x + 5, y + 5,
                    text=f"#{item['index'] + 1}",
                    fill="white",
                    font=("Arial", 10, "bold"),
                    anchor=tk.NW,
                    tags=f"label_{item['index']}"
                )

                # 显示文件名（截断过长的文件名）
                filename = os.path.splitext(os.path.basename(img_path))[0]
                max_filename_length = max(5, size[0] // 8)
                if len(filename) > max_filename_length:
                    filename = filename[:max_filename_length - 3] + "..."

                font_size = max(7, min(10, size[1] // 15))

                self.preview_canvas.create_text(
                    x + size[0] - 5, y + 5,
                    text=filename,
                    fill="white",
                    font=("Arial", font_size),
                    anchor=tk.NE,
                    tags=f"filename_{item['index']}"
                )

        # 更新滚动区域
        if self.image_rects:
            max_x = max(r['x2'] for r in self.image_rects)
            max_y = max(r['y2'] for r in self.image_rects)
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            scroll_width = max(canvas_width, max_x + 10)
            scroll_height = max(max_y + 10, canvas_height)
            self.preview_canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))

        # 绘制选中框
        if self.selected_image_indices:
            self.draw_selection_boxes()

        # 滚动到选中的图片
        if self.selected_image_index >= 0 and self.selected_image_index < len(self.image_rects):
            self.scroll_to_image(self.selected_image_index)

    def scroll_to_image(self, image_index):
        """
        滚动到指定索引的图片，确保该图片在可视区域内
        Args:
            image_index: 图片索引
        """
        if image_index < 0 or image_index >= len(self.image_rects):
            return

        rect = self.image_rects[image_index]
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        # 获取当前滚动位置
        scroll_x = self.preview_canvas.canvasx(0)
        scroll_y = self.preview_canvas.canvasy(0)

        # 计算图片中心点
        img_center_x = (rect['x1'] + rect['x2']) / 2
        img_center_y = (rect['y1'] + rect['y2']) / 2

        # 计算目标滚动位置（使图片居中）
        target_x = max(0, img_center_x - canvas_width / 2)
        target_y = max(0, img_center_y - canvas_height / 2)

        # 获取滚动区域的总尺寸
        scrollregion = self.preview_canvas.cget("scrollregion")
        if scrollregion:
            parts = scrollregion.split()
            if len(parts) == 4:
                max_scroll_x = float(parts[2])
                max_scroll_y = float(parts[3])

                # 计算滚动比例
                scroll_x_ratio = target_x / max_scroll_x
                scroll_y_ratio = target_y / max_scroll_y

                # 限制滚动比例在 0-1 之间
                scroll_x_ratio = max(0, min(1, scroll_x_ratio))
                scroll_y_ratio = max(0, min(1, scroll_y_ratio))

                # 执行滚动
                self.preview_canvas.xview_moveto(scroll_x_ratio)
                self.preview_canvas.yview_moveto(scroll_y_ratio)

    def draw_selection_box(self, index):
        """绘制选中框（单选）"""
        self.selected_image_indices = {index}
        self.draw_selection_boxes()

    def draw_selection_boxes(self):
        """绘制选中框（支持多选），遍历所有选中的图片索引并绘制蓝色边框"""
        # 清除旧的选中框
        self.preview_canvas.delete("selection_box")

        # 遍历所有选中的图片索引
        for index in self.selected_image_indices:
            if 0 <= index < len(self.image_rects):
                rect = self.image_rects[index]
                self.preview_canvas.create_rectangle(
                    rect['x1'], rect['y1'], rect['x2'], rect['y2'],
                    outline="#0066FF",
                    width=5,
                    tags="selection_box"
                )

        # 绘制裁剪图片的黄色虚线边框
        for img_path in self.pending_crops:
            # 找到该图片在列表中的索引
            if img_path in self.image_paths:
                index = self.image_paths.index(img_path)
                if 0 <= index < len(self.image_rects):
                    rect = self.image_rects[index]
                    self.preview_canvas.create_rectangle(
                        rect['x1'], rect['y1'], rect['x2'], rect['y2'],
                        outline="#FFFF00",
                        width=3,
                        dash=(5, 5),
                        tags="selection_box"
                    )

        # 确保选中框在最上层
        self.preview_canvas.tag_raise("selection_box")

    def on_preview_left_click(self, event):
        """处理预览区域左键点击事件，用于选择和拖拽图片"""
        # 获取点击位置
        click_x = self.preview_canvas.canvasx(event.x)
        click_y = self.preview_canvas.canvasy(event.y)

        # 检查是否点击了某张图片
        for i, rect in enumerate(self.image_rects):
            if rect['x1'] <= click_x <= rect['x2'] and rect['y1'] <= click_y <= rect['y2']:
                # 检查是否按下了Shift或Ctrl键
                shift_pressed = event.state & 0x1  # Shift键的位掩码
                ctrl_pressed = event.state & 0x4  # Ctrl键的位掩码

                if shift_pressed and self.last_selected_index >= 0:
                    # Shift+点击：范围选择
                    start = min(self.last_selected_index, i)
                    end = max(self.last_selected_index, i)

                    if ctrl_pressed:
                        # Ctrl+Shift：切换范围选择
                        for idx in range(start, end + 1):
                            if idx in self.selected_image_indices:
                                self.selected_image_indices.remove(idx)
                            else:
                                self.selected_image_indices.add(idx)
                    else:
                        # Shift：范围选择
                        self.selected_image_indices = set(range(start, end + 1))

                    self.last_selected_index = i
                elif ctrl_pressed:
                    # Ctrl+点击：切换选择状态
                    if i in self.selected_image_indices:
                        self.selected_image_indices.remove(i)
                    else:
                        self.selected_image_indices.add(i)
                    self.last_selected_index = i
                else:
                    # 普通点击：检查点击的图片是否已经在选中集合中
                    if i not in self.selected_image_indices:
                        # 如果点击的是未选中的图片，才切换到单选
                        self.selected_image_indices = {i}
                        self.last_selected_index = i
                    # 如果点击的是已选中的图片，则保持当前选择不变（用于拖拽）

                self.selected_image_index = i
                self.file_combobox.current(i)

                # 开始拖拽
                self.dragging_image_index = i
                self.drag_source_index = i
                self.drag_start_pos = (click_x, click_y)

                # 更新选中框显示
                self.draw_selection_boxes()
                from function.ui_operations import update_status_info
                update_status_info(self)

                return

        # 点击空白区域，清除选择
        self.dragging_image_index = -1
        self.drag_source_index = -1
        self.selected_image_index = -1
        self.selected_image_indices = set()
        self.draw_selection_boxes()

    def create_drag_preview(self, x, y, image_index):
        """创建文件图标拖拽预览"""
        try:
            if image_index >= len(self.image_paths):
                return

            # 获取文件名
            filename = os.path.basename(self.image_paths[image_index])

            # 根据选中的图片数量选择图标
            if len(self.selected_image_indices) > 1:
                # 多张图片：使用 photos.png
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', 'photos.png')
            else:
                # 单张图片：使用 photo.png
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', 'photo.png')

            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                # 缩放图标
                icon_size = 40
                icon_resized = icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                self.drag_preview_photo = ImageTk.PhotoImage(icon_resized)
                
                # 显示图标
                self.preview_canvas.create_image(
                    x, y,
                    image=self.drag_preview_photo,
                    anchor=tk.CENTER,
                    tags="drag_preview"
                )
            else:
                # 如果图标不存在，使用原来的文字显示
                icon_size = 40
                font_size = 10

                # 创建图标背景
                self.preview_canvas.create_rectangle(
                    x - icon_size // 2, y - icon_size // 2,
                    x + icon_size // 2, y + icon_size // 2,
                    fill="#E0E0E0",
                    outline="#666666",
                    width=2,
                    tags="drag_preview"
                )

                # 显示图标文字
                self.preview_canvas.create_text(
                    x, y - 5,
                    text="IMG",
                    font=("Arial", 16),
                    tags="drag_preview"
                )

                # 显示文件名（截断过长的文件名）
                max_name_length = 10
                display_name = filename
                if len(display_name) > max_name_length:
                    display_name = display_name[:max_name_length - 3] + "..."

                self.preview_canvas.create_text(
                    x, y + 15,
                    text=display_name,
                    font=("Arial", font_size),
                    fill="#333333",
                    tags="drag_preview"
                )

            # 将拖拽预览置于顶层
            self.preview_canvas.tag_raise("drag_preview")

        except Exception as e:
            print(f"创建拖拽预览失败: {e}")

    def on_preview_drag(self, event):
        """处理预览区域拖拽事件"""
        if self.dragging_image_index < 0:
            return

        try:
            # 获取拖拽位置
            drag_x = self.preview_canvas.canvasx(event.x)
            drag_y = self.preview_canvas.canvasy(event.y)

            # 如果还没有创建拖拽预览，则创建
            if not self.preview_canvas.find_withtag("drag_preview"):
                self.create_drag_preview(drag_x, drag_y, self.dragging_image_index)
            else:
                # 更新拖拽预览位置
                items = self.preview_canvas.find_withtag("drag_preview")
                for item in items:
                    # 获取当前坐标并更新位置
                    coords = self.preview_canvas.coords(item)
                    if len(coords) == 4:
                        dx = drag_x - (coords[0] + coords[2]) / 2
                        dy = drag_y - (coords[1] + coords[2]) / 2
                        self.preview_canvas.move(item, dx, dy)
                    elif len(coords) == 2:  # 图片中心点
                        dx = drag_x - coords[0]
                        dy = drag_y - coords[1]
                        self.preview_canvas.move(item, dx, dy)

                self.preview_canvas.tag_raise("drag_preview")

            # 更新插入光标位置
            self.update_insert_cursor(drag_x, drag_y)

        except Exception as e:
            print(f"拖拽失败: {e}")

    def update_insert_cursor(self, x, y):
        """更新插入光标位置（只显示垂直方向，确保两个文件之间只显示一个，光标在间隙正中心）"""
        try:
            # 清除旧的插入光标
            self.preview_canvas.delete("insert_cursor")

            # 初始化变量
            insert_index = -1
            cursor_x1, cursor_y1, cursor_x2, cursor_y2 = 0, 0, 0, 0

            # 遍历所有图片矩形
            for i, rect in enumerate(self.image_rects):
                if i != self.dragging_image_index and rect['x1'] <= x <= rect['x2'] and rect['y1'] <= y <= rect['y2']:
                    # 计算图片中心点
                    center_x = (rect['x1'] + rect['x2']) / 2

                    if x < center_x:
                        # 在图片左侧插入
                        insert_index = i
                        if i > 0:
                            # 在前一张图片和当前图片之间
                            prev_rect = self.image_rects[i - 1]
                            gap_center = (prev_rect['x2'] + rect['x1']) / 2
                            cursor_x1 = gap_center - 2
                            cursor_x2 = gap_center + 2
                        else:
                            # 在第一张图片左侧
                            cursor_x1 = rect['x1'] - 2
                            cursor_x2 = rect['x1'] + 2
                        cursor_y1 = rect['y1']
                        cursor_y2 = rect['y2']
                    else:
                        # 在图片右侧插入
                        insert_index = i + 1
                        if i < len(self.image_rects) - 1:
                            # 在当前图片和下一张图片之间
                            next_rect = self.image_rects[i + 1]
                            gap_center = (rect['x2'] + next_rect['x1']) / 2
                            cursor_x1 = gap_center - 2
                            cursor_x2 = gap_center + 2
                        else:
                            # 在最后一张图片右侧
                            cursor_x1 = rect['x2'] - 2
                            cursor_x2 = rect['x2'] + 2
                        cursor_y1 = rect['y1']
                        cursor_y2 = rect['y2']
                    break

            # 如果没有在图片上，查找最近的插入位置
            if insert_index == -1:
                min_distance = float('inf')
                closest_index = -1
                closest_side = None  # 'left'或'right'

                for i, rect in enumerate(self.image_rects):
                    # 只考虑同一行的图片
                    if y >= rect['y1'] and y <= rect['y2']:
                        # 检查左侧
                        if x < rect['x1']:
                            distance = rect['x1'] - x
                            if distance < min_distance:
                                min_distance = distance
                                closest_index = i
                                closest_side = 'left'
                        # 检查右侧
                        elif x > rect['x2']:
                            distance = x - rect['x2']
                            if distance < min_distance:
                                min_distance = distance
                                closest_index = i + 1
                                closest_side = 'right'

                # 只在两个文件之间显示插入光标，光标在间隙正中
                if closest_index >= 0 and closest_side == 'right':
                    # 如果在右侧，确保下一个位置有文件
                    if closest_index < len(self.image_rects):
                        insert_index = closest_index
                        current_rect = self.image_rects[closest_index - 1]
                        next_rect = self.image_rects[closest_index]
                        gap_center = (current_rect['x2'] + next_rect['x1']) / 2
                        cursor_x1 = gap_center - 2
                        cursor_x2 = gap_center + 2
                        cursor_y1 = current_rect['y1']
                        cursor_y2 = current_rect['y2']
                elif closest_index >= 0 and closest_side == 'left':
                    # 如果在左侧，确保前一个位置有文件
                    if closest_index > 0:
                        insert_index = closest_index
                        prev_rect = self.image_rects[closest_index - 1]
                        current_rect = self.image_rects[closest_index]
                        gap_center = (prev_rect['x2'] + current_rect['x1']) / 2
                        cursor_x1 = gap_center - 2
                        cursor_x2 = gap_center + 2
                        cursor_y1 = current_rect['y1']
                        cursor_y2 = current_rect['y2']

            # 绘制插入光标
            if insert_index >= 0:
                self.insert_index = insert_index
                # 绘制类似Word的红色垂直光标
                cursor_x = (cursor_x1 + cursor_x2) / 2
                self.preview_canvas.create_line(
                    cursor_x, cursor_y1, cursor_x, cursor_y2,
                    fill="#FF0000",
                    width=2,
                    tags="insert_cursor"
                )
                self.preview_canvas.tag_raise("insert_cursor")
            else:
                self.insert_index = -1

        except Exception as e:
            print(f"更新插入光标失败: {e}")

    def on_preview_release(self, event):
        """处理预览区域释放事件"""
        if self.dragging_image_index < 0:
            return

        try:
            # 如果有有效的插入位置，执行移动操作
            if self.insert_index >= 0 and self.insert_index != self.drag_source_index:
                # 保存当前状态到历史记录
                from function.history_manager import save_state
                save_state(self)

                # 检查是否是多选拖拽
                if len(self.selected_image_indices) > 1:
                    # 多选拖拽：移动所有选中的图片
                    # 1. 获取所有选中的索引，按升序排序
                    sorted_selected_indices = sorted(self.selected_image_indices)
                    
                    # 2. 计算插入位置的调整值
                    # 如果插入位置在源索引之后，需要减去已移除的图片数量
                    remove_count = 0
                    adjusted_insert_index = self.insert_index
                    
                    # 3. 收集所有要移动的图片路径
                    images_to_move = []
                    for idx in sorted_selected_indices:
                        if idx < self.insert_index:
                            remove_count += 1
                        images_to_move.append(self.image_paths[idx])
                    
                    # 4. 从原位置移除图片（从后往前移除，避免索引混乱）
                    for idx in reversed(sorted_selected_indices):
                        self.image_paths.pop(idx)
                    
                    # 5. 调整插入索引
                    if self.insert_index > sorted_selected_indices[-1]:
                        adjusted_insert_index = self.insert_index - len(sorted_selected_indices)
                    elif self.insert_index > sorted_selected_indices[0]:
                        adjusted_insert_index = self.insert_index - sum(1 for idx in sorted_selected_indices if idx < self.insert_index)
                    
                    # 6. 插入图片到新位置
                    for i, img_path in enumerate(images_to_move):
                        self.image_paths.insert(adjusted_insert_index + i, img_path)
                    
                    # 7. 更新选中索引
                    new_selected_indices = set(range(adjusted_insert_index, adjusted_insert_index + len(images_to_move)))
                    self.selected_image_indices = new_selected_indices
                    # 选中第一个移动的图片作为当前选中索引
                    self.selected_image_index = adjusted_insert_index
                else:
                    # 单选拖拽：移动单个图片
                    # 调整插入索引（因为删除源图片后索引会变化）
                    if self.insert_index > self.drag_source_index:
                        adjusted_insert_index = self.insert_index - 1
                    else:
                        adjusted_insert_index = self.insert_index

                    # 执行移动操作
                    source_path = self.image_paths.pop(self.drag_source_index)
                    self.image_paths.insert(adjusted_insert_index, source_path)

                    # 更新选中索引
                    self.selected_image_index = adjusted_insert_index
                    self.selected_image_indices = {adjusted_insert_index}

                # 更新UI（不重新绘制整个网格，只更新必要部分）
                self.update_image_positions()

        except Exception as e:
            print(f"释放失败: {e}")
        finally:
            # 清理拖拽相关资源
            self.preview_canvas.delete("drag_preview")
            self.preview_canvas.delete("insert_cursor")
            self.dragging_image_index = -1
            self.drag_source_index = -1
            self.drag_start_pos = None
            self.drag_preview_image = None
            self.drag_preview_photo = None
            self.insert_index = -1

    def update_image_positions(self):
        """更新图片位置（使用双缓冲技术减少闪烁）"""
        from function.image_utils import calculate_grid_layout
        
        # 获取Canvas实际尺寸
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        # 计算布局，使用实际的Canvas尺寸
        layout_data = calculate_grid_layout(
            self.image_paths,
            self.pending_crops,
            self.preview_scale,
            canvas_width=canvas_width,
            canvas_height=canvas_height
        )

        if not layout_data:
            return

        # 清空缓存
        self.image_rects.clear()
        self.preview_photos.clear()

        # 准备新的图片数据
        new_photos = []
        new_rects = []

        # 遍历布局数据，准备每张图片
        for item in layout_data:
            img_path = item['path']
            x, y = item['position']
            size = item['size']

            # 如果图片已裁剪，使用裁剪后的图片
            if img_path in self.pending_crops:
                img = self.pending_crops[img_path]
            else:
                img = load_image(img_path)

            if img:
                # 调整图片大小
                img_resized = resize_image(img, size[0], size[1])
                photo = create_photo_image(img_resized)
                new_photos.append(photo)
                new_rects.append({
                    'x1': x,
                    'y1': y,
                    'x2': x + size[0],
                    'y2': y + size[1]
                })

        # 一次性更新所有内容（减少闪烁）
        # 1. 清空画布
        self.preview_canvas.delete("all")
        
        # 2. 一次性绘制所有图片
        for i, (photo, item) in enumerate(zip(new_photos, layout_data)):
            x, y = item['position']
            size = item['size']
            img_path = item['path']
            
            # 绘制图片
            self.preview_canvas.create_image(x, y, image=photo, anchor=tk.NW, tags=f"image_{item['index']}")
            
            # 为所有图片添加细边框
            self.preview_canvas.create_rectangle(
                x, y, x + size[0], y + size[1],
                outline="#CCCCCC",
                width=1,
                tags=f"border_{item['index']}"
            )
            
            # 显示图片序号
            self.preview_canvas.create_text(
                x + 5, y + 5,
                text=f"#{item['index'] + 1}",
                fill="white",
                font=("Arial", 10, "bold"),
                anchor=tk.NW,
                tags=f"label_{item['index']}"
            )
            
            # 显示文件名（截断过长的文件名）
            filename = os.path.splitext(os.path.basename(img_path))[0]
            max_filename_length = max(5, size[0] // 8)
            if len(filename) > max_filename_length:
                filename = filename[:max_filename_length - 3] + "..."
            
            font_size = max(7, min(10, size[1] // 15))
            
            self.preview_canvas.create_text(
                x + size[0] - 5, y + 5,
                text=filename,
                fill="white",
                font=("Arial", font_size),
                anchor=tk.NE,
                tags=f"filename_{item['index']}"
            )

        # 3. 保存新的缓存数据
        self.preview_photos = new_photos
        self.image_rects = new_rects

        # 4. 重新绘制选中框
        if self.selected_image_indices:
            self.draw_selection_boxes()

        # 5. 更新滚动区域
        max_x = max(rect['x2'] for rect in self.image_rects) if self.image_rects else 0
        max_y = max(rect['y2'] for rect in self.image_rects) if self.image_rects else 0
        self.preview_canvas.configure(scrollregion=(0, 0, max_x + 20, max_y + 20))
        if self.selected_image_index >= 0 and self.selected_image_index < len(self.image_rects):
            self.scroll_to_image(self.selected_image_index)

    def on_preview_right_click(self, event):
        """处理预览区域右键点击事件"""
        # 获取点击位置
        click_x = self.preview_canvas.canvasx(event.x)
        click_y = self.preview_canvas.canvasy(event.y)

        # 查找被点击的图片
        clicked_index = -1
        for i, rect in enumerate(self.image_rects):
            if rect['x1'] <= click_x <= rect['x2'] and rect['y1'] <= click_y <= rect['y2']:
                clicked_index = i
                break

        if clicked_index >= 0:
            # 如果图片未被选中，则选中它
            if clicked_index not in self.selected_image_indices:
                self.selected_image_index = clicked_index
                self.file_combobox.current(clicked_index)
                self.draw_selection_boxes()
                from function.ui_operations import update_status_info
                update_status_info(self)

            # 显示右键菜单
            self.show_context_menu(event, clicked_index)

    def show_context_menu(self, event, index):
        """显示右键菜单"""
        if index < 0 or index >= len(self.image_paths):
            return

        context_menu = tk.Menu(self.root, tearoff=0)
        from function.ui_operations import enter_crop_mode
        from function.list_operations import show_image_properties, open_image_location, open_with_default_viewer, copy_images, cut_images, paste_images, delete_images

        context_menu.add_command(label="进入裁剪模式", command=lambda: enter_crop_mode(self))
        context_menu.add_separator()
        context_menu.add_command(label="复制", command=lambda: copy_images(self, index))
        context_menu.add_command(label="剪切", command=lambda: cut_images(self, index))
        context_menu.add_command(label="粘贴", command=lambda: paste_images(self, index))
        context_menu.add_separator()
        context_menu.add_command(label="删除", command=lambda: delete_images(self, index))
        context_menu.add_separator()
        context_menu.add_command(label="查看属性", command=lambda: show_image_properties(self, index))
        context_menu.add_command(label="打开位置", command=lambda: open_image_location(self, index))
        context_menu.add_command(label="用默认浏览器打开", command=lambda: open_with_default_viewer(self, index))

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def select_all_images(self, event=None):
        """全选所有图片"""
        from function.list_operations import select_all_images as ops_select_all_images
        ops_select_all_images(self, event)

    def on_drop_files(self, event):
        """
        处理拖拽文件到预览窗口的事件
        支持拖拽单个或多个文件、目录
        拖拽时会清除已有图片
        """
        try:
            # 解析拖拽的文件/目录列表
            data = event.data
            if not data:
                return

            # 处理Windows格式的拖拽数据
            # 格式1: {文件1 文件2 文件3} - 所有文件在一个花括号内
            # 格式2: {文件1} {文件2} {文件3} - 每个文件都有自己的花括号
            # 格式3: {"文件 1" "文件 2" "文件 3"} - 带空格的路径用引号包围
            paths = []

            # 先尝试提取所有花括号内的内容
            import re
            bracket_matches = re.findall(r'\{([^}]*)\}', data)

            if bracket_matches:
                # 如果找到花括号，提取其中的内容
                for match in bracket_matches:
                    match = match.strip()
                    if match:
                        # 检查是否包含引号（可能是带空格的路径）
                        if '"' in match or "'" in match:
                            # 使用正则表达式提取引号内的内容
                            quoted_matches = re.findall(r'["\']([^"\']+)["\']', match)
                            if quoted_matches:
                                paths.extend([m.strip() for m in quoted_matches if m.strip()])
                            else:
                                # 如果没有匹配到引号内容，直接添加
                                paths.append(match)
                        elif ' ' in match and not os.path.exists(match):
                            # 如果包含空格且不是有效路径，尝试分割
                            split_paths = match.split()
                            paths.extend([p.strip() for p in split_paths if p.strip()])
                        else:
                            # 否则直接添加
                            paths.append(match)
            else:
                # 如果没有花括号，直接使用原始数据
                paths.append(data.strip())

            # 如果提取到的路径为空，尝试直接分割
            if not paths:
                # 移除外层花括号
                if data.startswith('{') and data.endswith('}'):
                    data = data[1:-1]

                # 分割多个文件/目录
                paths = [p.strip() for p in data.split() if p.strip()]

            if not paths:
                return

            # 收集所有图片文件
            image_paths = []
            from function.file_manager import get_image_files, validate_image_path

            for path in paths:
                # 移除可能的引号
                path = path.strip('"').strip("'")

                if os.path.isdir(path):
                    # 如果是目录，获取目录中的所有图片
                    dir_images = get_image_files(path)
                    if dir_images:
                        image_paths.extend(dir_images)
                elif os.path.isfile(path):
                    # 如果是文件，检查是否是有效的图片文件
                    if validate_image_path(path):
                        image_paths.append(path)

            if image_paths:
                # 清除已有图片，只保留新拖拽的图片
                self.image_paths = image_paths

                # 重置选择状态
                self.selected_image_indices = set()
                self.selected_image_index = -1
                self.last_selected_index = -1
                self.pending_crops = {}
                self.pending_crop_coords = {}

                # 使用适应窗口模式
                from function.preview import fit_preview_to_window
                fit_preview_to_window(self)

        except Exception as e:
            print(f"拖拽文件处理失败: {e}")
            messagebox.showerror("错误", f"拖拽文件处理失败: {str(e)}")


def run():
    """
    启动GIF Maker GUI应用
    创建主窗口并启动事件循环
    """
    root = TkinterDnD.Tk()
    app = GifMakerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    run()

```

[回到目录](#目录)

---

<a name="file-gui__init__py"></a>
## 21. gui\__init__.py

**完整路径**: `E:\OneDrive\PythonProject\GifMaker\gui\__init__.py`

```python
# -*- coding: utf-8 -*-
"""
GIF Maker GUI模块
"""

from .main_window import GifMakerGUI, run

__all__ = ['GifMakerGUI', 'run']

```

[回到目录](#目录)

---

