import cv2

image_path = r"C:\Users\sathw\OneDrive\Pictures\Screenshots\Screenshot 2026-09-07 215524.png"
image = cv2.imread(image_path)
if image is None:
    print("Image not found")
    exit()
height, width = image.shape[:2]
print("Original Width:", width)
print("Original Height:", height)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
new_width = width * 2
new_height = height * 2
resized_image = cv2.resize(
    gray_image,
    (new_width, new_height)
)
blurred_image = cv2.GaussianBlur(
    resized_image,
    (5, 5),
    0
)
threshold_image = cv2.adaptiveThreshold(
    blurred_image,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    11,
    2
)
output_path = r"D:\contactlens_ai\image_module\processed_card.png"
cv2.imwrite(output_path, threshold_image)
print("Processed image saved successfully!")
print("Location:", output_path)