# -*- coding: utf-8 -*-
"""
UI助手模块
提供异步初始化策略和其他UI相关辅助功能
"""

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
    #  UI
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