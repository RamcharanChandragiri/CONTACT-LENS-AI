import cv2
image_path = r"C:\Users\sathw\OneDrive\Pictures\Screenshots\Screenshot 2026-09-07 215524.png"
image = cv2.imread(image_path)
if image is None:
    print("Error: Image could not be loaded.")
else:
    print("Image loaded successfully!")
    height, width, channels = image.shape
    print("Width:", width)
    print("Height:", height)
    print("Channels:", channels)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    new_width = width * 2
    new_height = height * 2
    resized_image = cv2.resize(gray_image, (new_width, new_height))
    blurred_image = cv2.GaussianBlur(resized_image,(5, 5),0)
    threshold_image = cv2.adaptiveThreshold(blurred_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    #cv2.imshow("Resized Image", resized_image)
    #cv2.imshow("Original Image", image)
    #cv2.imshow("Grayscale Image", gray_image)
    #cv2.imshow("Blurred Image", blurred_image)
    cv2.imshow("Threshold Image", threshold_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()