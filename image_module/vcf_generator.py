import os
import re


def create_vcf(contact):
    """
    Create a .vcf file for the contact and return its file path.
    """

    output_dir = os.path.join(
        "data",
        "generated_contacts"
    )
    os.makedirs(output_dir, exist_ok=True)

    name = (
        str(contact.get("name") or "Unknown Contact")
        .strip()
    )

    # Keep the filename Windows-safe.
    safe_name = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        name
    ).strip("._")

    if not safe_name:
        safe_name = "Unknown_Contact"

    file_path = os.path.join(
        output_dir,
        f"{safe_name}.vcf"
    )

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{name}"
    ]

    organization = contact.get("organization")
    if organization:
        lines.append(f"ORG:{organization}")

    designation = contact.get("designation")
    if designation:
        lines.append(f"TITLE:{designation}")

    for phone in contact.get("phone_numbers", []):
        if phone:
            lines.append(f"TEL:{phone}")

    email = contact.get("email")
    if email:
        lines.append(f"EMAIL:{email}")

    website = contact.get("website")
    if website:
        lines.append(f"URL:{website}")

    address = contact.get("address")
    if address:
        lines.append(f"ADR:;;{address};;;;")

    lines.append("END:VCARD")

    with open(file_path, "w", encoding="utf-8", newline="") as file:
        file.write("\n".join(lines))

    return file_path
