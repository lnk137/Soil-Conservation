from PIL import Image

def resize_and_black_to_white(image_path, output_path, size=(500, 500)):
    # 打开图像
    img = Image.open(image_path)
    img = img.convert("RGB")  # 确保图像为RGB模式
    
    # 调整图像大小
    img = img.resize(size)
# 保存修改后的图像
    img.save("img/temp.jpg")
    # 获取图像的宽度和高度
    width, height = img.size

    # 遍历每个像素
    for x in range(width):
        for y in range(height):
            r, g, b = img.getpixel((x, y))

            # 检查是否为黑色
            if r == 0 and g == 0 and b == 0:
                continue  # 保持黑色
            else:
                # 将其他颜色变为白色
                img.putpixel((x, y), (255, 255, 255))

    # 保存修改后的图像
    img.save(output_path)
    print(f"Image saved to {output_path}")

# 示例使用
input_image_path = "res/processed_image.jpg"  # 输入图像路径
output_image_path = "final/final_processed_image.png"  # 输出图像路径

resize_and_black_to_white(input_image_path, output_image_path)
