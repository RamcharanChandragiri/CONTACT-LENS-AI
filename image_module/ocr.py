import os

os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

from paddleocr import PaddleOCR


image_path = r"C:\Users\sathw\OneDrive\Pictures\Screenshots\Screenshot 2026-09-07 215524.png"

ocr = PaddleOCR(lang="en")

result = ocr.predict(image_path)


print("\n----- OCR TEXT WITH CENTER POSITIONS -----\n")


for res in result:

    texts = res["rec_texts"]
    boxes = res["rec_boxes"]

    for text, box in zip(texts, boxes):

        x1 = int(box[0])
        y1 = int(box[1])
        x2 = int(box[2])
        y2 = int(box[3])

        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        print("Text:", text)
        print("x1:", x1, "y1:", y1)
        print("x2:", x2, "y2:", y2)
        print("Center X:", center_x)
        print("Center Y:", center_y)
        print("-------------------------")