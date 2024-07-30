
import os
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sv_ttk
import io
import sys
import string
import math
sys.path.append('./')  # 无论如何都不许删这行代码，确保当前目录在系统路径中

# 使用PIL读取图像的函数
def read_image_with_pil(image_path):
    with open(image_path, 'rb') as f:
        img_bytes = f.read()  # 读取图像字节
    img = Image.open(io.BytesIO(img_bytes))  # 使用PIL打开图像
    return img

# 使用OpenCV处理图像的函数
def process_image(img_cv, lower_range, upper_range):
    hsv_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)  # 将图像转换为HSV色彩空间
    mask = cv2.inRange(hsv_img, lower_range, upper_range)  # 创建颜色掩码
    color_image = cv2.bitwise_and(img_cv, img_cv, mask=mask)  # 应用掩码提取颜色区域
    return color_image

# 调整图像大小并将非黑色像素转换为白色
def resize_and_black_to_white(img_pil, size=(500, 500)):
    img = img_pil.convert("RGB")  # 转换为RGB模式
    img = img.resize(size)  # 调整图像大小
    width, height = img.size
    for x in range(width):
        for y in range(height):
            r, g, b = img.getpixel((x, y))  # 获取像素值
            if r == 0 and g == 0 and b == 0:
                continue  # 如果是黑色像素，跳过
            else:
                img.putpixel((x, y), (255, 255, 255))  # 将非黑色像素转换为白色
    return img

# 使用OpenCV进行图像降噪处理
def denoise_image(img_pil, kernel_size, iterations):
    image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)  # 转换为灰度图像
    inverted_image = cv2.bitwise_not(image)  # 反转图像颜色
    kernel = np.ones((kernel_size, kernel_size), np.uint8)  # 创建卷积核
    eroded_inverted_image = cv2.erode(inverted_image, kernel, iterations=iterations)  # 腐蚀操作
    pil_image = Image.fromarray(cv2.bitwise_not(eroded_inverted_image))  # 转换为PIL图像
    cleaned_image = pil_image  # 清理后的图像
    return cleaned_image

# 计算图像中黑色像素的比例
def calculate_black_area_ratio(img_pil):
    img = np.array(img_pil.convert("L"))  # 转换为灰度图像数组
    total_pixels = img.size
    black_pixels = np.sum(img <= 150)  # 计算黑色像素数量
    black_ratio = black_pixels / total_pixels  # 计算黑色像素比例
    print(f"黑色像素比例{black_ratio},{total_pixels}个像素,{black_pixels}个黑色像素")
    height, width = img.shape
    black_area = black_ratio * height * width * 0.01  # 计算黑色区域面积
    return black_area, black_ratio

# 找到图像中符合目标比例的y坐标
def find_y_coordinate(img_pil, target_ratio=0.8):
    img = np.array(img_pil.convert("L"))  # 转换为灰度图像数组
    height, width = img.shape
    for y in range(height):
        row = img[y, :]  # 获取当前行像素值
        black_pixels = np.sum(row <= 120)  # 计算当前行黑色像素数量
        black_ratio = black_pixels / width  # 计算当前行黑色像素比例
        print(f"当前行为{y}, 黑色像素数{black_pixels}, 总像素数{width}")
        print(f"黑色像素比例{black_ratio}")
        if black_ratio <= target_ratio:
            return y  # 返回符合条件的y坐标
    return -1  # 如果没有找到符合条件的y坐标
def calculate_length_index(img_pil):
    img = np.array(img_pil.convert("L"))  # 转换为灰度图像数组
    height, width = img.shape
    ratio_list = []
    difference_proportion_list = []
    
    for y in range(height):
        row = img[y, :]  # 获取当前行像素值
        black_pixels = np.sum(row <= 120)  # 计算当前行黑色像素数量
        black_ratio = black_pixels / width  # 计算当前行黑色像素比例
        ratio_list.append(black_ratio)  # 保存当前行黑色像素比例
        
        # 如果列表中有至少两个元素，计算当前行与上一行的差值比例
        if len(ratio_list) >= 2:
            difference_proportion = abs(ratio_list[-1] - ratio_list[-2])
            difference_proportion_list.append(difference_proportion)
    
    print(f"黑色像素比例列表: {ratio_list}")
    print(f"黑色像素比例差值比例列表: {difference_proportion_list}")
    
    total_difference_proportion = sum(difference_proportion_list)
    total_difference_proportion = round(total_difference_proportion, 3) # 保留三位小数
    total_difference_proportion *= 100  # 乘以100
    print(f"总黑色像素比例差值比例: {total_difference_proportion}")
    return total_difference_proportion

