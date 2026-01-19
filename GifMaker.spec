# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules, collect_all

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Full path to the icon file
ICON_PATH = os.path.join(current_dir, 'icons', 'gif.png')

# 使用 collect_all 自动收集 PIL 模块的所有依赖
# collect_all 返回 (binaries, datas, hiddenimports)
pil_binaries, pil_datas, pil_hiddenimports = collect_all('PIL')

# 去重处理：确保每个 DLL 只被打包一次
seen_binaries = set()
unique_bins = []
# PyInstaller 的 binaries 格式为 (src_path, dest_path) 或 (src_path, dest_path, kind)
for binary in pil_binaries:
    # 解析 binary 格式
    if len(binary) == 3:
        src_path, dest_path, kind = binary
    else:
        src_path, dest_path = binary
        kind = None

    # 提取文件名
    file_name = os.path.basename(src_path)

    # 只对通用的 .dll 文件执行严格的文件名去重
    if file_name.endswith('.dll'):
        if file_name not in seen_binaries:
            if kind is not None:
                unique_bins.append((src_path, dest_path, kind))
            else:
                unique_bins.append((src_path, dest_path))
            seen_binaries.add(file_name)
    else:
        # 对于 .pyd 文件和其他文件，不进行去重
        if kind is not None:
            unique_bins.append((src_path, dest_path, kind))
        else:
            unique_bins.append((src_path, dest_path))

a = Analysis(
    ['GifMaker.py'],
    pathex=[],
    binaries=unique_bins,
    datas=[
        # Include project directories
        ('gui', 'gui'),
        ('function', 'function'),
        ('icons', 'icons'),
    ] + pil_datas,
    hiddenimports=[
        # Project modules
        'gui.main_window',
        'gui.preview',
        'gui.crop_gui',
        'gui.gifpreview_gui',
        'function.file_manager',
        'function.image_utils',
        'function.crop_backup',
        'function.history_manager',
        'function.gif_operations',
        'function.list_operations',
        'function.preview',
        'function.ui_operations',
        'function.photo_cropper',
        # PIL related modules
    ] + pil_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'pandas',
        'scipy',
        'IPython',
        'tensorboard',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GifMaker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
)

coll = COLLECT(
    exe,                # Include the EXE object defined above (main program)
    a.binaries,         # Collect all dependent DLLs/dynamic libraries
    a.datas,            # Collect all resource files (images, configs, etc.)
    strip=False,        # Whether to remove symbol table (usually False to avoid errors)
    upx=True,           # Whether to use UPX compression/obfuscation
    upx_exclude=[],     # Files to exclude from compression
    name='GifMaker',  # Final folder name that will be generated
)