import os
import cv2
import re

os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

from paddleocr import PaddleOCR


def extract_address(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return None

    height, width = image.shape[:2]
    center = (width // 2, height // 2)

    rotation_matrix = cv2.getRotationMatrix2D(
        center,
        30,
        1.0
    )

    rotated = cv2.warpAffine(
        image,
        rotation_matrix,
        (width, height)
    )

    address_crop = rotated[
        int(height * 0.45):int(height * 0.85),
        int(width * 0.05):int(width * 0.85)
    ]

    address_crop = cv2.resize(
        address_crop,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    ocr = PaddleOCR(lang="en")
    result = ocr.predict(address_crop)

    all_text = []

    for res in result:

        texts = res["rec_texts"]

        for text in texts:

            text = text.strip()

            if text:
                all_text.append(text)

    address_keywords = [
        "road",
        "rd",
        "street",
        "st",
        "plaza",
        "nagar",
        "colony",
        "area",
        "town",
        "city",
        "hyderabad",
        "warangal",
        "district",
        "near",
        "opposite",
        "beside"
    ]

    address_lines = []

    for text in all_text:

        text_lower = text.lower()

        if any(keyword in text_lower for keyword in address_keywords):

            if re.search(r"\d{10}", text):
                continue

            if "http" in text_lower:
                continue

            if "www." in text_lower:
                continue

            if "jeweller" in text_lower:
                continue

            address_lines.append(text)

    cleaned_lines = []

    for line in address_lines:

        if "acemearrdaan" in line.lower():
            continue

        cleaned_lines.append(line)

    if cleaned_lines:
        return " ".join(cleaned_lines)

    return None