import cv2
import numpy as np
from matplotlib import pyplot as plt

# 加载图像
image_path = "final/final_processed_image.png"
image = cv2.imread(image_path, 0)

# 反转图像颜色，使黑色变为白色，白色变为黑色
inverted_image = cv2.bitwise_not(image)

# 定义一个5x5的核，用于腐蚀操作
kernel = np.ones((3,3),np.uint8)

# 应用腐蚀操作来去除小的黑色噪点（现在已经变为白色）
eroded_inverted_image = cv2.erode(inverted_image, kernel, iterations=1)

# 再次反转图像颜色，恢复到原始颜色方案
cleaned_image = cv2.bitwise_not(eroded_inverted_image)

# 显示原始图像和清理后的图像
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title('原始图像')
plt.imshow(image, cmap='gray')
plt.axis('off')

plt.subplot(1, 2, 2)
plt.title('清理后的图像')
plt.imshow(cleaned_image, cmap='gray')
plt.axis('off')

plt.show()
