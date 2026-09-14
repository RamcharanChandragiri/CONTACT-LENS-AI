import os
import re

os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

from paddleocr import PaddleOCR


# ---------------------------------------------------------
# EXTRACT CONTACT FROM IMAGE
# ---------------------------------------------------------

def extract_contact(image_path):

    # -----------------------------------------------------
    # OCR
    # -----------------------------------------------------

    ocr = PaddleOCR(lang="en")

    result = ocr.predict(image_path)

    # -----------------------------------------------------
    # COLLECT OCR TEXT
    # -----------------------------------------------------

    lines = []

    for res in result:

        texts = res["rec_texts"]

        for item in texts:

            item = item.strip()

            if item:
                lines.append(item)

    # -----------------------------------------------------
    # PHONE NUMBER EXTRACTION
    # -----------------------------------------------------

    phone_numbers = []

    for line in lines:

        numbers = re.findall(
            r"\b\d{10}\b",
            line
        )

        for number in numbers:

            if number not in phone_numbers:
                phone_numbers.append(number)

    # -----------------------------------------------------
    # EMAIL EXTRACTION
    # -----------------------------------------------------

    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    email_addresses = re.findall(
        email_pattern,
        "\n".join(lines)
    )

    # -----------------------------------------------------
    # WEBSITE / SOCIAL MEDIA
    # -----------------------------------------------------

    url_pattern = r"(?:https?://|www\.)[^\s]+"

    urls = re.findall(
        url_pattern,
        "\n".join(lines)
    )

    website = None

    if urls:
        website = urls[0]

    # -----------------------------------------------------
    # ORGANIZATION EXTRACTION
    # -----------------------------------------------------

    organization_keywords = [

        "jewellers",
        "jeweller",
        "jewelry",
        "jewellery",
        "store",
        "shop",
        "enterprises",
        "solutions",
        "technologies",
        "technology",
        "company",
        "industries"

    ]

    ignore_words = [

        "exclusive",
        "cell",
        "phone",
        "mobile",
        "email",
        "http",
        "www"

    ]

    organization = ""

    for i, line in enumerate(lines):

        line_lower = line.lower()

        # Check organization keyword
        if any(
            keyword in line_lower
            for keyword in organization_keywords
        ):

            # Ignore unwanted lines
            if any(
                word in line_lower
                for word in ignore_words
            ):
                continue

            organization = line

            # Search previous OCR lines
            for j in range(
                i - 1,
                max(-1, i - 5),
                -1
            ):

                previous_line = lines[j].strip()
                previous_lower = previous_line.lower()

                # Ignore unwanted text
                if any(
                    word in previous_lower
                    for word in ignore_words
                ):
                    continue

                # Ignore phone numbers
                if re.search(
                    r"\d{7,}",
                    previous_line
                ):
                    continue

                # Ignore short text
                if len(previous_line) < 4:
                    continue

                # Ignore OCR noise
                if previous_line in [
                    "3",
                    "IPI"
                ]:
                    continue

                # Ignore corrupted jewellery line
                if "cz jeelery" in previous_lower:
                    continue

                organization = (
                    previous_line
                    + " "
                    + organization
                )

                break

            break

    # -----------------------------------------------------
    # RETURN UNIFIED EXTRACTION DATA
    # -----------------------------------------------------

    return {

        "organization": organization
        if organization
        else None,

        "phone_numbers": phone_numbers,

        "email_addresses": email_addresses,

        "website": website,

        "ocr_text": lines

    }


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    image_path = (
        r"C:\Users\sathw\OneDrive\Pictures"
        r"\Screenshots\Screenshot 2026-09-07 215524.png"
    )

    contact = extract_contact(image_path)

    print("\n" + "=" * 40)
    print("       IMAGE CONTACT EXTRACTION")
    print("=" * 40)

    print("\nOrganization:")
    print(contact["organization"])

    print("\nPhone Numbers:")

    for phone in contact["phone_numbers"]:
        print(phone)

    print("\nEmail Addresses:")

    if contact["email_addresses"]:
        for email in contact["email_addresses"]:
            print(email)
    else:
        print("No email found")

    print("\nWebsite:")
    print(contact["website"])

    print("\n" + "=" * 40)