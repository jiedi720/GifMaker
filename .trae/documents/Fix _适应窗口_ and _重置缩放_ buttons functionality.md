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