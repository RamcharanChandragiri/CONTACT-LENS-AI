import re
import phonenumbers



def extract_email(text):
    """Extract email addresses from normal and spoken formats."""

    text = text.lower()

    # 1. Normal email format
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    # 2. Spoken email format
    # Example:
    # rahul at gmail dot com
    spoken_text = text

    spoken_text = re.sub(r'\s+at\s+', '@', spoken_text)
    spoken_text = re.sub(r'\s+dot\s+', '.', spoken_text)

    match = re.search(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        spoken_text
    )

    if match:
        return match.group(0)

    return None


def extract_phone(text):
    """Extract Indian phone numbers from normal and spoken digit sequences."""

    # 1. Normal 10-digit phone number
    numbers = re.findall(r'(?<!\d)[6-9]\d{9}(?!\d)', text)

    for number in numbers:
        try:
            parsed = phonenumbers.parse(number, "IN")

            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(
                    parsed,
                    phonenumbers.PhoneNumberFormat.E164
                )

        except phonenumbers.NumberParseException:
            continue

    # 2. Handle spoken digits such as:
    # "9 8 7 6 5 4 3 2 1 0"

    spoken_digit_pattern = r'(?<!\d)([0-9](?:\s+[0-9]){9})(?!\d)'

    matches = re.findall(spoken_digit_pattern, text)

    for match in matches:

        number = re.sub(r'\s+', '', match)

        if number[0] in "6789":

            try:
                parsed = phonenumbers.parse(number, "IN")

                if phonenumbers.is_valid_number(parsed):
                    return phonenumbers.format_number(
                        parsed,
                        phonenumbers.PhoneNumberFormat.E164
                    )

            except phonenumbers.NumberParseException:
                continue

    return None


def extract_name(text):
    """Extract person's name."""

    patterns = [
        r"(?:my name is|i am|i'm)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

    return None


def extract_job_details(text):
    """Extract designation and company."""

    pattern = (
        r"(?:i am|i'm|i work as|i work as a|working as|work as)"
        r"\s+(?:a|an)?\s*"
        r"([A-Za-z ]+?)"
        r"\s+(?:at|in)\s+"
        r"([A-Za-z][A-Za-z ]+)"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        designation = match.group(1).strip()
        company = match.group(2).strip()

        # Remove unnecessary trailing words
        company = re.sub(
            r"\s+(my|and|with|phone|email)$",
            "",
            company,
            flags=re.IGNORECASE
        )

        return designation, company

    return None, None


def extract_contact(text):
    """Extract contact information from transcript."""

    designation, company = extract_job_details(text)

    contact = {
        "name": extract_name(text),
        "designation": designation,
        "company": company,
        "phone": extract_phone(text),
        "email": extract_email(text),
        "address": None,
        "website": None,
        "source": "voice",
        "confidence": 0.0
    }

    # Calculate confidence based on extracted fields
    fields = [
        contact["name"],
        contact["designation"],
        contact["company"],
        contact["phone"],
        contact["email"]
    ]

    extracted_fields = sum(
        1 for field in fields if field is not None
    )

    contact["confidence"] = round(
        extracted_fields / len(fields),
        2
    )

    return contact


if __name__ == "__main__":

    transcript = (
        "My name is Rahul Kumar. "
        "I am a software engineer at ABC Technologies. "
        "My phone number is 9876543210 and "
        "my email is rahul@example.com."
    )

    contact = extract_contact(transcript)

    print("\nExtracted Contact:")

    for key, value in contact.items():
        print(f"{key}: {value}")