# 在图像上绘制红线
def draw_red_line(img_pil, y_coordinate):
    draw = ImageDraw.Draw(img_pil)
    width, height = img_pil.size
    line_thickness = int(height * 0.005)  # 计算线条厚度
    draw.line([(0, y_coordinate), (width, y_coordinate)], fill="red", width=line_thickness)  # 绘制红线
    return img_pil

# 计算优先流百分比
def calculate_priority_flow_percentage(soil_width, y_coordinate, S_Black):
    a = soil_width * y_coordinate / 10  # 计算a值
    b = S_Black  # 获取黑色面积
    print(f"a={a}, b={b}")  # 调试信息
    result = f"{(1 - a / b) * 100:.2f}"  # 计算优先流百分比
    return result

# 主函数，创建并运行GUI应用程序
def main():
    root = tk.Tk()
    root.title("Preferential flow calculation")  # 设置窗口标题

    # 浏览文件函数
    def browse_file():
        file_path = filedialog.askopenfilename()  # 打开文件选择对话框
        if file_path:
            input_path_entry.delete(0, tk.END)
            input_path_entry.insert(0, file_path)
            if not manual_mode_var.get():
                update_image()
            else:
                update_manual_mode()

    # 保存文件函数
    def save_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile='processed_image.png')  # 打开保存文件对话框
        if file_path:
            output_path_entry.delete(0, tk.END)
            output_path_entry.insert(0, file_path)
            img = Image.fromarray(np.array(final_img))  # 将图像转换为PIL格式
            img.save(file_path)  # 保存图像
            messagebox.showinfo("完成", f"图像处理完成并保存到 {file_path}")

    # 更新图像函数
    def update_image():
        input_path = input_path_entry.get()
        if not input_path:
            messagebox.showerror("错误", "请输入图像路径")
            return
        
        lower_range, upper_range = get_color_ranges()
        if lower_range is None or upper_range is None:
            return
        
        img_pil = read_image_with_pil(input_path)
        img_pil = process_and_resize_image(img_pil, lower_range, upper_range)
        if img_pil is None:
            return
        
        apply_denoise_if_needed(img_pil)
        
        global S_Black, y_coordinate, black_ratio
        S_Black, black_ratio = calculate_black_area_ratio(final_img)
        black_area_label.config(text=f"染色面积: {S_Black:.2f} cm^2")
        
        y_coordinate = find_y_coordinate(final_img)
        total_difference_proportion=calculate_length_index(final_img)
        total_difference_proportion_label.config(text=f"长度指数: {total_difference_proportion:.2f} ")
        display_img = draw_red_line(final_img.copy(), y_coordinate)
        display_image(display_img)
        y_coordinate_label.config(text=f"基质流深度: {y_coordinate / 10} cm")

        try:
            soil_width = float(soil_profile_width_entry.get())
            priority_flow_percentage = calculate_priority_flow_percentage(soil_width, y_coordinate, S_Black)
            priority_flow_label.config(text=f"优先流百分比: {priority_flow_percentage} %")
            black_ratio_label.config(text=f"染色面积比: {black_ratio * 100:.2f} %")
        except ValueError:
            messagebox.showerror("错误", "土壤剖面垂直宽度必须是一个数字")

    # 计算优先流百分比按钮函数
    def calculate_priority_flow_percentage_button():
        global soil_width, S_Black, y_coordinate, black_ratio
        try:
            soil_width = float(soil_profile_width_entry.get())
            priority_flow_percentage = calculate_priority_flow_percentage(soil_width, y_coordinate, S_Black)
            priority_flow_label.config(text=f"优先流百分比: {priority_flow_percentage} %")
            black_ratio_label.config(text=f"染色面积比: {black_ratio * 100:.2f} %")
        except ValueError:
            messagebox.showerror("错误", "土壤剖面垂直宽度必须是一个数字")

    # 获取颜色范围函数
    def get_color_ranges():
        try:
            lower_R = int(lower_hue_entry.get())
            lower_G = int(lower_saturation_entry.get())
            lower_B = int(lower_value_entry.get())
            upper_R = int(upper_hue_entry.get())
            upper_G = int(upper_saturation_entry.get())
            upper_B = int(upper_value_entry.get())
        except ValueError:
            messagebox.showerror("错误", "颜色范围值必须是整数")


            return None, None
        
        lower_range = (lower_R, lower_G, lower_B)
        upper_range = (upper_R, upper_G, upper_B)
        print(f"Lower range: {lower_range}")  # 调试信息
        print(f"Upper range: {upper_range}")  # 调试信息
        return lower_range, upper_range

    # 处理并调整图像大小函数
    def process_and_resize_image(img_pil, lower_range, upper_range):
        img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        processed_img = process_image(img_cv, lower_range, upper_range)
        img_pil = Image.fromarray(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB))
        
        size = size_entry.get()
        if size:
            try:
                width, height = map(int, size.split('x'))
            except ValueError:
                messagebox.showerror("错误", "分辨率格式不正确，请输入例如 500x500")
                return None
        else:
            width, height = 500, 500
        
        resized_img = resize_and_black_to_white(img_pil, size=(width, height))
        return resized_img

    # 应用降噪处理（如果需要）
    def apply_denoise_if_needed(img_pil):
        global final_img
        if denoise_var.get():
            try:
                kernel_size = int(kernel_size_entry.get())
                iterations = int(iterations_entry.get())
            except ValueError:
                messagebox.showerror("错误", "核大小和迭代次数必须是整数")
                return
            final_img = denoise_image(img_pil, kernel_size, iterations)
        else:
            final_img = img_pil

    # 更新手动模式函数
    def update_manual_mode():
        input_path = input_path_entry.get()
        if not input_path:
            messagebox.showerror("错误", "请输入图像路径")
            return
        
        img_pil = read_image_with_pil(input_path)
        global final_img, S_Black, y_coordinate, black_ratio
        final_img = img_pil
        S_Black, black_ratio = calculate_black_area_ratio(final_img)
        black_area_label.config(text=f"染色面积: {S_Black:.2f} cm^2")
        
        y_coordinate = find_y_coordinate(final_img)
        total_difference_proportion=calculate_length_index(final_img)
        total_difference_proportion_label.config(text=f"长度指数: {total_difference_proportion:.2f} ")
        display_img = draw_red_line(final_img.copy(), y_coordinate)
        display_image(display_img)
        y_coordinate_label.config(text=f"基质流深度: {y_coordinate / 10} cm")

    # 显示图像函数
    def display_image(image):
        img = Image.fromarray(np.array(image))
        imgtk = ImageTk.PhotoImage(image=img)
        panel.config(image=imgtk)
        panel.image = imgtk

    # 创建GUI
    frame1 = ttk.Frame(root)
    frame1.pack(padx=10, pady=5, fill='x')
    ttk.Label(frame1, text="文件路径:").pack(side='left')
    input_path_entry = ttk.Entry(frame1, width=50)
    input_path_entry.pack(side='left', padx=10)
    browse_button = ttk.Button(frame1, text="浏览", command=browse_file)
    browse_button.pack(side='left')

    manual_mode_var = tk.BooleanVar()
    manual_mode_checkbox = ttk.Checkbutton(frame1, text="手动模式", variable=manual_mode_var)
    manual_mode_checkbox.pack(side='left')

    frame2 = ttk.Frame(root)
    frame2.pack(padx=10, pady=5, fill='x')
    ttk.Label(frame2, text="输出路径:").pack(side='left')
    output_path_entry = ttk.Entry(frame2, width=50)
    output_path_entry.pack(side='left', padx=10)
    save_button = ttk.Button(frame2, text="选择", command=save_file)
    save_button.pack(side='left')

    frame3 = ttk.Frame(root)
    frame3.pack(padx=10, pady=5, fill='x')
    ttk.Label(frame3, text="输入分辨率大小 (如500x500):").pack(side='left')
    size_entry = ttk.Entry(frame3, width=50)
    size_entry.pack(side='left', padx=10)

    frame4 = ttk.Frame(root)
    frame4.pack(padx=10, pady=5, fill='x')
    ttk.Label(frame4, text="下限R:").pack(side='left')
    lower_hue_entry = ttk.Entry(frame4, width=10)
    lower_hue_entry.insert(0, '0')
    lower_hue_entry.pack(side='left', padx=2)
    ttk.Label(frame4, text="下限G:").pack(side='left')
    lower_saturation_entry = ttk.Entry(frame4, width=10)
    lower_saturation_entry.insert(0, '50')
    lower_saturation_entry.pack(side='left', padx=2)
    ttk.Label(frame4, text="下限B:").pack(side='left')
    lower_value_entry = ttk.Entry(frame4, width=10)
    lower_value_entry.insert(0, '50')
    lower_value_entry.pack(side='left', padx=2)

    frame5 = ttk.Frame(root)
    frame5.pack(padx=10, pady=5, fill='x')
    ttk.Label(frame5, text="上限R:").pack(side='left')
    upper_hue_entry = ttk.Entry(frame5, width=10)
    upper_hue_entry.insert(0, '60')
    upper_hue_entry.pack(side='left', padx=2)
    ttk.Label(frame5, text="上限G:").pack(side='left')
    upper_saturation_entry = ttk.Entry(frame5, width=10)
    upper_saturation_entry.insert(0, '150')
    upper_saturation_entry.pack(side='left', padx=2)
    ttk.Label(frame5, text="上限B:").pack(side='left')
    upper_value_entry = ttk.Entry(frame5, width=10)
    upper_value_entry.insert(0, '150')
    upper_value_entry.pack(side='left', padx=2)

    frame6 = ttk.Frame(root)
    frame6.pack(padx=10, pady=10, fill='x')
    denoise_var = tk.BooleanVar()
    denoise_checkbox = ttk.Checkbutton(frame6, text="降噪处理", variable=denoise_var)
    denoise_checkbox.pack(side='left', padx=2)
    ttk.Label(frame6, text="核大小:").pack(side='left', padx=2)
    kernel_size_entry = ttk.Entry(frame6, width=5)
    kernel_size_entry.insert(0, '3')
    kernel_size_entry.pack(side='left', padx=2)
    ttk.Label(frame6, text="迭代次数:").pack(side='left', padx=2)
    iterations_entry = ttk.Entry(frame6, width=5)
    iterations_entry.insert(0, '1')
    iterations_entry.pack(side='left', padx=2)
    process_button = ttk.Button(frame6, text="更新图像", command=update_image)
    process_button.pack(side='left', padx=2)

    frame7 = ttk.Frame(root)
    frame7.pack(padx=10, pady=10, fill='x')
    black_area_label = ttk.Label(frame7, text="染色面积: (请先导入图片)", width=25)
    black_area_label.pack(side='left')

    y_coordinate_label = ttk.Label(frame7, text="基质流深度: (请先导入图片)", width=25)
    y_coordinate_label.pack(side='left')
    
    total_difference_proportion_label = ttk.Label(frame7, text="长度指数: (请先导入图片)", width=25)
    total_difference_proportion_label.pack(side='left')
    
    ttk.Label(frame7, text="土壤垂直剖面宽度 (cm):").pack(side='left')
    soil_profile_width_entry = ttk.Entry(frame7, width=5)
    soil_profile_width_entry.pack(side='left', padx=10)

    calculate_button = ttk.Button(frame7, text="计算", command=calculate_priority_flow_percentage_button)
    calculate_button.pack(side='left', padx=2)
   
    frame8 = ttk.Frame(root)
    frame8.pack(padx=10, pady=10, fill='x')
    black_ratio_label = ttk.Label(frame8, text="染色面积比: (请点击计算)", width=25)
    black_ratio_label.pack(side='left')
    priority_flow_label = ttk.Label(frame8, text="优先流百分比: (请点击计算)", width=25)
    priority_flow_label.pack(side='left')
    
    frame9 = ttk.Frame(root)
    frame9.pack(padx=10, pady=10, fill='x')
    panel = ttk.Label(frame9)
    panel.pack()
    
    sv_ttk.set_theme("light")  # 设置主题
    root.mainloop()  # 进入主循环

if __name__ == "__main__":
    main()  # 调用主函数
