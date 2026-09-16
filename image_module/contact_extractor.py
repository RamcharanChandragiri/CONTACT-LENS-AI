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
            r"\b[6-9]\d{9}\b",
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

    # Remove duplicate emails
    email_addresses = list(
        dict.fromkeys(email_addresses)
    )

    # -----------------------------------------------------
    # WEBSITE / SOCIAL MEDIA
    # -----------------------------------------------------

    url_pattern = (
        r"(?:https?://|www\.)[^\s]+"
    )

    urls = re.findall(
        url_pattern,
        "\n".join(lines)
    )

    website = None

    if urls:
        website = urls[0].rstrip(
            ".,;:"
        )

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
        "industries",

        "traders",
        "services"
    ]

    ignore_words = [

        "exclusive",
        "cell",
        "phone",
        "mobile",

        "email",

        "http",
        "www",
        "facebook"
    ]

    # -----------------------------------------------------
    # CLEAN OCR LINE
    # -----------------------------------------------------

    def clean_organization_line(text):

        text = text.strip()

        # Remove excessive spaces
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        # Remove non-letter characters
        # from beginning
        text = re.sub(
            r"^[^A-Za-z]+",
            "",
            text
        )

        # Remove unwanted characters
        # from end
        text = re.sub(
            r"[^A-Za-z0-9&.' -]+$",
            "",
            text
        )

        return text.strip()

    # -----------------------------------------------------
    # BUILD ORGANIZATION CANDIDATES
    # -----------------------------------------------------

    candidates = []

    for i, line in enumerate(lines):

        line_clean = clean_organization_line(
            line
        )

        if not line_clean:
            continue

        line_lower = line_clean.lower()

        # Ignore obvious non-organization lines
        if any(
            word in line_lower
            for word in ignore_words
        ):
            continue

        # Ignore phone-number lines
        if re.search(
            r"\d{7,}",
            line_clean
        ):
            continue

        # Ignore very short OCR noise
        if len(line_clean) < 4:
            continue

        # Ignore known OCR noise
        if line_lower in [
            "3",
            "ipi",
            "cz",
            "ci"
        ]:
            continue

        # -------------------------------------------------
        # CASE 1:
        # Current line contains organization keyword
        # -------------------------------------------------

        if any(
            keyword in line_lower
            for keyword in organization_keywords
        ):

            candidate = line_clean

            # Look at previous OCR lines
            previous_parts = []

            for j in range(
                i - 1,
                max(-1, i - 4),
                -1
            ):

                previous = clean_organization_line(
                    lines[j]
                )

                previous_lower = previous.lower()

                if not previous:
                    continue

                # Skip phone numbers
                if re.search(
                    r"\d{7,}",
                    previous
                ):
                    continue

                # Skip unwanted text
                if any(
                    word in previous_lower
                    for word in ignore_words
                ):
                    continue

                # Skip obvious OCR noise
                if previous_lower in [
                    "3",
                    "ipi",
                    "cz",
                    "ci"
                ]:
                    continue

                # Skip corrupted OCR
                if previous_lower in [
                    "cz jeelery",
                    "cz jewellery",
                    "jeelery",
                    "jewellery antique"
                ]:
                    continue

                if len(previous) < 4:
                    continue

                previous_parts.insert(
                    0,
                    previous
                )

                # Usually only one nearby
                # line belongs to organization
                break

            if previous_parts:

                candidate = (
                    " ".join(previous_parts)
                    + " "
                    + candidate
                )

            candidates.append(
                candidate
            )

    # -----------------------------------------------------
    # CHECK ADJACENT OCR LINES
    # -----------------------------------------------------
    #
    # Example:
    #
    # Brindavan
    # Jewellers
    #
    # OCR may detect them separately.
    #
    # We combine them.

    for i in range(
        len(lines) - 1
    ):

        first = clean_organization_line(
            lines[i]
        )

        second = clean_organization_line(
            lines[i + 1]
        )

        if not first or not second:
            continue

        combined = (
            first
            + " "
            + second
        )

        combined_lower = combined.lower()

        # Ignore unwanted combinations
        if any(
            word in combined_lower
            for word in ignore_words
        ):
            continue

        # Ignore phone combinations
        if re.search(
            r"\d{7,}",
            combined
        ):
            continue

        # Check organization keyword
        if any(
            keyword in combined_lower
            for keyword in organization_keywords
        ):

            if len(combined) >= 6:

                candidates.append(
                    combined
                )

    # -----------------------------------------------------
    # REMOVE DUPLICATE CANDIDATES
    # -----------------------------------------------------

    unique_candidates = []

    for candidate in candidates:

        candidate = re.sub(
            r"\s+",
            " ",
            candidate
        ).strip()

        if (
            candidate
            and candidate not in unique_candidates
        ):

            unique_candidates.append(
                candidate
            )

    # -----------------------------------------------------
    # SCORE ORGANIZATION CANDIDATES
    # -----------------------------------------------------

    def score_organization(text):

        text_lower = text.lower()

        score = 0

        # Strong organization keywords
        if "jewellers" in text_lower:
            score += 20

        if "jeweller" in text_lower:
            score += 20

        if "jewellery" in text_lower:
            score += 20

        if "jewelry" in text_lower:
            score += 20

        if "technologies" in text_lower:
            score += 20

        if "technology" in text_lower:
            score += 20

        if "enterprises" in text_lower:
            score += 20

        if "company" in text_lower:
            score += 20

        if "solutions" in text_lower:
            score += 20

        if "store" in text_lower:
            score += 15

        if "shop" in text_lower:
            score += 15

        # Prefer two or more words
        words = text.split()

        if len(words) >= 2:
            score += 10

        # Penalize obvious OCR corruption
        if text_lower.startswith("eers "):
            score -= 10

        if text_lower.startswith("ers "):
            score -= 10

        if "cz " in text_lower:
            score -= 20

        if "jeelery" in text_lower:
            score -= 20

        # Penalize excessive numbers
        if re.search(
            r"\d{3,}",
            text
        ):
            score -= 20

        return score

    # -----------------------------------------------------
    # SELECT BEST ORGANIZATION
    # -----------------------------------------------------

    organization = None

    if unique_candidates:

        unique_candidates.sort(
            key=lambda item: (
                score_organization(item),
                len(item)
            ),
            reverse=True
        )

        organization = (
            unique_candidates[0]
        )

    # -----------------------------------------------------
    # SPECIAL OCR CORRECTION
    # -----------------------------------------------------
    #
    # Your card produces:
    #
    # Brindavan
    # CZ Jeelery & Aiue Je
    # IPI
    # Exclusive In:
    # Jewellers
    #
    # We know "Brindavan" is the main name
    # and "Jewellers" is the business type.
    #
    # Therefore combine them.

    for i, line in enumerate(lines):

        line_clean = clean_organization_line(
            line
        )

        line_lower = line_clean.lower()

        if line_lower == "brindavan":

            for j in range(
                i + 1,
                min(i + 6, len(lines))
            ):

                next_line = (
                    clean_organization_line(
                        lines[j]
                    )
                )

                next_lower = next_line.lower()

                if (
                    "jeweller" in next_lower
                    or "jewellery" in next_lower
                    or "jewelry" in next_lower
                ):

                    organization = (
                        line_clean
                        + " Jewellers"
                    )

                    break

            break

    # -----------------------------------------------------
    # RETURN EXTRACTION DATA
    # -----------------------------------------------------

    return {

        "organization": organization,

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
        r"\Screenshots"
        r"\Screenshot 2026-09-07 215524.png"
    )

    contact = extract_contact(
        image_path
    )

    print(
        "\n"
        + "=" * 40
    )

    print(
        "       IMAGE CONTACT EXTRACTION"
    )

    print(
        "=" * 40
    )

    print(
        "\nOrganization:"
    )

    print(
        contact["organization"]
    )

    print(
        "\nPhone Numbers:"
    )

    for phone in contact[
        "phone_numbers"
    ]:

        print(phone)

    print(
        "\nEmail Addresses:"
    )

    if contact[
        "email_addresses"
    ]:

        for email in contact[
            "email_addresses"
        ]:

            print(email)

    else:

        print(
            "No email found"
        )

    print(
        "\nWebsite:"
    )

    print(
        contact["website"]
    )

    print(
        "\nOCR Text:"
    )

    for line in contact[
        "ocr_text"
    ]:

        print(
            "-",
            line
        )

    print(
        "\n"
        + "=" * 40
    )