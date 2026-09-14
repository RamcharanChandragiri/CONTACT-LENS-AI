import cv2
import numpy as np
image_path = r"C:\Users\sathw\OneDrive\Pictures\Screenshots\Screenshot 2026-09-07 215524.png"
image = cv2.imread(image_path)
if image is None:
    print("Image not found")
    exit()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 50, 150)
lines = cv2.HoughLinesP(
    edges,
    1,
    np.pi / 180,
    threshold=100,
    minLineLength=100,
    maxLineGap=20
)
angles = []
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(
            np.arctan2(y2 - y1, x2 - x1)
        )
        if -45 < angle < 45:
            angles.append(angle)
if len(angles) > 0:
    angle = np.median(angles)
else:
    angle = 0
print("Detected angle:", angle)
height, width = image.shape[:2]
center = (width // 2, height // 2)
rotation_matrix = cv2.getRotationMatrix2D(
    center,
    -angle,
    1.0
)
rotated = cv2.warpAffine(
    image,
    rotation_matrix,
    (width, height),
    borderMode=cv2.BORDER_REPLICATE
)
output_path = r"D:\contactlens_ai\image_module\straight_card.png"
cv2.imwrite(output_path, rotated)
print("Straightened image saved!")
print(output_path)