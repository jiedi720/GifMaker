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