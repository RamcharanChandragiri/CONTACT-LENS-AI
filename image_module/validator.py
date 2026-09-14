import re


# ---------------------------------------------------------
# VALIDATE CONTACT
# ---------------------------------------------------------

def validate_contact(contact):

    # -----------------------------------------------------
    # ORGANIZATION
    # -----------------------------------------------------

    organization = contact.get("organization")

    if organization:

        organization = organization.strip()

        organization = re.sub(
            r"\s+",
            " ",
            organization
        )

    # -----------------------------------------------------
    # PHONE NUMBERS
    # -----------------------------------------------------

    phone_numbers = contact.get(
        "phone_numbers",
        []
    )

    valid_phones = []

    for phone in phone_numbers:

        cleaned_phone = re.sub(
            r"[\s\-\(\)]",
            "",
            str(phone)
        )

        # Indian mobile number
        if re.fullmatch(
            r"[6-9]\d{9}",
            cleaned_phone
        ):

            if cleaned_phone not in valid_phones:
                valid_phones.append(cleaned_phone)

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email_addresses = contact.get(
        "email_addresses",
        []
    )

    valid_emails = []

    email_pattern = (
        r"^[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}$"
    )

    for email in email_addresses:

        email = email.strip()

        if re.fullmatch(
            email_pattern,
            email
        ):

            if email not in valid_emails:
                valid_emails.append(email)

    # -----------------------------------------------------
    # WEBSITE
    # -----------------------------------------------------

    website = contact.get("website")

    valid_website = None

    if website:

        website = website.strip()

        website = website.rstrip(
            ".,;:"
        )

        if re.match(
            r"^(https?://|www\.)",
            website,
            re.IGNORECASE
        ):

            if re.search(
                r"\.[A-Za-z]{2,}$",
                website
            ):
                valid_website = website

    # -----------------------------------------------------
    # ADDRESS
    # -----------------------------------------------------

    address = contact.get("address")

    valid_address = None

    if address:

        address = address.strip()

        address = re.sub(
            r"\s+",
            " ",
            address
        )

        # Remove obvious OCR garbage
        address_noise = [
            "acemearrdaan+fasn+erye"
        ]

        for noise in address_noise:

            address = address.replace(
                noise,
                ""
            ).strip()

        # Validate address
        if len(address) >= 10:

            if re.search(
                r"[A-Za-z]",
                address
            ):
                valid_address = address

    # -----------------------------------------------------
    # RETURN VALIDATED CONTACT
    # -----------------------------------------------------

    validated_contact = {

        "name": contact.get("name"),

        "organization": organization,

        "designation": contact.get(
            "designation"
        ),

        "phone_numbers": valid_phones,

        "email": (
            valid_emails[0]
            if valid_emails
            else None
        ),

        "website": valid_website,

        "address": valid_address,

        "source": contact.get(
            "source"
        ),

        "confidence": contact.get(
            "confidence",
            0.0
        ),

        "context": contact.get(
            "context"
        )

    }

    return validated_contact


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    test_contact = {

        "name": None,

        "organization":
            "Brindavan Jewellers",

        "designation": None,

        "phone_numbers": [
            "9959067704",
            "8309371149",
            "9912934662"
        ],

        "email_addresses": [],

        "website":
            "www.facebook.co",

        "address":
            "#15-8-429/D, Aheer Plaza, Feelkhana, Hyderabad",

        "source": "image",

        "confidence": 1.0,

        "context": None

    }

    validated = validate_contact(
        test_contact
    )

    print("\n" + "=" * 40)
    print("       VALIDATED CONTACT")
    print("=" * 40)

    for key, value in validated.items():

        print(f"{key}: {value}")

    print("=" * 40)