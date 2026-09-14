def create_contact(
    name=None,
    organization=None,
    designation=None,
    phone_numbers=None,
    email=None,
    website=None,
    address=None,
    source=None,
    confidence=0.0,
    context=None
):
    if phone_numbers is None:
        phone_numbers = []

    contact = {
        "name": name,
        "organization": organization,
        "designation": designation,
        "phone_numbers": phone_numbers,
        "email": email,
        "website": website,
        "address": address,
        "source": source,
        "confidence": confidence,
        "context": context
    }

    return contact


def print_contact(contact):
    print("\n" + "=" * 40)
    print("       UNIFIED CONTACT")
    print("=" * 40)

    for key, value in contact.items():
        print(f"{key}: {value}")

    print("=" * 40)