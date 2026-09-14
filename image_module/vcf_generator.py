def create_vcf(contact):
    vcf_content = []

    vcf_content.append("BEGIN:VCARD")
    vcf_content.append("VERSION:3.0")

    # Contact name selected by the user
    name = contact.get("name")

    if not name:
        name = "Unknown Contact"

    vcf_content.append(f"FN:{name}")

    # Organization
    organization = contact.get("organization")

    if organization:
        vcf_content.append(f"ORG:{organization}")

    # Phone numbers
    for phone in contact.get("phone_numbers", []):
        vcf_content.append(f"TEL:{phone}")

    # Email
    email = contact.get("email")

    if email:
        vcf_content.append(f"EMAIL:{email}")

    # Website / social media
    website = contact.get("website")

    if website:
        vcf_content.append(f"URL:{website}")

    # Address
    address = contact.get("address")

    if address:
        vcf_content.append(f"ADR:;;{address};;;;")

    vcf_content.append("END:VCARD")

    return "\n".join(vcf_content)