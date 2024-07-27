import cv2
import numpy as np

# 读取图像
img = cv2.imread('img/1.jpg')

# 显示原始图像
cv2.imshow('Original Image', img)
cv2.waitKey(0)

# 将图像从BGR转换为HSV
hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 定义HSV格式中绿色的范围
lower_range = (0, 50, 50)
upper_range = (60, 150, 150)

# 根据定义的范围创建掩模
mask = cv2.inRange(hsv_img, lower_range, upper_range)

# 将掩模与原图像结合，提取颜色范围内的部分
color_image = cv2.bitwise_and(img, img, mask=mask)

# 显示处理后的图像
cv2.imshow('Coloured Image', color_image)
cv2.waitKey(0)

# 关闭所有窗口
cv2.destroyAllWindows()

# 保存处理后的图像到res文件夹
cv2.imwrite('res/processed_image.jpg', color_image)
