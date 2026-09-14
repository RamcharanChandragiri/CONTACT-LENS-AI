from contact_model import create_contact


def convert_voice_contact(voice_contact):

    phone_numbers = []

    if voice_contact.get("phone"):
        phone_numbers.append(voice_contact["phone"])

    unified_contact = create_contact(
        name=voice_contact.get("name"),
        organization=voice_contact.get("company"),
        designation=voice_contact.get("designation"),
        phone_numbers=phone_numbers,
        email=voice_contact.get("email"),
        website=voice_contact.get("website"),
        address=voice_contact.get("address"),
        source=voice_contact.get("source", "voice"),
        confidence=voice_contact.get("confidence", 0.0),
        context=None
    )

    return unified_contact