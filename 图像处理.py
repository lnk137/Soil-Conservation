from PIL import Image, ImageOps
import numpy as np

# Load the image
image_path = "final/final_processed_image.png"
image = Image.open(image_path)

# Convert image to grayscale
gray_image = ImageOps.grayscale(image)

# Convert to numpy array
image_array = np.array(gray_image)

# Apply a threshold to remove small black spots
threshold = 200
binary_image = np.where(image_array > threshold, 255, 0).astype(np.uint8)

# Convert back to PIL image
processed_image = Image.fromarray(binary_image)

# Save the processed image
processed_image_path = "./age.png"
processed_image.save(processed_image_path)

processed_image.show()
