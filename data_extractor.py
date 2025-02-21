import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# 載入圖像
image = Image.open("img/Zaldivar_Cu_extraction3.png")
width, height = image.size
# Define the actual data range based on the plot
x_min, x_max = 0, 80  # X-axis: Time on stream [days]
y_min, y_max = 0, 100  # Y-axis: Cu extraction [%]

# Compute aspect ratio correction
fig_width = 10  # Adjust figure width
fig_height = fig_width * (height / width)

# Create figure with correct aspect ratio
fig, ax = plt.subplots(figsize=(fig_width, fig_height))

# Display the image correctly without distorting it
ax.imshow(plt.imread("img/Zaldivar_Cu_extraction3.png"), extent=[
          x_min, x_max, y_min, y_max], aspect='auto')

# 顯示圖像
ax.set_title("Click on the data points")
# X-axis: Time on stream [days]
ax.set_xlim(0, 80)
ax.set_ylim(0, 100)  # Y-axis: Cu extraction [%]
ax.grid(True, linestyle="--", alpha=0.5)
ax.imshow(image, extent=[0, 80, 0, 100])  # Ensure correct axis mapping

# 使用 ginput 提取數據點
points = plt.ginput(n=-1, timeout=0)  # n=-1 表示無限點擊，按 Enter 結束
plt.close()

# 將點轉換為 NumPy 陣列
data_points = np.array(points)

# 保存數據點
np.savetxt('data_points.csv', data_points, delimiter=',')
